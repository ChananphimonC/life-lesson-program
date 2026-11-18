"""Stage helpers for the visual POC: backgrounds, paper strip in perspective, folded block, crowd silhouettes, bowls.
Everything is drawn with the existing prototype_v2 Canvas (toon.py). 1280x720 frames."""
from __future__ import annotations

import math
import random

from poc_chars import draw  # noqa: F401  (re-exported)
from toon import INK, Canvas, chain, ellipse_pts, mix, shade, spline  # noqa: E402

W, H = 1280, 720
PAPER = (252, 250, 244)
PAPER_SH = (222, 220, 212)
SKINS = [(231, 190, 152), (214, 168, 128), (196, 150, 112), (236, 204, 176), (222, 176, 138)]


def new(bg=(255, 255, 255, 255), ss=2):
    return Canvas(W, H, ss=ss, bg=bg)


def rect(cv, x0, y0, x1, y1, col, ink=INK, lw=2.4, shade_col=None):
    cv.fill([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], col, ink=ink, lw=lw, shade_col=shade_col, depth=5)


def sky(cv, horizon, top=(138, 200, 236), bot=(255, 232, 190)):
    for i in range(24):
        t = i / 23
        y0, y1 = horizon * i / 24, horizon * (i + 1) / 24 + 2
        rect(cv, 0, y0, W, y1, mix(top, bot, t ** 1.4), ink=None)


def courtyard(cv, horizon=300, gate_x=640, gate_s=1.0, ground_top=(212, 184, 138), ground_bot=(190, 156, 108), flags=True):
    sky(cv, horizon)
    cv.ellipse(1080, 90, 46, 46, (255, 244, 200), ink=None, alpha=200)
    # distant tree line
    for i in range(14):
        x = i * 100 - 20
        cv.ellipse(x, horizon - 12, 70, 34 + (i % 3) * 8, (122, 170, 112), ink=None)
        cv.ellipse(x + 30, horizon - 6, 60, 26, (104, 154, 98), ink=None)
    # pagoda (far right)
    px = 1040
    cv.fill([(px - 70, horizon), (px - 50, horizon - 70), (px + 50, horizon - 70), (px + 70, horizon)], (250, 244, 228), ink=INK, lw=2)
    cv.fill([(px - 36, horizon - 70), (px - 24, horizon - 140), (px + 24, horizon - 140), (px + 36, horizon - 70)], (246, 238, 214), ink=INK, lw=2)
    cv.fill([(px - 14, horizon - 140), (px, horizon - 230), (px + 14, horizon - 140)], (236, 190, 90), ink=INK, lw=2)
    # temple wall + gate
    s = gate_s
    cv.fill([(0, horizon + 4), (W, horizon + 4), (W, horizon - 38), (0, horizon - 38)], (240, 226, 196), ink=INK, lw=2, shade_col=(222, 206, 172))
    gx = gate_x
    for dx in (-84, 84):
        rect(cv, gx + dx * s - 20 * s, horizon - 130 * s, gx + dx * s + 20 * s, horizon + 4, (196, 70, 60), shade_col=(166, 52, 46))
    rect(cv, gx - 120 * s, horizon - 168 * s, gx + 120 * s, horizon - 128 * s, (196, 70, 60), shade_col=(166, 52, 46))
    cv.fill([(gx - 150 * s, horizon - 168 * s), (gx, horizon - 226 * s), (gx + 150 * s, horizon - 168 * s)], (236, 168, 60), ink=INK, lw=2.4,
            shade_col=(214, 140, 44))
    cv.fill([(gx - 64 * s, horizon + 4), (gx - 64 * s, horizon - 80 * s), (gx, horizon - 108 * s), (gx + 64 * s, horizon - 80 * s),
             (gx + 64 * s, horizon + 4)], (150, 196, 120), ink=INK, lw=2)         # green fields seen through the gate
    # ground
    for i in range(14):
        t = i / 13
        y0 = horizon + 4 + (H - horizon) * (t ** 1.6)
        y1 = horizon + 4 + (H - horizon) * (((i + 1) / 13) ** 1.6) + 2
        rect(cv, 0, y0, W, y1, mix(ground_top, ground_bot, t), ink=None)
    rnd = random.Random(7)
    for _ in range(60):
        x, t = rnd.uniform(0, W), rnd.uniform(0.05, 1)
        y = horizon + 10 + (H - horizon - 10) * t ** 1.6
        cv.stroke([(x, y), (x + 8 * t + 3, y - 3 * t - 1)], shade(ground_bot, 0.86), 1.5, alpha=150)
    if flags:
        bunting(cv, -20, 54, W + 20, 38, 17)
        bunting(cv, -20, 112, W + 20, 98, 14)


