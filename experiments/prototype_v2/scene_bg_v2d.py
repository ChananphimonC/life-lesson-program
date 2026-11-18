"""Kitchen background for the v2d animation: the same room as scene_test.kitchen, re-laid out so nothing is hidden
behind or attached to a head. (scene_test.py itself is untouched; the approved scene_test.png stays reproducible.)

Why: in the v2c animation the tied-back curtains, the window plant, the papaya board and the chilli jar sat exactly
where the two heads are, so they read as pink "ears" and orange/red blobs stuck to the characters. Here the window with
its curtains and plant moves to the free left side of the wall, and the counter props move to the ends of the counter.

    Safe zone (kept empty of props): x 560-1470, the area both heads and the bowl move through.
"""

from __future__ import annotations

from pathlib import Path

from scene_test import BINK, H, W, WALL, glow, rect, table_front
from toon import Canvas, spline

OUT = Path(__file__).resolve().parent / "out"
SAFE_X = (560, 1470)


def kitchen_v2d(cv):
    # wall, floor
    cv.fill([(0, 0), (W, 0), (W, 820), (0, 820)], WALL, ink=None)
    cv.fill([(0, 820), (W, 820), (W, H), (0, H)], (226, 190, 148), ink=None)
    for i in range(-6, 16):
        x = i * 150
        cv.stroke([(W / 2 + (x - W / 2) * 0.82, 820), (W / 2 + (x - W / 2) * 1.35, H)], (206, 168, 126), 2.2)
    for y in (880, 960, 1050):
        cv.stroke([(0, y), (W, y)], (212, 176, 134), 1.6, alpha=160)
    cv.stroke([(0, 820), (W, 820)], BINK, 2.6)

    # window with tied-back curtains and a plant, on the free left part of the wall (x 300-600)
    wx0, wx1, wy0, wy1 = 330, 500, 130, 400          # right curtain ends ~x 545, clear of ปิ่น's hair (x >= 570)
    rect(cv, wx0, wy0, wx1, wy1, (204, 230, 244), r=8)
    cv.fill([(wx0 + 4, 290), (wx1 - 4, 290), (wx1 - 4, wy1 - 4), (wx0 + 4, wy1 - 4)], (182, 218, 186), ink=None)
    for x in (365, 415, 465):
        cv.ellipse(x, 292, 46, 28, (164, 206, 170))
    cv.stroke([((wx0 + wx1) / 2, wy0), ((wx0 + wx1) / 2, wy1)], BINK, 5)
    cv.stroke([(wx0, 262), (wx1, 262)], BINK, 4)
    cv.stroke([(wx0 - 40, 112), (wx1 + 40, 112)], (150, 116, 90), 6)
    for side, x0 in ((1, wx0 - 30), (-1, wx1 + 30)):
        tie = (x0 + side * 22, 290)
        outline = [(x0, 112), (x0 + side * 62, 112), (x0 + side * 44, 200), tie, (x0 + side * 40, 370),
                   (x0 + side * 52, 410), (x0, 410)]
        cv.fill(spline(outline, closed=True, n=5), (244, 178, 150), ink=BINK, lw=2.4, shade_col=(226, 152, 128), depth=6)
        for f in (0.33, 0.66):
            cv.stroke(spline([(x0 + side * 62 * f, 118), (x0 + side * (22 * f + 8), 240), (tie[0] - side * 6 * (1 - f), 284)],
                             n=4), (222, 148, 124), 2.0)
        cv.fill(spline([(tie[0] - 16, 282), (tie[0] + 16, 282), (tie[0] + 14, 298), (tie[0] - 14, 298)], closed=True, n=2),
                (250, 226, 160), ink=BINK, lw=2.0)
    rect(cv, wx0 - 14, wy1, wx1 + 14, wy1 + 14, (240, 226, 200), r=3)
    cv.fill(spline([(430, wy1 + 2), (426, wy1 - 30), (472, wy1 - 30), (468, wy1 + 2)], closed=True, n=3), (214, 130, 96),
            ink=BINK, lw=2.2)
    for a, b in (((450, wy1 - 28), (430, wy1 - 70)), ((450, wy1 - 28), (452, wy1 - 78)), ((450, wy1 - 28), (476, wy1 - 64))):
        cv.fill(spline([a, ((a[0] + b[0]) / 2 - 9, (a[1] + b[1]) / 2), b, ((a[0] + b[0]) / 2 + 9, (a[1] + b[1]) / 2)],
                       closed=True, n=4), (118, 176, 110), ink=BINK, lw=2.0)
    # one upper cabinet left of the window; the middle and right ones (which sat behind Pin) are gone
    rect(cv, 80, 110, 280, 330, (236, 222, 196), shade_col=(222, 204, 176))
    cv.ellipse(260, 300, 6, 6, (190, 160, 120), ink=BINK, lw=1.8)

    # backsplash tiles + counter + base cabinets
    cv.fill([(60, 430), (1520, 430), (1520, 560), (60, 560)], (220, 236, 228), ink=None)
    for x in range(60, 1521, 52):
        cv.stroke([(x, 430), (x, 560)], (202, 222, 214), 1.6)
    for y in (473, 516):
        cv.stroke([(60, y), (1520, y)], (202, 222, 214), 1.6)
    rect(cv, 40, 548, 1540, 582, (236, 228, 214), r=5)
    for i in range(6):
        rect(cv, 60 + i * 245, 582, 295 + i * 245, 818, (214, 188, 152), shade_col=(198, 170, 132), r=4)
        cv.stroke([(150 + i * 245, 610), (205 + i * 245, 610)], (170, 140, 104), 5)

    # counter props live at the two ends, outside the safe zone: kettle, papaya board, jar
    cv.fill(spline([(300, 548), (290, 486), (330, 462), (380, 462), (420, 486), (410, 548)], closed=True, n=5),
            (232, 120, 104), ink=BINK, lw=2.6, shade_col=(206, 96, 84), depth=8)
    cv.stroke(spline([(320, 470), (355, 430), (395, 470)], n=6), BINK, 6)
    cv.fill(spline([(418, 500), (452, 476), (458, 484), (424, 512)], closed=True, n=3), (232, 120, 104), ink=BINK, lw=2.2)
    rect(cv, 130, 530, 280, 548, (226, 186, 132), r=6)             # papaya board: moved from x 560-760 to the far left
    cv.fill(spline([(150, 530), (165, 500), (215, 490), (255, 506), (248, 530)], closed=True, n=6), (242, 160, 80),
            ink=BINK, lw=2.4, shade_col=(222, 136, 64), depth=6)
    cv.fill(spline([(198, 530), (206, 510), (248, 508), (246, 530)], closed=True, n=5), (250, 196, 120), ink=None)
    for x in (214, 226, 238):
        cv.ellipse(x, 521, 3.0, 3.8, (60, 44, 40))
    rect(cv, 500, 488, 556, 548, (246, 240, 230), r=10)                          # chilli jar: left of the safe zone
    cv.fill(spline([(506, 548), (506, 516), (550, 516), (550, 548)], closed=True, n=2), (216, 74, 60), ink=None)
    rect(cv, 496, 478, 560, 494, (110, 90, 80), r=4)

    # fridge, pendant lamp
    rect(cv, 1580, 200, 1840, 820, (232, 240, 242), shade_col=(208, 220, 224), r=18)
    cv.stroke([(1580, 430), (1840, 430)], BINK, 2.6)
    cv.stroke([(1604, 300), (1604, 400)], (176, 186, 190), 8)
    cv.stroke([(1604, 470), (1604, 600)], (176, 186, 190), 8)
    rect(cv, 1700, 250, 1770, 330, (255, 226, 120), r=4, lw=2)
    cv.ellipse(1735, 290, 16, 16, (240, 150, 90), ink=BINK, lw=1.8)
    cv.stroke([(975, 0), (975, 40)], BINK, 3)
    cv.fill(spline([(935, 80), (950, 44), (1000, 44), (1015, 80)], closed=True, n=4), (244, 214, 140), ink=BINK, lw=2.6)


def make_bg(path=None):
    cv = Canvas(W, H, ss=2, bg=(255, 255, 255, 255))
    kitchen_v2d(cv)
    glow(cv, 415, 270, 400, (255, 244, 214), 0.4)           # window light, on the window side now
    table_front(cv)
    img = cv.result().convert("RGB")
    img.save(path or OUT / "anim_bg_v2d.png")
    return img


if __name__ == "__main__":
    make_bg()
    print("ok")
