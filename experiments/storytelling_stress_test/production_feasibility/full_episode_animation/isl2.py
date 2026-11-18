"""Island, scene 2 (hour 3): the macaque steals Chula's bag, everybody chases it into the forest, Chiang Mai trades a coconut for the bag, the monkey is named 'ประธาน'."""
from isl_common import *  # noqa: F401,F403

NAME, I = "isl2", 2
DUR = scene_dur(I)
CAPS = []
MARK = ["ชั่วโมงที่สาม", "แต่ยังไม่ทันได้แจก", "จุฬาร้องลั่น", "ทุกคนวิ่งตามกันเข้าป่า", "ลิงนั่งอยู่บนกิ่งไม้", "ลาดกระบังกระซิบ", "เชียงใหม่ผ่ามะพร้าว", "ทุกคนปรบมือดังลั่น",
        "จุฬากับธรรมศาสตร์ต่างคนต่างทำหน้างอ"]
B = beats(I, MARK)
BE = B + [DUR - TAIL]
CUES = [(B[1] + 1.0, "whoosh", 0.5), (B[2] + 1.0, "gasp", 0.5), (B[3] + 1.0, "step", 0.5), (B[4] + 0.5, "ding", 0.3), (B[6] + 3.0, "pop", 0.4), (B[7] + 0.5, "cheer", 0.5)]
CROWD = ["thamma", "mahidol", "kaset", "kmitl", "kmutt", "silpa", "cmu", "kku", "psu"]


