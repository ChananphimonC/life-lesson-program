"""The puppy story kit (all procedural, soft rounded cartoon shapes, same engine as the rest): the dog 'โมจิ' (cream puppy with tan floppy ears), his things (kibble bowl,
unicorn plush with one torn ear, snack bag/cabinet, ball, mom's shirt, wall clock, phone, rain, lightning, motorbike) and the rooms seen from his height (morning bedroom,
living room + front door, rainy window, under the bed, under the dinner table, night bedroom, the soi at dusk). Registered into fin_props.REG_PROP / REG_BG so story.json can use them by name.

dog(cv, x, y, s, t, pose, ex, flip, look, hold, wag): (x, y) = the ground under the body, facing +x (flip=True faces left).
  pose: sit | stand | walk | run | lie | sleep | jump | beg      ex: neutral | happy | joy | sad | alert | sleepy | worry | sulk
"""
from __future__ import annotations

import math

import engine  # noqa: F401
import fin_props as FP
from props_future import *  # noqa: F401,F403
from toon import INK, mix, spline

W, H = 1280, 720
CREAM = (248, 228, 192)
CREAM_SH = (224, 190, 146)
MUZZLE = (255, 248, 234)
TAN = (216, 150, 92)
TAN_SH = (176, 112, 66)
NOSE = (58, 40, 46)
EYE = (36, 26, 30)


def _closed(t, seed):
    return ((t * 0.9 + seed) % 3.9) < 0.13


# ------------------------------------------------------------------------------------------------------------------------------------------------- the dog
def _head(cv, hx, hy, ex, t, look, seed, hold, ear_up=0.0, mouth_open=0.0):
    """Head 3/4 view facing +x. Far ear behind, near ear in front. Floppy ears react to the mood."""
    sad = ex in ("sad", "worry", "sulk")
    joy = ex in ("joy", "happy")
    alert = ex == "alert"
    sleepy = ex == "sleepy"
    droop = 1.0 if sad else (0.3 if sleepy else 0.0)
    flap = math.sin(t * 9 + seed) * (6 if ex == "joy" else 1.5)
    up = ear_up + (0.9 if alert else 0.0)
    # far ear
    cv.fill(spline([(hx - 8, hy - 26), (hx - 30, hy - 30 - 12 * up), (hx - 44, hy - 4 + 10 * droop + flap), (hx - 32, hy + 14 + 10 * droop), (hx - 14, hy + 2)], closed=True, n=3), TAN_SH, ink=INK, lw=2.4)
    cv.ellipse(hx + 2, hy, 41, 35, CREAM, ink=INK, lw=2.6, shade_col=CREAM_SH)                       # head
    cv.fill(spline([(hx - 6, hy - 30), (hx + 4, hy - 20), (hx + 14, hy - 30)], n=2), TAN, ink=None)          # tan patch over the top of the head
    cv.ellipse(hx + 28, hy + 13, 23, 17, MUZZLE, ink=INK, lw=2.2)                                 # muzzle
    cv.ellipse(hx + 45, hy + 5, 9, 6.8, NOSE, ink=INK, lw=1.6)                                  # nose
    cv.ellipse(hx + 43, hy + 3, 2.6, 1.8, (255, 255, 255), ink=None, alpha=200)
    cv.stroke([(hx + 45, hy + 11), (hx + 43, hy + 19)], INK, 2.0)                                  # lip line
    if mouth_open > 0.05 or ex == "joy":
        mo = max(mouth_open, 0.9 if ex == "joy" else 0.0)
        cv.fill(spline([(hx + 14, hy + 17), (hx + 24, hy + 18 + 14 * mo), (hx + 36, hy + 17)], closed=True, n=3), (150, 52, 66), ink=INK, lw=1.8)
        cv.ellipse(hx + 25, hy + 22 + 10 * mo, 7, 5 + 4 * mo, (255, 138, 150), ink=None)
    elif sad:
        cv.stroke(spline([(hx + 12, hy + 21), (hx + 24, hy + 15), (hx + 36, hy + 19)], n=3), INK, 2.2)
    else:
        cv.stroke(spline([(hx + 12, hy + 17), (hx + 24, hy + 22), (hx + 37, hy + 16)], n=3), INK, 2.2)   # little smile
    # eyes: two big dark glossy eyes
    for k, (ex_, ey_) in enumerate(((hx + 4, hy - 8), (hx + 30, hy - 9))):
        shut = _closed(t, seed + k * 0.0)
        if ex == "sleepy" and math.sin(t * 0.8 + seed) > -0.3 or (shut and not joy):
            cv.stroke(spline([(ex_ - 8, ey_ + 1), (ex_, ey_ + 5), (ex_ + 8, ey_ + 1)], n=3), INK, 2.8)
            continue
        if joy and ex == "joy":
            cv.stroke(spline([(ex_ - 8, ey_ + 4), (ex_, ey_ - 5), (ex_ + 8, ey_ + 4)], n=3), INK, 3.2)               # ^ ^ eyes
            continue
        r = 11.5 if alert else (10.5 if not sad else 11.0)
        cv.ellipse(ex_, ey_, r * 0.9, r + 1, EYE, ink=None)
        px, py = look * 3.2, (2.2 if sad else 0.0)
        cv.ellipse(ex_ + px - 2.6, ey_ + py - 3.2, 3.4, 3.8, (255, 255, 255), ink=None, alpha=235)
        cv.ellipse(ex_ + px + 2.6, ey_ + py + 3.2, 1.5, 1.5, (255, 255, 255), ink=None, alpha=160)
        if sad:
            cv.stroke([(ex_ - 7, ey_ - 11), (ex_ + 6, ey_ - 15)] if k == 0 else [(ex_ - 6, ey_ - 15), (ex_ + 7, ey_ - 11)], (150, 100, 66), 2.6)   # worried brows
        else:
            cv.ellipse(ex_ + 1, ey_ - 15 - (3 if alert else 0), 4.6, 2.6, TAN_SH, ink=None, alpha=210)   # the little tan 'eyebrow dots' of a puppy
    cv.ellipse(hx - 4, hy + 14, 9, 6, (246, 150, 140), ink=None, alpha=95)                         # blush
    if hold == "unicorn":
        unicorn(cv, hx + 54, hy + 44, 0.4, t, tilt=-28)
    # near ear (over the head)
    cv.fill(spline([(hx - 26, hy - 28), (hx - 6, hy - 38 - 12 * up), (hx - 2, hy - 6 + 14 * droop + flap), (hx - 14, hy + 12 + 12 * droop), (hx - 34, hy - 2)], closed=True, n=3), TAN, ink=INK, lw=2.4, shade_col=TAN_SH)


