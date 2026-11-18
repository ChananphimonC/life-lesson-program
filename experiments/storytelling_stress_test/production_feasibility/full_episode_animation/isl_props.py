"""Animals and props for the island story (all procedural, soft rounded cartoon shapes): macaque 'ประธาน', hermit crab, monitor lizard, hornbill, seagull, fish, sea turtle,
bats, fireflies, coconut, fish on a stick, campfire, bamboo raft with the big orange sail, ferry boat, signal mirror flash, net."""
from __future__ import annotations

import math

import engine  # noqa: F401
from props_future import *  # noqa: F401,F403
from toon import INK, mix, spline

FUR = (150, 108, 76)
FUR_SH = (112, 78, 54)
FACE = (232, 176, 150)


# ----------------------------------------------------------------------------------------------------------------- the monkey
def monkey(cv, x, y, s=1.0, pose="sit", t=0.0, flip=False, hold=None, mouth=False, seed=0.0):
    """The macaque 'ประธาน'. (x, y) = where its bottom sits on the ground. pose: sit | run | stand | arms_up | lean. hold = None | "bag" | "coconut" | "fish" | "seaweed"."""
    cv.push(x, y, scale=s, flip=flip)
    b = math.sin(t * 3 + seed) * 2
    tail_w = math.sin(t * 4 + seed) * 12
    if pose == "run":
        ph = t * 14 + seed
        cv.stroke(spline([(-24, -40), (-60, -50 + 8 * math.sin(ph)), (-84, -22 + 12 * math.sin(ph + 1)), (-96, -48)], n=3), FUR_SH, 7)
        body = [(-30, -26), (-34, -52), (-10, -66), (28, -62), (42, -40), (30, -22), (0, -16)]
        cv.fill(spline(body, closed=True, n=3), FUR, ink=INK, lw=2.6, shade_col=FUR_SH, depth=4)
        for sgn, off in ((1, 0), (-1, 1.7)):
            cv.stroke([(sgn * 14 - 10, -22), (sgn * 28 - 10 + 12 * math.sin(ph + off), -4 - 6 * abs(math.sin(ph + off)))], FUR_SH, 9)
            cv.stroke([(sgn * 14 + 22, -26), (sgn * 30 + 22 + 12 * math.sin(ph + off + 3), -4 - 6 * abs(math.sin(ph + off + 3)))], FUR_SH, 9)
        head = (48, -58)
    elif pose == "arms_up":
        cv.stroke(spline([(-22, -34), (-52, -30), (-70, -52 + tail_w * 0.4), (-62, -78)], n=3), FUR_SH, 7)
        cv.fill(spline([(-30, 0), (-34, -40), (-16, -66), (20, -64), (34, -38), (30, 0)], closed=True, n=3), FUR, ink=INK, lw=2.6, shade_col=FUR_SH, depth=4)
        cv.fill(spline([(-8, -22), (-6, -48), (14, -48), (18, -22)], closed=True, n=3), (206, 172, 140), ink=None)
        for sgn in (-1, 1):
            cv.stroke([(sgn * 26, -58), (sgn * 52, -88 + 4 * math.sin(t * 6))], FUR_SH, 8)
            cv.ellipse(sgn * 54, -92 + 4 * math.sin(t * 6), 7, 7, FUR_SH, ink=INK, lw=1.6)
        for sgn in (-1, 1):
            cv.fill(spline([(sgn * 10 - 6, 0), (sgn * 10 + 6, 0), (sgn * 16 + 8, -14), (sgn * 4 - 6, -14)], closed=True, n=2), FUR_SH, ink=INK, lw=1.8)
        head = (4, -78)
    else:                                                   # sit / stand / lean
        cv.stroke(spline([(-22, -26), (-60, -22), (-84, -40 + tail_w * 0.4), (-78, -74 + tail_w)], n=3), FUR_SH, 7)
        cv.fill(spline([(-32, 0), (-36, -38), (-18, -62 + b), (20, -62 + b), (36, -36), (32, 0)], closed=True, n=3), FUR, ink=INK, lw=2.6, shade_col=FUR_SH, depth=4)
        cv.fill(spline([(-10, -4), (-8, -40), (14, -40), (18, -4)], closed=True, n=3), (206, 172, 140), ink=None)
        for sgn in (-1, 1):
            cv.fill(spline([(sgn * 16 - 10, 2), (sgn * 16 + 12, 2), (sgn * 24 + 14, -16), (sgn * 8 - 10, -16)], closed=True, n=2), FUR_SH, ink=INK, lw=1.8)
        cv.stroke([(14, -48), (36, -30)], FUR_SH, 8)
        cv.stroke([(-14, -48), (-34, -26)], FUR_SH, 8)
        head = (4, -78 + b)
    hx, hy = head
    cv.ellipse(hx - 22, hy + 2, 8, 9, FACE, ink=INK, lw=1.8)             # ears
    cv.ellipse(hx + 22, hy + 2, 8, 9, FACE, ink=INK, lw=1.8)
    cv.ellipse(hx, hy, 26, 24, FUR, ink=INK, lw=2.6, shade_col=FUR_SH)
    cv.fill(spline([(hx - 18, hy + 2), (hx - 8, hy - 8), (hx, hy - 4), (hx + 8, hy - 8), (hx + 18, hy + 2), (hx + 14, hy + 20), (hx, hy + 24), (hx - 14, hy + 20)], closed=True, n=3), FACE, ink=INK, lw=1.8)
    for sgn in (-1, 1):
        cv.ellipse(hx + sgn * 8, hy + 1, 3.2, 4, (40, 30, 30), ink=None)
        cv.ellipse(hx + sgn * 8 + 1, hy - 0.5, 1.1, 1.1, (255, 255, 255), ink=None)
    cv.ellipse(hx, hy + 12, 5, 3.4, (60, 40, 40), ink=None)
    if mouth:
        cv.ellipse(hx, hy + 18, 5, 3.4, (120, 40, 50), ink=None)
    # cheeky brows (the "chairman" look)
    cv.stroke([(hx - 14, hy - 6), (hx - 3, hy - 7)], (60, 40, 32), 2.4)
    cv.stroke([(hx + 14, hy - 6), (hx + 3, hy - 7)], (60, 40, 32), 2.4)
    cv.stroke(spline([(hx - 6, hy + 17), (hx, hy + 20), (hx + 6, hy + 17)], n=2), (110, 60, 60), 1.8)
    if hold == "bag":
        rrect(cv, hx + 14, hy + 14, hx + 56, hy + 52, 8, (232, 120, 160), lw=2.4)
        cv.stroke([(hx + 24, hy + 14), (hx + 28, hy + 4), (hx + 44, hy + 4), (hx + 48, hy + 14)], (250, 220, 230), 3)
    elif hold == "coconut":
        cv.ellipse(hx + 26, hy + 30, 14, 14, (130, 94, 60), ink=INK, lw=2.2)
        for dx, dy in ((-4, -3), (4, -3), (0, 4)):
            cv.ellipse(hx + 26 + dx, hy + 30 + dy, 1.8, 1.8, (60, 40, 30), ink=None)
    elif hold == "fish":
        cv.fill(spline([(hx + 6, hy + 28), (hx + 30, hy + 20), (hx + 56, hy + 28), (hx + 70, hy + 20), (hx + 70, hy + 40), (hx + 56, hy + 32), (hx + 30, hy + 40)], closed=True, n=3),
                (200, 214, 226), ink=INK, lw=2.0)
    elif hold == "seaweed":
        cv.stroke(spline([(hx + 8, hy + 30), (hx + 28, hy + 20), (hx + 46, hy + 34), (hx + 62, hy + 24)], n=3), (60, 130, 80), 6)
    cv.pop()


