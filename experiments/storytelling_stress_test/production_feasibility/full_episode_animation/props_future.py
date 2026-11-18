"""Backgrounds, robots and props for the future-world story (all procedural, drawn with the rig's Canvas; no text in the world, only icons)."""
from __future__ import annotations

import math

from props import *  # noqa: F401,F403

WHITE = (246, 248, 250)
WHITE_SH = (214, 222, 232)
TEAL = (92, 188, 182)
TEAL_SH = (62, 150, 148)
NAVY = (44, 62, 100)
CYAN = (120, 230, 240)
ORANGE = (255, 168, 84)
LILAC = (172, 150, 222)
GLASS = (170, 214, 236)
PH = [0.0]                     # scene time, set by rw_common.tick(); drives marching dashes and ambient particles
SKYLINE = (96, 120, 168)


def rrect(cv, x0, y0, x1, y1, r, col, ink=INK, lw=2.4, shade_col=None, alpha=255):
    pts = []
    for cx, cy, a0 in ((x1 - r, y0 + r, -90), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180)):
        for k in range(6):
            a = math.radians(a0 + 90 * k / 5)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    cv.fill(pts, col, ink=ink, lw=lw, shade_col=shade_col, depth=4, alpha=alpha)


def waves(cv, x, y, u, n=3, r0=14, dr=14, col=(255, 255, 255), a0=-50, a1=50, lw=4, flip=False):
    """Sound waves leaving (x, y); u 0..1 moves them outward and fades them."""
    for k in range(n):
        f = (u * 1.5 + k / n) % 1.0
        r = r0 + dr * k + dr * f * 0.6
        pts = ellipse_pts(x, y, r, r, n=14, a0=(180 - a1) if flip else a0, a1=(180 - a0) if flip else a1)
        cv.stroke(pts, col, lw, alpha=int(235 * (1 - f * 0.7)))


# ----------------------------------------------------------------------------------------------------------------- city
def skyline(cv, horizon, scroll=0.0, seed=3, tod="morning", layers=2):
    """Towers in two parallax layers. scroll is pixels (the near layer moves faster)."""
    night = tod in ("dusk", "night")
    for layer in range(layers):
        k = 0.35 + 0.45 * layer
        col = mix(SKYLINE, (150, 176, 214), 0.5 - 0.35 * layer) if not night else mix((50, 56, 96), (90, 96, 140), layer * 0.5)
        x = -200 - ((scroll * k) % 220)
        i = 0
        while x < W + 220:
            wdt = 90 + ((i * 37 + seed * 11 + layer * 13) % 5) * 22
            hgt = 120 + ((i * 53 + seed * 17 + layer * 29) % 6) * 38 - layer * 30
            top = horizon - hgt
            cv.fill([(x, horizon + 4), (x, top + 12), (x + 14, top), (x + wdt - 14, top), (x + wdt, top + 12), (x + wdt, horizon + 4)], col, ink=INK if layer else None, lw=1.6)
            if layer == layers - 1:
                for wy in range(int(top + 26), int(horizon - 10), 26):
                    for wx in range(int(x + 14), int(x + wdt - 14), 22):
                        if (wx * 7 + wy * 3 + i) % 5 < 3:
                            cv.fill([(wx, wy), (wx + 11, wy), (wx + 11, wy + 12), (wx, wy + 12)], (255, 236, 160) if night else (200, 226, 244), ink=None)
            x += wdt + 18
            i += 1


def drones(cv, t, n=4, y0=120, x_speed=60):
    for i in range(n):
        x = (i * 340 + t * x_speed * (1 + 0.3 * (i % 2))) % (W + 200) - 100
        y = y0 + 30 * math.sin(t * 1.3 + i * 2) + i * 18
        cv.ellipse(x, y, 16, 7, WHITE, ink=INK, lw=1.6, shade_col=WHITE_SH)
        for dx in (-20, 20):
            cv.stroke([(x + dx * 0.7, y - 3), (x + dx, y - 6)], INK, 1.6)
            sp = math.sin(t * 40 + i + dx) * 12
            cv.stroke([(x + dx - sp, y - 7), (x + dx + sp, y - 7)], (90, 90, 100), 2.4)
        cv.ellipse(x, y + 4, 3, 3, ORANGE, ink=None)


def street(cv, t=0.0, scroll=0.0, tod="morning", horizon=360):
    sky = {"morning": ((150, 208, 240), (255, 238, 204)), "day": ((132, 198, 238), (232, 244, 250)), "dusk": ((86, 98, 160), (250, 174, 132)),
           "night": ((24, 32, 70), (74, 70, 118))}[tod]
    band(cv, -20, horizon, sky[0], sky[1], n=22)
    skyline(cv, horizon, scroll, tod=tod)
    drones(cv, t)
    # elevated rail
    rect(cv, -20, horizon - 70, W + 20, horizon - 56, (190, 198, 214), lw=2.0)
    for x in range(int(-(scroll * 0.9) % 260) - 260, W + 260, 260):
        rect(cv, x, horizon - 56, x + 16, horizon + 6, (170, 180, 200), lw=1.8)
    # sidewalk + road
    rect(cv, -20, horizon, W + 20, horizon + 70, (214, 214, 220), lw=2.0)
    band(cv, horizon + 70, H + 10, (110, 116, 134), (84, 90, 110), n=10)
    for x in range(int(-(scroll) % 150) - 150, W + 150, 150):
        rect(cv, x, 560, x + 70, 568, (240, 240, 244), ink=None)
    # a few street lamps / sensors
    for x in range(int(-(scroll * 1.1) % 420) - 420, W + 420, 420):
        cv.stroke([(x, horizon + 60), (x, horizon - 40)], (120, 130, 150), 5)
        cv.ellipse(x, horizon - 44, 9, 9, CYAN, ink=INK, lw=1.6)


