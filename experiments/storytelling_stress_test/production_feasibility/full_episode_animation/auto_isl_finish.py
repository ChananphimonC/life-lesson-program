"""Island story: render every scene, assemble with the narrator + SFX, QA metrics, file the episode in the library (playlist รู้หรือไม่).
Log: auto_isl_finish_log.txt (ends with DONE). Run detached."""
import os
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
LOG = HERE / "auto_isl_finish_log.txt"
STORY, PREFIX = "island_72", "isl"
ENV = {**os.environ, "PYTHONIOENCODING": "utf-8"}
TITLE = "ถ้ามหาวิทยาลัยดัง ๆ ติดเกาะร้าง 72 ชั่วโมง"


def log(*a):
    with LOG.open("a", encoding="utf-8") as f:
        print(time.strftime("%Y-%m-%d %H:%M:%S"), *a, file=f, flush=True)


env = {**ENV, "EPISODE_ORDER": ",".join(f"{PREFIX}{i}" for i in range(1, 13)), "EPISODE_DIR": str(HERE / STORY), "STORY_PREFIX": PREFIX, "STORY_OUT": "island_72_episode.mp4"}
(HERE / STORY / "scenes").mkdir(exist_ok=True)
t0 = time.time()
sys.path.insert(0, str(HERE))


def dur_of(f):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(f)], capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return -1.0


import importlib  # noqa: E402
os.environ.update({k: env[k] for k in ("EPISODE_ORDER", "EPISODE_DIR")})
for i in range(1, 13):
    name = f"{PREFIX}{i}"
    f = HERE / STORY / "scenes" / f"{name}.mp4"
    want = importlib.import_module(name).DUR
    if f.is_file() and abs(dur_of(f) - want) < 0.3:
        log("skip (already rendered)", name)
        continue
    p = subprocess.run([sys.executable, "-u", "episode.py", "frames", name], cwd=HERE, env=env, capture_output=True, text=True, encoding="utf-8")
    log("render", name, round(time.time() - t0), "s;", (p.stdout + p.stderr)[-200:].replace("\n", " | "))
p = subprocess.run([sys.executable, "-u", "robot_assemble.py"], cwd=HERE, env=env, capture_output=True, text=True, encoding="utf-8")
log("assemble:", (p.stdout + p.stderr)[-400:].replace("\n", " | "))
mp4 = HERE / STORY / "renders" / "island_72_episode.mp4"
qa_env = {**env, "QA_MP4": str(mp4), "QA_OUT": str(HERE / STORY / "qa")}
p = subprocess.run([sys.executable, "-u", "qa.py"], cwd=HERE, env=qa_env, capture_output=True, text=True, encoding="utf-8")
log("qa done", (p.stdout + p.stderr)[-200:].replace("\n", " | "))
if os.environ.get("ISL_FILE", "1") == "1":
    p = subprocess.run([sys.executable, "add_to_library.py", str(mp4), TITLE, "ถ้านักศึกษาจากสิบมหาวิทยาลัยดัง ๆ ของไทยติดเกาะร้างเจ็ดสิบสองชั่วโมง (เรื่องแต่งสนุก ๆ ผู้เล่าเสียงผู้ชายคนเดียว)",
                        "เรื่องเล่าผจญภัย", str(HERE / "covers_tmp" / "cover_isl.png"), "ติดเกาะ 72 ชั่วโมง\nใครจะรอด?", "รู้หรือไม่"], cwd=HERE, env=ENV, capture_output=True, text=True, encoding="utf-8")
    log("library:", (p.stdout + p.stderr)[-300:].replace("\n", " | "))
log("DONE")
