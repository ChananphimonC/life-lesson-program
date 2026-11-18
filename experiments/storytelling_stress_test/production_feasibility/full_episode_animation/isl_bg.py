"""Backgrounds for the island story (procedural, layered, soft colours): beach morning, forest, mangrove stream, tide pool, hill path, hilltop view, sunset beach, night beach with glowing sea,
dawn beach, cave in the rain, raft yard, storm sea, ferry dawn. Everything takes `t` so the sea, leaves and light keep moving."""
from __future__ import annotations

import math

import engine  # noqa: F401
from props_uni import INK, W, H, band, cloud, mix, rect, rrect, spline

SAND = (244, 222, 170)
SAND_SH = (222, 196, 140)


def _sea(cv, y0, t, top=(120, 214, 226), bot=(52, 150, 190), amp=6, lines=14, sparkle=0.0):
    band(cv, y0, H, top, bot, n=10, x0=0, x1=W)
    for r in range(lines):
        a = (r + 0.5) / lines
        yy = y0 + (H - y0) * (0.02 + 0.5 * a)
        pts = [(x, yy + amp * a * math.sin(x * 0.012 + t * 1.1 + r * 1.7)) for x in range(-20, W + 40, 40)]
        cv.stroke(spline(pts, n=2), mix(bot, (255, 255, 255), 0.35), 1.2 + 1.8 * a, alpha=int(90 + 70 * a))
    if sparkle > 0:
        for i in range(36):
            x = (i * 241 + t * 14 * (1 + i % 3)) % W
            y = y0 + 6 + ((i * 53) % max(20, int((H - y0) * 0.5)))
            a = max(0.0, math.sin(t * 3 + i * 2.1))
            cv.stroke([(x - 8, y), (x + 8, y)], (255, 255, 255), 1.8, alpha=int(200 * a * sparkle))


def _shore(cv, y, t, wet=(226, 204, 150), foam=True):
    """Foamy edge where the sea meets the sand at height y (the sand below)."""
    rect(cv, 0, y, W, H, SAND, ink=None)
    band(cv, y, y + 70, wet, SAND, n=6, x0=0, x1=W)
    if foam:
        k = 6 * math.sin(t * 0.9)
        pts = [(x, y + k + 5 * math.sin(x * 0.02 + t * 1.3)) for x in range(-20, W + 40, 30)]
        cv.stroke(spline(pts, n=2), (255, 255, 255), 5, alpha=210)
        cv.stroke(spline([(px, py - 8) for px, py in pts], n=2), (255, 255, 255), 2.4, alpha=120)


def palm(cv, x, y, h=300, t=0.0, lean=40, s=1.0, col=(54, 150, 84), seed=0.0, nuts=True):
    """A coconut palm: curved trunk with rings and a crown of swaying fronds."""
    cv.push(x, y, scale=s)
    top = (lean, -h)
    mid = (lean * 0.25, -h * 0.5)
    trunk = spline([(0, 0), mid, top], n=4)
    cv.stroke(trunk, INK, 24)
    cv.stroke(trunk, (150, 108, 76), 19)
    cv.stroke([(px + 5, py) for px, py in trunk], (180, 138, 98), 5, alpha=140)
    for i in range(1, 9):
        u = i / 9
        px, py = trunk[int(u * (len(trunk) - 1))]
        cv.stroke([(px - 10, py), (px + 10, py - 2)], (112, 80, 56), 2, alpha=160)
    tx, ty = top
    for i in range(11):
        a = -math.pi * 1.04 + (i + 0.5) * math.pi * 1.08 / 11 + 0.12 * math.sin(t * 1.3 + i + seed)
        L = 150 + 30 * ((i * 7) % 3)
        ex, ey = tx + math.cos(a) * L, ty + math.sin(a) * L * 0.55 + 70 * abs(math.cos(a)) ** 1.5
        cx, cy = tx + math.cos(a) * L * 0.55, ty + math.sin(a) * L * 0.7 - 14
        leaf = spline([(tx, ty), (cx, cy - 26), (ex, ey)], n=3) + spline([(ex, ey), (cx, cy + 22), (tx, ty)], n=3)
        cv.fill(leaf, mix(col, (255, 255, 255), 0.08 * (i % 2)), ink=INK, lw=2.2, shade_col=mix(col, (0, 0, 0), 0.25), depth=3)
        cv.stroke(spline([(tx, ty), (cx, cy), (ex, ey)], n=3), mix(col, (0, 0, 0), 0.3), 1.6)
    if nuts:
        for dx in (-12, 10):
            cv.ellipse(tx + dx, ty + 16, 11, 11, (120, 84, 54), ink=INK, lw=2.0)
    cv.pop()


