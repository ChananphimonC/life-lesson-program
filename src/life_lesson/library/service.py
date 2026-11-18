"""Library operations on finished episodes: export, delete, edit cover, rebuild
description, cut Shorts. Every file operation stays inside the output folder."""

from __future__ import annotations

import json
import logging
import re
import shutil
import sqlite3
from dataclasses import dataclass
from pathlib import Path

from life_lesson.config import Settings
from life_lesson.db import repository as repo
from life_lesson.errors import PipelineError
from life_lesson.generation.formats import get_format
from life_lesson.generation.schema import ScriptOutput, validate_script_json
from life_lesson.library.shorts import (
    block_end_times, pick_teaser_window, render_short, short_description, short_title,
)
from life_lesson.publish.credits import build_credits, channel_line
from life_lesson.publish.metadata import build_description, build_thumbnail_spec, build_title
from life_lesson.publish.thumbnail import render_thumbnail
from life_lesson.video.ffmpeg_assembler import extract_frame

logger = logging.getLogger(__name__)

SHORTS_FOLDER = "Shorts"


@dataclass
class EpisodeAssets:
    row: sqlite3.Row
    script: ScriptOutput
    starts_ms: list[int]
    duration_ms: int
    publish_dir: Path


def _require(row, ref: str):
    if row is None:
        raise PipelineError(f"No episode matches {ref!r} (use `list` to see ids; a unique prefix works).")
    return row


def _inside(base: Path, path: Path) -> bool:
    try:
        path.resolve().relative_to(base.resolve())
        return True
    except ValueError:
        return False


def load_episode(settings: Settings, conn: sqlite3.Connection, ref: str) -> EpisodeAssets:
    row = _require(repo.find_episode(conn, ref), ref)
    raw = repo.get_latest_script_json(conn, row["id"])
    if raw is None:
        raise PipelineError(f"Episode {row['id'][:8]} has no validated script.")
    pdir = Path(row["publish_dir"]) if row["publish_dir"] else settings.output_dir / "publish" / row["id"]
    starts, total = [], 0
    tl = pdir / "timeline.json"
    if tl.is_file():
        data = json.loads(tl.read_text(encoding="utf-8"))
        starts, total = data["block_starts_ms"], data["duration_ms"]
    return EpisodeAssets(row, validate_script_json(raw), starts, total, pdir)


def safe_filename(title: str) -> str:
    name = re.sub(r'[\\/:*?"<>|\x00-\x1f]', "", title).strip()
    name = re.sub(r"\s+", "_", name).strip("._")
    return (name or "episode")[:80]


def export_mp4(settings: Settings, conn: sqlite3.Connection, ref: str, *, dest_dir: Path | None = None, name: str | None = None) -> Path:
    row = _require(repo.find_episode(conn, ref), ref)
    if not row["video_path"] or not Path(row["video_path"]).is_file():
        raise PipelineError(f"Episode {row['id'][:8]} has no video file to export.")
    dest = Path(dest_dir) if dest_dir else (settings.export_dir or settings.output_dir / "export")
    dest.mkdir(parents=True, exist_ok=True)
    base = safe_filename(name or row["title"] or row["id"][:8])
    target = dest / f"{base}.mp4"
    n = 2
    while target.exists():
        target = dest / f"{base}_{n}.mp4"
        n += 1
    shutil.copy2(row["video_path"], target)
    return target


def _episode_files(settings: Settings, row) -> list[Path]:
    eid = row["id"]
    paths = [Path(p) for p in (row["video_path"], row["audio_path"]) if p]
    audio_dir = settings.audio_output_dir
    paths += [audio_dir / f"{eid}{suffix}" for suffix in (".narration.wav", ".bed.wav", ".wav")]
    pdir = Path(row["publish_dir"]) if row["publish_dir"] else settings.output_dir / "publish" / eid
    return paths + [pdir]


def delete_episode(settings: Settings, conn: sqlite3.Connection, ref: str, *, keep_files: bool = False, with_shorts: bool = False) -> list[Path]:
    """Delete an episode's records and (unless keep_files) its files. Returns removed paths.

    Files outside the output folder are never touched. An episode that still has
    Shorts is refused unless `with_shorts` is set.
    """
    row = _require(repo.find_episode(conn, ref), ref)
    shorts = repo.child_shorts(conn, row["id"])
    if shorts and not with_shorts:
        raise PipelineError(
            f"Episode {row['id'][:8]} has {len(shorts)} Short(s); delete them first or pass with_shorts."
        )
    removed: list[Path] = []
    for child in shorts:
        removed += delete_episode(settings, conn, child["id"], keep_files=keep_files)
    if not keep_files:
        for path in dict.fromkeys(_episode_files(settings, row)):
            if not _inside(settings.output_dir, path):
                logger.warning("Not deleting %s: outside the output folder", path)
                continue
            if path.is_dir():
                shutil.rmtree(path)
                removed.append(path)
            elif path.is_file():
                path.unlink()
                removed.append(path)
    repo.delete_episode_record(conn, row["id"])
    return removed


