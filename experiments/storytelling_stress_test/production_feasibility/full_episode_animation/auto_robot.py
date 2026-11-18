"""Robot episode, after the narration fix: split -> marks -> check -> render all scenes -> assemble. Log: auto_robot_log.txt (ends with DONE)."""
import os
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
LOG = HERE / "auto_robot_log.txt"


def log(*a):
    with LOG.open("a", encoding="utf-8") as f:
        f.write(time.strftime("%H:%M:%S ") + " ".join(str(x) for x in a) + "\n")


env = {**os.environ, "PYTHONIOENCODING": "utf-8", "VOICE_F0": "122"}
for sub in ("marks",):
    log("RUN", sub)
    p = subprocess.run([sys.executable, "-u", "voice_story.py", "robot_world", "know_robot_world.json", "rw", sub], cwd=HERE, env=env, capture_output=True, text=True, encoding="utf-8")
    log((p.stdout + p.stderr)[-1800:])
renv = {**env, "EPISODE_ORDER": ",".join(f"rw{i}" for i in range(1, 8)), "EPISODE_DIR": str(HERE / "robot_world"), "STORY_PREFIX": "rw", "STORY_OUT": "robot_world_episode.mp4"}
for f in (HERE / "robot_world" / "scenes").glob("*.mp4"):
    f.unlink()
t0 = time.time()
p = subprocess.run([sys.executable, "-u", "episode.py", "frames"], cwd=HERE, env=renv, capture_output=True, text=True, encoding="utf-8")
log("render", round(time.time() - t0), "s;", (p.stdout + p.stderr)[-500:].replace("\n", " | "))
p = subprocess.run([sys.executable, "-u", "robot_assemble.py"], cwd=HERE, env=renv, capture_output=True, text=True, encoding="utf-8")
log("assemble:", (p.stdout + p.stderr)[-400:].replace("\n", " | "))
log("DONE")