# ----------------------------------------------------------------------------------------------------------------- robots
def face_screen(cv, x, y, w, h, mood="happy", t=0.0, blink=False):
    rrect(cv, x - w / 2, y - h / 2, x + w / 2, y + h / 2, h * 0.3, NAVY, lw=2.0)
    ey = y - h * 0.08
    for dx in (-w * 0.2, w * 0.2):
        if blink or mood == "blink":
            cv.stroke([(x + dx - 6, ey), (x + dx + 6, ey)], CYAN, 3)
        elif mood == "think":
            cv.ellipse(x + dx, ey, 5, 3, CYAN, ink=None)
        else:
            cv.ellipse(x + dx, ey, 5, 6.5, CYAN, ink=None)
    if mood == "happy":
        cv.stroke(spline([(x - 8, y + h * 0.18), (x, y + h * 0.3), (x + 8, y + h * 0.18)], n=3), CYAN, 2.6)
    elif mood == "flat":
        cv.stroke([(x - 7, y + h * 0.24), (x + 7, y + h * 0.24)], CYAN, 2.6)
    elif mood == "sorry":
        cv.stroke(spline([(x - 8, y + h * 0.3), (x, y + h * 0.2), (x + 8, y + h * 0.3)], n=3), CYAN, 2.6)


def service_bot(cv, x, y, s=1.0, flip=False, t=0.0, mood="happy", wave=0.0, carry=None, ph=0.0, moving=False):
    """A friendly rolling service robot, feet (wheel) at y. wave 0..1 raises an arm; carry=(kind) draws a tray."""
    sg = -1 if flip else 1
    bob = math.sin(t * 3 + x * 0.01) * 2 * s if not moving else abs(math.sin(ph)) * 3 * s
    cv.ellipse(x, y + 2, 26 * s, 6 * s, (0, 0, 0), alpha=40)
    # wheel base
    rrect(cv, x - 22 * s, y - 16 * s, x + 22 * s, y - 2 * s, 7 * s, (120, 130, 150), lw=2.0)
    for dx in (-14, 14):
        cv.ellipse(x + dx * s, y - 7 * s, 7 * s, 7 * s, (60, 66, 84), ink=INK, lw=1.6)
    # body
    by = y - 16 * s - bob
    rrect(cv, x - 20 * s, by - 48 * s, x + 20 * s, by, 11 * s, WHITE, lw=2.4, shade_col=WHITE_SH)
    cv.ellipse(x, by - 22 * s, 6 * s, 6 * s, ORANGE, ink=INK, lw=1.4)
    # arms
    for side in (-1, 1):
        up = wave if side == sg else 0
        sx, sy = x + side * 21 * s, by - 38 * s
        ex = sx + side * (10 + 8 * up) * s
        ey = sy + (16 - 40 * up + 5 * math.sin(t * 9) * up) * s
        cv.stroke([(sx, sy), (ex, ey)], (190, 200, 216), 7 * s)
        cv.ellipse(ex, ey, 5.5 * s, 5.5 * s, TEAL, ink=INK, lw=1.4)
    # head
    hy = by - 62 * s
    cv.stroke([(x, by - 48 * s), (x, hy + 14 * s)], (150, 160, 180), 6 * s)
    rrect(cv, x - 24 * s, hy - 20 * s, x + 24 * s, hy + 18 * s, 13 * s, WHITE, lw=2.4, shade_col=WHITE_SH)
    face_screen(cv, x, hy - 1 * s, 38 * s, 26 * s, mood, t, blink=(math.sin(t * 1.7 + x) > 0.97))
    cv.stroke([(x, hy - 20 * s), (x, hy - 30 * s)], INK, 2.0)
    cv.ellipse(x, hy - 32 * s, 3.5 * s, 3.5 * s, ORANGE if int(t * 2) % 2 else CYAN, ink=INK, lw=1.2)
    if carry == "tray":
        cv.stroke([(x + sg * 24 * s, by - 28 * s), (x + sg * 44 * s, by - 28 * s)], (190, 200, 216), 5 * s)
        rect(cv, x + sg * 30 * s, by - 32 * s, x + sg * 58 * s, by - 29 * s, (170, 180, 200), lw=1.4)


def delivery_bot(cv, x, y, s=1.0, t=0.0, load=True, flip=False):
    sg = -1 if flip else 1
    cv.ellipse(x, y + 2, 28 * s, 5 * s, (0, 0, 0), alpha=40)
    rrect(cv, x - 26 * s, y - 34 * s, x + 26 * s, y - 8 * s, 8 * s, TEAL, lw=2.2, shade_col=TEAL_SH)
    if load:
        rect(cv, x - 16 * s, y - 52 * s, x + 14 * s, y - 34 * s, (232, 196, 140), lw=1.8)
    for dx in (-16, 16):
        cv.ellipse(x + dx * s, y - 8 * s, 8 * s, 8 * s, (60, 66, 84), ink=INK, lw=1.6)
        a = t * 8 + dx
        cv.stroke([(x + dx * s, y - 8 * s), (x + dx * s + math.cos(a) * 6 * s, y - 8 * s + math.sin(a) * 6 * s)], (200, 200, 210), 1.6)
    cv.ellipse(x + sg * 20 * s, y - 24 * s, 3.5 * s, 3.5 * s, CYAN, ink=None)


