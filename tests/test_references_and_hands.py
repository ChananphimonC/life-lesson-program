import json
import math
from io import BytesIO

from PIL import Image, ImageDraw

from life_lesson.generation.atmosphere import BlockMood
from life_lesson.video.illustrator import (
    _ik, character_colors, illustrate_scene, items_from_text,
)
from life_lesson.video.references import (
    blended_palette, dominant_palette, search_references,
)
from life_lesson.video.scenes import plan_scenes

from .test_publish_metadata import _script


# ---- reference lookup (fake network) -------------------------------------------

def _png(color):
    buf = BytesIO()
    img = Image.new("RGB", (80, 80), color)
    ImageDraw.Draw(img).rectangle([0, 0, 79, 20], fill=(10, 10, 10))
    img.save(buf, "PNG")
    return buf.getvalue()


class FakeNet:
    def __init__(self):
        self.urls = []

    def __call__(self, url):
        self.urls.append(url)
        if "api.openverse.org" in url:
            return json.dumps({"results": [
                {"title": "Wok", "creator": "Somchai", "license": "by", "license_version": "4.0",
                 "foreign_landing_url": "https://x/1", "thumbnail": "https://t/1.png"},
                {"title": "Stall", "creator": "", "license": "cc0", "license_version": "1.0",
                 "url": "https://x/2", "thumbnail": "https://t/2.png"}]}).encode()
        return _png((200, 60, 40) if url.endswith("1.png") else (40, 80, 200))


def test_palette_is_extracted_most_common_first():
    pal = dominant_palette(_png((200, 60, 40)))
    assert max(abs(a - b) for a, b in zip(pal[0], (200, 60, 40))) < 30


def test_search_returns_credited_references_and_only_sends_generic_query(tmp_path):
    net = FakeNet()
    refs = search_references("thai street food stall night", fetch=net, cache_dir=tmp_path)
    assert [r.title for r in refs] == ["Wok", "Stall"]
    assert refs[0].credit_line.startswith('Reference photo "Wok" by Somchai (BY 4.0)')
    assert "license_type=commercial" in net.urls[0] and "thai+street+food" in net.urls[0]
    assert len(blended_palette(refs)) >= 2


def test_search_is_cached(tmp_path):
    net = FakeNet()
    search_references("q", fetch=net, cache_dir=tmp_path)
    n = len(net.urls)
    again = search_references("q", fetch=net, cache_dir=tmp_path)
    assert len(net.urls) == n and again[0].title == "Wok"


def test_network_failure_never_raises():
    def boom(url):
        raise OSError("403 proxy")

    assert search_references("q", fetch=boom) == []


# ---- arms and hands ------------------------------------------------------------

def test_two_bone_arm_reaches_targets_and_keeps_bone_lengths():
    shoulder, U, F = (100.0, 100.0), 30.0, 30.0
    for target in [(130, 150), (60, 120), (120, 60), (100, 158)]:
        elbow, hand = _ik(shoulder, target, U, F)
        assert math.dist(shoulder, elbow) - U < 0.01 and abs(math.dist(elbow, hand) - F) < 0.01
        assert math.dist(hand, target) < 0.6
        assert elbow[1] >= min(shoulder[1], hand[1]) - 31  # elbow bends down, never inverts


def test_unreachable_target_is_clamped_not_stretched():
    elbow, hand = _ik((0, 0), (500, 0), 30, 30)
    assert math.dist((0, 0), hand) <= 60


def test_items_are_read_from_outfit_text():
    assert items_from_text("เอี๊ยมสีครีม ผ้าคลุมผม แว่นตา") == {"apron", "hairnet", "glasses"}
    assert items_from_text("เสื้อกันฝนสีเหลือง กระเป๋าเป้") == {"hood", "backpack"}
    assert character_colors("เสื้อโปโลสีชมพู", [], "ก")["sleeve"] == "short"
    assert character_colors("เสื้อฮู้ดสีเทา", [], "ก")["sleeve"] == "long"


def test_accessories_change_the_drawing():
    base = character_colors("เสื้อสีฟ้า", [], "ก")
    kitted = character_colors("เสื้อสีฟ้า", [], "ก", extra_items=("apron", "hairnet", "glasses"))
    mood = BlockMood(light="bright")
    a = illustrate_scene((480, 270), setting="street", mood=mood, characters=[base], seed="x")
    b = illustrate_scene((480, 270), setting="street", mood=mood, characters=[kitted], seed="x")
    assert a.tobytes() != b.tobytes()


# ---- the kaprao stall -----------------------------------------------------------

