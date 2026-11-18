"""Shared bits for the island story scenes (isl1..isl12): narration timing from the audio, beat helpers, students with idle life, small effects."""
from __future__ import annotations

import json
import math
from pathlib import Path

import isl_chars  # noqa: F401  (registers the ten students, the captain and the uniform wrappers)
from acting import *  # noqa: F401,F403
from props_uni import *  # noqa: F401,F403
from isl_chars import ACC  # noqa: F401
from isl_props import *  # noqa: F401,F403
from isl_bg import *  # noqa: F401,F403

ROOT = Path(__file__).resolve().parent / "island_72"
TIM = json.loads((ROOT / "audio" / "timing.json").read_text(encoding="utf-8")) if (ROOT / "audio" / "timing.json").is_file() else {}
DOC = json.loads((ROOT / "know_island_72.json").read_text(encoding="utf-8"))
_mk = ROOT / "audio" / "marks.json"
MARKS = json.loads(_mk.read_text(encoding="utf-8")) if _mk.is_file() else {}
LEAD, TAIL = 0.7, 1.0
_T = [0.0]
KS = {}
SWAY = mk(((-62, 160, 24), (-36, 200, 16)), ((62, 160, 24), (36, 200, 16)))


def _text(i):
    return DOC["scenes"][i - 1]["lines"][0]["text"]


def narr_dur(i):
    return TIM.get(str(i), {}).get("dur", len(_text(i)) / 11.5)


def scene_dur(i):
    return round(narr_dur(i) + LEAD + TAIL, 2)


def beats(i, markers):
    """Scene-local start of each beat: the marker phrase's timestamp snapped to a pause (audio/marks.json); proportional by text position until the audio exists."""
    text, d = _text(i), narr_dur(i)
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
    actor(cv, who, x, y, th, pose, ex, k=KS.get(who, 1.0) if k is None else k, **kw)


def walker(cv, who, x, y, t, speed=7.0, stride=16, lift=12, ex="happy", k=None, seed=0.0, pose=None, **kw):
    """Walking (always towards +x unless flip=True is passed on purpose)."""
    ph = t * speed + seed
    st(cv, who, x, y, pose=pose or walk_pose(ph), ex=ex, th=60, k=k, seed=seed, walk=dict(phase=ph, stride=stride, lift=lift), **kw)


def mouth_of(t, a, b, seed=0):
    return talk(t, a, b, seed)


def say_waves(cv, x, y, t, a, b, flip=False, col=(255, 255, 255)):
    if a <= t <= b:
        waves(cv, x, y, (t - a) * 1.2, n=3, r0=12, dr=11, col=col, a0=-45, a1=45, lw=3.4, flip=flip)


def pulse_ov(ov, t, amount=0.05):
    ov[:] = [(txt, x, y, size * (1 + amount * math.sin(t * 4 + x * 0.01)) if a > 0.9 else size, col, a) for (txt, x, y, size, col, a) in ov]


def clock_badge(cv, hour, t, x=1130, y=70):
    """Top-right countdown: a little sun/moon dial and the hours left (drawn as shapes: 72 small pips, the elapsed ones filled)."""
    left = 72 - hour
    rrect(cv, x - 120, y - 38, x + 120, y + 38, 18, (24, 34, 66), lw=2.6, ink=(255, 255, 255))
    for i in range(24):
        a = -math.pi / 2 + i / 24 * 2 * math.pi
        on = (i / 24 * 72) < hour
        cv.ellipse(x - 78 + math.cos(a) * 24, y + math.sin(a) * 24, 3.0, 3.0, (255, 214, 90) if on else (110, 126, 168), ink=None)
    cv.ellipse(x - 78, y, 8, 8, (255, 214, 90), ink=None)
    # remaining hours as big digits drawn with the overlay system by the scene (ov.append)
    return left


ORDER10 = ["chula", "thamma", "mahidol", "kaset", "kmitl", "kmutt", "silpa", "cmu", "kku", "psu"]


def lying(cv, who, x, y, k=0.62, ex="neutral", flip=False, ang=84, seed=0.0):
    """A student lying on the sand (the standing figure rotated about the feet)."""
    cv.push(0, 0, rot=-ang if flip else ang, pivot=(x, y))
    actor(cv, who, x, y, 40, REST, ex, k=k, flip=flip, shadow=False)
    cv.pop()
    cv.ellipse(x, y + 4, 90 * k, 12 * k, (0, 0, 0), ink=None, alpha=40)


def row_x(n, x0, x1):
    return [x0 + (x1 - x0) * i / max(1, n - 1) for i in range(n)]
