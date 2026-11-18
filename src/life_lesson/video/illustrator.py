"""Free, offline scene illustration: flat-vector style drawn with Pillow.

No image API and no cost. Each scene is drawn from its `setting`, `mood` and the
characters present (outfit colours from the character sheet), so the picture
matches the story and stays consistent across chapters. It is deliberately a
simple, stylised look (layered silhouettes, glowing lights, flat figures), not
hand-painted animation -- a paid image/animation model can replace
`illustrate_scene` later without touching the rest of the pipeline.
"""

from __future__ import annotations

import hashlib
import math
import random
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

from life_lesson.generation.atmosphere import BlockMood

SETTINGS = ("room", "office", "street", "city", "sea", "island", "forest", "night_sky")

# visual_cue keywords (Thai + English) -> setting, first hit wins
_KEYWORDS: list[tuple[str, tuple[str, ...]]] = [
    ("island", ("เกาะ", "island", "ชายหาด", "beach", "เรือแตก")),
    ("sea", ("ทะเล", "เรือ", "คลื่น", "sea", "boat", "ocean", "ท่าเรือ")),
    ("forest", ("ป่า", "ต้นไม้", "forest", "woods", "ภูเขา")),
    ("office", ("ออฟฟิศ", "office", "ที่ทำงาน", "ประชุม", "ลิฟต์", "ห้าง")),
    ("street", ("ถนน", "ซอย", "street", "ป้ายรถ", "ทางเท้า", "ร้านสะดวกซื้อ")),
    ("city", ("เมือง", "ตึก", "city", "skyline", "ดาดฟ้า", "คอนโด")),
    ("night_sky", ("ดาว", "ท้องฟ้า", "sky", "พระจันทร์")),
    ("room", ("ห้อง", "บ้าน", "เตียง", "โต๊ะ", "room", "bed", "desk", "ครัว", "หน้าจอ", "มือถือ")),
]

_COLOR_WORDS = {
    "เหลือง": (240, 196, 40), "yellow": (240, 196, 40), "แดง": (206, 52, 48), "red": (206, 52, 48),
    "ส้ม": (232, 128, 40), "orange": (232, 128, 40), "ฟ้า": (96, 168, 224), "sky": (96, 168, 224),
    "น้ำเงิน": (40, 70, 150), "blue": (40, 70, 150), "เขียว": (60, 150, 90), "green": (60, 150, 90),
    "ชมพู": (232, 130, 170), "pink": (232, 130, 170), "ม่วง": (130, 80, 170), "purple": (130, 80, 170),
    "ขาว": (236, 236, 230), "white": (236, 236, 230), "ดำ": (34, 34, 40), "black": (34, 34, 40),
    "เทา": (130, 134, 140), "gray": (130, 134, 140), "grey": (130, 134, 140),
    "น้ำตาล": (120, 80, 50), "brown": (120, 80, 50), "ครีม": (232, 220, 190), "cream": (232, 220, 190),
}


def infer_setting(visual_cue: str | None, explicit: str | None = None) -> str:
    if explicit in SETTINGS:
        return explicit  # type: ignore[return-value]
    text = (visual_cue or "").lower()
    for setting, words in _KEYWORDS:
        if any(w in text for w in words):
            return setting
    return "room"


def color_from_text(text: str | None, fallback_seed: str = "") -> tuple[int, int, int]:
    low = (text or "").lower()
    for word, rgb in _COLOR_WORDS.items():
        if word in low:
            return rgb
    h = hashlib.md5((text or fallback_seed).encode("utf-8")).digest()
    return (60 + h[0] % 150, 60 + h[1] % 150, 60 + h[2] % 150)


