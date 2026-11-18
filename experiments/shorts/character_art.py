"""Layered cartoon characters for Shorts, drawn with Pillow (no image-generation API).

Each character is drawn from its `characters/<id>.json` into separate RGBA layers on one
shared canvas: body, eyes open/closed, and 4 mouth shapes. `sprites()` composites every
(mouth, eyes) combination once at the target scale, so a frame only pastes a cached sprite.
"""

from __future__ import annotations

import json
import math
import sys
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "cartoon_storyboard"))  # shared Pillow drawing toolkit

from art import INK as _HARD_INK, Pen  # noqa: E402

INK = (118, 88, 72)  # softer warm brown than the backgrounds' outline, like the Life Lesson illustrations
from subtitles import _wrap_whole, font as thai_font  # noqa: E402

CW, CH = 520, 900  # canvas, feet at GROUND_Y
GROUND_Y = 880
HEAD = (260, 255)
MOUTH_NAMES = ("closed", "slight", "open", "wide")


def rgb(h: str):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _mix(a, b, t):
    return tuple(int(x + (y - x) * t) for x, y in zip(a, b))


def shade(c, f):
    return tuple(max(0, min(255, int(v * f))) for v in c)


def load_character(char_id: str) -> dict:
    path = HERE / "characters" / f"{char_id}.json"
    if not path.is_file():
        raise FileNotFoundError(f"character '{char_id}' not found ({path})")
    return json.loads(path.read_text(encoding="utf-8"))


def _outlined_ellipse(pen, cx, cy, rx, ry, fill, w=3.6):
    pen.ellipse(cx, cy, rx + w, ry + w, INK)
    pen.ellipse(cx, cy, rx, ry, fill)


def _smooth(pts, iterations=2, ratio=0.14):
    """Chaikin corner cutting: straight, stiff polygons become soft rounded shapes."""
    for _ in range(iterations):
        out = []
        for i, p in enumerate(pts):
            q = pts[(i + 1) % len(pts)]
            out.append((p[0] + (q[0] - p[0]) * ratio, p[1] + (q[1] - p[1]) * ratio))
            out.append((p[0] + (q[0] - p[0]) * (1 - ratio), p[1] + (q[1] - p[1]) * (1 - ratio)))
        pts = out
    return pts


def _outlined_poly(pen, pts, fill, w=3.6, smooth=2):
    pen.poly(_smooth(pts, smooth) if smooth else pts, fill, outline=INK, width=w)


def _limb(pen, a, b, width, fill, w=3.6, taper=0.3):
    n = 16
    discs = [(a[0] + (b[0] - a[0]) * i / n, a[1] + (b[1] - a[1]) * i / n, width * (1 - taper * i / n) / 2)
             for i in range(n + 1)]
    for x, y, r in discs:
        pen.circle(x, y, r + w, INK)
    for x, y, r in discs:
        pen.circle(x, y, r, fill)


