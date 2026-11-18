"""Per-line TTS for Shorts: Gemini first (under gemini_guard), edge-tts as the free fallback.

Every spoken line is cached as its own WAV in output/_work/tts/<short_id>/ (same cache layout
the Life Lesson episodes use); a line whose text/voice did not change is never synthesized again.
All WAVs are 24 kHz mono 16-bit so lines can be mixed straight into one timeline.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import subprocess
import time
import wave
from array import array
from io import BytesIO
from dataclasses import replace
from pathlib import Path

import gemini_guard
from life_lesson.config import Settings
from life_lesson.tts.gemini_tts import GeminiTTSProvider

HERE = Path(__file__).resolve().parent
CACHE = HERE.parent / "cartoon_storyboard" / "output" / "_work" / "tts"
SAMPLE_RATE = 24_000
EDGE_MIN_INTERVAL = 1.5  # seconds between edge-tts requests; the free endpoint throttles bursts
_last_edge = [0.0]


def _cache_key(character: dict, text, engine: str = "edge") -> str:
    """Gemini lines are keyed by character + Gemini voice + text only, so tweaking edge-tts rate/pitch never re-spends quota."""
    v = character["voice"]
    if engine == "gemini":
        raw = f"{character['id']}|{v['gemini']}|{_plain(text)}"
    else:
        body = text if isinstance(text, str) else json.dumps(text, ensure_ascii=False, sort_keys=True)
        raw = f"{character['id']}|{v['gemini']}|{v['edge']}|{v.get('edge_rate', '')}|{v.get('edge_pitch', '')}|{body}"
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:10]


def find_cached(short_id: str, idx: int, character: dict, text, engine: str) -> Path | None:
    path = CACHE / short_id / f"line{idx:02d}-{_cache_key(character, text, engine)}.{engine}.wav"
    return path if path.is_file() else None


def read_wav(path: Path) -> array:
    with wave.open(str(path), "rb") as w:
        assert w.getframerate() == SAMPLE_RATE and w.getnchannels() == 1 and w.getsampwidth() == 2, \
            f"{path.name}: expected 24 kHz mono 16-bit"
        samples = array("h")
        samples.frombytes(w.readframes(w.getnframes()))
    return samples


def write_wav(path: Path, samples: array) -> None:
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SAMPLE_RATE)
        w.writeframes(samples.tobytes())


def trim_silence(samples: array, threshold: int = 350, keep_ms: int = 90) -> array:
    """Cut the lead/tail silence TTS engines add, keeping a short margin."""
    idx = [i for i, s in enumerate(samples) if abs(s) > threshold]
    if not idx:
        return samples
    keep = SAMPLE_RATE * keep_ms // 1000
    return samples[max(0, idx[0] - keep): idx[-1] + keep]


def _plain(text) -> str:
    return text if isinstance(text, str) else " ".join(seg["t"] for seg in text)


def _gemini(settings: Settings, character: dict, text) -> bytes:
    text = _plain(text)
    provider = GeminiTTSProvider(replace(settings, gemini_tts_voice=character["voice"]["gemini"]))
    return gemini_guard.guarded("tts", lambda: provider.synthesize(text))


FINISH = ("highpass=f=80,lowpass=f=7600,equalizer=f=200:width_type=q:width=1:g=1.5,"
          "acompressor=threshold=-22dB:ratio=2:attack=15:release=250")


def _edge_segment(settings: Settings, voice: dict, text: str, rate: str, pitch: str) -> array:
    import edge_tts  # free, no key; pip install edge-tts

    mp3 = CACHE / "_edge_tmp.mp3"
    mp3.parent.mkdir(parents=True, exist_ok=True)
    for attempt in range(7):  # the free endpoint sometimes returns no audio under bursts; back off
        wait = EDGE_MIN_INTERVAL - (time.time() - _last_edge[0])
        if wait > 0:
            time.sleep(wait)
        _last_edge[0] = time.time()
        try:
            asyncio.run(edge_tts.Communicate(text, voice["edge"], rate=rate, pitch=pitch).save(str(mp3)))
            break
        except Exception:  # noqa: BLE001
            if attempt == 6:
                raise
            time.sleep(min(30.0, 3.0 * 2 ** attempt))
    wav = mp3.with_suffix(".wav")
    subprocess.run([settings.ffmpeg_binary, "-y", "-loglevel", "error", "-i", str(mp3), "-af", FINISH,
                    "-ar", str(SAMPLE_RATE), "-ac", "1", "-sample_fmt", "s16", str(wav)], check=True)
    samples = read_wav(wav)
    mp3.unlink(missing_ok=True)
    wav.unlink(missing_ok=True)
    return trim_silence(samples, keep_ms=40)


def _edge(settings: Settings, character: dict, text) -> bytes:
    v = character["voice"]
    segs = [{"t": text}] if isinstance(text, str) else text
    out = array("h")
    for k, seg in enumerate(segs):
        if k:
            out.extend(array("h", bytes(2 * int(SAMPLE_RATE * seg.get("gap", 0.04)))))
        out.extend(_edge_segment(settings, v, seg["t"], seg.get("rate", v.get("edge_rate", "+0%")),
                                 seg.get("pitch", v.get("edge_pitch", "+0Hz"))))
    buf = BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SAMPLE_RATE)
        w.writeframes(out.tobytes())
    return buf.getvalue()


def normalize(samples: array, peak: int = 23000) -> array:
    top = max((abs(x) for x in samples), default=0)
    if top == 0:
        return samples
    k = peak / top
    return array("h", (max(-32767, min(32767, int(x * k))) for x in samples))


class VoicingIncomplete(RuntimeError):
    """Gemini stopped (quota) before every line was voiced; finished lines stay cached for the next run."""


def synth_line(settings: Settings, short_id: str, idx: int, character: dict, text, mode: str = "auto") -> tuple[Path, str]:
    """Returns (wav path, engine: 'cache' | 'gemini' | 'edge'). 'auto' prefers Gemini and falls back to edge-tts;
    'gemini' never falls back (raises VoicingIncomplete when the quota stops it)."""
    engines = {"auto": ("gemini", "edge"), "gemini": ("gemini",), "edge": ("edge",)}[mode]
    folder = CACHE / short_id
    folder.mkdir(parents=True, exist_ok=True)
    errors = []
    for engine in engines:
        hit = find_cached(short_id, idx, character, text, engine)
        if hit:
            return hit, "cache"
        try:
            wav_bytes = (_gemini if engine == "gemini" else _edge)(settings, character, text)
        except Exception as exc:  # noqa: BLE001 - fall through to the next engine
            errors.append(f"{engine}: {str(exc)[:160]}")
            print(f"  line {idx}: {engine} TTS unavailable ({str(exc)[:110]}); trying next", flush=True)
            continue
        path = folder / f"line{idx:02d}-{_cache_key(character, text, engine)}.{engine}.wav"
        tmp = folder / "_tmp.wav"
        tmp.write_bytes(wav_bytes)
        write_wav(path, normalize(trim_silence(read_wav(tmp))))
        tmp.unlink()
        return path, engine
    msg = f"no TTS engine worked for line {idx}: {' | '.join(errors)}"
    raise (VoicingIncomplete if mode == "gemini" else RuntimeError)(msg)
