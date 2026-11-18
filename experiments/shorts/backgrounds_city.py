"""City-life scenes for the money / survival-in-Bangkok episodes: train cars, wholesale store, kitchen, street stall, cafe.
Generic places only (no brands or logos). Floor line near 0.80*H; characters stand a little in front of it.
"""

from __future__ import annotations

import math
import random

from PIL import ImageDraw

import backgrounds as B
from art import Pen, add_glow, mix, vgradient

SOFT_INK = (118, 88, 72)
TRAIN_WINDOWS = [(0.04, 0.12, 0.32, 0.50), (0.36, 0.12, 0.64, 0.50), (0.68, 0.12, 0.96, 0.50)]


def train_car(W, H, tunnel=False, bus=False):
    """Inside a train: three big windows (the view scrolls via the train_view / tunnel_view fx), straps, a bench."""
    wall = (214, 220, 232) if tunnel else (226, 230, 236)
    pen = Pen(W, H, base=vgradient(W, H, [(0, wall), (1, mix(wall, (190, 196, 206), 0.4))]))
    for x0, y0, x1, y1 in TRAIN_WINDOWS:
        pen.rect(W * x0 - 8, H * y0 - 8, W * x1 + 8, H * y1 + 8, (250, 250, 252), outline=SOFT_INK, width=5, radius=18)
        pen.rect(W * x0, H * y0, W * x1, H * y1, (28, 32, 52) if tunnel else (150, 190, 226), radius=12)
    pen.rect(0, H * 0.055, W, H * 0.075, (170, 176, 188))
    for k in range(7):
        x = W * (0.10 + k * 0.13)
        pen.line([(x, H * 0.075), (x, H * 0.13)], (236, 236, 240), 5)
        pen.circle(x, H * 0.155, H * 0.028, None, outline=(236, 236, 240), width=6)
    seat = (232, 120, 70) if tunnel else (74, 130, 196)
    if bus:
        seat = (240, 164, 72)
        wall = (246, 236, 214)
    pen.rect(0, H * 0.56, W, H * 0.80, seat, outline=SOFT_INK, width=4)
    for k in range(1, 8):
        pen.line([(W * k / 8, H * 0.56), (W * k / 8, H * 0.80)], mix(seat, (0, 0, 0), 0.25), 5)
    pen.rect(0, H * 0.80, W, H, (178, 178, 188))
    pen.line([(0, H * 0.80), (W, H * 0.80)], SOFT_INK, 4)
    return add_glow(pen.result().convert("RGB"), int(W * 0.5), int(H * 0.2), int(H * 0.6), (255, 255, 246), 0.3)


def bus_stop_dawn(W, H):
    """Early morning at a bus stop: pink-orange sky, dim buildings, a shelter with a bench, a lit street lamp."""
    pen = Pen(W, H, base=vgradient(W, H, [(0, (92, 98, 150)), (0.35, (226, 150, 140)), (0.62, (252, 206, 150)), (1, (190, 176, 170))]))
    rnd = random.Random(14)
    x = -30
    while x < W:
        bw, bh = rnd.uniform(W * 0.07, W * 0.13), rnd.uniform(H * 0.18, H * 0.42)
        pen.rect(x, H * 0.74 - bh, x + bw, H * 0.74, (122, 112, 138), outline=SOFT_INK, width=3)
        for wy in range(int(H * 0.74 - bh + 20), int(H * 0.72), 44):
            if rnd.random() < 0.35:
                pen.rect(x + bw * 0.2, wy, x + bw * 0.4, wy + 20, (255, 224, 150))
        x += bw
    pen.rect(W * 0.55, H * 0.40, W * 0.95, H * 0.44, (96, 118, 150), outline=SOFT_INK, width=4)                     # shelter roof
    for px in (0.57, 0.93):
        pen.rect(W * px - 5, H * 0.44, W * px + 5, H * 0.74, (118, 126, 140), outline=SOFT_INK, width=3)
    pen.rect(W * 0.60, H * 0.62, W * 0.90, H * 0.66, (170, 122, 84), outline=SOFT_INK, width=4, radius=6)          # bench
    pen.rect(W * 0.03, H * 0.30, W * 0.045, H * 0.74, (96, 102, 116))                                               # stop sign pole
    pen.circle(W * 0.0375, H * 0.27, H * 0.045, (70, 150, 220), outline=SOFT_INK, width=4)
    pen.circle(W * 0.0375, H * 0.27, H * 0.022, (255, 255, 255))
    pen.rect(W * 0.47, H * 0.20, W * 0.482, H * 0.74, (86, 90, 104))                                                  # street lamp
    pen.circle(W * 0.476, H * 0.19, H * 0.026, (255, 236, 170), outline=SOFT_INK, width=3)
    pen.rect(0, H * 0.74, W, H, (150, 150, 162))
    pen.rect(0, H * 0.74, W, H * 0.77, (200, 196, 190))
    pen.line([(0, H * 0.74), (W, H * 0.74)], SOFT_INK, 4)
    for xx in range(0, W, int(W * 0.14)):
        pen.rect(xx + 20, H * 0.90, xx + 20 + W * 0.07, H * 0.915, (236, 230, 200))
    return add_glow(pen.result().convert("RGB"), int(W * 0.476), int(H * 0.19), int(H * 0.3), (255, 226, 160), 0.4)


