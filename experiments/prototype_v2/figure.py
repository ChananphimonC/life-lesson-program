"""Prototype v2b bodies, hands, poses and held props for cast.py heads.

Arms are posed by 3D joints (shoulder -> elbow -> wrist, constant segment lengths) and projected with the same yaw
as the head, so the elbow bends where it should in every view. Each limb is one tapered outline (no circle chains),
stroked on its sides and end only, so it grows out of the shoulder instead of looking bolted on. Hands are single
silhouettes with a thumb; their wrist end is tucked under the cuff (hoodie) or merges with the bare arm (dress).
"""

from __future__ import annotations

import math

import numpy as np

from cast import CHARS, D2R, EXPR, hair_back, head, resolve_expr
from toon import INK, Canvas, chain, ellipse_pts, mix, shade, spline, tube, yaw

# --- bodies --------------------------------------------------------------------------------------------------------------------

BODY = {
    "pin": dict(
        top=(143, 214, 190), top_dark=(112, 182, 160), cuff=(214, 240, 228), bottom=(91, 123, 168),
        shoe=(246, 243, 236), sole=(196, 190, 184), ground=336,
        torso=[(108, 22, 18, -4), (116, 50, 30, -4), (126, 60, 34, -4), (150, 61, 36, -2), (185, 58, 35, 0),
               (215, 60, 36, 0), (236, 62, 37, 0)],
        shoulder=(56, 128, -2), upper=58, fore=54, arm_w=(26, 22, 18.5), sleeve="long",
        hip=(23, 230), knee_y=276, ankle_y=318, leg_w=(42, 32), skirt=None),
    "mom": dict(
        top=(242, 197, 107), top_dark=(222, 170, 84), cuff=(255, 246, 220), bottom=(242, 197, 107),
        shoe=(150, 96, 70), sole=(110, 70, 52), ground=350,
        torso=[(106, 20, 16, -4), (114, 46, 28, -4), (124, 55, 32, -4), (150, 54, 34, -2), (178, 50, 32, 0),
               (220, 62, 38, 0), (260, 72, 44, 0), (292, 80, 48, 0)],
        shoulder=(52, 126, -2), upper=58, fore=54, arm_w=(22, 18, 15), sleeve="puff",
        hip=(18, 290), knee_y=314, ankle_y=334, leg_w=(21, 17), skirt=True),
}


def torso_slices(cid, pregnant=False):
    sl = BODY[cid]["torso"]
    if not pregnant:
        return sl
    # resample densely and add a round bump under the empire seam; below it the dress hangs from the belly
    out = []
    y = sl[0][0]
    while y <= sl[-1][0]:
        a, b, z0 = slice_at(sl, y)
        g = math.exp(-((y - 206) / 36) ** 2)
        gw = math.exp(-((y - 232) / 40) ** 2)
        hang = max(g, 0.5) if y > 206 else g
        out.append((y, a + 14 * gw, b + 20 * max(g, 0.9 * hang), z0 + 18 * hang))
        y += 6
    return out


def slice_at(sl, y):
    if y <= sl[0][0]:
        return sl[0][1:]
    for (y0, *v0), (y1, *v1) in zip(sl, sl[1:]):
        if y0 <= y <= y1:
            t = (y - y0) / max(1e-6, y1 - y0)
            return tuple(a + (b - a) * t for a, b in zip(v0, v1))
    return sl[-1][1:]


def on_body(sl, phi_deg, y, th, lift=0.0):
    a, b, z0 = slice_at(sl, y)
    phi = phi_deg * D2R
    x, z = (a + lift) * math.sin(phi), z0 + (b + lift) * math.cos(phi)
    q = yaw((x, y, z), th)
    nx, nz = b * math.sin(phi), a * math.cos(phi)
    k = math.hypot(nx, nz) or 1
    return (q[0], y), yaw((nx / k, 0, nz / k), th)[2]


def body_line(cv, sl, th, y_of_phi, phis, col, lw, min_vis=0.05):
    pts = []
    for ph in phis:
        p, v = on_body(sl, ph, y_of_phi(ph), th, lift=1)
        if v > min_vis:
            pts.append(p)
        elif pts:
            break
    if len(pts) > 1:
        cv.stroke(spline(pts, n=5), col, lw)
    return pts


def lathe_band(sl, y0, y1, th):
    """Silhouette between two heights (for hems and bands)."""
    from toon import lathe
    ys = [y0 + (y1 - y0) * i / 4 for i in range(5)]
    return lathe([(y, *slice_at(sl, y)) for y in ys], th, n=3)


