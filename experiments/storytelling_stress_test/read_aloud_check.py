"""Text-only "read-aloud" analysis. It does NOT play or hear anything; it flags things a person reading the script aloud would
likely trip over, so a human can listen for them. Findings are heuristics, not verdicts.

    python read_aloud_check.py STRESS_TEST_SCRIPTS.md

Checks (per dialogue line unless noted)
  1. unbroken run of Thai text longer than RUN chars with no space/ellipsis/dash (nowhere to breathe)
  2. long single utterance (> LONG chars)
  3. formal/written-register or "AI-sounding" connectors and aphorism patterns
  4. numeric density: digits and spoken number words per scene (information dumping)
  5. talking-heads stretch: > STRETCH consecutive dialogue lines with no action/silent beat between them
  6. interview feel: share of a scene's lines that are questions
  7. scene with no action beat at all
  8. voice distinctness: each speaker's most frequent words/particles (does anyone sound the same?)
  9. phrases repeated verbatim across lines (3+ words by space split, Thai written with spaces only at phrase breaks)
Limits: no Thai tokenizer is installed (and none may be installed), so word-level checks rely on spaces and substrings.
"""

from __future__ import annotations

import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

RUN, LONG, STRETCH = 38, 150, 7
THAI = re.compile(r"[฀-๿]")
DIALOGUE = re.compile(r"^\*\*([^*]+?):\*\*\s*(.*)$")
HEADING = re.compile(r"^#### (ฉาก \d+[^⟦\n]*?)\s*(⟦T[^⟧]*⟧)?\s*$")
STORY = re.compile(r"^# (เรื่องที่ \d+[^\n]*)$")
FORMAL = ["อย่างไรก็ตาม", "ดังนั้น", "นอกจากนี้", "กล่าวคือ", "ในขณะเดียวกัน", "ซึ่งหมายความว่า", "โดยสรุป", "สิ่งสำคัญคือ",
          "อันที่จริง", "ล้วนแล้วแต่", "เป็นที่ทราบกันดี", "กล่าวได้ว่า", "ทั้งนี้", "ดังกล่าว", "ประการ"]
APHORISM = [r"คือสิ่งที่", r"นั่นแหละที่", r"ไม่ใช่[^ ]{1,12} แต่", r"ความจริงคือ", r"บางที[^ ]{0,10}เรา", r"ที่สุดของ"]
NUMWORDS = ["หนึ่ง", "สอง", "สาม", "สี่", "ห้า", "หก", "เจ็ด", "แปด", "เก้า", "สิบ", "ร้อย", "พัน", "หมื่น", "แสน", "ล้าน", "ยี่สิบ"]
QUESTION = ["ไหม", "หรือเปล่า", "เหรอ", "อะไร", "ทำไม", "ยังไง", "เท่าไหร่", "ที่ไหน", "ใคร", "กี่", "หรอ", "มั้ย"]
PARTICLES = ["ลูก", "ครับ", "ค่ะ", "นะ", "เอ็ง", "ยาย", "แล้ว", "ก็", "มัน", "จ้ะ", "เลย", "ไง", "สิ", "อ้าว", "โอ๊ย", "ป่ะ"]


def clean(s):
    return re.sub(r"\([^)]*\)", "", re.sub(r"\[[^\]]*\]", "", s)).strip()


