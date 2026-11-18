"""More backgrounds for the red-thread story (v2): courtyard with the snack table, restroom, dorm street at night, cafe, graduation lawn, a day/night split for the dating-app couple."""
from __future__ import annotations

import math

from props_uni import INK, W, H, band, cloud, mix, rect, rrect, spline
from rt_art import snack


def courtyard(cv, t=0.0):
    band(cv, 0, 400, (176, 224, 250), (236, 244, 238), n=10, x0=0, x1=W)
    cloud(cv, 220, 120, 1.0, (255, 255, 255))
    cloud(cv, 980, 90, 1.3, (255, 255, 255))
    rect(cv, 60, 140, 1220, 400, (232, 226, 216), lw=3.0)
    for r in range(2):
        for c in range(11):
            rect(cv, 100 + c * 102, 170 + r * 100, 170 + c * 102, 240 + r * 100, (172, 212, 238), lw=2.0)
    rect(cv, 0, 400, W, H, (150, 196, 128), ink=None)
    rect(cv, 0, 520, W, H, (204, 196, 182), ink=None)
    # a long snack table behind the students, loaded with colourful pouches
    rect(cv, 150, 430, 1130, 462, (196, 150, 108), lw=2.8, shade_col=(164, 120, 84))
    rect(cv, 170, 462, 190, 520, (150, 108, 76), lw=2.0)
    rect(cv, 1090, 462, 1110, 520, (150, 108, 76), lw=2.0)
    cols = [(240, 110, 90), (110, 170, 240), (250, 200, 80), (120, 200, 130), (200, 130, 220), (250, 150, 180)]
    for i in range(14):
        snack(cv, 200 + i * 66, 404 + 3 * math.sin(i), 0.66, cols[i % 6], rot=(i % 3 - 1) * 8)


def restroom(cv, t=0.0, door_open=0.0):
    rect(cv, 0, 0, W, H, (222, 238, 240), ink=None)
    for x in range(0, W, 80):
        cv.stroke([(x, 0), (x, 470)], (200, 220, 226), 1.6)
    for y in range(0, 470, 80):
        cv.stroke([(0, y), (W, y)], (200, 220, 226), 1.6)
    rect(cv, 0, 470, W, H, (176, 196, 204), ink=None)
    # a mirror and a sink on the right, two stall doors on the left
    rrect(cv, 800, 120, 1100, 340, 12, (226, 240, 252), lw=3.0)
    cv.stroke([(830, 300), (900, 150)], (255, 255, 255), 8, alpha=130)
    rrect(cv, 780, 380, 1120, 430, 14, (250, 250, 252), lw=3.0)
    cv.stroke([(950, 380), (950, 340), (990, 340)], (170, 176, 186), 6)
    for i in range(2):
        x0 = 110 + i * 250
        rect(cv, x0, 160, x0 + 220, 560, (120, 170, 204), lw=3.0)
        rect(cv, x0 + 10, 180, x0 + 210, 540, (150, 192, 220), ink=None)
        cv.ellipse(x0 + 190, 360, 6, 6, (230, 230, 240), ink=INK, lw=1.2)
    if door_open > 0:
        rect(cv, 1160, 140, 1280, 520, (176, 130, 96), lw=3.0)


