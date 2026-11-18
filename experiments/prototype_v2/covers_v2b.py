"""Prototype v2b stage 3: the two know_craving covers redrawn with the stage-1 characters (no API call).

    python covers_v2b.py -> out/cover_A_v2b.jpg, out/cover_B_v2b.jpg, out/covers_preview_v2b.png

A: the pregnant belly and the bowl are fully inside the frame (3/4 view, so the bump reads in silhouette).
B: brighter sky palette; ปิ่น's whole head sits inside the frame, the crop falls at the chest on purpose.
The review sheet shows each new cover at full size and 320 px next to the previous version at 320 px.
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "shorts"))

from covers_proto import paste_sprite, thought_cloud, title  # noqa: E402  (also puts the shared toolkit on sys.path)
import props_story  # noqa: E402
from art import add_glow, vgradient  # noqa: E402
from cast import D2R  # noqa: E402
from figure import figure  # noqa: E402
from subtitles import font  # noqa: E402
from toon import Canvas  # noqa: E402

W, H = 1920, 1080
OUT = HERE / "out"


def _figure_layer(cid, x, y, k, th, pose, expr, pregnant=False, flip=False):
    cv = Canvas(W, H, ss=2)
    cv.push(x, y, scale=k, flip=flip)
    figure(cv, cid, th, pose, expr, pregnant=pregnant, shadow=False)
    cv.pop()
    return cv.result()


def cover_a():
    img = vgradient(W, H, [(0, (255, 218, 130)), (0.6, (252, 182, 104)), (1, (240, 140, 92))]).convert("RGB")
    img = add_glow(img, int(W * 0.72), int(H * 0.5), int(H * 0.75), (255, 240, 204), 0.55).convert("RGBA")
    thought_cloud(img, W * 0.29, H * 0.66, 320, 220)
    for name, x, y, k in (("durian", 0.19, 0.62, 1.2), ("shabu", 0.33, 0.72, 1.15), ("oliang", 0.39, 0.53, 1.05)):
        paste_sprite(img, props_story.sprite(name, H), W * x, H * y, k)
    # head-to-hem: the bump (y ~ 214) and the bowl (y ~ 154) land well inside the frame; only the shins are cropped
    img.alpha_composite(_figure_layer("mom", 1390, 318, 2.55, 45 * D2R, "hold_high", "eager", pregnant=True, flip=True))
    title(img, "แม่ท้อง", 70, 40, 150, (255, 255, 255))
    title(img, "อยากกินอะไร?", 70, 205, 150, (255, 236, 120))
    return img.convert("RGB")


def cover_b():
    img = vgradient(W, H, [(0, (126, 200, 240)), (0.55, (176, 222, 240)), (1, (255, 214, 170))]).convert("RGB")
    img = add_glow(img, int(W * 0.30), int(H * 0.66), int(H * 0.5), (255, 236, 170), 0.8).convert("RGBA")
    paste_sprite(img, props_story.sprite("manuscript", H), W * 0.30, H * 0.75, 2.5)
    for name, x, y in (("honey", 0.16, 0.44), ("fruit", 0.30, 0.37), ("fish", 0.44, 0.44)):
        paste_sprite(img, props_story.sprite(name, H), W * x, H * y, 1.1)
    # head centre at y=470 with a 2.9x figure: crown ~120 px from the top, crop below the shoulders
    img.alpha_composite(_figure_layer("pin", 1440, 470, 2.9, 25 * D2R, "rest", "surprised", flip=True))
    title(img, "ลูกมาจากไหน?", 60, 30, 158, (255, 236, 120), stroke=(40, 60, 96))
    return img.convert("RGB")


def main():
    covers = {"A": cover_a(), "B": cover_b()}
    for k, im in covers.items():
        im.save(OUT / f"cover_{k}_v2b.jpg", quality=92)
    old = {k: Image.open(OUT / f"cover_{k}.jpg") for k in covers}
    sheet = Image.new("RGB", (960 + 40 + 320 + 40 + 320 + 40, 2 * 540 + 60), (236, 236, 236))
    d = ImageDraw.Draw(sheet)
    for i, (k, im) in enumerate(covers.items()):
        y = 20 + i * 560
        sheet.paste(im.resize((960, 540), Image.LANCZOS), (20, y))
        sheet.paste(im.resize((320, 180), Image.LANCZOS), (1000, y + 180))
        sheet.paste(old[k].resize((320, 180), Image.LANCZOS), (1360, y + 180))
        d.text((1000, y + 150), f"{k} v2b: 320 px", font=font(26, False), fill=(60, 60, 60))
        d.text((1360, y + 150), f"{k} old: 320 px", font=font(26, False), fill=(120, 120, 120))
    sheet.save(OUT / "covers_preview_v2b.png")
    print("ok")


if __name__ == "__main__":
    main()
