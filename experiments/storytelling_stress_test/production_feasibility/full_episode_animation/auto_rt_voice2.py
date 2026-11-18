"""Red thread: after a re-voice, equalise (match), split per scene, beat timestamps (validated), per-scene transcription check. Log: auto_rt_voice2_log.txt (ends with DONE)."""
import difflib
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "shorts"))
sys.path.insert(0, str(HERE.parents[3] / "src"))
LOG = HERE / "auto_rt_voice2_log.txt"
ENV = {**os.environ, "PYTHONIOENCODING": "utf-8"}
ENV.pop("VOICE_F0", None)


def log(*a):
    with LOG.open("a", encoding="utf-8") as f:
        print(time.strftime("%H:%M:%S"), *a, file=f, flush=True)


for cmd in ("match", "split", "marks"):
    log("RUN", cmd)
    p = subprocess.run([sys.executable, "-u", "voice_story.py", "red_thread", "know_red_thread.json", "rt", cmd], cwd=HERE, capture_output=True, text=True, encoding="utf-8", env=ENV)
    log("\n".join(l for l in (p.stdout + p.stderr).splitlines() if "automatic function calling" not in l)[-2500:])

import verify_voice as V  # noqa: E402

doc = json.loads((HERE / "red_thread" / "know_red_thread.json").read_text(encoding="utf-8"))
norm = lambda q: re.sub(r"[\s\"'“”.,!?…ๆ:;()\-]+", "", q)
log("RUN per-scene check")
for i in range(1, 8):
    text = doc["scenes"][i - 1]["lines"][0]["text"]
    try:
        heard = V.transcribe(HERE / "red_thread" / "audio" / f"r{i}.wav")
    except Exception as exc:  # noqa: BLE001
        log(f"scene {i}: transcription failed {str(exc)[:80]}")
        continue
    a, b = norm(text), norm(heard)
    sm = difflib.SequenceMatcher(None, a, b)
    log(f"scene {i}: ratio {sm.ratio():.2f} script {len(a)} heard {len(b)}")
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag != "equal" and (i2 - i1 >= 5 or j2 - j1 >= 5):
            log(f"   {tag} | script: {a[max(0, i1 - 4):i2 + 4][:60]} | heard: {b[max(0, j1 - 4):j2 + 4][:60]}")
log("DONE")