def _stall_script():
    s = _script(["เปิด", "สอง", "สาม", "สี่", "จบ"])
    s.characters[0].name = "เจ๊"
    s.characters[0].role = "แม่ค้าร้านตามสั่ง"
    s.characters[0].outfit = "เสื้อโปโลสีชมพู"
    for b in s.script_blocks:
        b.visual_cue = "เจ๊ร้านตามสั่งผัดกะเพราในกระทะไฟลุกตอนดึก"
    return s


def test_stall_cue_gives_the_cook_an_apron_hairnet_and_short_sleeves():
    scenes = plan_scenes(_stall_script(), [0, 20_000, 40_000, 60_000, 80_000], 100_000)
    assert scenes[0].setting == "food_stall" and scenes[0].recipe_id == "food_stall"
    look = scenes[0].looks[0]
    assert {"apron", "hairnet", "towel"} <= set(look["items"]) and look["sleeve"] == "short"


def test_customer_does_not_get_the_cooks_wardrobe():
    s = _stall_script()
    s.characters[0].name, s.characters[0].role, s.characters[0].outfit = "นิ่ม", "นักศึกษา", "เสื้อกันฝนสีเหลือง"
    look = plan_scenes(s, [0, 20_000, 40_000, 60_000, 80_000], 100_000)[0].looks[0]
    assert "apron" not in look["items"]


def test_stall_scene_renders_with_cook_flame_and_plate():
    cook = character_colors("เสื้อโปโลสีชมพู", [], "เจ๊", extra_items=("apron", "hairnet"), sleeve="short")
    img = illustrate_scene((640, 360), setting="food_stall", mood=BlockMood(light="dim", color="amber"),
                           characters=[cook], seed="k")
    px = list(img.get_flattened_data())
    assert any(r > 220 and 90 < g < 170 and b < 80 for r, g, b in px)  # orange flame
    assert any(r > 240 and g > 240 and b > 235 for r, g, b in px)       # white plate/egg
    assert any(abs(r - 248) < 12 and abs(g - 178) < 14 and b < 60 for r, g, b in px)  # yolk


def test_reference_palette_nudges_the_scene():
    cook = character_colors("เสื้อโปโลสีชมพู", [], "เจ๊", extra_items=("apron",))
    kw = dict(setting="food_stall", mood=BlockMood(light="dim"), characters=[cook], seed="k")
    plain = illustrate_scene((320, 180), **kw)
    tinted = illustrate_scene((320, 180), reference_palette=((200, 40, 40), (180, 60, 40)), **kw)
    assert plain.tobytes() != tinted.tobytes()


# ---- story scenes: place changes, alley, props, wardrobe -----------------------

def _story_script():
    s = _script(list("abcdefgh"))
    s.characters = [
        type(s.characters[0])(name="ต้อม", role="ไรเดอร์", outfit="เสื้อกันฝนสีเหลือง", palette=["#f0c428"]),
        type(s.characters[0])(name="เจ๊ปุ้ย", role="แม่ค้าร้านตามสั่ง", outfit="เสื้อโปโลสีชมพู"),
        type(s.characters[0])(name="ลุงแมว", role="คนกวาดซอย", outfit="เสื้อสะท้อนแสงสีส้ม หมวก", signature_item="ไม้กวาดและไฟคาดหัว"),
    ]
    cues = ["ต้อม เจ๊ปุ้ย ร้านตามสั่ง", "ต้อม เจ๊ปุ้ย ร้านตามสั่ง", "ต้อมในซอยตัน มีเงายืนอยู่สุดซอย", "ต้อมในซอยตัน",
            "ลุงแมวในซอยตัน ไฟคาดหัวสว่าง ต้อม", "เจ๊ปุ้ย ต้อม ร้านตามสั่ง", "ร้านตามสั่ง จานที่ช่องหน้าต่างหลังร้าน ต้อม", "ต้อม"]
    places = ["food_stall", "food_stall", "alley", "alley", "alley", "food_stall", "food_stall", "food_stall"]
    for b, c, pl in zip(s.script_blocks, cues, places):
        b.visual_cue, b.setting, b.chapter_title = c, pl, "บทเดียว"  # ONE chapter, several places
    return s


def test_a_change_of_place_inside_one_chapter_starts_a_new_scene():
    scenes = plan_scenes(_story_script(), [i * 10_000 for i in range(8)], 80_000)
    assert [x.setting for x in scenes] == ["food_stall", "alley", "food_stall"]
    assert len({x.title for x in scenes}) == 1 and scenes[0].end_ms == scenes[1].start_ms


