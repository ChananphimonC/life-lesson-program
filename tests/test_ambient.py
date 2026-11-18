import re
import shutil
import subprocess
import wave

import pytest

from life_lesson.audio.ambient import build_ambient_bed, default_sounds, scene_filtergraph
from life_lesson.generation.atmosphere import BlockMood
from life_lesson.video.scenes import Scene

needs_ffmpeg = pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="no ffmpeg")


def _mean_db(path):
    err = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(path), "-af", "volumedetect", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    return float(re.search(r"mean_volume: (-?[\d.]+) dB", err).group(1))


def _duration(path):
    with wave.open(str(path)) as w:
        return w.getnframes() / w.getframerate()


def test_default_sounds_follow_weather_and_tension():
    assert default_sounds(None) == []
    assert default_sounds(BlockMood(weather="storm")) == ["rain", "thunder"]
    assert "heartbeat" in default_sounds(BlockMood(weather="clear", tension=5))
    assert default_sounds(BlockMood(weather="clear", tension=1)) == ["room_tone"]


def test_silence_only_scene_has_no_graph():
    assert scene_filtergraph(BlockMood(sounds=["silence"]), 5) is None
    assert scene_filtergraph(None, 5) is None


@needs_ffmpeg
@pytest.mark.parametrize("snd", ["rain", "thunder", "wind", "waves", "room_tone", "heartbeat", "clock"])
def test_every_sound_renders_and_is_audible(tmp_path, snd):
    out = tmp_path / "s.wav"
    g = scene_filtergraph(BlockMood(sounds=[snd], tension=4), 6.0)
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-filter_complex", g, "-map", "[out]",
                    "-t", "6", "-ar", "44100", "-ac", "1", str(out)], check=True)
    assert -70 < _mean_db(out) < -10, snd


@needs_ffmpeg
def test_bed_spans_scenes_and_matches_total_length(tmp_path):
    scenes = [Scene(0, 0, 3000, "a", None, None, BlockMood(weather="rain")),
              Scene(1, 3000, 7000, "b", None, None, BlockMood(weather="storm", tension=5))]
    out = build_ambient_bed("ffmpeg", scenes, 7000, tmp_path / "bed.wav")
    assert abs(_duration(out) - 7.0) < 0.3
    assert _mean_db(out) > -60


@needs_ffmpeg
def test_no_sound_no_music_returns_none(tmp_path):
    scenes = [Scene(0, 0, 3000, "a", None, None, BlockMood(sounds=["silence"]))]
    assert build_ambient_bed("ffmpeg", scenes, 3000, tmp_path / "bed.wav") is None
