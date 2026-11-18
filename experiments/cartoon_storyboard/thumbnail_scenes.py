"""Settings (backdrops) for thumbnails, drawn with Pillow in the channel's illustrated style.

Each scene is `fn(w, h, time, sky) -> RGB image` with the floor line at 0.82*h (where characters stand) and no text,
so the Thai overlay stays crisp. All sizes are fractions of w/h, so 1280x720 and 3840x2160 exports match.
Generic settings only: no real brands, logos or station names.
"""

from __future__ import annotations

import random

from PIL import Image

import art
from art import INK, Pen, mix

SCENE_NAMES = ("train_station", "office", "bedroom", "street", "studio")
SCENE_HELP = {
    "train_station": "an elevated skytrain/metro platform: station canopy, columns, a train waiting at the edge, "
                     "yellow safety line (use for BTS / MRT / skytrain / station / commute requests)",
    "office": "an office: big window onto the city, desks and monitors (work / career / overtime)",
    "bedroom": "a bedroom: bed, window, a small lamp (loneliness at home / sleepless nights)",
    "street": "a city street: shopfronts both sides, road, street lamps (walking alone / crowds / rain)",
    "studio": "a bright explainer studio: pastel wall with soft shapes, light stage floor, warm spotlight "
              "(use for the bright 'รู้หรือไม่' explainer covers, facts and ideas)",
}


def _lit(time):
    return {"day": (255, 244, 214), "dusk": (255, 214, 150), "night": (255, 226, 150)}[time]


def _dim(c, time):
    return {"day": c, "dusk": mix(c, (120, 80, 110), 0.35), "night": mix(c, (14, 16, 38), 0.72)}[time]


def _floor(pen, w, h, color, line=INK):
    y0 = int(h * 0.82)
    pen.rect(0, y0, w, h, color)
    pen.rect(0, y0 - 4, w, y0 + 4, line)
    return y0


def train_station(w, h, time, sky):
    pen = Pen(w, h, base=sky)
    night = time == "night"
    art.city_skyline(pen, 0, w, int(h * 0.60), _dim((178, 186, 204), time), lit=0.4 if night else 0.1,
                     max_h=int(h * 0.30), seed=11)
    # the opposite track bed and the train waiting there
    pen.rect(0, h * 0.60, w, h * 0.70, _dim((150, 152, 162), time), outline=INK, width=4)
    body = _dim((228, 232, 238), time)
    pen.rect(w * 0.02, h * 0.34, w * 0.98, h * 0.62, body, radius=h * 0.05, outline=INK, width=5)
    pen.rect(w * 0.02, h * 0.505, w * 0.98, h * 0.545, _dim((70, 150, 170), time))
    glass = _lit(time) if night else _dim((196, 224, 244), time)
    for i in range(9):
        x = w * (0.05 + i * 0.1)
        pen.rect(x, h * 0.38, x + w * 0.075, h * 0.49, glass, radius=h * 0.012, outline=INK, width=3)
    pen.rect(w * 0.015, h * 0.60, w * 0.985, h * 0.64, _dim((96, 98, 110), time))
    # platform floor with tile lines and the yellow safety line
    y0 = int(h * 0.82)
    pen.rect(0, h * 0.64, w, h, _dim((206, 202, 196), time))
    pen.rect(0, h * 0.64 - 4, w, h * 0.64 + 4, INK)
    for k in range(1, 12):
        x = w * k / 12
        pen.line([(w / 2 + (x - w / 2) * 0.35, h * 0.66), (x, h)], _dim((178, 174, 170), time), 3)
    pen.rect(0, h * 0.69, w, h * 0.705, (236, 196, 60) if not night else (190, 150, 40))
    # canopy roof, columns and hanging lights
    pen.rect(0, 0, w, h * 0.13, _dim((112, 116, 128), time), outline=INK, width=4)
    for x in (0.06, 0.94):  # edge columns only: a middle one would hide a centred character
        pen.rect(w * x - w * 0.018, h * 0.13, w * x + w * 0.018, h * 0.82, _dim((150, 152, 164), time), outline=INK, width=4)
    for x in (0.22, 0.36, 0.64, 0.78):
        pen.rect(w * x - w * 0.05, h * 0.115, w * x + w * 0.05, h * 0.13, _lit(time))
    pen.rect(w * 0.40, h * 0.145, w * 0.60, h * 0.215, (64, 140, 150), radius=h * 0.014, outline=INK, width=4)  # generic sign board
    pen.circle(w * 0.43, h * 0.18, h * 0.022, (255, 255, 255))
    pen.rect(0, y0, w, h, _dim((196, 190, 184), time))
    pen.rect(0, y0 - 4, w, y0 + 4, INK)
    return pen.result().convert("RGB")


