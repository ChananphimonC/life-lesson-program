"""More animated props for the city-life episodes: detailed food and grocery icons, an arriving city bus, a subscribe
button with a swinging bell, rising hearts. Same soft warm outline as everything else; `draw(img, item, t, W, H)`.
"""

from __future__ import annotations

import math
from functools import lru_cache

from PIL import Image, ImageDraw

import props_story
from subtitles import font

INK = (118, 88, 72)
KINDS = {"bus", "subscribe", "hearts", "item"}


def _env(t, at, dur, fade=0.25):
    lt = t - at
    if lt < 0 or lt > dur:
        return 0.0, 0.0
    a = min(1.0, lt / fade, (dur - lt) / fade)
    x = min(1.0, lt / 0.35)
    s = 1 + 2.70158 * (x - 1) ** 3 + 1.70158 * (x - 1) ** 2
    return max(0.0, a), s


def _paste(img, spr, cx, cy, alpha=1.0, scale=1.0, angle=0.0):
    if alpha <= 0 or scale <= 0.02:
        return
    if abs(angle) > 0.05:
        spr = spr.rotate(angle, resample=Image.BICUBIC, expand=True)
    if abs(scale - 1) > 0.01:
        spr = spr.resize((max(1, int(spr.width * scale)), max(1, int(spr.height * scale))), Image.LANCZOS)
    if alpha < 1:
        spr = spr.copy()
        spr.putalpha(spr.getchannel("A").point(lambda v: int(v * alpha)))
    img.paste(spr, (int(cx - spr.width / 2), int(cy - spr.height / 2)), spr)


def _mix(a, b, t):
    return tuple(int(x + (y - x) * t) for x, y in zip(a, b))


def _canvas(s, scale=3):
    big = Image.new("RGBA", (s * scale, s * scale), (0, 0, 0, 0))
    return big, ImageDraw.Draw(big), scale


def _done(big, s):
    return big.resize((s, s), Image.LANCZOS)


# --- food and grocery icons (drawn 3x then reduced for smooth edges) ------------------------------------------------