def test_alley_cues_resolve_to_the_alley_setting():
    from life_lesson.video.scene_kb import retrieve_recipe

    assert retrieve_recipe("ต้อมในซอยตันหลังร้าน").setting == "alley"
    assert retrieve_recipe("เจ๊ร้านตามสั่งในซอยตัน").setting == "food_stall"  # the stall keyword wins


def test_props_come_from_the_cue():
    from life_lesson.video.scene_kb import props_from_cue

    assert props_from_cue("จานที่ช่องหน้าต่างหลังร้าน") == ("ledge_plate",)
    assert set(props_from_cue("ช่องหน้าต่างมีจานสองใบ")) >= {"ledge_plate", "second_plate"}
    assert "far_silhouette" in props_from_cue("มีเงายืนอยู่สุดซอย") and "half_eaten" in props_from_cue("ไข่ดาวหายไปครึ่งฟอง")
    assert props_from_cue("เฉยๆ") == ()


def test_sweeper_is_not_given_the_cooks_wardrobe_and_gets_his_headlamp():
    scenes = plan_scenes(_story_script(), [i * 10_000 for i in range(8)], 80_000)
    alley = next(x for x in scenes if x.setting == "alley")
    sweeper = next(l for l, n in zip(alley.looks, alley.character_names) if n == "ลุงแมว")
    assert "apron" not in sweeper["items"] and "headlamp" in sweeper["items"] and "cap" in sweeper["items"]
    assert "far_silhouette" in alley.props or "far_silhouette" in scenes[1].props


def test_empty_stall_has_no_flame_and_the_far_silhouette_is_dark():
    from life_lesson.generation.atmosphere import BlockMood

    mood = BlockMood(light="dim", weather="clear")
    cook = character_colors("เสื้อโปโลสีชมพู", [], "เจ๊", extra_items=("apron", "hairnet"), sleeve="short")
    cust = character_colors("เสื้อสีฟ้า", [], "ต้อม")
    with_cook = illustrate_scene((640, 360), setting="food_stall", mood=mood, characters=[cook, cust], seed="k")
    no_cook = illustrate_scene((640, 360), setting="food_stall", mood=mood, characters=[cust], seed="k")

    def orange(img):
        return sum(1 for r, g, b in img.get_flattened_data() if r > 230 and 100 < g < 180 and b < 90)

    assert orange(with_cook) > 150 and orange(no_cook) < orange(with_cook) * 0.2  # burner is off

    img = illustrate_scene((640, 360), setting="alley", mood=BlockMood(light="dark"), characters=[cust],
                           seed="a", props=("far_silhouette",))
    # a near-black figure stands where the lamp glow is brightest (centre-right of the alley)
    dark = sum(1 for x in range(330, 450) for y in range(110, 230) if sum(img.getpixel((x, y))) < 40)
    assert dark > 600


def test_ledge_plate_is_drawn_only_when_asked():
    cust = character_colors("เสื้อสีฟ้า", [], "ต้อม")
    kw = dict(setting="food_stall", mood=None, characters=[cust], seed="k")
    a = illustrate_scene((640, 360), **kw)
    b = illustrate_scene((640, 360), props=("ledge_plate",), **kw)
    assert a.tobytes() != b.tobytes()


def test_chapter_card_is_rendered_once_per_chapter_title(tmp_path, monkeypatch):
    """Drive the real assembler with ffmpeg and the drawing stubbed out; count card renders."""
    from life_lesson.video import scenes as sc

    cards = []
    monkeypatch.setattr(sc, "_run", lambda *a, **k: None)
    monkeypatch.setattr(sc, "illustrate_scene", lambda *a, **k: Image.new("RGB", (4, 4)).save(k["out_path"]))
    monkeypatch.setattr(sc, "render_chapter_card", lambda scene, size, out, **k: cards.append(scene.title))
    scenes = [sc.Scene(0, 0, 5000, "ซอยตัน", None, None), sc.Scene(1, 5000, 9000, "ซอยตัน", None, None),
              sc.Scene(2, 9000, 12000, "คนกวาดซอย", None, None)]
    audio = tmp_path / "a.wav"
    audio.write_bytes(b"x")
    sc.assemble_scene_video(ffmpeg_binary="ffmpeg", scenes=scenes, background_dir=tmp_path, audio_path=audio,
                            output_path=tmp_path / "o.mp4", width=64, height=36, visual_mode="illustrated")
    assert cards == ["ซอยตัน", "คนกวาดซอย"]


