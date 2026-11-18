"""University students for the red-thread story (new faces on the approved prototype_v2 rig; nothing in prototype_v2 is edited).

Uniform as the user described it: women = white short-sleeved blouse with a collar + black skirt; men = white long-sleeved collared shirt + black trousers;
a small generic gold pin on the chest (NOT a real university emblem). The rig has only a hoodie and a dress garment, so in memory:
  * male uniform: the hoodie branch with the hood, pocket, strings and hem band switched off (figure.on_body / toon.lathe / figure.lathe_band wrappers),
    then a collar, placket and buttons drawn after the figure in the same transform;
  * female uniform: the dress branch with a shorter torso, a black skirt silhouette drawn over the lower torso and a black hem, plus the same collar overlay.
Each student gets a different head (skin, hair colour and style, brows, glasses, eyes, jaw) from the Pin / Mom heads, a body build and a name.
"""
from __future__ import annotations

import copy
import math

import engine  # noqa: F401  (sets the import paths)
import poc_chars  # noqa: F401  (registers the earlier cast and the wrappers)
from poc_chars import Pinlike, _scale_body, cast, figure
from cast import MOM, PIN, feature
from toon import INK, mix, shade, spline
import toon

WHITE = (250, 250, 252)
WHITE_SH = (212, 218, 230)
BLACK = (36, 36, 44)
BLACK_SH = (22, 22, 30)
GOLD = (236, 192, 70)

# ---------------------------------------------------------------------------------------------------------------- accessories


def acc_glasses_thick(cv, c, th):
    pass


def acc_beard(cv, c, th):
    """Yue Lao's long white beard (starts below the mouth so he can still speak) and a white moustache."""
    top, f = feature(c, 0, c["mouth_y"] + 10, th)
    if top is None:
        return
    x0, y0 = top
    cv.fill(spline([(x0 - 40, y0 - 4), (x0 - 34, y0 + 40), (x0 - 14, y0 + 100), (x0, y0 + 130), (x0 + 14, y0 + 100), (x0 + 34, y0 + 40), (x0 + 40, y0 - 4),
                    (x0 + 18, y0 + 8), (x0, y0 + 4), (x0 - 18, y0 + 8)], closed=True, n=4), (246, 246, 248), ink=INK, lw=2.6, shade_col=(214, 216, 226))
    for k in (-14, 0, 14):
        cv.stroke(spline([(x0 + k, y0 + 14), (x0 + k * 0.9, y0 + 56), (x0 + k * 0.6, y0 + 96)], n=4), (200, 202, 214), 1.6)
    m, _ = feature(c, 0, c["nose_y"] + 10, th)
    if m is not None:
        w = 24 * (f if f else 1)
        cv.fill(spline([(m[0] - w, m[1] + 5), (m[0] - w * 0.4, m[1] - 3), (m[0], m[1]), (m[0] + w * 0.4, m[1] - 3), (m[0] + w, m[1] + 5), (m[0], m[1] + 8)], closed=True, n=3),
                (246, 246, 248), ink=INK, lw=1.8)


HAIRPIN = set()                                  # names that wear the little gold hairpin right now (set by the scene)


def acc_hairpin(cv, c, th):
    """A gold hairpin with a small pink flower stuck in the hair above the ear (only while "bua" is in HAIRPIN)."""
    if "bua" not in HAIRPIN:
        return
    p, f = feature(c, 64, -22, th)
    if p is None or f < 0.2:
        return
    x, y = p
    cv.stroke([(x - 14, y + 30), (x + 10, y - 26)], INK, 6.0)
    cv.stroke([(x - 14, y + 30), (x + 10, y - 26)], (240, 200, 90), 3.6)
    cv.stroke([(x - 8, y + 18), (x + 6, y - 14)], (255, 244, 190), 1.4, alpha=200)
    for k in range(5):                                              # the flower
        a = k * 1.2566 + 0.3
        cv.ellipse(x + 10 + math.cos(a) * 7, y - 28 + math.sin(a) * 7, 5.4, 5.4, (250, 130, 160), ink=INK, lw=1.4)
    cv.ellipse(x + 10, y - 28, 3.6, 3.6, (255, 226, 120), ink=INK, lw=1.2)


def acc_fern(cv, c, th):
    pass


def _spiky(cv, c, th, col):
    pass


# ---------------------------------------------------------------------------------------------------------------- the cast
def head_from(base, **kw):
    h = copy.deepcopy(base)
    h.update(kw)
    return h


