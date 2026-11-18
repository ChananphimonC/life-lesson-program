"""Timed overlays for Shorts scenes: icons/props that pop in, captions, banners, fades.

A scene lists them as {"type": ..., "at": seconds, "dur": seconds, ...}; `draw(img, item, t, W, H)`
renders one at scene-local time t. All Thai text is drawn locally with the Thai font.
"""

from __future__ import annotations

import math
from functools import lru_cache

from PIL import Image, ImageDraw

import character_art as CA
import props_knowledge
import props_city
import props_money
import props_story
from art import INK, Pen
from subtitles import font


def _pop(t, at, dur, fade=0.2):
    """(alpha, scale) for a pop-in / fade-out envelope."""
    lt = t - at
    if lt < 0 or lt > dur:
        return 0.0, 0.0
    a = min(1.0, lt / fade, (dur - lt) / fade)
    x = min(1.0, lt / 0.25)
    s = 1 + 2.70158 * (x - 1) ** 3 + 1.70158 * (x - 1) ** 2  # ease-out-back
    return max(0.0, a), s


def _paste(img, spr, cx, cy, alpha=1.0, scale=1.0):
    if alpha <= 0 or scale <= 0.02:
        return
    if scale != 1.0:
        spr = spr.resize((max(1, int(spr.width * scale)), max(1, int(spr.height * scale))), Image.BILINEAR)
    if alpha < 1:
        spr = spr.copy()
        spr.putalpha(spr.getchannel("A").point(lambda v: int(v * alpha)))
    img.paste(spr, (int(cx - spr.width / 2), int(cy - spr.height / 2)), spr)


@lru_cache(maxsize=None)
def matcha_dream():
    pen = Pen(640, 520)
    for x, y, r in ((40, 470, 18), (90, 420, 28)):
        pen.circle(x, y, r + 5, INK)
        pen.circle(x, y, r, (255, 255, 255))
    pen.ellipse(360, 220, 270, 200, INK)
    pen.ellipse(360, 220, 262, 192, (255, 255, 255))
    # iced matcha with pearls
    pen.poly([(180, 110), (300, 110), (286, 330), (194, 330)], INK)
    pen.poly([(188, 118), (292, 118), (280, 322), (200, 322)], (232, 244, 236))
    pen.poly([(192, 170), (288, 170), (280, 322), (200, 322)], (140, 186, 96))
    for x, y in ((214, 300), (240, 306), (266, 300), (226, 280), (254, 282)):
        pen.circle(x, y, 10, (60, 44, 40))
    pen.line([(260, 60), (246, 200)], (90, 170, 90), 12)
    # sushi
    for k, x in enumerate((380, 480)):
        pen.rect(x - 52, 250, x + 52, 310, INK, radius=26)
        pen.rect(x - 46, 256, x + 46, 304, (252, 250, 244), radius=22)
        pen.rect(x - 56, 214, x + 56, 262, INK, radius=22)
        pen.rect(x - 50, 220, x + 50, 256, (244, 140, 100) if k == 0 else (236, 96, 90), radius=18)
        for dx in (-26, 0, 26):
            pen.line([(x + dx - 10, 230), (x + dx + 10, 248)], (255, 214, 190), 5)
    return pen.result()


@lru_cache(maxsize=None)
def phone_screen():
    pen = Pen(520, 820)
    pen.rect(0, 0, 520, 820, INK, radius=60)
    pen.rect(16, 16, 504, 804, (250, 250, 252), radius=48)
    pen.rect(16, 16, 504, 150, (63, 167, 154), radius=48)
    pen.rect(16, 100, 504, 150, (63, 167, 154))
    pen.circle(260, 360, 110, (236, 92, 88))
    pen.line([(210, 310), (310, 410)], (255, 255, 255), 24)
    pen.line([(310, 310), (210, 410)], (255, 255, 255), 24)
    img = pen.result()
    d = ImageDraw.Draw(img)
    d.text((260, 84), "แอปเดลิเวอรี", font=font(46), fill=(255, 255, 255), anchor="mm")
    d.text((260, 540), "ขออภัยค่ะ", font=font(52), fill=(60, 50, 60), anchor="mm")
    d.text((260, 610), "ไม่สามารถจัดส่ง", font=font(42, False), fill=(90, 80, 90), anchor="mm")
    d.text((260, 664), "พื้นที่นี้ได้", font=font(42, False), fill=(90, 80, 90), anchor="mm")
    return img


@lru_cache(maxsize=None)
def island_badge():
    pen = Pen(360, 200)
    pen.rect(0, 0, 360, 200, INK, radius=40)
    pen.rect(8, 8, 352, 192, (255, 220, 120), radius=34)
    img = pen.result()
    ImageDraw.Draw(img).text((180, 100), "สถานะ: เกาะ", font=font(54), fill=(120, 60, 30), anchor="mm")
    return img


@lru_cache(maxsize=None)
def broken_heart():
    pen = Pen(220, 200)
    for grow, col in ((8, INK), (0, (232, 84, 104))):
        pen.circle(72, 74, 50 + grow, col)
        pen.circle(148, 74, 50 + grow, col)
        pen.poly([(22 - grow, 92), (198 + grow, 92), (110, 192 + grow)], col)
    pen.line([(110, 30), (96, 86), (124, 116), (106, 190)], INK, 10)
    return pen.result()


@lru_cache(maxsize=None)
def suitcase():
    pen = Pen(260, 300)
    pen.rect(90, 0, 170, 60, INK, radius=20)
    pen.rect(102, 12, 158, 60, (238, 222, 196), radius=14)
    pen.rect(10, 50, 250, 280, INK, radius=28)
    pen.rect(18, 58, 242, 272, (236, 120, 96), radius=22)
    for x in (80, 180):
        pen.rect(x - 8, 58, x + 8, 272, (206, 96, 76))
    for x in (50, 210):
        pen.circle(x, 286, 14, INK)
    return pen.result()


