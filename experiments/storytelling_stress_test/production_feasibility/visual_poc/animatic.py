"""Animatic = the key frames with camera moves (push-in / pan / shake) at 24 fps. This is NOT character animation: the
characters in each frame are static poses; only the virtual camera moves. Silent. Output: one MP4 per scene.

    python animatic.py            -> scene_a_paper_roll/scene_a_animatic.mp4, scene_b_bowls/scene_b_animatic.mp4
"""
from __future__ import annotations

import math
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw

import scene_a
import scene_b

HERE = Path(__file__).resolve().parent
W, H, FPS = 1280, 720, 24

# shot -> (zoom0, zoom1, centre0 (fx, fy), centre1, shake px)   centre = fraction of the frame kept in the middle of the crop
CAM = {
    "A01": (1.00, 1.18, (0.50, 0.5), (0.62, 0.45), 0), "A02": (1.00, 1.25, (0.5, 0.5), (0.5, 0.40), 0),
    "A03": (1.15, 1.00, (0.40, 0.5), (0.5, 0.5), 0), "A04": (1.00, 1.14, (0.5, 0.5), (0.5, 0.58), 0),
    "A05": (1.00, 1.12, (0.5, 0.5), (0.5, 0.45), 3), "A06": (1.12, 1.00, (0.5, 0.45), (0.5, 0.5), 0),
    "A07": (1.00, 1.16, (0.5, 0.5), (0.45, 0.5), 5), "A08": (1.00, 1.22, (0.4, 0.55), (0.28, 0.5), 0),
    "A09": (1.00, 1.18, (0.5, 0.5), (0.40, 0.5), 0), "A10": (1.20, 1.00, (0.55, 0.5), (0.5, 0.5), 0),
    "B01": (1.00, 1.12, (0.5, 0.5), (0.4, 0.5), 0), "B02": (1.00, 1.14, (0.5, 0.5), (0.65, 0.5), 0),
    "B03": (1.00, 1.15, (0.5, 0.5), (0.6, 0.45), 0), "B04": (1.00, 1.10, (0.5, 0.5), (0.5, 0.55), 0),
    "B05": (1.00, 1.20, (0.5, 0.5), (0.45, 0.62), 0), "B06": (1.25, 1.00, (0.4, 0.4), (0.5, 0.5), 0),
    "B07": (1.00, 1.20, (0.5, 0.5), (0.25, 0.55), 0), "B08": (1.00, 1.10, (0.5, 0.5), (0.5, 0.55), 0),
}


def ease(t):
    return t * t * (3 - 2 * t)


def clip_frames(img, name, dur):
    z0, z1, c0, c1, shake = CAM[name]
    n = int(dur * FPS)
    for i in range(n):
        t = ease(i / max(1, n - 1))
        z = z0 + (z1 - z0) * t
        fx = c0[0] + (c1[0] - c0[0]) * t
        fy = c0[1] + (c1[1] - c0[1]) * t
        cw, ch = W / z, H / z
        sx = math.sin(i * 1.9) * shake if shake and i < 14 else 0
        sy = math.cos(i * 2.3) * shake if shake and i < 14 else 0
        x0 = min(max(fx * W - cw / 2 + sx, 0), W - cw)
        y0 = min(max(fy * H - ch / 2 + sy, 0), H - ch)
        yield img.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + ch))


def render(shots, frames_dir, out):
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-movflags", "+faststart", str(out)]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    total = 0
    for name, _, dur, _ in shots:
        img = Image.open(frames_dir / f"{name}.png").convert("RGB")
        for fr in clip_frames(img, name, dur):
            p.stdin.write(fr.tobytes())
            total += 1
        for _ in range(3):                                                   # 3-frame hold between shots (hard cut)
            p.stdin.write(fr.tobytes())
            total += 1
    p.stdin.close()
    p.wait()
    print(out.name, total, "frames", round(total / FPS, 1), "s")


if __name__ == "__main__":
    render(scene_a.SHOTS, scene_a.OUT, scene_a.OUT.parent / "scene_a_animatic.mp4")
    render(scene_b.SHOTS, scene_b.OUT, scene_b.OUT.parent / "scene_b_animatic.mp4")