# ----------------------------------------------------------------------------------------------------------------- small animals
def hermit_crab(cv, x, y, s=1.0, t=0.0, hide=0.0, flip=False):
    """A hermit crab with a swirly pink shell; hide = 1 pulls it into the shell."""
    cv.push(x, y, scale=s, flip=flip)
    hop = abs(math.sin(t * 6)) * 3 * (1 - hide)
    if hide < 0.9:
        for sgn in (-1, 1):
            cv.stroke([(sgn * 8, -6 - hop), (sgn * (22 + 8 * (1 - hide)), 2)], (232, 120, 90), 3)
        cv.ellipse(14, -10 - hop, 7, 6, (240, 140, 100), ink=INK, lw=1.6)
        cv.stroke([(16, -16 - hop), (18, -24 - hop)], (232, 120, 90), 2)
        cv.ellipse(18, -26 - hop, 2.4, 2.4, (30, 30, 30), ink=None)
    cv.fill(spline([(-18, 0), (-20, -22), (-6, -34 - hop), (10, -26), (12, 0)], closed=True, n=3), (246, 196, 214), ink=INK, lw=2.2, shade_col=(214, 150, 176), depth=3)
    cv.stroke(spline([(-6, -24 - hop), (2, -20), (-2, -12), (-10, -10), (-8, -4)], n=3), (214, 140, 170), 2)
    cv.pop()


