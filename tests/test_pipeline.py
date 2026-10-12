import json
from pathlib import Path

import pytest

from life_lesson.config import Settings
from life_lesson.db import repository as repo
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
    def synthesize(self, text: str) -> bytes:
        return make_silence_wav(duration_ms=50)


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

    def fake_assemble_video(*, ffmpeg_binary, background_video, audio_path, output_path):
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
