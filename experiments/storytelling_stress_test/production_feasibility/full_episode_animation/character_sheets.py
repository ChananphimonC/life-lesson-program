"""Character sheets for the four episode characters (provisional designs built on the approved prototype_v2 rig; NOT approved designs).
Front / three-quarter / side views, an expression row and a walk-cycle strip for each. Output: CHARACTER_DESIGNS/sheet_<name>.png"""
from pathlib import Path

from acting import *  # noqa: F401,F403

OUT = Path(__file__).resolve().parent / "CHARACTER_DESIGNS"
OUT.mkdir(exist_ok=True)
NAMES = dict(ton="Ton (ต้น)", kaew="Kaew (ยายแก้ว)", chok="Chok (ลุงโชค)", uean="Uean (ป้าเอื้อน)")
EXS = ["neutral", "happy", "gape", "shout", "think", "deadpan", "plead", "gloat"]
for who in ("ton", "kaew", "chok", "uean"):
    cv = new_canvas(ss=2)
    cv.fill([(0, 0), (W, 0), (W, H), (0, H)], (250, 246, 238), ink=None)
    for i, th in enumerate((0, 40, 85)):
        actor(cv, who, 150 + i * 190, 350, th, REST, "neutral", k=0.62 if who != "ton" else 0.78)
    for i in range(6):
        ph = i / 6 * 2 * math.pi
        actor(cv, who, 740 + i * 90, 350, 60, walk_pose(ph), "neutral", k=0.4 if who != "ton" else 0.5, walk=dict(phase=ph, stride=12, lift=9))
    for i, e in enumerate(EXS):
        cv.push(110 + i * 150, 540, scale=0.52)
        figure.head(cv, cast.CHARS[who], math.radians(22), ex(e) if isinstance(ex(e), dict) else e)
        cv.pop()
    img = cv.result().convert("RGB")
    img.save(OUT / f"sheet_{who}.png")
print("ok")
