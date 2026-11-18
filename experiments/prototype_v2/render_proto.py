"""Prototype v2: the first 29 s of 'know_craving' re-shot as 7 storyboarded shots on the ALREADY-CACHED narration
(no TTS / API call). Shot boundaries sit on pauses found offline with ffmpeg silencedetect.

    python render_proto.py            # -> out/proto_craving_opening.mp4 + out/proto_contact.png + out/storyboard.json
    python render_proto.py --sheet    # contact sheet only (fast)

Isolated: imports existing modules read-only and writes only under experiments/prototype_v2/out.
"""

from __future__ import annotations

import json
import math
import shutil
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageFilter, ImageOps

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "shorts"))

import rig  # noqa: E402
import props_v2 as PV  # noqa: E402
import backgrounds  # noqa: E402
import backgrounds_flood  # noqa: E402,F401  (living_room)
import backgrounds_city  # noqa: E402,F401  (kitchen)
import character_art as CA  # noqa: E402
import lipsync  # noqa: E402
import props_story  # noqa: E402
import tts  # noqa: E402

W, H, FPS = 1920, 1080, 30
OUT = HERE / "out"
AUDIO = (HERE.parent / "cartoon_storyboard" / "output" / "_work" / "tts" / "know_craving" / "line01-02a6a1162f.gemini.wav")

# Pauses in the cached audio (ffmpeg silencedetect -34 dB, d=0.18): 0.65 2.97 4.40 9.68 10.95 13.94 17.52 18.88 21.52 23.33 25.34
SHOTS = [
    dict(id="S1", t0=0.00, t1=2.97, voice="เอ๊ะ! บ้านปิ่นมีคดีปริศนาค่ะ!",
         purpose="Hook: the narrator herself is startled; viewers meet her face first.",
         action="Close-up of ปิ่น turning to camera, eyebrows up, eyes wide; she speaks to the viewer.",
         shot="close-up, eye level, character right of centre; living room behind, blurred", motion="quick punch-in 0.25 s on 'เอ๊ะ', then hold",
         text="none"),
    dict(id="S2", t0=2.97, t1=6.15, voice="คุณยายตอนท้องแม่ กินทุเรียนแทบทุกวัน",
         purpose="Memory 1: grandma's craving. Warm sepia grade = the past, no caption needed.",
         action="คุณยาย holds a plate of golden durian pods with both hands, eyes closed, chewing happily.",
         shot="medium shot, slightly left; old living room in sepia", motion="slow lateral drift with parallax",
         text="none"),
    dict(id="S3a", t0=6.15, t1=10.95, voice="แม่ตอนท้องพี่สาว ไปกินสุกี้...ทุกสัปดาห์ เพราะอยากตับลวก",
         purpose="Memory 2: mum pregnant with the elder sister, at a hotpot restaurant every week.",
         action="Pregnant แม่ sits behind a table with a bubbling hotpot and a plate of liver, leaning in, eyes sparkling.",
         shot="medium shot, mum right, pot left foreground, table edge hides her lap", motion="steam and bubbles only",
         text="none"),
    dict(id="S3b", t0=10.95, t1=13.94, voice="แต่ลวกสุกนะคะ",
         purpose="Payoff joke: show the liver really is cooked.", action="Insert: a ladle slowly lifts a cooked, brown slice out of the pot.",
         shot="extreme close-up on the pot, no people", motion="ladle rises over 1.5 s", text="none"),
    dict(id="S4", t0=13.94, t1=17.52, voice="แต่พอท้องปิ่น แม่ทิ้งหมดเลย หันมากินตำผลไม้กับโอเลี้ยง!",
         purpose="Memory 3 (contrast): a different pregnancy, a totally different craving.",
         action="Pregnant แม่ in the kitchen hugs a bowl of fruit salad, grinning and chewing; an iced coffee waits on the counter.",
         shot="medium shot, mum centre-left, glass right", motion="whip-pan transition in, then chewing", text="none"),
    dict(id="S5", t0=17.52, t1=21.52, voice="แล้วพอปิ่นโตขึ้น แม่ไม่เคยแตะตำผลไม้อีกเลยนะคะ!",
         purpose="Twist: back in the present, mum refuses the very food she craved.",
         action="Grown-up ปิ่น offers a bowl of fruit salad; แม่ (not pregnant) gives a flat, unimpressed look and leans away.",
         shot="two-shot, ปิ่น left, แม่ right, present-day colours", motion="mum leans back at 19 s", text="none"),
    dict(id="S6", t0=21.52, t1=28.93, voice="ตกลงของที่แม่อยากกิน มันบอกอะไรเกี่ยวกับลูกหรือเปล่า วันนี้ปิ่นกับน้องหมาห้าตัว จะเปิดแฟ้มสืบสวนกันค่ะ!",
         purpose="The question that drives the episode, then the 'case' begins.",
         action="ปิ่น, hands clasped, puzzled; at 25.3 s she turns determined while the five dogs hop and the case folder opens.",
         shot="wide, low angle: dogs and folder in the foreground, ปิ่น behind", motion="dogs hop, folder opens", text="none"),
]
WHIP = (13.79, 14.09)                       # the one transition: S3b -> S4