def dog(cv, x, y, s=1.0, t=0.0, pose="sit", ex="neutral", flip=False, look=0.0, hold=None, wag=1.0, seed=0.0, **kw):
    cv.push(x, y, scale=s, flip=flip)
    ph = t * (10 if pose == "walk" else 17) + seed
    breath = math.sin(t * 2.4 + seed) * 1.6
    wagv = math.sin(t * (14 if ex in ("joy", "happy") else 6) + seed) * (0.9 if ex == "joy" else 0.5 if ex == "happy" else 0.18) * wag
    # shadow
    cv.ellipse(0, 2, 62, 9, (60, 40, 40), ink=None, alpha=48)

    def tail(rx, ry, curl=1.0):
        pts = [(rx, ry), (rx - 14, ry - 8 - 4 * curl), (rx - 18 + 3 * wagv * 6, ry - 26 - 4 * curl + 2 * wagv * 6), (rx - 6 + 7 * wagv * 6, ry - 38 - 3 * curl)]
        cv.stroke(spline(pts, n=3), INK, 24)
        cv.stroke(spline(pts, n=3), CREAM, 19)
        cv.ellipse(pts[-1][0], pts[-1][1], 12, 12, MUZZLE, ink=INK, lw=2.2)

    def leg(x0, y0, x1, y1, col=CREAM, w=17):
        cv.stroke([(x0, y0), (x1, y1)], INK, w + 4.5)
        cv.stroke([(x0, y0), (x1, y1)], col, w)
        cv.ellipse(x1 + 2, y1 - 1, 11.5, 7.4, MUZZLE, ink=INK, lw=2.0)

    if pose in ("sit", "beg"):
        up = 1.0 if pose == "beg" else 0.0
        tail(-56, -22, 1.0)
        cv.fill(spline([(-56, -20), (-58, -48), (-34, -76 - 4 * up), (4, -92 - 8 * up + breath), (28, -90 - 8 * up), (38, -64), (36, -22), (12, -4), (-30, -2)], closed=True, n=3), CREAM, ink=INK, lw=2.6, shade_col=CREAM_SH, depth=5)
        cv.fill(spline([(-52, -6), (-56, -34), (-34, -52), (-8, -36), (-4, -6)], closed=True, n=3), CREAM, ink=INK, lw=2.2, shade_col=CREAM_SH)           # haunch
        cv.fill(spline([(-8, -62), (4, -86), (22, -80), (28, -44), (14, -22), (-2, -34)], closed=True, n=3), MUZZLE, ink=None)                          # chest
        cv.fill(spline([(-52, -62), (-40, -86), (-14, -92 + breath), (-16, -70), (-38, -50)], closed=True, n=3), TAN, ink=None, alpha=235)                # back patch
        cv.ellipse(-10, -5, 17, 7, MUZZLE, ink=INK, lw=2.0)                                                                                              # hind paw
        leg(30, -52 - 6 * up, 32, -4 - (30 * up))
        leg(18, -52 - 6 * up, 20, -4 - (30 * up), CREAM_SH)
        _head(cv, 36, -112 - 6 * up + breath, ex, t, look, seed, hold)
    elif pose in ("stand", "walk", "run"):
        sw = 0.0 if pose == "stand" else (16 if pose == "walk" else 26)
        bob = (abs(math.sin(ph)) * (3 if pose == "walk" else 7)) if pose != "stand" else breath * 0.5
        tail(-52, -60 - bob, 0.4)
        for sx, col in ((-1, CREAM_SH), (1, CREAM_SH)):
            a = math.sin(ph + (0 if sx > 0 else math.pi)) * sw
            leg(-30 + sx * 4, -40 - bob, -34 + a + sx * 4, -4 - max(0, math.cos(ph + (0 if sx > 0 else math.pi))) * (6 if sw else 0), col)
        cv.fill(spline([(-52, -54 - bob), (-34, -80 - bob), (8, -84 - bob + breath), (42, -76 - bob), (54, -54 - bob), (38, -34 - bob), (0, -30 - bob), (-36, -34 - bob)], closed=True, n=3), CREAM, ink=INK, lw=2.6, shade_col=CREAM_SH, depth=5)
        cv.fill(spline([(-46, -66 - bob), (-30, -84 - bob), (6, -88 - bob), (10, -72 - bob), (-20, -56 - bob)], closed=True, n=3), TAN, ink=None, alpha=235)
        for sx in (-1, 1):
            a = math.sin(ph + (math.pi if sx > 0 else 0)) * sw
            leg(34 + sx * 4, -40 - bob, 38 + a + sx * 4, -4 - max(0, math.cos(ph + (math.pi if sx > 0 else 0))) * (6 if sw else 0))
        _head(cv, 66, -88 - bob + breath, ex, t, look, seed, hold, ear_up=0.0, mouth_open=0.7 if pose == "run" else 0.0)
    elif pose == "lie":
        tail(-62, -14, 0.0)
        cv.fill(spline([(-62, -4), (-62, -24), (-36, -44), (4, -46 + breath), (34, -38), (50, -20), (46, -2), (-20, 0)], closed=True, n=3), CREAM, ink=INK, lw=2.6, shade_col=CREAM_SH, depth=5)
        cv.fill(spline([(-56, -24), (-36, -42), (-2, -46 + breath), (-6, -30), (-34, -18)], closed=True, n=3), TAN, ink=None, alpha=235)
        _head(cv, 76, -36 + breath, ex, t, look, seed, hold)
        leg(46, -8, 96, -6, CREAM_SH, 15)
        leg(34, -10, 86, -2, CREAM, 15)
    elif pose == "sleep":
        cv.ellipse(0, -28, 60, 30, CREAM, ink=INK, lw=2.6, shade_col=CREAM_SH)
        cv.fill(spline([(-52, -30), (-30, -52 + breath), (8, -56 + breath), (-4, -34)], closed=True, n=3), TAN, ink=None, alpha=235)
        cv.stroke(spline([(-54, -28), (-72, -40), (-60, -64), (-40, -60)], n=3), INK, 17)
        cv.stroke(spline([(-54, -28), (-72, -40), (-60, -64), (-40, -60)], n=3), CREAM, 12)
        _head(cv, 34, -28 + breath, "sleepy", t, 0.0, seed, hold)
        leg(20, -10, 54, -8, CREAM_SH, 12)
    else:                                                                            # jump: front end lifted, tail going wild
        cv.push(-30, 0, rot=-22)
        tail(-52, -62, 0.4)
        for a in (-10, 0):
            leg(-30 + a, -40, -36 + a, -4, CREAM_SH)
        cv.fill(spline([(-52, -54), (-34, -80), (8, -84), (42, -76), (54, -54), (38, -34), (0, -30), (-36, -34)], closed=True, n=3), CREAM, ink=INK, lw=2.6, shade_col=CREAM_SH, depth=5)
        leg(34, -42, 60, -70 - 8 * math.sin(t * 14), CREAM)
        leg(46, -40, 72, -58 - 8 * math.sin(t * 14 + 2), CREAM_SH)
        _head(cv, 70, -98, "joy" if ex in ("joy", "happy") else ex, t, look, seed, hold, ear_up=0.0, mouth_open=1.0)
        cv.pop()
    cv.pop()


