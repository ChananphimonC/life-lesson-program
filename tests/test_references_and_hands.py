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