# --- limbs and hands -----------------------------------------------------------------------------------------------------------

def limb(cv, pts, widths, col, shade_col=None, ink=INK, lw=3.0, stroke_start=False):
    """One tapered limb through pts. widths: (start, middle, end). The start cap is not inked, so it merges."""
    w0, wm, w1 = widths
    f = lambda t: (w0 + (wm - w0) * t * 2) if t < 0.5 else (wm + (w1 - wm) * (t - 0.5) * 2)
    outline = tube(pts, f, n=8)
    cv.fill(outline, col, ink=None, shade_col=shade_col, depth=5)
    if ink:
        k = 6                                      # tube() appends a 6-point start cap at the end of the list
        cv.stroke(outline if stroke_start else outline[:-k + 1], ink, lw, closed=stroke_start)
    return outline


# hand templates: wrist at (0, 0), +y = along the hand, thumb on +x. Units = figure units (hand ~ 26 long).
HANDS = {
    "relaxed": dict(
        outline=[(-8, -2), (-9.5, 8), (-9.5, 17), (-6, 24.5), (0, 26.5), (6, 24), (8.5, 17), (9, 10),
                 (13, 13), (15, 9), (12, 3), (8, -2)],
        lines=[[(-3, 15), (-3.5, 22)], [(2, 16), (2, 23)]]),
    "cup": dict(                                # palm turned up under a bowl: flat mitten, fingertips curled a little
        outline=[(-8, -2), (-9.5, 9), (-9.5, 18), (-6, 24), (0, 26.5), (6.5, 24.5), (9, 19.5), (9, 13), (12.5, 11),
                 (14, 6.5), (11, 2.5), (8, -2)],
        lines=[[(-3.5, 17), (-3, 23)], [(2, 17.5), (2.5, 23.5)]]),
    "grip": dict(                               # fist around a handle (the handle passes at y ~ 14)
        outline=[(-9, -2), (-11, 7), (-11, 17), (-7, 23), (0, 24), (8, 22), (11, 15), (10, 7), (8, -2)],
        lines=[[(-6, 12), (5, 12)], [(-6, 17.5), (5, 17.5)]],
        thumb=[(4, 4), (12, 7), (13, 12), (9, 13), (3, 10)]),
    "open": dict(                               # palm out, fingers together and slightly fanned ("no thanks")
        outline=[(-9, -2), (-11.5, 9), (-12.5, 16), (-13, 25), (-11, 28.5), (-8.5, 27), (-8, 18.5), (-7.5, 32),
                 (-5, 35), (-2.6, 33), (-2.4, 19), (-1.6, 35.5), (1.2, 37.5), (3.6, 35.5), (3.2, 19), (4.6, 33.5),
                 (7.2, 35), (9.2, 32.5), (8.6, 17), (10.5, 12), (15.5, 10.5), (18, 7.5), (16, 4), (10, 3.5),
                 (8.5, -2)],
        lines=[]),
    "point": dict(
        outline=[(-9, -2), (-11, 8), (-10, 18), (-5, 22), (-3, 34), (0, 37), (3, 34), (3.5, 22), (9, 19),
                 (11, 12), (14, 10), (13, 4), (8, -2)],
        lines=[[(3.5, 19), (8.5, 17.5)]]),
}


def hand(cv, wrist, angle_deg, kind, skin, mirror=False, scale=1.0, part="all"):
    """Draw a hand at `wrist` pointing along angle_deg (0 = straight down). part: 'all' | 'base' | 'thumb'."""
    H = HANDS[kind]
    cv.push(wrist[0], wrist[1], rot=angle_deg, scale=scale, flip=mirror)
    if part in ("all", "base"):
        o = spline(H["outline"], n=5)
        cv.fill(o + [o[0]], skin, ink=None, shade_col=mix(skin, (226, 168, 158), 0.5), depth=2.2)
        cv.stroke(o, INK, 2.8)
        for ln in H["lines"]:
            cv.stroke(ln, mix(INK, skin, 0.35), 1.6)
    if part in ("all", "thumb") and H.get("thumb"):
        t = spline(H["thumb"], closed=True, n=5)
        cv.fill(t, skin, lw=2.6)
    cv.pop()


# --- props held in the hands ---------------------------------------------------------------------------------------------------

