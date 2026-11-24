"""Mouth movement from the real narration audio.

The speaker's mouth follows the loudness of the voice in each 1/fps window: loud = open, medium = half,
quiet = closed. Not phoneme-accurate, but it opens on syllables and shuts on pauses, so it matches the audio you hear.
"""

from __future__ import annotations

import array
import math
import wave
from pathlib import Path


def mouth_levels(wav_path: Path | None, start_ms: int, end_ms: int, fps: int) -> list[int] | None:
    """One value per animation step from start_ms: 0 closed, 1 open, 2 half. None if there is no usable voice."""
    if wav_path is None or not Path(wav_path).exists():
        return None
    try:
        with wave.open(str(wav_path), "rb") as w:
            if w.getsampwidth() != 2:
                return None
            rate, ch = w.getframerate(), w.getnchannels()
            w.setpos(min(w.getnframes(), int(rate * start_ms / 1000)))
            raw = w.readframes(max(0, int(rate * (end_ms - start_ms) / 1000)))
    except (wave.Error, EOFError, OSError):
        return None
    samples = array.array("h")
    samples.frombytes(raw[: len(raw) - len(raw) % 2])
    if ch > 1:
        samples = samples[::ch]
    win = max(1, int(rate / fps))
    rms = []
    for i in range(0, len(samples), win):
        seg = samples[i:i + win]
        if seg:
            rms.append(math.sqrt(sum(v * v for v in seg) / len(seg)))
    if not rms:
        return None
    ref = sorted(rms)[int(len(rms) * 0.9)] or 0.0
    if ref < 200:            # silent preview / no voice: let the caller fall back to the default pattern
        return None
    out = []
    for i, v in enumerate(rms):
        r = max(v, rms[i - 1] * 0.6 if i else 0.0) / ref      # a little release so the mouth doesn't flutter
        out.append(1 if r > 0.55 else (2 if r > 0.22 else 0))
    return out


def voiced_profile(wav_path: Path | None, start_ms: int, end_ms: int, win_ms: int = 20) -> list[bool] | None:
    """True for each win_ms window that holds speech (loud enough); None when the audio is missing or silent."""
    lv = mouth_levels(wav_path, start_ms, end_ms, max(1, 1000 // win_ms))
    if lv is None:
        return None
    return [v != 0 for v in lv]
