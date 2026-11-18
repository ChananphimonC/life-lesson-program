"""Prototype v2c animation-readiness test: one ~11 s kitchen scene with the refined characters (no API, no new audio).

Story beat (no on-screen text): ปิ่น inspects the bowl แม่ is holding through a magnifying glass; the lens really
magnifies the bowl. ปิ่น goes from curious to surprised; แม่ smells the bowl, winces and leans gently away, then
settles into a sheepish smile. Mouth movement for ปิ่น is driven by the already-cached narration (the last 11.4 s of
cartoon_storyboard/output/_work/tts/know_craving/line01-02a6a1162f.gemini.wav, read-only); nothing is synthesised.

    python anim_test.py --stills 0.5 3 5.2 7 10     -> out/anim_still_<t>.png
    python anim_test.py --render                    -> out/anim_frames/*.png (scratch; deleted after encoding) and out/anim_test_v2c.mp4
    python anim_test.py --sheet                     -> out/anim_storyboard_v2c.png (frame preview from the rendered frames)
"""

from __future__ import annotations

import math
import subprocess
import sys
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "shorts"))

from PIL import Image, ImageDraw  # noqa: E402

import lipsync  # noqa: E402
import tts  # noqa: E402
from cast import D2R, MOM, PIN, feature, mix_expr  # noqa: E402
from figure import ARM_LEN, BODY, figure, pose_lerp, solve_arm  # noqa: E402
from toon import Canvas, spline, yaw  # noqa: E402

OUT = HERE / "out"
FRAMES = OUT / "anim_frames"
W, H, FPS = 1920, 1080, 30
K = 2.0                                    # figure units -> pixels
LW, LH, OX, OY = 1300, 1010, 650, 262      # per-character layer: size and where the head centre sits
GROUND = 1035
PIN_X, MOM_X = 830, 1300
PIN_Y = GROUND - BODY["pin"]["ground"] * K
MOM_Y = GROUND - BODY["mom"]["ground"] * K
PIN_TH, MOM_TH = 40.0, 46.0

SRC_AUDIO = OUT / "proto_audio.wav"        # read-only copy of the cached narration (made in the first prototype)
T0 = 17.52                                 # start inside it (a pause), so the clip begins between phrases
DUR = 28.93 - T0
AUDIO = OUT / "anim_audio.wav"
VIDEO = OUT / "anim_test_v2c.mp4"


# --- keyframes ------------------------------------------------------------------------------------------------------------------

def _mp(smile, mw=1.0, skew=0.0, rnd=0.0, wave=0.0):
    return dict(smile=smile, mw=mw, skew=skew, rnd=rnd, wave=wave)


PIN_E = {
    "curious": dict(open=1.08, gaze=(3, 3), brow=(7, 3), mouth="smile", mp=_mp(0.45, 0.8), blush=0.8, tilt=7),
    "peer": dict(open=0.9, lid=0.16, gaze=(4, 3), brow=(9, 2), mouth="smile", mp=_mp(0.3, 0.7), blush=0.9, tilt=9),
    "surprised": dict(open=1.3, gaze=(3, 1), brow=(13, 10), mouth="o", mp=_mp(0, 0.55, rnd=1), open_=0.75, blush=0.5,
                      tilt=-2, pupil=0.85),
    "surprised_soft": dict(open=1.16, gaze=(3, 2), brow=(10, 8), mouth="o", mp=_mp(0, 0.6, rnd=0.8), open_=0.3,
                           blush=0.7, tilt=2, pupil=0.9),
    "amazed": dict(open=1.12, gaze=(3, 2), brow=(8, 7), mouth="open_smile", mp=_mp(0.9, 1.05), open_=0.3, blush=1.1,
                   tilt=-3, sparkle=True),
}
MOM_E = {
    "calm": dict(gaze=(3, 0), brow=(1, 0), mouth="smile", mp=_mp(0.9), blush=0.8, tilt=-1),
    "notice": dict(gaze=(2, 3), brow=(2, 1), mouth="smile", mp=_mp(0.6, 0.9), blush=0.8, tilt=0),
    "sniff": dict(open=0.88, lid=0.2, gaze=(2, 3), brow=(5, 1), wrinkle=0.45, mouth="smile", mp=_mp(0.25, 0.75),
                  blush=0.6, tilt=2),
    "wince": dict(open=0.8, lid=0.5, gaze=(4, 3), brow=(9, -4), wrinkle=1.0, mouth="pout", mp=_mp(-0.6, 0.6, wave=0.3),
                  blush=0.35, tilt=6),
    "polite": dict(open=0.9, lid=0.34, gaze=(4, 2), brow=(7, -2), wrinkle=0.5, mouth="smile", mp=_mp(0.25, 0.85, wave=0.5),
                   blush=0.6, tilt=4),
    "sheepish": dict(lid=0.12, gaze=(4, 1), brow=(5, -1), wrinkle=0.1, mouth="smile", mp=_mp(0.55, 0.9), blush=1.0,
                     tilt=3, sweat=True),
}


