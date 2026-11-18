"""Scenes for EP05 "เสียงที่หายไปกับการกระทำที่เหลืออยู่" (Actions Louder Than Words).

Same drawn style and conventions as `scenes.py` (local time `t`, events in
`self.ev`, camera returns (cx, cy, view width)).
"""

from __future__ import annotations

import math
import random

from PIL import Image, ImageDraw

import art
import character as C
from art import INK, Pen, ease_out_back, inked, mix, paste, shade, smoothstep
from scenes import NIGHT, Scene, _cache, lerp, place, sprite, walker
from scenes_ep02 import ring
from scenes_ep03 import paste_scaled, pop_scale, text, thai_font

DOG_BODY, DOG_PATCH, DOG_NOSE = (250, 244, 232), (200, 142, 98), (70, 52, 48)
TALKER = C.OTHERS[3]
SWEET = ["รักนะ", "ทุกอย่างทำเพื่อเธอ", "สัญญาเลย", "ตลอดไป", "ไม่ทิ้งกันแน่นอน"]


# --- the dog ----------------------------------------------------------------------------------

def _dog_shapes(pose, phase, wag, breath):
    """Primitive list in dog units (y up is negative), facing +x."""
    shapes, legs = [], []
    if pose == "sit":
        legs = [((4, -22), (4.5, 0), 2.6), ((7, -22), (8, 0), 2.6)]
        body = [("ell", (-7, -12), 13, 11, 0), ("ell", (-1, -24), 9, 13, -20)]
        head, snout_dy = (9, -38), 0
        back_paw = ("ell", (-4, -2), 7, 3.2, 0)
        tail = [(-18, -6), (-26, -10 - 6 * wag), (-30, -16 - 8 * wag)]
    elif pose == "lie":
        b = 1 + 0.035 * breath
        legs = [((18, -5), (31, -2), 2.6), ((16, -4), (28, -1), 2.6)]
        body = [("ell", (0, -9 * b), 22, 9 * b, 0)]
        head, snout_dy = (22, -13), 3
        back_paw = ("ell", (-14, -2), 8, 3, 0)
        tail = [(-21, -6), (-30, -3), (-36, -2 + 2 * wag)]
    else:  # walk
        s = math.sin(phase * 2 * math.pi)
        legs = [((10, -22), (10 + 6 * s, 0), 2.6), ((-10, -22), (-10 - 6 * s, 0), 2.6),
                ((13, -22), (13 - 6 * s, 0), 2.6), ((-7, -22), (-7 + 6 * s, 0), 2.6)]
        body = [("ell", (0, -25 + abs(s)), 19, 9, 0)]
        head, snout_dy = (21, -35 + abs(s)), 0
        back_paw = None
        tail = [(-18, -28), (-25, -36 - 4 * wag), (-27, -44 - 4 * wag)]
    return legs, body, head, snout_dy, back_paw, tail


