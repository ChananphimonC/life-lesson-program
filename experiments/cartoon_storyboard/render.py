"""Render a cartoon-storyboard MP4 for an existing episode, reusing its
already-generated narration audio. No API calls.

    python render.py                    # latest storyboarded episode -> output/videos/EPxx - <title>/
    python render.py --episode <id>     # a specific episode
    python render.py --preview          # keyframe PNGs + contact sheet only (output/_work/preview)
"""

from __future__ import annotations

import argparse
import json
import math
import sqlite3
import subprocess
import sys
import time
from pathlib import Path

from PIL import Image

from life_lesson.config import get_settings

import library
import scenes as S
import scenes_ep02 as E2
import scenes_ep03 as E3
import scenes_ep04 as E4
import scenes_ep05 as E5
import scenes_ep06 as E6
import scenes_stickers as SS
from storyboard import STORYBOARDS
from timing import analyze

OUT_DIR = library.WORK_DIR
FPS = 24
XFADE = 0.7
FADE_IN, FADE_OUT = 0.6, 2.0


def load_episode(db_path: Path, episode_id: str):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    ep = conn.execute(
        "SELECT e.audio_path, t.text, t.theme FROM episodes e JOIN topics t ON t.id = e.topic_id WHERE e.id = ?",
        (episode_id,),
    ).fetchone()
    if ep is None or not ep["audio_path"]:
        sys.exit(f"episode {episode_id} has no audio")
    row = conn.execute(
        "SELECT raw_json FROM scripts WHERE episode_id = ? AND validated = 1 ORDER BY id DESC LIMIT 1",
        (episode_id,),
    ).fetchone()
    script = json.loads(row["raw_json"])
    return Path(ep["audio_path"]), script["script_blocks"], {"topic": ep["text"], "theme": ep["theme"],
                                                            "title": script.get("title") or ep["text"]}


def latest_voiced(db_path: Path) -> str:
    conn = sqlite3.connect(db_path)
    for episode_id in reversed(list(STORYBOARDS)):
        row = conn.execute("SELECT audio_path FROM episodes WHERE id = ?", (episode_id,)).fetchone()
        if row and row[0] and Path(row[0]).exists():
            return episode_id
    sys.exit("no storyboarded episode has narration audio yet")


def build_timeline(storyboard, timings, total):
    by_seq = {b.sequence: b for b in timings}
    entries = []
    for seq, scene_list in storyboard.items():
        block = by_seq[seq]
        for name, anchor, events in scene_list:
            if anchor:
                start = block.anchor_time(anchor) - 0.2
            else:
                start = 0.0 if not entries else block.speech_start - 0.25
            ev, last = {}, start + 0.3
            for k, v in events.items():
                last = max(block.anchor_time(v, max_snap=0.6), last + 0.45)
                ev[k] = round(last, 3)
            entries.append({"scene": name, "start": round(start, 3), "events": ev})
    for a, b in zip(entries, entries[1:]):
        if b["start"] <= a["start"] + 1.0:
            raise ValueError(f"scene {b['scene']} starts too soon after {a['scene']}")
    for i, e in enumerate(entries):
        e["end"] = entries[i + 1]["start"] if i + 1 < len(entries) else total
    return entries


def make_scenes(entries, style):
    library = SS.SCENES if style == "stickers" else {**S.SCENES, **E2.SCENES, **E3.SCENES, **E4.SCENES, **E5.SCENES, **E6.SCENES}
    return [library[e["scene"]](e["end"] - e["start"], {k: v - e["start"] for k, v in e["events"].items()})
            for e in entries]


def frame_at(t, entries, scene_objs, total):
    idx = max(i for i, e in enumerate(entries) if e["start"] <= t or i == 0)
    for j in range(max(0, idx - 2)):
        scene_objs[j].release()

    def local(i):
        return scene_objs[i].frame(t - entries[i]["start"])

    img = None
    if idx > 0 and t - entries[idx]["start"] < XFADE / 2:
        b = entries[idx]["start"]
        img = Image.blend(local(idx - 1), local(idx), (t - (b - XFADE / 2)) / XFADE)
    elif idx + 1 < len(entries) and entries[idx + 1]["start"] - t < XFADE / 2:
        b = entries[idx + 1]["start"]
        img = Image.blend(local(idx), local(idx + 1), (t - (b - XFADE / 2)) / XFADE)
    else:
        img = local(idx)

    fade = min(1.0, t / FADE_IN, (total - t) / FADE_OUT)
    if fade < 1.0:
        img = Image.blend(Image.new("RGB", img.size, (0, 0, 0)), img, max(0.0, fade))
    return img


