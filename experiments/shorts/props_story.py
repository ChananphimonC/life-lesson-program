"""Props for the "pregnancy cravings" story: detailed food and object sprites (durian, hotpot, liver, fruit salad, iced
coffee, old book, carrot, baby, ultrasound...), a staggered card grid, an evidence meter and a rubber stamp.
Drawn at 3x then reduced for smooth edges; Thai labels avoid tone marks over upper vowels (the font cannot stack them).
"""

from __future__ import annotations

import math
from functools import lru_cache

from PIL import Image, ImageDraw

from subtitles import font

INK = (118, 88, 72)
KINDS = {"card_grid", "evidence", "stamp"}
SPRITES = {"durian", "shabu", "liver", "salad", "oliang", "manuscript", "carrot", "baby", "scan", "honey", "lime", "fish",
           "fruit", "soil", "chili", "candy", "chips", "cake"}


def _mix(a, b, t):
    return tuple(int(x + (y - x) * t) for x, y in zip(a, b))


@lru_cache(maxsize=None)
def sprite(kind: str, H: int) -> Image.Image:
    s = int(H * 0.17)
    k = 3
    big = Image.new("RGBA", (s * k, s * k), (0, 0, 0, 0))
    d = ImageDraw.Draw(big)
    u = s * k / 100.0
    w_line = max(2, int(1.3 * u))

    def P(*pts):
        return [(x * u, y * u) for x, y in pts]

    def ell(x0, y0, x1, y1, fill, outline=True):
        d.ellipse((x0 * u, y0 * u, x1 * u, y1 * u), fill=fill, outline=INK if outline else None, width=w_line)

    def rr(x0, y0, x1, y1, r, fill, outline=True):
        d.rounded_rectangle((x0 * u, y0 * u, x1 * u, y1 * u), r * u, fill=fill, outline=INK if outline else None, width=w_line)

    def poly(pts, fill, outline=True):
        d.polygon(P(*pts), fill=fill)
        if outline:
            d.line(P(*pts, pts[0]), fill=INK, width=w_line, joint="curve")

    def ln(pts, col, wd=2.0):
        d.line(P(*pts), fill=col, width=max(2, int(wd * u / 2)), joint="curve")

    if kind == "durian":                       # a husk with thorns, opened to show golden pods
        for a in range(0, 360, 18):
            r = math.radians(a)
            cx, cy = 50 + 38 * math.cos(r), 54 + 32 * math.sin(r)
            poly([(cx + 7 * math.cos(r + 1.6), cy + 7 * math.sin(r + 1.6)), (cx + 14 * math.cos(r), cy + 14 * math.sin(r)),
                  (cx + 7 * math.cos(r - 1.6), cy + 7 * math.sin(r - 1.6))], (150, 128, 52))
        ell(12, 22, 88, 86, (188, 180, 78))
        ell(24, 32, 76, 74, (252, 238, 196))
        for x, y in ((38, 50), (56, 46), (48, 62)):
            ell(x - 11, y - 9, x + 11, y + 9, (246, 200, 84))
            ell(x - 3, y - 2, x + 3, y + 3, (150, 96, 50), False)
    elif kind == "shabu":                      # a split hotpot seen from above with steam
        ell(8, 34, 92, 92, (150, 154, 164))
        ell(14, 40, 86, 86, (252, 252, 250))
        d.pieslice((16 * u, 42 * u, 84 * u, 84 * u), 90, 270, fill=(236, 110, 70))
        d.pieslice((16 * u, 42 * u, 84 * u, 84 * u), 270, 450, fill=(250, 226, 150))
        ln([(50, 42), (50, 84)], INK, 2)
        for x, y, col in ((30, 56, (112, 176, 96)), (36, 70, (250, 230, 230)), (64, 58, (240, 180, 170)), (68, 72, (112, 176, 96))):
            ell(x - 7, y - 5, x + 7, y + 5, col)
        for x in (36, 52, 66):
            ln([(x, 28), (x - 4, 18), (x + 2, 8)], (230, 232, 238), 2.4)
    elif kind == "liver":                      # blanched liver slices on a plate with a lime wedge
        ell(6, 40, 94, 92, (252, 252, 252))
        ell(14, 46, 86, 84, (244, 244, 246))
        for x, y, rx in ((34, 62, 17), (58, 58, 16), (46, 74, 18), (70, 72, 12)):
            ell(x - rx, y - 8, x + rx, y + 8, (112, 52, 52))
            ln([(x - rx * 0.5, y - 3), (x + rx * 0.3, y - 4)], (190, 110, 100), 2)
        d.pieslice((70 * u, 30 * u, 96 * u, 56 * u), 180, 360, fill=(150, 200, 90), outline=INK, width=w_line)
    elif kind == "salad":                      # fruit salad in a bowl: green mango, apple, chilli flakes, peanuts
        d.pieslice((8 * u, 8 * u, 92 * u, 94 * u), 0, 180, fill=(252, 244, 226), outline=INK, width=w_line)
        for x, y, col in ((26, 52, (170, 210, 96)), (40, 44, (236, 98, 84)), (54, 50, (170, 210, 96)), (66, 44, (250, 224, 120)),
                          (34, 62, (250, 224, 120)), (60, 62, (236, 98, 84)), (48, 58, (170, 210, 96))):
            rr(x - 9, y - 5, x + 9, y + 5, 3, col)
        for x, y in ((30, 48), (50, 42), (70, 54), (44, 66)):
            ell(x - 2, y - 2, x + 2, y + 2, (214, 60, 50), False)
        for x, y in ((36, 56), (62, 52), (54, 66)):
            ell(x - 3, y - 3, x + 3, y + 3, (216, 170, 110), False)
    elif kind == "oliang":                     # tall glass of black iced coffee
        poly([(28, 14), (72, 14), (66, 94), (34, 94)], (226, 236, 244))
        poly([(30, 36), (70, 36), (66, 94), (34, 94)], (84, 52, 38))
        for x, y in ((40, 50), (56, 58), (46, 74)):
            rr(x - 7, y - 7, x + 7, y + 7, 2, (226, 238, 246))
        ln([(52, 14), (62, -6)], (214, 70, 70), 4.4)
        ln([(55, 4), (59, -2)], (255, 255, 255), 2.4)
    elif kind == "manuscript":                 # an old bound text with a ribbon
        poly([(6, 22), (50, 30), (50, 90), (6, 82)], (234, 212, 160))
        poly([(94, 22), (50, 30), (50, 90), (94, 82)], (244, 224, 176))
        poly([(2, 18), (6, 22), (6, 82), (2, 78)], (130, 80, 56))
        for i in range(6):
            ln([(12, 38 + i * 8), (44, 42 + i * 8)], (140, 100, 70), 1.8)
            ln([(56, 42 + i * 8), (88, 38 + i * 8)], (140, 100, 70), 1.8)
        ln([(50, 30), (50, 90)], (170, 130, 90), 2.4)
        poly([(48, 90), (54, 90), (54, 102), (51, 98), (48, 102)], (210, 70, 70))
    elif kind == "carrot":
        poly([(30, 36), (70, 36), (56, 96), (44, 96)], (240, 140, 50))
        for y in (48, 60, 72):
            ln([(36 + (y - 48) * 0.35, y), (62 - (y - 48) * 0.35, y)], (206, 108, 36), 2)
        for dx, a in ((-14, -20), (0, 0), (14, 20)):
            poly([(50 + dx * 0.3, 38), (50 + dx - 5, 12), (50 + dx + 2, 4), (50 + dx + 8, 14)], (96, 170, 84))
    elif kind == "baby":                       # a baby's face with a hair curl, blush and a bib
        ell(18, 20, 82, 84, (252, 224, 200))
        for x in (38, 62):
            ell(x - 5, 46, x + 5, 60, (86, 60, 52), False)
            ell(x - 1, 48, x + 3, 52, (255, 255, 255), False)
        ln([(42, 70), (50, 74), (58, 70)], (176, 80, 80), 2.4)
        ell(26, 60, 38, 68, (248, 170, 160), False)
        ell(62, 60, 74, 68, (248, 170, 160), False)
        ln([(46, 22), (50, 10), (58, 14), (54, 22)], (150, 106, 76), 2.4)
        poly([(26, 84), (74, 84), (66, 100), (34, 100)], (150, 200, 240))
    elif kind == "scan":                       # an ultrasound screen with a little curled shape
        rr(6, 14, 94, 86, 8, (50, 54, 64))
        d.pieslice((16 * u, 10 * u, 84 * u, 120 * u), 220, 320, fill=(120, 128, 140))
        ell(38, 38, 62, 62, (206, 210, 218), False)
        ell(46, 30, 58, 42, (206, 210, 218), False)
        ln([(40, 60), (34, 70), (42, 74)], (206, 210, 218), 3)
        rr(70, 70, 88, 80, 3, (110, 220, 160), False)
    elif kind == "honey":
        rr(22, 36, 78, 94, 12, (236, 164, 40))
        rr(26, 22, 74, 38, 4, (250, 230, 170))
        rr(34, 52, 66, 76, 4, (252, 246, 226))
        ln([(40, 62), (60, 62)], (206, 140, 40), 2)
        ln([(40, 68), (56, 68)], (206, 140, 40), 2)
    elif kind == "lime":
        ell(14, 24, 86, 90, (150, 200, 80))
        ell(22, 32, 78, 82, (214, 236, 150))
        for a in range(0, 360, 45):
            r = math.radians(a)
            ln([(50, 57), (50 + 25 * math.cos(r), 57 + 25 * math.sin(r))], (250, 252, 230), 2.0)
    elif kind == "fish":
        poly([(14, 54), (60, 28), (84, 54), (60, 80)], (110, 168, 210))
        poly([(84, 54), (98, 38), (98, 70)], (84, 132, 176))
        ell(24, 46, 34, 56, (255, 255, 255))
        ell(27, 49, 32, 54, INK, False)
        ln([(40, 40), (46, 54), (40, 68)], (80, 128, 176), 2)
        ln([(52, 36), (58, 54), (52, 72)], (80, 128, 176), 2)
    elif kind == "fruit":                      # mango and apple
        ell(8, 38, 58, 90, (250, 190, 70))
        ln([(20, 52), (30, 48)], (255, 236, 160), 2.4)
        ell(44, 30, 92, 84, (226, 70, 70))
        ln([(68, 30), (70, 18)], (110, 80, 50), 2.4)
        poly([(70, 24), (84, 14), (82, 28)], (110, 176, 90))
    elif kind == "soil":
        poly([(10, 86), (22, 52), (40, 42), (60, 40), (80, 52), (92, 86)], (140, 96, 64))
        for x, y in ((30, 70), (46, 58), (62, 72), (72, 62), (52, 82), (24, 80)):
            ell(x - 3, y - 2, x + 3, y + 2, (104, 70, 46), False)
    elif kind == "chili":
        for ox, oy, col in ((0, 0, (216, 56, 46)), (14, 10, (230, 80, 56))):
            poly([(24 + ox, 30 + oy), (36 + ox, 26 + oy), (74 + ox, 72 + oy), (66 + ox, 80 + oy)], col)
            poly([(24 + ox, 30 + oy), (36 + ox, 26 + oy), (36 + ox, 16 + oy), (28 + ox, 18 + oy)], (96, 160, 80))
    elif kind == "candy":
        ell(30, 32, 70, 68, (244, 120, 150))
        ln([(36, 40), (62, 60)], (255, 240, 244), 3)
        ln([(34, 56), (56, 36)], (255, 240, 244), 3)
        poly([(30, 50), (6, 38), (6, 62)], (250, 190, 210))
        poly([(70, 50), (94, 38), (94, 62)], (250, 190, 210))
    elif kind == "chips":
        poly([(24, 20), (76, 20), (82, 92), (18, 92)], (250, 204, 70))
        ell(34, 42, 66, 70, (252, 232, 150))
        ln([(30, 24), (36, 18), (42, 24), (48, 18), (54, 24), (60, 18), (66, 24), (72, 18)], INK, 1.8)
    elif kind == "cake":
        rr(14, 52, 86, 92, 6, (250, 214, 226))
        rr(14, 40, 86, 58, 6, (250, 244, 232))
        ell(42, 24, 58, 42, (226, 70, 80))
        ln([(50, 24), (54, 14)], (110, 160, 80), 2.4)
    return big.resize((s, s), Image.LANCZOS)