def rocks(cv, x, y, w=160, h=90, col=(150, 146, 150), n=3):
    for i in range(n):
        ww = w * (1 - i * 0.22)
        hh = h * (1 - i * 0.18)
        ox = (i - 1) * w * 0.4
        cv.fill(spline([(x + ox - ww / 2, y), (x + ox - ww * 0.38, y - hh * 0.7), (x + ox, y - hh), (x + ox + ww * 0.4, y - hh * 0.6), (x + ox + ww / 2, y)], closed=True, n=3),
                mix(col, (255, 255, 255), 0.08 * i), ink=INK, lw=2.6, shade_col=mix(col, (0, 0, 0), 0.25), depth=5)


def leaf_big(cv, x, y, L=170, ang=-60, col=(48, 140, 70), wid=46):
    a = math.radians(ang)
    ex, ey = x + math.cos(a) * L, y + math.sin(a) * L
    nx, ny = -math.sin(a), math.cos(a)
    mx, my = (x + ex) / 2, (y + ey) / 2
    cv.fill(spline([(x, y), (mx + nx * wid, my + ny * wid), (ex, ey), (mx - nx * wid, my - ny * wid)], closed=True, n=3), col, ink=INK, lw=2.2, shade_col=mix(col, (0, 0, 0), 0.25), depth=3)
    cv.stroke([(x, y), (ex, ey)], mix(col, (0, 0, 0), 0.3), 1.8)


def _cloud_set(cv, t, y=90, tint=(255, 255, 255)):
    for i, (cx, cy, s) in enumerate(((180, y, 1.2), (620, y + 40, 1.0), (1010, y - 10, 1.3))):
        cloud(cv, (cx + t * 4 * (1 + i * 0.3)) % (W + 300) - 150, cy, s, tint)


# ----------------------------------------------------------------------------------------------------------------- 1 beach in the morning (wreck, gulls)
def beach_morning(cv, t=0.0, wreck=True):
    band(cv, 0, 340, (255, 214, 190), (150, 214, 244), n=12, x0=0, x1=W)
    cv.ellipse(300, 330, 90, 90, (255, 232, 170), ink=None, alpha=130)
    cv.ellipse(300, 330, 46, 46, (255, 246, 200), ink=None)
    _cloud_set(cv, t, 100, (255, 238, 230))
    _sea(cv, 330, t, (140, 214, 226), (56, 156, 196), sparkle=0.6)
    cv.fill([(0, 332), (60, 318), (150, 328), (230, 320), (230, 332)], (96, 150, 132), ink=None, alpha=200)       # far island
    if wreck:
        cv.push(980, 410, scale=1.0, rot=-8)
        cv.fill(spline([(-120, 0), (-100, -50), (-20, -86), (60, -60), (120, 0)], closed=True, n=3), (200, 150, 110), ink=INK, lw=3.0, shade_col=(150, 108, 76), depth=6)
        cv.stroke([(-90, -20), (90, -20)], (160, 112, 76), 2.4)
        cv.stroke([(-30, -86), (-30, -170)], (140, 100, 70), 7)
        cv.pop()
    _shore(cv, 470, t)
    palm(cv, 90, 560, 320, t, 70, 1.0)
    palm(cv, 1210, 600, 360, t, -80, 1.1, seed=2)
    rocks(cv, 1000, 700, 170, 80)
    for i in range(8):
        cv.ellipse(120 + i * 150 + (i * 37) % 60, 640 + (i * 29) % 70, 18, 4, SAND_SH, ink=None, alpha=130)