def _jaw(h, k):
    h["jaw"] = [(y, a * k, b * k, z) for y, a, b, z in h["jaw"]]
    return h


# male heads (hoodie branch: the head's own name must be "pin" so ears and the straight-hair rules match; style "short" drops the long back hair)
PHUM = head_from(PIN, name="pin", style="short", skin=(238, 200, 168), cheek=(238, 150, 130), hair=(30, 26, 30), hair_hi=(78, 70, 76),
                 glasses=dict(r=28, col=(60, 62, 76)), eye=dict(x=37, y=26, w=15, h=17, style="round"),
                 brow=dict(y=-8, half=15, w=5.5, col=(34, 28, 30)),
                 fringe=[(-78, 0), (-52, -18), (-22, -26), (8, -22), (38, -26), (62, -14), (78, 4)], notch=8)
KONG = _jaw(head_from(PIN, name="pin", style="short", skin=(208, 160, 120), cheek=(220, 130, 104), hair=(52, 34, 26), hair_hi=(110, 78, 56), glasses=None,
                      eye=dict(x=38, y=26, w=15, h=17, style="round"), brow=dict(y=-11, half=17, w=8.5, col=(44, 30, 24)),
                      fringe=[(-76, 6), (-58, -22), (-36, -34), (-12, -22), (10, -36), (34, -22), (58, -32), (76, 4)], notch=7), 1.06)
EM = _jaw(head_from(PIN, name="pin", style="short", skin=(228, 186, 150), cheek=(236, 134, 116), hair=(104, 66, 40), hair_hi=(170, 118, 80),
                    glasses=None, eye=dict(x=38, y=26, w=14, h=15, style="round"), brow=dict(y=-8, half=16, w=6.5, col=(30, 24, 24)),
                    fringe=[(-80, 4), (-60, -14), (-42, -2), (-22, -22), (0, -8), (20, -22), (42, -4), (62, -16), (80, 6)], notch=6), 1.12)
# female heads
BUA = head_from(PIN, name="pin", style="long", skin=(252, 226, 208), cheek=(246, 158, 150), hair=(36, 26, 28), hair_hi=(104, 80, 78), glasses=dict(r=27, col=(122, 74, 66)),
                eye=dict(x=37, y=25, w=17.5, h=22, style="round"), brow=dict(y=-9, half=15, w=4.5, col=(52, 38, 36)),
                fringe=[(-82, 34), (-64, 6), (-40, -10), (-12, -8), (14, -14), (40, -4), (62, 12), (82, 34)], notch=11, accessory=acc_hairpin)
MANAO = _jaw(head_from(MOM, name="mom", style="bob", skin=(242, 208, 184), cheek=(238, 140, 130), hair=(122, 74, 44), hair_hi=(190, 130, 84), mole=None,
                       glasses=dict(r=24, col=(190, 110, 120)), brow=dict(y=6, half=16, w=5.5, col=(100, 60, 40))), 1.0)
YUELAO = head_from(MOM, name="mom", style="bun", skin=(226, 186, 154), cheek=(226, 140, 124), hair=(244, 244, 248), hair_hi=(255, 255, 255), mole=None,
                   glasses=None, brow=dict(y=3, half=18, w=11.0, col=(236, 236, 242)),
                   fringe=[(-62, 8), (-40, -6), (-14, -12), (12, -10), (36, 0), (58, 14)], notch=7, accessory=acc_beard)



def acc_hijab(cv, c, th):
    """A soft headscarf: a ring around the face (outer wrap, opening for the face) that flows down over the neck and shoulders; folds radiate from under the chin."""
    top, f = feature(c, 0, 0, th)
    if top is None:
        return
    x0, y0 = top
    col, col_sh = c.get("scarf", (92, 150, 160)), c.get("scarf_sh", (64, 112, 124))
    outer = [(0, 176), (-60, 168), (-116, 130), (-126, 40), (-104, -44), (-52, -96), (0, -108), (52, -96), (104, -44), (126, 40), (116, 130), (60, 168)]
    inner = [(0, 104), (-40, 98), (-68, 70), (-78, 30), (-72, -14), (-48, -44), (0, -56), (48, -44), (72, -14), (78, 30), (68, 70), (40, 98)]
    o = spline([(x0 + x, y0 + y) for x, y in outer], closed=True, n=4)
    i = spline([(x0 + x, y0 + y) for x, y in inner], closed=True, n=4)
    ring = o + [o[0], i[0]] + i[::-1] + [i[0], o[0]]
    cv.fill(ring, col, ink=None, shade_col=col_sh, depth=6)
    cv.stroke(o, INK, 3.0, closed=True)
    cv.stroke(i, INK, 2.4, closed=True)
    for k in (-1, 1):                                                       # folds radiating from the chin
        cv.stroke(spline([(x0 + k * 14, y0 + 112), (x0 + k * 46, y0 + 138), (x0 + k * 84, y0 + 150)], n=3), mix(col, col_sh, 0.7), 2.4)
        cv.stroke(spline([(x0 + k * 56, y0 - 70), (x0 + k * 96, y0 - 22), (x0 + k * 104, y0 + 40)], n=3), mix(col, (255, 255, 255), 0.35), 2.6, alpha=170)