def _hex(value: str) -> tuple[int, int, int] | None:
    v = value.strip().lstrip("#")
    if re.fullmatch(r"[0-9a-fA-F]{6}", v):
        return tuple(int(v[i : i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]
    return None


def character_colors(outfit: str | None, palette: list[str] | None, name: str = "") -> dict:
    main = None
    for p in palette or []:
        main = _hex(p) or color_from_text(p) if any(c in (p or "").lower() for c in _COLOR_WORDS) or _hex(p) else main
        if main:
            break
    main = main or color_from_text(outfit, name)
    h = hashlib.md5(name.encode("utf-8")).digest()
    hair = [(30, 24, 22), (58, 40, 30), (24, 24, 30), (88, 60, 40)][h[0] % 4]
    skin = [(236, 200, 170), (214, 170, 130), (190, 140, 100)][h[1] % 3]
    accent = (240, 196, 40) if sum(main) < 380 else (206, 52, 48)
    return {"outfit": main, "hair": hair, "skin": skin, "accent": accent}


# -- drawing helpers ---------------------------------------------------------

def _lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def _gradient(size, top, bottom):
    w, h = size
    img = Image.new("RGB", size)
    d = ImageDraw.Draw(img)
    for y in range(h):
        d.line([(0, y), (w, y)], fill=_lerp(top, bottom, y / max(1, h - 1)))
    return img


def _glow(base: Image.Image, center, radius, color, strength=0.9):
    layer = Image.new("RGB", base.size, (0, 0, 0))
    d = ImageDraw.Draw(layer)
    cx, cy = center
    d.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill=tuple(int(c * strength) for c in color))
    layer = layer.filter(ImageFilter.GaussianBlur(radius * 0.55))
    return Image.blend(base, Image.composite(layer, base, Image.new("L", base.size, 255)), 0) if False else _screen(base, layer)


def _screen(a: Image.Image, b: Image.Image) -> Image.Image:
    from PIL import ImageChops

    return ImageChops.screen(a, b)


def _is_night(mood: BlockMood | None) -> bool:
    return mood is None or mood.light in ("dim", "dark", "neon", "flicker")


def _sky_colors(mood: BlockMood | None):
    light = mood.light if mood else "dim"
    if light == "bright":
        return (110, 168, 222), (226, 226, 214)
    if light == "golden":
        return (232, 150, 90), (252, 222, 160)
    if light == "dark":
        return (8, 12, 26), (26, 36, 62)
    if light == "neon":
        return (24, 14, 46), (70, 34, 90)
    return (16, 24, 46), (52, 66, 104)  # dim / flicker


def _stars(d: ImageDraw.ImageDraw, rng, w, h_limit, n=70):
    for _ in range(n):
        x, y = rng.randrange(w), rng.randrange(max(1, int(h_limit)))
        r = rng.choice((1, 1, 2))
        d.ellipse([x - r, y - r, x + r, y + r], fill=(220, 226, 240))


def _moon(img, center, r):
    d = ImageDraw.Draw(img)
    img.paste(_glow(img, center, r * 3, (90, 100, 130), 0.8))
    d = ImageDraw.Draw(img)
    cx, cy = center
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(238, 238, 224))
    d.ellipse([cx - r * 0.35, cy - r * 0.2, cx + r * 0.05, cy + r * 0.2], fill=(222, 222, 206))


def _skyline(d, rng, w, base_y, h_range, color, win_color, lit_p, bw=(40, 110)):
    x = -20
    while x < w + 20:
        bwid = rng.randrange(*bw)
        bh = rng.randrange(*h_range)
        d.rectangle([x, base_y - bh, x + bwid, base_y + 4], fill=color)
        if win_color and lit_p > 0:
            for wy in range(base_y - bh + 14, base_y - 8, 22):
                for wx in range(x + 8, x + bwid - 10, 18):
                    if rng.random() < lit_p:
                        d.rectangle([wx, wy, wx + 8, wy + 11], fill=win_color)
        x += bwid + rng.randrange(0, 8)


