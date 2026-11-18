"""Animated scene props for the city-life / money episodes: price tags, a salary notification, a pan with steam,
a wholesale cart that fills up, a spinning fan, an air-conditioner's cold air, smoke, food icons, falling coins.
Drawn locally (Thai text with the local font) and sized from the frame height H. Each is `draw(img, item, t, W, H)`
with the same at/dur timing as the other props.
"""

from __future__ import annotations

import math
from functools import lru_cache

from PIL import Image, ImageDraw

import props_city
from subtitles import font

INK = (118, 88, 72)
KINDS = {"tag", "notif", "pan", "cart", "fan", "aircon", "smoke", "food", "coins"}


def _env(t, at, dur, fade=0.25):
    lt = t - at
    if lt < 0 or lt > dur:
        return 0.0, 0.0
    a = min(1.0, lt / fade, (dur - lt) / fade)
    x = min(1.0, lt / 0.35)
    s = 1 + 2.70158 * (x - 1) ** 3 + 1.70158 * (x - 1) ** 2
    return max(0.0, a), s


def _paste(img, spr, cx, cy, alpha=1.0, scale=1.0):
    if alpha <= 0 or scale <= 0.02:
        return
    if abs(scale - 1) > 0.01:
        spr = spr.resize((max(1, int(spr.width * scale)), max(1, int(spr.height * scale))), Image.BILINEAR)
    if alpha < 1:
        spr = spr.copy()
        spr.putalpha(spr.getchannel("A").point(lambda v: int(v * alpha)))
    img.paste(spr, (int(cx - spr.width / 2), int(cy - spr.height / 2)), spr)


def _smooth(u):
    u = max(0.0, min(1.0, u))
    return u * u * (3 - 2 * u)


