"""Scenes for EP03 "ราคาที่จ่ายไปกับตัวเลขในบัญชี" (The Cost of Hustle).

Same drawn style and conventions as `scenes.py` (local time `t`, events in
`self.ev`, camera returns (cx, cy, view width)).
"""

from __future__ import annotations

import math
import random
from functools import lru_cache

from PIL import Image, ImageDraw, ImageFont

import art
import character as C
from art import INK, Pen, ease_out_back, inked, mix, paste, shade, smoothstep
from scenes import NIGHT, Scene, _cache, lerp, place, sprite, walker
from scenes_ep02 import building, ring, thought_cloud

GREEN, RED = (88, 170, 120), (214, 84, 72)


@lru_cache(maxsize=None)
def thai_font(size, bold=True):
    return ImageFont.truetype("LeelaUIb.ttf" if bold else "LeelawUI.ttf", size)


def text(pen, x, y, s, size, fill, anchor="mm", bold=True):
    pen.d.text((x * pen.ss, y * pen.ss), s, font=thai_font(int(size * pen.ss), bold), fill=fill, anchor=anchor)


def money(n):
    return f"{int(n):,}"


def card(label, amount, color, w=360, h=120, icon="฿"):
    """Inked notification / balance card: coin icon, Thai label, amount."""
    def make():
        pen = Pen(w, h)
        pen.rect(0, 0, w, h, (255, 253, 248), radius=26)
        pen.circle(58, h / 2, 34, INK)
        pen.circle(58, h / 2, 30, color)
        if icon == "check":
            pen.line([(42, h / 2), (54, h / 2 + 12), (76, h / 2 - 12)], (255, 255, 255), 7)
        else:
            text(pen, 58, h / 2 - 2, icon, 38, (255, 255, 255))
        text(pen, 108, h * 0.32, label, 26, (120, 112, 120), anchor="lm", bold=False)
        text(pen, 108, h * 0.66, amount, 40, INK, anchor="lm")
        return inked(pen.result(), 3.5)
    return _cache.get(("ep3_card", label, amount, color, w, h, icon), make)


def pop_scale(dt, dur=0.4):
    return 0.3 + 0.7 * ease_out_back(dt / dur)


def paste_scaled(world, spr, cx, cy, k, alpha=1.0):
    if k <= 0.02:
        return
    if abs(k - 1) > 0.01:
        spr = spr.resize((max(1, int(spr.width * k)), max(1, int(spr.height * k))), Image.BILINEAR)
    paste(world, spr, cx - spr.width / 2, cy - spr.height / 2, alpha)


def clock(world, cx, cy, r, t, speed):
    d = ImageDraw.Draw(world)
    d.ellipse((cx - r - 6, cy - r - 6, cx + r + 6, cy + r + 6), fill=INK)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(250, 248, 240))
    for k in range(12):
        a = k * math.pi / 6
        d.line((cx + 0.8 * r * math.sin(a), cy - 0.8 * r * math.cos(a), cx + 0.9 * r * math.sin(a),
                cy - 0.9 * r * math.cos(a)), fill=INK, width=4)
    for length, rate, w in ((0.5, speed / 12, 9), (0.78, speed, 6)):
        a = 2 * math.pi * rate * t
        d.line((cx, cy, cx + length * r * math.sin(a), cy - length * r * math.cos(a)), fill=INK, width=w)
    d.ellipse((cx - 7, cy - 7, cx + 7, cy + 7), fill=RED)


def cup(pen, x, y, k=1.0, can=False):
    if can:
        pen.rect(x - 15 * k, y - 50 * k, x + 15 * k, y, INK, radius=5 * k)
        pen.rect(x - 11 * k, y - 46 * k, x + 11 * k, y - 4 * k, (60, 90, 170), radius=4 * k)
        pen.poly([(x + 2 * k, y - 40 * k), (x - 6 * k, y - 22 * k), (x + 1 * k, y - 22 * k), (x - 4 * k, y - 10 * k),
                  (x + 7 * k, y - 28 * k), (x, y - 28 * k)], (250, 200, 70))
    else:
        pen.poly([(x - 20 * k, y - 56 * k), (x + 20 * k, y - 56 * k), (x + 14 * k, y), (x - 14 * k, y)], INK)
        pen.poly([(x - 16 * k, y - 52 * k), (x + 16 * k, y - 52 * k), (x + 11 * k, y - 4 * k), (x - 11 * k, y - 4 * k)],
                 (246, 240, 230))
        pen.rect(x - 15 * k, y - 38 * k, x + 15 * k, y - 24 * k, (150, 104, 76))
        pen.rect(x - 22 * k, y - 62 * k, x + 22 * k, y - 52 * k, INK, radius=4 * k)


def desk_set(pen, x, top, floor, k, night=True):
    """Desk with a laptop seen from the side; `x` is the desk's left edge."""
    w = 120 * k
    pen.rect(x - 4, top - 4, x + w + 4, top + 5 * k, INK, radius=6)
    pen.rect(x, top, x + w, top + 4 * k, (150, 112, 92), radius=4)
    for lx in (x + 8 * k, x + w - 12 * k):
        pen.rect(lx - 3, top, lx + 4 * k + 3, floor, INK)
        pen.rect(lx, top, lx + 4 * k, floor, (128, 94, 78))
    lx = x + 12 * k
    pen.poly([(lx - 2, top + 1), (lx + 34 * k, top + 1), (lx + 34 * k, top - 3 * k), (lx - 2, top - 3 * k)], INK)
    pen.poly([(lx, top - 1), (lx + 32 * k, top - 1), (lx + 32 * k, top - 2 * k), (lx, top - 2 * k)], (190, 196, 210))
    pen.poly([(lx + 30 * k, top - 2 * k), (lx + 34 * k, top - 2 * k), (lx + 42 * k, top - 30 * k),
              (lx + 38 * k, top - 30 * k)], INK)
    return lx + 40 * k, top - 16 * k  # screen glow point


