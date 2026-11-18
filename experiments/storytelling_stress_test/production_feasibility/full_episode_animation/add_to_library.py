"""File a finished MP4 in the cartoon-storyboard library (experiments/cartoon_storyboard/output/videos/EPxx - <title>/), the same layout
render.py uses, so preview.py lists, plays, renames and deletes it like any other episode.

    python add_to_library.py <mp4> "<title>" "<topic>" "<theme>" <cover.png> "<cover text>" [playlist name]

Writes: the MP4, info.json, cover_base.jpg (the given still, no text), a 1920x1080 cover.jpg = that still plus the Thai cover text (drawn locally by
covers.render, so the look is the same after a text edit in the library), a cover.json with a single plain concept and "base" set (so the cover editor opens
and keeps the picture), and files the episode in the given playlist (created if missing, 16:9).
If a folder with the same title exists it is updated in place (same EP number), so re-running never adds duplicates.
"""
import json
import shutil
import sys
import uuid
from pathlib import Path

import subprocess

from PIL import Image

HERE = Path(__file__).resolve().parent
CS = HERE.parents[2] / "cartoon_storyboard"
sys.path.insert(0, str(CS))
sys.path.insert(0, str(HERE.parents[3] / "src"))
sys.path.insert(0, str(HERE.parents[2] / "shorts"))
import library  # noqa: E402
import playlists  # noqa: E402
import covers  # noqa: E402


def duration_of(mp4):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(mp4)], capture_output=True, text=True)
    return float(out.stdout.strip())


def add(mp4, title, topic, theme, cover_png, cover_text, playlist="เรื่องเล่าการ์ตูน (ต้นแบบ)"):
    mp4 = Path(mp4)
    existing = next((e for e in library.episodes() if e["title"] == library.safe_title(title)), None)
    episode_id = existing["episode_id"] if existing else uuid.uuid4().hex
    dest = library.target_for(episode_id, title)
    shutil.copyfile(mp4, dest)
    library.write_info(dest, episode_id, title, topic, theme, duration_of(mp4))
    folder = dest.parent
    # the picture is kept WITHOUT text as cover_base.jpg; covers.set_base draws the title on it, and every later text edit in the library keeps this picture
    covers.set_base(folder.name, Image.open(cover_png).convert("RGB"), cover_text)
    data = playlists.load()
    pl = next((p for p in data["playlists"] if p["name"] == playlist), None) or playlists.add(playlist, "16:9")
    playlists.move(f"ep:{episode_id}", pl["id"])
    print("filed:", folder.name, "->", playlist)
    return folder


if __name__ == "__main__":
    a = sys.argv[1:]
    add(*a)
