"""v2d animation validation: the v2c scene with its visual defects fixed (separate from anim_test.py, which still
reproduces the v2c video).

Fixes: background re-laid out (scene_bg_v2d), smell lines routed in front of แม่'s face to her nose (never over the mouth),
subtle body language for แม่ (flinch, shoulders, lean, bowl lowered), a moving free arm for ปิ่น, and the magnifier tracking
the bowl while ปิ่น inspects it.

Audio: no narration. The soundtrack is built from the local procedural effects in shorts/sfx.py (a sniff, ปิ่น's gasp,
แม่'s sigh); each character's mouth is driven by the envelope of her own effect, so mouth and sound agree.

    python anim_v2d.py --stills 1 3 4.9 7        -> out/anim_v2d_still_<t>.png
    python anim_v2d.py --render                  -> out/anim_frames_v2d/ (scratch) + out/anim_test_v2d.mp4
    python anim_v2d.py --sheet                   -> out/anim_storyboard_v2d.png
    python anim_v2d.py --check                   -> numeric checks over every frame
"""

from __future__ import annotations

import math
import subprocess
import sys
from array import array
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "shorts"))

import numpy as np  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

import lipsync  # noqa: E402
import sfx  # noqa: E402
import tts  # noqa: E402
from cast import D2R, MOM, feature, mix_expr  # noqa: E402
from figure import ARM_LEN, BODY, figure, pose_lerp, solve_arm  # noqa: E402
from scene_bg_v2d import make_bg  # noqa: E402
from toon import Canvas, spline, yaw  # noqa: E402

OUT = HERE / "out"
FRAMES = OUT / "anim_frames_v2d"
W, H, FPS = 1920, 1080, 30
K = 2.0                                    # figure units -> pixels
LW, LH, OX, OY = 1300, 1010, 650, 262      # per-character layer: size and where the head centre sits
GROUND = 1035
PIN_X, MOM_X = 830, 1300
PIN_Y = GROUND - BODY["pin"]["ground"] * K
MOM_Y = GROUND - BODY["mom"]["ground"] * K
PIN_TH, MOM_TH = 40.0, 46.0
DUR = 11.4
BG = OUT / "anim_bg_v2d.png"
AUDIO = OUT / "anim_sfx_v2d.wav"
VIDEO = OUT / "anim_test_v2d.mp4"
SR = tts.SAMPLE_RATE

# sound events (seconds): a sniff as แม่ leans over the bowl, ปิ่น's gasp, แม่'s sigh as she settles
SNIFF_T, GASP_T, SIGH_T = 3.30, 4.90, 5.95


# --- keyframes ------------------------------------------------------------------------------------------------------------------

def _mp(smile, mw=1.0, skew=0.0, rnd=0.0, wave=0.0):
    return dict(smile=smile, mw=mw, skew=skew, rnd=rnd, wave=wave)


