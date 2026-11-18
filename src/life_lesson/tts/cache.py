"""Per-block voice cache and daily budget.

The narration is synthesised block by block. Each finished block is stored on
disk under a hash of (provider, model, voice, exact text), so:
  * re-running the same script never pays for a block twice;
  * a run can stop cleanly when the daily quota is spent (or after `budget`
    new blocks) and resume the next day from the cached blocks.
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path

from life_lesson.errors import PipelineError, TTSError


class VoiceBudgetExhausted(PipelineError):
    """Stop (not fail): the voice budget or the provider's quota ran out."""


def is_quota_error(message: str) -> bool:
    m = message.lower()
    return any(k in m for k in ("429", "resource_exhausted", "quota", "rate limit"))


class CachedTTS:
    def __init__(self, inner, cache_dir: Path, *, namespace: str, budget: int | None = None):
        self._inner = inner
        self._dir = Path(cache_dir)
        self._ns = namespace
        self._budget = budget
        self.hits = 0
        self.new_calls = 0

    def _path(self, text: str) -> Path:
        digest = hashlib.sha256(f"{self._ns}\n{text}".encode("utf-8")).hexdigest()[:32]
        return self._dir / f"{digest}.wav"

    def synthesize(self, text: str) -> bytes:
        path = self._path(text)
        if path.is_file() and path.stat().st_size > 44:
            self.hits += 1
            return path.read_bytes()
        if self._budget is not None and self.new_calls >= self._budget:
            raise VoiceBudgetExhausted(f"voice budget of {self._budget} new block(s) reached")
        try:
            wav = self._inner.synthesize(text)
        except TTSError as exc:
            if is_quota_error(str(exc)):
                raise VoiceBudgetExhausted(f"voice quota exhausted: {str(exc)[:160]}") from exc
            raise
        self._dir.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".tmp")
        tmp.write_bytes(wav)
        os.replace(tmp, path)  # atomic: an interrupted run never leaves a half-written block
        self.new_calls += 1
        return wav
