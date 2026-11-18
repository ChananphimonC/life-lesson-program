"""Deterministic safeguards that run BEFORE any LLM judgement.

1. `screen_topic` -- sensitive-topic pre-filter (PRODUCT.md §5, AI_DESIGN.md §6):
   self-harm, suicide, severe crisis, abuse, clinical/diagnostic framing.
   A match rejects the topic; it is never rewritten into a "softer" version.
2. `lexical_flags` -- cheap pattern hints (prescriptive words, religious terms)
   handed to the Critic as evidence to weigh. Dialogue by a character can
   legitimately contain "อย่า", so these are hints, not automatic failures.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from life_lesson.errors import SensitiveTopicError
from life_lesson.generation.schema import ScriptOutput

# Substring match (Thai has no word spaces); English matched case-insensitively.
SENSITIVE_TERMS = [
    "ฆ่าตัวตาย", "อยากตาย", "ปลิดชีวิต", "จบชีวิต", "ทำร้ายตัวเอง", "กรีดข้อมือ",
    "โรคซึมเศร้า", "ไบโพลาร์", "โรคจิต", "วินิจฉัย", "ผู้ป่วยจิตเวช",
    "ถูกทำร้าย", "ล่วงละเมิด", "ข่มขืน", "ความรุนแรงในครอบครัว",
    "suicide", "suicidal", "self-harm", "self harm", "kill myself", "rape", "abuse",
    "depression disorder", "bipolar", "diagnos",
]

_PRESCRIPTIVE = ["ควร", "ต้อง", "จง", "อย่า", "ห้าม", "ลอง", "คุณจะต้อง"]
_RELIGIOUS = ["พระพุทธเจ้า", "ธรรมะ", "พุทธ", "กรรม", "นิพพาน", "พระเจ้า", "คัมภีร์", "สวดมนต์", "บาป", "บุญ"]
_ATTRIBUTION = re.compile(r"(เคยกล่าวว่า|กล่าวไว้ว่า|ตามที่.{0,12}พูดไว้|นักปราชญ์|ผู้เฒ่าว่า|ดั่งที่เขาว่า|quote)", re.I)
_CLICHE = ["อย่ายอมแพ้", "พรุ่งนี้จะดีขึ้น", "ทุกอย่างจะผ่านไป", "เชื่อในตัวเอง", "ไม่มีอะไรเป็นไปไม่ได้"]


def screen_topic(topic_text: str, theme: str | None = None) -> None:
    haystack = f"{topic_text} {theme or ''}".lower()
    hits = [t for t in SENSITIVE_TERMS if t.lower() in haystack]
    if hits:
        raise SensitiveTopicError(
            f"Topic rejected by sensitive-topic filter (matched: {', '.join(hits)}). "
            "Choose a different topic; the system does not soften these themes."
        )


@dataclass(frozen=True)
class LexicalFlag:
    category: str
    term: str
    block_sequence: int


def lexical_flags(script: ScriptOutput) -> list[LexicalFlag]:
    flags: list[LexicalFlag] = []
    for block in script.script_blocks:
        text = block.text
        for term in _PRESCRIPTIVE:
            if term in text:
                flags.append(LexicalFlag("prescriptive_advice", term, block.sequence))
        for term in _RELIGIOUS:
            if term in text:
                flags.append(LexicalFlag("religious_teaching", term, block.sequence))
        for term in _CLICHE:
            if term in text:
                flags.append(LexicalFlag("generic_cliche", term, block.sequence))
        m = _ATTRIBUTION.search(text)
        if m:
            flags.append(LexicalFlag("quote_or_attribution", m.group(0), block.sequence))
        for term in SENSITIVE_TERMS:
            if term.lower() in text.lower():
                flags.append(LexicalFlag("therapy_or_clinical", term, block.sequence))
    return flags
