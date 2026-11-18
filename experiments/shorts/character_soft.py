"""Soft, organic office-worker characters (style "cute" in characters/<id>.json), version 2.

Art direction (from a Gemini brief + chibi/flat-vector references, see docs/PRODUCT.md "แนวการวาดตัวละคร"):
  * about 3 heads tall, SHORT soft neck, narrow shoulders, a slight waist, tapered slender limbs, small tidy hands
  * an egg-shaped face with a small chin, big glossy eyes, tiny nose, blush; fair warm skin
  * every shape is a smoothed curve (no perfect circles, half circles or rectangles); fold lines are free curves
  * dressed for the story: a woman in a blouse, belt, pencil skirt and low pumps; a man in a shirt with rolled
    sleeves, belt, slacks and loafers; both wear an ID lanyard (they are office workers)
Drawn in character_art's canvas (head centre (260, 258), feet ~y880) so the shared eye/mouth layers line up.
"""

from __future__ import annotations

import character_art as CA
from character_art import INK, _smooth, arms_pose, rgb, shade


def _shape(pen, pts, fill, w=3.4, iters=3, ratio=0.2, outline=True):
    pen.poly(_smooth(pts, iters, ratio), fill, outline=INK if outline else None, width=w)


def _line(pen, pts, color, width=3.4):
    pen.line(CA._spline(pts) if len(pts) == 3 else pts, color, width)


def M(p):
    """Map the shared arm-pose coordinates (old, broad torso) onto this slimmer body. Points far from the body's
    centre line (a raised or waving arm) are pushed further out so the hand clears the head and hair."""
    dx = p[0] - 260
    k = 0.74 + 0.21 * min(1.0, max(0.0, (abs(dx) - 100) / 100))
    return (260 + dx * k, 420 + (p[1] - 440) * 0.82)


def _tube(pen, pts, w0, w1, fill, outline_w=3.4):
    path = CA._spline(pts)
    n = len(path) - 1
    width = lambda i: (w0 + (w1 - w0) * i / n) / 2
    for i, (x, y) in enumerate(path):
        pen.circle(x, y, width(i) + outline_w, INK)
    for i, (x, y) in enumerate(path):
        pen.circle(x, y, width(i), fill)
    return path


def _hand(pen, x, y, skin, side):
    """A simple soft hand: one rounded teardrop in line with the arm, no thumb, fingers or nails drawn."""
    _shape(pen, [(x - 12, y - 6), (x + 12, y - 6), (x + 15, y + 12), (x + 6, y + 26), (x - 6, y + 26), (x - 15, y + 12)], skin, 3.2, 3, 0.28)