def bowl(cv, x, y, w=44, tilt=0.42, food=True):
    """ตำผลไม้ bowl seen slightly from above: rim ellipse, body, colourful fruit pieces."""
    rim_h = w * tilt * 0.5
    body = chain([(-w, 0), (-w * 0.88, w * 0.42), (-w * 0.45, w * 0.7), (0, w * 0.75)],
                 [(0, w * 0.75), (w * 0.45, w * 0.7), (w * 0.88, w * 0.42), (w, 0)], n=6)
    cv.push(x, y)
    cv.fill(body + ellipse_pts(0, 0, w, rim_h, n=40, a0=0, a1=180)[::-1], (236, 244, 248), shade_col=(196, 210, 220), depth=6)
    cv.stroke(spline([(-w * 0.9, w * 0.32), (0, w * 0.46), (w * 0.9, w * 0.32)], n=5), (120, 170, 200), 3.2)
    cv.ellipse(0, 0, w, rim_h, (250, 252, 252), ink=INK, lw=3.0)
    if food:
        cv.ellipse(0, 1, w * 0.86, rim_h * 0.72, (236, 196, 120))
        pieces = [(-0.5, 0.0, (250, 214, 90)), (-0.15, -0.25, (232, 92, 84)), (0.25, 0.05, (128, 190, 96)),
                  (0.55, -0.15, (250, 168, 80)), (-0.3, 0.35, (244, 236, 200)), (0.1, 0.4, (232, 92, 84)),
                  (0.45, 0.35, (250, 214, 90)), (-0.62, -0.28, (128, 190, 96))]
        for i, (px, py, col) in enumerate(pieces):
            r = w * (0.17 if i % 3 else 0.2)
            cv.fill(spline([(px * w - r, py * rim_h - r * 0.4), (px * w + r * 0.2, py * rim_h - r * 0.8),
                            (px * w + r, py * rim_h - r * 0.1), (px * w, py * rim_h + r * 0.55)], closed=True, n=4),
                    col, lw=2.0)
        cv.ellipse(w * 0.62, -rim_h * 0.5, 4, 2.6, (210, 60, 54))        # a chilli flake
    cv.pop()


def spoon(cv, a, b, col=(214, 220, 226)):
    """Spoon from handle end a to bowl end b."""
    cv.stroke([a, b], INK, 7.0)
    cv.stroke([a, b], col, 4.2)
    ang = math.atan2(b[1] - a[1], b[0] - a[0])
    cv.ellipse(b[0] + math.cos(ang) * 6, b[1] + math.sin(ang) * 6, 10, 6.5, col, ink=INK, lw=2.6,
               rot=math.degrees(ang))


def magnifier(cv, hand_pt, lens, r=24):
    """Handle from the fist to the rim, then the ring and glass."""
    d = math.hypot(lens[0] - hand_pt[0], lens[1] - hand_pt[1]) or 1
    ux, uy = (lens[0] - hand_pt[0]) / d, (lens[1] - hand_pt[1]) / d
    edge = (lens[0] - ux * (r + 1), lens[1] - uy * (r + 1))
    cv.stroke([hand_pt, edge], INK, 10)
    cv.stroke([hand_pt, edge], (150, 98, 66), 6.5)
    cv.stroke([(edge[0] - ux * 7, edge[1] - uy * 7), edge], (232, 186, 92), 9.5)          # collar where handle meets ring
    cv.ellipse(lens[0], lens[1], r, r, (226, 242, 252), ink=None, alpha=96)
    cv.stroke(ellipse_pts(lens[0], lens[1], r, r, n=48), INK, 9, closed=True)
    cv.stroke(ellipse_pts(lens[0], lens[1], r, r, n=48), (232, 186, 92), 5, closed=True)
    cv.stroke([(lens[0] - r * 0.55, lens[1] - r * 0.1), (lens[0] - r * 0.12, lens[1] - r * 0.55)], (255, 255, 255), 3,
              alpha=210)


def folder(cv, x, y, w=46, h=60, rot=0):
    cv.push(x, y, rot=rot)
    cv.fill(spline([(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)], closed=True, n=2),
            (232, 196, 120), shade_col=(208, 168, 96), depth=4)
    cv.fill([(-w / 2 + 4, -h / 2 - 6), (-w / 2 + 20, -h / 2 - 6), (-w / 2 + 24, -h / 2), (-w / 2 + 4, -h / 2)],
            (232, 196, 120))
    cv.stroke([(-w / 2 + 8, -4), (w / 2 - 8, -4)], (170, 120, 70), 2)
    cv.stroke([(-w / 2 + 8, 6), (w / 2 - 14, 6)], (170, 120, 70), 2)
    cv.pop()