def dog(pose="sit", scale=5.0, facing=1, phase=0.0, wag=0.0, breath=0.0, eyes_closed=False, tint=None):
    q = (pose, round(scale, 2), facing, round(phase * 12) / 12, round(wag, 1), round(breath, 1), eyes_closed, tint)

    def make():
        W, H, ox, oy = 90, 64, 45, 58
        pen = Pen(int(W * scale), int(H * scale))

        def P(p):
            return (ox + p[0]) * scale, (oy + p[1]) * scale

        legs, body, head, sdy, back_paw, tail = _dog_shapes(pose, q[3], wag, breath)
        ow = 0.9

        def ell(c, rx, ry, rot, fill, grow=0):
            pts = []
            for i in range(36):
                a = 2 * math.pi * i / 36
                x, y = (rx + grow) * math.cos(a), (ry + grow) * math.sin(a)
                r = math.radians(rot)
                pts.append(P((c[0] + x * math.cos(r) - y * math.sin(r), c[1] + x * math.sin(r) + y * math.cos(r))))
            pen.d.polygon([(x * pen.ss, y * pen.ss) for x, y in pts], fill=fill)

        def leg(a, b, w, fill, grow=0):
            pen.line([P(a), P(b)], fill, (2 * w + 2 * grow) * scale)

        hx, hy = head
        # outline pass, then fill pass
        for grow, col in ((ow, INK), (0, None)):
            pen.line([P(p) for p in tail], INK if col else DOG_BODY, (3.4 + 2 * grow) * scale)
            for a, b, w in legs:
                leg(a, b, w, col or shade(DOG_BODY, 0.95), grow)
            if back_paw:
                ell(*back_paw[1:4], back_paw[4], col or DOG_BODY, grow)
            for _, c, rx, ry, rot in body:
                ell(c, rx, ry, rot, col or DOG_BODY, grow)
            ell((hx, hy + sdy), 10, 9.5, 0, col or DOG_BODY, grow)
            ell((hx + 8, hy + 3 + sdy), 6.5, 4.6, 0, col or DOG_BODY, grow)
        ell((-6, -16 if pose == "sit" else -12), 6, 4, 10, DOG_PATCH)
        ell((hx - 3, hy - 2 + sdy), 4, 6, 25, DOG_PATCH)
        ell((hx - 5, hy + 2 + sdy), 3.6, 7.5, 25, INK, 0.7)
        ell((hx - 5, hy + 2 + sdy), 3.6, 7.5, 25, DOG_PATCH)
        ell((hx + 14, hy + 1 + sdy), 1.8, 1.4, 0, DOG_NOSE)
        ex, ey = hx + 4, hy - 1 + sdy
        if eyes_closed:
            pen.arc(*P((ex, ey)), 1.6 * scale, 1.0 * scale, 10, 170, DOG_NOSE, 0.7 * scale)
        else:
            ell((ex, ey), 1.3, 1.6, 0, DOG_NOSE)
            ell((ex + 0.4, ey - 0.6), 0.4, 0.4, 0, (255, 255, 255))
        pen.arc(*P((hx + 10, hy + 6 + sdy)), 2.0 * scale, 1.2 * scale, 20, 160, DOG_NOSE, 0.6 * scale)
        img = pen.result()
        if tint:
            r, g, b, a = img.split()
            img = Image.merge("RGBA", (r.point(lambda v: int(v * tint[0])), g.point(lambda v: int(v * tint[1])),
                                       b.point(lambda v: int(v * tint[2])), a))
        return img.transpose(Image.FLIP_LEFT_RIGHT) if facing < 0 else img

    return _cache.get(("dog", q), make)


def place_dog(world, spr, x, ground, scale, facing=1, alpha=1.0):
    ox = 45 * scale if facing > 0 else spr.width - 45 * scale
    paste(world, spr, x - ox, ground - 58 * scale, alpha)


def bubble(msg, size=40, pad=34, color=(255, 236, 242)):
    def make():
        f = thai_font(size)
        w = int(f.getlength(msg)) + 2 * pad
        h = size + 2 * pad
        pen = Pen(w + 12, h + 34)
        pen.rect(6, 6, w + 6, h + 6, color, radius=h / 2)
        pen.poly([(w * 0.3, h + 2), (w * 0.3 + 40, h + 2), (w * 0.3 - 6, h + 30)], color)
        pen.circle(30, h / 2 + 6, 10, (236, 110, 140))
        text(pen, w / 2 + 16, h / 2 + 6, msg, size, (150, 60, 90))
        return inked(pen.result(), 3.5)
    return _cache.get(("ep5_bubble", msg, size, color), make)


def home_bg(W, H, night=False):
    top, bot = ((48, 50, 84), (36, 38, 66)) if night else ((240, 226, 208), (230, 212, 192))
    pen = Pen(W, H, base=art.vgradient(W, H, [(0, top), (1, bot)]))
    floor = (44, 42, 66) if night else (196, 160, 126)
    pen.rect(0, 1160, W, H, floor)
    pen.rect(0, 1156, W, 1164, INK)
    return pen


# --- 1. a heart given to a sweet voice; the quiet one waits behind -------------------------------

