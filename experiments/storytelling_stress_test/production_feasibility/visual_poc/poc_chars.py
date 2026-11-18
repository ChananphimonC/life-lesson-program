"""POC cast: re-skins of the APPROVED prototype_v2 rig for the four Story-2 characters.

IMPORTANT LIMITATION (stated in README/VISUAL_EVALUATION): the only approved designs are Pin and Mom. Ton, Grandma Kaew,
Uncle Chok and Aunt Uean have no approved design, so these four are provisional stand-ins built from the same rig
(head geometry, expressions, IK arms, hands, shading) with new parameters. They are NOT approved designs.

Nothing in prototype_v2 is edited. The additions are made in memory, only inside this process:
  * extra entries in cast.CHARS / figure.BODY / figure.ARM_LEN,
  * a wrapper around hair_back (short hair / bun need no back mass; the original is used otherwise),
  * a wrapper around head that draws small per-character accessories (headband, bun, moustache, wrinkles),
  * `Pinlike`, a str whose == "pin" is True, so the hoodie/jeans branch of figure() is used for Ton and Chok without
    editing figure.py (the rig has only two garment types: hoodie+jeans and dress+skirt).
"""
from __future__ import annotations

import copy
import math
import sys
from pathlib import Path

PROTO = Path(__file__).resolve().parents[3] / "prototype_v2"
sys.path.insert(0, str(PROTO))

import cast  # noqa: E402
import figure  # noqa: E402
from cast import MOM, PIN, feature, surf  # noqa: E402
from toon import INK, mix, shade, spline  # noqa: E402


class Pinlike(str):
    def __eq__(self, o):
        return o == "pin" or str.__eq__(self, o)

    __hash__ = str.__hash__


def _scale_body(b, kx=1.0, kz=1.0):
    b = copy.deepcopy(b)
    b["torso"] = [(y, a * kx, bb * kz, z0) for y, a, bb, z0 in b["torso"]]
    return b


# ---- accessories (drawn after the head, in head-local coordinates) ------------------------------------------------------------

def _band(cv, c, th, y, col, lw, lift=9):
    pts = []
    for phi in range(-95, 96, 10):
        p, v = surf(c, phi, y + 7 * (abs(phi) / 95) ** 2, th, lift=lift)
        if p is not None and v > 0.0:
            pts.append(p)
    if len(pts) > 2:
        cv.stroke(spline(pts, n=4), INK, lw + 3.2)
        cv.stroke(spline(pts, n=4), col, lw)
    return pts


def acc_chok(cv, c, th):
    pts = _band(cv, c, th, -44, (236, 236, 226), 11)
    if pts:                                                         # knot at the side
        x, y = pts[-1]
        cv.fill(spline([(x - 4, y - 4), (x + 12, y - 12), (x + 10, y + 8), (x - 2, y + 5)], closed=True, n=3), (236, 236, 226), lw=2.4)
    p, f = feature(c, 0, c["nose_y"] + 8, th)                        # grey moustache
    if p is not None and f > 0.3:
        w = 22 * f
        cv.fill(spline([(p[0] - w, p[1] + 4), (p[0] - w * 0.4, p[1] - 3), (p[0], p[1] - 1), (p[0] + w * 0.4, p[1] - 3),
                        (p[0] + w, p[1] + 4), (p[0] + w * 0.4, p[1] + 5), (p[0], p[1] + 2), (p[0] - w * 0.4, p[1] + 5)],
                       closed=True, n=3), (176, 176, 172), lw=1.8)
    for side in (-1, 1):                                             # crow's feet
        q, fq = feature(c, 50 * side, 22, th)
        if q is not None and fq > 0.3:
            for k in (-6, 0, 6):
                cv.stroke([(q[0] + side * 7, q[1] + k), (q[0] + side * 14 * fq, q[1] + k * 1.5)], mix(INK, c["skin"], 0.5), 1.6)


def acc_kaew(cv, c, th):
    s = math.sin(th)
    bx, by = -55 * s, -118
    cv.ellipse(bx, by, 32, 28, c["hair"], ink=INK, lw=3.0, shade_col=shade(c["hair"], 0.8))
    cv.stroke(spline([(bx - 20, by - 4), (bx, by + 6), (bx + 20, by - 4)], n=4), shade(c["hair"], 0.7), 1.8)
    cv.stroke(spline([(bx - 24, by + 14), (bx, by + 22), (bx + 24, by + 14)], n=4), (196, 120, 130), 3.2)
    for side in (-1, 1):                                             # smile lines and eye wrinkles
        q, fq = feature(c, 46 * side, 60, th)
        if q is not None and fq > 0.3:
            cv.stroke(spline([(q[0], q[1] - 6), (q[0] + side * 3, q[1] + 6), (q[0], q[1] + 16)], n=4), mix(INK, c["skin"], 0.55), 1.7)
        q, fq = feature(c, 55 * side, 30, th)
        if q is not None and fq > 0.3:
            for k in (-4, 4):
                cv.stroke([(q[0] + side * 5, q[1] + k), (q[0] + side * 12 * fq, q[1] + k * 1.6)], mix(INK, c["skin"], 0.5), 1.5)