def chair(pen, x, floor, k):
    seat = floor - 18 * k
    pen.rect(x - 14 * k, seat - 3, x + 12 * k, seat + 4 * k, INK, radius=6)
    pen.rect(x - 13 * k, seat, x + 11 * k, seat + 3 * k, (70, 72, 92), radius=5)
    pen.rect(x - 16 * k, seat - 34 * k, x - 11 * k, seat + 2 * k, INK, radius=6)
    pen.rect(x - 15 * k, seat - 33 * k, x - 12 * k, seat, (70, 72, 92), radius=4)
    pen.rect(x - 2 * k, seat + 4 * k, x + 2 * k, floor - 3 * k, INK)
    pen.rect(x - 12 * k, floor - 4 * k, x + 12 * k, floor, INK, radius=4)


def office(W, H, X, GROUND, k, sky=True):
    pen = Pen(W, H, base=art.vgradient(W, H, [(0, (64, 68, 100)), (1, (50, 52, 82))]))
    pen.rect(0, GROUND, W, H, (44, 44, 70))
    pen.rect(0, GROUND - 4, W, GROUND + 4, INK)
    if sky:
        pen.rect(X - 34 * k - 8, 150, X + 70 * k + 8, 680, INK, radius=10)
    glow = desk_set(pen, X + 14 * k, GROUND - 33 * k, GROUND, k)
    chair(pen, X - 2 * k, GROUND, k)
    return pen, glow


# --- 1. the balance keeps rising ------------------------------------------------------

class BalanceRise(Scene):
    X, GROUND, S = 800, 1180, 6.2

    def build(self):
        pen, self.glow_pt = office(self.W, self.H, self.X, self.GROUND, self.S)
        pen.vgrad_rect(self.X - 34 * self.S, 150, self.X + 70 * self.S, 680, [(0, (20, 26, 60)), (1, (50, 54, 100))])
        art.stars(pen, self.X - 34 * self.S, 160, self.X + 70 * self.S, 400, 30, seed=2)
        art.city_skyline(pen, self.X - 34 * self.S, self.X + 70 * self.S, 680, (34, 40, 76), lit=0.4, max_h=260, seed=5)
        img = pen.result()
        return art.add_glow(img, *self.glow_pt, 260, (180, 210, 255), 0.4)

    def compose(self, t, world):
        tire = smoothstep((t - self.ev.get("cost", self.duration * 0.5)) / 3.0)
        level = round(tire * 4) / 4
        tint = tuple(round(lerp(1.0, v, level), 2) for v in (0.78, 0.8, 0.9))
        spr = sprite("ep3_type", C.type_desk, C.MAIN, self.S, 1, tint=tint, blink=C.blink_at(t),
                     phase=int(t * 6) % 2 * 0.25)
        place(world, spr, self.X, self.GROUND, self.S)
        clock(world, 1840, 300, 90, t, 1.6)
        u = smoothstep(t / self.duration)
        bal = card("ยอดเงินในบัญชี", money(round(lerp(48000, 1265000, u ** 1.3), -2)), GREEN, 520, 150)
        paste(world, bal, 1580 - bal.width / 2, 520)
        for i in range(int(self.duration / 1.3) + 1):
            te = 0.4 + i * 1.3
            dt = t - te
            if 0 <= dt < 2.4:
                c = card("เงินเข้า", "+" + money(12500 + 2500 * (i % 4)), GREEN, 330, 110)
                paste_scaled(world, c, 1640 + 90 * (i % 2), 960 - 140 * smoothstep(dt / 2.4), pop_scale(dt),
                             min(1.0, (2.4 - dt) / 0.5))

    def camera(self, t):
        u = self.u(t)
        return lerp(1200, 1250, u), lerp(675, 700, u), lerp(2400, 2050, u)


# --- 2. years of hustle: day-night cycles, cups pile up, the dream of "later" -----------

