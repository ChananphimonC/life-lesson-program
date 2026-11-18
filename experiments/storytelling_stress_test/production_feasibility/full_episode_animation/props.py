"""Backgrounds, props and small effects for the episode (all procedural, drawn with the rig's Canvas)."""
from __future__ import annotations

import math
import random

from engine import *  # noqa: F401,F403
from toon import chain

PAPER = (252, 250, 244)
PAPER_SH = (222, 220, 212)
STRING = (240, 190, 40)
CHALK = (250, 246, 232)


def rect(cv, x0, y0, x1, y1, col, ink=INK, lw=2.4, shade_col=None):
    cv.fill([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], col, ink=ink, lw=lw, shade_col=shade_col, depth=5)


def band(cv, y0, y1, c0, c1, n=18, x0=-300, x1=W + 300):
    for i in range(n):
        t = i / (n - 1)
        rect(cv, x0, y0 + (y1 - y0) * i / n, x1, y0 + (y1 - y0) * (i + 1) / n + 2, mix(c0, c1, t), ink=None)


# --------------------------------------------------------------------------------------------------------------- backgrounds
SKY = {"day": ((138, 200, 236), (255, 236, 196)), "gold": ((140, 180, 226), (255, 206, 150)), "dusk": ((70, 90, 150), (250, 170, 130)),
       "night": ((20, 28, 62), (70, 66, 110))}


def moon(cv, x, y, r=34, phase=0.5, col=(250, 244, 214)):
    """phase 0.5 = first quarter (right half lit)."""
    cv.ellipse(x, y, r, r, (200, 205, 225), ink=None, alpha=90 if phase < 1 else 0)
    if phase >= 1:
        cv.ellipse(x, y, r, r, col, ink=None)
        return
    cv.fill(ellipse_pts(x, y, r, r, n=40, a0=-90, a1=90), col, ink=None)
    cv.fill(ellipse_pts(x, y, r * (1 - 2 * phase) if phase < 0.5 else r * (2 * phase - 1), r, n=40, a0=-90, a1=90 if phase >= 0.5 else 270),
            col if phase >= 0.5 else (200, 205, 225), ink=None, alpha=255 if phase >= 0.5 else 0)


def flags(cv, y0, n=18, t=0.0, x0=-40, x1=W + 40, sag=18):
    cols = [(236, 84, 90), (250, 196, 70), (96, 176, 120), (84, 150, 210), (230, 130, 190)]
    pts = [(x0 + (x1 - x0) * i / 40, y0 + sag * math.sin(math.pi * i / 40)) for i in range(41)]
    cv.stroke(pts, (120, 96, 80), 2.0)
    for k in range(n):
        i = int(2 + k * 38 / n)
        x, y = pts[i]
        sw = 3 * math.sin(t * 3 + k)
        cv.fill([(x - 11, y), (x + 11, y), (x + sw, y + 26)], cols[k % 5], ink=INK, lw=1.6)


