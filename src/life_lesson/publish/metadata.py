"""Publishing metadata: YouTube description (chapters, real facts, credits),
thumbnail spec, and the human review checklist (docs/STYLE_GUIDE.md §6, §8, §10-12).

Pure functions over a validated `ScriptOutput` plus per-block start times, so
they are fully testable without audio/video tooling.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from life_lesson.generation.formats import FormatSpec
from life_lesson.generation.schema import ScriptOutput

MIN_CHAPTER_SECONDS = 10  # YouTube requires chapters >= 10s
MIN_CHAPTERS = 3

FICTION_DISCLAIMER = "ตัวละคร เหตุการณ์ และสถานที่ในเรื่องเป็นเรื่องแต่ง ตัวเลขเป็นค่าประมาณ"
AI_DISCLOSURE = "ภาพ เสียงบรรยาย และดนตรี สร้างด้วย AI"


def format_timestamp(ms: int) -> str:
    total = max(0, ms) // 1000
    h, rem = divmod(total, 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


@dataclass(frozen=True)
class Chapter:
    start_ms: int
    title: str


def build_chapters(script: ScriptOutput, block_starts_ms: list[int]) -> list[Chapter]:
    """Group consecutive blocks sharing a chapter_title; enforce YouTube rules.

    Returns [] when chapters cannot satisfy YouTube's rules (fewer than 3, or
    no titles) -- the description then simply omits the chapter list.
    """
    if len(block_starts_ms) != len(script.script_blocks):
        raise ValueError("block_starts_ms must have one entry per script block")

    chapters: list[Chapter] = []
    last_title: str | None = None
    for block, start in zip(script.script_blocks, block_starts_ms):
        title = (block.chapter_title or "").strip()
        if not title or title == last_title:
            continue
        chapters.append(Chapter(start, title))
        last_title = title

    if not chapters:
        return []
    chapters[0] = Chapter(0, chapters[0].title)  # must start at 0:00

    # Merge too-short chapters into the previous one.
    merged: list[Chapter] = [chapters[0]]
    for ch in chapters[1:]:
        if ch.start_ms - merged[-1].start_ms < MIN_CHAPTER_SECONDS * 1000:
            continue
        merged.append(ch)
    return merged if len(merged) >= MIN_CHAPTERS else []


def build_description(
    script: ScriptOutput,
    spec: FormatSpec,
    block_starts_ms: list[int],
    *,
    credits: list[str] | None = None,
    channel_line: str | None = None,
) -> str:
    parts: list[str] = []
    if script.summary:
        parts.append(script.summary.strip())

    if not spec.is_vertical:
        chapters = build_chapters(script, block_starts_ms)
        if chapters:
            parts.append(
                "\n".join(f"{format_timestamp(c.start_ms)} {c.title}" for c in chapters)
            )

    facts = [f for f in script.facts if f.claim.strip()]
    if facts:
        lines = ["ข้อมูลจริงในเรื่อง:"]
        for f in facts:
            lines.append(f"• {f.claim.strip()}")
        parts.append("\n".join(lines))
        sources = [f.source_hint.strip() for f in facts if f.source_hint]
        if sources:
            uniq = list(dict.fromkeys(sources))
            parts.append("แหล่งข้อมูล: " + ", ".join(uniq))

    if channel_line:
        parts.append(channel_line)
    parts.append(FICTION_DISCLAIMER)

    credit_lines = [AI_DISCLOSURE] + list(credits or [])
    parts.append("\n".join(credit_lines))

    if spec.name == "short":
        parts.append("#Shorts #ชีวิต #เล่าเรื่อง")
    return "\n\n".join(parts) + "\n"


def build_title(script: ScriptOutput, spec: FormatSpec) -> str:
    suffix = {"long": "เรื่องยาว · ตอนเดียวจบ", "standard": "ตอนเดียวจบ", "short": ""}[spec.name]
    title = script.title.strip()
    full = f"{title} ({suffix})" if suffix else title
    return full if len(full) <= 60 else title[:60]


def _split_headline(title: str) -> tuple[str, str]:
    """Two thumbnail lines without ever cutting a word.

    Thai has no spaces, so slicing at a character index breaks words in half.
    Split at a space if there is one; else at the word boundary nearest the
    middle if PyThaiNLP is installed; else keep a single line (the renderer
    shrinks it to fit).
    """
    title = title.strip()
    words = title.split()
    if len(words) >= 2:
        mid = (len(words) + 1) // 2
        return " ".join(words[:mid]), " ".join(words[mid:])
    try:  # optional dependency: pip install pythainlp
        from pythainlp.tokenize import word_tokenize

        tokens = [t for t in word_tokenize(title, keep_whitespace=False) if t.strip()]
        if len(tokens) >= 2:
            best = min(range(1, len(tokens)), key=lambda i: abs(len("".join(tokens[:i])) - len("".join(tokens[i:]))))
            return "".join(tokens[:best]), "".join(tokens[best:])
    except Exception:  # noqa: BLE001 - not installed / data missing: fall through
        pass
    return title, ""


SUBLINE_MAX_CHARS = 30


def _teaser(summary: str | None, max_chars: int = SUBLINE_MAX_CHARS) -> str:
    """A one-line cover teaser from the summary, cut only at a space (never mid-word).

    Thai has no spaces between words, so slicing at a character count breaks words
    ("...ตามสั่ง" -> "...ตามสั"). Prefer the first clause; if none fits, show no sub-line.
    """
    first = (summary or "").split("\n")[0].strip()
    if len(first) <= max_chars:
        return first
    cut = first.rfind(" ", 0, max_chars + 1)
    return first[:cut].strip() if cut >= 8 else ""


def build_thumbnail_spec(script: ScriptOutput, spec: FormatSpec, duration_ms: int) -> dict:
    line1, line2 = _split_headline(script.title.strip())
    first = script.script_blocks[0]
    minutes = max(1, round(duration_ms / 60000))
    pill = f"{spec.label_th} · {minutes} นาที" if spec.name != "short" else "Shorts"
    main = script.characters[0] if script.characters else None
    safe = (
        {"bottom_pct": 20, "right_pct": 12} if spec.is_vertical else {"bottom_pct": 8, "right_pct": 8}
    )
    return {
        "size": [spec.width, spec.height],
        "format": spec.name,
        "context_tag": first.time_label or first.chapter_title,
        "headline_line1": line1,
        "headline_line2": line2,
        "subline": script.subline or _teaser(script.summary),
        "pill": pill,
        "character": (
            {"name": main.name, "outfit": main.outfit, "palette": main.palette}
            if main
            else None
        ),
        "visual_cue": first.visual_cue,
        "safe_zone": safe,
        "rules": [
            "ตัวหนังสืออ่านออกที่ 160px กว้าง",
            "ตัวละครหรือวัตถุเดียว พื้นหลังมืด คอนทราสต์สูง",
            "ไม่หลอกลวง/ไม่สัญญาเกินเรื่อง/ไม่ใช้คำสั่งต่อผู้ชม",
        ],
    }


def build_review_checklist(script: ScriptOutput, spec: FormatSpec) -> str:
    """Human QA list (STYLE_GUIDE.md §10-12) pre-filled with auto-detected warnings."""
    warnings: list[str] = []
    low = [f.claim for f in script.facts if f.confidence == "low"]
    if low:
        warnings.append(f"ข้อเท็จจริงความมั่นใจต่ำ {len(low)} ข้อ — ตรวจแหล่งข้อมูลก่อนเผยแพร่")
    if not script.facts:
        warnings.append("ไม่มีรายการ facts — ถ้าเรื่องอ้างข้อมูลจริง ให้เพิ่มพร้อมแหล่งที่มา")
    missing_cues = [b.sequence for b in script.script_blocks if not b.visual_cue]
    if missing_cues:
        warnings.append(f"บทที่ไม่มี visual_cue: {missing_cues[:8]}")
    for ch in script.characters:
        for b in script.script_blocks:
            cue = b.visual_cue or ""
            if ch.name in cue and ch.outfit and ch.outfit not in cue:
                warnings.append(
                    f"บท {b.sequence}: cue พูดถึง {ch.name} แต่ไม่ระบุชุดตาม character sheet"
                )
    lines = ["# Review checklist", f"ตอน: {script.title} ({spec.name})", ""]
    if warnings:
        lines += ["## คำเตือนอัตโนมัติ"] + [f"- ⚠ {w}" for w in warnings] + [""]
    lines += [
        "## เสียงพากย์ (STYLE_GUIDE §10)",
        "- [ ] ฟังครบทั้งไฟล์ ออกเสียงตัวเลข/หน่วย/วรรณยุกต์ถูก",
        "- [ ] เสียงเดียวตลอดเรื่อง ไม่เร่ง ไม่เงียบเกินตั้งใจ",
        "- [ ] ระดับเสียงสมดุล ไม่คลิปแตก",
        "## ฉาก/ตัวละคร (§11, §13)",
        "- [ ] ภาพต่อเนื่อง ชุดตัวละครตรงตาม character sheet",
        "- [ ] ไม่มีโลโก้/บุคคลจริง/ภาพรุนแรง",
        "## เนื้อหา (PRODUCT §3, §5)",
        "- [ ] ไม่มีคำสั่ง/คำสอน/คำคม/อ้างศาสนา; ตอนจบเปิด",
        "- [ ] ไม่แตะหัวข้ออ่อนไหว",
        "## เครดิต/เผยแพร่ (§12)",
        "- [ ] แหล่งข้อมูลและ license ของพื้นหลัง/ดนตรีครบ",
        "- [ ] ติ๊ก 'altered or synthetic content' ใน YouTube Studio",
        "- [ ] Thumbnail อ่านออกที่ขนาดเล็ก",
    ]
    return "\n".join(lines) + "\n"


def write_publish_bundle(
    out_dir: Path,
    script: ScriptOutput,
    spec: FormatSpec,
    block_starts_ms: list[int],
    duration_ms: int,
    *,
    credits: list[str] | None = None,
    channel_line: str | None = None,
) -> dict[str, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "title": out_dir / "title.txt",
        "description": out_dir / "description.txt",
        "thumbnail": out_dir / "thumbnail.json",
        "review": out_dir / "review_checklist.md",
    }
    paths["title"].write_text(build_title(script, spec) + "\n", encoding="utf-8")
    paths["description"].write_text(
        build_description(script, spec, block_starts_ms, credits=credits, channel_line=channel_line), encoding="utf-8"
    )
    paths["thumbnail"].write_text(
        json.dumps(build_thumbnail_spec(script, spec, duration_ms), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    paths["review"].write_text(build_review_checklist(script, spec), encoding="utf-8")
    return paths
