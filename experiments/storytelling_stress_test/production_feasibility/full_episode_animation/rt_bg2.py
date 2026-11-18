"""More backgrounds for the red-thread story (v3): a golden-hour market lane, a warm storeroom for the activity (day -> night), a cherry-blossom tree corner. All procedural."""
from __future__ import annotations

import math

from props_uni import INK, W, H, band, cloud, mix, rect, rrect, spline
from rt_props2 import balloon, water_pile


def fairy_lights(cv, y0, y1, n, t, warm=1.0, x0=0, x1=W):
    """A string of fairy lights sagging between two heights, bulbs twinkling softly."""
    pts = [(x0 + (x1 - x0) * i / 40, y0 + (y1 - y0) * (i / 40) + 26 * math.sin(math.pi * i / 40)) for i in range(41)]
    cv.stroke(spline(pts, n=2), (90, 74, 66), 2.2)
    for j in range(n):
        px, py = pts[int((j + 0.5) / n * 40)]
        a = 0.6 + 0.4 * math.sin(t * 2.0 + j * 1.7)
        cv.ellipse(px, py + 6, 22, 22, (255, 220, 140), ink=None, alpha=int(60 * a * warm))
        cv.ellipse(px, py + 6, 6, 8, (255, 238, 170), ink=INK, lw=1.2)


def petals(cv, t, n=16, x0=0, x1=W, y0=0, y1=H):
    """Cherry-blossom petals drifting down through the picture."""
    for j in range(n):
        u = (t * 0.08 + j / n) % 1.0
        px = x0 + (x1 - x0) * (((j * 0.37) + 0.05 * math.sin(t * 0.7 + j)) % 1.0)
        py = y0 + (y1 - y0) * u
        cv.ellipse(px + 18 * math.sin(t * 1.1 + j), py, 5.5, 3.2, (255, 196, 214), ink=None, alpha=int(230 * math.sin(math.pi * min(1.0, u * 1.2))), rot=40 * math.sin(t + j) + 30)


def market_street(cv, t=0.0):
    """A lane of little shops at golden hour: awnings, flower pots, fairy lights, soft bokeh, a few drifting petals."""
    band(cv, 0, 470, (255, 232, 200), (250, 196, 172), n=12, x0=0, x1=W)
    for i, (x0, col) in enumerate(((20, (250, 140, 150)), (330, (140, 200, 230)), (640, (250, 206, 120)), (950, (170, 214, 160)))):
        rect(cv, x0, 170, x0 + 300, 470, mix(col, (255, 255, 255), 0.55), lw=2.6)
        for k in range(7):                                                           # striped awning
            cv.fill([(x0 + k * 43, 250), (x0 + k * 43 + 43, 250), (x0 + k * 43 + 47, 300), (x0 + k * 43 - 4, 300)], col if k % 2 == 0 else (255, 250, 244), ink=INK, lw=1.8)
        rect(cv, x0 + 30, 320, x0 + 270, 430, (255, 240, 214), lw=2.2)                # shop window with goods
        for k in range(5):
            rect(cv, x0 + 48 + k * 44, 360 + (k % 2) * 14, x0 + 76 + k * 44, 420, [(240, 110, 120), (120, 180, 230), (250, 200, 90), (140, 200, 140), (190, 140, 220)][(k + i) % 5], lw=1.6)
    rect(cv, 0, 470, W, H, (226, 184, 150), ink=None)
    for x in range(-40, W + 40, 120):                                                # cobbles
        cv.stroke([(x, 470), (x - 60 + (x - 640) * 0.1, H)], (200, 156, 124), 1.6, alpha=150)
    for y in (500, 540, 600, 670):
        cv.stroke([(0, y), (W, y)], (210, 168, 134), 1.4, alpha=120)
    for i in range(10):                                                              # flower pots along the front
        px = 60 + i * 130
        cv.fill([(px - 18, 470), (px + 18, 470), (px + 14, 500), (px - 14, 500)], (214, 120, 90), ink=INK, lw=1.8)
        for k in range(4):
            cv.ellipse(px - 12 + k * 8, 462 - (k % 2) * 8, 8, 8, [(250, 130, 160), (255, 214, 110), (190, 140, 230), (250, 170, 130)][(i + k) % 4], ink=INK, lw=1.2)
    fairy_lights(cv, 150, 190, 18, t, 1.0)
    fairy_lights(cv, 200, 230, 16, t + 1.3, 0.8)
    for i in range(12):
        cv.ellipse((i * 233) % W, 520 + (i * 67) % 160, 20 + (i % 3) * 8, 20 + (i % 3) * 8, (255, 236, 190), ink=None, alpha=24)
    petals(cv, t, 14)