def dorm_night(cv, t=0.0):
    band(cv, 0, 480, (22, 28, 70), (86, 76, 130), n=18, x0=0, x1=W)
    for i in range(50):
        x, y = (i * 211) % W, (i * 97) % 300
        cv.ellipse(x, y, 1.8, 1.8, (255, 255, 235), ink=None, alpha=int(110 + 100 * math.sin(t * 2 + i)))
    cv.ellipse(1040, 130, 52, 52, (252, 246, 214), ink=None)
    rect(cv, -10, 190, 520, 480, (70, 82, 128), lw=3.0)
    for r in range(4):
        for c in range(6):
            lit = (r * 5 + c * 3) % 4 < 2
            rect(cv, 20 + c * 80, 220 + r * 62, 70 + c * 80, 262 + r * 62, (255, 226, 150) if lit else (50, 60, 100), ink=None)
    rect(cv, 760, 250, 1300, 480, (64, 76, 120), lw=3.0)
    for r in range(3):
        for c in range(7):
            lit = (r * 3 + c * 5) % 4 < 2
            rect(cv, 780 + c * 74, 276 + r * 62, 826 + c * 74, 316 + r * 62, (255, 226, 150) if lit else (50, 60, 100), ink=None)
    rect(cv, -10, 480, W + 10, H, (96, 98, 126), ink=None)
    rect(cv, -10, 480, W + 10, 520, (118, 120, 148), ink=None)
    for lx in (640, 1220):
        cv.stroke([(lx, 480), (lx, 240)], (110, 114, 140), 6)
        cv.ellipse(lx, 232, 22, 22, (255, 236, 160), ink=INK, lw=2.4)
        cv.ellipse(lx, 232, 56, 56, (255, 236, 160), ink=None, alpha=44)


def cafe(cv, t=0.0):
    band(cv, 0, 430, (252, 236, 214), (242, 220, 190), n=8, x0=0, x1=W)
    rect(cv, 0, 430, W, H, (186, 148, 110), ink=None)
    rect(cv, 150, 90, 520, 300, (198, 232, 248), lw=3.0)
    cv.stroke([(335, 90), (335, 300)], (252, 252, 254), 3)
    for lx in (700, 940):
        cv.stroke([(lx, 0), (lx, 80)], (120, 90, 70), 3)
        cv.fill([(lx - 34, 130), (lx + 34, 130), (lx + 20, 80), (lx - 20, 80)], (252, 214, 140), ink=INK, lw=2.4)
    rrect(cv, 780, 120, 1160, 300, 10, (250, 244, 232), lw=2.8)            # a menu board with a few coloured bars
    for i in range(4):
        rect(cv, 810, 150 + i * 34, 810 + 140 + (i * 53) % 120, 162 + i * 34, [(240, 140, 120), (140, 190, 230), (250, 210, 100), (150, 210, 150)][i], ink=None)


def lawn(cv, t=0.0, deco=True):
    """Campus lawn: faculty building; with deco=True (graduation) also a flower arch and balloons."""
    band(cv, 0, 420, (150, 210, 250), (236, 246, 240), n=10, x0=0, x1=W)
    cloud(cv, 240, 110, 1.2, (255, 255, 255))
    cloud(cv, 1000, 150, 1.0, (255, 255, 255))
    rect(cv, 60, 130, 1220, 420, (232, 226, 216), lw=3.0)
    for r in range(2):
        for c in range(11):
            rect(cv, 100 + c * 102, 160 + r * 110, 170 + c * 102, 236 + r * 110, (172, 212, 238), lw=2.0)
    rect(cv, 0, 420, W, H, (130, 190, 120), ink=None)
    if not deco:
        return
    # arch of flowers
    cv.stroke(spline([(300, 560), (300, 330), (640, 250), (980, 330), (980, 560)], n=4), (88, 160, 96), 22)
    for i in range(16):
        u = i / 15
        x = 300 + u * 680
        y = 330 - 90 * math.sin(math.pi * u) + (60 if u < 0.06 or u > 0.94 else 0)
        cv.ellipse(x, y + 10, 10, 10, [(250, 120, 150), (255, 210, 100), (255, 255, 255), (190, 140, 230)][i % 4], ink=INK, lw=1.4)
    # balloons
    for i, (bx, by, col) in enumerate(((140, 330, (250, 110, 130)), (190, 300, (250, 210, 90)), (1110, 320, (120, 180, 240)), (1160, 290, (170, 220, 140)))):
        sway = 6 * math.sin(t * 1.4 + i)
        cv.stroke([(bx, by + 30), (bx + sway, 560)], (140, 140, 150), 1.6)
        cv.ellipse(bx + sway * 0.4, by, 26, 32, col, ink=INK, lw=2.2)
        cv.ellipse(bx - 8 + sway * 0.4, by - 10, 6, 9, (255, 255, 255), ink=None, alpha=150)