def seagull(cv, x, y, s=1.0, t=0.0, seed=0.0):
    """A seagull in flight: a soft 'M' shape that flaps."""
    f = math.sin(t * 5 + seed)
    cv.push(x, y, scale=s)
    cv.stroke(spline([(-30, -4 + 12 * f), (-14, -14), (0, 0), (14, -14), (30, -4 + 12 * f)], n=3), INK, 4.4)
    cv.stroke(spline([(-30, -4 + 12 * f), (-14, -14), (0, 0), (14, -14), (30, -4 + 12 * f)], n=3), (252, 252, 254), 2.4)
    cv.pop()


def lizard(cv, x, y, s=1.0, t=0.0, flip=False, moving=True):
    """A monitor lizard (ตะกวด): long body, tail, four legs, forked tongue."""
    cv.push(x, y, scale=s, flip=flip)
    ph = t * 3.2 if moving else 0
    body_c, body_sh = (120, 126, 86), (88, 94, 62)
    cv.stroke(spline([(-70, -14), (-120, -10 + 5 * math.sin(ph)), (-170, -18 + 8 * math.sin(ph + 1)), (-220, -10)], n=4), body_sh, 12)
    cv.fill(spline([(-84, -4), (-90, -34), (-40, -44), (40, -42), (82, -30), (84, -6), (40, 0), (-40, 2)], closed=True, n=4), body_c, ink=INK, lw=2.6, shade_col=body_sh, depth=5)
    for i in range(6):
        cv.ellipse(-56 + i * 24, -30, 5, 3.4, (160, 164, 112), ink=None)
    for lx, off in ((-48, 0), (-52, 1.6), (40, 1.6), (36, 0)):
        sw = 6 * math.sin(ph + off)
        cv.stroke([(lx, -8), (lx + sw, 6)], body_sh, 8)
        cv.ellipse(lx + sw + 2, 8, 7, 3.4, body_sh, ink=INK, lw=1.4)
    cv.fill(spline([(78, -30), (108, -34), (126, -22), (112, -10), (80, -8)], closed=True, n=3), body_c, ink=INK, lw=2.4, shade_col=body_sh)
    cv.ellipse(106, -28, 3, 3.4, (30, 26, 20), ink=None)
    tong = abs(math.sin(t * 2)) * 14
    cv.stroke([(124, -18), (134 + tong, -18), (142 + tong, -22)], (226, 70, 90), 2.2)
    cv.stroke([(134 + tong, -18), (142 + tong, -14)], (226, 70, 90), 2.2)
    cv.pop()


