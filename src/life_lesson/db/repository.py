"""SQLite access layer. Deliberately plain `sqlite3` + small functions
(no ORM) -- REQUIREMENTS.md's "keep it lightweight" principle applies to
the whole MVP, not just the TTS layer.
"""

from __future__ import annotations

import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

from life_lesson.db.schema import EPISODE_LIBRARY_COLUMNS, SCHEMA_SQL


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_id() -> str:
    return uuid.uuid4().hex


def connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA_SQL)
    existing = {row["name"] for row in conn.execute("PRAGMA table_info(episodes)")}
    for column, ddl in EPISODE_LIBRARY_COLUMNS.items():
        if column not in existing:
            conn.execute(f"ALTER TABLE episodes ADD COLUMN {column} {ddl}")
    conn.commit()


@contextmanager
def open_db(db_path: Path) -> Iterator[sqlite3.Connection]:
    conn = connect(db_path)
    try:
        init_db(conn)
        yield conn
    finally:
        conn.close()


# -- topics ----------------------------------------------------------------

def create_topic(conn: sqlite3.Connection, text: str, theme: str | None = None) -> str:
    topic_id = new_id()
    conn.execute(
        "INSERT INTO topics (id, theme, text, status, created_at) VALUES (?, ?, ?, ?, ?)",
        (topic_id, theme, text, "created", _now()),
    )
    conn.commit()
    return topic_id


def set_topic_status(conn: sqlite3.Connection, topic_id: str, status: str) -> None:
    conn.execute("UPDATE topics SET status = ? WHERE id = ?", (status, topic_id))
    conn.commit()


# -- episodes ----------------------------------------------------------------

def create_episode(conn: sqlite3.Connection, topic_id: str) -> str:
    episode_id = new_id()
    now = _now()
    conn.execute(
        "INSERT INTO episodes (id, topic_id, state, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
        (episode_id, topic_id, "DRAFT", now, now),
    )
    conn.commit()
    return episode_id


def update_episode_state(
    conn: sqlite3.Connection,
    episode_id: str,
    state: str,
    *,
    audio_path: str | None = None,
    video_path: str | None = None,
    error_message: str | None = None,
) -> None:
    fields = ["state = ?", "updated_at = ?"]
    values: list[object] = [state, _now()]
    if audio_path is not None:
        fields.append("audio_path = ?")
        values.append(audio_path)
    if video_path is not None:
        fields.append("video_path = ?")
        values.append(video_path)
    if error_message is not None:
        fields.append("error_message = ?")
        values.append(error_message)
    values.append(episode_id)
    conn.execute(f"UPDATE episodes SET {', '.join(fields)} WHERE id = ?", values)
    conn.commit()


def get_episode(conn: sqlite3.Connection, episode_id: str) -> sqlite3.Row | None:
    cur = conn.execute("SELECT * FROM episodes WHERE id = ?", (episode_id,))
    return cur.fetchone()


# -- prompt versions ---------------------------------------------------------

def register_prompt_version(
    conn: sqlite3.Connection, name: str, stage: str, version: str, template: str
) -> int:
    cur = conn.execute(
        "SELECT id FROM prompt_versions WHERE name = ? AND version = ?", (name, version)
    )
    row = cur.fetchone()
    if row is not None:
        return int(row["id"])
    cur = conn.execute(
        "INSERT INTO prompt_versions (name, stage, version, template, created_at) "
        "VALUES (?, ?, ?, ?, ?)",
        (name, stage, version, template, _now()),
    )
    conn.commit()
    return int(cur.lastrowid)


# -- scripts -------------------------------------------------------------

def save_script(
    conn: sqlite3.Connection,
    episode_id: str,
    prompt_version_id: int,
    raw_json: str,
    validated: bool,
) -> int:
    cur = conn.execute(
        "INSERT INTO scripts (episode_id, prompt_version_id, raw_json, validated, created_at) "
        "VALUES (?, ?, ?, ?, ?)",
        (episode_id, prompt_version_id, raw_json, int(validated), _now()),
    )
    conn.commit()
    return int(cur.lastrowid)


# -- generation attempts ---------------------------------------------------

def log_generation_attempt(
    conn: sqlite3.Connection,
    episode_id: str,
    stage: str,
    attempt_number: int,
    status: str,
    *,
    error_message: str | None = None,
    raw_response: str | None = None,
) -> int:
    cur = conn.execute(
        "INSERT INTO generation_attempts "
        "(episode_id, stage, attempt_number, status, error_message, raw_response, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (episode_id, stage, attempt_number, status, error_message, raw_response, _now()),
    )
    conn.commit()
    return int(cur.lastrowid)


# -- library: episode metadata, listing, deletion ----------------------------

_META_FIELDS = ("title", "format", "kind", "parent_episode_id", "publish_dir", "thumbnail_path", "series")


