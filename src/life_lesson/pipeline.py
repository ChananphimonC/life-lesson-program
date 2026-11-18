"""Episode pipeline orchestrator.

Topic -> sensitive-topic screen -> script (Gemini) -> validation -> Critic loop
-> per-block TTS (mood-directed voice and pacing) -> scene plan -> ambient bed
+ optional music -> mastering (-16 LUFS) -> scene video (grade/rain/cards) ->
publish bundle (title, description, thumbnail, shot list, review checklist).

States: DRAFT -> TOPIC -> SCRIPT -> CRITIC_REVIEW -> AUDIO -> VIDEO -> DONE.
Terminal alternatives: FAILED (technical error), FAILED_REVIEW (Critic still
unhappy after 3 rewrites: a human must decide), REJECTED (sensitive topic).
"""

from __future__ import annotations

import json
import logging
import sqlite3
from dataclasses import dataclass
from pathlib import Path

from life_lesson.audio.ambient import build_ambient_bed
from life_lesson.audio.mastering import master_audio, pick_music
from life_lesson.audio.wav_utils import concatenate_with_silence, wav_duration_ms
from life_lesson.config import Settings, get_settings
from life_lesson.db import repository as repo
from life_lesson.errors import PipelineError, SensitiveTopicError
from life_lesson.generation.atmosphere import scaled_pause_ms, styled_text
from life_lesson.generation.critic import (
    CATEGORIES,
    CRITIC_PROMPT_NAME,
    CRITIC_PROMPT_STAGE,
    CRITIC_PROMPT_VERSION,
    run_critic_loop,
)
from life_lesson.generation.formats import FormatSpec, get_format
from life_lesson.generation.gemini_client import generate_critic_text, generate_script_text
from life_lesson.generation.prompts import (
    SCRIPT_PROMPT_NAME,
    SCRIPT_PROMPT_STAGE,
    SCRIPT_PROMPT_VERSION,
    build_script_prompt,
)
from life_lesson.generation.safety import screen_topic
from life_lesson.generation.schema import ScriptOutput, check_format, validate_script_json
from life_lesson.publish.metadata import build_thumbnail_spec, write_publish_bundle
from life_lesson.publish.thumbnail import render_thumbnail
from life_lesson.tts.base import TTSProvider
from life_lesson.tts.gemini_tts import GeminiTTSProvider
from life_lesson.video.ffmpeg_assembler import assemble_video, extract_frame, pick_random_background
from dataclasses import replace

from life_lesson.video.references import blended_palette, search_references
from life_lesson.video.scene_kb import RECIPES
from life_lesson.video.scenes import (
    Scene,
    assemble_scene_video,
    plan_scenes,
    write_shot_list,
)

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
    critic: bool = True,
) -> PipelineResult:
    settings = settings or get_settings()
    spec = get_format(episode_format)

    with repo.open_db(settings.db_path) as conn:
        topic_id = repo.create_topic(conn, topic_text, theme)
        episode_id = repo.create_episode(conn, topic_id)
        logger.info("Created episode %s for topic %s", episode_id, topic_id)

        def result(state: str, **kw) -> PipelineResult:
            return PipelineResult(episode_id=episode_id, topic_id=topic_id, state=state, **kw)

        try:
            try:
                screen_topic(topic_text, theme)
            except SensitiveTopicError as exc:
                repo.set_topic_status(conn, topic_id, "rejected")
                repo.update_episode_state(conn, episode_id, "REJECTED", error_message=str(exc))
                return result("REJECTED", error_message=str(exc))

            script = _generate_and_persist_script(
                conn, settings, episode_id, topic_id, topic_text, theme, spec
            )
            if critic:
                script, passed = _review_script(conn, settings, episode_id, script, spec)
                if not passed:
                    msg = (
                        f"Critic still flagged the script after the maximum rewrites; "
                        "a human must edit, discard or restart the topic."
                    )
                    repo.update_episode_state(conn, episode_id, "FAILED_REVIEW", error_message=msg)
                    return result("FAILED_REVIEW", error_message=msg)

            narration_path, block_starts_ms, duration_ms = _synthesize_audio(
                conn, settings, episode_id, script, tts_provider
            )
            scenes = plan_scenes(script, block_starts_ms, duration_ms)
            scenes, reference_credits = _gather_references(settings, scenes)
            audio_path = _master(conn, settings, episode_id, narration_path, scenes, duration_ms)
            video_path = _assemble_video(conn, settings, episode_id, audio_path, spec, scenes)
            publish_dir = _write_publish_bundle(
                settings, episode_id, script, spec, block_starts_ms, duration_ms, scenes, video_path,
                extra_credits=reference_credits,
            )
            thumb = publish_dir / "thumbnail.png"
            repo.update_episode_meta(
                conn, episode_id, title=script.title, format=spec.name,
                publish_dir=str(publish_dir),
                thumbnail_path=str(thumb) if thumb.exists() else None,
            )
        except PipelineError as exc:
            logger.error("Pipeline failed for episode %s: %s", episode_id, exc)
            repo.update_episode_state(conn, episode_id, "FAILED", error_message=str(exc))
            return result("FAILED", error_message=str(exc))

        repo.update_episode_state(conn, episode_id, "DONE")
        return result("DONE", audio_path=audio_path, video_path=video_path, publish_dir=publish_dir)


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
    repo.log_generation_attempt(conn, episode_id, "script", 1, "success", raw_response=raw_text)

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

    repo.save_script(conn, episode_id, prompt_version_id, script.model_dump_json(), validated=True)
    repo.update_episode_state(conn, episode_id, "SCRIPT")
    logger.info("Script generated and validated for episode %s", episode_id)
    return script


