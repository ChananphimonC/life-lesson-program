"""Playlists for the library page, stored as a local file (no database change, episode files untouched):

    output/playlists.json   {"playlists": [{id, name, aspect, builtin}], "assign": {item_key: playlist_id}}

Item keys are stable across renames: "ep:<episode_id>" for Life Lesson episodes, "short:<id>" for clips made by
experiments/shorts/render_short.py (Shorts and the 16:9 "รู้หรือไม่" series). An item without an explicit assignment
falls into its default playlist, so existing episodes keep showing exactly where they were.
"""

from __future__ import annotations

import json
import uuid
from pathlib import Path

import library
import shorts_lib

PL_FILE = library.HERE / "output" / "playlists.json"
ASPECTS = ("16:9", "9:16", "1:1")
DEFAULTS = [
    {"id": "life_lesson", "name": "Life Lesson", "aspect": "16:9", "builtin": True},
    {"id": "shorts", "name": "Shorts", "aspect": "9:16", "builtin": True},
    {"id": "knowledge", "name": "รู้หรือไม่", "aspect": "16:9", "builtin": True},
]


def load() -> dict:
    try:
        data = json.loads(PL_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        data = {}
    data.setdefault("playlists", [])
    data.setdefault("assign", {})
    have = {p["id"] for p in data["playlists"]}
    for i, d in enumerate(DEFAULTS):
        if d["id"] not in have:
            data["playlists"].insert(i, dict(d))
    return data


def _save(data: dict) -> None:
    PL_FILE.parent.mkdir(parents=True, exist_ok=True)
    PL_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _find(data: dict, pid: str) -> dict:
    pl = next((p for p in data["playlists"] if p["id"] == pid), None)
    if pl is None:
        raise KeyError(pid)
    return pl


def _clean_name(name: str) -> str:
    name = " ".join(str(name).split())[:60]
    if not name:
        raise ValueError("ชื่อเพลย์ลิสต์ว่างไม่ได้")
    return name


def items() -> list[dict]:
    """Every clip in the library: {"key", "kind": "ep"|"short", "entry"}."""
    out = [{"key": f"ep:{e['episode_id']}", "kind": "ep", "entry": e} for e in library.episodes()]
    out += [{"key": f"short:{s['id']}", "kind": "short", "entry": s} for s in shorts_lib.shorts()]
    return out


def default_playlist(item: dict) -> str:
    if item["kind"] == "ep":
        return "life_lesson"
    entry = item["entry"]
    return entry.get("playlist") or ("knowledge" if entry.get("aspect") == "16:9" else "shorts")


def playlist_of(item: dict) -> str:
    """The playlist id an item is shown in (its assignment, or the default if that playlist is gone)."""
    data = load()
    pid = data["assign"].get(item["key"])
    return pid if pid in {p["id"] for p in data["playlists"]} else default_playlist(item)


def grouped() -> list[tuple[dict, list[dict]]]:
    """[(playlist, [items])] in playlist order; an assignment to a deleted playlist falls back to the default."""
    data = load()
    groups = {p["id"]: [] for p in data["playlists"]}
    for it in items():
        groups.setdefault(playlist_of(it), []).append(it)
    return [(p, groups.get(p["id"], [])) for p in data["playlists"]]


def add(name: str, aspect: str = "16:9") -> dict:
    if aspect not in ASPECTS:
        raise ValueError(f"อัตราส่วนต้องเป็น {', '.join(ASPECTS)}")
    data = load()
    pl = {"id": "pl_" + uuid.uuid4().hex[:8], "name": _clean_name(name), "aspect": aspect, "builtin": False}
    data["playlists"].append(pl)
    _save(data)
    return pl


def rename(pid: str, name: str) -> str:
    data = load()
    _find(data, pid)["name"] = _clean_name(name)
    _save(data)
    return _find(data, pid)["name"]


def delete(pid: str) -> None:
    data = load()
    pl = _find(data, pid)
    if pl.get("builtin"):
        raise ValueError("เพลย์ลิสต์ตั้งต้นลบไม่ได้ (เปลี่ยนชื่อได้)")
    if any(p["id"] == pid and its for p, its in grouped()):
        raise ValueError("ย้ายหรือลบคลิปในเพลย์ลิสต์นี้ออกก่อน แล้วค่อยลบเพลย์ลิสต์")
    data["playlists"] = [p for p in data["playlists"] if p["id"] != pid]
    data["assign"] = {k: v for k, v in data["assign"].items() if v != pid}
    _save(data)


def move(key: str, pid: str) -> None:
    data = load()
    _find(data, pid)
    if not any(it["key"] == key for it in items()):
        raise KeyError(key)
    data["assign"][key] = pid
    _save(data)