def pin_pose(wr, tip):
    return dict(R=((-66, 164, 30), wr), L=((64, 182, -6), (59, 234, 10)), hands=dict(R=("grip", 0), L=("relaxed", 0)),
                grip=dict(side="R", item="lens", tip=tip), late="R")


def mom_pose(z, y=138):
    """Both hands under the bowl; the bowl follows the wrists the IK actually reaches (nothing floats)."""
    wr, wl = [solve_arm((s * 52, 126, -2), (s * 52, 160, 48), (s * 32, y, z), *ARM_LEN["mom"])[1] for s in (-1, 1)]
    mid = tuple((a + b) / 2 for a, b in zip(wr, wl))
    return dict(R=((-52, 160, 48), wr), L=((52, 160, 48), wl), hands=dict(R=("cup", -6), L=("cup", 6)),
                bowl=(0, mid[1] - 10, mid[2] + 8))


# t, expression, pose, lean (deg), head turn (deg), head nod (units)
PIN_KEYS = [
    (0.0, "curious", pin_pose((-46, 124, 66), (-14, 116, 118)), 3.0, PIN_TH + 2, 0.0),
    (1.9, "curious", pin_pose((-40, 124, 96), (-8, 114, 150)), 6.0, PIN_TH + 3, 1.0),
    (4.4, "peer", pin_pose((-40, 128, 98), (-6, 120, 154)), 9.0, PIN_TH + 3, 2.0),
    (4.95, "surprised", pin_pose((-44, 126, 80), (-12, 116, 132)), -1.5, PIN_TH - 5, -3.0),
    (6.4, "surprised_soft", pin_pose((-44, 128, 78), (-12, 120, 130)), 0.5, PIN_TH - 3, -1.5),
    (8.6, "amazed", pin_pose((-46, 130, 64), (-14, 122, 118)), 1.5, PIN_TH, 0.0),
    (DUR, "amazed", pin_pose((-46, 130, 64), (-14, 122, 118)), 1.0, PIN_TH + 1, 0.0),
]
MOM_KEYS = [
    (0.0, "calm", mom_pose(90), 0.0, MOM_TH, 0.0),
    (2.4, "notice", mom_pose(92), 0.0, MOM_TH + 1, 1.0),
    (3.7, "sniff", mom_pose(92), 2.0, MOM_TH + 4, 2.0),
    (5.4, "wince", mom_pose(94), -3.5, MOM_TH - 4, 0.5),
    (7.2, "polite", mom_pose(94), -7.0, MOM_TH - 12, -0.5),
    (9.2, "sheepish", mom_pose(94), -6.0, MOM_TH - 9, 0.0),
    (DUR, "sheepish", mom_pose(94), -5.5, MOM_TH - 8, 0.0),
]
PIN_BLINKS = [1.15, 3.3, 6.95, 9.7]
MOM_BLINKS = [0.8, 2.2, 4.75, 7.9, 10.4]


def _ease(u):
    return u * u * (3 - 2 * u)


def state(keys, t, exprs):
    for a, b in zip(keys, keys[1:]):
        if a[0] <= t <= b[0]:
            u = _ease((t - a[0]) / (b[0] - a[0])) if b[0] > a[0] else 0.0
            break
    else:
        a = b = keys[-1]
        u = 0.0
    L = lambda x, y: x + (y - x) * u
    return dict(expr=mix_expr(exprs[a[1]], exprs[b[1]], u), pose=pose_lerp(a[2], b[2], u), lean=L(a[3], b[3]),
                head_th=L(a[4], b[4]), nod=L(a[5], b[5]))


