import json
import shutil
import subprocess
from pathlib import Path

import pytest
from PIL import Image

from life_lesson.config import Settings
from life_lesson.db import repository as repo
from life_lesson.errors import PipelineError
from life_lesson.library import cli, service
from life_lesson.publish.fonts import find_thai_font

from .test_shorts import _script, _timeline

needs_all = pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="needs ffmpeg")


def _settings(tmp_path) -> Settings:
    return Settings(
        gemini_api_key="k", gemini_script_model="m", gemini_tts_model="tts", gemini_tts_voice="Kore",
        db_path=tmp_path / "t.db", background_video_dir=tmp_path / "bg", output_dir=tmp_path / "out",
        ffmpeg_binary="ffmpeg", log_level="INFO", export_dir=tmp_path / "out" / "export",
        credits_file=tmp_path / "credits.txt", visual_mode="stock")


def _episode(settings, *, video=True, title="ชั้นห้า/เสียง:เคาะ"):
    """A finished episode as the pipeline leaves it: rows, script, files, timeline."""
    script = _script([2, 3, 3, 4, 4, 5, 5, 3, 2])
    starts, total = _timeline(script, 12_000)
    with repo.open_db(settings.db_path) as conn:
        tid = repo.create_topic(conn, "x")
        eid = repo.create_episode(conn, tid)
        pdir = settings.output_dir / "publish" / eid
        pdir.mkdir(parents=True)
        (pdir / "timeline.json").write_text(json.dumps({"block_starts_ms": starts, "duration_ms": total}))
        (pdir / "thumbnail.png").write_bytes(b"old")
        vid = settings.video_output_dir / f"{eid}.mp4"
        vid.parent.mkdir(parents=True, exist_ok=True)
        if video:
            vid.write_bytes(b"mp4")
        settings.audio_output_dir.mkdir(parents=True, exist_ok=True)
        (settings.audio_output_dir / f"{eid}.wav").write_bytes(b"w")
        repo.save_script(conn, eid, repo.register_prompt_version(conn, "s", "script", "v", "t"), script.model_dump_json(), True)
        repo.update_episode_state(conn, eid, "DONE", video_path=str(vid), audio_path=str(settings.audio_output_dir / f"{eid}.wav"))
        repo.update_episode_meta(conn, eid, title=title, format="long", publish_dir=str(pdir))
    return eid, vid, pdir


def test_export_makes_safe_unique_filenames(tmp_path):
    st = _settings(tmp_path); eid, vid, _ = _episode(st)
    with repo.open_db(st.db_path) as c:
        a = service.export_mp4(st, c, eid[:8])
        b = service.export_mp4(st, c, eid)
        assert a.name == "ชั้นห้าเสียงเคาะ.mp4" and b.name == "ชั้นห้าเสียงเคาะ_2.mp4"
        assert a.read_bytes() == b"mp4"
        assert service.export_mp4(st, c, eid, dest_dir=tmp_path / "usb", name="my clip").parent == tmp_path / "usb"


def test_export_without_video_is_a_clear_error(tmp_path):
    st = _settings(tmp_path); eid, *_ = _episode(st, video=False)
    with repo.open_db(st.db_path) as c, pytest.raises(PipelineError, match="no video"):
        service.export_mp4(st, c, eid)


def test_delete_removes_files_and_rows_but_stays_inside_output(tmp_path):
    st = _settings(tmp_path); eid, vid, pdir = _episode(st)
    outside = tmp_path / "keepme.mp4"; outside.write_bytes(b"precious")
    with repo.open_db(st.db_path) as c:
        c.execute("UPDATE episodes SET audio_path = ? WHERE id = ?", (str(outside), eid)); c.commit()
        removed = service.delete_episode(st, c, eid)
        assert vid in removed and pdir in removed
        assert outside.exists()  # outside the output folder: never touched
        assert not vid.exists() and not pdir.exists()
        assert repo.get_episode(c, eid) is None


def test_delete_keep_files_and_confirmation_rules(tmp_path):
    st = _settings(tmp_path); eid, vid, _ = _episode(st)
    with repo.open_db(st.db_path) as c:
        service.delete_episode(st, c, eid, keep_files=True)
        assert vid.exists() and repo.get_episode(c, eid) is None


def test_cli_delete_needs_yes(tmp_path, monkeypatch, capsys):
    st = _settings(tmp_path); eid, vid, _ = _episode(st)
    monkeypatch.setattr(cli, "get_settings", lambda: st)
    assert cli.main(["delete", eid[:8]]) == 2 and vid.exists()
    assert cli.main(["delete", eid[:8], "--yes"]) == 0 and not vid.exists()


def test_parent_with_shorts_is_protected(tmp_path):
    st = _settings(tmp_path); eid, *_ = _episode(st)
    with repo.open_db(st.db_path) as c:
        row = repo.get_episode(c, eid)
        sid = repo.create_episode(c, row["topic_id"])
        repo.update_episode_meta(c, sid, kind="short", parent_episode_id=eid)
        with pytest.raises(PipelineError, match="Short"):
            service.delete_episode(st, c, eid)
        service.delete_episode(st, c, eid, with_shorts=True)
        assert repo.get_episode(c, sid) is None and repo.get_episode(c, eid) is None


