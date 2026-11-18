"""Scene set built from the user's illustrated sticker sheets
(`experiments/character and props/`, cut out by extract_assets.py).

Stickers are static drawings, so motion comes from camera moves, sliding
and hop-walking stickers, pop-ins timed to the narration, glows, parallax
and small particles. Procedural backgrounds use the stickers' palette and
brown outlines so the two blend."""

from __future__ import annotations

import math
import random
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter

import art
from art import Pen, mix, paste, shade, smoothstep
from scenes import Scene, lerp

ASSETS = Path(__file__).resolve().parent / "output" / "assets"
INK = (84, 62, 54)
NIGHT = (0.78, 0.82, 1.0)


# (left, top, right, bottom) trims for cutouts that picked up a neighbor's fragments.
TRIMS = {"city/027": (0, 30, 0, 0)}


@lru_cache(maxsize=None)
def _load(aid: str) -> Image.Image:
    path = ASSETS / f"{aid}.png"
    if not path.exists():
        raise FileNotFoundError(f"missing sticker {aid}; run extract_assets.py first")
    im = Image.open(path).convert("RGBA")
    if aid in TRIMS:
        l, t, r, b = TRIMS[aid]
        im = im.crop((l, t, im.width - r, im.height - b))
    return im


@lru_cache(maxsize=1024)
def sticker(aid, scale=1.0, flip=False, tint=None, rot=0.0, glow=None):
    im = _load(aid)
    if abs(scale - 1.0) > 1e-3:
        im = im.resize((max(1, round(im.width * scale)), max(1, round(im.height * scale))), Image.LANCZOS)
        if scale > 1.05:
            r, g, b, a = im.split()
            rgb = Image.merge("RGB", (r, g, b)).filter(ImageFilter.UnsharpMask(radius=1.3, percent=60, threshold=2))
            im = Image.merge("RGBA", (*rgb.split(), a))
    if tint is not None:
        r, g, b, a = im.split()
        im = Image.merge("RGBA", (r.point(lambda v: int(v * tint[0])), g.point(lambda v: int(v * tint[1])),
                                  b.point(lambda v: int(v * tint[2])), a))
    if glow is not None:
        halo = Image.new("RGBA", im.size, (*glow, 0))
        halo.putalpha(im.getchannel("A").filter(ImageFilter.GaussianBlur(9)).point(lambda v: min(255, v * 2)))
        pad = Image.new("RGBA", (im.width + 40, im.height + 40), (0, 0, 0, 0))
        pad.alpha_composite(halo, (20, 20))
        pad.alpha_composite(im, (20, 20))
        im = pad
    if flip:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    if rot:
        im = im.rotate(rot, resample=Image.BICUBIC, expand=True)
    return im


def put(world, aid, cx, bottom, scale=1.0, alpha=1.0, flip=False, tint=None, rot=0.0, glow=None):
    im = sticker(aid, round(scale, 3), flip, tint, round(rot * 2) / 2, glow)
    paste(world, im, cx - im.width / 2, bottom - im.height, alpha)
    return im


def hop(distance, stride=95.0, height=9.0, rock=2.2):
    """Walking illusion for a static sticker: small hop + rock per step."""
    phase = distance / stride
    return -abs(math.sin(math.pi * phase)) * height, rock * math.sin(math.pi * phase)


def pop(dt, dur=0.45):
    return 0.35 + 0.65 * art.ease_out_back(dt / dur), min(1.0, dt / 0.25)


class StickerScene(Scene):
    W, H = 2112, 1188


# --- shared backgrounds --------------------------------------------------------

