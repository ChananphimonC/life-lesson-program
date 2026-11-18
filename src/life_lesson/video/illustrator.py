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

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from life_lesson.generation.atmosphere import BlockMood
from life_lesson.video.scene_kb import SceneRecipe, retrieve_recipe

SETTINGS = ("room", "office", "street", "city", "sea", "island", "forest", "night_sky", "food_stall")

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
    return retrieve_recipe(visual_cue).setting


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


ITEMS = ("apron", "cap", "hairnet", "glasses", "backpack", "hood", "lanyard", "towel")
_ITEM_WORDS = {
    "apron": ("เอี๊ยม", "ผ้ากันเปื้อน", "apron"),
    "cap": ("หมวก", "cap", "hat"),
    "hairnet": ("ตาข่ายคลุมผม", "ผ้าคลุมผม", "hairnet"),
    "glasses": ("แว่น", "glasses"),
    "backpack": ("กระเป๋าเป้", "เป้", "backpack"),
    "hood": ("ฮู้ด", "hood", "เสื้อกันฝน", "raincoat"),
    "lanyard": ("สายคล้องคอ", "บัตรนักศึกษา", "บัตรพนักงาน", "lanyard"),
    "towel": ("ผ้าขนหนู", "ผ้าเช็ดมือ", "towel"),
}
_SHORT_SLEEVE_WORDS = ("แขนสั้น", "โปโล", "เสื้อยืด", "t-shirt", "polo", "short sleeve")


def items_from_text(text: str | None) -> set[str]:
    low = (text or "").lower()
    return {item for item, words in _ITEM_WORDS.items() if any(w in low for w in words)}


def character_colors(
    outfit: str | None,
    palette: list[str] | None,
    name: str = "",
    extra_items: tuple[str, ...] | list[str] = (),
    sleeve: str | None = None,
) -> dict:
    main = None
    for pal in palette or []:
        main = _hex(pal) or (color_from_text(pal) if any(c in (pal or "").lower() for c in _COLOR_WORDS) else None)
        if main:
            break
    main = main or color_from_text(outfit, name)
    h = hashlib.md5(name.encode("utf-8")).digest()
    hair = [(30, 24, 22), (58, 40, 30), (24, 24, 30), (88, 60, 40)][h[0] % 4]
    skin = [(236, 200, 170), (214, 170, 130), (190, 140, 100)][h[1] % 3]
    accent = (240, 196, 40) if sum(main) < 380 else (206, 52, 48)
    items = tuple(sorted(items_from_text(outfit) | set(extra_items)))
    if sleeve is None:
        sleeve = "short" if any(w in (outfit or "").lower() for w in _SHORT_SLEEVE_WORDS) else "long"
    return {"outfit": main, "hair": hair, "skin": skin, "accent": accent, "items": items, "sleeve": sleeve}


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


def _ik(shoulder, target, upper, fore):
    """Two-bone arm: returns (elbow, hand) so bone lengths hold and the elbow points down."""
    sx, sy = shoulder
    tx, ty = target
    dx, dy = tx - sx, ty - sy
    d = math.hypot(dx, dy) or 1e-6
    reach = upper + fore - 0.5
    if d > reach:
        k = reach / d
        tx, ty, dx, dy, d = sx + dx * k, sy + dy * k, dx * k, dy * k, reach
    a = (upper * upper - fore * fore + d * d) / (2 * d)
    hh = math.sqrt(max(0.0, upper * upper - a * a))
    bx, by = sx + dx / d * a, sy + dy / d * a
    nx, ny = -dy / d, dx / d
    c1, c2 = (bx + nx * hh, by + ny * hh), (bx - nx * hh, by - ny * hh)
    return (c1 if c1[1] > c2[1] else c2), (tx, ty)


def _limb(d, p, q, width, color):
    d.line([p, q], fill=color, width=max(2, int(width)))
    r = width / 2
    for cx, cy in (p, q):
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)


