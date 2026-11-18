"""Render the thumbnail PNG from `build_thumbnail_spec` output (STYLE_GUIDE.md §8).

Layout (designed on a 1280x720 grid, scaled to the real size):
red context tag (top-left) / headline line 1 white + line 2 yellow /
subline / pill (bottom-left). Shorts use the vertical 9:16 layout with the
text kept inside the platform safe zone.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from life_lesson.publish.fonts import find_thai_font

WHITE = (255, 255, 255)
YELLOW = (255, 214, 10)
RED = (214, 52, 41)
SOFT = (200, 235, 190)
INK = (12, 16, 28)


def _hex_to_rgb(value: str) -> tuple[int, int, int] | None:
    v = value.strip().lstrip("#")
    if len(v) == 6:
        try:
            return tuple(int(v[i : i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]
        except ValueError:
            return None
    return None


def _backdrop(size: tuple[int, int], base_image: Path | None, tint: tuple[int, int, int]) -> Image.Image:
    w, h = size
    if base_image and Path(base_image).is_file():
        img = Image.open(base_image).convert("RGB")
        scale = max(w / img.width, h / img.height)
        img = img.resize((int(img.width * scale) + 1, int(img.height * scale) + 1))
        left, top = (img.width - w) // 2, (img.height - h) // 2
        img = img.crop((left, top, left + w, top + h))
    else:
        img = Image.new("RGB", size, INK)
        px = img.load()
        for y in range(h):
            k = y / h
            for x in range(0, w):
                # soft diagonal glow in the tint colour on a dark base
                g = max(0.0, 1.0 - ((x / w) * 0.6 + k * 0.9))
                px[x, y] = tuple(int(INK[i] + (tint[i] - INK[i]) * g * 0.45) for i in range(3))
    # darken for text contrast + left-to-right shade where the text sits
    shade = Image.new("L", size, 0)
    sd = ImageDraw.Draw(shade)
    for x in range(w):
        sd.line([(x, 0), (x, h)], fill=int(200 * max(0.0, 1.0 - x / (w * 0.8))))
    black = Image.new("RGB", size, (0, 0, 0))
    img = Image.composite(black, img, shade.filter(ImageFilter.GaussianBlur(8)))
    return Image.blend(img, Image.new("RGB", size, (0, 0, 0)), 0.15)


def _fit_font(draw: ImageDraw.ImageDraw, text: str, font_path: Path, start: int, max_w: int) -> ImageFont.FreeTypeFont:
    size = start
    while size > 14:
        font = ImageFont.truetype(str(font_path), size)
        if draw.textlength(text, font=font) <= max_w:
            return font
        size -= 4
    return ImageFont.truetype(str(font_path), 14)


def render_thumbnail(
    spec: dict,
    out_path: Path,
    *,
    base_image: Path | None = None,
    font_path: str | None = None,
) -> Path:
    w, h = spec["size"]
    vertical = h > w
    font_file = find_thai_font(font_path)
    palette = (spec.get("character") or {}).get("palette") or []
    tint = next((c for c in (_hex_to_rgb(p) for p in palette) if c), (60, 90, 160))

    img = _backdrop((w, h), base_image, tint)
    d = ImageDraw.Draw(img)
    u = (h / 1280) if vertical else (w / 1280)  # grid unit scale
    safe = spec.get("safe_zone", {})
    margin = int(64 * u)
    max_w = int(w * (1 - safe.get("right_pct", 8) / 100)) - margin * 2
    bottom_limit = int(h * (1 - safe.get("bottom_pct", 8) / 100))

    y = margin if not vertical else int(h * 0.2)

    tag = spec.get("context_tag")
    if tag:
        f = ImageFont.truetype(str(font_file), int(30 * u))
        tw = d.textlength(tag, font=f)
        pad = int(14 * u)
        d.rounded_rectangle([margin, y, margin + tw + pad * 2, y + int(52 * u)], radius=int(12 * u), fill=RED)
        d.text((margin + pad, y + int(6 * u)), tag, font=f, fill=WHITE)
        y += int(52 * u) + int(40 * u)

    head_size = int((130 if vertical else 100) * u)
    for text, color, start in (
        (spec["headline_line1"], WHITE, head_size),
        (spec["headline_line2"], YELLOW, head_size),
    ):
        font = _fit_font(d, text, font_file, start, max_w)
        # soft shadow for legibility at small sizes
        d.text((margin + 4, y + 5), text, font=font, fill=(0, 0, 0))
        d.text((margin, y), text, font=font, fill=color)
        y += int(font.size * 1.3)

    sub = spec.get("subline")
    if sub:
        font = _fit_font(d, sub, font_file, int(44 * u), max_w)
        d.text((margin, y + int(10 * u)), sub, font=font, fill=SOFT)

    pill = spec.get("pill")
    if pill:
        if y + int(120 * u) > bottom_limit - int(58 * u):
            raise ValueError("thumbnail text overflows the layout; shorten the title")
        f = ImageFont.truetype(str(font_file), int(32 * u))
        tw = d.textlength(pill, font=f)
        pad = int(22 * u)
        ph = int(58 * u)
        py = bottom_limit - ph
        d.rounded_rectangle([margin, py, margin + tw + pad * 2, py + ph], radius=ph // 2, fill=(20, 24, 36), outline=WHITE, width=max(2, int(2 * u)))
        d.text((margin + pad, py + int(7 * u)), pill, font=f, fill=WHITE)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, "PNG", optimize=True)
    return out_path