def window(pen, x0, y0, x1, y1, sky, sun=None, moon=None, star_seed=None, hills_color=None):
    pen.vgrad_rect(x0, y0, x1, y1, sky)
    if star_seed is not None:
        art.stars(pen, x0 + 10, y0 + 10, x1 - 10, y0 + (y1 - y0) * 0.7, 30, seed=star_seed)
    if sun:
        pen.circle(*sun, (255, 230, 160))
    if moon:
        pen.circle(*moon, (252, 240, 200))
    if hills_color:
        art.hills(pen, x0, x1, y1 - 50, 22, hills_color, period=260, bottom=y1)
    pen.rect(x0, y0, x1, y1, None, outline=INK, width=8)
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    pen.rect(mx - 7, y0, mx + 7, y1, (250, 246, 238), outline=INK, width=3)
    pen.rect(x0, my - 7, x1, my + 7, (250, 246, 238), outline=INK, width=3)
    pen.rect(x0 - 24, y1, x1 + 24, y1 + 26, (238, 226, 206), radius=6, outline=INK, width=4)


def day_sky(W, H, top=(170, 210, 236), bottom=(236, 242, 236)):
    return art.vgradient(W, H, [(0, top), (0.6, bottom), (1, bottom)])


def clouds(pen, spots):
    for cx, cy, s in spots:
        for dx, dy, r in ((-90, 10, 58), (0, -20, 78), (90, 8, 60), (40, 30, 52)):
            pen.circle(cx + dx * s, cy + dy * s, r * s, (255, 255, 255))


# --- 1. morning, opening the phone -------------------------------------------

class MorningSofa(StickerScene):
    def build(self):
        W, H = self.W, self.H
        pen = Pen(W, H, base=art.vgradient(W, H, [(0, (249, 239, 222)), (1, (241, 226, 204))]))
        pen.rect(0, 930, W, H, (220, 188, 150))
        for y in range(965, H, 64):
            pen.rect(0, y, W, y + 4, (204, 170, 132))
        pen.rect(0, 922, W, 936, (236, 218, 194))
        window(pen, 200, 190, 700, 640, [(0, (156, 200, 236)), (0.65, (255, 216, 176)), (1, (255, 190, 154))],
               sun=(450, 560, 78), hills_color=(222, 168, 168))
        for x0 in (120, 700):
            pen.rect(x0, 160, x0 + 110, 760, (232, 168, 148), radius=36, outline=INK, width=4)
        pen.rect(90, 140, 840, 160, (178, 130, 100), radius=8, outline=INK, width=3)
        pen.ellipse(1180, 1050, 520, 70, (230, 200, 166), outline=INK, width=3)
        pen.rect(1820, 760, 1920, 930, (196, 140, 110), radius=12, outline=INK, width=4)
        pen.ellipse(1870, 700, 90, 80, (120, 170, 120), outline=INK, width=4)
        pen.ellipse(1840, 650, 60, 60, (140, 186, 132), outline=INK, width=4)
        img = pen.result()
        img = art.overlay_alpha(img, lambda d: d.polygon([(260, 640), (700, 640), (1250, 1188), (420, 1188)],
                                                       fill=(255, 238, 200, 60)), 1.0)
        return art.add_glow(img, 450, 560, 220, (255, 230, 180), 0.5)

    def compose(self, t, world):
        rnd = random.Random(7)
        d = ImageDraw.Draw(world)
        for i in range(16):
            x0, y0, sp = rnd.uniform(320, 1150), rnd.uniform(680, 1150), rnd.uniform(8, 18)
            x = x0 + 26 * math.sin(t * 0.4 + i)
            y = y0 - (t * sp) % 240
            d.ellipse((x - 3, y - 3, x + 3, y + 3), fill=(255, 244, 214))
        s = 1.6
        put(world, "compare/011", 1220, 1020 + 1.5 * math.sin(t * 1.6), s)
        glow = art_glow(110, (190, 225, 255), 60 + 20 * math.sin(t * 3))
        paste(world, glow, 1220 - 382 * s / 2 + 215 * s - 110, 1020 - 305 * s + 160 * s - 110)

    def camera(self, t):
        u = self.u(t)
        return lerp(1056, 1200, u), lerp(594, 680, u), lerp(2112, 1700, u)