class SweetVoice(Scene):
    MAIN_X, TALK_X, DOG_X, GROUND, S = 1150, 600, 1800, 1200, 6.2

    def build(self):
        pen = home_bg(self.W, self.H)
        pen.rect(1500, 300, 2100, 760, INK, radius=12)
        pen.vgrad_rect(1506, 306, 2094, 754, [(0, (170, 210, 236)), (1, (250, 226, 196))])
        pen.rect(1796, 306, 1806, 754, INK)
        return art.add_glow(pen.result(), 1800, 500, 380, (255, 240, 210), 0.4)

    def compose(self, t, world):
        place_dog(world, dog("sit", 5.6, -1, wag=math.sin(t * 6)), self.DOG_X, self.GROUND, 5.6, -1)
        spr = sprite("ep5_talker", C.stand, TALKER, self.S, 1, look=(1.4, 0.0), blink=C.blink_at(t, offset=0.8))
        place(world, spr, self.TALK_X, self.GROUND, self.S)
        spr = sprite("ep5_listen", C.stand, C.MAIN, self.S, -1, look=(1.6, -0.4), blink=C.blink_at(t))
        place(world, spr, self.MAIN_X, self.GROUND, self.S, -1)
        for i, msg in enumerate(SWEET[:3]):
            te = 0.4 + 1.1 * i
            if t > te:
                b = bubble(msg)
                paste_scaled(world, b, self.TALK_X + 160 + 120 * (i % 2), 420 - 130 * i + 10 * math.sin(t * 1.4 + i),
                             pop_scale(t - te))

    def camera(self, t):
        u = self.u(t)
        return lerp(1000, 1250, u), lerp(690, 700, u), lerp(2100, 2400, u)


# --- 2. replayed promises turn out to be a facade -------------------------------------------------

class Facade(Scene):
    MAIN_X, CUT_X, GROUND, S = 1500, 800, 1200, 6.2

    def build(self):
        pen = home_bg(self.W, self.H)
        return pen.result()

    def compose(self, t, world):
        tf = self.ev.get("facade", self.duration * 0.4)
        tp = self.ev.get("pain", self.duration * 0.75)
        fall = smoothstep((t - tf) / 1.0)
        cut = _cache.get("ep5_cutout", self._cutout)
        if fall < 1:
            rot = 88 * fall * fall
            c = cut.rotate(-rot, expand=True, resample=Image.BICUBIC, center=(cut.width / 2, cut.height))
            paste(world, c, self.CUT_X - c.width / 2 + 180 * fall, self.GROUND - c.height + 30 * fall,
                  1 - 0.3 * fall)
        if t > tf:
            dt = t - tf
            x = self.CUT_X - 40 - 180 * dt
            spr = walker("ep5_leave", dt / 0.9, TALKER, self.S, facing=-1, look=(1.2, 0.0))
            place(world, spr, x, self.GROUND, self.S, -1, alpha=max(0.0, 1 - dt / 4))
            coins = _cache.get("ep5_giftbag", self._gift)
            paste(world, coins, x - 30 * self.S - coins.width / 2, self.GROUND - 40 * self.S, max(0.0, 1 - dt / 4))
        if t < tp:
            spr = sprite("ep5_look", C.stand, C.MAIN, self.S, -1, look=(1.4, -0.2), blink=C.blink_at(t, offset=1.2))
            place(world, spr, self.MAIN_X, self.GROUND, self.S, -1)
        else:
            spr = sprite("ep5_hurt", C.hug_knees, C.MAIN, self.S, -1, blink=C.blink_at(t), look=(1.3, 1.6))
            place(world, spr, self.MAIN_X, self.GROUND, self.S, -1, alpha=smoothstep((t - tp) / 0.5))
            heart = _cache.get("ep5_broken", self._broken_heart)
            paste_scaled(world, heart, self.MAIN_X, self.GROUND - 70 * self.S, pop_scale(t - tp, 0.5))
        for i, msg in enumerate(SWEET):
            te = 0.3 + 0.7 * i
            if t < te:
                continue
            gone = smoothstep((t - tf - 0.1 * i) / 0.8)
            b = bubble(msg, 36)
            x = 420 + 380 * i
            y = 300 + 90 * (i % 2) + 10 * math.sin(t + i) + 500 * gone * gone
            paste_scaled(world, b, x, y, pop_scale(t - te), 1 - gone)

    @staticmethod
    def _cutout():
        spr = C.render(C.stand(look=(1.4, 0.0)), TALKER, 6.2)
        w, h = spr.size
        pen = Pen(w, h + 40)
        board = spr.getchannel("A").point(lambda v: 255 if v > 0 else 0)
        base = Image.new("RGBA", (w, h + 40), (0, 0, 0, 0))
        tan = Image.new("RGBA", (w, h), (214, 186, 140, 255))
        base.paste(tan, (0, 0), board)
        base = inked(base, 5)
        base.alpha_composite(inked(spr, 1), (5 + 1, 5 + 1))
        d = ImageDraw.Draw(base)
        d.rectangle((w / 2 - 6, h - 160, w / 2 + 14, h + 40), fill=INK)
        return base

    @staticmethod
    def _gift():
        pen = Pen(140, 140)
        pen.rect(10, 30, 130, 136, (236, 196, 90), radius=10)
        pen.rect(60, 30, 80, 136, (226, 90, 100))
        pen.ellipse(52, 26, 22, 14, (226, 90, 100))
        pen.ellipse(88, 26, 22, 14, (226, 90, 100))
        return inked(pen.result(), 3)

    @staticmethod
    def _broken_heart():
        pen = Pen(160, 150)
        for grow, col in ((6, INK), (0, (220, 90, 110))):
            pen.circle(52, 56, 36 + grow, col)
            pen.circle(108, 56, 36 + grow, col)
            pen.poly([(16 - grow, 70), (144 + grow, 70), (80, 144 + grow)], col)
        pen.line([(80, 30), (70, 70), (90, 92), (78, 140)], INK, 8)
        return pen.result()

    def camera(self, t):
        u = self.u(t)
        return lerp(1150, 1300, u), lerp(680, 720, u), lerp(2400, 2000, u)