BAM = head_from(MOM, name="mom", style="bun", skin=(222, 178, 142), cheek=(232, 128, 114), hair=(40, 28, 26), hair_hi=(100, 76, 66), mole=(-26, 56),
                glasses=None, brow=dict(y=5, half=17, w=6.5, col=(50, 34, 30)))
JAKE = head_from(PIN, name="pin", style="short", skin=(250, 218, 196), cheek=(244, 150, 130), hair=(204, 160, 84), hair_hi=(236, 202, 130), glasses=None,
                 eye=dict(x=38, y=26, w=16, h=18, style="round"), brow=dict(y=-9, half=16, w=5.5, col=(150, 112, 62)),
                 fringe=[(-80, 2), (-58, -22), (-30, -12), (-6, -30), (20, -14), (46, -26), (66, -12), (80, 4)], notch=7)
FAA = head_from(PIN, name="pin", style="long", skin=(240, 206, 172), cheek=(244, 150, 140), hair=(26, 22, 26), hair_hi=(90, 76, 82), glasses=None,
                eye=dict(x=37, y=25, w=17, h=21, style="round"), brow=dict(y=-9, half=15, w=4.5, col=(40, 30, 30)),
                fringe=[(-82, 36), (-62, 4), (-38, -12), (-10, -10), (16, -16), (42, -6), (64, 10), (82, 36)], notch=11)
def acc_flower_clip(cv, c, th):
    """A small pink flower with a gold centre pinned beside the bun."""
    p, f = feature(c, -62, -40, th)
    if p is None or f < 0.2:
        return
    x, y = p
    for k in range(5):
        a = k * 1.2566 + 0.5
        cv.ellipse(x + math.cos(a) * 8, y + math.sin(a) * 8, 6.2, 6.2, (250, 146, 170), ink=INK, lw=1.5)
    cv.ellipse(x, y, 4.2, 4.2, (255, 226, 120), ink=INK, lw=1.3)


MARIAM = head_from(MOM, name="mom", style="bun", skin=(244, 212, 186), cheek=(240, 150, 140), hair=(46, 32, 30), hair_hi=(112, 84, 74), mole=None, glasses=None,
                   brow=dict(y=7, half=16, w=5.0, col=(52, 36, 30)), accessory=acc_flower_clip)
OMAR = _jaw(head_from(PIN, name="pin", style="short", skin=(214, 170, 132), cheek=(226, 132, 108), hair=(34, 26, 24), hair_hi=(82, 66, 56), glasses=None,
                      eye=dict(x=38, y=26, w=15, h=17, style="round"), brow=dict(y=-10, half=17, w=8.0, col=(36, 26, 22)),
                      fringe=[(-78, 4), (-56, -20), (-32, -16), (-8, -30), (18, -18), (44, -28), (64, -12), (78, 4)], notch=7), 1.04)

cast.CHARS.update(phum=PHUM, kong=KONG, em=EM, bua=BUA, manao=MANAO, yuelao=YUELAO, bam=BAM, jake=JAKE, faa=FAA, mariam=MARIAM, omar=OMAR)

_b = figure.BODY


def _male_body(top_scale=(1.0, 1.0), **kw):
    b = dict(_scale_body(_b["pin"], *top_scale), top=WHITE, top_dark=WHITE_SH, cuff=(232, 236, 246), bottom=(38, 38, 46), shoe=(40, 40, 48), sole=(220, 220, 224))
    b.update(kw)
    return b


