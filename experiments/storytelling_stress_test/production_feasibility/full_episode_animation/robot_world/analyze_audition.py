import difflib
import re
import sys
import wave
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
EXP = HERE.parents[3]
sys.path.insert(0, str(EXP / "shorts"))
sys.path.insert(0, str(EXP.parent / "src"))
import verify_voice as V  # noqa: E402

src = (HERE / "audition.py").read_text(encoding="utf-8")
ns = {}
exec(src[src.index("STYLE ="):src.index("settings =")], ns)
TEXT, STYLE = ns["TEXT"], ns["STYLE"]


def f0s(path):
    w = wave.open(str(path))
    x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(float)
    sr = w.getframerate()
    out, win = [], int(sr * 0.04)
    for i in range(0, len(x) - win * 2, win):
        seg = x[i:i + win * 2] - x[i:i + win * 2].mean()
        if np.sqrt((seg ** 2).mean()) < 600:
            continue
        ac = np.correlate(seg, seg, "full")[len(seg) - 1:]
        lo, hi = int(sr / 400), int(sr / 70)
        k = lo + np.argmax(ac[lo:hi])
        if ac[k] / ac[0] > 0.35:
            out.append(sr / k)
    return len(x) / sr, np.array(out)


norm = lambda s: re.sub(r"[\s\"'“”.,!?…ๆ:;()\-]+", "", s)
for v in sys.argv[1:]:
    p = HERE / "audition" / f"{v}.wav"
    n, f = f0s(p)
    heard = V.transcribe(p)
    r = difflib.SequenceMatcher(None, norm(TEXT), norm(heard)).ratio()
    style = norm(STYLE)[:12] in norm(heard)
    print(f"{v}: {n:.1f}s ({len(TEXT) / n:.1f} chars/s) F0 median {np.median(f):.0f} Hz, p10-p90 {np.percentile(f, 10):.0f}-{np.percentile(f, 90):.0f}, std {f.std():.0f}; "
          f"ASR similarity {r:.2f}; style read aloud: {style}")
    print("   heard:", heard[:120])
