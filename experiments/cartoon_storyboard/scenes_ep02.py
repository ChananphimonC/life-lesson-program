"""Scenes for EP02 "เงาของความเร่งรีบ": feeling alone in a crowded city.

Same drawn style and conventions as `scenes.py` (local time `t`, events in
`self.ev`, camera returns (cx, cy, view width)).
"""

from __future__ import annotations

import math
import random

from PIL import Image, ImageDraw, ImageFilter

import art
import character as C
from art import INK, Pen, inked, mix, paste, shade, smoothstep
from scenes import DUSK, NIGHT, Scene, _cache, lerp, place, sprite, walker

DUSK_CROWD = (0.86, 0.78, 0.86)
NIGHT_SOFT = (0.86, 0.88, 1.0)


# --- shared drawing ---------------------------------------------------------------

def building(pen, x0, x1, top, base, color, lit=0.4, seed=0, win=(255, 224, 160), dark=None,
             cell=(56, 70), ow=4):
    rnd = random.Random(seed)
    dark = dark or shade(color, 0.78)
    pen.rect(x0 - ow, top - ow, x1 + ow, base, INK, radius=8)
    pen.rect(x0, top, x1, base, color, radius=5)
    pen.rect(x0, top, x1, top + 18, shade(color, 0.9), radius=5)
    for y in range(top + 40, base - 70, cell[1]):
        for x in range(x0 + 26, x1 - 50, cell[0]):
            pen.rect(x, y, x + 30, y + 40, win if rnd.random() < lit else dark, radius=3)


def lamp_post(pen, x, ground, h=520, ink=INK, pole=(92, 96, 116), light=(255, 232, 170)):
    pen.rect(x - 9, ground - h, x + 9, ground, ink, radius=6)
    pen.rect(x - 5, ground - h, x + 5, ground, pole, radius=4)
    pen.rect(x - 8, ground - h - 6, x + 70, ground - h + 8, ink, radius=6)
    pen.ellipse(x + 62, ground - h + 14, 28, 16, ink)
    pen.ellipse(x + 62, ground - h + 14, 23, 11, light)


def train_car(length=1900, height=560, night=False):
    """Side view of a skytrain car (inked) and its door centers (x in sprite px)."""
    key = ("train_car", length, height, night)

    def make():
        pen = Pen(length, height)
        body, stripe = (234, 236, 240), (64, 148, 116)
        pen.rect(0, 16, length, height - 30, body, radius=70)
        pen.rect(0, height - 170, length, height - 128, stripe)
        pen.rect(30, height - 40, length - 30, height, (70, 72, 84), radius=10)
        doors = [length * 0.25, length * 0.75]
        glass = (255, 230, 170) if night else (150, 182, 210)
        for x0, x1 in ((60, doors[0] - 140), (doors[0] + 140, doors[1] - 140), (doors[1] + 140, length - 60)):
            pen.rect(x0, 100, x1, 300, INK, radius=24)
            pen.rect(x0 + 6, 106, x1 - 6, 294, glass, radius=20)
            if not night:
                pen.poly([(x0 + 40, 294), (x0 + 120, 106), (x0 + 170, 106), (x0 + 90, 294)], (178, 204, 226))
        for d in doors:
            pen.rect(d - 106, 70, d + 106, height - 40, INK, radius=10)
            pen.rect(d - 100, 76, d + 100, height - 40, (58, 62, 80) if not night else (250, 220, 160), radius=8)
        return inked(pen.result(), 4), doors

    return _cache.get(key, make)


def door_panel(height=444, width=100, night=False):
    def make():
        pen = Pen(width, height)
        pen.rect(0, 0, width, height, (226, 230, 236), radius=6)
        pen.rect(18, 40, width - 18, 230, INK, radius=12)
        pen.rect(22, 44, width - 22, 226, (255, 230, 170) if night else (150, 182, 210), radius=10)
        return inked(pen.result(), 3)
    return _cache.get(("door_panel", height, width, night), make)


def thought_cloud(size):
    def make():
        h = int(size * 0.72)
        pen = Pen(size, h)
        blobs = [(0.3, 0.56, 0.2), (0.5, 0.42, 0.26), (0.72, 0.54, 0.21), (0.52, 0.64, 0.22)]
        ow = max(3, size * 0.018)
        for x, y, r in blobs:
            pen.circle(x * size, y * h, r * size + ow, INK)
        for x, y, r in blobs:
            pen.circle(x * size, y * h, r * size, (255, 252, 246))
        for x in (0.38, 0.51, 0.64):
            pen.circle(x * size, 0.56 * h, size * 0.034, INK)
        return pen.result()
    return _cache.get(("thought", size), make)


def ring(world, cx, cy, r, color, alpha, width):
    """A soft-edged translucent ring composited onto an RGB world."""
    if alpha <= 0.01 or r <= 1:
        return
    pad = width + 4
    size = int(2 * (r + pad))
    layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    ImageDraw.Draw(layer).ellipse((pad, pad, size - pad, size - pad), outline=(*color, int(255 * alpha)),
                                  width=int(width))
    layer = layer.filter(ImageFilter.GaussianBlur(1.2))
    world.paste(layer, (int(cx - r - pad), int(cy - r - pad)), layer)


