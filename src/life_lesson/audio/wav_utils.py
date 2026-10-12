"""Concatenate per-block WAV clips with silence gaps.

This is how `[PAUSE_SHORT]`/`[PAUSE_LONG]`-style pacing (AI_DESIGN.md §3)
is realized in v0.1: each script block is synthesized separately, then
stitched together here with `pause_after_ms` of silence in between. This
works regardless of whether a given TTS provider supports native pause
markers, so no provider-specific pacing behavior leaks into the rest of
the pipeline (AI_DESIGN.md §3 fallback: post-processing silence insertion).

Uses only the stdlib `wave` module -- no ffmpeg/pydub dependency needed
for this step. All input clips are assumed to share the same format
(mono, 16-bit PCM); this holds for clips produced by a single TTS
provider within one episode.
"""

from __future__ import annotations

import wave
from pathlib import Path

from life_lesson.errors import TTSError


def concatenate_with_silence(clips_with_pauses: list[tuple[bytes, int]], output_path: Path) -> Path:
    """Write `output_path` as the concatenation of each (wav_bytes, pause_after_ms) pair.

    `pause_after_ms` inserts silence *after* the corresponding clip.
    """
    if not clips_with_pauses:
        raise TTSError("No audio clips to concatenate")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    params = None
    frames: list[bytes] = []

    for wav_bytes, pause_after_ms in clips_with_pauses:
        with _wave_reader(wav_bytes) as reader:
            clip_params = reader.getparams()
            if params is None:
                params = clip_params
            elif clip_params[:3] != params[:3]:
                raise TTSError(
                    "Audio clips have mismatched format "
                    f"(channels/sampwidth/framerate): {clip_params[:3]} vs {params[:3]}"
                )
            frames.append(reader.readframes(reader.getnframes()))

        if pause_after_ms > 0:
            frames.append(_silence_frames(params, pause_after_ms))

    with wave.open(str(output_path), "wb") as writer:
        writer.setnchannels(params.nchannels)
        writer.setsampwidth(params.sampwidth)
        writer.setframerate(params.framerate)
        for chunk in frames:
            writer.writeframes(chunk)

    return output_path


def _wave_reader(wav_bytes: bytes):
    import io

    return wave.open(io.BytesIO(wav_bytes), "rb")


def _silence_frames(params: wave._wave_params, duration_ms: int) -> bytes:
    num_frames = int(params.framerate * duration_ms / 1000)
    frame_size = params.nchannels * params.sampwidth
    return b"\x00" * (num_frames * frame_size)