def arm_robot(cv, x, y, s=1.0, t=0.0, ph=0.0, tool="spatula", target=None):
    """Kitchen arm: base on the counter at (x, y); two segments swinging by phase; ends in a gripper holding a tool."""
    rrect(cv, x - 26 * s, y - 14 * s, x + 26 * s, y, 5 * s, (120, 130, 150), lw=2.0)
    cv.ellipse(x, y - 16 * s, 12 * s, 12 * s, WHITE, ink=INK, lw=2.0, shade_col=WHITE_SH)
    a1 = math.radians(-60 + 25 * math.sin(ph))
    a2 = math.radians(40 + 40 * math.sin(ph * 1.7 + 1))
    j1 = (x + math.cos(a1) * 70 * s, y - 16 * s + math.sin(a1) * 70 * s)
    cv.stroke([(x, y - 16 * s), j1], (190, 200, 216), 13 * s)
    cv.stroke([(x, y - 16 * s), j1], WHITE, 7 * s)
    j2 = (j1[0] + math.cos(a1 + a2) * 62 * s, j1[1] + math.sin(a1 + a2) * 62 * s)
    if target:
        j2 = target
    cv.stroke([j1, j2], (190, 200, 216), 11 * s)
    cv.stroke([j1, j2], WHITE, 5.5 * s)
    cv.ellipse(j1[0], j1[1], 8 * s, 8 * s, ORANGE, ink=INK, lw=1.6)
    cv.ellipse(j2[0], j2[1], 6 * s, 6 * s, TEAL, ink=INK, lw=1.6)
    dx, dy = j2[0] - j1[0], j2[1] - j1[1]
    n = math.hypot(dx, dy) or 1
    tip = (j2[0] + dx / n * 22 * s, j2[1] + dy / n * 22 * s + 6 * s)
    if tool == "spatula":
        cv.stroke([j2, tip], (150, 150, 160), 3.4 * s)
        cv.fill(rot_pts([(tip[0] - 9 * s, tip[1]), (tip[0] + 9 * s, tip[1]), (tip[0] + 9 * s, tip[1] + 14 * s), (tip[0] - 9 * s, tip[1] + 14 * s)], tip[0], tip[1], math.atan2(dy, dx) - math.pi / 2),
                (200, 204, 214), ink=INK, lw=1.4)
    return j2


def pod(cv, x, y, s=1.0, door=0.0, t=0.0, flip=False, lights=True, window_people=None, tilt=0.0):
    """Driverless pod (side view, feet/wheels at y). door 0..1 slides the door open. window_people: list of (dx, kind) drawn through the glass."""
    sg = -1 if flip else 1
    cv.push(x, y, rot=tilt, scale=s, flip=flip)
    cv.ellipse(0, 4, 118, 10, (0, 0, 0), alpha=44)
    body = [(-112, -30), (-108, -62), (-84, -96), (-30, -112), (40, -112), (92, -92), (114, -58), (116, -30), (108, -14), (-104, -14)]
    cv.fill(spline(body, closed=True, n=5), (244, 250, 250), ink=INK, lw=3.0, shade_col=(206, 224, 228), depth=9)
    cv.fill(spline([(-104, -36), (-100, -50), (110, -50), (112, -36)], closed=True, n=3), TEAL, ink=None)
    # window band
    win = [(-84, -66), (-60, -98), (30, -104), (80, -90), (100, -64), (-84, -64)]
    cv.fill(spline(win, closed=True, n=4), GLASS, ink=INK, lw=2.2, shade_col=(130, 184, 214))
    for dx, kind in (window_people or []):
        hx, hy = dx, -80
        cv.ellipse(hx, hy, 11, 12, (231, 190, 152) if kind != "chok" else (190, 142, 104), ink=INK, lw=1.4)
        cv.ellipse(hx, hy - 6, 11, 8, (40, 34, 38) if kind != "chok" else (150, 150, 158), ink=None)
        cv.fill([(hx - 14, hy + 12), (hx + 14, hy + 12), (hx + 16, -64), (hx - 16, -64)], (240, 140, 80) if kind == "ton" else (86, 120, 150), ink=INK, lw=1.4)
    # door: an outlined panel that slides toward the rear and narrows as it opens, uncovering the dark cabin
    dw = 66 * (1 - door)
    if door > 0.02:
        cv.fill([(-30, -96), (36, -96), (36, -18), (-30, -18)], (64, 78, 104), ink=INK, lw=2.0)
        cv.fill([(-26, -64), (32, -64), (32, -30), (-26, -30)], (96, 112, 140), ink=None)
    if dw > 1:
        cv.fill([(-30 + 66 * door, -96), (-30 + 66 * door + dw, -96), (-30 + 66 * door + dw, -18), (-30 + 66 * door, -18)], (236, 246, 248), ink=INK, lw=2.0,
                shade_col=(206, 224, 228))
        cv.fill([(-26 + 66 * door, -92), (-26 + 66 * door + max(dw - 8, 1), -92), (-26 + 66 * door + max(dw - 8, 1), -66), (-26 + 66 * door, -66)], GLASS, ink=None)
    # lidar dome
    cv.ellipse(0, -116, 14, 8, (60, 70, 96), ink=INK, lw=2.0)
    a = t * 6
    cv.stroke([(0, -116), (math.cos(a) * 22, -116 - 4 + math.sin(a) * 3)], CYAN, 2.4, alpha=200)
    # wheels
    for wx in (-70, 74):
        cv.ellipse(wx, -14, 20, 20, (50, 54, 70), ink=INK, lw=2.4)
        cv.ellipse(wx, -14, 9, 9, (190, 196, 210), ink=INK, lw=1.4)
        aa = -t * 12 * sg + wx
        cv.stroke([(wx, -14), (wx + math.cos(aa) * 8, -14 + math.sin(aa) * 8)], (110, 116, 130), 2)
    if lights:
        cv.ellipse(110, -42, 6, 5, (255, 244, 170), ink=INK, lw=1.4)
        cv.ellipse(-108, -42, 5, 4, (250, 110, 100), ink=INK, lw=1.2)
    cv.pop()