def courtyard(cv, horizon=300, tod="day", gate_x=640, gate_s=1.0, t=0.0, show_flags=True, ground=((212, 184, 138), (190, 156, 108)), moon_pos=(1090, 100),
              moon_phase=0.5, x0=-300, x1=W + 300):
    c0, c1 = SKY[tod]
    band(cv, -200, horizon, c0, c1, 26, x0, x1)
    if tod in ("day", "gold", "dusk"):
        moon(cv, *moon_pos, r=36, phase=moon_phase)
    else:
        moon(cv, *moon_pos, r=40, phase=moon_phase, col=(252, 248, 224))
        rnd = random.Random(3)
        for _ in range(40):
            cv.ellipse(rnd.uniform(0, W), rnd.uniform(0, horizon - 40), 1.6, 1.6, (255, 255, 235), ink=None, alpha=int(150 + 100 * math.sin(t * 2 + _)))
    tree = (122, 170, 112) if tod != "night" else (40, 70, 70)
    for i in range(16):
        x = i * 100 - 80
        cv.ellipse(x, horizon - 12, 70, 34 + (i % 3) * 8, tree, ink=None)
        cv.ellipse(x + 30, horizon - 6, 60, 26, shade(tree, 0.9), ink=None)
    px = 1040
    wall = (250, 244, 228) if tod != "night" else (150, 150, 170)
    cv.fill([(px - 70, horizon), (px - 50, horizon - 70), (px + 50, horizon - 70), (px + 70, horizon)], wall, ink=INK, lw=2)
    cv.fill([(px - 36, horizon - 70), (px - 24, horizon - 140), (px + 24, horizon - 140), (px + 36, horizon - 70)], shade(wall, 0.97), ink=INK, lw=2)
    cv.fill([(px - 14, horizon - 140), (px, horizon - 230), (px + 14, horizon - 140)], (236, 190, 90), ink=INK, lw=2)
    rect(cv, x0, horizon - 38, x1, horizon + 4, (240, 226, 196) if tod != "night" else (150, 140, 150), lw=2, shade_col=(222, 206, 172))
    s, gx = gate_s, gate_x
    for dx in (-84, 84):
        rect(cv, gx + dx * s - 20 * s, horizon - 130 * s, gx + dx * s + 20 * s, horizon + 4, (196, 70, 60), shade_col=(166, 52, 46))
    rect(cv, gx - 120 * s, horizon - 168 * s, gx + 120 * s, horizon - 128 * s, (196, 70, 60), shade_col=(166, 52, 46))
    cv.fill([(gx - 150 * s, horizon - 168 * s), (gx, horizon - 226 * s), (gx + 150 * s, horizon - 168 * s)], (236, 168, 60), ink=INK, lw=2.4,
            shade_col=(214, 140, 44))
    cv.fill([(gx - 64 * s, horizon + 4), (gx - 64 * s, horizon - 80 * s), (gx, horizon - 108 * s), (gx + 64 * s, horizon - 80 * s), (gx + 64 * s, horizon + 4)],
            (150, 196, 120) if tod != "night" else (50, 90, 70), ink=INK, lw=2)
    g0, g1 = ground
    for i in range(14):
        tt = i / 13
        y0 = horizon + 4 + (900 - horizon) * (tt ** 1.6)
        y1 = horizon + 4 + (900 - horizon) * (((i + 1) / 13) ** 1.6) + 2
        rect(cv, x0, y0, x1, y1, mix(g0, g1, tt), ink=None)
    if show_flags:
        flags(cv, 54, 17, t)
        flags(cv, 112, 14, t + 1, sag=14)
    if tod in ("dusk", "night"):                       # festival bulbs
        for k in range(14):
            x = 20 + k * 92
            cv.ellipse(x, 150 + 12 * math.sin(k), 6, 6, (255, 226, 130), ink=None)
            cv.ellipse(x, 150 + 12 * math.sin(k), 16, 16, (255, 226, 130), ink=None, alpha=60)


def shop(cv, t=0.0, x=700, y=560, s=1.3):
    """Corner shop (ร้านชำ) facade, drawn at scale s about (x, y) = centre of the counter's foot. Counter: shop_counter()."""
    cv.push(x, y, scale=s)
    x = y = 0
    rect(cv, x - 330, y - 330, x + 330, y + 10, (236, 214, 170), shade_col=(216, 190, 146))
    rect(cv, x - 290, y - 250, x + 80, y - 40, (60, 52, 56), shade_col=(44, 38, 42))
    for k, cc in enumerate(((236, 110, 100), (96, 160, 210), (250, 200, 80), (120, 190, 130))):
        for j in range(3):
            rect(cv, x - 270 + j * 118 + 8, y - 234 + (k % 2) * 4, x - 270 + j * 118 + 8 + 66, y - 190, cc, lw=1.6)
    for k in range(7):
        cv.fill([(x - 340 + k * 100, y - 330), (x - 240 + k * 100, y - 330), (x - 240 + k * 100 - 14, y - 266), (x - 340 + k * 100 - 14, y - 266)],
                (232, 90, 84) if k % 2 else (252, 244, 232), ink=INK, lw=2)
    rect(cv, x + 150, y - 230, x + 320, y - 60, (60, 52, 56), shade_col=(44, 38, 42))
    cv.stroke([(x + 235, y - 230), (x + 235, y - 60)], INK, 3)
    cv.pop()


