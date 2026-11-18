"""Prototype v2: two hand-composed cover options for 'know_craving' (no API call), each with a 320 px preview.
Separate from cartoon_storyboard/covers.py, so the Life Lesson cover rules are untouched.

    python covers_proto.py   -> out/cover_A.jpg, out/cover_B.jpg, out/covers_preview.png
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "shorts"))

import rig  # noqa: E402
import props_story  # noqa: E402
import character_soft as CS  # noqa: E402
from art import Pen, add_glow, vgradient  # noqa: E402
from subtitles import font  # noqa: E402

W, H = 1920, 1080
OUT = HERE / "out"
INK = (118, 88, 72)


def title(img, text, x, y, size, fill, stroke=(70, 40, 30)):
    """Big Thai title straight on the picture: thick warm outline + soft drop shadow, no box behind it."""
    f = font(size)
    shadow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(shadow).text((x + 8, y + 10), text, font=f, fill=(40, 20, 10, 150), stroke_width=int(size * 0.09),
                                stroke_fill=(40, 20, 10, 150))
    img.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(8)))
    ImageDraw.Draw(img).text((x, y), text, font=f, fill=fill, stroke_width=int(size * 0.09), stroke_fill=stroke)


def thought_cloud(img, cx, cy, rx, ry):
    """An organic thought bubble (overlapping soft lobes) with two trailing dots, not a rectangle."""
    pen = Pen(W, H, ss=2)
    import math
    lobes = [(cx + rx * 0.78 * math.cos(a), cy + ry * 0.7 * math.sin(a)) for a in [i * math.pi / 4 for i in range(8)]]
    for x, y in lobes:
        pen.ellipse(x, y, rx * 0.42 + 6, ry * 0.46 + 6, INK)
    pen.ellipse(cx, cy, rx * 0.86 + 6, ry * 0.76 + 6, INK)
    for x, y in lobes:
        pen.ellipse(x, y, rx * 0.42, ry * 0.46, (255, 252, 244))
    pen.ellipse(cx, cy, rx * 0.86, ry * 0.76, (255, 252, 244))
    for (x, y, r) in ((cx + rx * 0.95, cy + ry * 1.05, 26), (cx + rx * 1.18, cy + ry * 1.32, 16)):
        pen.circle(x, y, r + 5, INK)
        pen.circle(x, y, r, (255, 252, 244))
    lay = pen.result()
    img.alpha_composite(lay)


def paste_sprite(img, spr, x, y, scale=1.0):
    if scale != 1.0:
        spr = spr.resize((int(spr.width * scale), int(spr.height * scale)), Image.LANCZOS)
    img.alpha_composite(spr, (int(x - spr.width / 2), int(y - spr.height / 2)))


def cover_a():
    """'แม่ท้องอยากกินอะไร?': a big, eager pregnant mum hugging her bowl; the other cravings float in her thoughts."""
    img = vgradient(W, H, [(0, (255, 214, 120)), (0.6, (252, 176, 96)), (1, (236, 132, 84))]).convert("RGBA")
    img = add_glow(img.convert("RGB"), int(W * 0.72), int(H * 0.45), int(H * 0.8), (255, 240, 200), 0.55).convert("RGBA")
    mom = rig.sprite("mom", "pregnant", "hold_chest", "eager", None, False, None, "salad_bowl", 1900)
    head_y = 258 / 900 * mom.height                     # head centre inside the sprite canvas
    img.alpha_composite(mom, (int(W * 0.72 - mom.width / 2), int(H * 0.36 - head_y)))
    thought_cloud(img, W * 0.30, H * 0.64, 330, 230)
    for name, x, y, k in (("durian", 0.20, 0.60, 1.25), ("shabu", 0.34, 0.70, 1.2), ("oliang", 0.40, 0.52, 1.1)):
        paste_sprite(img, props_story.sprite(name, H), W * x, H * y, k)
    title(img, "แม่ท้อง", 70, 40, 150, (255, 255, 255))
    title(img, "อยากกินอะไร?", 70, 205, 150, (255, 236, 120))
    return img.convert("RGB")


def cover_b():
    """'ลูกมาจากไหน?': ปิ่น's startled close-up against a glowing old manuscript; three craving icons rise from it."""
    img = vgradient(W, H, [(0, (40, 72, 108)), (1, (24, 44, 70))]).convert("RGB")
    img = add_glow(img, int(W * 0.30), int(H * 0.62), int(H * 0.55), (255, 214, 140), 0.75).convert("RGBA")
    book = props_story.sprite("manuscript", H)
    paste_sprite(img, book, W * 0.30, H * 0.74, 2.6)
    for name, x, y in (("honey", 0.17, 0.42), ("fruit", 0.30, 0.34), ("fish", 0.43, 0.42)):
        paste_sprite(img, props_story.sprite(name, H), W * x, H * y, 1.05)
    pin = rig.sprite("host_mint", "default", "relaxed", "surprised", None, False, None, None, 2500)
    head_y = 258 / 900 * pin.height
    img.alpha_composite(pin, (int(W * 0.75 - pin.width / 2), int(H * 0.50 - head_y)))
    title(img, "ลูกมาจากไหน?", 60, 40, 158, (255, 226, 110), stroke=(20, 30, 50))
    return img.convert("RGB")


def main():
    OUT.mkdir(exist_ok=True)
    covers = {"A": cover_a(), "B": cover_b()}
    for k, im in covers.items():
        im.save(OUT / f"cover_{k}.jpg", quality=92)
    # review sheet: each full cover beside its 320 px mobile-size preview (shown at actual pixels)
    sheet = Image.new("RGB", (960 + 40 + 320 + 40, 2 * 540 + 60), (236, 236, 236))
    d = ImageDraw.Draw(sheet)
    for i, (k, im) in enumerate(covers.items()):
        y = 20 + i * 560
        sheet.paste(im.resize((960, 540), Image.LANCZOS), (20, y))
        small = im.resize((320, 180), Image.LANCZOS)
        sheet.paste(small, (1000, y + 180))
        d.text((1000, y + 150), f"{k}: 320 px", font=font(26, False), fill=(60, 60, 60))
    sheet.save(OUT / "covers_preview.png")
    print("ok")


if __name__ == "__main__":
    main()
