"""Data-driven story scenes: a story is ONE json file (script text + a 'stage' list per scene), no per-episode Python.

    <root>/<story>/story.json   scenes[i] = {name, lines:[{speaker, text, say}], stage:[beat, beat, ...]}
    <root>/<story>/audio/timing.json, marks.json   (written by voice_story.py)

A beat (starts when its 'at' phrase is spoken; the first beat starts with the scene):
    {"at": "phrase", "bg": "bedroom", "bgkw": {...},
     "chars": [{"who": "phum", "x": 400, "y": 700, "k": 0.9, "th": 30, "flip": false, "ex": "happy" | ["worried","happy"], "pose": "REST" | ["REST","CHEER"], "talk": true,
                "walk_to": 700, "from": 100, "lean": 0}],
     "props": [{"k": "coins", "x": 600, "y": 650, "s": 1.0, "kw": {...}, "at": 0.0, "z": "front"}],
     "ov": [{"text": "41,667", "x": 640, "y": 150, "size": 110, "col": [255,230,120], "at": 0.2}],
     "sfx": "ding"}
episode.py asks story_engine.build('gs_<story>_<i>') for the scene module (see episode.mod).
"""
from __future__ import annotations

import json
import math
import os
from pathlib import Path

import isl_chars  # noqa: F401
import money_cast  # noqa: F401
import money_cast2  # noqa: F401
from acting import *  # noqa: F401,F403
from props_uni import *  # noqa: F401,F403
import props_uni as PU
import props_future as PF
import rt_bg as RB
import isl_bg as IB
from fin_props import REG_BG as FIN_BG, REG_PROP
import pup_props  # noqa: F401  (the puppy story's dog / props / rooms register themselves into fin_props)

HERE = Path(__file__).resolve().parent
ROOT = Path(os.environ.get("STORY_ROOT", str(HERE / "stories")))
LEAD, TAIL = 0.7, 1.0
SWAY = mk(((-62, 160, 24), (-36, 200, 16)), ((62, 160, 24), (36, 200, 16)))
POSES_BY_NAME = dict(REST=REST, CARRY=CARRY, HOLD_UP2=HOLD_UP2, ARMS_UP=ARMS_UP, CHEER=CHEER, PUSH=PUSH, HIP=HIP, HEADS=HEADS, SPREAD=SPREAD, CROSS=CROSS, POINT_UP=POINT_UP,
                     POINT_FWD=POINT_FWD, SHRUG=SHRUG, THINK=THINK, STOP=STOP, WRITE_A=WRITE_A, HAMMER=HAMMER, SCRUB=SCRUB)
EXPRESSIONS = ["neutral", "happy", "gape", "shout", "think", "deadpan", "plead", "gloat", "yikes", "aha", "smug", "laugh", "pant", "worried", "eager", "meh", "content", "determined", "surprised"]
CAST = ["jin", "pin", "mom", "tang", "beam", "nun", "coach", "phum", "bua", "kong", "manao", "em", "bam", "jake", "faa", "mariam", "omar", "guru", "chula", "thamma", "mahidol", "kaset", "kmitl", "kmutt", "silpa", "cmu", "kku", "psu", "captain", "yuelao"]


def _bg_table():
    t = dict(FIN_BG)
    for nm, mod in (("room", PF), ("bank", PF), ("supermarket", PF), ("rooftop", PF), ("workshop", PF), ("lecture", PU), ("library", PU), ("corridor", PU), ("cafe", RB), ("courtyard", RB),
                    ("lawn", RB), ("tea_garden", RB), ("beach", IB), ("sunset", IB), ("night_beach", IB), ("forest", IB)):
        fn = getattr(mod, nm, None) or getattr(mod, {"beach": "beach_morning", "sunset": "sunset_beach", "night_beach": "night_beach"}.get(nm, nm), None)
        if fn:
            t.setdefault(nm, fn)
    return t


REG_BG = _bg_table()


def load(story):
    return json.loads((ROOT / story / "story.json").read_text(encoding="utf-8"))