# --- poses ---------------------------------------------------------------------------------------------------------------------
# Joints in the character's own frame before yaw: x + = the character's LEFT (screen-right in front view), z + = forward.
# "R" is the character's right arm. Each hand: (kind, extra rotation deg). held: names drawn after the arms.

POSES = {
    "rest": dict(R=((-64, 182, -6), (-59, 234, 10)), L=((64, 182, -6), (59, 234, 10)),
                 hands=dict(R=("relaxed", 0), L=("relaxed", 0))),
    "hold_bowl": dict(R=((-60, 180, 6), (-40, 194, 48)), L=((60, 180, 6), (40, 194, 48)),
                      hands=dict(R=("cup", -10), L=("cup", 10)), bowl=(0, 184, 52)),
    "offer": dict(R=((-50, 152, 48), (-34, 160, 100)), L=((50, 152, 48), (34, 160, 100)),
                  hands=dict(R=("cup", -6), L=("cup", 6)), bowl=(0, 150, 106)),
    "magnify": dict(R=((-66, 164, 30), (-40, 106, 84)), L=((64, 182, -6), (59, 234, 10)),
                    hands=dict(R=("grip", 0), L=("relaxed", 0)),
                    grip=dict(side="R", item="lens", tip=(-10, 52, 134)), late="R"),
    "eat": dict(R=((-58, 176, 26), (-30, 134, 62)), L=((58, 180, 10), (32, 196, 52)),
                hands=dict(R=("grip", 0), L=("cup", 16)), bowl=(14, 184, 66),
                grip=dict(side="R", item="spoon", tip=(-2, 80, 94)), late="R"),
    "no_thanks": dict(R=((-36, 140, 50), (-14, 128, 102)), L=((64, 182, -6), (59, 234, 10)),
                      hands=dict(R=("open", 192), L=("relaxed", 0)), late="R"),
    "hold_high": dict(R=((-60, 176, 10), (-30, 166, 58)), L=((60, 176, 10), (30, 166, 58)),
                      hands=dict(R=("cup", -10), L=("cup", 10)), bowl=(0, 154, 70)),
}

ARM_LEN = {"pin": (55.0, 55.0), "mom": (57.0, 55.0)}      # upper arm, forearm


def solve_arm(sh, hint_elbow, wrist, l1, l2):
    """Two-bone IK in 3D: the wrist is the target (pulled back a little if out of reach), the elbow lands where the
    limb lengths demand, on the side the hint elbow points to. Keeps every arm the same length in every frame."""
    sh, wr = np.array(sh, float), np.array(wrist, float)
    v = wr - sh
    d = float(np.linalg.norm(v))
    dmax = (l1 + l2) * 0.985
    if d > dmax:
        wr, d = sh + v / d * dmax, dmax
        v = wr - sh
    u = v / d
    a = (d * d + l1 * l1 - l2 * l2) / (2 * d)
    h = math.sqrt(max(l1 * l1 - a * a, 0.0))
    hint = np.array(hint_elbow, float) - (sh + wr) / 2
    hp = hint - u * float(np.dot(hint, u))
    n = float(np.linalg.norm(hp))
    hp = hp / n if n > 1e-6 else np.array([0.0, 1.0, 0.0])
    return tuple(sh + u * a + hp * h), tuple(wr)


def pose_lerp(a, b, t):
    """Blend two pose dicts (same props): wrists, bend hints and prop positions move smoothly."""
    A = a if isinstance(a, dict) else POSES[a]
    B_ = b if isinstance(b, dict) else POSES[b]
    L = lambda u, v: tuple(x + (y - x) * t for x, y in zip(u, v))
    out = dict(B_ if t >= 0.5 else A)
    for side in ("R", "L"):
        out[side] = (L(A[side][0], B_[side][0]), L(A[side][1], B_[side][1]))
    hands = {}
    for side in ("R", "L"):
        ka, kb = A["hands"][side], B_["hands"][side]
        hands[side] = (kb[0] if t >= 0.5 else ka[0], ka[1] + (kb[1] - ka[1]) * t)
    out["hands"] = hands
    for key in ("bowl",):
        if key in A and key in B_:
            out[key] = L(A[key], B_[key])
    if "grip" in A and "grip" in B_:
        out["grip"] = dict(B_["grip"], tip=L(A["grip"]["tip"], B_["grip"]["tip"]))
    return out