# --- 3. the small one that waits by the door every day, and rests its head on our lap -------------

class WaitingDog(Scene):
    DOOR = (1500, 1880)
    MAIN_X, GROUND, S, DS = 900, 1200, 6.2, 5.8

    def build(self):
        pen = home_bg(self.W, self.H)
        x0, x1 = self.DOOR
        pen.rect(x0 - 10, 380, x1 + 10, 1160, INK, radius=8)
        pen.rect(x0, 390, x1, 1160, (170, 120, 86), radius=6)
        pen.circle(x0 + 40, 800, 14, (236, 196, 90))
        pen.rect(260, 320, 760, 760, INK, radius=12)
        pen.rect(266, 326, 754, 754, (200, 220, 236), radius=10)
        # sofa
        pen.rect(540, 900, 1260, 1160, INK, radius=40)
        pen.rect(546, 906, 1254, 1160, (120, 150, 170), radius=36)
        pen.rect(580, 1000, 1220, 1060, (140, 170, 190), radius=20)
        return pen.result()

    def compose(self, t, world):
        lap = self.ev.get("lap", self.duration * 0.6)
        cyc = (t / 2.2) % 1
        day = 0.5 - 0.5 * math.cos(cyc * 2 * math.pi)
        world.paste(art.vgradient(488, 428, [(0, mix((30, 36, 72), (150, 200, 236), day)),
                                             (1, mix((60, 64, 110), (250, 226, 196), day))]), (266, 326))
        if t < lap:
            x = self.DOOR[0] + 120
            place_dog(world, dog("sit", self.DS, 1, wag=math.sin(t * 7) * (0.4 + 0.6 * day)), x, self.GROUND,
                      self.DS, 1)
            return
        dt = t - lap
        seat = 1040
        ground = seat + 20 * self.S - 6
        spr = sprite("ep5_sofa", C.sit_desk_chin, C.MAIN, self.S, 1, blink=C.blink_at(t), look=(1.6, 2.0))
        place(world, spr, self.MAIN_X, ground, self.S, alpha=smoothstep(dt / 0.5))
        dx = lerp(self.DOOR[0] + 120, self.MAIN_X + 300, smoothstep(dt / 1.4))
        if dt < 1.4:
            place_dog(world, dog("walk", self.DS, -1, phase=dt * 1.6, wag=math.sin(t * 8)), dx, self.GROUND,
                      self.DS, -1)
        else:
            place_dog(world, dog("sit", self.DS, -1, wag=0.3 * math.sin(t * 3)), dx, self.GROUND, self.DS, -1)
            hearts = _cache.get("ep5_small_heart", self._heart)
            for i in range(3):
                p = ((t - lap - 1.4) * 0.6 + i / 3) % 1
                paste(world, hearts, dx - 140 + 30 * math.sin(p * 6 + i), 640 - 200 * p, 1 - p)

    @staticmethod
    def _heart():
        pen = Pen(60, 56)
        pen.circle(20, 20, 14, (236, 120, 140))
        pen.circle(40, 20, 14, (236, 120, 140))
        pen.poly([(6, 26), (54, 26), (30, 52)], (236, 120, 140))
        return pen.result()

    def camera(self, t):
        lap = self.ev.get("lap", self.duration * 0.6)
        u = smoothstep((t - lap + 0.3) / 2.0)
        return lerp(1600, 1150, u), lerp(700, 760, u), lerp(1900, 1900, u)