@lru_cache(maxsize=None)
def food_sprite(kind, H):
    s = int(H * 0.2)
    big, d, k = _canvas(s)
    u = s * k / 100.0                       # work in a 100x100 box

    def P(*pts):
        return [(x * u, y * u) for x, y in pts]

    def ell(x0, y0, x1, y1, fill, w=1.3):
        d.ellipse((x0 * u, y0 * u, x1 * u, y1 * u), fill=fill, outline=INK, width=max(2, int(w * u / 2)))

    def rr(x0, y0, x1, y1, r, fill, w=1.3):
        d.rounded_rectangle((x0 * u, y0 * u, x1 * u, y1 * u), r * u, fill=fill, outline=INK, width=max(2, int(w * u / 2)))

    def ln(pts, col, w=2):
        d.line(P(*pts), fill=col, width=max(2, int(w * u / 2)), joint="curve")

    if kind == "skewers":            # grilled pork skewers: glazed cubes with char marks, on bamboo sticks
        for j, (x0, rot) in enumerate(((22, -8), (46, -4), (70, 0))):
            ln([(x0 - 6, 98), (x0 + 12, 6)], (190, 150, 100), 3.4)
            for i in range(4):
                cx, cy = x0 + 6 - i * 2.2 + rot * 0.1, 24 + i * 17
                rr(cx - 11, cy - 8, cx + 11, cy + 8, 4, _mix((196, 98, 70), (150, 70, 50), (i % 2) * 0.5))
                ln([(cx - 7, cy - 3), (cx + 2, cy - 5)], (255, 190, 150), 2)       # glaze highlight
                ln([(cx - 5, cy + 3), (cx + 6, cy + 4)], (92, 48, 38), 2)           # char mark
    elif kind == "sticky":           # a woven bamboo sticky-rice basket with a lid and a little spilled rice
        rr(14, 46, 86, 94, 12, (214, 168, 98))
        for x in range(20, 86, 9):
            ln([(x, 48), (x - 6, 92)], (170, 126, 70), 2)
        for y in range(54, 92, 10):
            ln([(16, y), (84, y)], (170, 126, 70), 2)
        d.pieslice((10 * u, 14 * u, 90 * u, 78 * u), 180, 360, fill=(226, 184, 112), outline=INK, width=max(2, int(0.65 * u)))
        for y in (30, 42):
            ln([(20, y), (80, y)], (176, 134, 76), 2)
        ell(40, 8, 60, 22, (176, 134, 76))
        for x, y in ((24, 96), (30, 98), (36, 96), (42, 99)):
            ell(x, y - 3, x + 6, y + 2, (252, 250, 240), 0.8)
    elif kind == "coffee":           # iced coffee: dome lid, straw, ice, milk layer over coffee
        d.polygon(P((26, 28), (74, 28), (68, 94), (32, 94)), fill=(214, 226, 238, 235))
        d.polygon(P((28, 52), (72, 52), (68, 94), (32, 94)), fill=(122, 78, 52))
        d.polygon(P((27, 40), (73, 40), (71, 56), (29, 56)), fill=(226, 190, 150))
        for x, y in ((38, 62), (54, 70), (46, 82)):
            rr(x - 6, y - 6, x + 6, y + 6, 2, (230, 240, 248, 190), 0.8)
        d.line(P((26, 28), (32, 94), (68, 94), (74, 28), (26, 28)), fill=INK, width=int(1.4 * u), joint="curve")
        d.pieslice((24 * u, 8 * u, 76 * u, 48 * u), 180, 360, fill=(246, 246, 250, 235), outline=INK, width=int(1.1 * u))
        rr(22, 26, 78, 33, 3, (250, 250, 252))
        ln([(52, 26), (62, -4)], (80, 168, 100), 4)
    elif kind == "rice":             # rice with a sunny-side-up egg and cucumber
        ell(6, 52, 94, 96, (252, 252, 254))
        ell(14, 58, 86, 90, (240, 240, 244), 0.8)
        d.pieslice((22 * u, 22 * u, 78 * u, 82 * u), 180, 360, fill=(255, 253, 244), outline=INK, width=int(1.1 * u))
        for x, y in ((38, 44), (50, 38), (60, 48), (46, 52)):
            ln([(x, y), (x + 4, y + 1)], (214, 206, 190), 2)
        ell(46, 50, 82, 78, (255, 255, 252))
        ell(56, 55, 72, 69, (248, 188, 60))
        ln([(60, 58), (64, 57)], (255, 236, 160), 2)
        for x in (14, 24, 34):
            ell(x, 68, x + 9, 80, (130, 190, 110), 0.9)
    elif kind == "bag":              # takeaway paper bag
        d.polygon(P((20, 28), (80, 28), (86, 94), (14, 94)), fill=(250, 214, 140))
        d.line(P((20, 28), (80, 28), (86, 94), (14, 94), (20, 28)), fill=INK, width=int(1.4 * u), joint="curve")
        d.arc((30 * u, 6 * u, 70 * u, 52 * u), 180, 360, fill=INK, width=int(1.4 * u))
        ln([(30, 52), (70, 52)], (214, 170, 100), 2)
    big_img = _done(big, s)
    return big_img


@lru_cache(maxsize=None)
def item_sprite(kind, H):
    """Grocery items for the wholesale-store scene."""
    s = int(H * 0.17)
    big, d, k = _canvas(s)
    u = s * k / 100.0

    def P(*pts):
        return [(x * u, y * u) for x, y in pts]

    def ell(x0, y0, x1, y1, fill, w=1.2):
        d.ellipse((x0 * u, y0 * u, x1 * u, y1 * u), fill=fill, outline=INK, width=max(2, int(w * u / 2)))

    def rr(x0, y0, x1, y1, r, fill, w=1.2):
        d.rounded_rectangle((x0 * u, y0 * u, x1 * u, y1 * u), r * u, fill=fill, outline=INK, width=max(2, int(w * u / 2)))

    def ln(pts, col, w=2):
        d.line(P(*pts), fill=col, width=max(2, int(w * u / 2)), joint="curve")

    if kind == "eggs":               # a tray of eggs
        rr(8, 50, 92, 90, 8, (190, 196, 206))
        for r in range(2):
            for c in range(5):
                ell(14 + c * 15.5, 36 + r * 22, 28 + c * 15.5, 62 + r * 22, (246, 226, 190), 1.0)
        ln([(14, 90), (86, 90)], (150, 156, 168), 2)
    elif kind == "rice":             # a sack of rice with a stripe label
        d.polygon(P((24, 22), (76, 22), (84, 92), (16, 92)), fill=(240, 232, 212))
        d.line(P((24, 22), (76, 22), (84, 92), (16, 92), (24, 22)), fill=INK, width=int(1.3 * u), joint="curve")
        rr(24, 50, 76, 74, 4, (214, 90, 80))
        ln([(32, 62), (68, 62)], (255, 240, 220), 3)
        ln([(30, 22), (40, 12), (50, 22), (60, 12), (70, 22)], INK, 2)
    elif kind == "veg":              # leafy greens and a carrot
        for x, a in ((34, -20), (50, 0), (66, 20)):
            d.polygon(P((x, 90), (x - 14 + a * 0.4, 38), (x, 12), (x + 14 + a * 0.4, 38)), fill=(110, 178, 96), outline=INK)
            ln([(x, 88), (x + a * 0.2, 20)], (70, 130, 64), 2)
        d.polygon(P((70, 90), (96, 50), (86, 44), (62, 86)), fill=(238, 140, 60), outline=INK)
        ln([(78, 70), (86, 64)], (200, 100, 40), 2)
    elif kind == "pork":             # packed pork tray under cling film
        rr(8, 40, 92, 86, 8, (250, 250, 252))
        rr(14, 46, 86, 80, 10, (232, 130, 130))
        for x, y in ((28, 58), (48, 66), (66, 56)):
            ell(x - 10, y - 6, x + 10, y + 8, (246, 168, 160), 0.8)
        ln([(14, 44), (86, 76)], (255, 255, 255, 150), 3)
    elif kind == "box":              # a lunch box with a lid and food inside
        rr(10, 44, 90, 90, 8, (96, 172, 214))
        rr(10, 36, 90, 52, 5, (126, 196, 234))
        ell(22, 58, 46, 82, (252, 252, 254), 1.0)
        ell(54, 58, 78, 82, (236, 170, 100), 1.0)
        ln([(54, 66), (74, 74)], (160, 100, 50), 2)
    big_img = _done(big, s)
    return big_img


