import sqlite3

import pytest

from life_lesson.db import repository as repo


def _ep(conn, title="เรื่อง"):
    tid = repo.create_topic(conn, "t")
    eid = repo.create_episode(conn, tid)
    repo.update_episode_meta(conn, eid, title=title, format="long")
    return eid


def test_existing_v01_database_is_migrated(tmp_path):
    db = tmp_path / "old.db"
    conn = sqlite3.connect(db)
    conn.executescript("""
        CREATE TABLE topics (id TEXT PRIMARY KEY, theme TEXT, text TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'created', created_at TEXT NOT NULL);
        CREATE TABLE episodes (id TEXT PRIMARY KEY, topic_id TEXT NOT NULL, state TEXT NOT NULL DEFAULT 'DRAFT',
            audio_path TEXT, video_path TEXT, error_message TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL);
        INSERT INTO topics VALUES ('t','x','y','created','now');
        INSERT INTO episodes (id, topic_id, created_at, updated_at) VALUES ('e1','t','now','now');
    """)
    conn.commit(); conn.close()
    with repo.open_db(db) as c:
        row = repo.get_episode(c, "e1")
        assert row["kind"] == "episode" and row["title"] is None


def test_update_meta_and_unknown_field(tmp_path):
    with repo.open_db(tmp_path / "t.db") as c:
        eid = _ep(c)
        assert repo.get_episode(c, eid)["title"] == "เรื่อง"
        with pytest.raises(ValueError):
            repo.update_episode_meta(c, eid, bogus="x")


def test_find_episode_by_prefix_and_list_filters(tmp_path):
    with repo.open_db(tmp_path / "t.db") as c:
        a, b = _ep(c, "A"), _ep(c, "B")
        repo.update_episode_meta(c, b, kind="short", parent_episode_id=a)
        assert repo.find_episode(c, a[:8])["id"] == a
        assert repo.find_episode(c, "zzzz") is None
        assert [r["title"] for r in repo.list_episodes(c, kind="short")] == ["B"]
        assert [r["id"] for r in repo.child_shorts(c, a)] == [b]


def test_playlists_ordering_and_delete_keeps_episodes(tmp_path):
    with repo.open_db(tmp_path / "t.db") as c:
        a, b = _ep(c, "A"), _ep(c, "B")
        pid = repo.create_playlist(c, "Shorts", "folder")
        assert repo.create_playlist(c, "Shorts") == pid  # idempotent by name
        repo.add_to_playlist(c, pid, b); repo.add_to_playlist(c, pid, a); repo.add_to_playlist(c, pid, a)
        assert [r["title"] for r in repo.list_episodes(c, playlist_id=pid)] == ["B", "A"]
        assert repo.list_playlists(c)[0]["n"] == 2
        repo.remove_from_playlist(c, pid, b)
        repo.rename_playlist(c, pid, "Short clips")
        assert repo.find_playlist(c, "Short clips")["id"] == pid
        repo.delete_playlist(c, pid)
        assert repo.get_episode(c, a) is not None and repo.list_playlists(c) == []


def test_delete_episode_record_cascades(tmp_path):
    with repo.open_db(tmp_path / "t.db") as c:
        a = _ep(c)
        pid = repo.create_playlist(c, "P"); repo.add_to_playlist(c, pid, a)
        repo.log_generation_attempt(c, a, "script", 1, "success")
        repo.delete_episode_record(c, a)
        assert repo.get_episode(c, a) is None
        assert c.execute("SELECT COUNT(*) FROM playlist_items").fetchone()[0] == 0
        assert c.execute("SELECT COUNT(*) FROM generation_attempts").fetchone()[0] == 0
