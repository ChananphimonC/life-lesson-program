"""The Critic (AI_DESIGN.md §4): a SEPARATE pass from generation that checks the
full script against all seven prohibited categories, plus a bounded rewrite loop.

Process: critic -> (if any category fails) rewrite only the offending blocks ->
re-run the FULL critic on the revised script -> at most 3 rewrites, then give
up and let the caller mark the episode FAILED_REVIEW for a human.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Callable

from pydantic import BaseModel, Field, ValidationError

from life_lesson.errors import ScriptValidationError
from life_lesson.generation.formats import FormatSpec
from life_lesson.generation.safety import LexicalFlag, lexical_flags
from life_lesson.generation.schema import ScriptOutput, check_format, validate_script_json

CRITIC_PROMPT_NAME = "critic"
CRITIC_PROMPT_STAGE = "critic"
CRITIC_PROMPT_VERSION = "critic-v0.1.0"
MAX_REWRITES = 3

CATEGORIES: dict[str, str] = {
    "religious_teaching": "Teaches, references or paraphrases religious doctrine (Buddhist or any other).",
    "quote_or_attribution": "Quotes or closely paraphrases a named/recognisable person, author or book, with or without attribution.",
    "derivative_motivational": "A line closely resembles known motivational-content phrasing instead of an original observation.",
    "therapy_or_clinical": "Diagnoses, uses clinical terminology, implies professional mental-health guidance, or drifts into crisis territory (self-harm, abuse, violence, death).",
    "prescriptive_advice": "Tells the listener what to do/feel/believe (ควร, ต้อง, จง, อย่า, ลอง...). A CHARACTER saying it inside a scene is fine; the NARRATOR addressing the listener is not.",
    "generic_cliche": "Contains or ends on a stock inspirational line.",
    "manipulative_or_preachy": "Guilt-tripping, urgency pressure, a moral/lesson/summary at the end, or a tone pushing the listener to a conclusion instead of sitting with them.",
}


class CategoryResult(BaseModel):
    category: str
    passed: bool
    evidence: str = ""
    block_sequences: list[int] = Field(default_factory=list)


class CriticResult(BaseModel):
    results: list[CategoryResult]

    @property
    def passed(self) -> bool:
        return all(r.passed for r in self.results)

    @property
    def failed(self) -> list[CategoryResult]:
        return [r for r in self.results if not r.passed]


def parse_critic_result(raw: str) -> CriticResult:
    """Strict parse: every one of the 7 categories must be present exactly once."""
    text = raw.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        text = "\n".join(lines[1:-1] if lines[-1].strip().startswith("```") else lines[1:])
    try:
        result = CriticResult.model_validate(json.loads(text))
    except (json.JSONDecodeError, ValidationError) as exc:
        raise ScriptValidationError(f"Critic output is not valid: {exc}") from exc
    names = [r.category for r in result.results]
    missing = [c for c in CATEGORIES if c not in names]
    if missing or len(names) != len(set(names)) or set(names) - set(CATEGORIES):
        raise ScriptValidationError(
            f"Critic must return each of the {len(CATEGORIES)} categories exactly once; "
            f"missing={missing}, got={names}"
        )
    return result


def build_critic_prompt(script: ScriptOutput, flags: list[LexicalFlag]) -> str:
    cats = "\n".join(f'- "{k}": {v}' for k, v in CATEGORIES.items())
    hints = (
        "\n".join(f"- block {f.block_sequence}: '{f.term}' ({f.category})" for f in flags)
        if flags
        else "(none)"
    )
    return (
        "You are the Critic for a Thai life-REFLECTION channel. The product observes and "
        "offers perspective; it never advises, teaches, quotes, diagnoses or concludes.\n\n"
        "Review the FULL script below (all blocks, not only one phase) against these "
        f"{len(CATEGORIES)} categories:\n{cats}\n\n"
        "Automatic pattern hints (evidence to weigh, NOT verdicts):\n"
        f"{hints}\n\n"
        "Be strict about the narrator and the ending, lenient about in-scene dialogue.\n"
        'Respond with ONLY JSON: {"results": [{"category": "<id>", "passed": true|false, '
        '"evidence": "<short quote or reason>", "block_sequences": [<int>]}]} '
        "containing every category exactly once.\n\n"
        f"SCRIPT:\n{script.model_dump_json()}"
    )


def build_rewrite_prompt(script: ScriptOutput, failed: list[CategoryResult], spec: FormatSpec) -> str:
    problems = "\n".join(
        f"- {r.category} (blocks {r.block_sequences or 'unspecified'}): {r.evidence}" for r in failed
    )
    return (
        "Rewrite ONLY the offending blocks of this Thai life-reflection script so they are "
        "purely observational: no instructions, no moral, no quotes, no religion, no "
        "clinical language, no clichés, an open ending. Keep every other block, the "
        "sequence numbers, phases, chapter_titles, visual_cue, characters and facts "
        "unchanged. Keep the same number of blocks and the same JSON structure. "
        f"Format stays '{spec.name}'.\n\n"
        f"Problems found:\n{problems}\n\n"
        "Respond with ONLY the complete corrected JSON object.\n\n"
        f"SCRIPT:\n{script.model_dump_json()}"
    )


@dataclass
class CriticAttempt:
    attempt: int
    result: CriticResult
    flags: list[LexicalFlag] = field(default_factory=list)


@dataclass
class CriticOutcome:
    passed: bool
    script: ScriptOutput
    attempts: list[CriticAttempt]
    rewrites_used: int


def run_critic_loop(
    script: ScriptOutput,
    spec: FormatSpec,
    *,
    call_llm: Callable[[str], str],
    max_rewrites: int = MAX_REWRITES,
    on_critic: Callable[[int, CriticResult, str], None] | None = None,
    on_rewrite: Callable[[int, ScriptOutput], None] | None = None,
) -> CriticOutcome:
    attempts: list[CriticAttempt] = []
    rewrites = 0
    current = script
    while True:
        flags = lexical_flags(current)
        raw = call_llm(build_critic_prompt(current, flags))
        result = parse_critic_result(raw)
        attempts.append(CriticAttempt(len(attempts) + 1, result, flags))
        if on_critic:
            on_critic(len(attempts), result, raw)
        if result.passed:
            return CriticOutcome(True, current, attempts, rewrites)
        if rewrites >= max_rewrites:
            return CriticOutcome(False, current, attempts, rewrites)

        rewrites += 1
        raw_script = call_llm(build_rewrite_prompt(current, result.failed, spec))
        revised = validate_script_json(raw_script)
        check_format(revised, spec)
        revised.metadata.format = current.metadata.format
        revised.metadata.prompt_version = current.metadata.prompt_version
        revised.metadata.critic_attempt = rewrites + 1
        current = revised
        if on_rewrite:
            on_rewrite(rewrites, current)