# ------------------------------------------------------------------------------------------------------------------------------------------------- things
def unicorn(cv, x, y, s=1.0, t=0.0, tilt=0.0, **kw):
    """The unicorn plush: white-pink horse head + body, rainbow mane, gold horn, ONE ear chewed off, a button eye."""
    cv.push(x, y, rot=tilt, scale=s)
    cv.fill(spline([(-46, 0), (-52, -40), (-30, -78), (4, -84), (30, -66), (40, -30), (30, 0)], closed=True, n=3), (255, 244, 250), ink=INK, lw=2.8, shade_col=(238, 214, 232), depth=5)    # body
    cv.fill(spline([(10, -60), (26, -92), (62, -104), (86, -84), (88, -60), (64, -46), (30, -42)], closed=True, n=3), (255, 244, 250), ink=INK, lw=2.8, shade_col=(238, 214, 232), depth=5)   # head
    for i, c in enumerate(((255, 120, 130), (255, 190, 90), (250, 236, 110), (110, 210, 150), (110, 170, 240))):
        cv.stroke(spline([(14 - i * 2, -62 - i * 4), (-4 - i * 5, -80 - i * 3), (-18 - i * 6, -62 + i * 5)], n=3), c, 6)                                                               # mane
    cv.fill([(50, -98), (60, -140), (66, -98)], (255, 214, 90), ink=INK, lw=2.4)                                                                                                      # horn
    cv.stroke([(54, -108), (63, -112)], (230, 170, 50), 2.0)
    cv.fill(spline([(30, -96), (36, -108), (42, -96)], closed=True, n=2), (240, 190, 210), ink=INK, lw=2.0)                                                                           # the stub of the chewed ear
    cv.stroke([(44, -98), (58, -100)], (200, 150, 170), 2.0)
    cv.ellipse(64, -72, 5.5, 5.5, (50, 40, 60), ink=INK, lw=1.6)
    cv.ellipse(62.5, -73.5, 1.6, 1.6, (255, 255, 255), ink=None)
    cv.stroke(spline([(70, -54), (78, -52), (84, -58)], n=2), (170, 90, 120), 2.2)
    cv.stroke([(-20, -30), (-6, -26)], (222, 190, 214), 2.2)                                                                                                                         # stitches
    cv.pop()


