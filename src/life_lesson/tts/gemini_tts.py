"""Provisional TTS provider (v0.1): Gemini TTS.

Chosen because the Gemini API key is already required for script
generation, so v0.1 doesn't need a second vendor account. This is a
provisional choice only -- ARCHITECTURE.md/ROADMAP.md schedule a proper
multi-provider benchmark (Thai pronunciation, pacing, naturalness, cost)
for v0.2, and this module is isolated behind `tts.base.TTSProvider` so it
can be replaced without touching the rest of the pipeline.
"""

from __future__ import annotations

import logging
import wave
from io import BytesIO

from google import genai
from google.genai import types

from life_lesson.config import Settings
from life_lesson.errors import ConfigurationError, TTSError

logger = logging.getLogger(__name__)

# Gemini TTS returns raw PCM audio at this fixed format.
_SAMPLE_RATE_HZ = 24_000
_SAMPLE_WIDTH_BYTES = 2
_CHANNELS = 1


class GeminiTTSProvider:
    def __init__(self, settings: Settings):
        if not settings.gemini_api_key:
            raise ConfigurationError(
                "GEMINI_API_KEY is not set. Copy .env.example to .env and fill it in."
            )
        self._client = genai.Client(api_key=settings.gemini_api_key)
        self._model = settings.gemini_tts_model
        self._voice = settings.gemini_tts_voice

    def synthesize(self, text: str) -> bytes:
        try:
            response = self._client.models.generate_content(
                model=self._model,
                contents=text,
                config=types.GenerateContentConfig(
                    response_modalities=["AUDIO"],
                    speech_config=types.SpeechConfig(
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                voice_name=self._voice
                            )
                        )
                    ),
                ),
            )
        except Exception as exc:  # noqa: BLE001 - external API call
            raise TTSError(f"Gemini TTS request failed: {exc}") from exc

        pcm_bytes = _extract_pcm(response)
        if not pcm_bytes:
            raise TTSError("Gemini TTS returned no audio data")
        return _pcm_to_wav_bytes(pcm_bytes)


def _extract_pcm(response) -> bytes | None:
    try:
        candidates = response.candidates
        parts = candidates[0].content.parts
        for part in parts:
            inline_data = getattr(part, "inline_data", None)
            if inline_data is not None and inline_data.data:
                return inline_data.data
    except (AttributeError, IndexError, TypeError):
        return None
    return None


def _pcm_to_wav_bytes(pcm_bytes: bytes) -> bytes:
    buffer = BytesIO()
    with wave.open(buffer, "wb") as wav_file:
        wav_file.setnchannels(_CHANNELS)
        wav_file.setsampwidth(_SAMPLE_WIDTH_BYTES)
        wav_file.setframerate(_SAMPLE_RATE_HZ)
        wav_file.writeframes(pcm_bytes)
    return buffer.getvalue()
