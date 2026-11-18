"""One command from a story.json to a filed episode: validate -> voice (Gemini TTS) -> pitch match -> split -> beat marks -> ASR check -> render scenes -> assemble -> QA -> cover -> library.
Resumable: every step is skipped when its output already exists. Log: stories/<story>/run_log.txt (ends with DONE or FAILED).

    python auto_story.py <story> [--voice Fenrir] [--no-file]
"""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
story = sys.argv[1]
VOICE = sys.argv[sys.argv.index("--voice") + 1] if "--voice" in sys.argv else "Fenrir"
FILE = "--no-file" not in sys.argv
FORCE = "--force" in sys.argv                      # re-render the scenes / assemble even when the files already exist (they are overwritten)
SD = HERE / "stories" / story
LOG = SD / "run_log.txt"
ENV = {**os.environ, "PYTHONIOENCODING": "utf-8", "STORY_ROOT": str(HERE / "stories")}
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[2] / "shorts"))


def log(*a):
    with LOG.open("a", encoding="utf-8") as f:
        print(time.strftime("%Y-%m-%d %H:%M:%S"), *a, file=f, flush=True)


def run(args, env=None, tail=600):
    p = subprocess.run([sys.executable, "-u", *args], cwd=HERE, env=env or ENV, capture_output=True, text=True, encoding="utf-8", stdin=subprocess.DEVNULL)
    out = "\n".join(l for l in (p.stdout + p.stderr).splitlines() if "automatic function calling" not in l)
    return p.returncode, out[-tail:]


def fail(msg):
    log("FAILED", msg)
    sys.exit(1)


try:
    import story_engine as S
    doc = S.load(story)
    bad = S.validate(doc)
    if bad:
        fail("validate: " + " | ".join(bad[:8]))
    n = len(doc["scenes"])
    aud = SD / "audio"
    aud.mkdir(exist_ok=True)
    vs = ["voice_story.py", f"stories/{story}", "story.json", "gs"]
    # ---- voice
    if not all((aud / f"chunk{i}_raw.wav").is_file() for i in range(1, len(doc["chunks"]) + 1)):
        rc, out = run(vs + ["synth", VOICE])
        log("synth", out.replace("\n", " | "))
        if not all((aud / f"chunk{i}_raw.wav").is_file() for i in range(1, len(doc["chunks"]) + 1)):
            fail("voice incomplete (quota or error)")
    if not (aud / "chunk1.wav").is_file():
        log("match", run(vs + ["match"])[1].replace("\n", " | "))
    if not (aud / "timing.json").is_file():
        log("split", run(vs + ["split"])[1].replace("\n", " | "))
    if not (aud / "marks.json").is_file():
        log("marks", run(vs + ["marks"], tail=1500)[1].replace("\n", " | "))
    # ---- ASR check per scene (log only)
    if not (SD / "asr_check.txt").is_file():
        import difflib
        import re
        import verify_voice as V
        norm = lambda q: re.sub(r"[\s\"'“”.,!?…ๆ:;()\-]+", "", q)
        lines = []
        for i in range(1, n + 1):
            try:
                heard = V.transcribe(aud / f"r{i}.wav")
                lines.append(f"scene {i}: ratio {difflib.SequenceMatcher(None, norm(' '.join(l['text'] for l in doc['scenes'][i - 1]['lines'])), norm(heard)).ratio():.2f}")
            except Exception as exc:  # noqa: BLE001
                lines.append(f"scene {i}: transcription failed {str(exc)[:60]}")
        (SD / "asr_check.txt").write_text("\n".join(lines), encoding="utf-8")
        log("asr", " | ".join(lines))
    # ---- render
    names = [f"gs_{story}_{i}" for i in range(1, n + 1)]
    env = {**ENV, "EPISODE_ORDER": ",".join(names), "EPISODE_DIR": str(SD), "STORY_PREFIX": "gs", "STORY_OUT": f"{story}.mp4"}
    (SD / "scenes").mkdir(exist_ok=True)

    def dur_of(f):
        r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(f)], capture_output=True, text=True)
        try:
            return float(r.stdout.strip())
        except ValueError:
            return -1.0

    os.environ.update({"STORY_ROOT": str(HERE / "stories")})
    t0 = time.time()
    for i, name in enumerate(names, 1):
        want = S.Scene(story, i).DUR
        f = SD / "scenes" / f"{name}.mp4"
        if f.is_file() and abs(dur_of(f) - want) < 0.3 and not FORCE:
            continue
        rc, out = run(["episode.py", "frames", name], env=env, tail=200)
        log("render", name, round(time.time() - t0), "s", out.replace("\n", " | "))
        if not f.is_file():
            fail(f"render {name}")
    mp4 = SD / "renders" / f"{story}.mp4"
    if FORCE or not mp4.is_file():
        rc, out = run(["robot_assemble.py"], env=env, tail=300)
        log("assemble", out.replace("\n", " | "))
        if not mp4.is_file():
            fail("assemble")
        rc, out = run(["qa.py"], env={**env, "QA_MP4": str(mp4), "QA_OUT": str(SD / "qa")}, tail=200)
        log("qa", out.replace("\n", " | ")[-150:])
    # ---- cover + library
    cover = SD / "cover.png"
    S.render_cover(story, cover)
    if FILE:
        text = doc["cover"]["text"]
        rc, out = run(["add_to_library.py", str(mp4), doc["title"], doc.get("topic", doc["title"]), doc.get("theme", "เรื่องเล่า"), str(cover), text, "รู้หรือไม่"], tail=300)
        log("library", out.replace("\n", " | "))
    if FORCE or not (SD / "shorts" / "shorts.txt").is_file():
        rc, out = run(["make_shorts.py", str(mp4), str(aud / "timing.json"), "--title", doc["title"], "--texts", str(SD / "story.json"), "--out", str(SD / "shorts")], tail=200)
        log("shorts", "ok" if (SD / "shorts" / "shorts.txt").is_file() else out.replace("\n", " | "))
    log("DONE")
except SystemExit:
    raise
except Exception as exc:  # noqa: BLE001
    import traceback
    log("FAILED", traceback.format_exc()[-800:].replace("\n", " | "))
    sys.exit(1)
