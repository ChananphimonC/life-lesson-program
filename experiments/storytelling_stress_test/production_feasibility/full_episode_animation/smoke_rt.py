"""Smoke test + thread-flicker check for the red-thread scenes (no encoding): renders 2-second windows at full 24 fps after every beat, in every scene, and reports
exceptions and any frame where the amount of red thread changes abruptly (popping / vanishing lines). Usage: python smoke_rt.py [scene names...]"""
import os
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
os.environ["EPISODE_ORDER"] = ",".join(f"rt{i}" for i in range(1, 8))
os.environ["EPISODE_DIR"] = str(HERE / "red_thread")
os.environ["STORY_PREFIX"] = "rt"
sys.path.insert(0, str(HERE))
import episode  # noqa: E402


def work(a):
    name, i = a
    try:
        raw = episode.render_frame((name, i))
    except Exception as exc:  # noqa: BLE001
        return name, i, "ERR " + repr(exc)[:160], 0
    x = np.frombuffer(raw, np.uint8).reshape(720, 1280, 3).astype(np.int16)
    m = (x[:, :, 0] > 200) & (x[:, :, 1] < 110) & (x[:, :, 2] < 130) & (x[:, :, 0] - x[:, :, 1] > 110)
    return name, i, None, int(m.sum())


if __name__ == "__main__":
    names = sys.argv[1:] or [f"rt{i}" for i in range(1, 8)]
    jobs = []
    for n in names:
        m = episode.mod(n)
        starts = sorted(set(round(b + 0.6, 2) for b in m.B)) + [round(m.DUR / 2, 2)]
        for s in starts:
            jobs += [(n, int(s * 24) + k) for k in range(48) if int((s) * 24) + k < int(m.DUR * 24)]
    t0 = time.time()
    with Pool(4) as pool:
        res = pool.map(work, jobs, chunksize=4)
    errs = [r for r in res if r[2]]
    print("frames", len(res), "errors", len(errs), "time", round(time.time() - t0), "s")
    for r in errs[:10]:
        print(r)
    by = {}
    for n, i, e, c in res:
        by.setdefault(n, []).append((i, c))
    for n, lst in by.items():
        lst.sort()
        bad = []
        for (i0, c0), (i1, c1) in zip(lst, lst[1:]):
            if i1 - i0 == 1 and max(c0, c1) > 300 and abs(c1 - c0) / max(c0, c1) > 0.18:
                bad.append((i1, c0, c1))
        print(n, "abrupt red changes:", len(bad), bad[:8])
