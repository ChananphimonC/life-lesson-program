"""Scene A: the 100 m paper-roll folding attempt (10 key frames, 1280x720). Storyboard frames from the existing rig, not a
physical simulation; the failed 11th fold is an illustration of the idea "the thick stack cannot be bent", not a proof."""
from __future__ import annotations

import math
from pathlib import Path

from poc_chars import draw
from stage import *  # noqa: F401,F403
from stage import H, W, block, bowl_side, courtyard, lerp, mini, new, rect, strip
from toon import INK, mix, shade, spline

OUT = Path(__file__).resolve().parent / "scene_a_paper_roll" / "frames"

# ---- poses (joint hints/targets in the character's own frame, see prototype_v2/figure.py) --------------------------------------
P = {
    "rest": "rest",
    "arms_up": dict(R=((-84, 90, 0), (-60, 22, 20)), L=((84, 90, 0), (60, 22, 20)), hands=dict(R=("relaxed", 0), L=("relaxed", 0))),
    "cheer": dict(R=((-96, 80, 0), (-92, 4, 0)), L=((96, 80, 0), (92, 4, 0)), hands=dict(R=("relaxed", 0), L=("relaxed", 0))),
    "push": dict(R=((-64, 140, 30), (-34, 130, 104)), L=((64, 140, 30), (34, 130, 104)), hands=dict(R=("relaxed", 0), L=("relaxed", 0))),
    "point": dict(R=((-72, 120, 30), (-34, 96, 124)), L=((64, 182, -6), (59, 234, 10)), hands=dict(R=("point", 0), L=("relaxed", 0))),
    "hip": dict(R=((-100, 170, -10), (-54, 198, 6)), L=((100, 170, -10), (54, 198, 6)), hands=dict(R=("relaxed", 0), L=("relaxed", 0))),
    "heads": dict(R=((-104, 70, -10), (-40, -6, 14)), L=((104, 70, -10), (40, -6, 14)), hands=dict(R=("relaxed", 0), L=("relaxed", 0))),
    "spread": dict(R=((-112, 126, 0), (-170, 120, 0)), L=((112, 126, 0), (170, 120, 0)), hands=dict(R=("relaxed", 0), L=("relaxed", 0))),
    "cross": dict(R=((-40, 170, 30), (28, 164, 70)), L=((40, 176, 34), (-28, 172, 76)), hands=dict(R=("relaxed", 0), L=("relaxed", 0))),
    "hold_up": dict(R=((-70, 110, 20), (-48, 56, 70)), L=((64, 182, -6), (59, 234, 10)), hands=dict(R=("grip", 0), L=("relaxed", 0))),
}
EX = {
    "pant": dict(open=0.85, lid=0.35, gaze=(0, 2), brow=(8, -3), mouth="o", mp=dict(smile=0, mw=0.7, skew=0, rnd=1, wave=0), open_=0.7,
                 blush=1.1, tilt=5, sweat=True),
    "shout": dict(open=1.15, brow=(8, 8), mouth="open_smile", open_=1.0, blush=1.2, tilt=-3),
    "gloat": dict(open=0.8, lid=0.3, gaze=(3, 0), brow=(-4, 6), mouth="smirk", blush=0.9, tilt=-6),
    "gape": dict(open=1.3, gaze=(0, -1), brow=(13, 10), mouth="o", mp=dict(smile=0, mw=0.8, skew=0, rnd=1, wave=0), open_=1.0,
                 blush=0.3, pupil=0.7),
    "deadpan": dict(open=0.75, lid=0.5, gaze=(0, -2), brow=(-1, 1), mouth="pout", mp=dict(smile=-0.1, mw=0.6, skew=0, rnd=0, wave=0),
                    blush=0.5, tilt=0),
    "yikes": dict(open=1.2, brow=(10, -2), mouth="wavy", mp=dict(smile=0, mw=1.1, skew=0, rnd=0, wave=1), blush=0.3, tilt=4, sweat=True),
    "aha": dict(open=1.18, brow=(9, 8), mouth="open_smile", open_=0.5, blush=1.0, tilt=-6, sparkle=True),
}
EXN = {**EX}


def ex(n):
    return EX.get(n, n) if isinstance(n, str) else n


def dust(cv, x, y, r=1.0, n=4):
    for i in range(n):
        cv.ellipse(x - 26 * r * i, y - 4 * i, 14 * r + 3 * i, 9 * r + 2 * i, (236, 224, 200), ink=None, alpha=170)


def roll_disc(cv, x, y, r):
    cv.ellipse(x, y, r, r, PAPER, ink=INK, lw=2.4, shade_col=PAPER_SH)
    for k in (0.75, 0.52, 0.3):
        cv.ellipse(x, y, r * k, r * k, PAPER, ink=(190, 188, 178), lw=1.2)
    cv.ellipse(x, y, r * 0.12, r * 0.12, (150, 120, 90), ink=INK, lw=1.4)


