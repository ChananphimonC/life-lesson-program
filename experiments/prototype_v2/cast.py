"""Prototype v2b characters: น้องปิ่น and คุณแม่ built on toon.py, drawable at any yaw (front / 3/4 / side).

Design references are the existing characters (shorts/characters/host_mint.json, mom.json):
  ปิ่น  long dark straight hair, big round glasses, mint hoodie, jeans, white sneakers, cheerful.
  แม่   short soft wavy bob, yellow dress (pregnant variant), warm and gentle.
They now differ in more than glasses and clothes: head shape (round vs oval with a longer chin), eyes (round dark
eyes vs almond eyes with whites, lid crease and a beauty mark), brows, nose, mouth, hair silhouette and proportions.

Figure units: head centre at (0, 0), y down, feet on GROUND (per character). th = yaw in radians (0 = front,
positive = turning to face screen-right). Use Canvas.push(flip=True) for a figure facing left.
"""

from __future__ import annotations

import math

import numpy as np

from toon import INK, Canvas, chain, ellipse_pts, lathe, mix, shade, spline, tube, yaw

D2R = math.pi / 180

PIN = dict(
    name="pin", skin=(251, 224, 206), cheek=(246, 160, 152), hair=(62, 42, 38), hair_hi=(112, 80, 72),
    cran=(-8, -6, 100),                       # cranium sphere: centre y, centre z, radius
    jaw=[(10, 98, 84, 0), (35, 95, 82, 4), (55, 88, 76, 9), (70, 77, 66, 13), (82, 60, 52, 16), (91, 38, 34, 18),
         (96, 15, 14, 18), (98, 0, 2, 18)],
    eye=dict(x=37, y=25, w=17.5, h=22, style="round"),
    brow=dict(y=-9, half=15, w=5.0, col=(78, 52, 46)),
    nose_y=50, mouth_y=65, mouth_w=11, blush=(58, 52, 17, 9), ear_y=26,
    glasses=dict(r=31, col=(104, 74, 68)),
    hairline=lambda p: -42 + 22 * min(1, abs(p) / 60) ** 1.6 + (40 * (abs(p) - 60) / 40 if abs(p) > 60 else 0),
    fringe=[(-82, 34), (-62, 2), (-36, -14), (-8, -12), (20, -17), (46, -8), (66, 8), (82, 34)],
    notch=13,
    nose_bump=7,
)

MOM = dict(
    name="mom", skin=(247, 216, 196), cheek=(238, 152, 144), hair=(92, 60, 44), hair_hi=(150, 104, 80),
    cran=(-8, -6, 94),
    jaw=[(10, 92, 80, 0), (36, 89, 77, 4), (58, 81, 70, 9), (75, 67, 58, 14), (88, 49, 43, 18), (98, 29, 27, 21),
         (103, 10, 10, 22), (105, 0, 2, 22)],
    eye=dict(x=35, y=30, w=16, h=11.5, style="almond"),
    brow=dict(y=8, half=16, w=6.0, col=(96, 64, 50)),
    nose_y=56, mouth_y=74, mouth_w=13, blush=(54, 58, 18, 8), ear_y=32,
    glasses=None, mole=(24, 50),
    hairline=lambda p: -40 + 26 * min(1, abs(p) / 60) ** 1.6 + (44 * (abs(p) - 60) / 40 if abs(p) > 60 else 0),
    # side part on her right: a long swoop across the forehead, curtains reaching the jaw
    fringe=[(-90, 74), (-74, 36), (-56, 2), (-34, -22), (-8, -30), (18, -24), (42, -8), (62, 16), (78, 44),
            (90, 76)],
    notch=11,
    nose_bump=6,
)

CHARS = {"pin": PIN, "mom": MOM}


# --- head geometry -----------------------------------------------------------------------------------------------------------

def _lerp_table(tab, y):
    if y < tab[0][0] or y > tab[-1][0]:
        return None
    for (y0, *v0), (y1, *v1) in zip(tab, tab[1:]):
        if y0 <= y <= y1:
            t = (y - y0) / max(1e-6, y1 - y0)
            return tuple(a + (b - a) * t for a, b in zip(v0, v1))
    return tuple(tab[-1][1:])


def _parts(c, y):
    cy, cz, r = c["cran"]
    out = []
    if abs(y - cy) < r:
        ry = math.sqrt(r * r - (y - cy) ** 2)
        out.append((ry, ry, cz))
    j = _lerp_table(c["jaw"], y)
    if j:
        out.append(j)
    return out


def _ys(c):
    cy, _, r = c["cran"]
    return [cy - r + 0.5] + list(range(int(cy - r) + 4, int(c["jaw"][-1][0]), 4)) + [c["jaw"][-1][0]]


def extremes(c, y, th):
    cs, sn = math.cos(th), math.sin(th)
    lo, hi = None, None
    for a, b, z0 in _parts(c, y):
        h = math.sqrt((a * cs) ** 2 + (b * sn) ** 2)
        lo = z0 * sn - h if lo is None else min(lo, z0 * sn - h)
        hi = z0 * sn + h if hi is None else max(hi, z0 * sn + h)
    return lo, hi


