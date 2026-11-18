"""Contact sheet of the island backgrounds and animals (quick look while building) -> island_72/ref/isl_bgs.png / isl_animals.png"""
import sys
from pathlib import Path

from PIL import Image

import isl_common as C
from isl_common import *  # noqa: F401,F403

OUT = Path(__file__).resolve().parent / "island_72" / "ref"
OUT.mkdir(parents=True, exist_ok=True)
BG = [("beach", lambda cv, t: C.beach_morning(cv, t)), ("forest", lambda cv, t: C.forest(cv, t)), ("mangrove", lambda cv, t: C.mangrove(cv, t)),
      ("tidepool", lambda cv, t: C.tidepool(cv, t)), ("hillpath", lambda cv, t: C.hill_path(cv, t)), ("hilltop", lambda cv, t: C.hilltop(cv, t)),
      ("sunset", lambda cv, t: C.sunset_beach(cv, t)), ("night", lambda cv, t: C.night_beach(cv, t)), ("dawn", lambda cv, t: C.dawn_beach(cv, t)),
      ("cave", lambda cv, t: C.cave(cv, t)), ("yard", lambda cv, t: C.raft_yard(cv, t, 0.2)), ("storm", lambda cv, t: C.storm_sea(cv, t)),
      ("ferry", lambda cv, t: C.ferry_dawn(cv, t))]
only = sys.argv[1:]
tiles = []
for name, fn in BG:
    if only and name not in only:
        continue
    cv = new_canvas(ss=1)
    cv.push(0, 0, scale=1.0)
    fn(cv, 1.0)
    cv.pop()
    tiles.append(cv.result().convert("RGB").resize((640, 360)))
cols = 3
rows = (len(tiles) + cols - 1) // cols
sheet = Image.new("RGB", (cols * 640, rows * 360), (30, 30, 30))
for i, im in enumerate(tiles):
    sheet.paste(im, ((i % cols) * 640, (i // cols) * 360))
sheet.save(OUT / "isl_bgs.png")
# animals
cv = new_canvas(ss=2)
cv.push(0, 0, scale=1.0)
cv.fill([(0, 0), (W, 0), (W, H), (0, H)], (236, 244, 250), ink=None)
C.monkey(cv, 120, 200, 1.1, "sit", 1.0, hold="bag")
C.monkey(cv, 330, 200, 1.1, "run", 1.0)
C.monkey(cv, 520, 200, 1.1, "arms_up", 1.0)
C.hermit_crab(cv, 700, 180, 1.6, 1.0)
C.seagull(cv, 820, 120, 1.4, 1.0)
C.hornbill(cv, 1040, 120, 1.3, 1.0)
C.lizard(cv, 330, 420, 1.0, 1.0)
C.fish(cv, 640, 380, 1.8, 1.0)
C.sea_turtle(cv, 860, 410, 1.0, 1.0)
C.coconut(cv, 1100, 420, 1.6)
C.campfire(cv, 150, 690, 1.0)
C.net(cv, 420, 620, 1.0)
C.mirror_flash(cv, 650, 620, 1.0)
C.fish_on_stick(cv, 800, 600, 1.4)
C.ferry(cv, 1050, 700, 0.4, 1.0)
C.raft(cv, 1000, 560, 380, 1.0, rock=1.0)
cv.pop()
cv.result().convert("RGB").save(OUT / "isl_animals.png")
print("ok")
