"""Character voices for the episode (free edge-tts Thai voices, the same fallback engine the Shorts pipeline uses; no Gemini quota, no key).

Every spoken line of a scene (its CAPS entry: start, end, speaker, text) is synthesised once and cached in audio/voice/ (keyed by voice + text).
Stage directions in parentheses are not spoken. Speakers are told apart by voice: edge-tts has only two Thai voices (Niwat, Premwadee), so
each character gets its own pitch and speed on one of them. Lines are fitted to their window (sped up a little if they run long), and the
loudness envelope of each line is saved so the mouths can follow the real audio (engine.talk reads audio/voice_manifest.json).

    python voice.py            -> synthesises missing lines, writes audio/voice_track.wav + audio/voice_manifest.json
    python voice.py --report   -> prints the fit of every line (duration vs window)
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import wave
from array import array
from pathlib import Path
from types import SimpleNamespace

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.append(str(HERE.parents[2] / "shorts"))
sys.path.append(str(HERE.parents[3] / "src"))
import tts  # noqa: E402  (shorts/tts.py: _edge_segment, trim_silence, normalize)

CACHE = HERE / "audio" / "voice"
SR = tts.SAMPLE_RATE
FPS = 24
SETTINGS = SimpleNamespace(ffmpeg_binary="ffmpeg")

# one base voice + pitch/speed per character (the only way to tell speakers apart with two Thai voices)
VOICES = {
    "ton": dict(edge="th-TH-NiwatNeural", edge_pitch="+42Hz", edge_rate="+10%"),         # a boy: high, quick, eager
    "chok": dict(edge="th-TH-NiwatNeural", edge_pitch="-12Hz", edge_rate="-6%"),         # a laid-back uncle: low, slow
    "kaew": dict(edge="th-TH-PremwadeeNeural", edge_pitch="-22Hz", edge_rate="-10%"),    # an old woman: low, slow
    "uean": dict(edge="th-TH-PremwadeeNeural", edge_pitch="+8Hz", edge_rate="+8%"),      # a lively aunt: brighter, faster
    "pin": dict(edge="th-TH-PremwadeeNeural", edge_pitch="+38Hz", edge_rate="+6%"),      # ปิ่น, a girl: high and bright
    "mom": dict(edge="th-TH-PremwadeeNeural", edge_pitch="-4Hz", edge_rate="-4%"),       # แม่: warm, a little slower
}
SKIP = {("s4c", 0.0)}          # s4c's opening "เจ็ดแล้ว!" repeats the last line of s4b (the caption carried over the cut)
MAX_SPEEDUP = 1.35


def clean(text):
    t = re.sub(r"\([^)]*\)", "", text)
    t = t.replace("“", "").replace("”", "").replace("…", " ... ")
    return re.sub(r"\s+", " ", t).strip()


def edge_line(v, text, tmp):
    """One edge-tts request -> trimmed 24 kHz samples (own temp files, so nothing is shared with the storyboard app's cache)."""
    import asyncio
    import time

    import edge_tts

    mp3, wav = tmp.with_suffix(".mp3"), tmp.with_suffix(".wav")
    for attempt in range(6):
        try:
            asyncio.run(edge_tts.Communicate(text, v["edge"], rate=v["edge_rate"], pitch=v["edge_pitch"]).save(str(mp3)))
            break
        except Exception:  # noqa: BLE001 - the free endpoint throttles bursts
            if attempt == 5:
                raise
            time.sleep(2.0 * (attempt + 1))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(mp3), "-af", tts.FINISH, "-ar", str(SR), "-ac", "1", "-sample_fmt", "s16",
                    str(wav)], check=True)
    samples = tts.read_wav(wav)
    for f in (mp3, wav):
        try:
            f.unlink()
        except OSError:
            pass
    time.sleep(0.4)
    return tts.trim_silence(samples, keep_ms=40)