def hornbill(cv, x, y, s=1.0, t=0.0, flip=False, seed=0.0):
    """An oriental pied hornbill gliding: black/white body, a big yellow bill."""
    f = math.sin(t * 5 + seed)
    cv.push(x, y, scale=s, flip=flip)
    cv.fill(spline([(-40, -4), (-18, -12 + 6 * f), (14, -28 + 16 * f), (6, -4), (-18, 2)], closed=True, n=3), (36, 36, 44), ink=INK, lw=2.2)
    cv.fill(spline([(-60, 8), (-30, -6), (22, -8), (46, -2), (40, 10), (-10, 18), (-56, 14)], closed=True, n=3), (40, 40, 48), ink=INK, lw=2.4, shade_col=(24, 24, 30))
    cv.fill(spline([(-4, 6), (24, 0), (44, 0), (38, 10), (10, 14)], closed=True, n=3), (250, 250, 252), ink=None)
    cv.fill(spline([(-82, 10), (-60, 4), (-56, 14)], closed=True, n=2), (250, 250, 252), ink=INK, lw=1.8)
    cv.fill(spline([(44, -4), (82, 0), (70, 10), (44, 8)], closed=True, n=3), (250, 200, 70), ink=INK, lw=2.2)
    cv.fill(spline([(52, -10), (72, -10), (82, 0), (50, -2)], closed=True, n=3), (232, 120, 50), ink=INK, lw=1.8)
    cv.ellipse(36, -2, 2.4, 2.4, (250, 250, 250), ink=INK, lw=1.0)
    cv.pop()


def fish(cv, x, y, s=1.0, t=0.0, col=(120, 190, 236), flip=False, seed=0.0, dead=False):
    cv.push(x, y, scale=s, flip=flip)
    w = 0.0 if dead else math.sin(t * 6 + seed) * 4
    cv.fill(spline([(-20, 0 + w), (-34, -14), (-30, 14)], closed=True, n=2), mix(col, (255, 255, 255), 0.2), ink=INK, lw=1.8)
    cv.fill(spline([(-22, 0), (-4, -14), (18, -10), (30, 0), (18, 10), (-4, 14)], closed=True, n=3), col, ink=INK, lw=2.0, shade_col=mix(col, (0, 0, 0), 0.2))
    cv.stroke(spline([(-6, -10), (-2, 0), (-6, 10)], n=2), mix(col, (255, 255, 255), 0.4), 1.6)
    cv.ellipse(20, -3, 2.4, 2.4, (30, 30, 36), ink=None)
    cv.pop()


def sea_turtle(cv, x, y, s=1.0, t=0.0, flip=False, swim=True):
    """A sea turtle from the side: oval shell with a pattern, flippers, a small head."""
    cv.push(x, y, scale=s, flip=flip)
    f = math.sin(t * 2.2) * (14 if swim else 4)
    cv.fill(spline([(20, 4), (60, 0 + f * 0.2), (84, -6), (78, 8)], closed=True, n=2), (112, 160, 96), ink=INK, lw=2.0)
    cv.fill(spline([(-48, 10), (-70, 8), (-50, -4)], closed=True, n=2), (112, 160, 96), ink=INK, lw=2.0)
    cv.fill(spline([(-52, -6), (-40, -34), (0, -46), (44, -36), (58, -4), (30, 8), (-20, 10)], closed=True, n=4), (120, 150, 80), ink=INK, lw=2.6, shade_col=(86, 114, 58), depth=5)
    for dx, dy in ((-24, -20), (0, -26), (24, -20), (-8, -8), (16, -8)):
        cv.ellipse(dx, dy, 11, 9, (156, 190, 106), ink=INK, lw=1.4)
    cv.fill(spline([(10, 4), (-6, 22 + f), (-30, 28 + f), (-14, 6)], closed=True, n=3), (112, 160, 96), ink=INK, lw=2.0)
    cv.fill(spline([(30, -8), (50, -30 - f), (82, -40 - f), (66, -16)], closed=True, n=3), (112, 160, 96), ink=INK, lw=2.0)
    cv.ellipse(84, -6, 14, 11, (122, 170, 102), ink=INK, lw=2.2)
    cv.ellipse(88, -9, 2.4, 2.4, (30, 30, 36), ink=None)
    cv.pop()


