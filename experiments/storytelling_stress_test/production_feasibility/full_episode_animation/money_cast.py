"""Extra cast for money stories: 'guru' (a get-rich-quick guru: sunglasses, dark suit, red tie) on the same rig. Imported after isl_chars so the uniform overlay chain stays intact."""
from __future__ import annotations

import isl_chars  # noqa: F401
import uni_chars
import poc_chars
import figure
import cast
from uni_chars import _male_body, head_from, _p3
from poc_chars import Pinlike
from cast import PIN, feature
from toon import INK, mix


def acc_shades(cv, c, th):
    """Dark sunglasses across the eyes with a glint."""
    for sx in (-1, 1):
        p, f = feature(c, sx * 37, 27, th)
        if p is None or f < 0.2:
            continue
        cv.ellipse(p[0], p[1], 21 * f, 15 * f, (24, 24, 34), ink=INK, lw=2.2)
        cv.ellipse(p[0] - 5 * f, p[1] - 5 * f, 5 * f, 3 * f, (255, 255, 255), ink=None, alpha=210)
    a, fa = feature(c, -16, 24, th)
    b, fb = feature(c, 16, 24, th)
    if a is not None and b is not None and fa > 0.3 and fb > 0.3:
        cv.stroke([a, b], INK, 3.0)


GURU = head_from(PIN, name="pin", style="short", skin=(226, 176, 136), cheek=(228, 130, 110), hair=(20, 18, 22), hair_hi=(70, 66, 76), glasses=None,
                 eye=dict(x=38, y=26, w=15, h=17, style="round"), brow=dict(y=-12, half=18, w=8.0, col=(30, 24, 24)),
                 fringe=[(-78, 6), (-56, -22), (-30, -30), (-6, -20), (16, -32), (40, -20), (62, -26), (78, 4)], notch=7, accessory=acc_shades)
cast.CHARS["guru"] = GURU
figure.BODY["guru"] = _male_body((1.14, 1.08), top=(40, 40, 52), top_dark=(26, 26, 36), cuff=(36, 36, 46), bottom=(36, 36, 46))
figure.ARM_LEN["guru"] = (58.0, 56.0)
uni_chars.UNI["guru"] = "male"
uni_chars.NO_PIN.add("guru")
poc_chars.CID["guru"] = Pinlike("guru")
poc_chars.SCALE["guru"] = 0.98

_prev_overlay = uni_chars._uniform_overlay


def _overlay(cv, th, mode, gown=False, pin=True):
    _prev_overlay(cv, th, mode, gown=gown, pin=pin)
    if uni_chars._name[0] == "guru":
        red = (214, 40, 56)
        cv.fill([_p3(p, th) for p in ((-6, 106, 34), (6, 106, 34), (9, 122, 37), (-9, 122, 37))], red, ink=INK, lw=2.0)
        cv.fill([_p3(p, th) for p in ((-9, 122, 37), (9, 122, 37), (13, 196, 38), (0, 206, 39), (-13, 196, 38))], red, ink=INK, lw=2.2, shade_col=(160, 24, 38), depth=3)


uni_chars._uniform_overlay = _overlay
