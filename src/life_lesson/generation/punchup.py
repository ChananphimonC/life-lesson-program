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


def build_compare_prompt(a: ScriptOutput, b: ScriptOutput, series: str) -> str:
    def text(x: ScriptOutput) -> str:
        return "\n".join(f"[{blk.sequence}] {blk.text}" for blk in x.script_blocks)

    return (
        "You are a sharp Thai audience reader judging two versions (A and B) of the same narrated "
        "story. Imagine hearing each once, with no pictures. Which version would you keep "
        "listening to? Judge: the first 15 seconds (concrete, odd, a question you need answered), "
        "escalation (does each chapter change something?), a reversal that feels earned, specific "
        "detail over general, spoken-Thai naturalness (told, not read), and whether the voice avoids "
        "describing what a picture would show. Ignore length unless one drags.\n"
        + ("This is a reflection: judge curiosity and unresolved feeling, not danger.\n" if series == "reflection" else "")
        + '\nRespond with ONLY JSON: {"winner": "A" or "B" or "tie", "first_drop_off_block_A": <int or null>, '
        '"first_drop_off_block_B": <int or null>, "reason": "<one sentence>"}\n\n'
        f"VERSION A:\n{text(a)}\n\nVERSION B:\n{text(b)}"
    )


def _verdict(raw: str) -> str:
    import json

    try:
        data = json.loads(raw.strip().strip("`").removeprefix("json").strip())
        w = str(data.get("winner", "tie")).strip().upper()
        return w if w in ("A", "B") else "tie"
    except (ValueError, AttributeError):
        return "tie"


def judge_prefers_new(old: ScriptOutput, new: ScriptOutput, judge: Callable[[str], str], series: str) -> tuple[bool, str]:
    """Ask the reader-judge twice with the order swapped (LLM judges favour position A);
    the rewrite must win BOTH times."""
    first = _verdict(judge(build_compare_prompt(old, new, series)))   # new is B
    second = _verdict(judge(build_compare_prompt(new, old, series)))  # new is A
    return (first == "B" and second == "A"), f"judge: old-first={first}, new-first={second}"


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
    judge: Callable[[str], str] | None = None,
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
        # never accept a rewrite that adds mechanical problems...
        accepted = new_report.objective_penalty <= report.objective_penalty
        note = new_report.summary()[:240]
        if accepted and judge is not None:
            # ...and let the reader-judge, not keyword heuristics, decide "more gripping"
            accepted, verdict = judge_prefers_new(current, revised, judge, series)
            note = f"{verdict}; {note}"[:300]
        elif accepted:
            accepted = new_report.score > report.score  # no judge available: fall back to the linter
        rounds.append(PunchupRound(n, report.score, new_report.score, accepted, note))
        if on_round:
            on_round(rounds[-1], new_report)
        if not accepted:
            break
        current, report = revised, new_report
    return PunchupOutcome(current, first, report, rounds)
