import json

from life_lesson.generation.formats import get_format
from life_lesson.generation.schema import ScriptOutput
from life_lesson.publish.metadata import (
    build_chapters,
    build_description,
    build_review_checklist,
    build_thumbnail_spec,
    build_title,
    format_timestamp,
    write_publish_bundle,
)


def _script(chapter_titles, **extra):
    phases = ["hook", "exploration", "exploration", "shift", "outro"]
    blocks = [
        {"sequence": i + 1, "phase": phases[min(i, 4)], "text": "x", "pause_after_ms": 0,
         "chapter_title": t, "visual_cue": "ภาพ", "time_label": "23:47" if i == 0 else None}
        for i, t in enumerate(chapter_titles)
    ]
    data = {"topic_id": "t", "title": "ชั้นห้า เสียงเคาะ",
            "summary": "คืนหนึ่งในตึกเก่า",
            "metadata": {"mood": "calm", "estimated_duration_seconds": 1000},
            "script_blocks": blocks,
            "facts": [{"claim": "เสียงสะท้อนในตึกว่าง", "source_hint": "ฟิสิกส์เสียง", "confidence": "low"}],
            "characters": [{"name": "นิ่ม", "outfit": "เสื้อกันฝนสีเหลือง"}]}
    data.update(extra)
    return ScriptOutput.model_validate(data)


def test_timestamp_format():
    assert format_timestamp(0) == "0:00"
    assert format_timestamp(125_000) == "2:05"
    assert format_timestamp(3_725_000) == "1:02:05"


def test_chapters_start_at_zero_and_merge_short_ones():
    s = _script(["เปิด", "บทหนึ่ง", "บทสั้น", "บทสอง", "จบ"])
    starts = [0, 33_000, 36_000, 90_000, 150_000]
    chapters = build_chapters(s, starts)
    assert chapters[0].start_ms == 0
    assert [c.title for c in chapters] == ["เปิด", "บทหนึ่ง", "บทสอง", "จบ"]


def test_too_few_chapters_returns_empty():
    s = _script(["เปิด", "เปิด", "เปิด", "จบ", "จบ"])
    assert build_chapters(s, [0, 20_000, 40_000, 60_000, 80_000]) == []


def test_description_has_credits_facts_and_disclaimer():
    s = _script(["เปิด", "หนึ่ง", "สอง", "สาม", "จบ"])
    d = build_description(s, get_format("long"), [0, 20_000, 40_000, 60_000, 80_000],
                          credits=["เสียงพากย์: Gemini TTS"])
    assert d.splitlines()[0] == "คืนหนึ่งในตึกเก่า"
    assert "0:00 เปิด" in d and "ข้อมูลจริงในเรื่อง:" in d
    assert "เรื่องแต่ง" in d and "สร้างด้วย AI" in d and "Gemini TTS" in d


def test_short_has_no_chapters_and_has_hashtags():
    s = _script(["a", "b", "c", "d", "e"])
    d = build_description(s, get_format("short"), [0, 10_000, 20_000, 30_000, 40_000])
    assert "0:00" not in d and "#Shorts" in d


def test_thumbnail_spec_and_title():
    s = _script(["a", "b", "c", "d", "e"])
    spec = get_format("long")
    t = build_thumbnail_spec(s, spec, 20 * 60_000)
    assert t["size"] == [1920, 1080] and t["context_tag"] == "23:47"
    assert t["headline_line1"] == "ชั้นห้า" and "20 นาที" in t["pill"]
    assert t["character"]["outfit"] == "เสื้อกันฝนสีเหลือง"
    assert "ตอนเดียวจบ" in build_title(s, spec)
    assert build_thumbnail_spec(s, get_format("short"), 40_000)["size"] == [1080, 1920]


def test_review_checklist_warns_on_low_confidence_and_outfit_mismatch():
    s = _script(["a", "b", "c", "d", "e"])
    s.script_blocks[1].visual_cue = "นิ่ม ยืนที่ประตู"
    text = build_review_checklist(s, get_format("long"))
    assert "ความมั่นใจต่ำ" in text and "ไม่ระบุชุด" in text


def test_bundle_written(tmp_path):
    s = _script(["a", "b", "c", "d", "e"])
    paths = write_publish_bundle(tmp_path / "ep", s, get_format("long"),
                                 [0, 20_000, 40_000, 60_000, 80_000], 100_000)
    assert all(p.exists() for p in paths.values())
    assert json.loads(paths["thumbnail"].read_text(encoding="utf-8"))["format"] == "long"
