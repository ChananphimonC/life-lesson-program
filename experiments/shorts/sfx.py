"""Procedural sound effects (synthesised locally, no downloaded/copyrighted audio).

Every effect returns 24 kHz mono samples as an array('h'). `make(name)` is the registry used by
scripts: scene-level "sfx" cues and lines with "sfx_voice" (e.g. dogs barking, a sigh).
"""

from __future__ import annotations

import math
import random
from array import array

SR = 24_000


def _to_pcm(xs, gain=0.8) -> array:
    peak = max(1e-9, max(abs(x) for x in xs))
    return array("h", (int(max(-1.0, min(1.0, x / peak * gain)) * 32000) for x in xs))


def _env(i, n, attack=0.01, release=0.3):
    t = i / SR
    a = min(1.0, t / attack) if attack else 1.0
    r = min(1.0, (n - i) / SR / release) if release else 1.0
    return a * r


def _tone(freq, dur, wave="sine", release=0.2, f_end=None):
    n = int(dur * SR)
    out, ph = [], 0.0
    for i in range(n):
        f = freq if f_end is None else freq + (f_end - freq) * i / n
        ph += 2 * math.pi * f / SR
        s = math.sin(ph) if wave == "sine" else (2 * ((ph / (2 * math.pi)) % 1) - 1)
        out.append(s * _env(i, n, 0.005, release))
    return out


def _noise(dur, lowpass=0.1, seed=1, attack=0.01, release=0.3):
    rnd = random.Random(seed)
    n, y, out = int(dur * SR), 0.0, []
    for i in range(n):
        y += lowpass * (rnd.uniform(-1, 1) - y)
        out.append(y * _env(i, n, attack, release))
    return out


def _cat(*parts):
    out = []
    for p in parts:
        out.extend(p)
    return out


def _silence(dur):
    return [0.0] * int(dur * SR)


def news_jingle():
    return _to_pcm(_cat(_tone(784, 0.16), _tone(1047, 0.16), _tone(1319, 0.45, release=0.35)), 0.55)


def thunder():
    return _to_pcm(_noise(1.8, 0.02, seed=3, attack=0.05, release=1.2), 0.9)


def water(dur=6.0):
    xs = _noise(dur, 0.25, seed=5, attack=0.4, release=0.6)
    return _to_pcm([x * (0.7 + 0.3 * math.sin(2 * math.pi * 0.7 * i / SR)) for i, x in enumerate(xs)], 0.35)


def ding():
    return _to_pcm(_cat(_tone(1318, 0.12, release=0.1), _tone(1760, 0.3, release=0.25)), 0.6)


def heartbreak():
    crack = _noise(0.08, 0.9, seed=9, attack=0.001, release=0.06)
    return _to_pcm(_cat(crack, _tone(620, 0.55, release=0.3, f_end=180)), 0.6)


def bark(times=1):
    one = []
    for k in range(times):
        b = _tone(520, 0.17, "saw", release=0.1, f_end=300)
        nz = _noise(0.17, 0.5, seed=11 + k, attack=0.003, release=0.1)
        one += [0.7 * x + 0.5 * y for x, y in zip(b, nz)] + _silence(0.12)
    return _to_pcm(one, 0.7)


def sigh():
    return _to_pcm(_noise(1.1, 0.06, seed=13, attack=0.15, release=0.8), 0.45)


def cheer():
    xs = _noise(1.8, 0.35, seed=17, attack=0.1, release=0.9)
    return _to_pcm([x * (0.6 + 0.4 * abs(math.sin(2 * math.pi * 6 * i / SR))) for i, x in enumerate(xs)], 0.6)


def boing():
    return _to_pcm(_cat(_tone(220, 0.18, f_end=660, release=0.05), _tone(660, 0.3, f_end=180, release=0.25)), 0.55)


def splash():
    return _to_pcm(_noise(0.6, 0.6, seed=19, attack=0.005, release=0.5), 0.6)


def whoosh():
    xs = _noise(0.45, 0.3, seed=23, attack=0.2, release=0.25)
    return _to_pcm(xs, 0.5)


def gasp():
    return _to_pcm(_noise(0.35, 0.5, seed=29, attack=0.03, release=0.25), 0.4)


REGISTRY = {
    "news_jingle": news_jingle, "thunder": thunder, "water": water, "ding": ding, "heartbreak": heartbreak,
    "bark": lambda: bark(1), "bark3": lambda: bark(3), "sigh": sigh, "cheer": cheer, "boing": boing,
    "splash": splash, "whoosh": whoosh, "gasp": gasp,
}


def make(name: str) -> array:
    if name not in REGISTRY:
        raise KeyError(f"unknown sfx '{name}' (have: {', '.join(REGISTRY)})")
    return REGISTRY[name]()