@lru_cache(maxsize=64)
def _glow(radius, color, alpha):
    return art.glow_sprite(radius, color, alpha)


def art_glow(radius, color, alpha):
    return _glow(radius, color, int(alpha) // 10 * 10)


# --- 2. everyone else moving ahead --------------------------------------------

class OthersAhead(StickerScene):
    W = 3000
    WALKERS = [("components/003", 0, 330, 1.15), ("components/006", -420, 300, 1.12),
               ("components/007", -900, 250, 1.12), ("components/014", -1350, 230, 1.1),
               ("components/015", -1800, 240, 1.1), ("components/003", -2300, 320, 1.15)]

    def build(self):
        W, H = self.W, self.H
        pen = Pen(W, H, base=day_sky(W, H))
        clouds(pen, ((400, 200, 1.0), (1300, 150, 1.2), (2300, 230, 1.05)))
        art.hills(pen, 0, W, 760, 60, (196, 220, 214), period=1100)
        art.hills(pen, 0, W, 850, 45, (164, 204, 170), period=800, phase=2)
        pen.rect(0, 880, W, H, (160, 202, 150))
        pen.rect(0, 960, W, 1110, (232, 214, 176), outline=INK, width=4)
        for x in range(0, W, 180):
            pen.ellipse(x + 40, 1040, 10, 5, (210, 190, 152))
        return pen.result()

    def compose(self, t, world):
        put(world, "compare/002", 640, 1000, 1.3)
        for aid, x0, speed, s in self.WALKERS:
            x = x0 + speed * max(t, -0.5)
            if -300 < x < self.W + 300:
                dy, rot = hop(x - x0, stride=120, height=12)
                put(world, aid, x, 1100 + dy, s, rot=rot)

    def camera(self, t):
        u = self.u(t)
        return lerp(1056, 1200, u), 594, 2112


# --- 3. other people's success popping into the feed --------------------------

class FeedPosts(StickerScene):
    PHONE = (1030, 70, 1790, 1130)
    POSTS = [("trophy", "office/018"), ("house", "compare/034"), ("car", "compare/035"),
             ("briefcase", "office/019"), ("life", "compare/015")]
    SLOTS = [(0, 0), (1, 0), (0, 1), (1, 1), (0.5, 2)]

    def build(self):
        W, H = self.W, self.H
        img = art.vgradient(W, H, [(0, (124, 116, 172)), (0.55, (198, 164, 192)), (1, (244, 204, 190))])
        rnd = random.Random(11)

        def bokeh(d):
            for _ in range(24):
                x, y, r = rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(30, 110)
                d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 240, 230, rnd.randint(18, 46)))
        img = art.overlay_alpha(img, bokeh, 1.0)
        pen = Pen(W, H, base=img)
        x0, y0, x1, y1 = self.PHONE
        pen.rect(x0, y0, x1, y1, (46, 44, 60), radius=70, outline=INK, width=6)
        pen.rect(x0 + 28, y0 + 70, x1 - 28, y1 - 60, (250, 248, 244), radius=34)
        pen.rect((x0 + x1) / 2 - 70, y0 + 28, (x0 + x1) / 2 + 70, y0 + 44, (80, 78, 96), radius=8)
        return pen.result()

    @staticmethod
    @lru_cache(maxsize=16)
    def card(aid):
        w, h = 330, 300
        pen = Pen(w, h)
        pen.rect(6, 10, w - 2, h - 2, (0, 0, 0, 40), radius=24)
        pen.rect(0, 0, w - 8, h - 12, (255, 255, 255), radius=24, outline=(220, 214, 210), width=2)
        pen.circle(30, 28, 13, (210, 200, 230))
        pen.rect(52, 20, 150, 32, (225, 222, 228), radius=6)
        pen.circle(w - 40, h - 40, 11, (240, 120, 130))
        pen.rect(24, h - 46, 140, h - 36, (232, 228, 232), radius=5)
        card = pen.result()
        im = _load(aid)
        scale = min((w - 50) / im.width, (h - 110) / im.height)
        s = sticker(aid, round(scale, 3))
        card.alpha_composite(s, (int((w - 8 - s.width) / 2), int(48 + (h - 110 - s.height) / 2)))
        return card

    def compose(self, t, world):
        put(world, "compare/011", 520, 1040 + 1.5 * math.sin(t * 1.5), 1.3)
        x0, y0, x1, y1 = self.PHONE
        for (event, aid), (col, row) in zip(self.POSTS, self.SLOTS):
            te = self.ev.get(event)
            if te is None or t < te:
                continue
            scale, alpha = pop(t - te)
            card = self.card(aid)
            if abs(scale - 1) > 0.01:
                card = card.resize((max(4, int(card.width * scale)), max(4, int(card.height * scale))), Image.BILINEAR)
            cx = x0 + 60 + 165 + col * 345
            cy = y0 + 232 + row * 300
            paste(world, card, cx - card.width / 2, cy - card.height / 2, alpha)

    def camera(self, t):
        u = self.u(t)
        return lerp(1056, 1120, u), 594, lerp(2112, 1960, u)


