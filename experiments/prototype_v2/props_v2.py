"""Prototype v2 props and sets: objects characters hold (gripped between arm and fingers), a hotpot table seen from the
side, a ladle close-up, a case folder, and a warm hotpot-restaurant set. All curves are smoothed; no labels or boxes.
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "shorts"))
import character_art as CA  # noqa: E402,F401
import character_soft as CS  # noqa: E402
from art import Pen, add_glow, vgradient  # noqa: E402
from character_art import INK, shade  # noqa: E402

shape = CS._shape


# --- things held in two hands (drawn in body coordinates, centred between the wrists) ---------------------------------

def held_durian_plate(pen, c):
    x, y = c
    shape(pen, [(x - 64, y + 4), (x + 64, y + 4), (x + 54, y + 22), (x - 54, y + 22)], (250, 250, 248), 3.2, 3, 0.25)  # plate
    for dx, dy in ((-30, -8), (0, -14), (30, -8)):
        shape(pen, [(x + dx - 18, y + dy + 4), (x + dx - 10, y + dy - 12), (x + dx + 10, y + dy - 14), (x + dx + 18, y + dy + 2),
                    (x + dx + 8, y + dy + 10), (x + dx - 10, y + dy + 10)], (246, 204, 92), 3.0, 3, 0.3)          # golden pods
        pen.line(CS.CA._spline([(x + dx - 8, y + dy - 4), (x + dx, y + dy - 8), (x + dx + 8, y + dy - 4)]), (255, 236, 170), 3)


def held_salad_bowl(pen, c):
    x, y = c
    rnd = random.Random(4)
    for _ in range(11):                                                    # fruit pieces piled above the rim
        px, py = x + rnd.uniform(-44, 44), y - 14 + rnd.uniform(-14, 8)
        col = rnd.choice([(170, 210, 96), (236, 98, 84), (250, 224, 120), (200, 230, 140)])
        shape(pen, [(px - 10, py - 5), (px + 10, py - 6), (px + 11, py + 5), (px - 9, py + 6)], col, 2.4, 2, 0.3)
    for px, py in ((x - 20, y - 22), (x + 14, y - 26), (x + 34, y - 14)):
        pen.circle(px, py, 3, (214, 60, 50))
    shape(pen, [(x - 62, y - 8), (x + 62, y - 8), (x + 50, y + 26), (x + 24, y + 40), (x - 24, y + 40), (x - 50, y + 26)],
          (250, 244, 228), 3.4, 3, 0.25)
    pen.line(CS.CA._spline([(x - 54, y + 4), (x, y + 12), (x + 54, y + 4)]), (226, 160, 120), 3)


HELD = {"durian_plate": held_durian_plate, "salad_bowl": held_salad_bowl}


# --- set pieces in screen coordinates ------------------------------------------------------------------------------------

def restaurant(W, H):
    """A warm hotpot restaurant (generic, no brand): wooden slat wall, round paper lamps, a counter with bowls."""
    pen = Pen(W, H, base=vgradient(W, H, [(0, (196, 120, 84)), (0.55, (222, 160, 112)), (1, (176, 112, 80))]))
    for k in range(0, W, int(W * 0.035)):
        pen.line([(k, 0), (k, H * 0.62)], (184, 112, 78), 4)
    pen.rect(0, H * 0.60, W, H * 0.66, (150, 90, 62))
    for x in (0.18, 0.5, 0.82):
        pen.line([(W * x, 0), (W * x, H * 0.14)], (90, 60, 50), 3)
        pen.ellipse(W * x, H * 0.19, H * 0.07, H * 0.06, (255, 214, 140), outline=INK, width=3)
    for k in range(9):
        cx = W * (0.08 + k * 0.105)
        pen.ellipse(cx, H * 0.585, W * 0.03, H * 0.022, (240, 236, 226), outline=INK, width=2)
    pen.rect(0, H * 0.66, W, H, (120, 78, 60))
    img = pen.result().convert("RGB")
    for x in (0.18, 0.5, 0.82):
        img = add_glow(img, int(W * x), int(H * 0.19), int(H * 0.25), (255, 220, 150), 0.35)
    return img


def table_front(img, W, H, y_top, color=(150, 96, 64)):
    """A table edge in the foreground that hides the characters below the waist (they are 'at' the table)."""
    pen = Pen(W, H, ss=2)
    pen.rect(-20, y_top, W + 20, H + 20, color, outline=INK, width=4, radius=18)
    pen.rect(-20, y_top, W + 20, y_top + H * 0.035, shade(color, 1.18), outline=INK, width=4, radius=12)
    lay = pen.result()
    img.paste(lay, (0, 0), lay)


def hotpot(img, cx, cy, s, t, liver_up=0.0):
    """A steel hotpot on a burner seen from the side, bubbling broth and steam; optional ladle lifting a liver slice."""
    pen = Pen(img.width, img.height, ss=2)
    w, h = 150 * s, 74 * s
    pen.rect(cx - w * 0.62, cy + h * 0.45, cx + w * 0.62, cy + h * 0.75, (70, 70, 80), outline=INK, width=4, radius=10)  # burner
    shape(pen, [(cx - w, cy - h * 0.25), (cx + w, cy - h * 0.25), (cx + w * 0.92, cy + h * 0.5), (cx - w * 0.92, cy + h * 0.5)],
          (196, 202, 212), 4.0, 2, 0.12)
    pen.ellipse(cx, cy - h * 0.25, w, h * 0.32, (210, 216, 226), outline=INK, width=4)
    pen.ellipse(cx, cy - h * 0.25, w * 0.9, h * 0.26, (236, 132, 84))                                       # broth
    for k in range(7):                                                                                        # bubbles
        a = (t * 2.3 + k * 0.9) % 1.0
        bx = cx + (k - 3) * w * 0.24
        pen.circle(bx, cy - h * 0.25 - a * 6 * s, (3 + 4 * a) * s, (250, 190, 140))
    for x, col in ((-0.45, (110, 180, 100)), (0.38, (240, 236, 226)), (0.05, (120, 60, 56))):
        pen.ellipse(cx + w * x, cy - h * 0.28, 20 * s, 7 * s, col)
    pen.rect(cx - w * 1.12, cy - h * 0.12, cx - w * 0.98, cy + h * 0.06, (90, 92, 104), radius=4)              # handles
    pen.rect(cx + w * 0.98, cy - h * 0.12, cx + w * 1.12, cy + h * 0.06, (90, 92, 104), radius=4)
    if liver_up > 0:                                                                                          # ladle with a cooked slice
        lx, ly = cx + w * 0.25, cy - h * 0.3 - liver_up * 110 * s
        pen.line([(lx, ly), (lx + 150 * s, ly - 160 * s)], (170, 172, 184), 9 * s)
        shape(pen, [(lx - 44 * s, ly - 6 * s), (lx + 44 * s, ly - 6 * s), (lx + 36 * s, ly + 16 * s), (lx - 36 * s, ly + 16 * s)],
              (186, 190, 200), 3.4, 3, 0.25)
        shape(pen, [(lx - 30 * s, ly - 10 * s), (lx + 28 * s, ly - 14 * s), (lx + 32 * s, ly - 2 * s), (lx - 26 * s, ly + 2 * s)],
              (124, 74, 70), 3.0, 3, 0.3)                                                                    # cooked (brown-grey) liver
    lay = pen.result()
    img.paste(lay, (0, 0), lay)
    steam(img, cx, cy - h * 0.4, s, t)


def steam(img, cx, cy, s, t, n=6):
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for k in range(n):
        u = (t * 0.35 + k / n) % 1.0
        r = (14 + 30 * u) * s
        px = cx + math.sin(t * 1.7 + k * 1.9) * 26 * s + (k - n / 2) * 18 * s
        py = cy - u * 220 * s
        a = int(150 * math.sin(math.pi * u))
        d.ellipse((px - r, py - r, px + r, py + r), fill=(255, 255, 255, a))
    layer = layer.filter(ImageFilter.GaussianBlur(6 * s))
    img.paste(layer, (0, 0), layer)


def liver_plate(img, cx, cy, s):
    pen = Pen(img.width, img.height, ss=2)
    pen.ellipse(cx, cy, 120 * s, 30 * s, (250, 250, 250), outline=INK, width=4)
    for dx in (-60, -20, 20, 60):
        shape(pen, [(cx + dx * s - 26 * s, cy - 6 * s), (cx + dx * s + 22 * s, cy - 12 * s), (cx + dx * s + 26 * s, cy + 2 * s),
                    (cx + dx * s - 20 * s, cy + 6 * s)], (124, 52, 54), 2.8, 3, 0.3)                          # raw liver slices
    lay = pen.result()
    img.paste(lay, (0, 0), lay)


def case_folder(img, cx, cy, s, open_u=0.0):
    """A manila case folder on the floor, tied with red string; opens a little as the case starts."""
    pen = Pen(img.width, img.height, ss=2)
    w, h = 220 * s, 150 * s
    shape(pen, [(cx - w, cy - h * 0.3), (cx + w, cy - h * 0.3), (cx + w * 1.06, cy + h * 0.5), (cx - w * 1.06, cy + h * 0.5)],
          (226, 184, 116), 4.0, 2, 0.1)
    lift = open_u * 60 * s
    shape(pen, [(cx - w, cy - h * 0.3 - lift), (cx + w * 0.2, cy - h * 0.34 - lift * 1.3), (cx + w * 0.26, cy + h * 0.05 - lift),
                (cx - w * 1.02, cy + h * 0.1 - lift * 0.6)], (240, 204, 140), 3.6, 2, 0.12)
    for k in range(4):
        pen.line([(cx + w * 0.3, cy - h * 0.1 + k * 18 * s), (cx + w * 0.86, cy - h * 0.12 + k * 18 * s)], (190, 150, 100), 3)
    pen.line(CS.CA._spline([(cx - w * 0.1, cy + h * 0.1), (cx + w * 0.05, cy + h * 0.32), (cx + w * 0.3, cy + h * 0.24)]), (210, 60, 60), 5)
    pen.circle(cx + w * 0.62, cy + h * 0.2, 46 * s, None, outline=(90, 80, 80), width=9)                       # magnifier
    pen.circle(cx + w * 0.62, cy + h * 0.2, 40 * s, (226, 240, 250))
    pen.line([(cx + w * 0.62 + 30 * s, cy + h * 0.2 + 30 * s), (cx + w * 0.62 + 80 * s, cy + h * 0.2 + 80 * s)], (120, 80, 60), 16 * s)
    lay = pen.result()
    img.paste(lay, (0, 0), lay)
