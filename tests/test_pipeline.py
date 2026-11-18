import json
from pathlib import Path

import pytest

from life_lesson.config import Settings
from life_lesson.db import repository as repo
from life_lesson.generation.critic import CATEGORIES
from life_lesson import pipeline as pipeline_module

from .conftest import make_silence_wav

VALID_SCRIPT_JSON = json.dumps(
    {
        "topic_id": "any",
        "title": "title",
        "metadata": {"mood": "calm", "estimated_duration_seconds": 200},
        "script_blocks": [
            {"sequence": 1, "phase": "hook", "text": "a", "pause_after_ms": 100},
            {"sequence": 2, "phase": "exploration", "text": "b", "pause_after_ms": 100},
            {"sequence": 3, "phase": "shift", "text": "c", "pause_after_ms": 100},
            {"sequence": 4, "phase": "outro", "text": "d", "pause_after_ms": 100},
        ],
    }
)


class FakeTTSProvider:
    def __init__(self):
        self.texts = []

    def synthesize(self, text: str) -> bytes:
        self.texts.append(text)
        return make_silence_wav(duration_ms=50)


PASS_CRITIC_JSON = json.dumps(
    {"results": [{"category": c, "passed": True} for c in CATEGORIES]}
)


@pytest.fixture(autouse=True)
def _hermetic_llm_and_audio(monkeypatch):
    """No network and no ffmpeg for audio mastering in pipeline tests; those
    pieces have their own tests (test_critic, test_mastering, test_ambient)."""
    monkeypatch.setattr(pipeline_module, "generate_critic_text", lambda s, p: PASS_CRITIC_JSON)

    def fake_master(ffmpeg, narration, output, music=None, bed_gain_db=0.0):
        output.write_bytes(narration.read_bytes())
        return output

    monkeypatch.setattr(pipeline_module, "master_audio", fake_master)


def _settings(tmp_path: Path) -> Settings:
    return Settings(
        gemini_api_key="fake-key",
        gemini_script_model="fake-model",
        gemini_tts_model="fake-tts-model",
        gemini_tts_voice="Kore",
        db_path=tmp_path / "test.db",
        background_video_dir=tmp_path / "backgrounds",
        output_dir=tmp_path / "output",
        ffmpeg_binary="ffmpeg",
        log_level="INFO",
    )


def test_pipeline_success_path(tmp_path, monkeypatch):
    settings = _settings(tmp_path)

    monkeypatch.setattr(
        pipeline_module, "generate_script_text", lambda settings, prompt: VALID_SCRIPT_JSON
    )
    monkeypatch.setattr(
        pipeline_module,
        "pick_random_background",
        lambda background_dir: tmp_path / "backgrounds" / "fake.mp4",
    )

    def fake_assemble_video(*, ffmpeg_binary, background_video, audio_path, output_path, **_):
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(b"fake mp4 bytes")
        return output_path

    monkeypatch.setattr(pipeline_module, "assemble_video", fake_assemble_video)

    result = pipeline_module.run_pipeline(
        "some situation",
        theme="some theme",
        settings=settings,
        tts_provider=FakeTTSProvider(),
    )

    assert result.state == "DONE"
    assert result.audio_path is not None and result.audio_path.exists()
    assert result.video_path is not None and result.video_path.exists()

    with repo.open_db(settings.db_path) as conn:
        episode = repo.get_episode(conn, result.episode_id)
        assert episode["state"] == "DONE"
        assert episode["audio_path"] == str(result.audio_path)
        assert episode["video_path"] == str(result.video_path)

        attempts = conn.execute(
            "SELECT stage, status FROM generation_attempts WHERE episode_id = ? ORDER BY id",
            (result.episode_id,),
        ).fetchall()
        stages = [(row["stage"], row["status"]) for row in attempts]
        assert ("script", "success") in stages
        assert ("tts", "success") in stages
        assert ("video", "success") in stages