class HustleYears(Scene):
    X, GROUND, S = 800, 1180, 6.2
    WIN = None

    def build(self):
        pen, self.glow_pt = office(self.W, self.H, self.X, self.GROUND, self.S)
        self.WIN = (int(self.X - 34 * self.S), 150, int(self.X + 70 * self.S), 680)
        pen.rect(1640, 220, 1900, 520, INK, radius=12)
        pen.rect(1646, 226, 1894, 514, (250, 248, 240), radius=10)
        pen.rect(1646, 226, 1894, 300, RED, radius=10)
        return art.add_glow(pen.result(), *self.glow_pt, 260, (180, 210, 255), 0.35)

    def compose(self, t, world):
        x0, y0, x1, y1 = self.WIN
        cyc = (t / 2.4) % 1.0
        day = 0.5 - 0.5 * math.cos(cyc * 2 * math.pi)
        top = mix((20, 26, 62), (150, 200, 240), day)
        bottom = mix((54, 58, 104), (250, 226, 190), day)
        world.paste(art.vgradient(x1 - x0, y1 - y0, [(0, top), (1, bottom)]), (x0, y0))
        d = ImageDraw.Draw(world)
        sx, sy = lerp(x0 + 40, x1 - 40, cyc), y1 - 60 - 300 * math.sin(math.pi * cyc)
        col = (255, 226, 140) if day > 0.5 else (240, 236, 214)
        d.ellipse((sx - 40, sy - 40, sx + 40, sy + 40), fill=col)
        skyline = _cache.get("ep3_win_city", lambda: self._skyline(x1 - x0))
        world.paste(skyline, (x0, y1 - skyline.height), skyline)
        month = int(t / 1.2) % 12 + 1
        year = 2019 + int(t / 1.2) // 12 + int(t // 2.4) // 3
        page = _cache.get(("ep3_cal", year, month), lambda: self._calendar(year, month))
        world.paste(page, (1646, 226))
        n = min(9, int(t * 0.9) + 1)
        stuff = _cache.get(("ep3_cups", n), lambda: self._cups(n))
        top_y = self.GROUND - 33 * self.S
        paste(world, stuff, self.X + 14 * self.S + 64 * self.S, top_y - stuff.height + 2)
        spr = sprite("ep3_type", C.type_desk, C.MAIN, self.S, 1, blink=C.blink_at(t, offset=0.8),
                     phase=int(t * 6) % 2 * 0.25)
        place(world, spr, self.X, self.GROUND, self.S)
        ding = self.ev.get("ding")
        if ding is not None:
            for i in range(4):
                dt = t - ding - i * 0.45
                if 0 <= dt < 2.0:
                    c = card("เงินเข้า", "+" + money(15000 + 5000 * i), GREEN, 300, 100)
                    paste_scaled(world, c, self.glow_pt[0] + 120 + 140 * i, 640 - 160 * smoothstep(dt / 2),
                                 pop_scale(dt), min(1.0, (2.0 - dt) / 0.5))
        endure = self.ev.get("endure")
        if endure is not None and t >= endure:
            dt = t - endure
            cloud = thought_cloud(420)
            k = pop_scale(dt, 0.6)
            dream = _cache.get("ep3_dream", self._dream)
            cx, cy = 1330, 420 + 10 * math.sin(t * 1.5)
            paste_scaled(world, cloud, cx, cy, k)
            paste_scaled(world, dream, cx, cy + 6, k * 0.9)

    @staticmethod
    def _calendar(year, month):
        pen = Pen(248, 288)
        pen.rect(0, 0, 248, 288, (250, 248, 240))
        pen.rect(0, 0, 248, 74, RED)
        text(pen, 124, 37, str(year), 40, (255, 255, 255))
        text(pen, 124, 176, f"{month:02d}", 110, INK)
        return pen.result().convert("RGB")

    @staticmethod
    def _skyline(w):
        pen = Pen(w, 200)
        art.city_skyline(pen, 0, w, 200, (60, 64, 100), window=(255, 214, 150), lit=0.3, max_h=180, seed=7)
        return pen.result()

    @staticmethod
    def _cups(n):
        pen = Pen(60 * n + 40, 90)
        for i in range(n):
            cup(pen, 30 + 60 * i, 88, 1.0, can=i % 3 == 1)
        return pen.result()

    @staticmethod
    def _dream():
        pen = Pen(260, 150)
        pen.rect(0, 112, 260, 150, (130, 190, 230))
        pen.ellipse(130, 118, 140, 24, (246, 222, 170))
        pen.circle(210, 40, 24, (255, 214, 110))
        pen.rect(60, 50, 66, 118, (140, 100, 70))
        pen.rect(196, 50, 202, 118, (140, 100, 70))
        pen.line([(66, 60), (130, 92), (196, 60)], INK, 9)
        pen.line([(66, 60), (130, 92), (196, 60)], (236, 120, 110), 6)
        return pen.result()

    def camera(self, t):
        u = self.u(t)
        return lerp(1220, 1260, u), lerp(660, 680, u), lerp(2400, 2200, u)


# --- 3. the body sends its warning; the bill arrives -------------------------------------

class BodyWarning(Scene):
    X, GROUND, S = 1150, 1200, 6.6

    def build(self):
        pen, _ = office(self.W, self.H, 420, self.GROUND, 6.0, sky=False)
        img = pen.result()
        return art.add_glow(img, 1150, 700, 900, (40, 40, 66), 0.2)

    def compose(self, t, world):
        chest = (self.X + 6 * self.S, self.GROUND - 58 * self.S)
        for k in range(3):
            p = (t - k * 0.42) % 1.26
            ring(world, chest[0], chest[1], 30 + 260 * p / 1.26, (236, 96, 90), 0.6 * (1 - p / 1.26), 8)
        spr = sprite("ep3_chest", C.clutch_chest, C.MAIN, self.S, 1, blink=C.blink_at(t, offset=0.3))
        place(world, spr, self.X, self.GROUND, self.S)
        tb = self.ev.get("bill")
        if tb is not None and t >= tb:
            dt = t - tb
            paper = _cache.get("ep3_bill", bill_sprite)
            y = lerp(-200, 560, smoothstep(dt / 2.2))
            x = 1720 + 60 * math.sin(dt * 2.2)
            rot = 14 * math.sin(dt * 2.0) * (1 - smoothstep(dt / 2.2))
            p = paper.rotate(rot, expand=True, resample=Image.BICUBIC)
            paste(world, p, x - p.width / 2, y - p.height / 2)

    def camera(self, t):
        u = self.u(t)
        return lerp(1260, 1300, u), lerp(700, 660, u), lerp(2300, 1900, u)


def bill_sprite():
    pen = Pen(300, 380)
    pen.rect(0, 0, 300, 380, (252, 250, 244), radius=8)
    pen.rect(0, 0, 300, 70, (230, 236, 240), radius=8)
    pen.rect(20, 18, 54, 52, RED, radius=6)
    pen.rect(33, 22, 41, 48, (255, 255, 255))
    pen.rect(24, 31, 50, 39, (255, 255, 255))
    text(pen, 70, 35, "ค่ารักษาพยาบาล", 26, INK, anchor="lm")
    for k in range(6):
        y = 104 + k * 34
        pen.rect(24, y, 190 if k % 2 else 220, y + 8, (200, 196, 194), radius=4)
        pen.rect(236, y, 276, y + 8, (200, 196, 194), radius=4)
    pen.rect(20, 314, 280, 318, INK)
    text(pen, 24, 346, "รวม", 26, INK, anchor="lm")
    text(pen, 278, 346, "1,480,000", 30, RED, anchor="rm")
    return inked(pen.result(), 3.5)


