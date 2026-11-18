"""Close-up crops of the six areas the v2c refinements target, rendered from a chosen code directory.

    python closeups.py v2b_approved before     -> out/closeups_before.png
    python closeups.py . after                 -> out/closeups_after.png

Row 1 (Mom): front pregnancy silhouette | bob hair, 3/4 | bowl and spoon (eat pose)
Row 2 (Pin): side-view glasses and face | side-view hair, full length | magnifying-glass grip
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
code_dir = (HERE / sys.argv[1]).resolve()
tag = sys.argv[2]
sys.path.insert(0, str(code_dir))
sys.path.insert(0, str(HERE.parent / "shorts"))

from PIL import Image, ImageDraw  # noqa: E402

from cast import D2R  # noqa: E402
from figure import figure  # noqa: E402
from toon import Canvas  # noqa: E402

CELL_W, CELL_H = 640, 640
BG = (250, 246, 238, 255)


def cell(cid, th, pose, expr, pregnant, crop, scale):
    """Render the figure at `scale`, then crop (x0, y0, x1, y1) given in figure units around the head origin."""
    cv = Canvas(CELL_W, CELL_H, ss=3, bg=BG)
    x0, y0, x1, y1 = crop
    k = scale
    cv.push(-x0 * k, -y0 * k, scale=k)
    figure(cv, cid, th, pose, expr, pregnant=pregnant, shadow=False)
    cv.pop()
    return cv.result()


def main():
    cells = [
        cell("mom", 0, "rest", "neutral", True, (-110, 90, 110, 310), 2.9),             # front silhouette
        cell("mom", 35 * D2R, "rest", "neutral", True, (-130, -130, 130, 130), 2.45),    # bob, 3/4
        cell("mom", 40 * D2R, "eat", "content", True, (-90, 40, 90, 220), 3.5),          # bowl + spoon
        cell("pin", 82 * D2R, "rest", "neutral", False, (-130, -130, 130, 130), 2.45),   # side glasses
        cell("pin", 82 * D2R, "rest", "neutral", False, (-130, -120, 130, 300), 1.5),    # side hair
        cell("pin", 35 * D2R, "magnify", "determined", False, (-130, -60, 130, 200), 2.45),
    ]
    sheet = Image.new("RGB", (CELL_W * 3, CELL_H * 2), (250, 246, 238))
    for i, c in enumerate(cells):
        sheet.paste(c.convert("RGB"), ((i % 3) * CELL_W, (i // 3) * CELL_H))
    sheet.resize((sheet.width * 3 // 4, sheet.height * 3 // 4), Image.LANCZOS).save(HERE / "out" / f"closeups_{tag}.png")
    print("ok")


if __name__ == "__main__":
    main()