def bowl(cv, x, y, s=1.0, t=0.0, food=1.0, **kw):
    cv.push(x, y, scale=s)
    cv.ellipse(0, -2, 58, 10, (60, 40, 40), ink=None, alpha=50)
    cv.fill(spline([(-52, -34), (-46, -6), (-26, 0), (26, 0), (46, -6), (52, -34)], closed=True, n=3), (232, 96, 92), ink=INK, lw=2.8, shade_col=(196, 66, 70), depth=5)
    cv.ellipse(0, -34, 52, 10, (206, 70, 74), ink=INK, lw=2.4)
    if food > 0.05:
        cv.ellipse(0, -36, 44 * food, 8, (122, 80, 54), ink=None)
        for i in range(int(14 * food)):
            a = i * 2.4
            px, py = math.cos(a) * (6 + (i * 5) % 34) * 0.95, -38 - 6 * (i % 3)
            cv.ellipse(px, py, 7.5, 5.5, (150, 98, 62) if i % 2 else (126, 80, 52), ink=INK, lw=1.4)
    cv.ellipse(0, -16, 13, 9, (255, 230, 226), ink=None, alpha=200)                                    # a bone mark on the bowl
    cv.pop()


def ball(cv, x, y, s=1.0, t=0.0, **kw):
    cv.push(x, y, scale=s)
    cv.ellipse(0, -3, 26, 5, (60, 40, 40), ink=None, alpha=48)
    cv.ellipse(0, -26, 26, 26, (232, 84, 84), ink=INK, lw=2.6, shade_col=(190, 52, 62))
    cv.stroke(spline([(-22, -30), (0, -20), (22, -30)], n=3), (255, 230, 220), 3.2)
    cv.ellipse(-8, -36, 6, 4, (255, 255, 255), ink=None, alpha=170)
    cv.pop()


def snack(cv, x, y, s=1.0, t=0.0, **kw):
    """A crinkly treat bag."""
    cv.push(x, y, scale=s)
    cv.fill(spline([(-34, 0), (-38, -70), (-26, -96), (26, -96), (38, -70), (34, 0)], closed=True, n=3), (250, 190, 60), ink=INK, lw=2.8, shade_col=(222, 150, 40), depth=5)
    for i in range(6):
        cv.stroke([(-26 + i * 10, -96), (-26 + i * 10 + 2, -106 + (i % 2) * 4)], INK, 2.4)
    cv.fill(spline([(-18, -62), (-6, -72), (6, -64), (14, -72), (22, -58), (10, -46), (-6, -48), (-14, -42)], closed=True, n=2), (255, 244, 220), ink=INK, lw=1.8)
    cv.pop()


def cabinet(cv, x, y, s=1.0, t=0.0, **kw):
    """The treat cupboard (closed, the little door handle)."""
    cv.push(x, y, scale=s)
    rrect(cv, -90, -260, 90, 0, 10, (232, 196, 150), lw=3.0, shade_col=(200, 162, 116))
    rrect(cv, -78, -248, -4, -12, 6, (244, 214, 172), lw=2.4)
    rrect(cv, 4, -248, 78, -12, 6, (244, 214, 172), lw=2.4)
    cv.ellipse(-12, -130, 5, 5, (150, 108, 70), ink=INK, lw=1.6)
    cv.ellipse(12, -130, 5, 5, (150, 108, 70), ink=INK, lw=1.6)
    cv.fill(spline([(30, -200), (44, -214), (58, -200), (44, -186)], closed=True, n=2), (250, 190, 60), ink=INK, lw=2.0)
    cv.pop()


