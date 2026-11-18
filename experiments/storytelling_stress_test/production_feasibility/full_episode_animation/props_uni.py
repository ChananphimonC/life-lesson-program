"""Backgrounds, the red thread and small props for the red-thread campus story (procedural; no text in the world except icons)."""
from __future__ import annotations

import math

from props_future import *  # noqa: F401,F403  (rect, rrect, band, bubble, waves, dashed, coin, arrow, ambient, PH ...)

RED = (232, 52, 70)
RED_GLOW = (255, 120, 130)
CREAM = (250, 240, 222)
WOOD = (190, 146, 104)
WOOD_SH = (160, 118, 82)


# ----------------------------------------------------------------------------------------------------------------- the thread
def thread(cv, a, b, t=0.0, sag=70, w=3.4, slack=1.0, glow=True, extra=None, alpha=255):
    """The red thread between two points (pinkies). It hangs in a soft catenary that sways; `extra` = more points to pass through (for tangles)."""
    pts_in = [a] + (extra or []) + [b]
    pts = []
    for (x0, y0), (x1, y1) in zip(pts_in, pts_in[1:]):
        n = 10
        for i in range(n):
            u = i / n
            sw = math.sin(t * 1.6 + u * 5 + x0 * 0.01) * 4 * slack
            pts.append((x0 + (x1 - x0) * u, y0 + (y1 - y0) * u + sag * slack * math.sin(math.pi * u) + sw))
    pts.append(b)
    if glow:
        cv.stroke(spline(pts, n=3), RED_GLOW, w + 7, alpha=int(70 * alpha / 255))
    cv.stroke(spline(pts, n=3), RED, w, alpha=alpha)
    # tiny sparkle running along the thread
    k = int((t * 12) % len(pts))
    x, y = pts[k]
    cv.ellipse(x, y, 3.2, 3.2, (255, 235, 235), ink=None, alpha=int(200 * alpha / 255))
    return pts


def pinky(who_pos, side="R", dx=0, dy=0):
    x, y = who_pos
    return (x + dx, y + dy + 10)


def spool(cv, x, y, r=22, turn=0.0, col=RED):
    cv.ellipse(x, y, r, r * 0.9, col, ink=INK, lw=2.4, shade_col=mix(col, (0, 0, 0), 0.2))
    for k in range(4):
        a = turn + k * math.pi / 2
        cv.stroke([(x + math.cos(a) * r * 0.2, y + math.sin(a) * r * 0.2), (x + math.cos(a) * r * 0.85, y + math.sin(a) * r * 0.8)], mix(col, (255, 255, 255), 0.35), 2)
    rect(cv, x - r * 0.3, y - r * 1.3, x + r * 0.3, y - r * 0.8, (210, 170, 110), lw=1.6)


# ----------------------------------------------------------------------------------------------------------------- campus rooms
def lecture(cv, t=0.0, tod="day"):
    """Tech faculty lecture hall seen from the back-left: a big screen, windows, two rows of desks with laptops (drawn behind the students; desk fronts via desk_front)."""
    band(cv, 0, 430, (244, 238, 226), (232, 224, 208), n=8, x0=0, x1=W)
    rect(cv, 0, 430, W, H, (196, 170, 138), ink=None)
    # screen with code lines and a little circuit
    rrect(cv, 330, 60, 950, 340, 12, (252, 252, 254), lw=3.0)
    for i in range(6):
        L = 120 + ((i * 53) % 5) * 60
        rect(cv, 370, 100 + i * 34, 370 + L, 112 + i * 34, [(90, 150, 220), (120, 200, 160), (240, 170, 90)][i % 3], ink=None)
    cv.stroke([(780, 120), (820, 120), (820, 170), (870, 170)], (60, 70, 100), 3)
    for (cx, cy) in ((780, 120), (870, 170), (820, 220)):
        cv.ellipse(cx, cy, 7, 7, (255, 200, 70) if int(t * 2) % 2 else (240, 230, 160), ink=INK, lw=1.6)
    # windows with daylight
    for wx in (1040, 1150):
        rect(cv, wx, 90, wx + 96, 330, (190, 226, 248), lw=2.8)
        cv.stroke([(wx + 48, 90), (wx + 48, 330)], (252, 252, 254), 3)
        cv.stroke([(wx, 210), (wx + 96, 210)], (252, 252, 254), 3)
    # ceiling lamps
    for lx in (250, 640, 1030):
        rect(cv, lx - 50, 0, lx + 50, 14, (250, 250, 252), lw=2.0)


def desks(cv, y, x0=-20, x1=W + 20, laptops=True, t=0.0, col=WOOD):
    rect(cv, x0, y, x1, y + 26, col, lw=2.6, shade_col=WOOD_SH)
    rect(cv, x0, y + 26, x1, y + 70, mix(col, (0, 0, 0), 0.12), lw=2.6)
    if laptops:
        for i, x in enumerate(range(80, W, 190)):
            laptop(cv, x + 20 * math.sin(i), y + 6, 0.5, t, screen=[(80, 140, 200), (110, 190, 150), (240, 180, 100)][i % 3])


