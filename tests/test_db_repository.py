from life_lesson.db import repository as repo


def test_init_db_creates_tables(tmp_db_path):
    with repo.open_db(tmp_db_path) as conn:
        tables = {
            row["name"]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }
    assert {
        "topics",
        "episodes",
        "prompt_versions",
        "scripts",
        "generation_attempts",
    } <= tables


def test_create_topic_and_episode(tmp_db_path):
    with repo.open_db(tmp_db_path) as conn:
        topic_id = repo.create_topic(conn, "some situation", theme="falling behind")
        episode_id = repo.create_episode(conn, topic_id)

        episode = repo.get_episode(conn, episode_id)
        assert episode["topic_id"] == topic_id
        assert episode["state"] == "DRAFT"


def test_update_episode_state(tmp_db_path):
    with repo.open_db(tmp_db_path) as conn:
        topic_id = repo.create_topic(conn, "situation")
        episode_id = repo.create_episode(conn, topic_id)

        repo.update_episode_state(conn, episode_id, "SCRIPT")
        episode = repo.get_episode(conn, episode_id)
        assert episode["state"] == "SCRIPT"

        repo.update_episode_state(
            conn, episode_id, "FAILED", error_message="boom"
        )
        episode = repo.get_episode(conn, episode_id)
        assert episode["state"] == "FAILED"
        assert episode["error_message"] == "boom"


def test_register_prompt_version_is_idempotent(tmp_db_path):
    with repo.open_db(tmp_db_path) as conn:
        id1 = repo.register_prompt_version(conn, "script_generation", "script", "v1", "template text")
        id2 = repo.register_prompt_version(conn, "script_generation", "script", "v1", "template text")
        assert id1 == id2


def test_save_script_and_log_generation_attempt(tmp_db_path):
    with repo.open_db(tmp_db_path) as conn:
        topic_id = repo.create_topic(conn, "situation")
        episode_id = repo.create_episode(conn, topic_id)
        prompt_version_id = repo.register_prompt_version(
            conn, "script_generation", "script", "v1", "template"
        )

        script_id = repo.save_script(
            conn, episode_id, prompt_version_id, '{"foo": "bar"}', validated=True
        )
        assert script_id > 0

        attempt_id = repo.log_generation_attempt(
            conn, episode_id, "script", 1, "success"
        )
        assert attempt_id > 0

        row = conn.execute(
            "SELECT * FROM generation_attempts WHERE id = ?", (attempt_id,)
        ).fetchone()
        assert row["stage"] == "script"
        assert row["status"] == "success"
