"""Prototype v2 character rig: the existing soft characters (characters/<id>.json, character_soft.py shapes) with
  * a small set of hand-designed poses whose shoulder, elbow and wrist lengths stay consistent,
  * hands that follow the forearm's direction (no mitten pointing straight down while the arm points sideways),
  * held objects drawn between the arm and the fingers, so hands visibly grip them,
  * whole-face expressions: eyes, lids, brows, mouth and blush change together (not just the mouth).

Read-only use of the existing modules: nothing in experiments/shorts or experiments/cartoon_storyboard is modified.
"""

from __future__ import annotations

import math
import sys
from functools import lru_cache
from pathlib import Path

from PIL import Image

SHORTS = Path(__file__).resolve().parent.parent / "shorts"
sys.path.insert(0, str(SHORTS))

import character_art as CA  # noqa: E402  (also puts the shared Pillow toolkit on sys.path)
import character_soft as CS  # noqa: E402
from art import Pen  # noqa: E402
from character_art import INK, rgb, shade  # noqa: E402

SS = 3                      # supersampling for crisp close-ups
SHOULDER_L, SHOULDER_R = (192, 436), (328, 436)

# (shoulder, elbow, wrist) per arm, in body coordinates. Upper arm ~85 px, forearm ~65-80 px in every pose.
POSES = {
    "relaxed": ((SHOULDER_L, (184, 520), (190, 598)), (SHOULDER_R, (336, 520), (330, 598))),
    "hold_chest": ((SHOULDER_L, (180, 518), (232, 560)), (SHOULDER_R, (340, 518), (288, 560))),
    "clasp": ((SHOULDER_L, (184, 520), (250, 566)), (SHOULDER_R, (336, 520), (270, 566))),
    "offer": ((SHOULDER_L, (196, 520), (266, 548)), (SHOULDER_R, (350, 512), (318, 550))),
}


def _arm_tube(pen, pts, skin, sleeve, sleeve_frac, puff, cuff_fold):
    """character_soft._arm without the hand: the hand is drawn later, after any held object."""
    path = CS._tube(pen, pts, 31, 21, skin)
    n = len(path) - 1
    cut = max(2, int(n * sleeve_frac))
    width = lambda i: (31 + (21 - 31) * i / n) / 2
    extra = 3.5 if puff else 3
    for i in range(cut + 1):
        x, y = path[i]
        pen.circle(x, y, width(i) + extra + 3.4, INK)
    for i in range(cut + 1):
        x, y = path[i]
        pen.circle(x, y, width(i) + extra, sleeve)
    if cuff_fold:
        cx, cy = path[cut]
        pen.line([(cx - 17, cy - 2), (cx + 17, cy + 5)], shade(sleeve, 1.18), 9)
        pen.line([(cx - 17, cy - 2), (cx + 17, cy + 5)], shade(sleeve, 0.78), 2.5)
    sx, sy = path[0]
    pen.circle(sx, sy, width(0) + extra + 1, sleeve)
    return path


def _hand(pen, wrist, toward, skin):
    """A small mitten whose long axis follows the forearm (elbow -> wrist)."""
    ang = math.atan2(toward[1] - wrist[1], toward[0] - wrist[0]) - math.pi / 2   # +y in the template = along the arm
    c, s = math.cos(ang), math.sin(ang)
    tpl = [(-11, -4), (11, -4), (14, 12), (6, 26), (-6, 26), (-14, 12)]
    pts = [(wrist[0] + x * c - y * s, wrist[1] + x * s + y * c) for x, y in tpl]
    CS._shape(pen, pts, skin, 3.2, 3, 0.28)