def test_description_rebuild_has_chapters_credits_and_channel(tmp_path):
    st = _settings(tmp_path); eid, _, pdir = _episode(st)
    st.credits_file.write_text("วิดีโอพื้นหลัง: ตัวอย่าง (CC0)\n", encoding="utf-8")
    with repo.open_db(st.db_path) as c:
        # give chapters so the list renders
        raw = json.loads(repo.get_latest_script_json(c, eid))
        for i, b in enumerate(raw["script_blocks"]):
            b["chapter_title"] = f"บท {i}"
        repo.save_script(c, eid, 1, json.dumps(raw), True)
        out = service.rebuild_description(st, c, eid)
    text = out.read_text(encoding="utf-8")
    assert "0:00 บท 0" in text and "@SakidJai_สะกิดใจ" in text and "(CC0)" in text and "สร้างด้วย AI" in text


@pytest.mark.skipif(not (shutil.which("ffmpeg")), reason="needs ffmpeg")
def test_edit_cover_text_and_keep_a_backup(tmp_path):
    try:
        find_thai_font()
    except PipelineError:
        pytest.skip("no Thai font")
    st = _settings(tmp_path); eid, vid, pdir = _episode(st)
    with repo.open_db(st.db_path) as c:
        out = service.regenerate_thumbnail(st, c, eid, title="ชื่อใหม่ ของตอน", tag="คืนนี้ · 23:47", subline="เสียงที่ไม่มีใครตอบ")
        assert Image.open(out).size == (1920, 1080)
        assert (pdir / "thumbnail.prev.png").read_bytes() == b"old"
        spec = json.loads((pdir / "thumbnail.json").read_text(encoding="utf-8"))
        assert spec["headline_line1"] == "ชื่อใหม่" and spec["context_tag"] == "คืนนี้ · 23:47"
        assert repo.get_episode(c, eid)["title"] == "ชื่อใหม่ ของตอน"


@needs_all
def test_create_short_from_real_episode_registers_it_in_the_shorts_folder(tmp_path):
    try:
        find_thai_font()
    except PipelineError:
        pytest.skip("no Thai font")
    st = _settings(tmp_path); eid, vid, _ = _episode(st)
    subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i", "testsrc2=s=640x360:d=110:r=15", "-f", "lavfi",
                    "-i", "sine=f=300:d=110", "-shortest", "-pix_fmt", "yuv420p", str(vid)], check=True, capture_output=True)
    with repo.open_db(st.db_path) as c:
        res = service.create_short(st, c, eid, full_url="https://youtu.be/abc", width=360, height=640)
        assert res.video_path.is_file() and 30 < res.seconds < 60
        row = repo.get_episode(c, res.episode_id)
        assert row["kind"] == "short" and row["parent_episode_id"] == eid and row["state"] == "DONE"
        folder = repo.find_playlist(c, "Shorts")
        assert [r["id"] for r in repo.list_episodes(c, playlist_id=folder["id"])] == [res.episode_id]
        desc = (res.publish_dir / "description.txt").read_text(encoding="utf-8")
        assert "@SakidJai_สะกิดใจ" in desc and "https://youtu.be/abc" in desc and "#Shorts" in desc
        with pytest.raises(PipelineError, match="full episode"):
            service.create_short(st, c, res.episode_id)
        # the Short can be rebuilt/edited like any other library item
        assert service.rebuild_description(st, c, res.episode_id).is_file()


def test_playlist_cli_flow(tmp_path, monkeypatch, capsys):
    st = _settings(tmp_path); a, *_ = _episode(st); b, *_ = _episode(st, title="สอง")
    monkeypatch.setattr(cli, "get_settings", lambda: st)
    run = lambda *x: cli.main(list(x))
    assert run("playlist", "create", "ซีรีส์ 30 วัน") == 0
    assert run("playlist", "create", "Archive", "--folder") == 0
    assert run("playlist", "add", "ซีรีส์ 30 วัน", a[:8], b[:8]) == 0
    capsys.readouterr()
    assert run("list", "--playlist", "ซีรีส์ 30 วัน") == 0
    assert "ชั้นห้า" in capsys.readouterr().out
    assert run("playlist", "remove", "ซีรีส์ 30 วัน", a[:8]) == 0
    assert run("playlist", "rename", "ซีรีส์ 30 วัน", "ซีรีส์") == 0
    assert run("playlist", "delete", "ซีรีส์") == 2          # needs --yes
    assert run("playlist", "delete", "ซีรีส์", "--yes") == 0
    with repo.open_db(st.db_path) as c:
        assert repo.get_episode(c, a) is not None and repo.get_episode(c, b) is not None  # episodes survive
    assert run("playlist", "show", "nope") == 1
    assert run("show", "zzzz") == 1
