"""Thai text for Pillow *without* raqm (the shaping engine is not installed here).

Plain Pillow layout puts a tone mark that sits over an upper vowel (เมื่อ ที่ นี้ เนื้อ ปี้ กี่ ผู้ ...) at the same height as the vowel, so it vanishes ("เมื่อ" -> "เมือ").
`draw_line` draws the line without those stacked marks and then draws every one of them again, lifted above the vowel. Everything else is left to Pillow.
"""
from __future__ import annotations

UPPER = set("\u0e31\u0e34\u0e35\u0e36\u0e37\u0e47\u0e4d")      # mai han-akat, sara i / ii / ue / uee, mai taikhu, nikhahit
TONE = set("\u0e48\u0e49\u0e4a\u0e4b\u0e4c")                    # mai ek, tho, tri, chattawa, thanthakhat
LIFT = 0.215                                                     # how far (fraction of the font size) a stacked mark is raised


def split_stacked(line: str):
    """(line without the stacked marks, [(index in that string where the mark belongs, mark), ...])."""
    base, marks = [], []
    for ch in line:
        if ch in TONE and base and base[-1] in UPPER:
            marks.append((len(base), ch))
        else:
            base.append(ch)
    return "".join(base), marks


def draw_line(draw, xy, line, font, fill, anchor="la", stroke_width=0, stroke_fill=None, lift=LIFT):
    """Like draw.text for one line (no newlines), but with stacked tone marks drawn above the vowel."""
    base, marks = split_stacked(line)
    draw.text(xy, base, font=font, fill=fill, anchor=anchor, stroke_width=stroke_width, stroke_fill=stroke_fill)
    if not marks:
        return
    x, y = xy
    width = font.getlength(base)
    h = anchor[0]
    x0 = x - width / 2 if h == "m" else (x - width if h == "r" else x)
    size = getattr(font, "size", 100)
    for k, ch in marks:
        draw.text((x0 + font.getlength(base[:k]), y - size * lift), ch, font=font, fill=fill, anchor="l" + anchor[1], stroke_width=stroke_width, stroke_fill=stroke_fill)
