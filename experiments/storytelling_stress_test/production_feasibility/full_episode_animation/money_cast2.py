"""A new cast for the money stories (no school uniforms, nothing reused from the red-thread / island casts): everyday clothes, each with a design of their own.

  tang   (ตังค์)  broke 24-year-old: mustard hoodie, messy hair, tired eyes + stubble, backpack straps
  beam   (บีม)   TikTok-brainwashed best friend: teal hoodie, red snapback, headphones round the neck, huge cheeks
  nun    (พี่นุ่น) the bank cousin: deep-teal dress, high bun with a pencil stuck in it, gold hoops, staff lanyard, dry stare
  coach  (โค้ชทอง) get-rich-quick coach: gold blazer, slicked hair, sunglasses, big gold chain

Built on the same approved rig (prototype_v2 untouched). Hoodie men use the rig's own hoodie garment; nun the rig's dress garment.
"""
from __future__ import annotations

import math

import isl_chars  # noqa: F401  (keeps the overlay chain)
import uni_chars
import poc_chars
import figure
import cast
from uni_chars import head_from, _p3
from poc_chars import Pinlike, _scale_body
from cast import MOM, PIN, feature as _feature
from toon import INK, mix, spline

def feature(c, x, y, th):
    try:
        return _feature(c, x, y, th)
    except (ZeroDivisionError, ValueError):
        return None, 0


HOODIE_MEN = {"tang", "beam"}
_b = figure.BODY


def _dots(cv, c, th, pts, col, r=1.8, a=170):
    for x, y in pts:
        p, f = feature(c, x, y, th)
        if p is not None and f > 0.25:
            cv.ellipse(p[0], p[1], r * f, r * f, col, ink=None, alpha=a)


def acc_tang(cv, c, th):
    """Dark eye bags, stubble dots, a cowlick."""
    for sx in (-1, 1):
        p, f = feature(c, sx * 37, 45, th)
        if p is not None and f > 0.25:
            cv.ellipse(p[0], p[1], 16 * f, 5.5, (150, 118, 140), ink=None, alpha=170)
    _dots(cv, c, th, [(x, y) for x in (-30, -18, -6, 6, 18, 30) for y in (70, 80)], (90, 70, 66))
    p, f = feature(c, 6, -44, th)
    if p is not None and f > 0.2:
        cv.stroke(spline([(p[0], p[1] + 6), (p[0] + 4, p[1] - 16), (p[0] + 16, p[1] - 22)], n=3), c["hair"], 7)


def acc_beam(cv, c, th):
    """A red snapback cap (brim to the front) and huge round cheeks."""
    pts = []
    for x in range(-82, 86, 12):
        p, f = feature(c, x, -34 + (x / 82.0) ** 2 * 26, th)
        if p is not None and f > 0.15:
            pts.append(p)
    if len(pts) > 3:
        cv.stroke(spline(pts, n=3), INK, 24)
        cv.stroke(spline(pts, n=3), (214, 52, 60), 18)
        cv.stroke(spline([(px, py - 7) for px, py in pts], n=3), (240, 110, 110), 4, alpha=170)
    b, f = feature(c, 0, -34, th)
    if b is not None and f > 0.2:
        cv.fill(spline([(b[0] - 40 * f, b[1] + 6), (b[0], b[1] + 22), (b[0] + 40 * f, b[1] + 6), (b[0] + 30 * f, b[1] - 2), (b[0] - 30 * f, b[1] - 2)], closed=True, n=3), (170, 30, 40), ink=INK, lw=2.2)
    for sx in (-1, 1):
        p, f2 = feature(c, sx * 56, 46, th)
        if p is not None and f2 > 0.25:
            cv.ellipse(p[0], p[1], 15 * f2, 11 * f2, (250, 140, 130), ink=None, alpha=120)


def acc_nun(cv, c, th):
    """A pencil stuck through the bun and gold hoop earrings."""
    p, f = feature(c, -62, -40, th)
    if p is not None and f > 0.2:
        cv.stroke([(p[0] - 36, p[1] + 10), (p[0] + 40, p[1] - 22)], INK, 9)
        cv.stroke([(p[0] - 36, p[1] + 10), (p[0] + 40, p[1] - 22)], (250, 206, 70), 5.5)
        cv.ellipse(p[0] + 41, p[1] - 22, 4.6, 4.6, (240, 130, 140), ink=INK, lw=1.4)
    for sx in (-1, 1):
        e, f2 = feature(c, sx * 78, 42, th)
        if e is not None and f2 > 0.2:
            cv.ellipse(e[0], e[1] + 12, 8 * f2, 11 * f2, (255, 214, 90), ink=INK, lw=2.0, alpha=0)
            cv.stroke(spline([(e[0] - 7 * f2, e[1] + 4), (e[0] - 10 * f2, e[1] + 16), (e[0], e[1] + 24), (e[0] + 10 * f2, e[1] + 16), (e[0] + 7 * f2, e[1] + 4)], n=3), (255, 206, 70), 3.4)