# --- 4. lagging behind the others --------------------------------------------

class BehindOthers(StickerScene):
    W = 2600
    TRACK_X, TRACK_BOTTOM, SCALE = 1300, 1060, 1.85

    def build(self):
        W, H = self.W, self.H
        pen = Pen(W, H, base=day_sky(W, H, top=(176, 214, 238)))
        clouds(pen, ((500, 180, 0.9), (1600, 140, 1.1), (2300, 210, 0.9)))
        for x in range(60, W, 260):
            art.tree(pen, x, 640, h=220, leaf=(124, 176, 128))
        pen.rect(0, 600, W, H, (160, 200, 148))
        im = _load("compare/009")
        s = self.SCALE
        top = self.TRACK_BOTTOM - im.height * s

        def band(y0, y1, color):
            pen.rect(0, top + y0 * s, W, top + y1 * s, color)
        band(127, 144, (146, 171, 116))
        band(144, 147, (70, 40, 22))
        band(147, 287, (192, 102, 84))
        band(169, 172, (255, 244, 234))
        band(209, 212, (255, 244, 234))
        return pen.result()

    def compose(self, t, world):
        im = _feathered("compare/009", self.SCALE)
        x = self.TRACK_X - im.width / 2 + 25 * t
        paste(world, im, x, self.TRACK_BOTTOM - im.height)
        rnd = random.Random(3)
        d = ImageDraw.Draw(world)
        for i in range(6):
            y = self.TRACK_BOTTOM - im.height * 0.62 + i * 26
            x0 = x + 120 - ((t * 420 + rnd.uniform(0, 300)) % 300)
            d.line((x0 - 90, y, x0, y), fill=(250, 250, 250), width=4)

    def camera(self, t):
        u = self.u(t)
        return lerp(950, 1650, u), lerp(620, 600, u), 2112


@lru_cache(maxsize=4)
def _feathered(aid, scale, width=70):
    """Fade a sticker's left/right edges so it melts into the extended track."""
    out = sticker(aid, scale).copy()
    alpha = out.getchannel("A")
    ramp = Image.linear_gradient("L").rotate(90, expand=True).resize((width, out.height))
    mask = Image.new("L", out.size, 255)
    mask.paste(ramp, (0, 0))
    mask.paste(ramp.transpose(Image.FLIP_LEFT_RIGHT), (out.width - width, 0))
    out.putalpha(ImageChops.multiply(alpha, mask))
    return out


# --- 5. silent questions at night ---------------------------------------------

