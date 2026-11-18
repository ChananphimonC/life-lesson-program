"""Scenes for EP06 "อีเมลฉบับที่เท่าไหร่" (First Jobber's Struggle).

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
from scenes_ep02 import thought_cloud
from scenes_ep03 import GREEN, RED, card, chair, desk_set, paste_scaled, pop_scale, text

GOWN, STOLE = (46, 48, 70), (236, 190, 80)


def gown():
    def make():
        pen = Pen(360, 620)
        pen.line([(130, 40), (180, 8), (230, 40)], INK, 8)
        pen.line([(60, 70), (180, 30), (300, 70)], INK, 10)
        pen.poly([(90, 70), (270, 70), (330, 600), (30, 600)], GOWN)
        pen.poly([(30, 90), (90, 70), (60, 360), (0, 340)], shade(GOWN, 0.9))
        pen.poly([(330, 90), (270, 70), (300, 360), (360, 340)], shade(GOWN, 0.9))
        pen.poly([(150, 70), (175, 70), (160, 420), (130, 420)], STOLE)
        pen.poly([(185, 70), (210, 70), (230, 420), (200, 420)], STOLE)
        return inked(pen.result(), 4)
    return _cache.get("ep6_gown", make)


def cap():
    def make():
        pen = Pen(260, 170)
        pen.poly([(10, 60), (130, 10), (250, 60), (130, 110)], GOWN)
        pen.rect(70, 70, 190, 150, GOWN, radius=14)
        pen.line([(130, 60), (220, 80), (226, 150)], STOLE, 6)
        pen.circle(226, 154, 10, STOLE)
        return inked(pen.result(), 4)
    return _cache.get("ep6_cap", make)


def envelope(w=150, h=100, stamp=True):
    def make():
        pen = Pen(w, h)
        pen.rect(0, 0, w, h, (252, 250, 244), radius=6)
        pen.line([(4, 6), (w / 2, h * 0.58), (w - 4, 6)], (190, 184, 180), 4)
        if stamp:
            pen.circle(w / 2, h * 0.6, h * 0.17, RED)
            pen.line([(w / 2 - 8, h * 0.6 - 8), (w / 2 + 8, h * 0.6 + 8)], (255, 255, 255), 4)
            pen.line([(w / 2 + 8, h * 0.6 - 8), (w / 2 - 8, h * 0.6 + 8)], (255, 255, 255), 4)
        return inked(pen.result(), 3)
    return _cache.get(("ep6_env", w, h, stamp), make)


def room(W, H, night=False):
    top, bot = ((44, 48, 82), (34, 36, 64)) if night else ((226, 230, 236), (212, 216, 226))
    pen = Pen(W, H, base=art.vgradient(W, H, [(0, top), (1, bot)]))
    pen.rect(0, 1200, W, H, (42, 40, 62) if night else (186, 160, 136))
    pen.rect(0, 1196, W, 1204, INK)
    return pen


# --- 1. the gown goes to the back of the wardrobe ----------------------------------------------

class Wardrobe(Scene):
    X, GROUND, S = 820, 1200, 6.4
    WARD = (1300, 2100, 260)

    def build(self):
        pen = room(self.W, self.H)
        x0, x1, top = self.WARD
        pen.rect(x0 - 10, top - 10, x1 + 10, 1200, INK, radius=12)
        pen.rect(x0, top, x1, 1200, (90, 64, 52), radius=10)
        pen.rect(x0 + 30, top + 40, x1 - 30, 1160, (60, 44, 40))
        pen.rect(x0 + 30, top + 80, x1 - 30, top + 92, (170, 170, 180))
        pen.rect(160, 300, 560, 640, INK, radius=10)
        pen.rect(168, 308, 552, 632, (250, 248, 240), radius=8)
        pen.rect(200, 340, 520, 560, (200, 216, 236), radius=6)
        c = cap()
        cs = c.resize((c.width // 2, c.height // 2))
        pen.img.alpha_composite(cs.resize((cs.width * pen.ss, cs.height * pen.ss)), (int(300 * pen.ss), int(400 * pen.ss)))
        return pen.result()

    def compose(self, t, world):
        x0, x1, top = self.WARD
        g = gown()
        push = smoothstep((t - 1.0) / 2.5)
        gx = lerp(x0 + 260, x1 - 220, push)
        paste(world, g, gx - g.width / 2, top + 80)
        close = smoothstep((t - self.duration * 0.55) / 2.0)
        half = (x1 - x0) / 2
        d = ImageDraw.Draw(world)
        for side in (-1, 1):
            w = half * close
            if w < 14:
                continue
            ex = x0 if side < 0 else x1
            xa, xb = (ex, ex + w) if side < 0 else (ex - w, ex)
            d.rectangle((xa, top, xb, 1200), fill=INK)
            d.rectangle((xa + 6, top + 6, xb - 6, 1194), fill=(150, 108, 84))
            hx = xb - 30 if side < 0 else xa + 30
            d.ellipse((hx - 12, 700, hx + 12, 724), fill=(236, 196, 90))
        spr = sprite("ep6_closet", C.stand, C.MAIN, self.S, 1, look=(1.6, 0.4), blink=C.blink_at(t))
        place(world, spr, self.X, self.GROUND, self.S)

    def camera(self, t):
        u = self.u(t)
        return lerp(1300, 1250, u), lerp(700, 720, u), lerp(2200, 2400, u)


# --- 2. friends hired on the first try; for us, automatic rejections ----------------------------

class FriendsHired(Scene):
    W = 3600
    FRIENDS = [(500, 1), (900, 4), (1300, 0)]
    MAIN_X, GROUND, S = 2800, 1200, 6.4

    def build(self):
        pen = room(self.W, self.H)
        for x in range(200, 1700, 500):
            pen.rect(x, 260, x + 300, 700, INK, radius=10)
            pen.rect(x + 6, 266, x + 294, 694, (190, 210, 232), radius=8)
        pen.rect(1850, 0, 1950, 1200, INK)
        pen.rect(1856, 0, 1944, 1200, (200, 204, 214))
        pen.rect(1950, 0, self.W, 1200, (206, 208, 222))
        return pen.result()

    def compose(self, t, world):
        rnd = random.Random(1)
        for i, (x, pi) in enumerate(self.FRIENDS):
            pal = C.OTHERS[pi]
            spr = sprite("ep6_friend", C.hold_paper, pal, 5.8, 1, look=(0.0, 0.0), blink=C.blink_at(t, offset=i))
            place(world, spr, x, self.GROUND, 5.8)
        d = ImageDraw.Draw(world)
        for i in range(50):
            x = rnd.uniform(200, 1700) + 30 * math.sin(t * 2 + i)
            y = (rnd.uniform(0, 1000) + 140 * t) % 1100
            col = rnd.choice([(236, 110, 120), (250, 200, 80), (110, 180, 230), (130, 200, 140)])
            d.rectangle((x - 8, y - 4, x + 8, y + 4), fill=col)
        for i, x in enumerate(x for x, _ in self.FRIENDS):
            badge = card("สถานะ", "ผ่านแล้ว!", GREEN, 300, 100, icon="check")
            paste_scaled(world, badge, x, 440 + 10 * math.sin(t * 1.4 + i), pop_scale(t - 0.3 * i))
        spr = sprite("ep6_phone", C.front_phone, C.MAIN, self.S, 1, blink=C.blink_at(t, offset=0.6))
        place(world, spr, self.MAIN_X, self.GROUND, self.S)
        us = self.ev.get("us", self.duration * 0.4)
        for i in range(4):
            te = us + 0.6 + 0.6 * i
            if t > te:
                c = card("ทางเรามีความเสียใจอย่างยิ่ง...", "ไม่ผ่านการคัดเลือก", RED, 560, 130, icon="@")
                paste_scaled(world, c, self.MAIN_X + 400, 300 + 150 * i, pop_scale(t - te))

    def camera(self, t):
        us = self.ev.get("us", self.duration * 0.4)
        u = smoothstep((t - us + 0.3) / 2.2)
        return lerp(950, 3000, u), 680, 2400


# --- 3. the 20th, 30th, 40th email: confidence wearing thin ------------------------------------------

class EmailPile(Scene):
    X, GROUND, S = 900, 1200, 6.4

    def build(self):
        return room(self.W, self.H).result()

    def count(self, t):
        e30 = self.ev.get("n30", self.duration * 0.25)
        e40 = self.ev.get("n40", self.duration * 0.45)
        if t < e30:
            return int(lerp(12, 20, smoothstep(t / max(0.5, e30 * 0.6))))
        if t < e40:
            return int(lerp(20, 30, smoothstep((t - e30) / 0.8)))
        return int(lerp(30, 40, smoothstep((t - e40) / 0.8)))

    def compose(self, t, world):
        n = self.count(t)
        rnd = random.Random(5)
        for i in range(n):
            x = self.X + rnd.uniform(-520, 520)
            y = self.GROUND - 40 - (i // 6) * 34 + rnd.uniform(-10, 10)
            env = envelope()
            rot = rnd.uniform(-20, 20)
            e = _cache.get(("ep6_envrot", int(rot)), lambda: env.rotate(int(rot), expand=True, resample=Image.BICUBIC))
            paste(world, e, x - e.width / 2, y - e.height / 2)
        spr = sprite("ep6_down", C.stand, C.MAIN, self.S, 1, view="front", look=(0.0, 2.6), blink=C.blink_at(t))
        place(world, spr, self.X, self.GROUND, self.S)
        big = _cache.get(("ep6_count", n), lambda: self._counter(n))
        paste(world, big, 1700 - big.width / 2, 260)
        conf = max(0.06, 1 - (n - 12) / 30)
        d = ImageDraw.Draw(world)
        bx, by = 1460, 760
        text_img = _cache.get("ep6_conf_label", self._label)
        paste(world, text_img, bx, by - 70)
        d.rounded_rectangle((bx - 6, by - 6, bx + 486, by + 56), 18, fill=INK)
        d.rounded_rectangle((bx, by, bx + 480, by + 50), 14, fill=(240, 236, 230))
        col = GREEN if conf > 0.5 else ((236, 180, 70) if conf > 0.25 else RED)
        d.rounded_rectangle((bx + 6, by + 6, bx + 6 + 468 * conf, by + 44), 10, fill=col)

    @staticmethod
    def _counter(n):
        pen = Pen(520, 300)
        pen.rect(0, 0, 520, 300, (252, 250, 244), radius=30)
        text(pen, 260, 70, "อีเมลปฏิเสธฉบับที่", 40, (120, 112, 120), bold=False)
        text(pen, 260, 190, str(n), 150, RED)
        return inked(pen.result(), 4)

    @staticmethod
    def _label():
        pen = Pen(400, 60)
        text(pen, 0, 30, "ความมั่นใจ", 40, INK, anchor="lm")
        return pen.result()

    def camera(self, t):
        u = self.u(t)
        return lerp(1250, 1300, u), lerp(690, 700, u), lerp(2400, 2150, u)


# --- 4. rewriting the résumé, version after version ------------------------------------------------

class ResumeEdit(Scene):
    X, GROUND, S = 700, 1200, 6.4

    def build(self):
        pen = room(self.W, self.H)
        desk_set(pen, self.X + 14 * self.S, self.GROUND - 33 * self.S, self.GROUND, self.S)
        chair(pen, self.X - 2 * self.S, self.GROUND, self.S)
        return pen.result()

    def compose(self, t, world):
        spr = sprite("ep6_type", C.type_desk, C.MAIN, self.S, 1, blink=C.blink_at(t), phase=int(t * 6) % 2 * 0.25)
        place(world, spr, self.X, self.GROUND, self.S)
        same = self.ev.get("same", self.duration * 0.7)
        version = min(12, 1 + int(t / 0.6))
        doc = _cache.get(("ep6_resume", version), lambda: self._resume(version))
        paste(world, doc, 1560 - doc.width / 2, 170)
        if t > same:
            stamp = _cache.get("ep6_stamp", self._stamp)
            k = 1 + 1.5 * (1 - smoothstep((t - same) / 0.35))
            paste_scaled(world, stamp, 1600, 520, k, min(1.0, (t - same) / 0.2))

    @staticmethod
    def _resume(v):
        rnd = random.Random(v)
        pen = Pen(560, 760)
        pen.rect(0, 0, 560, 760, (252, 250, 244), radius=10)
        pen.circle(90, 100, 50, (200, 210, 230))
        text(pen, 170, 80, "เรซูเม่", 44, INK, anchor="lm")
        text(pen, 470, 80, f"v{v}", 40, (110, 160, 210))
        for k in range(14):
            y = 190 + k * 38
            w = rnd.uniform(220, 470)
            pen.rect(40, y, 40 + w, y + 12, (200, 196, 194), radius=5)
            if rnd.random() < 0.3:
                pen.line([(36, y + 6), (44 + w, y + 6)], RED, 4)
        return inked(pen.result(), 4)

    @staticmethod
    def _stamp():
        pen = Pen(420, 160)
        pen.rect(0, 0, 420, 160, (0, 0, 0, 0))
        pen.rect(6, 6, 414, 154, RED, radius=20)
        pen.rect(18, 18, 402, 142, (252, 236, 232), radius=14)
        text(pen, 210, 82, "ไม่ผ่าน", 80, RED)
        return pen.result().rotate(-12, expand=True, resample=Image.BICUBIC)

    def camera(self, t):
        u = self.u(t)
        return lerp(1200, 1250, u), lerp(680, 690, u), lerp(2400, 2200, u)


# --- 5. the heavy silence after leaving the interview room ----------------------------------------

class InterviewExit(Scene):
    W = 3000
    DOOR, BENCH, GROUND, S = 700, 1900, 1200, 6.4

    def build(self):
        pen = room(self.W, self.H)
        pen.rect(self.DOOR - 190, 380, self.DOOR + 190, 1200, INK, radius=8)
        pen.rect(self.DOOR - 180, 390, self.DOOR + 180, 1200, (60, 52, 58))
        pen.rect(self.DOOR - 140, 250, self.DOOR + 140, 330, INK, radius=10)
        pen.rect(self.DOOR - 134, 256, self.DOOR + 134, 324, (246, 244, 236), radius=8)
        text(pen, self.DOOR, 290, "ห้องสัมภาษณ์", 34, INK)
        bx = self.BENCH
        seat = self.GROUND - 18 * self.S
        pen.rect(bx - 260, seat - 6, bx + 260, seat + 30, INK, radius=10)
        pen.rect(bx - 254, seat, bx + 254, seat + 24, (170, 130, 96), radius=8)
        for lx in (bx - 220, bx + 200):
            pen.rect(lx - 4, seat + 30, lx + 24, self.GROUND, INK)
            pen.rect(lx, seat + 30, lx + 20, self.GROUND, (140, 104, 78))
        return pen.result()

    def compose(self, t, world):
        close = smoothstep((t - 0.6) / 1.4)
        d = ImageDraw.Draw(world)
        w = 360 * (1 - 0.9 * (1 - close))
        d.rectangle((self.DOOR - 180, 390, self.DOOR - 180 + w, 1200), fill=INK)
        d.rectangle((self.DOOR - 174, 396, self.DOOR - 186 + w, 1200), fill=(150, 108, 84))
        walk_end = 1.0 + (self.BENCH - self.DOOR - 40) / 140
        if t < walk_end:
            x = lerp(self.DOOR, self.BENCH - 40, max(0.0, t - 1.0) / (walk_end - 1.0)) if t > 1.0 else self.DOOR
            spr = walker("ep6_slow", t / 1.6, C.MAIN, self.S, stride=13.0, careful=True, look=(1.2, 2.0))
            place(world, spr, x, self.GROUND, self.S)
            self._x = x
        else:
            spr = sprite("ep6_bench", C.sit_desk_chin, C.MAIN, self.S, 1, blink=C.blink_at(t), look=(1.4, 1.8))
            place(world, spr, self.BENCH - 40, self.GROUND, self.S)
            self._x = self.BENCH - 40
        te = self.ev.get("unequal")
        if te is not None and t > te:
            cloud = thought_cloud(300)
            q = _cache.get("ep6_q", lambda: art.bubble_sprite("?", 120, INK))
            cx, cy = self._x + 260, self.GROUND - 120 * self.S
            k = pop_scale(t - te, 0.6)
            paste_scaled(world, cloud, cx, cy, k)
            paste_scaled(world, q, cx, cy + 4, k)

    def camera(self, t):
        x = getattr(self, "_x", self.DOOR)
        return x + 250, 690, 2300


# --- 6. life calendars that turn at different speeds; rejections become steps ----------------------

class Calendars(Scene):
    CALS = [(420, 1.8, (110, 160, 210)), (900, 0.5, (130, 190, 140)), (1380, 1.1, (236, 160, 90)), (1860, 0.25, RED)]

    def build(self):
        return room(self.W, self.H).result()

    def compose(self, t, world):
        for i, (x, speed, col) in enumerate(self.CALS):
            page = int(t * speed * 3) % 12 + 1
            c = _cache.get(("ep6_cal", page, col), lambda: self._cal(page, col))
            paste(world, c, x - c.width / 2, 300 + 10 * math.sin(t + i))
            pal = C.OTHERS[i * 2 % len(C.OTHERS)] if i != 3 else C.MAIN
            spr = walker("ep6_pace", t * speed * 0.8 + i * 0.25, pal, 4.4, stride=10 + 12 * speed)
            place(world, spr, x, self.GROUND if hasattr(self, "GROUND") else 1200, 4.4)

    @staticmethod
    def _cal(page, col):
        pen = Pen(300, 340)
        pen.rect(0, 0, 300, 340, (250, 248, 240), radius=14)
        pen.rect(0, 0, 300, 80, col, radius=14)
        text(pen, 150, 210, f"{page:02d}", 120, INK)
        return inked(pen.result(), 4)

    def camera(self, t):
        u = self.u(t)
        return 1150, lerp(680, 700, u), lerp(2400, 2200, u)


class EnvelopeStairs(Scene):
    W = 3200
    STEP_W, STEP_H, X0, GROUND, S = 220, 70, 500, 1240, 5.6
    N = 9

    def build(self):
        pen = Pen(self.W, self.H, base=art.vgradient(self.W, self.H, [(0, (196, 210, 236)), (1, (244, 232, 214))]))
        pen.rect(0, self.GROUND, self.W, self.H, (186, 160, 136))
        pen.rect(0, self.GROUND - 4, self.W, self.GROUND + 4, INK)
        img = pen.result()
        return art.add_glow(img, 2900, 300, 500, (255, 240, 200), 0.5)

    def step_top(self, i):
        return self.GROUND - (i + 1) * self.STEP_H

    def compose(self, t, world):
        built = min(self.N, int(t / 0.45) + 1)
        for i in range(built):
            x = self.X0 + i * self.STEP_W
            for j in range(i + 1):
                env = envelope(self.STEP_W, self.STEP_H + 6, stamp=(i + j) % 3 == 0)
                paste(world, env, x, self.GROUND - (j + 1) * self.STEP_H)
        climb_start = 1.2
        p = max(0.0, (t - climb_start) / max(1.0, self.duration - climb_start - 0.6))
        pos = min(built - 0.01, p * self.N)
        i = int(pos)
        x = self.X0 + pos * self.STEP_W + self.STEP_W * 0.5
        ground = self.step_top(i) + 2
        spr = walker("ep6_climb", t / 1.1, C.MAIN, self.S, stride=16.0, look=(1.4, -0.8))
        place(world, spr, x, ground, self.S)
        self._x, self._y = x, ground

    def camera(self, t):
        x, y = getattr(self, "_x", self.X0), getattr(self, "_y", self.GROUND)
        return x + 300, y - 380, 2300


# --- 7. a new email arrives; the finger hesitates -----------------------------------------------------

class NewEmail(Scene):
    X, S = 1000, 6.4

    def build(self):
        pen = room(self.W, self.H, night=True)
        top = 1200 - 20 * self.S + 4
        pen.rect(self.X - 150, top - 4, self.X + 900, top + 12 * self.S, INK, radius=20)
        pen.rect(self.X - 144, top, self.X + 894, top + 11 * self.S, (110, 120, 170), radius=18)
        pen.rect(self.X - 150, top + 12 * self.S, self.X + 900, 1200, (80, 64, 70))
        self.top = top
        return pen.result()

    def compose(self, t, world):
        door = _cache.get("ep6_door", self._door)
        reveal = smoothstep((t - self.duration * 0.45) / 3.0)
        paste(world, door, 2150 - door.width / 2, 1200 - door.height, 0.7 * reveal)
        glow = _cache.get("ep6_phone_glow", lambda: art.glow_sprite(150, (190, 225, 255), 150))
        pulse = 0.6 + 0.4 * math.sin(t * 3)
        hx, hy = self.X + 21 * self.S, self.top + 20 * self.S - 46 * self.S
        paste(world, glow, hx - 150, hy - 150, pulse)
        spr = sprite("ep6_sitphone", C.sit_phone, C.MAIN, self.S, 1, tint=NIGHT, blink=C.blink_at(t, offset=0.5))
        place(world, spr, self.X, self.top + 20 * self.S - 4, self.S)
        te = 0.8
        if t > te:
            c = card("อีเมลใหม่ 1 ฉบับ", "แตะเพื่อเปิดอ่าน", (110, 160, 210), 520, 140, icon="@")
            paste_scaled(world, c, hx + 320, hy - 300 + 8 * math.sin(t * 1.5), pop_scale(t - te))

    @staticmethod
    def _door():
        pen = Pen(360, 700)
        pen.rect(0, 0, 360, 700, (255, 236, 190), radius=12)
        pen.rect(30, 30, 330, 700, (255, 248, 226), radius=8)
        img = pen.result()
        return art.add_glow(img.convert("RGB"), 180, 350, 300, (255, 246, 220), 0.6).convert("RGBA")

    def camera(self, t):
        u = self.u(t)
        return lerp(1250, 1350, u), lerp(700, 720, u), lerp(2400, 2000, u)


Calendars.GROUND = 1200

SCENES = {
    "wardrobe": Wardrobe,
    "friends_hired": FriendsHired,
    "email_pile": EmailPile,
    "resume_edit": ResumeEdit,
    "interview_exit": InterviewExit,
    "calendars": Calendars,
    "envelope_stairs": EnvelopeStairs,
    "new_email": NewEmail,
}
