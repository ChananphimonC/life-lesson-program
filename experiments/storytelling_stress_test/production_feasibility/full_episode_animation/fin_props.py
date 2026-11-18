"""Props and backgrounds for money / AI / daily-life stories (procedural, soft cartoon style). Everything is looked up by NAME from the story JSON (story_engine.REG_PROP / REG_BG),
so a new episode needs no new code: bedroom, grill restaurant, conference hall, home desk, mall, coworking, calc board, dream sky + coins, bills, piggy bank, phone with an app screen,
cards, charts, bags, drinks, calculator, laptop, robot helper, flags, magnifier, shield ..."""
from __future__ import annotations

import math

import engine  # noqa: F401
from props_future import *  # noqa: F401,F403  (rect, rrect, band, coin, bubble, check_mark, arrow, phone ...)
from props_uni import cloud  # noqa: E402
from toon import INK, mix, spline

W, H = 1280, 720
GREEN = (84, 190, 120)
RED_C = (232, 76, 76)
GOLD = (255, 205, 70)


# ----------------------------------------------------------------------------------------------------------------- backgrounds
def bg_bedroom(cv, t=0.0, night=1.0, **kw):
    top = mix((255, 236, 210), (30, 34, 78), night)
    bot = mix((246, 224, 196), (54, 58, 108), night)
    band(cv, 0, 470, top, bot, n=8, x0=0, x1=W)
    rect(cv, 0, 470, W, H, mix((206, 170, 130), (92, 80, 96), night), ink=None)
    rect(cv, 760, 70, 1180, 360, mix((200, 236, 252), (22, 30, 70), night), lw=3.0)               # window with the city
    for i in range(14):
        x = 780 + (i * 61) % 380
        h = 60 + (i * 37) % 120
        rect(cv, x, 360 - h, x + 38, 360, mix((120, 150, 190), (36, 44, 96), night), ink=None)
        for r in range(int(h / 24)):
            if night > 0.3 and (i + r) % 3:
                rect(cv, x + 8, 360 - h + 6 + r * 24, x + 18, 360 - h + 14 + r * 24, (255, 226, 150), ink=None)
    cv.stroke([(970, 70), (970, 360)], (250, 250, 252), 4)
    cv.ellipse(1120, 130, 22, 22, mix((255, 244, 200), (250, 250, 235), night), ink=None, alpha=255 if night > 0.2 else 0)
    rrect(cv, 60, 330, 640, 560, 18, mix((236, 150, 150), (120, 80, 110), night), lw=3.0)                  # bed
    rrect(cv, 60, 300, 640, 360, 18, mix((250, 240, 232), (160, 150, 180), night), lw=3.0)
    rrect(cv, 90, 296, 250, 350, 16, mix((255, 255, 255), (190, 190, 220), night), lw=2.6)                # pillow
    rect(cv, 20, 560, 120, 600, (150, 106, 74), lw=2.4)
    rect(cv, 30, 600, 50, 700, (150, 106, 74), lw=2.4)


def bg_grill(cv, t=0.0, **kw):
    band(cv, 0, 520, (255, 214, 160), (236, 150, 110), n=8, x0=0, x1=W)
    rect(cv, 0, 520, W, H, (150, 100, 76), ink=None)
    for i, x in enumerate((140, 400, 660, 920, 1180)):                                                    # paper lanterns
        cv.stroke([(x, 0), (x, 70)], (110, 80, 60), 2.4)
        cv.ellipse(x, 110, 40, 50, (232, 70, 60) if i % 2 else (255, 190, 80), ink=INK, lw=2.4)
        cv.ellipse(x, 110, 90, 90, (255, 214, 130), ink=None, alpha=34)
    for i in range(8):                                                                                      # stacked plates on a shelf
        rect(cv, 60 + i * 150, 330, 190 + i * 150, 342, (130, 90, 66), lw=2.0)
    rect(cv, 160, 430, 1120, 470, (120, 80, 60), lw=3.0)                                                   # table
    cv.ellipse(640, 440, 170, 40, (70, 70, 80), ink=INK, lw=3.0)                                           # round grill pan
    cv.ellipse(640, 436, 140, 26, (230, 120, 60), ink=None)
    for q in range(5):
        u = (t * 0.5 + q / 5) % 1.0
        cv.ellipse(600 + 20 * q + 8 * math.sin(u * 6 + q), 400 - 130 * u, 20 + 14 * u, 14 + 10 * u, (250, 250, 252), ink=None, alpha=int(150 * (1 - u)))


