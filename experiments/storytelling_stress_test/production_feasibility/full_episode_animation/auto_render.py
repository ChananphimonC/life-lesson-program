"""After auto_voice.py has voiced both stories: render every scene of both stories, then assemble each MP4 (narration + sound effects). Logged to auto_render_log.txt.
It stops (and says why) if the audio is missing or older than this job, so a failed voicing never produces a silent or stale video."""
import os
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
LOG = HERE / "auto_render_log.txt"
VLOG = HERE / "auto_voice_log.txt"
START = time.time()


def log(*a):
    with LOG.open("a", encoding="utf-8") as f:
        print(time.strftime("%H:%M:%S"), *a, file=f, flush=True)


log("waiting for the voicing job")
while not (VLOG.is_file() and "DONE" in VLOG.read_text(encoding="utf-8")):
    time.sleep(30)
log("voicing finished")
for story, prefix, out in (("robot_world", "rw", "robot_world_episode.mp4"), ("red_thread", "rt", "red_thread_episode.mp4")):
    d = HERE / story / "audio"
    files = [d / f"r{i}.wav" for i in range(1, 8)]
    if not all(f.is_file() and f.stat().st_mtime > START - 6 * 3600 for f in files) or not (d / "timing.json").is_file():
        log("STOP: audio missing or stale for", story)
        continue
    env = {**os.environ, "EPISODE_ORDER": ",".join(f"{prefix}{i}" for i in range(1, 8)), "EPISODE_DIR": str(HERE / story), "PYTHONIOENCODING": "utf-8", "STORY_PREFIX": prefix,
           "STORY_OUT": out}
    for f in (HERE / story / "scenes").glob("*.mp4"):
        f.unlink()
    t0 = time.time()
    p = subprocess.run([sys.executable, "-u", "episode.py", "frames"], cwd=HERE, env=env, capture_output=True, text=True, encoding="utf-8")
    log(story, "render", round(time.time() - t0), "s;", (p.stdout + p.stderr)[-600:].replace("\n", " | "))
    p = subprocess.run([sys.executable, "-u", "robot_assemble.py"], cwd=HERE, env=env, capture_output=True, text=True, encoding="utf-8")
    log(story, "assemble:", (p.stdout + p.stderr)[-400:].replace("\n", " | "))
log("DONE")
