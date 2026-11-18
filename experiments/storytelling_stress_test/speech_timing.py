"""Duration estimate from the script's actual spoken text (not guessed, but not heard either).

    python speech_timing.py STRESS_TEST_SCRIPTS.md          -> per-scene and per-story table
    python speech_timing.py STRESS_TEST_SCRIPTS.md --fill   -> also rewrites the '⟦T…⟧' markers in scene headings

Method
  spoken seconds = Thai characters of dialogue (text in ( ) and [ ] removed) / RATE
  + GAP seconds for every spoken line (turn-taking breath)
  + the '⏱N' silent-action seconds written into the script.
RATE = 14.0 chars/s is the pooled speed of the project's own cached narration (8 lines, 3,527 chars / 251.6 s, range 10.9-16.4),
which already includes the narrator's natural pauses. Conversational Thai may be faster or slower; the 11 and 16.4 columns show the spread.
Limits: nothing was synthesised or listened to; overlapping speech/action is not modelled; scene lengths are +-15% at best.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

RATE, RATE_SLOW, RATE_FAST = 14.0, 11.0, 16.4
GAP = 0.35

THAI = re.compile(r"[฀-๿]")
DIALOGUE = re.compile(r"^\*\*([^*]+?):\*\*\s*(.*)$")
HEADING = re.compile(r"^#### (ฉาก \d+[^⟦\n]*?)\s*(⟦T[^⟧]*⟧)?\s*$")
STORY = re.compile(r"^# (เรื่องที่ \d+[^\n]*)$")
SILENT = re.compile(r"⏱(\d+(?:\.\d+)?)")


def clean(s: str) -> str:
    s = re.sub(r"\[[^\]]*\]", "", s)
    return re.sub(r"\([^)]*\)", "", s)


def parse(text: str):
    story, scene = None, None
    scenes = []
    for ln in text.splitlines():
        m = STORY.match(ln)
        if m:
            story = m.group(1)
            continue
        if HEADING.match(ln):
            scene = dict(story=story, name=HEADING.match(ln).group(1).strip(), chars=0, lines=0, silent=0.0)
            scenes.append(scene)
            continue
        if scene is None or ln.startswith("> ") or ln.startswith("#"):
            if ln.startswith("# "):
                scene = None
            continue
        d = DIALOGUE.match(ln)
        if d:
            scene["chars"] += len(THAI.findall(clean(d.group(2))))
            scene["lines"] += 1
            scene["silent"] += sum(float(x) for x in SILENT.findall(d.group(2)))
        elif ln.startswith("["):
            scene["silent"] += sum(float(x) for x in SILENT.findall(ln))
    return scenes


def secs(sc, rate):
    return sc["chars"] / rate + GAP * sc["lines"] + sc["silent"]


def mmss(x):
    return f"{int(x // 60)}:{int(round(x % 60)):02d}" if round(x % 60) < 60 else f"{int(x // 60) + 1}:00"


def main():
    path = Path(sys.argv[1])
    text = path.read_text(encoding="utf-8")
    scenes = parse(text)
    sys.stdout.reconfigure(encoding="utf-8")
    cur, t0 = None, 0.0
    totals = {}
    for sc in scenes:
        if sc["story"] != cur:
            cur, t0 = sc["story"], 0.0
        dur = secs(sc, RATE)
        sc["start"], sc["dur"] = t0, dur
        t0 += dur
        T = totals.setdefault(cur, dict(chars=0, lines=0, silent=0.0, slow=0.0, mid=0.0, fast=0.0))
        T["chars"] += sc["chars"]; T["lines"] += sc["lines"]; T["silent"] += sc["silent"]
        T["slow"] += secs(sc, RATE_SLOW); T["mid"] += dur; T["fast"] += secs(sc, RATE_FAST)
    print(f"{'story / scene':<46}{'chars':>6}{'lines':>6}{'silent s':>9}{'start':>7}{'dur s':>7}")
    cur = None
    for sc in scenes:
        if sc["story"] != cur:
            cur = sc["story"]
            print(f"\n== {cur}")
        print(f"  {sc['name']:<44}{sc['chars']:>6}{sc['lines']:>6}{sc['silent']:>9.0f}{mmss(sc['start']):>7}{sc['dur']:>7.0f}")
    print()
    for st, T in totals.items():
        sp = T["chars"] / RATE
        print(f"{st}: spoken text {T['chars']} Thai chars -> {sp:.0f} s of speech; silent action {T['silent']:.0f} s; "
              f"turn gaps {GAP * T['lines']:.0f} s; TOTAL {mmss(T['mid'])} (range {mmss(T['fast'])}-{mmss(T['slow'])} at 16.4-11 ch/s)")
    if "--fill" in sys.argv:
        out = []
        idx = 0
        for ln in text.splitlines():
            m = HEADING.match(ln)
            if m:
                sc = scenes[idx]
                idx += 1
                ln = f"#### {sc['name']} ⟦T เริ่ม {mmss(sc['start'])} · ยาว ≈ {sc['dur']:.0f} วิ⟧"
            out.append(ln)
        path.write_text("\n".join(out) + "\n", encoding="utf-8")
        print("filled", idx, "scene headings")


if __name__ == "__main__":
    main()
