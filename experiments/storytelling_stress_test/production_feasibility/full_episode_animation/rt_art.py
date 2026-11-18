"""Hand-built art for the red-thread story (v2): proper hearts, a real-looking pinky hook, the red thread that always starts at a pinky, bouquet, teddy bear,
a phone chat, snacks. Everything is procedural (Pillow via toon.Canvas); nothing in prototype_v2 is edited."""
from __future__ import annotations

import math

import engine  # noqa: F401  (sets the import paths)
import poc_chars  # noqa: F401
from poc_chars import figure
from props_uni import RED, RED_GLOW, rect, rrect
from toon import INK, mix, spline

PINK = (240, 84, 116)
PINK_SH = (206, 52, 88)
SKIN = (244, 206, 170)
SKIN_SH = (222, 170, 138)

# ------------------------------------------------------------------------------------------------------------------ pinky anchors
_REC: list = []
_orig_hand = figure.hand


def _hand_rec(cv, wrist, angle_deg, kind, skin, mirror=False, scale=1.0, part="all"):
    """Remember where every hand drawn by the rig lands on the screen (wrist and pinky side), so the thread can start at the real pinky."""
    if part in ("all", "base"):
        cv.push(wrist[0], wrist[1], rot=angle_deg, scale=scale, flip=mirror)
        p = cv.T([(0, 0), (-7.5, 19), (0, 22)])
        cv.pop()
        ss = cv.ss
        _REC.append(dict(w=(p[0][0] / ss, p[0][1] / ss), pk=(p[1][0] / ss, p[1][1] / ss), tip=(p[2][0] / ss, p[2][1] / ss)))
    if HIDE_ARMS[0]:
        return None
    return _orig_hand(cv, wrist, angle_deg, kind, skin, mirror, scale, part)


figure.hand = _hand_rec
HIDE_ARMS = [False]
_orig_limb, _orig_band = figure.limb, figure._band
_ARM_W = None


def _arm_widths():
    global _ARM_W
    if _ARM_W is None:
        _ARM_W = {tuple(b["arm_w"]) for b in figure.BODY.values() if "arm_w" in b}
    return _ARM_W


def _limb_hide(cv, pts, widths, col, *a, **k):
    if HIDE_ARMS[0] and len(pts) == 3 and tuple(widths) in _arm_widths():
        return []
    return _orig_limb(cv, pts, widths, col, *a, **k)


def _band_hide(*a, **k):
    return [] if HIDE_ARMS[0] else _orig_band(*a, **k)


figure.limb, figure._band = _limb_hide, _band_hide
LAST: dict = {}


def begin_actor():
    _REC.clear()


def end_actor(who):
    LAST[who] = list(_REC)


def pinky_of(who, toward_x=None, near=None):
    """Screen position of one of `who`'s pinkies, as drawn this frame: the hand closest to `toward_x` (or to the point `near`)."""
    recs = LAST.get(who) or []
    if not recs:
        return None
    if near is not None:
        r = min(recs, key=lambda q: math.hypot(q["pk"][0] - near[0], q["pk"][1] - near[1]))
    else:
        r = min(recs, key=lambda q: abs(q["pk"][0] - (toward_x if toward_x is not None else 0.0)))
    return r["pk"]


# ------------------------------------------------------------------------------------------------------------------ the thread
def _bez(p0, p1, p2, p3, n=36):
    out = []
    for i in range(n + 1):
        u = i / n
        a, b, c, d = (1 - u) ** 3, 3 * u * (1 - u) ** 2, 3 * u * u * (1 - u), u ** 3
        out.append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))
    return out


def ring(cv, p, s=1.0, alpha=255):
    """The red loop tied around a pinky."""
    if p is None:
        return
    cv.ellipse(p[0], p[1], 8.5 * s, 4.2 * s, RED, ink=None, alpha=alpha)
    cv.stroke([(p[0] - 9 * s, p[1]), (p[0], p[1] + 4.6 * s), (p[0] + 9 * s, p[1])], mix(RED, (120, 10, 30), 0.55), 1.8 * s, alpha=alpha)
    cv.ellipse(p[0] + 6 * s, p[1] - 3.2 * s, 2.6 * s, 2.0 * s, (255, 150, 160), ink=None, alpha=alpha)