PAPER_SH = (222, 220, 212)
PAPER = (252, 250, 244)


# ---- shots ----------------------------------------------------------------------------------------------------------------------

def a1(cv):
    """The roll gets away from the villagers. Establishes: the roll is enormous; Ton is the one who started it."""
    courtyard(cv, 300, gate_x=760)
    strip(cv, (330, 735), (760, 300), 100, 0.0, 0.8, creases=16)
    roll_disc(cv, *lerp((330, 735), (760, 300), 0.82), 30)
    dust(cv, *lerp((330, 735), (760, 300), 0.88), 0.5, 3)
    draw(cv, "uean", 240, 470, 20, P["rest"], ex("gape"), k=0.62)
    cv.stroke([(262, 380), (292, 360)], (150, 150, 156), 5)                                  # ladle falls from her hand
    cv.ellipse(296, 356, 10, 6, (176, 182, 190), ink=INK, lw=1.6)
    draw(cv, "chok", 520, 520, 40, P["arms_up"], ex("yikes"), k=0.6, lean=10)                 # running after it
    draw(cv, "ton", 1010, 715, 30, P["point"], ex("aha"), k=1.0, flip=True)


def a2(cv):
    """Reveal of scale: the strip runs through the gate and out of the village. Villagers lined along it."""
    courtyard(cv, 190, gate_x=640, gate_s=0.7)
    strip(cv, (640, 770), (640, 190), 150, 0.0, 0.97, creases=26)
    for i, t in enumerate((0.78, 0.70, 0.62, 0.54, 0.46, 0.38, 0.30, 0.22, 0.15)):
        p = lerp((640, 770), (640, 190), t)
        w = 150 * (1 - t)
        s = 1.7 * (1 - t) + 0.3
        for side in (-1, 1):
            if (i + (side > 0)) % 3 == 2:
                continue
            mini(cv, p[0] + side * (w + 26 * s), p[1] + 14, s, i * 2 + (side > 0), arms="forward", flip=side > 0, expr="o" if i % 4 == 0 else "grin")
    draw(cv, "ton", 330, 735, 30, P["spread"], ex("gape"), k=0.95)
    draw(cv, "chok", 930, 740, -30, P["hip"], ex("gloat"), k=0.8, flip=True)
    cv.stroke([(640, 774), (640, 190)], (255, 255, 255), 2, alpha=0)


def _arc_band(cv, pts, th=16, col=PAPER):
    top = spline(pts, n=14)
    bot = [(x, y + th) for x, y in top]
    cv.fill(top + bot[::-1], col, ink=INK, lw=2.4, shade_col=PAPER_SH, depth=3)


def a3(cv):
    """"Fold one!": the whole line lifts the strip into a big arch and brings the ends together."""
    courtyard(cv, 330, gate_x=1000, gate_s=0.8)
    _arc_band(cv, [(30, 640), (220, 420), (520, 290), (820, 270), (1100, 340), (1250, 520)], 20)
    for i, x in enumerate((140, 270, 420, 590, 760, 930, 1090, 1210)):
        y_top = 640 - (min(abs(x - 700), 600) ** 1.0) * -0.0
        yy = 620 + (i % 2) * 24
        s = 1.05 if i % 2 else 0.9
        mini(cv, x, yy, s, i * 3, arms="cheer", expr="grin" if i % 3 else "o")
    draw(cv, "chok", 620, 700, 0, P["arms_up"], ex("shout"), k=0.85)
    draw(cv, "ton", 1030, 715, -30, P["arms_up"], ex("eager"), k=0.95, flip=True)


def flat(cv, cx, y, w, depth, thick=3, col=PAPER):
    """Paper lying on the ground: top face (w x depth px, seen from above-front) and a thin front edge."""
    x0, x1 = cx - w / 2, cx + w / 2
    cv.fill([(x0, y), (x1, y), (x1 + depth * 0.5, y - depth * 0.6), (x0 + depth * 0.5, y - depth * 0.6)], col, ink=INK, lw=2.2, shade_col=PAPER_SH, depth=3)
    cv.fill([(x0, y), (x1, y), (x1, y + thick), (x0, y + thick)], (214, 212, 202), ink=INK, lw=1.8)


def beam(cv, cx, y, S, width_m, thick_m, len_m, cap=0.0, layers=26):
    """To-scale folded stack: width_m (along the beam), thick_m (height), len_m (depth). S = px per metre."""
    block(cv, cx, y, width_m * S, max(thick_m * S, 4), max(len_m * S, 6), layers=layers, cap=cap)


