import json

import pytest

from life_lesson.errors import ScriptValidationError
from life_lesson.generation.schema import validate_script_json

VALID_SCRIPT = {
    "topic_id": "req-123",
    "title": "ความเร็วที่แตกต่างกัน",
    "metadata": {"mood": "calm, reflective", "estimated_duration_seconds": 240},
    "script_blocks": [
        {"sequence": 1, "phase": "hook", "text": "hook text", "pause_after_ms": 1500},
        {"sequence": 2, "phase": "exploration", "text": "exploration text", "pause_after_ms": 2000},
        {"sequence": 3, "phase": "shift", "text": "shift text", "pause_after_ms": 1500},
        {"sequence": 4, "phase": "outro", "text": "outro text", "pause_after_ms": 2500},
    ],
}


def test_valid_script_parses():
    script = validate_script_json(json.dumps(VALID_SCRIPT))
    assert script.title == VALID_SCRIPT["title"]
    assert len(script.script_blocks) == 4
    assert script.script_blocks[0].phase == "hook"


def test_strips_markdown_fence():
    fenced = "```json\n" + json.dumps(VALID_SCRIPT) + "\n```"
    script = validate_script_json(fenced)
    assert script.title == VALID_SCRIPT["title"]


def test_rejects_invalid_json():
    with pytest.raises(ScriptValidationError):
        validate_script_json("not json at all {")


def test_rejects_missing_required_field():
    broken = dict(VALID_SCRIPT)
    del broken["title"]
    with pytest.raises(ScriptValidationError):
        validate_script_json(json.dumps(broken))


def test_rejects_missing_phase():
    broken = json.loads(json.dumps(VALID_SCRIPT))
    broken["script_blocks"] = [b for b in broken["script_blocks"] if b["phase"] != "shift"]
    with pytest.raises(ScriptValidationError):
        validate_script_json(json.dumps(broken))


def test_rejects_duplicate_sequence():
    broken = json.loads(json.dumps(VALID_SCRIPT))
    broken["script_blocks"][1]["sequence"] = broken["script_blocks"][0]["sequence"]
    with pytest.raises(ScriptValidationError):
        validate_script_json(json.dumps(broken))


def test_rejects_out_of_order_sequence():
    broken = json.loads(json.dumps(VALID_SCRIPT))
    broken["script_blocks"][0]["sequence"], broken["script_blocks"][1]["sequence"] = (
        broken["script_blocks"][1]["sequence"],
        broken["script_blocks"][0]["sequence"],
    )
    with pytest.raises(ScriptValidationError):
        validate_script_json(json.dumps(broken))


def test_rejects_empty_script_blocks():
    broken = dict(VALID_SCRIPT)
    broken["script_blocks"] = []
    with pytest.raises(ScriptValidationError):
        validate_script_json(json.dumps(broken))


def test_rejects_negative_pause():
    broken = json.loads(json.dumps(VALID_SCRIPT))
    broken["script_blocks"][0]["pause_after_ms"] = -1
    with pytest.raises(ScriptValidationError):
        validate_script_json(json.dumps(broken))


def _blocks(n, title=None, text="a"):
    phases = ["hook", "exploration", "shift", "outro"]
    return [
        {"sequence": i + 1, "phase": phases[min(i * 4 // n, 3)], "text": text,
         "pause_after_ms": 100, "chapter_title": title}
        for i in range(n)
    ]


def _script(blocks):
    from life_lesson.generation.schema import ScriptOutput

    return ScriptOutput.model_validate(
        {"topic_id": "t", "title": "t",
         "metadata": {"mood": "calm", "estimated_duration_seconds": 40},
         "script_blocks": blocks}
    )


def test_short_rejects_over_long_text():
    import pytest
    from life_lesson.errors import ScriptValidationError
    from life_lesson.generation.formats import get_format
    from life_lesson.generation.schema import check_format

    with pytest.raises(ScriptValidationError):
        check_format(_script(_blocks(4, text="ก" * 300)), get_format("short"))
    check_format(_script(_blocks(4, text="ก" * 50)), get_format("short"))


def test_long_requires_chapter_titles():
    import pytest
    from life_lesson.errors import ScriptValidationError
    from life_lesson.generation.formats import get_format
    from life_lesson.generation.schema import check_format

    with pytest.raises(ScriptValidationError):
        check_format(_script(_blocks(12)), get_format("long"))
    check_format(_script(_blocks(12, title="บท")), get_format("long"))