class Crowd:
    """People walking across the frame in lanes, wrapping around the world."""

    def __init__(self, W, n, seed, lanes, speed=(150, 230), both=True, stride=22.0):
        rnd = random.Random(seed)
        self.W, self.people = W, []
        for i in range(n):
            y, s = lanes[i % len(lanes)]
            self.people.append({
                "x0": rnd.uniform(0, W + 600), "y": y + rnd.uniform(-14, 14),
                "s": round(s * rnd.uniform(0.95, 1.05), 1), "v": rnd.uniform(*speed),
                "f": rnd.choice((1, -1)) if both else 1, "ph": rnd.random(),
                "pal": C.OTHERS[(i * 3 + seed) % len(C.OTHERS)], "stride": stride})

    def draw(self, world, t, split_y=None, behind=True, alpha=1.0, tint=None):
        for p in sorted(self.people, key=lambda p: p["y"]):
            if split_y is not None and (p["y"] > split_y) == behind:
                continue
            d = p["v"] * t
            x = (p["x0"] + p["f"] * d) % (self.W + 600) - 300
            phase = p["ph"] + d / (31.0 * p["s"] * p["stride"] / 22.0)
            spr = walker("crowd", phase, p["pal"], p["s"], facing=p["f"], tint=tint, stride=p["stride"])
            place(world, spr, x, p["y"], p["s"], facing=p["f"], alpha=alpha)


def main_front(t, scale, tint=None, look=(0.0, 0.6), offset=0.0):
    return sprite("ep2_front", C.stand, C.MAIN, scale, 1, tint=tint, view="front", look=look,
                  blink=C.blink_at(t, offset=offset))


# --- station -------------------------------------------------------------------------

WALL, SIGN = (222, 224, 230), (70, 118, 168)


def station_bg(W, H, glass=True):
    pen = Pen(W, H, base=art.vgradient(W, H, [(0, (228, 230, 234)), (1, (216, 218, 224))]))
    pen.rect(0, 0, W, 200, (84, 90, 110))
    for x in range(100, W, 440):
        pen.rect(x, 82, x + 260, 120, (255, 244, 214), radius=12)
    pen.rect(0, 196, W, 206, INK)
    for x in range(0, W, 120):
        pen.rect(x, 206, x + 3, 470, (204, 208, 216))
    pen.rect(0, 300, W, 372, SIGN)
    pen.rect(0, 296, W, 302, INK)
    pen.rect(0, 370, W, 376, INK)
    for x in range(320, W, 900):
        pen.rect(x - 4, 312, x + 84, 362, INK, radius=14)
        pen.rect(x, 316, x + 80, 358, (246, 248, 250), radius=12)
        pen.rect(x + 10, 324, x + 34, 340, SIGN, radius=3)
        pen.rect(x + 46, 324, x + 70, 340, SIGN, radius=3)
        pen.poly([(x + 110, 326), (x + 150, 326), (x + 150, 316), (x + 176, 337), (x + 150, 358),
                  (x + 150, 348), (x + 110, 348)], (246, 248, 250))
    sx = W / 2
    pen.rect(sx - 34, 214, sx + 34, 272, INK, radius=10)
    pen.rect(sx - 30, 218, sx + 30, 268, (70, 74, 90), radius=8)
    pen.circle(sx, 243, 16, (150, 156, 172))
    pen.rect(0, 466, W, 476, INK)
    pen.rect(0, 476, W, 1080, (50, 54, 70))
    pen.rect(0, 1026, W, 1040, (122, 126, 140))
    if glass:
        pen.rect(0, 556, W, 600, (186, 192, 204))
        pen.rect(0, 552, W, 558, INK)
        for x in range(0, W, 300):
            pen.rect(x + 6, 600, x + 294, 1080, INK)
            pen.rect(x + 12, 606, x + 288, 1080, (86, 108, 124))
            pen.poly([(x + 40, 1080), (x + 160, 606), (x + 200, 606), (x + 80, 1080)], (100, 124, 140))
    pen.rect(0, 1080, W, H, (218, 210, 198))
    pen.rect(0, 1076, W, 1086, INK)
    pen.rect(0, 1100, W, 1128, (238, 196, 84))
    for x in range(10, W, 36):
        pen.circle(x, 1114, 5, (214, 170, 62))
    for x in range(0, W, 200):
        pen.rect(x, 1128, x + 3, H, (206, 198, 186))
    return art.add_glow(pen.result(), W / 2, 100, 600, (255, 246, 222), 0.25)