# ----------------------------------------------------------------------------------------------------------------- 2 forest (monkey chase)
def forest(cv, t=0.0, dim=0.0, rays=True):
    band(cv, 0, H, (196, 232, 190), (110, 176, 120), n=12, x0=0, x1=W)
    for i in range(7):                                                                  # far trunks
        x = 40 + i * 190
        cv.stroke([(x, 80), (x + 8, 520)], (110, 150, 112), 34)
    for i in range(6):
        x = 120 + i * 200 + 30 * math.sin(i * 1.7)
        cv.stroke([(x, 0), (x + 12, 600)], (74, 98, 70), 44)
        cv.stroke([(x - 8, 0), (x + 2, 600)], (96, 126, 90), 12, alpha=160)
    for i in range(10):                                                                 # canopy blobs
        cv.ellipse(i * 150 - 20, 20 + (i % 3) * 14, 130, 80, (46, 120, 66), ink=None)
    if rays:
        for i in range(6):
            x = 150 + i * 200 + 20 * math.sin(t * 0.4 + i)
            cv.fill([(x - 24, 0), (x + 24, 0), (x + 150, 620), (x + 40, 620)], (255, 250, 200), ink=None, alpha=34)
    rect(cv, 0, 560, W, H, (112, 142, 84), ink=None)
    band(cv, 560, 640, (126, 156, 94), (146, 118, 80), n=5, x0=0, x1=W)
    for i in range(9):
        leaf_big(cv, 60 + i * 150, 620, 120 + (i % 3) * 30, -70 + (i % 4) * 16 + 4 * math.sin(t * 1.3 + i), (40 + (i % 3) * 14, 130 + (i % 2) * 20, 66))
    rect(cv, 0, 650, W, H, (150, 120, 84), ink=None)
    for i in range(8):
        cv.ellipse(70 + i * 160, 690 + (i % 3) * 8, 36, 7, (126, 98, 68), ink=None, alpha=160)
    if dim > 0:
        cv.fill([(0, 0), (W, 0), (W, H), (0, H)], (20, 30, 50), ink=None, alpha=int(150 * dim))


# ----------------------------------------------------------------------------------------------------------------- 3 mangrove stream (water)
def mangrove(cv, t=0.0):
    band(cv, 0, 300, (176, 224, 196), (110, 180, 140), n=10, x0=0, x1=W)
    for i in range(12):
        cv.ellipse(i * 120, 40 + (i % 3) * 20, 120, 76, (44, 126, 78), ink=None)
    for i in range(8):
        cv.ellipse(30 + i * 170, 150 + (i % 2) * 24, 110, 66, (62, 150, 92), ink=None, alpha=220)
    for i in range(10):                                                                  # hanging roots / vines
        x = 60 + i * 130
        cv.stroke(spline([(x, 60), (x + 6 * math.sin(t + i), 180), (x + 4, 280)], n=3), (96, 80, 60), 3.2)
    band(cv, 300, H, (110, 196, 168), (50, 130, 120), n=8, x0=0, x1=W)
    for r in range(10):
        yy = 320 + r * 38
        cv.stroke(spline([(x, yy + 3 * math.sin(x * 0.02 + t * 1.2 + r)) for x in range(-20, W + 40, 40)], n=2), (200, 240, 230), 1.6, alpha=100)
    for i in range(14):                                                                  # arching roots
        x = 20 + i * 96
        pts = [(x, 330), (x + 18, 270), (x + 46, 250 + 8 * (i % 3)), (x + 70, 280), (x + 82, 340)]
        cv.stroke(spline(pts, n=3), INK, 10)
        cv.stroke(spline(pts, n=3), (126, 92, 66), 6.5)
    for i in range(14):
        x = 20 + i * 96
        cv.stroke([(x + 50, 330), (x + 50, 420)], (126, 92, 66), 3, alpha=140)
    rect(cv, 0, 600, W, H, (108, 90, 66), ink=None)
    band(cv, 596, 640, (150, 126, 96), (108, 90, 66), n=4, x0=0, x1=W)
    for i in range(6):
        cv.ellipse(120 + i * 200, 668 + (i % 2) * 14, 44, 8, (84, 70, 52), ink=None, alpha=160)


