"""Publish finished clips into the owner's existing local library layout
(experiments/cartoon_storyboard + experiments/shorts), so they show up in that
library page with cover, playlist and download -- no changes to it needed.

    <videos_dir>/EP07 - <title>/EP07 - <title>.mp4
                               /info.json   {ep, title, episode_id, topic, theme, duration, rendered_at}
                               /cover.jpg   1920x1080, < 2 MB (YouTube limit)
                               /cover.json  {text, source}
    <shorts_dir>/<id>/short.mp4  /meta.json {"title"}  /audio.wav (its length is the duration)

Re-exporting the same episode updates its folder instead of creating EP08.
"""

from __future__ import annotations

import json
import re
import shutil
import sqlite3
import subprocess
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageFile

from life_lesson.config import Settings
from life_lesson.db import repository as repo
from life_lesson.errors import PipelineError

_ILLEGAL = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
_EP_DIR = re.compile(r"^EP(\d+) - ")
MAX_COVER_BYTES = 2 * 1024 * 1024


def safe_title(title: str) -> str:
    """Same rule as the owner's library.py so folder names match theirs."""
    title = _ILLEGAL.sub("", title).strip().rstrip(".")
    return re.sub(r"\s+", " ", title)[:80] or "untitled"


def _existing(videos_dir: Path) -> list[tuple[int, Path]]:
    out = []
    if videos_dir.is_dir():
        for folder in videos_dir.iterdir():
            m = _EP_DIR.match(folder.name)
            if m and folder.is_dir():
                out.append((int(m.group(1)), folder))
    return out


def next_ep_number(videos_dir: Path) -> int:
    return max((n for n, _ in _existing(videos_dir)), default=0) + 1


def _find_by_episode_id(videos_dir: Path, episode_id: str) -> Path | None:
    for _, folder in _existing(videos_dir):
        info = folder / "info.json"
        try:
            if info.is_file() and json.loads(info.read_text(encoding="utf-8")).get("episode_id") == episode_id:
                return folder
        except (OSError, ValueError):
            continue
    return None


def jpeg_under(png: Path, out: Path, limit: int = MAX_COVER_BYTES, size: tuple[int, int] = (1920, 1080)) -> Path:
    """Convert to JPEG, lowering quality until under `limit` bytes."""
    img = Image.open(png).convert("RGB")
    # Pillow's default encoder block is too small for `optimize` on detailed 1080p art
    # ("broken data stream when writing image file"); size it to the picture.
    ImageFile.MAXBLOCK = max(ImageFile.MAXBLOCK, img.width * img.height * 3)
    if img.size != size:
        img = img.resize(size, Image.LANCZOS)
    for quality in (95, 92, 88, 84, 80, 74, 68, 60):
        img.save(out, "JPEG", quality=quality, optimize=True, subsampling=0 if quality >= 90 else 2)
        if out.stat().st_size <= limit:
            return out
    raise PipelineError(f"cover could not be compressed under {limit} bytes")


def _duration_s(video: Path, ffmpeg: str) -> float:
    probe = Path(ffmpeg).with_name("ffprobe") if Path(ffmpeg).name == "ffmpeg" and Path(ffmpeg).parent != Path(".") else "ffprobe"
    try:
        out = subprocess.run([str(probe), "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(video)],
                             capture_output=True, text=True, check=True).stdout.strip()
        return float(out)
    except (OSError, ValueError, subprocess.CalledProcessError):
        return 0.0


def export_episode(settings: Settings, conn: sqlite3.Connection, ref: str, *, videos_dir: Path) -> Path:
    row = repo.find_episode(conn, ref)
    if row is None:
        raise PipelineError(f"No episode matches {ref!r}.")
    if row["kind"] == "short":
        raise PipelineError("This is a Short: use the shorts directory instead.")
    if not row["video_path"] or not Path(row["video_path"]).is_file():
        raise PipelineError("The episode has no video file to export.")
    title = row["title"] or row["id"][:8]
    videos_dir.mkdir(parents=True, exist_ok=True)

    folder = _find_by_episode_id(videos_dir, row["id"])
    if folder is None:
        ep = next_ep_number(videos_dir)
        folder = videos_dir / f"EP{ep:02d} - {safe_title(title)}"
    else:
        ep = int(_EP_DIR.match(folder.name).group(1))
    folder.mkdir(parents=True, exist_ok=True)

    mp4 = folder / f"{folder.name}.mp4"
    shutil.copy2(row["video_path"], mp4)
    topic = conn.execute("SELECT text, theme FROM topics WHERE id = ?", (row["topic_id"],)).fetchone()
    info = {
        "ep": ep, "title": safe_title(title), "episode_id": row["id"],
        "topic": topic["text"] if topic else title, "theme": topic["theme"] if topic else None,
        "duration": round(_duration_s(mp4, settings.ffmpeg_binary), 2),
        "rendered_at": datetime.now().isoformat(timespec="seconds"),
    }
    (folder / "info.json").write_text(json.dumps(info, ensure_ascii=False, indent=2), encoding="utf-8")

    thumb = Path(row["thumbnail_path"]) if row["thumbnail_path"] else None
    if thumb and thumb.is_file():
        jpeg_under(thumb, folder / "cover.jpg")
        spec_path = thumb.with_name("thumbnail.json")
        text = []
        if spec_path.is_file():
            spec = json.loads(spec_path.read_text(encoding="utf-8"))
            text = [spec.get("headline_line1", ""), spec.get("headline_line2", "")]
        (folder / "cover.json").write_text(
            json.dumps({"text": [t for t in text if t], "source": "life_lesson pipeline (illustrated)"}, ensure_ascii=False, indent=2),
            encoding="utf-8")
    return folder


def export_short(settings: Settings, conn: sqlite3.Connection, ref: str, *, shorts_dir: Path) -> Path:
    row = repo.find_episode(conn, ref)
    if row is None:
        raise PipelineError(f"No episode matches {ref!r}.")
    if row["kind"] != "short":
        raise PipelineError("This is a full episode: use the videos directory instead.")
    if not row["video_path"] or not Path(row["video_path"]).is_file():
        raise PipelineError("The Short has no video file to export.")
    folder = shorts_dir / row["id"]
    folder.mkdir(parents=True, exist_ok=True)
    shutil.copy2(row["video_path"], folder / "short.mp4")
    (folder / "meta.json").write_text(json.dumps({"title": " ".join((row["title"] or row["id"]).split())[:120]},
                                                 ensure_ascii=False, indent=2), encoding="utf-8")
    result = subprocess.run([settings.ffmpeg_binary, "-y", "-i", str(folder / "short.mp4"), "-vn", "-ac", "1",
                             "-ar", "24000", "-c:a", "pcm_s16le", str(folder / "audio.wav")],
                            capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise PipelineError(f"could not extract the Short's audio: {result.stderr[-300:]}")
    return folder
