"""Scene B: the 410-bowl wager as visual comedy (8 key frames, 1280x720). Growth is shown by physical arrangement: tower counts,
crates and space, not labels. 1+2+...+128 = 255 and the last crate holds 155 of the 256 slots needed (101 slots stay empty)."""
from __future__ import annotations

import math
from pathlib import Path

from poc_chars import draw
from scene_a import EX, P, ex  # noqa: F401  (same poses/expressions as scene A)
from stage import PAPER, H, W, block, bowl_side, bowl_tower, bowl_top, kitchen, mini, new, rect
from toon import INK, ellipse_pts, mix, shade, spline

OUT = Path(__file__).resolve().parent / "scene_b_bowls" / "frames"
WOOD = (176, 128, 92)
EXTRA = dict(P)
EXTRA["carry"] = dict(R=((-70, 150, 24), (-40, 140, 90)), L=((70, 150, 24), (40, 140, 90)), hands=dict(R=("cup", -6), L=("cup", 6)),
                      bowl=(0, 140, 92))
EXTRA["scrub"] = dict(R=((-70, 150, 24), (-36, 150, 84)), L=((70, 150, 24), (36, 160, 88)), hands=dict(R=("relaxed", 0), L=("relaxed", 0)))
EXTRA["tower_hold"] = dict(R=((-70, 120, 20), (-40, 70, 60)), L=((70, 120, 20), (40, 70, 60)), hands=dict(R=("relaxed", 0), L=("relaxed", 0)))
EXTRA["ladle_point"] = dict(R=((-66, 120, 30), (-30, 96, 120)), L=((64, 182, -6), (59, 234, 10)), hands=dict(R=("grip", 0), L=("relaxed", 0)),
                            grip=dict(side="R", item="spoon", tip=(-10, 74, 160)), late="R")


def counter(cv, y, x0=-20, x1=W + 20, depth=70):
    cv.fill([(x0, y), (x1, y), (x1 - 40, y - depth), (x0 + 40, y - depth)], (206, 160, 118), ink=INK, lw=2.4, shade_col=(188, 142, 102))
    rect(cv, x0, y, x1, y + 28, WOOD, shade_col=shade(WOOD, 0.84))
    for x in range(int(x0) + 60, int(x1), 180):
        cv.stroke([(x, y + 4), (x, y + 26)], shade(WOOD, 0.7), 2)


def sink(cv, x, y, w=300, moon=False):
    rect(cv, x - w / 2, y - 70, x + w / 2, y + 4, (190, 200, 208), shade_col=(160, 172, 182))
    cv.ellipse(x, y - 70, w / 2 - 6, 22, (120, 160, 200), ink=INK, lw=2.2)
    cv.ellipse(x, y - 70, w / 2 - 22, 15, (150, 190, 226), ink=None)
    if moon:
        cv.ellipse(x + 20, y - 70, 20, 8, (250, 244, 214), ink=None)
        cv.stroke([(x - 6, y - 70), (x + 46, y - 70)], (250, 244, 214), 1.4, alpha=160)
    for bx, by, br in ((-70, -76, 10), (-40, -82, 7), (30, -80, 9), (80, -72, 6), (-10, -88, 5)):
        cv.ellipse(x + bx, y + by, br, br * 0.9, (240, 250, 255), ink=INK, lw=1.2, alpha=230)
    cv.stroke([(x + w / 2 - 36, y - 70), (x + w / 2 - 36, y - 130), (x + w / 2 - 80, y - 130)], (160, 168, 176), 9)


def towers_row(cv, x0, y, n_towers, per=8, w=40, gap=46, wob=0.0):
    for i in range(n_towers):
        bowl_tower(cv, x0 + i * gap, y, w, per, wob=wob * ((i % 3) - 1))


def b1(cv):
    """One bowl. Ton, on his paper stool, is unimpressed; Aunt Uean sets the single bowl down like a card player."""
    kitchen(cv)
    counter(cv, 520)
    sink(cv, 330, 520)
    block(cv, 330, 652, 150, 56, 70, layers=10)
    draw(cv, "ton", 330, 598, 25, EXTRA["scrub"], ex("deadpan"), k=0.95)
    bowl_side(cv, 760, 518, 46)
    draw(cv, "uean", 980, 700, -30, EXTRA["hip"] if "hip" in EXTRA else P["hip"], ex("gloat"), k=0.95, flip=True)
    cv.stroke([(840, 440), (870, 466)], (255, 255, 255), 0, alpha=0)


def b2(cv):
    """One, two ... and she is carrying four. Counter holds exactly 1 + 2 bowls. Ton starts to suspect something."""
    kitchen(cv)
    counter(cv, 520)
    sink(cv, 250, 520)
    bowl_side(cv, 640, 518, 46)
    bowl_tower(cv, 720, 518, 46, 2)
    block(cv, 250, 652, 150, 56, 70, layers=10)
    draw(cv, "ton", 250, 598, 30, EXTRA["scrub"], ex("yikes"), k=0.95)
    draw(cv, "uean", 1060, 700, -30, EXTRA["tower_hold"], ex("gloat"), k=0.95, flip=True)
    bowl_tower(cv, 1040, 360, 46, 4, wob=2)                                  # the next group: 4 bowls on her head