def shirt(cv, x, y, s=1.0, t=0.0, **kw):
    """Mom's shirt dropped on the floor (smells like her)."""
    cv.push(x, y, scale=s)
    cv.ellipse(0, -2, 80, 10, (60, 40, 40), ink=None, alpha=36)
    cv.fill(spline([(-70, -6), (-58, -30), (-32, -40), (-14, -30), (14, -30), (32, -40), (58, -30), (70, -6), (40, 2), (-40, 2)], closed=True, n=3), (122, 176, 214), ink=INK, lw=2.6, shade_col=(92, 140, 182), depth=5)
    cv.fill(spline([(-14, -30), (0, -20), (14, -30)], closed=True, n=2), (96, 152, 192), ink=INK, lw=1.8)
    cv.pop()


def clock(cv, x, y, s=1.0, t=0.0, hour=6, minute=30, **kw):
    cv.push(x, y, scale=s)
    cv.ellipse(0, 0, 56, 56, (250, 246, 236), ink=INK, lw=4.0, shade_col=(226, 218, 204))
    for i in range(12):
        a = math.radians(i * 30 - 90)
        cv.stroke([(math.cos(a) * 44, math.sin(a) * 44), (math.cos(a) * 50, math.sin(a) * 50)], INK, 2.6)
    ah = math.radians((hour % 12 + minute / 60.0) * 30 - 90)
    am = math.radians(minute * 6 - 90)
    cv.stroke([(0, 0), (math.cos(ah) * 28, math.sin(ah) * 28)], INK, 5.5)
    cv.stroke([(0, 0), (math.cos(am) * 42, math.sin(am) * 42)], INK, 3.6)
    cv.ellipse(0, 0, 4, 4, (232, 84, 84), ink=INK, lw=1.4)
    cv.pop()


def rain(cv, x, y, s=1.0, t=0.0, w=420, h=300, heavy=1.0, **kw):
    """Falling streaks inside a box whose top-left is (x, y)."""
    for i in range(int(46 * heavy)):
        px = x + (i * 97.3) % w
        py = y + ((i * 53.7) + t * (520 + (i % 5) * 60)) % h
        cv.stroke([(px, py), (px - 5, py + 22)], (200, 224, 246), 2.6, alpha=200)


def bolt(cv, x, y, s=1.0, t=0.0, **kw):
    """A lightning flash: a yellow zig-zag + a short white pulse of the whole picture."""
    ph = (t * 0.9) % 3.0
    if ph > 0.22:
        return
    a = int(255 * (1 - ph / 0.22))
    cv.push(x, y, scale=s)
    cv.stroke([(0, 0), (-26, 60), (6, 62), (-30, 140), (30, 52), (0, 50), (22, 0)], (255, 236, 120), 9, alpha=a)
    cv.pop()
    cv.fill([(0, 0), (W, 0), (W, H), (0, H)], (255, 255, 255), ink=None, alpha=int(a * 0.45))


def phone_glow(cv, x, y, s=1.0, t=0.0, **kw):
    """A phone seen from below, its glow washing over a hand."""
    cv.push(x, y, scale=s)
    cv.ellipse(0, -90, 120, 90, (140, 190, 255), ink=None, alpha=38)
    rrect(cv, -56, -196, 56, 0, 14, (40, 44, 56), lw=3.0)
    rrect(cv, -48, -184, 48, -14, 8, (110, 170, 250), ink=None)
    for i in range(4):
        rrect(cv, -36, -170 + i * 36, 18 + (i % 2) * 14, -150 + i * 36, 4, (230, 244, 255), ink=None)
    cv.pop()


def bike(cv, x, y, s=1.0, t=0.0, beam=1.0, **kw):
    """The motorbike (side view, heading right) with a headlight beam; the sound dogs know by heart."""
    cv.push(x, y, scale=s)
    if beam > 0.05:
        cv.fill([(70, -60), (330, -110), (330, 0), (70, -40)], (255, 244, 180), ink=None, alpha=int(70 * beam))
    for wx in (-56, 56):
        cv.ellipse(wx, -26, 26, 26, (50, 52, 62), ink=INK, lw=3.0)
        cv.ellipse(wx, -26, 11, 11, (190, 196, 206), ink=INK, lw=2.0)
    cv.fill(spline([(-60, -30), (-48, -68), (-6, -74), (26, -60), (60, -30), (24, -30), (-18, -26)], closed=True, n=3), (232, 84, 70), ink=INK, lw=2.8, shade_col=(190, 56, 52), depth=5)
    cv.stroke([(40, -56), (56, -92), (70, -96)], INK, 6)
    cv.ellipse(70, -64, 8, 8, (255, 244, 190), ink=INK, lw=2.0)
    rrect(cv, -42, -80, 6, -66, 6, (50, 44, 52), lw=2.2)
    cv.pop()


def zzz(cv, x, y, s=1.0, t=0.0, **kw):
    for i in range(3):
        u = (t * 0.5 + i * 0.33) % 1.0
        sz = (16 + i * 8) * s
        px, py = x + i * 22 * s + u * 14, y - u * 70 * s - i * 18 * s
        a = int(255 * (1 - u))
        pts = [(px - sz, py - sz), (px + sz, py - sz), (px - sz, py + sz), (px + sz, py + sz)]
        cv.stroke(pts, (230, 238, 255), 4.4, alpha=a)


