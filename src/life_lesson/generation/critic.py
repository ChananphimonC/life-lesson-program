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


SERIES = ("reflection", "knowledge", "story")

# Knowledge series ("รู้หรือไม่ / ทำไม"): information and advice are allowed, but claims need sources.
KNOWLEDGE_CATEGORIES: dict[str, str] = {
    "unsupported_claim": "States a real-world fact, number, study or date that is NOT backed by an entry in the script's `facts` with a named source, or invents a source.",
    "belief_vs_evidence": "Presents a belief, tradition, superstition or popular theory as proven fact, or mocks people who hold it; beliefs must be told as beliefs, respectfully, apart from the evidence.",
    "therapy_or_clinical": "Diagnoses, claims a cure/treatment effect, replaces a doctor, or recommends a specific security/investment; health content needs a short 'general knowledge, not medical advice' note.",
    "quote_or_attribution": "Quotes a named person, author or book without a source in `facts`, or fabricates a quote.",
    "manipulative_or_preachy": "Fear-mongering, guilt-tripping, urgency pressure, or lecturing in place of explaining.",
}

# Fiction ("เรื่องแต่งสนุก ๆ"): comedy/adventure, clearly invented.
STORY_CATEGORIES: dict[str, str] = {
    "unsupported_claim": "Presents a real-world fact, number or date as true without a source in `facts` (invented events are fine, but must stay clearly fictional).",
    "defamation_or_stereotype": "Mocks a real individual, or turns a real group/institution's stereotype into a hurtful joke; affectionate personification of institutions is fine.",
    "therapy_or_clinical": "Shows gore, graphic violence, real tragedies, self-harm, abuse or crisis territory, or makes clinical claims. Spooky folklore told as a story is fine.",
    "derivative_content": "Copies the plot, characters or distinctive lines of an existing film, show, game or book.",
    "manipulative_or_preachy": "Preaches a moral at the listener or pressures them instead of entertaining.",
}

CATEGORIES_BY_SERIES: dict[str, dict[str, str]] = {
    "reflection": CATEGORIES,
    "knowledge": KNOWLEDGE_CATEGORIES,
    "story": STORY_CATEGORIES,
}


def categories_for(series: str) -> dict[str, str]:
    try:
        return CATEGORIES_BY_SERIES[series]
    except KeyError:
        raise ScriptValidationError(f"Unknown series {series!r}; expected one of {list(SERIES)}") from None


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


def parse_critic_result(raw: str, series: str = "reflection") -> CriticResult:
    """Strict parse: every category of the series must be present exactly once."""
    cats = categories_for(series)
    text = raw.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        text = "\n".join(lines[1:-1] if lines[-1].strip().startswith("```") else lines[1:])
    try:
        result = CriticResult.model_validate(json.loads(text))
    except (json.JSONDecodeError, ValidationError) as exc:
        raise ScriptValidationError(f"Critic output is not valid: {exc}") from exc
    names = [r.category for r in result.results]
    missing = [c for c in cats if c not in names]
    if missing or len(names) != len(set(names)) or set(names) - set(cats):
        raise ScriptValidationError(
            f"Critic must return each of the {len(cats)} categories exactly once; "
            f"missing={missing}, got={names}"
        )
    return result


_CRITIC_INTRO = {
    "reflection": (
        "You are the Critic for a Thai life-REFLECTION channel. The product observes and "
        "offers perspective; it never advises, teaches, quotes, diagnoses or concludes."
    ),
    "knowledge": (
        "You are the Critic for a Thai explainer series (\"รู้หรือไม่ / ทำไม\"). Information and "
        "general advice are allowed and the ending need not be open; what matters is honesty: "
        "sourced facts, beliefs told as beliefs, no medical or investment claims."
    ),
    "story": (
        "You are the Critic for a Thai comedy/adventure fiction series. The story is clearly "
        "invented and may be funny; what matters is no defamation, no copied IP, no crisis or "
        "violence themes, and no real-world fact stated as true without a source."
    ),
}


def build_critic_prompt(script: ScriptOutput, flags: list[LexicalFlag], series: str = "reflection") -> str:
    cats = "\n".join(f'- "{k}": {v}' for k, v in categories_for(series).items())
    hints = (
        "\n".join(f"- block {f.block_sequence}: '{f.term}' ({f.category})" for f in flags)
        if flags
        else "(none)"
    )
    leniency = (
        "Be strict about the narrator and the ending, lenient about in-scene dialogue."
        if series == "reflection"
        else "Judge the narration against the script's own `facts` list; the narrator may be playful."
    )
    return (
        f"{_CRITIC_INTRO[series]}\n\n"
        "Review the FULL script below (all blocks, not only one phase) against these "
        f"{len(categories_for(series))} categories:\n{cats}\n\n"
        "Automatic pattern hints (evidence to weigh, NOT verdicts):\n"
        f"{hints}\n\n"
        f"{leniency}\n"
        'Respond with ONLY JSON: {"results": [{"category": "<id>", "passed": true|false, '
        '"evidence": "<short quote or reason>", "block_sequences": [<int>]}]} '
        "containing every category exactly once.\n\n"
        f"SCRIPT:\n{script.model_dump_json()}"
    )


def build_rewrite_prompt(script: ScriptOutput, failed: list[CategoryResult], spec: FormatSpec, series: str = "reflection") -> str:
    problems = "\n".join(
        f"- {r.category} (blocks {r.block_sequences or 'unspecified'}): {r.evidence}" for r in failed
    )
    return (
        (
            "Rewrite ONLY the offending blocks of this Thai life-reflection script so they are "
            "purely observational: no instructions, no moral, no quotes, no religion, no "
            "clinical language, no clichés, an open ending. "
            if series == "reflection"
            else f"Rewrite ONLY the offending blocks of this Thai {series} script so they fix the problems below "
            "while keeping the voice, humour and facts that were fine. "
        )
        + "Keep every other block, the "
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
    series: str = "reflection",
) -> CriticOutcome:
    attempts: list[CriticAttempt] = []
    rewrites = 0
    current = script
    while True:
        flags = lexical_flags(current, series)
        raw = call_llm(build_critic_prompt(current, flags, series))
        result = parse_critic_result(raw, series)
        attempts.append(CriticAttempt(len(attempts) + 1, result, flags))
        if on_critic:
            on_critic(len(attempts), result, raw)
        if result.passed:
            return CriticOutcome(True, current, attempts, rewrites)
        if rewrites >= max_rewrites:
            return CriticOutcome(False, current, attempts, rewrites)

        rewrites += 1
        raw_script = call_llm(build_rewrite_prompt(current, result.failed, spec, series))
        revised = validate_script_json(raw_script)
        check_format(revised, spec)
        revised.metadata.format = current.metadata.format
        revised.metadata.prompt_version = current.metadata.prompt_version
        revised.metadata.critic_attempt = rewrites + 1
        current = revised
        if on_rewrite:
            on_rewrite(rewrites, current)
