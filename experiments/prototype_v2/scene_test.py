"""Prototype v2b stage 2: one test scene built from the stage-1 characters.

Story beat (know_craving, present day): ปิ่น offers แม่ a bowl of ตำผลไม้, the dish แม่ craved every day while
pregnant with ปิ่น; แม่ leans back with a "no thanks" palm (she has not touched it since). No text on screen.

    python scene_test.py  -> out/scene_test.png (+ out/scene_test_320.png, out/scene_test_notext_check.png)
"""

from __future__ import annotations

from pathlib import Path

from cast import D2R
from figure import bowl, figure
from toon import INK, Canvas, chain, ellipse_pts, mix, shade, spline

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
W, H = 1920, 1080
WALL = (250, 238, 214)
BINK = mix(INK, WALL, 0.3)          # lighter outline for the set, so the characters stay in front


def rect(cv, x0, y0, x1, y1, col, ink=BINK, lw=2.6, r=6, shade_col=None):
    pts = chain([(x0 + r, y0), (x1 - r, y0)], [(x1 - r, y0), (x1, y0), (x1, y0 + r)], [(x1, y0 + r), (x1, y1 - r)],
                [(x1, y1 - r), (x1, y1), (x1 - r, y1)], [(x1 - r, y1), (x0 + r, y1)], [(x0 + r, y1), (x0, y1), (x0, y1 - r)],
                [(x0, y1 - r), (x0, y0 + r)], [(x0, y0 + r), (x0, y0), (x0 + r, y0)], n=4)
    cv.fill(pts, col, ink=ink, lw=lw, shade_col=shade_col, depth=5)