def link(cv, a, b, t=0.0, sag=70.0, w=3.6, alpha=255, glow=True, tie=True, sway=1.0, spark=True):
    """The red thread from pinky a to pinky b: one smooth cubic curve that hangs a little and breathes, so it follows both hands wherever they go.
    No dashes, no noise, no popping: only the endpoints (the hands) move."""
    if a is None or b is None:
        return None
    dx = b[0] - a[0]
    s = sag + 5.0 * sway * math.sin(t * 1.3)
    p1 = (a[0] + dx * 0.28, a[1] + s * 1.1)
    p2 = (b[0] - dx * 0.28, b[1] + s * 1.1)
    pts = _bez(a, p1, p2, b)
    sp = spline(pts, n=2)
    if glow:
        cv.stroke(sp, RED_GLOW, w + 6.0, alpha=int(60 * alpha / 255))
    cv.stroke(sp, (150, 22, 44), w + 2.4, alpha=alpha)             # a darker edge keeps the thin line visible after video compression (chroma is half resolution)
    cv.stroke(sp, RED, w, alpha=alpha)
    cv.stroke(sp, (255, 130, 140), max(1.0, w * 0.35), alpha=int(150 * alpha / 255))
    if spark:
        u = (t * 0.28) % 1.0
        x, y = pts[int(u * (len(pts) - 1))]
        fade = math.sin(math.pi * u)
        cv.ellipse(x, y, 4.2, 4.2, (255, 240, 240), ink=None, alpha=int(190 * fade * alpha / 255))
    if tie:
        ring(cv, a, alpha=alpha)
        ring(cv, b, alpha=alpha)
    return pts


def off_edge(p, side, drop=30.0):
    """A point beyond the screen edge (side -1 left / +1 right) for a thread that goes on out of the picture."""
    return (-60.0 if side < 0 else 1340.0, p[1] + drop)


# ------------------------------------------------------------------------------------------------------------------ hearts
def heart_pts(x, y, s, rot=0.0, n=90, a0=0.0, a1=2 * math.pi):
    out = []
    c, sn = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    for i in range(n + 1):
        t = a0 + (a1 - a0) * i / n
        hx = 16 * math.sin(t) ** 3
        hy = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
        px, py = hx * s / 16.0, hy * s / 16.0 + 0.04 * s
        out.append((x + px * c - py * sn, y + px * sn + py * c))
    return out


def heart(cv, x, y, s=60, col=PINK, rot=0.0, alpha=255, glow=0.0, lw=3.0, ink=INK):
    """A proper love heart: smooth parametric outline, soft shade, a glint on the left lobe."""
    if glow > 0:
        cv.fill(heart_pts(x, y, s * 1.35, rot), col, ink=None, alpha=int(60 * glow * alpha / 255))
    pts = heart_pts(x, y, s, rot)
    cv.fill(pts, col, ink=ink, lw=lw, shade_col=mix(col, (120, 20, 50), 0.35), depth=max(3.0, s * 0.10), alpha=alpha)
    g = heart_pts(x, y, s * 0.72, rot, n=40, a0=-0.55, a1=-0.05)
    g = [(gx - s * 0.12, gy - s * 0.08) for gx, gy in g]
    cv.stroke(spline(g, n=2), (255, 255, 255), max(2.0, s * 0.07), alpha=int(190 * alpha / 255))
    cv.ellipse(x - s * 0.52, y - s * 0.30, max(2.0, s * 0.06), max(2.0, s * 0.06), (255, 255, 255), ink=None, alpha=int(200 * alpha / 255))


def _crack(s, x, y):
    return [(x, y - 0.30 * s), (x - 0.16 * s, y - 0.10 * s), (x + 0.12 * s, y + 0.10 * s), (x - 0.08 * s, y + 0.36 * s), (x, y + 0.98 * s)]


