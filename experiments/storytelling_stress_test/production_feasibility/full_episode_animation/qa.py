"""QA on the RENDERED mp4 (not on the source): decode every frame at 160x90, measure frame-to-frame change per scene (is anything moving?),
detect jumps / black frames, and save contact sheets. Usage: python qa.py"""
import json
import os
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image

import episode

HERE = Path(__file__).resolve().parent
MP4 = Path(os.environ.get("QA_MP4", str(HERE / "renders" / "pab_hai_thueng_duangjan_full_episode.mp4")))
OUT = Path(os.environ.get("QA_OUT", str(HERE / "qa")))
OUT.mkdir(exist_ok=True)
FPS = 24

p = subprocess.run(["ffmpeg", "-v", "error", "-i", str(MP4), "-vf", "scale=160:90,format=gray", "-f", "rawvideo", "-"], capture_output=True)
data = np.frombuffer(p.stdout, np.uint8).reshape(-1, 90, 160).astype(np.int16)
n = len(data)
diff = np.abs(np.diff(data, axis=0)).mean(axis=(1, 2))                # change between consecutive frames
tl, total = episode.timeline()
rep = {"frames": n, "seconds": n / FPS, "scenes": {}}
for name, t0, dur in tl:
    a, b = int(t0 * FPS), min(int((t0 + dur) * FPS), n - 1)
    d = diff[a:b - 1]
    rep["scenes"][name] = dict(start=t0, dur=dur, mean_change=round(float(d.mean()), 3), pct_frames_moving=round(float((d > 0.15).mean() * 100), 1),
                               longest_still_s=0.0, max_jump=round(float(d.max()), 2))
    still, best = 0, 0
    for v in d:
        still = still + 1 if v < 0.05 else 0
        best = max(best, still)
    rep["scenes"][name]["longest_still_s"] = round(best / FPS, 2)
mean_lum = data.mean(axis=(1, 2))
rep["black_frames"] = [int(i) for i in np.where(mean_lum < 8)[0]]
rep["jump_frames_over_25"] = [int(i) for i in np.where(diff > 25)[0]]
(OUT / "qa_metrics.json").write_text(json.dumps(rep, indent=1), encoding="utf-8")
print(json.dumps(rep, indent=1))

# contact sheets: one frame every 12 s
times = list(range(2, int(total), 12))
for k in range(0, len(times), 12):
    chunk = times[k:k + 12]
    ims = []
    for t in chunk:
        f = OUT / f"f_{t}.png"
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", str(t), "-i", str(MP4), "-frames:v", "1", "-vf", "scale=426:240", str(f)])
        ims.append(Image.open(f))
    sheet = Image.new("RGB", (4 * 430, 3 * 244), (20, 20, 20))
    for i, im in enumerate(ims):
        sheet.paste(im, ((i % 4) * 430 + 2, (i // 4) * 244 + 2))
    sheet.save(OUT / f"contact_{k // 12 + 1}.png")
    for t in chunk:
        (OUT / f"f_{t}.png").unlink()
print("sheets done")