class NightQuestion(StickerScene):
    def build(self):
        W, H = self.W, self.H
        pen = Pen(W, H, base=art.vgradient(W, H, [(0, (52, 60, 102)), (1, (38, 44, 80))]))
        pen.rect(0, 960, W, H, (40, 40, 68))
        pen.rect(0, 952, W, 966, (60, 62, 96))
        window(pen, 220, 170, 720, 620, [(0, (20, 28, 66)), (1, (54, 64, 114))], moon=(570, 290, 46),
               star_seed=5, hills_color=(32, 38, 72))
        img = pen.result()
        return art.add_glow(img, 570, 290, 140, (240, 236, 210), 0.4)

    def compose(self, t, world):
        s = 1.55
        im = _load("compare/004")
        cx, bottom = 1120, 1010
        glow = art_glow(260, (170, 210, 255), 110 + 20 * math.sin(t * 2.3))
        paste(world, glow, cx + im.width * s * 0.3 - 260, bottom - im.height * s * 0.55 - 260)
        put(world, "compare/004", cx, bottom, s, tint=NIGHT)
        for key, x, y, sc in (("q1", 820, 470, 1.9), ("q2", 930, 380, 1.4)):
            te = self.ev.get(key)
            if te is not None and t >= te:
                scale, alpha = pop(t - te)
                put(world, "office/028", x, y - 30 * smoothstep((t - te) / 4), sc * scale, alpha=alpha)

    def camera(self, t):
        u = self.u(t)
        return lerp(1056, 1060, u), lerp(594, 640, u), lerp(2112, 1760, u)


# --- 6. the gap between who we are and who we think we should be -------------

class GapIdeal(StickerScene):
    def build(self):
        W, H = self.W, self.H
        pen = Pen(W, H, base=art.vgradient(W, H, [(0, (50, 46, 98)), (0.55, (118, 94, 160)), (1, (228, 168, 180))]))
        art.stars(pen, 0, 0, W, 600, 60, seed=21)
        pen.ellipse(560, 960, 330, 70, (96, 86, 134))
        pen.rect(250, 900, 870, 960, (126, 114, 162), radius=36, outline=(80, 70, 116), width=4)
        pen.ellipse(1600, 640, 300, 64, (110, 98, 150))
        pen.rect(1320, 580, 1880, 636, (142, 128, 178), radius=34, outline=(90, 80, 126), width=4)
        for i in range(9):
            x = lerp(900, 1300, i / 8)
            y = lerp(890, 600, i / 8) - 110 * math.sin(math.pi * i / 8)
            pen.circle(x, y, 7, (230, 214, 240))
        return art.add_glow(pen.result(), 1600, 480, 280, (255, 230, 190), 0.25)

    def compose(self, t, world):
        rnd = random.Random(4)
        d = ImageDraw.Draw(world)
        for i in range(22):
            x = rnd.uniform(0, self.W) + 18 * math.sin(t * 0.5 + i)
            y = (rnd.uniform(0, self.H) - t * rnd.uniform(10, 28)) % self.H
            d.ellipse((x - 2.5, y - 2.5, x + 2.5, y + 2.5), fill=(250, 236, 250))
        put(world, "compare/004", 560, 905, 1.25, tint=(0.88, 0.86, 1.0))
        te = self.ev.get("ideal")
        if te is not None and t >= te:
            put(world, "compare/012", 1600, 595 + 6 * math.sin(t * 1.4), 1.3,
                alpha=min(0.92, (t - te) / 1.2), glow=(255, 226, 170))

    def camera(self, t):
        reveal = self.ev.get("ideal", self.duration) + 0.8
        u = self.u(t, end=reveal)
        return lerp(640, 1056, u), lerp(760, 594, u), lerp(1500, 2112, u)


# --- 7. everyone's path is shaped differently ---------------------------------