def heart_broken(cv, x, y, s=60, split=0.0, col=PINK, alpha=255):
    """A heart that cracks along a zig-zag and falls into two pieces (split 0..1)."""
    if split <= 0.02:
        heart(cv, x, y, s, col, alpha=alpha)
        zz = _crack(s, x, y)
        cv.stroke(zz[:3], INK, 2.4, alpha=int(255 * min(1.0, split / 0.02 + 0.0)) if split > 0 else 0)
        return
    top = (x, y + 0.04 * s - 5 * s / 16.0)
    zz = _crack(s, x, y)
    right = heart_pts(x, y, s, n=60, a0=0.0, a1=math.pi)[:-1]
    left = heart_pts(x, y, s, n=60, a0=math.pi, a1=2 * math.pi)
    right_poly = right + [(zz[-1][0], zz[-1][1])] + zz[-2::-1]
    left_poly = left + zz[1:]
    d = split * 0.42 * s
    sh = mix(col, (120, 20, 50), 0.35)
    for poly, sg in ((left_poly, -1), (right_poly, 1)):
        cv.push(sg * d, split * split * 0.55 * s, rot=sg * 22 * split, pivot=(x, y))
        cv.fill(poly, col, ink=INK, lw=3.0, shade_col=sh, depth=max(3.0, s * 0.10), alpha=alpha)
        cv.pop()


# ------------------------------------------------------------------------------------------------------------------ hands that look like hands
def _cap(cv, pts, w, skin=SKIN, sh=SKIN_SH, ink_w=2.6):
    sp = spline(pts, n=3)
    cv.stroke(sp, INK, w + ink_w * 2)
    cv.stroke(sp, skin, w)
    cv.stroke(spline([(px + w * 0.16, py + w * 0.18) for px, py in pts], n=3), sh, max(2.0, w * 0.22), alpha=120)


def hand_pinky(cv, x, y, s=1.0, flip=False, skin=SKIN, hook=1.0, sleeve=(250, 250, 252), sleeve_len=150):
    """A hand seen from the front, wrist at (x, y), fingers up: index / middle / ring curled over the palm (three rounded bars with knuckle creases),
    the thumb pressed across them, the little finger raised with two joints and a nail, its tip curling into a hook (hook 0..1).
    Returns the screen position of the little finger's middle joint (where the thread band goes)."""
    sg = -1 if flip else 1
    cv.push(x, y, scale=s, flip=flip)
    sh = mix(skin, (210, 150, 130), 0.5)
    crease = mix(INK, skin, 0.35)
    # sleeve (shirt cuff) and wrist
    cv.fill([(-42, 8), (42, 8), (50, sleeve_len), (-50, sleeve_len)], sleeve, ink=INK, lw=3.0, shade_col=(214, 220, 232), depth=5)
    cv.fill([(-30, 14), (30, 14), (32, -14), (-32, -14)], skin, ink=INK, lw=2.6, shade_col=sh, depth=4)
    # palm
    cv.fill(spline([(-48, -12), (-54, -56), (-48, -100), (0, -108), (50, -100), (54, -56), (48, -12)], closed=True, n=3), skin, ink=INK, lw=3.0, shade_col=sh, depth=7)
    # the little finger first (it lies behind the thumb): knuckle -> two joints -> hooked tip
    c = max(0.0, min(1.0, hook))
    base = [(40, -96), (40, -124), (40, -148)]
    tipc = [(40, -148), (40 + 6 * c, -162), (40 + 22 * c, -168), (40 + 36 * c, -158), (40 + 36 * c, -140)]
    pk = base + tipc[1:]
    _cap(cv, pk, 19, skin, sh)
    for jy in (-122, -148):
        cv.stroke([(33, jy), (47, jy)], crease, 1.8)
    nx, ny = pk[-1]
    cv.ellipse(nx, ny + 3, 4.4, 5.6, (252, 232, 226), ink=INK, lw=1.4)
    # three curled fingers: rounded bars in front of the palm
    for fx in (-30, -4, 22):
        bar = [(fx - 14, -102), (fx + 14, -102), (fx + 15, -58), (fx + 9, -44), (fx - 9, -44), (fx - 15, -58)]
        cv.fill(spline(bar, closed=True, n=3), skin, ink=INK, lw=2.8, shade_col=sh, depth=4)
        cv.stroke([(fx - 9, -82), (fx + 9, -82)], crease, 1.8)
        cv.stroke([(fx - 7, -66), (fx + 7, -66)], crease, 1.4)
    # thumb across the fingers
    _cap(cv, [(-56, -66), (-40, -34), (-6, -26), (22, -36)], 22, skin, sh)
    cv.stroke(spline([(-30, -30), (-16, -29)], n=2), crease, 1.6)
    cv.pop()
    return (x + sg * 40 * s, y - 130 * s)


