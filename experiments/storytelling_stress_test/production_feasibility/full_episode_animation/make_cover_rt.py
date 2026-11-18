"""Cover still for the red-thread episode: the old man under the moon (the god who ties the red thread) with a big heart made of red thread. 1280x720 png -> add_to_library composes the title on top."""
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import episode  # noqa: E402,F401
import rt_common as C  # noqa: E402
from engine import new_canvas  # noqa: E402

cv = new_canvas()
C.tick(2.0)
C.moon_sky(cv, 1.3)
C.ambient(cv, 2.0, 40, (255, 240, 200), seed=9)
C.cloud(cv, 300, 690, 2.0)
C.cloud(cv, 1000, 700, 2.3)
cx, cy, s = 930, 500, 180
# the heart: a soft pink glow, a pale fill and the red thread running round it, ending in a loose loop and two tails
cv.fill(C.heart_pts(cx, cy, s * 1.5), C.RED_GLOW, ink=None, alpha=40)
cv.fill(C.heart_pts(cx, cy, s * 1.0), (255, 190, 205), ink=None, alpha=70)
outline = C.heart_pts(cx, cy, s, n=140)
sp = C.spline(outline, n=2)
cv.stroke(sp, C.RED_GLOW, 26, alpha=70)
cv.stroke(sp, C.RED, 11)
cv.stroke(sp, (255, 150, 160), 3.5, alpha=170)
for k in range(12):
    a = k * math.pi / 6
    cv.ellipse(cx + math.cos(a) * s * 1.35, cy + math.sin(a) * s * 1.2, 5, 5, (255, 244, 214), ink=None, alpha=200)
C.heart(cv, cx, cy + 10, 62, C.PINK, glow=1.0)
# the old man on the left, a thread from his hand to the heart's tip, the book of couples in the other hand
C.st(cv, "yuelao", 330, 722, pose=C.pl(C.REST, C.mk(((-60, 150, 30), (-30, 130, 90)), ((60, 150, 30), (30, 130, 90))), 0.8), ex="smug", th=20, k=1.28)
C.book(cv, 404, 590, 1.2, rot=-12)
a = (470, 566)
b = (cx - 20, cy + s * 0.95)
C.link(cv, a, b, 2.0, sag=60, w=6.0, tie=False, spark=False)
C.ring(cv, a, 1.6)
cv.result().convert("RGB").save(HERE / "covers_tmp" / "cover_rt.png")
print("saved")