def bats(cv, t, n=10, y0=120, spread=800, x0=250, dark=1.0):
    """A stream of bats leaving the cave at dusk."""
    for i in range(n):
        u = (t * 0.12 + i / n) % 1.0
        x = x0 + u * spread
        y = y0 + 60 * math.sin(u * 5 + i) - 90 * u
        w = math.sin(t * 12 + i * 2)
        s = 0.7 + 0.5 * ((i * 37) % 10) / 10
        cv.push(x, y, scale=s)
        cv.stroke(spline([(-18, -2 + 7 * w), (-8, -8), (0, 0), (8, -8), (18, -2 + 7 * w)], n=3), (40, 30, 56), 4)
        cv.ellipse(0, 2, 4.4, 5, (50, 38, 66), ink=None)
        cv.pop()


def fireflies(cv, t, n=40, x0=0, x1=1280, y0=300, y1=620, glow=1.0):
    for i in range(n):
        px = x0 + (x1 - x0) * (((i * 0.6180339) + 0.05 * math.sin(t * 0.4 + i)) % 1.0)
        py = y0 + (y1 - y0) * (((i * 0.3819) + 0.05 * math.sin(t * 0.5 + i * 1.3)) % 1.0) + 10 * math.sin(t + i)
        a = max(0.0, math.sin(t * 2.6 + i * 1.9)) ** 2
        if a < 0.05:
            continue
        cv.ellipse(px, py, 11, 11, (210, 255, 120), ink=None, alpha=int(70 * a * glow))
        cv.ellipse(px, py, 3.2, 3.2, (246, 255, 180), ink=None, alpha=int(255 * a * glow))


# ----------------------------------------------------------------------------------------------------------------- props
def coconut(cv, x, y, s=1.0, cracked=0.0):
    cv.push(x, y, scale=s)
    cv.ellipse(0, -14, 15, 15, (126, 88, 56), ink=INK, lw=2.2, shade_col=(94, 64, 40))
    for dx, dy in ((-4, -17), (4, -17), (0, -10)):
        cv.ellipse(dx, dy, 1.8, 1.8, (50, 34, 24), ink=None)
    if cracked > 0:
        cv.stroke([(-10, -20), (-2, -14), (-8, -8), (2, -2)], (250, 240, 214), 2.2, alpha=int(255 * cracked))
    cv.pop()


def campfire(cv, x, y, t, s=1.0, size=1.0):
    """A bonfire with crossed logs, animated flames, sparks and a warm glow on the ground."""
    cv.ellipse(x, y - 10 * s, 190 * s * size, 74 * s * size, (255, 170, 80), ink=None, alpha=44)
    cv.ellipse(x, y - 10 * s, 110 * s * size, 42 * s * size, (255, 200, 110), ink=None, alpha=58)
    cv.push(x, y, scale=s)
    for sgn in (-1, 1):
        cv.stroke([(sgn * 46, 0), (-sgn * 28, -22)], INK, 15)
        cv.stroke([(sgn * 46, 0), (-sgn * 28, -22)], (122, 84, 56), 11)
    for j in range(4):
        w = 34 * size * (1 - j * 0.2)
        h = (90 + 20 * math.sin(t * 8 + j * 1.7)) * size * (1 - j * 0.15)
        sw = 7 * math.sin(t * 6 + j * 2.1)
        col = [(240, 100, 50), (250, 150, 50), (255, 206, 80), (255, 246, 190)][j]
        cv.fill(spline([(-w, -20), (-w * 0.7, -h * 0.5), (sw * 0.6, -h), (w * 0.7, -h * 0.45), (w, -20)], closed=True, n=4), col, ink=INK if j == 0 else None, lw=2.4)
    for i in range(7):
        u = (t * 0.7 + i / 7) % 1.0
        cv.ellipse(math.sin(i * 2.3 + t) * 36 * u, -50 - 150 * u * size, 2.4 * (1 - u) + 0.8, 2.4 * (1 - u) + 0.8, (255, 214, 120), ink=None, alpha=int(255 * (1 - u)))
    cv.pop()