def _tree(d, x, base_y, h, color, kind="pine"):
    if kind == "palm":
        d.line([(x, base_y), (x + h * 0.12, base_y - h)], fill=color, width=max(4, int(h * 0.05)))
        tip = (x + h * 0.12, base_y - h)
        for ang in (-150, -115, -75, -35, -170, -10):
            a = math.radians(ang)
            ex, ey = tip[0] + math.cos(a) * h * 0.5, tip[1] + math.sin(a) * h * 0.25 + h * 0.12
            d.polygon([tip, (tip[0] + math.cos(a) * h * 0.25, tip[1] - h * 0.07), (ex, ey)], fill=color)
        return
    for i in range(3):
        top = base_y - h + i * h * 0.22
        wid = h * (0.22 + i * 0.1)
        d.polygon([(x, top), (x - wid, top + h * 0.38), (x + wid, top + h * 0.38)], fill=color)
    d.rectangle([x - h * 0.03, base_y - h * 0.12, x + h * 0.03, base_y], fill=color)


def _lamp_post(img, d, x, base_y, h, night):
    d.rectangle([x - 3, base_y - h, x + 3, base_y], fill=(24, 26, 34))
    d.rectangle([x - 14, base_y - h - 6, x + 14, base_y - h + 4], fill=(24, 26, 34))
    if night:
        return (x, base_y - h + 8)
    return None


EXPRESSIONS = ("neutral", "soft", "smile", "worried", "wide")


def expression_for(mood: BlockMood | None) -> str:
    """Face that matches the scene's feeling (tension + narrator voice)."""
    if mood is None:
        return "neutral"
    if mood.tension >= 5 or mood.voice == "urgent":
        return "wide"
    if mood.tension >= 4 or mood.voice == "tense":
        return "worried"
    if mood.voice == "warm":
        return "smile"
    if mood.voice in ("hushed", "wistful"):
        return "soft"
    return "neutral"


def _draw_face(d, x, head_y, s, expression: str):
    ink = (34, 28, 30)
    ey = head_y - 1 * s
    wide = expression == "wide"
    for sign in (-1, 1):
        cx = x + sign * 7.5 * s
        rw, rh = (5.0, 5.8) if wide else (3.8, 4.4)
        d.ellipse([cx - rw * s, ey - rh * s, cx + rw * s, ey + rh * s], fill=(252, 250, 246))
        look = 0.8 * s * sign * -0.0  # looking straight at the viewer
        pr = 2.3 * s if not wide else 1.9 * s
        d.ellipse([cx - pr + look, ey - pr, cx + pr + look, ey + pr], fill=ink)
        # eyebrow: outer end at sign*13, inner end at sign*3
        outer, inner = (x + sign * 13 * s, x + sign * 3 * s)
        by = ey - (9.5 if wide else 8.5) * s
        if expression in ("worried", "wide"):
            o_y, i_y = by + 2.5 * s, by - 2.5 * s      # inner ends raised: worry
        elif expression == "soft":
            o_y, i_y = by + 1.5 * s, by - 0.8 * s
        elif expression == "smile":
            o_y, i_y = by + 0.5 * s, by - 0.5 * s
        else:
            o_y, i_y = by, by
        d.line([(outer, o_y), (inner, i_y)], fill=ink, width=max(2, int(1.8 * s)))
    my = head_y + 10 * s
    w = max(2, int(1.8 * s))
    if expression == "smile":
        d.arc([x - 7 * s, my - 6 * s, x + 7 * s, my + 5 * s], 15, 165, fill=ink, width=w)
        for sign in (-1, 1):  # blush
            d.ellipse([x + sign * 11 * s - 3 * s, my - 4 * s, x + sign * 11 * s + 3 * s, my - 0.5 * s], fill=(236, 150, 140))
    elif expression == "soft":
        d.arc([x - 5 * s, my - 4 * s, x + 5 * s, my + 3 * s], 20, 160, fill=ink, width=w)
    elif expression == "worried":
        d.arc([x - 5 * s, my - 1 * s, x + 5 * s, my + 6 * s], 200, 340, fill=ink, width=w)
    elif expression == "wide":
        d.ellipse([x - 3.2 * s, my - 2 * s, x + 3.2 * s, my + 5 * s], fill=(120, 40, 44))
    else:
        d.line([(x - 4 * s, my + 1 * s), (x + 4 * s, my + 1 * s)], fill=ink, width=w)


