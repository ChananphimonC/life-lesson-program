"""Cast of the island story (ติดเกาะ 72 ชั่วโมง): ten students that stand for ten well-known Thai universities, the ferry captain, built on the same approved rig as the red-thread cast
(nothing in prototype_v2 is edited). Everybody wears the common student base (white shirt + dark bottom, small pin) from uni_chars; the university shows in the accent colour
(scarf / headband / cap), the hair, the skin and a prop. Faces and hair are cartoon designs, not real people. See island_72/CAST_ART.md.
"""
from __future__ import annotations

import math

import uni_chars  # noqa: F401  (installs the uniform wrapper and the base cast)
from uni_chars import _female_body, _male_body, head_from, _p3, WHITE
import poc_chars
from poc_chars import Pinlike
from cast import MOM, PIN, feature
from toon import INK, mix, spline
import figure

# accent colours (approximate; see CAST_ART.md)
ACC = dict(chula=(232, 106, 154), thamma=(242, 194, 48), mahidol=(31, 60, 136), kaset=(46, 155, 74), kmitl=(242, 140, 40), kmutt=(245, 166, 35),
           silpa=(15, 138, 107), cmu=(123, 63, 160), kku=(181, 71, 46), psu=(47, 111, 208), captain=(27, 58, 140))
ACC2 = dict(thamma=(200, 32, 47), kmitl=(252, 252, 252), kmutt=(247, 201, 72), captain=(212, 168, 42))


def _line(cv, c, th, pts, col, w, ink_w=None):
    ps = []
    for x, y in pts:
        p, f = feature(c, x, y, th)
        if p is None or f < 0.18:
            if len(ps) > 1:
                break
            continue
        ps.append(p)
    if len(ps) >= 2:
        sp = spline(ps, n=3)
        if ink_w:
            cv.stroke(sp, INK, ink_w)
        cv.stroke(sp, col, w)


def acc_bow(cv, c, th):
    """Chulalongkorn: a pink bow holding half of the hair."""
    p, f = feature(c, -8, -34, th)
    if p is None or f < 0.2:
        return
    x, y = p
    col = ACC["chula"]
    for s in (-1, 1):
        cv.fill(spline([(x, y), (x + s * 20, y - 14), (x + s * 34, y - 4), (x + s * 30, y + 14), (x + s * 14, y + 10)], closed=True, n=3), col, ink=INK, lw=2.2,
                shade_col=mix(col, (0, 0, 0), 0.2), depth=3)
    cv.ellipse(x, y, 7, 7, mix(col, (255, 255, 255), 0.25), ink=INK, lw=2.0)


def acc_headband(cv, c, th):
    """Thammasat: a yellow headband with a red stripe across the forehead."""
    pts = [(x, -30 + (x / 80.0) ** 2 * 30) for x in range(-78, 82, 13)]
    _line(cv, c, th, pts, ACC["thamma"], 9, ink_w=12)
    _line(cv, c, th, [(x, y + 1.0) for x, y in pts], ACC2["thamma"], 3)


def acc_undereye(cv, c, th):
    """Mahidol: tired shadows under the eyes (little sleep) + a tied-back hair band."""
    for sx in (-1, 1):
        p, f = feature(c, sx * 37, 44, th)
        if p is not None and f > 0.25:
            cv.ellipse(p[0], p[1], 15 * f, 5.5, (168, 140, 176), ink=None, alpha=150)
    p, f = feature(c, 74, -6, th)
    if p is not None and f > 0.2:
        cv.ellipse(p[0], p[1], 5, 9, ACC["mahidol"], ink=INK, lw=1.6)


def acc_leafcap(cv, c, th):
    """Kasetsart: a green cap with a leaf stuck in the side."""
    pts = [(x, -34 + (x / 80.0) ** 2 * 26) for x in range(-80, 84, 12)]
    _line(cv, c, th, pts, ACC["kaset"], 17, ink_w=21)
    p, f = feature(c, 54, -34, th)
    if p is not None and f > 0.2:
        x, y = p
        cv.fill(spline([(x, y), (x + 10, y - 22), (x + 26, y - 30), (x + 22, y - 10), (x + 8, y + 2)], closed=True, n=3), (96, 196, 96), ink=INK, lw=2.0)
        cv.stroke([(x + 2, y - 2), (x + 20, y - 24)], (40, 120, 60), 1.8)