def speaker_pulse(world, t, cx, cy=243):
    d = ImageDraw.Draw(world)
    for k in range(3):
        p = (t - k * 0.35) % 3.2
        if p > 1.2:
            continue
        r = 46 + 70 * p
        c = mix(SIGN, WALL, p / 1.2)
        d.arc((cx - r, cy - r, cx + r, cy + r), -38, 38, fill=c, width=7)
        d.arc((cx - r, cy - r, cx + r, cy + r), 142, 218, fill=c, width=7)


class StationCrowd(Scene):
    W = 3000
    MAIN_X, MAIN_Y, S = 1500, 1222, 5.6
    LANES = [(1150, 4.8), (1300, 6.0)]

    def __init__(self, duration, events=None):
        super().__init__(duration, events)
        self.crowd = Crowd(self.W, 14, 5, self.LANES, speed=(150, 230))

    def build(self):
        return station_bg(self.W, self.H, glass=True)

    def crowd_alpha(self, t):
        return 1.0

    def compose(self, t, world):
        speaker_pulse(world, t, self.W / 2)
        a = self.crowd_alpha(t)
        self.crowd.draw(world, t, self.MAIN_Y, True, alpha=a)
        self.extra(t, world)
        place(world, main_front(t, self.S), self.MAIN_X, self.MAIN_Y, self.S)
        self.crowd.draw(world, t, self.MAIN_Y, False, alpha=a)

    def extra(self, t, world):
        pass

    def camera(self, t):
        u = self.u(t)
        return self.MAIN_X, lerp(675, 720, u), lerp(2400, 2050, u)


class StationQuiet(StationCrowd):
    def quiet(self, t):
        return smoothstep((t - self.ev.get("quiet", self.duration * 0.4) + 0.3) / 1.8)

    def crowd_alpha(self, t):
        return 1.0 - 0.72 * self.quiet(t)

    def extra(self, t, world):
        q = self.quiet(t)
        if q > 0.01:
            glow = _cache.get("ep2_quiet_glow", lambda: art.glow_sprite(520, (255, 240, 205), 170))
            paste(world, glow, self.MAIN_X - 520, self.MAIN_Y - 52 * self.S - 520, q)

    def camera(self, t):
        u = self.u(t)
        return self.MAIN_X, lerp(720, 860, u), lerp(2050, 1350, u)


# --- city pavement: everyone rushing, we turn see-through -----------------------------

class RushPast(Scene):
    W = 3000
    MAIN_X, MAIN_Y, S = 1500, 1222, 5.6

    def __init__(self, duration, events=None):
        super().__init__(duration, events)
        self.crowd = Crowd(self.W, 16, 11, [(1150, 4.8), (1300, 6.0)], speed=(270, 360))

    def build(self):
        W, H = self.W, self.H
        pen = Pen(W, H, base=art.vgradient(W, H, [(0, (196, 214, 228)), (0.7, (238, 230, 216)), (1, (238, 230, 216))]))
        art.city_skyline(pen, 0, W, 760, (204, 210, 222), window=(222, 228, 236), lit=0.3, max_h=420, seed=2)
        rnd = random.Random(8)
        colors = [(226, 190, 160), (180, 198, 210), (216, 206, 178), (198, 178, 192), (172, 194, 172), (232, 214, 190)]
        x = -40
        i = 0
        while x < W:
            w = rnd.randint(320, 520)
            building(pen, x, x + w - 24, rnd.randint(300, 640), 1080, colors[i % len(colors)], lit=0.15, seed=i,
                     win=(250, 240, 214), dark=(150, 176, 198))
            x += w
            i += 1
        pen.rect(0, 1080, W, H, (210, 204, 196))
        pen.rect(0, 1076, W, 1086, INK)
        for gx in range(0, W, 180):
            pen.rect(gx, 1086, gx + 3, H, (196, 190, 182))
        for lx in (420, 1300, 2200):
            lamp_post(pen, lx, 1090)
        return pen.result()

    def ghost(self, t):
        return smoothstep((t - self.ev.get("ghost", self.duration * 0.5) + 0.2) / 1.6)

    def compose(self, t, world):
        self.crowd.draw(world, t, self.MAIN_Y, True)
        place(world, main_front(t, self.S, look=(0.0, 1.4), offset=0.8), self.MAIN_X, self.MAIN_Y, self.S,
              alpha=1.0 - 0.5 * self.ghost(t))
        self.crowd.draw(world, t, self.MAIN_Y, False)

    def camera(self, t):
        u = self.u(t)
        return self.MAIN_X, lerp(690, 760, u), lerp(2400, 1900, u)


# --- alone in a dark room ---------------------------------------------------------------