# ----------------------------------------------------------------------------------------------------------------- 4 tide pool afternoon (fishing / cooking)
def tidepool(cv, t=0.0):
    band(cv, 0, 300, (255, 232, 180), (186, 226, 244), n=10, x0=0, x1=W)
    cv.ellipse(980, 120, 70, 70, (255, 240, 190), ink=None, alpha=140)
    cv.ellipse(980, 120, 38, 38, (255, 248, 214), ink=None)
    _cloud_set(cv, t, 90, (255, 252, 242))
    _sea(cv, 300, t, (150, 232, 228), (62, 176, 190), sparkle=0.8)
    rocks(cv, 150, 470, 300, 150, (146, 140, 146), 3)
    rocks(cv, 1120, 450, 280, 130, (146, 140, 146), 3)
    _shore(cv, 520, t, wet=(232, 214, 160))
    for i in range(5):                                                                    # tide pools
        cx, cy = 200 + i * 220, 600 + (i % 2) * 40
        cv.ellipse(cx, cy, 90, 22, (126, 214, 226), ink=INK, lw=2.0, alpha=230)
        cv.ellipse(cx - 20, cy - 4, 30, 6, (220, 252, 252), ink=None, alpha=130)
    for i in range(7):
        cv.ellipse(70 + i * 180, 700, 20, 5, SAND_SH, ink=None, alpha=130)
    palm(cv, 620, 520, 250, t, -30, 0.8, seed=1.3)


# ----------------------------------------------------------------------------------------------------------------- 5 hill path and 5b hilltop view
def hill_path(cv, t=0.0):
    band(cv, 0, H, (190, 228, 196), (96, 150, 96), n=12, x0=0, x1=W)
    for i in range(8):
        x = 60 + i * 170
        cv.stroke([(x, 0), (x + 10, 520)], (66, 96, 64), 52)
        cv.stroke([(x - 10, 0), (x - 2, 520)], (94, 126, 86), 14, alpha=150)
    for i in range(10):
        cv.ellipse(i * 140 - 10, 30 + (i % 3) * 16, 120, 70, (40, 108, 60), ink=None)
    for i in range(5):
        x = 150 + i * 240
        cv.fill([(x - 20, 0), (x + 20, 0), (x + 130, 660), (x + 30, 660)], (255, 250, 200), ink=None, alpha=30)
    cv.fill([(0, 560), (W, 470), (W, H), (0, H)], (134, 108, 76), ink=None)                 # a sloping path
    cv.fill([(0, 560), (W, 470), (W, 500), (0, 600)], (160, 132, 94), ink=None)
    for i in range(8):
        leaf_big(cv, 40 + i * 180, 520 - i * 8, 130, -80 + (i % 3) * 18 + 5 * math.sin(t * 1.4 + i), (44, 132 + (i % 2) * 20, 70))
    for i in range(8):
        cv.ellipse(100 + i * 160, 650 - i * 6, 40, 7, (112, 90, 62), ink=None, alpha=150)


def hilltop(cv, t=0.0, storm=1.0, flash=0.0):
    """The view from the top: sea, the ferry channel on the right, a dark storm wall far away."""
    band(cv, 0, 400, (150, 210, 244), (255, 232, 206), n=12, x0=0, x1=W)
    _cloud_set(cv, t, 90)
    # the storm wall on the right horizon
    for i in range(9):
        x = 760 + i * 70 + 12 * math.sin(t * 0.3 + i)
        y = 230 + (i % 3) * 14 - 10 * storm
        cv.ellipse(x, y, 150, 110 * storm + 20, mix((190, 200, 220), (70, 76, 108), storm), ink=None, alpha=235)
    for i in range(4):
        x = 900 + i * 120
        cv.stroke([(x, 350), (x - 30, 440)], (200, 206, 224), 2, alpha=int(120 * storm))
    if flash > 0:
        cv.ellipse(1010, 250, 150, 90, (255, 255, 240), ink=None, alpha=int(150 * flash))
    _sea(cv, 400, t, (120, 196, 232), (56, 130, 190), amp=3, lines=10, sparkle=0.4)
    cv.fill([(380, 402), (440, 380), (520, 396), (540, 402)], (90, 150, 130), ink=None, alpha=200)   # a far islet
    # channel buoys
    for i in range(4):
        cv.ellipse(660 + i * 70, 430 + i * 8, 6, 8, (240, 80, 70), ink=INK, lw=1.2)
    # foreground ledge
    cv.fill([(0, 560), (180, 520), (420, 540), (700, 520), (W, 560), (W, H), (0, H)], (132, 122, 118), ink=INK, lw=3.0, shade_col=(100, 92, 90), depth=8)
    cv.fill([(0, 600), (W, 590), (W, H), (0, H)], (102, 126, 80), ink=None)
    for i in range(10):
        leaf_big(cv, 30 + i * 130, 610, 90, -80 + (i % 3) * 20 + 4 * math.sin(t * 1.5 + i), (56, 140, 70))