def _female_body(kx=0.92, kz=0.92, **kw):
    b = dict(_scale_body(_b["mom"], kx, kz), top=WHITE, top_dark=WHITE_SH, cuff=BLACK, bottom=BLACK, shoe=(40, 40, 48), sole=(220, 220, 224))
    # knee-length skirt: the dress ends at the knee, the shins show
    b["torso"] = [(y, a * kx, bb * kz, z0) for y, a, bb, z0 in [(106, 20, 16, -4), (114, 46, 28, -4), (124, 55, 32, -4), (150, 54, 34, -2), (178, 48, 31, 0),
                                                              (208, 56, 35, 0), (236, 66, 40, 0), (262, 72, 43, 0)]]
    b["hip"] = (18, 262)
    b.update(kw)
    return b


_b["phum"] = _male_body((1.0, 1.0))
_b["kong"] = _male_body((1.14, 1.1))
_b["em"] = _male_body((1.3, 1.25))
_b["bua"] = _female_body(0.9, 0.9)
_b["manao"] = _female_body(0.92, 0.92)
_b["yuelao"] = dict(_scale_body(_b["mom"], 1.0, 1.0), top=(238, 196, 64), top_dark=(204, 160, 40), cuff=(200, 52, 60), bottom=(238, 196, 64), shoe=(130, 96, 60), sole=(90, 70, 50))
_b["bam"] = _female_body(0.94, 0.94)
_b["faa"] = dict(_scale_body(_b["mom"], 0.9, 0.9), top=(244, 150, 170), top_dark=(214, 116, 140), cuff=(250, 230, 236), bottom=(244, 150, 170), shoe=(250, 250, 252), sole=(220, 220, 224))
_b["mariam"] = dict(_scale_body(_b["mom"], 0.96, 0.96), top=(178, 152, 212), top_dark=(146, 120, 184), cuff=(244, 236, 250), bottom=(178, 152, 212), shoe=(250, 250, 252), sole=(220, 220, 224))
_b["jake"] = dict(_scale_body(_b["pin"], 1.14, 1.1), top=(64, 104, 168), top_dark=(44, 78, 134), cuff=(54, 90, 150), bottom=(70, 76, 96), shoe=(244, 244, 248), sole=(200, 200, 208))
_b["omar"] = _male_body((1.08, 1.06), top=(120, 176, 160), top_dark=(88, 140, 126), cuff=(104, 158, 144), bottom=(60, 66, 92), shoe=(92, 66, 50), sole=(214, 210, 200))
figure.ARM_LEN.update(phum=(54.0, 52.0), kong=(58.0, 56.0), em=(54.0, 52.0), bua=(52.0, 50.0), manao=(52.0, 50.0), yuelao=(54.0, 52.0), bam=(52.0, 50.0), jake=(58.0, 56.0),
                      faa=(52.0, 50.0), mariam=(54.0, 52.0), omar=(56.0, 54.0))

UNI = dict(phum="male", kong="male", em="male", bua="female", manao="female", bam="female", omar="male")
NO_PIN = {"omar"}                                # a plain shirt: no gold university pin
poc_chars.CID.update(phum=Pinlike("phum"), kong=Pinlike("kong"), em=Pinlike("em"), bua="bua", manao="manao", yuelao="yuelao", bam="bam", jake=Pinlike("jake"), faa="faa", mariam="mariam", omar=Pinlike("omar"))
poc_chars.SCALE.update(phum=0.92, kong=0.98, em=0.9, bua=0.9, manao=0.88, yuelao=0.95, bam=0.9, jake=1.0, faa=0.9, mariam=0.9, omar=0.96)

# ---------------------------------------------------------------------------------------------------------------- garment wrappers
_mode = [None]
_cv = [None]
_name = [None]
GOWN = set()                                   # names drawn in a black graduation gown right now (set by the scene)
GOWN_BLACK, GOWN_SH = (30, 30, 38), (16, 16, 24)
_orig_figure = figure.figure
_orig_on_body = figure.on_body
_orig_lathe_band = figure.lathe_band
_orig_lathe = toon.lathe


def _on_body(sl, phi_deg, y, th, lift=0.0):
    p, v = _orig_on_body(sl, phi_deg, y, th, lift)
    if _mode[0] == "male":
        return p, -1.0                      # no pocket, no drawstrings, no collar-roll lines
    return p, v


def _lathe(slices, th, n=6):
    if _mode[0] == "male" and len(slices) == 4 and slices[0][0] == 98:
        return []                           # no hood
    return _orig_lathe(slices, th, n)


