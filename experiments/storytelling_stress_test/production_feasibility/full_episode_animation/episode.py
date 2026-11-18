"""Episode driver: renders every scene frame by frame (multiprocessing), muxes the procedural sound effects, writes one MP4.

    python episode.py frames  [scene ...]      -> render only (silent MP4 per scene) into scenes/
    python episode.py full                      -> whole episode: renders/pab_hai_thueng_duangjan_full_episode.mp4
"""
from __future__ import annotations

import importlib
import os
import subprocess
import sys
import time
import wave
from multiprocessing import Pool
from pathlib import Path

import numpy as np
from PIL import Image

import audio
import captions
import engine
from engine import FPS, H, W, new_canvas

HERE = Path(__file__).resolve().parent
ORDER = os.environ.get("EPISODE_ORDER", "s0,s1,s2,s3,s4a,s4b,s4c,s5,s6").split(",")
OUT = Path(os.environ.get("EPISODE_DIR", str(HERE)))
FADE = 0.3
SUBTITLES = False                # the speakers are told apart by voice; on-screen numbers and labels (draw_overlay) stay
_mods = {}


def mod(name):
    if name not in _mods:
        if name.startswith("gs_"):                      # data-driven story scene (story_engine): gs_<story>_<i>
            import story_engine
            _mods[name] = story_engine.build(name)
        else:
            _mods[name] = importlib.import_module(name)
    return _mods[name]


def timeline():
    t0, out = 0.0, []
    for n in ORDER:
        m = mod(n)
        out.append((n, t0, m.DUR))
        t0 += m.DUR
    return out, t0


def render_frame(args):
    name, i = args
    m = mod(name)
    t = i / FPS
    engine.CUR = name
    cv = new_canvas()
    ov = []
    m.draw(cv, t, ov)
    img = cv.result().convert("RGBA")
    captions.draw_overlay(img, ov)
    if SUBTITLES:
        captions.overlay(img, m.CAPS, t)
    # scene-boundary fades
    a = 1.0
    if name != ORDER[0]:
        a = min(a, t / FADE)
    if name != ORDER[-1]:
        a = min(a, (m.DUR - t) / FADE)
    if a < 1.0:
        img = Image.blend(Image.new("RGBA", img.size, (0, 0, 0, 255)), img, max(0.0, a))
    return img.convert("RGB").tobytes()


def encode(frames_iter, out_path, audio_path=None):
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-"]
    if audio_path:
        cmd += ["-i", str(audio_path), "-c:a", "aac", "-b:a", "160k", "-shortest"]
    cmd += ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "17", "-preset", "medium", "-tune", "animation", "-movflags", "+faststart", str(out_path)]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    n = 0
    for fr in frames_iter:
        p.stdin.write(fr)
        n += 1
    p.stdin.close()
    p.wait()
    return n


def write_wav(samples, path):
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(audio.SR)
        w.writeframes(samples.tobytes())


def build_audio(path):
    """SFX + voice. The SFX are lowered while someone speaks so the lines stay clear."""
    tl, total = timeline()
    cues = []
    for n, t0, dur in tl:
        for tc, name, g in mod(n).CUES:
            if 0 <= tc < dur:
                cues.append((t0 + tc, name, g))
    sfx = audio.mix(cues, total).astype(np.float32) / 32768.0
    vf = HERE / "audio" / "voice_track.wav"
    if vf.is_file():
        with wave.open(str(vf), "rb") as w:
            v = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768.0
        n = max(len(sfx), len(v))
        sfx, v = np.pad(sfx, (0, n - len(sfx))), np.pad(v, (0, n - len(v)))
        win = audio.SR // 20
        lvl = np.sqrt(np.convolve(v ** 2, np.ones(win) / win, mode="same"))
        duck = np.clip(lvl / 0.03, 0, 1)
        duck = np.convolve(duck, np.ones(audio.SR // 4) / (audio.SR // 4), mode="same")
        out = v * 1.0 + sfx * (1.0 - 0.6 * np.clip(duck, 0, 1)) * 0.8
    else:
        out = sfx
    peak = np.abs(out).max()
    if peak > 0.95:
        out = out * (0.95 / peak)
    write_wav((out * 32767).astype(np.int16), path)
    return total


def jobs(names):
    return [(n, i) for n in names for i in range(int(round(mod(n).DUR * FPS)))]


if __name__ == "__main__":
    mode = sys.argv[1]
    (OUT / "scenes").mkdir(exist_ok=True)
    (HERE / "renders").mkdir(exist_ok=True)
    (HERE / "audio").mkdir(exist_ok=True)
    t_start = time.time()
    with Pool(8) as pool:
        if mode == "frames":
            names = sys.argv[2:] or ORDER
            for n in names:
                js = jobs([n])
                cnt = encode(pool.imap(render_frame, js, chunksize=6), OUT / "scenes" / f"{n}.mp4")
                print(n, cnt, "frames", round(time.time() - t_start), "s", flush=True)
        else:
            total = build_audio(HERE / "audio" / "episode_sfx.wav")
            js = jobs(ORDER)
            cnt = encode(pool.imap(render_frame, js, chunksize=6), HERE / "renders" / "pab_hai_thueng_duangjan_full_episode.mp4", HERE / "audio" / "episode_sfx.wav")
            print("frames", cnt, "duration", round(total, 1), "s; wall", round(time.time() - t_start), "s")