def fx_train_view(img, t, dur, W, H, speed=1.0, windows=None):
    """Scenery sliding past the train windows: far skyline (slow), nearer buildings, then poles (fast)."""
    d = ImageDraw.Draw(img)
    for x0, y0, x1, y1 in (windows or TRAIN_WINDOWS):
        bx0, by0, bx1, by1 = int(W * x0), int(H * y0), int(W * x1), int(H * y1)
        for y in range(by0, by1, 4):
            u = (y - by0) / (by1 - by0)
            d.rectangle((bx0, y, bx1, y + 4), fill=tuple(int(a + (b - a) * u) for a, b in zip((150, 190, 226), (210, 226, 238))))
        span = int(W * 0.9)
        for layer, (sp, col, base_h, bw) in enumerate(((60, (170, 184, 208), 0.18, 70), (200, (130, 150, 182), 0.28, 110))):
            off = (t * sp * speed) % span
            for k in range(14):
                x = bx0 + ((k * (bw + 24) - off) % span) - 40
                hgt = (by1 - by0) * (base_h + 0.22 * ((k * 37 + layer * 11) % 7) / 7)
                if bx0 - bw < x < bx1:
                    d.rectangle((max(bx0, x), by1 - hgt, min(bx1, x + bw), by1), fill=col)
        off = (t * 760 * speed) % 420
        for x in range(bx0 - 420, bx1 + 420, 420):
            px = x + 420 - off
            if bx0 <= px <= bx1:
                d.rectangle((px - 7, by0, px + 7, by1), fill=(96, 98, 110))
        d.rectangle((bx0, by1 - 14, bx1, by1), fill=(150, 156, 170))
    return img


def fx_tunnel_view(img, t, dur, W, H, speed=1.0, windows=None):
    """Dark tunnel with lamps streaking past, and a lit platform flash now and then."""
    d = ImageDraw.Draw(img)
    for x0, y0, x1, y1 in (windows or TRAIN_WINDOWS):
        bx0, by0, bx1, by1 = int(W * x0), int(H * y0), int(W * x1), int(H * y1)
        d.rectangle((bx0, by0, bx1, by1), fill=(26, 30, 48))
        off = (t * 900 * speed) % 360
        for x in range(bx0 - 360, bx1 + 360, 360):
            px = x + 360 - off
            for dx in (0, -40, -80):
                if bx0 <= px + dx <= bx1:
                    d.line([(px + dx, (by0 + by1) / 2 - 8), (px + dx, (by0 + by1) / 2 + 8)], fill=(255, 236, 170), width=6)
        flash = max(0.0, math.sin(t * 0.55 + 1.3)) ** 14
        if flash > 0.05:
            d.rectangle((bx0, by1 - 70, bx1, by1), fill=tuple(int(a + (b - a) * flash) for a, b in zip((26, 30, 48), (230, 226, 200))))
    return img