def _p(pt, th):
    q = yaw(pt, th)
    return (q[0], q[1]), q[2]


def figure(cv: Canvas, cid, th, pose="rest", expr="neutral", pregnant=False, lean=0.0, talk=None, shadow=True,
           blink=0.0, head_th=None, head_dy=0.0, shrug=0.0):
    """Whole character with feet at local y = BODY[cid]['ground'], centred at x = 0.
    pose: a name from POSES or a pose dict (see pose_lerp); expr: a name or an expression dict (cast.mix_expr);
    head_th turns the head independently of the body; head_dy nods it; blink 0..1 closes the lids;
    shrug raises both shoulders (units, default 0)."""
    c, B = CHARS[cid], BODY[cid]
    P = pose if isinstance(pose, dict) else POSES[pose]
    skin = c["skin"]
    skin_sh = mix(skin, (226, 168, 158), 0.5)
    sl = torso_slices(cid, pregnant)
    e = resolve_expr(expr)
    tilt = e.get("tilt", 0)
    th_h = th if head_th is None else head_th
    G = B["ground"]
    l1, l2 = ARM_LEN[cid]
    if shadow:
        cv.ellipse(0, G + 2, 74, 12, (0, 0, 0), alpha=34)

    def arm(side):
        """One arm with its hand (and the prop it grips, drawn first so the fingers wrap over it)."""
        sx = -1 if side == "R" else 1
        sh3 = (B["shoulder"][0] * sx * (1 - 0.012 * shrug), B["shoulder"][1] - shrug, B["shoulder"][2])
        hint, wr_t = P[side]
        el3, wr3 = solve_arm(sh3, hint, wr_t, l1, l2)
        (s2, _), (e2, _), (w2, wz) = _p(sh3, th), _p(el3, th), _p(wr3, th)
        kind, extra = P["hands"][side]
        fx, fy = w2[0] - e2[0], w2[1] - e2[1]
        grip = P.get("grip") if P.get("grip") and P["grip"]["side"] == side else None
        if kind == "cup" and P.get("bowl"):          # tuck the fingers under the bowl instead of past its edge
            (bx, by), _ = _p(P["bowl"], th)
            fx, fy = (bx - w2[0]) * 0.6 + fx * 0.4, (by + 20 - w2[1]) * 0.6 + fy * 0.4
        ang = math.degrees(math.atan2(-fx, fy)) + extra
        if kind == "open":                           # a raised palm is posed absolutely: fingers up, tipped forward
            ang = extra
        # thumb toward the character's front: mirror the template when the forward direction points screen-left
        fwd = yaw((0, 0, 1), th)[0] + 0.35 * (-sx) * math.cos(th)
        mirror = (fwd < 0) != (ang > 90 or ang < -90)
        if kind == "open":
            mirror = sx > 0
        if grip:                                     # fist wraps the handle: handle crosses the fist, thumb on top
            (tx, ty), _ = _p(grip["tip"], th)
            n = math.hypot(tx - w2[0], ty - w2[1]) or 1
            ux, uy = (tx - w2[0]) / n, (ty - w2[1]) / n
            fn = math.hypot(fx, fy) or 1
            phi_f = math.atan2(fx / fn, fy / fn)
            cand = max(((-uy, ux), (uy, -ux)), key=lambda v: v[0] * fx / fn + v[1] * fy / fn)
            phi = math.atan2(cand[0], cand[1])
            phi = phi_f + max(-0.96, min(0.96, (phi - phi_f + math.pi) % (2 * math.pi) - math.pi))     # wrist bends <= 55 deg
            dy_ = (math.sin(phi), math.cos(phi))
            # local +x (thumb side) must point along the handle toward the tip: pick the flip that does so
            dir_x = (dy_[1], -dy_[0])
            mirror = (dir_x[0] * ux + dir_x[1] * uy) < 0
            ang = math.degrees(math.atan2(dy_[0], dy_[1])) if mirror else math.degrees(math.atan2(-dy_[0], dy_[1]))
            gp = (w2[0] + dy_[0] * 13, w2[1] + dy_[1] * 13)
            a_pt = (gp[0] - ux * 9, gp[1] - uy * 9)
            if grip["item"] == "lens":
                magnifier(cv, a_pt, (tx, ty))
            else:
                spoon(cv, a_pt, (tx, ty))
        aw = B["arm_w"]
        if B["sleeve"] == "long":
            hand(cv, w2, ang, kind, skin, mirror, part="base")
            limb(cv, [s2, e2, w2], aw, B["top"], shade_col=B["top_dark"])
            cv.fill(_band(e2, w2, 0.8, aw[2] + 2), B["cuff"], lw=2.8)          # cuff ribbing
            cv.stroke(spline([(e2[0] * 0.4 + s2[0] * 0.6 + 5, e2[1] * 0.4 + s2[1] * 0.6),
                              (e2[0] + 3, e2[1] - 4)], n=3), B["top_dark"], 1.8)
        else:
            limb(cv, [s2, e2, w2], aw, skin, shade_col=skin_sh)
            hand(cv, w2, ang, kind, skin, mirror, part="base", scale=1.15 if kind == "open" else 1.0)
            at = lambda t: (s2[0] + (e2[0] - s2[0]) * t, s2[1] + (e2[1] - s2[1]) * t)         # puff sleeve
            limb(cv, [s2, at(0.25), at(0.5)], (32, 37, 30), B["top"], shade_col=B["top_dark"], stroke_start=False)
            ex, ey = at(0.5)
            dx, dy = e2[0] - s2[0], e2[1] - s2[1]
            n = math.hypot(dx, dy) or 1
            nx, ny = -dy / n * 13, dx / n * 13
            cv.stroke(spline([(ex - nx, ey - ny - 2), (ex, ey + 2.5), (ex + nx, ey + ny - 2)], n=4), B["cuff"], 3.2)
        if grip:
            hand(cv, w2, ang, "grip", skin, mirror, part="thumb")
        return w2, ang, kind, mirror

    def arm_depth(side):
        hint, wr_t = P[side]
        return (_p(hint, th)[1] + _p(wr_t, th)[1]) / 2

    order = sorted(("R", "L"), key=arm_depth)
    behind = [s_ for s_ in order if arm_depth(s_) < -12]
    front = [s_ for s_ in order if s_ not in behind]
    late = P.get("late")

    cv.push(0, 0, rot=lean, pivot=(0, B["hip"][1]))
    cv.push(0, head_dy, rot=tilt, pivot=(0, 95))
    hair_back(cv, c, th_h)
    cv.pop()
    for s_ in behind:
        arm(s_)
    cv.pop()

    # legs + shoes (no lean)
    hx, hy = B["hip"]
    legs = sorted((-1, 1), key=lambda sx: yaw((hx * sx, 0, 0), th)[2])
    for sx in legs:
        hip3, knee3, ank3 = (hx * sx, hy, 0), (hx * sx * 1.02, B["knee_y"], 2), (hx * sx, B["ankle_y"], 0)
        pts = [_p(p, th)[0] for p in (hip3, knee3, ank3)]
        if B["skirt"]:
            limb(cv, pts, (B["leg_w"][0], B["leg_w"][0] - 2, B["leg_w"][1]), skin, shade_col=skin_sh)
        else:
            limb(cv, pts, (B["leg_w"][0], B["leg_w"][0] - 4, B["leg_w"][1]), B["bottom"],
                 shade_col=shade(B["bottom"], 0.86))
        _shoe(cv, (hx * sx, 0), th, B)

    cv.push(0, 0, rot=lean, pivot=(0, hy))
    # neck, hood behind it, torso
    if cid == "pin":
        hood = [(y, a, b, z0) for y, a, b, z0 in [(98, 20, 16, -26), (106, 42, 30, -22), (118, 46, 32, -18),
                                                   (128, 34, 24, -16)]]
        from toon import lathe
        cv.fill(lathe(hood, th, n=4), B["top_dark"], lw=3.0)
    cv.fill(tube([(0, 76), (0, 122)], 30), skin, lw=3.0, shade_col=skin_sh, depth=5)
    cv.fill(spline([(-15, 92), (0, 100), (15, 92), (15, 104), (-15, 104)], closed=True, n=3), skin_sh, ink=None)
    from toon import lathe
    cv.fill(lathe(sl, th, n=6), B["top"], lw=3.2, shade_col=B["top_dark"], depth=9)
    if cid == "pin":
        # hem ribbing, kangaroo pocket, collar roll, drawstrings
        cv.fill(lathe_band(sl, 226, 236, th), B["cuff"], lw=3.0)
        pocket = []
        for ph, y in ((-46, 196), (-30, 192), (0, 191), (30, 192), (46, 196), (52, 224), (0, 225), (-52, 224)):
            p, v = on_body(sl, ph, y, th, lift=1.5)
            if v > -0.1:
                pocket.append(p)
        if len(pocket) > 4:
            cv.fill(spline(pocket, closed=True, n=3), B["top_dark"], lw=2.6)
        body_line(cv, sl, th, lambda ph: 112 + 12 * math.cos(ph * D2R) ** 2, range(-90, 91, 15), B["cuff"], 9)
        for ph in (-14, 14):
            a, va = on_body(sl, ph, 122, th, lift=2)
            b, vb = on_body(sl, ph * 1.2, 160, th, lift=2)
            if va > 0.1 and vb > 0.1:
                cv.stroke(spline([a, ((a[0] + b[0]) / 2 + 2, (a[1] + b[1]) / 2), b], n=4), B["cuff"], 3.2)
                cv.ellipse(b[0], b[1] + 3, 2.6, 4, (240, 240, 240), ink=INK, lw=1.4)
    else:
        cv.fill(lathe_band(sl, 282, 292, th), B["cuff"], lw=3.0)
        body_line(cv, sl, th, lambda ph: 114 + 12 * math.cos(ph * D2R) ** 2, range(-70, 71, 10), B["cuff"], 7)
        body_line(cv, sl, th, lambda ph: 176, range(-85, 86, 10), B["cuff"], 4.5)
        for ph in (-30, 24):                        # soft folds in the skirt
            a, va = on_body(sl, ph, 200, th, lift=1)
            b, vb = on_body(sl, ph * 1.2, 278, th, lift=1)
            if va > 0.15 and vb > 0.15:
                cv.stroke(spline([a, ((a[0] + b[0]) / 2 - 3, (a[1] + b[1]) / 2), b], n=4), B["top_dark"], 2.0)
        if pregnant:                                # the bump: a fold curving under it and a soft highlight on top
            body_line(cv, sl, th, lambda ph: 246 + 9 * math.cos(ph * D2R) ** 2, range(-62, 63, 8), B["top_dark"], 2.4)
            pts = []
            for ph, y in ((58, 196), (52, 214), (46, 234), (36, 252)):       # soft shade down the far side of the bump
                q, v = on_body(sl, ph, y, th, lift=0.5)
                if v > 0.1:
                    pts.append(q)
            if len(pts) > 2:
                cv.stroke(spline(pts, n=5), B["top_dark"], 6.0, alpha=120)
    # ปิ่น's long front locks fall over the shoulders
    if cid == "pin":
        cv.push(0, 0, rot=tilt * 0.5, pivot=(0, 95))
        for sx in sorted((-1, 1), key=lambda sx: yaw((80 * sx, 0, 26), th)[2]):
            pts3 = [(78 * sx, 40, 22), (74 * sx, 100, 30), (66 * sx, 150, 34), (60 * sx, 190, 34)]
            pts = [_p(p, th)[0] for p in pts3]
            if yaw(pts3[1], th)[2] < -10:
                continue
            o = tube(pts, lambda t: 30 * (1 - t) ** 0.7 + 3, n=6)
            cv.fill(o, c["hair"], lw=3.0)
            cv.stroke(spline([pts[0], pts[1], pts[2]], n=4), shade(c["hair"], 0.72), 1.6)
        cv.pop()

    held = []
    for s_ in front:
        if s_ != late:
            held.append((s_, arm(s_)))
    _held_props(cv, cid, P, th, held, skin, before_head=True)
    cv.push(0, head_dy, rot=tilt, pivot=(0, 95))
    head(cv, c, th_h, expr, talk=talk, back=False, blink=blink)
    cv.pop()
    if late and late in front:
        held.append((late, arm(late)))
    cv.pop()


