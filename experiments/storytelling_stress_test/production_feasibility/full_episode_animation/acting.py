"""Reusable poses and expressions (as parameter dicts for the prototype_v2 rig) plus small acting helpers."""
from __future__ import annotations

from engine import *  # noqa: F401,F403


def mk(R, L=None, hr="relaxed", hl="relaxed", **extra):
    """Pose from (elbow-hint, wrist-target) pairs in the character's frame (x+ = character's left, y down, z forward)."""
    L = L or ((64, 182, -6), (59, 234, 10))
    return dict(R=R, L=L, hands=dict(R=(hr, 0), L=(hl, 0)), **extra)


def mirror(R):
    return tuple((-x, y, z) for x, y, z in R)


REST = POSES["rest"]
CARRY = mk(((-62, 160, 20), (-36, 150, 96)), ((62, 160, 20), (36, 160, 90)))
HOLD_UP2 = mk(((-70, 110, 20), (-46, 56, 80)), ((70, 110, 20), (46, 56, 80)))
ARMS_UP = mk(((-84, 90, 0), (-60, 22, 20)), ((84, 90, 0), (60, 22, 20)))
CHEER = mk(((-96, 80, 0), (-92, 4, 0)), ((96, 80, 0), (92, 4, 0)))
PUSH = mk(((-64, 140, 30), (-34, 130, 104)), ((64, 140, 30), (34, 130, 104)))
HIP = mk(((-100, 170, -10), (-54, 198, 6)), ((100, 170, -10), (54, 198, 6)))
HEADS = mk(((-104, 70, -10), (-40, -6, 14)), ((104, 70, -10), (40, -6, 14)))
SPREAD = mk(((-112, 126, 0), (-170, 120, 0)), ((112, 126, 0), (170, 120, 0)))
CROSS = mk(((-40, 170, 30), (28, 164, 70)), ((40, 176, 34), (-28, 172, 76)))
POINT_UP = mk(((-80, 100, 10), (-46, 12, 80)), hr="point")
POINT_FWD = mk(((-72, 120, 30), (-34, 96, 124)), hr="point")
SHRUG = mk(((-84, 130, 20), (-70, 100, 70)), ((84, 130, 20), (70, 100, 70)))
THINK = mk(((-52, 120, 40), (-18, 66, 96)))
STOP = dict(R=((-36, 140, 50), (-14, 128, 102)), L=((64, 182, -6), (59, 234, 10)), hands=dict(R=("open", 192), L=("relaxed", 0)), late="R")
WRITE_A = mk(((-62, 160, 30), (-30, 188, 100)), ((62, 160, 24), (34, 180, 80)))
EAT_A = dict(POSES["eat"])
EAT_B = dict(POSES["eat"], R=((-58, 176, 26), (-26, 112, 66)), grip=dict(POSES["eat"]["grip"], tip=(-2, 52, 98)))
HAMMER = mk(((-80, 100, 10), (-60, 40, 40)))                                 # arm raised, holding something (ladle)
SCRUB = mk(((-70, 150, 24), (-36, 150, 84)), ((70, 150, 24), (36, 160, 88)))
LADLE_POINT = dict(POSES["rest"], R=((-66, 120, 30), (-30, 96, 120)), hands=dict(R=("grip", 0), L=("relaxed", 0)),
                   grip=dict(side="R", item="spoon", tip=(-10, 74, 160)), late="R")


def write_pose(t, rate=7.0, base=WRITE_A):
    """Writing: the right wrist scribbles left-right at the counter."""
    wob = math.sin(t * rate) * 14
    R = (base["R"][0], (base["R"][1][0] + wob, base["R"][1][1] + abs(math.sin(t * rate * 0.5)) * 6, base["R"][1][2]))
    return dict(base, R=R)


def pl(a, b, u):
    return pose_lerp(a, b, ease(u))


def walk_ph(t, speed=7.0):
    return t * speed


EX = {
    "neutral": "neutral",
    "pant": dict(open=0.85, lid=0.35, gaze=(0, 2), brow=(8, -3), mouth="o", mp=dict(smile=0, mw=0.7, skew=0, rnd=1, wave=0), open_=0.7, blush=1.1, tilt=5,
                 sweat=True),
    "shout": dict(open=1.15, brow=(8, 8), mouth="open_smile", open_=1.0, blush=1.2, tilt=-3),
    "gloat": dict(open=0.8, lid=0.3, gaze=(3, 0), brow=(-4, 6), mouth="smirk", blush=0.9, tilt=-6),
    "gape": dict(open=1.3, gaze=(0, -1), brow=(13, 10), mouth="o", mp=dict(smile=0, mw=0.8, skew=0, rnd=1, wave=0), open_=1.0, blush=0.3, pupil=0.7),
    "deadpan": dict(open=0.75, lid=0.5, gaze=(0, -2), brow=(-1, 1), mouth="pout", mp=dict(smile=-0.1, mw=0.6, skew=0, rnd=0, wave=0), blush=0.5),
    "yikes": dict(open=1.2, brow=(10, -2), mouth="wavy", mp=dict(smile=0, mw=1.1, skew=0, rnd=0, wave=1), blush=0.3, tilt=4, sweat=True),
    "aha": dict(open=1.18, brow=(9, 8), mouth="open_smile", open_=0.5, blush=1.0, tilt=-6, sparkle=True),
    "smug": dict(open=0.9, lid=0.18, gaze=(2, 0), brow=(2, 4), mouth="smirk", blush=0.9, tilt=-4),
    "think": dict(open=1.0, lid=0.1, gaze=(-3, -3), brow=(8, 2), mouth="pout", mp=dict(smile=0.0, mw=0.6, skew=0.4, rnd=0, wave=0), blush=0.5, tilt=5),
    "laugh": dict(open=0.0, happy=True, brow=(5, 3), mouth="open_smile", open_=1.0, blush=1.3, tilt=-5),
    "plead": dict(open=1.1, lid=0.0, gaze=(0, -2), brow=(10, -6), mouth="wavy", mp=dict(smile=-0.1, mw=1.0, skew=0, rnd=0, wave=1), blush=0.8, tilt=6),
}


import engine as _engine  # noqa: E402

_engine.EXMAP.update({k: v for k, v in EX.items() if not isinstance(v, str)})


def ex(n):
    return EX.get(n, n) if isinstance(n, str) else n


def exl(a, b, u):
    return mix_expr(ex(a), ex(b), ease(u))
