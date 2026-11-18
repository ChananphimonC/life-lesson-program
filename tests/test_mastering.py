import random
import re
import shutil
import subprocess
import wave

import pytest

from life_lesson.audio.mastering import build_master_command, master_audio, pick_music

needs_ffmpeg = pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="ffmpeg not installed")


def _tone(path, seconds=3, hz=220, amp=0.05):
    import math, struct

    rate = 24000
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate)
        w.writeframes(b"".join(
            struct.pack("<h", int(32767 * amp * math.sin(2 * math.pi * hz * i / rate)))
            for i in range(rate * seconds)))


def _measure_lufs(path):
    out = subprocess.run(
        ["ffmpeg", "-hide_banner", "-i", str(path), "-af", "ebur128", "-f", "null", "-"],
        capture_output=True, text=True).stderr
    return float(re.findall(r"I:\s+(-?\d+\.\d+) LUFS", out)[-1])


def test_command_without_music_has_loudnorm():
    cmd = build_master_command("ffmpeg", "in.wav", "out.wav", None)
    assert "loudnorm=I=-16" in " ".join(cmd)


def test_command_with_music_ducks_and_mixes():
    cmd = " ".join(build_master_command("ffmpeg", "in.wav", "out.wav", "m.mp3"))
    assert "sidechaincompress" in cmd and "amix" in cmd and "-stream_loop" in cmd


def test_pick_music(tmp_path):
    assert pick_music(None) is None and pick_music(tmp_path / "nope") is None
    assert pick_music(tmp_path) is None
    (tmp_path / "a.mp3").write_bytes(b"x"); (tmp_path / "n.txt").write_text("x")
    assert pick_music(tmp_path, rng=random.Random(1)).name == "a.mp3"


@needs_ffmpeg
def test_master_hits_target_loudness(tmp_path):
    src = tmp_path / "n.wav"; _tone(src, 5)
    out = master_audio("ffmpeg", src, tmp_path / "m.wav")
    assert -18.5 < _measure_lufs(out) < -13.5


@needs_ffmpeg
def test_master_with_music_keeps_narration_length(tmp_path):
    src = tmp_path / "n.wav"; _tone(src, 4, amp=0.2)
    bed = tmp_path / "bed.wav"; _tone(bed, 2, hz=110, amp=0.2)
    out = master_audio("ffmpeg", src, tmp_path / "m.wav", music=bed)
    with wave.open(str(out)) as w:
        assert abs(w.getnframes() / w.getframerate() - 4) < 0.3