def pod_inside(cv, t=0.0, scroll=0.0, wheel_hint=False):
    """Interior of a pod: large window with the city sliding past, two bench seats facing each other, a small round display, no steering wheel."""
    rect(cv, 0, 0, W, H, (232, 238, 242), ink=None)
    # window
    rrect(cv, 70, 60, W - 70, 420, 30, GLASS, lw=4.0)
    cv.push(70, 60)
    # city through the glass (clip by redrawing frame after)
    band(cv, 0, 250, (150, 208, 240), (255, 238, 204), n=12, x0=0, x1=W - 140)
    cv.pop()
    skyline(cv, 330, scroll * 2.2, seed=5, tod="morning")
    rect(cv, 70, 330, W - 70, 420, (214, 214, 220), ink=None)
    rect(cv, 70, 372, W - 70, 420, (100, 106, 126), ink=None)
    for x in range(int(-(scroll * 3.4) % 160) - 160, W, 160):
        rect(cv, x, 398, x + 70, 404, (240, 240, 244), ink=None)
    # hide the overflow of the skyline outside the window with the cabin walls
    rect(cv, -10, -10, 70, H + 10, (232, 238, 242), ink=None)
    rect(cv, W - 70, -10, W + 10, H + 10, (232, 238, 242), ink=None)
    rect(cv, -10, -10, W + 10, 60, (232, 238, 242), ink=None)
    rect(cv, -10, 420, W + 10, H + 10, (206, 216, 226), ink=None)
    rrect(cv, 70, 60, W - 70, 420, 30, GLASS, lw=4.0, alpha=0)
    cv.stroke([(70, 60), (W - 70, 60), (W - 70, 420), (70, 420), (70, 60)], INK, 4)
    cv.stroke(spline([(100, 80), (180, 70), (240, 140)], n=4), (255, 255, 255), 6, alpha=120)
    # floor
    rect(cv, -10, 560, W + 10, H + 10, (196, 206, 220), ink=None)
    # display (where the dashboard would be)
    rrect(cv, W / 2 - 62, 470, W / 2 + 62, 550, 12, NAVY, lw=2.6)
    cv.ellipse(W / 2, 510, 20, 20, CYAN, ink=None, alpha=120 + int(80 * math.sin(t * 4)))


def pod_benches(cv, t=0.0):
    """The two bench seats, drawn after the passengers so they sit behind them."""
    for bx, flipx in ((250, 1), (W - 250, -1)):
        rrect(cv, bx - 170, 650, bx + 170, 740, 24, TEAL, lw=2.6, shade_col=TEAL_SH)
        rrect(cv, bx - 170 if flipx > 0 else bx + 126, 420, bx - 126 if flipx > 0 else bx + 170, 740, 20, TEAL_SH, lw=2.0)


# ----------------------------------------------------------------------------------------------------------------- food
def kiosk(cv, x, y, s=1.0, t=0.0, listening=0.0, ok=0.0):
    """Tall ordering kiosk; listening 0..1 shows a mic glow and wave bars; ok 0..1 shows a tick on the screen."""
    cv.ellipse(x, y + 2, 50 * s, 8 * s, (0, 0, 0), alpha=40)
    rrect(cv, x - 44 * s, y - 220 * s, x + 44 * s, y, 12 * s, (232, 160, 96), lw=2.8, shade_col=(200, 126, 70))
    rrect(cv, x - 34 * s, y - 206 * s, x + 34 * s, y - 120 * s, 8 * s, NAVY, lw=2.2)
    # menu tiles (icons only): rice plate, noodle bowl, drink
    for i, col in enumerate(((255, 214, 120), (255, 150, 110), (130, 200, 236))):
        tx0 = x - 28 * s + i * 20 * s
        rect(cv, tx0, y - 198 * s, tx0 + 17 * s, y - 176 * s, col, ink=None)
        cv.ellipse(tx0 + 8.5 * s, y - 187 * s, 5 * s, 3.4 * s, WHITE, ink=None)
    if ok > 0:
        cv.stroke([(x - 14 * s, y - 145 * s), (x - 4 * s, y - 133 * s), (x + 16 * s, y - 160 * s)], (110, 230, 140), 5 * s, alpha=int(255 * ok))
    else:
        for i in range(5):
            h = (4 + 12 * abs(math.sin(t * 7 + i * 1.3))) * listening * s
            rect(cv, x - 22 * s + i * 11 * s, y - 138 * s - h, x - 16 * s + i * 11 * s, y - 138 * s, CYAN, ink=None)
    cv.ellipse(x, y - 108 * s, 7 * s, 7 * s, (255, 90, 90) if listening > 0.1 else (120, 130, 150), ink=INK, lw=1.4)
    rect(cv, x - 24 * s, y - 80 * s, x + 24 * s, y - 60 * s, (60, 66, 84), lw=1.8)             # slot where the order comes out
    for dy in (40, 30):
        cv.stroke([(x - 26 * s, y - dy * s), (x + 26 * s, y - dy * s)], (200, 126, 70), 2.0)


def plate(cv, x, y, s=1.0, steam=0.0, t=0.0):
    cv.ellipse(x, y, 28 * s, 9 * s, WHITE, ink=INK, lw=2.0, shade_col=WHITE_SH)
    cv.fill(spline([(x - 16 * s, y - 2 * s), (x - 10 * s, y - 14 * s), (x + 10 * s, y - 14 * s), (x + 16 * s, y - 2 * s)], closed=True, n=3), (252, 250, 240), ink=INK, lw=1.6)
    cv.fill(spline([(x - 12 * s, y - 14 * s), (x, y - 20 * s), (x + 12 * s, y - 14 * s), (x, y - 10 * s)], closed=True, n=3), (236, 190, 120), ink=INK, lw=1.4)
    for k in range(3):
        if steam > 0:
            sx = x - 8 * s + k * 8 * s
            cv.stroke(spline([(sx, y - 24 * s), (sx + 3 * math.sin(t * 4 + k) * s, y - 34 * s), (sx - 2 * s, y - 46 * s)], n=3), (255, 255, 255), 2.4, alpha=int(180 * steam))


def robot_kitchen(cv, t=0.0, cook=0.0):
    """Counter, hanging lamps, a kitchen arm and a rail with plates; cook 0..1 sets how far the dish is."""
    rect(cv, 0, 0, W, 330, (246, 232, 214), ink=None)
    rect(cv, 0, 330, W, H, (230, 214, 190), ink=None)
    rect(cv, 40, 60, 1240, 70, (190, 198, 214), lw=2.0)
    for i in range(5):
        lx = 160 + i * 240
        cv.stroke([(lx, 70), (lx, 110)], (150, 160, 180), 3)
        cv.fill([(lx - 22, 134), (lx + 22, 134), (lx + 12, 110), (lx - 12, 110)], (252, 226, 150), ink=INK, lw=2.0)
    rect(cv, -10, 380, W + 10, 420, (206, 214, 226), lw=2.4)
    rect(cv, -10, 420, W + 10, 560, (170, 182, 204), lw=2.4, shade_col=(150, 164, 190))
    return 380