def test_pipeline_records_failure_on_invalid_script_json(tmp_path, monkeypatch):
    settings = _settings(tmp_path)

    monkeypatch.setattr(
        pipeline_module, "generate_script_text", lambda settings, prompt: "not valid json {"
    )

    result = pipeline_module.run_pipeline(
        "some situation", settings=settings, tts_provider=FakeTTSProvider()
    )

    assert result.state == "FAILED"
    assert result.error_message is not None

    with repo.open_db(settings.db_path) as conn:
        episode = repo.get_episode(conn, result.episode_id)
        assert episode["state"] == "FAILED"
        assert episode["error_message"]


def test_pipeline_records_failure_when_no_background_video(tmp_path, monkeypatch):
    settings = _settings(tmp_path)
    settings.background_video_dir.mkdir(parents=True, exist_ok=True)  # empty dir

    monkeypatch.setattr(
        pipeline_module, "generate_script_text", lambda settings, prompt: VALID_SCRIPT_JSON
    )

    result = pipeline_module.run_pipeline(
        "some situation", settings=settings, tts_provider=FakeTTSProvider()
    )

    assert result.state == "FAILED"
    assert "background" in result.error_message.lower()


def _script_json(n_blocks, chapter=True):
    phases = ["hook", "exploration", "shift", "outro"]
    return json.dumps(
        {
            "topic_id": "any",
            "title": "ชั้นห้า เสียงเคาะ",
            "summary": "คืนหนึ่งในตึกเก่า",
            "metadata": {"mood": "calm", "estimated_duration_seconds": 40},
            "script_blocks": [
                {
                    "sequence": i + 1,
                    "phase": phases[min(i * 4 // n_blocks, 3)],
                    "text": "ข้อความ",
                    "pause_after_ms": 100,
                    "chapter_title": f"บท {i // 3 + 1}" if chapter else None,
                    "visual_cue": "ภาพ",
                }
                for i in range(n_blocks)
            ],
        }
    )


def _run(tmp_path, monkeypatch, script_json, fmt):
    settings = _settings(tmp_path)
    calls = {}
    monkeypatch.setattr(
        pipeline_module, "generate_script_text", lambda s, p: (calls.setdefault("prompt", p), script_json)[1]
    )
    monkeypatch.setattr(
        pipeline_module, "pick_random_background", lambda d: tmp_path / "fake.mp4"
    )

    def fake_assemble(*, output_path, width=0, height=0, **_):
        calls["size"] = (width, height)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(b"x")
        return output_path

    monkeypatch.setattr(pipeline_module, "assemble_video", fake_assemble)
    monkeypatch.setattr(pipeline_module, "assemble_scene_video", fake_assemble)
    result = pipeline_module.run_pipeline(
        "situation", settings=settings, tts_provider=FakeTTSProvider(), episode_format=fmt
    )
    return result, calls


def test_short_format_renders_vertical_and_writes_publish_bundle(tmp_path, monkeypatch):
    result, calls = _run(tmp_path, monkeypatch, _script_json(4, chapter=False), "short")
    assert result.state == "DONE", result.error_message
    assert calls["size"] == (1080, 1920)
    assert "YouTube Short" in calls["prompt"]
    assert (result.publish_dir / "description.txt").exists()
    assert (result.publish_dir / "thumbnail.json").exists()
    assert "#Shorts" in (result.publish_dir / "description.txt").read_text(encoding="utf-8")


def test_long_format_has_chapters_in_description(tmp_path, monkeypatch):
    # FakeTTS clips are 50ms, so make chapters long enough via pauses.
    raw = json.loads(_script_json(12))
    for b in raw["script_blocks"]:
        b["pause_after_ms"] = 6000
    result, calls = _run(tmp_path, monkeypatch, json.dumps(raw), "long")
    assert result.state == "DONE", result.error_message
    assert calls["size"] == (1920, 1080)
    desc = (result.publish_dir / "description.txt").read_text(encoding="utf-8")
    assert "0:00 บท 1" in desc and "สร้างด้วย AI" in desc


def test_format_violation_fails_episode(tmp_path, monkeypatch):
    result, _ = _run(tmp_path, monkeypatch, _script_json(4, chapter=False), "long")
    assert result.state == "FAILED"


def test_sensitive_topic_is_rejected_before_any_generation(tmp_path, monkeypatch):
    settings = _settings(tmp_path)

    def boom(*a, **k):
        raise AssertionError("must not call the LLM for a rejected topic")

    monkeypatch.setattr(pipeline_module, "generate_script_text", boom)
    result = pipeline_module.run_pipeline("เรื่องของคนที่อยากตาย", settings=settings,
                                          tts_provider=FakeTTSProvider())
    assert result.state == "REJECTED"
    with repo.open_db(settings.db_path) as conn:
        assert repo.get_episode(conn, result.episode_id)["state"] == "REJECTED"
        row = conn.execute("SELECT status FROM topics WHERE id = ?", (result.topic_id,)).fetchone()
        assert row["status"] == "rejected"


def test_critic_failure_after_three_rewrites_ends_in_failed_review(tmp_path, monkeypatch):
    settings = _settings(tmp_path)
    monkeypatch.setattr(pipeline_module, "generate_script_text", lambda s, p: VALID_SCRIPT_JSON)
    bad = json.dumps({"results": [
        {"category": c, "passed": c != "generic_cliche", "evidence": "x"} for c in CATEGORIES]})

    def critic_llm(s, prompt):
        return bad if prompt.startswith("You are the Critic") else VALID_SCRIPT_JSON

    monkeypatch.setattr(pipeline_module, "generate_critic_text", critic_llm)
    tts = FakeTTSProvider()
    result = pipeline_module.run_pipeline("situation", settings=settings, tts_provider=tts)

    assert result.state == "FAILED_REVIEW"
    assert tts.texts == []  # nothing is voiced when the script did not pass review
    with repo.open_db(settings.db_path) as conn:
        stages = [r["stage"] for r in conn.execute(
            "SELECT stage FROM generation_attempts WHERE episode_id = ? ORDER BY id",
            (result.episode_id,))]
    assert stages.count("critic") == 4 and stages.count("rewrite") == 3


def test_moods_drive_voice_directive_pause_and_scene_video(tmp_path, monkeypatch):
    raw = json.loads(_script_json(4, chapter=False))
    for b in raw["script_blocks"]:
        b["pause_after_ms"] = 2000
        b["mood"] = {"light": "dark", "weather": "storm", "color": "teal",
                     "tension": 5, "voice": "urgent", "sounds": ["rain", "thunder"]}
    seen = {}
    monkeypatch.setattr(pipeline_module, "build_ambient_bed",
                        lambda ff, scenes, total, out, music=None: seen.setdefault("scenes", scenes) and None)
    result, calls = _run(tmp_path, monkeypatch, json.dumps(raw), "standard")
    assert result.state == "DONE", result.error_message
    # scene path used (moods present) with the scene carrying the storm mood
    assert calls["size"] == (1920, 1080)
    assert seen["scenes"][0].mood.weather == "storm"
    # tension 5 tightens 2000ms pauses to 55% (1100ms): 4 blocks x (50ms clip + 1100ms)
    assert seen["scenes"][-1].end_ms == 4 * (50 + 1100)
    shots = json.loads((result.publish_dir / "shot_list.json").read_text(encoding="utf-8"))
    assert shots[0]["mood"]["weather"] == "storm"


def _touch_video(**k):
    k["output_path"].parent.mkdir(parents=True, exist_ok=True)
    k["output_path"].write_bytes(b"x")
    return k["output_path"]


def test_tts_receives_voice_directive(tmp_path, monkeypatch):
    raw = json.loads(_script_json(4, chapter=False))
    raw["script_blocks"][0]["mood"] = {"voice": "hushed", "tension": 3}
    settings = _settings(tmp_path)
    monkeypatch.setattr(pipeline_module, "generate_script_text", lambda s, p: json.dumps(raw))
    monkeypatch.setattr(pipeline_module, "pick_random_background", lambda d: tmp_path / "f.mp4")
    monkeypatch.setattr(pipeline_module, "assemble_video", _touch_video)
    monkeypatch.setattr(pipeline_module, "assemble_scene_video", _touch_video)
    monkeypatch.setattr(pipeline_module, "build_ambient_bed", lambda *a, **k: None)
    tts = FakeTTSProvider()
    pipeline_module.run_pipeline("situation", settings=settings, tts_provider=tts)
    assert tts.texts[0].startswith("Say in a close, hushed") and tts.texts[1] == "ข้อความ"