def _review_script(
    conn: sqlite3.Connection,
    settings: Settings,
    episode_id: str,
    script: ScriptOutput,
    spec: FormatSpec,
) -> tuple[ScriptOutput, bool]:
    repo.update_episode_state(conn, episode_id, "CRITIC_REVIEW")
    version_id = repo.register_prompt_version(
        conn,
        CRITIC_PROMPT_NAME,
        CRITIC_PROMPT_STAGE,
        CRITIC_PROMPT_VERSION,
        "categories: " + ", ".join(CATEGORIES),
    )

    def on_critic(attempt: int, result, raw: str) -> None:
        failed = [r.category for r in result.failed]
        repo.log_generation_attempt(
            conn, episode_id, "critic", attempt,
            "passed" if result.passed else "failed",
            error_message=", ".join(failed) or None, raw_response=raw,
        )

    def on_rewrite(n: int, revised: ScriptOutput) -> None:
        repo.log_generation_attempt(conn, episode_id, "rewrite", n, "success")
        repo.save_script(conn, episode_id, version_id, revised.model_dump_json(), validated=True)

    outcome = run_critic_loop(
        script,
        spec,
        call_llm=lambda prompt: generate_critic_text(settings, prompt),
        on_critic=on_critic,
        on_rewrite=on_rewrite,
    )
    logger.info(
        "Critic %s for episode %s after %d rewrite(s)",
        "passed" if outcome.passed else "FAILED", episode_id, outcome.rewrites_used,
    )
    return outcome.script, outcome.passed


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
        text = styled_text(block.text, block.mood) if settings.tts_style_directives else block.text
        wav_bytes = provider.synthesize(text)
        pause = scaled_pause_ms(block.pause_after_ms, block.mood)
        clips_with_pauses.append((wav_bytes, pause))
        block_starts_ms.append(cursor_ms)
        cursor_ms += wav_duration_ms(wav_bytes) + pause

    output_path = settings.audio_output_dir / f"{episode_id}.narration.wav"
    concatenate_with_silence(clips_with_pauses, output_path)

    repo.log_generation_attempt(conn, episode_id, "tts", 1, "success")
    logger.info("Narration synthesized for episode %s: %s", episode_id, output_path)
    return output_path, block_starts_ms, cursor_ms


def _master(
    conn: sqlite3.Connection,
    settings: Settings,
    episode_id: str,
    narration_path: Path,
    scenes: list[Scene],
    duration_ms: int,
) -> Path:
    """Ambient bed (+ optional music) under the narration, normalised to -16 LUFS."""
    music = pick_music(settings.music_dir)
    bed = build_ambient_bed(
        settings.ffmpeg_binary, scenes, duration_ms,
        settings.audio_output_dir / f"{episode_id}.bed.wav", music=music,
    )
    output = settings.audio_output_dir / f"{episode_id}.wav"
    master_audio(settings.ffmpeg_binary, narration_path, output, music=bed, bed_gain_db=0.0)

    repo.log_generation_attempt(conn, episode_id, "master", 1, "success")
    repo.update_episode_state(conn, episode_id, "AUDIO", audio_path=str(output))
    return output