def supermarket(cv, t=0.0, gate_open=0.0):
    """Aisle shelves with colourful products, ceiling cameras, and an exit gate with a green light."""
    band(cv, 0, 330, (236, 244, 250), (214, 230, 242), n=8, x0=0, x1=W)
    rect(cv, 0, 330, W, H, (226, 232, 238), ink=None)
    for k in range(0, W, 120):
        cv.stroke([(k, 330), (k - 120 + 640 * 0, H)], (210, 218, 228), 1.2, alpha=80)
    cols = [(240, 120, 110), (250, 200, 90), (120, 190, 130), (110, 160, 220), (190, 140, 220), (240, 160, 100)]
    for sx, sw in ((40, 360), (440, 360)):
        rect(cv, sx, 170, sx + sw, 420, (236, 238, 244), lw=2.6, shade_col=(214, 218, 230))
        for r in range(3):
            ry = 200 + r * 70
            rect(cv, sx + 6, ry + 54, sx + sw - 6, ry + 62, (190, 196, 210), lw=1.6)
            for j in range(9):
                bw = 28 + (j * 7 + r * 3) % 9
                bx = sx + 14 + j * 38
                rect(cv, bx, ry + 54 - 40 - (j + r) % 3 * 4, bx + bw - 6, ry + 54, cols[(j + r * 2) % 6], lw=1.4)
    # ceiling cameras
    for cx in (200, 620, 1040):
        cv.stroke([(cx, 0), (cx, 50)], (150, 160, 180), 4)
        cv.ellipse(cx, 56, 18, 12, (70, 76, 96), ink=INK, lw=2.0)
        cv.ellipse(cx + 4, 58, 5, 5, (255, 80, 80) if int(t * 3) % 2 == 0 else (120, 40, 40), ink=None)
    # exit gate (right)
    rect(cv, 900, 250, 920, 520, (190, 198, 214), lw=2.4)
    rect(cv, 1160, 250, 1180, 520, (190, 198, 214), lw=2.4)
    rect(cv, 900, 232, 1180, 252, (190, 198, 214), lw=2.4)
    cv.ellipse(1040, 242, 14, 8, (110, 230, 140) if gate_open >= 0.5 else (230, 230, 120), ink=INK, lw=1.6)
    return 560


# ----------------------------------------------------------------------------------------------------------------- misc scenes
def room(cv, t=0.0, tod="morning"):
    """A small flat: wall, floor, a big window onto the future city, a ceiling speaker."""
    rect(cv, 0, 0, W, 470, (250, 238, 220), ink=None)
    rect(cv, 0, 470, W, H, (214, 188, 156), ink=None)
    rect(cv, 0, 466, W, 478, (190, 164, 134), ink=None)
    # window
    x0, y0, x1, y1 = 340, 70, 940, 380
    rect(cv, x0 - 10, y0 - 10, x1 + 10, y1 + 10, (250, 250, 252), lw=3.0)
    band(cv, y0, y1, (150, 208, 240), (255, 238, 204), n=12, x0=x0, x1=x1)
    cv.push(0, 0)
    skyline(cv, y1 - 6, 0, seed=7, tod=tod, layers=2)
    cv.pop()
    # re-cover the outside of the window
    rect(cv, -10, -10, x0 - 10, H, (250, 238, 220), ink=None)
    rect(cv, x1 + 10, -10, W + 10, H, (250, 238, 220), ink=None)
    rect(cv, x0 - 10, -10, x1 + 10, y0 - 10, (250, 238, 220), ink=None)
    rect(cv, x0 - 10, y1 + 10, x1 + 10, 470, (250, 238, 220), ink=None)
    rect(cv, -10, 0, W + 10, 0, (0, 0, 0), ink=None)
    drones(cv, t, n=2, y0=130)
    cv.stroke([(x0 - 10, y0 - 10), (x1 + 10, y0 - 10), (x1 + 10, y1 + 10), (x0 - 10, y1 + 10), (x0 - 10, y0 - 10)], INK, 3)
    cv.stroke([((x0 + x1) / 2, y0 - 10), ((x0 + x1) / 2, y1 + 10)], INK, 2)
    # ceiling speaker
    rrect(cv, 1040, 40, 1140, 84, 10, WHITE, lw=2.4, shade_col=WHITE_SH)
    for i in range(5):
        cv.stroke([(1056 + i * 18, 52), (1056 + i * 18, 72)], (150, 160, 180), 2)


def mat(cv, x, y, w=210, col=(120, 160, 210), sleeping=False):
    cv.fill([(x - w / 2, y), (x + w / 2, y), (x + w / 2 + 14, y + 26), (x - w / 2 - 14, y + 26)], col, ink=INK, lw=2.2, shade_col=mix(col, (0, 0, 0), 0.2))


def phone(cv, x, y, s=1.0, ring=0.0, t=0.0, angle=0.0):
    cv.push(x, y, rot=angle, scale=s)
    rrect(cv, -22, -40, 22, 40, 8, (50, 56, 76), lw=2.4)
    rect(cv, -17, -32, 17, 24, (70, 150, 200), ink=None)
    cv.ellipse(0, 32, 4, 4, (200, 206, 220), ink=None)
    cv.pop()
    if ring > 0:
        for k in range(3):
            cv.stroke(ellipse_pts(x + 26 * s, y - 36 * s, 10 + 10 * k, 10 + 10 * k, n=10, a0=-60, a1=40), (255, 200, 80), 3, alpha=int(255 * ring))