def _env(t, at, dur, fade=0.25):
    lt = t - at
    if lt < 0 or lt > dur:
        return 0.0, 0.0
    a = min(1.0, lt / fade, (dur - lt) / fade)
    x = min(1.0, lt / 0.35)
    sc = 1 + 2.70158 * (x - 1) ** 3 + 1.70158 * (x - 1) ** 2
    return max(0.0, a), sc


def _paste(img, spr, cx, cy, alpha=1.0, scale=1.0, angle=0.0):
    if alpha <= 0 or scale <= 0.02:
        return
    if abs(angle) > 0.05:
        spr = spr.rotate(angle, resample=Image.BICUBIC, expand=True)
    if abs(scale - 1) > 0.01:
        spr = spr.resize((max(1, int(spr.width * scale)), max(1, int(spr.height * scale))), Image.LANCZOS)
    if alpha < 1:
        spr = spr.copy()
        spr.putalpha(spr.getchannel("A").point(lambda v: int(v * alpha)))
    img.paste(spr, (int(cx - spr.width / 2), int(cy - spr.height / 2)), spr)


@lru_cache(maxsize=None)
def card_sprite(icon: str, label: str, sub: str, accent: tuple, H: int) -> Image.Image:
    ic = sprite(icon, H)
    w, h = int(H * 0.30), int(H * 0.34)
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((3, 3, w - 3, h - 3), int(h * 0.1), fill=(255, 252, 244), outline=INK, width=4)
    d.rounded_rectangle((3, 3, w - 3, int(h * 0.12)), int(h * 0.1), fill=accent)
    img.paste(ic, (int((w - ic.width) / 2), int(h * 0.12)), ic)
    f = font(int(h * 0.11))
    size = int(h * 0.11)
    while size > 14 and font(size).getlength(label) > w * 0.9:
        size -= 2
    d.text((w / 2, h * 0.74), label, font=font(size), fill=(70, 54, 50), anchor="mm")
    if sub:
        sf = font(int(h * 0.075), False)
        d.text((w / 2, h * 0.88), sub, font=sf, fill=(130, 100, 90), anchor="mm")
    return img