def sun_beam(cv, x, y, s=1.0, t=0.0, **kw):
    cv.fill([(x, y), (x + 220 * s, y), (x + 420 * s, y + 520 * s), (x + 120 * s, y + 520 * s)], (255, 244, 200), ink=None, alpha=70)


def hand(cv, x, y, s=1.0, t=0.0, pat=1.0, sleeve=(236, 150, 150), **kw):
    """A hand + sleeve coming in from the top of the picture, patting (or scratching) the dog's head. (x, y) = where the palm lands."""
    dy = math.sin(t * 6.0) * 9 * pat
    cv.push(x, y + dy, scale=s)
    cv.stroke([(70, -520), (24, -60)], INK, 62)
    cv.stroke([(70, -520), (24, -60)], sleeve, 54)
    cv.stroke([(30, -120), (36, -40)], (210, 110, 112), 6, alpha=140)
    cv.fill(spline([(-34, -8), (-40, -34), (-26, -62), (24, -66), (44, -40), (38, -8), (0, 8)], closed=True, n=3), (236, 192, 158), ink=INK, lw=2.6, shade_col=(214, 164, 130), depth=4)
    for i, fx in enumerate((-30, -10, 10, 30)):
        cv.ellipse(fx, 6 + (i % 2) * 3, 9, 12, (236, 192, 158), ink=INK, lw=2.2)
    cv.pop()


# ------------------------------------------------------------------------------------------------------------------------------------------------- rooms (the dog's eye level)
def _floor(cv, y0, col, col2=None, planks=True):
    cv.fill([(0, y0), (W, y0), (W, H), (0, H)], col, ink=None)
    if planks:
        for i in range(1, 7):
            yy = y0 + i * (H - y0) / 7.0
            cv.stroke([(0, yy), (W, yy)], col2 or mix(col, (0, 0, 0), 0.12), 2.0, alpha=170)


def _window(cv, x0, y0, x1, y1, sky0, sky1, cross=True):
    rrect(cv, x0 - 10, y0 - 10, x1 + 10, y1 + 10, 8, (250, 244, 232), lw=3.0)
    band(cv, y0, y1, sky0, sky1, n=8, x0=x0, x1=x1)
    if cross:
        cv.stroke([((x0 + x1) / 2, y0), ((x0 + x1) / 2, y1)], (250, 244, 232), 6)
        cv.stroke([(x0, (y0 + y1) / 2), (x1, (y0 + y1) / 2)], (250, 244, 232), 6)


def bg_pup_bedroom(cv, t=0.0, light=1.0, **kw):
    """Mom's bedroom in the early morning, seen from the dog's height."""
    band(cv, 0, 470, mix((250, 226, 196), (40, 44, 80), 1 - light), mix((246, 212, 178), (54, 56, 96), 1 - light), n=8, x0=0, x1=W)
    _floor(cv, 470, mix((196, 150, 108), (70, 60, 84), 1 - light))
    _window(cv, 820, 70, 1140, 330, mix((255, 236, 190), (30, 40, 90), 1 - light), mix((255, 214, 170), (50, 60, 110), 1 - light))
    if light > 0.4:
        sun_beam(cv, 840, 120, 1.0)
    rrect(cv, 30, 300, 700, 470, 24, mix((236, 150, 150), (110, 76, 100), 1 - light), lw=3.0)                          # bed (the high side, the dog looks up at it)
    rrect(cv, 30, 250, 700, 330, 24, mix((250, 240, 232), (170, 160, 190), 1 - light), lw=3.0)
    rrect(cv, 60, 226, 250, 294, 22, mix((255, 255, 255), (200, 200, 226), 1 - light), lw=2.6)
    cv.fill(spline([(300, 258), (360, 200), (470, 188), (560, 224), (620, 258)], closed=True, n=3), mix((226, 130, 134), (96, 64, 90), 1 - light), ink=INK, lw=2.6)   # a lump under the blanket
    rect(cv, 730, 380, 860, 470, mix((170, 120, 84), (80, 60, 70), 1 - light), lw=2.6)                                  # bedside table
    clock(cv, 795, 350, 0.42, t, hour=5, minute=30)


