"""Backgrounds + animated effects for the flood comedy Short (reusable in later episodes).

Stores are drawn as generic shops (no real brand names, logos or colour schemes) so the cartoon is
never mistaken for real footage of a real store.
"""

from __future__ import annotations

import math
import random

from PIL import Image, ImageDraw

import backgrounds as B
from art import INK, Pen, add_glow, vgradient

WATER = (86, 150, 186)


def _house(pen, cx, base, s, wall=(246, 230, 200), roof=(176, 84, 70)):
    w, h = 520 * s, 300 * s
    x0 = cx - w / 2
    pen.rect(x0 - 20 * s, base - 40 * s, x0 + w + 20 * s, base, (196, 186, 170), outline=INK, width=4)    # raised base
    pen.rect(x0, base - 40 * s - h, x0 + w, base - 40 * s, wall, outline=INK, width=5)
    pen.poly([(x0 - 50 * s, base - 40 * s - h), (cx, base - 40 * s - h - 190 * s), (x0 + w + 50 * s, base - 40 * s - h)],
             roof, outline=INK, width=5)
    for wx in (x0 + 60 * s, x0 + w - 170 * s):
        pen.rect(wx, base - 40 * s - h + 70 * s, wx + 110 * s, base - 40 * s - h + 170 * s, (170, 210, 230), outline=INK, width=4)
        pen.line([(wx + 55 * s, base - 40 * s - h + 70 * s), (wx + 55 * s, base - 40 * s - h + 170 * s)], INK, 3)
    pen.rect(cx - 55 * s, base - 40 * s - 190 * s, cx + 55 * s, base - 40 * s, (150, 100, 70), outline=INK, width=4)
    pen.circle(cx + 35 * s, base - 40 * s - 95 * s, 7 * s, (236, 196, 90))


def _clouds(pen, W, H, rnd, n=5, col=(250, 250, 252)):
    for _ in range(n):
        x, y, r = rnd.uniform(0, W), rnd.uniform(0.05 * H, 0.2 * H), rnd.uniform(50, 90)
        for dx, dr in ((-r, 0.7), (0, 1.0), (r, 0.75)):
            pen.circle(x + dx, y, r * dr, col)


def flood_yard(W, H):
    rnd = random.Random(2)
    pen = Pen(W, H, base=vgradient(W, H, [(0, (150, 176, 206)), (0.35, (206, 222, 236)), (1, (206, 222, 236))]))
    _clouds(pen, W, H, rnd, 6, (236, 240, 246))
    pen.rect(0, 0.50 * H, W, H, (118, 176, 96))                                    # lawn
    for _ in range(140):
        x, y = rnd.uniform(0, W), rnd.uniform(0.52 * H, H)
        pen.line([(x, y), (x + 4, y - 16)], (96, 152, 80), 3)
    for x in (0.1 * W, 0.9 * W):
        pen.line([(x, 0.52 * H), (x, 0.34 * H)], (120, 90, 66), 22)
        pen.circle(x, 0.31 * H, 90, (96, 150, 92), outline=INK, width=4)
    _house(pen, W / 2, 0.56 * H, W / 1080 * 1.2)
    for x in range(0, W + 1, 60):                                                    # front fence
        pen.rect(x, 0.70 * H, x + 18, 0.78 * H, (240, 236, 226), outline=INK, width=3)
    pen.rect(0, 0.72 * H, W, 0.735 * H, (240, 236, 226), outline=INK, width=3)
    return pen.result().convert("RGB")


