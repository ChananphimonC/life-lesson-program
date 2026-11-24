"""Extra places for the chicken-rice story: roadside tricycle cart + motorbike, wet market, shopping mall.

Same flat, supersampled style as `illustrator.py` (which calls these lazily, so this
module may import its helpers). Each returns (img, ground, lights, fg, info) like `_food_stall`.
"""

from __future__ import annotations

import math
import random


from PIL import Image, ImageDraw, ImageFont

from life_lesson.video.illustrator import _ANIM, _flame, _gradient, _lamp_post, _lerp, _sky_colors, _skyline


def _text(d, xy, text, font_path, size, fill):
    if not font_path:
        return
    try:
        d.text(xy, text, font=ImageFont.truetype(str(font_path), max(8, int(size))), fill=fill)
    except OSError:
        pass


def plate_chicken_rice(d, cx, cy, s, fried=False):
    """Khao man gai: oily rice mound, sliced chicken (pale = boiled, golden = fried), cucumber, dip bowl."""
    d.ellipse([cx - 44 * s, cy - 11 * s, cx + 44 * s, cy + 13 * s], fill=(246, 246, 240), outline=(200, 200, 196), width=max(1, int(1.5 * s)))
    d.ellipse([cx - 40 * s, cy - 26 * s, cx - 2 * s, cy + 2 * s], fill=(250, 238, 196))            # oily rice
    meat = (200, 128, 52) if fried else (244, 230, 200)
    for k in range(5):                                                                              # sliced chicken
        d.rounded_rectangle([cx - 2 * s + k * 7 * s, cy - 18 * s + (k % 2) * 3 * s, cx + 8 * s + k * 7 * s, cy + 2 * s + (k % 2) * 3 * s], 3 * s, fill=meat, outline=_lerp(meat, (120, 80, 40), 0.35))
    for k in range(4):                                                                              # cucumber
        d.ellipse([cx - 40 * s + k * 9 * s, cy + 2 * s, cx - 31 * s + k * 9 * s, cy + 10 * s], fill=(126, 176, 96), outline=(70, 120, 60))
    if not fried:
        for k in range(5):                                                                          # yellow skin edge + glossy sheen on boiled slices
            x0 = cx - 2 * s + k * 7 * s
            d.line([(x0, cy - 18 * s + (k % 2) * 3 * s), (x0 + 10 * s, cy - 18 * s + (k % 2) * 3 * s)], fill=(236, 198, 96), width=max(2, int(2.2 * s)))
            d.line([(x0 + 2 * s, cy - 13 * s + (k % 2) * 3 * s), (x0 + 7 * s, cy - 13 * s + (k % 2) * 3 * s)], fill=(255, 252, 238), width=max(1, int(1.4 * s)))
    d.ellipse([cx - 14 * s, cy - 31 * s, cx - 8 * s, cy - 26 * s], fill=(70, 150, 80))              # cilantro
    d.ellipse([cx + 30 * s, cy - 14 * s, cx + 46 * s, cy - 6 * s], fill=(120, 70, 36))             # dip (tao jiao)


def chicken_bird(d, hx, y, s, fried=False):
    """One hanging chicken. Boiled = pale, glossy skin with pores and a wing fold; fried = crisp golden with dark crackle."""
    skin = (214, 132, 52) if fried else (248, 232, 190)
    edge = _lerp(skin, (90, 50, 20), 0.45)
    d.ellipse([hx - 18 * s, y + 30 * s, hx + 18 * s, y + 94 * s], fill=skin, outline=edge, width=max(1, int(2 * s)))     # body
    d.ellipse([hx - 14 * s, y + 26 * s, hx + 14 * s, y + 44 * s], fill=_lerp(skin, (255, 255, 255), 0.1), outline=edge)    # neck/breast top
    d.arc([hx - 15 * s, y + 46 * s, hx + 3 * s, y + 78 * s], 200, 330, fill=edge, width=max(1, int(1.6 * s)))             # wing fold
    d.arc([hx - 2 * s, y + 52 * s, hx + 16 * s, y + 88 * s], 230, 350, fill=edge, width=max(1, int(1.2 * s)))             # thigh line
    rnd = random.Random(int(hx) % 997)
    for _ in range(26):                                                                                                      # skin pores / crackle
        px, py = hx + rnd.uniform(-12, 12) * s, y + rnd.uniform(40, 86) * s
        d.ellipse([px - 0.9 * s, py - 0.9 * s, px + 0.9 * s, py + 0.9 * s], fill=_lerp(skin, (110, 60, 24) if fried else (190, 150, 90), 0.55))
    d.ellipse([hx - 10 * s, y + 38 * s, hx - 1 * s, y + 66 * s], fill=_lerp(skin, (255, 255, 255), 0.5 if not fried else 0.3))  # glossy sheen
    for lx in (-9, 9):                                                                                                       # drumsticks with knuckles
        d.rounded_rectangle([hx + lx * s - 4.5 * s, y + 90 * s, hx + lx * s + 4.5 * s, y + 114 * s], 4 * s, fill=_lerp(skin, edge, 0.2), outline=edge)
        d.ellipse([hx + lx * s - 4 * s, y + 110 * s, hx + lx * s + 4 * s, y + 118 * s], fill=(236, 226, 206))
    if not fried:                                                                                                            # a thread of ginger left on the skin
        d.ellipse([hx + 4 * s, y + 70 * s, hx + 10 * s, y + 74 * s], fill=(214, 176, 90))


def _bulb_string(d, lights, x0, x1, y, h, n=9, sag=0.03):
    for i in range(n):
        t = i / (n - 1)
        x = x0 + (x1 - x0) * t
        yy = y + int(h * sag * 4 * t * (1 - t))
        dim = (i + _ANIM["phase"]) % 4 == 0
        d.ellipse([x - 6, yy - 6, x + 6, yy + 8], fill=(214, 186, 120) if dim else (255, 240, 176))
        lights.append(((int(x), int(yy)), int(h * 0.04), (255, 214, 120)))
    d.line([(x0, y), (x1, y)], fill=(30, 30, 34), width=2)