def shop_counter(cv, x=700, y=560, s=1.3):
    """Counter front strips (draw AFTER the characters standing behind it) and the noodle-window sill."""
    cv.push(x, y, scale=s)
    rect(cv, -310, -40, 100, 10, (186, 134, 92), shade_col=(160, 112, 76))
    rect(cv, -320, -62, 110, -36, (214, 164, 118), shade_col=(190, 142, 98))
    rect(cv, 140, -62, 330, -44, (214, 164, 118), shade_col=(190, 142, 98))
    rect(cv, 140, -44, 330, 10, (186, 134, 92), shade_col=(160, 112, 76))
    cv.pop()


def kitchen(cv, t=0.0):
    band(cv, -100, 380, (40, 52, 86), (96, 84, 100), 20)
    band(cv, 380, 900, (170, 130, 98), (132, 96, 70), 12)
    for xx in (120, 360, 600, 840, 1080):
        rect(cv, xx - 90, 150, xx + 90, 162, (120, 86, 60))
        for k in range(3):
            cv.ellipse(xx - 54 + k * 54, 130, 22, 20, (176, 182, 190), ink=INK, lw=2, shade_col=(142, 150, 160))
    for xx in (200, 700, 1000):
        cv.stroke([(xx, 0), (xx, 36)], INK, 2)
        sw = math.sin(t * 1.5 + xx) * 2
        cv.ellipse(xx + sw, 52, 22, 20, (255, 226, 140), ink=INK, lw=2)
        cv.ellipse(xx + sw, 52, 60, 60, (255, 226, 140), ink=None, alpha=28)
    rect(cv, 1000, 190, 1200, 330, (28, 40, 78), shade_col=(18, 28, 60))
    moon(cv, 1100, 252, r=30, phase=0.5)
    cv.stroke([(1100, 190), (1100, 330)], (120, 86, 60), 4)
    cv.stroke([(1000, 260), (1200, 260)], (120, 86, 60), 4)


def counter(cv, y, x0=-40, x1=W + 40, depth=70):
    cv.fill([(x0, y), (x1, y), (x1 - 40, y - depth), (x0 + 40, y - depth)], (206, 160, 118), ink=INK, lw=2.4, shade_col=(188, 142, 102))
    rect(cv, x0, y, x1, y + 28, (176, 128, 92), shade_col=(148, 106, 76))


def sink(cv, x, y, w=300, moon_on=False, t=0.0):
    rect(cv, x - w / 2, y - 70, x + w / 2, y + 4, (190, 200, 208), shade_col=(160, 172, 182))
    cv.ellipse(x, y - 70, w / 2 - 6, 22, (120, 160, 200), ink=INK, lw=2.2)
    cv.ellipse(x, y - 70, w / 2 - 22, 15, (150, 190, 226), ink=None)
    if moon_on:
        for i in range(5):
            cv.stroke([(x + 4 - 22 + i * 12 + 3 * math.sin(t * 5 + i), y - 70 + (i - 2) * 1.5 + 0.8 * math.sin(t * 6 + i)),
                       (x + 4 - 6 + i * 12, y - 70 + (i - 2) * 1.5)], (250, 244, 214), 3 + (i % 2), alpha=210)
    for k, (bx, by, br) in enumerate(((-70, -76, 10), (-40, -82, 7), (30, -80, 9), (80, -72, 6), (-10, -88, 5))):
        bb = 1 + 0.12 * math.sin(t * 2 + k)
        cv.ellipse(x + bx, y + by - 2 * math.sin(t + k), br * bb, br * 0.9 * bb, (240, 250, 255), ink=INK, lw=1.2, alpha=230)
    cv.stroke([(x + w / 2 - 36, y - 70), (x + w / 2 - 36, y - 130), (x + w / 2 - 80, y - 130)], (160, 168, 176), 9)


