import json

from life_lesson.generation.formats import get_format
from life_lesson.generation.punchup import build_punchup_prompt, run_punchup
from life_lesson.generation.suspense import lint_script

from .test_suspense import GOOD, _script

FLAT = ["สวัสดีค่ะ วันนี้เราจะมาพูดถึงร้านตามสั่ง"] + ["เจ๊ขายของทุกวัน"] * 3 + ["ข้อแรก เจ๊ยิ้ม"] + ["เจ๊ปิดร้าน"] * 3
SPEC = get_format("standard")


def _llm_returning(script):
    calls = []

    def call(prompt):
        calls.append(prompt)
        return script.model_dump_json()

    call.calls = calls
    return call


def test_already_good_script_is_left_alone():
    s = _script(GOOD, tensions=[3, 3, 4, 4, 5, 5, 4, 3])
    llm = _llm_returning(s)
    out = run_punchup(s, SPEC, call_llm=llm)
    assert out.rounds == [] and out.script is s and not out.improved and llm.calls == []


def test_flat_script_is_rewritten_and_the_better_version_kept():
    flat = _script(FLAT, tensions=[3] * 8)
    better = _script(GOOD, tensions=[3, 3, 4, 4, 5, 5, 4, 3])
    llm = _llm_returning(better)
    out = run_punchup(flat, SPEC, call_llm=llm)
    assert out.improved and out.after.score > out.before.score
    assert out.script.script_blocks[0].text == GOOD[0]
    assert out.rounds[0].accepted
    # the prompt carries the concrete findings and the suspense rules
    p = llm.calls[0]
    assert "greeting_opening" in p and "SUSPENSE ENGINE" in p and "never add a fact without a source" in p


def test_a_rewrite_that_scores_worse_is_never_accepted():
    flat = _script(FLAT, tensions=[3] * 8)
    worse = _script(["สวัสดีค่ะ ทั้งนี้ ข้อแรก เจ๊ยิ้ม ราคา 50 บาท"] * 8, tensions=[3] * 8)
    assert lint_script(worse).score < lint_script(flat).score
    out = run_punchup(flat, SPEC, call_llm=_llm_returning(worse), threshold=101)
    assert out.script is flat and not out.improved and out.rounds[0].accepted is False


def test_invalid_model_output_stops_cleanly():
    flat = _script(FLAT)
    out = run_punchup(flat, SPEC, call_llm=lambda p: "not json {")
    assert out.script is flat and out.rounds[0].accepted is False and "rejected" in out.rounds[0].note


def test_rounds_are_bounded():
    flat = _script(FLAT, tensions=[3] * 8)
    steps = iter([_script(FLAT[:1] + GOOD[1:4] + FLAT[4:], tensions=[3] * 8), _script(GOOD[:7] + FLAT[-1:], tensions=[3, 3, 4, 4, 5, 5, 4, 3])])
    calls = []

    def llm(prompt):
        calls.append(1)
        return next(steps).model_dump_json()

    run_punchup(flat, SPEC, call_llm=llm, max_rounds=2, threshold=101)
    assert len(calls) <= 2


def test_reflection_prompt_keeps_the_no_advice_rule_other_series_do_not():
    flat = _script(FLAT)
    r = build_punchup_prompt(flat, lint_script(flat), SPEC, "reflection")
    k = build_punchup_prompt(flat, lint_script(flat, "knowledge"), SPEC, "knowledge")
    assert "no advice" in r and "no advice" not in k


# ---- the reader-judge (pairwise, order-swapped) -------------------------------

def _judge_always(winner_when_new_is_b, winner_when_new_is_a):
    """Fake judge: answers by which position the NEW script occupies."""
    def judge(prompt):
        new_is_b = prompt.index("[1] " + GOOD[0]) > prompt.index("VERSION B:")  # GOOD[0] opens the new script
        return json.dumps({"winner": winner_when_new_is_b if new_is_b else winner_when_new_is_a})
    return judge


def test_judge_must_prefer_the_rewrite_in_both_orders():
    flat = _script(FLAT, tensions=[3] * 8)
    better = _script(GOOD, tensions=[3, 3, 4, 4, 5, 5, 4, 3])
    out = run_punchup(flat, SPEC, call_llm=_llm_returning(better), judge=_judge_always("B", "A"), threshold=101, max_rounds=1)
    assert out.improved and out.script is not flat and "old-first=B" in out.rounds[0].note

    # position bias: judge always says "A" -> rewrite rejected even though mechanics improved
    biased = run_punchup(flat, SPEC, call_llm=_llm_returning(better), judge=lambda p: '{"winner": "A"}', threshold=101, max_rounds=1)
    assert biased.script is flat and not biased.rounds[0].accepted

    # the judge says the old one is better
    reject = run_punchup(flat, SPEC, call_llm=_llm_returning(better), judge=_judge_always("A", "B"), threshold=101, max_rounds=1)
    assert reject.script is flat


def test_garbage_judge_output_counts_as_tie_and_rejects():
    flat = _script(FLAT, tensions=[3] * 8)
    better = _script(GOOD, tensions=[3, 3, 4, 4, 5, 5, 4, 3])
    out = run_punchup(flat, SPEC, call_llm=_llm_returning(better), judge=lambda p: "I think B", threshold=101, max_rounds=1)
    assert out.script is flat


def test_a_mechanically_worse_rewrite_is_rejected_even_if_the_judge_likes_it():
    flat = _script(GOOD, tensions=[3, 3, 4, 4, 5, 5, 4, 3])
    worse = _script(["สวัสดีค่ะ ทั้งนี้ ข้อแรก เจ๊ยิ้ม ราคา 50 บาท"] * 8, tensions=[3] * 8)
    out = run_punchup(flat, SPEC, call_llm=_llm_returning(worse), judge=lambda p: '{"winner": "B"}', threshold=101, max_rounds=1)
    assert out.script is flat


def test_soft_signals_do_not_block_a_better_rewrite_without_a_judge_score_can_still_win():
    # objective hygiene equal, total score decides when no judge exists
    flat = _script(FLAT, tensions=[3] * 8)
    better = _script(GOOD, tensions=[3, 3, 4, 4, 5, 5, 4, 3])
    assert run_punchup(flat, SPEC, call_llm=_llm_returning(better), threshold=101, max_rounds=1).improved


def test_soft_findings_are_marked_and_halved():
    r = lint_script(_script(["ร้านตามสั่งอยู่ปากซอยขายกะเพรา"] * 8))
    soft = [f for f in r.findings if f.soft]
    assert soft and all(f.code in {"weak_hook", "flat_chapter_ends", "few_open_loops", "monotone_rhythm"} for f in soft)
    assert r.objective_penalty <= 100 - r.score
