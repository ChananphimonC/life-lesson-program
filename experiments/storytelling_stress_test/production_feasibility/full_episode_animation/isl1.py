"""Island, scene 1 (hour 0, morning): the monkey 'chairman' teaser, ten students wake on the beach, Chula wants a meeting, Thammasat objects, Kasetsart is up a palm,
Mahidol checks pulses, the two engineers argue over a plank, Songkhla announces the 72 hours, the monkey eyes the bag."""
from isl_common import *  # noqa: F401,F403

NAME, I = "isl1", 1
DUR = scene_dur(I)
CAPS = []
MARK = ["ก่อนจะเล่า", "สิบมหาวิทยาลัย หนึ่งเกาะร้าง", "จุฬาตื่นก่อน", "ธรรมศาสตร์สะดุ้งตื่น", "เกษตรไม่ได้ยินสักคำ", "มหิดลเดินจับชีพจร", "ลาดกระบังกับบางมดกำลังเถียง",
        "คนสุดท้ายที่ลุกขึ้น", "ทุกคนเงียบไปหนึ่งวินาที", "แต่ทะเลไม่รอใคร"]
B = beats(I, MARK)
BE = B + [DUR - TAIL]
CUES = [(B[1] + 1.0, "whoosh", 0.4), (B[2] + 1.0, "ding", 0.4), (B[3] + 0.8, "gasp", 0.5), (B[4] + 2.0, "thump", 0.5), (B[6] + 3.0, "grunt", 0.4), (B[7] + 4.0, "chime", 0.5),
        (B[9] + 1.0, "pop", 0.4)]
XS = row_x(10, 150, 1130)