# ------------------------------------------------------------------------------------------------------------------ paper
def rot_pts(pts, cx, cy, ang):
    c, s = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    return [(cx + (x - cx) * c - (y - cy) * s, cy + (x - cx) * s + (y - cy) * c) for x, y in pts]


def sheet(cv, cx, cy, w, h, ang=0.0, alpha=255, col=PAPER, edge=None):
    pts = rot_pts([(cx - w / 2, cy - h / 2), (cx + w / 2, cy - h / 2), (cx + w / 2, cy + h / 2), (cx - w / 2, cy + h / 2)], cx, cy, ang)
    cv.fill(pts, col, ink=edge or INK, lw=2.0, shade_col=PAPER_SH, depth=2.5, alpha=alpha)


def ribbon(cv, pts, th, col=PAPER, ink=INK, lw=2.0):
    """A thick band along a polyline (side view of a sheet or a stack of sheets)."""
    top = spline(pts, n=10) if len(pts) > 2 else pts
    bot = [(x, y - th) for x, y in top]
    cv.fill(top + bot[::-1], col, ink=ink, lw=lw)


def table_paper(cv, cx, cy, w, h, folds, prog, alt0=True, depth=0.42, lift_k=0.35, drift=False):
    """Paper on a table seen from the front-above. folds = folds already done, prog = progress of the next fold (0 = none).
    Fold k halves the width (k even) or the height (k odd), so an A4 sheet folds in alternating directions."""
    W0, H0 = w, h
    cw, ch = W0, H0
    for k in range(folds):
        if drift:                                                    # the stack stays where the flap landed (no snap to the centre)
            if k % 2 == 0:
                cx += cw / 4
            else:
                cy += ch * depth / 4
        if k % 2 == 0:
            cw /= 2
        else:
            ch /= 2
    layers = 2 ** folds
    th = max(1.5, 0.143 * 2 ** folds)                                # to scale: 1.43 px per mm, 0.1 mm per layer
    x0, x1 = cx - cw / 2, cx + cw / 2
    y0, y1 = cy - ch * depth / 2, cy + ch * depth / 2
    # stack body (side thickness) + top; while a fold is under way only the half that stays has a side
    bx0 = (cx if folds % 2 == 0 else x0) if (prog > 0 and drift) else x0
    cv.fill([(bx0, y1), (x1, y1), (x1, y1 + th), (bx0, y1 + th)], (214, 212, 202), ink=INK, lw=1.8)
    top_pts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    if prog <= 0:
        cv.fill(top_pts, PAPER, ink=INK, lw=2.2, shade_col=PAPER_SH, depth=2)
        return
    # the next fold: left half (or the far half) rotates over
    k = folds
    if k % 2 == 0:                                                   # fold left half over the right half about the vertical centre line
        xm = cx
        cv.fill([(xm, y0), (x1, y0), (x1, y1), (xm, y1)], PAPER, ink=INK, lw=2.2, shade_col=PAPER_SH, depth=2)
        a = math.pi * prog
        fx = xm + (x0 - xm) * math.cos(a)
        lift = math.sin(a) * ch * lift_k
        back = prog > 0.5
        cv.fill([(xm, y0 - lift), (fx, y0 - lift * 1.1), (fx, y1 - lift * 1.1 + 0), (xm, y1 - lift)], PAPER_SH if back else PAPER, ink=INK, lw=2.2)
    else:                                                            # fold the far half toward the viewer
        ym = cy
        cv.fill([(x0, ym), (x1, ym), (x1, y1), (x0, y1)], PAPER, ink=INK, lw=2.2, shade_col=PAPER_SH, depth=2)
        a = math.pi * prog
        fy = ym + (y0 - ym) * math.cos(a)
        lift = math.sin(a) * cw * 0.12
        cv.fill([(x0, ym - lift), (x1, ym - lift), (x1, fy - lift), (x0, fy - lift)], PAPER_SH if prog > 0.5 else PAPER, ink=INK, lw=2.2)


