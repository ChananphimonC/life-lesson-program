"""Procedural sound effects (numpy, generated locally; no downloaded audio, no TTS, no voice). 24 kHz mono float arrays."""
from __future__ import annotations

import math

import numpy as np

SR = 24_000
RNG = np.random.default_rng(7)


def t_(dur):
    return np.arange(int(dur * SR)) / SR


def env(n, a=0.005, r=0.2):
    e = np.ones(n)
    na, nr = max(1, int(a * SR)), max(1, int(r * SR))
    e[:na] = np.linspace(0, 1, na)
    e[-nr:] = np.minimum(e[-nr:], np.linspace(1, 0, nr))
    return e


def decay(n, k):
    return np.exp(-np.arange(n) / SR * k)


def noise(dur, lp=0.2, seed=None):
    r = np.random.default_rng(seed) if seed is not None else RNG
    x = r.uniform(-1, 1, int(dur * SR))
    y = np.zeros_like(x)
    acc = 0.0
    for i in range(len(x)):
        acc += lp * (x[i] - acc)
        y[i] = acc
    return y / (np.abs(y).max() + 1e-9)


def hp_noise(dur, seed=None):
    x = noise(dur, 0.9, seed)
    return x - noise(dur, 0.05, seed)


def sine(f, dur, f2=None):
    tt = t_(dur)
    f_arr = f if f2 is None else np.linspace(f, f2, len(tt))
    return np.sin(2 * np.pi * np.cumsum(f_arr) / SR) if f2 is not None else np.sin(2 * np.pi * f * tt)


def step():
    d = 0.09
    n = int(d * SR)
    return (0.8 * sine(95, d, 55) * decay(n, 40) + 0.35 * noise(d, 0.35) * decay(n, 55))


def thump():
    d = 0.3
    n = int(d * SR)
    return 0.9 * sine(80, d, 38) * decay(n, 14) + 0.5 * noise(d, 0.25) * decay(n, 30)


def paper():
    d = 0.4
    n = int(d * SR)
    x = hp_noise(d) * np.abs(np.sin(np.linspace(0, 9 * np.pi, n) + 1.3)) ** 0.8
    return 0.55 * x * env(n, 0.01, 0.15)


def rip():
    d = 0.45
    n = int(d * SR)
    return 0.6 * hp_noise(d) * np.linspace(0.3, 1, n) * env(n, 0.02, 0.1)


def tap():
    d = 0.05
    n = int(d * SR)
    return 0.7 * sine(1700, d) * decay(n, 120) + 0.2 * hp_noise(d) * decay(n, 150)


def ding():
    d = 0.8
    n = int(d * SR)
    return 0.5 * (sine(1320, d) + 0.5 * sine(1980, d) + 0.25 * sine(2640, d)) * decay(n, 5) * env(n, 0.003, 0.1)


def bang():
    d = 0.6
    n = int(d * SR)
    x = sine(430, d) + 0.7 * sine(640, d) + 0.5 * sine(1010, d) + 0.35 * sine(1530, d)
    return 0.55 * x / 2.5 * decay(n, 7) + 0.3 * hp_noise(d) * decay(n, 60)


def ladle():
    d = 0.35
    n = int(d * SR)
    x = sine(880, d) + 0.6 * sine(1310, d) + 0.4 * sine(2150, d)
    return 0.5 * x / 2 * decay(n, 12)


def clink():
    d = 0.3
    n = int(d * SR)
    x = sine(2300, d) + 0.7 * sine(3120, d) + 0.4 * sine(4300, d)
    return 0.4 * x / 2 * decay(n, 18)


def plop():
    d = 0.16
    n = int(d * SR)
    return 0.7 * sine(420, d, 140) * decay(n, 22)


def pop():
    d = 0.08
    n = int(d * SR)
    return 0.6 * sine(700, d, 280) * decay(n, 40)


def whoosh():
    d = 0.55
    n = int(d * SR)
    return 0.55 * noise(d, 0.12) * np.sin(np.linspace(0, math.pi, n)) ** 1.5


def spit():
    d = 0.5
    n = int(d * SR)
    return 0.6 * hp_noise(d) * decay(n, 7) * env(n, 0.003, 0.1)


def gasp():
    d = 0.45
    n = int(d * SR)
    return 0.4 * noise(d, 0.45) * np.sin(np.linspace(0, math.pi, n)) ** 0.8


def spoon():
    d = 0.14
    n = int(d * SR)
    return 0.35 * (sine(2600, d) + 0.5 * sine(3900, d)) * decay(n, 40)


