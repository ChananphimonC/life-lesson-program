"""Scene library. Each scene draws a static background once, then composes
animated elements (characters, cars, cards...) per frame and applies a
camera move. Local time `t` is seconds since the scene's start; it can be
slightly negative or exceed `duration` during crossfades."""

from __future__ import annotations

import math
import random

from PIL import Image, ImageDraw

import art
import character as C
from art import Pen, mix, shade, smoothstep, paste

OUT = (1920, 1080)
_cache = C.SpriteCache()

NIGHT = (0.74, 0.78, 0.98)
DUSK = (0.92, 0.82, 0.86)
DUSK_OTHERS = (0.8, 0.7, 0.82)


def lerp(a, b, t):
    return a + (b - a) * t


def sprite(name, pose_fn, pal, scale, facing=1, tint=None, glow=None, **kw):
    key = (name, tuple(sorted(kw.items())), pal, round(scale, 3), facing, tint, glow)
    return _cache.get(key, lambda: C.render(pose_fn(**kw), pal, scale, facing, tint=tint, glow=glow))


def place(world, spr, x, ground_y, scale, facing=1, alpha=1.0):
    ox = C.ORIGIN_X * scale if facing > 0 else spr.width - C.ORIGIN_X * scale
    paste(world, spr, x - ox, ground_y - C.ORIGIN_Y * scale, alpha)


def walker(name, phase, pal, scale, facing=1, tint=None, frames=16, **kw):
    q = int(round((phase % 1.0) * frames)) % frames
    return sprite(f"{name}#{q}", lambda **k: C.walk(q / frames, **k), pal, scale, facing, tint, **kw)


def runner(phase, pal, scale, facing=1, tint=None, frames=12):
    q = int(round((phase % 1.0) * frames)) % frames
    return sprite(f"run#{q}", lambda: C.run(q / frames), pal, scale, facing, tint)


class Scene:
    W, H = 2400, 1350

    def __init__(self, duration, events=None):
        self.duration = max(0.5, duration)
        self.ev = events or {}
        self._bg = None

    def bg(self):
        if self._bg is None:
            self._bg = self.build().convert("RGB")
        return self._bg

    def release(self):
        self._bg = None

    def build(self):
        raise NotImplementedError

    def compose(self, t, world):
        pass

    def camera(self, t):
        return self.W / 2, self.H / 2, self.W

    def u(self, t, end=None):
        return smoothstep(t / (end or self.duration))

    def frame(self, t):
        world = self.bg().copy()
        self.compose(t, world)
        cx, cy, vw = self.camera(t)
        vh = vw * OUT[1] / OUT[0]
        cx = min(max(cx, vw / 2), self.W - vw / 2)
        cy = min(max(cy, vh / 2), self.H - vh / 2)
        return world.transform(OUT, Image.EXTENT, (cx - vw / 2, cy - vh / 2, cx + vw / 2, cy + vh / 2),
                               Image.BILINEAR)


# --- 1. morning, scrolling the phone in bed --------------------------------