def acc_uean(cv, c, th):
    pts = _band(cv, c, th, -40, (232, 84, 90), 11)
    for x, y in pts[::2]:
        cv.ellipse(x, y, 2.2, 2.2, (255, 244, 230))
    if pts:
        x, y = pts[0] if th > 0 else pts[-1]
        cv.fill(spline([(x, y - 2), (x - 16, y - 14), (x - 12, y + 4)], closed=True, n=3), (232, 84, 90), lw=2.4)


def acc_ton(cv, c, th):
    p, f = feature(c, 50, 52, th)                                   # a tooth-gap grin is drawn by the mouth; add a plaster
    if p is not None and f > 0.5:
        cv.fill(spline([(p[0] - 9, p[1] - 3), (p[0] + 9, p[1] - 8), (p[0] + 11, p[1] - 1), (p[0] - 7, p[1] + 4)], closed=True, n=2),
                (246, 214, 170), lw=1.6)


# ---- characters -----------------------------------------------------------------------------------------------------------------

def _jaw_scale(c, k):
    c["jaw"] = [(y, a * k, b * k, z) for y, a, b, z in c["jaw"]]
    return c


TON = dict(copy.deepcopy(PIN), name="pin", style="short", skin=(231, 190, 152), cheek=(236, 140, 120),
           hair=(36, 30, 30), hair_hi=(86, 76, 74), glasses=None, accessory=acc_ton,
           fringe=[(-74, -4), (-46, -20), (-16, -26), (14, -24), (44, -18), (72, -2)], notch=8,
           brow=dict(y=-10, half=15, w=6.5, col=(40, 30, 28)))
CHOK = _jaw_scale(dict(copy.deepcopy(PIN), name="pin", style="short", skin=(196, 150, 112), cheek=(214, 130, 104),
                       hair=(150, 150, 150), hair_hi=(200, 200, 200), glasses=None, accessory=acc_chok,
                       fringe=[(-70, 0), (-44, -14), (-14, -20), (14, -18), (44, -12), (70, 2)], notch=7,
                       eye=dict(x=37, y=26, w=14, h=16, style="round"),
                       brow=dict(y=-6, half=17, w=8.0, col=(120, 120, 120))), 1.06)
KAEW = dict(copy.deepcopy(MOM), name="mom", style="bun", skin=(236, 204, 176), cheek=(232, 150, 140),
            hair=(214, 214, 220), hair_hi=(250, 250, 255), accessory=acc_kaew, mole=None,
            glasses=dict(r=24, col=(150, 120, 90)),
            fringe=[(-62, 8), (-40, -6), (-14, -12), (12, -10), (36, 0), (58, 14)], notch=7,
            brow=dict(y=8, half=16, w=4.0, col=(150, 140, 140)))
UEAN = _jaw_scale(dict(copy.deepcopy(MOM), name="mom", style="bob", skin=(220, 172, 134), cheek=(232, 130, 110),
                       hair=(48, 36, 34), hair_hi=(100, 80, 74), accessory=acc_uean, mole=None,
                       brow=dict(y=8, half=16, w=7.0, col=(60, 44, 40))), 1.07)

cast.CHARS.update(ton=TON, chok=CHOK, kaew=KAEW, uean=UEAN)

_b = figure.BODY
_b["ton"] = dict(copy.deepcopy(_b["pin"]), top=(236, 122, 60), top_dark=(204, 96, 44), cuff=(220, 108, 54),
                 bottom=(66, 84, 120), shoe=(214, 70, 60), sole=(240, 230, 220))
_b["chok"] = dict(_scale_body(_b["pin"], 1.16, 1.12), top=(96, 128, 156), top_dark=(70, 100, 128), cuff=(80, 110, 138),
                  bottom=(132, 112, 84), shoe=(110, 84, 62), sole=(80, 60, 44))
_b["kaew"] = dict(_scale_body(_b["mom"], 0.92, 0.92), top=(160, 130, 184), top_dark=(132, 104, 158), cuff=(144, 114, 168),
                  bottom=(160, 130, 184), shoe=(120, 90, 70))
_b["uean"] = dict(_scale_body(_b["mom"], 1.14, 1.16), top=(236, 112, 100), top_dark=(204, 84, 76), cuff=(214, 96, 88),
                  bottom=(236, 112, 100), shoe=(90, 120, 150))
