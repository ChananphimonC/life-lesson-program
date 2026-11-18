import json

import pytest

from life_lesson.errors import ScriptValidationError, SensitiveTopicError
from life_lesson.generation.critic import (
    CATEGORIES, build_critic_prompt, parse_critic_result, run_critic_loop,
)
from life_lesson.generation.formats import get_format
from life_lesson.generation.safety import lexical_flags, screen_topic

from .test_publish_metadata import _script


def _result(failed=()):
    return json.dumps({"results": [
        {"category": c, "passed": c not in failed, "evidence": "x" if c in failed else "",
         "block_sequences": [2] if c in failed else []}
        for c in CATEGORIES]})


def _script_json(script):
    return script.model_dump_json()


def test_sensitive_topics_rejected():
    for bad in ("คนที่อยากตาย", "self-harm story", "ถูกล่วงละเมิด"):
        with pytest.raises(SensitiveTopicError):
            screen_topic(bad)
    screen_topic("เพื่อนซื้อบ้านแล้วเราเช่าอยู่")


def test_lexical_flags_find_prescriptive_and_cliche():
    s = _script(list("abcde"))
    s.script_blocks[1].text = "คุณควรลองใหม่ อย่ายอมแพ้"
    cats = {f.category for f in lexical_flags(s)}
    assert {"prescriptive_advice", "generic_cliche"} <= cats


def test_parse_requires_all_seven_categories():
    parse_critic_result(_result())
    broken = json.loads(_result()); broken["results"].pop()
    with pytest.raises(ScriptValidationError):
        parse_critic_result(json.dumps(broken))
    with pytest.raises(ScriptValidationError):
        parse_critic_result("nope")


def test_prompt_lists_every_category_and_hints():
    s = _script(list("abcde"))
    s.script_blocks[0].text = "คุณต้องไป"
    p = build_critic_prompt(s, lexical_flags(s))
    assert all(c in p for c in CATEGORIES) and "block 1" in p


def test_loop_passes_first_time():
    s = _script(list("abcde"))
    out = run_critic_loop(s, get_format("standard"), call_llm=lambda p: _result())
    assert out.passed and out.rewrites_used == 0


def test_loop_rewrites_then_passes():
    s = _script(list("abcde"))
    calls = []

    def llm(prompt):
        calls.append(prompt)
        if prompt.startswith("You are the Critic"):
            return _result(failed=("prescriptive_advice",)) if len(calls) == 1 else _result()
        return _script_json(s)

    out = run_critic_loop(s, get_format("standard"), call_llm=llm)
    assert out.passed and out.rewrites_used == 1 and len(out.attempts) == 2


def test_loop_gives_up_after_three_rewrites():
    s = _script(list("abcde"))

    def llm(prompt):
        return _result(failed=("generic_cliche",)) if prompt.startswith("You are the Critic") else _script_json(s)

    out = run_critic_loop(s, get_format("standard"), call_llm=llm)
    assert not out.passed and out.rewrites_used == 3 and len(out.attempts) == 4


def test_each_series_has_its_own_categories_and_strict_parse():
    from life_lesson.generation.critic import CATEGORIES_BY_SERIES, build_critic_prompt, parse_critic_result

    for series, cats in CATEGORIES_BY_SERIES.items():
        raw = json.dumps({"results": [{"category": c, "passed": True} for c in cats]})
        assert parse_critic_result(raw, series).passed
        p = build_critic_prompt(_script(list("abcde")), [], series)
        assert p.startswith("You are the Critic") and all(c in p for c in cats)
    # a reflection verdict is not valid for the knowledge series
    with pytest.raises(ScriptValidationError):
        parse_critic_result(_result(), "knowledge")
    with pytest.raises(ScriptValidationError):
        parse_critic_result(_result(), "bogus")


def test_knowledge_series_does_not_flag_advice_or_belief_words():
    from life_lesson.generation.safety import lexical_flags

    s = _script(list("abcde"))
    s.script_blocks[1].text = "คุณควรกินผักให้มากขึ้น ตามความเชื่อโบราณเรื่องกรรม"
    assert lexical_flags(s, "reflection")
    assert lexical_flags(s, "knowledge") == []
