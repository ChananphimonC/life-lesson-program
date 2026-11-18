"""Small Pillow drawing toolkit: supersampled anti-aliased shapes, gradients,
glows, and reusable scenery pieces (hills, trees, furniture, etc.)."""

from __future__ import annotations

import math
import random

from PIL import Image, ImageDraw, ImageFilter, ImageFont

SS = 2
INK = (84, 62, 54)  # warm brown outline used by the illustration sheets


def mix(c1, c2, t):
    return tuple(int(round(a + (b - a) * t)) for a, b in zip(c1, c2))


def shade(c, f):
    return tuple(max(0, min(255, int(v * f))) for v in c[:3])


def smoothstep(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def ease_out_back(x):
    x = max(0.0, min(1.0, x))
    c1, c3 = 1.70158, 2.70158
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2


def vgradient(w, h, stops):
    """stops: list of (position 0..1, rgb)."""
    col = Image.new("RGB", (1, h))
    px = col.load()
    for y in range(h):
        p = y / max(1, h - 1)
        for (p0, c0), (p1, c1) in zip(stops, stops[1:]):
            if p0 <= p <= p1:
                px[0, y] = mix(c0, c1, (p - p0) / max(1e-6, p1 - p0))
                break
        else:
            px[0, y] = stops[-1][1] if p > stops[-1][0] else stops[0][1]
    return col.resize((w, h), Image.NEAREST)


def add_glow(img, cx, cy, radius, color, strength=0.6):
    """Soft radial light composited onto `img` (RGB or RGBA), computed at low
    resolution for speed."""
    k = 8
    w, h = img.size
    mask = Image.new("L", (max(1, w // k), max(1, h // k)), 0)
    d = ImageDraw.Draw(mask)
    r = radius / k
    d.ellipse((cx / k - r, cy / k - r, cx / k + r, cy / k + r), fill=int(255 * strength))
    mask = mask.filter(ImageFilter.GaussianBlur(r * 0.6)).resize((w, h), Image.BILINEAR)
    layer = Image.new(img.mode, img.size, color if img.mode == "RGB" else (*color, 255))
    return Image.composite(layer, img, mask)


def overlay_alpha(base, layer_draw_fn, alpha):
    """Draw with `layer_draw_fn(draw)` on a transparent layer and composite it
    onto `base` at the given opacity."""
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    layer_draw_fn(ImageDraw.Draw(layer))
    if alpha < 1:
        a = layer.getchannel("A").point(lambda v: int(v * alpha))
        layer.putalpha(a)
    out = base.convert("RGBA")
    out.alpha_composite(layer)
    return out.convert(base.mode)


def font(size, bold=True):
    for name in (("segoeuib.ttf", "arialbd.ttf") if bold else ("segoeui.ttf", "arial.ttf")):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default(size=size)


class Pen:
    """Supersampled drawing surface. All coordinates are in final pixels."""

    def __init__(self, w, h, base=None, mode="RGBA", ss=SS):
        self.w, self.h, self.ss = w, h, ss
        if base is not None:
            self.img = base.convert(mode).resize((w * ss, h * ss), Image.BILINEAR)
        else:
            self.img = Image.new(mode, (w * ss, h * ss), (0, 0, 0, 0) if mode == "RGBA" else (0, 0, 0))
        self.d = ImageDraw.Draw(self.img)

    def _s(self, v):
        return v * self.ss

    def _pts(self, pts):
        return [(x * self.ss, y * self.ss) for x, y in pts]

    def ellipse(self, cx, cy, rx, ry, fill, outline=None, width=0):
        s = self.ss
        self.d.ellipse((cx * s - rx * s, cy * s - ry * s, cx * s + rx * s, cy * s + ry * s),
                       fill=fill, outline=outline, width=int(width * s))

    def circle(self, cx, cy, r, fill, outline=None, width=0):
        self.ellipse(cx, cy, r, r, fill, outline, width)

    def rect(self, x0, y0, x1, y1, fill, radius=0, outline=None, width=0):
        s = self.ss
        box = (x0 * s, y0 * s, x1 * s, y1 * s)
        if radius:
            self.d.rounded_rectangle(box, radius=radius * s, fill=fill, outline=outline, width=int(width * s))
        else:
            self.d.rectangle(box, fill=fill, outline=outline, width=int(width * s))

    def poly(self, pts, fill, outline=None, width=0):
        self.d.polygon(self._pts(pts), fill=fill, outline=outline, width=int(width * self.ss) if outline else 0)

    def line(self, pts, color, width, round_caps=True):
        p = self._pts(pts)
        self.d.line(p, fill=color, width=max(1, int(width * self.ss)), joint="curve")
        if round_caps:
            r = width * self.ss / 2
            for x, y in (p[0], p[-1]):
                self.d.ellipse((x - r, y - r, x + r, y + r), fill=color)

    def arc(self, cx, cy, rx, ry, start, end, color, width):
        s = self.ss
        self.d.arc((cx * s - rx * s, cy * s - ry * s, cx * s + rx * s, cy * s + ry * s),
                   start, end, fill=color, width=max(1, int(width * s)))

    def chord(self, cx, cy, rx, ry, start, end, fill):
        s = self.ss
        self.d.chord((cx * s - rx * s, cy * s - ry * s, cx * s + rx * s, cy * s + ry * s), start, end, fill=fill)

    def vgrad_rect(self, x0, y0, x1, y1, stops, steps=60):
        for i in range(steps):
            t0, t1 = i / steps, (i + 1) / steps
            c = None
            mid = (t0 + t1) / 2
            for (p0, c0), (p1, c1) in zip(stops, stops[1:]):
                if p0 <= mid <= p1:
                    c = mix(c0, c1, (mid - p0) / max(1e-6, p1 - p0))
                    break
            c = c or stops[-1][1]
            self.rect(x0, y0 + (y1 - y0) * t0, x1, y0 + (y1 - y0) * t1 + 1, c)

    def text(self, x, y, s, size, fill, anchor="mm"):
        self.d.text((x * self.ss, y * self.ss), s, font=font(int(size * self.ss)), fill=fill, anchor=anchor)

    def result(self):
        return self.img.resize((self.w, self.h), Image.LANCZOS)


# --- scenery pieces ---------------------------------------------------------

def hills(pen, x0, x1, base_y, amp, color, period=900, phase=0.0, bottom=None):
    bottom = pen.h if bottom is None else bottom
    pts = [(x0, bottom)]
    x = x0
    while x <= x1:
        y = base_y - amp * (0.6 * math.sin(x / period * 2 * math.pi + phase)
                            + 0.4 * math.sin(x / (period * 0.43) * 2 * math.pi + phase * 1.7))
        pts.append((x, y))
        x += 20
    pts.append((x1, bottom))
    pen.poly(pts, color)


def stars(pen, x0, y0, x1, y1, n, seed=1, color=(255, 250, 230)):
    rnd = random.Random(seed)
    for _ in range(n):
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        r = rnd.choice((1.4, 1.8, 2.2, 3.0))
        pen.circle(x, y, r, mix(color, (180, 190, 230), rnd.random() * 0.4))


def tree(pen, x, ground_y, h=420, leaf=(110, 170, 120), trunk=(130, 95, 70)):
    ink = mix(shade(leaf, 0.45), INK, 0.5)
    ow = max(2.5, h * 0.008)
    pen.rect(x - h * 0.05 - ow, ground_y - h * 0.55, x + h * 0.05 + ow, ground_y + ow, ink, radius=h * 0.03)
    pen.rect(x - h * 0.05, ground_y - h * 0.55, x + h * 0.05, ground_y, trunk, radius=h * 0.03)
    blobs = ((-0.18, -0.62, 0.22), (0.2, -0.6, 0.22), (0, -0.78, 0.26), (-0.16, -0.86, 0.2), (0.18, -0.84, 0.2))
    for dx, dy, r in blobs:
        pen.circle(x + dx * h, ground_y + dy * h, r * h + ow, ink)
    dark = shade(leaf, 0.86)
    for i, (dx, dy, r) in enumerate(blobs):
        pen.circle(x + dx * h, ground_y + dy * h, r * h, dark if i < 2 else leaf)
    for dx, dy in ((-0.1, -0.7), (0.12, -0.92), (0.08, -0.62)):
        pen.arc(x + dx * h, ground_y + dy * h, h * 0.05, h * 0.035, 200, 340, ink, ow * 0.7)


def flower(pen, x, y, r=10, petal=(250, 190, 200), center=(250, 215, 110)):
    pen.line([(x, y), (x, y + r * 3)], (110, 160, 110), r * 0.35)
    for a in range(5):
        ang = a * 2 * math.pi / 5
        pen.circle(x + math.cos(ang) * r * 0.8, y + math.sin(ang) * r * 0.8, r * 0.6, petal)
    pen.circle(x, y, r * 0.45, center)


def city_skyline(pen, x0, x1, base_y, color, window=(255, 214, 140), seed=3, lit=0.35, max_h=380):
    rnd = random.Random(seed)
    x = x0
    dims = []
    while x < x1:
        w = rnd.randint(90, 190)
        h = rnd.randint(int(max_h * 0.35), max_h)
        pen.rect(x, base_y - h, x + w - 6, base_y, color)
        for wy in range(int(base_y - h + 24), int(base_y - 20), 34):
            for wx in range(int(x + 16), int(x + w - 26), 30):
                if rnd.random() < lit:
                    pen.rect(wx, wy, wx + 14, wy + 18, window)
                dims.append((wx, wy))
        x += w
    return dims


def car_sprite(color, scale=1.0):
    w, h = int(260 * scale), int(110 * scale)
    pen = Pen(w, h)
    s = scale
    pen.rect(8 * s, 40 * s, 252 * s, 88 * s, color, radius=20 * s)
    pen.poly([(60 * s, 44 * s), (90 * s, 10 * s), (180 * s, 10 * s), (215 * s, 44 * s)], shade(color, 0.92))
    pen.poly([(78 * s, 42 * s), (98 * s, 18 * s), (135 * s, 18 * s), (135 * s, 42 * s)], (200, 225, 245))
    pen.poly([(143 * s, 42 * s), (143 * s, 18 * s), (174 * s, 18 * s), (200 * s, 42 * s)], (200, 225, 245))
    for cx in (65, 195):
        pen.circle(cx * s, 88 * s, 20 * s, (45, 45, 55))
        pen.circle(cx * s, 88 * s, 8 * s, (170, 170, 180))
    pen.rect(236 * s, 52 * s, 250 * s, 62 * s, (255, 236, 160), radius=4 * s)
    return inked(pen.result(), max(2.0, 3.2 * s))


def card_sprite(kind, size=230):
    """White rounded 'post' card with a simple icon."""
    pad = 16
    pen = Pen(size + pad * 2, size + pad * 2)
    pen.rect(pad + 6, pad + 10, pad + size + 6, pad + size + 10, (0, 0, 0, 50), radius=34)
    pen.rect(pad, pad, pad + size, pad + size, (255, 253, 248), radius=34)
    cx, cy, u = pad + size / 2, pad + size / 2, size / 10
    if kind == "house":
        pen.poly([(cx - 3.2 * u, cy - 0.2 * u), (cx, cy - 3.2 * u), (cx + 3.2 * u, cy - 0.2 * u)], (232, 120, 100))
        pen.rect(cx - 2.5 * u, cy - 0.4 * u, cx + 2.5 * u, cy + 3 * u, (250, 220, 170))
        pen.rect(cx - 0.7 * u, cy + 1 * u, cx + 0.7 * u, cy + 3 * u, (150, 105, 80))
        pen.rect(cx + 1 * u, cy + 0.2 * u, cx + 2 * u, cy + 1.2 * u, (160, 205, 235))
    elif kind == "car":
        car = car_sprite((110, 160, 220), scale=size / 330)
        pen.img.alpha_composite(car.resize((car.width * SS, car.height * SS)),
                                (int((cx - car.width / 2) * SS), int((cy - car.height / 2) * SS)))
    elif kind == "briefcase":
        pen.rect(cx - 1.2 * u, cy - 2.6 * u, cx + 1.2 * u, cy - 1.4 * u, None, radius=0.4 * u,
                 outline=(120, 85, 60), width=0.45 * u)
        pen.rect(cx - 3.2 * u, cy - 1.8 * u, cx + 3.2 * u, cy + 2.6 * u, (150, 105, 75), radius=0.7 * u)
        pen.rect(cx - 3.2 * u, cy - 0.2 * u, cx + 3.2 * u, cy + 0.3 * u, (120, 85, 60))
        pen.rect(cx - 0.5 * u, cy - 0.5 * u, cx + 0.5 * u, cy + 0.6 * u, (240, 200, 110), radius=0.2 * u)
    elif kind == "trophy":
        pen.rect(cx - 2.4 * u, cy - 3 * u, cx + 2.4 * u, cy + 0.2 * u, (245, 195, 80), radius=1.4 * u)
        pen.rect(cx - 0.5 * u, cy, cx + 0.5 * u, cy + 1.6 * u, (225, 170, 60))
        pen.rect(cx - 1.8 * u, cy + 1.6 * u, cx + 1.8 * u, cy + 2.6 * u, (200, 150, 55), radius=0.3 * u)
        pen.arc(cx - 2.6 * u, cy - 1.6 * u, 1.1 * u, 1.1 * u, 90, 270, (245, 195, 80), 0.45 * u)
        pen.arc(cx + 2.6 * u, cy - 1.6 * u, 1.1 * u, 1.1 * u, 270, 90, (245, 195, 80), 0.45 * u)
    elif kind == "sparkle":
        for dx, dy, r, c in ((0, 0, 2.6, (240, 160, 180)), (-2.4, -2.2, 1.1, (250, 205, 110)),
                             (2.4, 2.0, 1.0, (140, 200, 230))):
            x, y, rr = cx + dx * u, cy + dy * u, r * u
            pen.poly([(x, y - rr), (x + rr * 0.28, y - rr * 0.28), (x + rr, y), (x + rr * 0.28, y + rr * 0.28),
                      (x, y + rr), (x - rr * 0.28, y + rr * 0.28), (x - rr, y), (x - rr * 0.28, y - rr * 0.28)], c)
    pen.circle(pad + size - 26, pad + 26, 9, (240, 120, 130))
    return inked(pen.result(), 3.0)


def signpost_sprite(scale=1.0):
    s = scale
    pen = Pen(int(420 * s), int(560 * s))
    wood, dark = (170, 125, 85), (130, 92, 62)
    pen.rect(196 * s, 90 * s, 224 * s, 560 * s, dark, radius=8 * s)
    pen.poly([(40 * s, 120 * s), (300 * s, 120 * s), (300 * s, 190 * s), (40 * s, 190 * s), (8 * s, 155 * s)], wood)
    pen.poly([(120 * s, 230 * s), (380 * s, 230 * s), (412 * s, 265 * s), (380 * s, 300 * s), (120 * s, 300 * s)], wood)
    pen.poly([(60 * s, 340 * s), (290 * s, 340 * s), (290 * s, 400 * s), (60 * s, 400 * s), (30 * s, 370 * s)], shade(wood, 0.92))
    for y in (155, 265, 370):
        pen.text(210 * s if y != 265 else 250 * s, y * s, "?", 44 * s, (250, 235, 205))
    return inked(pen.result(), 3.5 * s)


def ruler_sprite(length=1200, height=110):
    pen = Pen(length, height)
    pen.rect(0, 0, length, height, (248, 214, 110), radius=14)
    for i, x in enumerate(range(30, length - 20, 30)):
        h = 50 if i % 5 == 0 else 26
        pen.rect(x - 2, 0, x + 2, h, (150, 115, 60))
    return inked(pen.result(), 3.5)


def butterfly_sprite(open_wings=True, color=(245, 170, 120)):
    pen = Pen(60, 50)
    if open_wings:
        pen.ellipse(18, 18, 14, 12, color)
        pen.ellipse(42, 18, 14, 12, color)
        pen.ellipse(20, 34, 10, 8, shade(color, 0.9))
        pen.ellipse(40, 34, 10, 8, shade(color, 0.9))
    else:
        pen.ellipse(24, 22, 6, 14, color)
        pen.ellipse(36, 22, 6, 14, color)
    pen.rect(28, 12, 32, 42, (70, 60, 60), radius=2)
    return inked(pen.result(), 2.0)


def glow_sprite(radius, color, max_alpha=150):
    size = int(radius * 2)
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse((radius * 0.45, radius * 0.45, radius * 1.55, radius * 1.55), fill=max_alpha)
    mask = mask.filter(ImageFilter.GaussianBlur(radius * 0.32))
    spr = Image.new("RGBA", (size, size), (*color, 0))
    spr.putalpha(mask)
    return spr


def bubble_sprite(text="?", size=150, color=(255, 252, 240)):
    pen = Pen(size, size)
    pen.text(size / 2, size / 2, text, size * 0.78, color)
    return pen.result()


def inked(sprite, width=3.0, color=INK):
    """Give a flat sprite the sheets' outline: a dilated silhouette in `color`
    underneath it. The canvas grows by the outline width on every side."""
    pad = int(math.ceil(width)) + 1
    canvas = Image.new("RGBA", (sprite.width + 2 * pad, sprite.height + 2 * pad), (0, 0, 0, 0))
    canvas.paste(sprite, (pad, pad))
    solid = canvas.getchannel("A").point(lambda v: 255 if v > 110 else 0)
    ring = solid.filter(ImageFilter.MaxFilter(2 * int(round(width)) + 1)).filter(ImageFilter.GaussianBlur(0.6))
    out = Image.new("RGBA", canvas.size, (*color, 0))
    out.putalpha(ring)
    out.alpha_composite(canvas)
    return out


def with_opacity(sprite, alpha):
    if alpha >= 0.999:
        return sprite
    s = sprite.copy()
    s.putalpha(s.getchannel("A").point(lambda v: int(v * max(0.0, alpha))))
    return s


def paste(world, sprite, x, y, alpha=1.0):
    """Alpha-composite `sprite` with its top-left at (x, y)."""
    if alpha <= 0.01:
        return
    sprite = with_opacity(sprite, alpha)
    world.paste(sprite, (int(round(x)), int(round(y))), sprite)
