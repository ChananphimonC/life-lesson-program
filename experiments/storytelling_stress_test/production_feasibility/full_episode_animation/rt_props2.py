"""More props for the red-thread story (v3): the activity-day things (water packs, shopping bags, cartons, tape, scissors, balloons) and the dry-noodle bowl with a sprig of coriander."""
from __future__ import annotations

import math

import engine  # noqa: F401
from rt_art import INK, mix, spline


def waterpack(cv, x, y, s=1.0):
    """A shrink-wrapped pack of six drinking-water bottles (two rows of three) with a carrying handle. (x, y) = bottom centre."""
    cv.push(x, y, scale=s)
    cv.fill(spline([(-52, -2), (-54, -70), (52, -70), (54, -2)], closed=True, n=3), (214, 236, 250), ink=INK, lw=2.4, shade_col=(176, 208, 232), depth=4)
    for r in range(2):
        for c in range(3):
            bx = -34 + c * 34
            by = -4 - r * 32
            cv.fill([(bx - 11, by), (bx + 11, by), (bx + 10, by - 24), (bx - 10, by - 24)], (170, 214, 244), ink=INK, lw=1.4)
            cv.fill([(bx - 6, by - 24), (bx + 6, by - 24), (bx + 5, by - 31), (bx - 5, by - 31)], (170, 214, 244), ink=INK, lw=1.2)
            cv.ellipse(bx, by - 33, 5.6, 3.4, (60, 130, 220), ink=INK, lw=1.2)
            cv.stroke([(bx - 5, by - 14), (bx + 5, by - 14)], (255, 255, 255), 2.0, alpha=190)
    cv.stroke(spline([(-26, -74), (-18, -92), (18, -92), (26, -74)], n=3), INK, 6)
    cv.stroke(spline([(-26, -74), (-18, -92), (18, -92), (26, -74)], n=3), (120, 190, 240), 3.2)
    cv.pop()


def water_pile(cv, x, y, layers=4, s=0.9):
    """A pile of water packs: `layers` rows of two packs side by side (bottom centre at (x, y))."""
    for r in range(layers):
        for c in (-1, 1):
            waterpack(cv, x + c * 54 * s, y - r * 72 * s, s)


def shop_bag(cv, x, y, s=1.0, col=(250, 214, 200)):
    """A paper shopping bag with a paper roll and pens poking out. (x, y) = bottom centre."""
    cv.push(x, y, scale=s)
    cv.fill([(-30, 0), (30, 0), (34, -64), (-34, -64)], col, ink=INK, lw=2.4, shade_col=mix(col, (0, 0, 0), 0.2), depth=4)
    cv.stroke([(-20, -64), (-20, -90)], (240, 230, 220), 4)
    cv.stroke([(20, -64), (20, -90)], (240, 230, 220), 4)
    cv.fill([(-22, -64), (-10, -64), (-8, -94), (-24, -94)], (252, 252, 252), ink=INK, lw=1.8)
    cv.stroke([(6, -64), (14, -98)], (240, 90, 110), 4)
    cv.stroke([(14, -64), (24, -96)], (90, 150, 230), 4)
    cv.ellipse(0, -30, 11, 11, (255, 244, 214), ink=INK, lw=1.6)
    cv.pop()


def carton(cv, x, y, s=1.0, w=96, h=64, col=(214, 170, 116)):
    """A cardboard box with a taped lid. (x, y) = bottom centre."""
    cv.push(x, y, scale=s)
    cv.fill([(-w / 2, 0), (w / 2, 0), (w / 2, -h), (-w / 2, -h)], col, ink=INK, lw=2.4, shade_col=mix(col, (0, 0, 0), 0.22), depth=5)
    cv.fill([(-w / 2, -h), (w / 2, -h), (w / 2 - 8, -h - 12), (-w / 2 + 8, -h - 12)], mix(col, (255, 255, 255), 0.2), ink=INK, lw=2.0)
    cv.fill([(-9, -h - 12), (9, -h - 12), (9, 0), (-9, 0)], (236, 214, 160), ink=None, alpha=200)
    cv.pop()