class OwnPaths(StickerScene):
    START_X = 330
    # (base y, width, end x, wave amp, wave period, goal sticker, goal scale, walker, walker speed)
    PATHS = [(700, 30, 1760, 30, 120, "pace/014", 0.75, "components/015", 120),
             (820, 40, 1180, 0, 1, "compare/033", 0.8, "components/013", 80),
             (950, 50, 1900, 64, 280, "compare/034", 0.75, "components/012", 150),
             (1090, 60, 1520, 14, 480, "pace/043", 0.85, "components/014", 100)]

    @staticmethod
    def path_y(y0, x0, amp, period, x):
        return y0 + amp * math.sin((x - x0) / period)

    def build(self):
        W, H = self.W, self.H
        pen = Pen(W, H, base=day_sky(W, H, top=(172, 214, 240), bottom=(244, 240, 222)))
        clouds(pen, ((400, 150, 0.8), (1500, 120, 1.0)))
        art.hills(pen, 0, W, 560, 50, (188, 214, 190), period=1000)
        pen.rect(0, 600, W, H, (162, 204, 160))
        for y0, w, x1, amp, period, *_ in self.PATHS:
            pts = [(x, self.path_y(y0, self.START_X, amp, period, x)) for x in range(self.START_X, int(x1) + 1, 20)]
            pen.line(pts, INK, w + 8)
            pen.line(pts, (232, 214, 174), w)
        pen.rect(self.START_X - 6, 640, self.START_X + 6, 1140, (250, 250, 246), radius=4, outline=INK, width=2)
        return pen.result()

    def compose(self, t, world):
        for y0, w, x1, amp, period, goal, gs, walker, speed in self.PATHS:
            put(world, goal, x1 + 20, self.path_y(y0, self.START_X, amp, period, x1) + 10, gs)
        for y0, w, x1, amp, period, goal, gs, walker, speed in self.PATHS:
            x = min(x1 - 120, self.START_X + 60 + speed * max(0.0, t))
            moving = x < x1 - 120
            dy, rot = hop(x, stride=90, height=8) if moving else (0, 0)
            put(world, walker, x, self.path_y(y0, self.START_X, amp, period, x) + 14 + dy, 0.62, rot=rot)
        te = self.ev.get("ruler")
        if te is not None and t >= te:
            dt = t - te
            ruler = _ruler()
            x = lerp(-1300, self.START_X, art.ease_out_back(dt / 0.9))
            alpha = 1.0 if dt < 2.2 else max(0.0, 1 - (dt - 2.2) / 0.8)
            paste(world, ruler, x, 420, alpha)

    def camera(self, t):
        u = self.u(t)
        return lerp(1056, 1080, u), lerp(620, 640, u), lerp(2112, 1980, u)


@lru_cache(maxsize=1)
def _ruler(length=1300, height=100):
    pen = Pen(length, height)
    pen.rect(2, 2, length - 2, height - 2, (248, 214, 110), radius=12, outline=INK, width=4)
    for i, x in enumerate(range(30, length - 20, 30)):
        pen.rect(x - 2, 4, x + 2, 46 if i % 5 == 0 else 24, (150, 115, 60))
    return pen.result()


# --- 8. exploring, then resting ------------------------------------------------

class ExploreRest(StickerScene):
    W = 3000

    def build(self):
        W, H = self.W, self.H
        pen = Pen(W, H, base=day_sky(W, H, top=(186, 218, 236), bottom=(252, 236, 204)))
        clouds(pen, ((500, 170, 0.9), (1700, 130, 1.1), (2600, 200, 0.9)))
        art.hills(pen, 0, W, 760, 50, (196, 214, 176), period=1200)
        pen.rect(0, 830, W, H, (166, 206, 150))
        art.hills(pen, 0, W, 850, 20, (166, 206, 150), period=500)
        rnd = random.Random(2)
        for _ in range(26):
            x, y = rnd.uniform(100, 2900), rnd.uniform(1060, 1170)
            art.flower(pen, x, y, rnd.uniform(9, 13), petal=rnd.choice([(250, 190, 200), (250, 226, 150), (200, 190, 250)]))
        return art.add_glow(pen.result(), 300, 160, 300, (255, 240, 200), 0.5)

    def compose(self, t, world):
        put(world, "pace/018", 850, 1060, 1.35)
        put(world, "pace/002", 2200, 1080, 1.4)
        for i, (x0, y0, sp) in enumerate(((600, 520, 160), (1600, 420, 140))):
            x = (x0 + sp * t) % (self.W + 200) - 100
            y = y0 + 40 * math.sin(t * 2.2 + i)
            put(world, "components/043", x, y, 0.9, rot=8 * math.sin(t * 4 + i))
        sx = 300 + 18 * (t + 2)
        put(world, "pace/034", sx, 1180, 1.0)

    def camera(self, t):
        rest = self.ev.get("rest", self.duration * 0.4)
        shift = smoothstep((t - rest + 0.3) / 2.2)
        return lerp(lerp(900, 1050, smoothstep(t / max(0.1, rest))), 2050, shift), 640, lerp(1900, 1980, shift)