def acc_coach(cv, c, th):
    """Sunglasses and a shiny hair highlight."""
    for sx in (-1, 1):
        p, f = feature(c, sx * 37, 27, th)
        if p is None or f < 0.2:
            continue
        cv.ellipse(p[0], p[1], 22 * f, 15 * f, (20, 20, 30), ink=INK, lw=2.2)
        cv.ellipse(p[0] - 6 * f, p[1] - 5 * f, 6 * f, 3 * f, (255, 255, 255), ink=None, alpha=220)
    a, fa = feature(c, -16, 24, th)
    b, fb = feature(c, 16, 24, th)
    if a is not None and b is not None and fa > 0.3 and fb > 0.3:
        cv.stroke([a, b], INK, 3.0)
    for k in range(3):
        h, fh = feature(c, -30 + 30 * k, -32, th)
        if h is not None and fh > 0.2:
            cv.stroke([(h[0] - 10, h[1] + 4), (h[0] + 10, h[1] - 4)], (255, 255, 255), 3, alpha=150)


def _butterfly(cv, x, y, f, col, rot=0.0):
    for sx in (-1, 1):
        cv.fill(spline([(x, y), (x + sx * 13 * f, y - 10 * f), (x + sx * 17 * f, y + 2 * f), (x + sx * 6 * f, y + 7 * f)], closed=True, n=2), col, ink=INK, lw=1.6)
    cv.ellipse(x, y, 2.2 * f, 4 * f, INK, ink=None)


def acc_jin(cv, c, th):
    """Two butterfly clips in a lavender bob, a heart sticker under one eye, gold hoops."""
    for k, (hx, hy) in enumerate(((-52, -20), (58, -26))):
        p, f = feature(c, hx, hy, th)
        if p is not None and f > 0.25:
            _butterfly(cv, p[0], p[1], f * 1.1, (255, 214, 90) if k == 0 else (130, 220, 230))
    p, f = feature(c, 50, 58, th)
    if p is not None and f > 0.3:
        cv.fill(spline([(p[0], p[1] + 7 * f), (p[0] - 7 * f, p[1] - 1 * f), (p[0] - 3 * f, p[1] - 6 * f), (p[0], p[1] - 3 * f), (p[0] + 3 * f, p[1] - 6 * f), (p[0] + 7 * f, p[1] - 1 * f)], closed=True, n=2), (255, 120, 150), ink=None)
    for sx in (-1, 1):
        e, f2 = feature(c, sx * 78, 44, th)
        if e is not None and f2 > 0.2:
            cv.stroke(spline([(e[0] - 6 * f2, e[1] + 2), (e[0] - 9 * f2, e[1] + 13), (e[0], e[1] + 21), (e[0] + 9 * f2, e[1] + 13), (e[0] + 6 * f2, e[1] + 2)], n=3), (255, 206, 70), 3.2)


TANG = head_from(PIN, name="pin", style="short", skin=(226, 184, 148), cheek=(226, 132, 112), hair=(46, 34, 28), hair_hi=(100, 80, 66), glasses=None,
                 eye=dict(x=38, y=27, w=14, h=15, style="round"), brow=dict(y=-6, half=16, w=6.5, col=(40, 30, 26)),
                 fringe=[(-80, 6), (-62, -16), (-44, 2), (-26, -24), (-6, -8), (14, -28), (34, -6), (54, -22), (72, -4), (82, 8)], notch=7, accessory=acc_tang)
BEAM = head_from(PIN, name="pin", style="short", skin=(244, 208, 176), cheek=(246, 130, 120), hair=(26, 22, 22), hair_hi=(80, 70, 70), glasses=None,
                 eye=dict(x=38, y=26, w=16, h=18, style="round"), brow=dict(y=-12, half=17, w=8.0, col=(30, 24, 24)),
                 fringe=[(-78, 2), (-56, -14), (-30, -16), (0, -18), (30, -16), (56, -14), (78, 2)], notch=5, accessory=acc_beam)
NUN = head_from(MOM, name="mom", style="bun", skin=(204, 156, 122), cheek=(226, 120, 104), hair=(30, 22, 24), hair_hi=(96, 76, 72), mole=(40, 62), glasses=None,
                brow=dict(y=2, half=18, w=5.0, col=(36, 26, 24)), accessory=acc_nun)
