"""Raw MP4 assembly via FFmpeg (REQUIREMENTS.md §1: one background video +
TTS audio -> 16:9 MP4, no subtitles yet -- that's v0.4).
"""

from __future__ import annotations

import logging
import random
import subprocess
from pathlib import Path

from life_lesson.errors import VideoAssemblyError

logger = logging.getLogger(__name__)

_VIDEO_EXTENSIONS = {".mp4", ".mov", ".mkv", ".webm"}
_TARGET_WIDTH = 1920
_TARGET_HEIGHT = 1080


def pick_random_background(background_dir: Path) -> Path:
    if not background_dir.is_dir():
        raise VideoAssemblyError(
            f"Background video directory does not exist: {background_dir}"
        )
    candidates = [
        p for p in background_dir.iterdir() if p.suffix.lower() in _VIDEO_EXTENSIONS
    ]
    if not candidates:
        raise VideoAssemblyError(
            f"No background video files found in {background_dir} "
            f"(expected one of {sorted(_VIDEO_EXTENSIONS)})"
        )
    return random.choice(candidates)


def assemble_video(
    *,
    ffmpeg_binary: str,
    background_video: Path,
    audio_path: Path,
    output_path: Path,
) -> Path:
    """Loop `background_video` to match `audio_path`'s length, mux the audio
    in, and write a 16:9 H.264/AAC MP4 to `output_path`.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    scale_filter = (
        f"scale={_TARGET_WIDTH}:{_TARGET_HEIGHT}:force_original_aspect_ratio=increase,"
        f"crop={_TARGET_WIDTH}:{_TARGET_HEIGHT}"
    )
    command = [
        ffmpeg_binary,
        "-y",
        "-stream_loop",
        "-1",
        "-i",
        str(background_video),
        "-i",
        str(audio_path),
        "-map",
        "0:v:0",
        "-map",
        "1:a:0",
        "-vf",
        scale_filter,
        "-c:v",
        "libx264",
        "-c:a",
        "aac",
        # Resample from the TTS engine's native 24kHz: many players' AAC
        # decoders silently drop audio at non-standard sample rates even
        # though ffmpeg itself decodes it fine.
        "-ar",
        "44100",
        "-pix_fmt",
        "yuv420p",
        "-shortest",
        # Without this, ffmpeg writes the moov atom (the index players need
        # to even recognize tracks/codecs) at the END of the file. Most
        # players either refuse to open the file at all or play video while
        # silently failing to resolve the audio track until that's read.
        "-movflags",
        "+faststart",
        str(output_path),
    ]

    logger.info("Running ffmpeg: %s", " ".join(command))
    try:
        result = subprocess.run(
            command, capture_output=True, text=True, check=False
        )
    except FileNotFoundError as exc:
        raise VideoAssemblyError(
            f"ffmpeg binary not found ('{ffmpeg_binary}'). Install ffmpeg or "
            "set FFMPEG_BINARY to its full path."
        ) from exc

    if result.returncode != 0:
        raise VideoAssemblyError(
            f"ffmpeg failed (exit code {result.returncode}): {result.stderr[-2000:]}"
        )

    return output_path
