"""Island, scene 5 (hour 12): the climb, the monitor lizard, the hornbills, the view of the strait and the storm wall, the signal mirror, the raft plan."""
from isl_common import *  # noqa: F401,F403

NAME, I = "isl5", 5
DUR = scene_dur(I)
CAPS = []
MARK = ["ชั่วโมงที่สิบสอง", "ทางขึ้นเป็นป่ารก", "จนกลางทางมีตะกวด", "เชียงใหม่ที่เดินท้ายสุด", "ตะกวดมองเชียงใหม่", "ด้านบนมีนกเงือก", "ขึ้นถึงยอดเขา", "ลาดกระบังก้มลงถอด", "บางมดมองเมฆดำ"]
B = beats(I, MARK)
BE = B + [DUR - TAIL]
CUES = [(B[1] + 2.0, "step", 0.4), (B[2] + 1.0, "gasp", 0.5), (B[4] + 1.0, "sigh", 0.4), (B[5] + 1.0, "whoosh", 0.4), (B[6] + 1.0, "chime", 0.5), (B[7] + 3.0, "ding", 0.5), (B[8] + 1.0, "thump", 0.5)]
FILE = ["psu", "thamma", "chula", "kaset", "kku", "kmitl", "kmutt", "mahidol", "silpa", "cmu"]


def draw(cv, t, ov):
    cv.push(0, 0, scale=1.0)
    tick(t)
    k = which(t, B)
    if k in (0, 1):
        beach_morning(cv, t, wreck=False)
        if k == 1:
            hill_path(cv, t)
        run = fr(t, BE, k, 0.0, 1.0)
        for j, w in enumerate(FILE):
            x = -80 + 1250 * run - j * 100 if k == 1 else 80 + 560 * run - j * 40
            y = 700 - 130 * (x / 1280.0) * (1 if k == 1 else 0) + 6 * (j % 2)
            walker(cv, w, x, y, t, speed=6.5, stride=12, lift=10, ex="happy" if k == 0 else "pant", k=0.6, seed=j)
        if k == 1:
            ov.append(("•", 200, 130, 1, (255, 255, 255), 0.0))
    elif k in (2, 3, 4):
        hill_path(cv, t)
        lx = 330 + 40 * ease(fr(t, BE, 2, 0.0, 0.5))
        liz_move = k == 2 and fr(t, BE, 2, 0.0, 0.7) < 1.0
        lz = lizard(cv, 640 if k == 2 else 640 + 220 * ease(fr(t, BE, 4, 0.2, 0.9)), 640 - 10 * (0 if k == 2 else 0), 1.15, t, moving=True)
        for j, w in enumerate(("psu", "thamma", "chula", "kaset", "kku")):
            st(cv, w, 90 + j * 90, 700 + 6 * (j % 2), pose=REST, ex="gape", th=0, k=0.5, seed=j) if k == 2 else None
        if k == 2:
            ov.append(("!", 640, 380, 100, (255, 120, 100), 0.9))
            st(cv, "chula", 980, 700, pose=HEADS, ex="yikes", th=-30, flip=True, k=0.9)
            ov.append(("!", 980, 400, 80, (255, 120, 100), 0.8))
        if k >= 3:
            a = ease(fr(t, BE, 3, 0.0, 0.6)) if k == 3 else 1.0
            st(cv, "cmu", 360 + 160 * a, 700, pose=walk_pose(t * 4) if a < 0.99 else REST, ex="happy", th=60 if a < 0.99 else 20, k=0.95,
               walk=dict(phase=t * 4, stride=10, lift=8) if a < 0.99 else None, mouth=mouth_of(t, B[3] + 1.0, B[4] - 1.0, 4) if k == 3 else 0)
            for j, w in enumerate(("psu", "thamma", "chula", "kaset", "kku")):
                st(cv, w, 940 + j * 66, 705 + 6 * (j % 2), pose=REST, ex="worried", th=-30, flip=True, k=0.5, seed=j)
        if k == 4:
            ov.append(("•_•", 700, 520, 30, (255, 255, 255), 0.0))
    elif k == 5:
        hill_path(cv, t)
        for q in range(3):
            hornbill(cv, 1300 - ((t * 140 + q * 220) % 1500), 150 + 70 * q + 12 * math.sin(t + q), 1.4, t, flip=True, seed=q)
        for j, w in enumerate(("silpa", "cmu", "psu", "chula", "kku")):
            st(cv, w, 150 + j * 150, 705 + 6 * (j % 2), pose=POINT_UP if j == 0 else REST, ex="aha" if j == 0 else "gape", th=20, k=0.7, seed=j)
    elif k == 6:
        hilltop(cv, t, storm=ease(fr(t, BE, 6, 0.5, 1.0)))
        for j, w in enumerate(("psu", "thamma", "chula", "kaset", "kku", "cmu", "silpa")):
            st(cv, w, 140 + j * 120, 640 + 4 * (j % 2), pose=REST, ex="gape", th=-40 if False else 30, k=0.62, seed=j)
        ov.append(("72", 1090, 100, 100, (255, 244, 200), 0.0))
    elif k == 7:
        hilltop(cv, t, storm=1.0)
        a = ease(fr(t, BE, 7, 0.2, 0.5))
        st(cv, "kmitl", 520, 640, pose=reach("kmitl", 520, 640, 20, 0.95, {"R": (640, 420)}, kinds=("grip", "relaxed")), ex="eager", th=20, k=0.95, mouth=mouth_of(t, B[7] + 1.0, B[8] - 0.8, 4))
        cv.ellipse(650, 420, 22, 22, (200, 230, 250), ink=INK, lw=2.4)
        mirror_flash(cv, 650, 420, t, 1.2, on=a > 0.3)
        if a > 0.3:
            for q in range(3):
                x0 = 650 + (t * 200 + q * 120) % 360
                cv.stroke([(x0, 430 + (x0 - 650) * 0.04), (x0 + 38, 432 + (x0 - 650) * 0.04)], (255, 255, 230), 5, alpha=200)
        for j, w in enumerate(("kmutt", "kaset", "thamma", "silpa")):
            st(cv, w, 820 + j * 105, 650 + 4 * (j % 2), pose=REST, ex="aha" if j == 0 else "gape", th=-30, flip=True, k=0.62, seed=j)
    else:
        hilltop(cv, t, storm=1.0, flash=max(0.0, math.sin(t * 7)) ** 6)
        st(cv, "kmutt", 520, 650, pose=reach("kmutt", 520, 650, 20, 1.0, {"R": (640, 450)}, kinds=("point", "relaxed")), ex="worried", th=20, k=1.0, mouth=mouth_of(t, B[8] + 0.6, B[8] + 3.5, 3))
        st(cv, "kmitl", 820, 650, pose=CROSS, ex="deadpan", th=-30, flip=True, k=1.0, seed=2)
        ov.append(("?", 820, 420, 80, (255, 255, 255), 0.7))
        ov.append(("!", 520, 420, 80, (255, 120, 100), 0.7))
    cv.pop()
    pulse_ov(ov, t)
