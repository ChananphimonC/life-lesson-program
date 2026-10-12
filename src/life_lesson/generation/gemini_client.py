"""Thin wrapper around the Gemini API for script generation.

Kept as plain functions (not a class hierarchy / provider interface) --
REQUIREMENTS.md explicitly asks not to over-engineer provider abstractions
in v0.1. This module is the only place that talks to `google.genai` for
text generation, so swapping models/providers later stays localized.
"""

from __future__ import annotations

import logging

from google import genai
from google.genai import types

from life_lesson.config import Settings
from life_lesson.errors import ConfigurationError, ScriptGenerationError

logger = logging.getLogger(__name__)


def _client(settings: Settings) -> genai.Client:
    if not settings.gemini_api_key:
        raise ConfigurationError(
            "GEMINI_API_KEY is not set. Copy .env.example to .env and fill it in."
        )
    return genai.Client(api_key=settings.gemini_api_key)


def generate_script_text(settings: Settings, prompt: str) -> str:
    """Call Gemini to generate the raw script JSON text for a prompt.

    Returns the raw text response. Does NOT validate or parse it -- that is
    `generation.schema.validate_script_json`'s job, kept separate so this
    function stays a thin, testable I/O boundary.
    """
    client = _client(settings)
    try:
        response = client.models.generate_content(
            model=settings.gemini_script_model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.9,
            ),
        )
    except Exception as exc:  # noqa: BLE001 - external API call, surface as our error type
        raise ScriptGenerationError(f"Gemini script generation request failed: {exc}") from exc

    text = getattr(response, "text", None)
    if not text:
        raise ScriptGenerationError("Gemini returned an empty script response")
    return text
