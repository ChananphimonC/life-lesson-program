"""Scenes for EP04 "ป้ายราคาที่ต้องแลก" (Trend Chaser & The Debt Trap).

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
from scenes_ep02 import building, ring
from scenes_ep03 import GREEN, RED, card, money, paste_scaled, pop_scale, text

GOLD = (224, 176, 80)
BAG_COLORS = [(236, 150, 160), (150, 120, 196), (240, 196, 90), (120, 176, 150), (96, 120, 170)]


# --- props --------------------------------------------------------------------------

def shopping_bag(color, w=150, h=170):
    def make():
        pen = Pen(w + 10, h + 60)
        pen.arc(w / 2 + 5, 52, w * 0.26, 40, 180, 360, INK, 9)
        pen.arc(w / 2 + 5, 52, w * 0.26, 40, 180, 360, shade(color, 0.7), 5)
        pen.rect(5, 50, w + 5, h + 55, color, radius=10)
        pen.rect(5, 50, w + 5, 74, shade(color, 0.88), radius=10)
        pen.circle(w / 2 + 5, 50 + h * 0.55, w * 0.14, (255, 250, 240))
        pen.circle(w / 2 + 5, 50 + h * 0.55, w * 0.07, color)
        return inked(pen.result(), 3.5)
    return _cache.get(("ep4_bag", color, w, h), make)


def brand_box(w=420, h=300):
    def make():
        pen = Pen(w, h)
        pen.rect(0, 40, w, h, (236, 150, 72), radius=10)
        pen.rect(-6, 20, w + 6, 76, (222, 132, 56), radius=10)
        pen.rect(w / 2 - 16, 20, w / 2 + 16, h, (120, 70, 50))
        pen.ellipse(w / 2 - 44, 18, 40, 22, (120, 70, 50))
        pen.ellipse(w / 2 + 44, 18, 40, 22, (120, 70, 50))
        text(pen, w * 0.25, h * 0.62, "LUXE", 44, (255, 240, 220))
        return inked(pen.result(), 4)
    return _cache.get(("ep4_box", w, h), make)


def handbag(w=320, h=240):
    def make():
        pen = Pen(w, h)
        pen.arc(w / 2, 90, w * 0.3, 80, 180, 360, INK, 14)
        pen.arc(w / 2, 90, w * 0.3, 80, 180, 360, (150, 100, 70), 9)
        pen.poly([(30, 90), (w - 30, 90), (w - 6, h - 6), (6, h - 6)], (196, 132, 92))
        pen.rect(30, 90, w - 30, 128, (176, 112, 76))
        pen.rect(w / 2 - 26, 112, w / 2 + 26, 150, GOLD, radius=6)
        return inked(pen.result(), 4)
    return _cache.get(("ep4_handbag", w, h), make)


def noodle_cup(k=1.0):
    def make():
        w, h = int(110 * k), int(130 * k)
        pen = Pen(w, h)
        pen.poly([(4, 14), (w - 4, 14), (w - 18 * k, h - 2), (18 * k, h - 2)], (250, 246, 236))
        pen.rect(4, 0, w - 4, 18 * k, (226, 80, 70), radius=4)
        pen.rect(20 * k, 50 * k, w - 20 * k, 80 * k, (240, 190, 80), radius=4)
        return inked(pen.result(), 3)
    return _cache.get(("ep4_noodle", k), make)


def heart(size=90, color=(236, 86, 110)):
    def make():
        pen = Pen(size, size)
        s = size / 140
        for grow, col in ((6, INK), (0, color)):
            pen.circle(46 * s, 50 * s, 32 * s + grow * s, col)
            pen.circle(94 * s, 50 * s, 32 * s + grow * s, col)
            pen.poly([(14 * s - grow * s, 62 * s), (126 * s + grow * s, 62 * s), (70 * s, 128 * s + grow * s)], col)
        return pen.result()
    return _cache.get(("ep4_heart", size, color), make)


def comment(msg, w=300, h=110):
    def make():
        pen = Pen(w, h + 24)
        pen.rect(0, 0, w, h, (255, 253, 248), radius=30)
        pen.poly([(40, h - 2), (80, h - 2), (36, h + 22)], (255, 253, 248))
        pen.circle(54, h / 2, 30, (200, 206, 220))
        text(pen, 100, h / 2, msg, 34, INK, anchor="lm")
        return inked(pen.result(), 3.5)
    return _cache.get(("ep4_comment", msg, w, h), make)


COMMENTS = ["สวยมาก!", "ปังมาก", "อยากได้บ้าง", "ใบนี้หายากนะ", "รวยจัง", "ของแท้ป่ะ"]


def room_bg(W, H, dim=1.0):
    wall_top, wall_bot = mix((40, 36, 56), (92, 84, 118), dim), mix((30, 28, 44), (72, 64, 96), dim)
    pen = Pen(W, H, base=art.vgradient(W, H, [(0, wall_top), (1, wall_bot)]))
    floor = mix((26, 24, 38), (82, 70, 84), dim)
    pen.rect(0, 1150, W, H, floor)
    pen.rect(0, 1146, W, 1154, INK)
    # bed
    pen.rect(1594, 820, 2290, 1150, INK, radius=30)
    pen.rect(1600, 826, 2284, 1150, mix((60, 46, 52), (120, 92, 92), dim), radius=26)
    pen.rect(1234, 1000, 2290, 1080, INK, radius=24)
    pen.rect(1240, 1006, 2284, 1074, mix((70, 76, 104), (160, 168, 200), dim), radius=22)
    pen.rect(1250, 1074, 1290, 1150, INK)
    # small lamp on a box
    pen.rect(280, 980, 520, 1150, INK, radius=8)
    pen.rect(286, 986, 514, 1150, mix((60, 52, 60), (150, 120, 100), dim), radius=6)
    pen.poly([(330, 980), (470, 980), (440, 860), (360, 860)], mix((80, 76, 90), (250, 214, 150), dim))
    return pen


# --- 1. the shopping on the bed in a small dim room ----------------------------------------

class UnboxRoom(Scene):
    X, S = 1370, 6.0

    def build(self):
        pen = room_bg(self.W, self.H, 0.65)
        img = pen.result()
        return art.add_glow(img, 400, 900, 380, (255, 214, 150), 0.45)

    def compose(self, t, world):
        box = brand_box()
        paste(world, box, 1760, 1006 - box.height + 6)
        for i, (x, c) in enumerate(((1560, BAG_COLORS[0]), (2180, BAG_COLORS[1]), (2050, BAG_COLORS[2]))):
            b = shopping_bag(c)
            paste(world, b, x - b.width / 2, 1010 - b.height)
        ground = 1006 + 20 * self.S - 6
        spr = sprite("ep4_bedsit", C.sit_phone, C.MAIN, self.S, 1, tint=(0.88, 0.86, 0.94),
                     blink=C.blink_at(t, offset=0.6))
        place(world, spr, self.X, ground, self.S)

    def camera(self, t):
        u = self.u(t)
        return lerp(1900, 1450, u), lerp(800, 760, u), lerp(1600, 2100, u)


# --- 2. checkout: the balance drops to almost nothing ------------------------------------------

class Checkout(Scene):
    PX, PY, PW, PH = 1200, 690, 600, 1100
    BEFORE, AFTER = 41250, 2350

    def build(self):
        W, H = self.W, self.H
        img = art.vgradient(W, H, [(0, (64, 58, 88)), (1, (40, 36, 60))])
        pen = Pen(W, H, base=img)
        x0, y0 = self.PX - self.PW / 2, self.PY - self.PH / 2
        pen.rect(x0 - 8, y0 - 8, x0 + self.PW + 8, y0 + self.PH + 8, INK, radius=70)
        pen.rect(x0, y0, x0 + self.PW, y0 + self.PH, (40, 42, 54), radius=64)
        sx0, sy0, sx1, sy1 = x0 + 24, y0 + 60, x0 + self.PW - 24, y0 + self.PH - 60
        pen.rect(sx0, sy0, sx1, sy1, (250, 248, 244), radius=30)
        text(pen, self.PX, sy0 + 60, "ชำระเงิน", 46, INK)
        pen.rect(sx0 + 40, sy0 + 120, sx1 - 40, sy0 + 470, (236, 228, 216), radius=24)
        bag = handbag(260, 196)
        pen.img.alpha_composite(bag.resize((bag.width * pen.ss, bag.height * pen.ss)),
                                (int((self.PX - bag.width / 2) * pen.ss), int((sy0 + 190) * pen.ss)))
        text(pen, sx0 + 40, sy0 + 530, "ยอดชำระ", 34, (120, 112, 120), anchor="lm", bold=False)
        text(pen, sx1 - 40, sy0 + 530, "38,900", 46, INK, anchor="rm")
        pen.rect(sx0 + 40, sy0 + 580, sx1 - 40, sy0 + 584, (220, 214, 210))
        text(pen, sx0 + 40, sy0 + 640, "ยอดเงินคงเหลือ", 34, (120, 112, 120), anchor="lm", bold=False)
        self.balance_at = (sx1 - 40, sy0 + 700)
        self.button = (self.PX, sy1 - 110)
        pen.rect(sx0 + 40, sy1 - 160, sx1 - 40, sy1 - 60, (60, 160, 110), radius=40)
        text(pen, self.PX, sy1 - 110, "ยืนยันชำระเงิน", 40, (255, 255, 255))
        return pen.result()

    def compose(self, t, world):
        cardspr = _cache.get("ep4_credit", self._credit)
        slide = smoothstep(t / 0.8)
        paste(world, cardspr, lerp(-500, 260, slide), 520)
        drop = self.ev.get("drop", self.duration * 0.3)
        u = smoothstep((t - drop) / 1.6)
        value = round(lerp(self.BEFORE, self.AFTER, u), -1)
        col = mix(INK, RED, u)
        key = ("ep4_bal", int(value), col)
        num = _cache.get(key, lambda: self._number(money(value), col))
        x, y = self.balance_at
        world.paste(num, (int(x - num.width), int(y - num.height / 2)))
        tap = drop - 0.6
        if t > tap:
            p = (t - tap) / 0.8
            if p < 1:
                ring(world, *self.button, 20 + 160 * p, (255, 255, 255), 0.8 * (1 - p), 8)
        excite = self.ev.get("excite")
        if excite is not None and t > excite:
            rnd = random.Random(4)
            dt = t - excite
            for i in range(16):
                a = rnd.uniform(0, 2 * math.pi)
                r = 380 + 260 * smoothstep(dt / 2) + 40 * math.sin(t * 3 + i)
                k = 0.6 + 0.4 * math.sin(t * 5 + i)
                fade = max(0.0, 1 - max(0.0, dt - 2.5) / 1.5)
                sp = _cache.get(("ep4_spark", i % 3), lambda: self._sparkle(i % 3))
                paste_scaled(world, sp, self.PX + r * math.cos(a), self.PY + r * math.sin(a) * 0.8, k, fade)

    @staticmethod
    def _number(s, col):
        pen = Pen(420, 80)
        pen.rect(0, 0, 420, 80, (250, 248, 244))
        text(pen, 416, 40, s, 54, col, anchor="rm")
        return pen.result().convert("RGB")

    @staticmethod
    def _credit():
        pen = Pen(420, 260)
        pen.rect(0, 0, 420, 260, (70, 84, 140), radius=24)
        pen.rect(0, 60, 420, 100, (40, 46, 80))
        pen.rect(40, 130, 110, 180, GOLD, radius=10)
        text(pen, 40, 220, "**** 0427", 30, (230, 234, 250), anchor="lm")
        return inked(pen.result(), 4)

    @staticmethod
    def _sparkle(kind):
        col = [(255, 226, 120), (255, 176, 196), (170, 220, 255)][kind]
        pen = Pen(70, 70)
        c, r = 35, 30
        pen.poly([(c, c - r), (c + 8, c - 8), (c + r, c), (c + 8, c + 8), (c, c + r), (c - 8, c + 8), (c - r, c),
                  (c - 8, c - 8)], col)
        return pen.result()

    def camera(self, t):
        u = self.u(t)
        return self.PX - 60, lerp(690, 700, u), lerp(2300, 1900, u)


# --- 3. the photo and the instant likes ---------------------------------------------------------

class PhotoShoot(Scene):
    X, GROUND, S = 820, 1220, 6.2
    TABLE = (1420, 1880, 960)

    def build(self):
        W, H = self.W, self.H
        pen = Pen(W, H, base=art.vgradient(W, H, [(0, (236, 222, 214)), (1, (222, 206, 198))]))
        pen.rect(0, 1220, W, H, (196, 170, 150))
        pen.rect(0, 1216, W, 1224, INK)
        x0, x1, top = self.TABLE
        pen.rect(x0 - 6, top - 6, x1 + 6, top + 30, INK, radius=8)
        pen.rect(x0, top, x1, top + 24, (250, 248, 244), radius=6)
        for lx in (x0 + 40, x1 - 60):
            pen.rect(lx - 4, top + 24, lx + 24, 1220, INK)
            pen.rect(lx, top + 24, lx + 20, 1220, (220, 214, 206))
        pen.rect(2050, 300, 2066, 1220, INK)
        pen.circle(2058, 300, 120, INK)
        pen.circle(2058, 300, 108, (255, 250, 236))
        pen.circle(2058, 300, 70, (236, 222, 214))
        img = pen.result()
        return art.add_glow(img, 1650, 760, 520, (255, 248, 230), 0.5)

    def compose(self, t, world):
        x0, x1, top = self.TABLE
        bag = handbag()
        paste(world, bag, (x0 + x1) / 2 - bag.width / 2, top - bag.height + 8)
        spr = sprite("ep4_photo", C.phone_up, C.MAIN, self.S, 1, blink=C.blink_at(t, offset=1.4))
        place(world, spr, self.X, self.GROUND, self.S)
        flash = 1.4
        if flash < t < flash + 0.35:
            a = 1 - (t - flash) / 0.35
            world.paste(Image.blend(world, Image.new("RGB", world.size, (255, 255, 255)), 0.7 * a))
        post = self.ev.get("post")
        if post is not None and t > post:
            dt = t - post
            rnd = random.Random(2)
            for i in range(18):
                te = i * 0.28
                if dt < te:
                    continue
                age = dt - te
                x = rnd.uniform(1100, 2200)
                y = rnd.uniform(380, 900) - 50 * age
                if i % 3 == 2:
                    c = comment(COMMENTS[i % len(COMMENTS)])
                    paste_scaled(world, c, x, y, pop_scale(age), min(1.0, max(0.0, 3.5 - age)))
                else:
                    h = heart(80 + 30 * (i % 2))
                    paste_scaled(world, h, x, y, pop_scale(age, 0.3), min(1.0, max(0.0, 3.0 - age)))
            likes = int(1284 * smoothstep(dt / 4))
            badge = card("ยอดไลก์", money(likes), (236, 86, 110), 330, 110)
            paste(world, badge, 220, 240)

    def camera(self, t):
        u = self.u(t)
        return lerp(1250, 1350, u), lerp(700, 660, u), lerp(2400, 2150, u)


# --- 4. a few minutes in the spotlight, then quiet ---------------------------------------------------

class Spotlight(Scene):
    X, GROUND, S = 1200, 1160, 6.8

    def build(self):
        W, H = self.W, self.H
        pen = Pen(W, H, base=art.vgradient(W, H, [(0, (34, 30, 54)), (1, (26, 24, 42))]))
        pen.ellipse(self.X, self.GROUND + 30, 420, 70, INK)
        pen.ellipse(self.X, self.GROUND + 20, 410, 62, (96, 84, 124))
        pen.rect(self.X - 410, self.GROUND + 20, self.X + 410, self.GROUND + 120, (80, 70, 104))
        pen.ellipse(self.X, self.GROUND + 120, 410, 62, (80, 70, 104))
        return pen.result()

    def quiet(self, t):
        return smoothstep((t - self.ev.get("quiet", self.duration * 0.6) + 0.2) / 2.2)

    def compose(self, t, world):
        q = self.quiet(t)
        light = 1 - 0.8 * q
        cone = _cache.get("ep4_cone", self._cone)
        paste(world, cone, self.X - cone.width / 2, 0, light)
        rnd = random.Random(6)
        for i in range(26):
            ph = rnd.uniform(0, 6.28)
            radius = rnd.uniform(380, 820)
            speed = rnd.uniform(0.25, 0.5) * (1 if i % 2 else -1)
            a = ph + speed * t
            x = self.X + radius * math.cos(a)
            y = 700 + radius * 0.45 * math.sin(a) - 120
            fall = 600 * q * q * rnd.uniform(0.6, 1.2)
            alpha = (1 - q) * min(1.0, t / 0.6)
            if alpha <= 0.02:
                continue
            if i % 4 == 3:
                c = comment(COMMENTS[i % len(COMMENTS)])
                paste_scaled(world, c, x, y + fall, 0.75, alpha)
            else:
                paste_scaled(world, heart(70 + 20 * (i % 3)), x, y + fall, 1.0, alpha)
        look = (0.0, -1.0) if q < 0.5 else (0.0, 2.4)
        spr = sprite("ep4_spot", C.stand, C.MAIN, self.S, 1, view="front", look=look,
                     blink=C.blink_at(t, offset=0.2))
        place(world, spr, self.X, self.GROUND, self.S)

    @staticmethod
    def _cone():
        w, h = 1300, 1300
        mask = Image.new("L", (w, h), 0)
        ImageDraw.Draw(mask).polygon([(w / 2 - 120, 0), (w / 2 + 120, 0), (w - 60, h), (60, h)], fill=90)
        from PIL import ImageFilter
        mask = mask.filter(ImageFilter.GaussianBlur(30))
        spr = Image.new("RGBA", (w, h), (255, 240, 200, 0))
        spr.putalpha(mask)
        return spr

    def camera(self, t):
        u = self.u(t)
        return self.X, lerp(700, 720, u), lerp(2400, 1900, u)


# --- 5. what's left: the bill and instant noodles till month-end ----------------------------------

class NoodleMonth(Scene):
    X, GROUND, S = 820, 1200, 6.2

    def build(self):
        W, H = self.W, self.H
        pen = Pen(W, H, base=art.vgradient(W, H, [(0, (92, 84, 118)), (1, (72, 64, 96))]))
        pen.rect(0, self.GROUND, W, H, (70, 60, 74))
        pen.rect(0, self.GROUND - 4, W, self.GROUND + 4, INK)
        top = self.GROUND - 33 * self.S
        x0 = self.X + 14 * self.S
        pen.rect(x0 - 4, top - 4, x0 + 110 * self.S + 4, top + 5 * self.S, INK, radius=6)
        pen.rect(x0, top, x0 + 110 * self.S, top + 4 * self.S, (150, 112, 92), radius=4)
        for lx in (x0 + 8 * self.S, x0 + 100 * self.S):
            pen.rect(lx - 3, top, lx + 4 * self.S + 3, self.GROUND, INK)
            pen.rect(lx, top, lx + 4 * self.S, self.GROUND, (128, 94, 78))
        pen.rect(1716, 196, 1984, 504, INK, radius=12)
        pen.rect(1722, 202, 1978, 498, (250, 248, 240), radius=10)
        pen.rect(1722, 202, 1978, 270, RED, radius=10)
        text(pen, 1850, 236, "สิ้นเดือน", 34, (255, 255, 255))
        text(pen, 1850, 390, "31", 120, INK)
        self.top, self.x0 = top, x0
        return pen.result()

    def compose(self, t, world):
        cup = noodle_cup()
        cx = self.x0 + 34 * self.S
        paste(world, cup, cx - cup.width / 2, self.top - cup.height + 4)
        d = ImageDraw.Draw(world)
        for k in range(3):
            p = (t * 0.6 + k / 3) % 1
            sx = cx - 24 + 24 * k + 12 * math.sin(t * 2 + k)
            sy = self.top - cup.height - 20 - 120 * p
            col = mix((92, 84, 118), (236, 232, 240), 1 - p)
            d.line((sx, sy, sx + 10 * math.sin(p * 6), sy - 40), fill=col, width=6)
        spr = sprite("ep4_chin", C.sit_desk_chin, C.MAIN, self.S, 1, blink=C.blink_at(t, offset=0.4),
                     look=(1.4, 1.4))
        place(world, spr, self.X, self.GROUND, self.S)
        bill = card("ยอดเรียกเก็บบัตรเครดิต", "38,900", RED, 480, 140)
        paste_scaled(world, bill, 1640, 720 + 8 * math.sin(t * 1.4), pop_scale(t, 0.5))
        te = self.ev.get("noodle")
        if te is not None and t > te:
            n = min(14, int((t - te) / 0.35) + 1)
            for i in range(n):
                col, row = i % 5, i // 5
                c = noodle_cup(0.8)
                age = t - te - i * 0.35
                k = ease_out_back(age / 0.35)
                paste_scaled(world, c, 1420 + col * 96 + row * 48, self.GROUND - c.height / 2 - row * 100, k)

    def camera(self, t):
        u = self.u(t)
        return lerp(1250, 1300, u), lerp(690, 700, u), lerp(2400, 2150, u)


# --- 6. strangers who scroll past without looking --------------------------------------------------

class Strangers(Scene):
    W = 3000
    X, GROUND, S = 1500, 1222, 5.6

    def build(self):
        W, H = self.W, self.H
        pen = Pen(W, H, base=art.vgradient(W, H, [(0, (176, 182, 200)), (1, (210, 210, 216))]))
        pen.rect(1080, 140, 1920, 820, INK, radius=30)
        pen.rect(1090, 150, 1910, 810, (250, 248, 244), radius=24)
        pen.rect(1120, 200, 1880, 680, (236, 228, 216), radius=16)
        bag = handbag(420, 316)
        pen.img.alpha_composite(bag.resize((bag.width * pen.ss, bag.height * pen.ss)),
                                (int((1500 - bag.width / 2) * pen.ss), int(300 * pen.ss)))
        pen.rect(0, 1080, W, H, (196, 196, 204))
        pen.rect(0, 1076, W, 1084, INK)
        img = pen.result()
        h = heart(60)
        img.paste(h, (1130, 712), h)
        p2 = Pen(400, 70)
        text(p2, 0, 35, "1,284", 44, INK, anchor="lm")
        t2 = p2.result()
        img.paste(t2, (1200, 708), t2)
        return img

    def compose(self, t, world):
        rnd = random.Random(15)
        people = []
        for i in range(16):
            y = (1150, 1300)[i % 2] + rnd.uniform(-12, 12)
            s = (4.8, 6.0)[i % 2]
            f = rnd.choice((1, -1))
            v = rnd.uniform(240, 340)
            x = (rnd.uniform(0, self.W + 600) + f * v * t) % (self.W + 600) - 300
            people.append((y, x, s, f, v, rnd.random()))
        people.append((self.GROUND, None, None, None, None, None))
        for y, x, s, f, v, ph in sorted(people, key=lambda p: p[0]):
            if x is None:
                spr = sprite("ep4_front", C.stand, C.MAIN, self.S, 1, view="front", look=(0.0, 1.6),
                             blink=C.blink_at(t, offset=1.0))
                place(world, spr, self.X, self.GROUND, self.S)
                continue
            spr = walker("ep4_crowd", ph + v * t / (31 * s), C.OTHER, s, facing=f, tint=(0.82, 0.82, 0.88))
            place(world, spr, x, y, s, f, alpha=0.88)

    def camera(self, t):
        u = self.u(t)
        return self.X, lerp(640, 700, u), lerp(2400, 2050, u)


# --- 7. carrying more and more bags; the account goes negative -------------------------------------

class HeavyBags(Scene):
    W = 3600
    X0, SPEED, GROUND, S = 800, 60, 1222, 5.8

    def build(self):
        W, H = self.W, self.H
        pen = Pen(W, H, base=art.vgradient(W, H, [(0, (120, 110, 168)), (0.6, (230, 168, 150)), (1, (240, 200, 170))]))
        rnd = random.Random(30)
        x, i = -40, 0
        colors = [(170, 140, 160), (150, 130, 168), (180, 150, 150), (140, 124, 156)]
        while x < W:
            w = rnd.randint(320, 520)
            building(pen, x, x + w - 24, rnd.randint(300, 600), 1080, colors[i % 4], lit=0.4, seed=80 + i)
            x += w
            i += 1
        pen.rect(0, 1080, W, H, (176, 150, 150))
        pen.rect(0, 1076, W, 1084, INK)
        for gx in range(0, W, 180):
            pen.rect(gx, 1084, gx + 3, H, (160, 136, 138))
        return pen.result()

    def main_x(self, t):
        return self.X0 + self.SPEED * t

    def compose(self, t, world):
        x = self.main_x(t)
        n = min(7, 2 + int(t / 1.1))
        spr = walker("ep4_heavy", t / 1.7, C.MAIN, self.S, stride=12.0, careful=True, look=(1.2, 2.0))
        hx, hy = x + 4 * self.S, self.GROUND - 46 * self.S
        for i in range(n):
            b = shopping_bag(BAG_COLORS[i % len(BAG_COLORS)], 120, 140)
            sw = 6 * math.sin(t * 3.2 + i)
            if i % 2 == 0:
                paste(world, b, hx - b.width / 2 - 40 * (i // 2) + sw, hy - 30 + 16 * (i // 2))
        place(world, spr, x, self.GROUND, self.S)
        for i in range(n):
            if i % 2 == 1:
                b = shopping_bag(BAG_COLORS[i % len(BAG_COLORS)], 120, 140)
                sw = 6 * math.sin(t * 3.2 + i)
                paste(world, b, hx - b.width / 2 + 30 + 40 * (i // 2) + sw, hy - 20 + 16 * (i // 2))
        te = self.ev.get("minus")
        if te is not None and t > te:
            c = card("ยอดในบัญชี", "-48,500", RED, 420, 130)
            paste_scaled(world, c, x + 60, self.GROUND - 112 * self.S - 20 * smoothstep((t - te) / 2),
                         pop_scale(t - te, 0.5))

    def camera(self, t):
        return self.main_x(t) + 200, lerp(690, 700, self.u(t)), 2300


# --- 8. in the dark, the thing sits still; the debt notice blinks -----------------------------------

class DebtGlow(Scene):
    def build(self):
        pen = room_bg(self.W, self.H, 0.25)
        pen.rect(700, 900, 1140, 930, INK, radius=8)
        pen.rect(706, 906, 1134, 924, (70, 56, 60), radius=6)
        for lx in (730, 1090):
            pen.rect(lx - 4, 930, lx + 24, 1150, INK)
            pen.rect(lx, 930, lx + 20, 1150, (60, 48, 54))
        return pen.result()

    def compose(self, t, world):
        bag = handbag(260, 196)
        dim = bag.copy()
        r, g, b, a = dim.split()
        dim = Image.merge("RGBA", (r.point(lambda v: int(v * 0.5)), g.point(lambda v: int(v * 0.48)),
                                   b.point(lambda v: int(v * 0.6)), a))
        dim = _cache.get("ep4_dimbag", lambda: dim)
        paste(world, dim, 800, 906 - dim.height + 8)
        pulse = 0.5 + 0.5 * math.sin(t * 2.4)
        glow = _cache.get("ep4_red_glow", lambda: art.glow_sprite(140, (240, 90, 80), 170))
        paste(world, glow, 1060 - 140, 890 - 140, 0.35 + 0.5 * pulse)
        d = ImageDraw.Draw(world)
        d.rounded_rectangle((1010, 878, 1110, 904), 8, fill=INK)
        d.rounded_rectangle((1014, 882, 1106, 900), 6, fill=mix((40, 30, 40), (250, 110, 100), pulse))
        spr = sprite("ep4_hug", C.hug_knees, C.MAIN, 6.0, 1, tint=(0.62, 0.6, 0.74), blink=C.blink_at(t, offset=0.4),
                     look=(1.4, 0.6))
        place(world, spr, 1500, 1150, 6.0)

    def camera(self, t):
        u = self.u(t)
        return lerp(1200, 1050, u), lerp(720, 800, u), lerp(2400, 1700, u)


SCENES = {
    "unbox_room": UnboxRoom,
    "checkout": Checkout,
    "photo_shoot": PhotoShoot,
    "spotlight": Spotlight,
    "noodle_month": NoodleMonth,
    "strangers": Strangers,
    "heavy_bags": HeavyBags,
    "debt_glow": DebtGlow,
}