def draw(cv, t, ov):
    cv.push(0, 0, scale=1.0)
    tick(t)
    k = which(t, B)
    ph = walk_ph(t, 8.0)
    if k in (0, 1, 2):
        beach_morning(cv, t, wreck=False)
        palm(cv, 980, 700, 400, t, -40, 1.1, seed=1.7)
        for j, w in enumerate(("mahidol", "kaset", "kku", "cmu", "silpa", "psu")):
            st(cv, w, 640 + j * 100, 690 + 6 * (j % 2), pose=REST, ex="neutral", th=30 if j % 2 else -30, flip=j % 2 == 0, k=0.5, seed=j)
        # Chula shows the contents of the dry bag
        ofs = fr(t, BE, 0, 0.0, 1.0) if k == 0 else 1.0
        st(cv, "chula", 380, 700, pose=reach("chula", 380, 700, 30, 0.95, {"R": (470, 640)}, kinds=("relaxed", "relaxed")), ex="eager", th=30, k=0.95, mouth=mouth_of(t, B[0] + 1.0, B[1] - 0.6, 1) if k == 0 else 0)
        dry_bag(cv, 480, 690, 1.3, open_=1.0)
        # the paper things: a diary, a name card, bread
        rrect(cv, 520, 640, 566, 676, 4, (252, 252, 254), lw=2.0)
        rrect(cv, 578, 650, 614, 676, 3, (250, 236, 196), lw=2.0)
        if k >= 1:
            u = ease(fr(t, BE, 1, 0.1, 0.7))
            mx = 980 - 560 * u
            my = 340 + 280 * u - 120 * math.sin(math.pi * u)
            monkey(cv, mx, my, 1.0, "arms_up" if u < 0.55 else "run", t, flip=True, hold="bag" if u > 0.5 else None)
            if u > 0.55:
                u2 = ease(fr(t, BE, 1, 0.6, 1.0)) + (fr(t, BE, 2, 0.0, 0.5) if k == 2 else 0)
                monkey(cv, mx, my, 0.001, "sit", t)
        if k == 2:
            monkey(cv, 420 + 700 * ease(fr(t, BE, 2, 0.0, 0.8)), 700, 1.0, "run", t, hold="bag")
            st(cv, "chula", 380, 700, pose=ARMS_UP, ex="shout", th=40, k=0.95, mouth=mouth_of(t, B[2] + 0.4, B[3] - 0.8, 2))
            st(cv, "thamma", 220, 700, pose=POINT_FWD, ex="shout", th=40, k=0.98, mouth=mouth_of(t, B[2] + 2.0, B[3] - 0.4, 3))
            say_waves(cv, 450, 470, t, B[2] + 0.4, B[3] - 0.8)
    elif k == 3:
        forest(cv, t)
        # everybody runs +x through the forest, Kasetsart in front, the monkey far ahead
        run = fr(t, BE, 3, 0.0, 1.0)
        monkey(cv, 1200 - 160 * run, 640, 0.8, "run", t, flip=False, hold="bag")
        order = ["kaset", "thamma", "chula", "kmitl", "kmutt", "mahidol", "silpa", "cmu", "kku", "psu"]
        for j, w in enumerate(order):
            x = -100 + 1200 * run - j * 85
            walker(cv, w, x, 700 + 8 * (j % 2), t, speed=10, stride=18, lift=14, ex="shout" if j < 3 else "pant", k=0.62, seed=j)
    elif k == 4:
        forest(cv, t)
        cv.stroke(spline([(300, 220), (640, 210), (980, 240)], n=3), INK, 22)
        cv.stroke(spline([(300, 220), (640, 210), (980, 240)], n=3), (120, 90, 60), 16)
        monkey(cv, 760, 220, 1.2, "sit", t, mouth=True, hold="bag")
        st(cv, "kaset", 470, 700, pose=reach("kaset", 470, 700, 20, 0.95, {"R": (520, 460)}, kinds=("point", "relaxed")), ex="eager", th=20, k=0.95)
        for j, w in enumerate(("chula", "thamma", "kmitl")):
            st(cv, w, 640 + j * 130, 700 + 6 * (j % 2), pose=POINT_UP, ex="gape", th=-20, flip=True, k=0.9, seed=j)
    elif k == 5:
        forest(cv, t)
        cv.stroke(spline([(300, 220), (640, 210), (980, 240)], n=3), INK, 22)
        cv.stroke(spline([(300, 220), (640, 210), (980, 240)], n=3), (120, 90, 60), 16)
        monkey(cv, 760, 220, 1.2, "sit", t, hold="bag")
        a = in_(t, BE, 5, 0.1, 0.6)
        st(cv, "kmitl", 360, 700, pose=reach("kmitl", 360, 700, 30, 0.95, {"R": (470, 520)}, kinds=("grip", "relaxed")), ex="smug", th=30, k=0.95)
        plank(cv, 470, 520, 0.7, ang=-70, w=140, h=14)
        st(cv, "mahidol", 640, 700, pose=STOP, ex="shout", th=-30, flip=True, k=0.95, mouth=mouth_of(t, B[5] + 3.0, B[6] - 0.5, 4))
        ov.append(("!", 640, 380, 90, (255, 120, 100), 0.8 if a else 0.2))
        ov.append(("X", 470, 430, 70, (255, 80, 80), 0.9))
    elif k == 6:
        forest(cv, t)
        cv.stroke(spline([(300, 220), (640, 210), (980, 240)], n=3), INK, 22)
        cv.stroke(spline([(300, 220), (640, 210), (980, 240)], n=3), (120, 90, 60), 16)
        u = ease(fr(t, BE, 6, 0.55, 1.0))
        monkey(cv, 760, 220, 1.2, "sit", t, hold="bag" if u < 0.9 else "coconut", mouth=u > 0.5)
        st(cv, "cmu", 560, 700, pose=reach("cmu", 560, 700, 20, 0.95, {"R": (680, 360)}, kinds=("open", "relaxed")), ex="happy", th=20, k=0.95)
        coconut(cv, 690, 380, 1.4)
        coconut(cv, 722, 372, 1.2)
        for j, w in enumerate(("chula", "kaset", "thamma")):
            st(cv, w, 300 + j * 90, 710, pose=REST, ex="gape", th=30, k=0.55, seed=j)
    elif k == 7:
        forest(cv, t)
        monkey(cv, 780, 470, 1.4, "sit", t, hold="coconut", mouth=True)
        dry_bag(cv, 560, 700, 1.3)
        st(cv, "chula", 400, 700, pose=CHEER, ex="happy", th=30, k=0.95)
        for j, w in enumerate(("cmu", "kaset", "kku", "mahidol", "silpa")):
            st(cv, w, 940 + j * 70 - (200 if j > 2 else 0), 710 + 6 * (j % 2), pose=CHEER, ex="laugh", th=-30, flip=True, k=0.6, seed=j)
        # a small "chairman" sash
        cv.fill([(742, 420), (770, 410), (800, 450), (772, 460)], (232, 60, 70), ink=INK, lw=1.6) if in_(t, BE, 7, 0.4, 1.0) else None
        ov.append(("ประธาน", 780, 330, 60, (255, 244, 200), ease(fr(t, BE, 7, 0.45, 0.65))))
    else:
        forest(cv, t)
        st(cv, "chula", 470, 700, pose=CROSS, ex="deadpan", th=30, k=0.98)
        st(cv, "thamma", 790, 700, pose=CROSS, ex="deadpan", th=-30, flip=True, k=0.98)
        # Chula tucks a card back into the bag
        u = ease(fr(t, BE, 8, 0.2, 0.7))
        dry_bag(cv, 630, 700, 1.3)
        rrect(cv, 616, 600 + 70 * u, 650, 628 + 70 * u, 3, (250, 244, 214), lw=2.0)
        monkey(cv, 1060, 700, 1.0, "sit", t, hold="coconut")
    cv.pop()
    pulse_ov(ov, t)
