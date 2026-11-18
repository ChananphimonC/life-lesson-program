import json
import shutil
import subprocess

import pytest

from life_lesson.errors import PipelineError
from life_lesson.generation.schema import ScriptOutput
from life_lesson.library.shorts import (
    block_end_times, caption_chunks, pick_teaser_window, render_short,
    short_description, short_title,
)
from life_lesson.publish.fonts import find_thai_font


def _script(tensions, phases=None, pause=1000):
    n = len(tensions)
    phases = phases or (["hook"] + ["exploration"] * (n - 3) + ["shift", "outro"])
    blocks = [
        {"sequence": i + 1, "phase": phases[i], "text": f"ประโยคที่ {i + 1} ของเรื่อง นี่คือข้อความ",
         "pause_after_ms": pause, "mood": {"tension": t}}
        for i, t in enumerate(tensions)
    ]
    return ScriptOutput.model_validate({
        "topic_id": "t", "title": "ชั้นห้า", "summary": "คืนหนึ่งในตึกเก่า",
        "metadata": {"mood": "m", "estimated_duration_seconds": 600}, "script_blocks": blocks})


def _timeline(script, block_ms=12_000):
    starts = [i * block_ms for i in range(len(script.script_blocks))]
    return starts, len(starts) * block_ms


def test_window_never_contains_outro_or_the_spoiler_tail():
    s = _script([2, 3, 3, 4, 4, 5, 5, 3, 2])
    starts, total = _timeline(s)
    w = pick_teaser_window(s, starts, total)
    assert all(b.phase != "outro" for b in s.script_blocks[w.first : w.last + 1])
    assert w.end_ms <= total * 0.88
    assert 30 <= w.duration_s <= 55


def test_window_prefers_the_cold_open_when_it_is_tense_enough():
    s = _script([4, 4, 4, 3, 3, 3, 3, 3, 2])
    starts, total = _timeline(s)
    assert pick_teaser_window(s, starts, total).first == 0


def test_window_prefers_the_tense_stretch_over_a_flat_one():
    s = _script([1, 1, 1, 1, 4, 5, 5, 4, 3, 2, 2], phases=["hook"] + ["exploration"] * 8 + ["shift", "outro"])
    starts, total = _timeline(s)
    w = pick_teaser_window(s, starts, total)
    assert w.first >= 3


def test_offset_gives_a_different_short():
    s = _script([2, 3, 3, 4, 4, 5, 5, 3, 2])
    starts, total = _timeline(s)
    a = pick_teaser_window(s, starts, total, offset=0)
    b = pick_teaser_window(s, starts, total, offset=1)
    assert (a.first, a.last) != (b.first, b.last)


def test_tiny_episode_still_yields_a_window():
    s = _script([2, 3, 4, 2])
    starts, total = _timeline(s, block_ms=8_000)
    w = pick_teaser_window(s, starts, total)
    assert w.last >= w.first and w.duration_s <= 55


def test_block_ends_subtract_scaled_pause():
    s = _script([5, 5, 5, 5], pause=2000)
    ends = block_end_times(s, [0, 10_000, 20_000, 30_000], 40_000)
    assert ends[0] == 10_000 - 1100  # tension 5 -> 55% of 2000ms


def test_caption_chunks_are_short_and_cover_the_whole_block():
    text = "ถ้าซอมบี้ตามเสียง ที่ปลอดภัยที่สุดคือ กลางน้ำ อย่าเพิ่งส่งเสียงแม้แต่หยดเดียว"
    chunks = caption_chunks(text, 1000, 9000)
    assert all(len(c) <= 26 for c, _, _ in chunks)
    assert chunks[0][1] == 1000 and chunks[-1][2] == 9000
    assert all(a[2] == b[1] for a, b in zip(chunks, chunks[1:]))
    assert caption_chunks("", 0, 100) == []
    assert len(caption_chunks("ก" * 80, 0, 100)) == 4  # no-space text is hard-wrapped


def test_title_and_description_point_to_the_channel():
    s = _script([2, 3, 3, 4, 4, 5, 5, 3, 2])
    starts, total = _timeline(s)
    w = pick_teaser_window(s, starts, total)
    assert len(short_title(s, w)) <= 40
    d = short_description(s, channel_handle="@SakidJai_สะกิดใจ", channel_url="https://y/c", full_url="https://y/v")
    assert "@SakidJai_สะกิดใจ" in d and "https://y/v" in d and "#Shorts" in d and "สร้างด้วย AI" in d
    assert "https://y/c" in short_description(s, channel_handle="@x", channel_url="https://y/c")


def _ready():
    try:
        find_thai_font()
    except PipelineError:
        return False
    return shutil.which("ffmpeg") is not None


@pytest.mark.skipif(not _ready(), reason="needs ffmpeg + Thai font")
def test_real_cut_is_vertical_with_cta_tail(tmp_path):
    src = tmp_path / "full.mp4"
    subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i", "testsrc2=s=640x360:d=120:r=15",
                    "-f", "lavfi", "-i", "sine=f=300:d=120", "-shortest", "-pix_fmt", "yuv420p", str(src)],
                   check=True, capture_output=True)
    s = _script([2, 3, 3, 4, 4, 5, 5, 3, 2])
    starts, total = _timeline(s, 12_000)
    ends = block_end_times(s, starts, total)
    w = pick_teaser_window(s, starts, total)
    out = render_short(ffmpeg_binary="ffmpeg", source_video=src, window=w, script=s, starts_ms=starts,
                       ends_ms=ends, output_path=tmp_path / "s.mp4", channel_handle="@SakidJai_สะกิดใจ",
                       title="ชั้นห้า", width=360, height=640)
    probe = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height,duration",
                            "-of", "json", str(out)], capture_output=True, text=True, check=True)
    st = {x["codec_type"]: x for x in json.loads(probe.stdout)["streams"]}
    assert (st["video"]["width"], st["video"]["height"]) == (360, 640) and "audio" in st
    assert abs(float(st["video"]["duration"]) - (w.duration_s + 3)) < 0.8
