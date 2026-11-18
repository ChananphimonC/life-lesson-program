import json
import shutil
import subprocess
import wave

import pytest
from PIL import Image

from life_lesson.errors import PipelineError
from life_lesson.generation.atmosphere import BlockMood
from life_lesson.publish.fonts import find_thai_font
from life_lesson.video.illustrator import (
    SETTINGS, character_colors, color_from_text, illustrate_scene, infer_setting,
)
from life_lesson.video.scenes import assemble_scene_video, plan_scenes

from .test_publish_metadata import _script


def test_infer_setting_from_thai_and_english_cues():
    assert infer_setting("นักศึกษานั่งริมหาดบนเกาะ") == "island"
    assert infer_setting("เรือเล็กกลางทะเลตอนฝนตก") == "sea"
    assert infer_setting("a woman at her desk") == "room"
    assert infer_setting("ไม่มีคำบอกใบ้") == "room"
    assert infer_setting("whatever", explicit="forest") == "forest"
    assert infer_setting("whatever", explicit="bogus") == "room"


def test_outfit_colour_words_drive_the_figure():
    assert color_from_text("เสื้อกันฝนสีเหลือง") == (240, 196, 40)
    assert color_from_text("red hoodie") == (206, 52, 48)
    # unknown words fall back to a stable hash colour (same name -> same colour)
    assert color_from_text("???", "นิ่ม") == color_from_text("???", "นิ่ม")
    assert character_colors("เสื้อสีฟ้า", [], "a")["outfit"] == (96, 168, 224)
    assert character_colors("x", ["#102030"], "a")["outfit"] == (16, 32, 48)


@pytest.mark.parametrize("setting", SETTINGS)
def test_every_setting_draws_and_is_deterministic(setting, tmp_path):
    chars = [character_colors("เสื้อสีแดง", [], "ก")]
    a = illustrate_scene((320, 180), setting=setting, mood=BlockMood(light="dark"), characters=chars, seed="x")
    b = illustrate_scene((320, 180), setting=setting, mood=BlockMood(light="dark"), characters=chars, seed="x")
    assert a.size == (320, 180) and a.tobytes() == b.tobytes()
    assert len(set(a.resize((32, 18)).get_flattened_data())) > 10  # not a blank canvas


def test_character_colour_actually_appears_in_the_picture():
    red = character_colors("เสื้อสีแดง", [], "ก")["outfit"]
    img = illustrate_scene((640, 360), setting="street", mood=BlockMood(light="bright"),
                           characters=[character_colors("เสื้อสีแดง", [], "ก")], seed="s")
    assert any(sum(abs(a - b) for a, b in zip(px, red)) < 24 for px in img.get_flattened_data())


def test_plan_scenes_assigns_setting_and_characters():
    s = _script(["เปิด", "สอง", "สาม", "สี่", "จบ"])
    for b, cue in zip(s.script_blocks, ["นิ่มนั่งในห้อง", "นิ่มริมทะเล", "เกาะกลางคืน", "ป่า", "ถนน"]):
        b.visual_cue = cue
    s.characters[0].name = "นิ่ม"
    scenes = plan_scenes(s, [0, 20_000, 40_000, 60_000, 80_000], 100_000)
    assert [x.setting for x in scenes] == ["room", "sea", "island", "forest", "street"]
    assert scenes[0].character_names == ("นิ่ม",) and scenes[0].looks[0]["outfit"] == (240, 196, 40)


def _have_ffmpeg_and_font():
    try:
        find_thai_font()
    except PipelineError:
        return False
    return shutil.which("ffmpeg") is not None


@pytest.mark.skipif(not _have_ffmpeg_and_font(), reason="needs ffmpeg + Thai font")
def test_illustrated_video_needs_no_background_clips(tmp_path):
    s = _script(["เปิด", "สอง", "สาม", "สี่", "จบ"])
    for b, cue in zip(s.script_blocks, ["ห้อง", "ทะเล", "เกาะ", "ป่า", "ถนน"]):
        b.visual_cue = cue
        b.mood = BlockMood(light="dark", weather="storm", tension=5)
    scenes = plan_scenes(s, [0, 4_000, 8_000, 12_000, 16_000], 20_000)
    audio = tmp_path / "a.wav"
    with wave.open(str(audio), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(24000)
        w.writeframes(b"\x00\x00" * 24000 * 20)
    out = assemble_scene_video(
        ffmpeg_binary="ffmpeg", scenes=scenes, background_dir=tmp_path / "does-not-exist",
        audio_path=audio, output_path=tmp_path / "o.mp4", width=640, height=360,
        visual_mode="illustrated")
    probe = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,duration",
                            "-of", "json", str(out)], capture_output=True, text=True, check=True)
    streams = {x["codec_type"]: x for x in json.loads(probe.stdout)["streams"]}
    assert streams["video"]["width"] == 640 and abs(float(streams["video"]["duration"]) - 20) < 0.6


def test_expression_follows_mood():
    from life_lesson.video.illustrator import expression_for

    assert expression_for(None) == "neutral"
    assert expression_for(BlockMood(tension=5, voice="calm")) == "wide"
    assert expression_for(BlockMood(tension=2, voice="urgent")) == "wide"
    assert expression_for(BlockMood(tension=4, voice="calm")) == "worried"
    assert expression_for(BlockMood(tension=2, voice="warm")) == "smile"
    assert expression_for(BlockMood(tension=2, voice="hushed")) == "soft"


def test_faces_differ_between_expressions():
    chars = [character_colors("เสื้อสีแดง", [], "ก")]
    calm = illustrate_scene((640, 360), setting="street", mood=BlockMood(light="dim", voice="calm", tension=2), characters=chars, seed="f")
    scared = illustrate_scene((640, 360), setting="street", mood=BlockMood(light="dim", voice="urgent", tension=5), characters=chars, seed="f")
    assert calm.tobytes() != scared.tobytes()
