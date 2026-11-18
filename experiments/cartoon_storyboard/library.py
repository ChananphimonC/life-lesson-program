"""The finished-video library: one folder per episode under output/videos/.

    output/videos/EP01 - <title>/EP01 - <title>.mp4
                                /info.json   {ep, title, episode_id, topic, theme, duration, rendered_at}

`render.py` files new renders here; `preview.py` lists, renames and deletes them.
"""

from __future__ import annotations

import json
import re
import shutil
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
LIB_DIR = HERE / "output" / "videos"
WORK_DIR = HERE / "output" / "_work"  # logs, timeline, keyframe previews

_ILLEGAL = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


def safe_title(title: str) -> str:
    title = _ILLEGAL.sub("", title).strip().rstrip(".")
    return re.sub(r"\s+", " ", title)[:80] or "untitled"


def _name(ep: int, title: str) -> str:
    return f"EP{ep:02d} - {safe_title(title)}"


def episodes() -> list[dict]:
    """All library entries, newest episode number first."""
    items = []
    if not LIB_DIR.exists():
        return items
    for folder in LIB_DIR.iterdir():
        info_path = folder / "info.json"
        if not info_path.is_file():
            continue
        info = json.loads(info_path.read_text(encoding="utf-8"))
        video = folder / f"{folder.name}.mp4"
        info["folder"] = folder.name
        info["video"] = video if video.is_file() else None
        items.append(info)
    return sorted(items, key=lambda i: i["ep"], reverse=True)


def find(folder_name: str) -> dict | None:
    return next((e for e in episodes() if e["folder"] == folder_name), None)


def target_for(episode_id: str, title: str) -> Path:
    """The MP4 path for an episode: its existing folder, or a new EP number."""
    existing = next((e for e in episodes() if e["episode_id"] == episode_id), None)
    if existing:
        return LIB_DIR / existing["folder"] / f"{existing['folder']}.mp4"
    ep = max((e["ep"] for e in episodes()), default=0) + 1
    name = _name(ep, title)
    (LIB_DIR / name).mkdir(parents=True, exist_ok=True)
    return LIB_DIR / name / f"{name}.mp4"


def write_info(video: Path, episode_id: str, title: str, topic: str, theme: str | None, duration: float):
    folder = video.parent
    ep = int(folder.name[2:4])
    old = folder / "info.json"
    info = json.loads(old.read_text(encoding="utf-8")) if old.is_file() else {}
    info.update({"ep": ep, "title": info.get("title", title), "episode_id": episode_id, "topic": topic,
                 "theme": theme, "duration": round(duration, 2),
                 "rendered_at": datetime.now().isoformat(timespec="seconds")})
    old.write_text(json.dumps(info, ensure_ascii=False, indent=2), encoding="utf-8")


def rename(folder_name: str, new_title: str) -> str:
    entry = find(folder_name)
    if entry is None:
        raise KeyError(folder_name)
    new_name = _name(entry["ep"], new_title)
    src = LIB_DIR / folder_name
    if new_name != folder_name:
        if (LIB_DIR / new_name).exists():
            raise FileExistsError(new_name)
        if entry["video"]:
            entry["video"].rename(src / f"{new_name}.mp4")
        src = src.rename(LIB_DIR / new_name)
    info = json.loads((src / "info.json").read_text(encoding="utf-8"))
    info["title"] = safe_title(new_title)
    (src / "info.json").write_text(json.dumps(info, ensure_ascii=False, indent=2), encoding="utf-8")
    return new_name


def delete(folder_name: str):
    if find(folder_name) is None:
        raise KeyError(folder_name)
    shutil.rmtree(LIB_DIR / folder_name)