class MorningPhone(Scene):
    S, X, GROUND = 7.6, 1330, 1078

    def build(self):
        W, H = self.W, self.H
        pen = Pen(W, H, base=art.vgradient(W, H, [(0, (250, 237, 216)), (1, (242, 222, 196))]))
        pen.rect(0, 1080, W, H, (212, 176, 136))
        for y in range(1110, H, 70):
            pen.rect(0, y, W, y + 4, (196, 160, 122))
        pen.rect(0, 1072, W, 1086, (232, 214, 190))
        pen.vgrad_rect(260, 230, 860, 760, [(0, (150, 196, 236)), (0.62, (255, 214, 172)), (1, (255, 186, 150))])
        pen.circle(560, 650, 92, (255, 232, 168))
        art.hills(pen, 260, 860, 700, 30, (226, 168, 170), period=320, bottom=760)
        art.hills(pen, 260, 860, 735, 20, (200, 150, 165), period=230, phase=1.2, bottom=760)
        pen.rect(260, 230, 860, 760, None, outline=(255, 250, 242), width=24)
        pen.rect(551, 230, 569, 760, (255, 250, 242))
        pen.rect(260, 486, 860, 504, (255, 250, 242))
        pen.rect(230, 760, 890, 792, (240, 228, 210), radius=6)
        for x0 in (150, 860):
            pen.rect(x0, 190, x0 + 120, 860, (236, 166, 146), radius=40)
            for fx in (x0 + 35, x0 + 80):
                pen.rect(fx, 230, fx + 6, 840, (220, 146, 128))
        pen.rect(120, 175, 1010, 195, (180, 130, 100), radius=10)
        # bed
        pen.rect(1960, 640, 2280, 1080, (186, 136, 102), radius=36)
        pen.rect(1190, 926, 2260, 1000, (246, 243, 236), radius=26)
        pen.rect(1460, 900, 2260, 1010, (150, 184, 216), radius=34)
        pen.rect(1460, 1000, 2260, 1010, (128, 162, 196))
        pen.rect(2040, 850, 2240, 925, (252, 250, 246), radius=30)
        pen.rect(1200, 1000, 1240, 1080, (160, 116, 86))
        pen.ellipse(700, 1150, 420, 52, (226, 196, 160))
        img = pen.result()
        beam = lambda d: d.polygon([(330, 760), (860, 760), (1500, 1340), (500, 1340)], fill=(255, 238, 200, 70))
        img = art.overlay_alpha(img, beam, 1.0)
        return art.add_glow(img, 560, 650, 240, (255, 230, 180), 0.55)

    def compose(self, t, world):
        rnd = random.Random(7)
        d = ImageDraw.Draw(world)
        for i in range(18):
            x0, y0, sp = rnd.uniform(420, 1300), rnd.uniform(780, 1300), rnd.uniform(8, 20)
            x = x0 + 30 * math.sin(t * 0.4 + i)
            y = y0 - (t * sp) % 260
            d.ellipse((x - 3, y - 3, x + 3, y + 3), fill=(255, 244, 214))
        glow = _cache.get("phone_glow", lambda: art.glow_sprite(120, (190, 225, 255), 120))
        px, py = self.X - 21 * self.S, self.GROUND - 46 * self.S
        paste(world, glow, px - 120, py - 120)
        spr = sprite("sit_phone", C.sit_phone, C.MAIN, self.S, -1, blink=C.blink_at(t))
        place(world, spr, self.X, self.GROUND, self.S, -1)

    def camera(self, t):
        u = self.u(t)
        return lerp(1200, 1260, u), lerp(675, 690, u), lerp(2400, 1650, u)


# --- 2. everyone else running ahead ------------------------------------------

class OthersRunning(Scene):
    W = 3200
    RUNNERS = [(1500, 1090, 300, 5.0, 0.0), (900, 1075, 330, 4.8, 0.3), (250, 1120, 290, 5.3, 0.6),
               (-350, 1085, 340, 5.0, 0.15), (-950, 1110, 310, 5.1, 0.45), (-1500, 1080, 335, 4.9, 0.7),
               (-2100, 1115, 300, 5.2, 0.85)]

    def build(self):
        W, H = self.W, self.H
        pen = Pen(W, H, base=art.vgradient(W, H, [(0, (166, 208, 240)), (0.62, (232, 242, 246)), (1, (232, 242, 246))]))
        for cx, cy, s in ((500, 230, 1.0), (1500, 170, 1.3), (2600, 260, 1.1)):
            for dx, dy, r in ((-90, 10, 60), (0, -20, 80), (90, 8, 62), (40, 30, 55)):
                pen.circle(cx + dx * s, cy + dy * s, r * s, (255, 255, 255))
        art.hills(pen, 0, W, 860, 70, (196, 218, 220), period=1100)
        art.hills(pen, 0, W, 960, 50, (160, 202, 176), period=800, phase=2.0)
        for x in (300, 900, 2100, 2900):
            art.tree(pen, x, 1000, h=260, leaf=(120, 176, 128))
        pen.rect(0, 1000, W, H, (150, 196, 140))
        pen.rect(0, 1040, W, 1160, (228, 208, 168))
        pen.rect(0, 1040, W, 1050, (206, 184, 144))
        pen.rect(0, 1150, W, 1160, (206, 184, 144))
        img = pen.result()
        return art.add_glow(img, 2900, 150, 260, (255, 246, 210), 0.6)

    def compose(self, t, world):
        for i, (x0, y, speed, s, ph) in enumerate(self.RUNNERS):
            x = x0 + speed * max(t, -0.5)
            if x < self.W + 300:
                place(world, runner(ph + t / 0.55, C.OTHERS[i % len(C.OTHERS)], s), x, y, s)
        spr = sprite("stand", C.stand, C.MAIN, 5.4, 1, look=(1.6, 0.0), blink=C.blink_at(t, offset=1.1))
        place(world, spr, 620, 1112, 5.4)

    def camera(self, t):
        u = self.u(t)
        return lerp(1150, 1520, u), 690, 2300


