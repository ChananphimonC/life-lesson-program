"""Subtitles for the full-length video: the script text itself, never re-transcribed.

Every on-screen caption is a slice of a block's `text` (so tone marks and vowels can't drift),
timed across that block's narration. Also written as .srt for YouTube's caption upload.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image

from life_lesson.generation.schema import ScriptOutput

Cue = tuple[str, int, int]  # text, start_ms, end_ms


def caption_cues(script: ScriptOutput, starts_ms: list[int], total_ms: int, max_chars: int = 30) -> list[Cue]:
    from life_lesson.library.shorts import block_end_times, caption_chunks   # lazy: shorts imports the video package

    ends = block_end_times(script, starts_ms, total_ms)
    cues: list[Cue] = []
    for block, a, b in zip(script.script_blocks, starts_ms, ends):
        cues.extend(caption_chunks(block.text, a, b, max_chars))
    return cues


def _ts(ms: int) -> str:
    h, rem = divmod(ms, 3_600_000)
    m, rem = divmod(rem, 60_000)
    s, milli = divmod(rem, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{milli:03d}"


def write_srt(cues: list[Cue], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(f"{i}\n{_ts(a)} --> {_ts(b)}\n{t}\n\n" for i, (t, a, b) in enumerate(cues, 1)), encoding="utf-8")
    return path


def render_caption(text: str, size: tuple[int, int], font_path: Path) -> Image.Image:
    """Transparent full-frame PNG with one caption near the bottom (below the chapter card)."""
    from life_lesson.library.shorts import _png_text

    return _png_text(text, size, font_path, max(24, int(size[1] * 0.048)), box=True, y_frac=0.865)
