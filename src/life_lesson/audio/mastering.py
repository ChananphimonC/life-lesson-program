"""Narration mastering with FFmpeg (STYLE_GUIDE.md §10).

- Loudness-normalise the narration to -16 LUFS (YouTube-friendly, mobile-safe).
- Optionally mix an ambient music bed underneath, ducked while the narrator
  speaks (sidechain compression) so the voice always stays on top.
"""

from __future__ import annotations

import logging
import random
import subprocess
from pathlib import Path

from life_lesson.errors import TTSError

logger = logging.getLogger(__name__)

TARGET_LUFS = -16
TRUE_PEAK_DB = -1.5
LRA = 11
MUSIC_EXTENSIONS = {".mp3", ".wav", ".m4a", ".ogg", ".flac"}
MUSIC_GAIN_DB = -20  # bed level before ducking


def pick_music(music_dir: Path | None, *, rng: random.Random | None = None) -> Path | None:
    if music_dir is None or not music_dir.is_dir():
        return None
    tracks = sorted(p for p in music_dir.iterdir() if p.suffix.lower() in MUSIC_EXTENSIONS)
    if not tracks:
        return None
    return (rng or random).choice(tracks)


def build_master_command(
    ffmpeg_binary: str,
    narration: Path,
    output: Path,
    music: Path | None,
    bed_gain_db: float = MUSIC_GAIN_DB,
) -> list[str]:
    loud = f"loudnorm=I={TARGET_LUFS}:TP={TRUE_PEAK_DB}:LRA={LRA}"
    if music is None:
        return [
            ffmpeg_binary, "-y", "-i", str(narration),
            "-af", loud, "-ar", "44100", "-ac", "1", str(output),
        ]
    graph = (
        # narration is split: one copy drives the ducking, one is mixed
        "[0:a]asplit=2[voice][sc];"
        f"[1:a]volume={bed_gain_db}dB,aformat=sample_rates=44100:channel_layouts=mono[bed];"
        "[bed][sc]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=600[ducked];"
        "[voice]aformat=sample_rates=44100:channel_layouts=mono[v];"
        "[v][ducked]amix=inputs=2:duration=first:dropout_transition=0:normalize=0[mix];"
        f"[mix]{loud}[out]"
    )
    return [
        ffmpeg_binary, "-y",
        "-i", str(narration),
        "-stream_loop", "-1", "-i", str(music),
        "-filter_complex", graph,
        "-map", "[out]", "-ar", "44100", "-ac", "1", str(output),
    ]


def master_audio(
    ffmpeg_binary: str,
    narration: Path,
    output: Path,
    music: Path | None = None,
    bed_gain_db: float = MUSIC_GAIN_DB,
) -> Path:
    output.parent.mkdir(parents=True, exist_ok=True)
    command = build_master_command(ffmpeg_binary, narration, output, music, bed_gain_db)
    logger.info("Mastering audio (music=%s)", music)
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=False)
    except FileNotFoundError as exc:
        raise TTSError(f"ffmpeg binary not found ('{ffmpeg_binary}')") from exc
    if result.returncode != 0:
        raise TTSError(f"audio mastering failed: {result.stderr[-1500:]}")
    return output
