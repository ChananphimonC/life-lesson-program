"""Reusable code-drawn backgrounds for Shorts, any aspect (layout is in fractions of W/H).
Each background returns an RGB image and is cached as backgrounds/<name>_<W>x<H>.png."""

from __future__ import annotations

import random
from pathlib import Path

from PIL import Image

import character_art  # noqa: F401  (puts cartoon_storyboard on sys.path)
from art import INK, Pen, add_glow, hills, vgradient  # noqa: E402

HERE = Path(__file__).resolve().parent
GROUND = 0.66  # characters' feet, as a fraction of H


def _boat(pen, cx, y, s, hull, fruits, umbrella=None):
    w, h = 300 * s, 46 * s
    if umbrella:
        pen.line([(cx - 30 * s, y - 170 * s), (cx - 30 * s, y - 20 * s)], INK, 7 * s)
        pen.chord(cx - 30 * s, y - 150 * s, 128 * s, 76 * s, 180, 360, INK)
        pen.chord(cx - 30 * s, y - 150 * s, 120 * s, 70 * s, 180, 360, umbrella)
    for i, c in enumerate(fruits):
        px = cx - w / 2 + 50 * s + i * 38 * s
        for dy in (0, -26 * s):
            pen.circle(px + (13 * s if dy else 0), y - h - 12 * s + dy, 19 * s, INK)
            pen.circle(px + (13 * s if dy else 0), y - h - 12 * s + dy, 16 * s, c)
    pen.poly([(cx - w / 2, y - h), (cx + w / 2, y - h), (cx + w / 2 - 44 * s, y), (cx - w / 2 + 44 * s, y)],
             hull, outline=INK, width=4)
    pen.rect(cx - w / 2, y - h, cx + w / 2, y - h + 8 * s, tuple(int(v * 0.8) for v in hull))


def _house(pen, x, y, s, wall, roof):
    w, h = 130 * s, 80 * s
    for px in (x + 10 * s, x + w - 10 * s):
        pen.rect(px - 4 * s, y, px + 4 * s, y + 60 * s, (110, 84, 66))
    pen.rect(x, y - h, x + w, y, wall, outline=INK, width=3)
    pen.poly([(x - 14 * s, y - h), (x + w / 2, y - h - 54 * s), (x + w + 14 * s, y - h)], roof, outline=INK, width=3)
    pen.rect(x + w * 0.38, y - h * 0.7, x + w * 0.62, y - h * 0.15, (80, 62, 56))


def _palm(pen, x, y, h, lean):
    top = (x + lean, y - h)
    pen.line([(x, y), (x + lean * 0.4, y - h * 0.55), top], (120, 92, 70), 16)
    for dx, dy in ((-150, 40), (-110, -30), (-40, -60), (60, -50), (120, -10), (150, 50)):
        pen.line([top, (top[0] + dx * 0.5, top[1] + dy * 0.4 - 30), (top[0] + dx, top[1] + dy + 30)], (86, 150, 96), 14)