# --- 9. a highway for some, a careful dirt path for others --------------------

class HighwayDirt(StickerScene):
    H = 1850
    CARS = [("compare/035", 1150, 0, 640, False), ("components/033", 1300, 900, 640, False),
            ("components/045", 900, 1500, 640, False), ("compare/035", 1200, 400, 520, True),
            ("components/033", 1050, 1300, 520, True)]

    def build(self):
        W, H = self.W, self.H
        pen = Pen(W, H, base=art.vgradient(W, H, [(0, (166, 206, 236)), (0.22, (226, 238, 242)),
                                                   (0.45, (152, 198, 142)), (1, (128, 176, 122))]))
        art.city_skyline(pen, 0, W, 470, (184, 198, 216), window=(208, 220, 232), lit=0.4, max_h=230, seed=4)
        pen.rect(0, 470, W, 960, (142, 190, 130))
        pen.rect(0, 500, W, 700, (92, 96, 112), outline=INK, width=5)
        for x in range(0, W, 200):
            pen.rect(x, 594, x + 110, 606, (250, 250, 250))
        for x in range(0, W, 90):
            pen.rect(x, 716, x + 10, 760, (184, 188, 200))
        pen.rect(0, 712, W, 724, (204, 208, 218))
        art.hills(pen, 0, W, 960, 26, (114, 162, 110), period=700)
        pen.rect(0, 990, W, H, (140, 186, 128))
        rnd = random.Random(9)
        path = [(x, 1600 + 46 * math.sin(x / 420)) for x in range(-50, W + 100, 50)]
        pen.line(path, INK, 128)
        pen.line(path, (214, 190, 150), 120)
        for _ in range(60):
            x = rnd.uniform(0, W)
            y = 1600 + 46 * math.sin(x / 420) + rnd.uniform(-45, 45)
            pen.ellipse(x, y, rnd.uniform(6, 15), rnd.uniform(4, 8), (150, 136, 120))
        for _ in range(36):
            x, y = rnd.uniform(0, W), rnd.uniform(1050, 1830)
            if abs(y - 1600 - 46 * math.sin(x / 420)) > 90:
                for dx in (-8, 0, 8):
                    pen.line([(x + dx, y), (x + dx * 1.8, y - 28)], (100, 150, 96), 5)
        return pen.result()

    def compose(self, t, world):
        span = self.W + 700
        for aid, speed, offset, y, leftward in self.CARS:
            if leftward:
                x = self.W + 350 - (offset + speed * t) % span
            else:
                x = (offset + speed * t) % span - 350
            put(world, aid, x, y + 2 * math.sin(t * 20 + offset), 1.0, flip=leftward)
        x = 700 + 42 * t
        dy, rot = hop(x, stride=70, height=5, rock=1.5)
        put(world, "pace/001", x, 1600 + 46 * math.sin(x / 420) + 30 + dy, 1.0, rot=rot)
        put(world, "pace/034", 1500 + 10 * t, 1600 + 46 * math.sin(1500 / 420) + 40, 0.9)

    def camera(self, t):
        td = self.ev.get("dirt", self.duration * 0.5)
        tilt = smoothstep((t - td + 0.2) / 1.8)
        x = 700 + 42 * t
        return lerp(1056, x + 280, tilt), lerp(590, 1270, tilt), 2112


