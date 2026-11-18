"""Wait for the Gemini TTS quota to reset (>= 8 requests left), then run auto_story.py for one story. Log: stories/<id>/wait_log.txt.   python wait_and_run.py <story> [--voice Fenrir]"""
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import daily_runner as D  # noqa: E402

story = sys.argv[1]
log = HERE / "stories" / story / "wait_log.txt"
t0 = time.time()
while time.time() - t0 < 5 * 3600:
    left = D.tts_left()
    with log.open("a", encoding="utf-8") as f:
        print(time.strftime("%H:%M:%S"), "tts left", left, file=f, flush=True)
    if left >= 8:
        p = subprocess.run([sys.executable, "-u", "auto_story.py", story] + sys.argv[2:], cwd=HERE, stdin=subprocess.DEVNULL)
        with log.open("a", encoding="utf-8") as f:
            print(time.strftime("%H:%M:%S"), "auto_story exit", p.returncode, file=f, flush=True)
        break
    time.sleep(300)
