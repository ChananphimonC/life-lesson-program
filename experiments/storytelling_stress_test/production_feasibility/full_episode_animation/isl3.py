"""Island, scene 3 (hour 6): thirst, Mahidol forbids sea water, the engineers build a solar still, Kasetsart follows the ants to a stream, Thammasat wants equal shares,
Chula's schedule and the useless call to an alumnus, Mahidol: boil it first, Songkhla keeps watching the sea."""
from isl_common import *  # noqa: F401,F403

NAME, I = "isl3", 3
DUR = scene_dur(I)
CAPS = []
MARK = ["ชั่วโมงที่หก", "มหิดลตัดบททันที", "ทุกคนหันมามองมหิดล", "ลาดกระบังกับบางมดช่วยกันทำเครื่องกลั่น", "สองคนหยุดเถียง", "ส่วนเกษตรเดินเข้าป่า", "ธรรมศาสตร์ยกมือประกาศ",
        "จุฬากางตารางเวร", "มหิดลสั่งเสียงเข้ม"]
B = beats(I, MARK)
BE = B + [DUR - TAIL]
CUES = [(B[1] + 0.5, "gasp", 0.5), (B[2] + 3.0, "sigh", 0.4), (B[4] + 0.2, "ding", 0.5), (B[5] + 4.0, "step", 0.4), (B[6] + 1.0, "pop", 0.4), (B[8] + 1.0, "ding", 0.3)]


def sun_hot(cv, t, a=1.0):
    cv.ellipse(1080, 120, 150, 150, (255, 244, 200), ink=None, alpha=int(60 * a))
    cv.ellipse(1080, 120, 62, 62, (255, 236, 150), ink=None, alpha=int(255 * a))


def still(cv, x, y, drops=0.0, t=0.0):
    """A solar still: a coconut-shell bowl in the sand under a plastic sheet; drops run down and fall into a cup."""
    cv.ellipse(x, y, 130, 24, (214, 190, 140), ink=None, alpha=160)
    cv.fill(spline([(x - 60, y), (x - 40, y - 60), (x, y - 100), (x + 40, y - 60), (x + 60, y)], closed=True, n=3), (206, 232, 250), ink=INK, lw=2.4, alpha=150)
    cv.stroke([(x - 40, y - 62), (x - 10, y - 60), (x + 18, y - 56)], (255, 255, 255), 2.2, alpha=150)
    cv.fill(spline([(x - 24, y), (x - 30, y - 10), (x + 30, y - 10), (x + 24, y)], closed=True, n=2), (126, 88, 56), ink=INK, lw=2.2)
    for i in range(3):
        u = (t * 0.8 + i / 3) % 1.0
        cv.ellipse(x + 8 * (i - 1), y - 60 + 46 * u, 2.4 + 1.2 * drops, 3.2 + 1.6 * drops, (150, 214, 255), ink=INK, lw=0.8, alpha=int(255 * drops))