# --- 3. other people's success floating out of the phone -------------------

class FeedSuccess(Scene):
    S, X, GROUND = 12.0, 1200, 1520
    CARDS = [("trophy", "trophy", 420, 470), ("house", "house", 700, 190),
             ("car", "car", 1700, 190), ("briefcase", "briefcase", 1980, 470), ("life", "sparkle", 1200, 120)]

    def build(self):
        W, H = self.W, self.H
        img = art.vgradient(W, H, [(0, (120, 112, 170)), (0.55, (196, 160, 190)), (1, (246, 200, 186))])
        rnd = random.Random(11)

        def bokeh(d):
            for _ in range(26):
                x, y, r = rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(30, 120)
                d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 240, 230, rnd.randint(18, 50)))
        return art.overlay_alpha(img, bokeh, 1.0)

    def compose(self, t, world):
        glow = _cache.get("phone_glow_big", lambda: art.glow_sprite(260, (200, 230, 255), 140))
        paste(world, glow, self.X - 260, self.GROUND - 50 * self.S - 260)
        spr = sprite("front_phone", C.front_phone, C.MAIN, self.S, 1, blink=C.blink_at(t, offset=0.5))
        place(world, spr, self.X, self.GROUND, self.S)
        for i, (event, kind, x, y) in enumerate(self.CARDS):
            te = self.ev.get(event)
            if te is None or t < te:
                continue
            dt = t - te
            pop = art.ease_out_back(dt / 0.45)
            card = _cache.get(("card", kind), lambda: art.card_sprite(kind, 230))
            size = max(4, int(card.width * (0.3 + 0.7 * pop)))
            c = card.resize((size, size), Image.BILINEAR) if size != card.width else card
            fy = y + 10 * math.sin(t * 1.6 + i) - 30 * smoothstep(dt / 3)
            paste(world, c, x - size / 2, fy - size / 2, min(1.0, dt / 0.25))

    def camera(self, t):
        u = self.u(t)
        return 1200, lerp(640, 610, u), lerp(2400, 2160, u)


# --- 4. walking slowly behind the others at dusk -----------------------------

class WalkingBehind(Scene):
    W = 4200
    MAIN_SPEED, MAIN_X0 = 78, 700
    OTHERS = [(1250, 4.9, 0.0), (1450, 5.2, 0.4), (1700, 5.0, 0.7), (1900, 5.1, 0.2)]

    def build(self):
        W, H = self.W, self.H
        pen = Pen(W, H, base=art.vgradient(W, H, [(0, (104, 96, 168)), (0.55, (236, 150, 124)), (0.78, (252, 204, 154)), (1, (252, 204, 154))]))
        pen.circle(2700, 840, 120, (255, 214, 156))
        art.hills(pen, 0, W, 900, 80, (160, 112, 150), period=1300)
        art.hills(pen, 0, W, 1000, 60, (118, 86, 132), period=900, phase=1.4)
        for x in (350, 1500, 2300, 3400, 3900):
            art.tree(pen, x, 1060, h=300, leaf=(84, 66, 104), trunk=(70, 54, 86))
        pen.rect(0, 1050, W, H, (86, 72, 112))
        pen.rect(0, 1080, W, 1180, (152, 120, 142))
        img = pen.result()
        return art.add_glow(img, 2700, 840, 420, (255, 200, 150), 0.55)

    def main_x(self, t):
        return self.MAIN_X0 + self.MAIN_SPEED * t

    def compose(self, t, world):
        for i, (x0, s, ph) in enumerate(self.OTHERS):
            x = x0 + 185 * t
            place(world, walker("walk_o", ph + t / 0.85, C.OTHERS[i], s, tint=DUSK_OTHERS), x, 1130, s)
        x = self.main_x(t)
        spr = walker("walk", t / 1.35, C.MAIN, 5.4, tint=DUSK, stride=17.0, look=(1.4, 0.6))
        place(world, spr, x, 1140, 5.4)

    def camera(self, t):
        return self.main_x(t) + 620, 700, 2300