def blink_at(t, times):
    for b in times:
        d = t - b
        if 0 <= d < 0.17:
            return d / 0.06 if d < 0.06 else (1.0 if d < 0.085 else 1 - (d - 0.085) / 0.085)
    return 0.0


# --- layers ---------------------------------------------------------------------------------------------------------------------

def layer(cid, th, flip, st, blink, talk, pregnant, t):
    """One character on a transparent layer; subtle breathing and head float keep them alive between key poses."""
    br = math.sin(2 * math.pi * t / 3.7 + (0.0 if cid == "pin" else 1.3))
    cv = Canvas(LW, LH, ss=2)
    cv.push(OX, OY, scale=K, flip=flip)
    figure(cv, cid, th * D2R, st["pose"], st["expr"], pregnant=pregnant, lean=st["lean"] + 0.3 * br, talk=talk, blink=blink,
           head_th=st["head_th"] * D2R, head_dy=st["nod"] + 0.7 * br)
    cv.pop()
    return cv.result()


def _lean_pt(pt, lean, pivot_y):
    c, s = math.cos(math.radians(lean)), math.sin(math.radians(lean))
    x, y = pt[0], pt[1] - pivot_y
    return x * c - y * s, pivot_y + x * s + y * c


def lens_center(st):
    tip = st["pose"]["grip"]["tip"]
    q = yaw(tip, PIN_TH * D2R)
    x, y = _lean_pt((q[0], q[1]), st["lean"], BODY["pin"]["hip"][1])
    return PIN_X + x * K, PIN_Y + y * K


def mom_points(st):
    """Screen positions of the bowl and of แม่'s nose (she faces screen-left, so x is mirrored)."""
    th = MOM_TH * D2R
    q = yaw(st["pose"]["bowl"], th)
    bx, by = _lean_pt((q[0], q[1]), st["lean"], BODY["mom"]["hip"][1])
    (nx, ny), _ = feature(MOM, 0, MOM["nose_y"], st["head_th"] * D2R)
    nx, ny = _lean_pt((nx, ny + st["nod"]), st["lean"], BODY["mom"]["hip"][1])
    return (MOM_X - bx * K, MOM_Y + by * K), (MOM_X - nx * K, MOM_Y + ny * K)


def aroma(frame, bowl, nose, amt, t):
    """Three wavering smell lines rising from the bowl toward แม่'s nose: the reason she reacts, shown without words."""
    if amt < 0.02:
        return
    x0, y0 = int(min(bowl[0], nose[0]) - 70), int(min(bowl[1], nose[1]) - 70)
    x1, y1 = int(max(bowl[0], nose[0]) + 70), int(max(bowl[1], nose[1]) + 40)
    cv = Canvas(x1 - x0, y1 - y0, ss=3)
    cv.push(-x0, -y0)
    for k, off in enumerate((-16, 0, 16)):
        a = (bowl[0] + off, bowl[1] - 26)
        b = (nose[0] + off * 0.3 + 4, nose[1] + 4)
        pts = []
        for i in range(11):
            u = i / 10
            wob = 8 * math.sin(u * 7 + t * 5.5 + k * 1.9) * (0.35 + 0.65 * u)
            pts.append((a[0] + (b[0] - a[0]) * u + wob, a[1] + (b[1] - a[1]) * u))
        cv.stroke(spline(pts, n=4), (168, 198, 104), 4.6 - k * 0.5, alpha=int(200 * amt * (1 - 0.15 * k)))
    cv.pop()
    frame.alpha_composite(cv.result(), (x0, y0))


def magnify(frame, c, r=24 * K, mag=1.7):
    """Replace the glass interior with a magnified crop of what is behind it, so the lens does its job."""
    ri = int(r - 5.5)
    half = int(ri / mag)
    cx, cy = int(c[0]), int(c[1])
    crop = frame.crop((cx - half, cy - half, cx + half, cy + half)).resize((ri * 2, ri * 2), Image.LANCZOS)
    mask = Image.new("L", (ri * 8, ri * 8), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, ri * 8 - 1, ri * 8 - 1), fill=255)
    mask = mask.resize((ri * 2, ri * 2), Image.LANCZOS)
    frame.paste(crop.convert("RGB"), (cx - ri, cy - ri), mask)
    d = ImageDraw.Draw(frame)
    d.arc((cx - ri + 5, cy - ri + 5, cx + ri - 5, cy + ri - 5), 200, 250, fill=(255, 255, 255), width=3)


