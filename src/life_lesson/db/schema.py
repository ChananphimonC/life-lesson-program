"""SQLite schema (REQUIREMENTS.md §1: episodes, topics, scripts,
prompt_versions, generation_attempts -- the minimum tables needed to
resume or diagnose a failed generation).

v0.1 episode states: DRAFT -> TOPIC -> SCRIPT -> AUDIO -> VIDEO -> DONE,
plus a generic FAILED state for technical errors at any step. The wider
state machine in REQUIREMENTS.md (CRITIC_REVIEW, SUBTITLES, HUMAN_REVIEW,
PUBLISHED, FAILED_REVIEW) is reserved for v0.2+/v0.3 and not enforced yet;
the `state` column is a free-form TEXT column so later milestones can add
those states without a migration.
"""

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS topics (
    id TEXT PRIMARY KEY,
    theme TEXT,
    text TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'created',
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS episodes (
    id TEXT PRIMARY KEY,
    topic_id TEXT NOT NULL REFERENCES topics(id),
    state TEXT NOT NULL DEFAULT 'DRAFT',
    audio_path TEXT,
    video_path TEXT,
    error_message TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS prompt_versions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    stage TEXT NOT NULL,
    version TEXT NOT NULL,
    template TEXT NOT NULL,
    created_at TEXT NOT NULL,
    UNIQUE(name, version)
);

CREATE TABLE IF NOT EXISTS scripts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    episode_id TEXT NOT NULL REFERENCES episodes(id),
    prompt_version_id INTEGER NOT NULL REFERENCES prompt_versions(id),
    raw_json TEXT NOT NULL,
    validated INTEGER NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS generation_attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    episode_id TEXT NOT NULL REFERENCES episodes(id),
    stage TEXT NOT NULL,
    attempt_number INTEGER NOT NULL,
    status TEXT NOT NULL,
    error_message TEXT,
    raw_response TEXT,
    created_at TEXT NOT NULL
);
"""