def head_outline(c, th):
    right, left = [], []
    s4 = max(0.0, math.sin(th)) ** 6
    for y in _ys(c):
        e = extremes(c, y, th)
        if e[0] is None:
            continue
        bump = c["nose_bump"] * s4 * math.exp(-((y - c["nose_y"] + 2) / 6.5) ** 2)
        bump += 2.5 * s4 * math.exp(-((y - c["mouth_y"] - 4) / 5) ** 2)        # lips
        right.append((e[1] + bump, y))
        left.append((e[0], y))
    return spline(right, n=4) + spline(left[::-1], n=4)


def surf(c, phi_deg, y, th, lift=0.0):
    """Point on the head surface at azimuth phi (deg, 0 = nose direction, + = character's left = screen-right
    in front view) and height y. Returns ((x', y), visibility)."""
    phi = phi_deg * D2R
    best = None
    for a, b, z0 in _parts(c, y):
        p = (a * math.sin(phi), z0 + b * math.cos(phi))
        out = p[0] * math.sin(phi) + p[1] * math.cos(phi)
        if best is None or out > best[0]:
            nx, nz = b * math.sin(phi), a * math.cos(phi)
            k = math.hypot(nx, nz) or 1
            best = (out, p, (nx / k, nz / k))
    if best is None:
        return None, -1
    _, (x, z), (nx, nz) = best
    x, z = x + nx * lift, z + nz * lift
    q = yaw((x, y, z), th)
    return (q[0], y), yaw((nx, 0, nz), th)[2]


def feature(c, x, y, th, lift=0.0):
    """A face feature placed by its front-view x offset; returns ((x', y), foreshortening 0..1)."""
    parts = _parts(c, y)
    a = max(p[0] for p in parts) if parts else 1
    phi = math.degrees(math.asin(max(-0.98, min(0.98, x / a))))
    pos, vis = surf(c, phi, y, th, lift)
    return pos, vis


# --- expressions -------------------------------------------------------------------------------------------------------------

# open: eye height scale, lid: upper lid drop 0..1, gaze: iris offset, brow: (inner raise, outer raise),
# mouth: shape, open: 0..1, blush: 0..1.5, tilt: head tilt degrees, sweat: bool
EXPR = {
    "neutral":    dict(open=1.0, lid=0.0, gaze=(0, 0), brow=(0, 0), mouth="smile", open_=0, blush=0.7, tilt=0),
    "happy":      dict(open=0.0, happy=True, brow=(5, 3), mouth="open_smile", open_=0.8, blush=1.25, tilt=-5),
    "surprised":  dict(open=1.22, lid=0.0, gaze=(0, -1), brow=(11, 9), mouth="o", open_=0.8, blush=0.4, tilt=3,
                       pupil=0.8),
    "worried":    dict(open=1.0, lid=0.12, gaze=(-3, 1), brow=(8, -4), mouth="wavy", open_=0, blush=0.4, tilt=4,
                       sweat=True),
    "determined": dict(open=1.05, lid=0.24, gaze=(3, 0), brow=(-12, 6), mouth="smirk", open_=0, blush=0.8, tilt=-5,
                       sparkle=True),
    "eager":      dict(open=1.12, lid=0.0, gaze=(2, -1), brow=(7, 6), mouth="open_smile", open_=1.0, blush=1.3,
                       tilt=-4, sparkle=True),
    "meh":        dict(open=0.9, lid=0.55, gaze=(4, 1), brow=(-2, 5), mouth="pout", open_=0, blush=0.3, tilt=6),
    "content":    dict(open=0.0, happy=True, brow=(2, 1), mouth="smile", open_=0, blush=1.0, tilt=-3),
}


# --- head drawing ------------------------------------------------------------------------------------------------------------

# Mouth shapes as parameters, so two expressions can be blended frame by frame:
# smile (-1 frown .. 1 big smile), mw (width), skew (right corner up), rnd (0 = D-shape .. 1 = round "o"), wave (wobbly line).
MOUTHP = {
    "smile": dict(smile=0.9, mw=1.0, skew=0.0, rnd=0.0, wave=0.0),
    "open_smile": dict(smile=0.9, mw=1.1, skew=0.0, rnd=0.0, wave=0.0),
    "o": dict(smile=0.0, mw=0.55, skew=0.0, rnd=1.0, wave=0.0),
    "wavy": dict(smile=0.0, mw=0.95, skew=0.0, rnd=0.0, wave=1.0),
    "smirk": dict(smile=0.6, mw=1.0, skew=1.0, rnd=0.0, wave=0.0),
    "pout": dict(smile=-0.8, mw=0.6, skew=0.0, rnd=0.0, wave=0.0),
}
_NUM = ("open", "lid", "blush", "tilt", "open_", "pupil", "wrinkle")
_NUM_DEFAULT = dict(open=1.0, lid=0.0, blush=0.7, tilt=0.0, open_=0.0, pupil=1.0, wrinkle=0.0)