# --- 5. a quiet question at the desk at night --------------------------------

class NightDesk(Scene):
    S, X, GROUND = 6.8, 1080, 1100

    def build(self):
        W, H = self.W, self.H
        pen = Pen(W, H, base=art.vgradient(W, H, [(0, (46, 54, 96)), (1, (34, 40, 74))]))
        pen.rect(0, 1100, W, H, (36, 36, 62))
        pen.vgrad_rect(180, 200, 700, 700, [(0, (18, 26, 62)), (1, (52, 62, 112))])
        art.stars(pen, 190, 210, 690, 600, 40, seed=5)
        pen.circle(540, 330, 55, (250, 242, 214))
        art.city_skyline(pen, 180, 700, 700, (26, 32, 66), lit=0.3, max_h=200, seed=8)
        pen.rect(180, 200, 700, 700, None, outline=(74, 82, 126), width=20)
        pen.rect(431, 200, 449, 700, (74, 82, 126))
        pen.rect(150, 700, 730, 726, (80, 88, 132), radius=6)
        # desk
        pen.rect(1180, 856, 2080, 886, (122, 92, 82), radius=8)
        pen.rect(2000, 886, 2030, 1100, (100, 74, 66))
        pen.rect(1600, 886, 1630, 1100, (100, 74, 66))
        pen.rect(1400, 842, 1650, 858, (170, 176, 196), radius=4)
        pen.poly([(1430, 846), (1650, 846), (1610, 690), (1410, 700)], (60, 64, 84))
        pen.poly([(1442, 838), (1638, 838), (1600, 702), (1422, 710)], (180, 210, 248))
        pen.rect(1760, 790, 1840, 856, (226, 120, 110), radius=10)
        pen.rect(1730, 830, 1900, 856, (120, 150, 190), radius=4)
        pen.rect(1745, 806, 1885, 830, (240, 220, 160), radius=4)
        pen.ellipse(1960, 852, 60, 12, (70, 70, 90))
        pen.line([(1960, 848), (1925, 700), (1995, 610)], (70, 70, 90), 12)
        pen.poly([(1950, 590), (2080, 600), (2060, 690), (1960, 670)], (240, 196, 120))
        # chair
        pen.rect(990, 770, 1012, 1000, (88, 70, 92), radius=8)
        pen.rect(990, 962, 1170, 990, (104, 84, 108), radius=8)
        pen.rect(1000, 990, 1020, 1100, (88, 70, 92))
        pen.rect(1140, 990, 1160, 1100, (88, 70, 92))
        img = pen.result()
        img = art.add_glow(img, 2010, 700, 380, (255, 206, 140), 0.42)
        img = art.add_glow(img, 1520, 770, 260, (170, 205, 255), 0.35)
        return art.add_glow(img, 540, 330, 160, (240, 236, 210), 0.4)

    def compose(self, t, world):
        look = (1.5, 0.6) if (t % 6) < 3.8 else (1.0, -0.6)
        spr = sprite("desk", C.sit_desk_chin, C.MAIN, self.S, 1, tint=NIGHT, blink=C.blink_at(t, offset=2.0), look=look)
        place(world, spr, self.X, self.GROUND, self.S)
        q = _cache.get("qmark", lambda: art.bubble_sprite("?", 150))
        qs = _cache.get("qmark_s", lambda: art.bubble_sprite("?", 105))
        for key, spr_q, x, y in (("q1", q, 1180, 470), ("q2", qs, 1300, 400)):
            te = self.ev.get(key)
            if te is not None and t >= te:
                dt = t - te
                paste(world, spr_q, x, y - 40 * smoothstep(dt / 4), min(0.85, dt / 0.6))

    def camera(self, t):
        u = self.u(t)
        return lerp(1200, 1280, u), lerp(700, 680, u), lerp(2400, 1800, u)


# --- 6. the gap between who we are and who we think we should be -----------

