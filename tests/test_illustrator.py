import json
import shutil
import subprocess
import wave

import pytest

from life_lesson.errors import PipelineError
from life_lesson.generation.atmosphere import BlockMood
from life_lesson.publish.fonts import find_thai_font
from life_lesson.video.illustrator import (
    SETTINGS, character_colors, color_from_text, illustrate_scene,
)
from life_lesson.video.scenes import assemble_scene_video, plan_scenes

from .test_publish_metadata import _script


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


def test_speaker_gets_focus_and_open_mouth(tmp_path):
    from life_lesson.video.illustrator import character_colors, illustrate_scene

    cast = [character_colors("เสื้อยืดสีฟ้า", None, name="ไอซ์", hair="ผมสั้น สีดำ", gender="ชาย"),
            character_colors("เสื้อเบลาส์สีแดง", None, name="ใบเฟิร์น", hair="ผมยาว สีน้ำตาล", gender="หญิง")]
    focus: dict = {}
    illustrate_scene((640, 360), setting="bus", mood=BlockMood(light="dark"), characters=cast, seed=1,
                     out_path=tmp_path / "a.png", speaker="ไอซ์", focus_out=focus)
    assert 0 < focus["x"] < 1 and 0 < focus["y"] < 1
    quiet: dict = {}
    illustrate_scene((640, 360), setting="bus", mood=BlockMood(light="dark"), characters=cast, seed=1,
                     out_path=tmp_path / "b.png", focus_out=quiet)
    assert quiet == {}


def test_animation_phases_change_the_picture(tmp_path):
    """Limited animation: different phases must draw different frames (stir, walk, mouth) -- not copies of one still."""
    from PIL import ImageChops
    from life_lesson.video.illustrator import character_colors, illustrate_scene

    cook = character_colors("เสื้อสีขาว", None, name="ป้า", extra_items=("apron",))
    walker = character_colors("เสื้อสีฟ้า", None, name="ต้อม")
    mood = BlockMood(light="dark")

    def frame(setting, chars, ph, props=(), speaker=None, mouth=0):
        return illustrate_scene((480, 270), setting=setting, mood=mood, characters=chars, seed=1, props=props,
                                speaker=speaker, anim={"phase": ph, "breath": 0.0, "blink": False, "mouth": mouth})

    assert ImageChops.difference(frame("food_stall", [cook], 0), frame("food_stall", [cook], 2)).getbbox()
    assert ImageChops.difference(frame("street", [walker], 0, ("walking",)), frame("street", [walker], 2, ("walking",))).getbbox()
    assert ImageChops.difference(frame("street", [walker], 0, (), "ต้อม", 0), frame("street", [walker], 0, (), "ต้อม", 1)).getbbox()


def test_new_places_draw_and_cart_vendor_chops(tmp_path):
    from PIL import ImageChops
    from life_lesson.video.illustrator import SETTINGS, character_colors, illustrate_scene

    assert {"chicken_cart", "market", "mall"} <= set(SETTINGS)
    vendor = character_colors("เสื้อสีเหลือง", None, name="ป้า", extra_items=("apron",))
    mood = BlockMood(light="golden")
    imgs = [illustrate_scene((480, 270), setting=st, mood=mood, characters=[vendor], seed=1) for st in ("chicken_cart", "market", "mall")]
    assert all(ImageChops.difference(imgs[0], i).getbbox() for i in imgs[1:])   # three different places
    f = lambda ph: illustrate_scene((480, 270), setting="chicken_cart", mood=mood, characters=[vendor], seed=1,
                                    anim={"phase": ph, "breath": 0.0, "blink": False, "mouth": 0})
    assert ImageChops.difference(f(0), f(2)).getbbox()      # the cleaver comes down: not a still picture


def test_office_and_kitchen_have_detail_and_people_cast_shadows():
    from PIL import ImageChops
    from life_lesson.video.illustrator import character_colors, illustrate_scene

    mood = BlockMood(light="bright")
    cook = character_colors("เสื้อสีเหลือง", None, name="ป้า", extra_items=("apron",), age="50s", hair="ผมดัดลอนสั้น สีเทา", gender="หญิง")
    assert cook["older"] is True and cook["hair_style"] == "curly"
    young = character_colors("เสื้อสีฟ้า", None, name="ฟ้า", age="20s", gender="หญิง")
    assert young["older"] is False
    for st in ("office", "kitchen"):
        empty = illustrate_scene((480, 270), setting=st, mood=mood, characters=[], seed=1)
        full = illustrate_scene((480, 270), setting=st, mood=mood, characters=[young], seed=1)
        assert ImageChops.difference(empty, full).getbbox()
    # office wall clock / window: not a flat colour field
    office = illustrate_scene((480, 270), setting="office", mood=mood, characters=[], seed=1)
    assert len(set(office.resize((48, 27)).getdata())) > 40


