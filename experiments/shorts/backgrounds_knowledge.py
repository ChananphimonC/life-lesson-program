"""Backgrounds for the "รู้หรือไม่" explainer series (any aspect; drawn for 16:9 first). Feet line at GROUND."""

from __future__ import annotations

import random

import backgrounds as B
from art import INK, Pen, add_glow, vgradient

SOFT_INK = (118, 88, 72)


def studio(W, H):
    """A friendly explainer set: pastel wall with soft shapes, a light stage floor, a warm spotlight."""
    rnd = random.Random(3)
    pen = Pen(W, H, base=vgradient(W, H, [(0, (252, 236, 214)), (0.66, (246, 222, 200)), (1, (232, 204, 182))]))
    for _ in range(14):
        x, y, r = rnd.uniform(0, W), rnd.uniform(0, H * 0.6), rnd.uniform(H * 0.04, H * 0.12)
        pen.circle(x, y, r, rnd.choice([(250, 214, 190), (232, 228, 206), (214, 230, 226), (246, 206, 214)]))
    floor = B.GROUND * H
    pen.rect(0, floor - H * 0.02, W, H, (226, 190, 158))
    pen.rect(0, floor - H * 0.02, W, floor, (240, 210, 180))
    pen.line([(0, floor - H * 0.02), (W, floor - H * 0.02)], SOFT_INK, 4)
    for k in range(1, 10):
        x = W * k / 10
        pen.line([(W / 2 + (x - W / 2) * 0.55, floor + 2), (x, H)], (212, 176, 146), 3)
    img = pen.result().convert("RGB")
    return add_glow(img, int(W * 0.5), int(H * 0.3), int(H * 0.55), (255, 246, 224), 0.35)


def study_room(W, H):
    """Bookshelves and a desk lamp: for history / research moments."""
    rnd = random.Random(8)
    pen = Pen(W, H, base=vgradient(W, H, [(0, (230, 214, 196)), (1, (214, 194, 174))]))
    floor = B.GROUND * H
    sx0, sx1 = W * 0.04, W * 0.42                                                     # bookshelf
    pen.rect(sx0, H * 0.08, sx1, floor, (150, 104, 76), outline=SOFT_INK, width=5)
    for r in range(4):
        y = H * 0.12 + r * (floor - H * 0.16) / 4
        pen.rect(sx0 + 10, y + (floor - H * 0.16) / 4 - 12, sx1 - 10, y + (floor - H * 0.16) / 4, (120, 82, 60))
        x = sx0 + 16
        while x < sx1 - 30:
            bw = rnd.uniform(18, 34) * W / 1920
            bh = rnd.uniform(0.6, 0.9) * (floor - H * 0.16) / 4
            pen.rect(x, y + (floor - H * 0.16) / 4 - 12 - bh, x + bw, y + (floor - H * 0.16) / 4 - 12,
                     rnd.choice([(196, 92, 80), (92, 132, 170), (120, 160, 110), (226, 180, 90), (150, 110, 160)]),
                     outline=SOFT_INK, width=2)
            x += bw + 3
    wx0, wx1 = W * 0.62, W * 0.94                                                     # window
    pen.rect(wx0, H * 0.10, wx1, H * 0.46, (250, 246, 238), outline=SOFT_INK, width=5)
    pen.rect(wx0 + 12, H * 0.10 + 12, wx1 - 12, H * 0.46 - 12, (178, 210, 232))
    pen.line([((wx0 + wx1) / 2, H * 0.10), ((wx0 + wx1) / 2, H * 0.46)], SOFT_INK, 5)
    pen.rect(0, floor, W, H, (172, 128, 96))
    pen.line([(0, floor), (W, floor)], SOFT_INK, 4)
    return add_glow(pen.result().convert("RGB"), int(W * 0.78), int(H * 0.28), int(H * 0.4), (255, 240, 210), 0.3)


B.register("studio", studio)
B.register("study_room", study_room)