def wholesale(W, H):
    """A big wholesale aisle: tall shelves of cartons and bulk packs, ceiling lights."""
    rnd = random.Random(9)
    pen = Pen(W, H, base=vgradient(W, H, [(0, (232, 232, 240)), (1, (214, 210, 206))]))
    for k in range(6):
        pen.rect(W * (0.07 + k * 0.17), H * 0.02, W * (0.07 + k * 0.17) + W * 0.10, H * 0.045, (255, 250, 220))
    for row in range(3):
        y1 = H * (0.30 + row * 0.19)
        pen.rect(0, y1 - H * 0.17, W, y1, (86, 122, 170), outline=SOFT_INK, width=4)
        x = 8
        while x < W:
            bw, bh = rnd.uniform(W * 0.035, W * 0.075), rnd.uniform(H * 0.07, H * 0.15)
            col = rnd.choice([(196, 150, 100), (210, 170, 120), (226, 90, 80), (246, 200, 80), (120, 180, 110), (240, 240, 240)])
            pen.rect(x, y1 - bh, x + bw, y1 - 4, col, outline=SOFT_INK, width=3, radius=6)
            x += bw + 6
    pen.rect(0, H * 0.80, W, H, (200, 196, 190))
    pen.line([(0, H * 0.80), (W, H * 0.80)], SOFT_INK, 4)
    for k in range(1, 10):
        pen.line([(W / 2 + (W * k / 10 - W / 2) * 0.6, H * 0.80), (W * k / 10, H)], (186, 182, 176), 3)
    return add_glow(pen.result().convert("RGB"), int(W * 0.5), int(H * 0.15), int(H * 0.7), (255, 252, 236), 0.28)


def kitchen(W, H):
    """A small home kitchen: tiled wall, upper cabinet, window, counter with a gas stove."""
    pen = Pen(W, H, base=vgradient(W, H, [(0, (250, 240, 222)), (1, (240, 226, 204))]))
    for r in range(8):
        for c in range(16):
            pen.rect(c * W / 16 + 2, H * 0.30 + r * H * 0.04, (c + 1) * W / 16 - 2, H * 0.30 + (r + 1) * H * 0.04 - 2,
                     (255, 252, 244) if (r + c) % 2 else (246, 240, 228), radius=3)
    pen.rect(W * 0.04, H * 0.04, W * 0.40, H * 0.26, (206, 150, 108), outline=SOFT_INK, width=5, radius=8)
    for x in (0.04, 0.22):
        pen.rect(W * x + 8, H * 0.06, W * (x + 0.16) - 4, H * 0.24, (222, 170, 126), outline=SOFT_INK, width=3, radius=6)
    pen.rect(W * 0.58, H * 0.08, W * 0.92, H * 0.34, (250, 248, 242), outline=SOFT_INK, width=5)
    pen.rect(W * 0.59, H * 0.10, W * 0.91, H * 0.32, (186, 218, 238))
    pen.rect(0, H * 0.58, W, H * 0.80, (190, 150, 116), outline=SOFT_INK, width=5)
    pen.rect(0, H * 0.56, W, H * 0.60, (232, 226, 216), outline=SOFT_INK, width=4)
    pen.rect(W * 0.52, H * 0.50, W * 0.80, H * 0.56, (74, 74, 84), outline=SOFT_INK, width=4, radius=8)
    for x in (0.58, 0.74):
        pen.circle(W * x, H * 0.53, H * 0.016, (200, 200, 210))
    pen.rect(0, H * 0.80, W, H, (214, 190, 156))
    pen.line([(0, H * 0.80), (W, H * 0.80)], SOFT_INK, 4)
    return add_glow(pen.result().convert("RGB"), int(W * 0.75), int(H * 0.2), int(H * 0.5), (255, 248, 226), 0.3)