def bg_conference(cv, t=0.0, **kw):
    band(cv, 0, 500, (60, 40, 90), (110, 70, 130), n=8, x0=0, x1=W)
    rect(cv, 0, 500, W, H, (86, 50, 70), ink=None)
    rrect(cv, 250, 70, 1030, 380, 14, (26, 28, 56), lw=3.4)                                               # huge screen
    rect(cv, 270, 90, 1010, 360, (40, 46, 96), ink=None)
    for i in range(4):                                                                                      # spotlights
        x = 300 + i * 250
        cv.fill([(x - 12, 0), (x + 12, 0), (x + 140, 520), (x - 140, 520)], (255, 240, 190), ink=None, alpha=24)
    for r in range(3):                                                                                      # rows of chairs
        for c in range(9):
            x = 90 + c * 130 + r * 30
            y = 560 + r * 56
            rrect(cv, x, y, x + 70, y + 40, 8, (120, 60, 70), lw=2.0)
    rect(cv, 0, 470, W, 490, (60, 32, 50), lw=2.0)


def bg_desk(cv, t=0.0, dusk=0.0, **kw):
    band(cv, 0, 470, mix((250, 238, 216), (252, 190, 140), dusk), mix((244, 226, 196), (140, 120, 170), dusk), n=8, x0=0, x1=W)
    rect(cv, 0, 470, W, H, (196, 160, 120), ink=None)
    rect(cv, 80, 70, 460, 330, mix((200, 236, 252), (250, 170, 120), dusk), lw=3.0)
    cv.stroke([(270, 70), (270, 330)], (250, 250, 252), 4)
    for i in range(7):
        x = 100 + i * 50
        rect(cv, x, 330 - 40 - (i * 29) % 80, x + 34, 330, mix((120, 150, 190), (100, 80, 130), dusk), ink=None)
    for i in range(3):                                                                                      # shelf with a plant and books
        rect(cv, 760, 150 + i * 120, 1200, 164 + i * 120, (150, 106, 74), lw=2.4)
    for i in range(6):
        rect(cv, 780 + i * 30, 90, 806 + i * 30, 150, [(232, 100, 100), (100, 160, 220), (250, 200, 90), (120, 200, 140)][i % 4], lw=1.8)
    cv.ellipse(1120, 118, 30, 24, (120, 196, 130), ink=INK, lw=2.2)
    cv.fill([(1100, 140), (1140, 140), (1134, 150), (1106, 150)], (200, 120, 90), ink=INK, lw=1.8)
    rect(cv, 160, 560, 1120, 590, (160, 110, 76), lw=3.0)
    rect(cv, 200, 590, 230, 710, (140, 96, 66), lw=2.4)
    rect(cv, 1050, 590, 1080, 710, (140, 96, 66), lw=2.4)


def bg_mall(cv, t=0.0, **kw):
    band(cv, 0, 420, (255, 244, 236), (255, 220, 214), n=6, x0=0, x1=W)
    rect(cv, 0, 470, W, H, (232, 214, 204), ink=None)
    for i, (x, col) in enumerate(((20, (250, 120, 140)), (330, (120, 190, 240)), (640, (250, 200, 90)), (950, (150, 210, 150)))):
        rect(cv, x, 120, x + 290, 470, mix(col, (255, 255, 255), 0.6), lw=3.0)
        rect(cv, x + 20, 150, x + 270, 220, col, lw=2.4)
        for k in range(4):
            rrect(cv, x + 32 + k * 58, 240, x + 74 + k * 58, 380, 6, [(250, 90, 100), (90, 150, 230), (250, 200, 80), (130, 200, 130)][(k + i) % 4], lw=2.0)
        cv.fill([(x + 40, 130), (x + 90, 130), (x + 66, 168)], (255, 255, 255), ink=INK, lw=1.8)             # red sale tag
        cv.ellipse(x + 245, 185, 22, 22, (232, 60, 70), ink=INK, lw=2.2)
    for i in range(10):
        cv.ellipse((i * 137) % W, 560 + (i * 61) % 120, 24, 24, (255, 255, 255), ink=None, alpha=24)