def draw_body(pen, d: dict, o: dict, pose: str, held=None):
    """The soft character body (no brows; the face layer adds them) in one of POSES, optionally holding `held`:
    a callable held(pen, (x, y)) drawn centred between the wrists, before the hands."""
    skin, cheek, hair = rgb(d["skin"]), rgb(d["cheek"]), rgb(d.get("hair", "#3B2A26"))
    top, bottom = rgb(o["top"]), rgb(o.get("bottom", "#4A5A80"))
    shoe = rgb(o.get("shoe", "#4A3B32"))
    style = d.get("hair_style", "short")
    woman = d.get("gender") == "female"
    kind = o.get("kind", d.get("outfit_kind", "blouse_skirt" if woman else "shirt_slacks"))
    if woman and style == "bob":
        CS._hair_back_woman(pen, hair)
    elif woman and style == "long":
        CS._hair_back_long(pen, hair)
    body = {"blouse_skirt": CS._woman, "shirt_slacks": CS._man, "hoodie_jeans": CS._hoodie_jeans, "dress": CS._dress,
            "sarong": CS._sarong}[kind]
    body(pen, d, o, skin, top, bottom, shoe)
    puff = kind in ("blouse_skirt", "dress", "sarong")
    sleeve = o.get("sleeve", 0.24 if puff else (0.5 if kind == "shirt_slacks" else 0.72))
    arms = POSES[pose]
    for pts in arms:
        _arm_tube(pen, list(pts), skin, top, sleeve, puff, kind == "shirt_slacks")
    if held is not None:
        (_, _, wl), (_, _, wr) = arms
        held(pen, ((wl[0] + wr[0]) / 2, (wl[1] + wr[1]) / 2))
    for _, elbow, wrist in arms:
        _hand(pen, wrist, (wrist[0] + (wrist[0] - elbow[0]), wrist[1] + (wrist[1] - elbow[1])), skin)
    CS._neck(pen, skin)
    for s in (-1, 1):
        CS._ear(pen, s, skin)
    CS._head(pen, skin, cheek)
    if d.get("age_lines"):
        CS._age_lines(pen, skin)
    if style in ("bob", "long"):
        _fringe_high(pen, hair, clip=(style == "bob" and not d.get("no_clip")))
    elif style == "gray_bun":
        CS._hair_gray(pen, hair)
    else:
        CS._hair_man(pen, hair)
    if d.get("glasses"):
        for x in (210, 310):
            pen.ellipse(x, 270, 36, 30, None, outline=(96, 72, 64), width=4)
        pen.line([(246, 268), (274, 268)], (96, 72, 64), 4)


def _fringe_high(pen, hair, clip=False):
    """Side-swept fringe with the hairline kept above the brows (the old fringe covered the left brow and eye)."""
    cap = [(134, 258), (144, 198), (184, 152), (242, 132), (306, 136), (356, 164), (384, 214), (388, 258), (370, 230),
           (342, 208), (306, 194), (272, 190), (240, 194), (210, 202), (184, 214), (160, 232), (142, 256)]
    CS._shape(pen, cap, hair, 3.6, 3, 0.18)
    CS._line(pen, [(204, 166), (252, 150), (308, 160)], shade(hair, 1.6), 5)
    if clip:
        CS._shape(pen, [(168, 200), (186, 190), (198, 206), (184, 218)], (250, 214, 110), 2.6, 2, 0.2)


# --- faces: eyes + lids + brows + mouth + blush, all chosen together ------------------------------------------------------

EXPRESSIONS = {
    #             eyes       brows        mouth (when not talking)   blush
    "neutral":   ("open",    "soft",      "smile", 0.0),
    "surprised": ("wide",    "raised",    "o", 0.0),
    "blissful":  ("happy",   "soft",      "grin_closed", 1.0),
    "eager":     ("sparkle", "raised",    "grin", 0.6),
    "delighted": ("happy",   "raised",    "grin", 0.8),
    "meh":       ("half",    "skeptic",   "flat", 0.0),
    "puzzled":   ("open",    "worried",   "small", 0.0),
    "determined": ("open",   "determined", "smirk", 0.3),
}


def _brows(pen, kind, col, dy):
    if kind == "raised":
        for x in (210, 310):
            pen.arc(x, 222 + dy, 30, 14, 200, 340, col, 6)
    elif kind == "worried":
        for x, s in ((210, 1), (310, -1)):
            pen.line([(x - 26 * s, 236 + dy), (x + 22 * s, 226 + dy)], col, 6)
    elif kind == "skeptic":
        pen.arc(210, 222 + dy, 30, 14, 200, 340, col, 6)
        pen.line([(284, 240 + dy), (334, 238 + dy)], col, 6)
    elif kind == "determined":
        for x, s in ((210, 1), (310, -1)):
            pen.line([(x - 26 * s, 228 + dy), (x + 24 * s, 238 + dy)], col, 6)
    else:
        for x in (210, 310):
            pen.arc(x, 232 + dy, 30, 13, 205, 335, col, 6)


def _eyes(pen, kind, closed, dy, skin, lashes):
    for i, x in enumerate((210, 310)):
        out = -1 if i == 0 else 1
        y = 270 + dy
        if closed or kind == "happy":
            pen.arc(x, y + (6 if kind == "happy" else 0), 16, 10 if kind == "happy" else 8,
                    200 if kind == "happy" else 20, 340 if kind == "happy" else 160, INK, 6)
            continue
        k = 1.35 if kind == "wide" else 1.22
        pen.ellipse(x, y, 13 * k, 17.5 * k, (58, 40, 40))
        pen.ellipse(x, y + 6, 9 * k, 9 * k, (110, 76, 66))
        hl = 4 if kind == "wide" else 5.5
        pen.circle(x + 5, y - 8, hl * (1.3 if kind == "sparkle" else 1.0), (255, 255, 255))
        pen.circle(x - 5, y + 8, 2.8, (255, 255, 255))
        if kind == "sparkle":
            pen.circle(x + 9, y + 2, 2.4, (255, 255, 255))
        if kind == "half":                                           # half-closed: only the lower half of the eye shows
            pen.poly([(x - 20, y - 26), (x + 20, y - 26), (x + 20, y), (x - 20, y)], skin)
            pen.chord(x, y, 13 * k, 17.5 * k, 0, 180, (58, 40, 40))
            pen.circle(x + 4, y + 6, 3, (255, 255, 255))
            pen.line([(x - 19, y), (x + 19, y - 1)], INK, 5)
        else:
            pen.arc(x, y, 16 * k, 20 * k, 200, 340, INK, 5)
        if lashes and kind != "half":
            pen.line([(x + out * 15 * k, y - 12), (x + out * 23 * k, y - 18)], INK, 3.4)


