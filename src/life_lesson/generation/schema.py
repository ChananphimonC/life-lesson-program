"""JSON schema validation for LLM script output (AI_DESIGN.md §9).

Malformed model output is rejected (raises `ScriptValidationError`), never
silently repaired or accepted as-is, per REQUIREMENTS.md §1.
"""

from __future__ import annotations

import json
from typing import Literal

from pydantic import BaseModel, Field, ValidationError, field_validator

from life_lesson.errors import ScriptValidationError

Phase = Literal["hook", "exploration", "shift", "outro"]
_REQUIRED_PHASES: tuple[Phase, ...] = ("hook", "exploration", "shift", "outro")


class ScriptBlock(BaseModel):
    sequence: int = Field(ge=1)
    phase: Phase
    text: str = Field(min_length=1)
    pause_after_ms: int = Field(ge=0)


class ScriptMetadata(BaseModel):
    mood: str
    estimated_duration_seconds: int = Field(gt=0)
    prompt_version: str | None = None
    critic_attempt: int = 1


class ScriptOutput(BaseModel):
    topic_id: str
    title: str = Field(min_length=1)
    metadata: ScriptMetadata
    script_blocks: list[ScriptBlock] = Field(min_length=1)

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