def _assemble_video(
    conn: sqlite3.Connection,
    settings: Settings,
    episode_id: str,
    audio_path: Path,
    spec: FormatSpec,
    scenes: list[Scene],
) -> Path:
    output_path = settings.video_output_dir / f"{episode_id}.mp4"
    needs_scenes = (
        settings.visual_mode == "illustrated" or len(scenes) > 1 or any(s.mood for s in scenes)
    )

    if needs_scenes:
        assemble_scene_video(
            ffmpeg_binary=settings.ffmpeg_binary,
            scenes=scenes,
            background_dir=settings.background_video_dir,
            audio_path=audio_path,
            output_path=output_path,
            width=spec.width,
            height=spec.height,
            show_cards=spec.name != "short",
            font_path=settings.thai_font_path,
            visual_mode=settings.visual_mode,
        )
    else:
        assemble_video(
            ffmpeg_binary=settings.ffmpeg_binary,
            background_video=pick_random_background(settings.background_video_dir),
            audio_path=audio_path,
            output_path=output_path,
            width=spec.width,
            height=spec.height,
        )

    repo.log_generation_attempt(conn, episode_id, "video", 1, "success")
    repo.update_episode_state(conn, episode_id, "VIDEO", video_path=str(output_path))
    logger.info("Video assembled for episode %s: %s", episode_id, output_path)
    return output_path


def _gather_references(settings: Settings, scenes: list[Scene]) -> tuple[list[Scene], list[str]]:
    """Opt-in: look up open-licence reference photos per scene type before drawing."""
    if not settings.reference_search or settings.visual_mode != "illustrated":
        return scenes, []
    queries = {r.id: r.search_query for r in RECIPES if r.search_query}
    cache: dict[str, list] = {}
    out, credits = [], []
    for scene in scenes:
        query = queries.get(scene.recipe_id)
        if not query:
            out.append(scene)
            continue
        if query not in cache:
            cache[query] = search_references(query, cache_dir=(settings.cache_dir / "references") if settings.cache_dir else None)
        refs = cache[query]
        out.append(replace(scene, ref_palette=blended_palette(refs)) if refs else scene)
        credits += [r.credit_line for r in refs if r.credit_line not in credits]
    return out, credits


def channel_line(settings: Settings) -> str:
    return f"ดูเรื่องเต็มและเรื่องใหม่ได้ที่ช่อง {settings.channel_handle}\n{settings.channel_url}"


def _credits(settings: Settings) -> list[str]:
    lines = [
        f"เสียงบรรยาย: {settings.gemini_tts_model} (voice: {settings.gemini_tts_voice})",
        "เสียงบรรยากาศ: สังเคราะห์ด้วยซอฟต์แวร์",
    ]
    path = settings.credits_file
    if path is not None and path.is_file():
        lines += [ln.strip() for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]
    else:
        lines.append("วิดีโอพื้นหลัง/ดนตรี: ระบุแหล่งที่มาและใบอนุญาตก่อนเผยแพร่ (assets/credits.txt)")
    return lines


def _write_publish_bundle(
    settings: Settings,
    episode_id: str,
    script: ScriptOutput,
    spec: FormatSpec,
    block_starts_ms: list[int],
    duration_ms: int,
    scenes: list[Scene],
    video_path: Path,
    extra_credits: list[str] | None = None,
) -> Path:
    out_dir = settings.output_dir / "publish" / episode_id
    write_publish_bundle(
        out_dir, script, spec, block_starts_ms, duration_ms,
        credits=_credits(settings) + (extra_credits or []), channel_line=channel_line(settings),
    )
    # Needed later to rebuild chapters / cut Shorts without re-running TTS.
    (out_dir / "timeline.json").write_text(
        json.dumps({"block_starts_ms": block_starts_ms, "duration_ms": duration_ms}), encoding="utf-8"
    )
    write_shot_list(scenes, out_dir / "shot_list.json")

    # Thumbnail PNG is best-effort: a missing Thai font must not sink an episode
    # whose video is already rendered; the JSON spec is always written.
    try:
        frame = extract_frame(settings.ffmpeg_binary, video_path, 1.5, out_dir / "frame.png")
    except PipelineError as exc:
        logger.warning("No frame for thumbnail backdrop: %s", exc)
        frame = None
    try:
        render_thumbnail(
            build_thumbnail_spec(script, spec, duration_ms),
            out_dir / "thumbnail.png",
            base_image=frame,
            font_path=settings.thai_font_path,
        )
    except (PipelineError, ValueError) as exc:
        logger.warning("Thumbnail PNG not rendered: %s", exc)

    logger.info("Publish bundle written for episode %s: %s", episode_id, out_dir)
    return out_dir