def library(cv, t=0.0):
    band(cv, 0, 470, (236, 224, 204), (222, 206, 182), n=8, x0=0, x1=W)
    rect(cv, 0, 470, W, H, (176, 140, 104), ink=None)
    cols = [(206, 90, 80), (90, 140, 200), (240, 190, 80), (110, 170, 120), (170, 120, 190), (230, 140, 100)]
    for sx in (30, 440, 850):
        rect(cv, sx, 70, sx + 380, 470, (150, 108, 76), lw=2.8)
        for r in range(4):
            ry = 90 + r * 94
            rect(cv, sx + 8, ry + 84, sx + 372, ry + 92, (120, 86, 60), lw=1.6)
            x = sx + 14
            j = 0
            while x < sx + 360:
                bw = 16 + (j * 7 + r * 5) % 14
                bh = 56 + (j * 11 + r * 3) % 24
                rect(cv, x, ry + 84 - bh, x + bw, ry + 84, cols[(j + r) % 6], lw=1.2)
                x += bw + 2
                j += 1
    # reading lamp glow
    cv.ellipse(1130, 360, 90, 90, (255, 236, 160), ink=None, alpha=70)


def corridor(cv, t=0.0):
    band(cv, 0, 440, (238, 236, 228), (224, 224, 214), n=8, x0=0, x1=W)
    rect(cv, 0, 440, W, H, (200, 196, 184), ink=None)
    for x in range(0, W, 160):
        cv.stroke([(x, 440), (x - 80 + (x - 640) * 0.2, H)], (184, 180, 168), 1.4, alpha=120)
    # lockers
    for i in range(7):
        rect(cv, 40 + i * 70, 160, 100 + i * 70, 440, [(110, 160, 200), (130, 180, 210)][i % 2], lw=2.2)
        rect(cv, 50 + i * 70, 190, 90 + i * 70, 200, (60, 90, 130), ink=None)
        cv.ellipse(94 + i * 70 - 8, 300, 3, 3, (230, 230, 240), ink=INK, lw=1.0)
    # the restroom door at the right, with two little signs
    rect(cv, 900, 140, 1100, 440, (176, 130, 96), lw=3.0, shade_col=WOOD_SH)
    rect(cv, 930, 90, 1070, 130, (252, 252, 254), lw=2.4)
    cv.ellipse(965, 108, 9, 9, (80, 140, 220), ink=None)
    cv.fill([(955, 118), (975, 118), (978, 126), (952, 126)], (80, 140, 220), ink=None)
    cv.ellipse(1035, 108, 9, 9, (230, 100, 150), ink=None)
    cv.fill([(1022, 128), (1048, 128), (1035, 114)], (230, 100, 150), ink=None)
    cv.ellipse(1086, 292, 6, 6, (210, 210, 218), ink=INK, lw=1.4)       # the door knob (the thread gets caught on it)
    # window
    rect(cv, 1160, 130, 1260, 360, (190, 226, 248), lw=2.6)


def stairs_night(cv, t=0.0):
    band(cv, 0, 480, (22, 30, 70), (84, 74, 126), n=18, x0=0, x1=W)
    for i in range(60):
        x, y = (i * 211) % W, (i * 97) % 300
        cv.ellipse(x, y, 1.8, 1.8, (255, 255, 235), ink=None, alpha=int(110 + 100 * math.sin(t * 2 + i)))
    cv.ellipse(1060, 120, 54, 54, (252, 246, 214), ink=None)
    cv.ellipse(1080, 112, 46, 46, (22, 30, 70), ink=None, alpha=0)
    # building with lit windows
    rect(cv, -10, 150, 700, 470, (70, 82, 128), lw=3.0)
    for r in range(4):
        for c in range(9):
            lit = (r * 7 + c * 3) % 5 < 3
            rect(cv, 20 + c * 74, 180 + r * 64, 70 + c * 74, 220 + r * 64, (255, 226, 150) if lit else (50, 60, 100), ink=None)
    rect(cv, -10, 470, W + 10, H, (96, 98, 126), ink=None)
    # steps
    for i in range(5):
        y = 470 + i * 56
        rect(cv, 220 + i * 6, y, 1000 - i * 6, y + 56, mix((170, 170, 190), (120, 120, 150), i / 5), lw=2.4)
    # lamp posts
    for lx in (100, 1180):
        cv.stroke([(lx, 470), (lx, 230)], (110, 114, 140), 6)
        cv.ellipse(lx, 222, 22, 22, (255, 236, 160), ink=INK, lw=2.4)
        cv.ellipse(lx, 222, 52, 52, (255, 236, 160), ink=None, alpha=44)


def moon_sky(cv, t=0.0, moon=True):
    band(cv, 0, H, (18, 24, 64), (66, 60, 118), n=20, x0=0, x1=W)
    for i in range(80):
        x, y = (i * 173) % W, (i * 89) % 560
        cv.ellipse(x, y, 1.6 + (i % 3) * 0.6, 1.6 + (i % 3) * 0.6, (255, 255, 235), ink=None, alpha=int(110 + 110 * math.sin(t * 2.2 + i)))
    if moon:
        cv.ellipse(640, 220, 130, 130, (252, 246, 216), ink=None, alpha=44)
        cv.ellipse(640, 220, 104, 104, (252, 246, 214), ink=None)
        for (dx, dy, r) in ((-30, -20, 16), (24, 28, 22), (36, -34, 10)):
            cv.ellipse(640 + dx, 220 + dy, r, r, (236, 228, 190), ink=None)