def office(w, h, time, sky):
    pen = Pen(w, h, base=Image.new("RGB", (w, h), _dim((226, 224, 232), time)))
    pen.rect(w * 0.46, h * 0.10, w * 0.96, h * 0.62, _dim((236, 236, 242), time), outline=INK, width=5)
    pen.rect(w * 0.48, h * 0.12, w * 0.94, h * 0.60, (0, 0, 0))                               # window pane
    win = sky.crop((int(w * 0.48), int(h * 0.12), int(w * 0.94), int(h * 0.60)))
    img = pen.result().convert("RGB")
    img.paste(win, (int(w * 0.48), int(h * 0.12)))
    pen = Pen(w, h, base=img)
    art.city_skyline(pen, w * 0.48, w * 0.94, int(h * 0.60), _dim((120, 128, 160), time), lit=0.5 if time == "night" else 0.15,
                     max_h=int(h * 0.22), seed=5)
    pen.line([(w * 0.71, h * 0.12), (w * 0.71, h * 0.60)], INK, 6)
    for x in (0.1, 0.3):                                                                       # ceiling lights
        pen.rect(w * x, h * 0.03, w * (x + 0.14), h * 0.045, _lit(time))
    desk = _dim((176, 140, 104), time)
    pen.rect(0, h * 0.70, w * 0.44, h * 0.74, desk, outline=INK, width=4)
    for x in (0.04, 0.2):                                                                      # monitors
        pen.rect(w * x, h * 0.56, w * (x + 0.12), h * 0.69, (50, 54, 70), radius=h * 0.01, outline=INK, width=4)
        pen.rect(w * (x + 0.008), h * 0.57, w * (x + 0.112), h * 0.68, _lit(time) if time != "day" else (170, 210, 236))
    y0 = _floor(pen, w, h, _dim((150, 150, 164), time))
    return pen.result().convert("RGB")


def bedroom(w, h, time, sky):
    pen = Pen(w, h, base=Image.new("RGB", (w, h), _dim((236, 214, 192), time)))
    pen.rect(w * 0.06, h * 0.12, w * 0.34, h * 0.58, _dim((250, 246, 240), time), outline=INK, width=5)
    img = pen.result().convert("RGB")
    img.paste(sky.crop((int(w * 0.07), int(h * 0.14), int(w * 0.33), int(h * 0.56))), (int(w * 0.07), int(h * 0.14)))
    pen = Pen(w, h, base=img)
    pen.line([(w * 0.2, h * 0.12), (w * 0.2, h * 0.58)], INK, 5)
    for x0, x1 in ((0.02, 0.10), (0.30, 0.38)):                                                # curtains
        pen.rect(w * x0, h * 0.09, w * x1, h * 0.64, _dim((196, 120, 120), time), outline=INK, width=4)
    y0 = _floor(pen, w, h, _dim((176, 132, 100), time))
    bed = _dim((120, 140, 190), time)
    pen.rect(w * 0.56, h * 0.58, w * 0.98, h * 0.84, _dim((140, 100, 80), time), radius=h * 0.02, outline=INK, width=5)
    pen.rect(w * 0.58, h * 0.52, w * 0.98, h * 0.72, bed, radius=h * 0.03, outline=INK, width=5)
    pen.rect(w * 0.60, h * 0.47, w * 0.72, h * 0.56, (250, 248, 244), radius=h * 0.03, outline=INK, width=4)
    pen.rect(w * 0.45, h * 0.62, w * 0.50, h * 0.82, _dim((150, 110, 84), time), outline=INK, width=4)    # night stand
    pen.rect(w * 0.455, h * 0.52, w * 0.495, h * 0.62, (250, 214, 130), radius=h * 0.012, outline=INK, width=4)  # lamp
    return art.add_glow(pen.result().convert("RGB"), int(w * 0.475), int(h * 0.55), int(h * 0.3), _lit(time),
                        0.55 if time != "day" else 0.15)


