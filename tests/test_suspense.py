from life_lesson.generation.schema import ScriptOutput
from life_lesson.generation.suspense import lint_script


def _script(texts, tensions=None, phases=None, titles=None, facts=None, motif=None):
    n = len(texts)
    phases = phases or (["hook"] + ["exploration"] * (n - 3) + ["shift", "outro"])
    blocks = []
    for i, t in enumerate(texts):
        b = {"sequence": i + 1, "phase": phases[i], "text": t, "pause_after_ms": 500}
        if titles:
            b["chapter_title"] = titles[i]
        if tensions:
            b["mood"] = {"tension": tensions[i]}
        blocks.append(b)
    return ScriptOutput.model_validate({
        "topic_id": "t", "title": "t",
        "metadata": {"mood": "m", "estimated_duration_seconds": 60, "motif": motif},
        "script_blocks": blocks, "facts": facts or []})


GOOD = [
    "เที่ยงคืนสิบสองนาที เจ๊ยังไม่ปิดร้าน แต่ไม่มีใครรู้ว่าเธอรออะไรอยู่",
    "เด็กคนนั้นยืนหน้าร้านมาสามคืนแล้ว ทำไมเขาไม่เคยสั่งอะไรเลย",
    "กระทะร้อนจนควันขึ้น เจ๊รู้ว่าถ้าเขาไม่สั่งคืนนี้ ก็คงไม่มีโอกาสอีก",
    "ในกล่องใต้เคาน์เตอร์ มีบิลค่าเช่าที่เจ๊ซ่อนไว้ แต่ใบที่สามไม่ใช่ของเจ๊",
    "ใครกันที่เขียนชื่อเด็กไว้บนบิลนั้น",
    "เจ๊ตักข้าวใส่จาน แล้วเงียบ",
    "ไข่ดาวไหม้ไปครึ่งฟอง และเด็กคนนั้นก็ยังไม่ขยับ",
    "บางที จานสุดท้ายอาจไม่ใช่ของเขา",
]


def test_gripping_script_scores_high():
    s = _script(GOOD, tensions=[3, 3, 4, 4, 5, 5, 4, 3])
    r = lint_script(s)
    assert r.score >= 80, r.summary()
    assert not r.high


def test_greeting_opening_is_a_high_finding():
    texts = ["สวัสดีค่ะ วันนี้เราจะมาพูดถึงร้านตามสั่ง"] + GOOD[1:]
    r = lint_script(_script(texts))
    assert any(f.code == "greeting_opening" for f in r.high)
    assert lint_script(_script(GOOD)).score > r.score


def test_flat_hook_flagged():
    texts = ["ร้านตามสั่งร้านหนึ่งอยู่ปากซอย ขายข้าวผัดกะเพราราคาห้าสิบบาท"] + ["เจ๊ขายของทุกวัน เจ๊ตื่นเช้า เจ๊ปิดดึก"] * 7
    assert any(f.code == "weak_hook" for f in lint_script(_script(texts)).findings)


def test_flat_tension_and_falling_tension():
    flat = lint_script(_script(GOOD, tensions=[3] * 8))
    assert any(f.code == "flat_tension" for f in flat.high)
    falling = lint_script(_script(GOOD, tensions=[5, 5, 4, 4, 3, 3, 2, 2]))
    assert any(f.code in ("tension_falls", "early_peak") for f in falling.findings)


def test_report_style_visual_narration_and_digits_are_found():
    texts = GOOD[:]
    texts[2] = "ข้อแรก เจ๊ยิ้ม แล้วใส่เสื้อสีชมพู ทั้งนี้ราคา 50 บาท"
    codes = {f.code for f in lint_script(_script(texts)).findings}
    assert {"report_style", "narrating_the_picture", "digits_in_narration"} <= codes


def test_chapter_end_hooks():
    titles = ["ก", "ก", "ข", "ข", "ค", "ค", "ง", "ง"]
    flat_ends = ["เล่าเรื่องหนึ่ง", "จบบทแรกอย่างเรียบ", "เล่าเรื่องสอง", "จบบทสองอย่างเรียบ", "เล่าเรื่องสาม", "จบบทสามอย่างเรียบ", "เล่าเรื่องสี่", "จบเรื่อง"]
    r = lint_script(_script(["เที่ยงคืน แต่ใครรออะไร"] + flat_ends[1:], titles=titles))
    assert any(f.code == "flat_chapter_ends" for f in r.findings)


def test_repetition_but_motif_is_allowed():
    rep = ["เจ๊ถือตะหลิวอยู่ตรงนั้นเสมอ"] * 7 + ["จบ"]
    assert any(f.code == "repetition" for f in lint_script(_script(rep)).findings)
    assert not any(f.code == "repetition" for f in lint_script(_script(rep, motif="เจ๊ถือตะหลิวอยู่ตรงนั้นเสมอ")).findings)


def test_series_specific_rules():
    assert any(f.code == "no_sources" for f in lint_script(_script(GOOD), "knowledge").high)
    summary = GOOD[:-1] + ["สรุปแล้วบทเรียนของเรื่องนี้คืออย่าทิ้งใคร"]
    assert any(f.code == "summarising_ending" for f in lint_script(_script(summary), "reflection").findings)
    assert not any(f.code == "summarising_ending" for f in lint_script(_script(summary), "story").findings)


def test_risky_tts_words_match_whole_words_only():
    clean = _script(GOOD[:-1] + ["คราวนี้เสียงลากมาจากหลังร้าน"])
    assert not any(f.code == "tts_risky_words" for f in lint_script(clean).findings)
    risky = _script(GOOD[:-1] + ["ราวห้าโมงเย็นเขาก็มา"])
    assert any(f.code == "tts_risky_words" for f in lint_script(risky).findings)
