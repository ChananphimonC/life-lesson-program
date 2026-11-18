"""Island, scene 6 (hour 14, sunset): the engineers quarrel, Thammasat and Chula quarrel, Chiang Mai suggests a match, the coconut football with Mahidol as referee, the sand 'เรารอด', 1-1."""
from isl_common import *  # noqa: F401,F403

NAME, I = "isl6", 6
DUR = scene_dur(I)
CAPS = []
MARK = ["ชั่วโมงที่สิบสี่", "ธรรมศาสตร์กับจุฬาก็ไม่ได้ช่วยอะไร", "เชียงใหม่ที่นั่งชิลอยู่", "ทุกคนหันไปมอง", "ลูกบอลคือมะพร้าวแห้ง", "ธรรมศาสตร์ขีดทรายเป็นตัวอักษร", "ทั้งสองฝ่ายวิ่งตามมะพร้าว", "ทุกคนหัวเราะจนลืม"]
B = beats(I, MARK)
BE = B + [DUR - TAIL]
CUES = [(B[1] + 1.0, "grunt", 0.4), (B[3] + 0.5, "ding", 0.4), (B[4] + 2.0, "pop", 0.5), (B[5] + 2.0, "cheer", 0.5), (B[6] + 1.0, "thump", 0.5), (B[6] + 5.0, "crack", 0.5), (B[7] + 0.5, "laugh", 0.6)]


def goal_posts(cv, x, y, flip=False):
    sx = -1 if flip else 1
    cv.stroke([(x, y), (x, y - 150), (x + sx * 70, y - 150 - 20), (x + sx * 70, y - 20)], INK, 12)
    cv.stroke([(x, y), (x, y - 150), (x + sx * 70, y - 170), (x + sx * 70, y - 20)], (222, 168, 100), 7)