def _tails(cv, ra, rb, lx, rx, ya, yb, s):
    cv.stroke(spline([ra, (ra[0] - 40 * s, ya - 60 * s), (lx - 90 * s, ya + 40 * s), (lx - 160 * s, ya + 170 * s), (lx - 260 * s, ya + 300 * s)], n=3), RED_GLOW, 9.0, alpha=70)
    cv.stroke(spline([ra, (ra[0] - 40 * s, ya - 60 * s), (lx - 90 * s, ya + 40 * s), (lx - 160 * s, ya + 170 * s), (lx - 260 * s, ya + 300 * s)], n=3), RED, 3.8)
    cv.stroke(spline([rb, (rb[0] + 40 * s, yb - 60 * s), (rx + 90 * s, yb + 40 * s), (rx + 160 * s, yb + 170 * s), (rx + 260 * s, yb + 300 * s)], n=3), RED_GLOW, 9.0, alpha=70)
    cv.stroke(spline([rb, (rb[0] + 40 * s, yb - 60 * s), (rx + 90 * s, yb + 40 * s), (rx + 160 * s, yb + 170 * s), (rx + 260 * s, yb + 300 * s)], n=3), RED, 3.8)


def pinky_hook(cv, x, y, s=1.0, t=0.0, alpha=255, tails=True, sleeve_len=150):
    """Close-up of two hands hooked by the little fingers, the red thread tied round both and trailing off behind the hands to the lower corners."""
    lx, rx = x - 46 * s, x + 46 * s
    bob = 4 * math.sin(t * 2.0) * s
    ya, yb = y + bob, y + 10 * s + bob
    ra, rb = (lx + 40 * s, ya - 118 * s), (rx - 40 * s, yb - 128 * s)
    # tails first, so they come out from behind the hands
    if tails:
        _tails(cv, ra, rb, lx, rx, ya, yb, s)
    hand_pinky(cv, rx, yb, s, flip=True, hook=1.0, sleeve=(250, 250, 252), sleeve_len=sleeve_len)
    hand_pinky(cv, lx, ya, s, flip=False, hook=1.0, sleeve_len=sleeve_len)
    link(cv, (ra[0] + 3 * s, ra[1] - 2 * s), (rb[0] - 3 * s, rb[1] - 4 * s), t, sag=-22 * s, w=3.2, tie=False, spark=False, glow=False)
    ring(cv, ra, 1.2 * s)
    ring(cv, rb, 1.2 * s)
    return ra, rb


# ------------------------------------------------------------------------------------------------------------------ props
def bouquet(cv, x, y, s=1.0, sway=0.0, cols=((250, 120, 150), (255, 200, 90), (255, 255, 255), (170, 130, 220))):
    """A flower bouquet held upright, wrapping paper cone below, ribbon, leaves. (x, y) = where the hand grips (the cone's waist)."""
    cv.push(x, y, scale=s, rot=sway)
    cv.fill([(-30, -14), (30, -14), (10, 66), (-10, 66)], (252, 244, 232), ink=INK, lw=2.6, shade_col=(226, 210, 190), depth=5)
    cv.fill([(-30, -14), (0, 20), (30, -14), (14, -20), (-14, -20)], (244, 196, 206), ink=INK, lw=2.4)
    for dx, dy in ((-36, -24), (-14, -34), (16, -36), (38, -22)):
        cv.fill(spline([(dx - 10, dy + 6), (dx, dy - 14), (dx + 12, dy + 4), (dx, dy + 14)], closed=True, n=3), (96, 168, 110), ink=INK, lw=2.0)
    for i, (dx, dy, r) in enumerate(((-26, -44, 15), (0, -58, 17), (26, -46, 15), (-8, -34, 14), (16, -30, 13))):
        col = cols[i % len(cols)]
        for k in range(6):
            a = k * math.pi / 3
            cv.ellipse(dx + math.cos(a) * r * 0.62, dy + math.sin(a) * r * 0.62, r * 0.5, r * 0.5, col, ink=INK, lw=1.4)
        cv.ellipse(dx, dy, r * 0.42, r * 0.42, (255, 226, 120), ink=INK, lw=1.4)
    cv.fill([(-14, -4), (14, -4), (22, 6), (0, 0), (-22, 6)], (236, 70, 100), ink=INK, lw=2.0)
    cv.ellipse(0, -2, 5, 5, (236, 70, 100), ink=INK, lw=1.8)
    cv.pop()