def _bowl_hand(cv, bx, by, w, sgn, skin):
    """A hand holding a bowl from the side: fingers wrap the front of the wall, the thumb rests over the rim."""
    for k in range(3):
        a = (bx + sgn * (w * 0.56 + 6 * k), by + w * (0.62 - 0.05 * k))
        b = (bx + sgn * (w * 0.84 + 3 * k), by + w * (0.22 + 0.04 * k))
        cv.stroke([a, b], INK, 10.2)
        cv.stroke([a, b], skin, 6.4)
    t0 = (bx + sgn * w * 0.9, by + 9)
    t1 = (bx + sgn * w * 0.7, by - 3.5)
    cv.stroke([t0, t1], INK, 11.6)
    cv.stroke([t0, t1], skin, 7.8)
    cv.stroke([(t1[0] - sgn * 1.2, t1[1] + 0.8), (t1[0] - sgn * 3.6, t1[1] + 1.6)], mix(INK, skin, 0.5), 1.4)   # nail


def _held_props(cv, cid, P, th, held, skin, before_head):
    if before_head and P.get("bowl"):
        (bx, by), _ = _p(P["bowl"], th)
        w = 40 if cid == "pin" else 38
        bowl(cv, bx, by, w=w)
        for side, (w2, ang, kind, mirror) in held:
            if kind == "cup":
                _bowl_hand(cv, bx, by, w, 1 if w2[0] > bx else -1, skin)
    if not before_head and P.get("bowl") and any(kind == "grip" for _, (_, _, kind, _) in held):
        pass
    if before_head and P.get("folder"):
        for side, (w2, ang, kind, mirror) in held:
            if side == "L":
                folder(cv, w2[0] + 6, w2[1] + 18, rot=-8)
                hand(cv, w2, ang, "grip", skin, mirror, part="thumb")