@lru_cache(maxsize=None)
def evidence_card(rows: tuple, head: str, filled_key: tuple, H: int) -> Image.Image:
    rh = int(H * 0.11)
    w, h = int(H * 1.0), rh * (len(rows) + 1) + int(H * 0.04)
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((3, 3, w - 3, h - 3), int(h * 0.06), fill=(255, 252, 244), outline=INK, width=4)
    d.text((w * 0.05, rh * 0.55), head, font=font(int(rh * 0.5)), fill=(90, 70, 64), anchor="lm")
    for i, (label, level) in enumerate(rows):
        y = rh * (i + 1) + rh * 0.55
        d.text((w * 0.05, y), label, font=font(int(rh * 0.46)), fill=(70, 54, 50), anchor="lm")
        n = filled_key[i]
        for j in range(5):
            cx = w * 0.62 + j * rh * 0.62
            on = j < n
            d.ellipse((cx - rh * 0.22, y - rh * 0.22, cx + rh * 0.22, y + rh * 0.22),
                      fill=((112, 188, 120) if level >= 3 else (236, 150, 90)) if on else (232, 224, 214), outline=INK, width=3)
    return img


@lru_cache(maxsize=None)
def stamp_sprite(text: str, H: int) -> Image.Image:
    f = font(int(H * 0.1))
    w = int(f.getlength(text)) + int(H * 0.14)
    h = int(H * 0.17)
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    col = (214, 70, 70)
    d.rounded_rectangle((4, 4, w - 4, h - 4), int(h * 0.2), outline=col, width=7)
    d.rounded_rectangle((14, 14, w - 14, h - 14), int(h * 0.15), outline=col, width=3)
    d.text((w / 2, h / 2 + 2), text, font=f, fill=col, anchor="mm")
    return img