def synth(who, text):
    CACHE.mkdir(parents=True, exist_ok=True)
    v = VOICES[who]
    key = hashlib.sha1(f"{who}|{v['edge']}|{v['edge_pitch']}|{v['edge_rate']}|{text}".encode("utf-8")).hexdigest()[:12]
    path = CACHE / f"{who}-{key}.wav"
    if not path.is_file():
        samples = edge_line(v, text, path.with_suffix(".tmp"))
        tts.write_wav(path, tts.normalize(samples, 24000))
    with wave.open(str(path), "rb") as w:
        return np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768.0


def speed_up(x, f):
    """Tempo change without changing the pitch (ffmpeg atempo)."""
    if f <= 1.005:
        return x
    p = subprocess.run(["ffmpeg", "-v", "error", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", "-af", f"atempo={f:.4f}",
                        "-f", "f32le", "-"], input=x.astype("<f4").tobytes(), capture_output=True, check=True)
    return np.frombuffer(p.stdout, "<f4").astype(np.float32)


def envelope(x):
    win = SR // FPS
    n = len(x) // win + 1
    rms = np.array([np.sqrt(np.mean(x[i * win:(i + 1) * win] ** 2)) if len(x[i * win:(i + 1) * win]) else 0.0 for i in range(n)])
    loud = np.sort(rms[rms > 0.01])
    ref = loud[int(len(loud) * 0.9)] if len(loud) else 1.0
    lv = np.clip(rms / ref, 0, 1)
    sm = (np.r_[lv[0], lv[:-1]] + 2 * lv + np.r_[lv[1:], lv[-1]]) / 4
    return np.where(sm < 0.12, 0.0, np.clip(sm ** 0.8 * 1.1, 0, 1))


def build(timeline, report=False):
    """timeline: [(scene module name, absolute start, duration, CAPS)]. Returns the voice track and the manifest."""
    total = timeline[-1][1] + timeline[-1][2]
    track = np.zeros(int((total + 1) * SR), np.float32)
    clips = []
    for name, t0, dur, caps in timeline:
        spoken = [(a, b, who, clean(text)) for a, b, who, text in caps if clean(text) and (name, a) not in SKIP]
        for i, (a, b, who, text) in enumerate(spoken):
            x = synth(who, text)
            d, win = len(x) / SR, b - a
            room_end = (spoken[i + 1][0] - 0.1) if i + 1 < len(spoken) else min(dur - 0.1, b + 1.5)   # how far this line may run on
            allowed = max(win, room_end - a)
            f = max(1.0, min(MAX_SPEEDUP, d / max(win, 0.3)))
            if d / f > allowed:
                f = min(MAX_SPEEDUP, d / allowed)
            y = speed_up(x, f)
            start = a + 0.04
            end = start + len(y) / SR
            j = int((t0 + start) * SR)
            track[j:j + len(y)] += y
            clips.append(dict(scene=name, a=a, b=b, who=who, text=text, start=start, end=end, speed=round(f, 3), natural=round(d, 2),
                              env=[round(float(v), 3) for v in envelope(y)], overrun=round(max(0.0, end - max(b, 0)), 2)))
            if report:
                print(f"{name:4s} {a:6.1f} {who:5s} nat {d:5.2f}s win {win:4.1f}s speed {f:4.2f} ends {end:6.2f} (window ends {b:5.1f})  {text[:40]}")
    return track, clips


if __name__ == "__main__":
    import episode
    tl, total = episode.timeline()
    timeline = []
    for n, t0, dur in tl:
        timeline.append((n, t0, dur, episode.mod(n).CAPS))
    track, clips = build(timeline, report="--report" in sys.argv or True)
    out = HERE / "audio"
    out.mkdir(exist_ok=True)
    tts.write_wav(out / "voice_track.wav", array("h", (np.clip(track, -1, 1) * 32000).astype(np.int16)))
    (out / "voice_manifest.json").write_text(json.dumps(clips, ensure_ascii=False), encoding="utf-8")
    print("lines", len(clips), "overruns >0.5s:", [(c["scene"], c["a"]) for c in clips if c["overrun"] > 0.5])
