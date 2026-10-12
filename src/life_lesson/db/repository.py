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

from life_lesson.db.schema import SCHEMA_SQL


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