# --- the arriving bus ------------------------------------------------------------------------------------------------

@lru_cache(maxsize=None)
def bus_sprite(H):
    w, h = int(H * 0.95), int(H * 0.40)
    k = 2
    big = Image.new("RGBA", (w * k, h * k), (0, 0, 0, 0))
    d = ImageDraw.Draw(big)
    W2, H2 = w * k, h * k

    def rr(x0, y0, x1, y1, r, fill, wd=4):
        d.rounded_rectangle((x0 * W2, y0 * H2, x1 * W2, y1 * H2), r * H2, fill=fill, outline=INK, width=wd * k)

    rr(0.02, 0.06, 0.98, 0.84, 0.12, (244, 138, 52))                       # body
    rr(0.02, 0.60, 0.98, 0.84, 0.08, (252, 246, 232))                       # cream skirt
    rr(0.06, 0.16, 0.30, 0.50, 0.05, (196, 226, 244))                       # windows
    rr(0.33, 0.16, 0.57, 0.50, 0.05, (196, 226, 244))
    rr(0.60, 0.16, 0.76, 0.50, 0.05, (196, 226, 244))
    rr(0.79, 0.12, 0.96, 0.58, 0.05, (196, 226, 244))                       # front windscreen
    d.line([(0.78 * W2, 0.12 * H2), (0.78 * W2, 0.84 * H2)], fill=INK, width=4 * k)
    rr(0.60, 0.50, 0.76, 0.84, 0.03, (214, 232, 246))                       # door
    rr(0.40, 0.02, 0.60, 0.11, 0.03, (60, 56, 64))                          # blank route board
    for cx in (0.22, 0.80):
        d.ellipse(((cx - 0.075) * W2, 0.68 * H2, (cx + 0.075) * W2, 0.98 * H2), fill=(66, 64, 74), outline=INK, width=4 * k)
        d.ellipse(((cx - 0.03) * W2, 0.78 * H2, (cx + 0.03) * W2, 0.88 * H2), fill=(190, 192, 202))
    d.ellipse((0.95 * W2, 0.62 * H2, 0.99 * W2, 0.70 * H2), fill=(255, 238, 150), outline=INK, width=3 * k)
    return big.resize((w, h), Image.LANCZOS)


@lru_cache(maxsize=None)
def subscribe_sprite(H):
    w, h = int(H * 0.46), int(H * 0.16)
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((4, 4, w - 4, h - 4), int(h * 0.3), fill=(236, 70, 70), outline=INK, width=5)
    d.text((w * 0.62, h / 2 + 2), "ติดตาม", font=font(int(h * 0.5)), fill=(255, 255, 255), anchor="mm", stroke_width=3, stroke_fill=(150, 40, 40))
    return img