def split_world(cv, t=0.0):
    """Left: Thailand at night. Right: America in the morning. One chat bridges them."""
    for x0, x1, top, bot in ((0, 640, (22, 28, 74), (78, 70, 130)), (640, W, (150, 208, 248), (252, 238, 214))):
        band(cv, 0, H, top, bot, n=14, x0=x0, x1=x1)
    for i in range(30):
        x, y = (i * 173) % 620, (i * 89) % 320
        cv.ellipse(x, y, 1.7, 1.7, (255, 255, 235), ink=None, alpha=int(120 + 100 * math.sin(t * 2 + i)))
    cv.ellipse(540, 120, 46, 46, (252, 246, 214), ink=None)
    cv.ellipse(1060, 120, 54, 54, (255, 238, 150), ink=None)
    cloud(cv, 860, 200, 1.1, (255, 255, 255))
    rect(cv, 0, 560, 640, H, (54, 60, 96), ink=None)
    rect(cv, 640, 560, W, H, (170, 200, 140), ink=None)
    for i, (x, h) in enumerate(((40, 220), (150, 300), (270, 180), (380, 260), (480, 200), (580, 280))):
        rect(cv, x, 560 - h, x + 90, 560, (56, 66, 110), lw=2.4)
        for r in range(int(h / 50)):
            for c in range(2):
                lit = (i + r + c) % 3 != 0
                rect(cv, x + 12 + c * 40, 560 - h + 14 + r * 46, x + 40 + c * 40, 560 - h + 38 + r * 46, (255, 226, 150) if lit else (40, 50, 90), ink=None)
    for i, (x, h) in enumerate(((700, 200), (820, 150), (940, 230), (1080, 170), (1180, 210))):
        rect(cv, x, 560 - h, x + 100, 560, (232, 168, 140), lw=2.4)
        for r in range(int(h / 50)):
            rect(cv, x + 14, 560 - h + 14 + r * 46, x + 86, 560 - h + 36 + r * 46, (190, 224, 244), ink=None)
    cv.stroke([(640, 0), (640, H)], (255, 255, 255), 3, alpha=100)


def stall(cv, t=0.0):
    """A little market stall on the campus lawn: a striped awning and a table with rows of hairpins (little gold pins with pink flowers)."""
    lawn(cv, t, deco=False)
    rect(cv, 760, 470, 1240, 504, (186, 142, 100), lw=2.8, shade_col=(154, 112, 78))
    rect(cv, 780, 504, 800, 690, (150, 108, 76), lw=2.0)
    rect(cv, 1200, 504, 1220, 690, (150, 108, 76), lw=2.0)
    for i in range(8):                                                           # the awning: stripes
        x0 = 740 + i * 66
        cv.fill([(x0, 250), (x0 + 66, 250), (x0 + 74, 330), (x0 - 8, 330)], (250, 120, 130) if i % 2 == 0 else (255, 250, 244), ink=INK, lw=2.0)
    cv.stroke([(780, 330), (780, 470)], (140, 100, 70), 5)
    cv.stroke([(1210, 330), (1210, 470)], (140, 100, 70), 5)
    for i in range(7):                                                           # hairpins lying on the table
        x = 800 + i * 62
        cv.stroke([(x, 482), (x + 44, 496)], INK, 6)
        cv.stroke([(x, 482), (x + 44, 496)], (240, 200, 90), 3.4)
        for k in range(5):
            a = k * 1.2566
            cv.ellipse(x - 2 + math.cos(a) * 6, 482 + math.sin(a) * 6, 4.6, 4.6, [(250, 130, 160), (170, 130, 230), (120, 190, 240)][i % 3], ink=INK, lw=1.2)


