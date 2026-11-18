"""Prototype v2b drawing layer: smooth spline outlines on top of Pillow (no new dependency).

Why a new layer: the existing soft characters are built from circles and fixed polygons in one frontal
template (arms = chains of circles, hands = hexagons), which is what makes them look stiff. Here
  * every outline is a centripetal Catmull-Rom spline, so shapes are organic,
  * limbs are one tapered polygon (no visible joints) and hands are drawn as one silhouette with a thumb,
  * fills get a cel-shade crescent away from the light, clipped to the shape,
  * a tiny 2.5D model (stacked ellipse slices + yaw) lets one character be drawn front / 3/4 / side.

Coordinates are in figure units; Canvas.push() places/scales/rotates/flips them. Supersampled, then reduced.
"""

from __future__ import annotations

import math

import numpy as np
from PIL import Image, ImageDraw

INK = (86, 58, 52)


def mix(a, b, t):
    return tuple(int(round(x + (y - x) * t)) for x, y in zip(a, b))


def shade(c, f):
    return tuple(max(0, min(255, int(v * f))) for v in c[:3])


# --- curves ----------------------------------------------------------------------------------------------------------------

def spline(pts, closed=False, n=10):
    """Centripetal Catmull-Rom through pts (no overshoot, no cusps) -> dense list of (x, y)."""
    P = [np.asarray(p, float) for p in pts]
    if len(P) < 3 and not closed:
        return [tuple(p) for p in P]
    P = [P[-1]] + P + [P[0], P[1]] if closed else [2 * P[0] - P[1]] + P + [2 * P[-1] - P[-2]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        t0 = 0.0
        t1 = t0 + max(np.hypot(*(p1 - p0)), 1e-3) ** 0.5
        t2 = t1 + max(np.hypot(*(p2 - p1)), 1e-3) ** 0.5
        t3 = t2 + max(np.hypot(*(p3 - p2)), 1e-3) ** 0.5
        for t in np.linspace(t1, t2, n, endpoint=False):
            a1 = (t1 - t) / (t1 - t0) * p0 + (t - t0) / (t1 - t0) * p1
            a2 = (t2 - t) / (t2 - t1) * p1 + (t - t1) / (t2 - t1) * p2
            a3 = (t3 - t) / (t3 - t2) * p2 + (t - t2) / (t3 - t2) * p3
            b1 = (t2 - t) / (t2 - t0) * a1 + (t - t0) / (t2 - t0) * a2
            b2 = (t3 - t) / (t3 - t1) * a2 + (t - t1) / (t3 - t1) * a3
            out.append(tuple((t2 - t) / (t2 - t1) * b1 + (t - t1) / (t2 - t1) * b2))
    if not closed:
        out.append(tuple(P[-2]))
    return out


def chain(*segments, n=10):
    """Open splines joined end to end: a corner wherever one segment ends and the next begins."""
    out = []
    for seg in segments:
        s = spline(seg, n=n) if len(seg) > 2 else [tuple(map(float, p)) for p in seg]
        out += s[1:] if out else s
    return out


def tube(center, width, n=8):
    """A tapered stroke as one closed outline. width: number or f(t in 0..1) -> width. Round ends."""
    c = np.array(spline(center, n=n) if len(center) > 2 else center, float)
    if len(c) == 2:
        c = np.linspace(c[0], c[1], 8)
    seg = np.diff(c, axis=0)
    L = np.concatenate([[0], np.cumsum(np.hypot(seg[:, 0], seg[:, 1]))])
    t = L / max(L[-1], 1e-6)
    w = np.array([width(x) if callable(width) else width for x in t]) / 2
    tan = np.gradient(c, axis=0)
    tan /= np.maximum(np.hypot(tan[:, 0], tan[:, 1]), 1e-9)[:, None]
    nor = np.stack([-tan[:, 1], tan[:, 0]], 1)
    left, right = c + nor * w[:, None], c - nor * w[:, None]

    def cap(p, d, r, k=7):
        a0 = math.atan2(d[1], d[0])
        return [(p[0] + r * math.cos(a0 + math.pi / 2 - math.pi * i / k), p[1] + r * math.sin(a0 + math.pi / 2 - math.pi * i / k))
                for i in range(1, k)]
    end = cap(c[-1], tan[-1], w[-1])
    start = cap(c[0], -tan[0], w[0])
    return [tuple(p) for p in left] + end + [tuple(p) for p in right[::-1]] + start


def ellipse_pts(cx, cy, rx, ry, rot=0.0, n=48, a0=0.0, a1=360.0):
    c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    out = []
    for i in range(n + 1 if a1 - a0 < 360 else n):
        a = math.radians(a0 + (a1 - a0) * i / n)
        x, y = rx * math.cos(a), ry * math.sin(a)
        out.append((cx + x * c - y * s, cy + x * s + y * c))
    return out


# --- 2.5D: yaw about the vertical axis (theta > 0 turns the figure to face screen-right) ------------------------------------

def yaw(p, th):
    x, y, z = p
    c, s = math.cos(th), math.sin(th)
    return (x * c + z * s, y, -x * s + z * c)


def lathe(slices, th, n=6):
    """Silhouette of stacked horizontal ellipses (y, a = half width, b = half depth, z0 = depth centre)."""
    right, left = [], []
    c, s = math.cos(th), math.sin(th)
    for y, a, b, z0 in slices:
        half = math.sqrt((a * c) ** 2 + (b * s) ** 2)
        right.append((z0 * s + half, y))
        left.append((z0 * s - half, y))
    return spline(right, n=n) + spline(left[::-1], n=n)


def slice_point(y, a, b, z0, phi, th):
    """Point at azimuth phi (0 = front) on an ellipse slice, after yaw -> (x', y, visibility -1..1)."""
    p = (a * math.sin(phi), y, z0 + b * math.cos(phi))
    nx, nz = b * math.sin(phi), a * math.cos(phi)
    k = math.hypot(nx, nz) or 1
    q = yaw(p, th)
    vis = yaw((nx / k, 0, nz / k), th)[2]
    return (q[0], q[1]), vis


# --- canvas ------------------------------------------------------------------------------------------------------------------

class Canvas:
    def __init__(self, w, h, ss=4, bg=(0, 0, 0, 0)):
        self.w, self.h, self.ss = w, h, ss
        self.img = Image.new("RGBA", (w * ss, h * ss), bg)
        self.draw = ImageDraw.Draw(self.img)
        self.stack = [np.eye(3)]

    # transforms
    def push(self, tx=0.0, ty=0.0, rot=0.0, scale=1.0, flip=False, pivot=None):
        """Compose: move to (tx, ty), rotate `rot` degrees about `pivot` (local), scale, mirror horizontally."""
        m = np.eye(3)
        m[0, 2], m[1, 2] = tx, ty
        r = math.radians(rot)
        R = np.array([[math.cos(r), -math.sin(r), 0], [math.sin(r), math.cos(r), 0], [0, 0, 1]])
        S = np.diag([-scale if flip else scale, scale, 1])
        if pivot is not None:
            P, Pi = np.eye(3), np.eye(3)
            P[0, 2], P[1, 2] = pivot
            Pi[0, 2], Pi[1, 2] = -pivot[0], -pivot[1]
            R = P @ R @ Pi
        self.stack.append(self.stack[-1] @ m @ S @ R)

    def pop(self):
        self.stack.pop()

    @property
    def k(self):
        m = self.stack[-1]
        return math.sqrt(abs(m[0, 0] * m[1, 1] - m[0, 1] * m[1, 0]))

    def T(self, pts):
        m = self.stack[-1]
        a = np.asarray(pts, float).reshape(-1, 2)
        x = (m[0, 0] * a[:, 0] + m[0, 1] * a[:, 1] + m[0, 2]) * self.ss
        y = (m[1, 0] * a[:, 0] + m[1, 1] * a[:, 1] + m[1, 2]) * self.ss
        return list(zip(x.tolist(), y.tolist()))

    # drawing
    def fill(self, pts, col, ink=INK, lw=3.0, shade_col=None, light=(-1.0, -1.1), depth=7.0, alpha=255):
        """Filled outline. shade_col: a crescent of this colour on the side away from the light."""
        if len(pts) < 3:
            return
        poly = self.T(pts)
        col4 = (*col[:3], alpha)
        if shade_col is None and alpha < 255:          # ImageDraw overwrites alpha; blend through a layer instead
            self._blend(lambda d, o: d.polygon([(x - o[0], y - o[1]) for x, y in poly], fill=col4), poly)
        elif shade_col is None:
            self.draw.polygon(poly, fill=col4)
        else:
            xs, ys = [p[0] for p in poly], [p[1] for p in poly]
            x0, y0 = int(min(xs)) - 2, int(min(ys)) - 2
            x1, y1 = int(max(xs)) + 3, int(max(ys)) + 3
            if x1 - x0 < 2 or y1 - y0 < 2:
                return
            loc = [(x - x0, y - y0) for x, y in poly]
            mask = Image.new("L", (x1 - x0, y1 - y0), 0)
            ImageDraw.Draw(mask).polygon(loc, fill=alpha)
            lay = Image.new("RGBA", mask.size, (*shade_col[:3], 255))
            dd = ImageDraw.Draw(lay)
            off = depth * self.k * self.ss
            n = math.hypot(*light)
            ox, oy = light[0] / n * off, light[1] / n * off
            dd.polygon([(x + ox, y + oy) for x, y in loc], fill=(*col[:3], 255))
            lay.putalpha(mask)
            self.img.alpha_composite(lay, (x0, y0))
        if ink:
            self.stroke(pts, ink, lw, closed=True)

    def stroke(self, pts, col, lw=3.0, closed=False, alpha=255):
        if len(pts) < 2:
            return
        p = self.T(pts)
        if closed:
            p = p + p[:2]
        w = max(1, int(round(lw * self.k * self.ss)))
        c4 = (*col[:3], alpha)

        def paint(d, o):
            q = [(x - o[0], y - o[1]) for x, y in p]
            d.line(q, fill=c4, width=w, joint="curve")
            if not closed:
                r = w / 2
                for x, y in (q[0], q[-1]):
                    d.ellipse((x - r, y - r, x + r, y + r), fill=c4)
        if alpha < 255:
            self._blend(paint, p, pad=w)
        else:
            paint(self.draw, (0, 0))

    def _blend(self, paint, pts, pad=4):
        xs, ys = [q[0] for q in pts], [q[1] for q in pts]
        x0, y0 = max(0, int(min(xs)) - pad), max(0, int(min(ys)) - pad)
        x1, y1 = min(self.img.width, int(max(xs)) + pad + 2), min(self.img.height, int(max(ys)) + pad + 2)
        if x1 <= x0 or y1 <= y0:
            return
        lay = Image.new("RGBA", (x1 - x0, y1 - y0), (0, 0, 0, 0))
        paint(ImageDraw.Draw(lay), (x0, y0))
        self.img.alpha_composite(lay, (x0, y0))

    def taper(self, pts, w0, w1, col, wmid=None):
        """Brush stroke: width w0 -> (wmid) -> w1, no outline."""
        f = (lambda t: w0 + (w1 - w0) * t) if wmid is None else \
            (lambda t: (w0 + (wmid - w0) * t * 2) if t < 0.5 else (wmid + (w1 - wmid) * (t - 0.5) * 2))
        self.fill(tube(pts, f), col, ink=None)

    def ellipse(self, cx, cy, rx, ry, col, ink=None, lw=3.0, rot=0.0, shade_col=None, alpha=255):
        self.fill(ellipse_pts(cx, cy, rx, ry, rot), col, ink=ink, lw=lw, shade_col=shade_col, alpha=alpha)

    def result(self, size=None):
        return self.img.resize(size or (self.w, self.h), Image.LANCZOS)