def street_stall(W, H):
    """A street-food corner: shopfronts behind, a grill stall with skewers and a sticky-rice basket, striped awning."""
    pen = Pen(W, H, base=vgradient(W, H, [(0, (178, 208, 234)), (0.5, (236, 226, 204)), (1, (220, 200, 172))]))
    x = -20
    rnd = random.Random(31)
    while x < W:
        bw = rnd.uniform(W * 0.10, W * 0.16)
        pen.rect(x, H * 0.18, x + bw, H * 0.74, rnd.choice([(232, 206, 168), (214, 190, 196), (194, 208, 190), (234, 222, 164)]),
                 outline=SOFT_INK, width=4)
        for wx in range(3):
            pen.rect(x + bw * 0.12 + wx * bw * 0.28, H * 0.26, x + bw * 0.32 + wx * bw * 0.28, H * 0.36, (178, 208, 232))
        x += bw
    pen.poly([(W * 0.40, H * 0.30), (W * 0.98, H * 0.30), (W * 1.0, H * 0.42), (W * 0.38, H * 0.42)], (230, 110, 96),
             outline=SOFT_INK, width=5)
    for k in range(8):
        pen.rect(W * (0.40 + k * 0.075), H * 0.31, W * (0.40 + k * 0.075) + W * 0.0375, H * 0.41, (252, 244, 232))
    pen.rect(W * 0.42, H * 0.52, W * 0.96, H * 0.74, (150, 108, 76), outline=SOFT_INK, width=5, radius=10)
    pen.rect(W * 0.44, H * 0.47, W * 0.72, H * 0.54, (60, 56, 60), outline=SOFT_INK, width=4, radius=8)
    pen.rect(W * 0.46, H * 0.485, W * 0.70, H * 0.51, (236, 96, 40))
    for k in range(7):
        sx = W * (0.465 + k * 0.034)
        pen.line([(sx, H * 0.40), (sx + 14, H * 0.50)], (176, 140, 96), 5)
        for j in range(3):
            pen.circle(sx + 3 + j * 4, H * (0.43 + j * 0.022), H * 0.014, (212, 112, 96), outline=SOFT_INK, width=2)
    pen.rect(W * 0.78, H * 0.44, W * 0.90, H * 0.54, (236, 200, 120), outline=SOFT_INK, width=4, radius=18)
    pen.ellipse(W * 0.84, H * 0.44, W * 0.06, H * 0.02, (250, 246, 236), outline=SOFT_INK, width=3)
    pen.rect(0, H * 0.74, W, H, (190, 186, 182))
    pen.line([(0, H * 0.74), (W, H * 0.74)], SOFT_INK, 4)
    return add_glow(pen.result().convert("RGB"), int(W * 0.58), int(H * 0.48), int(H * 0.4), (255, 190, 110), 0.25)


def cafe(W, H):
    """A coffee shop counter: menu board, espresso machine, pastry case, round window."""
    pen = Pen(W, H, base=vgradient(W, H, [(0, (244, 228, 208)), (1, (230, 208, 180))]))
    pen.rect(W * 0.06, H * 0.08, W * 0.46, H * 0.34, (60, 52, 56), outline=SOFT_INK, width=6, radius=10)
    for r in range(5):
        pen.line([(W * 0.10, H * (0.13 + r * 0.045)), (W * (0.26 + 0.05 * (r % 3)), H * (0.13 + r * 0.045))], (236, 230, 216), 6)
        pen.line([(W * 0.36, H * (0.13 + r * 0.045)), (W * 0.42, H * (0.13 + r * 0.045))], (236, 190, 110), 6)
    pen.circle(W * 0.78, H * 0.22, H * 0.15, (250, 246, 238), outline=SOFT_INK, width=6)
    pen.circle(W * 0.78, H * 0.22, H * 0.125, (184, 214, 236))
    pen.rect(0, H * 0.56, W, H * 0.80, (150, 106, 76), outline=SOFT_INK, width=5)
    pen.rect(0, H * 0.54, W, H * 0.58, (232, 214, 190), outline=SOFT_INK, width=4)
    pen.rect(W * 0.60, H * 0.40, W * 0.84, H * 0.54, (170, 176, 186), outline=SOFT_INK, width=5, radius=10)
    pen.rect(W * 0.64, H * 0.44, W * 0.80, H * 0.48, (60, 62, 70))
    pen.rect(W * 0.12, H * 0.43, W * 0.40, H * 0.54, (236, 244, 248), outline=SOFT_INK, width=5, radius=10)
    for k in range(4):
        pen.ellipse(W * (0.16 + k * 0.065), H * 0.50, W * 0.024, H * 0.022, (232, 176, 110), outline=SOFT_INK, width=2)
    pen.rect(0, H * 0.80, W, H, (198, 170, 138))
    pen.line([(0, H * 0.80), (W, H * 0.80)], SOFT_INK, 4)
    return add_glow(pen.result().convert("RGB"), int(W * 0.5), int(H * 0.3), int(H * 0.5), (255, 232, 190), 0.28)


B.register("train_car", train_car)
B.register("bus_car", lambda W, H: train_car(W, H, bus=True))
B.register("bus_stop_dawn", bus_stop_dawn)
B.register("mrt_car", lambda W, H: train_car(W, H, tunnel=True))
B.register("wholesale", wholesale)
B.register("kitchen", kitchen)
B.register("street_stall", street_stall)
B.register("cafe", cafe)
B.FX.update({"train_view": fx_train_view, "tunnel_view": fx_tunnel_view})