def b3(cv):
    """Counter: 1, 2, 4 (small), then 8 (one tower) and 16 (two towers). She carries the next 8 on her head."""
    kitchen(cv)
    counter(cv, 530)
    bowl_side(cv, 440, 528, 40)
    bowl_tower(cv, 500, 528, 40, 2)
    bowl_tower(cv, 560, 528, 40, 4)
    bowl_tower(cv, 650, 528, 44, 8, wob=1.2)
    bowl_tower(cv, 760, 528, 44, 8, wob=-1.4)
    bowl_tower(cv, 820, 528, 44, 8, wob=1.8)
    sink(cv, 200, 530, w=260)
    block(cv, 200, 662, 150, 56, 70, layers=10)
    draw(cv, "ton", 200, 608, 20, EXTRA["scrub"], ex("gape"), k=0.95)
    draw(cv, "uean", 1090, 700, -30, EXTRA["tower_hold"], ex("gloat"), k=0.95, flip=True)
    bowl_tower(cv, 1070, 330, 44, 8, wob=3.5)


def b4(cv):
    """32 and 64. Counter: 1..16 (31 bowls: three towers of 8 and one of 7) + the 32 group (4 towers). Floor: the 64 group (8 towers).
    Children wobble past with towers on their heads."""
    kitchen(cv)
    counter(cv, 470)
    for i, n in enumerate((8, 8, 8, 7)):
        bowl_tower(cv, 60 + i * 56, 466, 40, n)
    for i in range(4):
        bowl_tower(cv, 330 + i * 60, 466, 40, 8, wob=1.0 * ((i % 3) - 1))
    for r, yy in enumerate((620, 700)):
        for i in range(4):
            bowl_tower(cv, 90 + i * 88 + (r % 2) * 40, yy, 44, 8, wob=0.8 * ((i % 3) - 1))
    for x, y, i in ((760, 560, 3), (1040, 600, 5)):
        mini(cv, x, y, 1.7, i, arms="up", expr="o")
        bowl_tower(cv, x, y - 114, 40, 8, wob=4)
    draw(cv, "ton", 640, 480, 0, EXTRA["tower_hold"], ex("yikes"), k=0.8, shadow=False)
    draw(cv, "uean", 1130, 715, -30, EXTRA["ladle_point"], ex("shout"), k=0.85, flip=True)


def b5(cv):
    """128: front row = the 128 group as 8 towers of 16; back row = everything before it (127 bowls: seven towers of 16 and one of 15).
    Total 255. Ton is dwarfed behind them."""
    kitchen(cv)
    draw(cv, "ton", 560, 560, 10, P["cheer"], ex("pant"), k=0.95, shadow=False)
    for i in range(8):                                                                       # back row (127)
        bowl_tower(cv, 60 + i * 130, 600, 50, 15 if i == 7 else 16, wob=1.0 * ((i % 3) - 1))
    for i in range(8):                                                                       # front row (the 128 group)
        bowl_tower(cv, 110 + i * 130, 712, 50, 16, wob=1.0 * ((i % 3) - 1))
    cv.stroke([(40, 716), (1200, 716)], (255, 230, 120), 3, alpha=0)
    draw(cv, "uean", 1160, 700, -30, EXTRA["ladle_point"], ex("gloat"), k=0.78, flip=True)
    draw(cv, "chok", 140, 500, 30, P["hip"], ex("gape"), k=0.55)


def _crate(cv, x, y, cols, rows, n, s=14, ghost=True, dashed=False):
    """Crate seen from a high oblique angle: grid of slots as ellipses, n of them filled (row by row)."""
    w, h = cols * s, rows * s * 0.55
    col = (186, 140, 100)
    cv.fill([(x - 6, y - 6), (x + w + 6, y - 6), (x + w + 6, y + h + 6), (x - 6, y + h + 6)], col, ink=INK, lw=2.2, shade_col=shade(col, 0.82))
    cv.fill([(x - 1, y - 1), (x + w + 1, y - 1), (x + w + 1, y + h + 1), (x - 1, y + h + 1)], (150, 110, 78), ink=None)
    k = 0
    for r in range(rows):
        for c in range(cols):
            cx, cy = x + c * s + s / 2, y + r * s * 0.55 + s * 0.28
            if k < n:
                cv.ellipse(cx, cy, s * 0.43, s * 0.3, (250, 250, 246), ink=INK, lw=1.0)
                cv.ellipse(cx, cy, s * 0.26, s * 0.18, (170, 200, 232), ink=None)
            elif ghost:
                cv.ellipse(cx, cy, s * 0.42, s * 0.29, (110, 82, 60), ink=(214, 180, 150), lw=1.2, alpha=170)
            k += 1
    if dashed:
        for i in range(0, int(w + 12), 16):
            cv.stroke([(x - 6 + i, y - 12), (x - 6 + min(i + 8, w + 12), y - 12)], (255, 90, 80), 3)
            cv.stroke([(x - 6 + i, y + h + 12), (x - 6 + min(i + 8, w + 12), y + h + 12)], (255, 90, 80), 3)
        for j in range(0, int(h + 24), 16):
            cv.stroke([(x - 12, y - 12 + j), (x - 12, y - 12 + min(j + 8, h + 24))], (255, 90, 80), 3)
            cv.stroke([(x + w + 12, y - 12 + j), (x + w + 12, y - 12 + min(j + 8, h + 24))], (255, 90, 80), 3)
    return w, h


