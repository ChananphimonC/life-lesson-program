"""python preview.py <scene> out.png t1 t2 ... : render a scene at the given local times and tile them (6 per sheet, 2 columns)."""
import importlib
import sys

from PIL import Image

import captions
from engine import new_canvas


def frame(mod, t):
    cv = new_canvas()
    ov = []
    mod.draw(cv, t, ov)
    img = cv.result().convert("RGBA")
    captions.draw_overlay(img, ov)
    captions.overlay(img, mod.CAPS, t)
    return img.convert("RGB")


if __name__ == "__main__":
    mod = importlib.import_module(sys.argv[1])
    out = sys.argv[2]
    ts = [float(x) for x in sys.argv[3:]]
    ims = [frame(mod, t).resize((640, 360)) for t in ts]
    rows = (len(ims) + 1) // 2
    sheet = Image.new("RGB", (1290, rows * 365), (30, 30, 30))
    for i, im in enumerate(ims):
        sheet.paste(im, (5 + (i % 2) * 645, 5 + (i // 2) * 365))
    sheet.save(out)
