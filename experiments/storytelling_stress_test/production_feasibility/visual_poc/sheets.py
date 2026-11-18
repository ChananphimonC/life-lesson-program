"""Labelled storyboard sheets (shot id + seconds) for both scenes -> scene_*/storyboard_sheet.png"""
from PIL import Image, ImageDraw, ImageFont

import scene_a
import scene_b


def sheet(shots, frames_dir, out, cols=2):
    tw, th = 640, 360
    f = ImageFont.load_default(20)
    rows = (len(shots) + cols - 1) // cols
    im = Image.new("RGB", (cols * (tw + 10) + 10, rows * (th + 10) + 10), (28, 28, 30))
    d = ImageDraw.Draw(im)
    t = 0.0
    for i, (name, _, dur, _) in enumerate(shots):
        x, y = 10 + (i % cols) * (tw + 10), 10 + (i // cols) * (th + 10)
        im.paste(Image.open(frames_dir / f"{name}.png").convert("RGB").resize((tw, th), Image.LANCZOS), (x, y))
        d.rectangle([x, y, x + 190, y + 28], fill=(0, 0, 0))
        d.text((x + 6, y + 3), f"{name}  {t:4.1f}-{t + dur:4.1f}s", fill=(255, 255, 255), font=f)
        t += dur
    im.save(out)


sheet(scene_a.SHOTS, scene_a.OUT, scene_a.OUT.parent / "storyboard_sheet.png")
sheet(scene_b.SHOTS, scene_b.OUT, scene_b.OUT.parent / "storyboard_sheet.png")
print("ok")