PIN_E = {
    "curious": dict(open=1.08, gaze=(3, 3), brow=(7, 3), mouth="smile", mp=_mp(0.45, 0.8), blush=0.8, tilt=7),
    "peer": dict(open=0.9, lid=0.16, gaze=(4, 3), brow=(9, 2), mouth="smile", mp=_mp(0.3, 0.7), blush=0.9, tilt=9),
    "surprised": dict(open=1.3, gaze=(3, 1), brow=(13, 10), mouth="o", mp=_mp(0, 0.55, rnd=1), open_=0.22, blush=0.5,
                      tilt=-2, pupil=0.85),
    "surprised_mid": dict(open=1.22, gaze=(3, 1), brow=(11, 9), mouth="o", mp=_mp(0, 0.58, rnd=1), open_=0.35, blush=0.6,
                          tilt=0, pupil=0.88),
    "surprised_soft": dict(open=1.16, gaze=(3, 2), brow=(10, 8), mouth="o", mp=_mp(0, 0.6, rnd=0.8), open_=0.12,
                           blush=0.7, tilt=2, pupil=0.9),
    "amazed": dict(open=1.12, gaze=(3, 2), brow=(8, 7), mouth="open_smile", mp=_mp(0.9, 1.05), open_=0.0, blush=1.1,
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


def pin_pose(wr, tip, wl=(59, 234, 10), hint_l=(64, 182, -6)):
    return dict(R=((-66, 164, 30), wr), L=(hint_l, wl), hands=dict(R=("grip", 0), L=("relaxed", 0)),
                grip=dict(side="R", item="lens", tip=tip), late="R")


def mom_pose(z, y=138):
    """Both hands under the bowl; the bowl follows the wrists the IK actually reaches (nothing floats)."""
    wr, wl = [solve_arm((s * 52, 126, -2), (s * 52, 160, 48), (s * 32, y, z), *ARM_LEN["mom"])[1] for s in (-1, 1)]
    mid = tuple((a + b) / 2 for a, b in zip(wr, wl))
    return dict(R=((-52, 160, 48), wr), L=((52, 160, 48), wl), hands=dict(R=("cup", -6), L=("cup", 6)),
                bowl=(0, mid[1] - 10, mid[2] + 8))


# t, expression, pose, lean (deg), head turn (deg), head nod (units), shoulder shrug (units)
PIN_KEYS = [
    (0.0, "curious", pin_pose((-46, 124, 66), (-14, 116, 118)), 3.0, PIN_TH + 2, 0.0, 0.0),
    (1.9, "curious", pin_pose((-40, 124, 96), (-8, 114, 150), wl=(58, 232, 12)), 5.0, PIN_TH + 3, 1.0, 0.0),
    (4.4, "peer", pin_pose((-40, 128, 98), (-6, 120, 154), wl=(58, 230, 14)), 6.5, PIN_TH + 3, 2.0, 0.0),
    (4.95, "surprised", pin_pose((-44, 126, 80), (-12, 116, 132), wl=(10, 152, 44), hint_l=(58, 176, 4)), -1.5,
     PIN_TH - 5, -3.0, 1.5),
    (5.6, "surprised_mid", pin_pose((-44, 127, 79), (-12, 118, 131), wl=(12, 156, 42), hint_l=(58, 178, 4)), 0.0,
     PIN_TH - 4, -2.2, 1.0),
    (6.4, "surprised_soft", pin_pose((-44, 128, 78), (-12, 120, 130), wl=(22, 172, 36), hint_l=(62, 182, 4)), 0.5,
     PIN_TH - 3, -1.5, 0.5),
    (8.6, "amazed", pin_pose((-46, 130, 64), (-14, 122, 118), wl=(50, 206, 34), hint_l=(66, 190, 4)), 1.5, PIN_TH, 0.0, 0.0),
    (DUR, "amazed", pin_pose((-46, 130, 64), (-14, 122, 118), wl=(54, 214, 26), hint_l=(65, 188, 0)), 1.0, PIN_TH + 1, 0.0,
     0.0),
]
MOM_KEYS = [
    (0.0, "calm", mom_pose(90), 0.0, MOM_TH, 0.0, 0.0),
    (2.4, "notice", mom_pose(92), 0.0, MOM_TH + 1, 1.0, 0.0),
    (3.7, "sniff", mom_pose(92), 2.0, MOM_TH + 4, 2.0, 0.0),
    (4.35, "wince", mom_pose(93, 140), -1.5, MOM_TH, 1.0, 1.4),
    (4.95, "wince", mom_pose(94, 143), -5.0, MOM_TH - 6, 0.5, 3.0),        # the flinch: shoulders up, quick lean back
    (5.7, "wince", mom_pose(94, 145), -3.8, MOM_TH - 5, 0.5, 2.2),
    (7.2, "polite", mom_pose(94, 148), -6.5, MOM_TH - 12, -0.5, 0.8),      # shoulders drop with the sigh, bowl lowered
    (9.2, "sheepish", mom_pose(94, 150), -6.0, MOM_TH - 9, 0.0, 0.4),
    (DUR, "sheepish", mom_pose(94, 150), -5.5, MOM_TH - 8, 0.0, 0.3),
]
# (start, duration): irregular on purpose, one double blink after the surprise
PIN_BLINKS = [(1.15, 0.17), (3.3, 0.2), (6.95, 0.15), (7.18, 0.15), (9.7, 0.18)]
MOM_BLINKS = [(0.8, 0.16), (2.2, 0.18), (4.65, 0.2), (7.9, 0.17), (10.4, 0.15)]


def _ease(u):
    return u * u * (3 - 2 * u)


def _ramp(t, a, b):
    return _ease(min(1.0, max(0.0, (t - a) / (b - a))))


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
                head_th=L(a[4], b[4]), nod=L(a[5], b[5]), shrug=L(a[6], b[6]))


def blink_at(t, events):
    for b, dur in events:
        d = (t - b) / dur
        if 0 <= d < 1:
            return d / 0.35 if d < 0.35 else (1.0 if d < 0.5 else 1 - (d - 0.5) / 0.5)
    return 0.0


# --- audio ----------------------------------------------------------------------------------------------------------------------

def build_audio(write=False):
    """Sniff + gasp + sigh on a silent bed. Returns (mixed, pin_only, mom_only) as 16-bit sample arrays."""
    n = int(DUR * SR)

    def lane(events):
        buf = [0] * n
        for name, t, gain in events:
            for i, v in enumerate(sfx.make(name)):
                j = int(t * SR) + i
                if j < n:
                    buf[j] += int(v * gain)
        return buf

    pin = lane([("gasp", GASP_T, 1.0)])
    mom = lane([("sigh", SIGH_T, 1.0)])
    sniff = lane([("whoosh", SNIFF_T, 0.4)])
    clip = lambda xs: array("h", [max(-32000, min(32000, x)) for x in xs])
    mixed = clip([a + b + c for a, b, c in zip(pin, mom, sniff)])
    if write:
        tts.write_wav(AUDIO, mixed)
    return mixed, clip(pin), clip(mom)


# --- scene geometry -------------------------------------------------------------------------------------------------------------

def _lean_pt(pt, lean, pivot_y):
    c, s = math.cos(math.radians(lean)), math.sin(math.radians(lean))
    x, y = pt[0], pt[1] - pivot_y
    return x * c - y * s, pivot_y + x * s + y * c


def lens_center(st):
    q = yaw(st["pose"]["grip"]["tip"], PIN_TH * D2R)
    x, y = _lean_pt((q[0], q[1]), st["lean"], BODY["pin"]["hip"][1])
    return PIN_X + x * K, PIN_Y + y * K


def _mom_head_pt(st, y_units):
    (px, py), _ = feature(MOM, 0, y_units, st["head_th"] * D2R)
    x, y = _lean_pt((px, py + st["nod"]), st["lean"], BODY["mom"]["hip"][1])
    return MOM_X - x * K, MOM_Y + y * K            # แม่ faces screen-left, so x is mirrored


def mom_points(st):
    """Screen positions of the bowl, แม่'s nose and mouth."""
    q = yaw(st["pose"]["bowl"], MOM_TH * D2R)
    bx, by = _lean_pt((q[0], q[1]), st["lean"], BODY["mom"]["hip"][1])
    return (MOM_X - bx * K, MOM_Y + by * K), _mom_head_pt(st, MOM["nose_y"]), _mom_head_pt(st, MOM["mouth_y"])


def aroma_lines(bowl, nose, t):
    """Three smell lines: they rise straight from the bowl, then curve in at nose height from the front, ending in the
    air a little before the nose tip. The route never crosses the mouth (it stays on the bowl side of the face)."""
    lines = []
    for k, off in enumerate((-14, 0, 14)):
        a = (bowl[0] + off * 0.7, bowl[1] - 24)
        b = (nose[0] - 34 + off * 0.35, nose[1] + 4)
        pts = []
        for i in range(12):
            u = i / 11
            wob = 7 * math.sin(u * 7 + t * 5.5 + k * 1.9) * (0.3 + 0.7 * u) * (1 - u ** 3)
            pts.append((a[0] + (b[0] - a[0]) * u ** 2.4 + wob, a[1] + (b[1] - a[1]) * u))
        lines.append(pts)
    return lines


def aroma(frame, bowl, nose, amt, t):
    if amt < 0.02:
        return
    lines = aroma_lines(bowl, nose, t)
    xs = [p[0] for ln in lines for p in ln]
    ys = [p[1] for ln in lines for p in ln]
    x0, y0, x1, y1 = int(min(xs) - 30), int(min(ys) - 30), int(max(xs) + 30), int(max(ys) + 30)
    cv = Canvas(x1 - x0, y1 - y0, ss=3)
    cv.push(-x0, -y0)
    for k, pts in enumerate(lines):
        cv.stroke(spline(pts, n=4), (168, 198, 104), 4.6 - k * 0.5, alpha=int(200 * amt * (1 - 0.15 * k)))
    cv.pop()
    frame.alpha_composite(cv.result(), (x0, y0))


def track_lens(ps, bowl, t):
    """While ปิ่น inspects the bowl, keep the glass over it (it follows the bowl as แม่ leans and lowers it); afterwards it
    only loosely follows. The hand moves with the lens, and the wrist is kept within reach so the handle never stretches."""
    w = _ramp(t, 1.0, 1.9) * (1 - 0.65 * _ramp(t, 4.5, 5.2))
    if w <= 0.001:
        return
    target = (bowl[0] - 50, bowl[1] - 12)
    sh = np.array((-BODY["pin"]["shoulder"][0], BODY["pin"]["shoulder"][1], BODY["pin"]["shoulder"][2]), float)
    lim = sum(ARM_LEN["pin"]) * 0.965
    for _ in range(2):
        cur = lens_center(ps)
        dx = max(-14, min(14, (target[0] - cur[0]) / K / math.cos(PIN_TH * D2R) * w))
        dy = max(-14, min(14, (target[1] - cur[1]) / K * w))
        hint, wr = ps["pose"]["R"]
        tip = ps["pose"]["grip"]["tip"]
        wr2, tip2 = np.array((wr[0] + dx, wr[1] + dy, wr[2]), float), np.array((tip[0] + dx, tip[1] + dy, tip[2]), float)
        v = wr2 - sh
        d = float(np.linalg.norm(v))
        if d > lim:
            shift = v / d * lim - v
            wr2, tip2 = wr2 + shift, tip2 + shift
        ps["pose"]["R"] = (hint, tuple(float(x) for x in wr2))
        ps["pose"]["grip"] = dict(ps["pose"]["grip"], tip=tuple(float(x) for x in tip2))


def magnify(frame, c, r=24 * K, mag=1.7, source=None):
    """Replace the glass interior with a magnified crop of what is behind it, so the lens does its job."""
    ri = int(r - 5.5)
    half = int(ri / mag)
    cx, cy = int(c[0]), int(c[1])
    crop = (source or frame).crop((cx - half, cy - half, cx + half, cy + half)).resize((ri * 2, ri * 2), Image.LANCZOS)
    mask = Image.new("L", (ri * 8, ri * 8), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, ri * 8 - 1, ri * 8 - 1), fill=255)
    mask = mask.resize((ri * 2, ri * 2), Image.LANCZOS)
    frame.paste(crop.convert("RGB"), (cx - ri, cy - ri), mask)
    ImageDraw.Draw(frame).arc((cx - ri + 5, cy - ri + 5, cx + ri - 5, cy + ri - 5), 200, 250, fill=(255, 255, 255), width=3)