def draw(img, item, t, W, H):
    kind = item["type"]
    at, dur = item.get("at", 0.0), item.get("dur", 999.0)
    alpha, scale = _env(t, at, dur)
    if alpha <= 0:
        return img
    lt = t - at
    x, y = item.get("pos", (0.5, 0.4))
    cx, cy = x * W, y * H
    sc = item.get("scale", 1.0)
    if kind == "stamp":
        x_ = min(1.0, lt / 0.22)
        s = 1.6 - 0.6 * (1 - (1 - x_) ** 3)                                  # slams down from large
        _paste(img, stamp_sprite(item["text"], H), cx, cy, alpha, s * sc, angle=item.get("angle", 10))
    elif kind == "card_grid":
        items = item["items"]
        cols = item.get("cols", 3)
        step = item.get("step", max(0.5, min(dur * 0.8 / len(items), 3.0)))
        cw, ch = int(H * 0.30 * sc), int(H * 0.34 * sc)
        gap = int(H * 0.025)
        rows = (len(items) + cols - 1) // cols
        total_w = cols * cw + (cols - 1) * gap
        total_h = rows * ch + (rows - 1) * gap
        for i, it in enumerate(items):
            a2, s2 = _env(lt, i * step, 999.0)
            r, c = divmod(i, cols)
            ox = cx - total_w / 2 + c * (cw + gap) + cw / 2
            oy = cy - total_h / 2 + r * (ch + gap) + ch / 2
            spr = card_sprite(it["icon"], it["label"], it.get("sub", ""), tuple(it.get("accent", (244, 178, 92))), H)
            _paste(img, spr, ox, oy, alpha * a2, min(1.0, s2) * sc)
    elif kind == "evidence":
        rows = tuple((r["label"], r["level"]) for r in item["rows"])
        step = item.get("step", max(0.6, min(dur * 0.7 / len(rows), 3.0)))
        filled = tuple(min(r["level"], int(max(0.0, lt - i * step) / 0.25)) for i, r in enumerate(item["rows"]))
        _paste(img, evidence_card(rows, item.get("head", ""), filled, H), cx, cy, alpha, min(1.0, scale) * sc)
    return img
