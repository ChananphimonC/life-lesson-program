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

from PIL import ImageChops, Image, ImageDraw, ImageFilter, ImageFont

from life_lesson.errors import PipelineError
from life_lesson.generation.atmosphere import BlockMood
from life_lesson.publish.fonts import find_thai_font
from life_lesson.video.scene_kb import SceneRecipe

SETTINGS = ("room", "office", "street", "city", "sea", "island", "forest", "night_sky", "food_stall", "alley", "bus", "chicken_cart", "market", "mall", "kitchen", "bts", "compare", "bus_stop", "home_front")

_COLOR_WORDS = {
    "เหลือง": (240, 196, 40), "yellow": (240, 196, 40), "แดง": (206, 52, 48), "red": (206, 52, 48),
    "ส้ม": (232, 128, 40), "orange": (232, 128, 40), "ฟ้า": (96, 168, 224), "sky": (96, 168, 224),
    "น้ำเงิน": (40, 70, 150), "blue": (40, 70, 150), "เขียว": (60, 150, 90), "green": (60, 150, 90),
    "ชมพู": (232, 130, 170), "pink": (232, 130, 170), "ม่วง": (130, 80, 170), "purple": (130, 80, 170),
    "ขาว": (236, 236, 230), "white": (236, 236, 230), "ดำ": (34, 34, 40), "black": (34, 34, 40),
    "เทา": (130, 134, 140), "gray": (130, 134, 140), "grey": (130, 134, 140),
    "น้ำตาล": (120, 80, 50), "brown": (120, 80, 50), "ครีม": (232, 220, 190), "cream": (232, 220, 190),
}


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


_ITEM_WORDS = {
    "apron": ("เอี๊ยม", "ผ้ากันเปื้อน", "apron"),
    "cap": ("หมวก", "cap", "hat"),
    "hairnet": ("ตาข่ายคลุมผม", "ผ้าคลุมผม", "hairnet"),
    "glasses": ("แว่น", "glasses"),
    "backpack": ("กระเป๋าเป้", "เป้", "backpack"),
    "hood": ("ฮู้ด", "hood", "เสื้อกันฝน", "raincoat"),
    "lanyard": ("สายคล้องคอ", "บัตรนักศึกษา", "บัตรพนักงาน", "lanyard"),
    "towel": ("ผ้าขนหนู", "ผ้าเช็ดมือ", "towel"),
    "headlamp": ("ไฟคาดหัว", "headlamp"),
    "earbuds": ("หูฟัง", "earbuds"),
    "collar": ("คอปก", "เชิ้ต", "เบลาส์", "โปโล", "collar"),
    "bow": ("โบว์", "ผูกโบ", "bow"),
    "waist_wrap": ("ผูกเอว", "waist"),
    "skirt_white": ("กระโปรงสีขาว", "กระโปรงขาว"),
    "shopping_bags": ("ถุงตลาด", "ถุงพลาสติก"),
    "conductor_bag": ("กระเป๋ากระบอก", "กระเป๋ารถเมล์", "ที่เก็บตั๋ว", "กระเป๋าตั๋ว"),
    "laptop_bag": ("ถุงใส่โน้ตบุ๊ก", "กระเป๋าโน้ตบุ๊ก", "ถุงโน้ตบุ๊ก"),
}
_SHORT_SLEEVE_WORDS = ("แขนสั้น", "โปโล", "เสื้อยืด", "t-shirt", "polo", "short sleeve")


def items_from_text(text: str | None) -> set[str]:
    low = (text or "").lower()
    return {item for item, words in _ITEM_WORDS.items() if any(w in low for w in words)}


_HAIR_COLORS = [("น้ำตาลเข้ม", (70, 44, 30)), ("น้ำตาลอ่อน", (140, 96, 60)), ("น้ำตาล", (100, 66, 44)), ("ดำ", (30, 24, 22)),
                ("เทา", (124, 124, 132)), ("ขาว", (226, 226, 228)), ("บลอนด์", (222, 186, 98)), ("ทอง", (222, 186, 98)),
                ("แดง", (150, 54, 42)), ("ชมพู", (232, 130, 170)), ("black", (30, 24, 22)), ("brown", (100, 66, 44))]
_HAIR_STYLES = [("หางม้า", "ponytail"), ("ผมมวย", "bun"), ("มวย", "bun"), ("ดัด", "curly"), ("ลอน", "curly"), ("บ๊อบ", "bob"),
                ("ยาว", "long"), ("สยาย", "long"), ("สั้น", "short"), ("เกรียน", "short")]


def hair_from_text(text: str | None) -> tuple[tuple[int, int, int] | None, str | None]:
    low = (text or "").lower()
    color = next((rgb for w, rgb in _HAIR_COLORS if w in low), None)
    style = next((st for w, st in _HAIR_STYLES if w in low), None)
    return color, style


def character_colors(
    outfit: str | None,
    palette: list[str] | None,
    name: str = "",
    extra_items: tuple[str, ...] | list[str] = (),
    sleeve: str | None = None,
    hair: str | None = None,
    gender: str | None = None,
    age: str | None = None,
) -> dict:
    main = None
    for pal in palette or []:
        main = _hex(pal) or (color_from_text(pal) if any(c in (pal or "").lower() for c in _COLOR_WORDS) else None)
        if main:
            break
    main = main or color_from_text(outfit, name)
    h = hashlib.md5(name.encode("utf-8")).digest()
    hair_rgb, style = hair_from_text(hair)
    hair_rgb = hair_rgb or [(30, 24, 22), (58, 40, 30), (24, 24, 30), (88, 60, 40)][h[0] % 4]
    digits = [int(t) for t in re.findall(r"\d+", age or "")]
    older = bool(digits) and digits[0] >= 45
    if older:  # grey creeping into the hair
        hair_rgb = _lerp(hair_rgb, (150, 150, 156), 0.55)
    female = (gender or "").strip().lower() in ("หญิง", "female", "f") or (not gender and style in ("long", "ponytail", "bun"))
    skin = [(248, 222, 198), (240, 208, 178), (228, 190, 154)][h[1] % 3]
    accent = (240, 196, 40) if sum(main) < 380 else (206, 52, 48)
    items = tuple(sorted(items_from_text(outfit) | set(extra_items)))
    if sleeve is None:
        sleeve = "short" if any(w in (outfit or "").lower() for w in _SHORT_SLEEVE_WORDS) else "long"
    return {"name": name, "outfit": main, "hair": hair_rgb, "skin": skin, "accent": accent, "items": items, "sleeve": sleeve,
            "hair_style": style or ("long" if female else "short"), "female": female, "older": older}


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
    return _screen(base, layer)


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
    for idx in range(n):
        x, y = rng.randrange(w), rng.randrange(max(1, int(h_limit)))
        r = rng.choice((1, 1, 2))
        if (idx + _ANIM["phase"]) % 6 == 0:      # a few stars dim on each step: the sky twinkles
            r = 0
        d.ellipse([x - r, y - r, x + r, y + r], fill=(220, 226, 240))