# --- frame ----------------------------------------------------------------------------------------------------------------------

def layer(cid, th, flip, st, blink, talk, pregnant, t):
    """One character on a transparent layer; subtle breathing and head float keep them alive between key poses."""
    br = math.sin(2 * math.pi * t / 3.7 + (0.0 if cid == "pin" else 1.3))
    cv = Canvas(LW, LH, ss=2)
    cv.push(OX, OY, scale=K, flip=flip)
    figure(cv, cid, th * D2R, st["pose"], st["expr"], pregnant=pregnant, lean=st["lean"] + 0.3 * br, talk=talk, blink=blink,
           head_th=st["head_th"] * D2R, head_dy=st["nod"] + 0.7 * br, shrug=st["shrug"])
    cv.pop()
    return cv.result()


_BG = None
_TRACKS = None


def _init():
    global _BG, _TRACKS
    _BG = Image.open(BG).convert("RGBA")
    _, pin, mom = build_audio()
    _TRACKS = (lipsync.mouth_track(pin, FPS), lipsync.mouth_track(mom, FPS))


def frame_state(f):
    """Everything that defines frame f (also used by the numeric checks)."""
    t = f / FPS
    ms = state(MOM_KEYS, t, MOM_E)
    bowl, nose, mouth = mom_points(ms)
    ps = state(PIN_KEYS, t, PIN_E)
    track_lens(ps, bowl, t)
    tip = ps["pose"]["grip"]["tip"]
    ps["pose"]["grip"] = dict(ps["pose"]["grip"], tip=(tip[0] + 0.9 * math.sin(t * 4.1), tip[1] + 0.9 * math.sin(t * 3.3 + 1),
                                                       tip[2]))
    return t, ps, ms, bowl, nose, mouth