def draw(cv, t, ov):
    cv.push(0, 0, scale=1.0)
    tick(t)
    k = which(t, B)
    sun_u = 0.2 + 0.8 * fr(t, BE, 0, 0.0, 1.0) if k == 0 else (1.0 if k > 0 else 0.0)
    sunset_beach(cv, t, sun=0.4 + 0.5 * ((t / DUR) if DUR else 0))
    if k in (0, 1):
        a = in_(t, BE, 0, 0.2, 0.9) or k == 1
        st(cv, "kmitl", 380, 700, pose=CROSS, ex="deadpan", th=-30, flip=True, k=1.0)
        st(cv, "kmutt", 560, 700, pose=CROSS, ex="deadpan", th=30, k=1.0, seed=1)
        ov.append(("#", 470, 360, 1, (255, 255, 255), 0.0))
        if k == 0:
            plank(cv, 470, 640, 1.0, ang=-3)
        else:
            st(cv, "thamma", 820, 700, pose=POINT_FWD, ex="shout", th=-30, flip=True, k=1.0, mouth=mouth_of(t, B[1] + 0.5, B[2] - 0.6, 2))
            st(cv, "chula", 1040, 700, pose=POINT_FWD, ex="shout", th=30 if False else -30, flip=True, k=0.95, mouth=mouth_of(t, B[1] + 1.2, B[2] - 0.4, 3))
            ov.append(("!", 930, 340, 100, (255, 120, 100), 0.9))
            for q in range(4):                                                   # gulls flee
                seagull(cv, 900 + 90 * q + (t * 120) % 400, 120 + 30 * q, 1.0, t, seed=q)
    elif k in (2, 3):
        palm(cv, 300, 700, 340, t, 40, 1.0, col=(34, 70, 66), nuts=False)
        st(cv, "cmu", 480, 700, pose=reach("cmu", 480, 700, 30, 1.0, {"R": (590, 560)}, kinds=("point", "relaxed")) if k == 3 else REST, ex="happy", th=30, k=1.0,
           mouth=mouth_of(t, B[2] + 1.5, B[3] - 0.5, 4) if k == 2 else mouth_of(t, B[3], B[3] + 2.0, 4))
        coconut(cv, 690, 700, 1.8)
        for j, w in enumerate(("thamma", "chula", "kaset", "kku", "mahidol", "silpa")):
            if k == 3:
                st(cv, w, 830 + j * 70, 705 + 6 * (j % 2), pose=REST, ex="aha" if j % 2 else "gape", th=-30, flip=True, k=0.6, seed=j)
    elif k == 4:
        # teams line up: Chula side (left, pink) and Thammasat side (right, yellow), Mahidol with the shell whistle in the middle
        coconut(cv, 640, 700, 1.8)
        for j, w in enumerate(("chula", "kmitl", "silpa", "cmu")):
            st(cv, w, 240 + j * 80, 700 + 6 * (j % 2), pose=REST, ex="eager", th=30, k=0.8, seed=j)
        for j, w in enumerate(("thamma", "kmutt", "kaset", "psu")):
            st(cv, w, 1040 - j * 80, 700 + 6 * (j % 2), pose=REST, ex="eager", th=-30, flip=True, k=0.8, seed=j + 3)
        st(cv, "mahidol", 640, 640, pose=reach("mahidol", 640, 640, 0, 0.8, {"R": (672, 520)}, kinds=("relaxed", "relaxed")), ex="deadpan", th=0, k=0.8)
        cv.ellipse(676, 520, 7, 5, (250, 244, 230), ink=INK, lw=1.4)
        goal_posts(cv, 60, 700)
        goal_posts(cv, 1220, 700, flip=True)
    elif k == 5:
        # the sand message 'เรารอด' written big on the beach, Thammasat finishing the last stroke, Kasetsart and Khon Kaen cheering at the side
        y0 = 560
        for i, ch in enumerate("เรารอด"):
            pass
        ov.append(("เรารอด", 640, 250, 130, (250, 240, 214), ease(fr(t, BE, 5, 0.3, 0.7))))
        st(cv, "thamma", 400, 700, pose=reach("thamma", 400, 700, 30, 1.0, {"R": (470, 690)}, kinds=("grip", "relaxed")), ex="eager", th=30, k=1.0, lean=14)
        for j, w in enumerate(("kaset", "kku")):
            st(cv, w, 940 + j * 110, 705, pose=CHEER, ex="laugh", th=-30, flip=True, k=0.8, seed=j)
        st(cv, "chula", 760, 700, pose=CROSS, ex="smug", th=-30, flip=True, k=0.9, seed=4)
    elif k == 6:
        # the match: the coconut rolls, everyone chases it, a collision pile and the coconut cracks
        u = fr(t, BE, 6, 0.0, 0.85)
        cx = 220 + 800 * (0.5 + 0.5 * math.sin(u * 9))
        coconut(cv, cx, 700, 1.6, cracked=1.0 if u > 0.8 else 0.0)
        for j, w in enumerate(("chula", "kmitl", "silpa", "cmu")):
            walker(cv, w, 160 + (cx - 160) * (0.2 + 0.2 * j) if False else cx - 120 - 70 * j, 700 + 8 * (j % 2), t, speed=9, stride=16, lift=12, ex="pant", k=0.72, seed=j)
        for j, w in enumerate(("thamma", "kmutt", "kaset", "psu")):
            st(cv, w, cx + 120 + 70 * j, 700 + 8 * (j % 2), pose=walk_pose(-t * 9 + j), ex="pant", th=-60, flip=True, k=0.72, seed=j + 3, walk=dict(phase=-t * 9 + j, stride=16, lift=12))
        st(cv, "mahidol", 640, 560, pose=REST, ex="shout", th=0, k=0.55)
        if u > 0.82:
            for q in range(5):
                cv.ellipse(cx + 30 * math.cos(q * 1.3), 660 + 18 * math.sin(q * 1.3), 20, 20, (255, 255, 255), ink=None, alpha=110)
    else:
        for j, w in enumerate(ORDER10):
            lying(cv, w, 120 + j * 115, 620 + 10 * (j % 2), 0.55, ex="laugh", flip=j % 2 == 0)
        ov.append(("1 - 1", 640, 260, 150, (255, 244, 200), ease(fr(t, BE, 7, 0.1, 0.4))))
    cv.pop()
    pulse_ov(ov, t)