def test_scene_things_really_move_between_steps():
    """Flames, steam/bubbles, bulbs, flickering lights, serving a plate and crossing the street are all animated."""
    from PIL import ImageChops
    from life_lesson.video.illustrator import character_colors, illustrate_scene

    cook = character_colors("เสื้อสีเหลือง", None, name="ป้า", extra_items=("apron",))
    walker = character_colors("เสื้อสีฟ้า", None, name="ต้อม")

    def fr(setting, ph, chars=(), props=(), light="golden", prog=None):
        return illustrate_scene((480, 270), setting=setting, mood=BlockMood(light=light), characters=list(chars), seed=1, props=props,
                                anim={"phase": ph, "breath": 0.0, "blink": False, "mouth": 0, "prog": prog})

    differs = lambda a, b: ImageChops.difference(a, b).getbbox() is not None
    assert differs(fr("kitchen", 0), fr("kitchen", 3))                       # fire + bubbles + steam
    assert differs(fr("chicken_cart", 0, light="dim"), fr("chicken_cart", 1, light="dim"))   # bulbs twinkle
    assert differs(fr("office", 0, light="flicker"), fr("office", 1, light="flicker"))        # tube flickers
    assert differs(fr("chicken_cart", 0, [cook], ("serving",)), fr("chicken_cart", 2, [cook], ("serving",)))
    a, b = fr("street", 0, [walker], ("walking",), prog=0.1), fr("street", 0, [walker], ("walking",), prog=0.9)
    assert differs(a, b)                                                     # the walker crosses the frame


def test_bts_scrolls_and_compare_shows_both_columns():
    from PIL import ImageChops
    from life_lesson.video.illustrator import SETTINGS, character_colors, illustrate_scene

    assert {"bts", "compare"} <= set(SETTINGS)
    fa = character_colors("เสื้อสีฟ้า", None, name="ฟ้า")
    vendor = character_colors("เสื้อสีเหลือง", None, name="ป้า", extra_items=("apron",))
    mood = BlockMood(light="bright")
    f = lambda ph: illustrate_scene((480, 270), setting="bts", mood=mood, characters=[fa], seed=1,
                                    anim={"phase": ph, "breath": 0.0, "blink": False, "mouth": 0})
    assert ImageChops.difference(f(0), f(3)).getbbox()          # the city slides past the window
    img = illustrate_scene((480, 270), setting="compare", mood=mood, characters=[fa, vendor], seed=1)
    left, right = img.crop((0, 0, 240, 270)), img.crop((240, 0, 480, 270))
    assert ImageChops.difference(left, right).getbbox()
    assert left.getpixel((5, 5)) != right.getpixel((5, 5))     # cool column vs warm column


def test_every_setting_has_some_motion_between_steps():
    """No scene is a still: stars/windows/waves/bus sway/etc. differ between animation steps."""
    from PIL import ImageChops
    from life_lesson.video.illustrator import SETTINGS, character_colors, illustrate_scene

    fa = character_colors("เสื้อสีฟ้า", None, name="ฟ้า")
    cook = character_colors("เสื้อสีเหลือง", None, name="ป้า", extra_items=("apron",))   # a stall with no cook is cold on purpose
    mood = BlockMood(light="dark")
    for st in SETTINGS:
        f = lambda ph: illustrate_scene((320, 180), setting=st, mood=mood, characters=[cook if st == "food_stall" else fa], seed="m",
                                        compare={"left": "A", "right": "B", "rows": [{"label": "x", "left": 1, "right": 2}]},
                                        anim={"phase": ph, "breath": 0.0, "blink": False, "mouth": 0})
        assert any(ImageChops.difference(f(0), f(k)).getbbox() for k in (1, 2, 3)), st


def test_captions_never_orphan_a_thai_vowel_or_tone_mark():
    from life_lesson.library.shorts import caption_chunks

    text = "เธอเดินผ่านห้างสรรพสินค้าที่เปิดแอร์เย็นจัดแล้วซื้อขนมอย่างไม่ได้ตั้งใจถุงใหญ่กว่าที่คิด" * 2
    for chunk, _, _ in caption_chunks(text, 0, 10000, 20):
        assert chunk[0] not in "ะาำัิีึืุู็่้๊๋์ๆ", chunk
        assert chunk[-1] not in "เแโใไ", chunk
    assert "".join(c for c, _, _ in caption_chunks(text, 0, 10000, 20)).replace(" ", "") == text


def test_bus_stop_bus_rolls_in_and_new_items_draw():
    from PIL import ImageChops
    from life_lesson.video.illustrator import SETTINGS, character_colors, illustrate_scene

    assert "bus_stop" in SETTINGS
    f = lambda pr: illustrate_scene((480, 270), setting="bus_stop", mood=BlockMood(light="golden"), characters=[], seed=1,
                                    props=("arriving",), anim={"phase": 0, "breath": 0.0, "blink": False, "mouth": 0, "prog": pr})
    assert ImageChops.difference(f(0.1), f(0.9)).getbbox()
    plain = character_colors("เสื้อสีฟ้า", None, name="พี่")
    conductor = character_colors("เสื้อสีฟ้า กระเป๋ากระบอกตั๋ว", None, name="พี่")
    laptop = character_colors("เสื้อสีขาว ถุงใส่โน้ตบุ๊ก", None, name="น้ำ")
    assert "conductor_bag" in conductor["items"] and "laptop_bag" in laptop["items"] and "conductor_bag" not in plain["items"]