# Scale reference for every shot below: Ton (1.4 m) = 269 px * k  ->  S = 192 * k px per metre. The roll is assumed 2 m wide
# (NOT the 0.30 m in the v2 script, whose stack would be brick-sized); 100 m x 2 m x 0.1 mm = 16 kg.

def a4(cv):
    """Folds 2-5: the strip is now ~3 m long, 2 m wide and 3 mm thick: a floppy tarp. Aunt Uean stands on one end, arms folded."""
    courtyard(cv, 320, gate_x=250, gate_s=0.7)
    S = 230
    flat(cv, 640, 650, 2 * S, 3.1 * S * 0.8, thick=4)
    strip(cv, (1060, 740), (250, 320), 90, 0.0, 0.45, creases=8)
    draw(cv, "uean", 640, 590, 0, P["cross"], ex("gloat"), k=0.86)
    draw(cv, "ton", 300, 700, 38, P["push"], ex("determined"), k=1.2, lean=8)
    draw(cv, "chok", 1010, 700, -40, P["push"], ex("pant"), k=1.0, flip=True, lean=8)
    for i, x in enumerate((110, 1190)):
        mini(cv, x, 610, 1.6, i + 2, arms="forward", flip=x > 600, expr="o" if i % 2 else "grin")


def a5(cv):
    """Folds 6-8: 0.4 m long, 2 m wide, 2.6 cm thick: a plank. Ton leaps onto it to press it flat, everyone else is wheezing."""
    courtyard(cv, 330, gate_x=1050, gate_s=0.7)
    S = 230
    flat(cv, 640, 660, 2 * S, 0.39 * S * 1.6, thick=7)
    cv.ellipse(640, 664, 200, 14, (0, 0, 0), alpha=40)
    draw(cv, "ton", 640, 470, 20, P["cheer"], ex("shout"), k=1.2, lean=-14, shadow=False)
    draw(cv, "chok", 190, 705, 40, P["push"], ex("pant"), k=1.0, lean=14)
    draw(cv, "uean", 1090, 715, -30, P["push"], ex("shout"), k=1.0, flip=True, lean=10)
    for i, x in enumerate((60, 1230, 360)):
        mini(cv, x, 585, 1.5, i + 4, arms="forward", flip=x > 600, squash=0.2, expr="o")


def a6(cv):
    """Fold 10 (to scale): a 2 m beam only 10 cm high and 10 cm deep. Ton, who wanted to prove it was impossible, balances on the result."""
    courtyard(cv, 330, gate_x=250, gate_s=0.7)
    S = 290
    beam(cv, 640, 660, S, 2.0, 0.102, 0.098, layers=30)
    draw(cv, "ton", 640, 632, 0, P["cheer"], ex("gape"), k=1.4, shadow=False)
    for i, (x, y) in enumerate(((150, 640), (330, 600), (950, 600), (1130, 640))):
        mini(cv, x, y, 1.6, i + 1, arms="cheer" if i % 2 else "forward", squash=0.45 if i % 2 == 0 else 0, expr="grin")
    for k in range(26):                                                                         # festival flags thrown up
        x, y = 60 + k * 46, 120 + (k * 53) % 200
        cv.fill([(x, y), (x + 14, y + 6), (x + 3, y + 20)], [(236, 84, 90), (250, 196, 70), (96, 176, 120), (84, 150, 210)][k % 4],
                ink=INK, lw=1.2)
    draw(cv, "uean", 90, 710, 30, P["rest"], ex("pant"), k=1.05)
    draw(cv, "chok", 1190, 710, -30, P["hip"], ex("pant"), k=1.0, flip=True)


def a7(cv):
    """Fold 11: everyone pushes along the long edge of the beam; the outer layers puff out along it and the beam refuses to turn over.
    Aunt Uean bounces off. (Illustration of the idea, not a simulation.)"""
    courtyard(cv, 330, gate_x=1100, gate_s=0.7)
    S = 290
    beam(cv, 640, 650, S, 2.0, 0.102, 0.098, cap=0.55, layers=30)
    draw(cv, "uean", 780, 400, -10, P["arms_up"], ex("gape"), k=0.9, lean=-24, shadow=False)           # boing
    for i in range(3):
        cv.stroke([(780 + (i - 1) * 24, 420 + 6 * i), (780 + (i - 1) * 30, 470 + 6 * i)], (255, 190, 90), 4)
    draw(cv, "chok", 190, 705, 40, P["push"], ex("yikes"), k=1.0)
    draw(cv, "ton", 1100, 715, -30, P["heads"], ex("gape"), k=1.2, flip=True)
    for i, x in enumerate((330, 470, 800, 940)):
        mini(cv, x, 700, 1.7, i + 6, arms="forward", flip=x > 640, expr="o")