def _draw_arm(d, shoulder, target, s, colors):
    outfit, skin = colors["outfit"], colors["skin"]
    short = colors.get("sleeve") == "short"
    U = F = 30 * s
    elbow, hand = _ik(shoulder, target, U, F)
    _limb(d, shoulder, elbow, 12.5 * s, outfit)
    fore_color = skin if short else outfit
    _limb(d, elbow, hand, 10 * s, fore_color)
    if short:  # sleeve hem covers the top of the forearm
        k = 0.22
        hem = (elbow[0] + (hand[0] - elbow[0]) * k, elbow[1] + (hand[1] - elbow[1]) * k)
        _limb(d, elbow, hem, 12 * s, outfit)
    hx, hy = hand
    d.ellipse([hx - 6.6 * s, hy - 6.6 * s, hx + 6.6 * s, hy + 6.6 * s], fill=skin)           # palm
    d.ellipse([hx - 1.5 * s, hy + 3 * s, hx + 5.5 * s, hy + 9 * s], fill=skin)               # fingers curled
    return hand


def _draw_character(d, x, ground_y, s, colors, sitting=False, expression="neutral", hands=None, items=None):
    """`hands` = {"L": (x, y), "R": (x, y)} screen-side targets in pixels; default pose if None."""
    outfit, hair, skin, accent = colors["outfit"], colors["hair"], colors["skin"], colors["accent"]
    items = set(items if items is not None else colors.get("items", ()))
    dark = tuple(max(0, c - 40) for c in outfit)
    light = tuple(min(255, c + 50) for c in outfit)

    if sitting:
        torso_top, torso_bot, head_y = ground_y - 112 * s, ground_y - 4 * s, ground_y - 138 * s
    else:
        torso_top, torso_bot, head_y = ground_y - 128 * s, ground_y - 54 * s, ground_y - 152 * s
    shoulder_y = torso_top + 9 * s

    if "backpack" in items:  # behind the body
        bp = tuple(max(0, c - 70) for c in accent)
        d.rounded_rectangle([x - 30 * s, torso_top + 4 * s, x + 30 * s, torso_bot - 4 * s], 10 * s, fill=(58, 62, 78))
    if not sitting:
        d.rectangle([x - 14 * s, ground_y - 62 * s, x - 3 * s, ground_y], fill=dark)
        d.rectangle([x + 3 * s, ground_y - 62 * s, x + 14 * s, ground_y], fill=dark)
        for sign in (-1, 1):  # shoes / rubber sandals
            d.rounded_rectangle([x + sign * 8.5 * s - 10 * s, ground_y - 5 * s, x + sign * 8.5 * s + 10 * s, ground_y + 2 * s], 3 * s, fill=(36, 36, 44))
    d.rounded_rectangle([x - 22 * s, torso_top, x + 22 * s, torso_bot], 12 * s, fill=outfit)

    if "apron" in items:
        ap = (60, 62, 76) if sum(outfit) > 560 else (236, 230, 214)
        d.polygon([(x - 13 * s, torso_top + 6 * s), (x + 13 * s, torso_top + 6 * s),
                   (x + 21 * s, torso_bot), (x - 21 * s, torso_bot)], fill=ap)
        d.line([(x - 13 * s, torso_top + 6 * s), (x - 7 * s, torso_top - 8 * s)], fill=ap, width=max(2, int(3 * s)))
        d.line([(x + 13 * s, torso_top + 6 * s), (x + 7 * s, torso_top - 8 * s)], fill=ap, width=max(2, int(3 * s)))
        d.rounded_rectangle([x - 9 * s, torso_bot - 26 * s, x + 9 * s, torso_bot - 10 * s], 3 * s, outline=tuple(max(0, c - 40) for c in ap), width=max(1, int(1.5 * s)))
    if "lanyard" in items:
        d.line([(x - 6 * s, torso_top - 4 * s), (x, torso_top + 30 * s)], fill=accent, width=max(2, int(2 * s)))
        d.line([(x + 6 * s, torso_top - 4 * s), (x, torso_top + 30 * s)], fill=accent, width=max(2, int(2 * s)))
        d.rounded_rectangle([x - 7 * s, torso_top + 30 * s, x + 7 * s, torso_top + 46 * s], 2 * s, fill=(245, 245, 240))
        d.rectangle([x - 7 * s, torso_top + 30 * s, x + 7 * s, torso_top + 34 * s], fill=accent)
    if "backpack" in items:
        for sign in (-1, 1):
            d.line([(x + sign * 12 * s, torso_top + 2 * s), (x + sign * 15 * s, torso_bot - 6 * s)], fill=(58, 62, 78), width=max(3, int(5 * s)))

    # arms (default: hanging at the sides, or forearms forward when seated)
    sh_l, sh_r = (x - 22 * s, shoulder_y), (x + 22 * s, shoulder_y)
    if hands is None:
        if sitting:
            hands = {"L": (x - 6 * s, ground_y - 22 * s), "R": (x + 40 * s, ground_y - 22 * s)}
        else:
            hands = {"L": (x - 27 * s, shoulder_y + 58 * s), "R": (x + 27 * s, shoulder_y + 58 * s)}
    hand_pos = {"L": _draw_arm(d, sh_l, hands["L"], s, colors), "R": _draw_arm(d, sh_r, hands["R"], s, colors)}
    if "towel" in items:
        d.rounded_rectangle([x - 30 * s, torso_top - 2 * s, x - 14 * s, torso_top + 30 * s], 3 * s, fill=(190, 214, 232))
        for k in range(3):
            d.line([(x - 30 * s, torso_top + (6 + 8 * k) * s), (x - 14 * s, torso_top + (6 + 8 * k) * s)], fill=(120, 160, 196), width=max(1, int(1.5 * s)))

    # neck + head
    if "hood" in items:
        d.ellipse([x - 26 * s, head_y - 26 * s, x + 26 * s, head_y + 24 * s], fill=outfit)
        d.polygon([(x - 26 * s, head_y + 4 * s), (x + 26 * s, head_y + 4 * s), (x + 20 * s, torso_top + 8 * s), (x - 20 * s, torso_top + 8 * s)], fill=outfit)
    d.rectangle([x - 5 * s, head_y + 16 * s, x + 5 * s, head_y + 28 * s], fill=skin)
    d.ellipse([x - 17 * s, head_y - 18 * s, x + 17 * s, head_y + 20 * s], fill=skin)
    if "hood" not in items:
        d.pieslice([x - 19 * s, head_y - 24 * s, x + 19 * s, head_y + 14 * s], 180, 360, fill=hair)
        d.rectangle([x - 19 * s, head_y - 8 * s, x - 13 * s, head_y + 6 * s], fill=hair)
    else:
        d.pieslice([x - 18 * s, head_y - 21 * s, x + 18 * s, head_y + 4 * s], 180, 360, fill=outfit)
    if "hairnet" in items:
        net = (232, 232, 238)
        d.pieslice([x - 20 * s, head_y - 26 * s, x + 20 * s, head_y + 16 * s], 180, 360, outline=net, width=max(2, int(2 * s)))
        for k in range(-2, 3):
            d.line([(x + k * 7 * s, head_y - 24 * s), (x + k * 5 * s, head_y - 6 * s)], fill=net, width=max(1, int(1 * s)))
    if "cap" in items:
        d.pieslice([x - 20 * s, head_y - 28 * s, x + 20 * s, head_y + 8 * s], 180, 360, fill=accent)
        d.rounded_rectangle([x - 22 * s, head_y - 6 * s, x + 24 * s, head_y - 1 * s], 2 * s, fill=tuple(max(0, c - 40) for c in accent))
    _draw_face(d, x, head_y, s, expression)
    if "glasses" in items:
        ey = head_y - 1 * s
        for sign in (-1, 1):
            d.ellipse([x + sign * 7.5 * s - 7 * s, ey - 7 * s, x + sign * 7.5 * s + 7 * s, ey + 7 * s], outline=(30, 30, 36), width=max(2, int(1.8 * s)))
        d.line([(x - 0.5 * s, ey), (x + 0.5 * s, ey)], fill=(30, 30, 36), width=max(2, int(1.8 * s)))
    return hand_pos


