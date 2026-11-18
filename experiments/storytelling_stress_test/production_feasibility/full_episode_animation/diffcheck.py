import difflib, json, re, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "shorts"))
sys.path.insert(0, str(HERE.parents[3] / "src"))
import verify_voice as V  # noqa: E402

story, script, ci = sys.argv[1], sys.argv[2], int(sys.argv[3])
doc = json.loads((HERE / story / script).read_text(encoding="utf-8"))
texts = [s["lines"][0]["text"] for s in doc["scenes"]]
norm = lambda q: re.sub(r"[\s\"'“”.,!?…ๆ:;()\-]+", "", q)
want = norm(" ".join(texts[s - 1] for s in doc["chunks"][ci - 1]))
heard = None
for _ in range(4):
    try:
        heard = V.transcribe(HERE / story / "audio" / f"chunk{ci}_raw.wav")
        break
    except Exception as e:  # noqa: BLE001
        print("retry", str(e)[:60])
h = norm(heard)
sm = difflib.SequenceMatcher(None, want, h)
print(f"chunk {ci}: ratio {sm.ratio():.2f}")
for tag, i1, i2, j1, j2 in sm.get_opcodes():
    if tag != "equal" and (i2 - i1 > 1 or j2 - j1 > 1):
        print(tag, "| script:", want[max(0, i1 - 6):i2 + 6], "| heard:", h[max(0, j1 - 6):j2 + 6])