class GapIdeal(Scene):
    def build(self):
        W, H = self.W, self.H
        pen = Pen(W, H, base=art.vgradient(W, H, [(0, (50, 46, 98)), (0.55, (118, 94, 160)), (1, (228, 168, 180))]))
        art.stars(pen, 0, 0, W, 700, 70, seed=21)
        pen.ellipse(640, 1050, 360, 80, (96, 86, 134))
        pen.rect(300, 990, 980, 1050, (124, 112, 160), radius=40)
        pen.ellipse(1830, 700, 330, 70, (110, 98, 150))
        pen.rect(1520, 630, 2140, 690, (140, 126, 176), radius=36)
        for i in range(9):
            x = lerp(1010, 1490, i / 8)
            y = lerp(980, 640, i / 8) - 120 * math.sin(math.pi * i / 8)
            pen.circle(x, y, 7, (230, 214, 240))
        img = pen.result()
        return art.add_glow(img, 1830, 560, 300, (255, 230, 190), 0.25)

    def compose(self, t, world):
        rnd = random.Random(4)
        d = ImageDraw.Draw(world)
        for i in range(24):
            x = rnd.uniform(0, self.W) + 20 * math.sin(t * 0.5 + i)
            y = (rnd.uniform(0, self.H) - t * rnd.uniform(10, 30)) % self.H
            d.ellipse((x - 2.5, y - 2.5, x + 2.5, y + 2.5), fill=(250, 236, 250))
        spr = sprite("stand_up", C.stand, C.MAIN, 5.6, 1, look=(1.6, -1.4), blink=C.blink_at(t, offset=0.7))
        place(world, spr, 650, 992, 5.6)
        te = self.ev.get("ideal")
        if te is not None and t >= te:
            ideal = sprite("ideal", C.stand, C.IDEAL, 5.6, 1, glow=(255, 226, 170), view="front", look=(0.0, 0.0))
            place(world, ideal, 1830, 632, 5.6, alpha=min(0.82, (t - te) / 1.2))

    def camera(self, t):
        reveal = self.ev.get("ideal", self.duration) + 0.8
        u = self.u(t, end=reveal)
        return lerp(760, 1200, u), lerp(820, 700, u), lerp(1500, 2400, u)


# --- 7. everyone's path is shaped differently --------------------------------

class DifferentPaths(Scene):
    START_X = 380
    # (base y, width, end x, wave amplitude, wave period, flag color)
    PATHS = [(830, 34, 2050, 34, 130, (236, 120, 120)),
             (960, 44, 1350, 0, 1, (120, 170, 230)),
             (1095, 54, 2200, 70, 300, (246, 196, 90)),
             (1235, 64, 1800, 14, 520, (170, 130, 220))]

    @staticmethod
    def _path_pts(y0, x0, x1, amp, period):
        pts, x = [], x0
        while x <= x1:
            pts.append((x, y0 + amp * math.sin((x - x0) / period)))
            x += 20
        return pts

    def build(self):
        W, H = self.W, self.H
        pen = Pen(W, H, base=art.vgradient(W, H, [(0, (172, 214, 240)), (0.5, (244, 240, 222)), (1, (244, 240, 222))]))
        art.hills(pen, 0, W, 700, 60, (188, 214, 190), period=1000)
        pen.rect(0, 740, W, H, (160, 204, 162))
        for y0, w, x1, amp, period, flag in self.PATHS:
            pts = self._path_pts(y0, self.START_X, x1, amp, period)
            pen.line(pts, (198, 174, 132), w + 12)
            pen.line(pts, (232, 214, 174), w)
            ex, ey = pts[-1]
            pen.rect(ex - 4, ey - 150, ex + 4, ey, (120, 96, 80))
            pen.poly([(ex + 4, ey - 150), (ex + 84, ey - 122), (ex + 4, ey - 94)], flag)
        pen.rect(self.START_X - 6, 780, self.START_X + 6, 1300, (250, 250, 246), radius=4)
        for x, y in ((700, 900), (1600, 1030), (2250, 1300), (1150, 1170), (1900, 900), (900, 1310)):
            art.flower(pen, x, y, 12)
        art.tree(pen, 2280, 760, h=240, leaf=(110, 170, 120))
        art.tree(pen, 120, 790, h=210, leaf=(120, 176, 128))
        img = pen.result()
        return art.add_glow(img, 1900, 120, 300, (255, 246, 214), 0.5)

    def compose(self, t, world):
        spr = sprite("stand_paths", C.stand, C.MAIN, 5.0, 1, look=(1.5, -0.4), blink=C.blink_at(t, offset=1.6))
        place(world, spr, 260, 1250, 5.0)
        te = self.ev.get("ruler")
        if te is not None and t >= te:
            dt = t - te
            ruler = _cache.get("ruler", lambda: art.ruler_sprite(1300, 110))
            x = lerp(-1300, self.START_X, art.ease_out_back(dt / 0.9))
            alpha = 1.0 if dt < 2.2 else max(0.0, 1 - (dt - 2.2) / 0.8)
            paste(world, ruler, x, 600, alpha)

    def camera(self, t):
        u = self.u(t)
        return lerp(1200, 1180, u), lerp(700, 720, u), lerp(2400, 2240, u)


