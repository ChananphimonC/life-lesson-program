"""Script doctor, part 1: an offline "why isn't this gripping?" linter.

Scores a script 0-100 on the things that actually make narrated stories hold
attention (docs/STORYTELLING_BIBLE.md, docs/KNOWLEDGE_STORY_PLAYBOOK.md) and
returns concrete, block-level findings that the punch-up rewrite pass can act
on. It is a heuristic, not a taste oracle: it catches the common, mechanical
failures (flat opening, no chapter-end hooks, flat tension curve, report-style
connectors, the narrator describing what the picture shows, repetition) and
leaves taste to the human reviewer.
"""

from __future__ import annotations

import re
import statistics
from collections import Counter
from dataclasses import dataclass, field

from life_lesson.generation.schema import ScriptOutput

HOOK_MARKERS = ("ไหม", "ทำไม", "ใคร", "อะไร", "ยังไง", "เมื่อไหร่", "ที่ไหน", "?", "แต่", "จนกระทั่ง", "ก่อนที่", "ยังไม่รู้", "ไม่มีใคร", "ไม่ได้", "แล้ว...")
GREETINGS = ("สวัสดี", "ยินดีต้อนรับ", "วันนี้เราจะ", "ในวิดีโอนี้", "ก่อนอื่น", "ขอต้อนรับ")
REPORT_CONNECTORS = ("ข้อแรก", "ข้อที่สอง", "ข้อสุดท้าย", "สรุปก็คือ", "ทั้งนี้", "กล่าวคือ", "อย่างไรก็ตาม", "นอกจากนี้", "ดังนั้น", "ประการแรก", "ประการที่สอง")
VISUAL_NARRATION = ("ยิ้ม", "หัวเราะ", "สีหน้า", "ใส่เสื้อ", "สวมเสื้อ", "ท่าทาง", "ตาเบิกกว้าง", "คิ้วขมวด", "ทำหน้า", "พยักหน้า", "ส่ายหัว", "แววตา")
TTS_RISKY = ("ราว", "ฝั่ง", "ทาย", "สุก ๆ ดิบ ๆ", "ค่าห้อง")
SUMMARY_ENDINGS = ("สรุป", "บทเรียน", "ข้อคิด", "เพราะฉะนั้น", "ดังนั้น", "สิ่งที่เราได้เรียนรู้")

SEVERITY_PENALTY = {"high": 15, "med": 8, "low": 3}


# Findings a keyword/regex check can establish reliably. Everything else is a
# SOFT signal (a rough proxy for "feels gripping"): shown to the rewriter as a
# hint and counted at half weight, but never allowed to decide whether a
# rewrite is better -- only the pairwise reader judge or a human can do that.
SOFT_CODES = {"weak_hook", "flat_chapter_ends", "few_open_loops", "monotone_rhythm", "early_peak", "peak_at_end"}


@dataclass
class Finding:
    code: str
    severity: str  # high | med | low
    message: str
    blocks: list[int] = field(default_factory=list)
    penalty: int = 0

    @property
    def soft(self) -> bool:
        return self.code in SOFT_CODES


@dataclass
class LintReport:
    score: int
    findings: list[Finding]
    stats: dict

    @property
    def high(self) -> list[Finding]:
        return [f for f in self.findings if f.severity == "high"]

    @property
    def objective_penalty(self) -> int:
        """Penalty from mechanically verifiable problems only."""
        return sum(f.penalty for f in self.findings if not f.soft)

    def summary(self) -> str:
        lines = [f"score {self.score}/100"]
        for f in self.findings:
            tag = f"{f.severity}/soft" if f.soft else f.severity
            where = f" (blocks {f.blocks})" if f.blocks else ""
            lines.append(f"- [{tag}] {f.code}: {f.message}{where}")
        return "\n".join(lines)


def _has(text: str, markers) -> bool:
    return any(m in text for m in markers)


def _chapters(script: ScriptOutput) -> list[list]:
    """Group consecutive blocks by chapter_title; fall back to phase."""
    groups, last = [], object()
    for b in script.script_blocks:
        key = (b.chapter_title or "").strip() or f"phase:{b.phase}"
        if key != last:
            groups.append([])
            last = key
        groups[-1].append(b)
    return groups