def bg_pup_living(cv, t=0.0, light=1.0, door_open=0.0, **kw):
    """Living room, afternoon: window, sofa, the front door on the right, a rug."""
    dim = 1 - light
    band(cv, 0, 470, mix((250, 238, 214), (60, 62, 86), dim), mix((242, 224, 196), (70, 70, 94), dim), n=8, x0=0, x1=W)
    _floor(cv, 470, mix((200, 156, 112), (90, 80, 90), dim))
    _window(cv, 110, 80, 430, 330, mix((190, 226, 250), (80, 90, 120), dim), mix((236, 246, 255), (110, 116, 140), dim))
    rrect(cv, 520, 270, 900, 470, 28, mix((120, 170, 160), (70, 96, 100), dim), lw=3.0, shade_col=mix((92, 140, 132), (50, 70, 76), dim))                 # sofa
    rrect(cv, 540, 220, 880, 330, 24, mix((140, 188, 178), (80, 106, 110), dim), lw=3.0)
    cv.ellipse(640, 470, 270, 30, mix((232, 130, 130), (120, 80, 96), dim), ink=None, alpha=190)                                                        # rug
    # front door (right)
    x0, x1 = 980, 1230
    if door_open > 0.02:
        cv.fill([(x0, 80), (x1, 80), (x1, 470), (x0, 470)], (255, 214, 140), ink=None)                                                                  # warm light outside
        cv.fill([(x0 + 40, 470), (x1 + 120, 720), (x0 - 80, 720)], (255, 224, 160), ink=None, alpha=int(110 * door_open))
        rrect(cv, x0 - 8, 80, x0 + 18 + 200 * (1 - door_open), 470, 6, (180, 126, 84), lw=3.0)
    else:
        rrect(cv, x0, 80, x1, 470, 8, (182, 128, 86), lw=3.0, shade_col=(150, 100, 66))
        rrect(cv, x0 + 24, 110, x1 - 24, 270, 6, (198, 146, 100), lw=2.0)
        rrect(cv, x0 + 24, 290, x1 - 24, 440, 6, (198, 146, 100), lw=2.0)
        cv.ellipse(x1 - 36, 300, 10, 10, (250, 214, 100), ink=INK, lw=2.0)
        rect(cv, x0 + 6, 462, x1 - 6, 470, mix((255, 230, 180), (60, 50, 60), dim), ink=None)                                                           # light under the door


def bg_pup_rain(cv, t=0.0, **kw):
    """A grey afternoon: big window with rain; the room is dim and cold."""
    band(cv, 0, 470, (176, 182, 198), (160, 166, 184), n=8, x0=0, x1=W)
    _floor(cv, 470, (140, 118, 104))
    _window(cv, 380, 50, 900, 380, (110, 124, 150), (150, 160, 180))
    rain(cv, 380, 50, 1.0, t, w=520, h=330, heavy=1.2)
    for i in range(4):
        px = 420 + i * 140 + (t * 6) % 6
        cv.stroke([(px, 70), (px + 3, 360 + (i * 37) % 40)], (214, 232, 248), 3.0, alpha=140)                                                            # drops running down the glass
    cv.fill([(0, 0), (W, 0), (W, H), (0, H)], (40, 50, 80), ink=None, alpha=40)
    rrect(cv, 20, 420, 360, 470, 16, (110, 140, 140), lw=2.6)


def bg_pup_under_bed(cv, t=0.0, **kw):
    """Under the bed: dark, narrow, safe. A strip of grey light at the far end, the slats above."""
    cv.fill([(0, 0), (W, 0), (W, H), (0, H)], (26, 24, 46), ink=None)
    band(cv, 0, 150, (48, 40, 70), (30, 28, 52), n=6, x0=0, x1=W)
    for i in range(7):
        rect(cv, 20 + i * 190, 20, 150 + i * 190, 150, (74, 56, 62), ink=None)                                                                          # slats
    rect(cv, 0, 150, W, 182, (62, 46, 52), ink=None)
    _floor(cv, 520, (40, 36, 60), (34, 30, 52), planks=False)
    cv.fill([(1060, 182), (W, 182), (W, 520), (1060, 520)], (92, 98, 124), ink=None, alpha=110)                                                           # light from the room
    for i in range(5):                                                                                                                                    # dust bunnies and a lost sock
        cv.ellipse(120 + i * 210, 526, 26, 8, (60, 56, 78), ink=None, alpha=140)
    cv.fill(spline([(300, 580), (342, 566), (376, 574), (364, 598), (320, 602)], closed=True, n=3), (150, 90, 110), ink=INK, lw=1.8)


def bg_pup_table(cv, t=0.0, **kw):
    """Under the dinner table: legs of the table and chairs, four pairs of feet, crumbs."""
    band(cv, 0, 470, (250, 226, 190), (244, 210, 170), n=8, x0=0, x1=W)
    _floor(cv, 470, (206, 160, 116))
    cv.fill([(0, 0), (W, 0), (W, 120), (0, 120)], (252, 246, 236), ink=None)                                                                              # table cloth
    for i in range(14):
        cv.fill([(i * 100, 120), (i * 100 + 100, 120), (i * 100 + 50, 150)], (232, 120, 120) if i % 2 else (252, 246, 236), ink=INK, lw=1.8)
    for xx in (60, 1220):
        rect(cv, xx - 20, 150, xx + 20, 600, (172, 120, 82), lw=2.6)
    for k, (xx, col) in enumerate(((330, (232, 170, 130)), (520, (232, 170, 130)), (780, (210, 150, 120)), (960, (214, 156, 124)))):
        cv.fill(spline([(xx - 26, 150), (xx + 26, 150), (xx + 24, 440), (xx + 36, 500), (xx + 34, 548), (xx - 36, 548), (xx - 34, 500), (xx - 24, 440)], closed=True, n=3), col, ink=INK, lw=2.4)
        cv.ellipse(xx, 552, 44, 12, (92, 70, 82) if k % 2 else (130, 90, 100), ink=INK, lw=2.0)
        cv.fill([(xx - 20, 300), (xx + 20, 300), (xx + 22, 342), (xx - 22, 342)], (110, 130, 200) if k % 2 == 0 else (250, 226, 120), ink=None, alpha=210)   # trouser / skirt hem
    for i in range(7):
        cv.ellipse(190 + i * 150, 590 + (i % 2) * 16, 6, 4, (190, 140, 90), ink=None)                                                                      # crumbs


