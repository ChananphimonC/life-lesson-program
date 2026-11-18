import json
import shutil
import subprocess
import wave
from pathlib import Path

import pytest

from life_lesson.errors import PipelineError, VideoAssemblyError
from life_lesson.publish.fonts import find_thai_font
from life_lesson.video.scenes import (
    Scene, assemble_scene_video, assign_backgrounds, list_backgrounds,
    plan_scenes, render_chapter_card, write_shot_list,
)

from .test_publish_metadata import _script

needs_ffmpeg = pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="no ffmpeg")


def test_plan_scenes_groups_by_chapter_and_tiles_timeline():
    s = _script(["เปิด", "เปิด", "สอง", "สาม", "จบ"])
    scenes = plan_scenes(s, [0, 5_000, 12_000, 30_000, 50_000], 70_000)
    assert [x.title for x in scenes] == ["เปิด", "สอง", "สาม", "จบ"]
    assert scenes[0].start_ms == 0 and scenes[-1].end_ms == 70_000
    assert all(a.end_ms == b.start_ms for a, b in zip(scenes, scenes[1:]))


def test_short_scene_merges_into_previous():
    s = _script(["a", "b", "c", "d", "e"])
    scenes = plan_scenes(s, [0, 10_000, 11_000, 30_000, 50_000], 70_000)
    assert [x.title for x in scenes] == ["a", "b", "d", "e"]


def test_no_titles_gives_single_scene():
    s = _script([None] * 5)
    scenes = plan_scenes(s, [0, 1, 2, 3, 4], 40_000)
    assert len(scenes) == 1 and scenes[0].end_ms == 40_000


def test_backgrounds_rotate_without_immediate_repeat():
    clips = [Path("a.mp4"), Path("b.mp4")]
    chosen = assign_backgrounds(5, clips)
    assert all(x != y for x, y in zip(chosen, chosen[1:]))


def test_list_backgrounds_errors(tmp_path):
    with pytest.raises(VideoAssemblyError):
        list_backgrounds(tmp_path / "missing")
    with pytest.raises(VideoAssemblyError):
        list_backgrounds(tmp_path)


def test_shot_list_written(tmp_path):
    p = write_shot_list([Scene(0, 0, 9000, "เปิด", "23:47", "ภาพ")], tmp_path / "shots.json")
    assert json.loads(p.read_text(encoding="utf-8"))[0]["visual_cue"] == "ภาพ"


def _have_font():
    try:
        find_thai_font(); return True
    except PipelineError:
        return False


@pytest.mark.skipif(not _have_font(), reason="no Thai font")
def test_chapter_card_is_transparent_png(tmp_path):
    from PIL import Image

    out = render_chapter_card(Scene(0, 0, 9000, "ชั้นห้า", "23:47", None), (1280, 720), tmp_path / "c.png")
    img = Image.open(out)
    assert img.mode == "RGBA" and img.getpixel((2, 2))[3] == 0


@needs_ffmpeg
@pytest.mark.skipif(not _have_font(), reason="no Thai font")
def test_real_ffmpeg_assembles_scenes(tmp_path):
    bg = tmp_path / "bg"; bg.mkdir()
    for i, color in enumerate(("blue", "green")):
        subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i", f"color=c={color}:s=320x180:d=2",
                        "-pix_fmt", "yuv420p", str(bg / f"c{i}.mp4")], check=True, capture_output=True)
    audio = tmp_path / "a.wav"
    with wave.open(str(audio), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(24000)
        w.writeframes(b"\x00\x00" * 24000 * 9)
    scenes = [Scene(0, 0, 4500, "เปิด", "23:47", None), Scene(1, 4500, 9000, "บทสอง", None, None)]
    out = assemble_scene_video(
        ffmpeg_binary="ffmpeg", scenes=scenes, background_dir=bg, audio_path=audio,
        output_path=tmp_path / "o.mp4", width=640, height=360)
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height,duration",
         "-of", "json", str(out)], capture_output=True, text=True, check=True)
    streams = {s["codec_type"]: s for s in json.loads(probe.stdout)["streams"]}
    assert streams["video"]["width"] == 640 and streams["video"]["height"] == 360
    assert "audio" in streams
    assert abs(float(streams["video"]["duration"]) - 9.0) < 0.5


def _mean_rgb(path, at=1.5):
    out = subprocess.run(
        ["ffmpeg", "-loglevel", "error", "-i", str(path), "-ss", str(at),
         "-vf", "scale=1:1:flags=area,format=rgb24", "-frames:v", "1", "-f", "rawvideo", "-"],
        capture_output=True, check=True).stdout
    return tuple(out[:3])


@needs_ffmpeg
def test_rain_keeps_colours(tmp_path):
    """Regression: blend->yuv420p once collapsed green and spiked red/blue."""
    from life_lesson.generation.atmosphere import BlockMood

    bg = tmp_path / "bg"; bg.mkdir()
    subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i", "color=c=0x202c3a:s=320x180:d=3",
                    "-pix_fmt", "yuv420p", str(bg / "c.mp4")], check=True, capture_output=True)
    audio = tmp_path / "a.wav"
    with wave.open(str(audio), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(24000)
        w.writeframes(b"\x00\x00" * 24000 * 4)

    def render(name, mood):
        return assemble_scene_video(
            ffmpeg_binary="ffmpeg", scenes=[Scene(0, 0, 4000, None, None, None, mood)],
            background_dir=bg, audio_path=audio, output_path=tmp_path / f"{name}.mp4",
            width=320, height=180)

    clear = _mean_rgb(render("clear", BlockMood(light="dim", weather="clear", color="cool", tension=2)))
    rain = _mean_rgb(render("rain", BlockMood(light="dim", weather="rain", color="cool", tension=2)))
    storm = _mean_rgb(render("storm", BlockMood(light="dim", weather="storm", color="cool", tension=2)))
    for other in (rain, storm):
        # rain adds light streaks but must not shift hue: green stays within reach of clear
        assert all(abs(a - b) < 30 for a, b in zip(clear, other)), (clear, other)
        assert other[2] >= other[1] >= other[0] - 5  # still a cool, blue-ish picture


@needs_ffmpeg
def test_rain_layer_is_sparse_so_it_never_veils_the_picture():
    """Regression: rain once covered ~8-13% of every frame and hid the artwork."""
    import io

    from life_lesson.generation.atmosphere import BlockMood, rain_chain

    for weather, limit in (("rain", 3.5), ("storm", 5.5)):
        chain = rain_chain(480, 270, BlockMood(weather=weather))
        out = subprocess.run(["ffmpeg", "-loglevel", "error", "-f", "lavfi", "-i", chain, "-frames:v", "1",
                              "-vf", "format=gray", "-f", "image2pipe", "-vcodec", "png", "-"],
                             capture_output=True, check=True).stdout
        from PIL import Image

        img = Image.open(io.BytesIO(out)).convert("L")
        share = 100 * sum(1 for p in img.get_flattened_data() if p > 128) / (480 * 270)
        assert 0.3 < share < limit, (weather, share)