def frame_at(f):
    if _BG is None:
        _init()
    t, ps, ms, bowl, nose, mouth = frame_state(f)
    (ps_shape, ps_level), (ms_shape, ms_level) = _TRACKS[0][min(f, len(_TRACKS[0]) - 1)], _TRACKS[1][min(f, len(_TRACKS[1]) - 1)]
    pin_talk = ps_level if ps_shape >= 1 else 0.0
    mom_talk = 0.5 * ms_level if ms_shape >= 1 else 0.0           # an exhale: the mouth only parts a little
    img = _BG.copy()
    img.alpha_composite(layer("mom", MOM_TH, True, ms, blink_at(t, MOM_BLINKS), mom_talk, True, t),
                        (int(MOM_X - OX), int(MOM_Y - OY)))
    amt = _ramp(t, 2.6, 4.2) * (1 - 0.6 * _ramp(t, 8.6, 10.2))
    aroma(img, bowl, nose, amt, t)
    pin_blink = 0.0 if 4.7 < t < 6.1 else blink_at(t, PIN_BLINKS)
    behind = img.convert("RGB")                       # what is behind the glass: the room, แม่ and the bowl
    img.alpha_composite(layer("pin", PIN_TH, False, ps, pin_blink, pin_talk, False, t), (int(PIN_X - OX), int(PIN_Y - OY)))
    out = img.convert("RGB")
    magnify(out, lens_center(ps), source=behind)
    return out