# -- scenes --------------------------------------------------------------------

def _scene_background(setting: str, size, mood: BlockMood | None, rng: random.Random, fig_s: float = 1.0, font_path: Path | None = None, ref=()):
    w, h = size
    top, bottom = _sky_colors(mood)
    if ref:  # reference photos nudge the palette toward real-world colour
        top, bottom = _lerp(top, ref[0], 0.18), _lerp(bottom, ref[min(1, len(ref) - 1)], 0.18)
    night = _is_night(mood)
    img = _gradient(size, top, bottom)
    d = ImageDraw.Draw(img)
    ground = int(h * 0.78)
    lights: list[tuple[tuple[int, int], int, tuple[int, int, int]]] = []
    seat = None
    fg: list = []  # callables(draw) painted AFTER characters (desks, boat rails)
    info: dict = {}

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
    elif setting == "food_stall":
        img, ground, lights, fg, info = _food_stall(img, size, mood, rng, fig_s, font_path, night, ref)
        d = ImageDraw.Draw(img)
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
    return img, ground, lights, seat, fg, info


def _flame(d, cx, base_y, s, scale=1.0):
    for dx, hh, col in ((-34, 30, (255, 120, 30)), (-12, 44, (255, 150, 40)), (12, 40, (255, 140, 30)), (34, 28, (255, 110, 30)), (0, 26, (255, 214, 90))):
        w = 11 * s * scale
        top = base_y - hh * s * scale
        cx2 = cx + dx * s * scale
        d.polygon([(cx2 - w, base_y), (cx2 - w * 0.4, top + hh * s * 0.35), (cx2, top), (cx2 + w * 0.4, top + hh * s * 0.35), (cx2 + w, base_y)], fill=col)