def draw(cv, t, ov):
    cv.push(0, 0, scale=1.0)
    tick(t)
    k = which(t, B)
    beach_morning(cv, t, wreck=(k != 0))
    for j in range(3):
        seagull(cv, 200 + 330 * j + 30 * math.sin(t + j), 110 + 40 * j, 1.0, t, seed=j)
    if k == 0:
        # the teaser: the monkey sits on a rock like a chairman, the ten students stand in two obedient rows in front of it
        rocks(cv, 640, 620, 300, 190)
        monkey(cv, 640, 470, 2.4, "sit", t, mouth=True)
        for j, w in enumerate(ORDER10):
            side = -1 if j < 5 else 1
            x = 640 + side * (170 + 112 * (j % 5))
            st(cv, w, x, 690 + 8 * (j % 2), pose=REST, ex="deadpan" if j % 2 else "neutral", th=-40 * side if False else (40 if side < 0 else -40), flip=side > 0, k=0.5, seed=j)
    elif k == 1:
        for j, w in enumerate(ORDER10):
            lying(cv, w, XS[j], 640 + 22 * (j % 2), 0.55, ex="neutral", flip=(j % 2 == 1), seed=j)
        ov.append(("72", 640, 130, 150, (255, 244, 200), ease(fr(t, BE, 1, 0.1, 0.4))))
    elif k == 2:
        for j, w in enumerate(ORDER10):
            if w != "chula":
                lying(cv, w, XS[j], 650 + 20 * (j % 2), 0.5, flip=(j % 2 == 1))
        up = ease(fr(t, BE, 2, 0.0, 0.3))
        st(cv, "chula", 400, 700, pose=POINT_UP if up > 0.9 else REST, ex="eager" if up > 0.9 else "neutral", th=30, k=0.95, mouth=mouth_of(t, B[2] + 1.0, B[3] - 0.6, 1))
        say_waves(cv, 480, 470, t, B[2] + 1.0, B[3] - 0.6)
    elif k == 3:
        for j, w in enumerate(ORDER10):
            if w not in ("chula", "thamma"):
                lying(cv, w, XS[j], 650 + 20 * (j % 2), 0.5, flip=(j % 2 == 1))
        st(cv, "chula", 360, 700, pose=REST, ex="neutral", th=35, k=0.95)
        sh = in_(t, BE, 3, 0.15, 0.85)
        st(cv, "thamma", 780, 700, pose=POINT_FWD if sh else REST, ex="shout" if sh else "gape", th=-30, flip=True, k=0.98, mouth=mouth_of(t, B[3] + 0.8, B[4] - 0.8, 2) if sh else 0)
        say_waves(cv, 700, 470, t, B[3] + 0.8, B[4] - 0.8, flip=True)
        ov.append(("!", 780, 330, 90, (255, 120, 100), ease(fr(t, BE, 3, 0.1, 0.25))))
    elif k == 4:
        palm(cv, 880, 700, 420, t, 30, 1.2, seed=0.5)
        cv.push(0, 0)
        st(cv, "kaset", 905, 360, pose=CHEER, ex="laugh", th=0, k=0.55, bob=0)
        for q in range(3):
            u = (t * 0.8 + q / 3) % 1.0
            coconut(cv, 880 + 30 * q - 20, 380 + 300 * u * u, 0.9)
        cv.pop()
        st(cv, "kku", 520, 700, pose=HEADS if False else REST, ex="laugh", th=30, k=0.9)
        st(cv, "chula", 300, 700, pose=POINT_UP, ex="plead", th=30, k=0.9, seed=2)
        ov.append(("?", 300, 350, 80, (255, 255, 255), 0.7))
    elif k == 5:
        lying(cv, "kku", 330, 680, 0.62, ex="laugh")
        pu = math.sin(t * 5)
        st(cv, "mahidol", 470, 700, pose=reach("mahidol", 470, 700, 40, 0.95, {"R": (390, 640)}, kinds=("relaxed", "relaxed")), ex="deadpan", th=40, k=0.95)
        cv.ellipse(392, 636, 30 + 10 * abs(pu), 12 + 4 * abs(pu), (255, 120, 140), ink=None, alpha=int(110 + 80 * abs(pu)))
        st(cv, "cmu", 740, 700, pose=REST, ex="happy", th=-30, flip=True, k=0.95, seed=1)
        st(cv, "silpa", 990, 700, pose=reach("silpa", 990, 700, -35, 0.95, {"R": (1010, 520)}, kinds=("relaxed", "open")), ex="aha", th=-35, flip=True, k=0.95, seed=3)
        cv.ellipse(1060, 290, 70, 70, (255, 240, 190), ink=None, alpha=60)
    elif k == 6:
        for j in (0, 1, 2, 3, 6, 7, 8, 9):
            pass
        plank(cv, 640, 640, 1.2, ang=-4)
        a = in_(t, BE, 6, 0.1, 0.9)
        st(cv, "kmitl", 470, 700, pose=reach("kmitl", 470, 700, 30, 0.98, {"R": (560, 620), "L": (580, 646)}), ex="deadpan" if a else "neutral", th=30, k=0.98,
           mouth=mouth_of(t, B[6] + 0.6, B[7] - 1.0, 3))
        st(cv, "kmutt", 810, 700, pose=reach("kmutt", 810, 700, -30, 0.98, {"R": (730, 630), "L": (716, 656)}), ex="shout" if a else "neutral", th=-30, flip=True, k=0.98,
           mouth=mouth_of(t, B[6] + 1.5, B[7] - 0.4, 4))
        ov.append(("?", 470, 380, 70, (255, 255, 255), 0.6))
        ov.append(("!", 810, 380, 70, (255, 120, 100), 0.6))
    elif k == 7:
        cv.push(0, 0)
        st(cv, "psu", 640, 700, pose=reach("psu", 640, 700, 0, 1.0, {"R": (760, 470)}, kinds=("point", "relaxed")), ex="deadpan", th=-60, k=1.0, mouth=mouth_of(t, B[7] + 2.0, B[8] - 0.5, 5))
        cv.pop()
        for j, w in enumerate(("chula", "thamma", "mahidol", "kaset", "kku", "cmu", "silpa", "kmitl", "kmutt")):
            x = 80 + j * 66
            st(cv, w, x, 720 + 6 * (j % 2), pose=REST, ex="worried" if j % 2 else "gape", th=-35, flip=True, k=0.46, seed=j)
        ov.append(("72", 1000, 150, 170, (255, 244, 200), ease(fr(t, BE, 7, 0.3, 0.55))))
    elif k == 8:
        for j, w in enumerate(("mahidol", "kaset", "kmitl", "kmutt", "silpa", "cmu", "kku", "psu")):
            st(cv, w, 100 + j * 150, 705 + 8 * (j % 2), pose=REST, ex="gape", th=0 if j % 2 else 30, k=0.55, seed=j)
        arg = in_(t, BE, 8, 0.25, 0.95)
        st(cv, "chula", 520, 700, pose=POINT_FWD if arg else REST, ex="shout" if arg else "deadpan", th=45, k=0.95, mouth=mouth_of(t, B[8] + 1.0, B[9] - 0.5, 6) if arg else 0)
        st(cv, "thamma", 780, 700, pose=POINT_FWD if arg else REST, ex="shout" if arg else "deadpan", th=-45, flip=True, k=0.98, mouth=mouth_of(t, B[8] + 1.4, B[9] - 0.3, 7) if arg else 0)
        if arg:
            ov.append(("!", 640, 330, 100, (255, 120, 100), 0.8))
    else:
        rocks(cv, 330, 700, 200, 90)
        dry_bag(cv, 330, 690, 1.4)
        st(cv, "chula", 520, 700, pose=REST, ex="deadpan", th=-30, flip=True, k=0.95)
        st(cv, "thamma", 700, 700, pose=CROSS, ex="deadpan", th=30, k=0.98, seed=1)
        # the eyes in the tree
        palm(cv, 150, 700, 380, t, 80, 1.0, seed=1)
        monkey(cv, 220, 340, 0.9, "sit", t)
        a = ease(fr(t, BE, 9, 0.2, 0.5))
        ov.append(("•_•", 330, 420, 54, (255, 255, 255), a))
    cv.pop()
    pulse_ov(ov, t)