@lru_cache(maxsize=None)
def bell_sprite(H):
    s = int(H * 0.16)
    k = 3
    big = Image.new("RGBA", (s * k, s * k), (0, 0, 0, 0))
    d = ImageDraw.Draw(big)
    u = s * k / 100.0
    d.pieslice((22 * u, 14 * u, 78 * u, 70 * u), 180, 360, fill=(255, 208, 70), outline=INK, width=int(2.2 * u))
    d.polygon([(22 * u, 42 * u), (78 * u, 42 * u), (88 * u, 72 * u), (12 * u, 72 * u)], fill=(255, 208, 70), outline=INK)
    d.line([(22 * u, 42 * u), (12 * u, 72 * u), (88 * u, 72 * u), (78 * u, 42 * u)], fill=INK, width=int(2.2 * u), joint="curve")
    d.ellipse((40 * u, 70 * u, 60 * u, 90 * u), fill=(214, 150, 40), outline=INK, width=int(2 * u))
    d.ellipse((42 * u, 6 * u, 58 * u, 20 * u), fill=(255, 208, 70), outline=INK, width=int(2 * u))
    d.arc((34 * u, 24 * u, 52 * u, 52 * u), 190, 260, fill=(255, 246, 200), width=int(3 * u))
    return big.resize((s, s), Image.LANCZOS)


@lru_cache(maxsize=None)
def heart_sprite(size):
    k = 3
    big = Image.new("RGBA", (size * k, size * k), (0, 0, 0, 0))
    d = ImageDraw.Draw(big)
    u = size * k / 100.0
    for grow, col in ((3, INK), (0, (240, 96, 120))):
        d.ellipse(((14 - grow) * u, (14 - grow) * u, (54 + grow) * u, (54 + grow) * u), fill=col)
        d.ellipse(((46 - grow) * u, (14 - grow) * u, (86 + grow) * u, (54 + grow) * u), fill=col)
        d.polygon([((16 - grow) * u, 42 * u), ((84 + grow) * u, 42 * u), (50 * u, (88 + grow) * u)], fill=col)
    d.ellipse((24 * u, 24 * u, 34 * u, 34 * u), fill=(255, 200, 210))
    return big.resize((size, size), Image.LANCZOS)


def draw(img, item, t, W, H):
    kind = item["type"]
    at, dur = item.get("at", 0.0), item.get("dur", 999.0)
    alpha, scale = _env(t, at, dur)
    if alpha <= 0 and kind != "bus":
        return img
    lt = t - at
    x, y = item.get("pos", (0.5, 0.3))
    cx, cy = x * W, y * H
    sc = item.get("scale", 1.0)
    if kind == "item":
        _paste(img, (props_story.sprite(item["item"], H) if item["item"] in props_story.SPRITES else item_sprite(item["item"], H)), cx, cy - math.sin(lt * 3) * H * 0.004, alpha, min(1.0, scale) * sc)
    elif kind == "bus":
        if lt < 0 or lt > dur:
            return img
        x0, x1 = item.get("x0", 1.25), item.get("x1", 0.62)
        u = min(1.0, lt / min(dur, item.get("arrive", 3.0)))
        u = 1 - (1 - u) ** 3                                    # decelerates into the stop
        px = (x0 + (x1 - x0) * u) * W
        bob = math.sin(lt * 9) * H * 0.003 * (1 - u) + math.sin(lt * 2.4) * H * 0.0015
        spr = bus_sprite(H)
        _paste(img, spr, px, cy + bob, 1.0, sc)
    elif kind == "subscribe":                                   # the yellow bell sits inside the red button
        pulse = 1 + 0.04 * math.sin(lt * 5)
        box = subscribe_sprite(H)
        k = min(1.0, scale) * pulse * sc
        _paste(img, box, cx, cy, alpha, k)
        swing = math.sin(lt * 7) * 16 * max(0.0, 1 - (lt % 2.2) / 1.6)
        _paste(img, bell_sprite(H), cx - box.width * k * 0.31, cy + H * 0.004, alpha, 0.62 * k, angle=swing)
    elif kind == "hearts":
        n = item.get("n", 10)
        for i in range(n):
            u = ((lt * 0.28 + i / n) % 1.0)
            px = (0.08 + 0.84 * ((i * 0.381) % 1.0)) * W + math.sin(lt * 2 + i) * H * 0.02
            py = H * (1.02 - u * 0.9)
            a = math.sin(math.pi * u) * alpha
            size = int(H * (0.05 + 0.04 * ((i * 5) % 3) / 3))
            _paste(img, heart_sprite(size), px, py, a)
    return img