def envelope(cv, x, y, w=70, rot=0.0, open_amt=0.0, sealed=True):
    h = w * 0.72
    pts = rot_pts([(x - w / 2, y - h / 2), (x + w / 2, y - h / 2), (x + w / 2, y + h / 2), (x - w / 2, y + h / 2)], x, y, rot)
    cv.fill(pts, (186, 132, 82), ink=INK, lw=2.2, shade_col=(160, 110, 66), depth=3)
    fl = [(x - w / 2, y - h / 2), (x, y - h / 2 + h * 0.52 * (1 - 2 * open_amt)), (x + w / 2, y - h / 2)]
    cv.fill(rot_pts(fl, x, y, rot), (200, 146, 92) if open_amt < 0.5 else (170, 120, 76), ink=INK, lw=2.0)
    if sealed and open_amt < 0.1:
        c = rot_pts([(x, y - h / 2 + h * 0.52)], x, y, rot)[0]
        cv.ellipse(c[0], c[1], 7, 7, (210, 60, 54), ink=INK, lw=1.4)


def cup(cv, x, y, w=70, h=80, slips=0):
    cv.fill(spline([(x - w / 2, y - h), (x - w * 0.38, y), (x + w * 0.38, y), (x + w / 2, y - h)], closed=True, n=4), (236, 244, 248), ink=INK,
            lw=2.2, shade_col=(200, 214, 224))
    for i in range(slips):
        cv.fill(rot_pts([(x - 10 + i * 9, y - h - 4), (x + 4 + i * 9, y - h - 4), (x + 4 + i * 9, y - h + 10), (x - 10 + i * 9, y - h + 10)],
                        x, y - h, -14 + i * 11), PAPER, ink=INK, lw=1.4)
    cv.ellipse(x, y - h, w / 2, 10, (210, 224, 232), ink=INK, lw=2)


def ladle(cv, a, b, r=12):
    cv.stroke([a, b], INK, 7)
    cv.stroke([a, b], (170, 170, 176), 4)
    ang = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
    cv.ellipse(b[0] + math.cos(math.radians(ang)) * r * 0.6, b[1] + math.sin(math.radians(ang)) * r * 0.6, r, r * 0.7, (190, 192, 198), ink=INK, lw=2.2,
               rot=ang)


def pot(cv, x, y, w=90):
    cv.fill(spline([(x - w / 2, y - w * 0.7), (x - w * 0.55, y - 4), (x + w * 0.55, y - 4), (x + w / 2, y - w * 0.7)], closed=True, n=4), (176, 182, 190), ink=INK,
            lw=2.4, shade_col=(142, 150, 160))
    cv.ellipse(x, y - w * 0.7, w / 2, 11, (150, 156, 166), ink=INK, lw=2.2)
    cv.stroke([(x - w / 2 - 12, y - w * 0.56), (x - w / 2, y - w * 0.56)], INK, 5)


def spool(cv, x, y, r=26, turn=0.0):
    cv.ellipse(x, y, r, r, (170, 120, 80), ink=INK, lw=2.4, shade_col=(140, 96, 62))
    cv.ellipse(x, y, r * 0.78, r * 0.78, STRING, ink=INK, lw=1.6)
    for k in range(4):
        a = turn + k * math.pi / 2
        cv.stroke([(x, y), (x + math.cos(a) * r * 0.74, y + math.sin(a) * r * 0.74)], (200, 150, 30), 2)
    cv.ellipse(x, y, 5, 5, (150, 100, 60), ink=INK, lw=1.4)


def bowl_side(cv, x, y, w, col=(250, 250, 246), rim=(120, 170, 214)):
    h = w * 0.5
    cv.fill(spline([(x - w / 2, y - h), (x - w * 0.36, y - 2), (x + w * 0.36, y - 2), (x + w / 2, y - h)], closed=True, n=5), col, ink=INK, lw=1.8,
            shade_col=(214, 224, 232), depth=3)
    cv.stroke([(x - w / 2 + 2, y - h + 5), (x + w / 2 - 2, y - h + 5)], rim, 2.2)