def tea_garden(cv, t=0.0):
    """A pretty evening tea pavilion: peach sky, a blossoming branch with falling petals, glowing paper lanterns, a wooden terrace with a rail, soft bokeh."""
    band(cv, 0, 470, (255, 226, 196), (250, 190, 170), n=14, x0=0, x1=W)
    cv.ellipse(980, 190, 70, 70, (255, 244, 214), ink=None)
    cv.ellipse(980, 190, 110, 110, (255, 236, 200), ink=None, alpha=60)
    # far hills
    cv.fill([(0, 470), (0, 360), (180, 320), (380, 380), (560, 340), (760, 400), (980, 330), (1160, 390), (1280, 350), (1280, 470)], (222, 168, 160), ink=None)
    cv.fill([(0, 470), (0, 410), (240, 380), (460, 430), (700, 392), (940, 440), (1280, 400), (1280, 470)], (200, 146, 148), ink=None)
    # a blossoming branch from the top-left
    cv.stroke(spline([(-20, 60), (160, 90), (320, 170), (470, 190)], n=4), (110, 78, 70), 12)
    cv.stroke(spline([(150, 90), (200, 40), (280, 20)], n=3), (110, 78, 70), 7)
    cv.stroke(spline([(310, 165), (350, 230), (420, 262)], n=3), (110, 78, 70), 6)
    for i in range(46):
        x = 40 + (i * 53) % 440
        y = 60 + ((i * 37) % 150) + (x * 0.18)
        r = 8 + (i % 4) * 2
        cv.ellipse(x, y, r, r, (255, 190, 208) if i % 3 else (255, 220, 230), ink=None, alpha=235)
    for j in range(16):                                                           # falling petals
        u = (t * 0.07 + j * 0.0625) % 1.0
        px = 120 + (j * 83) % 560 + 40 * math.sin(t * 0.9 + j)
        py = 140 + 560 * u
        cv.ellipse(px, py, 5.5, 3.2, (255, 196, 214), ink=None, alpha=int(235 * math.sin(math.pi * min(1.0, u * 1.3))), rot=40 * math.sin(t + j) + 30)
    # terrace floor and rail
    rect(cv, 0, 470, W, H, (196, 150, 110), ink=None)
    for x in range(0, W, 140):
        cv.stroke([(x, 470), (x - 60 + (x - 640) * 0.12, H)], (166, 120, 86), 2.0, alpha=140)
    rect(cv, 0, 440, W, 456, (138, 96, 70), lw=2.4)
    for x in range(30, W, 120):
        rect(cv, x, 456, x + 14, 520, (150, 106, 78), lw=1.8)
    # paper lanterns on strings with a warm glow
    for i, lx in enumerate((560, 760, 960, 1160)):
        sw = 6 * math.sin(t * 1.3 + i)
        cv.stroke([(lx, 0), (lx + sw * 0.4, 96)], (120, 90, 70), 2.6)
        cv.ellipse(lx + sw, 140, 74, 74, (255, 214, 140), ink=None, alpha=38)
        cv.ellipse(lx + sw, 142, 30, 40, (250, 120, 110) if i % 2 else (255, 190, 90), ink=INK, lw=2.4)
        cv.stroke([(lx + sw - 22, 130), (lx + sw + 22, 130)], (255, 236, 190), 2.0, alpha=150)
        cv.stroke([(lx + sw - 26, 148), (lx + sw + 26, 148)], (255, 236, 190), 2.0, alpha=150)
    for i in range(14):                                                           # soft bokeh lights
        cv.ellipse((i * 211) % W, 520 + (i * 61) % 180, 18 + (i % 3) * 8, 18 + (i % 3) * 8, (255, 236, 190), ink=None, alpha=26)


def tea_table(cv, x0=400, x1=900, y=600):
    """A low wooden table in front of the couple (drawn over their legs)."""
    rect(cv, x0, y, x1, y + 30, (170, 116, 84), lw=2.8, shade_col=(140, 96, 70))
    cv.fill([(x0 + 40, y + 30), (x0 + 60, y + 30), (x0 + 54, y + 112), (x0 + 34, y + 112)], (140, 96, 70), ink=INK, lw=2.0)
    cv.fill([(x1 - 60, y + 30), (x1 - 40, y + 30), (x1 - 34, y + 112), (x1 - 54, y + 112)], (140, 96, 70), ink=INK, lw=2.0)