@lru_cache(maxsize=None)
def exclaim(text="!"):
    img = Image.new("RGBA", (220, 220), (0, 0, 0, 0))
    ImageDraw.Draw(img).text((110, 110), text, font=font(150), fill=(255, 236, 80), anchor="mm",
                             stroke_width=10, stroke_fill=INK)
    return img


@lru_cache(maxsize=None)
def _caption(text, style, W):
    size = {"title": 70, "banner": 58, "end": 76, "small": 50, "note": 30, "hero": 118}[style]
    f = font(size)
    lines = text.split("\n")
    lh = int(size * 1.3)
    w = int(max(f.getlength(ln) for ln in lines)) + 80
    h = lh * len(lines) + 40
    img = Image.new("RGBA", (min(W, w), h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if style in ("banner", "end", "note", "hero"):
        d.rounded_rectangle((0, 0, img.width - 1, h - 1), 28, fill=(30, 24, 32, 200))
    color = {"title": (255, 255, 255), "banner": (255, 236, 120), "end": (186, 232, 140), "small": (255, 255, 255),
             "note": (240, 236, 228), "hero": (255, 214, 102)}[style]
    for i, ln in enumerate(lines):
        d.text((img.width // 2, 20 + i * lh), ln, font=f, fill=color, anchor="ma", stroke_width=6, stroke_fill=(30, 20, 22))
    return img


@lru_cache(maxsize=None)
def news_bar(W, text):
    img = Image.new("RGBA", (W, 170), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, W, 96), fill=(206, 40, 48, 255))
    d.rectangle((0, 96, W, 170), fill=(255, 255, 255, 235))
    d.text((40, 48), "ข่าวด่วน", font=font(64), fill=(255, 255, 255), anchor="lm")
    d.text((40, 133), text, font=font(42, False), fill=(40, 30, 40), anchor="lm")
    return img


def draw(img, item, t, W, H):
    kind = item["type"]
    if kind in props_knowledge.KINDS:
        return props_knowledge.draw(img, item, t, W, H)
    if kind in props_money.KINDS:
        return props_money.draw(img, item, t, W, H)
    if kind in props_city.KINDS:
        return props_city.draw(img, item, t, W, H)
    if kind in props_story.KINDS:
        return props_story.draw(img, item, t, W, H)
    at, dur = item.get("at", 0.0), item.get("dur", 999.0)
    alpha, scale = _pop(t, at, dur)
    if alpha <= 0:
        return img
    x, y = item.get("pos", (0.5, 0.3))
    cx, cy = x * W, y * H
    if kind == "news_bar":
        spr = news_bar(W, item.get("text", ""))
        _paste(img, spr, W / 2, item.get("y", 0.06) * H + spr.height / 2, alpha)
    elif kind == "caption":
        _paste(img, _caption(item["text"], item.get("style", "title"), W), cx, cy, alpha, min(1.0, scale))
    elif kind in ("matcha_dream", "phone_screen", "island_badge", "broken_heart", "suitcase"):
        spr = globals()[kind]()
        _paste(img, spr, cx, cy, alpha, scale * item.get("scale", 1.0))
    elif kind == "exclaim":
        _paste(img, exclaim(item.get("text", "!")), cx, cy, alpha, scale * item.get("scale", 1.0))
    elif kind == "fade_black":
        lt = t - at
        a = min(1.0, lt / item.get("fade", 0.3), (dur - lt) / item.get("fade", 0.3))
        black = Image.new("RGB", img.size, (8, 6, 10))
        img = Image.blend(img, black, max(0.0, min(1.0, a)) * item.get("max", 1.0))
    elif kind == "door_close":
        lt = max(0.0, t - at)
        u = min(1.0, lt / item.get("speed", 0.5))
        x0, y0, x1, y1 = (v * (W if i % 2 == 0 else H) for i, v in enumerate(item["box"]))
        d = ImageDraw.Draw(img)
        d.rectangle((x0, y0, x0 + (x1 - x0) * u, y1), fill=(150, 100, 70), outline=INK, width=5)
        if u > 0.9:
            d.ellipse((x0 + (x1 - x0) * 0.85 - 10, (y0 + y1) / 2 - 10, x0 + (x1 - x0) * 0.85 + 10, (y0 + y1) / 2 + 10),
                      fill=(236, 196, 90))
    elif kind == "char_move":  # a character sliding across (e.g. the fisherman's boat passing the window)
        lt = t - at
        u = min(1.0, max(0.0, lt / dur))
        x = item["x0"] + (item["x1"] - item["x0"]) * u
        spr = CA.sprite(item["id"], item["outfit"], 1 if item["x1"] > item["x0"] else -1, 0, False, item["scale"])
        if item.get("flip"):
            spr = spr.transpose(Image.FLIP_LEFT_RIGHT)
        bob = 6 * math.sin(lt * 4)
        _paste(img, spr, x * W, item["y"] * H - spr.height / 2 + bob, alpha)
    elif kind == "leashes":
        d = ImageDraw.Draw(img)
        hx, hy = item["hand"]
        for px, py in item["to"]:
            sag = 40
            pts = [(hx * W + (px - hx) * W * k / 10, hy * H + (py - hy) * H * k / 10 + sag * math.sin(math.pi * k / 10))
                   for k in range(11)]
            d.line(pts, fill=(220, 80, 80), width=6)
    return img