def _moon(img, center, r):
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
                    if rng.random() < lit_p and (wx * 7 + wy * 13 + (_ANIM["phase"] // 2) * 31) % 23 != 0:   # a window now and then switches off/on
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



_RIM = {"bright": (255, 255, 250), "golden": (255, 226, 170), "neon": (210, 160, 255)}


def _shade_layer(layer: Image.Image, mood: BlockMood | None) -> Image.Image:
    """Give flat figures volume: light rim on the lit (top-left) edge, shadow on the far (bottom-right) edge,
    and a soft ground occlusion toward the feet. Works only inside the figures' bounding box (cheap)."""
    bbox = layer.getchannel("A").getbbox()
    if not bbox:
        return layer
    pad = 8
    box = (max(0, bbox[0] - pad), max(0, bbox[1] - pad), min(layer.size[0], bbox[2] + pad), min(layer.size[1], bbox[3] + pad))
    part = layer.crop(box)
    a = part.getchannel("A")
    k = max(2, int(part.size[1] * 0.012))
    lit = ImageChops.subtract(a, ImageChops.offset(a, k, k)).filter(ImageFilter.GaussianBlur(k * 0.8))
    far = ImageChops.subtract(a, ImageChops.offset(a, -k, -k)).filter(ImageFilter.GaussianBlur(k * 0.9))
    rgb = part.convert("RGB")
    tint = _RIM.get(mood.light if mood else "dim", (150, 180, 255))
    lit_img = Image.blend(rgb, Image.new("RGB", rgb.size, tint), 0.5)
    dark_img = rgb.point(lambda v: int(v * 0.58))
    rgb = Image.composite(lit_img, rgb, lit.point(lambda v: min(255, v * 2)))
    rgb = Image.composite(dark_img, rgb, far.point(lambda v: min(255, int(v * 2.2))))
    ao = Image.linear_gradient("L").resize(part.size)                                  # 0 at top -> 255 at feet
    rgb = Image.composite(rgb.point(lambda v: int(v * 0.80)), rgb, ao.point(lambda v: max(0, v - 150) * 2))
    part = rgb.convert("RGBA")
    part.putalpha(a)
    out = layer.copy()
    out.paste(part, box[:2])
    return out


def _cast_shadow(base: Image.Image, layer: Image.Image, strength: float = 0.34) -> Image.Image:
    """The people (and foreground objects) throw a soft shadow down-right onto the set behind them: the set reads as a
    place with depth, and the figures stand in front of it instead of being stickers on it."""
    bbox = layer.getchannel("A").getbbox()
    if not bbox:
        return base
    h = base.size[1]
    dx, dy, r = int(h * 0.016), int(h * 0.010), max(2, int(h * 0.007))
    pad = r * 3 + dx + dy
    box = (max(0, bbox[0] - pad), max(0, bbox[1] - pad), min(base.size[0], bbox[2] + pad), min(base.size[1], bbox[3] + pad))
    a = layer.getchannel("A").crop(box)
    sh = ImageChops.offset(a, dx, dy).filter(ImageFilter.GaussianBlur(r))
    mask = sh.point(lambda v: int(v * strength))
    region = base.crop(box)
    dark = region.point(lambda v: int(v * 0.55))
    out = base.copy()
    out.paste(Image.composite(dark, region, mask), box[:2])
    return out


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


def _draw_face(d, x, head_y, s, expression: str, female: bool = False, talking: bool = False, older: bool = False):
    ink = (44, 32, 30)
    brow = (66, 46, 38)
    ey = head_y - 0.5 * s
    wide = expression == "wide"
    if expression == "asleep":
        for sign in (-1, 1):
            cx = x + sign * 7.2 * s
            d.arc([cx - 3.8 * s, ey - 3.4 * s, cx + 3.8 * s, ey + 2.6 * s], 15, 165, fill=ink, width=max(2, int(1.6 * s)))
    for sign in (-1, 1) if expression != "asleep" else ():
        cx = x + sign * 7.2 * s
        # almond eye: a soft lens shape (never a big round stare), brown iris with a shine
        rw, rh = (3.9, 3.0) if wide else (3.6, 2.4)
        d.ellipse([cx - rw * s, ey - rh * s, cx + rw * s, ey + rh * s], fill=(250, 247, 242))
        ir = 1.85 * s if not wide else 1.7 * s
        d.ellipse([cx - ir, ey - ir * 1.05, cx + ir, ey + ir * 1.05], fill=(78, 52, 40))
        d.ellipse([cx - ir * 0.5, ey - ir * 0.55, cx + ir * 0.5, ey + ir * 0.55], fill=(24, 18, 18))
        d.ellipse([cx + 0.1 * s, ey - 1.5 * s, cx + 1.2 * s, ey - 0.4 * s], fill=(255, 255, 255))           # eye shine
        d.arc([cx - 4.1 * s, ey - 3.4 * s, cx + 4.1 * s, ey + 1.2 * s], 198, 342, fill=ink, width=max(1, int(1.3 * s)))   # upper lid
        # eyebrow: thin, softly curved; outer end at sign*12.5, inner end at sign*3
        outer, inner = (x + sign * 12.5 * s, x + sign * 3.2 * s)
        by = ey - 6.8 * s
        if expression in ("worried", "wide"):
            o_y, i_y = by + 1.6 * s, by - 1.6 * s
        elif expression == "soft":
            o_y, i_y = by + 1.0 * s, by - 0.5 * s
        elif expression == "smile":
            o_y, i_y = by + 0.4 * s, by - 0.4 * s
        else:
            o_y, i_y = by + 0.3 * s, by - 0.2 * s
        mid = ((outer + inner) / 2, (o_y + i_y) / 2 - 1.1 * s)                        # a gentle arch
        d.line([(outer, o_y), mid, (inner, i_y)], fill=brow, width=max(1, int(1.2 * s)), joint="curve")
    if female and expression != "asleep":   # lashes at the outer corners + soft cheeks
        for sign in (-1, 1):
            cx = x + sign * 7.2 * s
            ox = cx + sign * 3.3 * s
            d.line([(ox, ey - 1.6 * s), (ox + sign * 2.6 * s, ey - 3.6 * s)], fill=ink, width=max(1, int(1.2 * s)))
            d.ellipse([x + sign * 12 * s - 3.2 * s, head_y + 5 * s, x + sign * 12 * s + 3.2 * s, head_y + 9.5 * s], fill=(238, 160, 150))
    my = head_y + 10 * s
    w = max(2, int(1.8 * s))
    d.arc([x - 2.2 * s, head_y + 3.5 * s, x + 2.2 * s, head_y + 8 * s], 20, 160, fill=(176, 120, 100), width=max(1, int(1.3 * s)))   # nose
    if older:   # age lines: forehead, crow's feet, smile lines
        wr = (206, 164, 136)
        for sign in (-1, 1):
            ox = x + sign * 13.2 * s
            d.line([(ox, ey - 0.5 * s), (ox + sign * 2.6 * s, ey - 2.2 * s)], fill=wr, width=max(1, int(1.1 * s)))
            d.line([(ox, ey + 1.2 * s), (ox + sign * 2.6 * s, ey + 2.4 * s)], fill=wr, width=max(1, int(1.1 * s)))
            d.arc([x + sign * 8.2 * s - 2.2 * s, head_y + 4.6 * s, x + sign * 8.2 * s + 2.2 * s, my + 3.4 * s], 100 if sign > 0 else 260, 260 if sign > 0 else 80, fill=wr, width=max(1, int(1.0 * s)))   # soft smile line
    lip = (196, 74, 86) if female else ink
    if talking and expression != "asleep":   # the speaker: mouth open mid-word ("half" = between syllables)
        open_h = 6.4 if talking is True else 2.6
        d.ellipse([x - 4.4 * s, my - 2.6 * s, x + 4.4 * s, my + open_h * s], fill=(122, 38, 44))
        if talking is True:
            d.ellipse([x - 2.6 * s, my + 2.6 * s, x + 2.6 * s, my + 6.0 * s], fill=(226, 120, 120))
        return
    if expression == "asleep":  # eyes shut: pretending to sleep
        d.line([(x - 4 * s, my + 1 * s), (x + 4 * s, my + 1 * s)], fill=lip, width=w)
        return
    if expression == "smile":
        d.arc([x - 7 * s, my - 6 * s, x + 7 * s, my + 5 * s], 15, 165, fill=lip, width=w)
        for sign in (-1, 1):  # blush
            d.ellipse([x + sign * 11 * s - 3 * s, my - 4 * s, x + sign * 11 * s + 3 * s, my - 0.5 * s], fill=(236, 150, 140))
    elif expression == "soft":
        d.arc([x - 5 * s, my - 4 * s, x + 5 * s, my + 3 * s], 20, 160, fill=lip, width=w)
    elif expression == "worried":
        d.arc([x - 5 * s, my - 1 * s, x + 5 * s, my + 6 * s], 200, 340, fill=lip, width=w)
    elif expression == "wide":
        d.ellipse([x - 3.2 * s, my - 2 * s, x + 3.2 * s, my + 5 * s], fill=(120, 40, 44))
    else:
        d.arc([x - 4.4 * s, my - 3.4 * s, x + 4.4 * s, my + 2.2 * s], 20, 160, fill=lip, width=w)   # a faint, friendly curve


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


def _ground_shadow(d, x, y, s, night):
    """Soft contact shadow so people sit IN the scene, not on it."""
    k = 0.34 if night else 0.22
    for i, grow in enumerate((1.0, 0.75, 0.5)):
        c = (int(40 * (1 - k)), int(36 * (1 - k)), int(44 * (1 - k)))
        d.ellipse([x - 40 * s * grow, y - 5 * s * grow, x + 40 * s * grow, y + 7 * s * grow], fill=c)


def _knee(hip, foot, upper, lower, forward=1):
    """Two-bone leg whose knee bends toward the walking direction (+x)."""
    dx, dy = foot[0] - hip[0], foot[1] - hip[1]
    dist = max(1e-6, min(math.hypot(dx, dy), upper + lower - 0.01))
    a = (upper * upper - lower * lower + dist * dist) / (2 * dist)
    hh = math.sqrt(max(upper * upper - a * a, 0.0))
    ux, uy = dx / math.hypot(dx, dy or 1e-6), dy / math.hypot(dx, dy or 1e-6)
    nx, ny = -uy, ux                                   # a normal to the hip->foot line
    if nx * forward < 0:
        nx, ny = -nx, -ny
    return (hip[0] + ux * a + nx * hh, hip[1] + uy * a + ny * hh)


def _draw_walker_side(d, x, ground_y, s, colors, phase, expression="neutral"):
    """Profile (side-on) walking figure facing right: alternating stride, bent knees, opposite arm swing,
    nose in profile, hair/ponytail swinging behind. Used when someone crosses the frame."""
    outfit, hair, skin = colors["outfit"], colors["hair"], colors["skin"]
    items = set(colors.get("items", ()))
    dark = tuple(max(0, c - 55) for c in outfit)
    th = 2 * math.pi * phase / 8
    hip = (x, ground_y - 64 * s)
    torso_top = ground_y - 126 * s
    head_y = ground_y - 150 * s + abs(math.sin(th)) * -1.6 * s       # footfall bob
    style = colors.get("hair_style", "short")
    if "backpack" in items:
        d.rounded_rectangle([x - 30 * s, torso_top + 4 * s, x - 8 * s, hip[1] - 4 * s], 8 * s, fill=(58, 62, 78))
    # far leg + far arm (behind the body, a shade darker)
    for k, shade in ((1, 0.78), (0, 1.0)):
        ph = th + (math.pi if k else 0)
        foot = (x + 24 * s * math.sin(ph), ground_y - 9 * s * max(0.0, math.cos(ph)) - 2 * s)
        knee = _knee(hip, foot, 33 * s, 33 * s)
        col = tuple(int(c * shade) for c in dark)
        _limb(d, hip, knee, 13 * s, col)
        _limb(d, knee, foot, 12 * s, col)
        d.rounded_rectangle([foot[0] - 6 * s, foot[1] - 5 * s, foot[0] + 17 * s, foot[1] + 5 * s], 4 * s, fill=(36, 36, 44))   # shoe pointing forward
        if k:   # far arm, drawn before the torso
            sh = (x - 1 * s, torso_top + 12 * s)
            hand = (x + 22 * s * math.sin(ph + math.pi), torso_top + 62 * s)
            e, hnd = _ik(sh, hand, 29 * s, 29 * s)
            _limb(d, sh, e, 11 * s, tuple(int(c * 0.8) for c in outfit))
            _limb(d, e, hnd, 9.5 * s, tuple(int(c * 0.8) for c in skin))
    d.rounded_rectangle([x - 13 * s, torso_top, x + 13 * s, hip[1] + 8 * s], 9 * s, fill=outfit)                     # torso in profile
    if colors.get("female"):
        d.ellipse([x + 5 * s, torso_top + 12 * s, x + 16 * s, torso_top + 25 * s], fill=outfit)                       # bust line
    if "lanyard" in items:
        d.line([(x + 6 * s, torso_top + 2 * s), (x + 10 * s, torso_top + 30 * s)], fill=(206, 60, 70), width=max(2, int(2 * s)))
        d.rounded_rectangle([x + 6 * s, torso_top + 30 * s, x + 15 * s, torso_top + 44 * s], 2 * s, fill=(245, 245, 240))
    # near arm swings opposite to the near leg
    sh = (x + 1 * s, torso_top + 12 * s)
    hand = (x + 22 * s * math.sin(th + math.pi), torso_top + 62 * s)
    e, hnd = _ik(sh, hand, 29 * s, 29 * s)
    _limb(d, sh, e, 12 * s, outfit)
    _limb(d, e, hnd, 10 * s, skin)
    if "laptop_bag" in items:
        d.rounded_rectangle([hnd[0] - 6 * s, hnd[1], hnd[0] + 24 * s, hnd[1] + 30 * s], 4 * s, fill=(70, 78, 98), outline=(40, 44, 58))
    # head in profile
    d.rectangle([x - 4 * s, head_y + 14 * s, x + 6 * s, torso_top + 4 * s], fill=skin)
    if style in ("long", "ponytail", "bun", "bob"):
        sw = 4 * s * math.sin(th - 0.6)
        if style == "ponytail":
            d.polygon([(x - 10 * s, head_y - 8 * s), (x - 20 * s + sw, head_y + 40 * s), (x - 6 * s + sw, head_y + 52 * s), (x - 2 * s, head_y + 4 * s)], fill=hair)
        elif style == "long":
            d.polygon([(x - 14 * s, head_y - 10 * s), (x - 24 * s + sw, head_y + 62 * s), (x - 4 * s + sw, head_y + 66 * s), (x + 2 * s, head_y + 6 * s)], fill=hair)
    d.ellipse([x - 16 * s, head_y - 19 * s, x + 16 * s, head_y + 19 * s], fill=skin)                                   # skull / face
    d.ellipse([x + 4 * s, head_y + 6 * s, x + 17 * s, head_y + 21 * s], fill=skin)                                    # chin + jaw line
    d.polygon([(x + 14 * s, head_y + 0 * s), (x + 20 * s, head_y + 6 * s), (x + 14 * s, head_y + 9 * s)], fill=skin)    # nose
    # hair in profile: it covers the whole crown, the back of the head and sweeps to a hairline above the brow
    d.ellipse([x - 21 * s, head_y - 28 * s, x + 15 * s, head_y - 2 * s], fill=hair)                                     # crown (no bald forehead)
    d.polygon([(x - 21 * s, head_y - 14 * s), (x - 19 * s, head_y + 16 * s), (x - 4 * s, head_y + 14 * s),
               (x - 2 * s, head_y - 2 * s), (x + 10 * s, head_y - 11 * s), (x + 4 * s, head_y - 24 * s)], fill=hair)  # back of head, ear covered
    d.polygon([(x + 14 * s, head_y - 17 * s), (x + 17.5 * s, head_y - 11 * s), (x + 11 * s, head_y - 12.5 * s), (x + 5 * s, head_y - 15 * s)], fill=hair)   # fringe stays above the brow
    d.arc([x - 15 * s, head_y - 26 * s, x + 6 * s, head_y - 8 * s], 200, 330, fill=tuple(min(255, c + 36) for c in hair), width=max(1, int(2 * s)))  # shine
    if style == "bun":
        d.ellipse([x - 20 * s, head_y - 36 * s, x - 5 * s, head_y - 21 * s], fill=hair)
    if style not in ("long", "ponytail", "bob"):
        d.ellipse([x - 5 * s, head_y + 1 * s, x + 2 * s, head_y + 8 * s], fill=tuple(max(0, c - 14) for c in skin))    # ear (hidden under long hair)
    ink_, brow_ = (44, 32, 30), (66, 46, 38)
    d.ellipse([x + 6.5 * s, head_y - 3.4 * s, x + 12.5 * s, head_y + 1.4 * s], fill=(250, 247, 242))                    # eye white (almond, in profile)
    d.ellipse([x + 8.6 * s, head_y - 3.0 * s, x + 12.2 * s, head_y + 1.2 * s], fill=(78, 52, 40))                       # brown iris looking ahead
    d.ellipse([x + 10 * s, head_y - 2.2 * s, x + 12 * s, head_y + 0.2 * s], fill=(24, 18, 18))                          # pupil
    d.ellipse([x + 10.6 * s, head_y - 2.8 * s, x + 11.8 * s, head_y - 1.6 * s], fill=(255, 255, 255))                   # shine
    d.arc([x + 6 * s, head_y - 4.8 * s, x + 13 * s, head_y + 0.4 * s], 205, 330, fill=ink_, width=max(1, int(1.1 * s)))   # upper lid
    if colors.get("female"):
        d.line([(x + 12.2 * s, head_y - 2.4 * s), (x + 15 * s, head_y - 4.6 * s)], fill=ink_, width=max(1, int(1.2 * s)))   # lash
    d.arc([x + 4.5 * s, head_y - 11 * s, x + 14 * s, head_y - 4 * s], 215, 325, fill=brow_, width=max(1, int(1.3 * s)))   # eyebrow, clear of the fringe
    if colors.get("female"):
        d.ellipse([x + 6 * s, head_y + 4.5 * s, x + 11 * s, head_y + 9 * s], fill=(240, 176, 166))                      # blush
    mc = (196, 74, 86) if colors.get("female") else ink_
    d.arc([x + 6 * s, head_y + 8 * s, x + 14 * s, head_y + 14 * s], 25, 150, fill=mc, width=max(2, int(1.6 * s)))      # smiling lips
    return {"head": (x, head_y), "L": hnd, "R": hnd}


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


def _draw_character(d, x, ground_y, s, colors, sitting=False, expression="neutral", hands=None, items=None, talking=False, breath=0.0, walk=None):
    """`hands` = {"L": (x, y), "R": (x, y)} screen-side targets in pixels; default pose if None."""
    outfit, hair, skin, accent = colors["outfit"], colors["hair"], colors["skin"], colors["accent"]
    items = set(items if items is not None else colors.get("items", ()))
    dark = tuple(max(0, c - 40) for c in outfit)

    female = bool(colors.get("female"))
    sho = (19.5 if female else 22) * s          # shoulder half-width: arms hang from here
    leg_in, leg_out = (4.5, 11.5) if female else (3, 14)
    if sitting:
        torso_top, torso_bot, head_y = ground_y - 112 * s, ground_y - 4 * s, ground_y - 138 * s
    else:
        torso_top, torso_bot, head_y = ground_y - 128 * s, ground_y - 54 * s, ground_y - 152 * s
    head_y += breath * 1.5 * s   # breathing: the head rises and settles a hair
    shoulder_y = torso_top + 9 * s

    if "backpack" in items:  # behind the body
        d.rounded_rectangle([x - 30 * s, torso_top + 4 * s, x + 30 * s, torso_bot - 4 * s], 10 * s, fill=(58, 62, 78))
    foot = {-1: 0.0, 1: 0.0}   # horizontal foot offset per side (walking cycle)
    lift = {-1: 0.0, 1: 0.0}
    if walk is not None and not sitting:
        sw = math.sin(2 * math.pi * walk / 8)
        foot = {-1: sw * 11 * s, 1: -sw * 11 * s}
        lift = {-1: max(0.0, sw) * 7 * s, 1: max(0.0, -sw) * 7 * s}
    if not sitting and walk is not None:
        for sign, (a, b) in ((-1, (leg_out, leg_in)), (1, (leg_in, leg_out))):
            top_y, fy = ground_y - 62 * s, ground_y - lift[sign]
            d.polygon([(x + sign * leg_in * s if sign == 1 else x - leg_out * s, top_y),
                       (x + sign * leg_in * s + (leg_out - leg_in) * s * sign if False else (x + leg_out * s if sign == 1 else x - leg_in * s), top_y),
                       ((x + leg_out * s if sign == 1 else x - leg_in * s) + foot[sign], fy),
                       ((x + leg_in * s if sign == 1 else x - leg_out * s) + foot[sign], fy)], fill=dark)
    elif not sitting:
        d.rectangle([x - leg_out * s, ground_y - 62 * s, x - leg_in * s, ground_y], fill=dark)
        d.rectangle([x + leg_in * s, ground_y - 62 * s, x + leg_out * s, ground_y], fill=dark)
    if not sitting:
        if "shopping_bags" in items:  # market bags dumped around the feet
            for dx, col, hh in ((-44, (232, 120, 120), 40), (36, (120, 180, 230), 34), (58, (240, 214, 120), 28)):
                bx = x + dx * s
                d.rounded_rectangle([bx - 14 * s, ground_y - hh * s, bx + 14 * s, ground_y + 2 * s], 8 * s, fill=col)
                d.arc([bx - 9 * s, ground_y - (hh + 14) * s, bx + 9 * s, ground_y - (hh - 4) * s], 180, 360, fill=tuple(c - 40 for c in col), width=max(2, int(2 * s)))
        for sign in (-1, 1):  # shoes / rubber sandals
            d.rounded_rectangle([x + sign * 8.5 * s - 10 * s + foot[sign], ground_y - 5 * s - lift[sign], x + sign * 8.5 * s + 10 * s + foot[sign], ground_y + 2 * s - lift[sign]], 3 * s, fill=(36, 36, 44))
    style = colors.get("hair_style", "short")
    if style == "long" and "hood" not in items:       # long hair falls behind the shoulders
        d.rounded_rectangle([x - 27 * s, head_y - 22 * s, x + 27 * s, torso_top + 50 * s], 16 * s, fill=hair)
        for k in range(-2, 3):  # wavy ends: overlapping curls instead of a straight cut
            cx_ = x + k * 11 * s
            d.ellipse([cx_ - 8.5 * s, torso_top + 40 * s + (k % 2) * 5 * s, cx_ + 8.5 * s, torso_top + 64 * s + (k % 2) * 5 * s], fill=hair)
        light = tuple(min(255, c + 26) for c in hair)
        for k in (-20, -11, -2, 8, 17):  # long soft strands
            pts = [(x + k * s + 3.2 * s * math.sin(t * 0.18 + k), head_y - 12 * s + t * s) for t in range(0, int((torso_top - head_y) / max(s, 0.01)) + 56, 6)]
            if len(pts) > 1:
                d.line(pts, fill=light, width=max(1, int(1.4 * s)))
    if female:  # hourglass: shoulders, a defined waist, gentle hips
        H = torso_bot - torso_top
        half = [(0.0, 15.0), (0.06, 19.5), (0.30, 18.0), (0.58, 13.5), (0.82, 17.5), (1.0, 20.0)]
        right = [(x + hw * s, torso_top + t * H) for t, hw in half]
        left = [(x - hw * s, torso_top + t * H) for t, hw in reversed(half)]
        d.polygon(right + left, fill=outfit)
        for px_, py_ in ((x - 17 * s, torso_top + 5 * s), (x + 17 * s, torso_top + 5 * s)):  # rounded shoulders
            d.ellipse([px_ - 4.5 * s, py_ - 4.5 * s, px_ + 4.5 * s, py_ + 4.5 * s], fill=outfit)
    else:
        d.rounded_rectangle([x - 22 * s, torso_top, x + 22 * s, torso_bot], 12 * s, fill=outfit)
    if "collar" in items:  # white blouse collar
        d.polygon([(x - 4 * s, torso_top + 1 * s), (x - 17 * s, torso_top + 4 * s), (x - 10 * s, torso_top + 17 * s)], fill=(250, 250, 248), outline=(214, 214, 210))
        d.polygon([(x + 4 * s, torso_top + 1 * s), (x + 17 * s, torso_top + 4 * s), (x + 10 * s, torso_top + 17 * s)], fill=(250, 250, 248), outline=(214, 214, 210))
    if "collar" in items and "bow" not in items:   # button placket + cuffs on a shirt
        for k in range(4):
            d.ellipse([x - 1.5 * s, torso_top + (20 + k * 11) * s - 1.5 * s, x + 1.5 * s, torso_top + (20 + k * 11) * s + 1.5 * s], fill=(250, 250, 246), outline=(200, 200, 196))
        d.line([(x, torso_top + 17 * s), (x, torso_bot - 4 * s)], fill=tuple(max(0, c - 26) for c in outfit), width=max(1, int(1.2 * s)))
    if "bow" in items:     # ribbon bow at the neck
        bc = (250, 250, 248) if sum(outfit) < 600 else (210, 70, 90)
        d.polygon([(x, torso_top + 12 * s), (x - 13 * s, torso_top + 5 * s), (x - 13 * s, torso_top + 19 * s)], fill=bc)
        d.polygon([(x, torso_top + 12 * s), (x + 13 * s, torso_top + 5 * s), (x + 13 * s, torso_top + 19 * s)], fill=bc)
        d.ellipse([x - 4 * s, torso_top + 8 * s, x + 4 * s, torso_top + 16 * s], fill=tuple(max(0, c - 30) for c in bc))
    if "skirt_white" in items and not sitting:  # flared white skirt over the upper legs
        d.polygon([(x - 20 * s, torso_bot - 6 * s), (x + 20 * s, torso_bot - 6 * s),
                   (x + 31 * s, ground_y - 36 * s), (x - 31 * s, ground_y - 36 * s)], fill=(246, 246, 242), outline=(214, 214, 210), width=max(1, int(1.5 * s)))
    if "waist_wrap" in items:  # cardigan tied round the waist: band, knot and two tails
        wc = (122, 126, 134)
        wy = torso_bot - 4 * s
        wh = (18 if female else 24) * s
        d.rounded_rectangle([x - wh, wy - 7 * s, x + wh, wy + 7 * s], 4 * s, fill=wc)
        d.ellipse([x + 8 * s, wy - 9 * s, x + 22 * s, wy + 5 * s], fill=tuple(c - 14 for c in wc))
        d.polygon([(x + 10 * s, wy + 3 * s), (x + 6 * s, wy + 26 * s), (x + 15 * s, wy + 22 * s)], fill=wc)
        d.polygon([(x + 17 * s, wy + 3 * s), (x + 22 * s, wy + 24 * s), (x + 27 * s, wy + 14 * s)], fill=tuple(c - 14 for c in wc))

    if "apron" in items:
        ap = (60, 62, 76) if sum(outfit) > 560 else (236, 230, 214)
        d.polygon([(x - 13 * s, torso_top + 6 * s), (x + 13 * s, torso_top + 6 * s),
                   (x + 21 * s, torso_bot), (x - 21 * s, torso_bot)], fill=ap)
        d.line([(x - 13 * s, torso_top + 6 * s), (x - 7 * s, torso_top - 8 * s)], fill=ap, width=max(2, int(3 * s)))
        d.line([(x + 13 * s, torso_top + 6 * s), (x + 7 * s, torso_top - 8 * s)], fill=ap, width=max(2, int(3 * s)))
        d.rounded_rectangle([x - 9 * s, torso_bot - 26 * s, x + 9 * s, torso_bot - 10 * s], 3 * s, outline=tuple(max(0, c - 40) for c in ap), width=max(1, int(1.5 * s)))
    if "conductor_bag" in items:   # cross-body strap + the orange ticket pouch on the hip
        d.line([(x - 14 * s, torso_top - 2 * s), (x + 24 * s, torso_bot - 14 * s)], fill=(120, 74, 40), width=max(3, int(4 * s)))
        d.rounded_rectangle([x + 14 * s, torso_bot - 36 * s, x + 40 * s, torso_bot - 8 * s], 5 * s, fill=(222, 128, 40), outline=(150, 80, 24), width=max(1, int(2 * s)))
        d.ellipse([x + 22 * s, torso_bot - 28 * s, x + 32 * s, torso_bot - 18 * s], fill=(250, 232, 190))
    if "laptop_bag" in items:      # slim bag hanging from one shoulder at the hip
        d.line([(x + 14 * s, torso_top - 2 * s), (x - 30 * s, torso_bot - 16 * s)], fill=(50, 54, 66), width=max(3, int(3 * s)))
        d.rounded_rectangle([x - 52 * s, torso_bot - 34 * s, x - 14 * s, torso_bot - 4 * s], 4 * s, fill=(70, 78, 98), outline=(40, 44, 58), width=max(1, int(2 * s)))
        d.line([(x - 52 * s, torso_bot - 26 * s), (x - 14 * s, torso_bot - 26 * s)], fill=(40, 44, 58), width=max(1, int(2 * s)))
    if "lanyard" in items:
        d.line([(x - 6 * s, torso_top - 4 * s), (x, torso_top + 30 * s)], fill=accent, width=max(2, int(2 * s)))
        d.line([(x + 6 * s, torso_top - 4 * s), (x, torso_top + 30 * s)], fill=accent, width=max(2, int(2 * s)))
        d.rounded_rectangle([x - 7 * s, torso_top + 30 * s, x + 7 * s, torso_top + 46 * s], 2 * s, fill=(245, 245, 240))
        d.rectangle([x - 7 * s, torso_top + 30 * s, x + 7 * s, torso_top + 34 * s], fill=accent)
    if "backpack" in items:
        for sign in (-1, 1):
            d.line([(x + sign * 12 * s, torso_top + 2 * s), (x + sign * 15 * s, torso_bot - 6 * s)], fill=(58, 62, 78), width=max(3, int(5 * s)))

    # arms (default: hanging at the sides, or forearms forward when seated)
    sh_l, sh_r = (x - sho, shoulder_y), (x + sho, shoulder_y)
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
    d.rectangle([x - 5 * s, head_y + 16 * s, x + 5 * s, head_y + 21 * s], fill=tuple(max(0, c - 22) for c in skin))     # shadow under the chin
    for sign_ in (-1, 1):                                                                                            # ears (+ small earrings for women)
        d.ellipse([x + sign_ * 17 * s - 3.4 * s, head_y - 2 * s, x + sign_ * 17 * s + 3.4 * s, head_y + 8 * s], fill=tuple(max(0, c - 12) for c in skin))
        if colors.get("female"):
            d.ellipse([x + sign_ * 17 * s - 1.6 * s, head_y + 8 * s, x + sign_ * 17 * s + 1.6 * s, head_y + 11 * s], fill=(250, 214, 120))
    d.ellipse([x - 17 * s, head_y - 18 * s, x + 17 * s, head_y + 20 * s], fill=skin)
    if "hood" not in items:
        if style in ("long", "bob", "curly"):  # side locks framing the face, over the shoulders
            ln = {"long": 52, "bob": 24, "curly": 30}[style]
            for sign in (-1, 1):
                d.rounded_rectangle([x + sign * 19 * s - 6 * s, head_y - 8 * s, x + sign * 19 * s + 6 * s, head_y + ln * s], 6 * s, fill=hair)
        if style == "ponytail":   # a long tail that swings with the breath
            sw = 3 * s * math.sin(_ANIM["phase"] * 0.8)
            d.ellipse([x + 12 * s, head_y - 14 * s, x + 34 * s, head_y + 24 * s], fill=hair)
            d.polygon([(x + 16 * s, head_y + 10 * s), (x + 32 * s, head_y + 10 * s), (x + 36 * s + sw, head_y + 62 * s), (x + 22 * s + sw, head_y + 74 * s), (x + 14 * s + sw, head_y + 58 * s)], fill=hair)
            d.line([(x + 26 * s, head_y + 20 * s), (x + 28 * s + sw, head_y + 62 * s)], fill=tuple(min(255, c + 28) for c in hair), width=max(1, int(1.6 * s)))
        d.pieslice([x - 19 * s, head_y - 24 * s, x + 19 * s, head_y + 14 * s], 180, 360, fill=hair)
        if style in ("long", "bob", "curly", "ponytail"):  # a glossy highlight and a parting
            d.arc([x - 14 * s, head_y - 22 * s, x + 6 * s, head_y - 4 * s], 200, 300, fill=tuple(min(255, c + 34) for c in hair), width=max(2, int(2.4 * s)))
            d.line([(x + 2 * s, head_y - 24 * s), (x - 6 * s, head_y - 8 * s)], fill=tuple(max(0, c - 16) for c in hair), width=max(1, int(1.2 * s)))
        if style == "curly":   # permed curls over the crown (older women's classic short perm)
            for k in range(-3, 4):
                cxk = x + k * 5.6 * s
                d.ellipse([cxk - 5.2 * s, head_y - 28 * s + abs(k) * 2.4 * s, cxk + 5.2 * s, head_y - 16 * s + abs(k) * 2.4 * s], fill=hair)
        if style == "ponytail":   # side-swept fringe + a bright hair tie
            d.pieslice([x - 18 * s, head_y - 22 * s, x + 6 * s, head_y - 2 * s], 180, 300, fill=tuple(max(0, c - 10) for c in hair))
            d.ellipse([x + 13 * s, head_y - 4 * s, x + 21 * s, head_y + 4 * s], fill=(206, 60, 80))
        if style == "bun":
            d.ellipse([x - 10 * s, head_y - 36 * s, x + 10 * s, head_y - 18 * s], fill=hair)
        if style in ("short", "bob", "ponytail"):
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
    _draw_face(d, x, head_y, s, expression, colors.get("female", False), talking, colors.get("older", False))
    if "earbuds" in items:
        for sign in (-1, 1):
            d.ellipse([x + sign * 19 * s - 3 * s, head_y + 1 * s, x + sign * 19 * s + 3 * s, head_y + 7 * s], fill=(250, 250, 250))
        d.line([(x - 19 * s, head_y + 7 * s), (x - 16 * s, head_y + 30 * s), (x - 4 * s, torso_top + 16 * s)], fill=(235, 235, 235), width=max(1, int(1.4 * s)))
    if "headlamp" in items:
        d.rounded_rectangle([x - 7 * s, head_y - 19 * s, x + 7 * s, head_y - 11 * s], 3 * s, fill=(250, 240, 190), outline=(60, 60, 66), width=max(1, int(1.5 * s)))
        d.line([(x - 19 * s, head_y - 12 * s), (x + 19 * s, head_y - 12 * s)], fill=(60, 60, 66), width=max(2, int(2 * s)))
    if "glasses" in items:
        ey = head_y - 1 * s
        for sign in (-1, 1):
            d.ellipse([x + sign * 7.5 * s - 7 * s, ey - 7 * s, x + sign * 7.5 * s + 7 * s, ey + 7 * s], outline=(30, 30, 36), width=max(2, int(1.8 * s)))
        d.line([(x - 0.5 * s, ey), (x + 0.5 * s, ey)], fill=(30, 30, 36), width=max(2, int(1.8 * s)))
    hand_pos["head"] = (x, head_y)
    return hand_pos


# -- scenes --------------------------------------------------------------------

def _scene_background(setting: str, size, mood: BlockMood | None, rng: random.Random, fig_s: float = 1.0, font_path: Path | None = None, ref=(), cook_present: bool = True, props=(), layout: dict | None = None):
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
            from life_lesson.video import places
            places.office_back(img, (w, h), ground, night, lights, fig_s, font_path)
            d = ImageDraw.Draw(img)
            fg.append(lambda dd: places.office_front(dd, (w, h), ground, night, fig_s, font_path))
            lights.append(((int(w * 0.43), ground - 76), int(h * 0.18), (120, 190, 255)))
            seat = "sit"
    elif setting == "sea" or setting == "island":
        hor = int(h * 0.55)
        sea_top, sea_bot = (_lerp(top, (0, 30, 50), 0.5), _lerp(bottom, (0, 10, 30), 0.6)) if night else ((70, 140, 190), (30, 90, 140))
        img.paste(_gradient((w, h - hor), sea_top, sea_bot), (0, hor))
        d = ImageDraw.Draw(img)
        for i in range(26):
            y = hor + 10 + i * (h - hor) / 26
            x0 = rng.randrange(-80, w) + int(14 * math.sin(_ANIM["phase"] * 0.8 + i) * (0.4 + (y - hor) / (h - hor)))   # waves drift
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
    elif setting == "bus":
        lay = layout or {}
        img, ground, lights, fg, info = _bus(img, size, mood, rng, fig_s, night, props,
                                             lay.get("stand_xs", []), lay.get("bench_slots", []), lay.get("named_slots", []))
        d = ImageDraw.Draw(img)
    elif setting == "alley":
        img, ground, lights, fg, info = _alley(img, size, mood, rng, fig_s, night, props)
        d = ImageDraw.Draw(img)
    elif setting in ("chicken_cart", "market", "mall", "kitchen", "bts", "compare", "bus_stop", "home_front"):
        from life_lesson.video import places   # lazy: places imports helpers from this module
        img, ground, lights, fg, info = getattr(places, setting)(img, size, mood, rng, fig_s, font_path, night, props)
        d = ImageDraw.Draw(img)
    elif setting == "food_stall":
        img, ground, lights, fg, info = _food_stall(img, size, mood, rng, fig_s, font_path, night, ref, cook_present, props)
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
            if "bed" in props:   # waking up: bed with rumpled blanket, pillow and a glowing alarm clock
                dd.rounded_rectangle([int(w * 0.04), ground - 70, int(w * 0.48), ground - 18], 10, fill=(116, 128, 168) if night else (150, 170, 210))
                dd.rounded_rectangle([int(w * 0.05), ground - 86, int(w * 0.15), ground - 58], 12, fill=(236, 236, 240))                   # pillow
                dd.polygon([(int(w * 0.18), ground - 70), (int(w * 0.48), ground - 70), (int(w * 0.46), ground - 44), (int(w * 0.20), ground - 48)], fill=(92, 104, 148) if night else (126, 146, 190))   # blanket
                dd.rectangle([int(w * 0.04), ground - 18, int(w * 0.48), h], fill=(60, 44, 36))
                dd.rectangle([int(w * 0.50), ground - 52, int(w * 0.56), ground], fill=(96, 70, 52))                                      # bedside table
                dd.rectangle([int(w * 0.51), ground - 70, int(w * 0.55), ground - 52], fill=(40, 40, 48))                                 # alarm clock
                dd.rectangle([int(w * 0.512), ground - 66, int(w * 0.548), ground - 58], fill=(255, 90, 80))
                return
            dd.rectangle([int(w * 0.06), ground - 40, int(w * 0.46), ground - 22], fill=(96, 70, 52))
            dd.rectangle([int(w * 0.06), ground - 22, int(w * 0.46), h], fill=(60, 44, 36))
            dd.line([(lx, ly), (lx + 16, ly - 70), (lx - 14, ly - 120)], fill=(34, 34, 40), width=7)
            dd.polygon([(lx - 40, ly - 120), (lx + 8, ly - 120), (lx - 2, ly - 92), (lx - 32, ly - 92)], fill=(34, 34, 40))

        fg.append(desk)
        lights.append(((lx - 16, ly - 90), int(h * 0.3), (255, 196, 110) if night else (255, 236, 190)))
        seat = "sit"
    return img, ground, lights, seat, fg, info


_ANIM: dict = {"phase": 0, "prog": None}   # current animation step; things that move (flames, steam, bulbs) read it


def _flame(d, cx, base_y, s, scale=1.0):
    for dx, hh, col in ((-34, 30, (255, 120, 30)), (-12, 44, (255, 150, 40)), (12, 40, (255, 140, 30)), (34, 28, (255, 110, 30)), (0, 26, (255, 214, 90))):
        ph = _ANIM["phase"]
        hh = hh * (1 + 0.28 * math.sin(ph * 1.9 + dx * 0.35))            # each tongue of flame licks up and down
        w = 11 * s * scale
        top = base_y - hh * s * scale
        cx2 = cx + dx * s * scale + 2.2 * s * math.sin(ph * 1.3 + dx)
        d.polygon([(cx2 - w, base_y), (cx2 - w * 0.4, top + hh * s * 0.35), (cx2, top), (cx2 + w * 0.4, top + hh * s * 0.35), (cx2 + w, base_y)], fill=col)


def _plate_kaprao(d, cx, cy, s, half_eaten=False):
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
    if half_eaten:  # a bite taken out of the egg
        d.ellipse([cx - 22 * s, cy - 10 * s, cx - 7 * s, cy + 3 * s], fill=(246, 246, 240))


def _food_stall(img, size, mood, rng, s, font_path, night, ref=(), cook_present=True, props=()):
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
        if cook_present:  # the burner is off once the cook has left (story logic)
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
        if cook_present:
            # spatula: handle up to the cook's left hand, blade in the food
            sp_hand = (wok_x - int(28 * s), wok_y - int(46 * s))
            dd.line([sp_hand, (wok_x + int(6 * s), wok_y - int(4 * s))], fill=(150, 150, 158), width=max(3, int(5 * s)))
            dd.polygon([(wok_x + int(2 * s), wok_y - int(10 * s)), (wok_x + int(22 * s), wok_y), (wok_x + int(16 * s), wok_y + int(6 * s)), (wok_x - int(2 * s), wok_y - int(2 * s))], fill=(190, 192, 200))

    fg.append(front)
    # steam: soft translucent puffs drawn later via glow layer
    info.update(cook_x=cook_x, counter_y=counter_y, wok=(wok_x, wok_y, wok_r), handle_end=handle_end,
                spatula_hand=(wok_x - int(28 * s), wok_y - int(46 * s)), ground=ground, steam=(wok_x, wok_y - int(40 * s)))
    if cook_present:
        lights.append(((wok_x, wok_y), int(h * 0.2), (255, 140, 50)))
    else:
        info["steam"] = None  # cold wok, no steam
    if "ledge_plate" in props:  # the plate set out at the back window: the story's key object
        px, py = int(w * 0.70), int(h * 0.34)
        d.rectangle([px - int(14 * s), py - int(70 * s), px + int(120 * s), py + int(10 * s)], fill=(28, 24, 26))    # window opening
        d.rectangle([px - int(14 * s), py + int(2 * s), px + int(120 * s), py + int(12 * s)], fill=(120, 96, 70))   # sill
        _plate_kaprao(d, px + int(52 * s), py - int(8 * s), s * 0.8, half_eaten="half_eaten" in props)
        if "second_plate" in props:
            _plate_kaprao(d, px + int(112 * s), py - int(8 * s), s * 0.62)
        lights.append(((px + int(52 * s), py - int(24 * s)), int(h * 0.16), (255, 200, 120)))
        info["ledge_steam"] = (px + int(52 * s), py - int(30 * s))
    return img, ground, lights, fg, info


def _alley(img, size, mood, rng, s, night, props=()):
    """Dead-end soi at night: brick walls closing in toward one far lamp, wet ground, bins."""
    w, h = size
    d = ImageDraw.Draw(img)
    vx, vy = int(w * 0.62), int(h * 0.46)
    half_w, half_h = int(w * 0.10), int(h * 0.14)
    ground = int(h * 0.88)
    wall = (34, 30, 36) if night else (150, 130, 118)
    lights = []
    # sky strip between the walls
    top, bottom = _sky_colors(mood)
    img.paste(_gradient((w, int(h * 0.5)), _lerp(top, (0, 0, 0), 0.4), bottom), (0, 0))
    d = ImageDraw.Draw(img)
    # walls (perspective)
    d.polygon([(0, 0), (vx - half_w, vy - half_h), (vx - half_w, vy + half_h), (0, h)], fill=wall)
    d.polygon([(w, 0), (vx + half_w, vy - half_h), (vx + half_w, vy + half_h), (w, h)], fill=_lerp(wall, (0, 0, 0), 0.25))
    # bricks: rows converging to the vanishing point
    for k in range(1, 14):
        t = k / 14
        for sign, x_edge in ((-1, 0), (1, w)):
            y0 = int(0 + (vy - half_h) * t)
            y1 = int(h - (h - (vy + half_h)) * t)
            xe = int(x_edge + ((vx + sign * half_w) - x_edge) * t)
            d.line([(x_edge, int(h * t * 0.0 + y0 * 0) + int(h * (1 - t) * 0)), (xe, y0)], fill=_lerp(wall, (0, 0, 0), 0.35), width=2) if False else None
            d.line([(xe, y0), (xe, y1)], fill=_lerp(wall, (0, 0, 0), 0.3), width=2)
    # far end wall + lamp
    d.rectangle([vx - half_w, vy - half_h, vx + half_w, vy + half_h], fill=_lerp(wall, (0, 0, 0), 0.5))
    d.polygon([(0, h), (w, h), (vx + half_w, vy + half_h), (vx - half_w, vy + half_h)], fill=(30, 32, 40) if night else (110, 108, 104))  # wet ground
    for i in range(10):  # puddle streaks of lamp light
        y = int(vy + half_h + (h - vy - half_h) * (i + 1) / 11)
        span = int((vx - 0) * 0.04 * (i + 1))
        d.line([(vx - span, y), (vx + span, y)], fill=(90, 84, 64), width=max(2, int(1 + i * 0.6)))
    lamp = (vx, vy - int(half_h * 0.2))
    d.rectangle([lamp[0] - 3, lamp[1], lamp[0] + 3, vy + half_h], fill=(20, 20, 24))
    lights.append((lamp, int(h * 0.30), (255, 200, 120)))
    # bins and a pipe in the foreground right
    d.rounded_rectangle([int(w * 0.80), int(h * 0.66), int(w * 0.93), int(h * 0.92)], 8, fill=(26, 40, 34))
    d.rectangle([int(w * 0.80), int(h * 0.64), int(w * 0.93), int(h * 0.67)], fill=(18, 28, 24))
    d.rounded_rectangle([int(w * 0.07), int(h * 0.70), int(w * 0.15), int(h * 0.92)], 6, fill=(40, 34, 30))
    info: dict = {}
    if "far_silhouette" in props:  # a tall figure standing still at the far end
        def silhouette(dd):
            fx, fy = vx, vy + half_h
            fh = int(h * 0.30)
            sil = (6, 6, 9)
            dd.ellipse([fx - fh * 0.11, fy - fh, fx + fh * 0.11, fy - fh * 0.78], fill=sil)
            dd.rounded_rectangle([fx - fh * 0.16, fy - fh * 0.80, fx + fh * 0.16, fy - fh * 0.28], int(fh * 0.06), fill=sil)
            dd.rectangle([fx - fh * 0.11, fy - fh * 0.30, fx + fh * 0.11, fy], fill=sil)
            dd.line([(fx - fh * 0.16, fy - fh * 0.74), (fx - fh * 0.24, fy - fh * 0.40)], fill=sil, width=max(3, int(fh * 0.07)))
            dd.line([(fx + fh * 0.16, fy - fh * 0.74), (fx + fh * 0.24, fy - fh * 0.40)], fill=sil, width=max(3, int(fh * 0.07)))
        info["post"] = [silhouette]
    return img, ground, lights, [], info


def _bus(img, size, mood, rng, s, night, props, stand_xs, bench_slots, named_slots):
    """Inside a city bus (longitudinal bench seats along the wall, windows above,
    fluorescent strip, handrails). Background passengers sit with eyes closed unless
    `passengers_awake` is in props."""
    w, h = size
    d = ImageDraw.Draw(img)
    light = mood.light if mood else "dim"
    sky_a, sky_b = {
        "golden": ((236, 150, 84), (252, 214, 150)),
        "bright": ((120, 176, 228), (232, 232, 220)),
    }.get(light, ((22, 26, 52), (70, 62, 96)) if light != "dark" else ((8, 10, 24), (30, 30, 56)))
    wall = (186, 190, 194) if light in ("golden", "bright") else (84, 90, 100)
    d.rectangle([0, 0, w, h], fill=wall)
    d.rectangle([0, 0, w, int(h * 0.15)], fill=_lerp(wall, (255, 255, 255), 0.15))              # ceiling
    for fx in (0.12, 0.40, 0.68):                                                              # fluorescent strips
        d.rounded_rectangle([int(w * fx), int(h * 0.055), int(w * (fx + 0.2)), int(h * 0.075)], 6, fill=(246, 250, 255))
    # four windows with the evening city sliding past
    wins = []
    for i in range(4):
        x0 = int(w * (0.03 + i * 0.24)); x1 = x0 + int(w * 0.21)
        y0, y1 = int(h * 0.17), int(h * 0.50)
        img.paste(_gradient((x1 - x0, y1 - y0), sky_a, sky_b), (x0, y0))
        d = ImageDraw.Draw(img)
        _skyline(d, rng, x1, y1, (int(h * 0.04), int(h * 0.13)), _lerp(sky_a, (0, 0, 0), 0.65), (252, 220, 130) if light not in ("golden", "bright") else None, 0.25, bw=(18, 46))
        d.rectangle([x0 - 6, y0 - 6, x0, y1 + 6], fill=(40, 44, 52)); d.rectangle([x1, y0 - 6, x1 + 6, y1 + 6], fill=(40, 44, 52))
        d.rectangle([x0 - 6, y0 - 8, x1 + 6, y0], fill=(40, 44, 52)); d.rectangle([x0 - 6, y1, x1 + 6, y1 + 8], fill=(40, 44, 52))
        wins.append((x0, x1))
    # wall panel + priority-seat sign
    d.rectangle([0, int(h * 0.50), w, int(h * 0.64)], fill=_lerp(wall, (60, 70, 90), 0.35))
    sx = int(w * 0.04)
    d.rounded_rectangle([sx, int(h * 0.54), sx + int(w * 0.11), int(h * 0.60)], 6, fill=(60, 110, 200))
    for k in range(4):
        d.ellipse([sx + 10 + k * int(w * 0.024), int(h * 0.555), sx + 10 + k * int(w * 0.024) + int(w * 0.016), int(h * 0.555) + int(w * 0.016)], fill=(250, 250, 250))
    # bench along the wall
    bench_top = int(h * 0.74)
    d.rectangle([0, int(h * 0.60), w, bench_top], fill=(54, 96, 182))                          # seat back
    d.rectangle([0, bench_top, w, int(h * 0.80)], fill=(70, 120, 214))                         # cushion
    d.rectangle([0, int(h * 0.80), w, int(h * 0.84)], fill=(40, 60, 110))
    d.rectangle([0, int(h * 0.84), w, h], fill=(52, 54, 60))                                   # floor
    for fx in range(0, w, 48):
        d.line([(fx, int(h * 0.86)), (fx, h)], fill=(40, 42, 46), width=3)
    awake = "passengers_awake" in props
    palettes = ["#d07a6e", "#6ea078", "#e6c878", "#8c78be", "#5a96be"]
    names = ["ผู้โดยสาร1", "ผู้โดยสาร2", "ผู้โดยสาร3", "ผู้โดยสาร4", "ผู้โดยสาร5"]
    for k, fx in enumerate(bench_slots):
        cx = int(w * fx)
        sc = s * 0.95
        for dx in (-14, 3):  # legs hang below the cushion
            d.rectangle([cx + dx * sc, bench_top - 4 * sc, cx + (dx + 11) * sc, int(h * 0.88)], fill=(48, 52, 70))
        if fx in named_slots:
            continue  # a named character is drawn here later
        hairs = [("ผมยาว ดำ", "หญิง"), ("ผมสั้น น้ำตาล", "ชาย"), ("ผมบ๊อบ ดำ", "หญิง"), ("ผมมวย เทา", "หญิง"), ("ผมสั้น ดำ", "ชาย")]
        col = character_colors("เสื้อ", [palettes[k % len(palettes)]], names[k], hair=hairs[k % 5][0], gender=hairs[k % 5][1])
        _draw_character(d, cx, bench_top + int(22 * sc), sc, col, sitting=True,
                        expression="neutral" if awake else "asleep",
                        hands={"L": (cx - 10 * sc, bench_top - 14 * sc), "R": (cx + 10 * sc, bench_top - 14 * sc)})
    # overhead rail with hanging loops, and a vertical pole next to each standing passenger
    d.rectangle([0, int(h * 0.19), w, int(h * 0.205)], fill=(205, 210, 216))
    for k in range(9):
        lx = int(w * (0.06 + k * 0.115))
        d.line([(lx, int(h * 0.205)), (lx, int(h * 0.30))], fill=(70, 70, 76), width=max(2, int(3 * s)))
        d.ellipse([lx - 9 * s, int(h * 0.30), lx + 9 * s, int(h * 0.30) + 22 * s], outline=(240, 240, 240), width=max(3, int(4 * s)))
    for sx_ in stand_xs:
        d.rectangle([sx_ - 4 * s, int(h * 0.19), sx_ + 4 * s, int(h * 0.92)], fill=(214, 218, 224))
    lights = [((int(w * fx) + int(w * 0.1), int(h * 0.075)), int(h * 0.30), (230, 240, 255)) for fx in (0.12, 0.40, 0.68)]
    return img, int(h * 0.94), lights, [], {"bench_top": bench_top}


def _steam(img: Image.Image, origin, s: float, rng: random.Random) -> Image.Image:
    ph = _ANIM["phase"]
    rng = random.Random(ph * 7 + 1)                    # puffs re-roll every step so the steam really moves
    origin = (origin[0], origin[1] - (ph % 8) * 3 * s)
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
    props: tuple = (),
    speaker: str | None = None,
    focus_out: dict | None = None,
    anim: dict | None = None,
    compare: dict | None = None,
    signs: dict | None = None,
) -> Image.Image:
    """Draw one scene. `characters` = list of dicts from `character_colors`."""
    _ANIM["phase"] = (anim or {}).get("phase", 0)
    _ANIM["prog"] = (anim or {}).get("prog")
    _ANIM["compare"] = compare
    _ANIM["signs"] = signs
    if font_path is None:  # signs carry Thai text: find a font ourselves (best effort)
        try:
            font_path = find_thai_font()
        except PipelineError:
            font_path = None
    ss = 2  # supersample for smooth edges
    w, h = size[0] * ss, size[1] * ss
    rng = random.Random(int(hashlib.md5(f"{seed}{setting}".encode()).hexdigest(), 16) % (2**32))
    s = h / 720 * 1.3 * (1.45 if setting in ("food_stall", "chicken_cart") else (1.5 if setting == "bus" else 1.0))
    layout = None
    if setting == "bus":
        seated = [c for c in (characters or []) if "seated" in c.get("items", ())]
        standing = [c for c in (characters or []) if "seated" not in c.get("items", ())]
        if "protagonist_seated" in props and standing:   # she has a seat now; whoever had it stands
            seated, standing = [standing[0]] + seated[1:], seated[:1] + standing[1:]
        slots = [0.10, 0.28, 0.46, 0.64, 0.82]
        s_stand = s * 1.2
        named_slots = [0.46, 0.64, 0.28, 0.82, 0.10][: len(seated)]
        stand_slots = [0.33, 0.72, 0.52, 0.18]
        layout = {"bench_slots": slots, "named_slots": named_slots, "stand_xs": [int(w * fx) + int(28 * s_stand) for fx in stand_slots[: len(standing)]],
                  "seated": seated, "standing": standing, "stand_slots": stand_slots}
    img, ground, lights, seat, fg, info = _scene_background(
        setting, (w, h), mood, rng, s, font_path, tuple(reference_palette),
        cook_present=any("apron" in c.get("items", ()) for c in (characters or [])), props=tuple(props), layout=layout,
    )

    night_ = _is_night(mood)
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))   # everyone is drawn on their own layer, then lit and composited
    focus: dict = {}

    def draw_fig(d_, x_, gy_, s_, col_, **kw):
        """Draw one person; the speaker is a touch bigger, mid-word, softly lit, and recorded as the close-up target."""
        is_speaker = bool(speaker) and col_.get("name") == speaker
        talking = is_speaker
        a = anim or {}
        if is_speaker and "mouth" in a:
            talking = (False, True, "half")[a["mouth"]]
        if a.get("blink") and kw.get("expression") != "asleep":
            kw["expression"] = "asleep"      # eyes shut for one frame = a blink
        if is_speaker:
            s_ = s_ * 1.08
            if kw.get("expression") == "asleep" and not a.get("blink"):
                kw["expression"] = "neutral"
        br = a.get("breath", 0.0)
        if kw.get("walk") is not None:
            br = -abs(math.sin(math.pi * kw["walk"] / 4)) * 1.6     # footfall bob
        _ground_shadow(d_, x_, gy_ + (0 if not kw.get("sitting") else 22 * s_), s_, night_)
        pos = _draw_character(d_, x_, gy_, s_, col_, talking=talking, breath=br, **kw)
        if is_speaker:
            focus["x"], focus["y"] = pos["head"][0] / w, pos["head"][1] / h
            lights.append(((pos["head"][0], pos["head"][1]), int(h * 0.2), (104, 92, 80)))
        return pos

    figs = characters or []
    bus_subject_x = None
    hero = (characters or [None])[0]  # the first character is the heroine
    if layout is not None:  # bus: seated people on the bench, standers holding the poles
        face = expression_for(mood)
        d = ImageDraw.Draw(layer)
        pretending = "passengers_awake" not in props and "protagonist_seated" not in props and (mood is None or mood.tension < 5)
        for i, (col, fx) in enumerate(zip(layout["seated"], layout["named_slots"])):
            cx = int(w * fx) + int(3 * s * math.sin(_ANIM["phase"] * 0.8 + i))   # the bus rocks: everyone sways a little
            sc = s * 0.95
            hands = {"L": (cx - 10 * sc, info["bench_top"] - 14 * sc), "R": (cx + 10 * sc, info["bench_top"] - 14 * sc)}
            if mood is not None and mood.tension >= 5 and layout["stand_slots"] and i == 0 and layout["standing"]:
                px = int(w * layout["stand_slots"][0])
                hands["R"] = (px + 24 * s * 1.2, ground - 96 * s * 1.2)   # he catches her arm
            draw_fig(d, cx, info["bench_top"] + int(22 * sc), sc, col, sitting=True,
                            expression="asleep" if (pretending and i == 0) else face, hands=hands)
            if col is hero:
                lights.append(((cx, info["bench_top"] - int(70 * sc)), int(h * 0.24), (92, 78, 70)))
        for k, (col, fx) in enumerate(zip(layout["standing"], layout["stand_slots"])):
            cx = int(w * fx) + int(4 * s * math.sin(_ANIM["phase"] * 0.8 + k + 1.5))
            ss_ = s * 1.2 * (1.1 if col is hero else 1.0)   # the heroine is a touch bigger and softly lit
            shoulder_y = ground - 120 * ss_
            hands = {"R": (cx + 28 * ss_, shoulder_y - 30 * ss_), "L": (cx - 22 * ss_, shoulder_y + 58 * ss_)}
            if k == 0 and mood is not None and mood.tension >= 3 and "protagonist_seated" not in props:   # presses her belly
                hands["L"] = (cx - 4 * ss_, ground - 84 * ss_)
            draw_fig(d, cx, ground, ss_, col, expression=face, hands=hands)
            if col is hero:
                lights.append(((cx, ground - int(100 * ss_)), int(h * 0.24), (92, 78, 70)))
            if bus_subject_x is None:
                bus_subject_x = cx / w
        figs = []
    n = len(figs)
    face = expression_for(mood)
    cook_placed = False
    customers = 0
    subject_x = bus_subject_x
    for i, col in enumerate(figs):
        d = ImageDraw.Draw(layer)
        hands = None
        if setting == "food_stall":
            if "apron" in col.get("items", ()) and not cook_placed:
                cook_placed = True
                subject_x = info["cook_x"] / w
                ph = (anim or {}).get("phase", 0)
                ang = 2 * math.pi * ph / 8
                sx, sy = info["spatula_hand"]      # stir-fry: spatula circles in the wok, the other hand tosses the handle
                draw_fig(d, info["cook_x"], ground, s, col, expression=face,
                         hands={"L": (sx + 15 * s * math.cos(ang), sy + 8 * s * math.sin(ang)),
                                "R": (info["handle_end"][0], info["handle_end"][1] + 5 * s * math.sin(ang * 2))})
            else:  # customers stand to the right of the counter, side by side
                cx = int(w * (0.64 + 0.125 * customers))
                customers += 1
                pos = draw_fig(d, cx, ground, s, col, expression=face)
                if "headlamp" in col.get("items", ()):
                    lights.append(((pos["head"][0], pos["head"][1] - int(10 * s)), int(h * 0.2), (255, 246, 210)))
            continue
        if setting == "compare":   # first character stands under the left column, the vendor under the right
            side = info["right_x"] if "apron" in col.get("items", ()) else info["left_x"]
            if subject_x is None:
                subject_x = side / w
            draw_fig(d, side, ground, s * 1.25, col, expression=face)
            continue
        if setting == "chicken_cart":
            if "apron" in col.get("items", ()) and not cook_placed:
                cook_placed = True
                subject_x = info["cook_x"] / w
                bx0, by0, bx1, by1 = info["board"]
                ph = (anim or {}).get("phase", 0)
                chop = abs(math.sin(math.pi * ph / 4))              # cleaver rises and falls twice per cycle
                bxm = (bx0 + bx1) // 2
                pos = draw_fig(d, info["cook_x"], ground, s * 1.25, col, expression=face,
                               hands={"R": (bxm + 14 * s, by0 - 38 * s + 30 * s * (1 - chop)), "L": (bxm - 26 * s, by0 - 8 * s)})
                if "serving" in props:                               # lifts the plate across the counter toward the customer
                    t_ = (math.sin(2 * math.pi * ph / 8) + 1) / 2
                    px_, py_ = bxm + (30 + 80 * t_) * s, by0 - (26 + 14 * t_) * s
                    pos = draw_fig(d, info["cook_x"], ground, s * 1.25, col, expression=face, hands={"R": (px_ + 20 * s, py_ + 4 * s), "L": (px_ - 22 * s, py_ + 4 * s)})
                    from life_lesson.video.places import plate_chicken_rice
                    plate_chicken_rice(d, px_, py_ + 8 * s, s * 0.8)
                else:
                    hx, hy = pos["R"]                                # cleaver follows the hand
                    d.line([(hx, hy), (hx + 4 * s, hy + 34 * s)], fill=(214, 216, 224), width=max(6, int(14 * s)))
                    d.line([(hx, hy - 4 * s), (hx - 2 * s, hy - 22 * s)], fill=(120, 80, 44), width=max(4, int(8 * s)))
            else:  # customers sit on the plastic stools
                sx = info["stools"][min(customers, len(info["stools"]) - 1)]
                customers += 1
                seat_top = info["stool_top"]
                pos = draw_fig(d, sx, seat_top + int(22 * s), s, col, sitting=True, expression=face,
                               hands={"L": (sx - 26 * s, seat_top - 40 * s), "R": (sx + 30 * s, seat_top - 46 * s)})
                if subject_x is None:
                    subject_x = sx / w
            continue
        x = int(w * (0.5 if n == 1 else 0.3 + 0.4 * i / max(1, n - 1)))
        if setting == "alley":
            x = int(w * (0.2 + 0.17 * i))
        if setting in ("room", "office"):
            x = int(w * (0.22 + 0.1 * i))
        gy = ground - 22 if seat == "sit" else (ground - 4 if seat == "boat" else ground)
        if seat == "sit":  # hands rest on the desk top
            desk_top = ground - 40
            hands = {"L": (x - 4 * s, desk_top - 6), "R": (x + 38 * s, desk_top - 6)}
        if subject_x is None:
            subject_x = x / w
        scale_ = s * (1.45 if seat == "sit" else (1.1 if seat else (1.3 if setting == "alley" else (1.7 if setting == "kitchen" else (1.6 if setting in ("mall", "market") else (1.5 if setting == "bts" else (1.7 if setting == "bus_stop" else (1.55 if setting == "home_front" else 1.4))))))))
        wk = None
        if "walking" in props and seat is None and _ANIM["prog"] is not None:   # really crosses the frame
            x = int(w * (0.14 + 0.72 * _ANIM["prog"]) - i * 0.07 * w)
        if "walking" in props and seat is None:   # walking cycle: legs and arms swing, body bobs
            wk = (anim or {}).get("phase", 0) + 2 * i
            sw_ = math.sin(2 * math.pi * wk / 8)
            hands = {"L": (x - 24 * scale_, gy - 62 * scale_ + 12 * scale_ * sw_), "R": (x + 24 * scale_, gy - 62 * scale_ - 12 * scale_ * sw_)}   # arms swing up/down at the sides
        coffee = "coffee" in props and wk is None and seat is None
        carrying = "carrying" in props and wk is None and seat is None
        if coffee or carrying:
            lift = max(0.0, math.sin(math.pi * _ANIM["phase"] / 8)) ** 2 if coffee else 0.0   # a sip each cycle
            rx = x + (26 - 14 * lift) * scale_
            ry = gy - (66 + 74 * lift) * scale_ + (3 * scale_ * math.sin(_ANIM["phase"] * 0.8) if carrying else 0)
            hands = {"L": (x - 27 * scale_, gy - 61 * scale_), "R": (rx, ry)}
        if wk is not None and _ANIM["prog"] is not None:   # crossing the frame: draw her side-on, a real stride
            _ground_shadow(d, x, gy, scale_, night_)
            pos = _draw_walker_side(d, x, gy, scale_, col, wk, face)
        else:
            pos = draw_fig(d, x, gy, scale_, col, sitting=seat is not None, expression=face, hands=hands, walk=wk)
        if coffee:       # paper cup in the hand: it travels up to the mouth and back
            hx, hy = pos["R"]
            d.rounded_rectangle([hx - 6.5 * scale_, hy - 15 * scale_, hx + 6.5 * scale_, hy + 5 * scale_], 2 * scale_, fill=(250, 246, 238), outline=(190, 170, 150), width=max(1, int(1.5 * scale_)))
            d.rectangle([hx - 6.5 * scale_, hy - 9 * scale_, hx + 6.5 * scale_, hy - 3 * scale_], fill=(150, 98, 60))
            d.rounded_rectangle([hx - 7.5 * scale_, hy - 18 * scale_, hx + 7.5 * scale_, hy - 14 * scale_], 2 * scale_, fill=(60, 44, 36))
        if carrying:     # a big shopping bag swinging from the hand
            hx, hy = pos["R"]
            d.rounded_rectangle([hx - 15 * scale_, hy + 8 * scale_, hx + 15 * scale_, hy + 46 * scale_], 4 * scale_, fill=(236, 98, 120), outline=(170, 60, 84), width=max(1, int(2 * scale_)))
            d.arc([hx - 8 * scale_, hy - 2 * scale_, hx + 8 * scale_, hy + 16 * scale_], 180, 360, fill=(120, 40, 56), width=max(2, int(2.4 * scale_)))
        if "headlamp" in col.get("items", ()):  # the lamp lights his face and the wall behind
            lights.append(((pos["head"][0], pos["head"][1] - int(10 * s)), int(h * 0.22), (255, 246, 210)))

    if focus_out is not None:
        focus_out.update(focus)
    if subject_out is not None:
        subject_out["x"] = subject_x if subject_x is not None else 0.5
    d = ImageDraw.Draw(layer)
    for paint in fg:
        paint(d)
    layer = _shade_layer(layer, mood)                       # volume: rim light, far-edge shadow, foot occlusion
    if setting != "compare":
        img = _cast_shadow(img, layer, 0.22 if _is_night(mood) else 0.34)   # soft cast shadow on the set behind
    img = Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")
    night = _is_night(mood)
    ph = _ANIM["phase"]
    for center, radius, color in lights:
        if night or setting in ("island", "food_stall", "chicken_cart", "kitchen"):
            k = 1.0
            if color[2] < 170:                       # warm lights (fire, bulbs) breathe
                k = 0.82 + 0.26 * math.sin(ph * 1.7 + center[0] * 0.013)
            if mood is not None and mood.light == "flicker":   # failing tube: drops out on some steps
                k = 0.25 if ph % 3 == 0 else (0.55 if ph % 5 == 1 else 1.0)
            img = _glow(img, center, radius, color, 0.75 * k)
    d = ImageDraw.Draw(img)
    for paint in info.get("post", ()):
        paint(d)
    if setting in ("food_stall", "chicken_cart"):
        if info.get("steam"):
            img = _steam(img, info["steam"], s, rng)
        if info.get("ledge_steam"):  # thin wisp over the plate set out at the back window
            img = _steam(img, info["ledge_steam"], s * 0.35, rng)

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