def bunting(cv, x0, y0, x1, y1, n):
    cols = [(236, 84, 90), (250, 196, 70), (96, 176, 120), (84, 150, 210), (230, 130, 190)]
    pts = [(x0 + (x1 - x0) * i / 40, y0 + (y1 - y0) * i / 40 + 16 * math.sin(math.pi * i / 40)) for i in range(41)]
    cv.stroke(pts, (120, 96, 80), 2.0)
    for k in range(n):
        i = int(2 + k * 38 / n)
        x, y = pts[i]
        cv.fill([(x - 11, y), (x + 11, y), (x, y + 26)], cols[k % 5], ink=INK, lw=1.6)


def kitchen(cv, horizon=380):
    """Night temple-fair kitchen: warm lamps, dark teal back wall, a long table, hanging pots."""
    for i in range(20):
        rect(cv, 0, horizon * i / 20, W, horizon * (i + 1) / 20 + 2, mix((40, 52, 86), (96, 84, 100), i / 19), ink=None)
    for i in range(12):
        t = i / 11
        y0 = horizon + (H - horizon) * t ** 1.5
        y1 = horizon + (H - horizon) * ((i + 1) / 11) ** 1.5 + 2
        rect(cv, 0, y0, W, y1, mix((170, 130, 98), (132, 96, 70), t), ink=None)
    # shelves + hanging pots
    for x in (120, 360, 600, 840, 1080):
        rect(cv, x - 90, 150, x + 90, 162, (120, 86, 60))
        for k in range(3):
            cv.ellipse(x - 54 + k * 54, 130, 22, 20, (176, 182, 190), ink=INK, lw=2, shade_col=(142, 150, 160))
    for x in (200, 700, 1000):
        cv.stroke([(x, 0), (x, 36)], INK, 2)
        cv.ellipse(x, 52, 22, 20, (255, 224, 140), ink=INK, lw=2)
    cv.ellipse(640, 340, 700, 260, (255, 226, 160), ink=None, alpha=40)
    # moon through a window
    rect(cv, 1000, 190, 1200, 330, (28, 40, 78), shade_col=(18, 28, 60))
    cv.ellipse(1100, 252, 30, 30, (250, 244, 214), ink=None)
    cv.stroke([(1100, 190), (1100, 330)], (120, 86, 60), 4)
    cv.stroke([(1000, 260), (1200, 260)], (120, 86, 60), 4)


# --- paper strip in perspective ---------------------------------------------------------------------------------------------

def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def strip(cv, near, vp, wn, t0=0.0, t1=0.85, creases=14, col=PAPER):
    """A flat paper band lying on the ground, from `near` (x, y, with half-width wn px) toward the vanishing point."""
    pA, pB = lerp(near, vp, t0), lerp(near, vp, t1)
    wA, wB = wn * (1 - t0), wn * (1 - t1)
    quad = [(pA[0] - wA, pA[1]), (pA[0] + wA, pA[1]), (pB[0] + wB, pB[1]), (pB[0] - wB, pB[1])]
    cv.fill(quad, col, ink=INK, lw=2.2, shade_col=PAPER_SH, depth=3)
    for i in range(1, creases):
        t = t0 + (t1 - t0) * (i / creases) ** 1.3
        p = lerp(near, vp, t)
        w = wn * (1 - t)
        cv.stroke([(p[0] - w, p[1]), (p[0] + w, p[1])], (226, 224, 214), 1.2, alpha=170)


def block(cv, x, y, w, h, d, layers=14, top_col=PAPER, face_col=(246, 244, 236), cap=0):
    """A folded stack seen from front-above: x,y = bottom-centre of the front face. Layer lines on the front/side show the
    thickness. `cap`: draw the crumpled outer layers of a failed fold (0..1)."""
    x0, x1 = x - w / 2, x + w / 2
    dx, dy = d * 0.55, d * 0.42
    cv.fill([(x1, y), (x1 + dx, y - dy), (x1 + dx, y - h - dy), (x1, y - h)], shade(face_col, 0.84), ink=INK, lw=2.4)
    cv.fill([(x0, y - h), (x1, y - h), (x1 + dx, y - h - dy), (x0 + dx, y - h - dy)], top_col, ink=INK, lw=2.4)
    cv.fill([(x0, y), (x1, y), (x1, y - h), (x0, y - h)], face_col, ink=INK, lw=2.6)
    for i in range(1, layers):
        yy = y - h * i / layers
        cv.stroke([(x0 + 3, yy), (x1 - 3, yy)], (214, 212, 202), 1.4)
        cv.stroke([(x1, yy), (x1 + dx, yy - dy)], (190, 188, 178), 1.2)
    if cap:
        # the failed fold: the OUTER layers (top and bottom of the stack) are pulled out and buckle at the bend end, the inner
        # ones barely move. Illustration of the idea, not a simulation.
        n = 14
        for i in range(n):
            yy = y - h * (i + 0.5) / n
            outer = abs(i - (n - 1) / 2) / ((n - 1) / 2)                    # 0 in the middle .. 1 at the outer layers
            bulge = cap * (10 + 70 * outer ** 1.6) + 4 * math.sin(i * 2.3)
            lw_ = h / n * 0.46
            col = PAPER if i % 2 else (238, 236, 226)
            cv.fill(spline([(x1 - 3, yy - lw_), (x1 + bulge * 0.7, yy - lw_ * 1.2 - 4 * outer), (x1 + bulge, yy), (x1 + bulge * 0.7, yy + lw_ * 1.2 + 4 * outer),
                            (x1 - 3, yy + lw_)], closed=True, n=4), col, ink=INK, lw=1.7)
        for i in (0, n - 1):                                                  # a torn, crumpled corner at the very top/bottom
            yy = y - h * (i + 0.5) / n + (-8 if i == 0 else 8)
            cv.stroke([(x1 + cap * 40, yy), (x1 + cap * 52, yy + (-6 if i == 0 else 6)), (x1 + cap * 44, yy + (-12 if i == 0 else 12)),
                       (x1 + cap * 58, yy + (-16 if i == 0 else 16))], INK, 1.8)