def call_center(cv, t=0.0, active=0.0):
    """Rows of dark racks with blinking lights and sound-wave bars on screens; one big headset-wearing bot in front."""
    band(cv, 0, 420, (44, 56, 90), (64, 78, 120), n=10, x0=0, x1=W)
    rect(cv, 0, 420, W, H, (36, 44, 72), ink=None)
    for r in range(2):
        for i in range(8):
            x0 = 40 + i * 152
            y0 = 90 + r * 160
            rrect(cv, x0, y0, x0 + 130, y0 + 130, 10, (60, 72, 108), lw=2.2)
            for k in range(4):
                lit = (math.sin(t * 3 + i * 1.7 + k * 2.3 + r) > 0)
                cv.ellipse(x0 + 20 + k * 30, y0 + 20, 5, 5, (120, 240, 160) if lit else (50, 90, 70), ink=None)
            rect(cv, x0 + 14, y0 + 40, x0 + 116, y0 + 112, (24, 30, 52), ink=None)
            for k in range(9):
                h = (6 + 26 * abs(math.sin(t * 6 + i + k * 0.9 + r * 2))) * (0.3 + 0.7 * active)
                rect(cv, x0 + 20 + k * 10, y0 + 76 - h / 2, x0 + 26 + k * 10, y0 + 76 + h / 2, CYAN, ink=None)
    # headsets on the racks
    for i in (1, 4, 6):
        x0 = 40 + i * 152 + 65
        cv.stroke(ellipse_pts(x0, 86, 22, 18, n=14, a0=180, a1=360), (210, 216, 230), 4)
        cv.ellipse(x0 - 22, 90, 5, 8, (210, 216, 230), ink=None)
        cv.ellipse(x0 + 22, 90, 5, 8, (210, 216, 230), ink=None)


def person_grid(cv, x0, y0, cols=10, rows=10, step=34, new=0, gone=0, t=0.0, reveal=1.0):
    """100 little people: the first `gone` are red (lost), the next `new` are green (added), the rest grey. Reveal 0..1 fills them in row by row."""
    total = cols * rows
    for i in range(total):
        if i / total > reveal:
            break
        r, c = divmod(i, cols)
        x, y = x0 + c * step, y0 + r * step
        if i < gone:
            col = (236, 96, 88)
        elif i >= total - new:
            col = (96, 196, 132)
        else:
            col = (176, 188, 208)
        cv.ellipse(x, y - 9, 7, 7, col, ink=INK, lw=1.2)
        cv.fill(spline([(x - 9, y + 11), (x - 7, y), (x + 7, y), (x + 9, y + 11)], closed=True, n=3), col, ink=INK, lw=1.2)


def bank(cv, t=0.0):
    """Old bank hall: counter with a glass window and a teller's seat, plain walls and a clock."""
    rect(cv, 0, 0, W, 470, (240, 230, 208), ink=None)
    rect(cv, 0, 470, W, H, (196, 176, 148), ink=None)
    cv.ellipse(300, 130, 36, 36, WHITE, ink=INK, lw=3.0)
    a = t * 0.3
    cv.stroke([(300, 130), (300 + math.cos(a) * 22, 130 + math.sin(a) * 22)], INK, 3)
    cv.stroke([(300, 130), (300, 106)], INK, 3)
    rect(cv, 520, 220, 1180, 450, (210, 196, 170), lw=2.6, shade_col=(190, 174, 146))
    rect(cv, 540, 240, 1160, 360, (184, 220, 238), lw=2.4)
    cv.stroke([(540, 300), (1160, 300)], (255, 255, 255), 2, alpha=140)
    for x in (680, 840, 1000):
        cv.stroke([(x, 240), (x, 360)], INK, 2)
    rect(cv, 500, 440, 1200, 470, (150, 120, 92), lw=2.4)


def atm(cv, x, y, s=1.0, t=0.0, use=0.0):
    cv.ellipse(x, y + 2, 50 * s, 8 * s, (0, 0, 0), alpha=40)
    rrect(cv, x - 46 * s, y - 190 * s, x + 46 * s, y, 8 * s, (92, 116, 160), lw=2.8, shade_col=(66, 88, 130))
    rrect(cv, x - 34 * s, y - 176 * s, x + 34 * s, y - 120 * s, 6 * s, (150, 230, 190), lw=2.0)
    rect(cv, x - 30 * s, y - 108 * s, x + 30 * s, y - 76 * s, (60, 66, 84), lw=1.8)
    for i in range(3):
        for j in range(3):
            cv.ellipse(x - 14 * s + i * 14 * s, y - 62 * s + j * 12 * s, 3.4 * s, 3.4 * s, (210, 214, 224), ink=None)
    rect(cv, x - 26 * s, y - 24 * s, x + 26 * s, y - 14 * s, (30, 34, 46), lw=1.6)
    if use > 0:
        k = use
        rect(cv, x - 22 * s, y - 24 * s - 18 * k * s, x + 22 * s, y - 14 * s, (120, 200, 120), lw=1.4) if k < 0.99 else None