def teddy(cv, x, y, s=1.0, tilt=0.0, col=(190, 130, 84)):
    """A teddy bear sitting; (x, y) = centre of the tummy."""
    sh = mix(col, (80, 40, 20), 0.35)
    lt = mix(col, (255, 230, 200), 0.55)
    cv.push(x, y, scale=s, rot=tilt)
    for dx in (-26, 26):                                               # legs and feet
        cv.ellipse(dx, 40, 16, 20, col, ink=INK, lw=2.4, shade_col=sh)
        cv.ellipse(dx, 48, 10, 8, lt, ink=INK, lw=1.8)
    cv.ellipse(0, 6, 34, 40, col, ink=INK, lw=2.8, shade_col=sh)       # body
    cv.ellipse(0, 12, 20, 24, lt, ink=None)
    for dx, rot in ((-40, 30), (40, -30)):                             # arms
        cv.ellipse(dx, 0, 12, 22, col, ink=INK, lw=2.4, shade_col=sh, rot=rot)
    for dx in (-26, 26):                                               # ears
        cv.ellipse(dx, -56, 12, 12, col, ink=INK, lw=2.4, shade_col=sh)
        cv.ellipse(dx, -55, 6, 6, lt, ink=None)
    cv.ellipse(0, -36, 30, 27, col, ink=INK, lw=2.8, shade_col=sh)     # head
    cv.ellipse(0, -28, 14, 11, lt, ink=INK, lw=1.8)
    cv.ellipse(0, -31, 4.4, 3.2, (60, 36, 30), ink=None)
    cv.stroke([(0, -28), (0, -23)], (60, 36, 30), 1.6)
    cv.stroke(spline([(-7, -22), (0, -19), (7, -22)], n=2), (60, 36, 30), 1.6)
    for dx in (-11, 11):
        cv.ellipse(dx, -42, 3.4, 4.2, (50, 30, 26), ink=None)
        cv.ellipse(dx - 1, -43.5, 1.2, 1.2, (255, 255, 255), ink=None)
    cv.fill([(-14, -12), (0, -8), (14, -12), (14, -4), (0, -8), (-14, -4)], (236, 70, 100), ink=INK, lw=1.8)   # bow tie
    cv.ellipse(0, -8, 3.4, 3.4, (236, 70, 100), ink=INK, lw=1.4)
    cv.pop()


def snack(cv, x, y, s=1.0, col=(240, 110, 90), rot=0.0):
    """A snack pouch (crimped top and bottom, a round label)."""
    cv.push(x, y, scale=s, rot=rot)
    cv.fill([(-20, -26), (20, -26), (24, 24), (-24, 24)], col, ink=INK, lw=2.4, shade_col=mix(col, (0, 0, 0), 0.2), depth=4)
    for yy in (-30, 28):
        cv.fill([(-22, yy - 4), (22, yy - 4), (22, yy + 4), (-22, yy + 4)], mix(col, (255, 255, 255), 0.35), ink=INK, lw=1.8)
    cv.ellipse(0, 0, 11, 11, (255, 244, 214), ink=INK, lw=1.8)
    cv.ellipse(0, 0, 4, 4, mix(col, (0, 0, 0), 0.25), ink=None)
    cv.pop()