def main():
    text = Path(sys.argv[1]).read_text(encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    story, scene = None, None
    data = defaultdict(lambda: defaultdict(lambda: dict(lines=[], since_action=0, max_stretch=0, actions=0)))
    order = []
    speakers = defaultdict(lambda: defaultdict(Counter))
    for ln in text.splitlines():
        m = STORY.match(ln)
        if m:
            story, scene = m.group(1), None
            continue
        h = HEADING.match(ln)
        if h:
            scene = h.group(1).strip()
            order.append((story, scene))
            continue
        if scene is None or ln.startswith(">") or ln.startswith("#"):
            continue
        d = DIALOGUE.match(ln)
        S = data[story][scene]
        if d:
            who = re.sub(r"\s*\(.*?\)", "", d.group(1)).strip()
            txt = clean(d.group(2))
            S["lines"].append((who, txt))
            S["since_action"] += 1
            S["max_stretch"] = max(S["max_stretch"], S["since_action"])
            for p in PARTICLES:
                # "สิ" must not match inside "สิบ" (ten); "ก็" etc. are plain substrings
                speakers[story][who][p] += len(re.findall("สิ(?!บ)", txt)) if p == "สิ" else txt.count(p)
            speakers[story][who]["_chars"] += len(THAI.findall(txt))
            speakers[story][who]["_lines"] += 1
        elif ln.startswith("["):
            S["since_action"] = 0
            S["actions"] += 1

    findings = 0
    for story, scene in order:
        S = data[story][scene]
        notes = []
        for who, txt in S["lines"]:
            runs = [len(THAI.findall(r)) for r in re.split(r"[ …—\-,!? ]+", txt)]
            if runs and max(runs) > RUN:
                notes.append(f"  - ไม่มีที่หายใจ {max(runs)} ตัวอักษร ({who}): «{txt[:60]}…»")
            n = len(THAI.findall(txt))
            if n > LONG:
                notes.append(f"  - บทพูดเดียวยาว {n} ตัวอักษร ({who}): «{txt[:60]}…»")
            for w in FORMAL:
                if w in txt:
                    notes.append(f"  - สำนวนทางการ '{w}' ({who}): «{txt[:60]}…»")
            for pat in APHORISM:
                mm = re.search(pat, txt)
                if mm:
                    notes.append(f"  - ลักษณะสุภาษิต/เขียนเกิน '{mm.group(0)}' ({who}): «{txt[:70]}…»")
        digits = sum(len(re.findall(r"\d+", t)) for _, t in S["lines"])
        words = sum(sum(t.count(w) for w in NUMWORDS) for _, t in S["lines"])
        if digits + words > 12:
            notes.append(f"  - ความหนาแน่นตัวเลขสูง: ตัวเลข/คำบอกจำนวน {digits + words} จุดในฉากเดียว")
        if S["max_stretch"] > STRETCH:
            notes.append(f"  - ช่วงคนพูดต่อเนื่องไม่มีภาพ/การกระทำคั่น {S['max_stretch']} บรรทัดติด")
        q = sum(1 for _, t in S["lines"] if any(t.rstrip().endswith(w) for w in QUESTION))
        if S["lines"] and q / len(S["lines"]) > 0.4 and len(S["lines"]) >= 5:
            notes.append(f"  - ฉากเป็นคำถามคำตอบเกือบทั้งหมด ({q}/{len(S['lines'])} บรรทัดลงท้ายเป็นคำถาม) เสี่ยงให้ความรู้สึกสัมภาษณ์")
        if S["actions"] == 0 and S["lines"]:
            notes.append("  - ฉากไม่มีบรรทัดภาพ/การกระทำเลย")
        print(f"{story} / {scene}: {len(S['lines'])} บรรทัดพูด, {S['actions']} บรรทัดภาพ, ตัวเลข {digits + words}, "
              f"คนพูดต่อเนื่องมากสุด {S['max_stretch']} บรรทัด" + ("" if notes else "  — ไม่มีข้อสังเกต"))
        for n in notes:
            print(n)
            findings += 1

    print("\n== ความต่างของเสียงตัวละคร (คำลงท้าย/ติดปากต่อ 100 ตัวอักษรที่พูด)")
    for story, sp in speakers.items():
        print(story)
        for who, c in sp.items():
            chars = max(1, c["_chars"])
            top = [(p, c[p]) for p in PARTICLES if c[p]]
            top.sort(key=lambda x: -x[1])
            share = ", ".join(f"{p}×{n} ({100 * n / chars:.1f}/100)" for p, n in top[:4]) or "—"
            print(f"  {who:<16} {c['_lines']:>3} บรรทัด {c['_chars']:>5} ตัวอักษร  {share}")

    print("\n== วลีที่ซ้ำคำต่อคำข้ามบรรทัด (≥ 12 ตัวอักษร)")
    seen = Counter()
    for story, scene in order:
        for who, txt in data[story][scene]["lines"]:
            for chunk in [c for c in re.split(r"[ …—!?]+", txt) if len(THAI.findall(c)) >= 12]:
                seen[(story, chunk)] += 1
    reps = [(k, v) for k, v in seen.items() if v > 1]
    for (story, chunk), v in reps:
        print(f"  ×{v} {story[:14]}: «{chunk}»")
    if not reps:
        print("  ไม่พบ")
    print(f"\nรวมข้อสังเกตทั้งหมด {findings} จุด (เป็นฮิวริสติก ต้องให้คนฟังตรวจ)")


if __name__ == "__main__":
    main()
