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