def test_menu_sign_text_is_drawn_even_when_no_font_is_passed():
    from life_lesson.errors import PipelineError
    from life_lesson.publish.fonts import find_thai_font

    try:
        find_thai_font()
    except PipelineError:
        import pytest

        pytest.skip("no Thai font")
    cust = character_colors("เสื้อสีฟ้า", [], "ต้อม")
    img = illustrate_scene((960, 540), setting="food_stall", mood=None, characters=[cust], seed="k")  # no font_path
    sign = img.crop((int(960 * 0.06), int(540 * 0.2), int(960 * 0.36), int(540 * 0.36)))
    light = sum(1 for r, g, b in sign.get_flattened_data() if r > 230 and g > 220)  # cream lettering on the red board
    assert light > 150


# ---- the bus (frames of "แกล้งหลับ ทั้งคันรถ") -----------------------------------

def _bus_script():
    from pathlib import Path

    from life_lesson.generation.schema import validate_script_json

    return validate_script_json((Path(__file__).resolve().parents[1] / "stories" / "bus_seat" / "script.json").read_text(encoding="utf-8"))


def test_the_bus_story_is_a_valid_standard_script_with_no_mechanical_lint_findings():
    from life_lesson.generation.formats import get_format
    from life_lesson.generation.schema import check_format
    from life_lesson.generation.suspense import lint_script

    s = _bus_script()
    check_format(s, get_format("standard"))
    assert all(b.setting == "bus" for b in s.script_blocks)
    assert lint_script(s, "story").objective_penalty == 0


def test_bus_cues_resolve_to_the_bus_and_pick_story_props():
    from life_lesson.video.scene_kb import props_from_cue, retrieve_recipe

    assert retrieve_recipe("ใบเฟิร์นยืนโหนราวเหล็กในรถเมล์แน่น").setting == "bus"
    assert "passengers_awake" in props_from_cue("ผู้โดยสารทั้งคันรถเมล์ลืมตาพร้อมกัน")
    assert "protagonist_seated" in props_from_cue("ใบเฟิร์นนั่งลงบนรถเมล์")


def test_items_for_the_bus_cast_come_from_their_outfits_and_roles():
    s = _bus_script()
    scenes = plan_scenes(s, [i * 20_000 for i in range(12)], 240_000)
    by_name = {}
    for sc in scenes:
        for n, look in zip(sc.character_names, sc.looks):
            by_name.setdefault(n, look)
    assert {"skirt_white", "waist_wrap"} <= set(by_name["ใบเฟิร์น"]["items"])
    assert {"earbuds", "seated"} <= set(by_name["ไอซ์"]["items"])
    assert "shopping_bags" in by_name["ป้าแตน"]["items"]


def _bus_frame(props=(), mood=None, who=("ใบเฟิร์น", "ไอซ์")):
    from life_lesson.generation.atmosphere import BlockMood

    s = _bus_script()
    looks = []
    for c in s.characters:
        if c.name in who:
            looks.append(character_colors(c.outfit, c.palette, c.name, extra_items=("seated",) if "นั่ง" in c.role else ()))
    return illustrate_scene((640, 360), setting="bus", mood=mood or BlockMood(light="dim", tension=3), characters=looks, seed="b", props=props)


def test_every_bus_prop_changes_the_picture_and_eyes_open_vs_shut_differ():
    base = _bus_frame()
    assert base.tobytes() != _bus_frame(props=("passengers_awake",)).tobytes()      # the whole bus opens its eyes
    assert base.tobytes() != _bus_frame(props=("protagonist_seated",)).tobytes()    # she has the seat, he stands


def test_standing_passenger_is_not_shorter_than_the_seated_ones():
    """Regression: seated figures (a desk pose) once towered over the close standing one."""
    img = _bus_frame()
    px = img.load()
    blue = (127, 179, 224)  # her shirt colour: topmost shirt pixel ~ head height proxy
    ys = [y for y in range(360) for x in range(0, 640, 2) if all(abs(a - b) < 14 for a, b in zip(px[x, y], blue))]
    assert ys and min(ys) < 360 * 0.62  # her torso reaches up into the window band, like the seated passengers' heads


def test_engine_sound_exists_and_is_audible():
    import shutil
    import subprocess

    import pytest

    from life_lesson.audio.ambient import scene_filtergraph
    from life_lesson.generation.atmosphere import BlockMood

    g = scene_filtergraph(BlockMood(sounds=["engine"]), 2.0)
    assert g and "lowpass=f=110" in g
    if shutil.which("ffmpeg") is None:
        pytest.skip("no ffmpeg")
    r = subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-filter_complex", g, "-map", "[out]", "-t", "2", "-f", "null", "-"], capture_output=True)
    assert r.returncode == 0