def fish_on_stick(cv, x, y, s=1.0, ang=-30):
    cv.push(x, y, scale=s, rot=ang)
    cv.stroke([(-60, 0), (60, 0)], (126, 90, 60), 4)
    cv.fill(spline([(-24, 0), (-8, -12), (16, -9), (30, 0), (16, 9), (-8, 12)], closed=True, n=3), (206, 150, 96), ink=INK, lw=2.0)
    cv.stroke([(-6, -8), (-2, 0), (-6, 8)], (238, 190, 130), 1.6)
    cv.pop()


def net(cv, x, y, s=1.0, t=0.0, spread=1.0):
    """A cast net spreading in the air (a fan of mesh)."""
    cv.push(x, y, scale=s)
    r = 90 * spread
    for i in range(12):
        a = i / 12 * 2 * math.pi
        cv.stroke([(0, 0), (math.cos(a) * r, math.sin(a) * r * 0.55)], (232, 232, 224), 1.6, alpha=210)
    for k in (0.3, 0.55, 0.8, 1.0):
        pts = [(math.cos(i / 24 * 2 * math.pi) * r * k, math.sin(i / 24 * 2 * math.pi) * r * 0.55 * k) for i in range(25)]
        cv.stroke(pts, (232, 232, 224), 1.6, alpha=210)
    cv.pop()


def mirror_flash(cv, x, y, t, s=1.0, on=True):
    """A bright sun-glint star at (x, y) with rays (the signal mirror)."""
    if not on:
        return
    k = 0.6 + 0.4 * abs(math.sin(t * 9))
    cv.ellipse(x, y, 60 * s * k, 60 * s * k, (255, 255, 230), ink=None, alpha=90)
    for i in range(8):
        a = i * math.pi / 4 + t
        L = (60 if i % 2 == 0 else 34) * s * k
        cv.stroke([(x, y), (x + math.cos(a) * L, y + math.sin(a) * L)], (255, 255, 240), 3.2, alpha=230)
    cv.ellipse(x, y, 9 * s, 9 * s, (255, 255, 255), ink=None)


# ----------------------------------------------------------------------------------------------------------------- raft, sail, ferry
def sail(cv, x, y, w=250, h=330, t=0.0, wind=1.0, tear=0.0):
    """The big orange-red sail sewn from everybody's shirts, with a gold sun painted in the middle. (x, y) = foot of the mast."""
    cv.stroke([(x, y), (x, y - h - 30)], INK, 11)
    cv.stroke([(x, y), (x, y - h - 30)], (150, 106, 70), 7)
    bulge = 38 * wind
    sw = 9 * math.sin(t * 3)
    top, bot = y - h, y - 24
    poly = [(x + 6, top), (x + w * 0.5 + bulge * 0.5 + sw, top + h * 0.2), (x + w + sw, top + h * 0.5 + bulge * 0.3), (x + w * 0.9 + sw, bot - 10), (x + 6, bot)]
    cv.fill(spline(poly, closed=True, n=3), (236, 92, 54), ink=INK, lw=3.0, shade_col=(196, 60, 40), depth=6)
    cx, cy = x + w * 0.5 + sw * 0.6, top + h * 0.5
    cv.ellipse(cx, cy, 52, 52, (255, 214, 90), ink=INK, lw=2.4)
    for i in range(12):
        a = i * math.pi / 6 + t * 0.3
        cv.stroke([(cx + math.cos(a) * 62, cy + math.sin(a) * 62), (cx + math.cos(a) * 82, cy + math.sin(a) * 82)], (255, 214, 90), 5)
    for i in range(3):                                                 # seams where the shirts were sewn together
        yy = top + h * (0.25 + i * 0.25)
        cv.stroke(spline([(x + 10, yy), (x + w * 0.5 + sw, yy + 6 + bulge * 0.1), (x + w * 0.9 + sw, yy + 4)], n=3), (255, 244, 214), 1.8, alpha=150)
    if tear > 0:
        cv.fill([(x + w * 0.7, top + h * 0.3), (x + w * 0.95, top + h * 0.5), (x + w * 0.8, top + h * 0.56)], (200, 230, 250), ink=INK, lw=2.0, alpha=int(255 * tear))


