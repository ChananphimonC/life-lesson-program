import json
import shutil
import subprocess
import wave

import pytest
from PIL import Image

from life_lesson.db import repository as repo
from life_lesson.errors import PipelineError
from life_lesson.library import cli, legacy

from .test_library_service import _episode, _settings

needs_ffmpeg = pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="no ffmpeg")


def _with_cover(st, eid):
    with repo.open_db(st.db_path) as c:
        row = repo.get_episode(c, eid)
        png = st.output_dir / "publish" / eid / "thumbnail.png"
        img = Image.new("RGB", (1920, 1080))
        px = img.load()
        for x in range(0, 1920, 3):          # noisy art: forces JPEG quality search
            for y in range(0, 1080, 3):
                px[x, y] = ((x * 7) % 255, (y * 13) % 255, (x + y) % 255)
        img.save(png)
        (png.parent / "thumbnail.json").write_text(json.dumps({"headline_line1": "ชั้นห้า", "headline_line2": "เสียงเคาะ"}), encoding="utf-8")
        repo.update_episode_meta(c, eid, thumbnail_path=str(png))
        assert row["id"] == eid


def test_safe_title_matches_the_owner_rule():
    assert legacy.safe_title('ชั้นห้า: เสียง/เคาะ?  ') == "ชั้นห้า เสียงเคาะ"
    assert legacy.safe_title("???") == "untitled" and len(legacy.safe_title("ก" * 200)) == 80


def test_episode_goes_into_the_ep_layout_with_info_and_small_cover(tmp_path):
    st = _settings(tmp_path)
    eid, vid, _ = _episode(st)
    _with_cover(st, eid)
    videos = tmp_path / "lib" / "videos"
    (videos / "EP05 - เรื่องเก่า").mkdir(parents=True)
    with repo.open_db(st.db_path) as c:
        folder = legacy.export_episode(st, c, eid, videos_dir=videos)
    assert folder.name == "EP06 - ชั้นห้าเสียงเคาะ"          # next number after EP05
    assert (folder / f"{folder.name}.mp4").read_bytes() == b"mp4"
    info = json.loads((folder / "info.json").read_text(encoding="utf-8"))
    assert info["ep"] == 6 and info["episode_id"] == eid and info["title"] == "ชั้นห้าเสียงเคาะ"
    assert set(info) >= {"ep", "title", "episode_id", "topic", "theme", "duration", "rendered_at"}
    cover = folder / "cover.jpg"
    assert cover.stat().st_size <= legacy.MAX_COVER_BYTES and Image.open(cover).size == (1920, 1080)
    assert json.loads((folder / "cover.json").read_text(encoding="utf-8"))["text"] == ["ชั้นห้า", "เสียงเคาะ"]


def test_exporting_twice_updates_in_place_not_ep_plus_one(tmp_path):
    st = _settings(tmp_path)
    eid, *_ = _episode(st)
    videos = tmp_path / "videos"
    with repo.open_db(st.db_path) as c:
        a = legacy.export_episode(st, c, eid, videos_dir=videos)
        b = legacy.export_episode(st, c, eid, videos_dir=videos)
    assert a == b and len(list(videos.iterdir())) == 1


def test_wrong_kind_is_refused(tmp_path):
    st = _settings(tmp_path)
    eid, *_ = _episode(st)
    with repo.open_db(st.db_path) as c:
        with pytest.raises(PipelineError, match="full episode"):
            legacy.export_short(st, c, eid, shorts_dir=tmp_path / "s")
        repo.update_episode_meta(c, eid, kind="short")
        with pytest.raises(PipelineError, match="Short"):
            legacy.export_episode(st, c, eid, videos_dir=tmp_path / "v")


@needs_ffmpeg
def test_short_goes_into_the_shorts_layout_with_audio_wav(tmp_path):
    st = _settings(tmp_path)
    eid, vid, _ = _episode(st)
    subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i", "testsrc2=s=160x284:d=3:r=10", "-f", "lavfi", "-i", "sine=f=300:d=3",
                    "-shortest", "-pix_fmt", "yuv420p", str(vid)], check=True, capture_output=True)
    with repo.open_db(st.db_path) as c:
        repo.update_episode_meta(c, eid, kind="short", title="ฮุกสั้น")
        folder = legacy.export_short(st, c, eid, shorts_dir=tmp_path / "shorts")
    assert folder.name == eid and (folder / "short.mp4").is_file()
    assert json.loads((folder / "meta.json").read_text(encoding="utf-8")) == {"title": "ฮุกสั้น"}
    with wave.open(str(folder / "audio.wav")) as w:   # the owner's library reads the length from this file
        assert abs(w.getnframes() / w.getframerate() - 3) < 0.3


def test_cli_asks_for_the_right_directory(tmp_path, monkeypatch, capsys):
    st = _settings(tmp_path)
    eid, *_ = _episode(st)
    monkeypatch.setattr(cli, "get_settings", lambda: st)
    assert cli.main(["export-legacy", eid[:8]]) == 2
    assert "--videos-dir" in capsys.readouterr().err
    assert cli.main(["export-legacy", eid[:8], "--videos-dir", str(tmp_path / "v")]) == 0