def street(w, h, time, sky):
    pen = Pen(w, h, base=sky)
    rnd = random.Random(21)
    cols = [(236, 208, 168), (214, 184, 190), (190, 206, 190), (232, 218, 160), (178, 190, 214)]
    x = -20
    while x < w:
        bw = rnd.uniform(0.09, 0.14) * w
        top = rnd.uniform(0.18, 0.40) * h
        pen.rect(x, top, x + bw, h * 0.82, _dim(rnd.choice(cols), time), outline=INK, width=4)
        for wy in range(int(top + h * 0.05), int(h * 0.70), int(h * 0.09)):
            for wx in range(int(x + bw * 0.12), int(x + bw * 0.8), int(w * 0.035)):
                pen.rect(wx, wy, wx + w * 0.022, wy + h * 0.05, _lit(time) if time == "night" and rnd.random() < 0.6
                         else _dim((170, 200, 226), time))
        x += bw + w * 0.004
    y0 = _floor(pen, w, h, _dim((120, 122, 134), time))
    for k in range(0, 8):                                                                      # road dashes
        pen.rect(w * (0.05 + k * 0.13), h * 0.93, w * (0.05 + k * 0.13 + 0.07), h * 0.945, (240, 232, 200))
    for lx in (0.2, 0.8):                                                                      # street lamps
        pen.rect(w * lx - 6, h * 0.30, w * lx + 6, y0, (70, 72, 84))
        pen.circle(w * lx, h * 0.29, h * 0.03, _lit(time))
    img = pen.result().convert("RGB")
    if time != "day":
        for lx in (0.2, 0.8):
            img = art.add_glow(img, int(w * lx), int(h * 0.29), int(h * 0.22), _lit(time), 0.5)
    return img


def studio(w, h, time, sky):
    """Bright explainer set (the look of the 'รู้หรือไม่' series), ignores the time of day on purpose."""
    rnd = random.Random(3)
    pen = Pen(w, h, base=art.vgradient(w, h, [(0, (252, 236, 214)), (0.66, (246, 222, 200)), (1, (232, 204, 182))]))
    for _ in range(14):
        pen.circle(rnd.uniform(0, w), rnd.uniform(0, h * 0.6), rnd.uniform(h * 0.04, h * 0.12),
                   rnd.choice([(250, 214, 190), (232, 228, 206), (214, 230, 226), (246, 206, 214)]))
    floor = h * 0.82
    pen.rect(0, floor, w, h, (240, 210, 180))
    pen.line([(0, floor), (w, floor)], INK, 4)
    img = art.add_glow(pen.result().convert("RGB"), int(w * 0.5), int(h * 0.3), int(h * 0.55), (255, 246, 224), 0.35)
    return img


SCENES = {"train_station": train_station, "office": office, "bedroom": bedroom, "street": street, "studio": studio}


def scene_image(name: str, w: int, h: int, time: str, sky: Image.Image) -> Image.Image:
    return SCENES[name](w, h, time, sky)