def raft(cv, x, y, w=420, t=0.0, tilt=0.0, sail_on=True, wind=1.0, tear=0.0, building=1.0, rock=0.0):
    """A bamboo raft seen from the side with lashings, a mast and the sail. (x, y) = waterline centre. building 0..1 = how many logs are on."""
    cv.push(x, y + 6 * math.sin(t * 1.6) * rock, scale=1.0, rot=tilt + 3 * math.sin(t * 1.4) * rock, pivot=(0, 0))
    n = max(1, int(round(7 * building)))
    lw_ = w / 7
    for i in range(n):
        lx = -w / 2 + i * lw_
        cv.fill(spline([(lx, -22), (lx + lw_ - 4, -22), (lx + lw_ - 4, 8), (lx, 8)], closed=True, n=2), (214, 184, 108), ink=INK, lw=2.4, shade_col=(176, 146, 80), depth=3)
        cv.stroke([(lx + 2, -10), (lx + lw_ - 6, -10)], (240, 214, 140), 2.2, alpha=150)
    if building > 0.6:
        for bx in (-w / 2 + 40, w / 2 - 60):
            cv.fill([(bx, -24), (bx + 18, -24), (bx + 18, 12), (bx, 12)], (150, 106, 70), ink=INK, lw=2.0)
            for k in range(3):
                cv.stroke([(bx - 2, -18 + k * 12), (bx + 20, -14 + k * 12)], (96, 70, 44), 2.4)
    if sail_on and building > 0.9:
        sail(cv, -20, -22, w=min(260, w * 0.62), h=300, t=t, wind=wind, tear=tear)
    cv.pop()


def ferry(cv, x, y, s=1.0, t=0.0, flip=False, smoke=True):
    """A white two-deck ferry with a blue stripe, windows and a funnel. (x, y) = waterline centre."""
    cv.push(x, y + 3 * math.sin(t * 1.2), scale=s, flip=flip)
    cv.fill(spline([(-300, -40), (300, -40), (340, -64), (270, 0), (-250, 0)], closed=True, n=2), (250, 250, 252), ink=INK, lw=3.0, shade_col=(204, 212, 230), depth=6)
    cv.fill([(-296, -34), (310, -34), (320, -46), (-296, -46)], (40, 90, 170), ink=None)
    cv.fill([(-250, -40), (200, -40), (200, -120), (-250, -120)], (246, 246, 250), ink=INK, lw=3.0, shade_col=(206, 212, 230), depth=5)
    for i in range(8):
        cv.fill([(-232 + i * 56, -62), (-198 + i * 56, -62), (-198 + i * 56, -94), (-232 + i * 56, -94)], (168, 214, 244), ink=INK, lw=2.0)
    cv.fill([(-170, -120), (100, -120), (100, -176), (-170, -176)], (246, 246, 250), ink=INK, lw=3.0, shade_col=(206, 212, 230), depth=5)
    for i in range(4):
        cv.fill([(-154 + i * 62, -134), (-116 + i * 62, -134), (-116 + i * 62, -162), (-154 + i * 62, -162)], (168, 214, 244), ink=INK, lw=2.0)
    cv.fill([(-60, -176), (4, -176), (4, -232), (-60, -232)], (232, 80, 70), ink=INK, lw=3.0)
    cv.fill([(-60, -216), (4, -216), (4, -204), (-60, -204)], (255, 255, 255), ink=None)
    if smoke:
        for j in range(4):
            u = (t * 0.4 + j / 4) % 1.0
            cv.ellipse(-28 - 70 * u, -240 - 90 * u, 18 + 26 * u, 14 + 18 * u, (246, 246, 250), ink=None, alpha=int(180 * (1 - u)))
    cv.pop()


