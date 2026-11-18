"""Red thread v2, unattended: wait until the Gemini TTS daily quota has reset (>= 3 requests left), voice the story with a FEMALE narrator (Kore, 3 chunks), equalise,
split per scene, beat timestamps, transcription check, render every scene, assemble, QA metrics, back up the old library video and file the new one (EP10, playlist "รู้หรือไม่").
Everything is logged to auto_rt_log.txt (ends with DONE). Run detached."""
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "shorts"))
sys.path.insert(0, str(HERE.parents[3] / "src"))
import gemini_guard  # noqa: E402

LOG = HERE / "auto_rt_log.txt"
STORY, SCRIPT, PREFIX = "red_thread", "know_red_thread.json", "rt"
ENV = {**os.environ, "PYTHONIOENCODING": "utf-8"}
ENV.pop("VOICE_F0", None)


def log(*a):
    with LOG.open("a", encoding="utf-8") as f:
        print(time.strftime("%Y-%m-%d %H:%M:%S"), *a, file=f, flush=True)


def run(cmd, *extra, timeout=None):
    log("RUN", cmd)
    p = subprocess.run([sys.executable, "-u", "voice_story.py", STORY, SCRIPT, PREFIX, cmd, *extra], cwd=HERE, capture_output=True, text=True, encoding="utf-8", env=ENV, timeout=timeout)
    out = "\n".join(l for l in (p.stdout + p.stderr).splitlines() if "Direct use of automatic function calling" not in l)
    log(out[-2500:])
    return out


log("waiting for the quota reset; TTS used today", gemini_guard.used_today("tts"), "of", gemini_guard.limit_for("tts"))
while gemini_guard.limit_for("tts") - gemini_guard.used_today("tts") < 3:
    time.sleep(60)
log("quota day", gemini_guard._today(), "used", gemini_guard.used_today("tts"))
time.sleep(20)
aud = HERE / STORY / "audio"
for attempt in range(3):
    run("synth", "Kore")
    if all((aud / f"chunk{i}_raw.wav").is_file() and (aud / f"chunk{i}_raw.wav").stat().st_mtime > time.time() - 3 * 3600 for i in (1, 2, 3)):
        break
    log("a chunk is missing, retrying in 10 minutes")
    time.sleep(600)
else:
    log("STOP: voicing failed")
    sys.exit(1)
run("match")
run("split")
run("marks")
run("check")

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
# back up the video that is in the library now, then file the new one in place
vids = HERE.parents[2] / "cartoon_storyboard" / "output" / "videos"
old = next(vids.glob("EP10 - *"), None)
if old is not None:
    src = next(old.glob("*.mp4"), None)
    if src is not None:
        shutil.copyfile(src, HERE / STORY / "renders" / "red_thread_library_backup_before_v2.mp4")
p = subprocess.run([sys.executable, "add_to_library.py", str(mp4), "ด้ายแดง ที่ไม่มีใครมองเห็น", "เรื่องเล่าจากตำนานด้ายแดง: ต้ากับปิ่นนั่งห้องเดียวกันมาสามปีโดยไม่รู้ชื่อกัน (ผู้เล่าเสียงผู้หญิงคนเดียว)",
                    "ความสัมพันธ์และความเชื่อ", str(HERE / "covers_tmp" / "cover_rt.png"), "ด้ายแดง\nที่ไม่มีใครมองเห็น", "รู้หรือไม่"], cwd=HERE, env=ENV, capture_output=True, text=True, encoding="utf-8")
log("library:", (p.stdout + p.stderr)[-300:].replace("\n", " | "))
log("DONE")