def acc_squareglasses(cv, c, th):
    """KMITL: neat square-ish glasses on top (the rig's round ones stay, an extra bridge makes them look sharper)."""
    pass


def acc_paint(cv, c, th):
    """Silpakorn: smudges of paint on the cheek and nose."""
    for x, y, col, r in ((-44, 40, (46, 168, 128), 7), (-30, 52, (46, 168, 128), 4), (22, 26, (250, 210, 80), 4.5)):
        p, f = feature(c, x, y, th)
        if p is not None and f > 0.25:
            cv.ellipse(p[0], p[1], r * f, r * 0.7 * f, col, ink=None, alpha=215)


def acc_curlpuffs(cv, c, th):
    """Khon Kaen: two big curly puffs of hair either side of the head."""
    for sx in (-1, 1):
        p, f = feature(c, sx * 78, -4, th)
        if p is None or f < 0.2:
            continue
        for dx, dy, r in ((0, -8, 17), (sx * 11, 8, 15), (-sx * 4, 22, 12)):
            cv.ellipse(p[0] + dx * f, p[1] + dy, r, r, c["hair"], ink=INK, lw=2.2)


def acc_captain(cv, c, th):
    """Ferry captain: a navy cap with a gold badge and a grey moustache."""
    crown = []
    for x in range(-84, 88, 12):
        p, f = feature(c, x, -34 - 46 * math.sqrt(max(0.0, 1 - (x / 86.0) ** 2)), th)
        if p is None or f < 0.15:
            continue
        crown.append(p)
    base = []
    for x in range(84, -88, -12):
        p, f = feature(c, x, -30 + (x / 82.0) ** 2 * 22, th)
        if p is not None and f >= 0.15:
            base.append(p)
    if len(crown) > 3 and len(base) > 3:
        cv.fill(spline(crown + base, closed=True, n=2), mix(ACC["captain"], (255, 255, 255), 0.12), ink=INK, lw=2.6)
    pts = [(x, -36 + (x / 82.0) ** 2 * 24) for x in range(-82, 86, 12)]
    _line(cv, c, th, pts, ACC["captain"], 14, ink_w=18)
    p, f = feature(c, 0, -42, th)
    if p is not None and f > 0.2:
        cv.ellipse(p[0], p[1] - 4, 8, 8, ACC2["captain"], ink=INK, lw=1.6)
    m, f2 = feature(c, 0, c["nose_y"] + 12, th)
    if m is not None:
        w = 22 * (f2 if f2 else 1)
        cv.fill(spline([(m[0] - w, m[1] + 6), (m[0] - w * 0.4, m[1] - 3), (m[0], m[1]), (m[0] + w * 0.4, m[1] - 3), (m[0] + w, m[1] + 6), (m[0], m[1] + 9)], closed=True, n=3),
                (190, 190, 196), ink=INK, lw=1.6)


# ---------------------------------------------------------------------------------------------------------------- heads
CHULA = head_from(PIN, name="pin", style="long", skin=(252, 228, 214), cheek=(246, 150, 156), hair=(28, 22, 26), hair_hi=(96, 80, 90), glasses=None,
                  eye=dict(x=37, y=25, w=18, h=23, style="round"), brow=dict(y=-9, half=15, w=4.0, col=(46, 34, 34)),
                  fringe=[(-82, 36), (-62, 6), (-38, -14), (-10, -12), (14, -16), (42, -6), (64, 12), (82, 36)], notch=11, accessory=acc_bow)
THAMMA = head_from(PIN, name="pin", style="short", skin=(222, 176, 138), cheek=(232, 128, 108), hair=(34, 24, 22), hair_hi=(86, 66, 56), glasses=None,
                   eye=dict(x=38, y=26, w=15, h=17, style="round"), brow=dict(y=-12, half=18, w=9.0, col=(40, 28, 24)),
                   fringe=[(-78, 6), (-58, -20), (-34, -10), (-10, -30), (14, -14), (38, -32), (60, -14), (78, 6)], notch=7, accessory=acc_headband)
MAHIDOL = head_from(MOM, name="mom", style="bob", skin=(250, 236, 226), cheek=(240, 150, 150), hair=(32, 26, 36), hair_hi=(100, 86, 112), mole=None,
                    glasses=dict(r=25, col=(40, 60, 120)), brow=dict(y=6, half=16, w=4.6, col=(46, 34, 40)), accessory=acc_undereye)