def living_room(W, H, night=False):
    wall = (238, 222, 196) if not night else (150, 136, 150)
    pen = Pen(W, H, base=vgradient(W, H, [(0, wall), (0.6, B.shade(wall, 0.94)), (1, B.shade(wall, 0.9))]))
    floor_y = 0.58 * H
    pen.rect(0, floor_y, W, H, (190, 142, 100) if not night else (120, 90, 80))
    for y in range(int(floor_y), H, 70):
        pen.line([(0, y), (W, y)], (160, 116, 80) if not night else (96, 72, 64), 3)
    # window to the flooded yard (right)
    wx0, wy0, wx1, wy1 = 0.52 * W, 0.14 * H, 0.94 * W, 0.42 * H
    pen.rect(wx0 - 14, wy0 - 14, wx1 + 14, wy1 + 14, (250, 248, 240), outline=INK, width=5)
    sky = (170, 196, 220) if not night else (58, 66, 104)
    pen.rect(wx0, wy0, wx1, wy1, sky)
    pen.rect(wx0, wy0 + (wy1 - wy0) * 0.55, wx1, wy1, WATER if not night else (52, 84, 116))
    for k in range(6):
        x = wx0 + 20 + k * (wx1 - wx0) / 6
        pen.rect(x, wy0 + (wy1 - wy0) * 0.45, x + 12, wy0 + (wy1 - wy0) * 0.62, (240, 236, 226))
    pen.line([((wx0 + wx1) / 2, wy0), ((wx0 + wx1) / 2, wy1)], INK, 6)
    # front door (left), half open, water outside
    dx0, dy0, dx1 = 0.06 * W, 0.20 * H, 0.32 * W
    pen.rect(dx0 - 12, dy0 - 12, dx1 + 12, floor_y, (250, 248, 240), outline=INK, width=5)
    pen.rect(dx0, dy0, dx1, floor_y, WATER if not night else (52, 84, 116))
    pen.rect(dx0, dy0, dx1, dy0 + (floor_y - dy0) * 0.45, sky)
    pen.poly([(dx0, dy0), (dx0 + 70, dy0 + 30), (dx0 + 70, floor_y + 20), (dx0, floor_y)], (150, 100, 70), outline=INK, width=4)
    # sofa, picture, plant
    pen.rect(0.36 * W, 0.44 * H, 0.98 * W, 0.58 * H, (110, 140, 160), radius=30, outline=INK, width=5)
    pen.rect(0.38 * W, 0.40 * H, 0.96 * W, 0.47 * H, (126, 158, 178), radius=26, outline=INK, width=5)
    pen.rect(0.38 * W, 0.04 * H, 0.48 * W, 0.11 * H, (250, 240, 214), outline=INK, width=4)
    pen.circle(0.43 * W, 0.075 * H, 26, (127, 176, 105))
    img = pen.result().convert("RGB")
    if night:
        img = add_glow(img, 0.7 * W, 0.08 * H, 0.45 * W, (255, 226, 160), 0.35)
    return img


def _store_shelves(pen, W, H, y0, y1, stock, rnd, colors):
    cols = 4
    sw = W / cols
    for c in range(cols):
        x0 = c * sw + 14
        pen.rect(x0, y0, x0 + sw - 28, y1, (220, 216, 210), outline=INK, width=4)
        rows = 5
        for r in range(rows):
            sy = y0 + (y1 - y0) * (r + 1) / (rows + 0.3)
            pen.rect(x0, sy, x0 + sw - 28, sy + 10, (170, 166, 160))
            n = int(stock * 5)
            for k in range(n):
                if rnd.random() < stock:
                    bx = x0 + 10 + k * (sw - 48) / max(1, n)
                    pen.rect(bx, sy - 64, bx + (sw - 60) / max(1, n) - 6, sy, rnd.choice(colors), outline=INK, width=2)


def wholesale_store(W, H):
    rnd = random.Random(8)
    pen = Pen(W, H, base=vgradient(W, H, [(0, (210, 214, 222)), (0.6, (226, 228, 232)), (1, (200, 202, 206))]))
    for x in range(80, W, 240):                                                       # ceiling lights
        pen.rect(x, 0.03 * H, x + 150, 0.045 * H, (255, 252, 230))
    pen.rect(0.2 * W, 0.07 * H, 0.8 * W, 0.12 * H, (64, 104, 170), radius=12, outline=INK, width=4)
    B.subtitles_text(pen, W / 2, 0.095 * H, "โซนอาหารแห้ง", 54, (255, 255, 255))
    _store_shelves(pen, W, H, 0.16 * H, 0.58 * H, 0.55, rnd,
                   [(236, 196, 80), (226, 96, 80), (236, 236, 236), (120, 170, 220), (240, 150, 70)])
    pen.rect(0, 0.58 * H, W, H, (178, 182, 188))
    for x in range(0, W, 140):
        pen.line([(x, 0.58 * H), (x - 200, H)], (160, 164, 170), 3)
    for x, s in ((0.85 * W, 0.6),):                                                  # a cart in the back
        pen.rect(x - 90 * s, 0.50 * H, x + 90 * s, 0.56 * H, (200, 204, 210), outline=INK, width=4)
    return pen.result().convert("RGB")