def chicken_cart(img, size, mood, rng, s, font_path, night, props=()):
    """Tricycle cart hitched to a motorbike on the roadside: glass case with hanging boiled + fried chicken,
    chopping board, rice pot with steam, plastic stools, string bulbs. Vendor stands at the right end of the counter."""
    w, h = size
    d = ImageDraw.Draw(img)
    ground = int(h * 0.86)
    lights, fg, info = [], [], {}
    top, bottom = _sky_colors(mood)
    img.paste(_gradient((w, ground), top, bottom), (0, 0))
    d = ImageDraw.Draw(img)
    far = _lerp(top, (0, 0, 0), 0.3) if night else _lerp(bottom, (70, 90, 120), 0.5)
    near = _lerp(top, (0, 0, 0), 0.55) if night else _lerp(bottom, (50, 60, 80), 0.6)
    _skyline(d, rng, w, ground - int(h * 0.1), (int(h * 0.12), int(h * 0.34)), far, (250, 214, 120) if night else None, 0.16)
    # shop shutters along the pavement
    sy = int(h * 0.50)
    d.rectangle([0, sy, w, ground], fill=_lerp(near, (255, 255, 255), 0.06))
    for x in range(0, w, int(44 * s)):
        d.line([(x, sy), (x, ground)], fill=_lerp(near, (0, 0, 0), 0.25), width=2)
    d.rectangle([0, ground, w, h], fill=_lerp(near, (0, 0, 0), 0.25) if night else (126, 124, 120))     # pavement + road
    d.rectangle([0, ground + int(h * 0.07), w, h], fill=(38, 38, 44) if night else (84, 84, 90))
    for x in range(0, w, int(120 * s)):
        d.rectangle([x, ground + int(h * 0.105), x + int(60 * s), ground + int(h * 0.115)], fill=(220, 210, 160))
    spot = _lamp_post(img, d, int(w * 0.93), ground, int(h * 0.42), night)
    if spot:
        lights.append((spot, int(h * 0.2), (255, 214, 130)))

    # ---- motorbike on the left (the cart is hitched to its side)
    mx = int(w * 0.075)
    wr = int(34 * s)
    for wx in (mx - int(46 * s), mx + int(74 * s)):
        d.ellipse([wx - wr, ground - 2 * wr + 6, wx + wr, ground + 6], fill=(22, 22, 26))
        d.ellipse([wx - wr * 0.55, ground - 1.55 * wr + 6, wx + wr * 0.55, ground - 0.45 * wr + 6], fill=(150, 150, 158))
    d.rounded_rectangle([mx - int(30 * s), ground - int(96 * s), mx + int(80 * s), ground - int(48 * s)], int(14 * s), fill=(176, 40, 40))   # body
    d.rounded_rectangle([mx + int(6 * s), ground - int(110 * s), mx + int(62 * s), ground - int(92 * s)], int(8 * s), fill=(30, 30, 36))     # seat
    d.line([(mx - int(46 * s), ground - int(40 * s)), (mx - int(40 * s), ground - int(120 * s))], fill=(60, 60, 68), width=max(4, int(7 * s)))  # fork
    d.line([(mx - int(52 * s), ground - int(124 * s)), (mx - int(22 * s), ground - int(128 * s))], fill=(30, 30, 36), width=max(4, int(6 * s)))  # handlebar
    d.ellipse([mx - int(58 * s), ground - int(118 * s), mx - int(42 * s), ground - int(100 * s)], fill=(255, 238, 170))                       # headlight
    if night:
        lights.append(((mx - int(50 * s), ground - int(110 * s)), int(h * 0.1), (255, 232, 160)))

    # ---- cart body
    cx0, cx1 = int(w * 0.19), int(w * 0.62)
    counter_y = ground - int(104 * s)
    d.line([(cx0 - int(10 * s), ground - int(60 * s)), (mx + int(50 * s), ground - int(60 * s))], fill=(70, 70, 78), width=max(5, int(8 * s)))   # hitch bar


    def cart_front(dd):
        # steel box, wheels and price panel are drawn AFTER the vendor so she stands behind the cart
        dd.rectangle([cx0, counter_y, cx1, ground - int(30 * s)], fill=(196, 198, 204))
        dd.rectangle([cx0, counter_y, cx1, counter_y + int(10 * s)], fill=(228, 230, 236))
        dd.rectangle([cx0, ground - int(40 * s), cx1, ground - int(2 * s)], fill=(104, 108, 120))      # skirt: hides the vendor's legs
        for wx in (cx0 + int(38 * s), cx1 - int(38 * s)):
            dd.ellipse([wx - int(26 * s), ground - int(52 * s), wx + int(26 * s), ground + 4], fill=(24, 24, 28))
            dd.ellipse([wx - int(13 * s), ground - int(39 * s), wx + int(13 * s), ground - int(9 * s)], fill=(150, 150, 158))
        bx0_, by0_ = int(w * 0.02), counter_y - int(150 * s)        # price board hangs above the motorbike, clear of caption + vendor
        dd.rounded_rectangle([bx0_, by0_, bx0_ + int(150 * s), by0_ + int(70 * s)], int(8 * s), fill=(252, 244, 214), outline=(176, 36, 40), width=max(2, int(3 * s)))
        _text(dd, (bx0_ + int(12 * s), by0_ + int(6 * s)), "ธรรมดา 50 บาท", font_path, 17 * s, (176, 36, 40))
        _text(dd, (bx0_ + int(12 * s), by0_ + int(36 * s)), "พิเศษ 60 บาท", font_path, 17 * s, (176, 36, 40))

    fg.append(cart_front)

    # glass case with hanging chicken (left half of the cart)
    gx0, gx1 = cx0 + int(14 * s), cx0 + int((cx1 - cx0) * 0.52)
    gy0 = counter_y - int(150 * s)
    d.rectangle([gx0, gy0, gx1, counter_y], fill=(66, 44, 34) if night else (96, 70, 52))                 # dark inside
    d.rectangle([gx0 + 6, gy0 + 6, gx1 - 6, counter_y - 6], fill=(118, 84, 56) if not night else (74, 52, 40))
    d.line([(gx0 + 8, gy0 + int(16 * s)), (gx1 - 8, gy0 + int(16 * s))], fill=(190, 190, 198), width=max(3, int(4 * s)))   # hanging rail
    n = 5
    for i in range(n):
        hx = gx0 + int((gx1 - gx0) * (i + 0.5) / n)
        d.line([(hx, gy0 + int(16 * s)), (hx, gy0 + int(34 * s))], fill=(190, 190, 198), width=max(2, int(3 * s)))
        chicken_bird(d, hx, gy0 + int(4 * s), s * 0.92, fried=i >= 3)
    d.rectangle([gx0 + 6, counter_y - int(34 * s), gx1 - 6, counter_y - 6], fill=(214, 214, 220))              # tray of chopped pieces
    for k in range(7):
        d.rounded_rectangle([gx0 + 14 + k * int(15 * s), counter_y - int(30 * s), gx0 + 14 + k * int(15 * s) + int(11 * s), counter_y - int(14 * s)], int(3 * s), fill=(244, 230, 200) if k < 4 else (206, 134, 54))
    # sign + price board on top of the case
    sg0, sg1 = gx0 - int(10 * s), gx1 + int(10 * s)
    d.rounded_rectangle([sg0, gy0 - int(60 * s), sg1, gy0 - int(8 * s)], int(8 * s), fill=(196, 40, 44), outline=(250, 226, 150), width=max(3, int(4 * s)))
    _text(d, (sg0 + int(16 * s), gy0 - int(58 * s)), "ข้าวมันไก่", font_path, 30 * s, (255, 244, 214))

    # chopping board + rice pot on the right half; vendor stands behind the board
    bx = int(cx0 + (cx1 - cx0) * 0.72)
    board = (bx - int(36 * s), counter_y - int(8 * s), bx + int(36 * s), counter_y + int(2 * s))
    d.rounded_rectangle(board, int(4 * s), fill=(176, 128, 76), outline=(120, 80, 44), width=2)
    for k in range(3):                                                                                      # half-chopped chicken on the board
        d.rounded_rectangle([bx - int(26 * s) + k * int(16 * s), board[1] - int(10 * s), bx - int(14 * s) + k * int(16 * s), board[1] + int(2 * s)], int(3 * s), fill=(244, 230, 200))
    px = cx1 - int(30 * s)
    d.rounded_rectangle([px - int(24 * s), counter_y - int(52 * s), px + int(24 * s), counter_y], int(6 * s), fill=(236, 238, 244), outline=(160, 164, 176), width=2)   # soup pot
    d.rectangle([px - int(26 * s), counter_y - int(56 * s), px + int(26 * s), counter_y - int(48 * s)], fill=(196, 40, 44))

    # tables + plastic stools on the right
    tx = int(w * 0.775)
    table_y = ground - int(66 * s)
    d.rectangle([tx - int(54 * s), table_y, tx + int(54 * s), table_y + int(8 * s)], fill=(210, 64, 56))
    for lx in (-44, 44):
        d.rectangle([tx + int(lx * s) - 3, table_y + int(8 * s), tx + int(lx * s) + 3, ground], fill=(150, 150, 156))
    plate_chicken_rice(d, tx - int(12 * s), table_y - int(2 * s), s * 0.9)
    stools = [int(w * 0.675), int(w * 0.875)]
    for sx in stools:
        d.rounded_rectangle([sx - int(22 * s), ground - int(46 * s), sx + int(22 * s), ground - int(36 * s)], int(4 * s), fill=(214, 78, 70))
        for lx in (-16, 16):
            d.rectangle([sx + int(lx * s) - int(3 * s), ground - int(36 * s), sx + int(lx * s) + int(3 * s), ground], fill=(190, 64, 58))

    _bulb_string(d, lights, cx0 - int(30 * s), int(w * 0.98), int(h * 0.20), h)

    info.update(cook_x=bx, counter_y=counter_y, board=board, stools=stools, stool_top=ground - int(46 * s),
                ground=ground, steam=(px, counter_y - int(60 * s)))
    return img, ground, lights, fg, info