def _arm(pen, pts, skin, sleeve, sleeve_frac, side, puff=False, cuff_fold=False):
    path = _tube(pen, pts, 31, 21, skin)
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
    cx, cy = path[cut]
    if cuff_fold:                                                   # rolled-up sleeve: a lighter folded band
        pen.line([(cx - 17, cy - 2), (cx + 17, cy + 5)], shade(sleeve, 1.18), 9)
        pen.line([(cx - 17, cy - 2), (cx + 17, cy + 5)], shade(sleeve, 0.78), 2.5)
    sx, sy = path[0]
    pen.circle(sx, sy, width(0) + extra + 1, sleeve)                # shoulder melts into the shirt
    ex, ey = path[n // 2]
    _line(pen, [(ex - 12, ey - 8), (ex - 2, ey), (ex + 8, ey + 3)], shade(skin, 0.82), 2.6)   # elbow crease
    hx, hy = path[-1]
    _hand(pen, hx, hy, skin, side)


def _ear(pen, side, skin):
    x = 260 + side * 124
    pts = [(x - side * 6, 246), (x + side * 16, 238), (x + side * 26, 262), (x + side * 22, 292), (x + side * 4, 304), (x - side * 8, 292)]
    _shape(pen, pts, skin, 3.0, 3, 0.25)
    _line(pen, [(x + side * 2, 258), (x + side * 12, 266), (x + side * 8, 284)], shade(skin, 0.8), 2.4)


def _head(pen, skin, cheek):
    egg = [(260, 138), (318, 146), (364, 184), (384, 244), (380, 306), (352, 352), (308, 384), (260, 392), (212, 384),
           (168, 352), (140, 306), (136, 244), (156, 184), (202, 146)]
    _shape(pen, egg, skin, 3.6, 3, 0.2)
    for x in (206, 314):
        pen.ellipse(x, 312, 22, 12, CA._mix(skin, cheek, 0.55))                      # blush
    _line(pen, [(254, 300), (260, 306), (268, 300)], shade(skin, 0.72), 3)             # tiny nose


def _neck(pen, skin):
    _shape(pen, [(236, 366), (284, 366), (290, 414), (230, 414)], shade(skin, 0.95), 3.2, 3, 0.2)
    pen.ellipse(260, 384, 26, 10, shade(skin, 0.86))                                  # shadow under the chin


def _lanyard(pen, accent, badge):
    pen.line([(240, 416), (258, 520)], accent, 3.4)
    pen.line([(280, 416), (262, 520)], accent, 3.4)
    _shape(pen, [(240, 522), (284, 522), (284, 568), (240, 568)], (252, 250, 246), 3, 2, 0.15)
    pen.rect(246, 528, 278, 540, badge, radius=3)
    pen.line([(248, 550), (276, 550)], (200, 196, 190), 2.4)
    pen.line([(248, 558), (268, 558)], (200, 196, 190), 2.4)


# --- hair ------------------------------------------------------------------------------------------------------------

def _hair_back_woman(pen, hair):
    """A tidy bob that ends at the jaw/shoulder and curls in a little."""
    pts = [(142, 250), (128, 330), (130, 396), (142, 436), (168, 450), (196, 438), (212, 408), (308, 408), (324, 438),
           (352, 450), (378, 436), (390, 396), (392, 330), (378, 250)]
    _shape(pen, pts, hair, 3.6, 3, 0.2)


def _hair_front_woman(pen, hair, clip=True):
    cap = [(134, 256), (144, 196), (184, 152), (240, 132), (304, 136), (354, 162), (384, 214), (388, 262), (372, 240),
           (344, 224), (304, 218), (262, 226), (226, 246), (190, 276), (164, 300), (150, 322), (140, 300)]
    _shape(pen, cap, hair, 3.6, 3, 0.18)
    _line(pen, [(200, 168), (250, 152), (304, 162)], shade(hair, 1.6), 5)                       # one soft highlight
    if clip:
        _shape(pen, [(168, 214), (186, 204), (198, 220), (184, 232)], (250, 214, 110), 2.6, 2, 0.2)   # little hair clip


def _hair_man(pen, hair):
    cap = [(142, 262), (146, 204), (178, 156), (236, 130), (298, 130), (352, 152), (382, 200), (384, 262), (370, 236),
           (352, 214), (318, 200), (288, 188), (262, 178), (234, 188), (206, 212), (176, 232), (152, 250)]
    _shape(pen, cap, hair, 3.6, 3, 0.18)
    hl = shade(hair, 1.9)
    _line(pen, [(200, 160), (252, 140), (312, 150)], hl, 5)


# --- bodies ----------------------------------------------------------------------------------------------------------

def _shoes_woman(pen, shoe):
    for s in (-1, 1):
        x = 260 + s * 24
        _shape(pen, [(x - s * 20, 850), (x + s * 12, 846), (x + s * 34, 866), (x + s * 24, 880), (x - s * 18, 880)], shoe, 3.2, 3, 0.2)
        pen.line([(x + s * 4, 856), (x + s * 20, 868)], shade(shoe, 1.6), 3)


def _shoes_man(pen, shoe):
    for s in (-1, 1):
        x = 260 + s * 30
        _shape(pen, [(x - s * 22, 846), (x + s * 8, 844), (x + s * 34, 862), (x + s * 32, 880), (x - s * 20, 880)], shoe, 3.2, 3, 0.2)
        pen.line([(x + s * 8, 860), (x + s * 28, 870)], shade(shoe, 1.8), 3)


def _woman(pen, d, o, skin, top, bottom, shoe):
    for s in (-1, 1):                                                         # slim legs
        _tube(pen, [(260 + s * 24, 716), (260 + s * 25, 790), (260 + s * 24, 852)], 36, 23, shade(skin, 0.97), 3.2)
    _shoes_woman(pen, shoe)
    skirt = [(206, 580), (314, 580), (328, 636), (312, 716), (260, 722), (208, 716), (192, 636)]
    _shape(pen, skirt, bottom, 3.6, 3, 0.15)
    for pts in ([(236, 600), (232, 660), (236, 714)], [(284, 600), (290, 660), (284, 714)]):
        _line(pen, pts, shade(bottom, 0.82), 3.4)                              # soft fold lines
    blouse = [(236, 410), (200, 418), (176, 442), (176, 500), (192, 548), (206, 592), (314, 592), (328, 548), (344, 500),
              (344, 442), (320, 418), (284, 410)]
    _shape(pen, blouse, top, 3.6, 3, 0.2)
    _line(pen, [(198, 520), (214, 548), (212, 576)], shade(top, 0.8), 3.2)
    _line(pen, [(322, 520), (306, 548), (308, 576)], shade(top, 0.8), 3.2)
    pen.line([(260, 440), (260, 584)], shade(top, 0.84), 2.6)                  # button placket
    for y in (468, 506, 544):
        pen.circle(260, y, 3.2, (252, 250, 244))
    belt = (112, 78, 58)
    _shape(pen, [(204, 578), (316, 578), (318, 596), (202, 596)], belt, 3.0, 2, 0.12)
    pen.rect(252, 580, 268, 594, (232, 196, 110), radius=3)
    for s in (-1, 1):                                                         # round collar flaps
        _shape(pen, [(260 + s * 4, 410), (260 + s * 40, 408), (260 + s * 52, 428), (260 + s * 20, 442)], shade(top, 1.12), 3.0, 3, 0.22)


def _man(pen, d, o, skin, top, bottom, shoe):
    for s in (-1, 1):
        _tube(pen, [(260 + s * 26, 604), (260 + s * 26, 740), (260 + s * 25, 850)], 76, 50, bottom, 3.4)
        pen.line([(260 + s * 26, 700), (260 + s * 28, 760)], shade(bottom, 0.8), 3)       # trouser crease
    _shoes_man(pen, shoe)
    shirt = [(234, 410), (196, 418), (176, 440), (176, 500), (190, 548), (204, 604), (316, 604), (330, 548), (344, 500),
             (344, 440), (324, 418), (286, 410)]
    _shape(pen, shirt, top, 3.6, 3, 0.2)
    _line(pen, [(196, 500), (208, 546), (206, 584)], shade(top, 0.82), 3.2)
    _line(pen, [(324, 500), (312, 546), (314, 584)], shade(top, 0.82), 3.2)
    pen.line([(260, 438), (260, 596)], shade(top, 0.8), 2.6)
    for y in (470, 510, 550):
        pen.circle(260, y, 3.2, (250, 250, 244))
    _shape(pen, [(206, 592), (314, 592), (316, 612), (204, 612)], (74, 56, 46), 3.0, 2, 0.12)   # belt
    pen.rect(250, 594, 270, 610, (214, 188, 120), radius=3)
    _shape(pen, [(212, 482), (240, 482), (240, 516), (212, 516)], shade(top, 1.1), 2.8, 2, 0.15)   # chest pocket
    for s in (-1, 1):                                                         # shirt collar, top button open
        _shape(pen, [(260 + s * 2, 412), (260 + s * 44, 410), (260 + s * 58, 440), (260 + s * 14, 456)], shade(top, 1.15), 3.0, 2, 0.15)


# --- more women: a hoodie-and-jeans host, a pregnant mum in a dress, a grandmother in a sarong ----------------------------

def _hair_back_long(pen, hair):
    pts = [(142, 250), (126, 340), (124, 450), (132, 540), (156, 566), (196, 556), (214, 480), (306, 480), (324, 556),
           (364, 566), (388, 540), (396, 450), (394, 340), (378, 250)]
    _shape(pen, pts, hair, 3.6, 3, 0.2)


def _hair_front_part(pen, hair):
    """Smooth side-parted fringe (host): no extra locks."""
    cap = [(136, 256), (146, 198), (186, 154), (242, 132), (306, 136), (356, 164), (384, 214), (388, 262), (374, 244),
           (346, 226), (310, 214), (276, 206), (246, 216), (214, 238), (180, 268), (152, 296), (140, 290)]
    _shape(pen, cap, hair, 3.6, 3, 0.18)
    _line(pen, [(204, 166), (252, 150), (308, 160)], shade(hair, 1.6), 5)


def _hair_perm(pen, hair):
    """Short soft curls (mum): overlapping rounded tufts around the head and a side-swept fringe."""
    for x, y, rx, ry in ((160, 230, 40, 56), (360, 230, 40, 56), (200, 170, 56, 44), (260, 150, 62, 44), (322, 170, 56, 44),
                         (150, 300, 30, 40), (370, 300, 30, 40)):
        CA._outlined_ellipse(pen, x, y, rx, ry, hair, 3.4)
    fringe = [(150, 250), (160, 200), (210, 172), (270, 166), (330, 180), (372, 214), (376, 252), (350, 232), (310, 220),
              (262, 224), (214, 244), (176, 270)]
    _shape(pen, fringe, hair, 3.4, 3, 0.2)
    _line(pen, [(206, 178), (254, 164), (308, 174)], shade(hair, 1.6), 5)


def _hair_gray(pen, hair):
    """Grandmother: neat swept-back grey hair with a round bun on top and a little pin."""
    CA._outlined_ellipse(pen, 260, 118, 50, 42, hair, 3.4)
    cap = [(138, 262), (146, 196), (186, 152), (244, 134), (308, 138), (358, 164), (384, 214), (386, 262), (366, 236),
           (330, 214), (290, 206), (250, 208), (210, 218), (172, 238), (150, 254)]
    _shape(pen, cap, hair, 3.6, 3, 0.18)
    _line(pen, [(200, 168), (252, 152), (310, 164)], shade(hair, 1.25), 5)
    _shape(pen, [(300, 100), (322, 94), (326, 112), (306, 118)], (232, 186, 96), 2.6, 2, 0.2)


def _legs_skin(pen, skin, y0=740, wide=36):
    for s in (-1, 1):
        _tube(pen, [(260 + s * 24, y0), (260 + s * 25, (y0 + 852) // 2), (260 + s * 24, 852)], wide, 23, shade(skin, 0.97), 3.2)


def _flats(pen, shoe):
    for s in (-1, 1):
        x = 260 + s * 26
        _shape(pen, [(x - s * 20, 856), (x + s * 14, 852), (x + s * 34, 866), (x + s * 26, 880), (x - s * 18, 880)], shoe, 3.2, 3, 0.2)


def _hoodie_jeans(pen, d, o, skin, top, bottom, shoe):
    for s in (-1, 1):
        _tube(pen, [(260 + s * 26, 612), (260 + s * 26, 740), (260 + s * 25, 850)], 74, 52, bottom, 3.4)
        pen.line([(260 + s * 26, 700), (260 + s * 28, 760)], shade(bottom, 0.82), 3)
        pen.line([(260 + s * 8, 846), (260 + s * 44, 850)], shade(bottom, 1.3), 6)          # turned-up cuff
    for s in (-1, 1):                                                                       # white sneakers
        x = 260 + s * 30
        _shape(pen, [(x - s * 22, 846), (x + s * 8, 844), (x + s * 36, 864), (x + s * 34, 880), (x - s * 20, 880)], (248, 246, 240), 3.2, 3, 0.2)
        pen.line([(x - s * 20, 872), (x + s * 34, 872)], shade(top, 1.05), 5)
    body = [(232, 408), (190, 420), (166, 452), (160, 540), (168, 626), (352, 626), (360, 540), (354, 452), (330, 420), (288, 408)]
    _shape(pen, body, top, 3.6, 3, 0.22)
    _shape(pen, [(200, 396), (260, 384), (320, 396), (338, 428), (260, 452), (182, 428)], shade(top, 0.9), 3.2, 3, 0.2)   # hood bunched at the neck
    acc = rgb(o.get("accent", "#F4EBD0"))
    for x in (240, 282):
        pen.line([(x, 450), (x - 4 if x < 260 else x + 4, 510)], acc, 3.6)
        pen.circle(x - 4 if x < 260 else x + 4, 514, 4.4, acc)
    _shape(pen, [(198, 566), (322, 566), (336, 624), (184, 624)], shade(top, 0.9), 3.2, 3, 0.18)                          # kangaroo pocket
    _line(pen, [(176, 500), (186, 560), (182, 604)], shade(top, 0.82), 3.2)
    _line(pen, [(344, 500), (334, 560), (338, 604)], shade(top, 0.82), 3.2)


def _dress(pen, d, o, skin, top, bottom, shoe):
    belly = bool(o.get("belly"))
    _legs_skin(pen, skin, 742)
    _flats(pen, shoe)
    w = 12 if belly else 0
    pts = [(236, 410), (200, 418), (178, 442), (178, 500), (194, 548), (180 - w, 604), (168 - w, 664), (152, 744), (260, 752),
           (368, 744), (352 + w, 664), (340 + w, 604), (326, 548), (342, 500), (342, 442), (320, 418), (284, 410)]
    _shape(pen, pts, top, 3.6, 3, 0.2)
    pen.line(CA._spline([(196, 552), (260, 566), (324, 552)]), shade(top, 0.78), 5)                                      # empire waistline
    _line(pen, [(228, 590), (222, 660), (212, 740)], shade(top, 0.84), 3.2)
    _line(pen, [(292, 590), (298, 660), (308, 740)], shade(top, 0.84), 3.2)
    if belly:                                                                 # a round bump under the empire waist
        _shape(pen, [(190, 600), (260, 578), (330, 600), (344, 650), (320, 696), (260, 708), (200, 696), (176, 650)], shade(top, 1.06), 3.2, 3, 0.25)
        _line(pen, [(214, 666), (260, 684), (306, 666)], shade(top, 0.82), 3.0)
    acc = rgb(o.get("accent", "#FFFFFF"))
    for x, y in ((214, 470), (250, 500), (300, 470), (230, 640), (292, 690), (206, 700), (320, 626)):
        pen.circle(x, y, 4.2, acc)
    _shape(pen, [(228, 410), (260, 436), (292, 410), (270, 408), (260, 414), (250, 408)], shade(top, 1.12), 3.0, 2, 0.15)     # soft V neckline


def _sarong(pen, d, o, skin, top, bottom, shoe):
    _legs_skin(pen, skin, 790, 30)
    for s in (-1, 1):                                                                       # sandals
        x = 260 + s * 26
        _shape(pen, [(x - s * 18, 862), (x + s * 14, 858), (x + s * 30, 870), (x + s * 22, 880), (x - s * 16, 880)], shoe, 3.0, 3, 0.2)
    skirt = [(204, 584), (316, 584), (328, 690), (324, 794), (196, 794), (192, 690)]
    _shape(pen, skirt, bottom, 3.6, 3, 0.14)
    pen.rect(196, 760, 324, 792, shade(bottom, 0.72), radius=3)                             # hem band
    acc = rgb(o.get("accent", "#F4E2B0"))
    pen.line([(198, 772), (322, 772)], acc, 4)
    for x in range(214, 316, 24):
        pen.circle(x, 782, 3.6, acc)
    blouse = [(236, 410), (198, 418), (174, 442), (172, 500), (186, 548), (200, 592), (320, 592), (334, 548), (348, 500),
              (346, 442), (322, 418), (284, 410)]
    _shape(pen, blouse, top, 3.6, 3, 0.2)
    flower = rgb(o.get("flower", "#F6D9E0"))
    for x, y in ((206, 470), (250, 500), (300, 466), (226, 548), (290, 556), (330, 520), (196, 520)):
        pen.circle(x, y, 7, flower)
        pen.circle(x, y, 2.6, (250, 214, 110))
    _shape(pen, [(228, 410), (260, 438), (292, 410)], shade(top, 1.1), 3.0, 2, 0.2)


def _age_lines(pen, skin):
    for s in (-1, 1):
        _line(pen, [(260 + s * 96, 316), (260 + s * 108, 326), (260 + s * 100, 340)], shade(skin, 0.78), 2.6)
        _line(pen, [(260 + s * 64, 262), (260 + s * 74, 272)], shade(skin, 0.8), 2.2)


def draw(pen, d: dict, o: dict):
    skin, cheek, hair = rgb(d["skin"]), rgb(d["cheek"]), rgb(d.get("hair", "#3B2A26"))
    top, bottom = rgb(o["top"]), rgb(o.get("bottom", "#4A5A80"))
    shoe = rgb(o.get("shoe", "#4A3B32"))
    style = d.get("hair_style", "short")
    woman = d.get("gender") == "female"
    kind = o.get("kind", d.get("outfit_kind", "blouse_skirt" if woman else "shirt_slacks"))
    arms = arms_pose(o.get("arms", "down"))
    front = any(k in o.get("arms", "") for k in ("eat", "sip"))
    if woman and style == "bob":
        _hair_back_woman(pen, hair)
    elif woman and style == "long":
        _hair_back_long(pen, hair)
    body = {"blouse_skirt": _woman, "shirt_slacks": _man, "hoodie_jeans": _hoodie_jeans, "dress": _dress, "sarong": _sarong}[kind]
    body(pen, d, o, skin, top, bottom, shoe)
    if kind in ("blouse_skirt", "shirt_slacks") and not o.get("no_lanyard"):
        _lanyard(pen, rgb(o.get("lanyard", "#E8605A")), rgb(o.get("badge", "#78B8E6")))
    puff = kind in ("blouse_skirt", "dress", "sarong")
    sleeve = o.get("sleeve", 0.24 if puff else (0.5 if kind == "shirt_slacks" else 0.72))

    def draw_arms():
        mapped = [tuple(M(p) for p in a) for a in arms]
        for side, pts in zip((-1, 1), mapped):
            _arm(pen, list(pts), skin, top, sleeve, side, puff=puff, cuff_fold=(kind == "shirt_slacks"))
        if o.get("prop"):
            hand = mapped[1][2] if o.get("prop_hand", "right") == "right" else mapped[0][2]
            if o.get("arms") in ("phone", "hold"):
                hand = ((mapped[0][2][0] + mapped[1][2][0]) / 2, mapped[0][2][1])
            CA._prop(pen, o["prop"], hand, o)
            for pts in mapped:
                _hand(pen, pts[2][0], pts[2][1] + 4, skin, 1)

    if not front:
        draw_arms()
    _neck(pen, skin)
    for s in (-1, 1):
        _ear(pen, s, skin)
    _head(pen, skin, cheek)
    if d.get("age_lines"):
        _age_lines(pen, skin)
    if style == "bob":
        _hair_front_woman(pen, hair, clip=not d.get("no_clip"))
    elif style == "long":
        _hair_front_part(pen, hair)
    elif style == "perm":
        _hair_perm(pen, hair)
    elif style == "gray_bun":
        _hair_gray(pen, hair)
    else:
        _hair_man(pen, hair)
    if front:
        draw_arms()
    if d.get("glasses"):
        for x in (210, 310):
            pen.ellipse(x, 270, 36, 30, None, outline=(96, 72, 64), width=4)
        pen.line([(246, 268), (274, 268)], (96, 72, 64), 4)
    CA._brows_styled(pen, o.get("brows", d.get("brows", "normal")), shade(hair, 1.0))
