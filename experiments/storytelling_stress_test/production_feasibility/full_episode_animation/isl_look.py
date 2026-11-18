"""Look at a scene: one still per beat (middle of each beat) -> island_72/ref/look_<scene>.png.   python isl_look.py isl1 [beat ...]"""
import importlib
import sys
from pathlib import Path

from PIL import Image

import captions
import engine
from engine import new_canvas

name = sys.argv[1]
import story_engine
m = story_engine.build(name) if name.startswith("gs_") else importlib.import_module(name)
engine.CUR = name
BE = m.BE
sel = [int(a) for a in sys.argv[2:]] or list(range(len(BE) - 1))
tiles = []
for k in sel:
    t = (BE[k] + BE[k + 1]) / 2 if len(sys.argv) <= 2 else BE[k] + 0.6 * (BE[k + 1] - BE[k])
    cv = new_canvas(ss=1)
    ov = []
    m.draw(cv, t, ov)
    img = cv.result().convert("RGBA")
    captions.draw_overlay(img, ov)
    tiles.append(img.convert("RGB").resize((640, 360)))
cols = 3
rows = (len(tiles) + cols - 1) // cols
sheet = Image.new("RGB", (cols * 640, rows * 360), (30, 30, 30))
for i, im in enumerate(tiles):
    sheet.paste(im, ((i % cols) * 640, (i // cols) * 360))
out = Path(__file__).resolve().parent / "island_72" / "ref" / f"look_{name}.png"
sheet.save(out)
print("saved", out, "beats", len(BE) - 1, "dur", round(m.DUR, 1))