def _plate_kaprao(d, cx, cy, s):
    d.ellipse([cx - 42 * s, cy - 11 * s, cx + 42 * s, cy + 13 * s], fill=(246, 246, 240), outline=(200, 200, 196), width=max(1, int(1.5 * s)))
    d.ellipse([cx - 40 * s, cy - 24 * s, cx - 2 * s, cy + 2 * s], fill=(252, 250, 242))             # rice
    d.ellipse([cx - 6 * s, cy - 26 * s, cx + 36 * s, cy + 2 * s], fill=(120, 74, 46))                # minced pork
    rnd = random.Random(7)
    for _ in range(14):  # holy basil leaves + chilies
        px, py = cx - 2 * s + rnd.uniform(-2, 36) * s * 0.9, cy - 14 * s + rnd.uniform(-10, 8) * s
        d.ellipse([px - 3.2 * s, py - 2 * s, px + 3.2 * s, py + 2 * s], fill=(50, 120, 56))
    for k in range(4):
        px, py = cx + (4 + k * 8) * s, cy - 18 * s + (k % 2) * 7 * s
        d.ellipse([px - 2.5 * s, py - 1.3 * s, px + 2.5 * s, py + 1.3 * s], fill=(206, 52, 40))
    d.ellipse([cx - 20 * s, cy - 8 * s, cx + 8 * s, cy + 11 * s], fill=(252, 250, 244))              # fried egg
    d.ellipse([cx - 10 * s, cy - 3 * s, cx - 2 * s, cy + 5 * s], fill=(248, 178, 28))                # yolk