@lru_cache(maxsize=None)
def tag_sprite(text, color, H):
    f = font(int(H * 0.06))
    w = int(f.getlength(text)) + int(H * 0.09)
    h = int(H * 0.095)
    img = Image.new("RGBA", (w + 8, h + 8), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((4, 4, w + 4, h + 4), int(h * 0.4), fill=color, outline=INK, width=4)
    d.ellipse((12, h / 2 - 5, 22, h / 2 + 5), fill=(255, 252, 244), outline=INK, width=2)
    d.text((w / 2 + 12, h / 2 + 4), text, font=f, fill=(255, 255, 255), anchor="mm", stroke_width=4, stroke_fill=INK)
    return img


@lru_cache(maxsize=None)
def notif_sprite(title, amount, W, H):
    w, h = int(W * 0.46), int(H * 0.13)
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((2, 2, w - 2, h - 2), int(h * 0.3), fill=(255, 255, 255, 245), outline=INK, width=4)
    d.ellipse((h * 0.18, h * 0.18, h * 0.82, h * 0.82), fill=(94, 190, 128), outline=INK, width=3)
    d.text((h / 2, h / 2), "฿", font=font(int(h * 0.42)), fill=(255, 255, 255), anchor="mm")
    d.text((h * 0.95, h * 0.34), title, font=font(int(h * 0.27), False), fill=(90, 74, 70), anchor="lm")
    d.text((h * 0.95, h * 0.68), amount, font=font(int(h * 0.36)), fill=(56, 150, 96), anchor="lm")
    return img


@lru_cache(maxsize=None)
def pan_sprite(H):
    s = int(H * 0.30)
    img = Image.new("RGBA", (int(s * 1.9), s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx, cy = s * 0.7, s * 0.62
    d.rounded_rectangle((cx + s * 0.38, cy - s * 0.05, cx + s * 1.1, cy + s * 0.06), 10, fill=(150, 108, 76), outline=INK, width=4)
    d.ellipse((cx - s * 0.5, cy - s * 0.22, cx + s * 0.5, cy + s * 0.2), fill=(60, 60, 70), outline=INK, width=5)
    d.ellipse((cx - s * 0.42, cy - s * 0.18, cx + s * 0.42, cy + s * 0.12), fill=(250, 216, 120))
    for dx, dy, col in ((-0.2, -0.08, (230, 120, 90)), (0.05, -0.12, (120, 180, 100)), (0.22, -0.04, (232, 150, 90)), (-0.05, 0.0, (250, 240, 220))):
        d.ellipse((cx + s * dx - 12, cy + s * dy - 9, cx + s * dx + 12, cy + s * dy + 9), fill=col, outline=INK, width=2)
    return img


def _puffs(img, t, x, y, H, n=5, rise=0.16, col=(250, 250, 252), width=0.035, alpha=170):
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for k in range(n):
        u = ((t * 0.45 + k / n) % 1.0)
        r = H * (0.018 + 0.03 * u)
        px = x + math.sin(t * 2 + k * 1.7) * H * width + (k - n / 2) * H * 0.006
        py = y - u * H * rise
        a = int(alpha * math.sin(math.pi * u))
        d.ellipse((px - r, py - r, px + r, py + r), fill=col + (a,))
    img.alpha_composite(layer) if img.mode == "RGBA" else img.paste(layer, (0, 0), layer)


@lru_cache(maxsize=None)
def cart_sprite(boxes, H):
    w, h = int(H * 0.48), int(H * 0.36)
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cols = [(206, 160, 110), (230, 96, 84), (246, 200, 90), (126, 184, 112), (110, 150, 206), (240, 236, 228)]
    for i in range(boxes):
        bx = w * (0.14 + (i % 3) * 0.24)
        by = h * (0.42 - (i // 3) * 0.2)
        d.rounded_rectangle((bx, by, bx + w * 0.22, by + h * 0.2), 6, fill=cols[i % len(cols)], outline=INK, width=3)
    d.polygon([(w * 0.06, h * 0.50), (w * 0.94, h * 0.50), (w * 0.84, h * 0.82), (w * 0.16, h * 0.82)], fill=(206, 212, 222), outline=INK)
    d.line([(w * 0.06, h * 0.50), (w * 0.94, h * 0.50), (w * 0.84, h * 0.82), (w * 0.16, h * 0.82), (w * 0.06, h * 0.50)], fill=INK, width=5)
    for k in range(1, 6):
        d.line([(w * (0.06 + k * 0.145), h * 0.52), (w * (0.16 + k * 0.1 - 0.06), h * 0.81)], fill=(150, 156, 170), width=3)
    d.line([(w * 0.06, h * 0.50), (w * 0.0, h * 0.28), (w * 0.14, h * 0.26)], fill=INK, width=6)
    for x in (0.24, 0.76):
        d.ellipse((w * x - 12, h * 0.84, w * x + 12, h * 0.84 + 24), fill=(70, 70, 80), outline=INK, width=3)
    return img


def _fan(img, t, cx, cy, H, spin):
    r = H * 0.1
    layer = Image.new("RGBA", (int(r * 3), int(r * 4.2)), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    mx, my = layer.width / 2, r * 1.5
    d.rectangle((mx - 8, my + r * 0.9, mx + 8, layer.height - 14), fill=(190, 196, 206), outline=INK)
    d.ellipse((mx - r * 0.7, layer.height - 28, mx + r * 0.7, layer.height - 4), fill=(170, 176, 190), outline=INK, width=3)
    d.ellipse((mx - r * 1.15, my - r * 1.15, mx + r * 1.15, my + r * 1.15), outline=INK, width=5, fill=(226, 238, 246, 80))
    for k in range(3):
        a = spin + k * 2 * math.pi / 3
        pts = [(mx, my), (mx + r * math.cos(a - 0.35), my + r * math.sin(a - 0.35)),
               (mx + r * 0.95 * math.cos(a), my + r * 0.95 * math.sin(a)), (mx + r * math.cos(a + 0.35), my + r * math.sin(a + 0.35))]
        d.polygon(pts, fill=(120, 190, 224, 220), outline=INK)
    d.ellipse((mx - 9, my - 9, mx + 9, my + 9), fill=(236, 236, 240), outline=INK, width=3)
    return layer


@lru_cache(maxsize=None)
def food_sprite(kind, H):
    s = int(H * 0.2)
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if kind == "skewers":
        for k in range(3):
            x = s * (0.28 + k * 0.22)
            d.line([(x - 10, s * 0.92), (x + 22, s * 0.1)], fill=(176, 140, 96), width=6)
            for j in range(3):
                d.ellipse((x + 2 - j * 4, s * (0.2 + j * 0.2), x + 34 - j * 4, s * (0.2 + j * 0.2) + 28), fill=(214, 112, 96), outline=INK, width=3)
    elif kind == "sticky":
        d.rounded_rectangle((s * 0.16, s * 0.3, s * 0.84, s * 0.88), 18, fill=(245, 236, 210), outline=INK, width=4)
        d.ellipse((s * 0.22, s * 0.12, s * 0.78, s * 0.42), fill=(252, 250, 240), outline=INK, width=4)
        d.line([(s * 0.2, s * 0.58), (s * 0.8, s * 0.58)], fill=(180, 150, 100), width=5)
    elif kind == "coffee":
        d.polygon([(s * 0.26, s * 0.22), (s * 0.74, s * 0.22), (s * 0.68, s * 0.9), (s * 0.32, s * 0.9)], fill=(200, 150, 100), outline=INK)
        d.line([(s * 0.26, s * 0.22), (s * 0.74, s * 0.22), (s * 0.68, s * 0.9), (s * 0.32, s * 0.9), (s * 0.26, s * 0.22)], fill=INK, width=5)
        d.rounded_rectangle((s * 0.22, s * 0.1, s * 0.78, s * 0.24), 8, fill=(250, 250, 252), outline=INK, width=4)
        d.line([(s * 0.5, s * 0.1), (s * 0.58, s * -0.05)], fill=(70, 150, 90), width=6)
    elif kind == "rice":
        d.ellipse((s * 0.1, s * 0.5, s * 0.9, s * 0.92), fill=(250, 250, 252), outline=INK, width=4)
        d.ellipse((s * 0.2, s * 0.22, s * 0.8, s * 0.7), fill=(255, 252, 240), outline=INK, width=3)
        d.ellipse((s * 0.5, s * 0.3, s * 0.78, s * 0.55), fill=(236, 170, 100))
    elif kind == "bag":
        d.polygon([(s * 0.2, s * 0.3), (s * 0.8, s * 0.3), (s * 0.86, s * 0.92), (s * 0.14, s * 0.92)], fill=(250, 214, 140), outline=INK)
        d.line([(s * 0.2, s * 0.3), (s * 0.8, s * 0.3), (s * 0.86, s * 0.92), (s * 0.14, s * 0.92), (s * 0.2, s * 0.3)], fill=INK, width=5)
        d.arc((s * 0.3, s * 0.05, s * 0.7, s * 0.5), 180, 360, fill=INK, width=6)
    return img


def draw(img, item, t, W, H):
    kind = item["type"]
    at, dur = item.get("at", 0.0), item.get("dur", 999.0)
    alpha, scale = _env(t, at, dur)
    if alpha <= 0:
        return img
    lt = t - at
    x, y = item.get("pos", (0.5, 0.3))
    cx, cy = x * W, y * H
    sc = item.get("scale", 1.0)
    if kind == "tag":
        spr = tag_sprite(item["text"], tuple(item.get("color", (236, 120, 90))), H)
        rise = _smooth(lt / min(dur, 3.0)) * H * 0.04
        _paste(img, spr, cx, cy - rise, alpha, min(1.0, scale) * sc)
    elif kind == "notif":
        spr = notif_sprite(item.get("title", "เงินเดือนเข้า"), item["amount"], W, H)
        drop = _smooth(lt / 0.45) * _smooth((dur - lt) / 0.45)
        _paste(img, spr, cx, -spr.height / 2 + drop * (cy + spr.height / 2), 1.0, sc)
    elif kind == "pan":
        spr = pan_sprite(H)
        _paste(img, spr, cx, cy + math.sin(lt * 7) * H * 0.004, alpha, sc)
        _puffs(img, t, cx - spr.width * 0.1, cy - spr.height * 0.28, H)
    elif kind == "cart":
        x0, x1 = item["x0"], item.get("x1", item["x0"])
        px = (x0 + (x1 - x0) * _smooth(lt / dur)) * W
        boxes = min(6, int(lt / dur * 7))
        bob = abs(math.sin(lt * 4.2)) * H * 0.006 if x1 != x0 else 0
        _paste(img, cart_sprite(boxes, H), px, cy - bob, alpha, sc)
    elif kind == "fan":
        spr = _fan(img, t, cx, cy, H, spin=lt * 14)
        _paste(img, spr, cx, cy, alpha, sc)
    elif kind == "aircon":
        d = ImageDraw.Draw(img)
        w, h = int(W * 0.17), int(H * 0.07)
        d.rounded_rectangle((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), 14, fill=(248, 250, 252), outline=INK, width=4)
        d.line([(cx - w * 0.4, cy + h * 0.2), (cx + w * 0.4, cy + h * 0.2)], fill=(150, 160, 176), width=5)
        for k in range(5):
            u = ((lt * 0.5 + k / 5) % 1.0)
            px = cx + (k - 2) * w * 0.17 + math.sin(lt * 2 + k) * 10
            py = cy + h / 2 + u * H * 0.22
            a = int(200 * math.sin(math.pi * u))
            layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
            ImageDraw.Draw(layer).line([(px, py), (px + 14, py + 10), (px, py + 20), (px + 14, py + 30)], fill=(150, 210, 240, a), width=6)
            img.paste(layer, (0, 0), layer)
    elif kind == "smoke":
        _puffs(img, t, cx, cy, H, n=6, rise=0.2, col=(236, 236, 240), width=0.05, alpha=150)
    elif kind == "food":
        _paste(img, props_city.food_sprite(item["food"], H), cx, cy - math.sin(lt * 3) * H * 0.004, alpha, min(1.0, scale) * sc)
    elif kind == "coins":
        d = ImageDraw.Draw(img)
        n = item.get("n", 14)
        for k in range(n):
            u = ((lt * 0.4 + k * 0.137) % 1.0)
            px = (0.1 + 0.8 * ((k * 0.618) % 1.0)) * W
            py = -0.05 * H + u * H * 1.1
            r = H * 0.026 * (0.8 + 0.4 * ((k * 7) % 3) / 3)
            sq = abs(math.cos(lt * 5 + k))                       # coin turning
            d.ellipse((px - r * sq - 2, py - r - 2, px + r * sq + 2, py + r + 2), fill=INK)
            d.ellipse((px - r * sq, py - r, px + r * sq, py + r), fill=(255, 208, 70))
    return img
