"""Shared bits for the red-thread story scenes (rt1..rt7): narration timing from the audio, beat fractions, students with idle life."""
from __future__ import annotations

import json
from pathlib import Path

import uni_chars  # noqa: F401  (registers the students and the uniform wrappers)
from acting import *  # noqa: F401,F403
from props_uni import *  # noqa: F401,F403
import rt_art  # noqa: F401  (records where the rig puts every hand, so the thread starts at a real pinky)
from rt_art import *  # noqa: F401,F403
from rt_bg import *  # noqa: F401,F403
from rt_props2 import *  # noqa: F401,F403
from rt_bg2 import *  # noqa: F401,F403

ROOT = Path(__file__).resolve().parent / "red_thread"
TIM = json.loads((ROOT / "audio" / "timing.json").read_text(encoding="utf-8")) if (ROOT / "audio" / "timing.json").is_file() else {}
DOC = json.loads((ROOT / "know_red_thread.json").read_text(encoding="utf-8"))
_mk = ROOT / "audio" / "marks.json"
MARKS = json.loads(_mk.read_text(encoding="utf-8")) if _mk.is_file() else {}
LEAD, TAIL = 0.7, 1.0
_T = [0.0]


def scene_dur(i):
    d = TIM.get(str(i), {}).get("dur", [60, 61, 41, 44, 66, 41, 40][i - 1])
    return round(d + LEAD + TAIL, 2)


def beats(i, markers):
    """Scene-local start of each beat: the model's timestamp of the marker phrase snapped to a pause (audio/marks.json); proportional by text position until the audio exists."""
    text = DOC["scenes"][i - 1]["lines"][0]["text"]
    d = TIM.get(str(i), {}).get("dur", [60, 61, 41, 44, 66, 41, 40][i - 1])
    marks = MARKS.get(str(i), {})
    out = [0.0]
    for m in markers[1:]:
        k = text.find(m)
        assert k >= 0, f"marker not in scene {i}: {m}"
        out.append(LEAD + (marks[m]["snapped"] if m in marks else k / len(text) * d))
    for j in range(1, len(out)):
        out[j] = max(out[j], out[j - 1] + 1.5)
    return out


def which(t, b):
    k = 0
    for j, bt in enumerate(b):
        if t >= bt:
            k = j
    return k


def fr(t, BE, k, a, b):
    u = (t - BE[k]) / max(0.01, BE[k + 1] - BE[k])
    return seg(u, a, b)


def in_(t, BE, k, a, b):
    u = (t - BE[k]) / max(0.01, BE[k + 1] - BE[k])
    return a <= u < b


SWAY = mk(((-62, 160, 24), (-36, 200, 16)), ((62, 160, 24), (36, 200, 16)))
KS = dict(phum=0.98, bua=1.0, kong=1.0, manao=1.0, em=1.0, yuelao=1.0, bam=1.0, jake=1.0, faa=1.0, mariam=1.0, omar=1.0)


def tick(t):
    _T[0] = t
    PH[0] = t


def st(cv, who, x, y, pose=REST, ex="neutral", k=None, th=40, seed=0.0, **kw):
    """A student with idle life (breath, sway, blink). pose REST gets a gentle arm sway."""
    t = _T[0]
    kw["lean"] = kw.get("lean", 0.0) + 1.3 * math.sin(t * 2.0 + seed + len(who))
    kw["bob"] = kw.get("bob", 0.0) + 1.2 * abs(math.sin(t * 2.0 + seed + len(who)))
    kw.setdefault("blink_v", blink(t, 0.1 + 0.37 * (seed + len(who))))
    if pose is REST and kw.get("walk") is None:
        pose = pl(REST, SWAY, 0.5 + 0.5 * math.sin(t * 1.3 + seed))
    rt_art.begin_actor()
    actor(cv, who, x, y, th, pose, ex, k=KS.get(who, 1.0) if k is None else k, **kw)
    rt_art.end_actor(who)


def pinky_pos(who, x, y, pose, k, th=40, flip=False, side="R"):
    """Where a student's pinky roughly is: the wrist plus a short step along the hand."""
    wx, wy = wrist_pos(who, x, y, th, pose, side, k, flip)
    return (wx, wy + 12)


def mouth_of(t, a, b, seed=0):
    return talk(t, a, b, seed)


def say_waves(cv, x, y, t, a, b, flip=False, col=(255, 255, 255)):
    if a <= t <= b:
        waves(cv, x, y, (t - a) * 1.2, n=3, r0=12, dr=11, col=col, a0=-45, a1=45, lw=3.4, flip=flip)


