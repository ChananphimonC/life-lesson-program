from __future__ import annotations

import sys
import wave
from io import BytesIO
from pathlib import Path

import pytest

# Allow running tests without an editable install (`pip install -e .`).
SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


def make_silence_wav(duration_ms: int = 100, framerate: int = 24_000) -> bytes:
    """Build a tiny valid mono 16-bit PCM WAV clip for tests, with no
    dependency on a real TTS call."""
    n_frames = int(framerate * duration_ms / 1000)
    buffer = BytesIO()
    with wave.open(buffer, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(framerate)
        wav_file.writeframes(b"\x00\x00" * n_frames)
    return buffer.getvalue()


@pytest.fixture
def tmp_db_path(tmp_path: Path) -> Path:
    return tmp_path / "test.db"