def _draw_character(d, x, ground_y, s, colors, sitting=False, expression="neutral"):
    outfit, hair, skin, accent = colors["outfit"], colors["hair"], colors["skin"], colors["accent"]
    dark = tuple(max(0, c - 40) for c in outfit)
    if sitting:
        # torso + arms resting forward; legs are hidden behind the desk / boat
        d.rounded_rectangle([x - 24 * s, ground_y - 112 * s, x + 24 * s, ground_y - 4 * s], 14 * s, fill=outfit)
        d.rounded_rectangle([x + 10 * s, ground_y - 98 * s, x + 54 * s, ground_y - 80 * s], 8 * s, fill=outfit)
        head_y = ground_y - 138 * s
    else:
        d.rectangle([x - 14 * s, ground_y - 62 * s, x - 3 * s, ground_y], fill=dark)
        d.rectangle([x + 3 * s, ground_y - 62 * s, x + 14 * s, ground_y], fill=dark)
        d.rounded_rectangle([x - 22 * s, ground_y - 128 * s, x + 22 * s, ground_y - 54 * s], 12 * s, fill=outfit)
        d.rounded_rectangle([x - 30 * s, ground_y - 124 * s, x - 20 * s, ground_y - 70 * s], 5 * s, fill=outfit)
        d.rounded_rectangle([x + 20 * s, ground_y - 124 * s, x + 30 * s, ground_y - 70 * s], 5 * s, fill=outfit)
        head_y = ground_y - 152 * s
    d.rectangle([x - 5 * s, head_y + 16 * s, x + 5 * s, head_y + 28 * s], fill=skin)
    d.ellipse([x - 17 * s, head_y - 18 * s, x + 17 * s, head_y + 20 * s], fill=skin)
    d.pieslice([x - 19 * s, head_y - 24 * s, x + 19 * s, head_y + 14 * s], 180, 360, fill=hair)
    d.rectangle([x - 19 * s, head_y - 8 * s, x - 13 * s, head_y + 6 * s], fill=hair)
    _draw_face(d, x, head_y, s, expression)
    # signature item: a small accent-coloured object in hand / at the side
    d.rounded_rectangle([x + 26 * s, ground_y - 78 * s, x + 38 * s, ground_y - 62 * s], 3 * s, fill=accent)


# -- scenes --------------------------------------------------------------------