def regenerate_thumbnail(
    settings: Settings, conn: sqlite3.Connection, ref: str, *,
    title: str | None = None, tag: str | None = None, subline: str | None = None,
    frame_at: float | None = None, base_image: Path | None = None,
) -> Path:
    """Re-render the cover with edited text and/or a different backdrop frame."""
    a = load_episode(settings, conn, ref)
    spec = get_format(a.row["format"] or "standard")
    script = a.script.model_copy(deep=True)
    if title:
        script.title = title
    tspec = build_thumbnail_spec(script, spec, a.duration_ms or 60_000)
    if tag is not None:
        tspec["context_tag"] = tag or None
    if subline is not None:
        tspec["subline"] = subline
    out = a.publish_dir / "thumbnail.png"
    if out.is_file():
        shutil.copy2(out, a.publish_dir / "thumbnail.prev.png")
    backdrop = base_image
    if backdrop is None and frame_at is not None and a.row["video_path"]:
        backdrop = extract_frame(settings.ffmpeg_binary, Path(a.row["video_path"]), frame_at, a.publish_dir / "frame.png")
    elif backdrop is None and (a.publish_dir / "frame.png").is_file():
        backdrop = a.publish_dir / "frame.png"
    render_thumbnail(tspec, out, base_image=backdrop, font_path=settings.thai_font_path)
    (a.publish_dir / "thumbnail.json").write_text(json.dumps(tspec, ensure_ascii=False, indent=2), encoding="utf-8")
    repo.update_episode_meta(conn, a.row["id"], thumbnail_path=str(out), **({"title": title} if title else {}))
    return out


def rebuild_description(settings: Settings, conn: sqlite3.Connection, ref: str, *, full_url: str | None = None) -> Path:
    a = load_episode(settings, conn, ref)
    spec = get_format(a.row["format"] or "standard")
    if a.row["kind"] == "short":
        text = short_description(a.script, channel_handle=settings.channel_handle,
                                 channel_url=settings.channel_url, full_url=full_url)
    else:
        if not a.starts_ms:
            raise PipelineError("timeline.json is missing, so chapters cannot be rebuilt.")
        text = build_description(a.script, spec, a.starts_ms, credits=build_credits(settings),
                                 channel_line=channel_line(settings))
    out = a.publish_dir / "description.txt"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    (a.publish_dir / "title.txt").write_text(
        (a.row["title"] or build_title(a.script, spec)) + "\n", encoding="utf-8")
    return out


@dataclass
class ShortResult:
    episode_id: str
    video_path: Path
    publish_dir: Path
    title: str
    seconds: float


def create_short(
    settings: Settings, conn: sqlite3.Connection, ref: str, *,
    full_url: str | None = None, offset: int = 0, min_s: float = 30, max_s: float = 55,
    width: int = 1080, height: int = 1920, layout: str = "fit",
) -> ShortResult:
    """Cut a Short from the real episode and register it in the library (folder "Shorts")."""
    a = load_episode(settings, conn, ref)
    if a.row["kind"] == "short":
        raise PipelineError("Cut Shorts from a full episode, not from another Short.")
    if not a.starts_ms:
        raise PipelineError("timeline.json is missing; re-run the episode to cut a Short.")
    src = Path(a.row["video_path"] or "")
    if not src.is_file():
        raise PipelineError(f"Source video not found: {src}")

    ends = block_end_times(a.script, a.starts_ms, a.duration_ms)
    window = pick_teaser_window(a.script, a.starts_ms, a.duration_ms, min_s=min_s, max_s=max_s, offset=offset)
    title = short_title(a.script, window)

    short_id = repo.create_episode(conn, a.row["topic_id"])
    video = settings.video_output_dir / f"{short_id}.mp4"
    pdir = settings.output_dir / "publish" / short_id
    try:
        render_short(
            ffmpeg_binary=settings.ffmpeg_binary, source_video=src, window=window, script=a.script,
            starts_ms=a.starts_ms, ends_ms=ends, output_path=video,
            channel_handle=settings.channel_handle, title=a.script.title,
            font_path=settings.thai_font_path, width=width, height=height, layout=layout,
        )
    except PipelineError:
        repo.delete_episode_record(conn, short_id)
        raise

    pdir.mkdir(parents=True, exist_ok=True)
    (pdir / "title.txt").write_text(title + "\n", encoding="utf-8")
    (pdir / "description.txt").write_text(
        short_description(a.script, channel_handle=settings.channel_handle,
                          channel_url=settings.channel_url, full_url=full_url), encoding="utf-8")
    (pdir / "window.json").write_text(json.dumps({
        "parent": a.row["id"], "first_block": window.first, "last_block": window.last,
        "start_ms": window.start_ms, "end_ms": window.end_ms, "score": round(window.score, 2)}), encoding="utf-8")

    thumb = None
    try:  # best-effort vertical cover from the Short itself
        frame = extract_frame(settings.ffmpeg_binary, video, 1.0, pdir / "frame.png")
        tspec = build_thumbnail_spec(a.script, get_format("short"), int(window.duration_s * 1000))
        tspec["size"] = [width, height]
        thumb = render_thumbnail(tspec, pdir / "thumbnail.png", base_image=frame, font_path=settings.thai_font_path)
    except (PipelineError, ValueError) as exc:
        logger.warning("Short cover not rendered: %s", exc)

    repo.update_episode_meta(
        conn, short_id, title=title, format="short", kind="short", parent_episode_id=a.row["id"],
        publish_dir=str(pdir), thumbnail_path=str(thumb) if thumb else None)
    repo.update_episode_state(conn, short_id, "DONE", video_path=str(video))
    # the short reuses the parent's script so it can be edited/rebuilt like any episode
    repo.save_script(conn, short_id, _any_prompt_version(conn), a.script.model_dump_json(), validated=True)
    repo.add_to_playlist(conn, repo.create_playlist(conn, SHORTS_FOLDER, "folder"), short_id)
    return ShortResult(short_id, video, pdir, title, window.duration_s + 3.0)


def _any_prompt_version(conn: sqlite3.Connection) -> int:
    return repo.register_prompt_version(conn, "short_cut", "short", "short-cut-v1", "teaser window selection")