def pulse_ov(ov, t, amount=0.05):
    ov[:] = [(txt, x, y, size * (1 + amount * math.sin(t * 4 + x * 0.01)) if a > 0.9 else size, col, a) for (txt, x, y, size, col, a) in ov]


# ----------------------------------------------------------------------------------------------------------------- v2 helpers: positions, seated hands, the thread tied to real pinkies
SCALE_OF_NAME = dict(phum=0.92, bua=0.9, kong=0.98, manao=0.88, em=0.9, yuelao=0.95, bam=0.9, jake=1.0, faa=0.9, mariam=0.9, omar=0.96)
POS: dict = {}
BODYPASS: dict = {}


def _remember(who, x, y):
    POS[who] = (x, y)


_st_v1 = st


def st(cv, who, x, y, pose=REST, ex="neutral", k=None, th=40, seed=0.0, hide_arms=False, **kw):          # noqa: F811  (v2: remembers where everybody stands; can hide the arms)
    _remember(who, x, y)
    t_ = _T[0]
    BODYPASS[who] = dict(lean=kw.get("lean", 0.0) + 1.3 * math.sin(t_ * 2.0 + seed + len(who)), bob=kw.get("bob", 0.0) + 1.2 * abs(math.sin(t_ * 2.0 + seed + len(who))))
    rt_art.HIDE_ARMS[0] = hide_arms
    try:
        return _st_v1(cv, who, x, y, pose=pose, ex=ex, k=k, th=th, seed=seed, **kw)
    finally:
        rt_art.HIDE_ARMS[0] = False


def desk_pose(who, x, y, th, k, flip=False, hy=598, spread=34, kinds=("relaxed", "relaxed")):
    """Both hands resting on the desktop in front of a seated student (the body stands behind the desk)."""
    s = k
    return reach(who, x, y, th, s, {"R": (x - spread * 1.0, hy), "L": (x + spread * 1.0, hy + 2)}, kinds=kinds, z=70, flip=flip)


def seated(cv, who, x, y=730, k=0.82, th=0.0, flip=False, ex="neutral", hy=598, spread=34, **kw):
    """Body of a student seated behind a desk. The arms are NOT drawn here (they would show twice); seated_front() draws them once, in front of the desk."""
    pose = desk_pose(who, x, y, th, k * KS.get(who, 1.0), flip, hy, spread)
    st(cv, who, x, y, pose=pose, ex=ex, th=th, k=k, flip=flip, hide_arms=True, **kw)
    return pose


def seated_front(cv, who, x, y, pose, th=0.0, k=0.82, flip=False, lean=0.0):
    """Draw the arms and hands in front of the desk (after desks()) with the same sway as the body, and remember the pinkies."""
    bp = BODYPASS.get(who, dict(lean=0.0, bob=0.0))
    rt_art.begin_actor()
    cv.push(0, -bp["bob"])
    front_arms(cv, who, x, y, th, pose, k=k * KS.get(who, 1.0), lean=bp["lean"], flip=flip)
    cv.pop()
    rt_art.end_actor(who)


def tie(cv, a, b, t, sag=60.0, alpha=255, w=3.6, spark=True):
    """The red thread between the pinkies of a and b (whichever of their hands is nearer the other), as drawn this frame."""
    if a not in POS or b not in POS:
        return None
    pa = pinky_of(a, toward_x=POS[b][0])
    pb = pinky_of(b, toward_x=POS[a][0])
    return link(cv, pa, pb, t, sag=sag, alpha=alpha, w=w, spark=spark)


def tie_out(cv, a, side, t, sag=90.0, alpha=255, y_drop=40.0):
    """The thread from a's pinky going on out of the picture (side -1 left / +1 right), toward someone who is not on screen."""
    if a not in POS:
        return None
    pa = pinky_of(a, toward_x=-1000 if side < 0 else 2400)
    if pa is None:
        return None
    ring(cv, pa, alpha=alpha)
    return link(cv, pa, off_edge(pa, side, y_drop), t, sag=sag, alpha=alpha, tie=False)


def sigh_puff(cv, who, x, y, t, k=1.0, seed=0.0, side=1):
    """A little breath cloud that drifts up beside (never on) a character's head: a sigh or steam."""
    hx, hy = head_pos(who, x, y, k * KS.get(who, 1.0), 0.0)
    s = SCALE_OF_NAME.get(who, 0.9) * k
    for j in range(2):
        u = (t * 0.8 + j * 0.45 + seed) % 1.0
        puff(cv, hx + side * (88 * s + 10 * j), hy + 6 * s - 46 * u, 11 * s + 2, u, col=(240, 240, 248))