def bg_cowork(cv, t=0.0, **kw):
    band(cv, 0, 470, (236, 244, 250), (216, 232, 242), n=6, x0=0, x1=W)
    rect(cv, 0, 470, W, H, (190, 176, 160), ink=None)
    rect(cv, 60, 90, 560, 380, (200, 232, 250), lw=3.0)
    for i in range(10):
        x = 80 + i * 46
        rect(cv, x, 380 - 70 - (i * 41) % 120, x + 34, 380, (140, 170, 210), ink=None)
    for k, x in enumerate((700, 900, 1100)):
        rect(cv, x, 330, x + 160, 350, (176, 130, 96), lw=2.4)
        rect(cv, x + 70, 350, x + 90, 470, (150, 106, 74), lw=2.0)
        rrect(cv, x + 30, 250, x + 130, 330, 6, (60, 70, 100), lw=2.6)
        cv.ellipse(x + 80, 290, 6, 6, (120, 230, 150), ink=None)
    cv.ellipse(1220, 400, 40, 50, (120, 200, 130), ink=INK, lw=2.4)


def bg_calc(cv, t=0.0, **kw):
    """A dark-blue grid board for the math scenes."""
    band(cv, 0, H, (26, 40, 86), (14, 22, 56), n=10, x0=0, x1=W)
    for x in range(0, W, 64):
        cv.stroke([(x, 0), (x, H)], (60, 80, 140), 1.2, alpha=70)
    for y in range(0, H, 64):
        cv.stroke([(0, y), (W, y)], (60, 80, 140), 1.2, alpha=70)
    rect(cv, 0, 650, W, H, (30, 34, 70), ink=None)


def bg_dream(cv, t=0.0, **kw):
    band(cv, 0, H, (255, 224, 240), (190, 220, 255), n=12, x0=0, x1=W)
    for i in range(14):
        x = (i * 211 + t * 12) % (W + 80) - 40
        y = 80 + (i * 83) % 460 + 12 * math.sin(t * 1.2 + i)
        coin(cv, x, y, 14 + (i % 3) * 5)
    for i, (cx, cy, s) in enumerate(((220, 120, 1.4), (700, 200, 1.1), (1080, 100, 1.5))):
        cloud(cv, cx, cy, s, (255, 255, 255))
    rect(cv, 0, 640, W, H, (255, 240, 230), ink=None)


def bg_street_day(cv, t=0.0, **kw):
    band(cv, 0, 470, (160, 214, 250), (236, 246, 252), n=8, x0=0, x1=W)
    for i, (x, h) in enumerate(((20, 260), (200, 330), (380, 220), (560, 300), (760, 240), (960, 340), (1140, 270))):
        rect(cv, x, 470 - h, x + 150, 470, [(236, 196, 160), (190, 210, 236), (240, 220, 170), (214, 190, 220)][i % 4], lw=2.6)
        for r in range(int(h / 56)):
            for c in range(2):
                rect(cv, x + 24 + c * 56, 470 - h + 18 + r * 56, x + 60 + c * 56, 470 - h + 48 + r * 56, (190, 226, 248), lw=1.6)
    rect(cv, 0, 470, W, H, (176, 176, 184), ink=None)
    rect(cv, 0, 470, W, 520, (214, 214, 220), ink=None)
    for x in range(0, W, 160):
        cv.stroke([(x, 650), (x + 80, 650)], (255, 255, 255), 6)


# ----------------------------------------------------------------------------------------------------------------- props
def pr_coins(cv, x, y, s=1.0, t=0.0, n=5, **kw):
    for i in range(n):
        coin(cv, x + (i % 2) * 6 * s, y - i * 10 * s, 22 * s)