def kitchen(cv):
    # wall + warm light from the window
    cv.fill([(0, 0), (W, 0), (W, 820), (0, 820)], WALL, ink=None)
    # floor: planks converging slightly toward the back wall
    cv.fill([(0, 820), (W, 820), (W, H), (0, H)], (226, 190, 148), ink=None)
    for i in range(-6, 16):
        x = i * 150
        cv.stroke([(W / 2 + (x - W / 2) * 0.82, 820), (W / 2 + (x - W / 2) * 1.35, H)], (206, 168, 126), 2.2)
    for y in (880, 960, 1050):
        cv.stroke([(0, y), (W, y)], (212, 176, 134), 1.6, alpha=160)
    cv.stroke([(0, 820), (W, 820)], BINK, 2.6)
    # window between the two heads: it frames the offer
    wx0, wx1, wy0, wy1 = 830, 1120, 120, 410
    rect(cv, wx0, wy0, wx1, wy1, (204, 230, 244), r=8)
    cv.fill([(wx0 + 4, 300), (wx1 - 4, 300), (wx1 - 4, wy1 - 4), (wx0 + 4, wy1 - 4)], (182, 218, 186), ink=None)
    for x in (880, 960, 1040, 1090):
        cv.ellipse(x, 300, 60, 34, (164, 206, 170))
    cv.stroke([((wx0 + wx1) / 2, wy0), ((wx0 + wx1) / 2, wy1)], BINK, 5)
    cv.stroke([(wx0, 270), (wx1, 270)], BINK, 4)
    cv.stroke([(wx0 - 60, 104), (wx1 + 60, 104)], (150, 116, 90), 6)
    for side, x0 in ((1, wx0 - 50), (-1, wx1 + 50)):        # tied-back drapes with folds
        tie = (x0 + side * 34, 300)
        outline = [(x0, 104), (x0 + side * 96, 104), (x0 + side * 70, 200), tie, (x0 + side * 62, 380),
                   (x0 + side * 82, 430), (x0, 430)]
        cv.fill(spline(outline, closed=True, n=5), (244, 178, 150), ink=BINK, lw=2.4, shade_col=(226, 152, 128), depth=7)
        for f in (0.33, 0.66):
            cv.stroke(spline([(x0 + side * 96 * f, 110), (x0 + side * (34 * f + 10), 250), (tie[0] - side * 8 * (1 - f), 296)],
                             n=4), (222, 148, 124), 2.2)
            cv.stroke(spline([(tie[0] - side * 6 * (1 - f), 312), (x0 + side * (60 * f + 6), 400), (x0 + side * 78 * f, 426)],
                             n=4), (222, 148, 124), 2.2)
        cv.fill(spline([(tie[0] - 22, 292), (tie[0] + 22, 292), (tie[0] + 20, 310), (tie[0] - 20, 310)], closed=True, n=2),
                (250, 226, 160), ink=BINK, lw=2.2)
    rect(cv, wx0 - 20, wy1, wx1 + 20, wy1 + 16, (240, 226, 200), r=3)
    cv.fill(spline([(1050, wy1 + 2), (1044, wy1 - 34), (1096, wy1 - 34), (1090, wy1 + 2)], closed=True, n=3), (214, 130, 96),
            ink=BINK, lw=2.2)
    for a, b in (((1070, wy1 - 32), (1046, wy1 - 80)), ((1070, wy1 - 32), (1072, wy1 - 90)), ((1070, wy1 - 32), (1100, wy1 - 74))):
        cv.fill(spline([a, ((a[0] + b[0]) / 2 - 10, (a[1] + b[1]) / 2), b, ((a[0] + b[0]) / 2 + 10, (a[1] + b[1]) / 2)],
                       closed=True, n=4), (118, 176, 110), ink=BINK, lw=2.0)
    # upper cabinets
    for i in range(3):
        rect(cv, 90 + i * 210, 110, 290 + i * 210, 330, (236, 222, 196), shade_col=(222, 204, 176))
        cv.ellipse(270 + i * 210, 300, 6, 6, (190, 160, 120), ink=BINK, lw=1.8)
    # backsplash tiles + counter
    cv.fill([(60, 430), (1520, 430), (1520, 560), (60, 560)], (220, 236, 228), ink=None)
    for x in range(60, 1521, 52):
        cv.stroke([(x, 430), (x, 560)], (202, 222, 214), 1.6)
    for y in (473, 516):
        cv.stroke([(60, y), (1520, y)], (202, 222, 214), 1.6)
    rect(cv, 40, 548, 1540, 582, (236, 228, 214), r=5)
    for i in range(6):
        rect(cv, 60 + i * 245, 582, 295 + i * 245, 818, (214, 188, 152), shade_col=(198, 170, 132), r=4)
        cv.stroke([(150 + i * 245, 610), (205 + i * 245, 610)], (170, 140, 104), 5)
    # things on the counter: kettle, cutting board with a papaya, jar of chilli
    cv.fill(spline([(300, 548), (290, 486), (330, 462), (380, 462), (420, 486), (410, 548)], closed=True, n=5),
            (232, 120, 104), ink=BINK, lw=2.6, shade_col=(206, 96, 84), depth=8)
    cv.stroke(spline([(320, 470), (355, 430), (395, 470)], n=6), BINK, 6)
    cv.fill(spline([(418, 500), (452, 476), (458, 484), (424, 512)], closed=True, n=3), (232, 120, 104), ink=BINK, lw=2.2)
    rect(cv, 560, 530, 760, 548, (226, 186, 132), r=6)
    cv.fill(spline([(590, 530), (610, 498), (680, 486), (730, 504), (720, 530)], closed=True, n=6), (242, 160, 80),
            ink=BINK, lw=2.4, shade_col=(222, 136, 64), depth=6)
    cv.fill(spline([(650, 530), (660, 508), (720, 506), (716, 530)], closed=True, n=5), (250, 196, 120), ink=None)
    for x in (676, 690, 704):
        cv.ellipse(x, 520, 3.2, 4, (60, 44, 40))
    rect(cv, 1440, 488, 1500, 548, (246, 240, 230), r=10)
    cv.fill(spline([(1446, 548), (1446, 516), (1494, 516), (1494, 548)], closed=True, n=2), (216, 74, 60), ink=None)
    rect(cv, 1436, 478, 1504, 494, (110, 90, 80), r=4)
    # fridge
    rect(cv, 1580, 200, 1840, 820, (232, 240, 242), shade_col=(208, 220, 224), r=18)
    cv.stroke([(1580, 430), (1840, 430)], BINK, 2.6)
    cv.stroke([(1604, 300), (1604, 400)], (176, 186, 190), 8)
    cv.stroke([(1604, 470), (1604, 600)], (176, 186, 190), 8)
    rect(cv, 1700, 250, 1770, 330, (255, 226, 120), r=4, lw=2)                     # a child's drawing on the door
    cv.ellipse(1735, 290, 16, 16, (240, 150, 90), ink=BINK, lw=1.8)
    # pendant lamp
    cv.stroke([(975, 0), (975, 40)], BINK, 3)
    cv.fill(spline([(935, 80), (950, 44), (1000, 44), (1015, 80)], closed=True, n=4), (244, 214, 140), ink=BINK, lw=2.6)