# --- 10. distant footsteps, then the silent room -------------------------------

class NightRoom(StickerScene):
    def build(self):
        W, H = self.W, self.H
        pen = Pen(W, H, base=art.vgradient(W, H, [(0, (22, 26, 54)), (1, (40, 44, 82))]))
        art.stars(pen, 0, 0, W, H, 140, seed=12)
        return pen.result()

    def compose(self, t, world):
        tr = self.ev.get("room", self.duration * 0.5)
        mix_ = smoothstep((t - tr + 0.4) / 0.9)
        if mix_ < 1:
            put(world, "city/027", 1056, 990 + 6 * math.sin(t), 2.3, alpha=1 - mix_)
        if mix_ > 0:
            s, bottom = 2.05, 1010 + 4 * math.sin(t * 0.8)
            put(world, "compare/001", 1056, bottom, s, alpha=mix_)
            glow = art_glow(140, (170, 210, 255), 70 + 20 * math.sin(t * 2.5))
            paste(world, glow, 1056 - 487 * s / 2 + 205 * s - 140, bottom - 405 * s + 150 * s - 140, mix_)

    def camera(self, t):
        u = self.u(t)
        return 1056, lerp(594, 600, u), lerp(2112, 1880, u)


# --- 11. walking on at our own pace -------------------------------------------

class OwnPace(StickerScene):
    W = 3600
    X0, SIGN_X, GROUND = 700, 2700, 1060

    def build(self):
        W, H = self.W, self.H
        pen = Pen(W, H, base=art.vgradient(W, H, [(0, (24, 30, 70)), (0.55, (72, 72, 134)), (0.82, (226, 162, 150)), (1, (226, 162, 150))]))
        art.stars(pen, 0, 0, W, 600, 150, seed=31)
        pen.circle(480, 230, 62, (250, 242, 214))
        art.hills(pen, 0, W, 820, 60, (60, 60, 108), period=1300)
        art.hills(pen, 0, W, 900, 44, (44, 46, 88), period=900, phase=2.2)
        pen.rect(0, 940, W, H, (40, 42, 80))
        pen.rect(0, 990, W, 1100, (72, 74, 114), outline=(30, 30, 60), width=4)
        for x in range(0, W, 220):
            pen.rect(x, 1040, x + 110, 1048, (150, 150, 180))
        img = art.add_glow(pen.result(), 480, 230, 190, (240, 236, 210), 0.45)
        return art.add_glow(img, 3200, 900, 650, (255, 196, 160), 0.35)

    def main_x(self, t):
        arrive = self.ev.get("sign", self.duration * 0.7)
        return lerp(self.X0, self.SIGN_X - 170, min(1.0, max(0.0, t) / arrive))

    def compose(self, t, world):
        put(world, "compare/036", self.SIGN_X + 40, 1000, 1.7, tint=NIGHT)
        x = self.main_x(t)
        arrive = self.ev.get("sign", self.duration * 0.7)
        dy, rot = hop(x, stride=95, height=9) if t < arrive else (0, 0)
        put(world, "city/003", x, self.GROUND + dy, 1.15, tint=NIGHT, rot=rot)

    def camera(self, t):
        arrive = self.ev.get("sign", self.duration * 0.7)
        after = smoothstep((t - arrive) / 4)
        return self.main_x(t) + 260, lerp(600, 610, after), lerp(2112, 1800, after)


SCENES = {
    "morning_phone": MorningSofa,
    "others_running": OthersAhead,
    "feed_success": FeedPosts,
    "walking_behind": BehindOthers,
    "night_desk": NightQuestion,
    "gap_ideal": GapIdeal,
    "different_paths": OwnPaths,
    "explore_rest": ExploreRest,
    "highway_dirt": HighwayDirt,
    "night_window": NightRoom,
    "own_pace": OwnPace,
}