class DarkRoom(Scene):
    X, GROUND, S = 1050, 1110, 6.2

    def build(self):
        W, H = self.W, self.H
        pen = Pen(W, H, base=art.vgradient(W, H, [(0, (40, 42, 70)), (1, (32, 34, 60))]))
        pen.rect(0, 1100, W, H, (30, 30, 52))
        pen.rect(0, 1096, W, 1104, (22, 22, 40))
        pen.rect(282, 182, 818, 718, INK)
        pen.vgrad_rect(290, 190, 810, 710, [(0, (26, 34, 70)), (1, (58, 66, 112))])
        art.stars(pen, 300, 200, 800, 520, 30, seed=3)
        for y in range(214, 700, 34):
            pen.rect(290, y, 810, y + 12, (70, 74, 110))
        for i, y in enumerate(range(1150, 1340, 46)):
            pen.poly([(300 + i * 60, y), (820 + i * 60, y), (860 + i * 60, y + 18), (340 + i * 60, y + 18)], (48, 50, 84))
        # bed
        pen.rect(1594, 760, 2266, 1100, INK, radius=34)
        pen.rect(1600, 766, 2260, 1100, (82, 64, 72), radius=30)
        pen.rect(1494, 914, 2266, 1006, INK, radius=24)
        pen.rect(1500, 920, 2260, 1000, (96, 104, 140), radius=22)
        pen.rect(2050, 856, 2236, 924, INK, radius=24)
        pen.rect(2056, 862, 2230, 918, (140, 146, 176), radius=20)
        # unlit lamp on a stool
        pen.rect(1380, 900, 1480, 1100, INK, radius=6)
        pen.rect(1386, 906, 1474, 1100, (70, 58, 70), radius=4)
        pen.poly([(1392, 900), (1468, 900), (1450, 820), (1410, 820)], (110, 110, 132))
        img = pen.result()
        return art.add_glow(img, 550, 450, 320, (150, 170, 230), 0.25)

    def compose(self, t, world):
        spr = sprite("ep2_hug", C.hug_knees, C.MAIN, self.S, 1, tint=NIGHT, blink=C.blink_at(t, offset=1.3),
                     look=(1.2, 1.4))
        place(world, spr, self.X, self.GROUND, self.S)

    def camera(self, t):
        u = self.u(t)
        return lerp(1200, 1120, u), lerp(675, 700, u), lerp(2400, 1900, u)


# --- inside a crowded train: everyone connected to a screen, not to each other ---------

class TrainInterior(Scene):
    WINDOWS = [(150, 710), (930, 1490), (1710, 2270)]
    RIDERS = [(330, 5.6), (760, 5.9), (1720, 5.8), (2110, 5.6)]
    MAIN_X, GROUND, S = 1230, 1300, 5.9

    def build(self):
        W, H = self.W, self.H
        pen = Pen(W, H, base=art.vgradient(W, H, [(0, (236, 232, 222)), (1, (226, 220, 208))]))
        pen.rect(0, 0, W, 170, (212, 208, 198))
        pen.rect(0, 120, W, 148, (255, 250, 236))
        pen.rect(0, 166, W, 174, INK)
        pen.rect(0, 204, W, 228, INK, radius=10)
        pen.rect(0, 208, W, 224, (176, 182, 192), radius=8)
        for x0, x1 in self.WINDOWS:
            pen.rect(x0 - 16, 284, x1 + 16, 716, INK, radius=16)
            pen.rect(x0 - 10, 290, x1 + 10, 710, (200, 204, 212), radius=12)
        pen.rect(0, 760, W, 792, (90, 150, 190))
        for x0, x1 in self.WINDOWS:
            pen.rect(x0 - 6, 934, x1 + 6, 1050, INK, radius=26)
            pen.rect(x0, 940, x1, 1044, (96, 130, 180), radius=22)
            pen.rect(x0, 1044, x1, 1100, (70, 72, 86))
        pen.rect(0, 1160, W, H, (156, 156, 166))
        pen.rect(0, 1156, W, 1164, INK)
        img = pen.result()
        self.strip = self._skyline_strip()
        return img

    @staticmethod
    def _skyline_strip():
        def make():
            w, h = 5200, 420
            pen = Pen(w, h, base=art.vgradient(w, h, [(0, (120, 104, 168)), (0.55, (236, 160, 132)),
                                                      (1, (252, 204, 160))]), ss=1)
            pen.circle(1400, 250, 70, (255, 226, 170))
            art.city_skyline(pen, 0, w, 420, (96, 84, 128), window=(255, 214, 150), lit=0.3, max_h=300, seed=6)
            art.city_skyline(pen, 0, w, 420, (72, 64, 104), window=(255, 220, 160), lit=0.25, max_h=170, seed=9)
            return pen.result().convert("RGB")
        return _cache.get("ep2_strip", make)

    def head(self, x, s):
        return x, self.GROUND - 80 * s

    def compose(self, t, world):
        off = int(t * 320) % (self.strip.width - 2600)
        for x0, x1 in self.WINDOWS:
            world.paste(self.strip.crop((off + x0, 0, off + x1, 420)), (x0, 290))
        d = ImageDraw.Draw(world)
        for i, x in enumerate(range(120, self.W, 240)):
            a = math.radians(5 * math.sin(t * 2.2 + i * 0.7))
            ex, ey = x + 110 * math.sin(a), 224 + 110 * math.cos(a)
            d.line((x, 224, ex, ey), fill=INK, width=12)
            d.line((x, 224, ex, ey), fill=(206, 208, 214), width=6)
            d.ellipse((ex - 22, ey - 4, ex + 22, ey + 40), outline=INK, width=8)
        for i, (x, s) in enumerate(self.RIDERS):
            pal = C.OTHERS[(i * 2 + 1) % len(C.OTHERS)]
            spr = sprite("ep2_rider", C.front_phone, pal, s, 1, blink=C.blink_at(t, offset=i * 0.9))
            place(world, spr, x, self.GROUND, s)
        place(world, main_front(t, self.S, look=(2.2, 0.2), offset=0.4), self.MAIN_X, self.GROUND, self.S)
        self.links(t, world)

    def links(self, t, world):
        te = self.ev.get("lines")
        if te is None or t < te:
            return
        dt = t - te
        grow = smoothstep(dt / 0.9)
        fade = 1.0 - smoothstep((dt - 3.2) / 1.0)
        gap = smoothstep((dt - 1.4) / 1.2)
        if fade <= 0:
            return
        d = ImageDraw.Draw(world)
        mx, my = self.head(self.MAIN_X, self.S)
        bg = (232, 226, 214)
        for x, s in self.RIDERS:
            hx, hy = self.head(x, s)
            n = 22
            for k in range(1, n):
                f = k / n
                if f > grow:
                    break
                if abs(f - 0.5) < 0.22 * gap:
                    continue
                px = lerp(mx, hx, f)
                py = lerp(my - 120, hy - 120, f) - 130 * math.sin(math.pi * f)
                c = mix(bg, (232, 150, 90), fade)
                d.ellipse((px - 7, py - 7, px + 7, py + 7), fill=c)

    def camera(self, t):
        u = self.u(t)
        return (lerp(1200, 1230, u) + 8 * math.sin(t * 2.1), lerp(690, 740, u) + 4 * math.sin(t * 3.3),
                lerp(2400, 2150, u))