# --- 8. exploring, then resting for a while ----------------------------------

class ExploreRest(Scene):
    W = 3000
    WALK_X0, ROCK_X, GROUND, ROCK_TOP = 1250, 1960, 1120, 1052

    def build(self):
        W, H = self.W, self.H
        pen = Pen(W, H, base=art.vgradient(W, H, [(0, (186, 218, 236)), (0.6, (252, 236, 204)), (1, (252, 236, 204))]))
        art.hills(pen, 0, W, 860, 60, (196, 214, 176), period=1200)
        pen.rect(0, 960, W, H, (164, 206, 150))
        art.hills(pen, 0, W, 980, 25, (164, 206, 150), period=500)
        art.tree(pen, 2250, 1120, h=900, leaf=(116, 172, 116))
        pen.ellipse(2030, 1090, 140, 58, (150, 146, 150))
        pen.ellipse(2015, 1070, 120, 40, (176, 172, 176))
        rnd = random.Random(2)
        for _ in range(26):
            x, y = rnd.uniform(200, 2900), rnd.uniform(1130, 1320)
            art.flower(pen, x, y, rnd.uniform(9, 14), petal=rnd.choice([(250, 190, 200), (250, 226, 150), (200, 190, 250)]))
        for _ in range(40):
            x, y = rnd.uniform(0, W), rnd.uniform(1000, 1340)
            pen.ellipse(x, y, rnd.uniform(8, 18), rnd.uniform(4, 7), (136, 130, 128))
        return art.add_glow(pen.result(), 300, 160, 320, (255, 240, 200), 0.5)

    def compose(self, t, world):
        rest = self.ev.get("rest", self.duration * 0.5)
        for i, (x0, y0) in enumerate(((1500, 880), (2500, 760))):
            x = x0 + 120 * math.sin(t * 0.7 + i * 2)
            y = y0 + 50 * math.sin(t * 1.9 + i)
            b = _cache.get(("bf", int(t * 8 + i) % 2), lambda: art.butterfly_sprite(int(t * 8 + i) % 2 == 0))
            paste(world, b, x, y)
        fade = 0.45
        if t < rest + fade:
            p = min(1.0, max(0.0, t / rest))
            x = lerp(self.WALK_X0, self.ROCK_X - 90, p)
            moving = t < rest
            if moving:
                spr = walker("walk_look", t / 1.5, C.MAIN, 5.4, stride=15.0, look=(1.4, 1.8))
            else:
                spr = sprite("stand_look", C.stand, C.MAIN, 5.4, 1, look=(1.4, 1.6))
            place(world, spr, x, self.GROUND, 5.4, alpha=1.0 if t < rest else 1 - (t - rest) / fade)
        if t >= rest:
            spr = sprite("hug_rock", C.hug_knees, C.MAIN, 5.4, 1, blink=C.blink_at(t), look=(1.6, 1.0))
            place(world, spr, self.ROCK_X, self.ROCK_TOP, 5.4, alpha=min(1.0, (t - rest) / fade))

    def camera(self, t):
        u = self.u(t)
        return lerp(1500, 1850, u), 720, lerp(2300, 2050, u)


# --- 9. a highway for some, a careful dirt path for others -------------------