# --- 4. at the hospital, holding the bill: years that can't be bought back ---------------

class BillHospital(Scene):
    X, GROUND, S = 1200, 1230, 6.8

    def build(self):
        W, H = self.W, self.H
        pen = Pen(W, H, base=art.vgradient(W, H, [(0, (214, 232, 226)), (1, (198, 222, 214))]))
        pen.rect(0, 0, W, 120, (236, 240, 238))
        for x in range(150, W, 520):
            pen.rect(x, 40, x + 300, 80, (255, 252, 236), radius=12)
        pen.rect(0, 116, W, 124, INK)
        pen.rect(0, 760, W, 776, INK, radius=4)
        pen.rect(0, 763, W, 773, (170, 184, 190), radius=3)
        pen.rect(0, 860, W, 1230, (180, 208, 200))
        pen.rect(0, 856, W, 864, INK)
        for x0 in (200, 1900):
            pen.rect(x0 - 6, 330, x0 + 306, 1230, INK, radius=8)
            pen.rect(x0, 336, x0 + 300, 1230, (236, 240, 244), radius=6)
            pen.rect(x0 + 40, 380, x0 + 110, 640, (180, 210, 230), radius=8)
            pen.rect(x0 + 230, 760, x0 + 250, 860, (160, 166, 176), radius=6)
        pen.rect(1966, 230, 2134, 300, INK, radius=10)
        pen.rect(1970, 234, 2130, 296, RED, radius=8)
        text(pen, 2050, 264, "ER", 46, (255, 255, 255))
        pen.rect(0, 1230, W, H, (226, 228, 222))
        pen.rect(0, 1226, W, 1234, INK)
        for x in range(0, W, 160):
            pen.rect(x, 1234, x + 3, H, (208, 210, 204))
        return pen.result()

    def compose(self, t, world):
        spr = sprite("ep3_paper", C.hold_paper, C.MAIN, self.S, 1, blink=C.blink_at(t, offset=1.1))
        place(world, spr, self.X, self.GROUND, self.S)
        if t > 0.3:
            dt = t - 0.3
            bill = card("ค่ารักษาพยาบาล", "1,480,000", RED, 460, 140)
            save = card("เงินเก็บก้อนแรก", "1,265,000", GREEN, 460, 140)
            k = pop_scale(dt, 0.5)
            paste_scaled(world, bill, 640, 420 + 8 * math.sin(t * 1.3), k)
            paste_scaled(world, save, 1760, 470 + 8 * math.sin(t * 1.3 + 1), k * 0.86)
        te = self.ev.get("time")
        if te is not None and t >= te:
            rnd = random.Random(5)
            page = _cache.get("ep3_page", page_sprite)
            for i in range(12):
                dt = t - te - i * 0.32
                if dt <= 0:
                    continue
                x = self.X + 60 + 520 * dt + rnd.uniform(-40, 40)
                y = 760 - 160 * dt + 60 * math.sin(dt * 3 + i) + rnd.uniform(-60, 60)
                a = max(0.0, 1 - dt / 2.6)
                if a > 0:
                    p = page.rotate((dt * 140 + i * 40) % 360, expand=True, resample=Image.BICUBIC)
                    paste(world, p, x - p.width / 2, y - p.height / 2, a)

    def camera(self, t):
        u = self.u(t)
        return lerp(1200, 1220, u), lerp(690, 700, u), lerp(2400, 2100, u)


def page_sprite():
    pen = Pen(90, 100)
    pen.rect(0, 0, 90, 100, (252, 250, 244), radius=6)
    pen.rect(0, 0, 90, 26, RED, radius=6)
    pen.rect(22, 44, 68, 80, (210, 206, 204), radius=4)
    return inked(pen.result(), 2.5)


# --- 5. the sealed office; outside, the world keeps turning ---------------------------------

