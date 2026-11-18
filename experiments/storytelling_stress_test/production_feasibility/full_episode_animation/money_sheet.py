"""Character sheet of the money cast -> stories/money_v2/cast_sheet.png"""
from pathlib import Path

import money_cast2  # noqa: F401
from acting import *  # noqa: F401,F403

OUT = Path(__file__).resolve().parent / "stories" / "money_v4"
OUT.mkdir(parents=True, exist_ok=True)
NAMES = ["tang", "jin", "nun", "coach"]
cv = new_canvas(ss=2)
cv.fill([(0, 0), (W, 0), (W, H), (0, H)], (250, 246, 238), ink=None)
for i, who in enumerate(NAMES):
    actor(cv, who, 170 + i * 310, 340, 0, REST, "happy", k=0.78)
    actor(cv, who, 170 + i * 310, 690, 40, REST, "deadpan", k=0.78)
cv.result().convert("RGB").save(OUT / "cast_sheet.png")
print("ok")
