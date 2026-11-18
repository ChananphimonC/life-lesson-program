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