def _shoe(cv, foot, th, B):
    """Shoe from a sole ellipse on the ground and an ankle ellipse, seen from slightly above."""
    fx, fz = foot
    G, ay = B["ground"], B["ankle_y"]
    pts = []
    L = 22 if B["skirt"] is None else 17
    Wd = 15 if B["skirt"] is None else 11
    for i in range(24):
        a = i / 24 * 2 * math.pi
        for (cx, cz, rx, rz, y) in ((fx, 8, Wd, L, G), (fx, 0, Wd * 0.8, Wd * 0.8, ay + 2)):
            q = yaw((cx + rx * math.cos(a), y, cz + rz * math.sin(a)), th)
            pts.append((q[0], q[1] - q[2] * 0.12))
    hull = _hull(pts)
    cv.fill(spline(hull, closed=True, n=3), B["shoe"], lw=3.0, shade_col=shade(B["shoe"], 0.88), depth=4)
    sole = []
    for i in range(13):
        a = math.pi * i / 12
        q = yaw((fx + Wd * math.cos(a), G, 8 + L * math.sin(a)), th)
        sole.append((q[0], q[1] - q[2] * 0.12))
    cv.stroke(spline(sole, n=3), B["sole"], 3.0)


def _band(e2, w2, k, w):
    """Cuff ribbing: a band from k along the forearm to the wrist, slightly rounded at the open end."""
    dx, dy = w2[0] - e2[0], w2[1] - e2[1]
    n = math.hypot(dx, dy) or 1
    ux, uy, nx, ny = dx / n, dy / n, -dy / n * w / 2, dx / n * w / 2
    a = (e2[0] + dx * k, e2[1] + dy * k)
    b = (w2[0] + ux * 2, w2[1] + uy * 2)
    return chain([(a[0] + nx, a[1] + ny), (b[0] + nx, b[1] + ny)],
                 [(b[0] + nx, b[1] + ny), (b[0] + ux * 3, b[1] + uy * 3), (b[0] - nx, b[1] - ny)],
                 [(b[0] - nx, b[1] - ny), (a[0] - nx, a[1] - ny)], n=5)


def _hull(pts):
    pts = sorted(set((round(x, 2), round(y, 2)) for x, y in pts))
    if len(pts) < 3:
        return pts

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lower, upper = [], []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]


if __name__ == "__main__":
    from pathlib import Path
    out = Path(__file__).resolve().parent / "out"
    cv = Canvas(1800, 820, ss=3, bg=(250, 246, 238, 255))
    for i, (cid, th, pose, ex, preg, lean) in enumerate([
            ("pin", 0, "rest", "neutral", False, 0), ("pin", 35 * D2R, "hold_bowl", "happy", False, 0),
            ("pin", 82 * D2R, "rest", "neutral", False, 0), ("pin", 35 * D2R, "magnify", "determined", False, 0),
            ("mom", 0, "rest", "neutral", True, 0), ("mom", 35 * D2R, "eat", "content", True, 0),
            ("mom", 82 * D2R, "rest", "neutral", True, 0), ("mom", 35 * D2R, "no_thanks", "meh", False, -7)]):
        cv.push(120 + i * 222, 300, scale=0.92)
        figure(cv, cid, th, pose, ex, pregnant=preg, lean=lean)
        cv.pop()
    cv.result().save(out / "v2b_bodies.png")
    print("ok")