def _spline(pts, n=40):
    """Catmull-Rom through 3 points (shoulder, elbow, hand): one continuous curve, no joint."""
    p0, p1, p2 = pts
    a, b = (2 * p0[0] - p1[0], 2 * p0[1] - p1[1]), (2 * p2[0] - p1[0], 2 * p2[1] - p1[1])
    out = []
    for seg, (q0, q1, q2, q3) in enumerate(((a, p0, p1, p2), (p0, p1, p2, b))):
        for i in range(n // 2 + (1 if seg else 0)):
            t = i / (n // 2)
            out.append(tuple(0.5 * ((2 * q1[k]) + (-q0[k] + q2[k]) * t + (2 * q0[k] - 5 * q1[k] + 4 * q2[k] - q3[k]) * t * t
                                    + (-q0[k] + 3 * q1[k] - 3 * q2[k] + q3[k]) * t ** 3) for k in (0, 1)))
    return out


def _arm(pen, pts, skin, sleeve, w0=44, w1=30, sleeve_frac=0.5, w=3.6):
    """A tapered arm along one smooth curve: skin forearm, sleeve over the upper arm, blended into the shoulder."""
    path = _spline(pts)
    n = len(path) - 1
    width = lambda i: (w0 + (w1 - w0) * i / n) / 2
    for i, (x, y) in enumerate(path):
        pen.circle(x, y, width(i) + w, INK)
    for i, (x, y) in enumerate(path):
        pen.circle(x, y, width(i), skin)
    cut = int(n * sleeve_frac)
    for i in range(cut + 1):
        x, y = path[i]
        pen.circle(x, y, width(i) + (w if i == cut else 0), INK if i == cut else sleeve)
    for i in range(cut):
        x, y = path[i]
        pen.circle(x, y, width(i) + 1, sleeve)
    x, y = path[0]
    pen.circle(x, y, width(0) + 2, sleeve)                  # hides the outline ring at the shoulder: arm and shirt merge


# --- bodies -------------------------------------------------------------------------------

def _head_and_face_base(pen, skin, cheek):
    mix = _mix
    pen.rect(222, 350, 298, 440, shade(skin, 0.94), radius=18)          # neck
    for x in (138, 382):
        _outlined_ellipse(pen, x, 268, 24, 30, skin)                    # ears
    _outlined_ellipse(pen, HEAD[0], HEAD[1], 120, 118, skin)            # head
    for x in (203, 317):
        pen.ellipse(x, 308, 24, 13, mix(skin, cheek, 0.5))               # cheeks (opaque: layers are pasted over the scene)
    pen.arc(260, 290, 9, 6, 20, 160, INK, 4)                            # nose


def _brows(pen, hair_col=INK):
    for x in (212, 308):
        pen.arc(x, 232, 30, 13, 205, 335, hair_col, 7)


def draw_monk(pen: Pen, d: dict, o: dict):
    skin, cheek = rgb(d["skin"]), rgb(d["cheek"])
    robe, dark, inner = rgb(o["robe"]), rgb(o["robe_dark"]), rgb(o["inner"])
    for x in (205, 315):                                                # feet + sandals
        _outlined_ellipse(pen, x, 866, 42, 13, skin)
        pen.ellipse(x, 874, 42, 7, (120, 84, 60))
    _outlined_poly(pen, [(168, 700), (352, 700), (360, 856), (160, 856)], inner)      # under-robe
    _outlined_poly(pen, [(150, 418), (372, 418), (410, 850), (112, 850)], robe)       # robe
    _outlined_poly(pen, [(150, 418), (212, 418), (380, 700), (330, 770), (150, 560)], dark)  # sash fold
    pen.line([(160, 760), (362, 760)], dark, 5)
    _head_and_face_base(pen, skin, cheek)
    pen.ellipse(222, 168, 46, 16, shade(skin, 1.1))                     # shaved-head shine
    _brows(pen)
    for a, b in (((165, 440), (180, 610)), ((355, 440), (340, 610))):  # arms
        _limb(pen, a, b, 52, robe)
    bowl = rgb(o["bowl"])
    _outlined_ellipse(pen, 260, 640, 92, 22, shade(bowl, 1.3))                        # bowl rim
    pen.chord(260, 640, 92, 70, 0, 180, INK)
    pen.chord(260, 640, 86, 64, 0, 180, bowl)
    for x in (172, 348):
        _outlined_ellipse(pen, x, 628, 22, 20, skin)                    # hands on the bowl


def draw_vendor(pen: Pen, d: dict, o: dict):
    skin, cheek, hair = rgb(d["skin"]), rgb(d["cheek"]), rgb(d["hair"])
    blouse, apron, pants = rgb(o["blouse"]), rgb(o["apron"]), rgb(o["pants"])
    for x in (205, 315):                                                # flip-flops
        _outlined_ellipse(pen, x, 866, 40, 13, skin)
        pen.ellipse(x, 874, 40, 7, (200, 80, 80))
    _outlined_poly(pen, [(176, 690), (344, 690), (352, 860), (268, 860), (260, 740), (252, 860), (168, 860)], pants)
    _outlined_poly(pen, [(156, 418), (364, 418), (380, 730), (140, 730)], blouse)     # blouse
    _outlined_poly(pen, [(196, 468), (324, 468), (346, 745), (174, 745)], apron)      # apron
    pen.line([(196, 468), (176, 428)], INK, 6)
    pen.line([(324, 468), (344, 428)], INK, 6)
    _outlined_poly(pen, [(214, 640), (306, 640), (306, 705), (214, 705)], shade(apron, 0.85), 4)  # pocket
    # hair behind the head
    _outlined_ellipse(pen, HEAD[0], HEAD[1] - 18, 132, 118, hair)
    _head_and_face_base(pen, skin, cheek)
    if o["hat"]:
        straw, band = rgb(o["straw"]), rgb(o["band"])
        _outlined_ellipse(pen, 260, 148, 118, 80, straw)                                # crown
        pen.rect(142, 140, 378, 168, band)
        _outlined_ellipse(pen, 260, 166, 210, 34, shade(straw, 0.96))                   # brim
        for x in range(90, 440, 34):
            pen.line([(x, 158), (x + 10, 174)], shade(straw, 0.8), 3)
    else:
        for x, y in ((150, 230), (370, 230)):
            _outlined_ellipse(pen, x, y, 30, 52, hair)
        _outlined_ellipse(pen, 260, 150, 122, 56, hair)                                 # fringe
        _outlined_ellipse(pen, 260, 108, 40, 34, hair)                                  # bun
    _brows(pen, shade(hair, 0.9))
    _limb(pen, (162, 440), (112, 560), 46, blouse)                       # left arm on hip
    _limb(pen, (112, 560), (156, 650), 42, blouse)
    _outlined_ellipse(pen, 158, 660, 22, 20, skin)
    _limb(pen, (358, 440), (412, 520), 46, blouse)                       # right arm holding a mango
    _limb(pen, (412, 520), (398, 450), 42, blouse)
    _outlined_ellipse(pen, 398, 430, 26, 36, rgb(o["mango"]))
    pen.ellipse(404, 410, 8, 6, (255, 238, 170))
    _outlined_poly(pen, [(398, 398), (420, 380), (428, 396)], (84, 160, 80), 3)
    _outlined_ellipse(pen, 388, 476, 20, 18, skin)


def _rot_ellipse(cx, cy, rx, ry, deg, n=40):
    r = math.radians(deg)
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        x, y = rx * math.cos(a), ry * math.sin(a)
        pts.append((cx + x * math.cos(r) - y * math.sin(r), cy + x * math.sin(r) + y * math.cos(r)))
    return pts


def _star4(pen, cx, cy, r, fill):
    k = r * 0.28
    pen.poly([(cx, cy - r), (cx + k, cy - k), (cx + r, cy), (cx + k, cy + k),
              (cx, cy + r), (cx - k, cy + k), (cx - r, cy), (cx - k, cy - k)], fill)


def _hair_cap(pen, hair, hairline, r=127, w=5):
    """Hair that follows the head's curve; `hairline` runs right-to-left across the forehead."""
    arc = [(260 + r * math.cos(math.radians(a)), 255 + r * math.sin(math.radians(a))) for a in range(188, 353, 6)]
    _outlined_poly(pen, arc + hairline, hair, w)


def draw_star(pen: Pen, d: dict, o: dict):
    skin, cheek, hair = rgb(d["skin"]), rgb(d["cheek"]), rgb(o["hair"])
    gown, light, gold = rgb(o["gown"]), rgb(o["gown_light"]), rgb(o["gold"])
    _outlined_poly(pen, [(128, 240), (392, 240), (418, 590), (372, 650), (148, 650), (102, 590)], hair)   # long hair behind
    for x in (205, 315):                                                                                  # heels
        _outlined_poly(pen, [(x - 34, 846), (x + 30, 846), (x + 38, 872), (x - 36, 872)], rgb(o["shoe"]), 4)
    _outlined_poly(pen, [(172, 418), (348, 418), (340, 480), (180, 480)], skin)                           # shoulders / chest
    pts = [(176, 478), (222, 502), (260, 474), (298, 502), (344, 478), (334, 530), (322, 590), (392, 700),
           (424, 862), (96, 862), (128, 700), (198, 590), (186, 530)]
    _outlined_poly(pen, pts, gown)                                                                        # mermaid gown
    _outlined_poly(pen, [(186, 556), (334, 556), (326, 596), (194, 596)], light, 4)                       # waist sash
    _outlined_poly(pen, [(100, 832), (420, 832), (424, 862), (96, 862)], light, 4)                         # hem band
    for x, y, r in ((215, 600, 9), (180, 700, 11), (250, 760, 10), (160, 820, 8), (340, 760, 9), (385, 820, 11),
                    (225, 540, 7), (300, 650, 8), (270, 830, 8), (205, 760, 6)):
        _star4(pen, x, y, r * 1.5, gold if (x + y) % 2 else (255, 250, 235))
    _limb(pen, (176, 440), (118, 545), 40, skin)                                                          # hand on hip
    _limb(pen, (118, 545), (168, 650), 38, skin)
    _outlined_ellipse(pen, 172, 660, 21, 19, skin)
    _limb(pen, (346, 440), (428, 392), 40, skin)                                                          # star wave
    _limb(pen, (428, 392), (446, 296), 38, skin)
    _outlined_ellipse(pen, 448, 270, 25, 29, skin)
    pen.ellipse(440, 330, 20, 7, gold)
    _head_and_face_base(pen, skin, cheek)
    for x in (140, 380):                                                                                  # earrings
        pen.line([(x, 290), (x, 322)], gold, 5)
        _outlined_ellipse(pen, x, 332, 11, 12, gold, 3)
    _hair_cap(pen, hair, [(386, 236), (352, 226), (316, 206), (282, 188), (246, 202), (206, 214), (160, 226), (134, 238)])
    _outlined_poly(pen, [(120, 250), (176, 290), (172, 540), (112, 560), (104, 400)], hair)               # front locks
    _outlined_poly(pen, [(400, 250), (344, 290), (348, 540), (408, 560), (416, 400)], hair)
    _outlined_poly(pen, [(204, 150), (212, 108), (236, 134), (260, 98), (284, 134), (308, 108), (316, 150)], gold, 4)  # tiara
    _star4(pen, 336, 196, 20, gold)
    _brows(pen, shade(hair, 0.9))


def draw_politician(pen: Pen, d: dict, o: dict):
    skin, cheek, hair = rgb(d["skin"]), rgb(d["cheek"]), rgb(d["hair"])
    jacket, dark, button = rgb(o["jacket"]), rgb(o["jacket_dark"]), rgb(o["button"])
    for x in (200, 320):                                                                                  # shoes
        _outlined_ellipse(pen, x, 866, 44, 13, rgb(o["shoe"]))
    _outlined_poly(pen, [(166, 700), (352, 700), (362, 862), (268, 862), (260, 760), (252, 862), (160, 862)], rgb(o["pants"]))
    _outlined_poly(pen, [(146, 418), (376, 418), (394, 742), (126, 742)], jacket)                          # jacket
    if o["tie"]:
        _outlined_poly(pen, [(228, 418), (292, 418), (260, 470)], (246, 246, 250), 4)                      # shirt
        _outlined_poly(pen, [(250, 440), (270, 440), (278, 600), (260, 622), (242, 600)], rgb(o["tie"]), 4)
        pen.line([(260, 470), (260, 742)], dark, 4)
        for y in (560, 640):
            _outlined_ellipse(pen, 260, y, 6, 6, button, 2)
    else:                                                                                                  # ratchapaen: stand collar + 5 gold buttons
        _outlined_poly(pen, [(222, 400), (298, 400), (304, 446), (216, 446)], jacket, 4)
        pen.line([(260, 446), (260, 742)], dark, 4)
        for y in (480, 540, 600, 660, 715):
            _outlined_ellipse(pen, 260, y, 7, 7, button, 3)
        _outlined_poly(pen, [(170, 520), (232, 520), (232, 580), (170, 580)], dark, 4)                     # chest pocket
        _outlined_poly(pen, [(160, 660), (232, 660), (232, 732), (160, 732)], dark, 4)
        _outlined_poly(pen, [(288, 660), (360, 660), (360, 732), (288, 732)], dark, 4)
    _outlined_poly(pen, [(284, 510), (362, 510), (362, 552), (284, 552)], (252, 252, 246), 3)             # name tag (fictional)
    pen.d.text((323 * pen.ss, 531 * pen.ss), d["tag"], font=thai_font(int(17 * pen.ss)), fill=INK, anchor="mm")
    _limb(pen, (158, 440), (122, 560), 52, jacket)                                                         # left arm holds the speech paper
    _limb(pen, (122, 560), (190, 596), 48, jacket)
    _outlined_poly(pen, [(150, 540), (226, 530), (232, 612), (156, 622)], (250, 248, 236), 3)
    for yy in (558, 574, 590):
        pen.line([(166, yy + 4), (214, yy)], (160, 156, 150), 3)
    _outlined_ellipse(pen, 200, 600, 21, 19, skin)
    _limb(pen, (364, 440), (420, 520), 52, jacket)                                                         # right arm raised, greeting
    _limb(pen, (420, 520), (404, 440), 48, jacket)
    _outlined_ellipse(pen, 402, 418, 25, 28, skin)
    _head_and_face_base(pen, skin, cheek)
    _hair_cap(pen, hair, [(386, 236), (350, 218), (312, 206), (290, 200), (262, 214), (226, 212), (186, 214), (150, 222), (134, 238)])
    pen.line([(290, 200), (284, 140)], shade(hair, 0.6), 4)                                                # side part
    _brows(pen, shade(hair, 0.62))


def draw_mosquito(pen: Pen, d: dict, o: dict):
    skin, cheek = rgb(d["skin"]), rgb(d["cheek"])
    body, stripe, wing = rgb(o["body"]), rgb(o["stripe"]), rgb(o["wing"])
    for deg, x in ((-38, 150), (38, 370)):                                                                 # wings
        pts = _rot_ellipse(x, 392, 118, 40, deg)
        _outlined_poly(pen, pts, wing, 4)
    leg = (74, 66, 80)
    for a, k, b in (((226, 520), (120, 620), (108, 860)), ((294, 520), (400, 620), (412, 860)),
                    ((236, 540), (176, 660), (176, 866)), ((284, 540), (344, 660), (344, 866))):           # long legs
        pen.line([a, k, b], INK, 17)
        pen.line([a, k, b], leg, 9)
        pen.line([(b[0] - 24 * (1 if b[0] > 260 else -1), 868), (b[0] + 8, 868)], INK, 11)
    for a, b in (((232, 430), (150, 470)), ((288, 430), (370, 470))):                                      # little front arms
        mid = (a[0] + (b[0] - a[0]) * 0.5, a[1] + 50)
        pen.line([a, mid, b], INK, 16)
        pen.line([a, mid, b], leg, 8)
    _outlined_ellipse(pen, 260, 462, 76, 66, body)                                                         # thorax
    cy, rx, ry = 628, 66, 118                                                                              # striped abdomen
    belly = rgb(o["belly"]) if o["belly"] else None
    pen.ellipse(260, cy, rx + 5, ry + 5, INK)
    for y in range(cy - ry, cy + ry):
        w = rx * math.sqrt(max(0.0, 1 - ((y - cy) / ry) ** 2))
        col = stripe if ((y - (cy - ry)) // 30) % 2 else body
        if belly and y > cy:
            col = belly if ((y - (cy - ry)) // 30) % 2 == 0 else shade(belly, 1.25)
        pen.rect(260 - w, y, 260 + w, y + 1.5, col)
    for sx, ex, ey in ((-1, 170, 40), (1, 350, 40)):                                                       # antennae
        pen.line([(260 + sx * 60, 150), (260 + sx * 100, 96), (ex, ey)], INK, 8)
        pen.ellipse(ex, ey, 11, 14, (92, 84, 96), outline=INK, width=3)
    _head_and_face_base(pen, skin, cheek)
    pen.line([(294, 298), (398, 402)], INK, 14)                                                            # needle-like proboscis (in front)
    pen.line([(294, 298), (398, 402)], (92, 84, 96), 7)
    _brows(pen)


# --- generic people (hair / clothes / props / brows are data in characters/<id>.json) --------

def _brows_styled(pen, style, col, dy=0):
    if style == "angry":
        for x, s in ((212, 1), (308, -1)):
            pen.line([(x - 30 * s, 220 + dy), (x + 26 * s, 238 + dy)], col, 9)
    elif style == "sad":
        for x, s in ((212, 1), (308, -1)):
            pen.line([(x - 30 * s, 238 + dy), (x + 26 * s, 222 + dy)], col, 8)
    else:
        _brows(pen, col)


def _hair_back(pen, style, hair):
    if style in ("long", "bun_long"):
        _outlined_poly(pen, [(128, 240), (392, 240), (412, 540), (108, 540)], hair)
    elif style == "perm":
        for x, y in ((150, 300), (370, 300), (160, 360), (360, 360)):
            _outlined_ellipse(pen, x, y, 44, 44, hair)


def _hair_front(pen, style, hair):
    if style in ("short", "long", "bun", "bun_long"):
        _hair_cap(pen, hair, [(386, 236), (350, 222), (310, 204), (270, 196), (236, 210), (196, 214), (156, 226), (134, 238)])
    if style in ("bun", "bun_long"):
        _outlined_ellipse(pen, 260, 112, 48, 40, hair)
    if style == "perm":
        for i in range(9):
            a = math.radians(190 + i * 20)
            _outlined_ellipse(pen, 260 + 120 * math.cos(a), 246 + 112 * math.sin(a), 42, 40, hair)
        _outlined_ellipse(pen, 260, 176, 110, 46, hair)
    if style == "balding":
        for x in (142, 378):
            _outlined_ellipse(pen, x, 220, 22, 40, hair, 4)


def _hat(pen, kind, col):
    if kind == "bucket":
        _outlined_poly(pen, [(160, 190), (360, 190), (340, 104), (180, 104)], col)
        _outlined_ellipse(pen, 260, 196, 168, 30, shade(col, 0.9))
    elif kind == "cap":
        _hair_cap(pen, col, [(386, 236), (380, 200), (140, 200), (134, 238)])
        _outlined_ellipse(pen, 330, 206, 90, 18, shade(col, 0.85))


def _prop(pen, kind, at, o):
    x, y = at
    if kind == "phone":
        _outlined_poly(pen, [(x - 30, y - 56), (x + 30, y - 56), (x + 30, y + 50), (x - 30, y + 50)], (52, 48, 60), 4)
        pen.rect(x - 22, y - 46, x + 22, y + 38, (150, 220, 190))
    elif kind == "book":
        _outlined_poly(pen, [(x - 46, y - 50), (x, y - 40), (x, y + 30), (x - 46, y + 20)], (196, 92, 80), 4)
        _outlined_poly(pen, [(x, y - 40), (x + 46, y - 50), (x + 46, y + 20), (x, y + 30)], (214, 108, 92), 4)
        for k in range(3):
            pen.line([(x + 8, y - 24 + k * 14), (x + 36, y - 30 + k * 14)], (250, 230, 210), 3)
    elif kind == "cup":
        _outlined_poly(pen, [(x - 28, y - 60), (x + 28, y - 60), (x + 22, y + 20), (x - 22, y + 20)], (200, 226, 240), 4)
        pen.rect(x - 22, y - 30, x + 20, y + 16, (190, 214, 230))
    elif kind == "net":
        pen.line([(x, y), (x + 70, y - 190)], (150, 110, 70), 10)
        _outlined_ellipse(pen, x + 86, y - 230, 52, 44, (230, 230, 220), 4)
        for k in range(-2, 3):
            pen.line([(x + 86 + 18 * k, y - 270), (x + 86 + 18 * k, y - 190)], (170, 170, 160), 2)
    elif kind == "bags":
        for dx, col in ((-30, (236, 236, 236)), (30, (250, 214, 120))):
            _outlined_poly(pen, [(x + dx - 34, y), (x + dx + 34, y), (x + dx + 40, y + 96), (x + dx - 40, y + 96)], col, 4)
            pen.arc(x + dx, y, 20, 18, 180, 360, INK, 5)
    elif kind == "leash":
        _outlined_ellipse(pen, x, y, 14, 14, (220, 80, 80), 3)
    elif kind == "fish":
        fx, fy, k = x, y - 70, 0.65
        _outlined_poly(pen, [(fx + 70 * k, fy), (fx + 128 * k, fy - 40 * k), (fx + 118 * k, fy), (fx + 128 * k, fy + 40 * k)],
                       (96, 140, 176), 3)
        _outlined_ellipse(pen, fx, fy, 78 * k, 40 * k, (120, 170, 206), 3)
        pen.ellipse(fx + 6 * k, fy + 16 * k, 62 * k, 16 * k, (232, 240, 246))
        pen.circle(fx - 44 * k, fy - 8 * k, 9 * k, (255, 255, 255))
        pen.circle(fx - 44 * k, fy - 8 * k, 4.5 * k, INK)
    elif kind == "sandal":
        _outlined_ellipse(pen, x, y - 30, 30, 54, (80, 140, 210), 4)
        pen.line([(x - 20, y - 50), (x, y - 30), (x + 20, y - 50)], INK, 5)


ARM_POSES = {  # (shoulder, elbow, hand) for left and right arm
    "down": (((160, 440), (140, 560), (150, 660)), ((360, 440), (380, 560), (370, 660))),
    "phone": (((160, 440), (150, 560), (226, 560)), ((360, 440), (370, 560), (294, 560))),
    "raise": (((160, 440), (140, 560), (150, 660)), ((360, 440), (440, 380), (452, 270))),
    "both_up": (((160, 440), (80, 380), (70, 260)), ((360, 440), (440, 380), (452, 260))),
    "hold": (((160, 440), (150, 560), (220, 600)), ((360, 440), (370, 560), (300, 600))),
    "hips": (((160, 440), (110, 540), (160, 640)), ((360, 440), (410, 540), (360, 640))),
    "fish_up": (((160, 440), (140, 560), (150, 660)), ((360, 440), (420, 380), (432, 300))),
    "eat": (((160, 440), (140, 560), (150, 660)), ((360, 440), (410, 540), (306, 338))),
    "stir_a": (((160, 440), (150, 565), (214, 600)), ((360, 440), (392, 565), (290, 612))),
    "stir_b": (((160, 440), (150, 565), (214, 600)), ((360, 440), (380, 560), (338, 586))),
    "wave_a": (((160, 440), (140, 560), (150, 660)), ((360, 440), (440, 380), (440, 270))),
    "wave_b": (((160, 440), (140, 560), (150, 660)), ((360, 440), (440, 390), (478, 300))),
    "push": (((160, 440), (170, 560), (214, 610)), ((360, 440), (350, 560), (306, 610))),
    "sip": (((160, 440), (140, 560), (150, 660)), ((360, 440), (400, 535), (300, 344))),
    "hold_low": (((160, 440), (150, 570), (206, 640)), ((360, 440), (370, 570), (314, 640))),
}


def arms_pose(spec: str):
    """'name' or 'a>b@k' (k in 0..8): the pose k/8 of the way from a to b, for smooth arm animation."""
    if ">" not in spec:
        return ARM_POSES[spec]
    ab, k = spec.split("@")
    a, b = ab.split(">")
    t = int(k) / 8
    return tuple(tuple(tuple(pa[i] + (pb[i] - pa[i]) * t for i in (0, 1)) for pa, pb in zip(la, lb))
                 for la, lb in zip(ARM_POSES[a], ARM_POSES[b]))


def draw_person(pen: Pen, d: dict, o: dict):
    if d.get("style") == "cute":                       # soft organic people (curves, folds, mitten hands)
        import character_soft
        return character_soft.draw(pen, d, o)
    skin, cheek, hair = rgb(d["skin"]), rgb(d["cheek"]), rgb(d.get("hair", "#3B2A26"))
    top, bottom = rgb(o["top"]), rgb(o.get("bottom", "#4A5A80"))
    style = d.get("hair_style", "short")
    cute = d.get("style") == "cute"
    _hair_back(pen, style, hair)
    if not o.get("boat"):
        if o.get("skirt"):                                  # bare legs, no round shoe discs under the feet
            for x in (212, 308):
                _limb(pen, (x, 820), (x, 872), 26, skin)
            _outlined_poly(pen, [(168, 690), (352, 690), (380, 850), (140, 850)], bottom)
        else:
            for x in (205, 315):
                _outlined_ellipse(pen, x, 866, 42, 13, rgb(o.get("shoe", "#5A4038")))
            _outlined_poly(pen, [(172, 690), (348, 690), (356, 860), (268, 860), (260, 750), (252, 860), (164, 860)], bottom)
    if o.get("backpack"):                                                                               # delivery box (generic colours)
        bp = rgb(o["backpack"])
        _outlined_poly(pen, [(112, 420), (408, 420), (420, 690), (100, 690)], bp, 5)
        pen.line([(112, 520), (408, 520)], shade(bp, 0.8), 6)
    if cute:
        pen.poly(_smooth([(150, 420), (370, 420), (392, 735), (128, 735)], 3, 0.22), top, outline=INK, width=3.6)  # round torso
    else:
        _outlined_poly(pen, [(152, 418), (368, 418), (384, 730), (136, 730)], top)                        # torso
    ts = o.get("top_style", "shirt")
    acc = rgb(o.get("accent", "#FFFFFF"))
    if ts == "hoodie":
        _outlined_poly(pen, [(190, 418), (330, 418), (300, 470), (220, 470)], shade(top, 0.85), 4)
        _outlined_poly(pen, [(200, 600), (320, 600), (330, 690), (190, 690)], shade(top, 0.9), 4)
        pen.line([(236, 470), (232, 540)], acc, 5)
        pen.line([(284, 470), (288, 540)], acc, 5)
    elif ts == "apron":
        _outlined_poly(pen, [(196, 468), (324, 468), (346, 745), (174, 745)], acc)
    elif ts == "vest":
        _outlined_poly(pen, [(152, 418), (230, 418), (230, 730), (136, 730)], acc, 4)
        _outlined_poly(pen, [(290, 418), (368, 418), (384, 730), (290, 730)], acc, 4)
    elif ts == "floral":
        for x, y in ((190, 500), (300, 520), (230, 620), (330, 640), (180, 690)):
            pen.circle(x, y, 13, acc)
            pen.circle(x, y, 5, (250, 230, 120))
    elif ts == "polo":
        _outlined_poly(pen, [(222, 418), (298, 418), (260, 480)], shade(top, 0.8), 4)
    def draw_arms():
        arms = arms_pose(o.get("arms", "down"))
        for a, e, h in arms:
            if cute:
                _arm(pen, [a, e, h], skin, top, sleeve_frac=o.get("sleeve", 0.5))
            else:
                _limb(pen, a, e, 46, top)
                _limb(pen, e, h, 42, top)
        if o.get("prop"):
            hand = arms[1][2] if o.get("prop_hand", "right") == "right" else arms[0][2]
            if o.get("arms") in ("phone", "hold"):
                hand = ((arms[0][2][0] + arms[1][2][0]) / 2, arms[0][2][1])
            _prop(pen, o["prop"], hand, o)
        for _, _, h in arms:
            _outlined_ellipse(pen, h[0], h[1], 26 if cute else 22, 24 if cute else 20, skin)
    front = any(k in o.get("arms", "") for k in ("eat", "sip"))               # hand at the mouth: drawn over the face
    if not front:
        draw_arms()
    if o.get("boat"):                                                                                   # sitting in a boat
        oar = (150, 110, 70)
        pen.line([(120, 520), (430, 860)], INK, 18)
        pen.line([(120, 520), (430, 860)], oar, 10)
        _outlined_poly(pen, [(20, 690), (500, 690), (450, 820), (70, 820)], rgb(o.get("boat_color", "#9C6A44")))
        pen.rect(20, 690, 500, 712, shade(rgb(o.get("boat_color", "#9C6A44")), 0.8))
    _head_and_face_base(pen, skin, cheek)
    _hair_front(pen, style, hair)
    if front:
        draw_arms()
    if d.get("glasses"):
        for x in (210, 310):
            pen.ellipse(x, 268, 34, 28, None, outline=INK, width=5)
        pen.line([(244, 266), (276, 266)], INK, 5)
    if d.get("mustache"):
        _outlined_poly(pen, [(222, 318), (260, 308), (298, 318), (286, 328), (260, 322), (234, 328)], hair, 3)
    if o.get("hat"):
        _hat(pen, o["hat"], rgb(o.get("hat_color", "#C9B37E")))
    _brows_styled(pen, o.get("brows", d.get("brows", "normal")), shade(hair, 0.85))


# --- dogs: head stays where the shared face layers are, the body is a small sitting dog ------

def _fluff_ellipse(pen, cx, cy, rx, ry, n, rr, col):
    """Fluffy outline: tufts along the edge, then a solid fill so the inside is never hollow."""
    pts = [(cx + rx * math.cos(2 * math.pi * i / n), cy + ry * math.sin(2 * math.pi * i / n)) for i in range(n)]
    for x, y in pts:
        pen.circle(x, y, rr + 5, INK)
    pen.ellipse(cx, cy, rx + 5, ry + 5, INK)
    for x, y in pts:
        pen.circle(x, y, rr, col)
    pen.ellipse(cx, cy, rx, ry, col)


def _heart(pen, cx, cy, s, col):
    pen.circle(cx - 0.5 * s, cy - 0.3 * s, 0.55 * s, col)
    pen.circle(cx + 0.5 * s, cy - 0.3 * s, 0.55 * s, col)
    pen.poly([(cx - 1.02 * s, cy - 0.1 * s), (cx + 1.02 * s, cy - 0.1 * s), (cx, cy + 1.1 * s)], col)


def face_dy(ch: dict, outfit: str) -> int:
    """How far below the standard head position this character's face is drawn."""
    return ch["outfits"][outfit].get("face_dy", ch["draw"].get("face_dy", 0))


def draw_dog(pen: Pen, d: dict, o: dict):
    coat, light = rgb(d["coat"]), rgb(d.get("light", "#F6EFE6"))
    hc = rgb(d.get("head", d["coat"]))
    ears = rgb(d.get("ears", d.get("head", d["coat"])))
    breed, back, lying = d["breed"], o.get("back", False), o.get("lying", False)
    hy = 255 + o.get("face_dy", d.get("face_dy", 0))
    pom = breed == "pom"
    # body
    if lying:
        if pom:
            _fluff_ellipse(pen, 300, 806, 170, 66, 22, 26, coat)
            _fluff_ellipse(pen, 450, 760, 40, 34, 8, 20, shade(coat, 1.04))          # plume tail
        else:
            _outlined_ellipse(pen, 300, 812, 160, 60, coat)
        for x in (128, 186):
            _outlined_ellipse(pen, x, 862, 34, 16, light)
    else:
        if pom:
            _fluff_ellipse(pen, 380 if not back else 260, 700 if not back else 640, 46, 40, 9, 22, shade(coat, 1.04))
            _fluff_ellipse(pen, 260, 742, 118, 120, 18, 26, coat)
            if not back:
                _fluff_ellipse(pen, 260, 660, 92, 62, 14, 22, light if d.get("light_ruff") else coat)
        else:
            pen.line([(318, 830), (392, 780), (404, 720)], INK, 15)
            pen.line([(318, 830), (392, 780), (404, 720)], coat, 7)
            _outlined_ellipse(pen, 260, 742, 84, 122, coat)
            if back and d.get("back_pattern"):
                pat = rgb(d["back_pattern"])
                for x, y, rx, ry in ((260, 700, 30, 46), (226, 780, 18, 26), (294, 786, 20, 28), (260, 836, 14, 16)):
                    pen.ellipse(x, y, rx, ry, pat)
            elif d.get("chest") and not back:
                _outlined_ellipse(pen, 260, 742, 50, 96, light, 4)
        for x in (220, 300):                                                                     # front paws
            if not pom and not back:
                _limb(pen, (x, 790), (x, 856), 24, light if d.get("chest") else coat, 4)
            _outlined_ellipse(pen, x, 864, 32, 16, light if (pom or d.get("chest")) and not back else coat)
    # head
    if not pom:
        for s in (-1, 1):
            _outlined_poly(pen, [(260 + s * 70, hy - 65), (260 + s * 186, hy - 192), (260 + s * 120, hy - 5)], ears)
            if not back:
                pen.poly([(260 + s * 92, hy - 58), (260 + s * 166, hy - 158), (260 + s * 122, hy - 22)], (240, 180, 180))
    else:
        for s in (-1, 1):
            _outlined_poly(pen, [(260 + s * 58, hy - 96), (260 + s * 104, hy - 156), (260 + s * 116, hy - 72)], ears)
        _fluff_ellipse(pen, 260, hy, 116, 108, 20, 24, hc)
    _outlined_ellipse(pen, 260, hy, 120, 112, hc)
    if d.get("heart"):                                                                           # Latte: white heart, centre of the crown
        _heart(pen, 260, hy - 78, 24, (255, 255, 255))
    if back:
        return
    if d.get("blaze"):                                                                           # white stripe up the face
        pen.poly([(242, hy + 70), (278, hy + 70), (268, hy - 90), (252, hy - 90)], light)
    if d.get("eye_patches"):
        for x in (210, 310):
            pen.ellipse(x, hy + 12, 40, 34, rgb(d["eye_patches"]))
    _outlined_ellipse(pen, 260, hy + 70, 74, 50, light, 4)                                       # muzzle
    pen.ellipse(260, hy + 42, 20, 14, INK)                                                       # nose
    pen.ellipse(255, hy + 37, 6, 4, (130, 120, 120))
    if o.get("brows"):
        _brows_styled(pen, o["brows"], shade(hc, 0.5), hy - 255)


def draw_none(pen: Pen, d: dict, o: dict):
    """Voice-only speaker (narrator, phone app): nothing is drawn."""


DRAWERS = {"monk": draw_monk, "vendor": draw_vendor, "star": draw_star,
           "politician": draw_politician, "mosquito": draw_mosquito,
           "person": draw_person, "dog": draw_dog, "none": draw_none}


# --- face layers --------------------------------------------------------------------------

def _soft_shade(img: Image.Image) -> Image.Image:
    w, h = img.size
    alpha = img.getchannel("A")
    horiz = Image.linear_gradient("L").transpose(Image.ROTATE_90).resize((w, h))   # black left -> white right
    vert = Image.linear_gradient("L").resize((w, h))                                # black top -> white bottom
    shadow_a = ImageChops.add(horiz.point(lambda v: max(0, v - 120) // 3), vert.point(lambda v: max(0, v - 190) // 5))
    light_a = ImageChops.multiply(horiz.point(lambda v: max(0, 110 - v) // 5), vert.point(lambda v: max(0, 200 - v) // 2 + 40))
    out = img.copy()
    for color, a in (((70, 44, 70), shadow_a), ((255, 250, 235), light_a)):
        layer = Image.new("RGBA", (w, h), color + (0,))
        layer.putalpha(ImageChops.multiply(a, alpha))
        out = Image.alpha_composite(out, layer)
    return out


def _eyes(pen, closed: bool, look: int, cute: bool = False, lashes: bool = True):
    k = 1.22 if cute else 1.0                        # cute style: larger, glossy eyes with a lid line and lash flicks
    for i, x in enumerate((210, 310)):
        out = -1 if i == 0 else 1
        if closed:
            pen.arc(x, 268, 15 * k, 8 * k, 20, 160, INK, 6)
        else:
            pen.ellipse(x + 4 * look, 270, 13 * k, 17.5 * k, (58, 40, 40))
            pen.ellipse(x + 4 * look, 276, 9 * k, 9 * k, (110, 76, 66))             # lighter lower iris
            pen.circle(x + 4 * look + 4 * k, 262 - (3 if cute else 0), 5 * k, (255, 255, 255))
            if cute:
                pen.circle(x + 4 * look - 5, 278, 2.8, (255, 255, 255))
                pen.arc(x + 4 * look, 270, 15 * k, 19 * k, 200, 340, INK, 5)           # upper lid line
                if lashes:
                    pen.line([(x + out * 14 * k, 258), (x + out * 22 * k, 252)], INK, 3.4)   # lash flick


def _mouth(pen, shape: int):
    cx, cy = 260, 342
    dark, tongue = (112, 46, 52), (232, 120, 128)
    if shape == 0:
        pen.arc(cx, cy - 8, 24, 14, 20, 160, INK, 5)
    elif shape == 1:
        pen.ellipse(cx, cy, 17, 9, INK)
        pen.ellipse(cx, cy + 1, 13, 6, dark)
    elif shape == 2:
        pen.ellipse(cx, cy + 2, 25, 19, INK)
        pen.ellipse(cx, cy + 2, 20, 14, dark)
        pen.ellipse(cx, cy + 9, 12, 6, tongue)
    else:
        pen.ellipse(cx, cy + 4, 33, 29, INK)
        pen.ellipse(cx, cy + 4, 28, 24, dark)
        pen.rect(cx - 22, cy - 18, cx + 22, cy - 8, (250, 246, 240), radius=4)
        pen.ellipse(cx, cy + 16, 17, 8, tongue)


CHIBI_CUT = 392


def _chibi(img: Image.Image, k: float) -> tuple[Image.Image, int]:
    """Shrink everything below the neck by k (shorter torso and legs, head untouched), feet stay on GROUND.
    Returns the image and how far the head moved down."""
    low = img.crop((0, CHIBI_CUT, CW, CH))
    new_h = int((CH - CHIBI_CUT) * k)
    shift = (CH - CHIBI_CUT) - new_h
    out = Image.new("RGBA", img.size, (0, 0, 0, 0))
    out.paste(img.crop((0, 0, CW, CHIBI_CUT)), (0, shift))
    out.paste(low.resize((CW, new_h), Image.LANCZOS), (0, CHIBI_CUT + shift))
    return out, shift


@lru_cache(maxsize=None)
def _body(char_id: str, outfit: str, arms: str | None) -> tuple[Image.Image, int]:
    ch = load_character(char_id)
    if outfit not in ch["outfits"]:
        raise KeyError(f"character '{char_id}' has no outfit '{outfit}' (has: {', '.join(ch['outfits'])})")
    o = dict(ch["outfits"][outfit])
    if arms:
        o["arms"] = arms
    pen = Pen(CW, CH)
    DRAWERS[ch["draw"]["kind"]](pen, ch["draw"], o)
    body = _soft_shade(pen.result())
    k = ch["draw"].get("chibi")
    return _chibi(body, k) if k else (body, 0)


@lru_cache(maxsize=None)
def _faces(char_id: str, outfit: str, look: int) -> dict:
    ch = load_character(char_id)
    o = ch["outfits"][outfit]
    cute = ch["draw"].get("style") == "cute"
    out = {}
    faceless = o.get("back") or ch["draw"]["kind"] == "none"  # back view / voice-only: no face layers
    for closed in (False, True):
        pen = Pen(CW, CH)
        if not faceless:
            _eyes(pen, closed or o.get("eyes") == "closed", look, cute, ch["draw"].get("lashes", cute))
        out["eyes_closed" if closed else "eyes_open"] = pen.result()
    for i in range(4):
        pen = Pen(CW, CH)
        if not faceless:
            _mouth(pen, i)
        out[f"mouth{i}"] = pen.result()
    dy = face_dy(ch, outfit) + _body(char_id, outfit, None)[1]
    if dy:
        for k in list(out):
            moved = Image.new("RGBA", out[k].size, (0, 0, 0, 0))
            moved.paste(out[k], (0, dy))
            out[k] = moved
    out["tilt"] = o.get("tilt", 0)
    return out


def layers(char_id: str, outfit: str, look: int, arms: str | None = None) -> dict:
    """look: -1 / 0 / +1 shifts the pupils so the pair faces each other. arms: optional pose override ('a>b@k')."""
    return {"body": _body(char_id, outfit, arms)[0], **_faces(char_id, outfit, look)}


@lru_cache(maxsize=None)
def sprite(char_id: str, outfit: str, look: int, mouth: int, eyes_closed: bool, scale: float,
           arms: str | None = None) -> Image.Image:
    L = layers(char_id, outfit, look, arms)
    img = L["body"].copy()
    img.alpha_composite(L["eyes_closed" if eyes_closed else "eyes_open"])
    img.alpha_composite(L[f"mouth{mouth}"])
    if L["tilt"]:
        img = img.rotate(L["tilt"], resample=Image.BICUBIC, center=(CW / 2, 640))
    size = (max(1, round(CW * scale)), max(1, round(CH * scale)))
    return img.resize(size, Image.LANCZOS)


def character_sheet(char_id: str) -> Path:
    """Reference sheet: every outfit x (4 mouth shapes + blink), the fixed traits and the voice."""
    ch = load_character(char_id)
    sc = 0.5
    cw, chh = round(CW * sc), round(CH * sc)
    outfits = list(ch["outfits"])
    head = 150 + 32 * (len(_wrap_whole('ลักษณะบังคับ: ' + '  /  '.join(c.replace(' ', ' ') for c in ch['fixed']), thai_font(24, False), cw * 5 - 48)) - 1)
    sheet = Image.new("RGB", (cw * 5, head + chh * len(outfits)), (238, 228, 210))
    d = ImageDraw.Draw(sheet)
    d.text((24, 14), f"{ch['name']}  ({ch['id']}, {ch['role']})", font=thai_font(44), fill=(60, 44, 40))
    traits = _wrap_whole("ลักษณะบังคับ: " + "  /  ".join(c.replace(" ", " ") for c in ch["fixed"]), thai_font(24, False), cw * 5 - 48)
    for k, ln in enumerate(traits):
        d.text((24, 74 + k * 32), ln.replace(" ", " "), font=thai_font(24, False), fill=(90, 70, 64))
    v = ch["voice"]
    d.text((24, head - 40), f"เสียง Gemini: {v['gemini']}   edge-tts: {v['edge']} {v.get('edge_pitch', '')}   สีซับ: {ch['subtitle_color']}",
           font=thai_font(22, False), fill=(90, 70, 64))
    for r, outfit in enumerate(outfits):
        for c in range(5):
            spr = sprite(char_id, outfit, 1, c if c < 4 else 0, c == 4, sc)
            sheet.paste(spr, (c * cw, head + r * chh), spr)
        d.text((10, head + r * chh + 6), outfit, font=thai_font(26), fill=(60, 44, 40))
    out = HERE / "output" / "sheets"
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"{char_id}_sheet.png"
    sheet.save(path)
    return path


if __name__ == "__main__":  # python character_art.py [id ...] -> output/sheets/<id>_sheet.png
    ids = sys.argv[1:] or [p.stem for p in sorted((HERE / "characters").glob("*.json"))]
    for cid in ids:
        print(character_sheet(cid))
