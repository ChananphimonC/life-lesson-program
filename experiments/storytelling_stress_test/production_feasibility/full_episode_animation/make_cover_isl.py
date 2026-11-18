"""Cover still for the island episode: sunset beach, the ten students (one scarf colour each) lined up in front of the macaque 'chairman' on a rock, the orange sail behind. 1280x720 png (no text; add_to_library puts the title on top)."""
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import episode  # noqa: E402,F401
import isl_common as C  # noqa: E402
from engine import new_canvas  # noqa: E402

cv = new_canvas()
C.tick(2.0)
cv.push(0, 0, scale=1.0)
C.sunset_beach(cv, 2.0, sun=0.55)
C.raft(cv, 330, 610, 400, 2.0, building=1.0, sail_on=True, wind=1.0, rock=0.0)
C.rocks(cv, 900, 700, 380, 210, (140, 132, 140), 3)
C.monkey(cv, 900, 520, 2.8, "sit", 2.0, mouth=True)
order = ["chula", "thamma", "mahidol", "kaset", "kmitl", "kmutt", "silpa", "cmu", "kku", "psu"]
for j, w in enumerate(order):
    x = 90 + j * 118
    C.st(cv, w, x, 706 + 6 * (j % 2), pose=C.REST, ex="happy" if j % 2 else "neutral", th=30 if x < 640 else -30, flip=x >= 640, k=0.6, seed=j)
cv.pop()
cv.result().convert("RGB").save(HERE / "covers_tmp" / "cover_isl.png")
print("saved")