# --- crowd -------------------------------------------------------------------------------------------------------------------

_SHIRTS = [(236, 110, 96), (96, 150, 200), (240, 190, 80), (110, 170, 120), (170, 120, 190), (230, 140, 100), (90, 170, 170)]


def mini(cv, x, y, s=1.0, i=0, arms="up", flip=False, squash=0.0, expr="grin"):
    """Cheap silhouette villager (feet at y). Used only in the background of wide shots."""
    sk = SKINS[i % 5]
    sh = _SHIRTS[i % 7]
    hh = 22 * s
    bw, bh = 15 * s, 38 * s * (1 - squash)
    cv.ellipse(x, y + 2, 16 * s, 4 * s, (0, 0, 0), alpha=40)
    for dx in (-5, 5):
        cv.stroke([(x + dx * s, y - 18 * s), (x + dx * s, y)], (80, 70, 90), 6 * s)
    cv.fill(spline([(x - bw, y - 16 * s), (x - bw * 0.8, y - 16 * s - bh), (x + bw * 0.8, y - 16 * s - bh), (x + bw, y - 16 * s)], closed=True, n=3),
            sh, ink=INK, lw=1.8)
    hy = y - 16 * s - bh - hh * 0.7
    if arms == "up":
        for sx in (-1, 1):
            cv.stroke([(x + sx * bw * 0.8, y - 16 * s - bh * 0.85), (x + sx * 22 * s, y - 16 * s - bh - 26 * s)], sk, 6 * s)
    elif arms == "forward":
        for sx in (-1, 1):
            cv.stroke([(x + sx * bw * 0.8, y - 16 * s - bh * 0.85), (x + sx * 12 * s, y - 16 * s - bh * 0.35)], sk, 6 * s)
    elif arms == "cheer":
        for sx in (-1, 1):
            cv.stroke([(x + sx * bw * 0.8, y - 16 * s - bh * 0.85), (x + sx * 26 * s, y - 16 * s - bh - 40 * s)], sk, 6 * s)
    cv.ellipse(x, hy, hh * 0.8, hh * 0.85, sk, ink=INK, lw=1.8)
    cv.ellipse(x, hy - hh * 0.3, hh * 0.82, hh * 0.6, (50 + 20 * (i % 3), 40, 40), ink=None)
    if expr == "grin":
        cv.stroke(spline([(x - 6 * s, hy + 3 * s), (x, hy + 8 * s), (x + 6 * s, hy + 3 * s)], n=3), INK, 1.6)
    elif expr == "o":
        cv.ellipse(x, hy + 6 * s, 3 * s, 4 * s, INK)
    for dx in (-5, 5):
        cv.ellipse(x + dx * s, hy - 1 * s, 1.6 * s, 2.2 * s, INK)


# --- bowls ---------------------------------------------------------------------------------------------------------------------

def bowl_top(cv, x, y, r, col=(250, 250, 246)):
    cv.ellipse(x, y, r, r, col, ink=INK, lw=1.4)
    cv.ellipse(x, y, r * 0.62, r * 0.62, mix(col, (170, 200, 232), 0.5), ink=None)
    cv.ellipse(x - r * 0.3, y - r * 0.3, r * 0.14, r * 0.14, (255, 255, 255), ink=None)


def bowl_side(cv, x, y, w, col=(250, 250, 246), rim=(120, 170, 214)):
    """A bowl from the side, base at y. w = full width."""
    h = w * 0.5
    cv.fill(spline([(x - w / 2, y - h), (x - w * 0.36, y - 2), (x + w * 0.36, y - 2), (x + w / 2, y - h)], closed=True, n=5), col,
            ink=INK, lw=1.8, shade_col=(214, 224, 232), depth=3)
    cv.stroke([(x - w / 2 + 2, y - h + 5), (x + w / 2 - 2, y - h + 5)], rim, 2.2)


def bowl_tower(cv, x, y, w, n, wob=0.0):
    """n bowls stacked, tower leaning by `wob` px per bowl."""
    step = w * 0.18
    for i in range(n):
        bowl_side(cv, x + wob * i * (i / max(1, n)) , y - step * i, w)
