"""Amplitude-based mouth shapes (no phoneme model, no GPU).

`mouth_track(samples, fps)` returns one (shape, level) per video frame of a spoken line:
shape 0..3 = closed / slight / open / wide, level 0..1 = loudness (drives the body bounce).
"""

from __future__ import annotations

from array import array

SAMPLE_RATE = 24_000
THRESHOLDS = (0.10, 0.34, 0.68)  # level -> shape boundaries
MIN_HOLD = 2                     # frames a shape must last, so the mouth doesn't flicker


def frame_levels(samples: array, fps: int) -> list[float]:
    win = SAMPLE_RATE // fps
    rms = []
    for i in range(0, len(samples), win):
        chunk = samples[i:i + win]
        rms.append((sum(s * s for s in chunk) / max(1, len(chunk))) ** 0.5)
    loud = sorted(r for r in rms if r > 250)
    ref = loud[int(len(loud) * 0.9)] if loud else 1.0
    return [min(1.0, r / ref) for r in rms]


def _shape(level: float) -> int:
    return sum(level >= t for t in THRESHOLDS)


def mouth_track(samples: array, fps: int) -> list[tuple[int, float]]:
    levels = frame_levels(samples, fps)
    smooth = [(levels[max(0, i - 1)] + 2 * levels[i] + levels[min(len(levels) - 1, i + 1)]) / 4
              for i in range(len(levels))]
    shapes = [_shape(v) for v in smooth]
    i = 0
    while i < len(shapes):  # absorb 1-frame blips into the previous shape
        j = i
        while j < len(shapes) and shapes[j] == shapes[i]:
            j += 1
        if j - i < MIN_HOLD and i > 0:
            shapes[i:j] = [shapes[i - 1]] * (j - i)
        i = j
    return list(zip(shapes, smooth))
