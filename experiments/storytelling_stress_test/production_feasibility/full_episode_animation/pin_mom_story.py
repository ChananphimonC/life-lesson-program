"""Pin and Mom with the smelly bowl, as a short story with voice (the approved anim_v2d scene, unchanged, plus a few spoken lines).

anim_v2d.py is imported, not edited: only its audio (its own sniff / gasp / sigh effects plus the voices below) and its output
paths are replaced. The mouths follow the loudness of each character's own audio lane, as in the original.
The five lines are NEW production text written for this clip (the scene had no dialogue); they are not from any earlier script.

    python pin_mom_story.py            -> pin_mom/pin_mom_story.mp4 (1920x1080, 30 fps)
"""
import subprocess
import sys
from array import array
from multiprocessing import Pool
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "prototype_v2"))
sys.path.insert(0, str(HERE))
import anim_v2d as A  # noqa: E402
import voice  # noqa: E402

OUTD = HERE / "pin_mom"
OUTD.mkdir(exist_ok=True)
A.FRAMES = OUTD / "frames"
A.AUDIO = OUTD / "pin_mom_audio.wav"
A.VIDEO = OUTD / "pin_mom_story.mp4"
LINES = [("pin", 0.5, "แม่คะ ขอหนูส่องชามนี้หน่อยนะ"), ("mom", 3.95, "ทำไมกลิ่นแปลก ๆ นะ"), ("pin", 5.5, "แม่! มีขนฟู ๆ ขึ้นด้วย!"),
         ("mom", 7.3, "แม่ลืมเก็บเข้าตู้เย็นนี่เอง"), ("pin", 9.3, "ว้าว! ราสวยจัง!")]
_orig = A.build_audio


def build_audio(write=False):
    mixed, pin, mom = _orig(False)
    n = len(mixed)
    lanes = {"pin": np.array(pin, np.int32), "mom": np.array(mom, np.int32)}
    for who, t0, text in LINES:
        x = voice.synth(who, text)
        y = (x * 26000).astype(np.int32)
        i = int(t0 * A.SR)
        j = min(n, i + len(y))
        lanes[who][i:j] += y[:j - i]
    clip = lambda a: array("h", np.clip(a, -32000, 32000).astype(np.int16).tobytes())
    pin2, mom2 = clip(lanes["pin"]), clip(lanes["mom"])
    mixed2 = clip(np.array(pin2, np.int32) + np.array(mom2, np.int32) + (np.array(mixed, np.int32) - np.array(pin, np.int32) - np.array(mom, np.int32)))
    if write:
        A.tts.write_wav(A.AUDIO, mixed2)
    return mixed2, pin2, mom2


A.build_audio = build_audio

if __name__ == "__main__":
    A.FRAMES.mkdir(exist_ok=True)
    build_audio(write=True)
    n = int(A.DUR * A.FPS)
    with Pool(6, initializer=A._init) as pool:
        for i, _ in enumerate(pool.imap_unordered(A._save, range(n))):
            if i % 60 == 0:
                print(f"  {i}/{n}", flush=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(A.FPS), "-i", str(A.FRAMES / "f%04d.png"), "-i", str(A.AUDIO),
                    "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-shortest",
                    "-movflags", "+faststart", str(A.VIDEO)], check=True)
    print("video:", A.VIDEO)
