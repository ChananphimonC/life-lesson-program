"""The Shorts (9:16) side of the library: reads what experiments/shorts/render_short.py produced.

    experiments/shorts/output/<id>/short.mp4
                                  /meta.json      {"title": ...}  editable from the library page
                                  /audio.wav      the mixed soundtrack (its length is the duration)

Kept apart from library.py so Shorts never mix into the Life Lesson playlist (EP numbering, 16:9).
"""

from __future__ import annotations

import json
import shutil
import wave
from datetime import datetime
from pathlib import Path

import library

HERE = Path(__file__).resolve().parent
SHORTS_DIR = HERE.parent / "shorts" / "output"
SCRIPTS_DIR = HERE.parent / "shorts" / "scripts"


def script_for(short_id: str) -> dict:
    for p in SCRIPTS_DIR.glob("*.json"):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if data.get("id") == short_id:
            return data
    return {}


def _script_title(short_id: str) -> str | None:
    return script_for(short_id).get("title")


def shorts() -> list[dict]:
    """All rendered Shorts, newest first."""
    items = []
    if not SHORTS_DIR.exists():
        return items
    for folder in SHORTS_DIR.iterdir():
        video = folder / "short.mp4"
        if not video.is_file():
            continue
        meta_path = folder / "meta.json"
        meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.is_file() else {}
        duration = 0.0
        try:
            with wave.open(str(folder / "audio.wav"), "rb") as w:
                duration = w.getnframes() / w.getframerate()
        except (OSError, wave.Error):
            pass
        script = script_for(folder.name)
        summary = " ".join(ln.get("text", "") for sc in script.get("scenes", []) for ln in sc.get("lines", [])
                           if not ln.get("sfx_voice"))
        items.append({"id": folder.name, "title": meta.get("title") or script.get("title") or folder.name,
                      "aspect": script.get("aspect", "9:16"), "playlist": script.get("playlist"),
                      "summary": summary[:4000],
                      "video": video, "duration": duration, "size": video.stat().st_size,
                      "rendered_at": datetime.fromtimestamp(video.stat().st_mtime).isoformat(timespec="minutes")})
    return sorted(items, key=lambda i: i["rendered_at"], reverse=True)


def find(short_id: str) -> dict | None:
    return next((s for s in shorts() if s["id"] == short_id), None)


def rename(short_id: str, title: str) -> str:
    entry = find(short_id)
    if entry is None:
        raise KeyError(short_id)
    title = " ".join(title.split())[:120]
    if not title:
        raise ValueError("empty title")
    (SHORTS_DIR / short_id / "meta.json").write_text(json.dumps({"title": title}, ensure_ascii=False, indent=2),
                                                     encoding="utf-8")
    return title


def download_name(entry: dict) -> str:
    return f"{library.safe_title(entry['title'])}.mp4"


def delete(short_id: str) -> None:
    """Remove a rendered Short (its whole output folder: mp4, audio, timeline, meta).
    The script JSON in experiments/shorts/scripts/ is never touched, so it can be re-rendered."""
    if find(short_id) is None:  # only ids of folders that really hold a Short
        raise KeyError(short_id)
    shutil.rmtree(SHORTS_DIR / short_id)