def update_episode_meta(conn: sqlite3.Connection, episode_id: str, **fields: str | None) -> None:
    unknown = set(fields) - set(_META_FIELDS)
    if unknown:
        raise ValueError(f"unknown episode fields: {sorted(unknown)}")
    if not fields:
        return
    sets = ", ".join(f"{k} = ?" for k in fields) + ", updated_at = ?"
    conn.execute(
        f"UPDATE episodes SET {sets} WHERE id = ?", [*fields.values(), _now(), episode_id]
    )
    conn.commit()


def list_episodes(
    conn: sqlite3.Connection,
    *,
    kind: str | None = None,
    state: str | None = None,
    playlist_id: str | None = None,
) -> list[sqlite3.Row]:
    sql = "SELECT e.* FROM episodes e"
    where: list[str] = []
    args: list[object] = []
    if playlist_id:
        sql += " JOIN playlist_items pi ON pi.episode_id = e.id"
        where.append("pi.playlist_id = ?")
        args.append(playlist_id)
    if kind:
        where.append("e.kind = ?")
        args.append(kind)
    if state:
        where.append("e.state = ?")
        args.append(state)
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY " + ("pi.position" if playlist_id else "e.created_at DESC")
    return conn.execute(sql, args).fetchall()


def get_latest_script_json(conn: sqlite3.Connection, episode_id: str) -> str | None:
    row = conn.execute(
        "SELECT raw_json FROM scripts WHERE episode_id = ? AND validated = 1 "
        "ORDER BY id DESC LIMIT 1",
        (episode_id,),
    ).fetchone()
    return row["raw_json"] if row else None


def find_episode(conn: sqlite3.Connection, ref: str) -> sqlite3.Row | None:
    """Look up by full id or unique id prefix (so the CLI can take short ids)."""
    rows = conn.execute("SELECT * FROM episodes WHERE id LIKE ?", (ref + "%",)).fetchall()
    return rows[0] if len(rows) == 1 else None


def child_shorts(conn: sqlite3.Connection, episode_id: str) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT * FROM episodes WHERE parent_episode_id = ? ORDER BY created_at", (episode_id,)
    ).fetchall()


def delete_episode_record(conn: sqlite3.Connection, episode_id: str) -> None:
    """Remove an episode and everything that hangs off it (rows only)."""
    for table in ("generation_attempts", "scripts", "playlist_items"):
        conn.execute(f"DELETE FROM {table} WHERE episode_id = ?", (episode_id,))
    conn.execute("DELETE FROM episodes WHERE id = ?", (episode_id,))
    conn.commit()


# -- library: playlists / folders ---------------------------------------------

def create_playlist(conn: sqlite3.Connection, name: str, kind: str = "playlist") -> str:
    if kind not in ("playlist", "folder"):
        raise ValueError("kind must be 'playlist' or 'folder'")
    existing = conn.execute("SELECT id FROM playlists WHERE name = ?", (name,)).fetchone()
    if existing:
        return existing["id"]
    pid = new_id()
    conn.execute(
        "INSERT INTO playlists (id, name, kind, created_at) VALUES (?, ?, ?, ?)",
        (pid, name, kind, _now()),
    )
    conn.commit()
    return pid


def find_playlist(conn: sqlite3.Connection, ref: str) -> sqlite3.Row | None:
    row = conn.execute("SELECT * FROM playlists WHERE name = ?", (ref,)).fetchone()
    if row:
        return row
    rows = conn.execute("SELECT * FROM playlists WHERE id LIKE ?", (ref + "%",)).fetchall()
    return rows[0] if len(rows) == 1 else None


def list_playlists(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT p.*, (SELECT COUNT(*) FROM playlist_items i WHERE i.playlist_id = p.id) AS n "
        "FROM playlists p ORDER BY p.name"
    ).fetchall()


def add_to_playlist(conn: sqlite3.Connection, playlist_id: str, episode_id: str) -> None:
    pos = conn.execute(
        "SELECT COALESCE(MAX(position), 0) + 1 FROM playlist_items WHERE playlist_id = ?",
        (playlist_id,),
    ).fetchone()[0]
    conn.execute(
        "INSERT OR IGNORE INTO playlist_items (playlist_id, episode_id, position) VALUES (?, ?, ?)",
        (playlist_id, episode_id, pos),
    )
    conn.commit()


def remove_from_playlist(conn: sqlite3.Connection, playlist_id: str, episode_id: str) -> None:
    conn.execute(
        "DELETE FROM playlist_items WHERE playlist_id = ? AND episode_id = ?",
        (playlist_id, episode_id),
    )
    conn.commit()


def rename_playlist(conn: sqlite3.Connection, playlist_id: str, new_name: str) -> None:
    conn.execute("UPDATE playlists SET name = ? WHERE id = ?", (new_name, playlist_id))
    conn.commit()


def delete_playlist(conn: sqlite3.Connection, playlist_id: str) -> None:
    """Deletes the playlist/folder only -- never the episodes inside it."""
    conn.execute("DELETE FROM playlist_items WHERE playlist_id = ?", (playlist_id,))
    conn.execute("DELETE FROM playlists WHERE id = ?", (playlist_id,))
    conn.commit()