def bowl_tower(cv, x, y, w, n, wob=0.0, t=0.0):
    step = w * 0.18
    for i in range(n):
        sway = wob * (i / max(1, n)) ** 1.5 * math.sin(t * 4.0 + 0.4 * i)
        bowl_side(cv, x + sway, y - step * i, w)


def tower_h(w, n):
    return w * 0.18 * (n - 1) + w * 0.5


def crate(cv, x, y, cols, rows, n_filled, s=18, pop=None, ghost=True, dashed=False, t=0.0):
    """Crate seen from a high oblique angle: grid of slots. n_filled slots hold a bowl (row by row); `pop` = (index, 0..1) bowl being dropped in."""
    w, h = cols * s, rows * s * 0.55
    col = (186, 140, 100)
    cv.fill([(x - 6, y - 6), (x + w + 6, y - 6), (x + w + 6, y + h + 6), (x - 6, y + h + 6)], col, ink=INK, lw=2.2, shade_col=shade(col, 0.82))
    cv.fill([(x - 1, y - 1), (x + w + 1, y - 1), (x + w + 1, y + h + 1), (x - 1, y + h + 1)], (150, 110, 78), ink=None)
    k = 0
    for r in range(rows):
        for c in range(cols):
            cx, cy = x + c * s + s / 2, y + r * s * 0.55 + s * 0.28
            if k < n_filled:
                cv.ellipse(cx, cy, s * 0.43, s * 0.3, (250, 250, 246), ink=INK, lw=1.0)
                cv.ellipse(cx, cy, s * 0.26, s * 0.18, (170, 200, 232), ink=None)
            elif pop and k == pop[0]:
                u = pop[1]
                cv.ellipse(cx, cy - (1 - u) * 60, s * 0.43 * (0.8 + 0.2 * u), s * 0.3 * (0.8 + 0.2 * u), (250, 250, 246), ink=INK, lw=1.0)
            elif ghost:
                cv.ellipse(cx, cy, s * 0.42, s * 0.29, (110, 82, 60), ink=(214, 180, 150), lw=1.2, alpha=170)
            k += 1
    if dashed:
        dash = 16
        for i in range(0, int(w + 12), dash):
            cv.stroke([(x - 6 + i, y - 12), (x - 6 + min(i + 8, w + 12), y - 12)], (255, 90, 80), 3)
            cv.stroke([(x - 6 + i, y + h + 12), (x - 6 + min(i + 8, w + 12), y + h + 12)], (255, 90, 80), 3)
        for j in range(0, int(h + 24), dash):
            cv.stroke([(x - 12, y - 12 + j), (x - 12, y - 12 + min(j + 8, h + 24))], (255, 90, 80), 3)
            cv.stroke([(x + w + 12, y - 12 + j), (x + w + 12, y - 12 + min(j + 8, h + 24))], (255, 90, 80), 3)
    return w, h


# ------------------------------------------------------------------------------------------------------------------ crowd + fx
SKINS = [(231, 190, 152), (214, 168, 128), (196, 150, 112), (236, 204, 176), (222, 176, 138)]
SHIRTS = [(236, 110, 96), (96, 150, 200), (240, 190, 80), (110, 170, 120), (170, 120, 190), (230, 140, 100), (90, 170, 170)]