def table_front(cv):
    """Dining table end in the left foreground (overlaps the frame edge): a glass of โอเลี้ยง and the papaya plate."""
    cv.fill([(-40, 760), (330, 760), (360, 800), (-40, 800)], (204, 150, 104), ink=INK, lw=3, shade_col=(184, 130, 88))
    cv.fill([(-40, 800), (360, 800), (360, 822), (-40, 822)], (176, 122, 82), ink=INK, lw=3)
    cv.fill([(300, 822), (334, 822), (330, 1090), (304, 1090)], (176, 122, 82), ink=INK, lw=3)
    # oliang glass
    cv.fill([(170, 640), (226, 640), (220, 770), (176, 770)], (90, 56, 40), ink=INK, lw=3)
    cv.fill([(170, 640), (226, 640), (224, 670), (172, 670)], (230, 240, 246), ink=None, alpha=180)
    for (x, y) in ((186, 690), (206, 712), (190, 735)):
        cv.fill([(x, y), (x + 16, y - 4), (x + 18, y + 12), (x + 2, y + 14)], (220, 236, 244), ink=None, alpha=160)
    cv.stroke([(210, 600), (198, 700)], (232, 90, 90), 6)


def aroma(cv, x0, y0, x1, y1):
    """Three wavy aroma lines drifting from the bowl toward แม่: why she leans away, shown without words."""
    for k, dy in enumerate((-22, 0, 22)):
        pts = []
        for i in range(9):
            t = i / 8
            pts.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * t + dy + 9 * ((-1) ** i) * (0.4 + t)))
        cv.stroke(spline(pts, n=5), (178, 196, 120), 4.2 - k * 0.4, alpha=190)


def recoil(cv, x, y):
    """Short motion arcs behind แม่'s head: she is pulling back."""
    for i, (dx, dy, l) in enumerate(((0, 0, 70), (26, 40, 52), (22, -44, 50))):
        cv.stroke(spline([(x + dx, y + dy - l / 2), (x + dx + 14, y + dy), (x + dx, y + dy + l / 2)], n=4), INK, 4.2)


def glow(cv, cx, cy, r, col, strength):
    """Soft radial light composited into the canvas (blurred at low resolution, so no hard edge)."""
    from PIL import Image, ImageDraw, ImageFilter
    k = 8
    m = Image.new("L", (W // k, H // k), 0)
    ImageDraw.Draw(m).ellipse(((cx - r) / k, (cy - r * 0.8) / k, (cx + r) / k, (cy + r * 0.8) / k), fill=int(255 * strength))
    m = m.filter(ImageFilter.GaussianBlur(r / k * 0.5)).resize(cv.img.size, Image.BILINEAR)
    lay = Image.new("RGBA", cv.img.size, (*col, 255))
    lay.putalpha(m)
    cv.img.alpha_composite(lay)


def render():
    cv = Canvas(W, H, ss=2, bg=(255, 255, 255, 255))
    kitchen(cv)
    glow(cv, 975, 270, 520, (255, 244, 214), 0.4)            # window light on the set only
    k = 1.55
    # ปิ่น: 3/4 facing right, offering the bowl
    cv.push(700, 440, scale=k)
    figure(cv, "pin", 48 * D2R, "offer", "eager")
    cv.pop()
    # แม่: 3/4 facing left (mirrored), leaning back, palm up
    cv.push(1250, 425, scale=k, flip=True)
    figure(cv, "mom", 58 * D2R, "no_thanks", "meh", lean=-6)
    cv.pop()
    aroma(cv, 890, 640, 1060, 560)
    recoil(cv, 1530, 440)
    table_front(cv)
    img = cv.result().convert("RGB")
    img.save(OUT / "scene_test.png")
    img.resize((320, 180)).save(OUT / "scene_test_320.png")
    return img


if __name__ == "__main__":
    render()
    print("ok")