class HighwayDirt(Scene):
    H = 2100
    CARS = [((222, 96, 92), 1150, 0, 700), ((96, 150, 220), 1300, 900, 700), ((244, 196, 86), 1050, 1700, 700),
            ((150, 200, 160), 1250, 400, 590), ((200, 150, 220), 1100, 1300, 590)]

    def build(self):
        W, H = self.W, self.H
        pen = Pen(W, H, base=art.vgradient(W, H, [(0, (164, 206, 236)), (0.24, (226, 238, 242)), (0.5, (150, 196, 140)), (1, (126, 176, 122))]))
        art.city_skyline(pen, 0, W, 560, (180, 196, 214), window=(206, 220, 232), lit=0.4, max_h=260, seed=4)
        pen.rect(0, 560, W, 1050, (140, 190, 130))
        pen.rect(0, 610, W, 880, (88, 92, 108))
        pen.rect(0, 618, W, 628, (240, 240, 240))
        pen.rect(0, 862, W, 872, (240, 240, 240))
        for x in range(0, W, 200):
            pen.rect(x, 740, x + 110, 752, (250, 250, 250))
        for x in range(0, W, 90):
            pen.rect(x, 890, x + 10, 940, (180, 184, 196))
        pen.rect(0, 890, W, 902, (200, 204, 214))
        art.hills(pen, 0, W, 1060, 30, (110, 160, 108), period=700, bottom=H)
        pen.rect(0, 1080, W, H, (138, 186, 126))
        rnd = random.Random(9)
        path = [(x, 1830 + 50 * math.sin(x / 420)) for x in range(-50, W + 100, 50)]
        pen.line(path, (214, 190, 150), 120)
        for _ in range(70):
            x = rnd.uniform(0, W)
            y = 1830 + 50 * math.sin(x / 420) + rnd.uniform(-50, 50)
            pen.ellipse(x, y, rnd.uniform(6, 16), rnd.uniform(4, 9), (150, 136, 120))
        for _ in range(40):
            x, y = rnd.uniform(0, W), rnd.uniform(1150, 2080)
            if abs(y - 1830 - 50 * math.sin(x / 420)) > 90:
                for dx in (-8, 0, 8):
                    pen.line([(x + dx, y), (x + dx * 1.8, y - 30)], (100, 150, 96), 5)
        for x in (300, 1100, 2000):
            art.tree(pen, x, 1250, h=320, leaf=(100, 160, 108))
        return pen.result()

    def compose(self, t, world):
        for color, speed, offset, y in self.CARS:
            car = _cache.get(("car", color), lambda: art.car_sprite(color, 1.25))
            span = self.W + 700
            if y > 650:
                x = (offset + speed * t) % span - 350
                paste(world, car, x, y - car.height + 30)
            else:
                car_l = _cache.get(("carl", color), lambda: car.transpose(Image.FLIP_LEFT_RIGHT))
                x = self.W + 350 - (offset + speed * t) % span
                paste(world, car_l, x, y - car_l.height + 30)
        x = 800 + 48 * t
        y = 1830 + 50 * math.sin(x / 420) + 10
        spr = walker("walk_careful", t / 1.5, C.MAIN, 5.6, stride=12.0, careful=True, look=(1.2, 2.2))
        place(world, spr, x, y, 5.6)

    def camera(self, t):
        td = self.ev.get("dirt", self.duration * 0.5)
        tilt = smoothstep((t - td + 0.2) / 1.8)
        x = 800 + 48 * t
        return lerp(1200, x + 250, tilt), lerp(640, 1480, tilt), 2300


# --- 10. alone by the window at night ------------------------------------------