def phone(cv, x, y, s=1.0, msgs=(), t=0.0, alpha=255, glow=True):
    """A phone with a chat on screen: msgs = [(side 'L'|'R', width 0..1, appears_at_seconds, heart?)]; bubbles pop in at their time. No text."""
    cv.push(x, y, scale=s)
    if glow:
        cv.ellipse(0, 0, 230, 290, (255, 255, 255), ink=None, alpha=34)
    rrect(cv, -110, -200, 110, 200, 26, (44, 48, 66), lw=3.2)
    rrect(cv, -96, -176, 96, 178, 12, (246, 248, 252), lw=1.6)
    rect(cv, -96, -176, 96, -136, (110, 150, 230), ink=None)
    cv.ellipse(-70, -156, 11, 11, (255, 226, 200), ink=INK, lw=1.4)
    cv.stroke([(-52, -158), (24, -158)], (255, 255, 255), 5)
    cy = -118
    for side, wf, at, hrt in msgs:
        k = max(0.0, min(1.0, (t - at) * 4.0))
        if k <= 0:
            continue
        w = 150 * wf
        h = 38
        x0 = -88 if side == "L" else 88 - w
        col = (255, 255, 255) if side == "L" else (150, 220, 150)
        cv.push(x0 + (w / 2), cy + h / 2, scale=0.6 + 0.4 * k)
        rrect(cv, -w / 2, -h / 2, w / 2, h / 2, 14, col, lw=2.0)
        for ln in range(2 if wf > 0.55 else 1):
            cv.stroke([(-w / 2 + 12, -6 + ln * 12), (w / 2 - 12 - (ln * 22), -6 + ln * 12)], (170, 176, 190), 3)
        if hrt:
            heart(cv, w / 2 - 14, -h / 2 - 4, 11, PINK, lw=1.6)
        cv.pop()
        cy += h + 12
    cv.pop()


def tear(cv, x, y, s=1.0, alpha=255):
    cv.fill(spline([(x, y - 14 * s), (x - 8 * s, y + 2 * s), (x, y + 10 * s), (x + 8 * s, y + 2 * s)], closed=True, n=3), (150, 206, 250), ink=INK, lw=1.6, alpha=alpha)


def book(cv, x, y, s=1.0, rot=0.0):
    """The old man's register of couples: a thick red-covered book with a gold band."""
    cv.push(x, y, scale=s, rot=rot)
    cv.fill([(-34, -26), (34, -26), (34, 28), (-34, 28)], (176, 52, 60), ink=INK, lw=2.8, shade_col=(130, 30, 40), depth=5)
    cv.fill([(-30, -22), (30, -22), (30, 24), (-30, 24)], (252, 244, 226), ink=None)
    cv.stroke([(0, -26), (0, 28)], INK, 2.0)
    cv.stroke([(-4, -26), (-4, 28)], (236, 192, 70), 4)
    cv.pop()


def tangle_heart(cv, cx, cy, s=200.0, t=0.0, strands=10, alpha=255, w=3.4):
    """The tangled thread: many strands that wander and loop around the outline of one big heart, so from above the whole mess reads as a heart."""
    for j in range(strands):
        rj = 0.40 + 0.62 * ((j * 0.381) % 1.0)
        ph = j * 1.37
        sgn = 1 if j % 2 == 0 else -1
        pts = []
        n = 150
        for i in range(n + 1):
            a = (i / n) * 2 * math.pi * 1.0
            hx = 16 * math.sin(a) ** 3
            hy = -(13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a))
            bx, by = hx * s / 16.0 * rj, hy * s / 16.0 * rj
            ww = 0.05 * s
            lp = 0.075 * s * (0.5 + 0.5 * math.sin(3 * a + j))
            aa = sgn * a
            bx += ww * math.cos(7 * aa + ph + 0.5 * t) + lp * math.cos(15 * aa + ph * 2)
            by += ww * math.sin(7 * aa + ph + 0.5 * t) + lp * math.sin(15 * aa + ph * 2)
            pts.append((cx + bx, cy + by + 0.05 * s))
        sp = spline(pts, n=1)
        cv.stroke(sp, RED_GLOW, w + 5, alpha=int(34 * alpha / 255))
        cv.stroke(sp, RED, w, alpha=int(235 * alpha / 255))
    # a faint glow behind the heart
    cv.fill(heart_pts(cx, cy, s * 1.05), RED_GLOW, ink=None, alpha=int(22 * alpha / 255))


