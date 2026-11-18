from life_lesson.generation.prompts import build_script_prompt

REQUIRED_PHRASES = [
    "LIFE REFLECTION",
    "religious",
    "Quote or attribute",
    "motivational content",
    "therapy",
    "clinical",
    "prescriptive advice",
    "clich",
    "manipulative",
    "hook",
    "exploration",
    "shift",
    "outro",
]


def test_prompt_contains_all_core_content_constraints():
    prompt = build_script_prompt("req-1", "some specific situation", theme="a theme")
    for phrase in REQUIRED_PHRASES:
        assert phrase.lower() in prompt.lower(), f"missing constraint phrase: {phrase!r}"


def test_prompt_includes_topic_text_and_theme():
    prompt = build_script_prompt("req-1", "renting while friends buy houses", theme="falling behind")
    assert "renting while friends buy houses" in prompt
    assert "falling behind" in prompt


def test_prompt_omits_theme_line_when_not_given():
    prompt = build_script_prompt("req-1", "some situation", theme=None)
    assert "Broad theme:" not in prompt


def test_prompt_is_format_aware():
    short = build_script_prompt("t", "x", episode_format="short")
    long_ = build_script_prompt("t", "x", episode_format="long")
    assert "YouTube Short" in short and "chapter_title" in long_
    assert "cold open" in long_.lower()
    assert '"format": "short"' in short


def test_prompt_keeps_constraints_in_every_format():
    for fmt in ("short", "standard", "long"):
        prompt = build_script_prompt("t", "x", episode_format=fmt)
        for phrase in REQUIRED_PHRASES:
            assert phrase.lower() in prompt.lower()


def test_unknown_format_rejected():
    import pytest
    from life_lesson.errors import ScriptValidationError

    with pytest.raises(ScriptValidationError):
        build_script_prompt("t", "x", episode_format="movie")


def test_prompt_asks_for_character_sheet_and_story_craft():
    prompt = build_script_prompt("t", "x")
    assert '"characters"' in prompt and "outfit" in prompt
    assert "STORY CRAFT" in prompt