def resolve_expr(x):
    """An expression name or a dict (merged over 'neutral') -> a full parameter dict."""
    base = {**EXPR["neutral"], **(EXPR[x] if isinstance(x, str) else x)}
    base.setdefault("mp", dict(MOUTHP[base["mouth"]]))
    return base


def mix_expr(a, b, t):
    """Blend two expressions (names or dicts) at t in 0..1: numbers and mouth parameters are interpolated,
    on/off flags (happy eyes, sparkle, sweat drop) switch at the halfway point."""
    a, b = resolve_expr(a), resolve_expr(b)
    L = lambda u, v: u + (v - u) * t
    out = {k: L(a.get(k, _NUM_DEFAULT[k]), b.get(k, _NUM_DEFAULT[k])) for k in _NUM}
    for k in ("gaze", "brow"):
        out[k] = tuple(L(u, v) for u, v in zip(a.get(k, (0, 0)), b.get(k, (0, 0))))
    out["mp"] = {k: L(a["mp"][k], b["mp"][k]) for k in a["mp"]}
    src = a if t < 0.5 else b
    for k in ("happy", "sparkle", "sweat", "mouth"):
        if k in src:
            out[k] = src[k]
    out.setdefault("mouth", "smile")
    return out


def _cap_circle(c, th, grow=7):
    cy, cz, r = c["cran"]
    return (cz * math.sin(th), cy), r + grow


def _lock_edge(x0, x1, y, drop, n, seed=0.0, flick=0.0):
    """Lower edge of a hair mass from x0 to x1: n soft locks of uneven length, each ending in a slightly pointed tip
    (one smooth curve, so there are no saw teeth)."""
    pts, step = [(x0, y - drop * 0.25)], (x1 - x0) / n
    for i in range(n):
        a = x0 + step * i
        tip = a + step * (0.5 + 0.12 * math.sin(seed + i * 1.7))
        d = drop * (0.5 + 0.5 * abs(math.sin(seed * 1.3 + i * 2.1)))
        if i in (0, n - 1):
            d += flick
        pts += [(tip - step * 0.17, y + d * 0.72), (tip, y + d), (tip + step * 0.15, y + d * 0.7),
                (a + step * 0.98, y + d * 0.06 - drop * 0.1)]
    pts[-1] = (x1, y - drop * 0.25)
    return spline(pts, n=5)


def _sides(sl, th, wob=0.0):
    s, cs = math.sin(th), math.cos(th)
    right, left = [], []
    for y, a, b, z0 in sl:
        half = math.sqrt((a * cs) ** 2 + (b * s) ** 2)
        w = wob * math.sin(y / 15.0) if y > 0 else 0.0
        right.append((z0 * s + half + w, y))
        left.append((z0 * s - half - w, y))
    return right, left


def _x_at(side, y):
    ys = [p[1] for p in side]
    xs = [p[0] for p in side]
    return float(np.interp(y, ys, xs))


def _strands(cv, right, left, fracs, y0, y1, col, lw=1.5, alpha=200, lean=0.0):
    """Flow lines that follow the hair's own silhouette (a fraction of the way between its two edges)."""
    for k, f in enumerate(fracs):
        ys = [y0 + (y1 - y0) * i / 4 for i in range(5)]
        pts = [(_x_at(left, y) + (_x_at(right, y) - _x_at(left, y)) * f + lean * (y - y0) / max(1, y1 - y0) * (1 - 2 * f), y)
               for y in ys]
        cv.stroke(spline(pts, n=6), col, lw, alpha=alpha)