# --- dusk pavement: walking slowly while everyone overtakes ----------------------------

class LoudThoughts(Scene):
    W = 4200
    X0, SPEED, GROUND, S = 900, 70, 1225, 5.6

    def __init__(self, duration, events=None):
        super().__init__(duration, events)
        self.crowd = Crowd(self.W, 14, 23, [(1150, 4.8), (1300, 6.0)], speed=(240, 330), both=False)

    def build(self):
        W, H = self.W, self.H
        pen = Pen(W, H, base=art.vgradient(W, H, [(0, (104, 100, 170)), (0.55, (236, 156, 130)),
                                                  (0.8, (252, 204, 160)), (1, (252, 204, 160))]))
        art.city_skyline(pen, 0, W, 820, (150, 112, 150), window=(255, 214, 150), lit=0.25, max_h=420, seed=12)
        rnd = random.Random(4)
        colors = [(150, 120, 150), (128, 112, 150), (164, 128, 140), (120, 104, 136)]
        x, i = -40, 0
        while x < W:
            w = rnd.randint(320, 560)
            building(pen, x, x + w - 24, rnd.randint(320, 620), 1080, colors[i % len(colors)], lit=0.45,
                     seed=40 + i, win=(255, 214, 150))
            x += w
            i += 1
        pen.rect(0, 1080, W, H, (150, 128, 140))
        pen.rect(0, 1076, W, 1086, INK)
        for gx in range(0, W, 180):
            pen.rect(gx, 1086, gx + 3, H, (138, 118, 130))
        img = None
        lamps = list(range(600, W, 1000))
        for lx in lamps:
            lamp_post(pen, lx, 1090)
        img = pen.result()
        for lx in lamps:
            img = art.add_glow(img, lx + 62, 1090 - 506, 160, (255, 226, 160), 0.45)
        return img

    def main_x(self, t):
        return self.X0 + self.SPEED * t

    def compose(self, t, world):
        x = self.main_x(t)
        self.crowd.draw(world, t, self.GROUND, True, tint=DUSK_CROWD)
        echo = self.ev.get("echo")
        if echo is not None and t > echo:
            for k in range(4):
                p = ((t - echo) - k * 0.55) % 2.2
                if t - echo >= k * 0.55:
                    ring(world, x, self.GROUND - 50 * self.S, 120 + 520 * p / 2.2, (255, 236, 214),
                         0.55 * (1 - p / 2.2), 6)
        spr = walker("ep2_walk", t / 1.45, C.MAIN, self.S, tint=DUSK, stride=15.0, look=(1.3, 0.8))
        place(world, spr, x, self.GROUND, self.S)
        self.crowd.draw(world, t, self.GROUND, False, tint=DUSK_CROWD)
        self.thoughts(t, world, x)

    def thoughts(self, t, world, x):
        loud = self.ev.get("loud", self.duration * 0.5)
        grow = smoothstep((t - loud + 0.2) / 1.2)
        hx, hy = x + 40, self.GROUND - 100 * self.S
        d = ImageDraw.Draw(world)
        for k, (dx, dy, r) in enumerate(((34, -10, 9), (58, -44, 13))):
            px, py = hx + dx, hy + dy + 4 * math.sin(t * 2 + k)
            d.ellipse((px - r - 4, py - r - 4, px + r + 4, py + r + 4), fill=INK)
            d.ellipse((px - r, py - r, px + r, py + r), fill=(255, 252, 246))
        clouds = [(110, -150, 150 + 110 * grow, 0.0)]
        if grow > 0:
            clouds += [(-170, -240, 110 * grow, 0.3), (260, -300, 130 * grow, 0.6)]
        for dx, dy, size, ph in clouds:
            size = int(size / 10) * 10
            if size < 30:
                continue
            c = thought_cloud(size)
            paste(world, c, hx + dx - size / 2, hy + dy - c.height / 2 + 8 * math.sin(t * 1.4 + ph * 6))

    def camera(self, t):
        return self.main_x(t) + 250, lerp(690, 660, self.u(t)), 2300


