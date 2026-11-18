"""Script doctor, part 2: the punch-up rewrite loop.

lint (suspense.py) -> if below threshold, ask the model to rewrite the script to
fix the specific findings -> accept the rewrite ONLY if its lint score is higher
(so a "fix" can never make the script worse) -> repeat at most `max_rounds`.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from life_lesson.errors import ScriptValidationError
from life_lesson.generation.formats import FormatSpec
from life_lesson.generation.prompts import _SUSPENSE_ENGINE
from life_lesson.generation.schema import ScriptOutput, check_format, validate_script_json
from life_lesson.generation.suspense import LintReport, lint_script

PUNCHUP_PROMPT_NAME = "punchup"
PUNCHUP_PROMPT_STAGE = "punchup"
PUNCHUP_PROMPT_VERSION = "punchup-v0.1.0"
DEFAULT_THRESHOLD = 75
MAX_ROUNDS = 2


def build_punchup_prompt(script: ScriptOutput, report: LintReport, spec: FormatSpec, series: str) -> str:
    problems = "\n".join(
        f"- [{f.severity}] {f.code}: {f.message}" + (f" (blocks {f.blocks})" if f.blocks else "")
        for f in report.findings
    )
    reflection_note = (
        "This is a reflection: keep it observational, no advice, no moral, open ending; "
        "suspense = curiosity and unresolved feeling.\n"
        if series == "reflection"
        else ""
    )
    return (
        "You are the script doctor for a Thai narrated-video channel. The script below is "
        "accurate but not gripping enough. Rewrite it so a viewer cannot stop watching, by "
        "fixing the findings, using the suspense rules.\n\n"
        f"{_SUSPENSE_ENGINE}\n\n"
        f"{reflection_note}"
        f"Findings from the automatic linter (score {report.score}/100):\n{problems}\n\n"
        "You may rewrite the text of any block and add or remove blocks within the format "
        f"limits ({spec.min_blocks}-{spec.max_blocks} blocks, format '{spec.name}'). KEEP: the topic, "
        "every fact and its source (never add a fact without a source), the characters and "
        "their outfits, the chapter_titles and the order of phases, and the same JSON "
        "structure (mood, setting, visual_cue, pause_after_ms on every block; renumber "
        "`sequence` from 1). Keep the voice natural spoken Thai.\n\n"
        "Respond with ONLY the complete corrected JSON object.\n\n"
        f"SCRIPT:\n{script.model_dump_json()}"
    )


@dataclass
class PunchupRound:
    round: int
    before: int
    after: int | None
    accepted: bool
    note: str = ""


@dataclass
class PunchupOutcome:
    script: ScriptOutput
    before: LintReport
    after: LintReport
    rounds: list[PunchupRound]

    @property
    def improved(self) -> bool:
        return self.after.score > self.before.score


def run_punchup(
    script: ScriptOutput,
    spec: FormatSpec,
    *,
    call_llm: Callable[[str], str],
    series: str = "reflection",
    threshold: int = DEFAULT_THRESHOLD,
    max_rounds: int = MAX_ROUNDS,
    on_round: Callable[[PunchupRound, LintReport], None] | None = None,
) -> PunchupOutcome:
    first = lint_script(script, series)
    current, report, rounds = script, first, []
    for n in range(1, max_rounds + 1):
        if report.score >= threshold:
            break
        raw = call_llm(build_punchup_prompt(current, report, spec, series))
        try:
            revised = validate_script_json(raw)
            check_format(revised, spec)
        except ScriptValidationError as exc:
            rounds.append(PunchupRound(n, report.score, None, False, f"rejected: {exc}"[:200]))
            if on_round:
                on_round(rounds[-1], report)
            break
        revised.metadata.format = current.metadata.format
        revised.metadata.prompt_version = current.metadata.prompt_version
        new_report = lint_script(revised, series)
        accepted = new_report.score > report.score
        rounds.append(PunchupRound(n, report.score, new_report.score, accepted, new_report.summary()[:300]))
        if on_round:
            on_round(rounds[-1], new_report)
        if not accepted:
            break
        current, report = revised, new_report
    return PunchupOutcome(current, first, report, rounds)