def hair_back(cv: Canvas, c, th):
    """Hair mass behind the head and body."""
    hc, hs = c["hair"], shade(c["hair"], 0.82)
    if c["name"] == "pin":                      # long straight hair: a darker under-layer, then the front layer with locks
        under = [(-118, 8, 8, -8), (-108, 54, 54, -8), (-92, 82, 82, -10), (-50, 112, 110, -12), (10, 110, 100, -16),
                 (60, 100, 82, -30), (110, 84, 58, -44), (170, 74, 40, -54), (230, 68, 30, -58), (268, 60, 22, -58)]
        r, l = _sides(under, th)
        wd = abs(r[-1][0] - l[-1][0])
        edge = _lock_edge(min(r[-1][0], l[-1][0]), max(r[-1][0], l[-1][0]), 268, 16, max(2, min(4, int(wd / 24))), seed=0.6)
        cv.fill(spline(r, n=5) + edge[::-1] + spline(l[::-1], n=5), shade(hc, 0.68), lw=3.0)
        sl = [(-118, 8, 8, -6), (-108, 52, 52, -6), (-92, 78, 78, -6), (-50, 108, 106, -8), (10, 106, 96, -12),
              (60, 96, 78, -24), (110, 80, 54, -38), (170, 70, 36, -46), (230, 64, 26, -50), (252, 58, 22, -50)]
        r, l = _sides(sl, th)
        lo, hi = min(r[-1][0], l[-1][0]), max(r[-1][0], l[-1][0])
        edge = _lock_edge(lo, hi, 252, 16, max(2, min(4, int((hi - lo) / 24))), seed=2.2)
        cv.fill(spline(r, n=5) + edge[::-1] + spline(l[::-1], n=5), hc, lw=3.0, shade_col=hs, depth=9)
        _strands(cv, r, l, (0.2, 0.42, 0.64, 0.84), 50, 236, shade(hc, 0.7), lw=1.6, lean=4)
        gl = [(_x_at(l, y) + (_x_at(r, y) - _x_at(l, y)) * 0.3, y) for y in (24, 80, 140, 200)]
        cv.fill(tube(spline(gl, n=6), lambda t: 2 + 7 * math.sin(math.pi * t)), c["hair_hi"], ink=None, alpha=105)
    else:                                         # soft wavy bob: close to the skull, swelling at the cheeks, tips flick out
        sl = [(-112, 8, 8, -6), (-104, 48, 48, -6), (-90, 72, 70, -6), (-50, 102, 100, -8), (0, 104, 96, -10),
              (40, 108, 92, -14), (70, 116, 86, -20), (92, 118, 72, -26), (102, 112, 58, -30)]
        r, l = _sides(sl, th, wob=5)
        lo, hi = l[-1][0], r[-1][0]
        edge = _lock_edge(lo, hi, 102, 8, 5, seed=1.1, flick=3)
        cv.fill(spline(r, n=5) + edge[::-1] + spline(l[::-1], n=5), hc, lw=3.2, shade_col=hs, depth=10)
        _strands(cv, r, l, (0.14, 0.3, 0.7, 0.86), -40, 90, shade(hc, 0.74), lw=1.5, alpha=190, lean=-3)
        gl = [(_x_at(l, y) + (_x_at(r, y) - _x_at(l, y)) * 0.74, y) for y in (-20, 20, 60, 90)]
        cv.fill(tube(spline(gl, n=6), lambda t: 1.5 + 5 * math.sin(math.pi * t)), c["hair_hi"], ink=None, alpha=85)


def _face_region(c, th):
    hl = c["hairline"]
    top = []
    near_phi = -112 if c["name"] == "pin" else -86     # ปิ่น's hair is tucked behind the ear; แม่'s bob covers it
    for phi in [near_phi] + list(range(near_phi + 8 - near_phi % 8, 101, 8)):
        p, vis = surf(c, phi, hl(phi), th)
        if p is None:
            continue
        if vis < 0.02:                            # behind the far cheek: follow the silhouette instead
            lo, hi = extremes(c, p[1], th)
            p = (hi if phi > 0 else lo, p[1])
        top.append(p)
    chin_y = c["jaw"][-1][0]
    # far side = the silhouette (the cheek turning away); near side = the jaw-to-ear line on the surface
    far, near = [], []
    y0 = hl(100)
    ys = [y0 + (chin_y - y0) * i / 12 for i in range(13)]
    for y in ys:
        lo, hi = extremes(c, y, th)
        if lo is None:
            continue
        far.append((hi, y))
        p, vis = surf(c, near_phi, y, th)
        near.append((lo, y) if (p is None or vis < 0.02 or th < 0.05) else (max(lo, p[0]), y))
    far, near = spline(far, n=4), spline(near, n=4)
    region = top + far + near[::-1]
    jaw_line = far + near[::-1]
    return region, jaw_line


