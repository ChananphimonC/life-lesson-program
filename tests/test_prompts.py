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


def test_prompt_demands_mood_per_block_and_tension_curve():
    p = build_script_prompt("t", "x", episode_format="long")
    assert "ATMOSPHERE" in p and "TENSION CURVE" in p
    for value in ("storm", "hushed", "heartbeat", "flicker"):
        assert value in p
    assert '"mood"' in p and '"want"' in p


def test_example_json_in_prompt_is_not_broken_by_formatting():
    # .format() with unescaped braces would raise; every format must build
    for fmt in ("short", "standard", "long"):
        build_script_prompt("t", "x", episode_format=fmt)


def test_series_prompts_differ_where_they_must():
    refl = build_script_prompt("t", "x", series="reflection")
    know = build_script_prompt("t", "x", series="knowledge")
    story = build_script_prompt("t", "x", series="story")
    assert "LIFE REFLECTION" in refl and "comfort" in refl and "SUSPENSE ENGINE" in refl
    for p in (know, story):
        assert "comfort" not in p and "earn its place" in p and "SUSPENSE ENGINE" in p
        assert "LIFE REFLECTION" not in p and "NOT life advice" not in p
    assert "source" in know and "belief" in know.lower() and "FICTION" in story


def test_brief_is_included_and_unknown_series_rejected():
    import pytest

    p = build_script_prompt("t", "x", series="story", brief="premise: นักศึกษาติดเกาะ")
    assert "AUTHOR BRIEF" in p and "นักศึกษาติดเกาะ" in p
    assert "AUTHOR BRIEF" not in build_script_prompt("t", "x")
    with pytest.raises(ValueError):
        build_script_prompt("t", "x", series="poetry")


def test_suspense_rules_cover_the_core_techniques():
    p = build_script_prompt("t", "x")
    for phrase in ("HOOK", "CLOCK", "OPEN LOOPS", "CHAPTER-END HOOK", "PLANT AND PAY OFF", "REVERSAL", "NEVER narrate what the picture"):
        assert phrase in p