def market(img, size, mood, rng, s, font_path, night, props=()):
    """Early wet market: tarp-covered stalls, crates, hanging chickens, hanging bulbs."""
    w, h = size
    d = ImageDraw.Draw(img)
    ground = int(h * 0.86)
    lights, fg, info = [], [], {}
    d.rectangle([0, 0, w, ground], fill=(34, 34, 44) if night else (196, 190, 170))
    d.rectangle([0, ground, w, h], fill=(48, 50, 54) if night else (132, 128, 120))
    tarp = [(214, 70, 60), (64, 132, 200), (236, 190, 60), (80, 160, 100)]
    d.rectangle([0, int(h * 0.30), w, ground - int(90 * s)], fill=(60, 54, 52) if night else (150, 136, 116))   # stall back walls
    for i, col in enumerate(tarp):
        x0 = int(w * i / len(tarp))
        x1 = int(w * (i + 1) / len(tarp))
        d.polygon([(x0, int(h * 0.12)), (x1, int(h * 0.12)), (x1 - int(10 * s), int(h * 0.30)), (x0 + int(10 * s), int(h * 0.30))], fill=_lerp(col, (0, 0, 0), 0.35 if night else 0.0))
        for k in range(0, x1 - x0, int(46 * s)):
            d.line([(x0 + k, int(h * 0.12)), (x0 + k, int(h * 0.30))], fill=_lerp(col, (0, 0, 0), 0.3), width=2)
        # stall table + crates
        d.rectangle([x0 + int(20 * s), ground - int(90 * s), x1 - int(20 * s), ground - int(70 * s)], fill=(150, 150, 158))
        d.rectangle([x0 + int(24 * s), ground - int(70 * s), x1 - int(24 * s), ground], fill=(96, 98, 106))
        for k in range(3):
            c = (x0 + int(34 * s) + k * int((x1 - x0 - int(70 * s)) / 3), ground - int(120 * s))
            d.rounded_rectangle([c[0], c[1], c[0] + int(60 * s), c[1] + int(30 * s)], int(6 * s), fill=[(220, 150, 140), (150, 190, 120), (244, 220, 170)][(i + k) % 3])
    for k in range(5):                                                                                      # hanging chickens at the second stall
        hx = int(w * (0.30 + 0.035 * k))
        d.line([(hx, int(h * 0.30)), (hx, int(h * 0.36))], fill=(70, 70, 78), width=3)
        chicken_bird(d, hx, int(h * 0.36) - int(30 * s), s * 0.8)
    _bulb_string(d, lights, 0, w, int(h * 0.10), h, n=12)
    info.update(ground=ground, cook_x=int(w * 0.5))
    return img, ground, lights, fg, info


def mall(img, size, mood, rng, s, font_path, night, props=()):
    """Mall concourse: bright shopfront row, shiny floor, ceiling lights."""
    w, h = size
    d = ImageDraw.Draw(img)
    ground = int(h * 0.80)
    lights, fg, info = [], [], {}
    d.rectangle([0, 0, w, ground], fill=(232, 232, 238))
    d.rectangle([0, 0, w, int(h * 0.10)], fill=(214, 216, 226))
    for i in range(7):
        x = int(w * (i + 0.5) / 7)
        d.rounded_rectangle([x - int(30 * s), int(h * 0.03), x + int(30 * s), int(h * 0.06)], int(5 * s), fill=(255, 252, 236))
        lights.append(((x, int(h * 0.05)), int(h * 0.12), (255, 240, 200)))
    cols = [(236, 96, 120), (96, 164, 236), (250, 190, 70), (110, 200, 150), (180, 120, 230)]
    n = 5
    for i in range(n):
        x0 = int(w * i / n) + int(14 * s)
        x1 = int(w * (i + 1) / n) - int(14 * s)
        d.rectangle([x0, int(h * 0.16), x1, ground], fill=_lerp(cols[i], (255, 255, 255), 0.55))
        d.rectangle([x0, int(h * 0.16), x1, int(h * 0.27)], fill=cols[i])                                   # shop sign band
        d.rectangle([x0 + int(10 * s), int(h * 0.33), x1 - int(10 * s), ground - int(8 * s)], fill=(244, 248, 252))   # window
        for k in range(3):                                                                                   # items on display
            ix = x0 + int(30 * s) + k * int((x1 - x0 - int(60 * s)) / 3)
            d.rounded_rectangle([ix, ground - int(120 * s), ix + int(34 * s), ground - int(40 * s)], int(8 * s), fill=_lerp(cols[(i + k) % n], (255, 255, 255), 0.2))
    d.rectangle([0, ground, w, h], fill=(196, 198, 206))
    for x in range(0, w, int(90 * s)):
        d.line([(x, ground), (x - int(60 * s), h)], fill=(214, 216, 224), width=2)
    d.rectangle([0, ground, w, ground + int(10 * s)], fill=(168, 170, 180))
    ph = _ANIM["phase"]
    for i in range(n):                                                                                     # neon "SALE" strips blink across shops
        if (i + ph) % 3 == 0:
            x0 = int(w * i / n) + int(30 * s)
            d.rounded_rectangle([x0, int(h * 0.285), x0 + int(60 * s), int(h * 0.31)], int(4 * s), fill=(255, 250, 200))
    from life_lesson.video.illustrator import _draw_character, character_colors
    for k, base in enumerate((0.08, 0.22, 0.90)):                                                           # shoppers strolling past the windows
        col = character_colors(["เสื้อสีม่วง", "เสื้อสีเขียว", "เสื้อสีแดง"][k], None, name=f"mall{k}")
        px = int(w * (base + 0.004 * ph * (1 if k % 2 else -1)))
        _draw_character(d, px, ground - int(14 * s), s * 0.9, col, walk=(ph + 3 * k) % 8)
    for x in (0.05, 0.95):                                                                           # planters
        px = int(w * x)
        d.rounded_rectangle([px - int(22 * s), ground - int(36 * s), px + int(22 * s), ground + int(4 * s)], int(6 * s), fill=(120, 96, 76))
        for k, dx in enumerate((-14, 0, 14)):
            d.ellipse([px + int(dx * s) - int(14 * s), ground - int(90 * s) - (k % 2) * int(10 * s), px + int(dx * s) + int(14 * s), ground - int(30 * s)], fill=(70, 150, 96))
    for k in range(6):                                                                                    # soft floor reflections of the shop lights
        gx = int(w * (k + 0.5) / 6)
        d.rectangle([gx - int(30 * s), ground + int(14 * s), gx + int(30 * s), h], fill=(206, 208, 216))
    info.update(ground=ground, cook_x=int(w * 0.5))
    return img, ground, lights, fg, info