figure.ARM_LEN.update(ton=(52.0, 51.0), chok=(58.0, 55.0), kaew=(54.0, 52.0), uean=(57.0, 55.0))

CID = dict(ton=Pinlike("ton"), chok=Pinlike("chok"), kaew="kaew", uean="uean", pin=Pinlike("pin"), mom="mom")
SCALE = dict(ton=0.80, chok=1.0, kaew=0.90, uean=1.0, pin=0.9, mom=1.0)    # figure scale per character (child smaller)

_orig_hb, _orig_head = cast.hair_back, cast.head


def _hair_back(cv, c, th):
    if c.get("style") in ("short", "bun"):
        return
    return _orig_hb(cv, c, th)


def _face_pieces(pts):
    """The approved head fills its face skin as ONE polygon (hairline + far cheek + near cheek). At some turns the two cheek lines fold over each other and the even-odd fill
    then leaves thin hair-coloured bands across the face (they twitch as the body sways). Fill the same area as many small simple quads (one per row pair) instead,
    so a fold can only be painted twice, never left empty. Layout of the polygon: hairline points, then 49 far-cheek points, then the 49 near-cheek points reversed."""
    n = len(pts)
    if n < 100:
        return [pts]
    top, far, near = pts[:n - 98], pts[n - 98:n - 49], pts[n - 49:][::-1]
    pieces = [list(top) + [far[0], near[0]]]
    for i in range(len(far) - 1):                    # each quad overlaps its neighbours by 1.5 units, so no hairline gap can open between two of them
        pieces.append([(near[i][0], near[i][1] - 1.5), (far[i][0], far[i][1] - 1.5), (far[i + 1][0], far[i + 1][1] + 1.5), (near[i + 1][0], near[i + 1][1] + 1.5)])
    return pieces


def _head(cv, c, th, expr="neutral", talk=None, back=True, blink=0.0):
    skin = tuple(c["skin"][:3])
    plain_fill = cv.fill

    def fill(pts, col, *a, **k):
        if tuple(col[:3]) == skin and k.get("ink", 3) is None and not k.get("shade_col") and len(pts) > 100:
            for piece in _face_pieces(pts):
                plain_fill(piece, col, *a, **k)
            return None
        return plain_fill(pts, col, *a, **k)
    cv.fill = fill                                   # an instance attribute shadows the method for the duration of this head
    try:
        _orig_head(cv, c, th, expr, talk, back, blink)
    finally:
        del cv.fill
    if c.get("accessory"):
        c["accessory"](cv, c, th)


cast.hair_back = figure.hair_back = _hair_back
cast.head = figure.head = _head

# Pin's two long front locks are drawn by figure() for every "pin-like" body. Ton and Chok have short hair, so while
# NO_LOCKS is set the lock outline (tube with n=6 and a width function) and its 3-point highlight stroke are dropped.
NO_LOCKS = False
_tube, _spline = figure.tube, figure.spline


def _tube_w(pts, w, n=8):
    if NO_LOCKS and n == 6 and callable(w):
        return []
    return _tube(pts, w, n=n)


def _spline_w(pts, closed=False, n=10):
    if NO_LOCKS and n == 4 and len(pts) == 3 and not closed:
        return []
    return _spline(pts, closed=closed, n=n)


figure.tube, figure.spline = _tube_w, _spline_w


def ground(cid):
    return figure.BODY[cid]["ground"]


def draw(cv, who, x, feet_y, th_deg=0.0, pose="rest", expr="neutral", k=1.0, flip=False, lean=0.0, **kw):
    """Place a character with its feet at (x, feet_y) on the canvas. k multiplies the character's own scale."""
    global NO_LOCKS
    NO_LOCKS = who in ("ton", "chok")
    s = SCALE[who] * k
    cv.push(x, feet_y - ground(who) * s, scale=s, flip=flip)
    figure.figure(cv, CID[who], math.radians(th_deg), pose, expr, lean=lean, **kw)
    cv.pop()
    NO_LOCKS = False


if __name__ == "__main__":
    from toon import Canvas
    cv = Canvas(1800, 620, ss=3, bg=(250, 246, 238, 255))
    for i, who in enumerate(("ton", "kaew", "chok", "uean", "pin", "mom")):
        for j, (th, ex) in enumerate(((0, "neutral"), (38, "eager" if who == "ton" else "happy"))):
            draw(cv, who, 150 + i * 290 + j * 0, 560, th_deg=th, expr=ex, k=0.8 if j == 0 else 0.0001) if False else None
        draw(cv, who, 150 + i * 290, 560, th_deg=30, expr="happy", k=0.88)
    cv.result().save(Path(__file__).with_name("chars_sheet.png"))
    print("ok")