KASET = head_from(PIN, name="pin", style="short", skin=(190, 142, 104), cheek=(214, 110, 90), hair=(26, 22, 20), hair_hi=(60, 52, 46), glasses=None,
                  eye=dict(x=38, y=26, w=15, h=17, style="round"), brow=dict(y=-10, half=17, w=7.5, col=(30, 24, 20)),
                  fringe=[(-78, 2), (-56, -14), (-30, -16), (0, -18), (30, -16), (56, -14), (78, 2)], notch=5, accessory=acc_leafcap)
KMITL = head_from(PIN, name="pin", style="short", skin=(248, 228, 208), cheek=(240, 150, 130), hair=(30, 28, 38), hair_hi=(80, 80, 98), glasses=dict(r=27, col=(36, 40, 56)),
                  eye=dict(x=37, y=26, w=14, h=16, style="round"), brow=dict(y=-8, half=15, w=5.0, col=(30, 28, 34)),
                  fringe=[(-76, 2), (-54, -16), (-26, -24), (4, -22), (34, -24), (58, -14), (76, 2)], notch=8)
KMUTT = head_from(PIN, name="pin", style="short", skin=(214, 168, 130), cheek=(230, 128, 106), hair=(40, 28, 22), hair_hi=(100, 74, 56), glasses=None,
                  eye=dict(x=38, y=26, w=15, h=17, style="round"), brow=dict(y=-10, half=17, w=7.0, col=(40, 28, 22)),
                  fringe=[(-80, 6), (-64, -16), (-46, -2), (-30, -26), (-12, -6), (6, -30), (24, -8), (44, -28), (62, -10), (80, 6)], notch=6)
SILPA = head_from(MOM, name="mom", style="bob", skin=(250, 230, 216), cheek=(244, 146, 140), hair=(40, 44, 78), hair_hi=(120, 226, 196), mole=None, glasses=None,
                  brow=dict(y=5, half=16, w=4.4, col=(60, 70, 66)), accessory=acc_paint)
CMU = head_from(PIN, name="pin", style="short", skin=(246, 222, 200), cheek=(240, 146, 128), hair=(78, 52, 38), hair_hi=(140, 104, 78), glasses=None,
                eye=dict(x=38, y=27, w=15, h=14, style="round"), brow=dict(y=-8, half=16, w=5.0, col=(70, 48, 36)),
                fringe=[(-82, 14), (-66, -10), (-48, 6), (-30, -22), (-8, -8), (12, -26), (34, -10), (54, -22), (70, -4), (82, 16)], notch=9)
KKU = head_from(MOM, name="mom", style="bun", skin=(206, 156, 118), cheek=(230, 112, 96), hair=(40, 26, 22), hair_hi=(110, 78, 62), mole=None, glasses=None,
                brow=dict(y=5, half=17, w=6.0, col=(46, 30, 26)), accessory=acc_curlpuffs)
PSU = head_from(PIN, name="pin", style="short", skin=(176, 126, 92), cheek=(208, 104, 84), hair=(116, 80, 50), hair_hi=(190, 150, 100), glasses=None,
                eye=dict(x=38, y=27, w=14, h=12, style="round"), brow=dict(y=-9, half=17, w=6.5, col=(90, 62, 40)),
                fringe=[(-78, 4), (-56, -18), (-32, -10), (-6, -24), (20, -12), (46, -22), (66, -10), (78, 4)], notch=7)
CAPTAIN = head_from(PIN, name="pin", style="short", skin=(204, 156, 118), cheek=(222, 126, 104), hair=(176, 176, 184), hair_hi=(222, 222, 230), glasses=None,
                    eye=dict(x=38, y=26, w=14, h=15, style="round"), brow=dict(y=-9, half=17, w=8.0, col=(170, 170, 180)),
                    fringe=[(-78, 6), (-56, -12), (-30, -14), (0, -16), (30, -14), (56, -12), (78, 6)], notch=6, accessory=acc_captain)

HEADS = dict(chula=CHULA, thamma=THAMMA, mahidol=MAHIDOL, kaset=KASET, kmitl=KMITL, kmutt=KMUTT, silpa=SILPA, cmu=CMU, kku=KKU, psu=PSU, captain=CAPTAIN)
import cast  # noqa: E402
cast.CHARS.update(HEADS)

