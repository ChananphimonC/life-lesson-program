"""Animation engine for the full episode (thin layer over the prototype_v2 rig; nothing in prototype_v2 is edited).

What it adds to the existing rig, all in memory:
  * walk / run cycle: the rig's legs are static, so figure.limb and figure._shoe are wrapped to swing and lift the legs by phase;
  * keyframe helpers (ease, tween, pose/expression blending with the rig's own pose_lerp / mix_expr);
  * `Cast`: the four provisional episode characters (from visual_poc/poc_chars.py) drawn at a given world scale;
  * wrist_pos(): where a hand is on screen, so props (paper, bowls) can be attached to the hands.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
POC = HERE.parent / "visual_poc"
sys.path.insert(0, str(POC))
sys.path.insert(0, str(POC.parents[2] / "prototype_v2"))
sys.path.insert(0, str(HERE))

import cast  # noqa: E402
import figure  # noqa: E402
import poc_chars  # noqa: E402  (registers ton/chok/kaew/uean in memory; hides pin's locks for ton/chok)
from cast import mix_expr  # noqa: E402
from figure import BODY, POSES, pose_lerp, solve_arm  # noqa: E402
from toon import INK, Canvas, ellipse_pts, mix, shade, spline, yaw  # noqa: E402

W, H, FPS = 1280, 720, 24
CID, SCALE = poc_chars.CID, poc_chars.SCALE
PX_PER_M_REF = 192.0           # k = 1 draws Ton (1.4 m) 269 px tall -> 192 px per metre


# ---------------------------------------------------------------------------------------------------------------- math helpers
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease(u):
    u = clamp(u)
    return u * u * (3 - 2 * u)


def ease_out(u):
    u = clamp(u)
    return 1 - (1 - u) ** 3


def ease_in(u):
    u = clamp(u)
    return u ** 3


def seg(t, a, b):
    """Progress 0..1 of t inside [a, b]."""
    return clamp((t - a) / max(1e-9, b - a))


def lerp(a, b, u):
    if isinstance(a, (tuple, list)):
        return tuple(x + (y - x) * u for x, y in zip(a, b))
    return a + (b - a) * u


def keys(kf, t, e=ease):
    """kf = [(t0, v0), (t1, v1), ...] -> value at t (eased between keys, held outside)."""
    if t <= kf[0][0]:
        return kf[0][1]
    for (t0, v0), (t1, v1) in zip(kf, kf[1:]):
        if t <= t1:
            return lerp(v0, v1, e(seg(t, t0, t1)))
    return kf[-1][1]


def blink(t, seed=0.0):
    ph = (t * 0.37 + seed) % 1.0
    return max(0.0, 1 - abs(ph - 0.5) * 2 / 0.05) if abs(ph - 0.5) < 0.025 else 0.0


CUR = ""                       # name of the scene being drawn (set by episode.render_frame)
_voice = None


def _clips(scene):
    """Voice clips of a scene from audio/voice_manifest.json (written by voice.py); [] when there is no recorded voice."""
    global _voice
    if _voice is None:
        import json
        f = HERE / "audio" / "voice_manifest.json"
        _voice = {}
        if f.is_file():
            for c in json.loads(f.read_text(encoding="utf-8")):
                _voice.setdefault(c["scene"], []).append(c)
    return _voice.get(scene, [])


def talk(t, t0, t1, seed=0.0):
    """Mouth opening 0..1 while a line is spoken. With recorded voice the mouth follows the loudness of the actual audio;
    without it (no clip for this window) it falls back to a procedural flap that is only rhythm."""
    hits = [c for c in _clips(CUR) if t0 <= (c["a"] + c["b"]) / 2 <= t1]
    if hits:
        for c in hits:
            if c["start"] <= t < c["end"]:
                i = int((t - c["start"]) * FPS)
                return c["env"][min(i, len(c["env"]) - 1)]
        return 0.0
    if not (t0 <= t <= t1):
        return 0.0
    return clamp(0.15 + 0.85 * abs(math.sin((t - t0) * 9.5 + seed)) * (0.6 + 0.4 * math.sin((t - t0) * 3.1 + seed * 2)))


# ----------------------------------------------------------------------------------------------------------------- walk cycle
_legw = {}
_walk = None
_leg_i = 0
_limb, _shoe = figure.limb, figure._shoe


def _leg_widths(cid):
    B = BODY[str(cid)]
    return (B["leg_w"][0], B["leg_w"][0] - (2 if B["skirt"] else 4), B["leg_w"][1])


def _leg_off(i):
    ph, stride, lift = _walk["phase"], _walk["stride"], _walk["lift"]
    a = ph + i * math.pi
    return stride * math.sin(a), lift * max(0.0, math.cos(a))


def _limb_w(cv, pts, widths, col, shade_col=None, ink=INK, lw=3.0, stroke_start=False):
    if _walk is not None and len(pts) == 3 and tuple(widths) == _walk["legw"]:
        dx, up = _leg_off(_walk["i"] % 2)
        pts = [pts[0], (pts[1][0] + dx * 0.5, pts[1][1] - up * 0.55), (pts[2][0] + dx, pts[2][1] - up)]
    return _limb(cv, pts, widths, col, shade_col=shade_col, ink=ink, lw=lw, stroke_start=stroke_start)


def _shoe_w(cv, foot, th, B):
    global _walk
    if _walk is None:
        return _shoe(cv, foot, th, B)
    dx, up = _leg_off(_walk["i"] % 2)
    _walk["i"] += 1
    cv.push(dx, -up)
    _shoe(cv, foot, th, B)
    cv.pop()


figure.limb, figure._shoe = _limb_w, _shoe_w


def walk_pose(phase, swing=34.0, carry=None):
    """Arm swing for a walk cycle (arms opposite to legs); `carry` overrides both arms with a held pose."""
    if carry is not None:
        return carry
    s = math.sin(phase)
    r = ((-60, 168, 8 * s), (-54, 228, 24 * s))
    l = ((60, 168, -8 * s), (54, 228, -24 * s))
    return dict(R=r, L=l, hands=dict(R=("relaxed", 0), L=("relaxed", 0)))


# ------------------------------------------------------------------------------------------------------------------ drawing
EXMAP = {}


def actor(cv, who, x, feet_y, th=0.0, pose="rest", expr="neutral", k=1.0, flip=False, lean=0.0, mouth=0.0, blink_v=0.0,
          walk=None, bob=0.0, shadow=True, squash=1.0):
    """Draw one cast member with feet at (x, feet_y). th in degrees (0 front, + faces screen-right unless flip).
    walk = dict(phase, stride, lift) animates the legs. squash scales height (anticipation / landing)."""
    global _walk
    if isinstance(expr, str) and expr in EXMAP:
        expr = EXMAP[expr]
    poc_chars.NO_LOCKS = who in ("ton", "chok")
    s = SCALE[who] * k
    if walk:
        _walk = dict(walk, legw=_leg_widths(CID[who]), i=0)
        bob = bob or abs(math.sin(walk["phase"])) * 5 * s
    cv.push(x, feet_y - poc_chars.ground(who) * s * 1.0 + 0.0 - bob, scale=s, flip=flip)
    if squash != 1.0:
        cv.push(0, poc_chars.ground(who), scale=1.0)
        cv.pop()
    figure.figure(cv, CID[who], math.radians(th), pose, expr, lean=lean, talk=mouth or None, blink=blink_v, shadow=shadow)
    cv.pop()
    _walk = None
    poc_chars.NO_LOCKS = False


def wrist_pos(who, x, feet_y, th, pose, side="R", k=1.0, flip=False):
    """Screen position of a wrist for props attached to the hands (before IK clamping, good to a few px)."""
    P = pose if isinstance(pose, dict) else POSES[pose]
    s = SCALE[who] * k
    wx, wy, wz = P[side][1]
    q = yaw((wx, wy, wz), math.radians(th))
    sx = -1 if flip else 1
    top = feet_y - poc_chars.ground(who) * s
    return (x + sx * q[0] * s, top + q[1] * s)


def head_pos(who, x, feet_y, k=1.0, dy=0.0):
    s = SCALE[who] * k
    return (x, feet_y - poc_chars.ground(who) * s + dy * s)


def tween_pose(a, b, u):
    return pose_lerp(a, b, ease(u))


def tween_expr(a, b, u):
    return mix_expr(a, b, ease(u))


def new_canvas(ss=2):
    return Canvas(W, H, ss=ss, bg=(255, 255, 255, 255))


# ---------------------------------------------------------------------------------------------------------------- hands on props
def _screen_to_local(who, x, feet_y, th, k, pt, z, flip=False):
    """Inverse of wrist_pos: a screen point plus a depth z -> the wrist target in the character's frame."""
    s = SCALE[who] * k
    top = feet_y - poc_chars.ground(who) * s
    sx = -1 if flip else 1
    qx, qy = (pt[0] - x) / s * sx, (pt[1] - top) / s
    c, sn = math.cos(math.radians(th)), math.sin(math.radians(th))
    # yaw: (x, y, z) -> (x c + z sn, y, -x sn + z c); solve for the local x given the projected x and z
    lx = (qx - z * sn) / c if abs(c) > 1e-3 else qx
    return (lx, qy, z)


