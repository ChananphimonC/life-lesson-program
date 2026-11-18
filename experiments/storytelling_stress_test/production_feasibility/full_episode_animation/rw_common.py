"""Shared bits for the robot-world story scenes (rw1..rw7): narration timing, beat snapping, the two main characters."""
from __future__ import annotations

import json
from pathlib import Path

from acting import *  # noqa: F401,F403
from props_future import *  # noqa: F401,F403

ROOT = Path(__file__).resolve().parent / "robot_world"
TIM = json.loads((ROOT / "audio" / "timing.json").read_text(encoding="utf-8"))
DOC = json.loads((ROOT / "know_robot_world.json").read_text(encoding="utf-8"))
LEAD, TAIL = 0.7, 1.0
_mk = ROOT / "audio" / "marks.json"
MARKS = json.loads(_mk.read_text(encoding="utf-8")) if _mk.is_file() else {}


def scene_dur(i):
    return round(TIM[str(i)]["dur"] + LEAD + TAIL, 2)


def _align(text, dur, pauses):
    """Monotone alignment of the text's spaces (phrase breaks) to the pauses found in the audio, by position in the text vs position in time
    (edit-distance style: match, or skip a space / skip a pause). Returns {char index of the space: time of the matched pause}."""
    sp = [i for i, ch in enumerate(text) if ch == " "]
    S = [p / len(text) for p in sp]
    P = [p / dur for p in pauses]
    m, n, c = len(S), len(P), 0.05
    INF = 1e9
    dp = [[INF] * (n + 1) for _ in range(m + 1)]
    bk = [[None] * (n + 1) for _ in range(m + 1)]
    dp[0][0] = 0.0
    for i in range(m + 1):
        for j in range(n + 1):
            if dp[i][j] >= INF:
                continue
            if i < m and dp[i][j] + c < dp[i + 1][j]:
                dp[i + 1][j], bk[i + 1][j] = dp[i][j] + c, (i, j, False)
            if j < n and dp[i][j] + c < dp[i][j + 1]:
                dp[i][j + 1], bk[i][j + 1] = dp[i][j] + c, (i, j, False)
            if i < m and j < n:
                w = dp[i][j] + abs(S[i] - P[j]) * 2
                if w < dp[i + 1][j + 1]:
                    dp[i + 1][j + 1], bk[i + 1][j + 1] = w, (i, j, True)
    i, j, out = m, n, {}
    while (i, j) != (0, 0):
        pi, pj, hit = bk[i][j]
        if hit:
            out[sp[pi]] = pauses[pj]
        i, j = pi, pj
    return out


def beats(i, markers):
    """Scene-local start times of each beat. The first beat starts at 0; every other beat starts where its marker phrase is spoken: the pause that
    precedes the phrase (found by aligning the text's phrase breaks to the pauses in the audio), or an interpolation between matched pauses."""
    text = DOC["scenes"][i - 1]["lines"][0]["text"]
    d = TIM[str(i)]["dur"]
    marks = MARKS.get(str(i), {})
    match = _align(text, d, TIM[str(i)]["pauses"])
    keys_ = sorted(match)
    out = [0.0]
    for m in markers[1:]:
        k = text.find(m)
        assert k >= 0, f"marker not in scene {i}: {m}"
        if m in marks:                                   # the model's timestamp of the phrase, snapped to a pause
            out.append(LEAD + marks[m]["snapped"])
            continue
        prev = max([x for x in keys_ if x < k], default=None)
        if prev is not None and k - prev <= 1:
            tt = match[prev]
        else:
            nxt = min([x for x in keys_ if x >= k], default=None)
            ta, ca = (match[prev], prev) if prev is not None else (0.0, 0)
            tb, cb = (match[nxt], nxt) if nxt is not None else (d, len(text))
            tt = ta + (tb - ta) * (k - ca) / max(1, cb - ca)
        out.append(LEAD + tt)
    for j in range(1, len(out)):
        out[j] = max(out[j], out[j - 1] + 1.5)
    return out


def which(t, b):
    """Index of the beat active at t."""
    k = 0
    for j, bt in enumerate(b):
        if t >= bt:
            k = j
    return k


def seg2(t, a, b):
    return seg(t, a, b)


_T = [0.0]
SWAY = mk(((-62, 160, 24), (-36, 200, 16)), ((62, 160, 24), (36, 200, 16)))


def tick(t):
    """Call first in every draw(): the scene time for idle motion and marching dashes."""
    _T[0] = t
    PH[0] = t


def _alive(kw, pose, seed):
    """Breathing, a slow sway and arms that never freeze, unless the scene already sets them."""
    t = _T[0]
    kw["lean"] = kw.get("lean", 0.0) + 1.5 * math.sin(t * 2.0 + seed)
    kw["bob"] = kw.get("bob", 0.0) + 1.6 * abs(math.sin(t * 2.0 + seed))
    kw.setdefault("blink_v", blink(t, 0.1 + seed * 0.37))
    if pose is REST and kw.get("walk") is None:
        pose = pl(REST, SWAY, 0.5 + 0.5 * math.sin(t * 1.3 + seed))
    return pose


def ton(cv, x, y, pose=REST, ex="neutral", k=1.15, th=40, **kw):
    pose = _alive(kw, pose, 0.3)
    actor(cv, "ton", x, y, th, pose, ex, k=k, **kw)


def chok(cv, x, y, pose=REST, ex="neutral", k=1.1, th=50, **kw):
    pose = _alive(kw, pose, 1.9)
    actor(cv, "chok", x, y, th, pose, ex, k=k, **kw)


def mouth_of(t, a, b, seed=0):
    """A voice command to a machine (not the narrator): the mouth flaps and the machine answers; this is rhythm, not speech."""
    return talk(t, a, b, seed)


def say_waves(cv, x, y, t, a, b, flip=False, col=(255, 255, 255)):
    if a <= t <= b:
        waves(cv, x, y, (t - a) * 1.2, n=3, r0=12, dr=11, col=col, a0=-45, a1=45, lw=3.4, flip=flip)


def pulse_ov(ov, t, amount=0.05):
    """Numbers that have fully appeared breathe a little, so a held graphic is never frozen."""
    ov[:] = [(txt, x, y, size * (1 + amount * math.sin(t * 4 + x * 0.01)) if a > 0.9 else size, col, a) for (txt, x, y, size, col, a) in ov]


def fr(t, BE, k, a, b):
    """Progress 0..1 of t inside the stretch [a, b] (as fractions 0..1) of beat k; BE = beat starts plus the end of the narration."""
    u = (t - BE[k]) / max(0.01, BE[k + 1] - BE[k])
    return seg(u, a, b)


def in_(t, BE, k, a, b):
    u = (t - BE[k]) / max(0.01, BE[k + 1] - BE[k])
    return a <= u < b