def draw(cv, t, ov):
    cv.push(0, 0, scale=1.0)
    tick(t)
    k = which(t, B)
    if k in (0, 1, 2):
        tidepool(cv, t)
        sun_hot(cv, t)
        sweat = ["pant", "yikes", "pant"]
        for j, w in enumerate(("chula", "kaset", "kmitl", "cmu", "kku", "psu", "silpa")):
            st(cv, w, 130 + j * 170, 700 + 8 * (j % 2), pose=REST, ex="pant", th=30 if j % 2 else -30, flip=j % 2 == 0, k=0.62, seed=j)
        if k >= 1:
            st(cv, "mahidol", 640, 700, pose=STOP, ex="shout", th=0, k=1.0, mouth=mouth_of(t, B[1] + 0.3, B[2] - 0.6, 1))
            say_waves(cv, 700, 470, t, B[1] + 0.3, B[2] - 0.6)
            ov.append(("X", 790, 560, 100, (255, 80, 80), ease(fr(t, BE, 1, 0.2, 0.4))))
            # a hand holding up a cupped palm of sea water
            cv.ellipse(790, 600, 30, 10, (90, 170, 220), ink=INK, lw=1.8)
        if k == 2:
            st(cv, "mahidol", 640, 700, pose=REST, ex="deadpan", th=0, k=1.0)
            ov.append(("?", 380, 420, 90, (255, 255, 255), 0.7))
    elif k in (3, 4):
        tidepool(cv, t)
        sun_hot(cv, t)
        u = fr(t, BE, 3, 0.0, 1.0) if k == 3 else 1.0
        still(cv, 640, 640, drops=1.0 if k == 4 else 0.0, t=t)
        d = 15 if k == 3 else 12
        st(cv, "kmitl", 440, 700, pose=reach("kmitl", 440, 700, 30, 1.0, {"R": (580, 560)}, kinds=("point", "relaxed")), ex="deadpan", th=30, k=1.0,
           mouth=mouth_of(t, B[3] + 0.6, B[4] - 0.4, 2) if k == 3 else 0)
        st(cv, "kmutt", 860, 700, pose=reach("kmutt", 860, 700, -30, 1.0, {"R": (710, 550)}, kinds=("point", "relaxed")), ex="shout" if k == 3 else "gape", th=-30, flip=True, k=1.0,
           mouth=mouth_of(t, B[3] + 2.0, B[4] - 0.2, 3) if k == 3 else 0)
        if k == 3:
            ov.append(("15°", 440, 330, 70, (255, 244, 200), 0.9))
            ov.append(("12°", 860, 330, 70, (255, 244, 200), 0.9))
        else:
            cv.ellipse(640, 560, 40, 40, (150, 214, 255), ink=None, alpha=60)
            check_mark(cv, 640, 440, 1.6, a=ease(fr(t, BE, 4, 0.2, 0.4)))
    elif k == 5:
        mangrove(cv, t)
        run = fr(t, BE, 5, 0.0, 1.0)
        # ants marching +x along the log, Kasetsart bent over following them, the group behind
        for q in range(14):
            ax = (q * 70 + t * 60) % 1000 + 150
            cv.ellipse(ax, 604 + 2 * math.sin(t * 8 + q), 4, 3, (40, 30, 30), ink=None)
        st(cv, "kaset", 300 + 560 * run, 700, pose=walk_pose(t * 6), ex="eager", th=60, k=0.95, lean=14, walk=dict(phase=t * 6, stride=14, lift=10))
        for j, w in enumerate(("chula", "thamma", "mahidol", "cmu", "kku")):
            x = 140 + 560 * run - j * 90
            walker(cv, w, x, 710 + 6 * (j % 2), t, speed=6, stride=12, lift=9, ex="happy", k=0.6, seed=j)
        if run > 0.6:
            cv.ellipse(940, 640, 110, 22, (170, 232, 244), ink=INK, lw=2.4)
    elif k == 6:
        mangrove(cv, t)
        cv.ellipse(300, 650, 190, 36, (170, 232, 244), ink=INK, lw=2.4)
        for q in range(4):
            cv.stroke(spline([(220 + q * 60, 640), (240 + q * 60, 650), (260 + q * 60, 642)], n=2), (255, 255, 255), 2, alpha=170)
        st(cv, "thamma", 780, 700, pose=POINT_UP, ex="shout", th=-30, flip=True, k=1.0, mouth=mouth_of(t, B[6] + 0.5, B[7] - 0.4, 3))
        say_waves(cv, 700, 470, t, B[6] + 0.5, B[7] - 0.4, flip=True)
        for j, w in enumerate(("chula", "kaset", "cmu", "kku")):
            st(cv, w, 940 + j * 85, 710 + 6 * (j % 2), pose=REST, ex="neutral", th=-30, flip=True, k=0.55, seed=j)
        for q in range(10):
            cv.ellipse(500 + q * 12, 690, 9, 12, (170, 232, 244), ink=INK, lw=1.4)
    elif k == 7:
        mangrove(cv, t)
        cv.ellipse(300, 650, 190, 36, (170, 232, 244), ink=INK, lw=2.4)
        rrect(cv, 370, 330, 570, 470, 8, (252, 252, 254), lw=2.4)                    # the schedule on a board
        for r in range(5):
            cv.stroke([(390, 360 + r * 24), (540, 360 + r * 24)], (180, 190, 210), 2.4)
            cv.ellipse(380 + 10, 360 + r * 24, 4, 4, ACC["chula"], ink=None)
        st(cv, "chula", 640, 700, pose=reach("chula", 640, 700, 30, 1.0, {"R": (590, 520)}, kinds=("point", "relaxed")), ex="eager", th=30, k=1.0)
        u = ease(fr(t, BE, 7, 0.45, 0.8))
        st(cv, "chula", 640, 700, pose=reach("chula", 640, 700, 30, 1.0, {"L": (610, 470)}, kinds=("relaxed", "open")), ex="plead", th=30, k=1.0) if False else None
        phone(cv, 800, 600, 1.0, t=t) if False else None
        cv.fill([(796, 560), (826, 560), (826, 616), (796, 616)], (40, 44, 60), ink=INK, lw=2.0)
        ov.append(("0", 811, 520, 56, (255, 120, 100), ease(fr(t, BE, 7, 0.55, 0.7))))
        st(cv, "thamma", 940, 700, pose=REST, ex="deadpan", th=-30, flip=True, k=0.9)
    else:
        tidepool(cv, t)
        for q in range(5):                                                        # a little fire with a coconut-shell pot
            pass
        campfire(cv, 360, 700, t, 0.7, 0.8)
        cv.fill(spline([(318, 614), (320, 590), (400, 590), (402, 614)], closed=True, n=2), (126, 88, 56), ink=INK, lw=2.4)
        for q in range(3):
            u = (t * 0.7 + q / 3) % 1.0
            cv.ellipse(360 + 12 * math.sin(q + t), 580 - 60 * u, 12, 9, (255, 255, 255), ink=None, alpha=int(180 * (1 - u)))
        st(cv, "mahidol", 560, 700, pose=reach("mahidol", 560, 700, 30, 1.0, {"R": (460, 560)}, kinds=("point", "relaxed")), ex="deadpan", th=30, k=1.0,
           mouth=mouth_of(t, B[8] + 0.6, B[8] + 4.5, 2))
        # Songkhla far away at the water's edge, watching
        st(cv, "psu", 1030, 560, pose=REST, ex="deadpan", th=-80, flip=True, k=0.62)
        cv.ellipse(1030, 585, 60, 8, (0, 0, 0), ink=None, alpha=30)
        ov.append(("•_•", 900, 430, 36, (255, 255, 255), 0.5))
    cv.pop()
    pulse_ov(ov, t)