def yarn_loops(cv, pts, t=0.0, alpha=255, w=3.4, r=26):
    """A messy thread that winds round a list of waypoints (a pillar, a desk leg, a door knob): one loop and a half round each, joined by lazy curves."""
    path = []
    for i, (x, y) in enumerate(pts):
        a0 = i * 1.7
        for k in range(0, 27):
            a = a0 + k / 26 * 2 * math.pi * 1.4
            rr = r * (1.0 - 0.15 * (k / 26))
            path.append((x + math.cos(a) * rr, y + math.sin(a) * rr * 0.9))
    sp = spline(path, n=2)
    cv.stroke(sp, RED_GLOW, w + 5, alpha=int(50 * alpha / 255))
    cv.stroke(sp, RED, w, alpha=alpha)
    return path


def suitcase(cv, x, y, s=1.0, col=(226, 90, 90)):
    """A little rolling suitcase standing on its wheels; (x, y) = bottom centre."""
    cv.push(x, y, scale=s)
    cv.stroke([(0, -78), (0, -118)], (110, 110, 124), 5)
    cv.stroke([(-14, -118), (14, -118)], (110, 110, 124), 7)
    cv.fill(spline([(-30, -76), (30, -76), (32, -4), (-32, -4)], closed=True, n=2), col, ink=INK, lw=2.6, shade_col=mix(col, (0, 0, 0), 0.25), depth=5)
    for dx in (-14, 14):
        cv.stroke([(dx, -66), (dx, -14)], mix(col, (255, 255, 255), 0.3), 3)
    for dx in (-22, 22):
        cv.ellipse(dx, 0, 6, 6, (60, 60, 70), ink=INK, lw=1.6)
    cv.pop()


def knot(cv, x, y, s=1.0, col=RED):
    """An overhand knot in the thread."""
    pts = [(x - 40 * s, y + 6 * s), (x - 14 * s, y - 4 * s), (x + 12 * s, y - 26 * s), (x + 26 * s, y - 2 * s), (x + 6 * s, y + 22 * s), (x - 18 * s, y + 4 * s), (x - 4 * s, y - 20 * s), (x + 40 * s, y - 6 * s)]
    sp = spline(pts, n=3)
    cv.stroke(sp, RED_GLOW, 9, alpha=60)
    cv.stroke(sp, col, 4.2)


def hairpin(cv, x, y, s=1.0, rot=0.0, shine=0.0):
    """A hair pin (ปิ่นปักผม): a long gold pin with a small flower on its head. (x, y) = the flower; the pin hangs down from it."""
    cv.push(x, y, scale=s, rot=rot)
    cv.stroke([(0, 8), (0, 112)], INK, 7.0)
    cv.stroke([(0, 8), (0, 112)], (240, 200, 90), 4.2)
    cv.stroke([(-1, 14), (-1, 100)], (255, 246, 196), 1.6, alpha=190)
    for k in range(5):
        a = k * 1.2566 - 1.57
        cv.ellipse(math.cos(a) * 11, math.sin(a) * 11, 8.4, 8.4, (250, 130, 160), ink=INK, lw=1.8)
    cv.ellipse(0, 0, 6.2, 6.2, (255, 226, 120), ink=INK, lw=1.6)
    if shine > 0:
        for dx, dy in ((-20, -18), (22, -10), (12, 22)):
            cv.ellipse(dx, dy, 3.2 * shine, 3.2 * shine, (255, 250, 220), ink=None, alpha=int(230 * shine))
    cv.pop()


def tiffin(cv, x, y, s=1.0):
    """A tiffin carrier (ปิ่นโต): three round steel tiers on top of each other, clamped by an arched handle. (x, y) = bottom centre."""
    cv.push(x, y, scale=s)
    steel, steel_sh = (214, 220, 228), (160, 170, 184)
    for i, yy in enumerate((0, -46, -92)):
        cv.fill(spline([(-38, yy - 2), (-42, yy - 24), (-38, yy - 44), (38, yy - 44), (42, yy - 24), (38, yy - 2)], closed=True, n=3), steel, ink=INK, lw=2.6, shade_col=steel_sh, depth=5)
        cv.stroke([(-40, yy - 22), (40, yy - 22)], (120, 130, 150), 2.0)
        cv.ellipse(0, yy - 44, 36, 7, (236, 240, 246), ink=INK, lw=2.0)
    cv.ellipse(0, -138, 30, 6, (236, 240, 246), ink=INK, lw=2.0)                      # lid knob
    cv.ellipse(0, -146, 7, 7, (190, 198, 210), ink=INK, lw=2.0)
    cv.stroke(spline([(-44, -20), (-50, -90), (-34, -150), (0, -168), (34, -150), (50, -90), (44, -20)], n=3), INK, 8.0)
    cv.stroke(spline([(-44, -20), (-50, -90), (-34, -150), (0, -168), (34, -150), (50, -90), (44, -20)], n=3), (230, 120, 100), 4.6)
    cv.pop()