def mini(cv, x, y, s=1.0, i=0, arms="up", flip=False, phase=0.0, moving=False, expr="grin", squash=0.0, carry=None):
    """Background villager (feet at y). When `moving`, legs swing with `phase` and the body bobs."""
    sk, sh = SKINS[i % 5], SHIRTS[i % 7]
    hh = 22 * s
    bw, bh = 15 * s, 38 * s * (1 - squash)
    bob = abs(math.sin(phase)) * 3 * s if moving else 0
    cv.ellipse(x, y + 2, 16 * s, 4 * s, (0, 0, 0), alpha=40)
    for j, dx in enumerate((-5, 5)):
        sw = math.sin(phase + j * math.pi) * 6 * s if moving else 0
        up = max(0, math.cos(phase + j * math.pi)) * 5 * s if moving else 0
        cv.stroke([(x + dx * s, y - 18 * s - bob), (x + dx * s + sw, y - up)], (80, 70, 90), 6 * s)
    y0 = y - 16 * s - bob
    cv.fill(spline([(x - bw, y0), (x - bw * 0.8, y0 - bh), (x + bw * 0.8, y0 - bh), (x + bw, y0)], closed=True, n=3), sh, ink=INK, lw=1.8)
    hy = y0 - bh - hh * 0.7
    sg = -1 if flip else 1
    for side in (-1, 1):
        if arms == "up":
            tip = (x + side * 22 * s, y0 - bh - 26 * s)
        elif arms == "cheer":
            tip = (x + side * 26 * s, y0 - bh - 40 * s - 6 * s * abs(math.sin(phase)))
        elif arms == "forward":
            tip = (x + sg * (10 + 8 * side) * s, y0 - bh * 0.4)
        elif arms == "swing":
            tip = (x + side * 8 * s + side * math.sin(phase + (0 if side > 0 else math.pi)) * 12 * s, y0 - bh * 0.15)
        else:
            tip = (x + side * 14 * s, y0 - bh * 0.2)
        cv.stroke([(x + side * bw * 0.8, y0 - bh * 0.85), tip], sk, 6 * s)
    cv.ellipse(x, hy, hh * 0.8, hh * 0.85, sk, ink=INK, lw=1.8)
    cv.ellipse(x, hy - hh * 0.3, hh * 0.82, hh * 0.6, (50 + 20 * (i % 3), 40, 40), ink=None)
    if expr == "grin":
        cv.stroke(spline([(x - 6 * s, hy + 3 * s), (x, hy + 8 * s), (x + 6 * s, hy + 3 * s)], n=3), INK, 1.6)
    else:
        cv.ellipse(x, hy + 6 * s, 3 * s, 4 * s, INK)
    for dx in (-5, 5):
        cv.ellipse(x + dx * s, hy - 1 * s, 1.6 * s, 2.2 * s, INK)
    return hy


def puff(cv, x, y, r=14, u=0.0, col=(236, 224, 200)):
    """Dust / impact puff expanding and fading (u 0..1)."""
    for k in range(5):
        a = k * 1.26
        cv.ellipse(x + math.cos(a) * r * u * 1.8, y + math.sin(a) * r * u * 0.8 - u * 10, r * (0.6 + 0.8 * u), r * 0.55 * (0.6 + 0.8 * u), col, ink=None,
                   alpha=int(200 * (1 - u)))


def burst(cv, x, y, u, n=9, r0=20, r1=70, col=(255, 200, 70)):
    for k in range(n):
        a = k * 2 * math.pi / n
        cv.stroke([(x + math.cos(a) * (r0 + (r1 - r0) * u), y + math.sin(a) * (r0 + (r1 - r0) * u)),
                   (x + math.cos(a) * (r0 + (r1 - r0) * (u + 0.4)), y + math.sin(a) * (r0 + (r1 - r0) * (u + 0.4)))], col, 4, alpha=int(255 * (1 - u)))


def table(cv, cx, y_top, w=520, d=70, h=70):
    """Wooden table seen from the front-above: top surface (y_top = its back edge), front panel and legs."""
    x0, x1 = cx - w / 2, cx + w / 2
    cv.fill([(x0 + 30, y_top), (x1 - 30, y_top), (x1, y_top + d), (x0, y_top + d)], (214, 164, 118), ink=INK, lw=2.4, shade_col=(190, 142, 98))
    rect(cv, x0, y_top + d, x1, y_top + d + 26, (186, 134, 92), shade_col=(160, 112, 76))
    for lx in (x0 + 18, x1 - 38):
        rect(cv, lx, y_top + d + 26, lx + 20, y_top + d + 26 + h, (160, 112, 76))