def validate(doc):
    """Return a list of problems (empty = ok): unknown backgrounds/props/characters/poses/expressions, markers that are not in the scene text."""
    bad = []
    for i, sc in enumerate(doc["scenes"], 1):
        text = " ".join(l["text"] for l in sc["lines"])
        stage = sc.get("stage") or []
        if not stage:
            bad.append(f"scene {i}: no stage")
        for j, b in enumerate(stage):
            if j and b.get("at", "") not in text:
                bad.append(f"scene {i} beat {j}: marker not in text: {b.get('at')!r}")
            if b.get("bg") not in REG_BG:
                bad.append(f"scene {i} beat {j}: unknown bg {b.get('bg')!r}")
            for c in b.get("chars", []):
                if c.get("who") not in CAST:
                    bad.append(f"scene {i} beat {j}: unknown character {c.get('who')!r}")
                for p in ([c.get("pose")] if isinstance(c.get("pose"), str) else (c.get("pose") or [])):
                    if p not in POSES_BY_NAME:
                        bad.append(f"scene {i} beat {j}: unknown pose {p!r}")
                for e in ([c.get("ex")] if isinstance(c.get("ex"), str) else (c.get("ex") or [])):
                    if e not in EXPRESSIONS:
                        bad.append(f"scene {i} beat {j}: unknown expression {e!r}")
            for p in b.get("props", []):
                if p.get("k") not in REG_PROP:
                    bad.append(f"scene {i} beat {j}: unknown prop {p.get('k')!r}")
    return bad


def _pick(v, u):
    if isinstance(v, str):
        return v
    return v[min(len(v) - 1, int(u * len(v)))]


