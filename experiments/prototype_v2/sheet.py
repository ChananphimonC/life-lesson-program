"""Prototype v2b character sheets (stage 1 of the quality round): one sheet per character.

    python sheet.py   -> out/sheet_pin.png, out/sheet_mom.png

Each sheet: turnaround (front / 3/4 / side, resting pose), a holding pose and a story pose, five expressions,
and hand studies drawn with their forearm so the wrist joint can be checked.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageChops, ImageDraw

from cast import CHARS, D2R, EXPR, head
from figure import BODY, HANDS, _band, figure, hand, limb
from toon import Canvas, mix

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
W, H = 2400, 1500
BG = (250, 246, 238, 255)
TAG = "v2c"          # output suffix: the approved sheet_<id>.png (v2b) files are never overwritten

SHEETS = {
    "pin": dict(
        title="Pin (host)  /  v2c",
        turn=dict(pregnant=False),
        poses=[("hold_bowl", 35, "happy", False, 0, "ถือของ"), ("magnify", 35, "determined", False, 0, "เหตุการณ์: สืบ")],
        exprs=[("neutral", "ปกติ"), ("happy", "ดีใจ"), ("surprised", "ตกใจ"), ("worried", "กังวล"),
               ("determined", "มุ่งมั่น")],
        hands=[("relaxed", 0, "พัก"), ("cup", -20, "รองชาม"), ("grip", 0, "กำด้าม"), ("open", 180, "แบมือ"),
               ("point", 180, "ชี้")],
    ),
    "mom": dict(
        title="Mom  /  v2c",
        turn=dict(pregnant=True),
        poses=[("hold_high", 40, "eager", True, 0, "ถือของ"), ("eat", 40, "content", True, 0, "เหตุการณ์: กิน")],
        exprs=[("neutral", "ปกติ"), ("happy", "ดีใจ"), ("surprised", "ตกใจ"), ("meh", "ไม่เอา"), ("eager", "อยากกิน")],
        hands=[("relaxed", 0, "พัก"), ("cup", -20, "รองชาม"), ("grip", 0, "กำช้อน"), ("open", 180, "แบมือ"),
               ("point", 180, "ชี้")],
    ),
}


def label(img, x, y, text, size=30, col=(120, 100, 90), anchor="mm"):
    from subtitles import font
    ImageDraw.Draw(img).text((x, y), text, font=font(size, False), fill=col, anchor=anchor)


def build(cid):
    import sys
    sys.path.insert(0, str(HERE.parent / "shorts"))
    S = SHEETS[cid]
    c = CHARS[cid]
    cv = Canvas(W, H, ss=3, bg=BG)
    # turnaround
    k = 1.42
    for i, (deg, name) in enumerate(((0, "มุมตรง"), (35, "สามส่วน"), (82, "ด้านข้าง"))):
        cv.push(190 + i * 330, 250, scale=k)
        figure(cv, cid, deg * D2R, "rest", "neutral", pregnant=S["turn"]["pregnant"])
        cv.pop()
    # holding + story pose
    for i, (pose, deg, ex, preg, lean, name) in enumerate(S["poses"]):
        cv.push(1260 + i * 380, 250, scale=k)
        figure(cv, cid, deg * D2R, pose, ex, pregnant=preg, lean=lean)
        cv.pop()
    # expressions
    busts = []
    for i, (ex, name) in enumerate(S["exprs"]):     # bust portraits: head + shoulders, cropped below the chest
        bc = Canvas(250, 330, ss=3, bg=(0, 0, 0, 0))
        bc.push(125, 140, scale=1.0)
        figure(bc, cid, 18 * D2R, "rest", ex, pregnant=False, shadow=False)
        bc.pop()
        busts.append(bc.result())
    # hand studies with their forearm
    B = BODY[cid]
    skin = c["skin"]
    for i, (kind, ang, name) in enumerate(S["hands"]):
        x, y = 1430 + i * 200, 1140 if ang == 0 or kind == "cup" else 1210
        cv.push(x, y, scale=3.0)
        import math
        a = math.radians(ang)
        d = (-math.sin(a), math.cos(a))               # hand direction for this rotation
        el = (-d[0] * 34, -d[1] * 34)
        mirror = False
        if B["sleeve"] == "long":
            hand(cv, (0, 0), ang, kind, skin, mirror, part="base")
            limb(cv, [el, (0, 0)], (B["arm_w"][1], B["arm_w"][2] + 0.5, B["arm_w"][2]), B["top"], shade_col=B["top_dark"])
            cv.fill(_band(el, (0, 0), 0.62, B["arm_w"][2] + 2), B["cuff"], lw=2.8)
        else:
            limb(cv, [el, (0, 0)], (B["arm_w"][1], B["arm_w"][2] + 0.5, B["arm_w"][2]), skin,
                 shade_col=mix(skin, (226, 168, 158), 0.5))
            hand(cv, (0, 0), ang, kind, skin, mirror, part="base")
        if HANDS[kind].get("thumb"):
            hand(cv, (0, 0), ang, kind, skin, mirror, part="thumb")
        cv.pop()
    img = cv.result()
    for i, bimg in enumerate(busts):
        fade = Image.linear_gradient("L").resize(bimg.size).point(lambda v: 255 if v < 170 else max(0, 255 - (v - 170) * 3))
        alpha = ImageChops.multiply(bimg.getchannel("A"), fade)
        bimg.putalpha(alpha)
        img.alpha_composite(bimg, (25 + i * 250, 950))
    # labels (Thai words chosen without a tone mark over an upper vowel; the font cannot stack them yet)
    label(img, 60, 40, S["title"], 40, (90, 70, 60), anchor="lm")
    for i, (deg, name) in enumerate(((0, "มุมตรง"), (35, "สามส่วน"), (82, "ด้านข้าง"))):
        label(img, 190 + i * 330, 805, name)
    for i, p in enumerate(S["poses"]):
        label(img, 1260 + i * 380, 805, p[5])
    for i, (ex, name) in enumerate(S["exprs"]):
        label(img, 150 + i * 250, 1310, name)
    for i, (kind, ang, name) in enumerate(S["hands"]):
        label(img, 1430 + i * 200, 1370, name)
    label(img, 60, 890, "สีหน้า", 34, (90, 70, 60), anchor="lm")
    label(img, 1330, 890, "มือ / ข้อมือ / แขน", 34, (90, 70, 60), anchor="lm")
    ImageDraw.Draw(img).line([(80, 850), (W - 80, 850)], fill=(222, 212, 198), width=3)
    img.convert("RGB").save(OUT / f"sheet_{cid}_{TAG}.png")
    return img


if __name__ == "__main__":
    for cid in ("pin", "mom"):
        build(cid)
    print("ok")