def scribble():
    d = 0.7
    n = int(d * SR)
    return 0.4 * hp_noise(d) * (0.5 + 0.5 * np.abs(np.sin(np.linspace(0, 14 * np.pi, n)))) * env(n, 0.02, 0.1)


def grunt():
    d = 0.3
    n = int(d * SR)
    return 0.4 * (2 * ((np.cumsum(np.full(n, 125.0)) / SR) % 1) - 1) * env(n, 0.03, 0.15) * np.linspace(1, 0.6, n)


def cheer():
    d = 1.6
    n = int(d * SR)
    x = noise(d, 0.5) * (0.6 + 0.4 * np.sin(np.linspace(0, 20, n)))
    return 0.5 * x * env(n, 0.1, 0.5)


def crowd():
    d = 1.4
    n = int(d * SR)
    return 0.45 * noise(d, 0.35) * (0.7 + 0.3 * np.sin(np.linspace(0, 11, n))) * env(n, 0.15, 0.5)


def boing():
    d = 0.5
    n = int(d * SR)
    return 0.55 * sine(220, d, 700) * np.sin(np.linspace(0, 40 * math.pi / 8, n)) ** 2 * decay(n, 5) + 0.3 * sine(300, d, 160) * decay(n, 6)


def crickets():
    d = 4.0
    out = np.zeros(int(d * SR))
    for k in range(int(d / 0.25)):
        s0 = int(k * 0.25 * SR)
        seg_ = sine(4200, 0.18) * np.abs(np.sin(np.linspace(0, 6 * math.pi, int(0.18 * SR)))) * 0.15
        out[s0:s0 + len(seg_)] += seg_[: len(out) - s0]
    return out * env(len(out), 0.3, 0.5)


def mic():
    d = 0.35
    n = int(d * SR)
    return 0.4 * (sine(90, d) + 0.4 * hp_noise(d)) * decay(n, 8)


def whistle():
    d = 0.55
    n = int(d * SR)
    return 0.4 * sine(2400, d, 2900) * (0.8 + 0.2 * np.sin(np.linspace(0, 80, n))) * env(n, 0.02, 0.1)


def bamboo():
    d = 0.4
    n = int(d * SR)
    return 0.6 * (sine(520, d) + 0.5 * sine(1090, d)) / 1.5 * decay(n, 22) + 0.3 * hp_noise(d) * decay(n, 60)


def laugh():
    d = 1.2
    out = np.zeros(int(d * SR))
    for k in range(6):
        s0 = int(k * 0.17 * SR)
        s = sine(380 + 25 * (k % 2), 0.12, 300) * env(int(0.12 * SR), 0.01, 0.06) * (1 - k * 0.1)
        out[s0:s0 + len(s)] += s * 0.4
    return out


def water():
    d = 2.0
    n = int(d * SR)
    return 0.25 * noise(d, 0.12) * (0.7 + 0.3 * np.sin(np.linspace(0, 30, n))) * env(n, 0.2, 0.4)


def sigh():
    d = 1.0
    n = int(d * SR)
    return 0.3 * noise(d, 0.3) * np.sin(np.linspace(0, math.pi, n)) ** 1.2


SOUNDS = dict(step=step, thump=thump, paper=paper, rip=rip, tap=tap, ding=ding, bang=bang, ladle=ladle, clink=clink, plop=plop, pop=pop, whoosh=whoosh,
              spit=spit, gasp=gasp, spoon=spoon, scribble=scribble, grunt=grunt, cheer=cheer, crowd=crowd, boing=boing, crickets=crickets, mic=mic,
              whistle=whistle, bamboo=bamboo, laugh=laugh, water=water, sigh=sigh)
_cache = {}


def get(name):
    if name not in SOUNDS:
        return None
    if name not in _cache:
        _cache[name] = SOUNDS[name]()
    return _cache[name]


def mix(scene_cues, total_s):
    """scene_cues: list of (absolute time s, name, gain). Returns int16 samples, peak-limited (no clipping)."""
    out = np.zeros(int(total_s * SR) + SR)
    for t0, name, g in scene_cues:
        s = get(name)
        if s is None or g <= 0:
            continue
        i = int(t0 * SR)
        if i < 0 or i >= len(out):
            continue
        n = min(len(s), len(out) - i)
        out[i:i + n] += s[:n] * g
    peak = np.abs(out).max()
    if peak > 0.85:
        out *= 0.85 / peak
    # soft limiter for the very few overlapping peaks
    out = np.tanh(out * 1.2) / 1.2
    return (out[: int(total_s * SR)] * 32000).astype(np.int16)