def b6(cv):
    """Clarity shot (high oblique): crates double in size left to right. The ninth crate is outlined for 256 slots but holds 155."""
    kitchen(cv, horizon=140)
    cv.fill([(0, 140), (W, 140), (W, H), (0, H)], (150, 112, 82), ink=None)
    s = 18
    x = 26
    seq = [(1, 1, 1), (2, 1, 2), (2, 2, 4), (4, 2, 8), (4, 4, 16), (8, 4, 32), (8, 8, 64)]
    y0 = 175
    for cols, rows, n in seq:
        w, h = _crate(cv, x, y0, cols, rows, n, s=s)
        x += w + 28
    _crate(cv, 26, 330, 16, 8, 128, s=s)
    # the ninth: 16 x 16 slots, 155 filled
    _crate(cv, 400, 330, 16, 16, 155, s=s, dashed=True)
    draw(cv, "ton", 840, 715, 25, P["point"], ex("gape"), k=0.8, flip=True)
    draw(cv, "uean", 1050, 715, -30, P["cross"], ex("gloat"), k=0.8, flip=True)


def b7(cv):
    """Ton looks up at the last, short tower; Aunt Uean smiles and points her ladle at the sink. 'Wash.'"""
    kitchen(cv)
    counter(cv, 560)
    for i in range(10):
        bowl_tower(cv, 400 + i * 66, 556, 40, 8)
    for i in range(9):
        bowl_tower(cv, 433 + i * 66, 640, 40, 8)
    bowl_tower(cv, 433 + 9 * 66, 640, 40, 3)
    sink(cv, 190, 560, w=280)
    block(cv, 190, 700, 150, 56, 70, layers=10)
    draw(cv, "ton", 190, 646, 20, EXTRA["scrub"], ex({"open": 1.1, "lid": 0.0, "gaze": (3, -2), "brow": (10, -6), "mouth": "wavy",
                                                     "mp": dict(smile=-0.1, mw=1.0, skew=0, rnd=0, wave=1), "blush": 0.8, "tilt": 6}), k=1.0)
    draw(cv, "uean", 1060, 715, -30, EXTRA["ladle_point"], ex("gloat"), k=1.1, flip=True)


def b8(cv):
    """Last image: Ton scrubs, the moon trembles in the basin, Uncle Chok arrives with the bamboo for the night's second job."""
    kitchen(cv)
    counter(cv, 560)
    sink(cv, 500, 560, w=420, moon=True)
    block(cv, 500, 690, 170, 60, 70, layers=10)
    draw(cv, "ton", 500, 634, 10, EXTRA["scrub"], ex("deadpan"), k=1.05, lean=6)
    for i in range(10):
        bowl_tower(cv, 790 + i * 40, 556, 36, 8)
    draw(cv, "chok", 1140, 715, -35, EXTRA["hip"] if "hip" in EXTRA else P["hip"], ex("gloat"), k=1.0, flip=True)
    for i in range(4):                                                                                # bamboo sticks leaning on him
        cv.stroke([(1050 + i * 14, 710), (1000 + i * 26, 380)], (186, 168, 96), 9)
        cv.stroke([(1050 + i * 14, 710), (1000 + i * 26, 380)], (216, 196, 120), 5)


SHOTS = [("B01", b1, 3.0, "ชามใบเดียว"), ("B02", b2, 3.0, "สอง สี่"), ("B03", b3, 3.5, "หอชามสูงกว่าหัว"), ("B04", b4, 3.5, "พื้นเริ่มเต็ม"),
         ("B05", b5, 3.5, "ต้นจมในกองชาม"), ("B06", b6, 5.0, "ผังลัง: ช่องที่เก้าไม่เต็ม"), ("B07", b7, 3.5, "ป้า...ล้าง"),
         ("B08", b8, 4.0, "ดวงจันทร์ในอ่าง")]

if __name__ == "__main__":
    import sys
    OUT.mkdir(parents=True, exist_ok=True)
    want = set(sys.argv[1:])
    for name, fn, _, _ in SHOTS:
        if want and name not in want:
            continue
        cv = new()
        fn(cv)
        cv.result().convert("RGB").save(OUT / f"{name}.png")
        print(name, flush=True)