def floating_market(W: int, H: int) -> Image.Image:
    sky = vgradient(W, H, [(0, (255, 205, 160)), (0.16, (255, 230, 196)), (0.36, (204, 232, 236)), (1, (204, 232, 236))])
    pen = Pen(W, H, base=sky)
    water_y, dock_y = 0.36 * H, 0.60 * H
    hills(pen, 0, W, 0.30 * H, 0.02 * H, (172, 206, 156), period=520, bottom=water_y)
    hills(pen, 0, W, 0.33 * H, 0.015 * H, (130, 180, 130), period=380, phase=1.7, bottom=water_y)
    rnd = random.Random(5)
    walls = [(244, 214, 170), (236, 190, 160), (214, 226, 200), (250, 232, 190)]
    roofs = [(200, 96, 80), (170, 110, 76), (96, 130, 150), (210, 150, 70)]
    x = -20
    while x < W:
        _house(pen, x, 0.355 * H, 0.9 * W / 1080, rnd.choice(walls), rnd.choice(roofs))
        x += 150 * W / 1080
    for px, lean in ((0.08 * W, 40), (0.93 * W, -50)):
        _palm(pen, px, 0.355 * H, 0.2 * H, lean)
    pen.vgrad_rect(0, water_y, W, dock_y + 4, [(0, (112, 176, 170)), (1, (74, 130, 130))])
    for _ in range(70):
        rx, ry = rnd.uniform(0, W), rnd.uniform(water_y + 8, dock_y - 8)
        ln = rnd.uniform(26, 90) * (0.5 + (ry - water_y) / (dock_y - water_y))
        pen.line([(rx, ry), (rx + ln, ry)], (190, 226, 220), 3)
    k = W / 1080
    _boat(pen, 0.20 * W, 0.43 * H, 0.55 * k, (190, 120, 76), [(244, 200, 70), (240, 130, 70)], (230, 90, 100))
    _boat(pen, 0.78 * W, 0.455 * H, 0.62 * k, (150, 100, 70), [(120, 180, 90), (244, 190, 60), (230, 100, 80)], (80, 160, 200))
    _boat(pen, 0.52 * W, 0.50 * H, 0.8 * k, (176, 112, 74), [(250, 210, 80), (240, 150, 60), (120, 180, 90)], (240, 180, 70))
    _boat(pen, 0.10 * W, 0.555 * H, 1.0 * k, (162, 104, 70), [(230, 90, 80), (244, 200, 70), (120, 180, 90)], None)
    pen.rect(0, dock_y, W, H, INK)
    pen.rect(0, dock_y + 6, W, H, (176, 128, 88))
    step = 0.055 * H
    y = dock_y + step
    while y < H:
        pen.line([(0, y), (W, y)], (130, 92, 62), 4)
        y += step
    for i, jx in enumerate(range(0, W + 1, int(220 * k))):
        yy = dock_y + step * (i % 2)
        pen.line([(jx, yy), (jx, yy + step)], (130, 92, 62), 4)
    for px in (0.04 * W, 0.96 * W):
        pen.rect(px - 20 * k, dock_y - 120 * k, px + 20 * k, dock_y + 30 * k, (112, 80, 58), outline=INK, width=4)
    img = pen.result().convert("RGB")
    img = add_glow(img, 0.8 * W, 0.12 * H, 0.35 * W, (255, 244, 214), 0.45)
    dark = Image.new("RGB", (W, H), (28, 20, 22))  # darken the dock so subtitles read well
    mask = Image.linear_gradient("L").resize((W, H - int(0.68 * H)))
    full = Image.new("L", (W, H), 0)
    full.paste(mask.point(lambda v: int(v * 0.55)), (0, int(0.68 * H)))
    return Image.composite(dark, img, full)


BACKGROUNDS = {"floating_market": floating_market}
FX = {}  # name -> fn(img, t, scene_duration, W, H, **params) -> img, applied per frame


def register(name, fn):
    BACKGROUNDS[name] = fn


def shade(c, f):
    return tuple(max(0, min(255, int(v * f))) for v in c[:3])


def subtitles_text(pen, x, y, text, size, fill):
    """Thai text drawn with the local Thai font (never by a model, so it can't be misspelled)."""
    from subtitles import font
    pen.d.text((x * pen.ss, y * pen.ss), text, font=font(int(size * pen.ss)), fill=fill, anchor="mm",
               stroke_width=int(3 * pen.ss), stroke_fill=INK)


def get(name: str, W: int, H: int) -> Image.Image:
    if name not in BACKGROUNDS:
        raise KeyError(f"unknown background '{name}' (have: {', '.join(BACKGROUNDS)})")
    cache = HERE / "backgrounds" / f"{name}_{W}x{H}.png"
    if cache.is_file():
        return Image.open(cache).convert("RGB")
    img = BACKGROUNDS[name](W, H)
    cache.parent.mkdir(exist_ok=True)
    img.save(cache)
    return img


if __name__ == "__main__":
    get("floating_market", 1080, 1920).resize((540, 960)).save(HERE / "output" / "bg_test.png")