def _eye(cv, c, x, y, f, e, side, skin):
    """One eye at (x, y) with horizontal foreshortening f. side: -1 = character's right (screen-left in front view)."""
    E = c["eye"]
    w, h = E["w"] * (0.35 + 0.65 * f), E["h"]
    gx, gy = e.get("gaze", (0, 0))
    gx *= f
    if e.get("happy"):
        arc = [(x - w * 1.05, y + 3), (x, y - h * 0.55), (x + w * 1.05, y + 3)]
        cv.taper(arc, 4.2, 4.2, INK, wmid=5.6)
        return
    op = e.get("open", 1.0)
    if E["style"] == "round":
        hh = h * op
        cv.ellipse(x, y, w, hh, (64, 42, 38))
        cv.ellipse(x + gx * 0.6, y + hh * 0.28 + gy, w * 0.72, hh * 0.52, (150, 102, 84))
        cv.ellipse(x + gx, y + gy - 1, w * 0.42 * e.get("pupil", 1), hh * 0.5 * e.get("pupil", 1), (40, 26, 26))
        cv.ellipse(x + w * 0.35 + gx * 0.5, y - hh * 0.42, w * 0.34, hh * 0.24, (255, 255, 255))
        cv.ellipse(x - w * 0.38 + gx * 0.5, y + hh * 0.36, w * 0.17, hh * 0.12, (255, 255, 255))
        if e.get("sparkle"):
            cv.ellipse(x + w * 0.05, y + hh * 0.05, w * 0.12, hh * 0.1, (255, 255, 255))
        top = [(x - w * 1.12, y - hh * 0.32), (x - w * 0.5, y - hh * 0.98), (x + w * 0.5, y - hh * 0.98),
               (x + w * 1.12, y - hh * 0.36)]
        lid = e.get("lid", 0)
        if lid > 0:
            ly = y - hh + hh * (2 * lid if lid <= 0.5 else 1 + 0.9 * (lid - 0.5))
            cv.fill([(x - w * 1.3, y - hh * 1.2), (x + w * 1.3, y - hh * 1.2), (x + w * 1.3, ly), (x - w * 1.3, ly)],
                    skin, ink=None)
            if lid > 0.5:                              # lower lid rises to meet the upper one
                low = y + hh * (1.0 - 1.1 * (lid - 0.5))
                cv.fill([(x - w * 1.3, low), (x + w * 1.3, low), (x + w * 1.3, y + hh * 1.3), (x - w * 1.3, y + hh * 1.3)],
                        skin, ink=None)
                if e.get("_blush"):
                    e["_blush"]()
            top = [(x - w * 1.12, ly + 3), (x, ly - 1 + 6 * lid ** 3), (x + w * 1.12, ly + 4)]
        cv.taper(top, 3.0, 3.0, INK, wmid=5.2)
        o = side                               # outer corner direction in screen space (front view)
        ox = x + o * w * 1.05
        cv.taper([(ox, top[-1 if o > 0 else 0][1] + 1), (ox + o * 6, top[-1 if o > 0 else 0][1] - 5)], 3.4, 1.2, INK)
    else:                                      # almond: whites, round iris, crease, longer outer lash
        hh = h * op
        lid = e.get("lid", 0)
        upper = [(x - w * 1.15, y + 1), (x - w * 0.35, y - hh * 1.05), (x + w * 0.5, y - hh * 0.95),
                 (x + w * 1.15, y - 1)]
        lower = [(x + w * 1.15, y - 1), (x + w * 0.3, y + hh * 0.9), (x - w * 0.5, y + hh * 0.85),
                 (x - w * 1.15, y + 1)]
        outline = spline(upper, n=8) + spline(lower, n=8)[1:]
        cv.fill(outline, (255, 252, 248), ink=None)
        ir = min(w * 0.62, hh * 1.0) + 2
        cv.ellipse(x + gx, y + gy + 1, ir * 0.92, ir, (106, 70, 52))
        cv.ellipse(x + gx, y + gy + 1, ir * 0.48 * e.get("pupil", 1), ir * 0.52 * e.get("pupil", 1), (44, 28, 24))
        cv.ellipse(x + gx + ir * 0.35, y + gy - ir * 0.35, ir * 0.26, ir * 0.24, (255, 255, 255))
        if e.get("sparkle"):
            cv.ellipse(x + gx - ir * 0.3, y + gy + ir * 0.3, ir * 0.12, ir * 0.12, (255, 255, 255))
        # cover the iris outside the almond with skin (iris can exceed the opening)
        top_y, bot_y = y + gy - ir - 3, y + gy + ir + 4     # masks only as large as the iris, so the blush survives
        mask_top = [(x - w * 1.3, top_y), (x + w * 1.3, top_y)] + spline(upper, n=8)[::-1]
        low_lid = None
        if lid > 0:
            ly = y - hh + hh * (2 * lid if lid <= 0.5 else 1 + 0.9 * (lid - 0.5))
            if lid > 0.5:
                low_lid = y + hh * (1.0 - 1.1 * (lid - 0.5))
            mask_top = [(x - w * 1.5, min(top_y, y - hh * 1.6)), (x + w * 1.5, min(top_y, y - hh * 1.6)), (x + w * 1.5, ly), (x - w * 1.5, ly)]
            upper = [(x - w * 1.15, ly + 3), (x, ly - 1), (x + w * 1.15, ly + 3)]
        cv.fill(mask_top, skin, ink=None)
        cv.fill([(x + w * 1.3, bot_y), (x - w * 1.3, bot_y)] + spline(lower, n=8)[::-1], skin, ink=None)
        if low_lid is not None:
            cv.fill([(x - w * 1.3, low_lid), (x + w * 1.3, low_lid), (x + w * 1.3, y + hh * 1.5), (x - w * 1.3, y + hh * 1.5)],
                    skin, ink=None)
        cv.taper(upper, 2.6, 3.0, INK, wmid=5.0)
        lo_line = spline(lower, n=6)
        if low_lid is None:
            cv.stroke(lo_line[len(lo_line) // 4: len(lo_line) * 3 // 4], mix(INK, skin, 0.55), 1.5)
        up_line = spline(upper, n=6)                 # lid crease follows the lid curve, shorter than it
        crease = [(px, py - 6) for px, py in up_line[len(up_line) // 5: len(up_line) * 4 // 5]]
        cv.stroke(crease, mix(INK, skin, 0.42), 1.5)
        o = side
        end = upper[-1] if o > 0 else upper[0]
        cv.taper([end, (end[0] + o * 7, end[1] - 4)], 3.2, 0.8, INK)


def _brow(cv, c, x, y, f, e, side):
    B = c["brow"]
    inner, outer = e.get("brow", (0, 0))
    hw = B["half"] * (0.35 + 0.65 * f)
    s = side                                    # +1 means the outer end is screen-right
    dip = 2.0 * e.get("blink", 0.0)
    pi = (x - s * hw, y - inner + dip)
    po = (x + s * hw, y - outer + dip)
    mid = (x + s * hw * 0.1, (pi[1] + po[1]) / 2 - 4)
    cv.taper([pi, mid, po], B["w"], B["w"] * 0.55, B["col"], wmid=B["w"] * 1.05)


def _mouth(cv, c, x, y, f, e, talk):
    mp = e.get("mp") or MOUTHP[e.get("mouth", "smile")]
    w = c["mouth_w"] * (0.4 + 0.6 * f) * mp["mw"]
    dark, tongue = (126, 52, 58), (238, 130, 134)
    sm, sk, rnd = mp["smile"], mp["skew"], mp["rnd"]
    op = e.get("open_", 0.0)
    if talk is not None and talk > 0.04:
        op = max(op, 0.15 + 0.85 * talk)
    corner_l, corner_r = y - sm * 3.4 + sk * 2.2, y - sm * 3.4 - sk * 3.6
    mid = y + sm * 3.9
    if op < 0.07:                                 # closed: one expressive stroke through corners and middle
        wv = 2.4 * mp["wave"]
        pts = [(x - w, corner_l), (x - w * 0.5, corner_l + (mid - corner_l) * 0.75 + wv), (x, mid),
               (x + w * 0.5, corner_r + (mid - corner_r) * 0.75 - wv), (x + w, corner_r)]
        cv.taper(spline(pts, n=6), 2.6, 2.4, INK, wmid=3.4)
        if c["name"] == "mom" and rnd < 0.5:
            cv.stroke(spline([(x - w * 0.35, y + 7), (x, y + 8.2), (x + w * 0.35, y + 7)], n=4), mix(INK, c["skin"], 0.5), 1.5)
        return
    cw = 1 - 0.45 * rnd
    cy_round = y + 3
    ly = corner_l * (1 - rnd) + cy_round * rnd
    ry = corner_r * (1 - rnd) + cy_round * rnd
    top_y = y - 1.0 - rnd * (5 + 3 * op) - sm * 0.0
    bot_y = (y + (4 + 11 * op) * 0.8) * (1 - rnd) + (y + 10 + 4 * op) * rnd
    tx, bx = w * (0.55 - 0.22 * rnd), w * (0.55 - 0.15 * rnd)
    shape = spline([(x - w * cw * 1.1, ly), (x - tx, top_y), (x + tx, top_y), (x + w * cw * 1.1, ry),
                    (x + bx, bot_y), (x - bx, bot_y)], closed=True, n=6)
    cv.fill(shape, dark, lw=2.6)
    hh = bot_y - y
    if hh > 7:
        cv.fill(spline([(x - w * 0.5, bot_y - 1), (x, bot_y - hh * 0.38), (x + w * 0.5, bot_y - 1),
                        (x, bot_y + 0.5)], closed=True, n=6), tongue, ink=None)
    if c["name"] == "mom" and hh > 6 and rnd < 0.5:
        cv.fill(spline([(x - w * 0.8, y - 2.2), (x, y - 0.5), (x + w * 0.8, y - 2.2), (x, y + 2.6)], closed=True, n=5),
                (255, 252, 248), ink=None)


def _blush(cv, c, th, e, skin):
    """Cheek blush; the one on the far side is kept inside the face outline (it used to poke out at 3/4 turns)."""
    bx, by, brx, bry = c["blush"]
    lo, hi = extremes(c, by, th)
    for side in (-1, 1):
        p, f = feature(c, bx * side, by, th)
        if p is None or f <= 0.15:
            continue
        rx = brx * (0.35 + 0.65 * f)
        x = min(max(p[0], lo + rx + 3), hi - rx - 3)
        if abs(x - p[0]) > rx * 0.8:
            continue
        cv.ellipse(x, p[1], rx, bry, mix(skin, c["cheek"], 0.55 * e.get("blush", 0.7)))


def head(cv: Canvas, c, th, expr="neutral", talk=None, back=True, blink=0.0):
    """Draw the whole head with its centre at local (0, 0). back=False skips the hair mass behind (drawn earlier).
    expr: a name from EXPR or a parameter dict (see mix_expr); blink 0..1 closes the lids."""
    e = dict(resolve_expr(expr))
    e["lid"] = max(e.get("lid", 0.0), blink)
    e["blink"] = blink
    skin = c["skin"]
    skin_sh = mix(skin, (226, 170, 160), 0.45)
    if back:
        hair_back(cv, c, th)
    # skull + jaw silhouette
    cv.fill(head_outline(c, th), skin, lw=3.4)
    # hair cap over the cranium, then the face region on top of it
    (hx, hy), hr = _cap_circle(c, th, grow=7)
    cv.fill(ellipse_pts(hx, hy, hr, hr * 1.0, n=64), c["hair"], ink=None, shade_col=shade(c["hair"], 0.82), depth=8)
    region, jaw = _face_region(c, th)
    cv.fill(region, skin, ink=None)
    cv.stroke(jaw, INK, 3.4)
    # ears (ปิ่น only; แม่'s bob covers them)
    if c["name"] == "pin":
        for side in (-1, 1):
            p, vis = surf(c, 103 * side, c["ear_y"], th)
            if p is None or vis < -0.35:
                continue
            ew = 6 + 8 * max(0, abs(math.sin(th)) if side * th < 0 else 0.3 * (1 - abs(math.sin(th))))
            ex = p[0] + (-ew * 0.3 if p[0] < 0 else ew * 0.3)
            cv.ellipse(ex, p[1], ew, 15, skin, ink=INK, lw=3.0)
            cv.stroke(spline([(ex + (3 if p[0] < 0 else -3), p[1] - 7), (ex, p[1]), (ex + (2 if p[0] < 0 else -2), p[1] + 7)], n=4),
                      skin_sh, 2.4)
    _blush(cv, c, th, e, skin)
    e["_blush"] = lambda: _blush(cv, c, th, e, skin)          # an eye closing over the cheek redraws it
    if c.get("mole"):
        p, f = feature(c, -c["mole"][0], c["mole"][1], th)
        if p is not None and f > 0.2:
            cv.ellipse(p[0], p[1], 1.7, 1.7, (120, 80, 70))
    # nose and mouth
    p, f = feature(c, 0, c["nose_y"], th)
    sn = math.sin(th)
    if p is not None:
        if sn < 0.85:
            if c["name"] == "pin":
                cv.taper([(p[0] - 2 + 3 * sn, p[1] - 2), (p[0] + 1.5 * sn, p[1] + 2), (p[0] + 3 + 3 * sn, p[1])],
                         2.0, 1.4, mix(INK, skin, 0.25))
            else:
                cv.taper([(p[0] + 1 + 3 * sn, p[1] - 6), (p[0] + 3 + 4 * sn, p[1]), (p[0] + 4 * sn, p[1] + 2)],
                         1.0, 2.0, mix(INK, skin, 0.4))
    if e.get("wrinkle", 0) > 0.05 and p is not None:      # scrunched nose bridge (smell reaction)
        for dx in (-5, 5):
            cv.stroke(spline([(p[0] + dx - 3, p[1] - 15), (p[0] + dx, p[1] - 12.5), (p[0] + dx + 3, p[1] - 15)], n=4),
                      mix(INK, skin, 0.35), 1.7, alpha=int(170 * min(1, e["wrinkle"])))
    p, f = feature(c, 0, c["mouth_y"], th)
    if p is not None:
        _mouth(cv, c, p[0] - 3 * max(0, sn - 0.7), p[1], max(f, 0.35), e, talk)
    # fringe (over the forehead, under the eyes/brows so a raised brow can still read)
    _fringe(cv, c, th)
    E = c["eye"]
    eyes = {}
    for side in (-1, 1):
        p, f = eye_pos(c, side, th)
        if p is None:
            continue
        eyes[side] = (p, f)
        _eye(cv, c, p[0], p[1], f, e, side, skin)
        pb, fb = feature(c, E["x"] * side, c["brow"]["y"], th)
        if pb is not None:
            _brow(cv, c, p[0], pb[1], fb, e, side)            # brow follows the (possibly clamped) eye
    if c.get("glasses"):
        _glasses(cv, c, th, eyes)
    if e.get("sweat"):
        (hx, hy), hr = _cap_circle(c, th)
        sx = hx + hr * 0.72
        cv.fill(spline([(sx, -10), (sx + 7, 8), (sx, 14), (sx - 7, 8)], closed=True, n=6), (190, 226, 246), lw=2.4)


def _fringe(cv, c, th):
    cy, cz, r = c["cran"]
    hl = c["hairline"]
    top, bottom = [], []
    pts = c["fringe"]
    for phi, yb in pts:
        q, vq = surf(c, phi, yb, th, lift=3)
        if q is None or vq < 0.05:          # anchors turned away from us are simply not drawn (the cap shows there)
            continue
        p, _ = surf(c, phi, hl(phi) - 16, th, lift=4)
        top.append(p)
        bottom.append(q)
    if len(bottom) < 2:
        return
    # lower edge: pointed lock tips joined by rounded notches, so the fringe reads as hair, not a scalloped hem
    notch = c.get("notch", 9)
    segs = []
    for (x0, y0), (x1, y1) in zip(bottom, bottom[1:]):
        segs.append([(x0, y0), ((x0 + x1) / 2, (y0 + y1) / 2 - notch), (x1, y1)])
    lower = chain(*segs, n=6)
    shape = spline(top, n=5) + lower[::-1]
    cv.fill(shape, c["hair"], ink=None)
    cv.stroke(lower, INK, 3.2)
    # a few strands and a soft sheen
    for i in range(1, len(bottom) - 1, 2):
        a, b = top[min(i, len(top) - 1)], bottom[i]
        cv.stroke(spline([a, ((a[0] + b[0]) / 2 + 2, (a[1] + b[1]) / 2), (b[0], b[1] - 6)], n=5),
                  shade(c["hair"], 0.72), 1.6)
    (hx, hy), hr = _cap_circle(c, th)
    sheen = [(hx - hr * 0.55, hy - hr * 0.55), (hx - hr * 0.05, hy - hr * 0.78), (hx + hr * 0.5, hy - hr * 0.6)]
    cv.taper(sheen, 2, 2, c["hair_hi"], wmid=7)


def eye_pos(c, side, th):
    """Eye centre and foreshortening; an eye turning away is kept inside the cheek line (dropped only near profile)."""
    E = c["eye"]
    p, f = feature(c, E["x"] * side, E["y"], th, lift=-2)
    if p is None or f < 0.08:
        return None, f
    lo, hi = extremes(c, E["y"], th)
    ew = E["w"] * (0.35 + 0.65 * f) * 1.25
    if p[0] + ew > hi - 2 or p[0] - ew < lo + 2:
        if f < 0.3:
            return None, f
        p = (max(lo + ew + 2, min(hi - ew - 2, p[0])), p[1])
    return p, f


def _glasses(cv, c, th, eyes):
    G = c["glasses"]
    col, tint = G["col"], (214, 234, 246)
    s = math.sin(th)
    lens = []
    for side in (-1, 1):
        p, f = eyes.get(side, (None, 0))
        if p is None or f < 0.05:
            lens.append(None)
            continue
        rx = G["r"] * (0.2 + 0.8 * f ** 1.15)         # a lens seen edge-on narrows to a slim ellipse
        ry = G["r"] * 0.94
        cx, cy = p[0] + 3.0 * s, p[1] + 1             # the lens sits just in front of the eye
        cv.ellipse(cx, cy, rx, ry, tint, alpha=46)
        cv.stroke(ellipse_pts(cx, cy, rx, ry, n=40), col, 3.0, closed=True)
        cv.stroke(ellipse_pts(cx, cy, rx * 0.86, ry * 0.86, n=40, a0=200, a1=250), (255, 255, 255), 2.0, alpha=170)
        lens.append((cx, cy, rx, ry))
    if lens[0] and lens[1]:
        (x0, y0, r0, _), (x1, y1, r1, _) = lens
        cv.stroke(spline([(x0 + r0, y0 - 4), ((x0 + x1) / 2, y0 - 8), (x1 - r1, y1 - 4)], n=4), col, 3.0)
    elif abs(s) > 0.3:                              # profile: a short bridge and nose pad toward the nose
        L = lens[0] or lens[1]
        if L:
            cx, cy, rx, ry = L
            dn = 1 if s > 0 else -1
            cv.ellipse(cx + dn * (rx - 1.2), cy + ry * 0.34, 2.0, 3.2, col)
    if abs(s) > 0.2:                                # temple arm: hinge at the lens, along the temple, hooked behind the ear
        near = 0 if s > 0 else 1
        L = lens[near]
        ear, vis = surf(c, -103 if s > 0 else 103, c["ear_y"] - 4, th)
        if L and ear is not None:
            cx, cy, rx, ry = L
            d = -1 if s > 0 else 1                  # screen direction toward the back of the head
            hinge = (cx + d * rx * 0.94, cy - ry * 0.36)
            above = (ear[0] + 1, ear[1] - 8)
            hook = (ear[0] + d * 8, ear[1] + 5)
            cv.stroke(spline([hinge, ((hinge[0] + above[0]) / 2, (hinge[1] + above[1]) / 2 + 0.5), above,
                              (above[0] + d * 5, above[1] + 2), hook], n=6), col, 2.8)



# --- quick test: heads in three views + expressions --------------------------------------------------------------------------

if __name__ == "__main__":
    from pathlib import Path
    out = Path(__file__).resolve().parent / "out"
    cv = Canvas(1500, 760, ss=3, bg=(250, 246, 238, 255))
    for row, c in enumerate((PIN, MOM)):
        for i, th in enumerate((0, 35 * D2R, 82 * D2R)):
            cv.push(130 + i * 250, 170 + row * 370, scale=1.05)
            head(cv, c, th, "neutral")
            cv.pop()
        for i, ex in enumerate(("happy", "surprised", "worried", "determined" if c is PIN else "meh")):
            cv.push(860 + i * 165, 170 + row * 370, scale=0.7, rot=EXPR[ex].get("tilt", 0), pivot=(0, 90))
            head(cv, c, 18 * D2R, ex)
            cv.pop()
    cv.result().save(out / "v2b_heads.png")
    print("ok")
