"""Waits for the Gemini TTS quota reset, then auditions three deeper male voices with the same excited fairy-tale passage and measures them (pitch range, ASR check).
Results: robot_world/audition/<Voice>.wav and auto_audition_log.txt."""
import os
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "shorts"))
sys.path.insert(0, str(HERE.parents[3] / "src"))
import gemini_guard  # noqa: E402

LOG = HERE / "auto_audition_log.txt"
VOICES = ["Orus", "Algenib", "Charon"]


def log(*a):
    with LOG.open("a", encoding="utf-8") as f:
        print(time.strftime("%H:%M:%S"), *a, file=f, flush=True)


log("waiting for the quota reset")
while gemini_guard.used_today("tts") >= gemini_guard.limit_for("tts"):
    time.sleep(60)
time.sleep(10)
env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
rb = HERE / "robot_world"
p = subprocess.run([sys.executable, "-u", "audition.py", *VOICES], cwd=rb, env=env, capture_output=True, text=True, encoding="utf-8")
log("audition:", "\n".join(l for l in (p.stdout + p.stderr).splitlines() if "Direct use" not in l)[-1500:])
done = [v for v in VOICES if (rb / "audition" / f"{v}.wav").is_file()]
p = subprocess.run([sys.executable, "-u", "analyze_audition.py", *done], cwd=rb, env=env, capture_output=True, text=True, encoding="utf-8")
log("analysis:", "\n".join(l for l in (p.stdout + p.stderr).splitlines() if "Direct use" not in l and "transient" not in l)[-2500:])
log("DONE")