def _lathe_band(sl, y0, y1, th):
    if _mode[0] == "male" and _name[0] in GOWN:
        cv = _cv[0]                         # the gown: a black skirt from the waist to the knee over the trousers
        gw = [(y, *figure.slice_at(sl, min(y, 236))) for y in (190, 215, 245, 275, 305)]
        gw = [(y, a * (1.0 + 0.10 * i), b * (1.0 + 0.10 * i), z) for i, (y, a, b, z) in enumerate(gw)]
        cv.fill(_orig_lathe(gw, th, n=6), GOWN_BLACK, lw=3.0, shade_col=GOWN_SH, depth=9)
        return []
    if _mode[0] == "male":
        return []                           # no hoodie hem
    if _mode[0] == "female":
        return _orig_lathe(([(y, *figure.slice_at(sl, y)) for y in (254, 257, 260, 263, 266)]), th, n=3)     # black hem band
    return _orig_lathe_band(sl, y0, y1, th)


def _figure(cv, cid, th, pose="rest", expr="neutral", pregnant=False, lean=0.0, **kw):
    name = str(cid)
    mode = UNI.get(name)
    if mode is None:
        return _orig_figure(cv, cid, th, pose, expr, pregnant, lean, **kw)
    _mode[0], _cv[0], _name[0] = mode, cv, name
    gown_saved = None
    if name in GOWN:
        gown_saved = figure.BODY[name]
        figure.BODY[name] = dict(gown_saved, top=GOWN_BLACK, top_dark=GOWN_SH, cuff=GOWN_BLACK)
    poc_chars.NO_LOCKS = mode == "male"
    figure.on_body, figure.lathe_band, toon.lathe = _on_body, _lathe_band, _lathe
    try:
        if mode == "female":
            # draw the skirt right after the torso: wrap hair/torso order by drawing it when the hem band is requested (see _lathe_band) -- the band is
            # drawn right after the torso, so draw the skirt just before it
            figure.lathe_band = _skirt_then_band
        _orig_figure(cv, cid, th, pose, expr, pregnant, lean, **kw)
    finally:
        figure.on_body, figure.lathe_band, toon.lathe = _orig_on_body, _orig_lathe_band, _orig_lathe
        _mode[0] = None
        poc_chars.NO_LOCKS = False
        if gown_saved is not None:
            figure.BODY[name] = gown_saved
    # collar, placket and buttons in the figure's own transform (including the lean about the hip)
    B = figure.BODY[name]
    cv.push(0, 0, rot=lean, pivot=(0, B["hip"][1]))
    _uniform_overlay(cv, th, mode, gown=name in GOWN, pin=name not in NO_PIN)
    cv.pop()


def _skirt_then_band(sl, y0, y1, th):
    cv = _cv[0]
    sk = [(y, *figure.slice_at(sl, y)) for y in (200, 215, 230, 245, 262)]
    cv.fill(_orig_lathe(sk, th, n=6), BLACK, lw=3.0, shade_col=BLACK_SH, depth=9)
    return _lathe_band(sl, y0, y1, th)


def _p3(pt, th):
    return figure._p(pt, th)[0]


def _uniform_overlay(cv, th, mode, gown=False, pin=True):
    """Collar (two lapels), placket line, buttons, gold pin. Points are projected like the arms are: yaw about the body axis."""
    left = [(-22, 96, 24), (-3, 104, 33), (-3, 130, 36), (-26, 112, 28)]
    right = [(22, 96, 24), (3, 104, 33), (3, 130, 36), (26, 112, 28)]
    if mode == "female":
        left = [(-20, 98, 22), (-3, 104, 30), (-3, 126, 33), (-24, 110, 26)]
        right = [(20, 98, 22), (3, 104, 30), (3, 126, 33), (24, 110, 26)]
    for poly in (left, right):
        cv.fill([_p3(p, th) for p in poly], WHITE, ink=INK, lw=2.4, shade_col=WHITE_SH, depth=3)
    if gown:
        return                                # under the black gown only the white collar shows
    if mode == "male":
        top, bot = _p3((0, 128, 36), th), _p3((0, 232, 37), th)
        cv.stroke([top, bot], (190, 198, 214), 1.8)
        for y in (150, 178, 206):
            x, yy = _p3((0, y, 37), th)
            cv.ellipse(x, yy, 2.6, 2.6, (200, 206, 220), ink=INK, lw=1.0)
        px, py = _p3((-30, 176, 36), th)
        if pin:
            cv.ellipse(px, py, 5.4, 5.4, GOLD, ink=INK, lw=1.4)
    else:
        px, py = _p3((-24, 170, 30), th)
        cv.ellipse(px, py, 5.0, 5.0, GOLD, ink=INK, lw=1.4)


figure.figure = _figure