def pr_bills(cv, x, y, s=1.0, t=0.0, n=3, fan=0.0, **kw):
    for i in range(n):
        cv.push(x, y - i * 6 * s, scale=s, rot=fan * (i - (n - 1) / 2))
        rrect(cv, -50, -26, 50, 26, 6, (150, 214, 150), lw=2.4)
        cv.ellipse(0, 0, 14, 14, (206, 240, 190), ink=INK, lw=1.8)
        cv.stroke([(-40, -16), (-26, -16)], (100, 170, 110), 3)
        cv.stroke([(26, 16), (40, 16)], (100, 170, 110), 3)
        cv.pop()


def pr_moneybag(cv, x, y, s=1.0, t=0.0, **kw):
    cv.push(x, y, scale=s)
    cv.fill(spline([(-46, 0), (-56, -50), (-26, -86), (-12, -100), (12, -100), (26, -86), (56, -50), (46, 0)], closed=True, n=3), (206, 176, 110), ink=INK, lw=2.6, shade_col=(170, 140, 80), depth=4)
    cv.fill([(-20, -100), (20, -100), (30, -118), (-30, -118)], (206, 176, 110), ink=INK, lw=2.2)
    cv.stroke([(-24, -96), (24, -96)], (232, 80, 80), 5)
    cv.ellipse(0, -48, 24, 24, (255, 232, 140), ink=INK, lw=2.0)
    cv.stroke([(0, -60), (0, -36)], (170, 130, 40), 4)
    cv.pop()


def pr_piggy(cv, x, y, s=1.0, t=0.0, **kw):
    cv.push(x, y, scale=s)
    cv.fill(spline([(-70, -30), (-64, -76), (-20, -100), (30, -98), (66, -70), (74, -34), (50, -6), (-40, -4)], closed=True, n=3), (252, 170, 190), ink=INK, lw=2.8, shade_col=(224, 130, 160), depth=5)
    cv.ellipse(70, -50, 18, 14, (252, 150, 176), ink=INK, lw=2.2)
    cv.ellipse(66, -52, 2.6, 4, (120, 50, 70), ink=None)
    cv.ellipse(76, -52, 2.6, 4, (120, 50, 70), ink=None)
    cv.fill([(8, -100), (28, -122), (36, -96)], (252, 150, 176), ink=INK, lw=2.0)
    cv.ellipse(40, -70, 4, 4, (30, 30, 40), ink=None)
    cv.stroke([(-20, -92), (4, -94)], (110, 50, 70), 5)
    for dx in (-44, 34):
        cv.fill([(dx - 8, -6), (dx + 8, -6), (dx + 10, 14), (dx - 10, 14)], (252, 150, 176), ink=INK, lw=2.0)
    cv.stroke(spline([(-72, -50), (-92, -62), (-84, -78)], n=3), (252, 150, 176), 5)
    cv.pop()


def pr_phone(cv, x, y, s=1.0, t=0.0, screen=(40, 190, 120), **kw):
    """A big phone; the numbers on its screen are overlays set by the scene."""
    cv.push(x, y, scale=s)
    rrect(cv, -60, -200, 60, 0, 16, (40, 44, 56), lw=3.0)
    rrect(cv, -52, -188, 52, -12, 8, screen, ink=None)
    cv.ellipse(0, -194, 3, 3, (90, 96, 110), ink=None)
    cv.ellipse(0, -2, 8, 4, (90, 96, 110), ink=None)
    cv.pop()


def pr_card(cv, x, y, s=1.0, t=0.0, col=(250, 170, 60), **kw):
    cv.push(x, y, scale=s)
    rrect(cv, -60, -38, 60, 38, 8, col, lw=2.6)
    rect(cv, -60, -18, 60, -4, (60, 60, 76), ink=None)
    rrect(cv, -46, 10, -14, 22, 3, (255, 230, 150), lw=1.6)
    cv.ellipse(34, 18, 10, 10, (230, 80, 80), ink=None, alpha=220)
    cv.ellipse(46, 18, 10, 10, (250, 190, 70), ink=None, alpha=220)
    cv.pop()


