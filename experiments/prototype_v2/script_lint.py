"""Offline checklist helper for 'รู้หรือไม่' scripts (docs/KNOWLEDGE_STORY_PLAYBOOK.md §5). No API, no TTS.

    python script_lint.py ../shorts/scripts/know_craving.json

Reads the same JSON the knowledge renderer uses (scenes[].lines[].text/say, props[].text, sources[]).
It only flags things for a human to review; it never edits the script.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

CHARS_PER_SEC = 12.0          # measured on Gemini narration in earlier episodes
LIST_WORDS = ("ข้อแรก", "ข้อที่หนึ่ง", "ข้อสอง", "ข้อที่สอง", "ข้อสาม", "ข้อที่สาม", "สรุปก็คือ", "ทั้งนี้")
EMPTY_HOOKS = ("เอ๊ะ!", "เอ๊ะ", "เดี๋ยวก่อน!", "รู้หรือไม่ว่า", "สวัสดีค่ะ", "สวัสดีครับ")
TTS_RISKY = ("ราว", "ฝั่ง", "ทาย", "สุกๆ ดิบๆ", "สุก ๆ ดิบ ๆ", "ค่าห้อง", "แฟ้ม", "เบาะแส")
# Pillow without raqm drops a tone mark that sits over an upper vowel (e.g. ที่ นี้ เนื้อ)
STACKED = re.compile("[ัิ-ื็][่-๋]")
ARROWS = re.compile("[←-⇿]")


def lint(path: Path) -> list[str]:
    d = json.loads(path.read_text(encoding="utf-8"))
    out: list[str] = []
    spoken = []
    for si, sc in enumerate(d.get("scenes", [])):
        where = f"scene {si + 1} ({sc.get('name', '')})"
        for li, ln in enumerate(sc.get("lines", [])):
            say = ln.get("say") or ln.get("text", "")
            spoken.append(say)
            first = say.strip().split(" ")[0] if say.strip() else ""
            for w in LIST_WORDS:
                if w in say:
                    out.append(f"{where} line {li + 1}: list/report word '{w}' - turn it into an event or comparison")
            for w in EMPTY_HOOKS:
                if say.strip().startswith(w):
                    out.append(f"{where} line {li + 1}: opens with '{w}' - is there an event that earns it?")
                    break
            for w in TTS_RISKY:
                if w in say:
                    out.append(f"{where} line {li + 1}: '{w}' was misheard by TTS before")
            if first and any(first.startswith(w) for w in ("แฟ้ม", "เบาะแส", "แต่")):
                out.append(f"{where} line {li + 1}: first word '{first}' is often garbled - lead with an easy word")
        for pi, pr in enumerate(sc.get("props", []) or []):
            txt = pr.get("text") or ""
            if STACKED.search(txt):
                out.append(f"{where} prop {pi + 1}: on-screen '{txt}' has a tone mark over an upper vowel (renders wrong)")
            if ARROWS.search(txt):
                out.append(f"{where} prop {pi + 1}: on-screen '{txt}' has an arrow glyph (missing in the Thai font)")
    srcs = d.get("sources") or []
    if not srcs:
        out.append("no sources[] - every fact needs a checkable source")
    for i, s in enumerate(srcs):
        if not s.get("url"):
            out.append(f"source {i + 1}: no url")
    seen = {}
    for s in spoken:
        for sent in re.split(r"[ ]{2,}|[!?]", s):
            sent = sent.strip()
            if len(sent) >= 25:
                seen[sent] = seen.get(sent, 0) + 1
    out += [f"repeated sentence x{n}: '{s[:40]}...'" for s, n in seen.items() if n > 1]
    chars = sum(len(s.replace(" ", "")) for s in spoken)
    out.append(f"info: ~{chars} spoken chars = ~{chars / CHARS_PER_SEC / 60:.1f} min of narration (estimate)")
    return out


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    sys.stdout.reconfigure(encoding="utf-8")
    for p in sys.argv[1:]:
        print(f"== {p}")
        for msg in lint(Path(p)):
            print(" -", msg)


if __name__ == "__main__":
    main()
