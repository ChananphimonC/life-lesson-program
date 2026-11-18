"""Red thread v2, second half only (the voice is done and the beat times are fixed): render every scene, assemble, QA metrics, back up the library video, file EP10.
Log: auto_rt_finish_log.txt (ends with DONE). Run detached."""
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
LOG = HERE / "auto_rt_finish_log.txt"
STORY, PREFIX = "red_thread", "rt"
ENV = {**os.environ, "PYTHONIOENCODING": "utf-8"}


def log(*a):
    with LOG.open("a", encoding="utf-8") as f:
        print(time.strftime("%Y-%m-%d %H:%M:%S"), *a, file=f, flush=True)


env = {**ENV, "EPISODE_ORDER": ",".join(f"{PREFIX}{i}" for i in range(1, 8)), "EPISODE_DIR": str(HERE / STORY), "STORY_PREFIX": PREFIX, "STORY_OUT": "red_thread_episode.mp4"}
for f in (HERE / STORY / "scenes").glob("*.mp4"):
    f.unlink()
t0 = time.time()
p = subprocess.run([sys.executable, "-u", "episode.py", "frames"], cwd=HERE, env=env, capture_output=True, text=True, encoding="utf-8")
log("render", round(time.time() - t0), "s;", (p.stdout + p.stderr)[-600:].replace("\n", " | "))
p = subprocess.run([sys.executable, "-u", "robot_assemble.py"], cwd=HERE, env=env, capture_output=True, text=True, encoding="utf-8")
log("assemble:", (p.stdout + p.stderr)[-400:].replace("\n", " | "))
mp4 = HERE / STORY / "renders" / "red_thread_episode.mp4"
qa_env = {**env, "QA_MP4": str(mp4), "QA_OUT": str(HERE / STORY / "qa_v2")}
p = subprocess.run([sys.executable, "-u", "qa.py"], cwd=HERE, env=qa_env, capture_output=True, text=True, encoding="utf-8")
log("qa done", (p.stdout + p.stderr)[-200:].replace("\n", " | "))
vids = HERE.parents[2] / "cartoon_storyboard" / "output" / "videos"
old = next(vids.glob("EP10 - *"), None)
backup = HERE / STORY / "renders" / "red_thread_library_backup_before_v2.mp4"
if old is not None and not backup.exists():
    src = next(old.glob("*.mp4"), None)
    if src is not None:
        shutil.copyfile(src, backup)
p = subprocess.run([sys.executable, "add_to_library.py", str(mp4), "ด้ายแดง ที่ไม่มีใครมองเห็น", "เรื่องเล่าจากตำนานด้ายแดง: ต้ากับปิ่นนั่งห้องเดียวกันมาสามปีโดยไม่รู้ชื่อกัน (ผู้เล่าเสียงผู้หญิงคนเดียว)",
                    "ความสัมพันธ์และความเชื่อ", str(HERE / "covers_tmp" / "cover_rt.png"), "ด้ายแดง\nที่ไม่มีใครมองเห็น", "รู้หรือไม่"], cwd=HERE, env=ENV, capture_output=True, text=True, encoding="utf-8")
log("library:", (p.stdout + p.stderr)[-300:].replace("\n", " | "))
log("DONE")