def office_back(img, size, ground, night, lights, s, font_path):
    """Office wall: window with blinds onto the skyline, ceiling light panels, wall clock, partitions, plant."""
    w, h = size
    d = ImageDraw.Draw(img)
    wall = (58, 62, 78) if night else (226, 224, 218)
    shade = _lerp(wall, (0, 0, 0), 0.2)
    wx0, wy0, wx1, wy1 = int(w * 0.50), int(h * 0.14), int(w * 0.96), int(h * 0.60)
    # paint wall over everything except the window opening (keeps the skyline view inside it)
    view = img.crop((wx0, wy0, wx1, wy1))
    d.rectangle([0, 0, w, ground], fill=wall)
    img.paste(view, (wx0, wy0))
    d = ImageDraw.Draw(img)
    d.rectangle([wx0 - 10, wy0 - 10, wx1 + 10, wy1 + 10], outline=(34, 36, 44), width=10)
    for k in range(1, 4):
        d.line([(wx0 + (wx1 - wx0) * k // 4, wy0), (wx0 + (wx1 - wx0) * k // 4, wy1)], fill=(34, 36, 44), width=6)
    for yy in range(wy0 + 8, wy0 + int((wy1 - wy0) * 0.45), 16):                                           # half-open blinds
        d.rectangle([wx0, yy, wx1, yy + 8], fill=_lerp(wall, (255, 255, 255), 0.15) if not night else (80, 84, 100))
    d.rectangle([0, 0, w, int(h * 0.09)], fill=shade)                                                    # ceiling band
    for i in range(5):
        x = int(w * (i + 0.5) / 5)
        d.rectangle([x - int(44 * s), int(h * 0.02), x + int(44 * s), int(h * 0.055)], fill=(255, 252, 236))
        lights.append(((x, int(h * 0.05)), int(h * 0.16), (255, 248, 220)))
    cx, cy, r = int(w * 0.30), int(h * 0.27), int(34 * s)                                                # wall clock
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(250, 250, 248), outline=(40, 40, 48), width=max(3, int(4 * s)))
    d.line([(cx, cy), (cx, cy - int(r * 0.7))], fill=(30, 30, 36), width=max(2, int(3 * s)))
    d.line([(cx, cy), (cx + int(r * 0.5), cy)], fill=(30, 30, 36), width=max(2, int(3 * s)))
    d.rectangle([0, int(h * 0.60), int(w * 0.14), ground], fill=_lerp(wall, (0, 0, 0), 0.12))             # cubicle partition far left
    d.rectangle([int(w * 0.10), int(h * 0.38), int(w * 0.28), int(h * 0.45)], fill=(236, 176, 60))       # shelf of binders
    for k in range(6):
        d.rectangle([int(w * 0.10) + k * int(w * 0.03), int(h * 0.31), int(w * 0.10) + k * int(w * 0.03) + int(w * 0.022), int(h * 0.38)], fill=[(206, 70, 70), (70, 120, 200), (90, 160, 110)][k % 3])
    px = int(w * 0.93)                                                                                    # plant in the corner
    d.rounded_rectangle([px - int(22 * s), ground - int(50 * s), px + int(22 * s), ground], int(6 * s), fill=(120, 90, 70))
    for dx, hh in ((-16, 80), (0, 104), (16, 76)):
        d.ellipse([px + int(dx * s) - int(16 * s), ground - int(50 * s) - int(hh * s), px + int(dx * s) + int(16 * s), ground - int(40 * s)], fill=(60, 140, 90))
    # floor: carpet + long window-light shafts
    d.rectangle([0, ground, w, h], fill=_lerp(wall, (60, 70, 100), 0.5) if not night else (26, 28, 40))
    shaft = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(shaft).polygon([(wx0, ground), (wx0 + int(w * 0.08), ground), (int(w * 0.28), h), (int(w * 0.14), h)], fill=(255, 248, 210, 58 if not night else 24))
    img.alpha_composite(shaft) if img.mode == "RGBA" else img.paste(Image.alpha_composite(img.convert("RGBA"), shaft).convert("RGB"))


def office_front(dd, size, ground, night, s, font_path):
    """Desk with glowing monitor (chart), keyboard, mug, paper stack and a soft shadow on the floor under it."""
    w, h = size
    dx0, dx1 = int(w * 0.10), int(w * 0.62)
    dd.ellipse([dx0 - int(10 * s), ground - int(8 * s), dx1 + int(30 * s), ground + int(26 * s)], fill=(30, 28, 40) if night else (150, 146, 150))   # shadow under desk
    dd.rectangle([dx0, ground - 40, dx1, ground - 22], fill=(150, 112, 80) if not night else (70, 52, 44))
    dd.rectangle([dx0, ground - 22, dx1, h], fill=(96, 70, 54) if not night else (46, 36, 34))
    dd.rectangle([dx0 + 8, ground - 22, dx0 + int(26 * s), h], fill=(70, 50, 40) if not night else (34, 26, 26))                 # drawer side
    mx0, mx1 = int(w * 0.36), int(w * 0.52)
    dd.rectangle([mx0, ground - 128, mx1, ground - 44], fill=(26, 30, 38), outline=(60, 64, 76), width=4)                       # monitor
    dd.rectangle([mx0 + 8, ground - 120, mx1 - 8, ground - 52], fill=(40, 70, 120) if night else (60, 100, 160))
    for k, hh in enumerate([hh + 6 * math.sin(_ANIM["phase"] * 0.9 + k * 1.7) for k, hh in enumerate((20, 34, 26, 48, 38))]):                                                                                # chart bars on screen
        bx = mx0 + 18 + k * int((mx1 - mx0 - 36) / 5)
        dd.rectangle([bx, ground - 56 - hh, bx + int((mx1 - mx0 - 36) / 7), ground - 56], fill=(250, 214, 120))
    dd.rectangle([(mx0 + mx1) // 2 - 6, ground - 44, (mx0 + mx1) // 2 + 6, ground - 40], fill=(50, 54, 64))
    dd.rounded_rectangle([int(w * 0.25), ground - 46, int(w * 0.34), ground - 40], 3, fill=(210, 212, 220), outline=(120, 124, 134))   # keyboard
    dd.rounded_rectangle([int(w * 0.55), ground - 64, int(w * 0.575), ground - 40], 4, fill=(250, 250, 246), outline=(150, 150, 156))  # mug
    dd.rectangle([int(w * 0.585), ground - 56, int(w * 0.60), ground - 41], fill=(236, 238, 242))                                # paper stack
    dd.rectangle([int(w * 0.585), ground - 60, int(w * 0.60), ground - 56], fill=(220, 224, 232))


def kitchen(img, size, mood, rng, s, font_path, night, props=()):
    """Home kitchen at dawn: tiled wall, window light, gas stove with a big pot of boiling chicken, ginger/coriander root/garlic."""
    w, h = size
    d = ImageDraw.Draw(img)
    ground = int(h * 0.86)
    lights, fg, info = [], [], {}
    wall = (70, 76, 84) if night else (226, 214, 190)
    d.rectangle([0, 0, w, ground], fill=wall)
    for y in range(int(h * 0.30), ground, int(48 * s)):                                                   # wall tiles
        d.line([(0, y), (w, y)], fill=_lerp(wall, (0, 0, 0), 0.15), width=2)
    for x in range(0, w, int(48 * s)):
        d.line([(x, int(h * 0.30)), (x, ground)], fill=_lerp(wall, (0, 0, 0), 0.15), width=2)
    wx0, wy0, wx1, wy1 = int(w * 0.64), int(h * 0.10), int(w * 0.92), int(h * 0.42)                       # window with dawn light
    top, bottom = _sky_colors(mood)
    img.paste(_gradient((wx1 - wx0, wy1 - wy0), top, bottom), (wx0, wy0))
    d = ImageDraw.Draw(img)
    d.rectangle([wx0 - 8, wy0 - 8, wx1 + 8, wy1 + 8], outline=(110, 84, 60), width=8)
    d.line([((wx0 + wx1) // 2, wy0), ((wx0 + wx1) // 2, wy1)], fill=(110, 84, 60), width=6)
    lights.append((((wx0 + wx1) // 2, (wy0 + wy1) // 2), int(h * 0.34), (255, 226, 170)))
    d.rectangle([0, ground, w, h], fill=(150, 120, 96) if not night else (60, 50, 46))
    for k in range(6):                                                                                     # hanging ladle / pan on the wall
        hx = int(w * 0.06) + k * int(40 * s)
        d.line([(hx, int(h * 0.16)), (hx, int(h * 0.16) + int((50 + 10 * (k % 3)) * s))], fill=(120, 120, 128), width=max(2, int(3 * s)))
        d.ellipse([hx - int(10 * s), int(h * 0.16) + int((46 + 10 * (k % 3)) * s), hx + int(10 * s), int(h * 0.16) + int((66 + 10 * (k % 3)) * s)], fill=(168, 170, 178))
    cx = int(w * 0.40)
    counter_y = ground - int(80 * s)
    d.rectangle([int(w * 0.04), counter_y, int(w * 0.62), ground], fill=(190, 186, 176))                   # counter body
    d.rectangle([int(w * 0.04), counter_y, int(w * 0.62), counter_y + int(12 * s)], fill=(236, 232, 222))
    # prep bowls: ginger, coriander roots, garlic
    for k, col in enumerate(((214, 176, 100), (110, 150, 80), (246, 240, 224))):
        bx = int(w * 0.10) + k * int(60 * s)
        d.ellipse([bx - int(24 * s), counter_y - int(14 * s), bx + int(24 * s), counter_y + int(4 * s)], fill=(250, 250, 246), outline=(180, 180, 186))
        for j in range(4):
            d.ellipse([bx - int(18 * s) + j * int(9 * s), counter_y - int(22 * s) - (j % 2) * int(4 * s), bx - int(8 * s) + j * int(9 * s), counter_y - int(8 * s)], fill=col)
    pot_r = int(54 * s)
    pot_y = counter_y - int(60 * s)
    d.rectangle([cx - pot_r - int(6 * s), pot_y, cx + pot_r + int(6 * s), counter_y], fill=(176, 178, 186))        # pot body
    d.ellipse([cx - pot_r - int(6 * s), pot_y - int(14 * s), cx + pot_r + int(6 * s), pot_y + int(14 * s)], fill=(206, 208, 216), outline=(120, 122, 132), width=3)
    d.ellipse([cx - pot_r, pot_y - int(10 * s), cx + pot_r, pot_y + int(10 * s)], fill=(214, 186, 96))              # broth surface
    d.ellipse([cx - int(30 * s), pot_y - int(26 * s), cx + int(24 * s), pot_y + int(6 * s)], fill=(250, 232, 190), outline=(190, 150, 90), width=2)   # chicken breast breaking the surface
    for k in range(5):
        by_ = pot_y + int(5 * s * math.sin(_ANIM["phase"] * 1.4 + k * 2.1))
        d.ellipse([cx - pot_r + int(10 * s) + k * int(20 * s), by_ - int(4 * s), cx - pot_r + int(18 * s) + k * int(20 * s), by_ + int(4 * s)], fill=(236, 214, 140))   # oil bubbles rise and pop
    d.rounded_rectangle([cx + pot_r + int(6 * s), pot_y - int(6 * s), cx + pot_r + int(44 * s), pot_y + int(2 * s)], int(3 * s), fill=(120, 84, 50))    # handle
    _flame(d, cx, counter_y, s * 1.1, 0.8)
    info.update(cook_x=int(w * 0.50), ground=ground, counter_y=counter_y, steam=(cx, pot_y - int(30 * s)))
    lights.append(((cx, pot_y), int(h * 0.16), (255, 190, 110)))
    return img, ground, lights, fg, info


def bts(img, size, mood, rng, s, font_path, night, props=()):
    """Sky-train carriage: sliding doors, route strip above them, poles + hand straps, side seats,
    window onto a skyline that scrolls past (animated), commuters on their phones in the background."""
    from life_lesson.video.illustrator import _draw_character, character_colors

    w, h = size
    d = ImageDraw.Draw(img)
    ground = int(h * 0.86)
    lights, fg, info = [], [], {}
    wall = (214, 218, 226) if not night else (70, 76, 92)
    d.rectangle([0, 0, w, h], fill=wall)
    d.rectangle([0, 0, w, int(h * 0.07)], fill=_lerp(wall, (255, 255, 255), 0.35))                         # ceiling
    for i in range(6):
        x = int(w * (i + 0.5) / 6)
        d.rectangle([x - int(50 * s), int(h * 0.02), x + int(50 * s), int(h * 0.045)], fill=(255, 252, 240))
        lights.append(((x, int(h * 0.04)), int(h * 0.14), (255, 250, 230)))
    # route strip in Silom-line dark green; code badges + names at both ends, a dot rides the line
    sg = _ANIM.get("signs") or {}
    GREEN = (0, 104, 71)
    ry = int(h * 0.075)
    d.rounded_rectangle([int(w * 0.12), ry, int(w * 0.88), ry + int(52 * s)], int(8 * s), fill=(250, 250, 248), outline=GREEN, width=max(3, int(4 * s)))
    x0, x1 = int(w * 0.30), int(w * 0.70)
    d.line([(x0, ry + int(26 * s)), (x1, ry + int(26 * s))], fill=GREEN, width=max(5, int(7 * s)))
    for i in range(9):
        sx = int(x0 + (x1 - x0) * i / 8)
        d.ellipse([sx - int(5 * s), ry + int(21 * s), sx + int(5 * s), ry + int(31 * s)], fill=(255, 255, 255), outline=GREEN, width=max(2, int(2 * s)))
    prog = _ANIM["prog"] if _ANIM["prog"] is not None else 0.0
    px = int(x0 + (x1 - x0) * min(1.0, prog))
    on = (_ANIM["phase"] % 2) == 0
    d.ellipse([px - int(9 * s), ry + int(17 * s), px + int(9 * s), ry + int(35 * s)], fill=(255, 200, 40) if on else (255, 150, 40), outline=(30, 30, 36), width=max(1, int(2 * s)))
    for side, key in ((0, "from"), (1, "to")):
        if not sg.get(key):
            continue
        bx = int(w * 0.125) if side == 0 else int(w * 0.875) - int(40 * s)
        d.rounded_rectangle([bx, ry + int(6 * s), bx + int(40 * s), ry + int(46 * s)], int(6 * s), fill=GREEN)
        _text(d, (bx + int(5 * s), ry + int(12 * s)), sg.get(key + "_code", ""), font_path, 18 * s, (255, 255, 255))
        nx = bx + int(46 * s) if side == 0 else bx - int(len(sg[key]) * 10 * s) - int(6 * s)
        _text(d, (nx, ry + int(4 * s)), sg[key], font_path, 17 * s, (20, 70, 50))
        if sg.get(key + "_en"):
            _text(d, (nx, ry + int(26 * s)), sg[key + "_en"], font_path, 12 * s, (60, 100, 80))
    # windows with a scrolling skyline
    wy0, wy1 = int(h * 0.20), int(h * 0.52)
    top, bottom = _sky_colors(mood)
    sky = _gradient((w, wy1 - wy0), top, bottom)
    img.paste(sky, (0, wy0))
    d = ImageDraw.Draw(img)
    off = (_ANIM["phase"] * int(36 * s)) % int(w * 0.5)
    r2 = random.Random(5)
    x = -off
    while x < w + 100:
        bw, bh = r2.randrange(int(60 * s), int(150 * s)), r2.randrange(int(40 * s), int(wy1 - wy0 - 20 * s))
        d.rectangle([x, wy1 - bh, x + bw, wy1], fill=_lerp(bottom, (40, 50, 80), 0.55))
        x += bw + r2.randrange(0, int(20 * s))
    for k in range(5):                                                                                      # window frames
        fx = int(w * k / 4)
        d.rectangle([fx - int(10 * s), wy0, fx + int(10 * s), wy1], fill=wall)
    d.rectangle([0, wy0 - int(8 * s), w, wy0], fill=wall)
    d.rectangle([0, wy1, w, wy1 + int(8 * s)], fill=wall)
    # side seats (blue) under the windows + floor
    d.rectangle([0, int(h * 0.54), w, int(h * 0.72)], fill=(60, 110, 190))
    d.rectangle([0, int(h * 0.72), w, int(h * 0.76)], fill=(40, 80, 150))
    d.rectangle([0, ground - int(40 * s), w, h], fill=(120, 124, 134))
    d.rectangle([0, ground, w, h], fill=(96, 100, 112))
    # overhead rail + hanging straps (they sway)
    d.line([(0, int(h * 0.27) - int(60 * s)), (w, int(h * 0.27) - int(60 * s))], fill=(190, 194, 204), width=max(4, int(6 * s)))
    for k in range(9):
        hx = int(w * (k + 0.5) / 9)
        sway = int(5 * s * math.sin(_ANIM["phase"] * 0.8 + k))
        d.line([(hx, int(h * 0.27) - int(60 * s)), (hx + sway, int(h * 0.27) - int(10 * s))], fill=(60, 64, 76), width=max(2, int(3 * s)))
        d.ellipse([hx + sway - int(12 * s), int(h * 0.27) - int(10 * s), hx + sway + int(12 * s), int(h * 0.27) + int(18 * s)], outline=(240, 240, 244), width=max(3, int(4 * s)))
    # commuters on phones in the background (seated, faces lit by the screen)
    outfits = ["เสื้อสีเขียว", "เสื้อสีเหลือง", "เสื้อสีม่วง", "เสื้อสีแดง", "เสื้อสีเทา"]
    for k, fx in enumerate((0.09, 0.27, 0.73, 0.91)):
        col = character_colors(outfits[k % len(outfits)], None, name=f"extra{k}", extra_items=("seated",))
        _draw_character(d, int(w * fx), int(h * 0.74) + int(22 * s), s * 0.9, col, sitting=True,
                        hands={"L": (int(w * fx) - 8 * s, int(h * 0.70)), "R": (int(w * fx) + 8 * s, int(h * 0.70))})
        d.rounded_rectangle([int(w * fx) - 9 * s, int(h * 0.67), int(w * fx) + 9 * s, int(h * 0.70)], int(2 * s), fill=(180, 220, 255))   # phone
    # vertical pole near the middle
    d.rectangle([int(w * 0.62) - int(5 * s), int(h * 0.20), int(w * 0.62) + int(5 * s), ground], fill=(220, 224, 232))
    info.update(ground=ground, cook_x=int(w * 0.45))
    return img, ground, lights, fg, info


def compare(img, size, mood, rng, s, font_path, night, props=()):
    """Two columns, same day: office worker vs. rice-cart vendor. Hours and money as bars (story numbers)."""
    w, h = size
    d = ImageDraw.Draw(img)
    ground = int(h * 0.88)
    lights, fg, info = [], [], {}
    d.rectangle([0, 0, w // 2, h], fill=(48, 62, 92) if night else (205, 222, 244))
    d.rectangle([w // 2, 0, w, h], fill=(86, 56, 40) if night else (248, 222, 180))
    d.rectangle([w // 2 - int(3 * s), 0, w // 2 + int(3 * s), h], fill=(30, 30, 38))
    d.rectangle([0, ground, w, h], fill=(60, 60, 68) if night else (160, 156, 150))
    ink_l = (240, 244, 255) if night else (30, 50, 90)
    ink_r = (255, 236, 200) if night else (110, 50, 20)
    cfg = _ANIM.get("compare") or {}
    _text(d, (int(w * 0.07), int(h * 0.04)), cfg.get("left", "ฝั่งซ้าย"), font_path, 34 * s, ink_l)
    _text(d, (int(w * 0.57), int(h * 0.04)), cfg.get("right", "ฝั่งขวา"), font_path, 34 * s, ink_r)
    y = int(h * 0.14)
    for row in (cfg.get("rows") or [])[:3]:
        a, b = float(row["left"]), float(row["right"])
        mx = max(a, b, 1e-9)
        _text(d, (int(w * 0.07), y), row["label"], font_path, 22 * s, ink_l)
        _text(d, (int(w * 0.57), y), row["label"], font_path, 22 * s, ink_r)
        bar_h = int(38 * s)
        by = y + int(32 * s)
        grow = 0.94 + 0.06 * math.sin(_ANIM["phase"] * 0.8)           # the bars breathe a little
        d.rounded_rectangle([int(w * 0.07), by, int(w * 0.07) + int(w * 0.38 * a / mx * grow), by + bar_h], int(8 * s), fill=(70, 120, 210))
        d.rounded_rectangle([int(w * 0.57), by, int(w * 0.57) + int(w * 0.38 * b / mx * grow), by + bar_h], int(8 * s), fill=(226, 120, 40))
        _text(d, (int(w * 0.075), by + int(5 * s)), row.get("left_text", str(row["left"])), font_path, 17 * s, (255, 255, 255))
        _text(d, (int(w * 0.575), by + int(5 * s)), row.get("right_text", str(row["right"])), font_path, 17 * s, (255, 255, 255))
        y += int(92 * s)
    if cfg.get("note"):
        _text(d, (int(w * 0.36), int(h * 0.925)), cfg["note"], font_path, 15 * s, (255, 255, 255))
    info.update(ground=ground, cook_x=int(w * 0.75), left_x=int(w * 0.25), right_x=int(w * 0.75))
    return img, ground, lights, fg, info


def bus_stop(img, size, mood, rng, s, font_path, night, props=()):
    """Roadside bus stop in the evening. A blue-and-white electric bus rolls in from the right and stops
    (animated by `prog`), brake lights flash as it settles; shelter with bench, route sign, skyline behind."""
    w, h = size
    d = ImageDraw.Draw(img)
    ground = int(h * 0.90)
    lights, fg, info = [], [], {}
    top, bottom = _sky_colors(mood)
    img.paste(_gradient((w, int(h * 0.62)), top, bottom), (0, 0))
    d = ImageDraw.Draw(img)
    far = _lerp(top, (0, 0, 0), 0.3) if night else _lerp(bottom, (70, 90, 120), 0.5)
    _skyline(d, rng, w, int(h * 0.60), (int(h * 0.12), int(h * 0.36)), far, (250, 214, 120) if night else None, 0.2)
    d.rectangle([0, int(h * 0.60), w, int(h * 0.82)], fill=(54, 56, 64) if night else (96, 98, 106))             # road
    for x in range(0, w, int(110 * s)):
        d.rectangle([x, int(h * 0.71), x + int(56 * s), int(h * 0.72)], fill=(230, 224, 170))
    d.rectangle([0, int(h * 0.82), w, h], fill=(126, 124, 120) if not night else (66, 66, 72))                      # pavement
    d.rectangle([0, int(h * 0.82), w, int(h * 0.84)], fill=(190, 188, 180) if not night else (100, 100, 108))      # curb
    # the bus: eases in from the right
    prog = _ANIM["prog"] if _ANIM["prog"] is not None else 0.85
    t = 1 - (1 - min(1.0, prog * 1.15)) ** 2
    bw, bh = int(w * 0.62), int(h * 0.30)
    bx = int(w * 1.04 - (w * 1.04 - w * 0.34) * t)
    by1 = int(h * 0.805)
    by0 = by1 - bh
    d.rounded_rectangle([bx, by0, bx + bw, by1], int(14 * s), fill=(28, 92, 196))
    d.rectangle([bx, by0 + int(bh * 0.62), bx + bw, by0 + int(bh * 0.70)], fill=(240, 244, 252))                  # white stripe
    for k in range(5):                                                                                           # windows with silhouettes
        wx = bx + int(bw * (0.04 + 0.185 * k))
        d.rounded_rectangle([wx, by0 + int(bh * 0.1), wx + int(bw * 0.16), by0 + int(bh * 0.5)], int(6 * s), fill=(176, 214, 244))
        d.ellipse([wx + int(bw * 0.05), by0 + int(bh * 0.28), wx + int(bw * 0.11), by0 + int(bh * 0.42)], fill=(60, 70, 96))
    d.rounded_rectangle([bx + int(bw * 0.03), by0 + int(bh * 0.04), bx + int(bw * 0.2), by0 + int(bh * 0.1)], int(3 * s), fill=(20, 24, 32))   # destination board
    _text(d, (bx + int(bw * 0.04), by0 + int(bh * 0.03)), "547 ศาลายา", font_path, 13 * s, (255, 200, 60))
    for wx in (bx + int(bw * 0.2), bx + int(bw * 0.78)):
        d.ellipse([wx - int(30 * s), by1 - int(30 * s), wx + int(30 * s), by1 + int(30 * s)], fill=(22, 22, 26))
        d.ellipse([wx - int(14 * s), by1 - int(14 * s), wx + int(14 * s), by1 + int(14 * s)], fill=(150, 150, 158))
    d.ellipse([bx - int(6 * s), by1 - int(bh * 0.32), bx + int(10 * s), by1 - int(bh * 0.18)], fill=(255, 240, 180))   # headlight
    braking = t > 0.92 and (_ANIM["phase"] % 2 == 0)
    d.rectangle([bx + bw - int(10 * s), by0 + int(bh * 0.74), bx + bw, by0 + int(bh * 0.88)], fill=(255, 60, 50) if braking else (130, 30, 30))
    lights.append(((bx + int(4 * s), by1 - int(bh * 0.25)), int(h * 0.12), (255, 240, 190)))
    if braking:
        lights.append(((bx + bw, by0 + int(bh * 0.8)), int(h * 0.07), (255, 70, 60)))
    # shelter + sign on the pavement (left)
    sx0, sx1 = int(w * 0.04), int(w * 0.30)
    d.rectangle([sx0, int(h * 0.58), sx1, int(h * 0.605)], fill=(70, 76, 90))
    for x in (sx0 + int(8 * s), sx1 - int(8 * s)):
        d.rectangle([x - 3, int(h * 0.605), x + 3, int(h * 0.84)], fill=(70, 76, 90))
    d.rectangle([sx0 + int(14 * s), int(h * 0.76), sx1 - int(14 * s), int(h * 0.78)], fill=(150, 110, 70))        # bench
    px = int(w * 0.34)
    d.rectangle([px - 4, int(h * 0.50), px + 4, int(h * 0.86)], fill=(60, 64, 74))
    d.rounded_rectangle([px - int(30 * s), int(h * 0.46), px + int(30 * s), int(h * 0.53)], int(5 * s), fill=(220, 40, 50))
    _text(d, (px - int(26 * s), int(h * 0.455)), "547", font_path, 22 * s, (255, 255, 255))
    lights.append(((px, int(h * 0.50)), int(h * 0.1), (255, 220, 160)))
    stop = (_ANIM.get("signs") or {}).get("stop")
    if stop:   # BTS station board: dark-green Silom-line sign, code badge, Thai + English name
        sgn = _ANIM.get("signs") or {}
        d.rounded_rectangle([sx0, int(h * 0.30), sx1 + int(20 * s), int(h * 0.42)], int(8 * s), fill=(0, 104, 71), outline=(250, 250, 248), width=max(2, int(3 * s)))
        d.rounded_rectangle([sx0 + int(8 * s), int(h * 0.315), sx0 + int(58 * s), int(h * 0.405)], int(6 * s), fill=(250, 250, 248))
        _text(d, (sx0 + int(12 * s), int(h * 0.33)), sgn.get("stop_code", ""), font_path, 22 * s, (0, 104, 71))
        _text(d, (sx0 + int(66 * s), int(h * 0.308)), "สถานี" + stop, font_path, 22 * s, (255, 255, 255))
        if sgn.get("stop_en"):
            _text(d, (sx0 + int(66 * s), int(h * 0.36)), "BTS " + sgn["stop_en"], font_path, 15 * s, (200, 240, 220))
    info.update(ground=ground, cook_x=int(w * 0.5))
    return img, ground, lights, fg, info


def home_front(img, size, mood, rng, s, font_path, night, props=()):
    """The front of a Thai house at night: gate, concrete driveway ramp with a freshly drilled cut, a big rock left on it,
    a dented water pump on the wall dripping, wet ground with puddles, a flashlight beam that sweeps."""
    w, h = size
    d = ImageDraw.Draw(img)
    ground = int(h * 0.88)
    lights, fg, info = [], [], {}
    top, bottom = _sky_colors(mood)
    img.paste(_gradient((w, ground), top, bottom), (0, 0))
    d = ImageDraw.Draw(img)
    wall = (70, 66, 74) if night else (214, 204, 186)
    d.rectangle([int(w * 0.30), int(h * 0.20), w, ground], fill=wall)                                          # house wall
    d.polygon([(int(w * 0.28), int(h * 0.20)), (int(w * 0.65), int(h * 0.06)), (w, int(h * 0.06)), (w, int(h * 0.20))], fill=(96, 56, 52) if night else (176, 96, 80))   # roof
    d.rectangle([int(w * 0.70), int(h * 0.34), int(w * 0.92), int(h * 0.62)], fill=(250, 214, 140) if night else (180, 200, 220))   # lit window
    d.rectangle([int(w * 0.70), int(h * 0.34), int(w * 0.92), int(h * 0.62)], outline=(40, 34, 40), width=max(3, int(4 * s)))
    lights.append(((int(w * 0.81), int(h * 0.48)), int(h * 0.22), (255, 214, 140)))
    d.rectangle([0, int(h * 0.50), int(w * 0.30), ground], fill=(44, 46, 56) if night else (150, 150, 154))      # neighbour's wall / gate
    for k in range(0, int(w * 0.30), int(26 * s)):
        d.line([(k, int(h * 0.50)), (k, ground)], fill=(34, 36, 44) if night else (120, 120, 126), width=3)
    # ground: driveway ramp (concrete) + wet road
    d.rectangle([0, ground, w, h], fill=(52, 54, 62) if night else (130, 128, 124))
    d.polygon([(int(w * 0.30), ground), (int(w * 0.78), ground), (int(w * 0.86), int(h * 0.97)), (int(w * 0.24), int(h * 0.97))], fill=(120, 120, 126) if night else (176, 174, 168))
    d.polygon([(int(w * 0.40), ground + int(8 * s)), (int(w * 0.50), ground + int(8 * s)), (int(w * 0.52), int(h * 0.95)), (int(w * 0.38), int(h * 0.95))], fill=(84, 82, 88))   # drilled cut in the concrete
    # water pump on the wall (dented) with drips
    pxm, pym = int(w * 0.40), int(h * 0.66)
    d.rounded_rectangle([pxm - int(30 * s), pym - int(40 * s), pxm + int(30 * s), pym + int(30 * s)], int(8 * s), fill=(40, 90, 150), outline=(20, 50, 90), width=max(2, int(3 * s)))
    d.ellipse([pxm - int(18 * s), pym - int(12 * s), pxm + int(10 * s), pym + int(14 * s)], fill=(28, 70, 120))                    # the dent
    d.line([(pxm + int(30 * s), pym - int(10 * s)), (pxm + int(48 * s), pym - int(30 * s))], fill=(190, 192, 200), width=max(4, int(6 * s)))   # pipe stub
    ph = _ANIM["phase"]
    for k in range(3):                                                                                       # drips fall and restart
        yy = pym + int(30 * s) + ((ph * 5 + k * 9) % 24) * int(3 * s)
        d.ellipse([pxm + int((-8 + 8 * k) * s) - int(2 * s), yy - int(4 * s), pxm + int((-8 + 8 * k) * s) + int(2 * s), yy + int(4 * s)], fill=(150, 200, 240))
    # puddles with a shimmer
    for k, (fx, fy, fw) in enumerate(((0.34, 0.93, 0.16), (0.58, 0.95, 0.20), (0.18, 0.96, 0.12))):
        shim = 3 * s * math.sin(ph * 1.3 + k)
        d.ellipse([int(w * fx), int(h * fy) + shim, int(w * (fx + fw)), int(h * (fy + 0.035)) + shim], fill=(70, 86, 120) if night else (150, 176, 204))
    # the big rock left by the plumber
    rx, ry_ = int(w * 0.62), int(h * 0.93)
    d.polygon([(rx - int(60 * s), ry_), (rx - int(48 * s), ry_ - int(46 * s)), (rx - int(10 * s), ry_ - int(70 * s)), (rx + int(30 * s), ry_ - int(58 * s)), (rx + int(62 * s), ry_ - int(14 * s)), (rx + int(54 * s), ry_)],
              fill=(110, 108, 112), outline=(60, 58, 62))
    d.polygon([(rx - int(10 * s), ry_ - int(70 * s)), (rx + int(30 * s), ry_ - int(58 * s)), (rx + int(20 * s), ry_ - int(34 * s)), (rx - int(24 * s), ry_ - int(44 * s))], fill=(142, 140, 146))   # lit top face
    # flashlight beam sweeping slowly (mum at the gate)
    bx, by = int(w * 0.74), int(h * 0.74)
    sweep = 0.12 * math.sin(ph * 0.8)
    for reach, a in ((0.45, 0.5), (0.32, 0.9)):
        lights.append(((int(bx - w * reach * (0.7 + sweep)), int(by + h * 0.10)), int(h * 0.14), (255, 244, 200)))
    info.update(ground=ground, cook_x=int(w * 0.5))
    return img, ground, lights, fg, info