# --- the city that never stops ---------------------------------------------------------

class CityFlow(Scene):
    W = 3200
    MAIN_X, GROUND, S = 760, 1318, 4.6

    def build(self):
        W, H = self.W, self.H
        pen = Pen(W, H, base=art.vgradient(W, H, [(0, (20, 26, 62)), (0.5, (58, 56, 110)), (0.8, (118, 88, 138)),
                                                  (1, (118, 88, 138))]))
        art.stars(pen, 0, 0, W, 380, 70, seed=14)
        art.city_skyline(pen, 0, W, 760, (46, 50, 92), window=(255, 214, 150), lit=0.3, max_h=440, seed=15)
        rnd = random.Random(21)
        x, i = -30, 0
        while x < W:
            w = rnd.randint(280, 460)
            building(pen, x, x + w - 30, rnd.randint(420, 700), 1000, ((40, 44, 82), (52, 50, 90), (36, 40, 74))[i % 3],
                     lit=0.5, seed=60 + i, win=(255, 210, 140))
            x += w + rnd.randint(20, 120)
            i += 1
        pen.rect(0, 696, W, 744, INK)
        pen.rect(0, 702, W, 738, (96, 100, 128))
        for px in range(150, W, 520):
            pen.rect(px - 34, 744, px + 34, 1000, INK)
            pen.rect(px - 28, 744, px + 28, 1000, (82, 86, 114))
        pen.rect(0, 1000, W, 1130, (40, 42, 66))
        pen.rect(0, 996, W, 1004, INK)
        for gx in range(0, W, 160):
            pen.rect(gx, 1062, gx + 80, 1068, (120, 120, 150))
        pen.rect(0, 1150, W, H, (62, 62, 96))
        pen.rect(0, 1146, W, 1154, INK)
        for bx in range(0, W, 64):
            pen.rect(bx, 1180, bx + 8, 1236, (96, 96, 132))
        pen.rect(0, 1172, W, 1184, (110, 110, 146))
        pen.rect(0, 1236, W, 1246, INK)
        pen.rect(0, 1246, W, H, (70, 70, 106))
        return pen.result()

    def compose(self, t, world):
        car, doors = train_car(1900, 560, night=True)
        small = _cache.get("ep2_train_small", lambda: car.resize((int(car.width * 0.4), int(car.height * 0.4)),
                                                                 Image.LANCZOS))
        span = self.W + 2 * small.width + 600
        x = (t * 520) % span - 2 * small.width
        for k in range(2):
            paste(world, small, x + k * (small.width - 6), 700 - small.height + 4)
        d = ImageDraw.Draw(world)
        rnd = random.Random(3)
        for i in range(16):
            lane = 1040 if i % 2 == 0 else 1092
            v = rnd.uniform(380, 620) * (1 if lane == 1040 else -1)
            x0 = rnd.uniform(0, self.W + 400)
            cx = (x0 + v * t) % (self.W + 400) - 200
            col = (255, 226, 150) if v > 0 else (240, 110, 100)
            d.line((cx - 50, lane, cx + 50, lane), fill=col, width=9)
        spr = sprite("ep2_bridge", C.stand, C.MAIN, self.S, 1, tint=NIGHT, look=(1.4, -1.2),
                     blink=C.blink_at(t, offset=0.6))
        place(world, spr, self.MAIN_X, self.GROUND, self.S)

    def camera(self, t):
        u = self.u(t)
        return lerp(1250, 1900, u), 675, 2400


# --- an echo that says we can feel -------------------------------------------------------