def render_preview(entries, scene_objs, total):
    out = OUT_DIR / "preview"
    out.mkdir(parents=True, exist_ok=True)
    thumbs = []
    for i, e in enumerate(entries):
        dur = e["end"] - e["start"]
        for frac in (0.15, 0.55, 0.92):
            t = e["start"] + dur * frac
            img = frame_at(t, entries, scene_objs, total)
            small = img.resize((640, 360), Image.LANCZOS)
            small.save(out / f"{i + 1:02d}_{e['scene']}_{int(frac * 100):02d}.png")
            thumbs.append(small)
    cols = 3
    rows = math.ceil(len(thumbs) / cols)
    sheet = Image.new("RGB", (cols * 640, rows * 360), (0, 0, 0))
    for k, th in enumerate(thumbs):
        sheet.paste(th, ((k % cols) * 640, (k // cols) * 360))
    sheet.save(out / "contact_sheet.png")
    print(f"preview written to {out}")


def render_video(entries, scene_objs, total, audio_path, ffmpeg, out_path):
    n_frames = int(math.ceil(total * FPS))
    log_path = OUT_DIR / f"{out_path.stem}.ffmpeg.log"
    cmd = [ffmpeg, "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{S.OUT[0]}x{S.OUT[1]}",
           "-r", str(FPS), "-i", "-", "-i", str(audio_path), "-map", "0:v:0", "-map", "1:a:0",
           "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "160k", "-ar", "44100", "-shortest", "-movflags", "+faststart",
           str(out_path)]
    started = time.time()
    with open(log_path, "w") as log:
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=log)
        try:
            for f in range(n_frames):
                proc.stdin.write(frame_at(f / FPS, entries, scene_objs, total).tobytes())
                if f % (FPS * 10) == 0:
                    print(f"  {f / FPS:6.1f}s / {total:.1f}s  ({time.time() - started:.0f}s elapsed)", flush=True)
        finally:
            proc.stdin.close()
            code = proc.wait()
    if code != 0:
        sys.exit(f"ffmpeg failed ({code}); see {log_path}")
    print(f"video written to {out_path} in {time.time() - started:.0f}s")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--episode", default=None, help="default: latest storyboarded episode with audio")
    parser.add_argument("--preview", action="store_true")
    parser.add_argument("--style", choices=["stickers", "drawn"], default="drawn",
                        help="stickers = the illustration sheets; drawn = procedural character")
    args = parser.parse_args()

    settings = get_settings()
    if args.episode is None:
        args.episode = latest_voiced(settings.db_path)
    audio_path, blocks, meta = load_episode(settings.db_path, args.episode)
    timings, total = analyze(audio_path, blocks)
    entries = build_timeline(STORYBOARDS[args.episode], timings, total)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "timeline.json").write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")
    for e in entries:
        ev = ", ".join(f"{k}@{v:.2f}" for k, v in e["events"].items())
        print(f"{e['start']:7.2f}-{e['end']:7.2f}  {e['scene']:<16} {ev}")

    scene_objs = make_scenes(entries, args.style)
    if args.preview:
        render_preview(entries, scene_objs, total)
    else:
        out_path = library.target_for(args.episode, meta["title"])
        if args.style == "stickers":
            out_path = out_path.with_name(out_path.stem + " (stickers).mp4")
        render_video(entries, scene_objs, total, audio_path, settings.ffmpeg_binary, out_path)
        library.write_info(out_path, args.episode, meta["title"], meta["topic"], meta["theme"], total)
        try:
            import covers
            covers.ensure(out_path.parent.name)
            print(f"cover written to {out_path.parent / 'cover.jpg'}")
        except Exception as exc:  # the video is done either way; the cover can be made from preview.py
            print(f"cover skipped ({exc}); make it later in preview.py")


if __name__ == "__main__":
    main()