def lint_script(script: ScriptOutput, series: str = "reflection") -> LintReport:
    blocks = script.script_blocks
    findings: list[Finding] = []

    def add(code, severity, message, blocks_=None, penalty=None):
        findings.append(Finding(code, severity, message, blocks_ or [], penalty if penalty is not None else SEVERITY_PENALTY[severity]))

    # 1. the opening: concrete situation + a reason to keep listening, never a greeting
    opening = blocks[0].text[:160]
    if _has(opening, GREETINGS):
        add("greeting_opening", "high", "Opens with a greeting/introduction. Start inside a concrete moment with something unresolved.", [blocks[0].sequence])
    elif not _has(opening, HOOK_MARKERS):
        add("weak_hook", "med", "The first sentences set no question or tension. Open mid-moment and plant one unanswered question in the first 15 seconds.", [blocks[0].sequence])

    # 2. chapter-end hooks: every chapter except the last should end leaning forward
    chapters = _chapters(script)
    if len(chapters) >= 3:
        flat = [c[-1].sequence for c in chapters[:-1] if not _has(c[-1].text[-120:], HOOK_MARKERS)]
        if len(flat) > len(chapters[:-1]) * 0.5:
            add("flat_chapter_ends", "med", f"{len(flat)} of {len(chapters) - 1} chapters end without a hook. End each chapter on a new question, a reversal or a ticking clock.", flat)

    # 3. open loops early
    text_all = " ".join(b.text for b in blocks)
    head = text_all[: max(1, int(len(text_all) * 0.35))]
    qwords = sum(head.count(w) for w in ("ไหม", "ทำไม", "ใคร", "อะไร", "ยังไง", "ที่ไหน", "?"))
    if qwords < 2:
        add("few_open_loops", "med", "Fewer than two open questions in the first third. Keep at least one unanswered question alive at all times.")

    # 4. repetition (the motif is allowed to repeat)
    motif = (script.metadata.motif or "").strip()
    shingles = Counter()
    for b in blocks:
        t = re.sub(r"\s+", "", b.text)
        seen = {t[i : i + 9] for i in range(0, max(1, len(t) - 8))}
        shingles.update(seen)
    repeated = [s for s, c in shingles.items() if c >= 3 and (not motif or s not in motif and motif not in s)]
    if len(repeated) >= 3:
        add("repetition", "med", "Phrases repeat across blocks (" + ", ".join(repeated[:3]) + "). Say each thing once; let only the motif return.")

    # 5. report-style connectors and filler
    used = [c for c in REPORT_CONNECTORS if c in text_all]
    if used:
        add("report_style", "med", "Report/essay connectors make it sound read, not told: " + ", ".join(used) + ". Tell it like a friend would.", penalty=min(15, 5 * len(used)))

    # 6. narrator describing what the picture shows (TTS reads it aloud and it duplicates the image)
    vis = [(b.sequence, w) for b in blocks for w in VISUAL_NARRATION if w in b.text]
    if vis:
        add("narrating_the_picture", "low", "Narration describes faces/gestures/clothes (" + ", ".join(sorted({w for _, w in vis})) + "). Leave that to the picture; narrate what can't be seen.", sorted({s for s, _ in vis}), penalty=min(12, 3 * len(vis)))

    # 7. digits and risky words for the voice
    if re.search(r"\d", text_all):
        add("digits_in_narration", "low", "Digits in spoken text; write numbers as spoken Thai words so the voice reads them right.", [b.sequence for b in blocks if re.search(r"\d", b.text)][:6])
    # Thai has no spaces, so test the left edge only: "ราว" is risky, but "คราวนี้" (a consonant
    # precedes it) is a different word and is read correctly.
    risky = [w for w in TTS_RISKY if re.search(r"(?<![\u0e01-\u0e2e])" + re.escape(w), text_all)]
    if risky:
        add("tts_risky_words", "low", "Words the TTS often mispronounces: " + ", ".join(risky) + ". Re-listen or reword.", penalty=min(6, 2 * len(risky)))

    # 8. tension curve (needs moods)
    ts = [b.mood.tension for b in blocks if b.mood]
    stats: dict = {"blocks": len(blocks), "chapters": len(chapters), "chars": len(text_all)}
    if len(ts) >= 4:
        stats["tension_min_max"] = (min(ts), max(ts))
        peak = ts.index(max(ts)) / (len(ts) - 1)
        stats["peak_at"] = round(peak, 2)
        half = len(ts) // 2
        if max(ts) - min(ts) < 2:
            add("flat_tension", "high", "Tension never moves (range < 2). Build a curve: low or sharp start, climb through the middle, peak, then fall without resolving.")
        elif sum(ts[half:]) / len(ts[half:]) < sum(ts[:half]) / half:
            add("tension_falls", "med", "Tension is lower in the second half than the first; the story should climb toward the peak.")
        if series == "reflection" and peak > 0.97:
            add("peak_at_end", "low", "Peak lands on the last block; a reflection should let tension fall in the outro.")
        elif peak < 0.4:
            add("early_peak", "med", "The peak comes too early; hold something back for the turn.")
    else:
        stats["tension_min_max"] = None

    # 9. rhythm
    segments = [len(s) for b in blocks for s in b.text.split() if s]
    if len(segments) >= 8:
        sd = statistics.pstdev(segments)
        stats["segment_sd"] = round(sd, 1)
        if sd < 4.5:
            add("monotone_rhythm", "low", "Sentences are all about the same length. Mix short punches with one long breath per chapter.")
        if sum(1 for n in segments if n > 45) > len(segments) * 0.35:
            add("run_on_sentences", "med", "Many very long unbroken sentences; split them for the ear.")

    # 10. series-specific
    if series == "knowledge" and not script.facts:
        add("no_sources", "high", "Knowledge series needs sourced facts (name each source); none are listed.")
    if series == "reflection" and _has(blocks[-1].text[-160:], SUMMARY_ENDINGS):
        add("summarising_ending", "med", "The ending sums up or teaches. A reflection should stay open.", [blocks[-1].sequence])

    for f in findings:
        if f.soft:
            f.penalty = (f.penalty + 1) // 2  # soft signals count at half weight
    score = max(0, 100 - sum(f.penalty for f in findings))
    stats["findings"] = len(findings)
    return LintReport(score, findings, stats)
