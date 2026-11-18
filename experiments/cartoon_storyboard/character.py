"""A skeletal cartoon character drawn in the style of the illustration sheets
in `../character and props/`: warm brown outlines, tapered limbs with rounded
joints, a sweater with cuffs and hem, a 3/4 face with a tufted fringe, and a
soft cel shade on the side away from the light.

Units: the figure is ~100u tall standing; the origin is the ground point
under the hips. y grows downward (image coordinates). A limb angle of 0
points straight down; positive angles rotate toward +x (the facing side).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from PIL import Image, ImageChops, ImageDraw, ImageFilter

from art import INK, SS, mix, shade

THIGH, SHIN, UPPER, FORE = 18.0, 17.0, 14.0, 13.0
TORSO, NECK_TO_HEAD = 26.0, 16.0
CANVAS_W, CANVAS_H, ORIGIN_X, ORIGIN_Y = 150.0, 132.0, 75.0, 122.0
OW = 0.95          # outline width
DETAIL = 0.5       # inner detail strokes (hem, cuffs, collar)
LIGHT = (1.3, -1.0)  # shading: the shape shifted toward the light leaves a back/bottom crescent


@dataclass(frozen=True)
class Palette:
    skin: tuple
    hair: tuple
    top: tuple
    pants: tuple
    shoes: tuple
    ink: tuple = INK
    cheek: tuple | None = None
    face: bool = True
    hair_style: str = "short"


MAIN = Palette(skin=(250, 214, 184), hair=(78, 56, 46), top=(240, 184, 82), pants=(74, 98, 138),
               shoes=(122, 88, 70), cheek=(242, 150, 140))
OTHERS = [
    Palette(skin=(246, 208, 178), hair=(84, 60, 48), top=(214, 124, 108), pants=(84, 96, 128),
            shoes=(110, 80, 64), cheek=(240, 150, 140), hair_style="long"),
    Palette(skin=(238, 196, 164), hair=(62, 46, 40), top=(126, 162, 112), pants=(118, 112, 106),
            shoes=(96, 74, 62), cheek=(232, 146, 132)),
    Palette(skin=(248, 212, 182), hair=(96, 68, 52), top=(112, 150, 190), pants=(70, 80, 102),
            shoes=(236, 230, 220), cheek=(240, 150, 140)),
    Palette(skin=(242, 204, 174), hair=(70, 50, 42), top=(224, 156, 174), pants=(92, 112, 142),
            shoes=(116, 84, 68), cheek=(236, 146, 140), hair_style="long"),
    Palette(skin=(236, 198, 168), hair=(52, 40, 36), top=(78, 92, 122), pants=(62, 66, 80),
            shoes=(70, 56, 50), cheek=(228, 146, 134)),
    Palette(skin=(248, 214, 186), hair=(90, 64, 50), top=(238, 234, 224), pants=(98, 98, 108),
            shoes=(110, 80, 64), cheek=(240, 152, 142), hair_style="long"),
    Palette(skin=(240, 202, 170), hair=(66, 48, 42), top=(98, 162, 160), pants=(84, 90, 110),
            shoes=(236, 230, 220), cheek=(234, 148, 136)),
    Palette(skin=(244, 206, 176), hair=(80, 56, 46), top=(182, 132, 92), pants=(70, 82, 104),
            shoes=(96, 72, 60), cheek=(238, 150, 138), hair_style="long"),
]
OTHER = Palette(skin=(182, 190, 206), hair=(136, 144, 164), top=(156, 166, 188), pants=(124, 134, 156),
                shoes=(200, 206, 218), ink=(112, 120, 142), face=False)
IDEAL = Palette(skin=(255, 246, 222), hair=(255, 240, 205), top=(255, 236, 196), pants=(255, 232, 190),
                shoes=(255, 246, 222), ink=(240, 214, 170), face=False)


@dataclass
class Pose:
    view: str = "side"
    hip: tuple = (0.0, -38.0)
    lean: float = 2.0
    legs: list = field(default_factory=lambda: [("ang", -3, -3), ("ang", 3, 3)])
    arms: list = field(default_factory=lambda: [("ang", -6, 2), ("ang", 6, 10)])
    look: tuple = (0.0, 0.0)
    blink: bool = False
    phone: bool = False
    paper: bool = False         # holds a sheet of paper (a bill) instead of a phone
    leg_bend: tuple = (1, 1)
    arm_bend: tuple = (-1, -1)
    mood: str = "calm"          # calm | pensive
    shadow: bool = True         # soft contact shadow under the feet
    legs_front: bool = False    # draw the near leg in front of the torso (knees hugged)


# --- geometry -----------------------------------------------------------------

def _pt(o, ang, length):
    a = math.radians(ang)
    return (o[0] + length * math.sin(a), o[1] + length * math.cos(a))


def _ik(root, target, l1, l2, bend):
    dx, dy = target[0] - root[0], target[1] - root[1]
    d = max(abs(l1 - l2) + 1e-3, min(l1 + l2 - 1e-3, math.hypot(dx, dy)))
    a = math.atan2(dy, dx)
    b = math.acos((l1 * l1 + d * d - l2 * l2) / (2 * l1 * d))
    ang = a + bend * b
    joint = (root[0] + l1 * math.cos(ang), root[1] + l1 * math.sin(ang))
    end = (root[0] + (dx / max(1e-6, math.hypot(dx, dy))) * d, root[1] + (dy / max(1e-6, math.hypot(dx, dy))) * d)
    return joint, end


def _limb(root, spec, l1, l2, bend):
    if spec[0] == "ang":
        mid = _pt(root, spec[1], l1)
        return mid, _pt(mid, spec[2], l2)
    return _ik(root, spec[1], l1, l2, bend)


def _add(p, q, f=1.0):
    return (p[0] + q[0] * f, p[1] + q[1] * f)


def _unit(p, q):
    dx, dy = q[0] - p[0], q[1] - p[1]
    n = math.hypot(dx, dy) or 1e-6
    return dx / n, dy / n


def _smooth(pts, n=2, closed=False):
    """Chaikin corner cutting: rounds knees, elbows and polygon corners."""
    for _ in range(n):
        src = pts + [pts[0]] if closed else pts
        out = [] if closed else [pts[0]]
        for a, b in zip(src, src[1:]):
            out.append((0.75 * a[0] + 0.25 * b[0], 0.75 * a[1] + 0.25 * b[1]))
            out.append((0.25 * a[0] + 0.75 * b[0], 0.25 * a[1] + 0.75 * b[1]))
        if not closed:
            out.append(pts[-1])
        pts = out
    return pts


def _tube(pts, r0, r1, step=0.35):
    """A tapered limb as a chain of discs along the smoothed centerline."""
    pts = _smooth(list(pts))
    seg = [math.dist(a, b) for a, b in zip(pts, pts[1:])]
    total = sum(seg) or 1e-6
    prims, acc = [], 0.0
    for (a, b), length in zip(zip(pts, pts[1:]), seg):
        n = max(1, int(length / step))
        for i in range(n):
            f = i / n
            prims.append(("disc", (a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f),
                          r0 + (r1 - r0) * (acc + length * f) / total))
        acc += length
    prims.append(("disc", pts[-1], r1))
    return prims


def _ellipse(c, rx, ry, rot=0.0, n=40):
    ca, sa = math.cos(rot), math.sin(rot)
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        x, y = rx * math.cos(a), ry * math.sin(a)
        pts.append((c[0] + x * ca - y * sa, c[1] + x * sa + y * ca))
    return pts


def _arc(c, rx, ry, a0, a1, n=24):
    """Points on an ellipse; angles in degrees, 90 = up."""
    return [(c[0] + rx * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             c[1] - ry * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


def _rtrap(hb, ht, v0, v1, rt, rb):
    """Rounded trapezoid in (x, v) with v pointing up: half-width hb at the
    bottom (v0), ht at the top (v1), corner radii rb / rt."""
    pts = []
    for cx, cv, r, a0 in ((-hb + rb, v0 + rb, rb, 180), (hb - rb, v0 + rb, rb, 270),
                          (ht - rt, v1 - rt, rt, 0), (-ht + rt, v1 - rt, rt, 90)):
        for i in range(7):
            a = math.radians(a0 + 90 * i / 6)
            pts.append((cx + r * math.cos(a), cv + r * math.sin(a)))
    return pts


# --- drawing surface ------------------------------------------------------------

class _Canvas:
    """Supersampled RGBA canvas in figure units. A shape is a list of
    ("disc", center, r) / ("poly", points) primitives drawn as one union:
    outline first (grown by OW), then fill, then the shade crescent."""

    def __init__(self, k):
        self.f = k * SS
        self.img = Image.new("RGBA", (int(CANVAS_W * k) * SS, int(CANVAS_H * k) * SS), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.img)

    def P(self, p):
        return (ORIGIN_X + p[0]) * self.f, (ORIGIN_Y + p[1]) * self.f

    def _paint(self, d, prims, grow, off, fill):
        g = grow * self.f
        for prim in prims:
            if prim[0] == "disc":
                x, y = self.P(prim[1])
                x, y, r = x - off[0], y - off[1], prim[2] * self.f + g
                d.ellipse((x - r, y - r, x + r, y + r), fill=fill)
            else:
                pts = [(x - off[0], y - off[1]) for x, y in map(self.P, prim[1])]
                d.polygon(pts, fill=fill)
                if g > 0:
                    d.line(pts + [pts[0]], fill=fill, width=max(1, int(round(2 * g))), joint="curve")
                    for x, y in pts:
                        d.ellipse((x - g, y - g, x + g, y + g), fill=fill)

    def _bbox(self, prims, pad):
        xs, ys = [], []
        for prim in prims:
            if prim[0] == "disc":
                (x, y), r = self.P(prim[1]), prim[2] * self.f
                xs += [x - r, x + r]
                ys += [y - r, y + r]
            else:
                for x, y in map(self.P, prim[1]):
                    xs.append(x)
                    ys.append(y)
        w, h = self.img.size
        return (max(0, int(min(xs) - pad)), max(0, int(min(ys) - pad)),
                min(w, int(max(xs) + pad) + 1), min(h, int(max(ys) + pad) + 1))

    def shape(self, prims, fill, ink=None, shade_col=None, light=LIGHT):
        if ink is not None:
            self._paint(self.d, prims, OW, (0, 0), ink)
        self._paint(self.d, prims, 0, (0, 0), fill)
        if shade_col is None:
            return
        x0, y0, x1, y1 = self._bbox(prims, 4)
        if x1 <= x0 or y1 <= y0:
            return
        full, lit = Image.new("L", (x1 - x0, y1 - y0), 0), Image.new("L", (x1 - x0, y1 - y0), 0)
        self._paint(ImageDraw.Draw(full), prims, 0, (x0, y0), 255)
        self._paint(ImageDraw.Draw(lit), prims, 0, (x0 - light[0] * self.f, y0 - light[1] * self.f), 255)
        self.img.paste((*shade_col, 255), (x0, y0, x1, y1), ImageChops.subtract(full, lit))

    def stroke(self, pts, color, width):
        p = [self.P(q) for q in pts]
        w = width * self.f
        self.d.line(p, fill=color, width=max(1, int(round(w))), joint="curve")
        r = w / 2
        for x, y in (p[0], p[-1]):
            self.d.ellipse((x - r, y - r, x + r, y + r), fill=color)

    def result(self):
        return self.img.resize((self.img.width // SS, self.img.height // SS), Image.LANCZOS)


# --- the figure -------------------------------------------------------------------

def render(pose: Pose, pal: Palette, scale: float, facing: int = 1, tint=None, glow=None) -> Image.Image:
    """Return an RGBA sprite. Its origin (ground point) sits at
    (ORIGIN_X*scale, ORIGIN_Y*scale) in sprite pixels."""
    cv = _Canvas(scale)
    ink = pal.ink
    side = pose.view == "side"
    lean = math.radians(pose.lean)
    up = (math.sin(lean), -math.cos(lean))
    right = (math.cos(lean), math.sin(lean))
    hip = pose.hip
    sh = _add(hip, up, TORSO)
    head = _add(sh, up, NECK_TO_HEAD)

    def T(x, v):
        return (hip[0] + right[0] * x + up[0] * v, hip[1] + right[1] * x + up[1] * v)

    if side:
        hips = [(hip[0] - 2, hip[1]), (hip[0] + 1, hip[1])]
        shoulders = [(sh[0] - 2, sh[1] + 1.5), (sh[0] + 1, sh[1] + 1.5)]
    else:
        hips = [(hip[0] - 5.5, hip[1]), (hip[0] + 5.5, hip[1])]
        shoulders = [(sh[0] - 10, sh[1] + 2.5), (sh[0] + 10, sh[1] + 2.5)]
    legs = [_limb(hips[i], pose.legs[i], THIGH, SHIN, pose.leg_bend[i]) for i in range(2)]
    arms = [_limb(shoulders[i], pose.arms[i], UPPER, FORE, pose.arm_bend[i]) for i in range(2)]

    if side:
        face_c, blob_c, blob_r = _add(head, (1.4, 1.6)), _add(head, (-1.4, -1.6)), (12.6, 12.2)
    else:
        face_c, blob_c, blob_r = _add(head, (0.0, 1.6)), _add(head, (0.0, -1.8)), (13.0, 12.4)

    def shoe(i, color):
        knee, ankle = legs[i]
        if side:
            shin = math.degrees(math.atan2(ankle[0] - knee[0], ankle[1] - knee[1]))
            rot = math.radians(min(50.0, max(0.0, -shin) * 0.55))
            local = [(-3.2, 4.4), (6.4, 4.4), (7.6, 2.8), (6.0, 0.6), (2.0, -0.8), (-2.8, -0.4), (-3.9, 2.0)]
            ca, sa = math.cos(rot), math.sin(rot)
            pts = [(ankle[0] + x * ca - y * sa, ankle[1] + x * sa + y * ca) for x, y in local]
            prims = [("poly", _smooth(pts, 2, closed=True))]
        else:
            prims = [("poly", _ellipse(_add(ankle, (0, 2.5)), 4.2, 2.8))]
        cv.shape(prims, color, ink, shade(color, 0.8))

    def leg(i, color):
        knee, ankle = legs[i]
        cv.shape(_tube([hips[i], knee, ankle], 5.0, 4.1), color, ink, shade(color, 0.82))

    def hand(i, color):
        elbow, wrist = arms[i]
        d = _unit(elbow, wrist)
        perp = (-d[1], d[0]) if -d[1] >= 0 else (d[1], -d[0])
        c = _add(wrist, d, 3.0)
        prims = [("poly", _ellipse(c, 3.1, 2.6, math.atan2(d[1], d[0]), 28)),
                 ("disc", _add(_add(c, perp, 2.3), d, -0.6), 1.15)]
        cv.shape(prims, color, ink, shade(color, 0.92))

    def arm(i, color):
        elbow, wrist = arms[i]
        cv.shape(_tube([shoulders[i], elbow, wrist], 3.6, 3.05), color, ink, shade(color, 0.86))
        d = _unit(elbow, wrist)
        c = _add(wrist, d, -1.8)
        cv.stroke([_add(c, (-d[1], d[0]), 2.6), _add(c, (d[1], -d[0]), 2.6)], ink, DETAIL)

    def pelvis():
        c, rx, ry = (T(-0.4, -1.0), 7.6, 5.8) if side else (T(0, -1.2), 11.0, 6.2)
        cv.shape([("poly", _ellipse(c, rx, ry))], pal.pants, ink, shade(pal.pants, 0.82))

    def neck():
        top = _add(sh, up, 6)
        cv.shape(_tube([_add(sh, up, -1), top], 2.7 if side else 3.0, 2.6 if side else 2.9),
                 pal.skin, ink, shade(pal.skin, 0.9))

    def torso():
        hb, ht, rt = (8.8, 8.2, 5.5) if side else (12.4, 12.8, 6.5)
        v0, v1 = -3.2, TORSO + 1.8
        cv.shape([("poly", [T(x, v) for x, v in _rtrap(hb, ht, v0, v1, rt, 2.0)])],
                 pal.top, ink, shade(pal.top, 0.86))
        cv.stroke([T(-hb + 1.0, v0 + 1.8), T(hb - 1.0, v0 + 1.8)], ink, DETAIL)
        if side:
            cv.stroke(_smooth([T(0.5, v1 - 0.6), T(3.0, v1 - 2.0), T(5.8, v1 - 2.4)]), ink, DETAIL)
            cv.stroke([T(5.2, v0 + 3.4), T(6.2, v0 + 6.0)], ink, DETAIL * 0.85)
        else:
            cv.stroke(_smooth([T(-4.4, v1 - 0.8), T(-2.0, v1 - 2.8), T(0, v1 - 3.2),
                               T(2.0, v1 - 2.8), T(4.4, v1 - 0.8)]), ink, DETAIL)

    def back_hair():
        if pal.hair_style != "long":
            return
        c = _add(head, (-3.0, 0)) if side else head
        hw = 9.5 if side else 13.2
        pts = [(c[0] + x, c[1] - v) for x, v in _rtrap(hw, hw, -17.0, 4.0, 6.0, 3.5)]
        cv.shape([("poly", pts)], shade(pal.hair, 0.92), ink)

    def draw_head():
        F = face_c
        cv.shape([("poly", _ellipse(blob_c, *blob_r))], pal.hair, ink)
        if not side:
            for ex in (-10.6, 10.6):
                cv.shape([("poly", _ellipse(_add(F, (ex, 1.4)), 2.1, 2.8))], pal.skin, ink)
        rx, ry = (10.6, 10.2) if side else (11.0, 10.2)
        cv.shape([("poly", _ellipse(F, rx, ry))], pal.skin, ink, shade(pal.skin, 0.93))

        bc = (blob_c[0] - F[0], blob_c[1] - F[1])
        if side:
            fringe = [(10.9, -3.4), (8.6, -6.0), (7.4, -2.6), (4.8, -6.6), (3.0, -3.4), (0.2, -6.8),
                      (-1.6, -4.2), (-4.2, -6.6), (-7.4, -4.0), (-9.4, -1.0)]
            top = _arc(bc, blob_r[0] + 0.3, blob_r[1] + 0.3, 200, 10, 30)
            tuft = [(-5.6, -14.6), (-4.6, -16.6), (-3.0, -15.6), (-1.6, -17.0), (-0.2, -15.0)]
        else:
            fringe = [(11.4, -1.8), (8.8, -6.2), (7.0, -2.8), (4.2, -6.8), (2.0, -3.6), (-0.8, -7.0),
                      (-2.8, -3.8), (-5.6, -6.6), (-7.4, -3.6), (-9.6, -5.8), (-11.4, -1.8)]
            top = _arc(bc, blob_r[0] + 0.3, blob_r[1] + 0.3, 190, -10, 30)
            tuft = [(-2.6, -15.4), (-1.6, -17.4), (0.0, -16.2), (1.4, -17.6), (2.8, -15.4)]
        absol = lambda pts: [(F[0] + x, F[1] + y) for x, y in pts]
        cv.shape([("poly", absol(fringe + top)), ("poly", absol(tuft))], pal.hair, ink)
        hl = mix(pal.hair, (255, 255, 255), 0.22)
        strand = [(-8.0, -9.0), (-5.0, -11.6), (-1.4, -12.6)] if side else [(-6.4, -10.6), (-2.6, -12.8)]
        cv.stroke(_smooth(absol(strand)), hl, 0.8)
        if not pal.face:
            return

        lx, ly = pose.look
        eye_col, brow_col = (52, 40, 38), shade(pal.hair, 0.85)
        if side:
            eyes = [((5.8, 2.0), 1.3, -1), ((0.2, 1.9), 1.05, 1)]   # (pos, width, inner side)
            cheeks, mouth = [((-1.6, 5.2), 1.8)], (4.4, 6.8)
        else:
            eyes = [((-4.3, 2.0), 1.3, 1), ((4.3, 2.0), 1.3, -1)]
            cheeks, mouth = [((-6.8, 5.4), 2.2), ((6.8, 5.4), 2.2)], (0.0, 6.6)
        if pal.cheek:
            cheek = mix(pal.skin, pal.cheek, 0.55)
            for (cx, cy), w in cheeks:
                cv.shape([("poly", _ellipse(_add(F, (cx + lx * 0.5, cy + ly * 0.5)), w, 1.3))], cheek)
        for (ex, ey), w, inner in eyes:
            x, y = F[0] + ex + lx, F[1] + ey + ly
            if pose.blink:
                cv.stroke([(x - 1.5, y), (x, y + 0.7), (x + 1.5, y)], eye_col, 0.7)
            else:
                cv.shape([("poly", _ellipse((x, y), w, 1.75, n=24))], eye_col)
                cv.shape([("disc", (x + 0.45 * w, y - 0.6), 0.45)], (255, 255, 255))
            lift = 0.9 if pose.mood == "pensive" else 0.0
            cv.stroke([(x - 1.6 * inner, y - 3.4 + lift * 0.3), (x + 1.5 * inner, y - 3.5 - lift)], brow_col, 0.75)
        mx, my = F[0] + mouth[0] + lx * 0.7, F[1] + mouth[1] + ly * 0.6
        if pose.mood == "pensive":
            cv.stroke([(mx - 1.1, my + 0.35), (mx, my), (mx + 1.1, my + 0.35)], ink, 0.6)
        else:
            cv.stroke([(mx - 1.3, my), (mx, my + 0.7), (mx + 1.3, my)], ink, 0.6)

    def phone():
        h1, h2 = arms[0][1], arms[1][1]
        cx, cy = (h1[0] + h2[0]) / 2, (h1[1] + h2[1]) / 2 - 2.5
        if pose.paper:
            hw, hh = (2.0, 8.5) if side else (6.4, 8.6)
            pts = [(cx + x, cy - 1.5 - v) for x, v in _rtrap(hw, hw, -hh, hh, 0.6, 0.6)]
            cv.shape([("poly", pts)], (252, 250, 244), ink)
            if not side:
                for k in range(5):
                    y = cy - 7.0 + k * 2.6
                    cv.stroke([(cx - 4.2, y), (cx + (4.2 if k < 4 else 0.5), y)], (176, 170, 168), 0.45)
                cv.stroke([(cx + 1.4, cy + 4.4), (cx + 4.4, cy + 4.4)], (214, 80, 70), 0.7)
            return
        if side:
            pts = [(cx - 1.2, cy - 6.5), (cx + 1.6, cy - 6.0), (cx + 1.0, cy + 5.5), (cx - 1.8, cy + 5.0)]
            cv.shape([("poly", pts)], (52, 54, 70), ink)
        else:
            for hw, hh, r, color, outline in ((4.2, 6.8, 1.6, (52, 54, 70), ink), (3.4, 5.8, 1.0, (196, 228, 255), None)):
                pts = [(cx + x, cy - v) for x, v in _rtrap(hw, hw, -hh, hh, r, r)]
                cv.shape([("poly", pts)], color, outline)

    if pose.shadow and glow is None:
        x, y = cv.P((0.0, 1.0))
        rx, ry = 12.5 * cv.f, 2.3 * cv.f
        cv.d.ellipse((x - rx, y - ry, x + rx, y + ry), fill=(70, 52, 60, 52))
    back_hair()
    if side:
        far_top, far_pants, far_skin = shade(pal.top, 0.88), shade(pal.pants, 0.86), shade(pal.skin, 0.92)
        hand(0, far_skin)
        arm(0, far_top)
        shoe(0, shade(pal.shoes, 0.88))
        leg(0, far_pants)
        if not pose.legs_front:
            shoe(1, pal.shoes)
            leg(1, pal.pants)
        pelvis()
        neck()
        torso()
        if pose.legs_front:
            shoe(1, pal.shoes)
            leg(1, pal.pants)
        draw_head()
        if pose.phone or pose.paper:
            phone()
        hand(1, pal.skin)
        arm(1, pal.top)
    else:
        for i in range(2):
            shoe(i, pal.shoes)
            leg(i, pal.pants)
        pelvis()
        neck()
        torso()
        draw_head()
        for i in range(2):
            hand(i, pal.skin)
        for i in range(2):
            arm(i, pal.top)
        if pose.phone or pose.paper:
            phone()

    sprite = cv.result()
    if tint is not None:
        r, g, b, a = sprite.split()
        r = r.point(lambda v: int(v * tint[0]))
        g = g.point(lambda v: int(v * tint[1]))
        b = b.point(lambda v: int(v * tint[2]))
        sprite = Image.merge("RGBA", (r, g, b, a))
    if glow is not None:
        halo = Image.new("RGBA", sprite.size, (*glow, 0))
        halo.putalpha(sprite.getchannel("A").filter(ImageFilter.GaussianBlur(5 * scale)).point(lambda v: min(255, v * 2)))
        halo.alpha_composite(sprite)
        sprite = halo
    if facing < 0:
        sprite = sprite.transpose(Image.FLIP_LEFT_RIGHT)
    return sprite


# --- pose library -------------------------------------------------------------

def stand(look=(1.0, 0.0), blink=False, breath=0.0, view="side"):
    if view == "front":
        return Pose(view="front", hip=(0, -38 + breath), lean=0,
                    legs=[("ang", -4, -4), ("ang", 4, 4)], arms=[("ang", -14, -6), ("ang", 14, 6)],
                    look=look, blink=blink)
    return Pose(hip=(0, -38 + breath), look=look, blink=blink)


def walk(phase, look=(1.2, 0.2), stride=22.0, careful=False, blink=False):
    th = phase * 2 * math.pi
    near_t, far_t = stride * math.sin(th), -stride * math.sin(th)
    near_b = 26 * (1 + math.cos(th)) / 2
    far_b = 26 * (1 - math.cos(th)) / 2
    bob = -1.4 * (1 + math.cos(2 * th)) / 2
    arm = (12 if careful else 18) * math.sin(th)
    arm_lift = 24 if careful else 10
    return Pose(hip=(0, -38 + bob), lean=4,
                legs=[("ang", far_t, far_t - far_b), ("ang", near_t, near_t - near_b)],
                arms=[("ang", arm + (8 if careful else 0), arm + arm_lift), ("ang", -arm + (8 if careful else 0), -arm + arm_lift)],
                look=look, blink=blink)


def run(phase):
    th = phase * 2 * math.pi
    near_t, far_t = 36 * math.sin(th), -36 * math.sin(th)
    near_b = 55 * (1 + math.cos(th)) / 2
    far_b = 55 * (1 - math.cos(th)) / 2
    arm = 32 * math.sin(th)
    return Pose(hip=(0, -37 - 2 * abs(math.sin(th))), lean=14,
                legs=[("ang", far_t, far_t - far_b), ("ang", near_t, near_t - near_b)],
                arms=[("ang", arm, arm + 80), ("ang", -arm, -arm + 80)], look=(1.2, 0.0))


def sit_phone(blink=False, breath=0.0):
    return Pose(hip=(0, -20 + breath), lean=6,
                legs=[("ang", 84, 0), ("ang", 90, 2)],
                arms=[("ik", (19.5, -43.5)), ("ik", (22.5, -42.5))],
                look=(1.6, 2.4), blink=blink, phone=True, arm_bend=(1, 1), shadow=False)


def front_phone(blink=False, breath=0.0):
    return Pose(view="front", hip=(0, -38 + breath), lean=0,
                legs=[("ang", -4, -4), ("ang", 4, 4)],
                arms=[("ik", (-4.8, -47.0)), ("ik", (4.8, -47.0))],
                look=(0.0, 2.6), blink=blink, phone=True, arm_bend=(1, -1))


def sit_desk_chin(blink=False, breath=0.0, look=(1.5, 0.6)):
    return Pose(hip=(0, -20 + breath), lean=14,
                legs=[("ang", 84, 0), ("ang", 90, 2)],
                arms=[("ik", (26.0, -36.5)), ("ik", (16.5, -44.5))],
                look=look, blink=blink, arm_bend=(1, 1), mood="pensive", shadow=False)


def hug_knees(blink=False, breath=0.0, look=(1.5, 0.5)):
    return Pose(hip=(0, -7 + breath), lean=12,
                legs=[("ik", (15.5, -2.5)), ("ik", (17.0, -2.5))],
                arms=[("ik", (19.5, -24.0)), ("ik", (21.0, -22.5))],
                look=look, blink=blink, leg_bend=(-1, -1), arm_bend=(1, 1),
                mood="pensive", shadow=False, legs_front=True)


def type_desk(blink=False, breath=0.0, phase=0.0):
    """Sitting at a desk, both hands on the keyboard, tapping."""
    tap = 0.8 * math.sin(phase * 2 * math.pi)
    return Pose(hip=(0, -20 + breath), lean=10,
                legs=[("ang", 84, 0), ("ang", 90, 2)],
                arms=[("ik", (25.0, -33.5 - tap)), ("ik", (27.5, -33.0 + tap))],
                look=(1.6, 1.6), blink=blink, arm_bend=(1, 1), mood="pensive", shadow=False)


def asleep_desk(breath=0.0):
    """Slumped forward over the desk, head on the arms, eyes closed."""
    return Pose(hip=(0, -20 + breath * 0.5), lean=52,
                legs=[("ang", 84, 0), ("ang", 90, 2)],
                arms=[("ik", (30.0, -36.0)), ("ik", (33.0, -35.5))],
                look=(1.0, 1.4), blink=True, arm_bend=(1, 1), mood="pensive", shadow=False)


def clutch_chest(blink=False, breath=0.0):
    """Standing, bent a little, one hand pressed to the chest."""
    return Pose(hip=(0, -37 + breath), lean=12,
                legs=[("ang", -6, -2), ("ang", 8, 4)],
                arms=[("ang", 4, 12), ("ik", (12.0, -58.0))],
                look=(1.4, 1.8), blink=blink, arm_bend=(-1, 1), mood="pensive")


def hold_paper(blink=False, breath=0.0, look=(0.0, 2.6)):
    """Front view, holding a sheet of paper (the bill) at chest height."""
    return Pose(view="front", hip=(0, -38 + breath), lean=0,
                legs=[("ang", -4, -4), ("ang", 4, 4)],
                arms=[("ik", (-5.5, -50.0)), ("ik", (5.5, -50.0))],
                look=look, blink=blink, paper=True, arm_bend=(1, -1), mood="pensive")


def phone_up(blink=False, breath=0.0):
    """Standing, phone raised in front of the face to take a photo."""
    return Pose(hip=(0, -38 + breath), lean=3,
                legs=[("ang", -5, -3), ("ang", 6, 4)],
                arms=[("ik", (18.0, -63.0)), ("ik", (20.0, -62.0))],
                look=(1.8, 0.4), blink=blink, phone=True, arm_bend=(1, 1))


def recline_bed(blink=False, breath=0.0):
    """Propped up against a raised hospital bed, legs straight under a blanket."""
    return Pose(hip=(0, -20 + breath * 0.4), lean=-24,
                legs=[("ang", 90, 90), ("ang", 88, 90)],
                arms=[("ik", (12.0, -29.0)), ("ik", (15.0, -28.5))],
                look=(1.2, 0.8), blink=blink, arm_bend=(1, 1), mood="pensive", shadow=False)


class SpriteCache:
    def __init__(self):
        self._c = {}

    def get(self, key, make):
        if key not in self._c:
            self._c[key] = make()
        return self._c[key]


def blink_at(t, period=3.7, offset=0.0):
    return ((t + offset) % period) < 0.12