def _save(f):
    frame_at(f).save(FRAMES / f"f{f:04d}.png")
    return f


def main():
    OUT.mkdir(exist_ok=True)
    build_audio(write=True)
    make_bg()
    n = int(DUR * FPS)
    if "--stills" in sys.argv:
        _init()
        for tt in sys.argv[sys.argv.index("--stills") + 1:]:
            frame_at(int(float(tt) * FPS)).save(OUT / f"anim_v2d_still_{float(tt):g}.png")
        return
    if "--render" in sys.argv:
        FRAMES.mkdir(exist_ok=True)
        with Pool(6, initializer=_init) as pool:
            for i, _ in enumerate(pool.imap_unordered(_save, range(n))):
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
        sheet.save(OUT / "anim_storyboard_v2d.png")
        print("sheet ok")
    if "--check" in sys.argv:
        check(n)


def check(n):
    """Numeric checks over all frames: smell route vs mouth, lens vs bowl, handle length, limb lengths, reach."""
    min_mouth = 1e9
    min_nose = 1e9
    lens_gap, handle, arm_err, pulled = [], [], 0.0, 0.0
    for f in range(n):
        t, ps, ms, bowl, nose, mouth = frame_state(f)
        if _ramp(t, 2.6, 4.2) > 0.02:
            for ln in aroma_lines(bowl, nose, t):
                for p in ln:
                    min_mouth = min(min_mouth, math.hypot(p[0] - mouth[0], p[1] - mouth[1]))
                    min_nose = min(min_nose, math.hypot(p[0] - nose[0], p[1] - nose[1]))
        if 2.0 <= t <= 4.4:
            c = lens_center(ps)
            lens_gap.append(math.hypot(c[0] - bowl[0], c[1] - bowl[1]))
        hint, wr = ps["pose"]["R"]
        handle.append(float(np.linalg.norm(np.subtract(ps["pose"]["grip"]["tip"], wr))))
        for st, cid in ((ps, "pin"), (ms, "mom")):
            l1, l2 = ARM_LEN[cid]
            for side in ("R", "L"):
                sx = -1 if side == "R" else 1
                sh = (BODY[cid]["shoulder"][0] * sx, BODY[cid]["shoulder"][1] - st["shrug"], BODY[cid]["shoulder"][2])
                hnt, wt = st["pose"][side]
                el, wr2 = solve_arm(sh, hnt, wt, l1, l2)
                arm_err = max(arm_err, abs(np.linalg.norm(np.subtract(el, sh)) - l1), abs(np.linalg.norm(np.subtract(wr2, el)) - l2))
                pulled = max(pulled, float(np.linalg.norm(np.subtract(wr2, wt))))
    print(f"smell line -> mouth, closest approach: {min_mouth:.0f} px (mouth is ~{18 * K:.0f} px below the nose)")
    print(f"smell line -> nose tip, closest approach: {min_nose:.0f} px")
    print(f"lens centre -> bowl centre while inspecting (2.0-4.4 s): {min(lens_gap):.0f}-{max(lens_gap):.0f} px "
          f"(bowl radius ~{38 * K * 0.9:.0f} px, lens radius {24 * K:.0f} px)")
    print(f"lens handle length (wrist->lens, units): {min(handle):.1f}-{max(handle):.1f}")
    print(f"max limb-length error: {arm_err:.4f}; max wrist pull-back by reach limit: {pulled:.3f}")


if __name__ == "__main__":
    main()
