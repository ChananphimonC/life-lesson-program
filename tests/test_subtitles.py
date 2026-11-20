import json
from pathlib import Path

from life_lesson.generation.schema import ScriptOutput
from life_lesson.publish.fonts import find_thai_font
from life_lesson.video.subtitles import caption_cues, render_caption, write_srt

SCRIPT = ScriptOutput.model_validate(json.loads(Path("stories/chicken_rice/script.json").read_text(encoding="utf-8")))


def _timeline():
    starts = [i * 15000 for i in range(len(SCRIPT.script_blocks))]
    return starts, len(starts) * 15000


def test_captions_are_the_script_text_exactly():
    """No tone mark / vowel may be lost: the captions rejoined equal the script, ignoring spaces."""
    starts, total = _timeline()
    cues = caption_cues(SCRIPT, starts, total)
    got = "".join(t.replace(" ", "") for t, _, _ in cues)
    want = "".join(b.text.replace(" ", "").replace("\n", "") for b in SCRIPT.script_blocks)
    assert got == want
    assert all(len(t) <= 40 for t, _, _ in cues)
    assert all(a < b for _, a, b in cues) and all(cues[i][2] <= cues[i + 1][1] for i in range(len(cues) - 1))


def test_srt_format(tmp_path):
    starts, total = _timeline()
    out = write_srt(caption_cues(SCRIPT, starts, total), tmp_path / "s.srt").read_text(encoding="utf-8")
    assert out.startswith("1\n00:00:00,000 --> ")
    assert "ฟ้าใส" in out and "ป้าหน่อย" in out


def test_caption_png_has_text_in_the_bottom_band():
    img = render_caption("ขอข้าวมันไก่ต้มจานหนึ่งค่ะ", (640, 360), find_thai_font(None))
    assert img.size == (640, 360)
    top = img.crop((0, 0, 640, 200)).getchannel("A").getbbox()
    bottom = img.crop((0, 280, 640, 360)).getchannel("A").getbbox()
    assert top is None and bottom is not None