# ----------------------------------------------------------------------------------------------------------------- 6 sunset beach (football)
def sunset_beach(cv, t=0.0, sun=0.5):
    band(cv, 0, 360, (96, 80, 160), (255, 164, 96), n=14, x0=0, x1=W)
    sy = 300 + 70 * sun
    cv.ellipse(640, sy, 150, 150, (255, 190, 110), ink=None, alpha=70)
    cv.ellipse(640, sy, 86, 86, (255, 226, 150), ink=None)
    for i in range(6):                                                                   # streaks of cloud
        x = 100 + i * 220 + 8 * math.sin(t * 0.3 + i)
        cv.ellipse(x, 150 + (i % 3) * 36, 130, 12, (255, 196, 170), ink=None, alpha=170)
    _sea(cv, 360, t, (255, 176, 120), (108, 82, 150), amp=3, lines=12)
    for i in range(14):                                                                  # sun glitter path
        y = 380 + i * 14
        cv.stroke([(640 - 90 + i * 3 + 14 * math.sin(t * 2 + i), y), (640 + 90 - i * 3 - 14 * math.sin(t * 2.3 + i), y)], (255, 226, 160), 3, alpha=int(200 - i * 10))
    _shore(cv, 500, t, wet=(236, 190, 140))
    rect(cv, 0, 520, W, H, (238, 196, 140), ink=None)
    band(cv, 500, 570, (220, 170, 124), (238, 196, 140), n=5, x0=0, x1=W)
    for x, lean, hh in ((90, 60, 340), (1200, -70, 380)):
        palm(cv, x, 600, hh, t, lean, 1.0, col=(34, 70, 66), seed=x, nuts=False)
    for i in range(8):
        cv.ellipse(100 + i * 150, 690 + (i % 3) * 10, 22, 5, (206, 160, 110), ink=None, alpha=130)