def _food_stall(img, size, mood, rng, s, font_path, night, ref=()):
    """Roadside made-to-order shop (ร้านตามสั่ง): shopfront, counter, wok on flame,
    steam, menu board, plastic stools and a plate of pad kaprao."""
    w, h = size
    d = ImageDraw.Draw(img)
    ground = int(h * 0.86)
    lights, fg, info = [], [], {}
    wall = (52, 64, 66) if night else (190, 186, 160)
    if ref:
        wall = _lerp(wall, ref[0], 0.22)
    d.rectangle([0, int(h * 0.1), w, ground], fill=wall)
    for x in range(0, w, 46):                                           # rolled-up shutter slats on the side walls
        d.line([(x, int(h * 0.1)), (x, ground)], fill=tuple(max(0, c - 10) for c in wall), width=2)
    d.rectangle([0, ground, w, h], fill=(44, 44, 50) if night else (120, 118, 112))   # concrete floor
    # striped awning
    aw_h = int(h * 0.1)
    stripe = int(w / 14)
    for i in range(15):
        d.rectangle([i * stripe, 0, (i + 1) * stripe, aw_h], fill=(196, 46, 44) if i % 2 == 0 else (240, 236, 226))
    d.rectangle([0, aw_h, w, aw_h + 8], fill=(60, 24, 24))
    # menu board
    bx0, by0, bx1, by1 = int(w * 0.06), int(h * 0.2), int(w * 0.36), int(h * 0.36)
    d.rounded_rectangle([bx0, by0, bx1, by1], 10, fill=(176, 38, 38), outline=(250, 226, 150), width=5)
    if font_path:
        try:
            f1 = ImageFont.truetype(str(font_path), int((by1 - by0) * 0.36))
            f2 = ImageFont.truetype(str(font_path), int((by1 - by0) * 0.22))
            d.text((bx0 + 22, by0 + 12), "ผัดกะเพรา", font=f1, fill=(255, 244, 214))
            d.text((bx0 + 22, by0 + int((by1 - by0) * 0.58)), "ราดข้าว ไข่ดาว 50.-", font=f2, fill=(255, 214, 90))
        except OSError:
            pass
    # fluorescent tube
    tx0, tx1, ty = int(w * 0.42), int(w * 0.78), int(h * 0.15)
    d.rounded_rectangle([tx0, ty, tx1, ty + 12], 6, fill=(244, 248, 255))
    lights.append((((tx0 + tx1) // 2, ty + 6), int(h * 0.3), (150, 190, 255)))
    # counter + back shelf bottles
    cook_x = int(w * 0.42)
    counter_y = ground - int(66 * s)
    for i, col in enumerate(((120, 70, 36), (190, 50, 40), (60, 120, 70), (220, 190, 70))):
        bx = int(w * 0.1) + i * int(30 * s)
        d.rounded_rectangle([bx, counter_y - int(44 * s), bx + int(16 * s), counter_y], 5, fill=col)
        d.rectangle([bx + int(4 * s), counter_y - int(54 * s), bx + int(12 * s), counter_y - int(44 * s)], fill=(40, 40, 46))
    # wok handle goes to the cook's right-hand side (screen right) and is drawn BEHIND the character
    wok_x, wok_y, wok_r = cook_x, counter_y - int(30 * s), int(46 * s)   # wok_y = rim centre
    handle_end = (wok_x + wok_r + int(28 * s), wok_y - int(4 * s))
    d.line([(wok_x + wok_r - 6, wok_y), handle_end], fill=(30, 28, 30), width=max(4, int(9 * s)))
    d.line([(wok_x + wok_r + int(10 * s), wok_y - int(2 * s)), handle_end], fill=(130, 84, 48), width=max(6, int(12 * s)))
    # small table + stools + plate on the right
    tx = int(w * 0.865)
    table_y = ground - int(44 * s)
    d.rectangle([tx - int(60 * s), table_y, tx + int(60 * s), table_y + int(10 * s)], fill=(206, 60, 52))
    for lx in (-50, 50):
        d.rectangle([tx + int(lx * s) - 3, table_y + int(10 * s), tx + int(lx * s) + 3, ground], fill=(150, 150, 156))
    _plate_kaprao(d, tx - int(10 * s), table_y - int(2 * s), s * 0.95)
    d.rounded_rectangle([tx + int(34 * s), table_y - int(18 * s), tx + int(52 * s), table_y], 5, fill=(180, 206, 226))  # water glass
    for sx in (int(w * 0.775), int(w * 0.965)):
        d.ellipse([sx - int(28 * s), ground - int(40 * s), sx + int(28 * s), ground - int(26 * s)], fill=(60, 110, 200))
        d.rectangle([sx - int(24 * s), ground - int(33 * s), sx + int(24 * s), ground - int(6 * s)], fill=(50, 96, 180))
        d.ellipse([sx - int(30 * s), ground - int(8 * s), sx + int(30 * s), ground + int(2 * s)], fill=(36, 70, 140))

    def front(dd):
        # stainless counter front + wok bowl, food, spatula, steam
        dd.rectangle([int(w * 0.05), counter_y, int(w * 0.58), counter_y + int(14 * s)], fill=(196, 202, 210))
        dd.rectangle([int(w * 0.05), counter_y + int(14 * s), int(w * 0.58), ground], fill=(150, 156, 166))
        dd.line([(int(w * 0.05), counter_y + int(14 * s)), (int(w * 0.58), counter_y + int(14 * s))], fill=(120, 126, 136), width=3)
        # gas burner under the wok with flames
        dd.rectangle([wok_x - int(40 * s), counter_y - int(4 * s), wok_x + int(40 * s), counter_y + int(2 * s)], fill=(40, 40, 46))
        _flame(dd, wok_x, counter_y - int(2 * s), s * 1.15)
        # wok bowl (half ellipse) and rim
        bowl_bottom = counter_y - int(6 * s)
        dd.pieslice([wok_x - wok_r, 2 * wok_y - bowl_bottom, wok_x + wok_r, bowl_bottom], 0, 180, fill=(30, 30, 34))
        dd.ellipse([wok_x - wok_r, wok_y - int(14 * s), wok_x + wok_r, wok_y + int(14 * s)], fill=(58, 58, 64), outline=(120, 120, 128), width=max(2, int(2.5 * s)))
        dd.ellipse([wok_x - wok_r + int(7 * s), wok_y - int(10 * s), wok_x + wok_r - int(7 * s), wok_y + int(9 * s)], fill=(104, 62, 36))
        rnd = random.Random(11)
        for _ in range(26):
            fx = wok_x + rnd.uniform(-wok_r * 0.75, wok_r * 0.75)
            fy = wok_y + rnd.uniform(-4, 4) * s
            kind = rnd.random()
            col = (54, 128, 60) if kind < 0.5 else ((206, 52, 40) if kind < 0.7 else (150, 96, 60))
            dd.ellipse([fx - 4.5 * s, fy - 2.6 * s, fx + 4.5 * s, fy + 2.6 * s], fill=col)
        # spatula: handle up to the cook's left hand, blade in the food
        sp_hand = (wok_x - int(28 * s), wok_y - int(46 * s))
        dd.line([sp_hand, (wok_x + int(6 * s), wok_y - int(4 * s))], fill=(150, 150, 158), width=max(3, int(5 * s)))
        dd.polygon([(wok_x + int(2 * s), wok_y - int(10 * s)), (wok_x + int(22 * s), wok_y), (wok_x + int(16 * s), wok_y + int(6 * s)), (wok_x - int(2 * s), wok_y - int(2 * s))], fill=(190, 192, 200))

    fg.append(front)
    # steam: soft translucent puffs drawn later via glow layer
    info.update(cook_x=cook_x, counter_y=counter_y, wok=(wok_x, wok_y, wok_r), handle_end=handle_end,
                spatula_hand=(wok_x - int(28 * s), wok_y - int(46 * s)), ground=ground, steam=(wok_x, wok_y - int(40 * s)))
    lights.append(((wok_x, wok_y), int(h * 0.2), (255, 140, 50)))
    return img, ground, lights, fg, info


def _steam(img: Image.Image, origin, s: float, rng: random.Random) -> Image.Image:
    layer = Image.new("RGB", img.size, (0, 0, 0))
    d = ImageDraw.Draw(layer)
    ox, oy = origin
    for i in range(9):
        r = (16 + i * 5) * s
        cx = ox + math.sin(i * 1.3) * 18 * s + rng.uniform(-6, 6) * s
        cy = oy - i * 26 * s
        d.ellipse([cx - r, cy - r * 0.8, cx + r, cy + r * 0.8], fill=(64 - i * 5, 64 - i * 5, 68 - i * 5))
    return _screen(img, layer.filter(ImageFilter.GaussianBlur(14 * s)))


def illustrate_scene(
    size: tuple[int, int],
    *,
    setting: str,
    mood: BlockMood | None,
    characters: list[dict] | None,
    seed: str = "",
    out_path: Path | None = None,
    recipe: SceneRecipe | None = None,
    font_path: str | Path | None = None,
    reference_palette: tuple = (),
    subject_out: dict | None = None,
) -> Image.Image:
    """Draw one scene. `characters` = list of dicts from `character_colors`."""
    ss = 2  # supersample for smooth edges
    w, h = size[0] * ss, size[1] * ss
    rng = random.Random(int(hashlib.md5(f"{seed}{setting}".encode()).hexdigest(), 16) % (2**32))
    s = h / 720 * 1.3 * (1.45 if setting == "food_stall" else 1.0)
    img, ground, lights, seat, fg, info = _scene_background(setting, (w, h), mood, rng, s, font_path, tuple(reference_palette))

    figs = characters or []
    n = len(figs)
    face = expression_for(mood)
    cook_placed = False
    subject_x = None
    for i, col in enumerate(figs):
        d = ImageDraw.Draw(img)
        hands = None
        if setting == "food_stall":
            if "apron" in col.get("items", ()) and not cook_placed:
                cook_placed = True
                subject_x = info["cook_x"] / w
                _draw_character(d, info["cook_x"], ground, s, col, expression=face,
                                hands={"L": info["spatula_hand"], "R": info["handle_end"]})
            else:  # customer on the right
                _draw_character(d, int(w * (0.665 - 0.0 * i)), ground, s, col, expression=face)
            continue
        x = int(w * (0.5 if n == 1 else 0.3 + 0.4 * i / max(1, n - 1)))
        if setting in ("room", "office"):
            x = int(w * (0.22 + 0.1 * i))
        gy = ground - 22 if seat == "sit" else (ground - 4 if seat == "boat" else ground)
        if seat == "sit":  # hands rest on the desk top
            desk_top = ground - 40
            hands = {"L": (x - 4 * s, desk_top - 6), "R": (x + 38 * s, desk_top - 6)}
        if subject_x is None:
            subject_x = x / w
        _draw_character(d, x, gy, s * (1.1 if seat else 1.0), col, sitting=seat is not None,
                        expression=face, hands=hands)

    if subject_out is not None:
        subject_out["x"] = subject_x if subject_x is not None else 0.5
    d = ImageDraw.Draw(img)
    for paint in fg:
        paint(d)
    night = _is_night(mood)
    for center, radius, color in lights:
        if night or setting in ("island", "food_stall"):
            img = _glow(img, center, radius, color, 0.75)
    if setting == "food_stall":
        img = _steam(img, info["steam"], s, rng)

    img = img.resize(size, Image.LANCZOS)
    if out_path is not None:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(out_path)
    return img


def thumbnail_backdrop(size: tuple[int, int], *, zoom: float = 1.45, subject_at: float = 0.70, **scene_kwargs) -> Image.Image:
    """Clean cover art: the scene drawn without cards/fades, zoomed so the main
    character lands on the right and the headline can sit on the left."""
    info: dict = {}
    full = illustrate_scene(size, subject_out=info, **scene_kwargs)
    w, h = full.size
    cw, ch = int(w / zoom), int(h / zoom)
    x0 = int(max(0, min(w - cw, info["x"] * w - subject_at * cw)))
    y0 = int((h - ch) * 0.65)
    return full.crop((x0, y0, x0 + cw, y0 + ch)).resize(size, Image.LANCZOS)