class Scene:
    def __init__(self, story, i):
        self.story, self.I = story, i
        self.doc = load(story)
        self.sc = self.doc["scenes"][i - 1]
        self.text = " ".join(l["text"] for l in self.sc["lines"])
        aud = ROOT / story / "audio"
        tim = json.loads((aud / "timing.json").read_text(encoding="utf-8")) if (aud / "timing.json").is_file() else {}
        mk_ = json.loads((aud / "marks.json").read_text(encoding="utf-8")) if (aud / "marks.json").is_file() else {}
        d = tim.get(str(i), {}).get("dur", len(self.text) / 12.0)
        self.NAME = f"gs_{story}_{i}"
        self.DUR = round(d + LEAD + TAIL, 2)
        self.CAPS = []
        self.stage = self.sc["stage"]
        self.MARK = [b.get("at", "") for b in self.stage]
        marks = mk_.get(str(i), {})
        B = [0.0]
        for m in self.MARK[1:]:
            k = self.text.find(m)
            B.append(LEAD + (marks[m]["snapped"] if m in marks else k / max(1, len(self.text)) * d))
        for j in range(1, len(B)):
            B[j] = max(B[j], B[j - 1] + 1.5)
        self.B = B
        self.BE = B + [self.DUR - TAIL]
        self.CUES = []
        for j, b in enumerate(self.stage):
            if b.get("sfx"):
                self.CUES.append((B[j] + 0.8, b["sfx"], 0.5))

    # ------------------------------------------------------------------------------------------------------------- drawing
    def draw(self, cv, t, ov):
        _T[0] = t
        PF.PH[0] = t
        k = 0
        for j, bt in enumerate(self.B):
            if t >= bt:
                k = j
        b = self.stage[k]
        BE = self.BE
        u = max(0.0, min(1.0, (t - BE[k]) / max(0.01, BE[k + 1] - BE[k])))
        z = 1.0 + 0.05 * (u if k % 2 == 0 else 1.0 - u)           # a slow push-in / pull-out on every beat keeps the picture alive
        cv.push(640 * (1 - z), 360 * (1 - z), scale=z)
        REG_BG[b["bg"]](cv, t, **b.get("bgkw", {}))
        props = b.get("props", [])
        for p in props:
            if p.get("z", "back") == "back" and u >= p.get("at", 0.0):
                self._prop(cv, p, t)
        chars = sorted(enumerate(b.get("chars", [])), key=lambda ic: (ic[1].get("y", 700), ic[0]))
        for idx, c in chars:
            self._char(cv, c, t, k, u, idx)
        for p in props:
            if p.get("z", "back") == "front" and u >= p.get("at", 0.0):
                self._prop(cv, p, t)
        for o in b.get("ov", []):
            a = max(0.0, min(1.0, (u - o.get("at", 0.0)) / 0.12))
            if a > 0:
                ov.append((o["text"], o["x"], o["y"], o.get("size", 80), (255, 255, 255), a))       # one colour for every on-screen text, and it stays put (user's rule 2026-11-16)
        cv.pop()

    def _prop(self, cv, p, t):
        REG_PROP[p["k"]](cv, p.get("x", 640), p.get("y", 650), p.get("s", 1.0), t, **p.get("kw", {}))

    def _char(self, cv, c, t, k, u, idx):
        who = c["who"]
        x, y = c.get("x", 640), c.get("y", 700)
        kk = c.get("k", 0.9)
        th = c.get("th", 30)
        flip = c.get("flip", False)
        walking = False
        if "walk_to" in c:
            x0 = c.get("from", x)
            w = max(0.0, min(1.0, u / 0.7))
            x = x0 + (c["walk_to"] - x0) * ease(w)
            walking = 0.0 < w < 1.0
        ex = _pick(c.get("ex", "neutral"), u)
        pose_name = _pick(c.get("pose", "REST"), u)
        pose = POSES_BY_NAME[pose_name]
        seed = idx * 1.7
        lean = c.get("lean", 0.0) + 1.3 * math.sin(t * 2.0 + seed + len(who))
        bob = 1.2 * abs(math.sin(t * 2.0 + seed + len(who)))
        kw = dict(lean=lean, bob=bob, blink_v=blink(t, 0.1 + 0.37 * (seed + len(who))))
        if c.get("talk"):
            kw["mouth"] = talk(t, self.BE[k] + 0.4, self.BE[k + 1] - 0.5, idx)
            if self.BE[k] + 0.4 <= t <= self.BE[k + 1] - 0.5:
                waves(cv, x + (-70 if flip else 70) * kk, y - 270 * kk, (t - self.BE[k]) * 1.2, n=3, r0=12, dr=11, col=(255, 255, 255), a0=-45, a1=45, lw=3.4, flip=flip)
        if walking:
            ph = t * 7.0 + seed
            actor(cv, who, x, y, 60, walk_pose(ph), ex, k=kk, flip=flip, walk=dict(phase=ph, stride=16 * kk, lift=12 * kk), **kw)
        else:
            if pose is REST:
                pose = pl(REST, SWAY, 0.5 + 0.5 * math.sin(t * 1.3 + seed))
            actor(cv, who, x, y, th, pose, ex, k=kk, flip=flip, **kw)


_T = [0.0]


def build(name):
    """'gs_<story>_<i>' -> Scene (episode.mod hook)."""
    _, rest = name.split("gs_", 1)
    story, i = rest.rsplit("_", 1)
    return Scene(story, int(i))


def render_cover(story, out_png):
    """The cover still (no text; add_to_library draws the title): bg + chars + props from doc['cover']. 1280x720 png."""
    from engine import new_canvas
    doc = load(story)
    spec = doc["cover"]
    cv = new_canvas()
    cv.push(0, 0, scale=1.0)
    _T[0] = 2.0
    PF.PH[0] = 2.0
    sc = Scene.__new__(Scene)
    sc.BE, sc.B = [0.0, 100.0], [0.0]
    REG_BG[spec["bg"]](cv, 2.0, **spec.get("bgkw", {}))
    for p in spec.get("props", []):
        REG_PROP[p["k"]](cv, p.get("x", 640), p.get("y", 650), p.get("s", 1.0), 2.0, **p.get("kw", {}))
    for idx, c in enumerate(spec.get("chars", [])):
        sc._char(cv, c, 2.0, 0, 0.5, idx)
    cv.pop()
    cv.result().convert("RGB").save(out_png)
    return out_png