COACH = head_from(PIN, name="pin", style="short", skin=(238, 196, 160), cheek=(236, 140, 118), hair=(20, 18, 24), hair_hi=(120, 116, 140), glasses=None,
                  eye=dict(x=38, y=26, w=15, h=17, style="round"), brow=dict(y=-13, half=18, w=8.5, col=(26, 22, 22)),
                  fringe=[(-78, 8), (-58, -22), (-30, -34), (0, -38), (30, -34), (58, -22), (78, 8)], notch=6, accessory=acc_coach)
JIN = head_from(MOM, name="mom", style="bob", skin=(250, 214, 190), cheek=(248, 132, 140), hair=(188, 142, 214), hair_hi=(236, 206, 250), mole=None, glasses=None,
                eye=dict(x=37, y=27, w=17, h=20, style="round"), brow=dict(y=3, half=16, w=5.0, col=(120, 76, 130)), accessory=acc_jin)
cast.CHARS.update(tang=TANG, beam=BEAM, nun=NUN, coach=COACH, jin=JIN)

# bodies: hoodies for the two friends, the rig's dress for nun, a gold blazer on the male base for the coach
_b["tang"] = dict(_scale_body(_b["pin"], 1.02, 1.0), top=(238, 160, 50), top_dark=(204, 124, 30), cuff=(214, 134, 36), bottom=(70, 92, 140), shoe=(240, 240, 244), sole=(190, 190, 200))
_b["beam"] = dict(_scale_body(_b["pin"], 1.14, 1.08), top=(56, 170, 196), top_dark=(36, 130, 160), cuff=(40, 140, 168), bottom=(48, 52, 70), shoe=(250, 210, 60), sole=(200, 200, 208))
_b["nun"] = dict(_scale_body(_b["mom"], 0.98, 0.98), top=(34, 112, 122), top_dark=(22, 82, 92), cuff=(250, 236, 214), bottom=(34, 112, 122), shoe=(60, 40, 40), sole=(200, 190, 180))
_b["jin"] = dict(_scale_body(_b["mom"], 0.96, 0.98), top=(246, 124, 118), top_dark=(214, 90, 92), cuff=(255, 246, 232), bottom=(246, 124, 118), shoe=(250, 250, 252), sole=(200, 196, 214))
_b["coach"] = dict(_scale_body(_b["pin"], 1.2, 1.1), top=(240, 190, 60), top_dark=(204, 150, 30), cuff=(240, 190, 60), bottom=(30, 30, 38), shoe=(28, 28, 36), sole=(210, 200, 190))
figure.ARM_LEN.update(tang=(56.0, 54.0), beam=(60.0, 58.0), nun=(52.0, 50.0), coach=(60.0, 58.0), jin=(52.0, 50.0))
uni_chars.UNI["coach"] = "male"                          # the blazer is drawn with the shirt-collar overlay branch (no hood); the gold top colour makes it a blazer
uni_chars.NO_PIN.add("coach")
poc_chars.CID.update(tang=Pinlike("tang"), beam=Pinlike("beam"), nun="nun", coach=Pinlike("coach"), jin="jin")
poc_chars.SCALE.update(tang=0.92, beam=0.98, nun=0.9, coach=1.0, jin=0.9)

# hoodie men: hide the long-hair "locks" of the Pin rig exactly like the uniform wrapper does
_prev_figure = figure.figure


def _figure(cv, cid, th, pose="rest", expr="neutral", pregnant=False, lean=0.0, **kw):
    if str(cid) in HOODIE_MEN:
        poc_chars.NO_LOCKS = True
        try:
            return _prev_figure(cv, cid, th, pose, expr, pregnant, lean, **kw)
        finally:
            poc_chars.NO_LOCKS = False
    return _prev_figure(cv, cid, th, pose, expr, pregnant, lean, **kw)


figure.figure = _figure

# overlays: lanyard (nun), chain + white shirt (coach), headphones (beam), backpack straps (tang)
_prev_overlay = uni_chars._uniform_overlay


def _overlay(cv, th, mode, gown=False, pin=True):
    _prev_overlay(cv, th, mode, gown=gown, pin=pin)
    if uni_chars._name[0] == "coach":
        pts = [_p3(p, th) for p in ((-26, 104, 28), (-16, 140, 36), (0, 156, 38), (16, 140, 36), (26, 104, 28))]
        cv.stroke(spline(pts, n=3), INK, 7)
        cv.stroke(spline(pts, n=3), (255, 214, 70), 4)
        x, y = _p3((0, 158, 39), th)
        cv.ellipse(x, y, 7, 7, (255, 226, 110), ink=INK, lw=1.6)


uni_chars._uniform_overlay = _overlay
