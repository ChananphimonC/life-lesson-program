"""Waits for the Gemini TTS daily quota to reset (guard day changes), then voices both stories with the male narrator, one request per chunk, and prepares the audio
(pitch/loudness match, per-scene split, beat timestamps, transcription check). Everything is logged to auto_voice_log.txt. Run detached."""
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "shorts"))
sys.path.insert(0, str(HERE.parents[3] / "src"))
import gemini_guard  # noqa: E402

LOG = HERE / "auto_voice_log.txt"


def log(*a):
    with LOG.open("a", encoding="utf-8") as f:
        print(time.strftime("%H:%M:%S"), *a, file=f, flush=True)


def run(story, script, prefix, cmd, *extra):
    log("RUN", story, cmd)
    p = subprocess.run([sys.executable, "-u", "voice_story.py", story, script, prefix, cmd, *extra], cwd=HERE, capture_output=True, text=True, encoding="utf-8",
                       env={**__import__("os").environ, "PYTHONIOENCODING": "utf-8"})
    out = "\n".join(l for l in (p.stdout + p.stderr).splitlines() if "Direct use of automatic function calling" not in l)
    log(out[-3000:])
    return p.returncode


log("waiting for the quota reset; used today:", gemini_guard.used_today("tts"), "limit", gemini_guard.limit_for("tts"))
while gemini_guard.used_today("tts") >= gemini_guard.limit_for("tts"):
    time.sleep(60)
log("quota day", gemini_guard._today(), "used", gemini_guard.used_today("tts"))
time.sleep(30)
for story, script, prefix in (("robot_world", "know_robot_world.json", "rw"), ("red_thread", "know_red_thread.json", "rt")):
    run(story, script, prefix, "synth", "Algenib")
    run(story, script, prefix, "match")
    run(story, script, prefix, "split")
    run(story, script, prefix, "marks")
    run(story, script, prefix, "check")
log("DONE")
