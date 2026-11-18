"""JSON schema validation for LLM script output (AI_DESIGN.md §9).

Malformed model output is rejected (raises `ScriptValidationError`), never
silently repaired or accepted as-is, per REQUIREMENTS.md §1.
"""

from __future__ import annotations

import json
from typing import Literal

from pydantic import BaseModel, Field, ValidationError, field_validator

from life_lesson.errors import ScriptValidationError
from life_lesson.generation.atmosphere import BlockMood

Phase = Literal["hook", "exploration", "shift", "outro"]
_REQUIRED_PHASES: tuple[Phase, ...] = ("hook", "exploration", "shift", "outro")


class ScriptBlock(BaseModel):
    sequence: int = Field(ge=1)
    phase: Phase
    text: str = Field(min_length=1)
    pause_after_ms: int = Field(ge=0)
    # Style-guide fields (STYLE_GUIDE.md §4-5); optional so v0.1 scripts stay valid.
    chapter_title: str | None = None
    visual_cue: str | None = None
    time_label: str | None = None
    speaker: str | None = None  # character whose line dominates this block: gets a talking close-up
    mood: BlockMood | None = None
    # Where the scene happens, so the illustrator can draw it (free, offline).
    setting: Literal["room", "office", "street", "city", "sea", "island", "forest", "night_sky", "food_stall", "alley", "bus"] | None = None


class Fact(BaseModel):
    """A real-world fact the scene leans on, kept separate from invented story."""

    claim: str = Field(min_length=1)
    source_hint: str | None = None
    confidence: Literal["high", "medium", "low"] = "medium"


class Character(BaseModel):
    """Fixed look for a recurring character so visuals stay consistent
    across chapters (STYLE_GUIDE.md §13). Invented people only."""

    name: str = Field(min_length=1)
    role: str | None = None
    age_range: str | None = None
    outfit: str = Field(min_length=1)
    signature_item: str | None = None
    palette: list[str] = Field(default_factory=list)
    hair: str | None = None      # e.g. "ผมยาวสีน้ำตาลเข้ม ปล่อยสยาย" (style + colour words)
    gender: str | None = None    # "หญิง" / "ชาย" (drives lashes and default hair)
    # Story engine: what they want, what they fear, what is at stake.
    want: str | None = None
    fear: str | None = None
    stakes: str | None = None


class ScriptMetadata(BaseModel):
    mood: str
    estimated_duration_seconds: int = Field(gt=0)
    prompt_version: str | None = None
    critic_attempt: int = 1
    format: str = "standard"
    motif: str | None = None


class ScriptOutput(BaseModel):
    topic_id: str
    title: str = Field(min_length=1)
    metadata: ScriptMetadata
    script_blocks: list[ScriptBlock] = Field(min_length=1)
    facts: list[Fact] = Field(default_factory=list)
    characters: list[Character] = Field(default_factory=list)
    summary: str | None = None
    subline: str | None = None  # <=30 Thai chars teaser for the cover's single sub-line
    cover_block: int | None = None  # `sequence` of the block whose picture becomes the cover (default: the first)

    @field_validator("script_blocks")
    @classmethod
    def _validate_blocks(cls, blocks: list[ScriptBlock]) -> list[ScriptBlock]:
        sequences = [b.sequence for b in blocks]
        if sequences != sorted(sequences):
            raise ValueError("script_blocks must be ordered by ascending sequence")
        if len(set(sequences)) != len(sequences):
            raise ValueError("script_blocks sequence numbers must be unique")

        present_phases = {b.phase for b in blocks}
        missing = [p for p in _REQUIRED_PHASES if p not in present_phases]
        if missing:
            raise ValueError(f"script is missing required phase(s): {missing}")

        return blocks


def validate_script_json(raw_text: str) -> ScriptOutput:
    """Parse and validate raw LLM output text into a `ScriptOutput`.

    Raises `ScriptValidationError` on any JSON or schema failure -- callers
    must treat this as a rejected generation attempt, not attempt to repair
    the payload themselves.
    """
    cleaned = _strip_markdown_fence(raw_text)
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise ScriptValidationError(f"Model output is not valid JSON: {exc}") from exc

    try:
        return ScriptOutput.model_validate(data)
    except ValidationError as exc:
        raise ScriptValidationError(f"Model output failed schema validation: {exc}") from exc


def _strip_markdown_fence(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        stripped = "\n".join(lines).strip()
    return stripped


def check_format(script: ScriptOutput, spec) -> None:
    """Enforce format-specific structure (STYLE_GUIDE.md §4).

    Raises `ScriptValidationError` -- same reject-don't-repair rule as
    `validate_script_json`.
    """
    blocks = script.script_blocks
    if not spec.min_blocks <= len(blocks) <= spec.max_blocks:
        raise ScriptValidationError(
            f"{spec.name} script needs {spec.min_blocks}-{spec.max_blocks} blocks, "
            f"got {len(blocks)}"
        )
    if spec.max_chars is not None:
        total = sum(len(b.text) for b in blocks)
        if total > spec.max_chars:
            raise ScriptValidationError(
                f"{spec.name} script is too long to read in {spec.max_seconds}s: "
                f"{total} chars (max {spec.max_chars})"
            )
    if spec.needs_chapter_titles:
        missing = [b.sequence for b in blocks if not b.chapter_title]
        if missing:
            raise ScriptValidationError(
                f"{spec.name} script blocks missing chapter_title: {missing[:5]}"
            )
