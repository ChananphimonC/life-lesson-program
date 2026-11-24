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
    assert "ป้าหน่อย" in out and "คุณ" in out


def test_caption_png_has_text_in_the_bottom_band():
    img = render_caption("ขอข้าวมันไก่ต้มจานหนึ่งค่ะ", (640, 360), find_thai_font(None))
    assert img.size == (640, 360)
    top = img.crop((0, 0, 640, 200)).getchannel("A").getbbox()
    bottom = img.crop((0, 280, 640, 360)).getchannel("A").getbbox()
    assert top is None and bottom is not None


def test_captions_follow_the_speech_not_the_letters(tmp_path):
    """Two captions of equal length; the voice talks, pauses for 1 s, talks again -> the 2nd caption starts after the pause."""
    import math, struct, wave
    from life_lesson.video.subtitles import _warp_to_speech
    from life_lesson.video.lipsync import voiced_profile

    rate = 16000
    frames = bytearray()
    for loud, secs in ((True, 1.0), (False, 1.0), (True, 1.0)):
        for n in range(int(rate * secs)):
            frames += struct.pack("<h", int(12000 * math.sin(n * 0.3)) if loud else 0)
    p = tmp_path / "v.wav"
    with wave.open(str(p), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate); w.writeframes(bytes(frames))
    voiced = voiced_profile(p, 0, 3000, 20)
    plain = [("กขคง", 0, 1500), ("จฉชซ", 1500, 3000)]            # by letters: the split lands mid-pause
    warped = _warp_to_speech(plain, voiced, 0, 3000, 20)
    assert warped[0][2] >= 900 and warped[1][1] >= 900            # boundary sits at the end of the first spoken part, not at 1.5 s
    assert warped[1][1] != 1500 and warped[-1][2] == 3000