def tape_roll(cv, x, y, s=1.0):
    cv.ellipse(x, y, 17 * s, 17 * s, (244, 220, 120), ink=INK, lw=2.2)
    cv.ellipse(x, y, 8 * s, 8 * s, (255, 250, 236), ink=INK, lw=1.6)


def scissors(cv, x, y, s=1.0, rot=0.0):
    cv.push(x, y, scale=s, rot=rot)
    for d in (-10, 10):
        cv.stroke([(0, 0), (30, d)], INK, 7)
        cv.stroke([(0, 0), (30, d)], (214, 220, 228), 3.6)
    cv.ellipse(-8, -6, 8, 8, (240, 100, 100), ink=INK, lw=2.0)
    cv.ellipse(-8, 6, 8, 8, (240, 100, 100), ink=INK, lw=2.0)
    cv.pop()


def noodle_bowl(cv, x, y, s=1.0, t=0.0, steam=1.0, leaf=True):
    """A bowl of dry noodles (minced pork, green onion, chilli, a sprig of coriander). (x, y) = bottom centre."""
    cv.push(x, y, scale=s)
    cv.fill(spline([(-46, -34), (-40, -8), (-18, 0), (18, 0), (40, -8), (46, -34)], closed=True, n=3), (252, 250, 244), ink=INK, lw=2.6, shade_col=(214, 208, 198), depth=5)
    cv.stroke(spline([(-40, -20), (0, -10), (40, -20)], n=3), (90, 150, 214), 3.0)
    cv.ellipse(0, -34, 46, 12, (252, 250, 244), ink=INK, lw=2.4)
    cv.ellipse(0, -36, 40, 9, (236, 196, 120), ink=None)
    for k in range(9):
        cv.stroke(spline([(-34 + k * 8, -40), (-26 + k * 8, -34 + 4 * math.sin(k * 0.7)), (-20 + k * 8, -38)], n=2), (250, 224, 150), 3.0)
    for dx, col in ((-14, (160, 96, 70)), (4, (176, 110, 80)), (18, (150, 90, 64))):
        cv.ellipse(dx, -42, 8, 4.6, col, ink=None)
    for dx in (-24, 24, 8):
        cv.ellipse(dx, -44, 3, 2.2, (110, 190, 100), ink=None)
    cv.ellipse(-4, -46, 3.2, 2.2, (230, 70, 60), ink=None)
    if leaf:
        cv.stroke([(26, -44), (34, -52)], (80, 170, 90), 3)
        cv.ellipse(36, -54, 5, 4, (110, 200, 110), ink=None)
    if steam > 0:
        for q in range(3):
            u = (t * 0.5 + q / 3) % 1.0
            cv.stroke(spline([(-12 + 14 * q + 3 * math.sin(u * 9 + q), -50 - 44 * u), (-12 + 14 * q + 8 * math.sin(u * 7 + q), -66 - 44 * u),
                              (-12 + 14 * q + 3 * math.sin(u * 8 + q), -84 - 44 * u)], n=3), (255, 255, 255), 4, alpha=int(150 * steam * (1 - u)))
    cv.pop()


def sprig(cv, x, y, s=1.0, rot=0.0):
    """A sprig of coriander (the bit Ta picks out)."""
    cv.push(x, y, scale=s, rot=rot)
    cv.stroke([(0, 0), (0, -16)], (70, 160, 80), 3)
    for dx, dy in ((-7, -20), (0, -26), (7, -20)):
        cv.ellipse(dx, dy, 6, 5, (110, 200, 110), ink=INK, lw=1.2)
    cv.pop()


def balloon(cv, x, y, col, s=1.0, sway=0.0):
    cv.stroke(spline([(x, y + 34 * s), (x + sway, y + 90 * s), (x + sway * 0.4, y + 150 * s)], n=3), (150, 150, 160), 1.6)
    cv.ellipse(x, y, 22 * s, 28 * s, col, ink=INK, lw=2.2)
    cv.ellipse(x - 7 * s, y - 10 * s, 5 * s, 8 * s, (255, 255, 255), ink=None, alpha=150)