# --- frame ----------------------------------------------------------------------------------------------------------------------

_BG = None
_TRACK = None


def _init():
    global _BG, _TRACK
    _BG = Image.open(OUT / "anim_bg.png").convert("RGBA")
    _TRACK = lipsync.mouth_track(tts.read_wav(AUDIO), FPS)


def make_bg():
    import scene_test as S
    cv = Canvas(W, H, ss=2, bg=(255, 255, 255, 255))
    S.kitchen(cv)
    S.glow(cv, 975, 270, 520, (255, 244, 214), 0.4)
    S.table_front(cv)
    cv.result().convert("RGB").save(OUT / "anim_bg.png")


def frame_at(f):
    if _BG is None:
        _init()
    t = f / FPS
    ps, ms = state(PIN_KEYS, t, PIN_E), state(MOM_KEYS, t, MOM_E)
    shape, level = _TRACK[min(f, len(_TRACK) - 1)]
    talk = level if shape >= 1 else 0.0
    ps["pose"]["grip"]["tip"] = tuple(v + d for v, d in zip(ps["pose"]["grip"]["tip"],
                                                            (0.9 * math.sin(t * 4.1), 0.9 * math.sin(t * 3.3 + 1), 0)))
    img = _BG.copy()
    img.alpha_composite(layer("mom", MOM_TH, True, ms, blink_at(t, MOM_BLINKS), None, True, t), (int(MOM_X - OX), int(MOM_Y - OY)))
    bowl, nose = mom_points(ms)
    amt = min(1, max(0, (t - 2.6) / 1.6)) * (1 - 0.6 * min(1, max(0, (t - 8.6) / 1.6)))
    aroma(img, bowl, nose, amt, t)
    pin_blink = 0.0 if 4.7 < t < 6.1 else blink_at(t, PIN_BLINKS)
    img.alpha_composite(layer("pin", PIN_TH, False, ps, pin_blink, talk, False, t), (int(PIN_X - OX), int(PIN_Y - OY)))
    out = img.convert("RGB")
    magnify(out, lens_center(ps))
    return out


def _save(f):
    frame_at(f).save(FRAMES / f"f{f:04d}.png")
    return f


def prep_audio():
    if not AUDIO.exists():
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(T0), "-i", str(SRC_AUDIO), "-ar", "24000", "-ac", "1",
                        str(AUDIO)], check=True)


def main():
    OUT.mkdir(exist_ok=True)
    prep_audio()
    if "--stills" in sys.argv:
        make_bg()
        _init()
        for tt in sys.argv[sys.argv.index("--stills") + 1:]:
            frame_at(int(float(tt) * FPS)).save(OUT / f"anim_still_{float(tt):g}.png")
        return
    if "--render" in sys.argv:
        make_bg()
        FRAMES.mkdir(exist_ok=True)
        n = int(DUR * FPS)
        with Pool(6, initializer=_init) as pool:
            for i, f in enumerate(pool.imap_unordered(_save, range(n))):
                if i % 40 == 0:
                    print(f"  {i}/{n}", flush=True)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", str(FRAMES / "f%04d.png"),
                        "-i", str(AUDIO), "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
                        "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", str(VIDEO)], check=True)
        print("video:", VIDEO)
    if "--sheet" in sys.argv:
        times = [0.3, 1.9, 3.4, 4.5, 5.0, 5.7, 7.0, 8.6, 10.5]
        thumbs = [Image.open(FRAMES / f"f{int(t * FPS):04d}.png").resize((640, 360), Image.LANCZOS) for t in times]
        sheet = Image.new("RGB", (640 * 3, 360 * 3), (30, 30, 34))
        for i, th in enumerate(thumbs):
            sheet.paste(th, ((i % 3) * 640, (i // 3) * 360))
        sheet.save(OUT / "anim_storyboard_v2c.png")
        print("sheet ok")


if __name__ == "__main__":
    main()