class SealedOffice(Scene):
    W = 3700
    X, GROUND, S = 700, 1180, 6.2
    WALL = (1900, 2010)

    def build(self):
        W, H = self.W, self.H
        pen = Pen(W, H, base=art.vgradient(W, H, [(0, (150, 200, 236)), (0.6, (226, 238, 230)), (1, (226, 238, 230))]))
        art.hills(pen, self.WALL[1], W, 900, 50, (176, 210, 168), period=900)
        pen.rect(self.WALL[1], 1000, W, H, (150, 196, 140))
        pen.rect(self.WALL[1], 1060, W, 1150, (224, 206, 166))
        pen.rect(0, 0, self.WALL[0], H, (150, 152, 158))
        pen.rect(0, 0, self.WALL[0], 120, (128, 130, 138))
        pen.rect(200, 60, 700, 84, (240, 244, 236), radius=8)
        pen.rect(1100, 60, 1600, 84, (240, 244, 236), radius=8)
        pen.rect(0, self.GROUND, self.WALL[0], H, (120, 122, 132))
        pen.rect(0, self.GROUND - 4, self.WALL[0], self.GROUND + 4, INK)
        for x in (1220, 1560):
            pen.rect(x - 4, 520, x + 254, 1180, INK)
            pen.rect(x, 524, x + 250, 1180, (138, 140, 150))
            pen.rect(x + 20, 1080, x + 230, 1180, (126, 128, 138))
        pen.rect(self.WALL[0] - 6, 0, self.WALL[1] + 6, H, INK)
        pen.rect(self.WALL[0], 0, self.WALL[1], H, (112, 114, 124))
        desk_set(pen, self.X + 14 * self.S, self.GROUND - 33 * self.S, self.GROUND, self.S)
        chair(pen, self.X - 2 * self.S, self.GROUND, self.S)
        for i in range(7):
            cup(pen, self.X + 82 * self.S + 52 * i, self.GROUND - 33 * self.S + 2, 0.95, can=i % 2 == 0)
        return pen.result()

    def compose(self, t, world):
        flick = 1.0 if (t * 7) % 5 > 0.4 else 0.85
        if flick < 1:
            world.paste((140, 142, 150), (200, 60, 700, 84))
        spr = sprite("ep3_sleep", C.asleep_desk, C.MAIN, self.S, 1, tint=(0.9, 0.9, 0.94))
        place(world, spr, self.X, self.GROUND + 2 * math.sin(t * 1.8), self.S)
        self.battery(world, t)
        self.outside(world, t)

    def battery(self, world, t):
        bx, by = self.X + 30 * self.S, self.GROUND - 92 * self.S
        level = max(0.08, 1 - t / max(1.0, self.ev.get("outside", self.duration * 0.6)))
        d = ImageDraw.Draw(world)
        d.rounded_rectangle((bx - 6, by - 6, bx + 166, by + 76), 14, fill=INK)
        d.rounded_rectangle((bx, by, bx + 160, by + 70), 10, fill=(240, 240, 236))
        d.rectangle((bx + 166, by + 22, bx + 182, by + 48), fill=INK)
        col = GREEN if level > 0.5 else ((236, 180, 70) if level > 0.25 else RED)
        if level > 0.25 or int(t * 3) % 2 == 0:
            d.rounded_rectangle((bx + 8, by + 8, bx + 8 + 144 * level, by + 62), 6, fill=col)

    def outside(self, world, t):
        seasons = [(116, 176, 116), (236, 170, 90), (230, 236, 240), (240, 176, 200)]
        k = (t / 2.6) % 4
        leaf = mix(seasons[int(k)], seasons[(int(k) + 1) % 4], smoothstep(k % 1))
        pen_key = ("ep3_tree", tuple(c // 6 for c in leaf))
        tree = _cache.get(pen_key, lambda: self._tree(leaf))
        for x in (2250, 3050):
            paste(world, tree, x - tree.width / 2, 1080 - tree.height)
        for i, (x0, v, y, s) in enumerate(((2100, 120, 1150, 4.6), (3500, -90, 1110, 4.0), (2600, 150, 1170, 4.8))):
            x = 2010 + (x0 - 2010 + v * t) % 1700
            f = 1 if v > 0 else -1
            pal = C.OTHERS[(i * 3 + 2) % len(C.OTHERS)]
            place(world, walker("ep3_park", t / 0.9 + i * 0.3, pal, s, facing=f), x, y, s, f)
        bfly = _cache.get(("bf", int(t * 8) % 2), lambda: art.butterfly_sprite(int(t * 8) % 2 == 0))
        paste(world, bfly, 2700 + 200 * math.sin(t * 0.8), 760 + 60 * math.sin(t * 2.1))

    @staticmethod
    def _tree(leaf):
        pen = Pen(520, 560)
        art.tree(pen, 260, 556, h=540, leaf=leaf)
        return pen.result()

    def camera(self, t):
        to = self.ev.get("outside", self.duration * 0.6)
        u = smoothstep((t - to + 0.4) / 2.6)
        return lerp(1150, 2700, u), lerp(700, 690, u), lerp(2250, 2200, u)


# --- 6. building tomorrow, forgetting today ---------------------------------------------------

class FutureHouse(Scene):
    W = 3200
    X0, SPEED, GROUND, S = 600, 95, 1180, 5.4

    def build(self):
        W, H = self.W, self.H
        pen = Pen(W, H, base=art.vgradient(W, H, [(0, (150, 176, 226)), (0.55, (250, 210, 180)), (1, (250, 210, 180))]))
        art.hills(pen, 0, W, 760, 90, (196, 200, 214), period=1300)
        art.hills(pen, 0, W, 900, 60, (170, 204, 150), period=900, phase=1.0)
        pen.rect(0, 1000, W, H, (156, 200, 140))
        pts = [(x, 1190 - 0.12 * max(0, x - 1500)) for x in range(-40, W + 60, 40)]
        pen.line(pts, (210, 186, 140), 120)
        pen.line(pts, (232, 214, 170), 96)
        hx, hy = 2900, 980
        pen.rect(hx - 120, hy - 140, hx + 120, hy, INK, radius=6)
        pen.rect(hx - 114, hy - 134, hx + 114, hy - 4, (250, 232, 196), radius=4)
        pen.poly([(hx - 160, hy - 130), (hx, hy - 260), (hx + 160, hy - 130)], INK)
        pen.poly([(hx - 140, hy - 136), (hx, hy - 248), (hx + 140, hy - 136)], (226, 112, 96))
        pen.rect(hx - 30, hy - 80, hx + 30, hy - 4, (150, 104, 80))
        img = pen.result()
        return art.add_glow(img, hx, hy - 120, 380, (255, 236, 180), 0.55)

    def main_x(self, t):
        now = self.ev.get("now", self.duration * 0.5)
        return self.X0 + self.SPEED * min(t, now)

    def compose(self, t, world):
        now = self.ev.get("now", self.duration * 0.5)
        x = self.main_x(t)
        if t < now:
            spr = walker("ep3_walk", t / 1.2, C.MAIN, self.S, stride=18.0, look=(1.4, -0.6))
        else:
            spr = sprite("ep3_look_down", C.stand, C.MAIN, self.S, 1, look=(1.0, 2.4), blink=C.blink_at(t))
        place(world, spr, x, self.GROUND, self.S)
        if t >= now:
            rnd = random.Random(12)
            for i in range(14):
                dt = t - now - 0.12 * i
                if dt <= 0:
                    continue
                fx = x + rnd.uniform(-420, 420)
                fy = self.GROUND + rnd.uniform(-10, 120)
                k = ease_out_back(dt / 0.5)
                petal = rnd.choice([(250, 180, 196), (250, 220, 130), (196, 186, 250), (250, 160, 140)])
                fl = _cache.get(("ep3_flower", petal), lambda: self._flower(petal))
                paste_scaled(world, fl, fx, fy - fl.height * 0.5 * k, k)

    @staticmethod
    def _flower(petal):
        pen = Pen(60, 90)
        art.flower(pen, 30, 26, 14, petal=petal)
        return pen.result()

    def camera(self, t):
        now = self.ev.get("now", self.duration * 0.5)
        down = smoothstep((t - now) / 2.0)
        x = self.main_x(t)
        return lerp(x + 650, x + 100, down), lerp(675, 780, down), lerp(2400, 1700, down)


# --- 7. what was really paid: breath and time, no change given -------------------------------

class ScaleTime(Scene):
    PIVOT = (1200, 380)
    ARM = 560

    def build(self):
        W, H = self.W, self.H
        pen = Pen(W, H, base=art.vgradient(W, H, [(0, (244, 236, 222)), (1, (232, 220, 202))]))
        pen.rect(0, 1150, W, H, (214, 198, 176))
        pen.rect(0, 1146, W, 1154, INK)
        px, py = self.PIVOT
        pen.rect(px - 22, py, px + 22, 1110, INK, radius=8)
        pen.rect(px - 16, py, px + 16, 1110, (196, 160, 96), radius=6)
        pen.rect(px - 160, 1090, px + 160, 1150, INK, radius=14)
        pen.rect(px - 154, 1096, px + 154, 1146, (196, 160, 96), radius=12)
        return pen.result()

    def tilt(self, t):
        tip = self.ev.get("tip", self.duration * 0.5)
        return -4 + 16 * smoothstep((t - tip) / 2.5)

    def compose(self, t, world):
        px, py = self.PIVOT
        a = math.radians(self.tilt(t))
        ends = [(px - self.ARM * math.cos(a), py - self.ARM * math.sin(a)),
                (px + self.ARM * math.cos(a), py + self.ARM * math.sin(a))]
        d = ImageDraw.Draw(world)
        d.line((*ends[0], *ends[1]), fill=INK, width=26)
        d.line((*ends[0], *ends[1]), fill=(196, 160, 96), width=16)
        d.ellipse((px - 30, py - 30, px + 30, py + 30), fill=INK)
        d.ellipse((px - 22, py - 22, px + 22, py + 22), fill=(236, 200, 120))
        pans = []
        for ex, ey in ends:
            pan_y = ey + 300
            for sx in (-150, 150):
                d.line((ex, ey, ex + sx, pan_y), fill=INK, width=5)
            d.chord((ex - 190, pan_y - 60, ex + 190, pan_y + 60), 0, 180, fill=INK)
            d.chord((ex - 182, pan_y - 52, ex + 182, pan_y + 52), 0, 180, fill=(220, 186, 118))
            pans.append((ex, pan_y))
        coins = _cache.get("ep3_coins", self._coins)
        paste(world, coins, pans[0][0] - coins.width / 2, pans[0][1] - coins.height + 8)
        tip = self.ev.get("tip", self.duration * 0.5)
        drain = smoothstep((t - tip + 0.5) / 3.5)
        glass = self._hourglass(drain)
        paste(world, glass, pans[1][0] + 30 - glass.width / 2, pans[1][1] - glass.height + 6)
        heart = _cache.get("ep3_heart", self._heart)
        hk = (1 - 0.35 * drain) * (1 + 0.06 * math.sin(t * 6))
        paste_scaled(world, heart, pans[1][0] - 110, pans[1][1] - 60, hk, 1 - 0.5 * drain)
        if drain > 0:
            rnd = random.Random(3)
            for i in range(40):
                dt = (t - tip) - i * 0.06
                if dt <= 0:
                    continue
                gx = pans[1][0] + 30 + 60 * dt * (1 + rnd.random()) + 40 * math.sin(dt * 3 + i)
                gy = pans[1][1] - 140 - 80 * dt * rnd.random() + 30 * dt * dt
                al = max(0.0, 1 - dt / 2.5)
                if al > 0:
                    c = mix((240, 230, 214), (226, 186, 110), al)
                    d.ellipse((gx - 6, gy - 6, gx + 6, gy + 6), fill=c)
        self.receipt(world, t, tip)

    def receipt(self, world, t, tip):
        dt = t - tip - 1.2
        if dt <= 0:
            return
        slip = _cache.get("ep3_receipt", self._receipt)
        shown = int(slip.height * smoothstep(dt / 1.2))
        if shown < 4:
            return
        part = slip.crop((0, 0, slip.width, shown))
        paste(world, part, 2110 - slip.width / 2, 300)

    @staticmethod
    def _receipt():
        pen = Pen(300, 360)
        pen.rect(0, 0, 300, 360, (252, 252, 248))
        for x in range(0, 300, 20):
            pen.poly([(x, 360), (x + 10, 346), (x + 20, 360)], (232, 220, 202))
        text(pen, 150, 44, "ใบเสร็จ", 34, INK)
        pen.rect(24, 76, 276, 79, (200, 196, 194))
        text(pen, 26, 116, "จ่ายด้วย", 24, (120, 112, 120), anchor="lm", bold=False)
        text(pen, 274, 116, "เวลา", 26, INK, anchor="rm")
        text(pen, 274, 160, "ลมหายใจ", 26, INK, anchor="rm")
        pen.rect(24, 196, 276, 199, (200, 196, 194))
        text(pen, 26, 244, "เงินทอน", 30, INK, anchor="lm")
        text(pen, 274, 244, "0.00", 40, RED, anchor="rm")
        return inked(pen.result(), 3)

    @staticmethod
    def _coins():
        pen = Pen(320, 240)
        rnd = random.Random(1)
        for col, n in ((70, 5), (130, 7), (190, 6), (250, 4)):
            for i in range(n):
                y = 226 - i * 26
                pen.ellipse(col, y, 52, 18, INK)
                pen.ellipse(col, y - 2, 48, 14, (246, 200, 84))
        pen.rect(110, 60, 290, 140, INK, radius=8)
        pen.rect(116, 66, 284, 134, (150, 196, 140), radius=6)
        pen.circle(200, 100, 24, (120, 170, 112))
        return pen.result()

    @staticmethod
    def _heart():
        pen = Pen(140, 130)
        for grow, col in ((5, INK), (0, (232, 96, 100))):
            pen.circle(46, 46, 32 + grow, col)
            pen.circle(94, 46, 32 + grow, col)
            pen.poly([(14 - grow, 58), (126 + grow, 58), (70, 124 + grow)], col)
        return pen.result()

    @staticmethod
    def _hourglass(drain):
        q = round(drain * 12) / 12
        def make():
            pen = Pen(170, 260)
            pen.rect(0, 0, 170, 22, INK, radius=8)
            pen.rect(0, 238, 170, 260, INK, radius=8)
            for x in (14, 150):
                pen.rect(x, 20, x + 8, 240, (140, 104, 76))
            pen.poly([(24, 22), (146, 22), (92, 130), (146, 238), (24, 238), (78, 130)], INK)
            pen.poly([(30, 26), (140, 26), (88, 130), (140, 234), (30, 234), (82, 130)], (236, 244, 250))
            top_h = 90 * (1 - q)
            if top_h > 2:
                y0 = 120 - top_h
                pen.poly([(85 - 52 * top_h / 90, y0), (85 + 52 * top_h / 90, y0), (85, 122)], (226, 186, 110))
            bot_h = 40 * (1 - q) + 10
            pen.poly([(34, 232), (136, 232), (85, 232 - bot_h)], (226, 186, 110))
            return pen.result()
        return _cache.get(("ep3_glass", q), make)

    def camera(self, t):
        u = self.u(t)
        return 1240, lerp(700, 690, u), lerp(2400, 2100, u)


# --- 8. the hospital room in the rain; the body's pain replaces the notifications ------------------

class HospitalRain(Scene):
    X, ORIGIN, S = 900, 1020, 6.4

    def build(self):
        W, H = self.W, self.H
        S, X, O = self.S, self.X, self.ORIGIN
        pen = Pen(W, H, base=art.vgradient(W, H, [(0, (206, 222, 220)), (1, (190, 210, 206))]))
        pen.rect(0, 1230, W, H, (210, 214, 206))
        pen.rect(0, 1226, W, 1234, INK)
        pen.rect(1394, 166, 2106, 714, INK, radius=12)
        pen.vgrad_rect(1400, 172, 2100, 708, [(0, (70, 84, 120)), (1, (120, 132, 160))])
        art.city_skyline(pen, 1400, 2100, 708, (88, 98, 132), window=(240, 216, 170), lit=0.25, max_h=200, seed=4)
        pen.vgrad_rect(2100, 166, 2400, 716, [(0, mix((206, 222, 220), (190, 210, 206), 166 / 1350)),
                                             (1, mix((206, 222, 220), (190, 210, 206), 716 / 1350))])
        pen.rect(2100, 166, 2106, 714, INK)
        pen.rect(1744, 172, 1756, 708, INK)
        pen.rect(1394, 430, 2106, 442, INK)
        # backrest + mattress + frame
        top = O - 15 * S
        pen.rect(X - 30 * S, top - 4, X + 60 * S, top + 9 * S, INK, radius=18)
        pen.rect(X - 29 * S, top, X + 59 * S, top + 8 * S, (236, 240, 244), radius=16)
        pen.rect(X - 30 * S, top + 9 * S, X + 60 * S, top + 13 * S, (150, 156, 170), radius=6)
        for wx in (X - 24 * S, X + 54 * S):
            pen.rect(wx - 6, top + 13 * S, wx + 6, 1200, (150, 156, 170))
            pen.circle(wx, 1206, 22, INK)
            pen.circle(wx, 1206, 15, (110, 114, 128))
        a = math.radians(-24)
        bx, by = X - 8 * S, top + 2 * S
        ux, uy = math.sin(a), -math.cos(a)
        rx, ry = math.cos(a), math.sin(a)
        back = [(bx + rx * w + ux * v, by + ry * w + uy * v) for w, v in ((-10 * S, 0), (4 * S, 0), (4 * S, 50 * S), (-10 * S, 50 * S))]
        pen.poly(back, INK)
        inner = [(bx + rx * w + ux * v, by + ry * w + uy * v) for w, v in ((-9 * S, 1 * S), (3 * S, 1 * S), (3 * S, 49 * S), (-9 * S, 49 * S))]
        pen.poly(inner, (236, 240, 244))
        # IV pole + monitor + bedside table
        ix = X - 52 * S
        pen.rect(ix - 6, 300, ix + 6, 1210, INK)
        pen.rect(ix - 3, 300, ix + 3, 1210, (176, 180, 190))
        pen.rect(ix - 50, 300, ix + 50, 312, INK, radius=4)
        pen.rect(ix + 14, 312, ix + 74, 420, INK, radius=14)
        pen.rect(ix + 18, 316, ix + 70, 416, (220, 236, 246), radius=12)
        pen.rect(ix + 18, 360, ix + 70, 416, (196, 224, 240), radius=10)
        tx = X + 74 * S
        pen.rect(tx - 4, 860, tx + 254, 1230, INK, radius=10)
        pen.rect(tx, 864, tx + 250, 1230, (200, 210, 214), radius=8)
        pen.rect(tx + 40, 1000, tx + 210, 1006, INK)
        pen.rect(tx - 10, 520, tx + 270, 760, INK, radius=16)
        pen.rect(tx - 4, 526, tx + 264, 754, (40, 46, 56), radius=12)
        self.monitor = (tx + 6, 540, tx + 254, 740)
        return pen.result()

    def compose(self, t, world):
        self.rain(world, t)
        self.ecg(world, t)
        ix = self.X - 52 * self.S
        k = (t * 0.9) % 1
        d = ImageDraw.Draw(world)
        dy = 430 + 120 * k
        d.ellipse((ix + 40, dy - 6, ix + 50, dy + 6), fill=(170, 210, 240))
        d.line((ix + 44, 420, ix + 44, 560), fill=(196, 210, 220), width=4)
        spr = sprite("ep3_bed", C.recline_bed, C.MAIN, self.S, 1, blink=C.blink_at(t, offset=0.9))
        place(world, spr, self.X, self.ORIGIN, self.S)
        pain = self.ev.get("pain")
        if pain is not None and t > pain:
            cx, cy = self.X - 7 * self.S, self.ORIGIN - 37 * self.S
            fade_in = smoothstep((t - pain) / 1.0)
            for k in range(3):
                p = ((t - pain) - k * 0.5) % 1.5
                if t - pain >= k * 0.5:
                    ring(world, cx, cy, 30 + 230 * p / 1.5, (226, 90, 86), 0.55 * fade_in * (1 - p / 1.5), 7)
        blanket = _cache.get("ep3_blanket", self._blanket)
        paste(world, blanket, self.X - 6 * self.S, self.ORIGIN - 27 * self.S)
        self.phone(world, t)

    def _blanket(self):
        S = self.S
        pen = Pen(int(62 * S), int(16 * S))
        pen.rect(0, 0, 62 * S, 16 * S, INK, radius=5 * S)
        pen.rect(4, 4, 62 * S - 4, 16 * S - 4, (150, 196, 176), radius=5 * S)
        pen.rect(4, 4, 62 * S - 4, 3.2 * S, (236, 240, 244), radius=3 * S)
        return pen.result()

    def rain(self, world, t):
        d = ImageDraw.Draw(world)
        rnd = random.Random(9)
        for _ in range(60):
            x0 = rnd.uniform(1400, 2100)
            sp = rnd.uniform(700, 1000)
            y = 172 + (rnd.uniform(0, 536) + sp * t) % 536
            x = x0 - 0.15 * (y - 172)
            if 1400 < x < 2100 and not (1744 < x < 1756):
                d.line((x, y, x - 4, min(708, y + 26)), fill=(196, 210, 236), width=3)

    def ecg(self, world, t):
        x0, y0, x1, y1 = self.monitor
        d = ImageDraw.Draw(world)
        mid = (y0 + y1) / 2 + 20
        pts = []
        for i in range(0, int(x1 - x0), 4):
            ph = ((i + t * 220) % 240) / 240
            v = 0
            if 0.40 < ph < 0.44:
                v = -70 * (ph - 0.40) / 0.04
            elif 0.44 < ph < 0.48:
                v = -70 + 110 * (ph - 0.44) / 0.04
            elif 0.48 < ph < 0.52:
                v = 40 - 40 * (ph - 0.48) / 0.04
            pts.append((x0 + i, mid + v))
        d.line(pts, fill=(110, 230, 140), width=4)
        bpm = 72
        d.text((x1 - 70, y0 + 10), str(bpm), fill=(110, 230, 140), font=thai_font(36))

    def phone(self, world, t):
        tx = self.X + 74 * self.S
        px, py = tx + 70, 958
        d = ImageDraw.Draw(world)
        silence = self.ev.get("pain", self.duration * 0.6)
        buzz = 4 * math.sin(t * 60) if t < silence and int(t * 2) % 3 == 0 else 0
        d.rounded_rectangle((px - 6 + buzz, py - 6, px + 116 + buzz, py + 46), 10, fill=INK)
        d.rounded_rectangle((px + buzz, py, px + 110 + buzz, py + 40), 8, fill=(60, 64, 80))
        for i in range(6):
            appear = 0.4 + i * 0.5
            vanish = silence + 0.6 * i
            a = smoothstep((t - appear) / 0.3) * (1 - smoothstep((t - vanish) / 0.5))
            if a <= 0.02:
                continue
            bx, by = px + 20 + 34 * (i % 3), py - 40 - 46 * (i // 3)
            r = 15 * (0.5 + 0.5 * a)
            d.ellipse((bx - r - 3, by - r - 3, bx + r + 3, by + r + 3), fill=mix((200, 210, 214), INK, a))
            d.ellipse((bx - r, by - r, bx + r, by + r), fill=mix((200, 210, 214), RED, a))

    def camera(self, t):
        u = self.u(t)
        return lerp(1200, 1150, u), lerp(675, 700, u), lerp(2400, 1950, u)


SCENES = {
    "balance_rise": BalanceRise,
    "hustle_years": HustleYears,
    "body_warning": BodyWarning,
    "bill_hospital": BillHospital,
    "sealed_office": SealedOffice,
    "future_house": FutureHouse,
    "scale_time": ScaleTime,
    "hospital_rain": HospitalRain,
}