class NightWindow(Scene):
    def build(self):
        W, H = self.W, self.H
        pen = Pen(W, H, base=art.vgradient(W, H, [(0, (40, 46, 86)), (1, (30, 34, 66))]))
        pen.rect(0, 1080, W, H, (28, 30, 56))
        pen.vgrad_rect(600, 160, 1800, 860, [(0, (16, 22, 54)), (1, (50, 56, 104))])
        art.stars(pen, 610, 170, 1790, 520, 80, seed=12)
        pen.circle(1560, 300, 60, (250, 242, 214))
        self.windows = art.city_skyline(pen, 600, 1800, 800, (32, 38, 76), lit=0.4, max_h=330, seed=17)
        pen.rect(600, 800, 1800, 860, (44, 48, 84))
        pen.rect(600, 160, 1800, 860, None, outline=(64, 70, 116), width=26)
        pen.rect(1191, 160, 1209, 860, (64, 70, 116))
        pen.rect(560, 860, 1840, 940, (78, 72, 118), radius=14)
        pen.rect(600, 940, 1800, 1080, (54, 52, 92))
        img = pen.result()
        return art.add_glow(img, 1560, 300, 200, (240, 236, 210), 0.45)

    def compose(self, t, world):
        for i, (x0, speed, s) in enumerate(((560, 60, 1.5), (900, -45, 1.4), (1300, 52, 1.6))):
            x = 600 + (x0 - 600 + speed * t) % 1200
            fac = 1 if speed > 0 else -1
            spr = walker("tiny", t / 0.9 + i * 0.3, C.OTHER, s, facing=fac, tint=(0.3, 0.32, 0.5))
            place(world, spr, x, 855, s, facing=fac)
        spr = sprite("hug_window", C.hug_knees, C.MAIN, 6.0, 1, tint=NIGHT, blink=C.blink_at(t, offset=0.4), look=(1.4, -1.0))
        place(world, spr, 900, 902, 6.0)

    def camera(self, t):
        u = self.u(t)
        return lerp(1200, 1120, u), lerp(660, 640, u), lerp(2400, 1900, u)


# --- 11. walking on at our own pace toward the unknown ------------------------

class OwnPace(Scene):
    W = 4200
    X0, SIGN_X, GROUND = 900, 3050, 1112

    def build(self):
        W, H = self.W, self.H
        pen = Pen(W, H, base=art.vgradient(W, H, [(0, (24, 30, 70)), (0.55, (72, 72, 134)), (0.82, (226, 162, 150)), (1, (226, 162, 150))]))
        art.stars(pen, 0, 0, W, 650, 160, seed=31)
        pen.circle(500, 260, 70, (250, 242, 214))
        art.hills(pen, 0, W, 900, 70, (60, 60, 108), period=1300)
        art.hills(pen, 0, W, 1000, 50, (44, 46, 88), period=900, phase=2.2)
        pen.rect(0, 1040, W, H, (40, 42, 80))
        pen.rect(0, 1070, W, 1170, (70, 72, 112))
        for x in range(0, W, 220):
            pen.rect(x, 1116, x + 110, 1124, (150, 150, 180))
        sign = art.signpost_sprite(0.9)
        img = pen.result()
        img.paste(sign, (int(self.SIGN_X + 130 - sign.width / 2), int(1075 - sign.height)), sign)
        img = art.add_glow(img, 500, 260, 200, (240, 236, 210), 0.45)
        return art.add_glow(img, 3700, 1000, 700, (255, 196, 160), 0.35)

    def main_x(self, t):
        arrive = self.ev.get("sign", self.duration * 0.7)
        return lerp(self.X0, self.SIGN_X, min(1.0, max(0.0, t) / arrive))

    def compose(self, t, world):
        arrive = self.ev.get("sign", self.duration * 0.7)
        x = self.main_x(t)
        if t < arrive:
            spr = walker("walk_night", (x - self.X0) / 170, C.MAIN, 5.4, tint=NIGHT, stride=20.0, look=(1.3, 0.2))
        else:
            spr = sprite("stand_sign", C.stand, C.MAIN, 5.4, 1, tint=NIGHT, look=(1.2, -1.6), blink=C.blink_at(t))
        place(world, spr, x, self.GROUND, 5.4)

    def camera(self, t):
        arrive = self.ev.get("sign", self.duration * 0.7)
        after = smoothstep((t - arrive) / 4)
        return self.main_x(t) + 300, lerp(700, 680, after), lerp(2300, 1950, after)


SCENES = {
    "morning_phone": MorningPhone,
    "others_running": OthersRunning,
    "feed_success": FeedSuccess,
    "walking_behind": WalkingBehind,
    "night_desk": NightDesk,
    "gap_ideal": GapIdeal,
    "different_paths": DifferentPaths,
    "explore_rest": ExploreRest,
    "highway_dirt": HighwayDirt,
    "night_window": NightWindow,
    "own_pace": OwnPace,
}