def _sepia(img, amount=0.45):
    grey = ImageOps.grayscale(img)
    warm = ImageOps.colorize(grey, (70, 44, 30), (255, 236, 200))
    out = Image.blend(img, warm, amount)
    vign = Image.radial_gradient("L").resize(img.size).point(lambda v: max(0, v - 90) * 150 // 165)
    return Image.composite(Image.new("RGB", img.size, (60, 40, 30)), out, vign)


_bg_cache: dict = {}


def bg(name, zoom=1.0, blur=0.0, sepia=False):
    key = (name, zoom, blur, sepia)
    if key not in _bg_cache:
        img = PV.restaurant(W, H) if name == "restaurant" else backgrounds.BACKGROUNDS[name](W, H).convert("RGB")
        if zoom != 1.0:
            zw, zh = int(W / zoom), int(H / zoom)
            img = img.crop(((W - zw) // 2, (H - zh) // 2, (W + zw) // 2, (H + zh) // 2)).resize((W, H), Image.LANCZOS)
        if blur:
            img = img.filter(ImageFilter.GaussianBlur(blur))
        if sepia:
            img = _sepia(img)
        _bg_cache[key] = img
    return _bg_cache[key].copy()


def place(img, spr, cx, feet_y, scale=1.0, angle=0.0):
    if scale != 1.0:
        spr = spr.resize((int(spr.width * scale), int(spr.height * scale)), Image.LANCZOS)
    if angle:
        spr = spr.rotate(angle, resample=Image.BICUBIC, center=(spr.width / 2, spr.height * 0.97))
    img.paste(spr, (int(cx - spr.width / 2), int(feet_y - spr.height * (CA.GROUND_Y / CA.CH))), spr)


def ease(u):
    u = max(0.0, min(1.0, u))
    return u * u * (3 - 2 * u)


class Proto:
    W, H = W, H

    def __init__(self):
        self.samples = tts.read_wav(AUDIO)
        self.track = lipsync.mouth_track(self.samples, FPS)
        self.total = len(self.samples) / tts.SAMPLE_RATE

    def talk(self, t):
        f = min(int(t * FPS), len(self.track) - 1)
        level = sum(self.track[max(0, f - k)][1] for k in range(3)) / 3
        return min(6, int(level * 1.8 * 6 + 0.5))

    @staticmethod
    def blink(t, phase):
        return ((t + phase) % 3.6) < 0.13

    def shot_frame(self, s, t):
        lt = t - s["t0"]
        sid = s["id"]
        if sid == "S1":
            img = bg("living_room", 1.5, 7)
            k = 0.94 + 0.06 * (1 - (1 - min(1.0, lt / 0.25)) ** 3)
            spr = rig.sprite("host_mint", "default", "relaxed", "surprised", self.talk(t), self.blink(t, 0.4), None, None, 2050)
            place(img, spr, W * 0.60, H * 1.62, k)
            return img
        if sid == "S2":
            drift = ease(lt / (s["t1"] - s["t0"]))
            img = bg("living_room", 1.15, 2.5, True)
            img = img.transform(img.size, Image.AFFINE, (1, 0, -20 + 40 * drift, 0, 1, 0), resample=Image.BILINEAR)
            spr = rig.sprite("grandma", "default", "hold_chest", "blissful", None, False, int(lt * 4) % 2, "durian_plate", 1500)
            place(img, spr, W * 0.44 - 40 * drift, H * 1.18)
            return _sepia(img, 0.3)
        if sid == "S3a":
            img = bg("restaurant", 1.0, 2.0, True)
            spr = rig.sprite("mom", "pregnant", "clasp", "eager", None, self.blink(t, 1.1), None, None, 1450)
            place(img, spr, W * 0.66, H * 1.20)
            PV.table_front(img, W, H, H * 0.74)
            PV.hotpot(img, W * 0.30, H * 0.66, 2.3, t)
            PV.liver_plate(img, W * 0.50, H * 0.84, 1.6)
            return _sepia(img, 0.3)
        if sid == "S3b":
            img = bg("restaurant", 1.6, 9, True)
            PV.table_front(img, W, H, H * 0.78)
            PV.hotpot(img, W * 0.5, H * 0.68, 3.4, t, liver_up=ease((lt - 0.3) / 1.6))
            return _sepia(img, 0.3)
        if sid == "S4":
            img = bg("kitchen", 1.1, 2.0, True)
            glass = props_story.sprite("oliang", H)
            glass = glass.resize((int(glass.width * 1.6), int(glass.height * 1.6)), Image.LANCZOS)
            img.paste(glass, (int(W * 0.78 - glass.width / 2), int(H * 0.44)), glass)
            spr = rig.sprite("mom", "pregnant", "hold_chest", "delighted", None, False, int(lt * 4) % 2, "salad_bowl", 1500)
            place(img, spr, W * 0.42, H * 1.20)
            return _sepia(img, 0.3)
        if sid == "S5":
            img = bg("living_room", 1.1, 1.5)
            lean = -4 * ease((lt - 1.4) / 0.5)
            pin = rig.sprite("host_mint", "default", "offer", "eager", None, self.blink(t, 0.2), None, "salad_bowl", 1350)
            mom = rig.sprite("mom", "default", "clasp", "meh" if lt > 0.9 else "neutral", None, self.blink(t, 1.7), None, None, 1350)
            place(img, pin, W * 0.33, H * 1.10)
            place(img, mom, W * 0.70, H * 1.10, 1.0, lean)
            return img
        # S6
        img = bg("living_room", 1.0, 1.0)
        decided = t >= 25.34
        expr = "determined" if decided else "puzzled"
        talk = self.talk(t)
        pin = rig.sprite("host_mint", "default", "clasp", expr, talk, self.blink(t, 0.9), None, None, 1050)
        place(img, pin, W * 0.50, H * 0.90)
        PV.case_folder(img, W * 0.50, H * 0.90, 1.2, ease((t - 25.5) / 0.8))
        dogs = (("pom_brown", "calm", 0.12), ("pom_white", "default", 0.26), ("chi_bw", "default", 0.70),
                ("chi_latte", "default", 0.80), ("chi_nescafe", "default", 0.90))
        for i, (cid, outfit, x) in enumerate(dogs):
            spr = CA.sprite(cid, outfit, 1 if x < 0.5 else -1, 0, self.blink(t, i * 0.7), 0.92)
            hop = abs(math.sin(math.pi * (t * 1.6 + i * 0.3))) * 34 if decided else 0
            place(img, spr, W * x, H * 1.02 - hop)
        return img

    def shot_at(self, t):
        return next((s for s in SHOTS if t < s["t1"]), SHOTS[-1])

    def frame(self, t):
        a, b = WHIP
        if a <= t < b:                              # whip pan: the old shot streaks out left, the new one streaks in
            u = ease((t - a) / (b - a))
            old = self.shot_frame(SHOTS[3], a)
            new = self.shot_frame(SHOTS[4], b)
            canvas = Image.new("RGB", (W, H))
            smear = 1 + 46 * math.sin(math.pi * u)                    # strongest in the middle of the move
            for img, off in ((old, -u * W), (new, (1 - u) * W)):
                streak = img.resize((max(8, int(W / smear)), H), Image.BILINEAR).resize((W, H), Image.BILINEAR)
                canvas.paste(streak, (int(off), 0))
            return canvas
        s = self.shot_at(t)
        return self.shot_frame(s, t)


def contact(p: Proto, path: Path):
    times = [1.2, 2.4, 4.6, 8.4, 12.6, 13.95, 15.5, 20.0, 23.0, 27.0]
    tiles = [p.frame(tt).resize((480, 270), Image.LANCZOS) for tt in times]
    sheet = Image.new("RGB", (480 * 5, 270 * 2), (20, 20, 20))
    for i, im in enumerate(tiles):
        sheet.paste(im, ((i % 5) * 480, (i // 5) * 270))
    sheet.save(path)


def main():
    OUT.mkdir(exist_ok=True)
    p = Proto()
    (OUT / "storyboard.json").write_text(json.dumps({"source_audio": str(AUDIO), "fps": FPS, "transition": {"whip_pan": WHIP},
                                                      "shots": SHOTS}, ensure_ascii=False, indent=2), encoding="utf-8")
    contact(p, OUT / "proto_contact.png")
    if "--sheet" in sys.argv:
        print("sheet only")
        return
    import render_short
    audio = OUT / "proto_audio.wav"
    shutil.copy(AUDIO, audio)                       # a copy: the cached original is never touched
    render_short.encode(p, p.total, audio, OUT / "proto_craving_opening.mp4", "ffmpeg")
    print("video:", OUT / "proto_craving_opening.mp4", f"{p.total:.1f}s")


if __name__ == "__main__":
    main()