def pr_calc(cv, x, y, s=1.0, t=0.0, **kw):
    cv.push(x, y, scale=s)
    rrect(cv, -52, -120, 52, 0, 10, (70, 76, 96), lw=2.8)
    rrect(cv, -42, -108, 42, -78, 4, (180, 240, 196), lw=2.0)
    for r in range(4):
        for c in range(4):
            cv.ellipse(-30 + c * 20, -60 + r * 18, 6.5, 6.5, [(250, 160, 80), (210, 214, 224)][1 if c < 3 else 0], ink=INK, lw=1.2)
    cv.pop()


def pr_laptop(cv, x, y, s=1.0, t=0.0, screen=(120, 190, 250), **kw):
    cv.push(x, y, scale=s)
    rrect(cv, -90, -130, 90, -20, 8, (70, 76, 96), lw=2.8)
    rect(cv, -80, -120, 80, -30, screen, ink=None)
    cv.fill([(-110, -20), (110, -20), (122, 0), (-122, 0)], (190, 196, 210), ink=INK, lw=2.6)
    for i in range(3):
        cv.stroke([(-60, -100 + i * 22), (-10 + 40 * i, -100 + i * 22)], (255, 255, 255), 3, alpha=210)
    cv.pop()


def pr_chart(cv, x, y, s=1.0, t=0.0, kind="up", **kw):
    """A small chart board: kind = up | down | flat | bars | bars_up."""
    cv.push(x, y, scale=s)
    rrect(cv, -130, -170, 130, 0, 12, (252, 252, 254), lw=3.0)
    cv.stroke([(-110, -20), (110, -20)], (150, 156, 176), 2.4)
    cv.stroke([(-110, -20), (-110, -150)], (150, 156, 176), 2.4)
    if kind in ("up", "down", "flat"):
        ys = {"up": [-30, -44, -40, -70, -62, -100, -130], "down": [-130, -100, -108, -70, -76, -44, -30], "flat": [-80, -84, -78, -82, -80, -84, -80]}[kind]
        pts = [(-100 + i * 33, v) for i, v in enumerate(ys)]
        col = GREEN if kind == "up" else (RED_C if kind == "down" else (120, 140, 190))
        cv.stroke(spline(pts, n=3), col, 6)
        cv.ellipse(pts[-1][0], pts[-1][1], 7, 7, col, ink=INK, lw=1.8)
    else:
        for i in range(6):
            h = (30 + i * 18) if kind == "bars_up" else (40 + (i * 53) % 90)
            rect(cv, -96 + i * 34, -20 - h, -72 + i * 34, -20, GREEN if kind == "bars_up" else (120, 150, 220), lw=1.8)
    cv.pop()


def pr_bag(cv, x, y, s=1.0, t=0.0, col=(250, 140, 160), **kw):
    cv.push(x, y, scale=s)
    cv.fill([(-34, 0), (34, 0), (40, -76), (-40, -76)], col, ink=INK, lw=2.6, shade_col=mix(col, (0, 0, 0), 0.2), depth=4)
    cv.stroke(spline([(-22, -76), (-18, -104), (18, -104), (22, -76)], n=3), INK, 5)
    cv.ellipse(0, -38, 12, 12, (255, 255, 255), ink=None, alpha=200)
    cv.pop()