# ---------------------------------------------------------------------------------------------------------------- bodies (white student base; the captain wears a navy shirt)
_b = figure.BODY
_b["chula"] = _female_body(0.90, 0.90)
_b["thamma"] = _male_body((1.14, 1.10))
_b["mahidol"] = _female_body(0.92, 0.92)
_b["kaset"] = _male_body((1.18, 1.14))
_b["kmitl"] = _male_body((1.0, 0.94))
_b["kmutt"] = _male_body((1.12, 1.06))
_b["silpa"] = _female_body(0.84, 0.84)
_b["cmu"] = _male_body((1.0, 0.98))
_b["kku"] = _female_body(0.96, 0.96)
_b["psu"] = _male_body((1.2, 1.12))
_b["captain"] = _male_body((1.22, 1.2), top=(238, 240, 248), top_dark=(204, 210, 226), bottom=(34, 48, 96), cuff=(34, 48, 96))
figure.ARM_LEN.update(chula=(52.0, 50.0), thamma=(58.0, 56.0), mahidol=(52.0, 50.0), kaset=(60.0, 58.0), kmitl=(58.0, 56.0), kmutt=(56.0, 54.0), silpa=(48.0, 46.0),
                      cmu=(56.0, 54.0), kku=(54.0, 52.0), psu=(60.0, 58.0), captain=(58.0, 56.0))
FEMALE = {"chula", "mahidol", "silpa", "kku"}
for n in HEADS:
    uni_chars.UNI[n] = "female" if n in FEMALE else "male"
poc_chars.CID.update({n: (n if n in FEMALE else Pinlike(n)) for n in HEADS})
poc_chars.SCALE.update(chula=0.9, thamma=0.94, mahidol=0.9, kaset=0.96, kmitl=0.96, kmutt=0.88, silpa=0.8, cmu=0.94, kku=0.92, psu=0.98, captain=1.0)

# ---------------------------------------------------------------------------------------------------------------- the university accent on the body: a neck scarf + a short tail
_orig_overlay = uni_chars._uniform_overlay


def _scarf(cv, th, col, col2=None, kku=False):
    ring = [(-27, 100, 24), (-4, 108, 34), (4, 108, 34), (27, 100, 24), (31, 116, 28), (6, 124, 38), (-6, 124, 38), (-31, 116, 28)]
    cv.fill([_p3(p, th) for p in ring], col, ink=INK, lw=2.4, shade_col=mix(col, (0, 0, 0), 0.22), depth=3)
    tail = [(4, 118, 38), (24, 120, 36), (28, 166, 38), (14, 176, 39)]
    cv.fill([_p3(p, th) for p in tail], col, ink=INK, lw=2.2, shade_col=mix(col, (0, 0, 0), 0.22), depth=3)
    if col2:
        a, b = _p3((6, 150, 38), th), _p3((26, 152, 38), th)
        cv.stroke([a, b], col2, 3.0)


def _kku_cloth(cv, th):
    """A checked cloth (pha khao ma) over one shoulder and across the chest."""
    col, dark = ACC["kku"], (120, 40, 28)
    band = [(-38, 100, 22), (-10, 98, 32), (34, 188, 38), (6, 194, 40)]
    cv.fill([_p3(p, th) for p in band], col, ink=INK, lw=2.4, shade_col=dark, depth=3)
    for i in range(1, 4):
        u = i / 4
        a = _p3((-38 + 28 * u * 0.0 + (-10 + 38) * 0.0 + (-28 * (1 - u) - 10 * u * 0.0) * 0, 100 + 92 * u, 24 + 14 * u), th)
        b = _p3((-10 + 44 * u, 98 + 94 * u, 32 + 6 * u), th)
        cv.stroke([a, b], dark, 1.6)


def _overlay(cv, th, mode, gown=False, pin=True):
    _orig_overlay(cv, th, mode, gown=gown, pin=pin)
    name = uni_chars._name[0]
    if name in ("chula", "mahidol", "kmitl", "kmutt", "silpa", "cmu", "psu"):
        key = name
        _scarf(cv, th, ACC[key], ACC2.get(key))
    elif name == "kku":
        _kku_cloth(cv, th)
    elif name == "kaset":
        _scarf(cv, th, ACC["kaset"])
    elif name == "thamma":
        _scarf(cv, th, ACC["thamma"], ACC2["thamma"])
    elif name == "captain":
        _scarf(cv, th, ACC2["captain"])


uni_chars._uniform_overlay = _overlay