class Echo(Scene):
    X, GROUND, S = 1200, 1300, 7.2

    def build(self):
        W, H = self.W, self.H
        img = art.vgradient(W, H, [(0, (24, 28, 66)), (0.6, (62, 58, 112)), (1, (100, 80, 130))])
        rnd = random.Random(31)

        def bokeh(d):
            for _ in range(70):
                x, y, r = rnd.uniform(0, W), rnd.uniform(250, 1100), rnd.uniform(14, 60)
                c = rnd.choice([(255, 214, 150), (255, 190, 140), (190, 210, 255), (255, 236, 200)])
                d.ellipse((x - r, y - r, x + r, y + r), fill=(*c, rnd.randint(60, 140)))
        img = art.overlay_alpha(img, bokeh, 1.0).filter(ImageFilter.GaussianBlur(10))
        pen = Pen(W, H, base=img)
        pen.rect(0, 1150, W, H, (62, 62, 96))
        pen.rect(0, 1146, W, 1154, INK)
        for bx in range(0, W, 64):
            pen.rect(bx, 1080, bx + 8, 1150, (96, 96, 132))
        pen.rect(0, 1070, W, 1084, (110, 110, 146))
        return pen.result()

    def human(self, t):
        return smoothstep((t - self.ev.get("human", self.duration * 0.6) + 0.2) / 1.6)

    def compose(self, t, world):
        cy = self.GROUND - 56 * self.S
        h = self.human(t)
        if h > 0.01:
            glow = _cache.get("ep2_echo_glow", lambda: art.glow_sprite(560, (255, 226, 180), 190))
            paste(world, glow, self.X - 560, cy - 560, h)
        for k in range(3):
            p = (t - k * 0.75) % 2.25
            if t >= k * 0.75:
                ring(world, self.X, cy, 70 + 640 * p / 2.25, (255, 222, 170), (0.5 + 0.3 * h) * (1 - p / 2.25), 7)
        spr = main_front(t, self.S, tint=NIGHT_SOFT, look=(0.0, -0.4), offset=1.7)
        place(world, spr, self.X, self.GROUND, self.S)
        if h > 0.01:
            d = ImageDraw.Draw(world)
            rnd = random.Random(8)
            for i in range(26):
                px = self.X + rnd.uniform(-700, 700) + 20 * math.sin(t + i)
                py = (rnd.uniform(200, 1200) - t * rnd.uniform(20, 50)) % 1100 + 150
                r = rnd.uniform(3, 6)
                d.ellipse((px - r, py - r, px + r, py + r), fill=mix((70, 64, 116), (255, 236, 200), h))

    def camera(self, t):
        u = self.u(t)
        return self.X, lerp(675, 720, u), lerp(2400, 1800, u)


# --- one window among a million ----------------------------------------------------------

class MillionWindows(Scene):
    W, H = 4000, 2250
    CELL, WIN = (150, 190), (96, 128)

    def build(self):
        W, H = self.W, self.H
        pen = Pen(W, H, base=art.vgradient(W, H, [(0, (18, 22, 56)), (1, (52, 48, 100))]), ss=1)
        art.stars(pen, 0, 0, W, 400, 90, seed=40)
        rnd = random.Random(41)
        lit_cols = [(255, 214, 150), (255, 236, 190), (250, 198, 140), (196, 214, 250)]
        x, i = -60, 0
        self.main_win = None
        while x < W:
            w = 5 * self.CELL[0] if i != 4 else 4 * self.CELL[0]
            top = rnd.randint(120, 520)
            body = ((38, 42, 80), (46, 46, 88), (34, 38, 72))[i % 3]
            pen.rect(x - 6, top - 6, x + w + 6, H, INK)
            pen.rect(x, top, x + w, H, body)
            for row, wy in enumerate(range(top + 50, H - 120, self.CELL[1])):
                for col, wx in enumerate(range(x + 27, x + w - self.WIN[0], self.CELL[0])):
                    is_main = i == 4 and col == 1 and self.main_win is None and wy > 1000
                    if is_main:
                        self.main_win = (wx, wy, wx + self.WIN[0], wy + self.WIN[1])
                        pen.rect(wx, wy, wx + self.WIN[0], wy + self.WIN[1], (255, 228, 176))
                        continue
                    if rnd.random() < 0.58:
                        c = rnd.choice(lit_cols)
                        pen.rect(wx, wy, wx + self.WIN[0], wy + self.WIN[1], c)
                        if rnd.random() < 0.55:
                            sc = shade(c, 0.5)
                            hx = wx + rnd.uniform(28, self.WIN[0] - 28)
                            pen.circle(hx, wy + self.WIN[1] - 52, 15, sc)
                            pen.rect(hx - 26, wy + self.WIN[1] - 36, hx + 26, wy + self.WIN[1], sc, radius=12)
                    else:
                        pen.rect(wx, wy, wx + self.WIN[0], wy + self.WIN[1], shade(body, 0.75))
            x += w + rnd.randint(30, 110)
            i += 1
        return pen.result()

    def compose(self, t, world):
        x0, y0, x1, y1 = self.main_win
        s = 1.25
        glow = _cache.get("ep2_win_glow", lambda: art.glow_sprite(40, (190, 225, 255), 150))
        paste(world, glow, (x0 + x1) / 2 - 16 - 40, y1 - 50 - 40)
        spr = sprite("ep2_win", C.sit_phone, C.MAIN, s, -1, blink=C.blink_at(t))
        place(world, spr, (x0 + x1) / 2 + 12, y1 - 2, s, -1)

    def camera(self, t):
        if self.main_win is None:
            self.bg()
        x0, y0, x1, y1 = self.main_win
        u = smoothstep(t / max(1.0, self.duration * 0.9))
        z = u ** 1.6
        return lerp((x0 + x1) / 2, self.W / 2, z), lerp((y0 + y1) / 2, self.H / 2, z), lerp(700, self.W, z)