# ----------------------------------------------------------------------------------------------------------------- 7 night beach (glowing sea, fireflies in the mangrove)
def night_beach(cv, t=0.0, glow=1.0):
    band(cv, 0, 360, (10, 14, 44), (34, 48, 108), n=14, x0=0, x1=W)
    for i in range(90):
        x, y = (i * 7919 + i * i * 31) % W, (i * 104729 // 7 + i * 13) % 330
        a = 0.5 + 0.5 * math.sin(t * 2 + i)
        cv.ellipse(x, y, 1.6 + (i % 3) * 0.5, 1.6 + (i % 3) * 0.5, (255, 255, 240), ink=None, alpha=int(110 + 120 * a))
    cv.ellipse(210, 120, 38, 38, (252, 248, 224), ink=None)
    cv.ellipse(210, 120, 74, 74, (200, 214, 255), ink=None, alpha=40)
    _sea(cv, 360, t, (26, 56, 108), (10, 28, 74), amp=4, lines=12)
    for i in range(60):                                                                  # glowing plankton
        x = (i * 211 + t * 18 * (1 + i % 3)) % W
        y = 372 + ((i * 97) % 120)
        a = max(0.0, math.sin(t * 2.4 + i * 1.3)) ** 2
        cv.ellipse(x, y, 7, 3.4, (110, 240, 255), ink=None, alpha=int(70 * a * glow))
        cv.ellipse(x, y, 2.4, 1.4, (200, 255, 255), ink=None, alpha=int(255 * a * glow))
    _shore(cv, 500, t, wet=(70, 78, 112), foam=True)
    rect(cv, 0, 540, W, H, (58, 62, 94), ink=None)
    band(cv, 500, 580, (84, 90, 128), (58, 62, 94), n=5, x0=0, x1=W)
    cv.fill([(0, 600), (W, 600), (W, H), (0, H)], (44, 48, 78), ink=None)
    for x, lean, hh in ((80, 60, 330), (1220, -60, 360)):
        palm(cv, x, 640, hh, t, lean, 1.0, col=(16, 38, 44), seed=x, nuts=False)
    # mangrove edge on the right with fireflies are added by fireflies() in the scene


# ----------------------------------------------------------------------------------------------------------------- 8 dawn beach (turtle tracks, the nest)
def dawn_beach(cv, t=0.0):
    band(cv, 0, 330, (255, 190, 200), (255, 232, 176), n=14, x0=0, x1=W)
    cv.ellipse(760, 310, 120, 120, (255, 224, 170), ink=None, alpha=100)
    cv.ellipse(760, 318, 52, 52, (255, 244, 206), ink=None)
    _cloud_set(cv, t, 110, (255, 214, 214))
    _sea(cv, 330, t, (255, 214, 190), (126, 188, 214), amp=3, lines=12, sparkle=0.8)
    _shore(cv, 470, t, wet=(238, 214, 170))
    rect(cv, 0, 530, W, H, (240, 218, 164), ink=None)
    band(cv, 470, 540, (226, 202, 154), (240, 218, 164), n=5, x0=0, x1=W)
    # the turtle's track: two rows of flipper marks from the water up to the nest mound
    for i in range(14):
        u = i / 13
        x, y = 360 + u * 380, 480 + u * 150
        cv.ellipse(x - 12, y + 6 * (i % 2), 10, 4, (200, 170, 124), ink=None, alpha=210)
        cv.ellipse(x + 12, y + 6 * ((i + 1) % 2), 10, 4, (200, 170, 124), ink=None, alpha=210)
    cv.stroke(spline([(360, 486), (560, 560), (740, 630)], n=3), (210, 182, 138), 10, alpha=110)
    cv.ellipse(780, 660, 110, 30, (226, 198, 148), ink=INK, lw=2.4, shade_col=(200, 170, 124))    # the nest mound
    palm(cv, 90, 600, 330, t, 60, 1.0)
    palm(cv, 1210, 620, 350, t, -70, 1.0, seed=2.2)


# ----------------------------------------------------------------------------------------------------------------- 9 cave in the rain
def cave(cv, t=0.0, rain=1.0, fire=0.0):
    rect(cv, 0, 0, W, H, (62, 56, 74), ink=None)
    band(cv, 0, 600, (44, 40, 56), (84, 74, 90), n=10, x0=0, x1=W)
    # opening with the rain outside
    cv.fill(spline([(760, 640), (740, 300), (860, 120), (1060, 100), (1200, 220), (1220, 640)], closed=True, n=4), (120, 140, 168), ink=INK, lw=4.0)
    band(cv, 130, 640, (150, 168, 192), (96, 118, 146), n=8, x0=800, x1=1180)
    for i in range(40):
        x = 790 + (i * 53) % 400
        y = ((t * 520 * rain + i * 91) % 560) + 100
        cv.stroke([(x, y), (x - 10, y + 36)], (220, 236, 250), 2, alpha=int(190 * rain))
    for i in range(7):                                                                   # stalactites
        x = 80 + i * 170
        cv.fill([(x - 26, 0), (x + 26, 0), (x + 4, 90 + (i % 3) * 36)], (84, 76, 98), ink=INK, lw=2.4, shade_col=(60, 54, 74))
    rocks(cv, 120, 660, 260, 160, (92, 84, 98), 3)
    rect(cv, 0, 640, W, H, (78, 70, 84), ink=None)
    for i in range(9):
        cv.ellipse(60 + i * 150, 690 + (i % 3) * 8, 44, 7, (62, 56, 70), ink=None, alpha=180)
    if fire > 0:
        cv.ellipse(380, 640, 330, 130, (255, 170, 80), ink=None, alpha=int(52 * fire))


# ----------------------------------------------------------------------------------------------------------------- 10 raft yard (builds through the afternoon into the night)
def raft_yard(cv, t=0.0, tod=0.0):
    """tod 0 = late afternoon, 1 = night; bamboo stacks, rope coils, a half-built frame on the sand."""
    top = mix((255, 190, 120), (14, 20, 56), tod)
    bot = mix((255, 226, 170), (40, 52, 112), tod)
    band(cv, 0, 360, top, bot, n=14, x0=0, x1=W)
    if tod > 0.4:
        for i in range(70):
            x, y = (i * 7919 + i * i * 31) % W, (i * 104729 // 7 + i * 13) % 320
            cv.ellipse(x, y, 1.6, 1.6, (255, 255, 240), ink=None, alpha=int(200 * (tod - 0.4) / 0.6 * (0.6 + 0.4 * math.sin(t * 2 + i))))
    cv.ellipse(980, 280 + 100 * tod, 80, 80, mix((255, 224, 150), (230, 236, 255), tod), ink=None, alpha=int(255 * (1 - 0.3 * tod)))
    _sea(cv, 360, t, mix((255, 184, 130), (26, 54, 108), tod), mix((90, 160, 190), (10, 28, 74), tod), amp=3, lines=10)
    _shore(cv, 500, t, wet=mix((236, 200, 150), (70, 78, 112), tod))
    sand = mix((240, 206, 150), (56, 60, 92), tod)
    rect(cv, 0, 540, W, H, sand, ink=None)
    band(cv, 500, 580, mix((222, 186, 140), (84, 90, 128), tod), sand, n=5, x0=0, x1=W)
    for i in range(5):                                                                   # bamboo stack at the left
        cv.fill(spline([(40, 640 - i * 18), (260, 636 - i * 18), (264, 656 - i * 18), (36, 660 - i * 18)], closed=True, n=2), mix((214, 184, 108), (80, 84, 80), tod), ink=INK, lw=2.4)
    for i in range(3):
        cv.ellipse(1180, 670 - i * 12, 36 - i * 4, 10, mix((196, 160, 110), (74, 70, 70), tod), ink=INK, lw=2.0)
    palm(cv, 110, 600, 300, t, 50, 0.9, col=mix((54, 150, 84), (16, 44, 54), tod), seed=3)
    palm(cv, 1210, 610, 320, t, -60, 1.0, col=mix((54, 150, 84), (16, 44, 54), tod), seed=1)


# ----------------------------------------------------------------------------------------------------------------- 11 storm sea (on the raft)
def storm_sea(cv, t=0.0, flash=0.0, rain=1.0):
    band(cv, 0, 380, (36, 44, 66), (88, 104, 130), n=14, x0=0, x1=W)
    for i in range(10):
        cv.ellipse(i * 150 - 20 + 10 * math.sin(t * 0.5 + i), 70 + (i % 3) * 46, 190, 70, (52, 60, 84), ink=None, alpha=235)
    if flash > 0:
        cv.fill([(0, 0), (W, 0), (W, H), (0, H)], (240, 244, 255), ink=None, alpha=int(190 * flash))
        cv.stroke(spline([(820, 0), (790, 90), (830, 150), (780, 260), (810, 330)], n=1), (255, 255, 230), 7)
    band(cv, 380, H, (50, 92, 110), (14, 40, 60), n=10, x0=0, x1=W)
    for r in range(8):                                                                   # big rolling swells
        yy = 400 + r * 42
        amp = 10 + r * 6
        pts = [(x, yy + amp * math.sin(x * 0.006 + t * (1.4 + r * 0.1) + r * 1.4)) for x in range(-20, W + 40, 30)]
        cv.stroke(spline(pts, n=2), (170, 206, 214), 2.4 + r * 0.7, alpha=int(110 + r * 12))
        for x in range(0, W, 90):
            fx = x + 40 * math.sin(r + x)
            cv.ellipse(fx, yy + amp * math.sin(fx * 0.006 + t * (1.4 + r * 0.1) + r * 1.4) - 4, 22 + r * 3, 5, (240, 248, 252), ink=None, alpha=130)
    for i in range(70):
        x = (i * 97 + t * 80) % W
        y = ((t * 640 * rain + i * 53) % 760) - 20
        cv.stroke([(x, y), (x - 22, y + 56)], (214, 230, 244), 1.8, alpha=int(150 * rain))


# ----------------------------------------------------------------------------------------------------------------- 12 the ferry dawn
def ferry_dawn(cv, t=0.0, mist=1.0):
    band(cv, 0, 330, (255, 224, 170), (190, 226, 244), n=14, x0=0, x1=W)
    cv.ellipse(300, 320, 130, 130, (255, 236, 180), ink=None, alpha=90)
    for i in range(8):
        cv.ellipse(i * 180, 300 + 20 * math.sin(t * 0.4 + i), 190, 40, (255, 248, 232), ink=None, alpha=int(110 * mist))
    _sea(cv, 330, t, (196, 232, 238), (74, 160, 200), amp=3, lines=12, sparkle=0.8)
    _shore(cv, 520, t, wet=(240, 220, 176))
    palm(cv, 120, 620, 320, t, 60, 1.0)
    palm(cv, 1180, 640, 350, t, -70, 1.0, seed=2)
    for i in range(7):
        cv.ellipse(100 + i * 180, 700, 22, 5, SAND_SH, ink=None, alpha=130)
