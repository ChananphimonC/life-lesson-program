"""Derive real narration timing from the already-generated episode WAV.

Block boundaries: the pipeline inserts `pause_after_ms` of exact digital
silence (sample value 0) after every TTS block, so long runs of exact zeros
mark them precisely. Phrase pauses inside a block are found with a simple
RMS-energy threshold; scene anchors are estimated by text position and then
snapped to the nearest real phrase pause.
"""

from __future__ import annotations

import math
import unicodedata
import wave
from array import array
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class BlockTiming:
    sequence: int
    text: str
    speech_start: float
    speech_end: float
    pause_end: float
    phrase_pauses: list[tuple[float, float]] = field(default_factory=list)

    def anchor_time(self, anchor: str, max_snap: float = 1.6) -> float:
        """Time (seconds) at which the phrase starting with `anchor` is spoken."""
        if not anchor:
            return self.speech_start
        idx = self.text.find(anchor)
        if idx < 0:
            raise ValueError(f"anchor {anchor!r} not found in block {self.sequence}")

        aligned = self._aligned_time(idx)
        if aligned is not None:
            return aligned

        ratio = _weight(self.text[:idx]) / max(1, _weight(self.text))
        estimate = self.speech_start + ratio * (self.speech_end - self.speech_start)
        best, best_dist = estimate, max_snap
        for _, resume in self.phrase_pauses:
            dist = abs(resume - estimate)
            if dist < best_dist:
                best, best_dist = resume, dist
        return best

    def _voiced(self):
        voiced, cursor = [], self.speech_start
        for p0, p1 in sorted(self.phrase_pauses):
            if p0 > cursor:
                voiced.append((cursor, min(p0, self.speech_end)))
            cursor = max(cursor, p1)
        if cursor < self.speech_end:
            voiced.append((cursor, self.speech_end))
        return voiced

    def _aligned_time(self, char_idx: int) -> float | None:
        """Assign detected phrase pauses to spaces in the text (pauses almost
        always fall on spaces), choosing the grouping whose speaking rate is
        most uniform, then interpolate `char_idx` inside its matched span."""
        if self._alignment is None:
            self._alignment = _align(self.text, self._voiced()) or False
        if not self._alignment:
            return None
        for (seg_start, seg_end), (t0, t1) in self._alignment:
            if seg_start <= char_idx < seg_end:
                w_before = _weight(self.text[seg_start:char_idx])
                w_total = max(1, _weight(self.text[seg_start:seg_end]))
                return t0 + (t1 - t0) * w_before / w_total
        return None

    _alignment: list | bool | None = None


def _weight(s: str) -> int:
    """Spoken-length proxy: base characters only (Thai vowel/tone marks that
    combine with a consonant add little duration)."""
    return sum(1 for ch in s if not ch.isspace() and unicodedata.category(ch) != "Mn")


MID_PHRASE_PENALTY = 0.8


def _align(text: str, voiced: list[tuple[float, float]]):
    """Split `text` into len(voiced) consecutive spans. Span boundaries may sit
    on a space (free) or inside a phrase (penalized) -- TTS occasionally
    breathes mid-phrase. Cost favors spans whose duration matches a uniform
    speaking rate."""
    n = len(text)
    cands = [p for p in range(n + 1)
             if p in (0, n) or (text[p] != " " and unicodedata.category(text[p]) != "Mn")]
    weight_at = {}
    acc = 0
    for p in range(n + 1):
        weight_at[p] = acc
        if p < n and not text[p].isspace() and unicodedata.category(text[p]) != "Mn":
            acc += 1
    m = len(voiced)
    if m == 0 or acc == 0:
        return None
    rate = sum(b - a for a, b in voiced) / acc
    on_space = {p: p in (0, n) or text[p - 1] == " " for p in cands}

    inf = float("inf")
    nc = len(cands)
    cost = [[inf] * nc for _ in range(m + 1)]
    back = [[0] * nc for _ in range(m + 1)]
    cost[0][0] = 0.0
    for j in range(1, m + 1):
        d = voiced[j - 1][1] - voiced[j - 1][0]
        for bi in range(1, nc):
            if j == m and bi != nc - 1:
                continue
            wb = weight_at[cands[bi]]
            penalty = 0.0 if on_space[cands[bi]] else MID_PHRASE_PENALTY
            best, arg = inf, 0
            for ai in range(bi):
                prev = cost[j - 1][ai]
                if prev == inf:
                    continue
                w = wb - weight_at[cands[ai]]
                if w <= 0:
                    continue
                expected = rate * w
                c = prev + (d - expected) ** 2 / max(0.25, expected) + penalty
                if c < best:
                    best, arg = c, ai
            cost[j][bi], back[j][bi] = best, arg
    if cost[m][nc - 1] == inf:
        return None
    spans, bi = [], nc - 1
    for j in range(m, 0, -1):
        ai = back[j][bi]
        spans.append(((cands[ai], cands[bi]), voiced[j - 1]))
        bi = ai
    return list(reversed(spans))


def _read_mono_int16(path: Path) -> tuple[array, int]:
    with wave.open(str(path), "rb") as wav:
        if wav.getsampwidth() != 2 or wav.getnchannels() != 1:
            raise ValueError("expected mono 16-bit PCM WAV")
        rate = wav.getframerate()
        samples = array("h", wav.readframes(wav.getnframes()))
    return samples, rate


def _zero_runs(samples: array, min_len: int) -> list[tuple[int, int]]:
    runs, start = [], None
    for i, value in enumerate(samples):
        if value == 0:
            if start is None:
                start = i
        elif start is not None:
            if i - start >= min_len:
                runs.append((start, i))
            start = None
    if start is not None and len(samples) - start >= min_len:
        runs.append((start, len(samples)))
    return runs


def _quiet_runs(samples: array, rate: int, start: int, end: int,
                window_s: float = 0.01, threshold_db: float = -40.0,
                min_s: float = 0.18) -> list[tuple[float, float]]:
    window = max(1, int(rate * window_s))
    limit = 32768 * 10 ** (threshold_db / 20)
    runs, run_start = [], None
    for w0 in range(start, end, window):
        chunk = samples[w0:min(w0 + window, end)]
        rms = math.sqrt(sum(v * v for v in chunk) / len(chunk))
        if rms < limit:
            if run_start is None:
                run_start = w0
        elif run_start is not None:
            if (w0 - run_start) / rate >= min_s:
                runs.append((run_start / rate, w0 / rate))
            run_start = None
    return runs


def analyze(wav_path: Path, blocks: list[dict]) -> tuple[list[BlockTiming], float]:
    samples, rate = _read_mono_int16(wav_path)
    total = len(samples) / rate

    min_pause_ms = min(b["pause_after_ms"] for b in blocks)
    runs = _zero_runs(samples, int(rate * min_pause_ms / 1000 * 0.9))
    if len(runs) != len(blocks):
        raise ValueError(
            f"found {len(runs)} inserted pauses but script has {len(blocks)} blocks"
        )

    timings, cursor = [], 0
    for block, (z0, z1) in zip(blocks, runs):
        quiet = _quiet_runs(samples, rate, cursor, z0)
        timings.append(BlockTiming(
            sequence=block["sequence"],
            text=block["text"],
            speech_start=cursor / rate,
            speech_end=z0 / rate,
            pause_end=z1 / rate,
            phrase_pauses=quiet,
        ))
        cursor = z1
    return timings, total