def _scene_background(setting: str, size, mood: BlockMood | None, rng: random.Random):
    w, h = size
    top, bottom = _sky_colors(mood)
    night = _is_night(mood)
    img = _gradient(size, top, bottom)
    d = ImageDraw.Draw(img)
    ground = int(h * 0.78)
    lights: list[tuple[tuple[int, int], int, tuple[int, int, int]]] = []
    seat = None
    fg: list = []  # callables(draw) painted AFTER characters (desks, boat rails)

    if night:
        _stars(d, rng, w, h * 0.5, 60 if setting != "room" else 0)
    if setting in ("city", "street", "sea", "island", "night_sky", "forest") and night:
        _moon(img, (int(w * rng.uniform(0.7, 0.88)), int(h * 0.2)), int(h * 0.06))
        d = ImageDraw.Draw(img)

    far = _lerp(top, (0, 0, 0), 0.25) if night else _lerp(bottom, (60, 80, 110), 0.5)
    near = _lerp(top, (0, 0, 0), 0.6) if night else _lerp(bottom, (40, 50, 70), 0.7)
    win = (250, 214, 120) if night else None

    if setting in ("city", "street", "office"):
        _skyline(d, rng, w, ground - 30, (int(h * 0.18), int(h * 0.42)), far, win, 0.18)
        _skyline(d, rng, w, ground, (int(h * 0.1), int(h * 0.3)), near, win, 0.3, bw=(60, 150))
        d.rectangle([0, ground, w, h], fill=_lerp(near, (0, 0, 0), 0.3))
        d.rectangle([0, ground, w, ground + 8], fill=_lerp(near, (255, 255, 255), 0.12))
        if setting == "street":
            for lx in (int(w * 0.15), int(w * 0.5), int(w * 0.85)):
                spot = _lamp_post(img, d, lx, ground, int(h * 0.3), night)
                if spot:
                    lights.append((spot, int(h * 0.18), (255, 214, 130)))
        if setting == "office":
            fg.append(lambda dd: (
                dd.rectangle([int(w * 0.1), ground - 40, int(w * 0.62), ground - 22], fill=(54, 40, 34)),
                dd.rectangle([int(w * 0.1), ground - 22, int(w * 0.62), h], fill=(40, 30, 28)),
                dd.rectangle([int(w * 0.36), ground - 108, int(w * 0.5), ground - 44], fill=(24, 28, 36)),
            ))
            lights.append(((int(w * 0.43), ground - 76), int(h * 0.16), (120, 190, 255)))
            seat = "sit"
    elif setting == "sea" or setting == "island":
        hor = int(h * 0.55)
        sea_top, sea_bot = (_lerp(top, (0, 30, 50), 0.5), _lerp(bottom, (0, 10, 30), 0.6)) if night else ((70, 140, 190), (30, 90, 140))
        img.paste(_gradient((w, h - hor), sea_top, sea_bot), (0, hor))
        d = ImageDraw.Draw(img)
        for i in range(26):
            y = hor + 10 + i * (h - hor) / 26
            x0 = rng.randrange(-80, w)
            L = rng.randrange(60, 220) * (0.4 + (y - hor) / (h - hor))
            d.line([(x0, y), (x0 + L, y)], fill=_lerp(sea_top, (200, 220, 240), 0.35), width=max(2, int((y - hor) / 40)))
        if night:
            mx = int(w * 0.8)
            for i in range(14):
                y = hor + 14 + i * 22
                half = 10 + i * 5
                d.line([(mx - half, y), (mx + half, y)], fill=(150, 160, 185), width=3)
        if setting == "island":
            d.ellipse([int(w * 0.52), hor - int(h * 0.1), int(w * 1.1), hor + int(h * 0.14)], fill=near, outline=_lerp(near, (150, 160, 190), 0.35) if night else None, width=4)
            for i, tx in enumerate((0.64, 0.74, 0.86)):
                _tree(d, int(w * tx), hor - int(h * 0.02), int(h * (0.2 + 0.04 * (i % 2))), near, "palm")
            ground = int(h * 0.86)
            d.rectangle([0, ground, w, h], fill=_lerp((200, 180, 140), (0, 0, 0), 0.55 if night else 0.0))
            lights.append(((int(w * 0.22), ground - 18), int(h * 0.15), (255, 150, 60)))  # campfire
            d.polygon([(int(w * 0.22) - 14, ground), (int(w * 0.22), ground - 36), (int(w * 0.22) + 14, ground)], fill=(255, 170, 70))
        else:
            ground = int(h * 0.80)
            bx0, bx1 = int(w * 0.3), int(w * 0.72)
            fg.append(lambda dd: dd.polygon([(bx0 - 30, ground - 24), (bx1 + 30, ground - 24), (bx1 - 10, ground + 40), (bx0 + 10, ground + 40)], fill=(78, 54, 40)))
            seat = "boat"
    elif setting == "forest":
        for layer, (col, n, hh) in enumerate([(far, 14, 0.5), (near, 11, 0.62)]):
            for _ in range(n):
                _tree(d, rng.randrange(-20, w + 20), ground - layer * 14, int(h * hh * rng.uniform(0.7, 1.1)), col)
        fog = Image.new("RGB", size, (0, 0, 0))
        ImageDraw.Draw(fog).rectangle([0, int(h * 0.55), w, int(h * 0.78)], fill=_lerp(bottom, (30, 40, 50), 0.4))
        img = _screen(img, fog.filter(ImageFilter.GaussianBlur(30)))
        d = ImageDraw.Draw(img)
        d.rectangle([0, ground, w, h], fill=_lerp(near, (0, 0, 0), 0.4))
    elif setting == "night_sky":
        d.ellipse([-w * 0.2, ground - 40, w * 1.2, h * 1.6], fill=near)
    else:  # room
        wall = (46, 40, 52) if night else (214, 200, 180)
        d.rectangle([0, 0, w, ground], fill=wall)
        d.rectangle([0, ground, w, h], fill=_lerp(wall, (0, 0, 0), 0.45))
        wx0, wy0, wx1, wy1 = int(w * 0.58), int(h * 0.14), int(w * 0.86), int(h * 0.56)
        d.rectangle([wx0 - 10, wy0 - 10, wx1 + 10, wy1 + 10], fill=(22, 20, 26))
        sky = _gradient((wx1 - wx0, wy1 - wy0), top, bottom)
        img.paste(sky, (wx0, wy0))
        d = ImageDraw.Draw(img)
        if night:
            _stars(ImageDraw.Draw(img), rng, 0, 0, 0)
        d.line([((wx0 + wx1) // 2, wy0), ((wx0 + wx1) // 2, wy1)], fill=(22, 20, 26), width=8)
        d.line([(wx0, (wy0 + wy1) // 2), (wx1, (wy0 + wy1) // 2)], fill=(22, 20, 26), width=8)
        lx, ly = int(w * 0.40), ground - 40

        def desk(dd):
            dd.rectangle([int(w * 0.06), ground - 40, int(w * 0.46), ground - 22], fill=(96, 70, 52))
            dd.rectangle([int(w * 0.06), ground - 22, int(w * 0.46), h], fill=(60, 44, 36))
            dd.line([(lx, ly), (lx + 16, ly - 70), (lx - 14, ly - 120)], fill=(34, 34, 40), width=7)
            dd.polygon([(lx - 40, ly - 120), (lx + 8, ly - 120), (lx - 2, ly - 92), (lx - 32, ly - 92)], fill=(34, 34, 40))

        fg.append(desk)
        lights.append(((lx - 16, ly - 90), int(h * 0.3), (255, 196, 110) if night else (255, 236, 190)))
        seat = "sit"
    return img, ground, lights, seat, fg


def illustrate_scene(
    size: tuple[int, int],
    *,
    setting: str,
    mood: BlockMood | None,
    characters: list[dict] | None,
    seed: str = "",
    out_path: Path | None = None,
) -> Image.Image:
    """Draw one scene. `characters` = list of dicts from `character_colors`."""
    ss = 2  # supersample for smooth edges
    w, h = size[0] * ss, size[1] * ss
    rng = random.Random(int(hashlib.md5(f"{seed}{setting}".encode()).hexdigest(), 16) % (2**32))
    img, ground, lights, seat, fg = _scene_background(setting, (w, h), mood, rng)

    # characters (standing on the ground line, or sitting at the desk/boat)
    figs = characters or []
    n = len(figs)
    s = h / 720 * 1.3
    face = expression_for(mood)
    for i, col in enumerate(figs):
        x = int(w * (0.5 if n == 1 else 0.3 + 0.4 * i / max(1, n - 1)))
        if setting in ("room", "office"):
            x = int(w * (0.22 + 0.1 * i))
        d = ImageDraw.Draw(img)
        _draw_character(d, x, ground - 22 if seat == "sit" else (ground - 4 if seat == "boat" else ground),
                        s * (1.1 if seat else 1.0), col, sitting=seat is not None, expression=face)

    d = ImageDraw.Draw(img)
    for paint in fg:
        paint(d)
    night = _is_night(mood)
    for center, radius, color in lights:
        if night or setting in ("island",):
            img = _glow(img, center, radius, color, 0.75)

    img = img.resize(size, Image.LANCZOS)
    if out_path is not None:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(out_path)
    return img
