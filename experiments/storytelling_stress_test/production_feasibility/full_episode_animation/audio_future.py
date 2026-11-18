"""Extra procedural sounds for the robot-world story (registered into audio.SOUNDS on import). No recordings, no downloads."""
import math

import numpy as np

import audio
from audio import SR, decay, env, hp_noise, noise, sine


def chime():
    d = 0.9
    n = int(d * SR)
    a = sine(784, 0.4) * decay(int(0.4 * SR), 6)
    b = sine(1175, 0.7) * decay(int(0.7 * SR), 5)
    out = np.zeros(n)
    out[:len(a)] += 0.5 * a
    i = int(0.18 * SR)
    out[i:i + len(b)] += 0.5 * b[: n - i]
    return out


def hum():
    d = 2.2
    n = int(d * SR)
    tt = np.arange(n) / SR
    x = 0.25 * np.sin(2 * np.pi * 96 * tt) + 0.12 * np.sin(2 * np.pi * 192 * tt + 0.7) + 0.05 * noise(d, 0.05, 11)
    return x * np.sin(np.linspace(0, math.pi, n)) ** 0.6


def dooropen():
    d = 0.7
    n = int(d * SR)
    out = 0.35 * noise(d, 0.25, 5) * np.sin(np.linspace(0, math.pi, n))
    k = sine(500, 0.08) * decay(int(0.08 * SR), 40)
    out[:len(k)] += 0.3 * k
    return out


def bloop():
    d = 0.22
    n = int(d * SR)
    return 0.5 * sine(520, d, 980) * env(n, 0.004, 0.08)


def beep():
    d = 0.14
    n = int(d * SR)
    return 0.4 * sine(1480, d) * env(n, 0.004, 0.03)


def buzz():
    d = 0.5
    n = int(d * SR)
    tt = np.arange(n) / SR
    return 0.3 * np.sign(np.sin(2 * np.pi * 120 * tt)) * env(n, 0.01, 0.1)


def servo():
    d = 0.6
    n = int(d * SR)
    return 0.3 * sine(300, d, 620) * np.sin(np.linspace(0, math.pi, n)) + 0.1 * hp_noise(d, 3) * np.sin(np.linspace(0, math.pi, n))


def sizzle():
    d = 1.2
    n = int(d * SR)
    return 0.35 * hp_noise(d, 9) * env(n, 0.05, 0.4)


def typing():
    d = 0.9
    out = np.zeros(int(d * SR))
    for k in range(9):
        i = int((0.05 + k * 0.095) * SR)
        c = 0.4 * hp_noise(0.03, k) * decay(int(0.03 * SR), 90)
        out[i:i + len(c)] += c
    return out


def coin_s():
    d = 0.6
    n = int(d * SR)
    return 0.45 * (sine(1568, d) + 0.6 * sine(2093, d)) * decay(n, 7) * env(n, 0.002, 0.1)


def swoosh_up():
    d = 0.6
    n = int(d * SR)
    return 0.4 * sine(300, d, 1200) * env(n, 0.02, 0.2) + 0.15 * noise(d, 0.3, 4) * env(n, 0.02, 0.3)


def crack():
    """A glassy snap and a falling tone: a heart breaking."""
    d = 0.6
    n = int(d * SR)
    out = np.zeros(n)
    c = hp_noise(0.07, 3)
    out[:len(c)] += 0.7 * c * decay(len(c), 34)
    tone = sine(1100, 0.35, 260) * decay(int(0.35 * SR), 9)
    out[int(0.03 * SR):int(0.03 * SR) + len(tone)] += 0.28 * tone
    return out


audio.SOUNDS.update(crack=crack, chime=chime, hum=hum, dooropen=dooropen, bloop=bloop, beep=beep, buzz=buzz, servo=servo, sizzle=sizzle, typing=typing, coin=coin_s,
                    swoosh_up=swoosh_up)
