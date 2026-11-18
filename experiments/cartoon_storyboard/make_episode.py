"""Create an episode's script + narration for the cartoon renderer, with a
per-block TTS cache so a daily-quota stop can simply be resumed.

    python make_episode.py new "<topic>" --theme "<theme>"   # script, then voice
    python make_episode.py voice <episode_id>                 # (re)voice missing blocks
    python make_episode.py voice <id> [<id> ...] --render     # ...then render the cartoon MP4(s)

Uses the main pipeline's own script generation and Gemini TTS (free tier);
the stock-background MP4 step is skipped because render.py replaces it.
"""

from __future__ import annotations

import argparse
import hashlib
import sqlite3
import subprocess
import sys
from pathlib import Path

from life_lesson.audio.wav_utils import concatenate_with_silence
from life_lesson.config import get_settings
from life_lesson.db import repository as repo
from life_lesson.generation.schema import validate_script_json
from life_lesson.pipeline import _generate_and_persist_script
from life_lesson.tts.gemini_tts import GeminiTTSProvider

import library

CACHE = library.WORK_DIR / "tts"


def new(topic: str, theme: str | None) -> str:
    settings = get_settings()
    with repo.open_db(settings.db_path) as conn:
        topic_id = repo.create_topic(conn, topic, theme)
        episode_id = repo.create_episode(conn, topic_id)
        script = _generate_and_persist_script(conn, settings, episode_id, topic_id, topic, theme)
    print(f"episode_id: {episode_id}\ntitle: {script.title}")
    for b in script.script_blocks:
        print(f"\n[{b.sequence} {b.phase}] {b.text}")
    return episode_id


def voice(episode_id: str) -> bool:
    settings = get_settings()
    conn = sqlite3.connect(settings.db_path)
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT raw_json FROM scripts WHERE episode_id = ? AND validated = 1 "
                       "ORDER BY id DESC LIMIT 1", (episode_id,)).fetchone()
    if row is None:
        sys.exit(f"no validated script for {episode_id}")
    script = validate_script_json(row["raw_json"])
    folder = CACHE / episode_id
    folder.mkdir(parents=True, exist_ok=True)
    provider = None
    clips = []
    for b in script.script_blocks:
        digest = hashlib.sha1(b.text.encode("utf-8")).hexdigest()[:10]
        path = folder / f"block{b.sequence}-{digest}.wav"
        if not path.exists():
            provider = provider or GeminiTTSProvider(settings)
            try:
                path.write_bytes(provider.synthesize(b.text))
            except Exception as exc:  # quota (429) or a transient empty response
                print(f"block {b.sequence}: TTS stopped ({exc}). Re-run `python make_episode.py voice "
                      f"{episode_id}` later; finished blocks are kept.")
                return False
            print(f"block {b.sequence}: voiced")
        else:
            print(f"block {b.sequence}: cached")
        clips.append((path.read_bytes(), b.pause_after_ms))
    out = settings.audio_output_dir / f"{episode_id}.wav"
    concatenate_with_silence(clips, out)
    with repo.open_db(settings.db_path) as c2:
        repo.log_generation_attempt(c2, episode_id, "tts", 1, "success")
        repo.update_episode_state(c2, episode_id, "DONE", audio_path=str(out))
    print(f"audio: {out}")
    return True


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_new = sub.add_parser("new")
    p_new.add_argument("topic")
    p_new.add_argument("--theme")
    p_new.add_argument("--no-voice", action="store_true")
    p_voice = sub.add_parser("voice")
    p_voice.add_argument("episode_ids", nargs="+")
    p_voice.add_argument("--render", action="store_true", help="render the cartoon MP4 once voiced")
    args = parser.parse_args()
    if args.cmd == "new":
        ep = new(args.topic, args.theme)
        if not args.no_voice:
            voice(ep)
    else:
        for episode_id in args.episode_ids:
            if voice(episode_id) and args.render:
                subprocess.run([sys.executable, str(Path(__file__).with_name("render.py")), "--episode", episode_id],
                               check=True)


if __name__ == "__main__":
    main()
