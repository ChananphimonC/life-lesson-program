"""Playback-style inspection of the rendered v2d frames (no new rendering of the video).

    python inspect_v2d.py sheets    -> out/inspect_v2d_seq_<n>.png : every 3rd frame (10 fps) in order, with time stamps
    python inspect_v2d.py motion    -> frame-to-frame change, spikes, static-background check
    python inspect_v2d.py audio     -> sound intervals found in the muxed mp4 vs the planned effect times
    python inspect_v2d.py scale     -> character size across frames (silhouette box of each layer, every 10th frame)
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "shorts"))

import numpy as np  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

import anim_v2d as A  # noqa: E402
from subtitles import font  # noqa: E402

FR = A.FRAMES
N = int(A.DUR * A.FPS)


def frame(f):
    return Image.open(FR / f"f{f:04d}.png").convert("RGB")


def sheets():
    idx = list(range(0, N, 3))
    per, cols = 30, 5
    box = (560, 90, 1620, 760)                       # both characters, bowl and lens
    tw, th = 340, 215
    for s in range(0, len(idx), per):
        chunk = idx[s:s + per]
        rows = -(-len(chunk) // cols)
        sh = Image.new("RGB", (cols * tw, rows * th), (24, 24, 28))
        for i, f in enumerate(chunk):
            im = frame(f).crop(box).resize((tw, th), Image.LANCZOS)
            ImageDraw.Draw(im).text((8, 4), f"{f / A.FPS:4.2f}s", font=font(26, False), fill=(40, 40, 40))
            sh.paste(im, ((i % cols) * tw, (i // cols) * th))
        path = A.OUT / f"inspect_v2d_seq_{s // per + 1}.png"
        sh.save(path)
        print(path.name, f"frames {chunk[0]}-{chunk[-1]}")


def motion():
    small = [np.asarray(frame(f).convert("L").resize((480, 270)), np.float32) for f in range(N)]
    d = np.array([np.abs(small[i + 1] - small[i]).mean() for i in range(N - 1)])
    med = float(np.median(d))
    print(f"frame-to-frame mean change: median {med:.3f}, max {d.max():.3f} at {np.argmax(d) / A.FPS:.2f}s, "
          f"frames with change > 3x median: {(d > 3 * med).sum()}")
    spikes = sorted(((float(v), i) for i, v in enumerate(d) if v > 2.5 * med), reverse=True)[:8]
    print("largest steps:", ", ".join(f"{i / A.FPS:.2f}s ({v / med:.1f}x)" for v, i in spikes))
    # a 'pop' is a step much bigger than both of its neighbours (a smooth move has similar neighbours)
    pops = [i for i in range(1, len(d) - 1) if d[i] > 2.2 * max(d[i - 1], d[i + 1]) and d[i] > 1.5 * med]
    print("isolated single-frame pops:", [f"{i / A.FPS:.2f}s" for i in pops] or "none")
    # background that no character ever covers must be identical in every frame
    f0 = np.asarray(frame(0), np.int16)
    worst = 0
    for f in range(1, N, 6):
        cur = np.asarray(frame(f), np.int16)
        for (x0, y0, x1, y1) in ((0, 0, 520, 760), (1640, 0, 1920, 1080), (0, 0, 1920, 90)):
            worst = max(worst, int(np.abs(cur[y0:y1, x0:x1] - f0[y0:y1, x0:x1]).max()))
    print(f"static background (left wall/window/cabinet, fridge, ceiling) max pixel change over time: {worst}")


def audio():
    out = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(A.VIDEO), "-af", "silencedetect=n=-45dB:d=0.12", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    starts = [float(x.split(":")[1].split()[0]) for x in out.splitlines() if "silence_end" in x]
    ends = [float(x.split(":")[1].split()[0]) for x in out.splitlines() if "silence_start" in x]
    print("sound begins (s):", [round(x, 2) for x in starts])
    print("sound ends   (s):", [round(x, 2) for x in ends])
    print(f"planned effects: sniff {A.SNIFF_T}, gasp {A.GASP_T}, sigh {A.SIGH_T}")
    _, pin, mom = A.build_audio()
    tp, tm = A.lipsync.mouth_track(pin, A.FPS), A.lipsync.mouth_track(mom, A.FPS)
    on = lambda tr: [round(i / A.FPS, 2) for i, (s, _) in enumerate(tr) if s >= 1]
    p, m = on(tp), on(tm)
    print(f"Pin's mouth is driven open on frames {p[0]}-{p[-1]} s" if p else "no Pin mouth frames")
    print(f"Mom's mouth is driven open on frames {m[0]}-{m[-1]} s" if m else "no Mom mouth frames")


def scale():
    A._init()
    rows = {"pin": [], "mom": []}
    for f in range(0, N, 10):
        t, ps, ms, *_ = A.frame_state(f)
        for cid, th, flip, st, preg in (("pin", A.PIN_TH, False, ps, False), ("mom", A.MOM_TH, True, ms, True)):
            a = np.asarray(A.layer(cid, th, flip, st, 0.0, None, preg, t).getchannel("A"))
            ys, xs = np.nonzero(a > 40)
            rows[cid].append((ys.min(), ys.max(), xs.min(), xs.max()))
    for cid, r in rows.items():
        r = np.array(r)
        h = r[:, 1] - r[:, 0]
        print(f"{cid}: silhouette height {h.min()}-{h.max()} px (feet stay at y {r[:, 1].min()}-{r[:, 1].max()}), "
              f"top of head moves {r[:, 0].max() - r[:, 0].min()} px over the scene")


if __name__ == "__main__":
    {"sheets": sheets, "motion": motion, "audio": audio, "scale": scale}[sys.argv[1]]()