# --- 4. too many words, swirling around nothing ---------------------------------------------------

class WordStorm(Scene):
    def build(self):
        W, H = self.W, self.H
        return art.vgradient(W, H, [(0, (58, 52, 92)), (1, (96, 80, 128))])

    def compose(self, t, world):
        rnd = random.Random(3)
        cx, cy = 1200, 640
        d = ImageDraw.Draw(world)
        d.ellipse((cx - 160, cy - 160, cx + 160, cy + 160), outline=(150, 140, 190), width=6)
        words = SWEET + ["คิดถึง", "เชื่อใจได้", "ที่หนึ่ง", "ไม่เปลี่ยน", "แค่เธอ"]
        dissolve = smoothstep((t - self.duration * 0.55) / 2.5)
        for i in range(22):
            msg = words[i % len(words)]
            a = rnd.uniform(0, 6.28) + (0.6 + 0.3 * rnd.random()) * t * (1 if i % 2 else -1)
            r = rnd.uniform(260, 820) * (1 + 0.15 * math.sin(t + i))
            x, y = cx + r * math.cos(a), cy + 0.5 * r * math.sin(a) + 900 * dissolve * dissolve * rnd.random()
            b = bubble(msg, 44, 30, color=(246, 238, 250))
            paste_scaled(world, b, x, y, 1.0, max(0.0, min(1.0, t / 0.6)) * (1 - dissolve))

    def camera(self, t):
        u = self.u(t)
        return 1200, 675, lerp(2400, 1800, u)


# --- 5. silent, repeated actions: the slippers brought again and again ------------------------------

