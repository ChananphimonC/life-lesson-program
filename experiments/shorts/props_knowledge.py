"""Motion graphics for the "รู้หรือไม่" explainer series: letter pairs, a 16-type grid, a bell curve, Big Five
sliders and simple icons. Drawn locally (Thai text with the local font), sized from the frame height, animated
with the same pop-in / fade envelope as props.py.
"""

from __future__ import annotations

import math
from functools import lru_cache

from PIL import Image, ImageDraw

from art import Pen
from subtitles import font

INK = (118, 88, 72)
TILE_COLORS = [(244, 178, 92), (120, 180, 214), (148, 196, 120), (226, 132, 150)]


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


def _tile(letter, label, color, H):
    w, h = int(H * 0.27), int(H * 0.36)
    pen = Pen(w, h)
    pen.rect(4, 4, w - 4, h - 4, color, radius=h * 0.12, outline=INK, width=max(3, H // 300))
    img = pen.result()
    d = ImageDraw.Draw(img)
    d.text((w / 2, h * 0.40), letter, font=font(int(h * 0.42)), fill=(255, 255, 255), anchor="mm",
           stroke_width=max(3, H // 260), stroke_fill=INK)
    lab = font(int(h * 0.105))
    words, lines, cur = label.split(), [], ""
    for wd in words:
        cand = (cur + " " + wd).strip()
        if lab.getlength(cand) > w * 0.86 and cur:
            lines.append(cur)
            cur = wd
        else:
            cur = cand
    lines.append(cur)
    lines = lines[:2]
    size = int(h * 0.105)
    while size > 12 and max(font(size).getlength(ln) for ln in lines) > w * 0.86:  # shrink until it fits the tile
        size -= 2
    for i, ln in enumerate(lines):
        d.text((w / 2, h * 0.74 + i * h * 0.13), ln, font=font(size), fill=(255, 255, 255), anchor="mm",
               stroke_width=3, stroke_fill=INK)
    return img


@lru_cache(maxsize=None)
def pair_sprite(left, left_label, right, right_label, ci, H, cj=None):
    a = _tile(left, left_label, TILE_COLORS[ci % 4], H)
    b = _tile(right, right_label, TILE_COLORS[(ci + 1) % 4 if cj is None else cj % 4], H)
    gap = int(H * 0.12)
    img = Image.new("RGBA", (a.width + b.width + gap, a.height), (0, 0, 0, 0))
    img.paste(a, (0, 0), a)
    img.paste(b, (a.width + gap, 0), b)
    ImageDraw.Draw(img).text((a.width + gap / 2, a.height * 0.42), "vs", font=font(int(H * 0.06)), fill=(255, 255, 255),
                             anchor="mm", stroke_width=max(3, H // 300), stroke_fill=INK)
    return img


TYPES16 = ["ISTJ", "ISFJ", "INFJ", "INTJ", "ISTP", "ISFP", "INFP", "INTP",
           "ESTP", "ESFP", "ENFP", "ENTP", "ESTJ", "ESFJ", "ENFJ", "ENTJ"]


@lru_cache(maxsize=None)
def type_tile(code, H):
    w, h = int(H * 0.16), int(H * 0.09)
    pen = Pen(w, h)
    color = TILE_COLORS["SNFT".index(code[1]) % 4 if code[1] in "SN" else 0]
    color = TILE_COLORS[(("E" in code) * 2 + ("N" in code)) % 4]
    pen.rect(3, 3, w - 3, h - 3, color, radius=h * 0.25, outline=INK, width=max(2, H // 400))
    img = pen.result()
    ImageDraw.Draw(img).text((w / 2, h / 2), code, font=font(int(h * 0.5)), fill=(255, 255, 255), anchor="mm",
                             stroke_width=2, stroke_fill=INK)
    return img


@lru_cache(maxsize=None)
def bell_sprite(left, right, H):
    w, h = int(H * 0.85), int(H * 0.5)
    pen = Pen(w, h)
    pen.rect(0, 0, w, h, (255, 252, 244, 235), radius=h * 0.08, outline=INK, width=max(3, H // 300))
    base, top = h * 0.80, h * 0.16
    pts = [(w * 0.06 + (w * 0.88) * i / 80, base - (base - top) * math.exp(-((i / 80 - 0.5) ** 2) / 0.03)) for i in range(81)]
    pen.poly(pts + [(w * 0.94, base), (w * 0.06, base)], (170, 206, 230))
    pen.line(pts, INK, max(3, H // 280))
    pen.line([(w * 0.06, base), (w * 0.94, base)], INK, max(3, H // 300))
    pen.line([(w * 0.5, top - h * 0.05), (w * 0.5, base + h * 0.03)], (214, 72, 72), max(4, H // 220))
    img = pen.result()
    d = ImageDraw.Draw(img)
    f = font(int(h * 0.13))
    d.text((w * 0.2, h * 0.3), left, font=f, fill=(214, 120, 40), anchor="mm", stroke_width=3, stroke_fill=(255, 255, 255))
    d.text((w * 0.8, h * 0.3), right, font=f, fill=(60, 120, 180), anchor="mm", stroke_width=3, stroke_fill=(255, 255, 255))
    d.text((w / 2, h * 0.91), "คนส่วนใหญ่อยู่ตรงกลาง", font=font(int(h * 0.075), False), fill=(60, 44, 40), anchor="mm")
    return img


BIG5 = ["เปิดรับสิ่งใหม่", "มีระเบียบวินัย", "ชอบเข้าสังคม", "ใจดี เข้ากับคนง่าย", "อารมณ์อ่อนไหว"]


def sliders(img, item, t, W, H, alpha):
    w, row = int(H * 0.9), int(H * 0.085)
    x0 = item.get("pos", (0.5, 0.4))[0] * W - w / 2
    y0 = item.get("pos", (0.5, 0.4))[1] * H - row * 2.5
    lt = t - item["at"]
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    f = font(int(row * 0.42), False)
    targets = item.get("values", [0.7, 0.45, 0.6, 0.8, 0.35])
    for i, (label, v) in enumerate(zip(BIG5, targets)):
        y = y0 + i * row
        appear = max(0.0, min(1.0, (lt - i * 0.25) / 0.4))
        if appear <= 0:
            continue
        a = int(255 * alpha * appear)
        d.text((x0, y + row * 0.35), label, font=f, fill=(60, 44, 40, a), anchor="lm")
        bx0, bx1 = x0 + w * 0.36, x0 + w
        d.rounded_rectangle((bx0, y + row * 0.22, bx1, y + row * 0.48), radius=row * 0.13, fill=(236, 228, 214, a),
                            outline=INK + (a,), width=2)
        knob = 0.5 + (v - 0.5) * min(1.0, max(0.0, (lt - i * 0.25 - 0.3) / 0.8))
        kx = bx0 + (bx1 - bx0) * knob
        d.rounded_rectangle((bx0, y + row * 0.22, kx, y + row * 0.48), radius=row * 0.13,
                            fill=TILE_COLORS[i % 4] + (a,))
        d.ellipse((kx - row * 0.2, y + row * 0.15, kx + row * 0.2, y + row * 0.55), fill=(255, 255, 255, a),
                  outline=INK + (a,), width=3)
    out = img.convert("RGBA")
    out.alpha_composite(layer)
    return out.convert("RGB")


@lru_cache(maxsize=None)
def icon(kind, label, H):
    s = int(H * 0.26)
    pen = Pen(s, s)
    if kind == "book":
        pen.rect(s * 0.12, s * 0.18, s * 0.5, s * 0.82, (196, 92, 80), radius=s * 0.04, outline=INK, width=4)
        pen.rect(s * 0.5, s * 0.18, s * 0.88, s * 0.82, (214, 108, 92), radius=s * 0.04, outline=INK, width=4)
        for k in range(4):
            pen.line([(s * 0.58, s * (0.32 + k * 0.1)), (s * 0.8, s * (0.32 + k * 0.1))], (250, 230, 210), 4)
    elif kind == "sheet":
        pen.rect(s * 0.2, s * 0.1, s * 0.8, s * 0.9, (252, 250, 244), radius=s * 0.04, outline=INK, width=4)
        for k in range(5):
            y = s * (0.24 + k * 0.13)
            pen.circle(s * 0.3, y, s * 0.035, (120, 180, 214))
            pen.line([(s * 0.38, y), (s * 0.7, y)], (170, 160, 150), 4)
    elif kind == "cross":
        pen.circle(s / 2, s / 2, s * 0.42, (226, 88, 88), outline=INK, width=4)
        pen.line([(s * 0.32, s * 0.32), (s * 0.68, s * 0.68)], (255, 255, 255), s * 0.09)
        pen.line([(s * 0.68, s * 0.32), (s * 0.32, s * 0.68)], (255, 255, 255), s * 0.09)
    elif kind == "check":
        pen.circle(s / 2, s / 2, s * 0.42, (120, 188, 110), outline=INK, width=4)
        pen.line([(s * 0.3, s * 0.52), (s * 0.45, s * 0.66), (s * 0.72, s * 0.36)], (255, 255, 255), s * 0.09)
    elif kind == "chat":
        pen.rect(s * 0.1, s * 0.18, s * 0.9, s * 0.7, (255, 255, 255), radius=s * 0.12, outline=INK, width=4)
        pen.poly([(s * 0.28, s * 0.68), (s * 0.44, s * 0.68), (s * 0.24, s * 0.86)], (255, 255, 255))
        for k in range(3):
            pen.circle(s * (0.32 + k * 0.18), s * 0.44, s * 0.05, (170, 160, 150))
    img = pen.result()
    if label:
        out = Image.new("RGBA", (int(s * 3.2), int(s * 1.36)), (0, 0, 0, 0))
        out.paste(img, (int((out.width - s) / 2), 0), img)
        ImageDraw.Draw(out).text((out.width / 2, s * 1.16), label, font=font(int(s * 0.19)), fill=(60, 44, 40),
                                 anchor="mm", stroke_width=4, stroke_fill=(255, 255, 255))
        return out
    return img


BUDGET_COLS = [(120, 180, 214), (226, 132, 150)]  # first person, second person


def budget_card(head, rows, shown, hl, H):
    """A two-person budget table: `head` = [label, A, B]; rows = [[label, a, b], ...]; first `shown` rows visible.
    Rows listed in `hl` (indices) are drawn bold on a highlight band (totals, savings)."""
    rh = int(H * 0.082)
    w, h = int(H * 1.08), rh * (len(rows) + 1) + int(H * 0.05)
    pen = Pen(w, h)
    pen.rect(3, 3, w - 3, h - 3, (255, 252, 244), radius=h * 0.05, outline=INK, width=max(3, H // 300))
    img = pen.result()
    d = ImageDraw.Draw(img)
    x0, x1, x2 = w * 0.04, w * 0.60, w * 0.94
    fb, fn = font(int(rh * 0.56)), font(int(rh * 0.56), False)
    pen = None
    d.rounded_rectangle((8, 8, w - 8, rh), 16, fill=(244, 232, 214))
    d.text((x0, rh * 0.5), head[0], font=fb, fill=(90, 70, 64), anchor="lm")
    for col, (x, txt) in enumerate(((x1, head[1]), (x2, head[2]))):
        d.text((x, rh * 0.5), txt, font=fb, fill=BUDGET_COLS[col], anchor="rm", stroke_width=1, stroke_fill=(90, 70, 64))
    for i, row in enumerate(rows[:shown]):
        y = rh * (i + 1) + int(H * 0.02)
        bold = i in hl
        if bold:
            d.rounded_rectangle((12, y + 4, w - 12, y + rh - 2), 14, fill=(255, 232, 170))
        f = fb if bold else fn
        d.text((x0, y + rh * 0.5), row[0], font=f, fill=(70, 54, 50), anchor="lm")
        d.text((x1, y + rh * 0.5), row[1], font=f, fill=(70, 54, 50), anchor="rm")
        d.text((x2, y + rh * 0.5), row[2], font=f, fill=(70, 54, 50), anchor="rm")
    return img


def bars_card(labels, values, unit, grow, H):
    """Two animated bars (grow 0..1) with their values; for 'savings per month'."""
    w, h = int(H * 0.9), int(H * 0.62)
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    base, top = h * 0.84, h * 0.24
    top_v = max(values)
    for i, (lab, v) in enumerate(zip(labels, values)):
        x = w * (0.26 + i * 0.48)
        bh = (base - top) * (v / top_v) * grow
        d.rounded_rectangle((x - w * 0.14, base - bh, x + w * 0.14, base), 18, fill=BUDGET_COLS[i % 2], outline=INK, width=4)
        d.text((x, base + h * 0.07), lab, font=font(int(h * 0.1)), fill=(70, 54, 50), anchor="mm", stroke_width=3,
               stroke_fill=(255, 252, 244))
        if grow > 0.3:
            d.text((x, base - bh - h * 0.06), f"{int(v * min(1, grow)):,}", font=font(int(h * 0.1)), fill=(70, 54, 50),
                   anchor="mm", stroke_width=4, stroke_fill=(255, 252, 244))
    d.text((w / 2, h * 0.02), unit, font=font(int(h * 0.085), False), fill=(90, 70, 64), anchor="mt", stroke_width=3,
           stroke_fill=(255, 252, 244))
    return img


def draw(img, item, t, W, H):
    kind = item["type"]
    alpha, scale = _env(t, item.get("at", 0.0), item.get("dur", 999.0))
    if alpha <= 0:
        return img
    cx, cy = item.get("pos", (0.5, 0.35))[0] * W, item.get("pos", (0.5, 0.35))[1] * H
    if kind == "pair":
        ca, cb = (item["colors"] + [None, None])[:2] if "colors" in item else (item.get("color", 0), None)
        spr = pair_sprite(item["left"], item["left_label"], item["right"], item["right_label"], ca, H, cb)
        _paste(img, spr, cx, cy, alpha, scale * item.get("scale", 1.0))
    elif kind == "grid16":
        lt = t - item["at"]
        tw, th = type_tile("ISTJ", H).size
        for i, code in enumerate(TYPES16):
            a2, s2 = _env(lt, i * 0.08, 999)
            r, c = divmod(i, 4)
            _paste(img, type_tile(code, H), cx + (c - 1.5) * tw * 1.12, cy + (r - 1.5) * th * 1.25, alpha * a2, s2)
    elif kind == "bell":
        _paste(img, bell_sprite(item.get("left", "E"), item.get("right", "I"), H), cx, cy, alpha, scale)
    elif kind == "sliders":
        img = sliders(img, item, t, W, H, alpha)
    elif kind == "icon":
        _paste(img, icon(item["icon"], item.get("label", ""), H), cx, cy, alpha, scale * item.get("scale", 1.0))
    elif kind == "budget":
        lt = t - item["at"]
        n = len(item["rows"])
        step = item.get("step", max(0.4, item["dur"] * 0.7 / n))  # one row every `step` seconds
        shown = min(n, int(lt / step) + 1)
        _paste(img, budget_card(tuple(item["head"]), tuple(tuple(r) for r in item["rows"]), shown,
                                tuple(item.get("hl", [])), H), cx, cy, alpha, min(1.0, scale) * item.get("scale", 1.0))
    elif kind == "bars":
        grow = min(1.0, max(0.0, (t - item["at"]) / 1.6))
        _paste(img, bars_card(tuple(item["labels"]), tuple(item["values"]), item.get("unit", ""), grow, H), cx, cy,
               alpha, min(1.0, scale) * item.get("scale", 1.0))
    return img


KINDS = {"pair", "grid16", "bell", "sliders", "icon", "budget", "bars"}