def workshop(cv, t=0.0):
    """Chok's repair shop: pegboard of tools, a bench, a robot waiting for repair, bamboo kites hanging, a tea corner."""
    rect(cv, 0, 0, W, 470, (234, 214, 186), ink=None)
    rect(cv, 0, 470, W, H, (176, 140, 104), ink=None)
    rect(cv, 40, 60, 460, 330, (200, 164, 124), lw=2.6, shade_col=(176, 140, 104))
    for i, col in enumerate(((220, 90, 80), (240, 200, 80), (96, 150, 200), (120, 180, 120), (200, 110, 190))):
        x = 80 + i * 76
        cv.stroke([(x, 90), (x, 250)], (110, 110, 120), 7)
        cv.fill([(x - 12, 250), (x + 12, 250), (x + 8, 292), (x - 8, 292)], col, ink=INK, lw=1.6)
    rect(cv, 540, 360, 1240, 410, (150, 116, 84), lw=2.6, shade_col=(124, 94, 66))
    for lx in (580, 1180):
        rect(cv, lx, 410, lx + 22, 560, (124, 94, 66), lw=2.0)
    # kites hanging (bamboo + paper)
    for i, (kx, col) in enumerate(((620, (236, 100, 96)), (760, (250, 200, 90)), (900, (110, 170, 220)))):
        ky = 100 + 14 * math.sin(t * 1.4 + i)
        cv.stroke([(kx, 40), (kx, ky)], (120, 100, 80), 2)
        cv.fill([(kx, ky), (kx + 34, ky + 44), (kx, ky + 94), (kx - 34, ky + 44)], col, ink=INK, lw=2.0)
        cv.stroke([(kx, ky), (kx, ky + 94)], (186, 160, 100), 2.4)
        cv.stroke([(kx - 34, ky + 44), (kx + 34, ky + 44)], (186, 160, 100), 2.4)
    # tea corner
    rect(cv, 1020, 340, 1220, 360, (190, 150, 110), lw=2.2)
    cv.fill(spline([(1050, 340), (1046, 304), (1096, 304), (1092, 340)], closed=True, n=3), (236, 244, 248), ink=INK, lw=2.0)
    for k in range(3):
        cv.stroke(spline([(1062 + k * 10, 298), (1066 + k * 10 + 3 * math.sin(t * 3 + k), 286), (1060 + k * 10, 272)], n=3), (255, 255, 255), 2.2, alpha=150)
    cv.fill(spline([(1130, 340), (1128, 316), (1160, 316), (1158, 340)], closed=True, n=3), (236, 244, 248), ink=INK, lw=1.8)


def rooftop(cv, t=0.0, tod="dusk"):
    band(cv, 0, 360, (82, 92, 156), (252, 176, 134), n=22, x0=0, x1=W)
    moon(cv, 1090, 110, 30, 0.5)
    skyline(cv, 360, 0, seed=9, tod="dusk")
    drones(cv, t, n=3, y0=150, x_speed=30)
    rect(cv, -10, 360, W + 10, H + 10, (176, 170, 190), ink=None)
    rect(cv, -10, 360, W + 10, 376, (150, 146, 168), lw=2.0)
    # string lights
    for i in range(13):
        x = 40 + i * 100
        y = 90 + 24 * math.sin(math.pi * (i % 13) / 12)
        cv.ellipse(x, y + 40 * (0.2 + 0.8 * abs(math.sin(i * 0.5))) * 0 + 100, 6, 6, (255, 226, 140), ink=None)


# ----------------------------------------------------------------------------------------------------------------- icons and graphics
def dashed(cv, pts, col=(255, 255, 255), lw=3.0, dash=14, gap=9, alpha=255):
    """Dashed polyline whose dashes march along the path (so a dashed frame is never a frozen shape)."""
    period = dash + gap
    run = -((PH[0] * 26) % period)
    for a, b in zip(pts, pts[1:]):
        L = math.hypot(b[0] - a[0], b[1] - a[1]) or 1
        s = run
        while s < L:
            s0, s1 = max(0.0, s), min(L, s + dash)
            if s1 > s0:
                cv.stroke([(a[0] + (b[0] - a[0]) * s0 / L, a[1] + (b[1] - a[1]) * s0 / L), (a[0] + (b[0] - a[0]) * s1 / L, a[1] + (b[1] - a[1]) * s1 / L)], col, lw,
                          alpha=alpha)
            s += period
        run = s - L


def dashed_rect(cv, x0, y0, x1, y1, col=(255, 255, 255), lw=3.0, alpha=255):
    dashed(cv, [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)], col, lw, alpha=alpha)


def crystal_ball(cv, x, y, s=1.0, t=0.0):
    rrect(cv, x - 34 * s, y + 26 * s, x + 34 * s, y + 46 * s, 8 * s, (120, 84, 150), lw=2.2)
    cv.ellipse(x, y, 38 * s, 38 * s, (206, 190, 250), ink=INK, lw=2.6, shade_col=(160, 140, 220))
    for k in range(3):
        a = t * 1.2 + k * 2.1
        cv.ellipse(x + math.cos(a) * 14 * s, y + math.sin(a * 1.3) * 12 * s, 4 * s, 4 * s, (255, 255, 255), ink=None, alpha=200)
    cv.ellipse(x - 14 * s, y - 16 * s, 8 * s, 5 * s, (255, 255, 255), ink=None, alpha=170)


def arrow(cv, x, y, length=60, up=True, col=(96, 196, 132), w=16, alpha=255):
    d = -1 if up else 1
    cv.fill([(x - w / 2, y), (x - w / 2, y + d * length * 0.55), (x - w, y + d * length * 0.55), (x, y + d * length), (x + w, y + d * length * 0.55),
             (x + w / 2, y + d * length * 0.55), (x + w / 2, y)], col, ink=INK, lw=2.0, alpha=alpha)


def coin(cv, x, y, r=14, col=(255, 210, 80)):
    cv.ellipse(x, y, r, r, col, ink=INK, lw=2.0, shade_col=mix(col, (0, 0, 0), 0.18))
    cv.ellipse(x, y, r * 0.55, r * 0.55, mix(col, (255, 255, 255), 0.35), ink=None)


def wrench(cv, x, y, s=1.0, ang=-40, col=(196, 204, 218)):
    cv.push(x, y, rot=ang, scale=s)
    cv.stroke([(0, 24), (0, -18)], INK, 12)
    cv.stroke([(0, 24), (0, -18)], col, 8)
    cv.ellipse(0, -24, 13, 13, col, ink=INK, lw=2.2)
    cv.fill([(-5, -38), (5, -38), (4, -24), (-4, -24)], (250, 250, 250), ink=None)
    cv.pop()


def lens_icon(cv, x, y, s=1.0):
    cv.ellipse(x, y, 26 * s, 26 * s, (214, 240, 252), ink=INK, lw=3.0, alpha=255)
    cv.ellipse(x, y, 26 * s, 26 * s, (150, 200, 232), ink=None, alpha=70)
    cv.stroke([(x + 18 * s, y + 18 * s), (x + 40 * s, y + 40 * s)], INK, 9 * s)
    cv.stroke([(x + 18 * s, y + 18 * s), (x + 40 * s, y + 40 * s)], (200, 150, 90), 5 * s)


