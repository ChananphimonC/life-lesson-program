"""Backgrounds for the money / city-life comparison episodes: platform, street, dorm and condo rooms, market.
Station and street come from the thumbnail scenes (same style); room and market are drawn here. Feet line at GROUND.
"""

from __future__ import annotations

import random

import backgrounds as B
import thumbnail_scenes as TS
from art import INK, Pen, add_glow, mix, vgradient

SOFT_INK = (118, 88, 72)
DAY = [(0, (168, 202, 232)), (0.55, (234, 220, 198)), (1, (220, 198, 170))]


def _from_thumb(fn):
    return lambda W, H: fn(W, H, "day", vgradient(W, H, DAY))


def dorm_room(W, H):
    """A small bare room: single bed, a fan, a narrow window, a plastic wardrobe."""
    pen = Pen(W, H, base=vgradient(W, H, [(0, (232, 222, 206)), (1, (218, 204, 186))]))
    floor = H * 0.80
    pen.rect(W * 0.08, H * 0.12, W * 0.30, H * 0.50, (250, 246, 238), outline=SOFT_INK, width=5)
    pen.rect(W * 0.09, H * 0.14, W * 0.29, H * 0.48, (190, 214, 230))
    pen.rect(W * 0.52, H * 0.46, W * 0.96, floor, (150, 168, 196), outline=SOFT_INK, width=5, radius=12)   # bed
    pen.rect(W * 0.52, H * 0.40, W * 0.64, H * 0.50, (250, 246, 240), outline=SOFT_INK, width=4, radius=14)  # pillow
    pen.rect(W * 0.34, H * 0.32, W * 0.46, floor, (196, 206, 214), outline=SOFT_INK, width=4, radius=8)      # wardrobe
    pen.circle(W * 0.72, H * 0.20, H * 0.07, (236, 240, 244), outline=SOFT_INK, width=4)                    # wall fan
    pen.rect(W * 0, floor, W, H, (196, 170, 140))
    pen.line([(0, floor), (W, floor)], SOFT_INK, 4)
    return add_glow(pen.result().convert("RGB"), int(W * 0.2), int(H * 0.3), int(H * 0.4), (255, 244, 220), 0.3)


def condo_room(W, H):
    """A brighter condo room: a big window onto the city, a sofa, a plant."""
    pen = Pen(W, H, base=vgradient(W, H, [(0, (246, 238, 228)), (1, (232, 218, 202))]))
    floor = H * 0.80
    pen.rect(W * 0.08, H * 0.08, W * 0.62, H * 0.62, (250, 248, 244), outline=SOFT_INK, width=5)
    pen.rect(W * 0.095, H * 0.10, W * 0.605, H * 0.60, (176, 210, 236))
    rnd = random.Random(4)
    x = W * 0.10
    while x < W * 0.59:
        bw, bh = rnd.uniform(W * 0.02, W * 0.045), rnd.uniform(H * 0.10, H * 0.28)
        pen.rect(x, H * 0.60 - bh, x + bw, H * 0.60, mix((180, 190, 206), (150, 170, 196), rnd.random()))
        x += bw + 4
    pen.rect(W * 0.66, H * 0.50, W * 0.97, floor, (226, 138, 110), outline=SOFT_INK, width=5, radius=22)    # sofa
    pen.rect(W * 0.66, H * 0.40, W * 0.97, H * 0.56, (236, 156, 126), outline=SOFT_INK, width=5, radius=22)
    pen.rect(W * 0.63, floor - H * 0.16, W * 0.655, floor, (150, 104, 76))                                  # plant pot
    pen.circle(W * 0.64, floor - H * 0.22, H * 0.07, (118, 170, 108), outline=SOFT_INK, width=4)
    pen.rect(0, floor, W, H, (214, 186, 150))
    pen.line([(0, floor), (W, floor)], SOFT_INK, 4)
    return add_glow(pen.result().convert("RGB"), int(W * 0.35), int(H * 0.3), int(H * 0.5), (255, 248, 226), 0.35)


def market(W, H):
    """A wet-market lane: striped awnings, crates of vegetables, a hanging sign board (no text)."""
    rnd = random.Random(12)
    pen = Pen(W, H, base=vgradient(W, H, [(0, (244, 226, 196)), (1, (226, 204, 170))]))
    floor = H * 0.80
    for k in range(7):
        x0 = k * W / 6.4 - W * 0.02
        col = [(226, 112, 96), (250, 214, 120), (130, 188, 140)][k % 3]
        pen.poly([(x0, H * 0.20), (x0 + W / 6.4, H * 0.20), (x0 + W / 6.4 + 14, H * 0.34), (x0 - 14, H * 0.34)], col,
                 outline=SOFT_INK, width=4)
        pen.rect(x0 + 6, H * 0.34, x0 + W / 6.4 - 6, H * 0.40, shade_col(col))
    for k in range(6):
        cx = (k + 0.5) * W / 6
        pen.rect(cx - W * 0.05, floor - H * 0.13, cx + W * 0.05, floor, (170, 124, 86), outline=SOFT_INK, width=4, radius=8)
        for _ in range(7):
            pen.circle(cx + rnd.uniform(-W * 0.04, W * 0.04), floor - H * 0.14 + rnd.uniform(-8, 8), H * 0.032,
                       rnd.choice([(226, 96, 80), (246, 190, 70), (120, 180, 96), (170, 120, 190)]),
                       outline=SOFT_INK, width=2)
    pen.rect(0, floor, W, H, (206, 184, 150))
    pen.line([(0, floor), (W, floor)], SOFT_INK, 4)
    return add_glow(pen.result().convert("RGB"), int(W * 0.5), int(H * 0.25), int(H * 0.6), (255, 244, 216), 0.3)


def shade_col(c):
    return tuple(int(v * 0.88) for v in c)


B.register("platform_day", _from_thumb(TS.train_station))
B.register("street_day", _from_thumb(TS.street))
B.register("office_day", _from_thumb(TS.office))
B.register("dorm_room", dorm_room)
B.register("condo_room", condo_room)
B.register("market", market)