class QuietActions(Scene):
    W = 2600
    MAIN_X, GROUND, S, DS = 700, 1200, 6.2, 5.4

    def build(self):
        pen = home_bg(self.W, self.H)
        pen.rect(2100, 380, 2480, 1160, INK, radius=8)
        pen.rect(2110, 390, 2470, 1160, (170, 120, 86), radius=6)
        return art.add_glow(pen.result(), 900, 400, 600, (255, 236, 200), 0.3)

    def compose(self, t, world):
        spr = sprite("ep5_stand_home", C.stand, C.MAIN, self.S, 1, look=(1.6, 1.6), blink=C.blink_at(t, offset=0.7))
        place(world, spr, self.MAIN_X, self.GROUND, self.S)
        trip = 3.0
        k, p = int(t // trip), (t % trip) / trip
        left, right = self.MAIN_X + 200, 2200
        drop_x = self.MAIN_X + 160
        d = ImageDraw.Draw(world)
        for j in range(min(k, 4)):
            sx = drop_x - 60 * j
            d.rounded_rectangle((sx - 40, self.GROUND - 22, sx + 40, self.GROUND), 10, fill=INK)
            d.rounded_rectangle((sx - 36, self.GROUND - 18, sx + 36, self.GROUND - 4), 8, fill=(236, 140, 150))
        if p < 0.45:
            x, f, carry = lerp(left, right, p / 0.45), 1, False
        elif p < 0.55:
            x, f, carry = right, -1, True
        else:
            x, f, carry = lerp(right, left, (p - 0.55) / 0.45), -1, True
        if 0.45 <= p < 0.55:
            spr = dog("sit", self.DS, -1, wag=math.sin(t * 8))
        else:
            spr = dog("walk", self.DS, f, phase=t * 1.8, wag=math.sin(t * 8))
        place_dog(world, spr, x, self.GROUND, self.DS, f)
        if carry:
            mx = x + f * 22 * self.DS
            d.rounded_rectangle((mx - 34, self.GROUND - 190, mx + 34, self.GROUND - 172), 8, fill=INK)
            d.rounded_rectangle((mx - 30, self.GROUND - 186, mx + 30, self.GROUND - 176), 6, fill=(236, 140, 150))

    def camera(self, t):
        u = self.u(t)
        return lerp(1300, 1250, u), 700, lerp(2400, 2300, u)


# --- 6. at night, watching it breathe at the foot of the bed --------------------------------------

class BedsideBreath(Scene):
    X, S = 900, 6.4

    def build(self):
        W, H = self.W, self.H
        S, X = self.S, self.X
        pen = home_bg(W, H, night=True)
        pen.rect(1494, 200, 2106, 700, INK, radius=12)
        pen.vgrad_rect(1500, 206, 2100, 694, [(0, (20, 26, 60)), (1, (50, 54, 100))])
        art.stars(pen, 1510, 216, 2090, 600, 40, seed=7)
        pen.circle(1900, 330, 56, (250, 242, 214))
        self.top = 1020 - 15 * S
        pen.rect(X - 32 * S, self.top - 30 * S, X - 26 * S, 1160, INK, radius=10)
        pen.rect(X - 31 * S, self.top - 29 * S, X - 27 * S, 1160, (110, 80, 72), radius=8)
        pen.rect(X - 30 * S, self.top - 4, X + 110 * S, self.top + 10 * S, INK, radius=18)
        pen.rect(X - 29 * S, self.top, X + 109 * S, self.top + 9 * S, (120, 130, 170), radius=16)
        pen.rect(X - 30 * S, self.top + 10 * S, X + 110 * S, 1160, (90, 66, 64))
        img = pen.result()
        return art.add_glow(img, 1900, 330, 260, (240, 236, 210), 0.4)

    def compose(self, t, world):
        spr = sprite("ep5_bed", C.recline_bed, C.MAIN, self.S, 1, tint=NIGHT, blink=C.blink_at(t, offset=0.4))
        place(world, spr, self.X, 1020, self.S)
        blanket = _cache.get("ep5_blanket", self._blanket)
        paste(world, blanket, self.X - 6 * self.S, 1020 - 27 * self.S)
        breath = math.sin(t * 2.0)
        place_dog(world, dog("lie", 5.2, -1, breath=breath, eyes_closed=True, tint=(0.8, 0.82, 0.98)),
                  self.X + 92 * self.S, self.top + 2, 5.2, -1)
        for k in range(2):
            p = ((t * 0.5) + k / 2) % 1
            ring(world, self.X + 80 * self.S, self.top - 40, 30 + 90 * p, (220, 226, 250), 0.35 * (1 - p), 4)

    def _blanket(self):
        S = self.S
        pen = Pen(int(62 * S), int(16 * S))
        pen.rect(0, 0, 62 * S, 16 * S, INK, radius=5 * S)
        pen.rect(4, 4, 62 * S - 4, 16 * S - 4, (96, 110, 150), radius=5 * S)
        pen.rect(4, 4, 62 * S - 4, 3.2 * S, (190, 196, 220), radius=3 * S)
        return pen.result()

    def camera(self, t):
        u = self.u(t)
        return lerp(1300, 1350, u), lerp(700, 760, u), lerp(2400, 1900, u)


SCENES = {
    "sweet_voice": SweetVoice,
    "facade": Facade,
    "waiting_dog": WaitingDog,
    "word_storm": WordStorm,
    "quiet_actions": QuietActions,
    "bedside_breath": BedsideBreath,
}
