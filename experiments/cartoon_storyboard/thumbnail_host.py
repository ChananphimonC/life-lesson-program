"""Cover art for the bright "รู้หรือไม่" explainer series: the host (น้องปิ่น) and her five dogs in the studio next to graphics that
name the topic. Drawn with the shorts toolkit so the host looks exactly like she does in the video; the Thai/Latin
cover text is composed on top by covers.render, like every other cover.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

from PIL import Image, ImageDraw

SHORTS = Path(__file__).resolve().parent.parent / "shorts"
sys.path.insert(0, str(SHORTS))

import art  # noqa: E402
import character_art as CA  # noqa: E402
import props_knowledge as PK  # noqa: E402
from art import INK, Pen  # noqa: E402
from subtitles import font  # noqa: E402

HOST = "host_mint"  # id kept (scripts and voice cache use it); she is น้องปิ่น
DOGS = ["pom_brown", "pom_white", "chi_bw", "chi_latte", "chi_nescafe"]
MBTI_CODES = ["ENFP", "INTJ", "ISFP", "ESTJ", "INFJ", "ENTP"]


def _studio(w, h, accent):
    rnd = random.Random(5)
    pen = Pen(w, h, base=art.vgradient(w, h, [(0, (255, 240, 214)), (0.7, (252, 226, 196)), (1, (240, 208, 176))]))
    for _ in range(18):
        pen.circle(rnd.uniform(0, w), rnd.uniform(0, h * 0.8), rnd.uniform(h * 0.05, h * 0.16),
                   rnd.choice([(255, 214, 190), (236, 234, 206), (206, 232, 228), (250, 204, 216), accent]))
    floor = h * 0.86
    pen.rect(0, floor, w, h, (244, 214, 184))
    pen.line([(0, floor), (w, floor)], INK, 4)
    return art.add_glow(pen.result().convert("RGB"), int(w * 0.7), int(h * 0.4), int(h * 0.7), (255, 248, 230), 0.45)


def _host(h):
    spr = CA.sprite(HOST, "present", 1, 1, False, 1.0)
    spr = spr.crop(spr.getchannel("A").getbbox())
    k = h * 0.80 / spr.height
    return spr.resize((int(spr.width * k), int(spr.height * k)), Image.LANCZOS)


def _tiles(canvas, w, h, title):
    """The topic graphic on the left: MBTI type tiles, or a big question bubble for any other topic."""
    if "MBTI" in title.upper():
        big = 2.3
        for i, code in enumerate(MBTI_CODES):
            t = PK.type_tile(code, h)
            t = t.resize((int(t.width * big), int(t.height * big)), Image.LANCZOS).rotate(
                (-6, 4, -3, 5, -4, 3)[i], expand=True, resample=Image.BICUBIC)
            canvas.paste(t, (int(w * 0.05 + (i % 2) * w * 0.20 + (i // 2) * w * 0.01),
                             int(h * 0.36 + (i // 2) * h * 0.18)), t)
        return
    bubble = PK.icon("chat", "", h)
    bubble = bubble.resize((int(h * 0.7), int(h * 0.7)), Image.LANCZOS)
    ImageDraw.Draw(bubble).text((bubble.width * 0.5, bubble.height * 0.44), "?", font=font(int(h * 0.3)),
                                fill=(255, 150, 80), anchor="mm", stroke_width=6, stroke_fill=INK)
    canvas.paste(bubble, (int(w * 0.12), int(h * 0.34)), bubble)


def _sprite(char, outfit, frac, h):
    spr = CA.sprite(char, outfit, 1, 1, False, 1.0)
    spr = spr.crop(spr.getchannel("A").getbbox())
    k = h * frac / spr.height
    return spr.resize((int(spr.width * k), int(spr.height * k)), Image.LANCZOS)


def render_jobbers(w: int, h: int, accent: tuple[int, int, int]) -> Image.Image:
    """Comparison episode without the host: the two first-jobbers either side of the two salary tiles."""
    canvas = _studio(w, h, accent).convert("RGBA")
    pair = PK.pair_sprite("28K", "BTS", "40K", "MRT", 2, h, 1)
    pair = pair.resize((int(pair.width * 1.3), int(pair.height * 1.3)), Image.LANCZOS)
    canvas.alpha_composite(pair, (int(w * 0.5 - pair.width / 2), int(h * 0.36)))
    for char, outfit, x in (("jobber_ton", "default", 0.14), ("jobber_fah", "default", 0.86)):
        spr = _sprite(char, outfit, 0.74, h)
        canvas.alpha_composite(spr, (int(w * x - spr.width / 2), int(h * 0.97 - spr.height)))
    return canvas.convert("RGB")


def render_craving(w: int, h: int, accent: tuple[int, int, int]) -> Image.Image:
    """Pregnancy-cravings episode: the host and the pregnant mum with the foods from the story floating between them."""
    import props_story as PS
    canvas = _studio(w, h, accent).convert("RGBA")
    spots = (("durian", 0.36, 0.40), ("shabu", 0.50, 0.50), ("salad", 0.64, 0.40), ("oliang", 0.50, 0.30))
    for name, x, y in spots:
        spr = PS.sprite(name, h)
        spr = spr.resize((int(spr.width * 1.7), int(spr.height * 1.7)), Image.LANCZOS)
        canvas.alpha_composite(spr, (int(w * x - spr.width / 2), int(h * y)))
    for char, outfit, x in (("host_mint", "present", 0.15), ("mom", "pregnant", 0.85)):
        spr = _sprite(char, outfit, 0.78, h)
        canvas.alpha_composite(spr, (int(w * x - spr.width / 2), int(h * 0.97 - spr.height)))
    return canvas.convert("RGB")


def render(w: int, h: int, title: str, accent: tuple[int, int, int], kind: str = "host") -> Image.Image:
    if kind == "jobbers":
        return render_jobbers(w, h, accent)
    if kind == "craving":
        return render_craving(w, h, accent)
    canvas = _studio(w, h, accent).convert("RGBA")
    _tiles(canvas, w, h, title)
    host = _host(h)
    canvas.alpha_composite(host, (int(w * 0.80 - host.width / 2), int(h * 0.97 - host.height)))
    for i, dog in enumerate(DOGS):  # her five dogs sit around her feet
        spr = CA.sprite(dog, "default", 1, 0, False, 1.0)
        spr = spr.crop(spr.getchannel("A").getbbox())
        k = h * 0.17 / spr.height
        spr = spr.resize((int(spr.width * k), int(spr.height * k)), Image.LANCZOS)
        canvas.alpha_composite(spr, (int(w * (0.61 + i * 0.055) - spr.width / 2 + (i % 2) * 8),
                                     int(h * (0.97 - 0.02 * (i % 2)) - spr.height)))
    return canvas.convert("RGB")
