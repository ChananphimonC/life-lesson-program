"""Minimal TTS provider interface.

Intentionally a single `Protocol` with one method -- not a plugin
framework. REQUIREMENTS.md/ARCHITECTURE.md ask for the TTS integration to
be isolated enough to swap after the v0.2 benchmark, without building a
heavy abstraction now. This is that boundary: anything with a matching
`synthesize` method works.
"""

from __future__ import annotations

from typing import Protocol


class TTSProvider(Protocol):
    def synthesize(self, text: str) -> bytes:
        """Return mono 16-bit PCM WAV bytes for the given text."""
        ...