def teapot(cv, x, y, s=1.0, tilt=0.0):
    """A round porcelain teapot with a lid, spout and handle; (x, y) = bottom centre."""
    cv.push(x, y, scale=s, rot=tilt, pivot=(0, 0))
    white, sh = (252, 248, 240), (218, 208, 196)
    cv.stroke(spline([(30, -26), (62, -46), (58, -12), (34, -6)], n=3), INK, 9)
    cv.stroke(spline([(30, -26), (62, -46), (58, -12), (34, -6)], n=3), (236, 226, 214), 5)
    cv.fill(spline([(-34, -14), (-62, -52), (-72, -60), (-56, -62), (-30, -34)], closed=True, n=3), white, ink=INK, lw=2.4, shade_col=sh, depth=3)
    cv.ellipse(0, -34, 44, 36, white, ink=INK, lw=2.8, shade_col=sh)
    for dx in (-20, 0, 20):
        cv.stroke(spline([(dx - 6, -52), (dx, -38), (dx - 6, -20)], n=3), (240, 130, 150), 2.2, alpha=190)
    cv.fill([(-22, -66), (22, -66), (16, -74), (-16, -74)], white, ink=INK, lw=2.2)
    cv.ellipse(0, -78, 6, 5, (240, 130, 150), ink=INK, lw=1.6)
    cv.pop()


def teacup(cv, x, y, s=1.0, steam=0.0, t=0.0):
    """A small porcelain cup on a saucer with rising steam; (x, y) = bottom centre of the saucer."""
    cv.push(x, y, scale=s)
    cv.ellipse(0, -2, 34, 8, (252, 248, 240), ink=INK, lw=2.2)
    cv.fill(spline([(-24, -8), (-26, -34), (-14, -46), (14, -46), (26, -34), (24, -8), (0, 0)], closed=True, n=3), (252, 248, 240), ink=INK, lw=2.4, shade_col=(218, 208, 196), depth=3)
    cv.ellipse(0, -44, 24, 6, (214, 150, 92), ink=INK, lw=1.8)
    cv.stroke([(-18, -26), (18, -26)], (240, 130, 150), 2.0, alpha=200)
    cv.stroke(spline([(24, -34), (38, -34), (36, -18), (22, -16)], n=3), INK, 5.5)
    cv.stroke(spline([(24, -34), (38, -34), (36, -18), (22, -16)], n=3), (244, 238, 228), 3)
    if steam > 0:
        for q in range(3):
            u = (t * 0.45 + q / 3) % 1.0
            cv.stroke(spline([(-6 + 8 * q + 3 * math.sin(u * 9 + q), -50 - 50 * u), (-6 + 8 * q + 8 * math.sin(u * 7 + q), -66 - 50 * u), (-6 + 8 * q + 4 * math.sin(u * 8 + q), -84 - 50 * u)], n=3),
                      (255, 255, 255), 4, alpha=int(150 * steam * (1 - u)))
    cv.pop()


def sweets(cv, x, y, s=1.0):
    """A little plate of colourful sweets."""
    cv.push(x, y, scale=s)
    cv.ellipse(0, 0, 50, 11, (252, 248, 240), ink=INK, lw=2.2)
    for i, (dx, col) in enumerate(((-26, (250, 170, 190)), (-6, (255, 214, 120)), (14, (170, 210, 150)), (32, (190, 160, 230)))):
        cv.ellipse(dx, -10 - (i % 2) * 3, 11, 10, col, ink=INK, lw=1.8)
        cv.ellipse(dx - 3, -14 - (i % 2) * 3, 3, 2.4, (255, 255, 255), ink=None, alpha=190)
    cv.pop()
