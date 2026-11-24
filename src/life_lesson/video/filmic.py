"""Optional "filmic" look for the flat illustrations (VISUAL_LOOK=filmic): fine surface texture, soft bloom around lights,
an S-curve with warm highlights and cool shadows. Pure Pillow. Highlights are compressed (soft knee) so whites never burn out."""

from __future__ import annotations

from PIL import Image, ImageChops, ImageFilter


def _knee(v: int) -> int:
    return v if v < 205 else int(205 + (v - 205) * 0.45)


def _curve(v: int) -> int:
    t = v / 255
    return int(255 * (t * 0.55 + (t * t * (3 - 2 * t)) * 0.45))


def filmic(img: Image.Image) -> Image.Image:
    rgb = img.convert("RGB")
    w, h = rgb.size
    # 1) surface texture: multi-scale noise nudges brightness (concrete, brushed metal, skin) at low amplitude
    tex = Image.new("L", (w, h), 128)
    for scale, amp in ((2, 0.05), (6, 0.035), (24, 0.03)):
        n = Image.effect_noise((max(2, w // scale), max(2, h // scale)), 40).resize((w, h), Image.BICUBIC)
        n = n.point(lambda v, a=amp: int(128 + (v - 128) * a))
        tex = ImageChops.add(tex, n, 1.0, -128)
    tex_rgb = Image.merge("RGB", (tex, tex, tex))
    out = ImageChops.add(rgb, tex_rgb, 1.0, -128)
    # 2) bloom: only genuinely bright areas glow, kept modest
    lum = out.convert("L").point(lambda v: max(0, v - 200) * 3)
    glow = lum.filter(ImageFilter.GaussianBlur(max(6, h // 55)))
    glow_rgb = ImageChops.multiply(out, Image.merge("RGB", (glow, glow, glow))).point(lambda v: int(v * 0.55))
    out = ImageChops.screen(out, glow_rgb)
    # 3) tone: soft highlight knee + gentle S-curve, then split-tone (warm highlights, cool shadows)
    out = out.point(_knee).point(_curve)
    r, g, b = out.split()
    r = r.point(lambda v: min(255, v + int(8 * v / 255) - int(3 * (255 - v) / 255)))
    b = b.point(lambda v: min(255, max(0, v - int(6 * v / 255) + int(7 * (255 - v) / 255))))
    return Image.merge("RGB", (r, g, b))