def storeroom(cv, t=0.0, night=0.0):
    """A warm storeroom for the activity: shelves of boxes, a window with a blossom branch (day -> night), fairy lights, balloons, water packs, a rug on the wooden floor."""
    rect(cv, 0, 0, W, 470, (246, 226, 200), ink=None)
    if night > 0:
        cv.fill([(0, 0), (W, 0), (W, 470), (0, 470)], (50, 40, 80), ink=None, alpha=int(110 * night))
    rect(cv, 860, 90, 1180, 360, (255, 236, 214), lw=3.0)                            # the window
    rect(cv, 878, 108, 1162, 342, mix((255, 214, 176), (28, 34, 80), night), ink=None)
    if night > 0.2:
        cv.ellipse(1100, 160, 24, 24, (255, 246, 214), ink=None, alpha=int(255 * night))
        for i in range(10):
            cv.ellipse(890 + (i * 71) % 270, 120 + (i * 43) % 200, 1.8, 1.8, (255, 255, 235), ink=None, alpha=int(200 * night))
    cv.stroke([(1020, 108), (1020, 342)], (255, 250, 240), 4)
    cv.stroke([(878, 225), (1162, 225)], (255, 250, 240), 4)
    cv.stroke(spline([(1160, 120), (1060, 150), (960, 200), (880, 190)], n=4), (110, 78, 70), 7)
    for i in range(14):
        cv.ellipse(890 + (i * 37) % 260, 150 + ((i * 29) % 70), 9, 9, (255, 190, 208) if i % 3 else (255, 224, 232), ink=None, alpha=235)
    for sx in (30, 330):                                                             # shelves of boxes
        rect(cv, sx, 120, sx + 270, 470, (176, 130, 96), lw=2.8)
        for r in range(3):
            ry = 130 + r * 112
            rect(cv, sx + 6, ry + 100, sx + 264, ry + 108, (140, 100, 72), lw=1.6)
            x = sx + 12
            j = 0
            while x < sx + 240:
                bw = 38 + (j * 13 + r * 7) % 26
                bh = 44 + (j * 9 + r * 5) % 40
                col = [(214, 170, 116), (240, 130, 140), (130, 190, 230), (250, 206, 110), (150, 206, 150)][(j + r) % 5]
                rect(cv, x, ry + 100 - bh, x + bw, ry + 100, col, lw=1.6)
                x += bw + 4
                j += 1
    rect(cv, 0, 470, W, H, mix((196, 150, 108), (120, 90, 90), night * 0.4), ink=None)       # floor
    for x in range(-60, W + 60, 130):
        cv.stroke([(x, 470), (x - 50 + (x - 640) * 0.12, H)], (166, 120, 86), 2.0, alpha=140)
    cv.fill(spline([(180, 640), (360, 590), (940, 590), (1120, 640), (940, 720), (360, 720)], closed=True, n=3), (236, 170, 170), ink=INK, lw=2.4)       # a rug
    cv.fill(spline([(260, 640), (400, 604), (880, 604), (1020, 640), (880, 704), (400, 704)], closed=True, n=3), (252, 226, 214), ink=None, alpha=200)
    water_pile(cv, 1190, 540, layers=3, s=0.8)
    for i, col in enumerate(((250, 130, 150), (255, 214, 110), (130, 190, 240), (180, 150, 230))):
        balloon(cv, 700 + i * 34, 120 + (i % 2) * 22, col, 0.9, sway=6 * math.sin(t * 1.2 + i))
    fairy_lights(cv, 40, 70, 22, t, 1.0 + night * 0.9)
    petals(cv, t, 8, 860, 1180, 110, 470)


def sakura_tree(cv, t=0.0):
    """A big cherry-blossom tree in a quiet corner of the campus: pastel sky, blossoms overhead, falling petals, petals on the grass, soft light."""
    band(cv, 0, 470, (206, 232, 252), (255, 232, 238), n=12, x0=0, x1=W)
    cv.ellipse(1040, 140, 90, 90, (255, 248, 222), ink=None, alpha=120)
    cv.fill([(0, 470), (0, 380), (260, 340), (520, 400), (800, 350), (1100, 410), (1280, 370), (1280, 470)], (214, 224, 238), ink=None)
    rect(cv, 0, 470, W, H, (176, 212, 150), ink=None)
    rect(cv, 0, 470, W, 500, (190, 222, 164), ink=None)
    cv.fill([(150, 720), (196, 720), (212, 470), (190, 300), (170, 300), (160, 470)], (112, 80, 70), ink=INK, lw=2.8, shade_col=(86, 60, 54), depth=6)    # trunk and branches
    for pts in (((180, 330), (120, 250), (30, 200)), ((190, 320), (300, 240), (420, 190)), ((184, 300), (260, 160), (380, 60)), ((176, 300), (110, 150), (60, 40))):
        cv.stroke(spline(list(pts), n=3), (112, 80, 70), 14)
    for i in range(110):                                                             # the canopy
        cx = 20 + (i * 47) % 520
        cy = 20 + ((i * 31) % 240) + (cx * 0.08)
        r = 22 + (i % 5) * 6
        cv.ellipse(cx, cy, r, r * 0.86, [(255, 196, 214), (255, 214, 226), (250, 176, 200), (255, 230, 238)][i % 4], ink=None, alpha=235)
    for i in range(34):
        cv.ellipse(30 + (i * 83) % 520, 40 + (i * 53) % 260, 5, 5, (255, 255, 255), ink=None, alpha=120)
    petals(cv, t, 22, 0, 760, 60, 520)
    for i in range(30):                                                              # petals on the grass
        cv.ellipse(40 + (i * 109) % 1200, 520 + (i * 41) % 190, 6, 3.4, (255, 204, 220), ink=None, alpha=210, rot=(i * 37) % 180)
    for i in range(10):
        cv.ellipse((i * 251) % W, 540 + (i * 71) % 150, 22 + (i % 3) * 8, 22 + (i % 3) * 8, (255, 240, 214), ink=None, alpha=22)