def cloud(cv, x, y, s=1.0, col=(236, 236, 248)):
    for dx, dy, r in ((-60, 8, 38), (-20, -12, 46), (30, -6, 44), (70, 10, 34), (0, 18, 50)):
        cv.ellipse(x + dx * s, y + dy * s, r * s, r * s * 0.8, col, ink=None)


def airport(cv, t=0.0):
    band(cv, 0, 430, (226, 238, 250), (210, 226, 244), n=8, x0=0, x1=W)
    rect(cv, 0, 430, W, H, (198, 204, 214), ink=None)
    # big window with a plane gliding past
    rect(cv, 60, 60, 1220, 330, (170, 214, 244), lw=3.0)
    px = 100 + (t * 60) % 1100
    cv.fill([(px, 220), (px + 120, 206), (px + 150, 214), (px + 120, 224)], (250, 250, 252), ink=INK, lw=2.0)
    cv.fill([(px + 60, 214), (px + 96, 180), (px + 104, 184), (px + 84, 216)], (230, 232, 240), ink=INK, lw=1.6)
    # a departure board (just coloured rows, no text)
    rrect(cv, 400, 350, 880, 420, 8, (30, 40, 70), lw=2.4)
    for i in range(3):
        rect(cv, 420, 362 + i * 18, 560 + 120 * ((i * 3) % 3 + 1), 370 + i * 18, (255, 214, 90) if i == 0 else (130, 200, 240), ink=None)
    for i in range(5):
        rrect(cv, 80 + i * 240, 620, 80 + i * 240 + 170, 690, 10, (90, 110, 160), lw=2.0)


def teahouse(cv, t=0.0):
    band(cv, 0, 440, (252, 238, 212), (240, 220, 190), n=8, x0=0, x1=W)
    rect(cv, 0, 440, W, H, (184, 142, 102), ink=None)
    rect(cv, 140, 90, 360, 250, (200, 232, 248), lw=3.0)
    cv.stroke([(250, 90), (250, 250)], (252, 252, 254), 3)
    for lx in (640, 900):
        sw = 9 * math.sin(t * 1.6 + lx)
        cv.stroke([(lx, 0), (lx + sw * 0.5, 70)], (120, 90, 70), 3)
        cv.fill([(lx - 36 + sw, 120), (lx + 36 + sw, 120), (lx + 20 + sw * 0.5, 70), (lx - 20 + sw * 0.5, 70)], (252, 214, 140), ink=INK, lw=2.4)
    rect(cv, 380, 560, 900, 592, (150, 106, 72), lw=2.8, shade_col=(124, 88, 60))
    for lx in (420, 850):
        rect(cv, lx, 592, lx + 20, 700, (124, 88, 60), lw=2.0)


def world_threads(cv, t=0.0):
    """A map-like picture: sea, a mountain range, two towns far apart and the thread arcing over everything."""
    band(cv, 0, H, (150, 210, 244), (214, 240, 252), n=14, x0=0, x1=W)
    cv.fill([(0, 600), (260, 440), (420, 600)], (120, 160, 130), ink=INK, lw=2.4)
    cv.fill([(220, 600), (480, 380), (700, 600)], (140, 176, 140), ink=INK, lw=2.4)
    cv.fill([(480, 440), (560, 340), (640, 440)], (250, 250, 252), ink=INK, lw=2.0)
    rect(cv, 0, 600, W, H, (96, 170, 222), ink=None)
    for i in range(8):
        y = 620 + i * 12
        cv.stroke(spline([(0, y), (320, y + 8 * math.sin(t * 2 + i)), (640, y), (960, y + 8 * math.sin(t * 2 + i + 2)), (1280, y)], n=4), (170, 214, 244), 2.2, alpha=140)
    for x, y in ((120, 560), (1160, 560)):
        cv.fill([(x - 40, y + 40), (x - 40, y), (x, y - 40), (x + 40, y), (x + 40, y + 40)], (236, 216, 190), ink=INK, lw=2.2)
        rect(cv, x - 12, y + 6, x + 12, y + 40, (190, 120, 90), lw=1.6)


def mortarboard(cv, x, y, s=1.0, tilt=0.0):
    """A graduation cap over a head centre (x, y): board + tassel."""
    cv.push(x, y, rot=tilt, scale=s)
    cv.fill([(-46, 0), (0, -16), (46, 0), (0, 16)], (28, 28, 38), ink=INK, lw=2.2)
    cv.fill([(-26, 8), (26, 8), (22, 24), (-22, 24)], (40, 40, 52), ink=INK, lw=2.0)
    cv.stroke([(0, 0), (40, 12), (42, 36)], (240, 200, 70), 3)
    cv.ellipse(42, 38, 4, 6, (240, 200, 70), ink=INK, lw=1.2)
    cv.pop()