def a8(cv):
    """Ton makes the decision: STOP. He is the one who protects Uncle Chok's roll."""
    courtyard(cv, 330, gate_x=1100, gate_s=0.7)
    S = 290
    beam(cv, 860, 650, S, 2.0, 0.102, 0.098, cap=0.35, layers=30)
    draw(cv, "uean", 980, 330, -10, P["arms_up"], ex("yikes"), k=0.8, lean=10, shadow=False)           # frozen in mid-air above it
    draw(cv, "chok", 1170, 705, -40, P["hip"], ex("deadpan"), k=0.9, flip=True)
    p = dict(R=((-36, 140, 50), (-14, 128, 102)), L=((64, 182, -6), (59, 234, 10)), hands=dict(R=("open", 192), L=("relaxed", 0)), late="R")
    draw(cv, "ton", 300, 735, 18, p, ex("shout"), k=1.55)
    for i in range(3):
        cv.stroke([(560 + i * 18, 520), (580 + i * 18, 490)], (255, 190, 90), 5)


def a9(cv):
    """Insight: Ton compares string loops around the end of the stack. The lens inset shows why the next fold cannot be made."""
    courtyard(cv, 330, gate_x=240, gate_s=0.7, flags=False)
    beam(cv, 1010, 700, 250, 2.0, 0.102, 0.098, layers=30)
    cx, cy, R = 600, 300, 215
    cv.ellipse(cx, cy, R + 12, R + 12, (232, 186, 92), ink=INK, lw=3.4)
    cv.ellipse(cx, cy, R, R, (236, 246, 252), ink=INK, lw=2.4)
    arc = lambda r: [(cx - 40 + r * math.sin(a_), cy - r * math.cos(a_)) for a_ in [j * math.pi / 14 for j in range(0, 15)]]
    for i in range(6):                                                    # nested loops = the paper layers
        r = 30 + i * 28
        path = [(cx - 190, cy - r), (cx - 40, cy - r)] + arc(r)[1:] + [(cx - 40, cy + r), (cx - 190, cy + r)]
        cv.stroke(path, INK, 6)
        cv.stroke(path, PAPER, 3.6)
    cv.stroke(arc(30), (240, 190, 40), 6)                                  # short string on the inner loop
    cv.stroke(arc(30 + 5 * 28), (240, 190, 40), 6)                         # long string on the outer loop
    cv.stroke([(cx - 150, cy + 150), (cx - 250, cy + 215)], (150, 98, 66), 14)
    cv.stroke([(cx - 150, cy + 150), (cx - 250, cy + 215)], (232, 186, 92), 8)
    draw(cv, "ton", 250, 735, 25, P["hold_up"], ex("aha"), k=1.1)
    draw(cv, "chok", 1170, 715, -40, P["hip"], ex("aha"), k=0.75, flip=True)


def a10(cv):
    """Payoff: the plan has backfired. Ton lies on his back with his head on the paper beam like a pillow; Grandma walks in with the envelope."""
    courtyard(cv, 330, gate_x=160, gate_s=0.7)
    S = 290
    beam(cv, 760, 660, S, 2.0, 0.102, 0.098, layers=30)
    cv.push(430, 640, rot=90)                                                                      # lying on the ground, head toward the beam
    draw(cv, "ton", 0, 255, 0, P["spread"], ex("deadpan"), k=1.0, shadow=False)
    cv.pop()
    draw(cv, "kaew", 1090, 715, -30, P["cross"], ex("gloat"), k=1.2, flip=True)
    rect(cv, 985, 545, 1055, 597, (186, 132, 82), lw=2.4, shade_col=(160, 110, 66))              # sealed brown envelope held up
    cv.stroke([(985, 545), (1020, 573), (1055, 545)], INK, 2.0)
    cv.ellipse(1020, 573, 6, 6, (210, 60, 54), ink=INK, lw=1.4)
    draw(cv, "chok", 190, 700, 40, P["hip"], ex("deadpan"), k=0.8)
    draw(cv, "uean", 90, 705, 30, P["cross"], ex("gloat"), k=0.8)


SHOTS = [("A01", a1, 3.5, "ม้วนหนีไปเอง"), ("A02", a2, 3.5, "กระดาษยาวออกนอกหมู่บ้าน"), ("A03", a3, 3.5, "พับหนึ่ง!"),
         ("A04", a4, 3.0, "ผ้าใบกระดาษ"), ("A05", a5, 3.5, "แผ่นกระดาน ต้นกระโดดทับ"), ("A06", a6, 3.5, "สิบครั้ง! ได้คานกระดาษ"),
         ("A07", a7, 3.5, "ครั้งที่สิบเอ็ด ไม่ยอมงอ"), ("A08", a8, 3.0, "หยุด!"), ("A09", a9, 4.5, "วงนอกยาวกว่าวงใน"),
         ("A10", a10, 4.0, "แผนพังบนหลักฐานของตัวเอง")]

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
