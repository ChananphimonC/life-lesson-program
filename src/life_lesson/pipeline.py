"""v0.1 pipeline orchestrator:

Topic Input -> SQLite -> Gemini Script Generation -> JSON Validation ->
SQLite persistence -> TTS -> FFmpeg -> Raw 16:9 MP4

Episode states used in v0.1: DRAFT -> TOPIC -> SCRIPT -> AUDIO -> VIDEO ->
DONE, with a generic FAILED state (error_message recorded) if any stage
raises. No Critic, no subtitles, no PostgreSQL -- those are later
milestones (see ROADMAP.md).
"""

from __future__ import annotations

import logging
import sqlite3
from dataclasses import dataclass
from pathlib import Path

from life_lesson.audio.wav_utils import concatenate_with_silence, wav_duration_ms
from life_lesson.config import Settings, get_settings
from life_lesson.db import repository as repo
from life_lesson.errors import PipelineError
from life_lesson.generation.gemini_client import generate_script_text
from life_lesson.generation.prompts import (
    SCRIPT_PROMPT_NAME,
    SCRIPT_PROMPT_STAGE,
    SCRIPT_PROMPT_VERSION,
    build_script_prompt,
)
from life_lesson.generation.formats import FormatSpec, get_format
from life_lesson.generation.schema import ScriptOutput, check_format, validate_script_json
from life_lesson.publish.metadata import write_publish_bundle
from life_lesson.tts.base import TTSProvider
from life_lesson.tts.gemini_tts import GeminiTTSProvider
from life_lesson.video.ffmpeg_assembler import assemble_video, pick_random_background

logger = logging.getLogger(__name__)


@dataclass
class PipelineResult:
    episode_id: str
    topic_id: str
    state: str
    audio_path: Path | None = None
    video_path: Path | None = None
    publish_dir: Path | None = None
    error_message: str | None = None


def run_pipeline(
    topic_text: str,
    theme: str | None = None,
    *,
    settings: Settings | None = None,
    tts_provider: TTSProvider | None = None,
    episode_format: str | None = None,
) -> PipelineResult:
    settings = settings or get_settings()
    spec = get_format(episode_format)

    with repo.open_db(settings.db_path) as conn:
        topic_id = repo.create_topic(conn, topic_text, theme)
        episode_id = repo.create_episode(conn, topic_id)
        logger.info("Created episode %s for topic %s", episode_id, topic_id)

        try:
            script = _generate_and_persist_script(
                conn, settings, episode_id, topic_id, topic_text, theme, spec
            )
            audio_path, block_starts_ms, duration_ms = _synthesize_audio(
                conn, settings, episode_id, script, tts_provider
            )
            video_path = _assemble_video(conn, settings, episode_id, audio_path, spec)
            publish_dir = _write_publish_bundle(
                settings, episode_id, script, spec, block_starts_ms, duration_ms
            )
        except PipelineError as exc:
            logger.error("Pipeline failed for episode %s: %s", episode_id, exc)
            repo.update_episode_state(
                conn, episode_id, "FAILED", error_message=str(exc)
            )
            return PipelineResult(
                episode_id=episode_id,
                topic_id=topic_id,
                state="FAILED",
                error_message=str(exc),
            )

        repo.update_episode_state(conn, episode_id, "DONE")
        return PipelineResult(
            episode_id=episode_id,
            topic_id=topic_id,
            state="DONE",
            audio_path=audio_path,
            video_path=video_path,
            publish_dir=publish_dir,
        )


def _generate_and_persist_script(
    conn: sqlite3.Connection,
    settings: Settings,
    episode_id: str,
    topic_id: str,
    topic_text: str,
    theme: str | None,
    spec: FormatSpec,
) -> ScriptOutput:
    repo.update_episode_state(conn, episode_id, "TOPIC")

    prompt = build_script_prompt(topic_id, topic_text, theme, spec.name)
    prompt_version_id = repo.register_prompt_version(
        conn, SCRIPT_PROMPT_NAME, SCRIPT_PROMPT_STAGE, SCRIPT_PROMPT_VERSION, prompt
    )

    raw_text = generate_script_text(settings, prompt)
    repo.log_generation_attempt(
        conn, episode_id, "script", 1, "success", raw_response=raw_text
    )

    try:
        script = validate_script_json(raw_text)
        check_format(script, spec)
        script.metadata.format = spec.name
        script.metadata.prompt_version = SCRIPT_PROMPT_VERSION
    except PipelineError as exc:
        repo.log_generation_attempt(
            conn, episode_id, "script_validation", 1, "failed", error_message=str(exc)
        )
        repo.save_script(conn, episode_id, prompt_version_id, raw_text, validated=False)
        raise

    repo.save_script(
        conn, episode_id, prompt_version_id, script.model_dump_json(), validated=True
    )
    repo.update_episode_state(conn, episode_id, "SCRIPT")
    logger.info("Script generated and validated for episode %s", episode_id)
    return script


def _synthesize_audio(
    conn: sqlite3.Connection,
    settings: Settings,
    episode_id: str,
    script: ScriptOutput,
    tts_provider: TTSProvider | None,
) -> tuple[Path, list[int], int]:
    provider = tts_provider or GeminiTTSProvider(settings)

    clips_with_pauses: list[tuple[bytes, int]] = []
    block_starts_ms: list[int] = []
    cursor_ms = 0
    for block in script.script_blocks:
        wav_bytes = provider.synthesize(block.text)
        clips_with_pauses.append((wav_bytes, block.pause_after_ms))
        block_starts_ms.append(cursor_ms)
        cursor_ms += wav_duration_ms(wav_bytes) + block.pause_after_ms

    output_path = settings.audio_output_dir / f"{episode_id}.wav"
    concatenate_with_silence(clips_with_pauses, output_path)

    repo.log_generation_attempt(conn, episode_id, "tts", 1, "success")
    repo.update_episode_state(conn, episode_id, "AUDIO", audio_path=str(output_path))
    logger.info("Audio synthesized for episode %s: %s", episode_id, output_path)
    return output_path, block_starts_ms, cursor_ms


def _write_publish_bundle(
    settings: Settings,
    episode_id: str,
    script: ScriptOutput,
    spec: FormatSpec,
    block_starts_ms: list[int],
    duration_ms: int,
) -> Path:
    credits = [
        f"เสียงบรรยาย: {settings.gemini_tts_model} (voice: {settings.gemini_tts_voice})",
        "วิดีโอพื้นหลัง/ดนตรี: ระบุแหล่งที่มาและใบอนุญาตก่อนเผยแพร่",
    ]
    out_dir = settings.output_dir / "publish" / episode_id
    write_publish_bundle(
        out_dir, script, spec, block_starts_ms, duration_ms, credits=credits
    )
    logger.info("Publish bundle written for episode %s: %s", episode_id, out_dir)
    return out_dir


def _assemble_video(
    conn: sqlite3.Connection,
    settings: Settings,
    episode_id: str,
    audio_path: Path,
    spec: FormatSpec,
) -> Path:
    background_video = pick_random_background(settings.background_video_dir)
    output_path = settings.video_output_dir / f"{episode_id}.mp4"

    assemble_video(
        ffmpeg_binary=settings.ffmpeg_binary,
        background_video=background_video,
        audio_path=audio_path,
        output_path=output_path,
        width=spec.width,
        height=spec.height,
    )

    repo.log_generation_attempt(conn, episode_id, "video", 1, "success")
    repo.update_episode_state(conn, episode_id, "VIDEO", video_path=str(output_path))
    logger.info("Video assembled for episode %s: %s", episode_id, output_path)
    return output_path
