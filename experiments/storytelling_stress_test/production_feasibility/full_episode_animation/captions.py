"""Caption overlay for the episode. There is NO voice audio for this script, so dialogue is shown as captions.

Thai rendering: this Pillow build has no raqm, so a tone mark over an upper vowel (e.g. นี้ ครึ่ง เรื่อง กี่) is drawn on top of the
vowel and disappears. The project's own subtitle card (experiments/shorts/subtitles.py) has that defect, so this file draws
each character itself and lifts tone marks that sit over an upper vowel. Line wrapping reuses subtitles._wrap_whole.
"""
from __future__ import annotations

import sys
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.append(str(Path(__file__).resolve().parents[3] / "shorts"))
import subtitles  # noqa: E402

COL = {"ton": (255, 176, 96), "kaew": (222, 190, 255), "chok": (150, 206, 255), "uean": (255, 156, 150), "": (255, 255, 255)}
NAME = {"ton": "ต้น", "kaew": "ยายแก้ว", "chok": "ลุงโชค", "uean": "ป้าเอื้อน", "": ""}
UPPER_VOWEL = set("ัิีึืํ็")
TONE = set("่้๊๋์")
MARKS = set("ัิีึืฺุู็่้๊๋์ํ๎")


def _width(f, s):
    return sum(f.getlength(ch) for ch in s if ch not in MARKS)


def thai_text(d, x, y, s, f, fill, stroke_w, stroke_fill, size):
    """Draw s with its left edge at x; tone marks over upper vowels (or sara-am) are lifted so they stay visible.
    Two passes (every outline first, then every fill): a later glyph's outline must not cover the thin ascender of the glyph before it (ป + ี looked like บี)."""
    for fill_pass in ((stroke_fill, stroke_w), (fill, 0)):
        col, sw = fill_pass
        if sw == 0 and stroke_w == 0:
            continue
        cx, has_upper = x, False
        for i, ch in enumerate(s):
            if ch in MARKS:
                dy, dx = 0, 0
                if ch in TONE and has_upper:
                    dy = -size * 0.27
                if ch in TONE and s[i + 1:i + 2] == "ำ":          # น้ำ: the tone mark sits over the consonant, left of the nikhahit
                    dx = -size * 0.28
                d.text((cx + dx, y + dy), ch, font=f, fill=col, stroke_width=sw, stroke_fill=stroke_fill)
                if ch in UPPER_VOWEL:
                    has_upper = True
                continue
            d.text((cx, y), ch, font=f, fill=col, stroke_width=sw, stroke_fill=stroke_fill)
            has_upper = False
            cx += f.getlength(ch)


@lru_cache(maxsize=None)
def _card(text, who, W):
    margin = int(W * 0.04)
    max_w = W - 2 * margin
    size = 80
    while True:
        f = subtitles.font(size)
        lines = subtitles._wrap_whole(text, f, max_w)
        # width with marks excluded (they have zero advance but the basic layout still counts them)
        if (all(_width(f, ln) <= max_w for ln in lines) and len(lines) <= 2) or size <= 48:
            break
        size -= 4
    name_f = subtitles.font(int(size * 0.7))
    line_h, name_h = int(size * 1.45), (int(size * 1.15) if who else 0)
    img = Image.new("RGBA", (W, name_h + line_h * len(lines) + 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    stroke = max(4, size // 9)
    col = COL[who]
    if who:
        thai_text(d, W // 2 - _width(name_f, NAME[who]) / 2, 0, NAME[who], name_f, col, max(3, stroke - 2), (30, 20, 22), int(size * 0.7))
    y = name_h
    for ln in lines:
        thai_text(d, W // 2 - _width(f, ln) / 2, y, ln, f, col, stroke, (30, 20, 22), size)
        y += line_h
    return img


def overlay(img, caps, t, W=1280, H=720):
    """Draw the caption active at time t (local seconds) onto the RGBA PIL image."""
    for t0, t1, who, text in caps:
        if t0 <= t < t1:
            c = _card(text, who, 1500)
            sc = 0.56
            c = c.resize((int(c.width * sc), int(c.height * sc)), Image.LANCZOS)
            a = min(1.0, (t - t0) / 0.12, (t1 - t) / 0.12)
            if a < 1:
                c.putalpha(c.getchannel("A").point(lambda v: int(v * a)))
            img.alpha_composite(c, ((W - c.width) // 2, H - c.height - 10))
            break
    return img


def draw_overlay(img, items):
    """items: (text, cx, cy, size, (r, g, b), alpha 0..1) drawn centred, with a dark outline (big numbers, labels)."""
    d = ImageDraw.Draw(img, "RGBA")
    for text, cx, cy, size, col, a in items:
        f = subtitles.font(int(size))
        w = _width(f, text)
        lay = Image.new("RGBA", (int(w + size), int(size * 1.7)), (0, 0, 0, 0))
        ld = ImageDraw.Draw(lay)
        thai_text(ld, size * 0.5, size * 0.1, text, f, (*col, 255), max(3, int(size // 9)), (30, 20, 22, 255), int(size))
        if a < 1:
            lay.putalpha(lay.getchannel("A").point(lambda v: int(v * a)))
        img.alpha_composite(lay, (int(cx - lay.width / 2), int(cy - lay.height / 2)))
    return img
