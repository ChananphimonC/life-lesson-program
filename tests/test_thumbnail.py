import pytest
from PIL import Image

from life_lesson.errors import PipelineError
from life_lesson.generation.formats import get_format
from life_lesson.publish.fonts import find_thai_font
from life_lesson.publish.metadata import build_thumbnail_spec
from life_lesson.publish.thumbnail import render_thumbnail

from .test_publish_metadata import _script

try:
    find_thai_font()
    HAS_FONT = True
except PipelineError:
    HAS_FONT = False

pytestmark = pytest.mark.skipif(not HAS_FONT, reason="no Thai font installed")


def test_render_long_thumbnail(tmp_path):
    spec = build_thumbnail_spec(_script(list("abcde")), get_format("long"), 20 * 60_000)
    out = render_thumbnail(spec, tmp_path / "t.png")
    img = Image.open(out)
    assert img.size == (1920, 1080)
    # not a blank image: text pixels exist (white/yellow among dark background)
    assert len(set(img.convert("RGB").resize((64, 36)).get_flattened_data())) > 20


def test_render_short_is_vertical(tmp_path):
    spec = build_thumbnail_spec(_script(list("abcde")), get_format("short"), 40_000)
    img = Image.open(render_thumbnail(spec, tmp_path / "s.png"))
    assert img.size == (1080, 1920)


def test_missing_font_gives_clear_error(monkeypatch):
    monkeypatch.setattr("life_lesson.publish.fonts._CANDIDATES", [])
    with pytest.raises(PipelineError, match="THAI_FONT_PATH"):
        find_thai_font()


def test_headline_never_cuts_a_word_in_half():
    from life_lesson.publish.metadata import _split_headline

    assert _split_headline("กะเพรา จานสุดท้าย") == ("กะเพรา", "จานสุดท้าย")
    assert _split_headline("หนึ่ง สอง สาม") == ("หนึ่ง สอง", "สาม")
    one, two = _split_headline("กะเพราจานสุดท้าย")
    assert one + two == "กะเพราจานสุดท้าย"           # nothing lost
    assert two == "" or one in ("กะเพรา", "กะเพราจาน")  # only a real word boundary (needs pythainlp)


def test_single_line_title_renders(tmp_path):
    spec = build_thumbnail_spec(_script(list("abcde")), get_format("long"), 60_000)
    spec["headline_line1"], spec["headline_line2"] = "กะเพราจานสุดท้าย", ""
    assert Image.open(render_thumbnail(spec, tmp_path / "t.png")).size == (1920, 1080)


def test_backdrop_puts_the_subject_on_the_right():
    from life_lesson.generation.atmosphere import BlockMood
    from life_lesson.video.illustrator import character_colors, thumbnail_backdrop

    cook = character_colors("เสื้อโปโลสีชมพู", [], "เจ๊", extra_items=("apron", "hairnet"), sleeve="short")
    img = thumbnail_backdrop((640, 360), setting="food_stall", mood=BlockMood(light="dim"), characters=[cook], seed="k")
    assert img.size == (640, 360)
    # pink polo (232,160,184)-ish pixels should sit mostly in the right half
    px = img.load()
    pink = [x for x in range(640) for y in range(360) if abs(px[x, y][0] - 232) < 30 and abs(px[x, y][1] - 160) < 30 and abs(px[x, y][2] - 184) < 30]
    assert pink and sum(1 for x in pink if x > 320) / len(pink) > 0.6
