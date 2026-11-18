"""Character sheet of the island cast -> island_72/ref/isl_sheet_*.png"""
from pathlib import Path

import isl_chars  # noqa: F401
from acting import *  # noqa: F401,F403

OUT = Path(__file__).resolve().parent / "island_72" / "ref"
OUT.mkdir(parents=True, exist_ok=True)
NAMES = ["chula", "thamma", "mahidol", "kaset", "kmitl", "kmutt", "silpa", "cmu", "kku", "psu", "captain"]
cv = new_canvas(ss=2)
cv.fill([(0, 0), (W, 0), (W, H), (0, H)], (250, 246, 238), ink=None)
for i, who in enumerate(NAMES[:6]):
    actor(cv, who, 110 + i * 205, 330, 0, REST, "happy", k=0.62)
    actor(cv, who, 110 + i * 205, 670, 38, REST, "neutral", k=0.62)
cv.result().convert("RGB").save(OUT / "isl_sheet_a.png")
cv = new_canvas(ss=2)
cv.fill([(0, 0), (W, 0), (W, H), (0, H)], (250, 246, 238), ink=None)
for i, who in enumerate(NAMES[6:]):
    actor(cv, who, 130 + i * 240, 330, 0, REST, "happy", k=0.62)
    actor(cv, who, 130 + i * 240, 670, 38, REST, "neutral", k=0.62)
cv.result().convert("RGB").save(OUT / "isl_sheet_b.png")
print("ok")