# --- the next train arrives ----------------------------------------------------------------

class TrainArrives(Scene):
    W = 3200
    MAIN_X, MAIN_Y, S = 1600, 1222, 5.6
    STOP_X, GAP = -315, 30

    def __init__(self, duration, events=None):
        super().__init__(duration, events)
        rnd = random.Random(77)
        car, doors = train_car(1900, 560)
        self.doors = [self.STOP_X + k * (car.width + self.GAP - 8) + d for k in range(2) for d in doors]
        self.waiting = []
        for i, door in enumerate(self.doors[:3]):
            for side in (-1, 1):
                off = side * rnd.uniform(150, 260)
                y, s = ((1150, 4.8), (1300, 6.0))[(i + (side > 0)) % 2]
                self.waiting.append((door, off, y, s, C.OTHERS[(len(self.waiting) * 3) % len(C.OTHERS)]))
        self.leaving = [(self.doors[k], side, 1150 + 150 * ((k + j) % 2), 4.8 if (k + j) % 2 == 0 else 6.0,
                         0.25 * j + 0.4 * k, C.OTHERS[(5 + j * 3 + k) % len(C.OTHERS)])
                        for k in range(3) for j, side in enumerate((-1, 1))]

    def build(self):
        return station_bg(self.W, self.H, glass=False)

    def compose(self, t, world):
        speaker_pulse(world, t, self.W / 2)
        td = self.ev.get("doors", self.duration * 0.3)
        arrive = max(1.0, td - 0.7)
        u = min(1.0, max(0.0, t / arrive))
        shift = 2600 * (1 - u) ** 2
        car, doors = train_car(1900, 560)
        panel = door_panel(444, 100)
        open_ = smoothstep((t - td) / 0.9)
        for k in range(2):
            cx = self.STOP_X + shift + k * (car.width + self.GAP - 8)
            paste(world, car, cx, 1080 - car.height + 6)
            for d in doors:
                dx = cx + 4 + d
                for side in (-1, 1):
                    px = dx + side * (50 + 96 * open_) - 50
                    paste(world, panel, px - 4, 1080 - 40 - 444 + 4 - 4)

        people = []
        for i, (door, off, y, s, pal) in enumerate(self.waiting):
            tw = t - (td + 0.5 + 0.18 * i)
            face = 1 if off < 0 else -1
            if tw < 0:
                people.append((y, "stand", door + off, s, pal, face, 1.0))
                continue
            dist = abs(off)
            gone = 150 * tw
            if gone < dist:
                people.append((y, "walk", door + off + face * gone, s, pal, face, 1.0, gone))
            else:
                a = 1.0 - (gone - dist) / 90
                if a > 0:
                    people.append((y, "stand", door, s, pal, face, a))
        for door, side, y, s, delay, pal in self.leaving:
            te = td + 0.7 + delay
            if t < te:
                continue
            gone = 220 * (t - te)
            people.append((y, "walk", door + side * gone, s, pal, side, min(1.0, (t - te) / 0.4), gone))
        people.append((self.MAIN_Y, "main"))
        for p in sorted(people, key=lambda p: p[0]):
            if p[1] == "main":
                place(world, main_front(t, self.S, look=(0.0, 0.4), offset=2.1), self.MAIN_X, self.MAIN_Y, self.S)
            elif p[1] == "stand":
                _, _, x, s, pal, face, a = p
                spr = sprite("ep2_wait", C.stand, pal, s, face, look=(1.2, 0.0))
                place(world, spr, x, p[0], s, face, alpha=a)
            else:
                _, _, x, s, pal, face, a, gone = p
                spr = walker("ep2_board", gone / (31.0 * s), pal, s, facing=face)
                place(world, spr, x, p[0], s, face, alpha=a)

    def camera(self, t):
        td = self.ev.get("doors", self.duration * 0.3)
        still = self.ev.get("still", self.duration * 0.7)
        tight = smoothstep(t / max(1.0, td))
        back = smoothstep((t - still) / 4.0)
        vw = lerp(lerp(2400, 2000, tight), 2400, back)
        return self.MAIN_X, lerp(675, 740, tight) - 65 * back, vw


SCENES = {
    "station_crowd": StationCrowd,
    "station_quiet": StationQuiet,
    "rush_past": RushPast,
    "dark_room": DarkRoom,
    "train_interior": TrainInterior,
    "loud_thoughts": LoudThoughts,
    "city_flow": CityFlow,
    "echo": Echo,
    "million_windows": MillionWindows,
    "train_arrives": TrainArrives,
}
