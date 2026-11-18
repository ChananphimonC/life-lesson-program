"""Assemble the robot-world story: concatenate the rendered scene MP4s, mix the narrator (Gemini Kore voice, one request per scene) with the sound effects
(lowered under the voice) and mux to AAC.   EPISODE_ORDER=rw1,...,rw7 EPISODE_DIR=<robot_world> python robot_assemble.py"""
import os
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np

PREFIX = os.environ.get("STORY_PREFIX", "rw")
os.environ.setdefault("EPISODE_ORDER", ",".join(f"{PREFIX}{i}" for i in range(1, 8)))
HERE = Path(__file__).resolve().parent
os.environ.setdefault("EPISODE_DIR", str(HERE / ("robot_world" if PREFIX == "rw" else "red_thread")))
import audio  # noqa: E402
import audio_future  # noqa: E402,F401
import episode  # noqa: E402
import importlib  # noqa: E402
rw_common = importlib.import_module(f"{PREFIX}_common")

OUT = Path(os.environ["EPISODE_DIR"])
(OUT / "renders").mkdir(exist_ok=True)
tl, total = episode.timeline()


def read(p):
    with wave.open(str(p), "rb") as w:
        assert w.getframerate() == audio.SR and w.getnchannels() == 1
        return np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768.0


cues = []
for n, t0, dur in tl:
    for tc, name, g in episode.mod(n).CUES:
        if 0 <= tc < dur:
            cues.append((t0 + tc, name, g))
sfx = audio.mix(cues, total).astype(np.float32) / 32768.0
voice = np.zeros(len(sfx) + audio.SR * 2, np.float32)
for i, (n, t0, dur) in enumerate(tl, 1):
    v = read(OUT / "audio" / f"r{i}.wav")
    a = int((t0 + rw_common.LEAD) * audio.SR)
    voice[a:a + len(v)] += v
n_ = max(len(sfx), len(voice))
sfx, voice = np.pad(sfx, (0, n_ - len(sfx))), np.pad(voice, (0, n_ - len(voice)))
win = audio.SR // 20
lvl = np.sqrt(np.convolve(voice ** 2, np.ones(win) / win, mode="same"))
duck = np.convolve(np.clip(lvl / 0.03, 0, 1), np.ones(audio.SR // 4) / (audio.SR // 4), mode="same")
mix = voice * 1.0 + sfx * (1.0 - 0.65 * np.clip(duck, 0, 1)) * 0.75
mix = mix[: int(total * audio.SR)]
peak = np.abs(mix).max()
if peak > 0.95:
    mix *= 0.95 / peak
wav = OUT / "audio" / "mix.wav"
episode.write_wav((mix * 32767).astype(np.int16), wav)
lst = OUT / "scenes" / "list.txt"
lst.write_text("".join(f"file '{n}.mp4'\n" for n, _, _ in tl), encoding="utf-8")
dest = OUT / "renders" / os.environ.get("STORY_OUT", "robot_world_episode.mp4")
subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-i", str(wav), "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", str(dest)], check=True)
print("wrote", dest, round(total, 1), "s")