def reach(who, x, feet_y, th, k, pts, hints=None, kinds=("relaxed", "relaxed"), z=60, flip=False):
    """A pose whose hands land on screen points. pts = {"R": (x, y) or None, "L": ...}; a missing side stays at rest.
    The rig's IK clamps a target out of reach, so the hand is at most a few px short of it."""
    P = dict(POSES["rest"])
    for side, kind in zip(("R", "L"), kinds):
        base = P[side]
        if pts.get(side):
            wr = _screen_to_local(who, x, feet_y, th, k, pts[side], z, flip)
            sgn = -1 if side == "R" else 1
            hint = (hints or {}).get(side, (sgn * 78, wr[1] - 30, 10))
            P[side] = (hint, wr)
    P["hands"] = dict(R=(kinds[0], 0), L=(kinds[1], 0))
    return P


def front_arms(cv, who, x, feet_y, th, pose, k=1.0, lean=0.0, flip=False):
    """Draw only the arms and hands of a character again, so they lie in front of the table and the paper the body stands behind.
    Same transform and IK as figure.figure, so the arms match the first pass exactly (hooded long sleeves)."""
    cid = CID[who]
    c, B = cast.CHARS[cid], BODY[cid]
    skin = c["skin"]
    skin_sh = mix(skin, (226, 168, 158), 0.5)
    l1, l2 = figure.ARM_LEN[cid]
    th_r = math.radians(th)
    s = SCALE[who] * k
    poc_chars.NO_LOCKS = who in ("ton", "chok")
    cv.push(x, feet_y - poc_chars.ground(who) * s, scale=s, flip=flip)
    cv.push(0, 0, rot=lean, pivot=(0, B["hip"][1]))
    for side in sorted(("R", "L"), key=lambda sd: (figure._p(pose[sd][0], th_r)[1] + figure._p(pose[sd][1], th_r)[1])):
        sx = -1 if side == "R" else 1
        sh3 = (B["shoulder"][0] * sx, B["shoulder"][1], B["shoulder"][2])
        hint, wr_t = pose[side]
        el3, wr3 = solve_arm(sh3, hint, wr_t, l1, l2)
        (s2, _), (e2, _), (w2, _) = figure._p(sh3, th_r), figure._p(el3, th_r), figure._p(wr3, th_r)
        kind, extra = pose["hands"][side]
        fx, fy = w2[0] - e2[0], w2[1] - e2[1]
        ang = math.degrees(math.atan2(-fx, fy)) + extra
        fwd = yaw((0, 0, 1), th_r)[0] + 0.35 * (-sx) * math.cos(th_r)
        mirror = (fwd < 0) != (ang > 90 or ang < -90)
        figure.hand(cv, w2, ang, kind, skin, mirror, part="base")
        figure.limb(cv, [s2, e2, w2], B["arm_w"], B["top"], shade_col=B["top_dark"])
        cv.fill(figure._band(e2, w2, 0.8, B["arm_w"][2] + 2), B["cuff"], lw=2.8)
    cv.pop()
    cv.pop()
    poc_chars.NO_LOCKS = False
