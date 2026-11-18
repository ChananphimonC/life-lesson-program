"""Cut every sticker out of the illustration sheets in
`experiments/character and props/` into individual transparent PNGs.

    python extract_assets.py

Output: output/assets/<sheet>/<nnn>.png, plus output/assets/<sheet>_index.png
(the sheet with numbered boxes) and output/assets/index.json.
"""

from __future__ import annotations

import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage

HERE = Path(__file__).resolve().parent
SRC = HERE.parent / "character and props"
OUT = HERE / "output" / "assets"

SHEETS = {
    "Actions Louder": "actions",
    "City Loneliness": "city",
    "Finding Your Own Pace": "pace",
    "Props and office": "office",
    "The Comparison Trap": "compare",
    "The Cost of Hustle": "hustle",
    "Trend Chaser": "debt",
    "component and character + emotion": "emotion",
    "component and character.jpg": "components",
    "ธีม Burnout": "burnout",
    "สมรภูมิสมัครงาน": "jobhunt",
    "แคร์คนนอก": "family",
    # The two cha1 filenames are swapped relative to their content.
    "cha1.png": "cha1_glasses",
    "cha1 with glasses.png": "cha1_plain",
    "cha2.png": "cha2",
}

SOFT_LO, SOFT_HI, SOLID = 7.0, 38.0, 45.0
MIN_AREA = 500
GROUP_GAP = 7
SHADOW_PAD = 22


def slug_for(name: str) -> str | None:
    for key, slug in SHEETS.items():
        if name.startswith(key) or name == key:
            return slug
    return None


def estimate_background(img: np.ndarray, fg: np.ndarray, sigma: float = 60.0) -> np.ndarray:
    """Normalized convolution: blur the background-only pixels to get a smooth
    per-pixel background color (handles vignettes and two-tone sheets)."""
    w = (~fg).astype(np.float32)
    k = int(sigma * 3) | 1
    num = cv2.GaussianBlur(img * w[..., None], (k, k), sigma)
    den = cv2.GaussianBlur(w, (k, k), sigma)[..., None]
    return num / np.maximum(den, 1e-3)


def cut(img_rgb: np.ndarray):
    img = img_rgb.astype(np.float32)
    border = np.concatenate([img[:4].reshape(-1, 3), img[-4:].reshape(-1, 3),
                             img[:, :4].reshape(-1, 3), img[:, -4:].reshape(-1, 3)])
    bg = np.broadcast_to(np.median(border, axis=0), img.shape)
    fg = np.zeros(img.shape[:2], bool)
    for _ in range(2):
        diff = np.abs(img - bg).max(axis=2)
        fg = ndimage.binary_dilation(diff > SOFT_HI, iterations=6)
        bg = estimate_background(img, fg)
    diff = np.abs(img - bg).max(axis=2)

    solid = ndimage.binary_closing(diff > SOLID, iterations=2)
    solid = ndimage.binary_fill_holes(solid)
    solid = ndimage.binary_opening(solid, iterations=1)
    soft = np.clip((diff - SOFT_LO) / (SOFT_HI - SOFT_LO), 0, 1)
    alpha = np.maximum(soft, solid.astype(np.float32))
    alpha = cv2.GaussianBlur(alpha, (3, 3), 0.7)
    alpha[alpha < 0.04] = 0

    # Un-mix the background from partially transparent pixels (edges, shadows).
    a = np.maximum(alpha[..., None], 1e-3)
    color = np.clip((img - (1 - a) * bg) / a, 0, 255)
    color = np.where(alpha[..., None] > 0.97, img, color)
    rgba = np.dstack([color, alpha * 255]).astype(np.uint8)

    # Group by solid shapes only: soft shadows would otherwise bridge stickers.
    grouping = ndimage.binary_dilation(solid, iterations=GROUP_GAP)
    labels, _ = ndimage.label(grouping)
    h, w = alpha.shape
    boxes = []
    for i, sl in enumerate(ndimage.find_objects(labels), start=1):
        if sl is None:
            continue
        if ((labels[sl] == i) & solid[sl]).sum() < MIN_AREA:
            continue
        y0, y1 = max(0, sl[0].start - SHADOW_PAD), min(h, sl[0].stop + SHADOW_PAD)
        x0, x1 = max(0, sl[1].start - SHADOW_PAD), min(w, sl[1].stop + SHADOW_PAD)
        lab = labels[y0:y1, x0:x1]
        mine = ndimage.binary_dilation(lab == i, iterations=SHADOW_PAD)
        member = mine & ~((lab > 0) & (lab != i)) & (alpha[y0:y1, x0:x1] > 0)
        ys, xs = np.nonzero(member)
        if len(ys) == 0:
            continue
        by0, by1, bx0, bx1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        boxes.append((x0 + bx0, y0 + by0, x0 + bx1, y0 + by1, member[by0:by1, bx0:bx1]))
    boxes.sort(key=lambda b: (b[1] // 120, b[0]))
    return rgba, boxes


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    index = {}
    font = ImageFont.truetype("arialbd.ttf", 34)
    for path in sorted(SRC.iterdir()):
        slug = slug_for(path.name)
        if slug is None:
            print(f"skip {path.name}")
            continue
        img = np.array(Image.open(path).convert("RGB"))
        rgba, boxes = cut(img)
        sheet_dir = OUT / slug
        sheet_dir.mkdir(exist_ok=True)
        overview = Image.fromarray(img).convert("RGB")
        draw = ImageDraw.Draw(overview)
        entries = []
        for n, (x0, y0, x1, y1, member) in enumerate(boxes, start=1):
            piece = rgba[y0:y1, x0:x1].copy()
            piece[..., 3] = np.where(member, piece[..., 3], 0)
            Image.fromarray(piece, "RGBA").save(sheet_dir / f"{n:03d}.png")
            entries.append({"id": f"{slug}/{n:03d}", "box": [int(x0), int(y0), int(x1), int(y1)]})
            draw.rectangle((x0, y0, x1, y1), outline=(230, 40, 60), width=4)
            draw.rectangle((x0, y0, x0 + 64, y0 + 40), fill=(230, 40, 60))
            draw.text((x0 + 6, y0 + 2), str(n), fill=(255, 255, 255), font=font)
        overview.thumbnail((1400, 1400))
        overview.save(OUT / f"{slug}_index.png")
        index[slug] = {"source": path.name, "assets": entries}
        print(f"{slug}: {len(entries)} assets")
    (OUT / "index.json").write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
