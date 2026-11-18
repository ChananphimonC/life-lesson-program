"""Character sheet for the university cast: front / three-quarter views, a short walk strip and expression heads. -> CHARACTER_DESIGNS/uni_sheet_<name>.png"""
from pathlib import Path

import uni_chars  # noqa: F401
from acting import *  # noqa: F401,F403

OUT = Path(__file__).resolve().parent / "CHARACTER_DESIGNS"
OUT.mkdir(exist_ok=True)
NAMES = ["phum", "bua", "kong", "manao", "em", "yuelao"]
EXS = ["neutral", "happy", "gape", "shout", "think", "deadpan", "plead", "gloat"]
cv = new_canvas(ss=2)
cv.fill([(0, 0), (W, 0), (W, H), (0, H)], (250, 246, 238), ink=None)
for i, who in enumerate(NAMES):
    actor(cv, who, 110 + i * 205, 330, 0, REST, "neutral", k=0.62)
    actor(cv, who, 110 + i * 205, 660, 38, REST, "happy", k=0.62)
cv.result().convert("RGB").save(OUT / "uni_sheet_all.png")
for who in NAMES:
    c2 = new_canvas(ss=2)
    c2.fill([(0, 0), (W, 0), (W, H), (0, H)], (250, 246, 238), ink=None)
    for i, th in enumerate((0, 40, 85)):
        actor(c2, who, 150 + i * 190, 350, th, REST, "neutral", k=0.7)
    for i in range(6):
        ph = i / 6 * 2 * math.pi
        actor(c2, who, 740 + i * 90, 350, 60, walk_pose(ph), "neutral", k=0.42, walk=dict(phase=ph, stride=12, lift=9))
    for i, e in enumerate(EXS):
        c2.push(110 + i * 150, 540, scale=0.52)
        figure.head(c2, cast.CHARS[who], math.radians(22), ex(e) if isinstance(ex(e), dict) else e)
        c2.pop()
    c2.result().convert("RGB").save(OUT / f"uni_sheet_{who}.png")
print("ok")