def bulb(cv, x, y, s=1.0, on=1.0):
    cv.ellipse(x, y, 22 * s, 24 * s, (255, 232, 120) if on > 0.5 else (230, 230, 230), ink=INK, lw=2.6)
    rect(cv, x - 10 * s, y + 20 * s, x + 10 * s, y + 34 * s, (170, 176, 190), lw=2.0)
    if on > 0.5:
        for k in range(7):
            a = -math.pi + k * math.pi / 6
            cv.stroke([(x + math.cos(a) * 30 * s, y + math.sin(a) * 32 * s), (x + math.cos(a) * 42 * s, y + math.sin(a) * 44 * s)], (255, 214, 80), 3)


def kite(cv, x, y, s=1.0, ang=0.0, col=(236, 100, 96), tail=True, t=0.0):
    cv.push(x, y, rot=ang, scale=s)
    cv.fill([(0, -50), (34, 0), (0, 60), (-34, 0)], col, ink=INK, lw=2.4, shade_col=mix(col, (0, 0, 0), 0.18))
    cv.stroke([(0, -50), (0, 60)], (186, 160, 100), 2.6)
    cv.stroke([(-34, 0), (34, 0)], (186, 160, 100), 2.6)
    if tail:
        pts = [(0, 60)] + [(6 * math.sin(t * 4 + i * 0.9), 60 + 14 * (i + 1)) for i in range(6)]
        cv.stroke(spline(pts, n=4), (250, 200, 90), 3)
    cv.pop()


def teapot_cup(cv, x, y, s=1.0, steam=1.0, t=0.0):
    cv.fill(spline([(x - 18 * s, y), (x - 20 * s, y - 24 * s), (x + 20 * s, y - 24 * s), (x + 18 * s, y)], closed=True, n=3), (236, 244, 248), ink=INK, lw=2.0,
            shade_col=(206, 220, 230))
    for k in range(3):
        cv.stroke(spline([(x - 8 * s + k * 8 * s, y - 28 * s), (x - 5 * s + k * 8 * s + 3 * math.sin(t * 3 + k), y - 40 * s), (x - 9 * s + k * 8 * s, y - 52 * s)], n=3),
                  (255, 255, 255), 2.2, alpha=int(170 * steam))


def bank_building(cv, x, y, s=1.0, col=(214, 196, 160), pop=1.0):
    k = ease(pop)
    cv.push(x, y, scale=s * (0.2 + 0.8 * k))
    cv.fill([(-40, 0), (-40, -52), (0, -76), (40, -52), (40, 0)], col, ink=INK, lw=2.4, shade_col=mix(col, (0, 0, 0), 0.18))
    for dx in (-26, -9, 9, 26):
        rect(cv, dx - 4, -46, dx + 4, -6, (250, 244, 228), lw=1.6)
    coin(cv, 0, -52, 9)
    cv.pop()


def bubble(cv, x, y, w, h, tail=(0, 40), col=(255, 255, 255), alpha=255):
    rrect(cv, x - w / 2, y - h / 2, x + w / 2, y + h / 2, h * 0.35, col, lw=2.6, alpha=alpha)
    cv.fill([(x - 14 + tail[0] * 0.2, y + h / 2 - 3), (x + 10 + tail[0] * 0.2, y + h / 2 - 3), (x + tail[0], y + h / 2 + tail[1])], col, ink=INK, lw=2.4, alpha=alpha)
    rect(cv, x - 13 + tail[0] * 0.2, y + h / 2 - 5, x + 9 + tail[0] * 0.2, y + h / 2 + 1, col, ink=None)


def bars_in_bubble(cv, x, y, t, seed=0, n=7, col=(90, 120, 190), amp=1.0):
    for i in range(n):
        h = (4 + 22 * abs(math.sin(t * 6 + i * 1.1 + seed))) * amp
        rect(cv, x - n * 5 + i * 10, y - h / 2, x - n * 5 + i * 10 + 6, y + h / 2, col, ink=None)


def check_mark(cv, x, y, s=1.0, col=(96, 210, 130), lw=6, a=1.0):
    cv.stroke([(x - 14 * s, y), (x - 4 * s, y + 12 * s), (x + 16 * s, y - 14 * s)], col, lw * s, alpha=int(255 * a))


def cross_mark(cv, x, y, s=1.0, col=(236, 84, 80), lw=6, a=1.0):
    cv.stroke([(x - 13 * s, y - 13 * s), (x + 13 * s, y + 13 * s)], col, lw * s, alpha=int(255 * a))
    cv.stroke([(x - 13 * s, y + 13 * s), (x + 13 * s, y - 13 * s)], col, lw * s, alpha=int(255 * a))


def laptop(cv, x, y, s=1.0, t=0.0, screen=(70, 150, 200)):
    cv.fill([(x - 50 * s, y), (x + 50 * s, y), (x + 62 * s, y + 12 * s), (x - 62 * s, y + 12 * s)], (186, 194, 210), ink=INK, lw=2.2)
    rrect(cv, x - 46 * s, y - 70 * s, x + 46 * s, y, 5 * s, (60, 66, 84), lw=2.4)
    rect(cv, x - 40 * s, y - 64 * s, x + 40 * s, y - 6 * s, screen, ink=None)


def ambient(cv, t, n=30, col=(150, 190, 255), seed=1, y0=0, y1=None, speed=26):
    """Soft particles drifting upward over a dark panel: something is always moving."""
    y1 = H if y1 is None else y1
    for i in range(n):
        ph = (i * 0.6180339 + seed * 0.37) % 1.0
        x = (ph * W + 40 * math.sin(t * 0.7 + i)) % W
        y = y1 - ((ph * 977 + t * speed * (0.5 + (i % 5) * 0.25)) % (y1 - y0))
        r = 2 + (i % 4)
        cv.ellipse(x, y, r, r, col, ink=None, alpha=int(70 + 50 * math.sin(t * 2 + i)))