def bg_pup_night(cv, t=0.0, **kw):
    """Night: bluish room, a big window with the moon, the bed with mom sleeping, the dog's spot at the foot."""
    band(cv, 0, 470, (34, 40, 84), (52, 58, 108), n=8, x0=0, x1=W)
    _floor(cv, 470, (66, 58, 90))
    _window(cv, 860, 60, 1160, 300, (24, 34, 74), (50, 60, 112))
    cv.ellipse(1050, 130, 34, 34, (255, 246, 210), ink=None)
    cv.ellipse(1050, 130, 70, 70, (255, 246, 210), ink=None, alpha=44)
    for i, (sx, sy) in enumerate(((900, 100), (960, 220), (1100, 80), (1010, 240), (930, 160))):
        cv.ellipse(sx, sy, 2.6, 2.6, (255, 255, 240), ink=None, alpha=200 if (int(t * 2) + i) % 3 else 120)
    rrect(cv, 40, 330, 820, 560, 26, (150, 100, 130), lw=3.0)
    rrect(cv, 40, 300, 820, 380, 26, (196, 190, 220), lw=3.0)
    rrect(cv, 70, 276, 270, 346, 22, (226, 224, 244), lw=2.6)
    cv.fill(spline([(180, 340), (240, 270), (380, 252), (520, 292), (600, 340)], closed=True, n=3), (174, 108, 140), ink=INK, lw=2.6)                    # mom, a lump
    cv.ellipse(150, 300, 36, 30, (210, 170, 140), ink=INK, lw=2.4)
    cv.fill(spline([(118, 296), (150, 262), (190, 286), (182, 322), (126, 326)], closed=True, n=3), (40, 28, 34), ink=INK, lw=2.0)                          # her hair


def bg_pup_soi(cv, t=0.0, **kw):
    """The soi at dusk right after the rain: wet road, puddles, a street lamp, our house with the lit window on the right."""
    band(cv, 0, 360, (84, 74, 124), (250, 170, 120), n=10, x0=0, x1=W)
    for i, (hx, hw, hh) in enumerate(((60, 210, 250), (300, 170, 200), (500, 210, 280), (760, 160, 220))):
        cv.fill([(hx, 470 - hh), (hx + hw, 470 - hh), (hx + hw, 470), (hx, 470)], mix((90, 80, 120), (60, 56, 96), (i % 2) * 0.6), ink=INK, lw=2.4)
        for r in range(int(hh / 70)):
            for c in range(int(hw / 70)):
                if (r + c + i) % 3:
                    rect(cv, hx + 16 + c * 60, 470 - hh + 20 + r * 60, hx + 46 + c * 60, 470 - hh + 50 + r * 60, (255, 214, 130), ink=None)
    cv.fill([(0, 470), (W, 470), (W, H), (0, H)], (96, 100, 124), ink=None)
    for px, pw in ((200, 150), (520, 220), (860, 140)):
        cv.ellipse(px, 600, pw, 22, (190, 206, 232), ink=None, alpha=120)
    cv.stroke([(120, 470), (120, 190)], (60, 60, 76), 8)
    cv.ellipse(120, 182, 20, 20, (255, 238, 160), ink=INK, lw=2.4)
    cv.ellipse(120, 182, 70, 70, (255, 238, 160), ink=None, alpha=48)
    rrect(cv, 960, 150, 1260, 470, 10, (232, 196, 150), lw=3.0)                                                                                           # our house
    rect(cv, 1000, 200, 1090, 290, (255, 226, 140), lw=2.6)
    rect(cv, 1140, 320, 1230, 470, (178, 124, 84), lw=2.6)
    cv.fill([(900, 150), (1110, 90), (1320, 150)], (190, 86, 80), ink=INK, lw=2.8)


# ------------------------------------------------------------------------------------------------------------------------------------------------- registry
FP.REG_PROP.update(dog=dog, unicorn=unicorn, bowl=bowl, ball=ball, snack=snack, cabinet=cabinet, shirt=shirt, clock=clock, rain=rain, bolt=bolt, phone_glow=phone_glow, bike=bike,
                   zzz=zzz, sun_beam=sun_beam, hand=hand)
FP.REG_BG.update(pup_bedroom=bg_pup_bedroom, pup_living=bg_pup_living, pup_rain=bg_pup_rain, pup_under_bed=bg_pup_under_bed, pup_table=bg_pup_table, pup_night=bg_pup_night,
                 pup_soi=bg_pup_soi)