def pr_tea(cv, x, y, s=1.0, t=0.0, level=1.0, **kw):
    """A bubble-tea cup with a straw and tapioca pearls."""
    cv.push(x, y, scale=s)
    cv.fill([(-26, 0), (26, 0), (32, -90), (-32, -90)], (255, 244, 230), ink=INK, lw=2.4)
    cv.fill([(-24, 0), (24, 0), (28 - 2 * (1 - level) * 40, -80 * level), (-28 + 2 * (1 - level) * 40, -80 * level)], (206, 160, 110), ink=None)
    for i in range(6):
        cv.ellipse(-14 + (i % 3) * 14, -6 - (i // 3) * 12, 4, 4, (50, 36, 30), ink=None)
    cv.fill([(-36, -90), (36, -90), (36, -100), (-36, -100)], (240, 240, 244), ink=INK, lw=2.0)
    cv.stroke([(8, -100), (22, -140)], (230, 80, 90), 6)
    cv.pop()


def pr_coffee(cv, x, y, s=1.0, t=0.0, **kw):
    cv.push(x, y, scale=s)
    cv.fill([(-24, 0), (24, 0), (28, -56), (-28, -56)], (250, 250, 252), ink=INK, lw=2.4)
    cv.fill([(-28, -30), (28, -30), (27, -42), (-27, -42)], (170, 120, 80), ink=None)
    cv.stroke(spline([(28, -44), (46, -40), (28, -16)], n=3), INK, 4)
    for q in range(3):
        u = (t * 0.6 + q / 3) % 1.0
        cv.stroke(spline([(-8 + 8 * q, -62), (-12 + 8 * q, -84 - 30 * u), (-6 + 8 * q, -104 - 30 * u)], n=3), (255, 255, 255), 3, alpha=int(180 * (1 - u)))
    cv.pop()


def pr_box(cv, x, y, s=1.0, t=0.0, **kw):
    cv.push(x, y, scale=s)
    cv.fill([(-50, 0), (50, 0), (50, -64), (-50, -64)], (214, 170, 116), ink=INK, lw=2.6, shade_col=(176, 132, 84), depth=5)
    cv.fill([(-50, -64), (50, -64), (42, -76), (-42, -76)], (232, 196, 140), ink=INK, lw=2.2)
    cv.fill([(-8, -76), (8, -76), (8, 0), (-8, 0)], (240, 220, 170), ink=None, alpha=200)
    cv.pop()


def pr_robot(cv, x, y, s=1.0, t=0.0, mood="happy", **kw):
    """A little round AI helper robot with a screen face."""
    cv.push(x, y + 4 * math.sin(t * 2.4), scale=s)
    cv.ellipse(0, 6, 40, 8, (0, 0, 0), ink=None, alpha=30)
    cv.fill(spline([(-46, -10), (-52, -64), (-28, -96), (28, -96), (52, -64), (46, -10)], closed=True, n=3), (220, 230, 246), ink=INK, lw=2.8, shade_col=(176, 190, 220), depth=5)
    rrect(cv, -34, -80, 34, -34, 10, (30, 42, 80), lw=2.2)
    for sx in (-12, 12):
        cv.ellipse(sx, -62, 5, 6, (120, 240, 250), ink=None)
    cv.stroke(spline([(-10, -48), (0, -42 if mood == "happy" else -50), (10, -48)], n=3), (120, 240, 250), 3)
    cv.stroke([(0, -96), (0, -116)], INK, 4)
    cv.ellipse(0, -120, 7, 7, (255, 120, 120), ink=INK, lw=1.8)
    for sx in (-1, 1):
        cv.stroke([(sx * 50, -50), (sx * 72, -30 + 6 * math.sin(t * 3 + sx))], (176, 190, 220), 9)
    cv.pop()


def pr_flag(cv, x, y, s=1.0, t=0.0, col=(232, 60, 60), **kw):
    """A red flag on a pole (warning sign)."""
    cv.push(x, y, scale=s)
    cv.stroke([(0, 0), (0, -150)], INK, 8)
    cv.stroke([(0, 0), (0, -150)], (150, 110, 76), 5)
    sw = 8 * math.sin(t * 4)
    cv.fill(spline([(2, -148), (60, -140 + sw), (110, -150), (100, -120), (58, -112 + sw), (2, -104)], closed=True, n=3), col, ink=INK, lw=2.6, shade_col=mix(col, (0, 0, 0), 0.2))
    cv.pop()


def pr_magnifier(cv, x, y, s=1.0, t=0.0, **kw):
    cv.push(x, y, scale=s)
    cv.stroke([(26, -26), (62, 10)], INK, 14)
    cv.stroke([(26, -26), (62, 10)], (150, 106, 74), 9)
    cv.ellipse(0, -52, 40, 40, (200, 236, 252), ink=INK, lw=4.0, alpha=220)
    cv.stroke([(-20, -70), (-6, -80)], (255, 255, 255), 4, alpha=220)
    cv.pop()


def pr_shield(cv, x, y, s=1.0, t=0.0, **kw):
    cv.push(x, y, scale=s)
    cv.fill(spline([(-50, -90), (0, -108), (50, -90), (46, -40), (0, 0), (-46, -40)], closed=True, n=3), (96, 170, 240), ink=INK, lw=3.0, shade_col=(60, 126, 200), depth=5)
    check_mark(cv, 0, -52, 1.2, col=(255, 255, 255), lw=7, a=1.0)
    cv.pop()


def pr_calendar(cv, x, y, s=1.0, t=0.0, **kw):
    cv.push(x, y, scale=s)
    rrect(cv, -56, -110, 56, 0, 8, (252, 252, 254), lw=2.8)
    rect(cv, -56, -110, 56, -80, (232, 76, 76), lw=2.4)
    for r in range(3):
        for c in range(5):
            cv.ellipse(-36 + c * 18, -62 + r * 20, 4, 4, (170, 176, 196), ink=None)
    cv.pop()


def pr_hearts_burst(cv, x, y, s=1.0, t=0.0, **kw):
    for i in range(5):
        u = (t * 0.7 + i / 5) % 1.0
        cv.ellipse(x + 40 * math.sin(i * 2.2) * s, y - 100 * u * s, 8 * s, 8 * s, (255, 140, 170), ink=None, alpha=int(230 * (1 - u)))


def pr_steam(cv, x, y, s=1.0, t=0.0, **kw):
    for q in range(3):
        u = (t * 0.6 + q / 3) % 1.0
        cv.stroke(spline([(x - 10 + 10 * q, y), (x - 14 + 10 * q, y - 30 * s - 30 * u), (x - 8 + 10 * q, y - 60 * s - 30 * u)], n=3), (255, 255, 255), 3.4, alpha=int(180 * (1 - u)))


def pr_lock(cv, x, y, s=1.0, t=0.0, **kw):
    cv.push(x, y, scale=s)
    cv.stroke(spline([(-22, -60), (-22, -92), (22, -92), (22, -60)], n=3), INK, 11)
    cv.stroke(spline([(-22, -60), (-22, -92), (22, -92), (22, -60)], n=3), (190, 196, 212), 6)
    rrect(cv, -36, -62, 36, 0, 8, (250, 200, 70), lw=2.8)
    cv.ellipse(0, -34, 6, 6, (80, 60, 30), ink=None)
    cv.pop()


def pr_screen_board(cv, x, y, s=1.0, t=0.0, w=420, h=240, col=(24, 28, 56), **kw):
    """A big screen / board on the wall (text goes on top as overlays)."""
    cv.push(x, y, scale=s)
    rrect(cv, -w / 2, -h, w / 2, 0, 14, col, lw=3.4, ink=(250, 250, 252))
    cv.pop()


def pr_spotlight(cv, x, y, s=1.0, t=0.0, **kw):
    cv.fill([(x - 18, 0), (x + 18, 0), (x + 150 * s, 700), (x - 150 * s, 700)], (255, 244, 200), ink=None, alpha=40)


REG_BG = dict(bedroom=bg_bedroom, grill=bg_grill, conference=bg_conference, desk=bg_desk, mall=bg_mall, cowork=bg_cowork, calc=bg_calc, dream=bg_dream, street=bg_street_day)
REG_PROP = dict(coins=pr_coins, bills=pr_bills, moneybag=pr_moneybag, piggy=pr_piggy, phone=pr_phone, card=pr_card, calc=pr_calc, laptop=pr_laptop, chart=pr_chart, bag=pr_bag,
                tea=pr_tea, coffee=pr_coffee, box=pr_box, robot=pr_robot, flag=pr_flag, magnifier=pr_magnifier, shield=pr_shield, calendar=pr_calendar, hearts=pr_hearts_burst,
                steam=pr_steam, lock=pr_lock, board=pr_screen_board, spotlight=pr_spotlight)
