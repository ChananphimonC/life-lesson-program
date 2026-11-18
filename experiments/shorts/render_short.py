"""Scene Script JSON -> 9:16 (or 16:9 / 1:1) cartoon Short MP4.

    python render_short.py scripts/flood_island.json --tts edge --frames
    python render_short.py scripts/floating_market_demo.json            # Gemini TTS first, edge-tts fallback

Pipeline: per-line TTS (cached) -> timeline -> mixed WAV (voices + SFX) -> per-line amplitude mouth shapes
-> frames (background + fx + layered characters, only the speaker's mouth moves + props + subtitle) -> ffmpeg.

Script extras beyond the basic Scene Script (all optional):
  scene: lead, tail, min_dur, fx[], props[], sfx[], camera{zoom:[a,b], focus:[x,y]},
         cuts[{at_frac, background, characters, fx, camera}]  (the look changes part-way through one narration)
         background "split:a|b|Left label|Right label" = two framed panels side by side
  character: x / pos (x may be [from, to] with x_span), y (feet, fraction of H), scale, look, hop (+hop_rate), from_line / until_line,
             arms (pose name) / anim {arms:[a,b], period} (eased arm animation)
  line: say (TTS text if it differs from the subtitle), sfx_voice (a sound instead of TTS), pause (beat after),
        outfit (speaker's outfit from this line), set {char: outfit}, sfx (cue at line start), sub=false
  props/sfx items may use "line": n so their "at" is relative to that line's start, and dur "line".
"""

from __future__ import annotations

import argparse
import json
import math
import random
import subprocess
import sys
import time
from array import array
from pathlib import Path

from functools import lru_cache

from PIL import Image, ImageDraw, ImageFilter

import backgrounds
import backgrounds_flood  # noqa: F401  (registers its backgrounds + fx)
import backgrounds_knowledge  # noqa: F401  (studio / study_room)
import backgrounds_money  # noqa: F401  (platform, street, rooms, market)
import backgrounds_city  # noqa: F401  (train cars, wholesale, kitchen, stall, cafe + window fx)
import character_art as CA
import gemini_guard
import lipsync
import props
import sfx
import subtitles
import tts
from life_lesson.config import get_settings

HERE = Path(__file__).resolve().parent
OUT_ROOT = HERE / "output"
FPS = 30
ASPECTS = {"9:16": (1080, 1920), "16:9": (1920, 1080), "1:1": (1080, 1080)}
POS_X = {"left": 0.27, "center": 0.5, "right": 0.73}
GAP = 0.3  # a natural breath between speakers
CHAR_WIDTH_FRAC = 0.58
SUB_TOP, SUB_BOTTOM = 0.705, 0.89  # subtitle band; the bottom 11% stays clear for the Shorts UI
SCREEN_PROPS = {"caption", "news_bar", "fade_black", "phone_screen", "island_badge", "notif", "budget", "bars", "pair", "subscribe"}