def wave_band(cv, y0, y1, t, col_a, col_b, amp=8, n=16, foam=True):
    """A band of sea with moving wave lines and a little foam, from y0 to the bottom edge y1."""
    band(cv, y0, y1, col_a, col_b, n=10, x0=0, x1=1280)
    for r in range(n):
        yy = y0 + (y1 - y0) * (r + 0.5) / n
        a = 0.35 + 0.65 * (r / n)
        pts = []
        for x in range(-20, 1320, 40):
            pts.append((x, yy + amp * a * math.sin(x * 0.012 + t * 1.2 + r * 1.3)))
        cv.stroke(spline(pts, n=2), mix(col_b, (255, 255, 255), 0.25), 1.4 + a * 1.6, alpha=int(120 * a))


# ----------------------------------------------------------------------------------------------------------------- extra small props
def dry_bag(cv, x, y, s=1.0, open_=0.0):
    """Chulalongkorn's waterproof bag (pink roll-top). (x, y) = bottom centre."""
    cv.push(x, y, scale=s)
    cv.fill(spline([(-30, 0), (-34, -50), (-24, -78), (24, -78), (34, -50), (30, 0)], closed=True, n=3), (236, 122, 164), ink=INK, lw=2.6, shade_col=(196, 84, 128), depth=4)
    cv.fill([(-26, -78), (26, -78), (24, -92 - 14 * open_), (-24, -92 - 14 * open_)], (250, 190, 212), ink=INK, lw=2.2)
    cv.stroke([(-20, -60), (20, -60)], (255, 232, 240), 2.4, alpha=170)
    cv.pop()


def plank(cv, x, y, s=1.0, ang=0.0, w=170, h=22):
    cv.push(x, y, scale=s, rot=ang)
    cv.fill([(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)], (196, 150, 104), ink=INK, lw=2.4, shade_col=(160, 118, 80), depth=3)
    cv.stroke([(-w / 2 + 10, -2), (w / 2 - 10, 2)], (166, 122, 84), 1.6)
    cv.pop()


def bamboo(cv, x, y, L=260, ang=-80, w=14, col=(206, 184, 104)):
    import math as _m
    a = _m.radians(ang)
    ex, ey = x + _m.cos(a) * L, y + _m.sin(a) * L
    cv.stroke([(x, y), (ex, ey)], INK, w + 4)
    cv.stroke([(x, y), (ex, ey)], col, w)
    for i in range(1, int(L / 60)):
        px, py = x + _m.cos(a) * i * 60, y + _m.sin(a) * i * 60
        cv.stroke([(px - _m.sin(a) * (w / 2 + 2), py + _m.cos(a) * (w / 2 + 2)), (px + _m.sin(a) * (w / 2 + 2), py - _m.cos(a) * (w / 2 + 2))], (140, 120, 60), 2.4)


def bowl_leaf(cv, x, y, s=1.0, food=True):
    """A coconut-shell bowl with a bit of food on a banana leaf."""
    cv.push(x, y, scale=s)
    cv.fill(spline([(-34, 0), (-44, -10), (0, -18), (44, -10), (34, 0)], closed=True, n=3), (80, 170, 90), ink=INK, lw=2.0)
    cv.fill(spline([(-22, -8), (-16, -24), (16, -24), (22, -8)], closed=True, n=3), (126, 88, 56), ink=INK, lw=2.2)
    if food:
        cv.ellipse(0, -24, 16, 6, (240, 190, 100), ink=None)
        cv.ellipse(-6, -28, 6, 4, (110, 190, 100), ink=None)
    cv.pop()


def sun_glint(cv, x, y, t, s=1.0):
    mirror_flash(cv, x, y, t, s)