def convenience_store(W, H):
    rnd = random.Random(9)
    pen = Pen(W, H, base=vgradient(W, H, [(0, (236, 242, 244)), (1, (222, 230, 232))]))
    for x in range(60, W, 260):
        pen.rect(x, 0.025 * H, x + 180, 0.04 * H, (255, 255, 246))
    pen.rect(0.06 * W, 0.08 * H, 0.94 * W, 0.13 * H, (63, 167, 154), radius=10, outline=INK, width=4)
    B.subtitles_text(pen, W / 2, 0.105 * H, "ร้านสะดวกซื้อ", 52, (255, 255, 255))
    _store_shelves(pen, W, H, 0.17 * H, 0.58 * H, 0.08, rnd, [(236, 236, 236), (240, 200, 90)])  # nearly empty
    pen.rect(0, 0.58 * H, W, H, (214, 220, 222))
    for x in range(0, W, 120):
        pen.line([(x, 0.58 * H), (x, H)], (196, 204, 206), 3)
    return pen.result().convert("RGB")


def flooded_street(W, H):
    rnd = random.Random(4)
    pen = Pen(W, H, base=vgradient(W, H, [(0, (170, 196, 222)), (0.4, (214, 228, 238)), (1, (214, 228, 238))]))
    _clouds(pen, W, H, rnd, 4)
    colors = [(244, 214, 170), (226, 196, 206), (206, 226, 210), (250, 232, 190)]
    for i, x in enumerate(range(-40, W, 260)):                                         # row of houses across the soi
        top = 0.20 * H + (i % 2) * 40
        pen.rect(x, top, x + 240, 0.50 * H, colors[i % 4], outline=INK, width=4)
        pen.poly([(x - 20, top), (x + 120, top - 90), (x + 260, top)], (170, 96, 80), outline=INK, width=4)
        pen.rect(x + 70, top + 70, x + 170, top + 150, (170, 210, 230), outline=INK, width=3)
    pen.rect(0, 0.46 * H, W, H, WATER)                                                  # the soi is a canal now
    for _ in range(60):
        x, y = rnd.uniform(0, W), rnd.uniform(0.48 * H, H)
        pen.line([(x, y), (x + rnd.uniform(30, 90), y)], (150, 196, 220), 3)
    # porch on the right where the homeowner leans out
    pen.rect(0.56 * W, 0.40 * H, W, 0.68 * H, (246, 230, 200), outline=INK, width=5)
    pen.rect(0.56 * W, 0.66 * H, W, 0.70 * H, (196, 186, 170), outline=INK, width=4)
    pen.rect(0.62 * W, 0.44 * H, 0.94 * W, 0.62 * H, (150, 100, 70), outline=INK, width=4)    # doorway
    return pen.result().convert("RGB")


# --- per-frame effects -------------------------------------------------------------------------

def fx_flood_rise(img, t, dur, W, H, frm=0.92, to=0.60, rise=(0.25, 0.75)):
    """Water level eases from `frm` to `to` (fractions of H) between rise[0]..rise[1] of the scene."""
    u = min(1.0, max(0.0, (t / dur - rise[0]) / (rise[1] - rise[0])))
    u = u * u * (3 - 2 * u)
    level = (frm + (to - frm) * u) * H
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    pts = [(x, level + 10 * math.sin(x / 70 + t * 3)) for x in range(0, W + 30, 30)]
    d.polygon(pts + [(W, H), (0, H)], fill=(*WATER, 215))
    for k in range(10):
        y = level + 30 + k * (H - level) / 10
        off = (t * 60 + k * 90) % 200
        for x in range(-200, W, 200):
            d.line([(x + off, y), (x + off + 70, y)], fill=(190, 226, 240, 160), width=4)
    out = img.convert("RGBA")
    out.alpha_composite(layer)
    return out.convert("RGB")


def fx_shimmer(img, t, dur, W, H, top=0.46):
    d = ImageDraw.Draw(img)
    for k in range(8):
        y = top * H + 40 + k * (H * (1 - top) - 40) / 8
        off = (t * 50 + k * 70) % 220
        for x in range(-220, W, 220):
            d.line([(x + off, y), (x + off + 60, y)], fill=(196, 230, 244), width=3)
    return img


def fx_rain(img, t, dur, W, H, density=90):
    d = ImageDraw.Draw(img)
    rnd = random.Random(int(t * 30))
    for _ in range(density):
        x, y = rnd.uniform(0, W), rnd.uniform(0, H * 0.7)
        d.line([(x, y), (x - 10, y + 40)], fill=(220, 232, 244), width=3)
    return img


B.register("flood_yard", flood_yard)
B.register("living_room", living_room)
B.register("living_room_night", lambda W, H: living_room(W, H, night=True))
B.register("wholesale_store", wholesale_store)
B.register("convenience_store", convenience_store)
B.register("flooded_street", flooded_street)
B.FX.update({"flood_rise": fx_flood_rise, "shimmer": fx_shimmer, "rain": fx_rain})