def _mouth(pen, kind, level, dy):
    cx, cy = 260, 342 + dy
    dark, tongue = (112, 46, 52), (232, 120, 128)
    if level is not None:                                            # talking: opening follows the audio, shape stays smiley
        h = 4 + 22 * min(1.0, level * 1.8)
        pen.chord(cx, cy - 4, 26, h + 6, 0, 180, INK)
        pen.chord(cx, cy - 4, 21, h, 0, 180, dark)
        if h > 12:
            pen.ellipse(cx, cy + h * 0.55, 11, 5, tongue)
        return
    if kind == "smile":
        pen.arc(cx, cy - 8, 22, 13, 20, 160, INK, 5)
    elif kind == "grin_closed":
        pen.arc(cx, cy - 10, 26, 16, 15, 165, INK, 6)
    elif kind == "grin":
        pen.chord(cx, cy - 6, 28, 22, 0, 180, INK)
        pen.chord(cx, cy - 6, 23, 17, 0, 180, dark)
        pen.ellipse(cx, cy + 6, 11, 5, tongue)
    elif kind == "o":
        pen.ellipse(cx, cy + 2, 13, 16, INK)
        pen.ellipse(cx, cy + 2, 9, 12, dark)
    elif kind == "small":
        pen.ellipse(cx, cy, 8, 6, INK)
    elif kind == "flat":
        pen.line([(cx - 18, cy - 2), (cx + 16, cy)], INK, 5)
    elif kind == "smirk":
        pen.line(CS.CA._spline([(cx - 20, cy - 4), (cx + 2, cy + 2), (cx + 22, cy - 10)]), INK, 5)
    elif kind == "chew":
        pen.ellipse(cx, cy, 14, 7, INK)


def draw_face(pen, d, expr, talk_level, blink, chew_phase, dy):
    eyes, brows, mouth, blush = EXPRESSIONS[expr]
    skin = rgb(d["skin"])
    if blush:
        for x in (206, 314):
            pen.ellipse(x, 316 + dy, 26, 13, CA._mix(skin, (244, 150, 150), 0.45 * blush))
    _eyes(pen, eyes, blink, dy, skin, d.get("lashes", True))
    _brows(pen, brows, shade(rgb(d.get("hair", "#3B2A26")), 1.0), dy)
    if talk_level is None and chew_phase is not None:
        mouth = "chew" if chew_phase else "grin_closed"
    _mouth(pen, mouth, talk_level, dy)


def _chibi_scaled(img, k, f):
    """character_art._chibi for an image f times the base canvas (we keep the supersampled pixels for close-ups)."""
    cut, ch = int(CA.CHIBI_CUT * f), img.height
    low = img.crop((0, cut, img.width, ch))
    new_h = int((ch - cut) * k)
    shift = (ch - cut) - new_h
    out = Image.new("RGBA", img.size, (0, 0, 0, 0))
    out.paste(img.crop((0, 0, img.width, cut)), (0, shift))
    out.paste(low.resize((img.width, new_h), Image.LANCZOS), (0, cut + shift))
    return out, shift


@lru_cache(maxsize=256)
def sprite(char_id: str, outfit: str, pose: str, expr: str, talk: int | None, blink: bool, chew: int | None,
           held: str | None, height: int) -> Image.Image:
    """Full-body sprite whose canvas is `height` px tall (drawn at 3x, so close-ups stay sharp).
    talk = mouth opening step 0..6 while speaking, or None."""
    import props_v2
    ch = CA.load_character(char_id)
    d, o = ch["draw"], ch["outfits"][outfit]
    pen = Pen(CA.CW, CA.CH, ss=SS)
    draw_body(pen, d, o, pose, props_v2.HELD.get(held) if held else None)
    body = CA._soft_shade(pen.img)
    face = Pen(CA.CW, CA.CH, ss=SS)
    draw_face(face, d, expr, None if talk is None else talk / 6, blink, chew, 0)
    face_img = face.img
    if d.get("chibi"):
        body, dy = _chibi_scaled(body, d["chibi"], SS)
        moved = Image.new("RGBA", face_img.size, (0, 0, 0, 0))
        moved.paste(face_img, (0, dy))
        face_img = moved
    body.alpha_composite(face_img)
    return body.resize((max(1, round(body.width * height / body.height)), height), Image.LANCZOS)