def load_script(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    for key in ("id", "aspect", "scenes"):
        if key not in data:
            sys.exit(f"{path.name}: missing '{key}'")
    if data["aspect"] not in ASPECTS:
        sys.exit(f"{path.name}: aspect must be one of {', '.join(ASPECTS)}")
    for si, sc in enumerate(data["scenes"], 1):
        ids = {c["id"] for c in sc.get("characters", [])} | set(sc.get("offscreen", []))
        for li, line in enumerate(sc.get("lines", []), 1):
            who = line["speaker"]
            if who not in ids and CA.load_character(who)["draw"]["kind"] != "none":
                sys.exit(f"scene {si} line {li}: speaker '{who}' is not in this scene's characters")
    return data


def _resolve(item: dict, lines: list[dict], scene_start: float) -> dict:
    """Turn line-relative timing into scene-relative timing."""
    it = dict(item)
    if "line" in it:
        ln = lines[it["line"] - 1]
        length = ln["end"] - ln["start"]
        it["at"] = ln["start"] - scene_start + it.get("at", 0.0) + it.get("at_frac", 0.0) * length
        if it.get("dur") == "line":
            it["dur"] = ln["end"] - ln["start"] + it.get("extra", 0.3)
        elif "dur_frac" in it:
            it["dur"] = it["dur_frac"] * length
    return it


def build_timeline(data: dict, mode: str) -> tuple[list[dict], float]:
    settings = get_settings()
    t, items, n = 0.0, [], 0
    for si, sc in enumerate(data["scenes"]):
        start = t
        t += sc.get("lead", 0.12)
        scene_lines = []
        for line in sc.get("lines", []):
            n += 1
            ch = CA.load_character(line["speaker"])
            if line.get("sfx_voice"):
                samples, engine = sfx.make(line["sfx_voice"]), "sfx"
            else:
                path, engine = tts.synth_line(settings, data["id"], n, ch, line.get("say", line["text"]), mode)
                samples = tts.read_wav(path)
            dur = len(samples) / tts.SAMPLE_RATE
            it = {"n": n, "scene": si, "speaker": line["speaker"], "text": line["text"], "start": t, "end": t + dur,
                  "engine": engine, "samples": samples, "sub": line.get("sub", True),
                  "outfit": line.get("outfit"), "set": line.get("set", {}), "emotion": line.get("emotion", ""),
                  "chorus": line.get("chorus", [])}
            items.append(it)
            scene_lines.append(it)
            print(f"  {n:02d} s{si + 1} [{line['speaker']:12s}] {engine:6s} {dur:4.1f}s  {line['text'][:44]}", flush=True)
            t += dur + GAP + line.get("pause", 0.0)
        t = max(t - GAP + sc.get("tail", 0.25), start + sc.get("min_dur", 0.0))
        sc["_start"], sc["_end"], sc["_lines"] = start, t, scene_lines
        sc["_props"] = [_resolve(p, scene_lines, start) for p in sc.get("props", [])]
        sc["_sfx"] = [_resolve(s, scene_lines, start) for s in sc.get("sfx", [])]
        for ln, line in zip(scene_lines, sc.get("lines", [])):
            if line.get("sfx"):
                sc["_sfx"].append({"name": line["sfx"], "at": ln["start"] - start, "vol": line.get("sfx_vol", 0.6)})
    return items, t


def mix_audio(data: dict, items: list[dict], total: float, path: Path) -> None:
    n = int(total * tts.SAMPLE_RATE) + 2
    acc = [0.0] * n
    for it in items:
        off = int(it["start"] * tts.SAMPLE_RATE)
        for i, s in enumerate(it["samples"]):
            if off + i < n:
                acc[off + i] += s
    for sc in data["scenes"]:
        for cue in sc["_sfx"]:
            samples = sfx.water(cue.get("dur", 6.0)) if cue["name"] == "water" else sfx.make(cue["name"])
            off = int((sc["_start"] + cue.get("at", 0.0)) * tts.SAMPLE_RATE)
            vol = cue.get("vol", 0.5)
            for i, s in enumerate(samples):
                if 0 <= off + i < n:
                    acc[off + i] += s * vol
    peak = max(1.0, max(abs(v) for v in acc) / 32000)
    path.parent.mkdir(parents=True, exist_ok=True)
    tts.write_wav(path, array("h", (int(v / peak) for v in acc)))


class Renderer:
    def __init__(self, data: dict, items: list[dict], W: int, H: int):
        self.data, self.items, self.W, self.H = data, items, W, H
        self.base_scale = CHAR_WIDTH_FRAC * min(W, H * 9 / 16) / CA.CW
        for it in items:
            it["track"] = lipsync.mouth_track(it["samples"], FPS)
            ch = CA.load_character(it["speaker"])
            it["card"] = (subtitles.card(it["text"], ch["name"], CA.rgb(ch["subtitle_color"]), W)
                          if it["sub"] and data.get("subtitles", True) else None)
        self.bgs = {}
        rnd = random.Random(7)
        self.phase = {}
        for sc in data["scenes"]:
            for name in {sc["background"], *[c["background"] for c in sc.get("cuts", []) if "background" in c]}:
                self._load_bg(name)
            for c in sc.get("characters", []) + [c for cut in sc.get("cuts", []) for c in cut.get("characters", [])]:
                self.phase.setdefault(c["id"], rnd.uniform(0.3, 3.0))
            self._outfit_track(sc)

    def _load_bg(self, name: str) -> None:
        if name in self.bgs:
            return
        if name.startswith("split:"):                       # "split:left_bg|right_bg|Left name|Right name": two framed panels
            a, b, *labels = name[len("split:"):].split("|")
            self.bgs[name] = self._split(a, b, labels)
        else:
            self.bgs[name] = self._soften(backgrounds.get(name, self.W, self.H))

    def _split(self, a: str, b: str, labels: list[str]) -> Image.Image:
        W, H, gap = self.W, self.H, 18
        half = (W - 3 * gap) // 2
        base = Image.new("RGB", (W, H), (46, 36, 42))
        for i, name in enumerate((a, b)):
            panel = self._soften(backgrounds.get(name, half, H)).crop((0, gap, half, H - gap))
            mask = Image.new("L", panel.size, 0)
            ImageDraw.Draw(mask).rounded_rectangle((0, 0, panel.width - 1, panel.height - 1), 34, fill=255)
            x0 = gap + i * (half + gap)
            ImageDraw.Draw(base).rounded_rectangle((x0 - 5, gap - 5, x0 + half + 5, H - gap + 5), 38, fill=(255, 244, 226))
            base.paste(panel, (x0, gap), mask)
            if i < len(labels) and labels[i]:
                f = subtitles.font(int(H * 0.05))
                d = ImageDraw.Draw(base)
                w = int(f.getlength(labels[i])) + int(H * 0.06)
                col = ((125, 187, 106), (110, 182, 234))[i]
                d.rounded_rectangle((x0 + 18, gap + 18, x0 + 18 + w, gap + 18 + int(H * 0.075)), 24, fill=col, outline=(118, 88, 72), width=4)
                d.text((x0 + 18 + w / 2, gap + 18 + int(H * 0.0375) + 2), labels[i], font=f, fill=(255, 255, 255), anchor="mm",
                       stroke_width=3, stroke_fill=(118, 88, 72))
        return base

    def _soften(self, bg: Image.Image) -> Image.Image:
        if not self.data.get("soft", True):
            return bg
        soft = bg.filter(ImageFilter.GaussianBlur(2.2))
        vignette = Image.radial_gradient("L").resize(bg.size).point(lambda v: max(0, v - 120) * 38 // 135)
        return Image.composite(Image.new("RGB", bg.size, (30, 22, 34)), soft, vignette)

    def _outfit_track(self, sc):
        """Per character: [(abs time, outfit)] from the scene default and line-level changes."""
        track = {c["id"]: [(sc["_start"], c.get("outfit", "default"))] for c in sc.get("characters", [])}
        for ln in sc["_lines"]:
            if ln["outfit"] and ln["speaker"] in track:
                track[ln["speaker"]].append((ln["start"], ln["outfit"]))
            for cid, outfit in ln["set"].items():
                track.setdefault(cid, []).append((ln["start"], outfit))
        sc["_outfits"] = track

    def _visible(self, c, sc, t):
        lines = sc["_lines"]
        if "from_line" in c and t < lines[c["from_line"] - 1]["start"]:
            return False
        if "until_line" in c and t >= lines[c["until_line"] - 1]["end"] + 0.2:
            return False
        return True

    def _segment(self, sc, lt, dur):
        """The scene as it looks at scene-time lt: base scene overridden by the latest 'cuts' entry, plus that cut's span."""
        cuts = sorted(sc.get("cuts", []), key=lambda c: c["at_frac"])
        eff, t0, t1 = dict(sc), 0.0, dur
        for i, cut in enumerate(cuts):
            if lt >= cut["at_frac"] * dur - 1e-6:
                eff.update({k: v for k, v in cut.items() if k != "at_frac"})
                t0 = cut["at_frac"] * dur
                t1 = cuts[i + 1]["at_frac"] * dur if i + 1 < len(cuts) else dur
            elif i == 0:
                t1 = cut["at_frac"] * dur
        return eff, t0, max(0.05, t1 - t0)

    @staticmethod
    def _affine(spr, sy, angle, pivot, dx, dy):
        """Breathing (vertical scale about the feet) + a tiny lean, with sub-pixel placement: no jitter between frames."""
        phi = math.radians(angle)
        c, s_ = math.cos(phi), math.sin(phi)
        a, b, d, e = c, -s_ / sy, s_, c / sy
        px, py = pivot
        coeffs = (a, b, px - a * (px + dx) - b * (py + dy), d, e, py - d * (px + dx) - e * (py + dy))
        return spr.transform(spr.size, Image.AFFINE, coeffs, resample=Image.BICUBIC)

    @staticmethod
    @lru_cache(maxsize=None)
    def _shadow(w: int, h: int) -> Image.Image:
        k = 3
        big = Image.new("L", (w * k, h * k), 0)
        ImageDraw.Draw(big).ellipse((0, 0, w * k - 1, h * k - 1), fill=255)
        mask = big.resize((w, h), Image.LANCZOS).filter(ImageFilter.GaussianBlur(max(1, h // 5))).point(lambda v: int(v * 0.26))
        out = Image.new("RGBA", (w, h), (70, 48, 56, 0))
        out.putalpha(mask)
        return out

    def frame(self, t: float) -> Image.Image:
        scenes = self.data["scenes"]
        sc = next((s for s in scenes if t < s["_end"]), scenes[-1])
        lt = t - sc["_start"]
        dur = sc["_end"] - sc["_start"]
        eff, seg0, seglen = self._segment(sc, lt, dur)
        img = self.bgs[eff["background"]].copy()
        for fx in eff.get("fx", []):
            params = {k: v for k, v in fx.items() if k != "name"}
            img = backgrounds.FX[fx["name"]](img, lt, dur, self.W, self.H, **params)
        active = next((it for it in sc["_lines"] if it["start"] <= t < it["end"]), None)
        world_props = [p for p in sc["_props"] if p["type"] not in SCREEN_PROPS]
        for p in [p for p in world_props if p.get("behind")]:
            img = props.draw(img, p, lt, self.W, self.H)
        chars = [c for c in eff.get("characters", []) if self._visible(c, sc, t)]
        lay = self.data.get("layout", {})
        shift, grow = lay.get("y_shift", 0.0), lay.get("char_scale", 1.0)
        seg_u = (lt - seg0) / seglen
        for c in sorted(chars, key=lambda c: c.get("y", backgrounds.GROUND) + shift):
            ch = CA.load_character(c["id"])
            later = [o for (ts, o) in sc["_outfits"].get(c["id"], []) if sc["_start"] < ts <= t]
            outfit = later[-1] if later else c.get("outfit", "default")
            speaking = active is not None and (active["speaker"] == c["id"] or c["id"] in active["chorus"])
            fi = int((t - active["start"]) * FPS) if speaking else 0
            track = active["track"] if speaking else None
            shape, level = track[min(fi, len(track) - 1)] if speaking else (0, 0.0)
            smooth_level = (sum(track[max(0, min(fi, len(track) - 1) - k)][1] for k in range(6)) / 6) if speaking else 0.0
            scale = round(self.base_scale * grow * c.get("scale", 1.0) * ch["draw"].get("scale_mul", 1.0), 3)
            xs = c.get("x", POS_X.get(c.get("pos", "center"), 0.5))
            moving = 0.0
            if isinstance(xs, list):                                    # walks from xs[0] to xs[1] during c['x_span'] of the segment
                a_, b_ = c.get("x_span", [0.0, 1.0])
                u = min(1.0, max(0.0, (seg_u - a_) / max(1e-6, b_ - a_)))
                u = u * u * (3 - 2 * u)
                x_frac = xs[0] + (xs[1] - xs[0]) * u
                moving = 1.0 if 0.0 < u < 1.0 else 0.0
            else:
                x_frac = xs
            look = c.get("look", 1 if x_frac < 0.5 else -1 if x_frac > 0.5 else 0)
            blink = ((t + self.phase[c["id"]]) % 3.4) < 0.14
            arms = c.get("arms")
            anim = c.get("anim")
            if anim:                                                    # eased back-and-forth between two arm poses
                a_pose, b_pose = anim["arms"]
                k = round(8 * (0.5 - 0.5 * math.cos(2 * math.pi * (t + self.phase[c["id"]]) / anim.get("period", 1.2))))
                arms = f"{a_pose}>{b_pose}@{k}"
            spr = CA.sprite(c["id"], outfit, look, shape, blink, scale, arms)
            ph = t + self.phase[c["id"]]
            toward = 1 if x_frac < 0.5 else -1
            sy = 1 + 0.005 * math.sin(2 * math.pi * ph / 3.4) + 0.006 * smooth_level
            angle = 0.35 * math.sin(2 * math.pi * ph / 6.1) - toward * 0.7 * smooth_level
            bob = 0.0
            if moving:                                                  # a soft walking bounce, no leg motion
                step = 2 * math.pi * t * 2.1
                bob = abs(math.sin(step)) * 0.016 * spr.height
                angle += 1.0 * math.sin(step)
            if c.get("hop"):                                           # excited little hops (fraction of H), eased
                bob += abs(math.sin(math.pi * (t * c.get("hop_rate", 1.4) + self.phase[c["id"]]))) ** 1.5 * c["hop"] * self.H
            feet_y = (c.get("y", backgrounds.GROUND) + shift) * self.H
            top_f = feet_y + (CA.CH - CA.GROUND_Y) * scale - spr.height - bob
            left_f = x_frac * self.W - spr.width / 2
            ix, iy = math.floor(left_f), math.floor(top_f)
            pivot = (spr.width / 2, (CA.GROUND_Y / CA.CH) * spr.height)
            spr = self._affine(spr, sy, angle, pivot, left_f - ix, top_f - iy)
            if ch["draw"].get("style") == "cute":
                sw, sh = int(spr.width * 0.5), max(6, int(spr.height * 0.045))
                img.paste(self._shadow(sw, sh), (int(x_frac * self.W - sw / 2), int(feet_y - sh * 0.45)), self._shadow(sw, sh))
            img.paste(spr, (ix, iy), spr)
        for p in [p for p in world_props if not p.get("behind")]:
            img = props.draw(img, p, lt, self.W, self.H)
        cam = eff.get("camera", sc.get("camera", {"zoom": [1.0, 1.05], "focus": [0.5, 0.5]}))
        if cam:
            u = min(1.0, max(0.0, (lt - seg0) / seglen))
            u = u * u * (3 - 2 * u)
            z = cam["zoom"][0] + (cam["zoom"][1] - cam["zoom"][0]) * u
            fx_, fy_ = cam.get("focus", (0.5, 0.5))
            cw, chh = self.W / z, self.H / z
            x0 = min(max(0.0, fx_ * self.W - cw / 2), self.W - cw)
            y0 = min(max(0.0, fy_ * self.H - chh / 2), self.H - chh)
            img = img.resize((self.W, self.H), Image.BILINEAR, box=(x0, y0, x0 + cw, y0 + chh))
        for p in [p for p in sc["_props"] if p["type"] in SCREEN_PROPS and p["type"] != "fade_black"]:
            img = props.draw(img, p, lt, self.W, self.H)
        if active is not None and active["card"] is not None and t < active["end"] + 0.12:
            card = active["card"]
            top = int(SUB_TOP * self.H)
            if top + card.height > SUB_BOTTOM * self.H:
                top = int(SUB_BOTTOM * self.H - card.height)
            img.paste(card, (0, top), card)
        for p in [p for p in sc["_props"] if p["type"] == "fade_black"]:
            img = props.draw(img, p, lt, self.W, self.H)
        return img


def encode(r: Renderer, total: float, audio: Path, out: Path, ffmpeg: str) -> None:
    n = int(math.ceil(total * FPS))
    cmd = [ffmpeg, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{r.W}x{r.H}",
           "-r", str(FPS), "-i", "-", "-i", str(audio), "-map", "0:v:0", "-map", "1:a:0",
           "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", str(out)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    started = time.time()
    try:
        for f in range(n):
            proc.stdin.write(r.frame(f / FPS).tobytes())
            if f % (FPS * 10) == 0:
                print(f"  frame {f / FPS:5.1f}s / {total:.1f}s ({time.time() - started:.0f}s)", flush=True)
    finally:
        proc.stdin.close()
        code = proc.wait()
    if code:
        sys.exit(f"ffmpeg failed ({code})")


def contact_sheet(r: Renderer, items: list[dict], total: float, out: Path, cols: int = 8) -> None:
    """Sample frames from the renderer: the middle of every line (+ first/last frame)."""
    times = [0.1] + [(it["start"] + it["end"]) / 2 for it in items] + [total - 0.1]
    thumbs = [r.frame(min(t, total - 0.04)).resize((r.W // 4, r.H // 4), Image.LANCZOS) for t in times]
    rows = math.ceil(len(thumbs) / cols)
    sheet = Image.new("RGB", (cols * thumbs[0].width, rows * thumbs[0].height), (20, 20, 24))
    for i, th in enumerate(thumbs):
        sheet.paste(th, ((i % cols) * th.width, (i // cols) * th.height))
    sheet.save(out)
    print(f"contact sheet: {out}")


def voice_status(data: dict) -> tuple[int, int]:
    """(lines already voiced by Gemini, total spoken lines) -- read from the cache, no API calls."""
    done = total = n = 0
    for sc in data["scenes"]:
        for line in sc.get("lines", []):
            n += 1
            if line.get("sfx_voice"):
                continue
            total += 1
            ch = CA.load_character(line["speaker"])
            done += bool(tts.find_cached(data["id"], n, ch, line.get("say", line["text"]), "gemini"))
    return done, total


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("script", type=Path)
    ap.add_argument("--tts", choices=["auto", "gemini", "edge"], default="auto")
    ap.add_argument("--frames", action="store_true", help="write a contact sheet of sample frames")
    ap.add_argument("--no-video", action="store_true", help="only TTS + timeline (+ contact sheet)")
    ap.add_argument("--status", action="store_true", help="show how many lines Gemini has voiced (no API calls)")
    args = ap.parse_args()

    data = load_script(args.script)
    if args.status:
        done, total = voice_status(data)
        left = total - done
        print(f"Gemini voices: {done}/{total} lines done; {left} left "
              f"(~{math.ceil(left / gemini_guard.limit_for('tts'))} day(s) at {gemini_guard.limit_for('tts')} requests/day). "
              f"Today: {gemini_guard.summary()}")
        return
    W, H = ASPECTS[data["aspect"]]
    out_dir = OUT_ROOT / data["id"]
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"{data['title']}  ({data['aspect']} {W}x{H})  gemini usage today: {gemini_guard.summary()}")
    try:
        items, total = build_timeline(data, args.tts)
    except tts.VoicingIncomplete as exc:
        done, all_lines = voice_status(data)
        print(f"\nGemini stopped: {str(exc)[:160]}\n"
              f"Voiced {done}/{all_lines} lines (kept in the cache). Run the same command again after the quota resets "
              f"-- it continues where it stopped and renders the video once every line is voiced.")
        return
    print(f"  total {total:.1f}s")
    audio = out_dir / "audio.wav"
    mix_audio(data, items, total, audio)
    r = Renderer(data, items, W, H)
    meta = out_dir / "meta.json"
    if not meta.is_file():  # first render only: a title edited in the library page is never overwritten
        meta.write_text(json.dumps({"title": data["title"]}, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "timeline.json").write_text(json.dumps(
        [{k: v for k, v in it.items() if k not in ("samples", "track", "card")} for it in items],
        ensure_ascii=False, indent=2), encoding="utf-8")
    if args.frames or args.no_video:
        contact_sheet(r, items, total, out_dir / "contact_sheet.png")
    if not args.no_video:
        started = time.time()
        video = out_dir / "short.mp4"
        encode(r, total, audio, video, get_settings().ffmpeg_binary)
        print(f"video: {video}  ({total:.1f}s, rendered in {time.time() - started:.0f}s)  "
              f"gemini usage today: {gemini_guard.summary()}")


if __name__ == "__main__":
    main()
