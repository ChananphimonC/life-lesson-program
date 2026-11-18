"""Subtitle cards: big outlined Thai text, coloured per speaker, wrapped to fit and kept in safe areas."""

from __future__ import annotations

from functools import lru_cache

from PIL import Image, ImageDraw, ImageFont

BOLD, REGULAR = "LeelaUIb.ttf", "LeelawUI.ttf"
_NO_BREAK_BEFORE = {*map(chr, range(0x0E30, 0x0E3B)), *map(chr, range(0x0E45, 0x0E4F))}  # vowels/tone marks/ๆ
_NO_BREAK_AFTER = set("เแโใไ")


@lru_cache(maxsize=None)
def font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(BOLD if bold else REGULAR, size)


def _break_chars(token: str, f, max_w: int) -> list[str]:
    """Split one over-long unspaced Thai token at syllable-safe character positions."""
    lines, cur = [], ""
    for ch in token:
        if cur and f.getlength(cur + ch) > max_w and ch not in _NO_BREAK_BEFORE and cur[-1] not in _NO_BREAK_AFTER:
            lines.append(cur)
            cur = ch
        else:
            cur += ch
    return lines + [cur]


def wrap(text: str, f, max_w: int) -> list[str]:
    lines, cur = [], ""
    for tok in text.split():
        cand = f"{cur} {tok}".strip()
        if f.getlength(cand) <= max_w:
            cur = cand
            continue
        if cur:
            lines.append(cur)
        if f.getlength(tok) > max_w:
            parts = _break_chars(tok, f, max_w)
            lines.extend(parts[:-1])
            cur = parts[-1]
        else:
            cur = tok
    return lines + ([cur] if cur else [])


def _fits(lines, f, max_w):
    return all(f.getlength(ln) <= max_w for ln in lines)


def card(text: str, name: str, color: tuple, W: int, max_lines: int = 3) -> Image.Image:
    """RGBA card of width W: speaker name chip + wrapped, outlined text.
    Shrinks the font until whole words fit; only splits inside a word as a last resort."""
    margin = int(W * 0.07)
    max_w = W - 2 * margin
    size = 80
    while True:
        f = font(size)
        lines = _wrap_whole(text, f, max_w)
        if (_fits(lines, f, max_w) and len(lines) <= max_lines) or size <= 48:
            break
        size -= 4
    if not _fits(lines, f, max_w):
        lines = wrap(text, f, max_w)
    if len(lines) > 1 and len(lines[-1].replace(" ", "")) < 3:  # never leave a 1-2 character orphan line
        lines = [*lines[:-2], _balance(lines[-2], lines[-1], f)[0], _balance(lines[-2], lines[-1], f)[1]]
    name_f = font(int(size * 0.7))
    line_h = int(size * 1.3)
    name_h = int(size * 0.95)
    img = Image.new("RGBA", (W, name_h + line_h * len(lines) + 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    stroke = max(4, size // 9)
    d.text((W // 2, 0), name, font=name_f, fill=color, anchor="ma", stroke_width=max(3, stroke - 2), stroke_fill=(30, 20, 22))
    y = name_h
    for ln in lines:
        d.text((W // 2, y), ln, font=f, fill=color, anchor="ma", stroke_width=stroke, stroke_fill=(30, 20, 22))
        y += line_h
    return img


def _wrap_whole(text: str, f, max_w: int) -> list[str]:
    """Greedy wrap on spaces only (a word wider than max_w stays whole, on its own line)."""
    lines, cur = [], ""
    for tok in text.split():
        cand = f"{cur} {tok}".strip()
        if f.getlength(cand) <= max_w or not cur:
            cur = cand
        else:
            lines.append(cur)
            cur = tok
    return lines + ([cur] if cur else [])


def _balance(a: str, b: str, f) -> tuple[str, str]:
    """Re-split the last two lines at the syllable-safe point that evens out their widths."""
    joined = a + b if " " not in a + b else a + " " + b
    best, best_gap = (a, b), 1e9
    for i in range(2, len(joined) - 1):
        if joined[i] in _NO_BREAK_BEFORE or joined[i - 1] in _NO_BREAK_AFTER:
            continue
        left, right = joined[:i].strip(), joined[i:].strip()
        gap = abs(f.getlength(left) - f.getlength(right))
        if gap < best_gap:
            best, best_gap = (left, right), gap
    return best
