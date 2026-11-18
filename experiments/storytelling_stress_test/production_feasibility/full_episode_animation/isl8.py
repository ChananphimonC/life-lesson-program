"""Island, scene 8 (hour 28, dawn of day two): the turtle's tracks and nest, Khon Kaen's hungry look (a joke), the law of the sea turtle, the monkey eyes the nest, the bamboo fence,
the net on the posts, Silpakorn's painted sign, the monkey sulks, the sky turns."""
from isl_common import *  # noqa: F401,F403

NAME, I = "isl8", 8
DUR = scene_dur(I)
CAPS = []
MARK = ["ชั่วโมงที่ยี่สิบแปด", "เจอรอยลากยาว", "ขอนแก่นท้องร้องเสียงดัง", "มหิดลกับเกษตรสั่งเสียงเข้ม", "แต่ปัญหาคือประธาน", "เกษตรกับขอนแก่นตัดไผ่", "สงขลานครินทร์ปักไม้เสาสูง", "ศิลปากรวาดป้าย",
        "ส่วนประธานนั่งมองอยู่ไกล", "แต่ฟ้าด้านหลังกำลังเปลี่ยนสี"]
B = beats(I, MARK)
BE = B + [DUR - TAIL]
CUES = [(B[1] + 0.5, "gasp", 0.5), (B[2] + 1.0, "grunt", 0.4), (B[3] + 1.0, "gasp", 0.4), (B[5] + 2.0, "thump", 0.5), (B[6] + 2.0, "thump", 0.5), (B[7] + 3.0, "ding", 0.5), (B[8] + 1.0, "sigh", 0.4)]


def nest(cv, fence=0.0, net_=0.0, sign=0.0):
    cv.ellipse(780, 660, 110, 30, (226, 198, 148), ink=INK, lw=2.4, shade_col=(200, 170, 124))
    if fence > 0:
        n = int(round(9 * fence))
        for q in range(n):
            x = 680 + q * 25
            cv.stroke([(x, 700 + (8 if q % 2 else 0) * 0), (x, 610 - 4 * (q % 3))], INK, 11)
            cv.stroke([(x, 700), (x, 610 - 4 * (q % 3))], (214, 184, 108), 7)
        if n > 2:
            cv.stroke([(680, 640), (680 + 25 * (n - 1), 640)], (150, 110, 70), 4)
    if net_ > 0:
        for q in range(9):
            cv.stroke([(690 + q * 22, 560), (690 + q * 22, 640)], (240, 240, 232), 1.4, alpha=int(200 * net_))
        for r in range(4):
            cv.stroke([(690, 570 + r * 20), (888, 570 + r * 20)], (240, 240, 232), 1.4, alpha=int(200 * net_))
    if sign > 0:
        cv.stroke([(960, 700), (960, 540)], INK, 9)
        cv.stroke([(960, 700), (960, 540)], (150, 106, 70), 6)
        rrect(cv, 880, 470, 1040, 560, 8, (236, 214, 164), lw=2.6, alpha=int(255 * sign))
        sea_turtle(cv, 960, 520, 0.5, 0.0, swim=False)
        cv.stroke([(900, 486), (1020, 546)], (220, 60, 60), 7, alpha=int(255 * sign))


def draw(cv, t, ov):
    cv.push(0, 0, scale=1.0)
    tick(t)
    k = which(t, B)
    dawn_beach(cv, t)
    for j in range(3):
        seagull(cv, 160 + 360 * j + 30 * math.sin(t * 0.8 + j), 120 + 30 * j, 1.0, t, seed=j)
    if k in (0, 1):
        if k == 1:
            nest(cv)
            for j, w in enumerate(("silpa", "chula", "thamma", "mahidol")):
                st(cv, w, 180 + j * 110, 700 + 6 * (j % 2), pose=REST, ex="gape", th=30, k=0.72, seed=j)
            st(cv, "silpa", 180, 700, pose=ARMS_UP, ex="gape", th=30, k=0.72, seed=9)
        else:
            for j, w in enumerate(ORDER10):
                lying(cv, w, 120 + j * 115, 640 + 10 * (j % 2), 0.5, flip=j % 2 == 0)
            ov.append(("!", 150, 480, 90, (255, 255, 255), 0.0 if t < B[1] - 1 else 0.8))
            sea_turtle(cv, 340, 500, 0.6, t, swim=True, flip=True)
    elif k == 2:
        nest(cv)
        st(cv, "kku", 540, 700, pose=reach("kku", 540, 700, 30, 1.0, {"R": (700, 650)}, kinds=("point", "relaxed")), ex="deadpan", th=30, k=1.0, mouth=mouth_of(t, B[2] + 0.5, B[3] - 0.6, 2))
        for j, w in enumerate(("chula", "kmitl", "kmutt")):
            st(cv, w, 940 + j * 90, 705, pose=REST, ex="gape", th=-30, flip=True, k=0.62, seed=j)
        ov.append(("•_•", 700, 600, 36, (255, 255, 255), 0.7))
    elif k == 3:
        nest(cv)
        st(cv, "mahidol", 400, 700, pose=STOP, ex="shout", th=30, k=1.0, mouth=mouth_of(t, B[3] + 0.4, B[4] - 0.6, 3))
        st(cv, "kaset", 560, 700, pose=STOP, ex="shout", th=30, k=1.0, mouth=mouth_of(t, B[3] + 1.0, B[4] - 0.4, 4))
        st(cv, "kku", 1000, 700, pose=HEADS, ex="laugh", th=-30, flip=True, k=0.9)
        ov.append(("X", 780, 540, 100, (255, 80, 80), ease(fr(t, BE, 3, 0.3, 0.5))))
    elif k == 4:
        nest(cv)
        monkey(cv, 1100 - 240 * ease(fr(t, BE, 4, 0.1, 0.9)), 720, 1.1, "stand", t, flip=True, mouth=True)
        ov.append(("•_•", 900, 620, 36, (255, 255, 255), 0.8))
        for j, w in enumerate(("kaset", "kku", "chula")):
            st(cv, w, 200 + j * 110, 705, pose=POINT_FWD, ex="yikes", th=30, k=0.7, seed=j)
    elif k in (5, 6):
        fence = ease(fr(t, BE, 5, 0.0, 0.9)) if k == 5 else 1.0
        nest(cv, fence=fence, net_=ease(fr(t, BE, 6, 0.3, 0.9)) if k == 6 else 0.0)
        if k == 5:
            for j, w in enumerate(("kaset", "kku")):
                st(cv, w, 480 + j * 110, 705, pose=reach(w, 480 + j * 110, 705, 30, 0.9, {"R": (600 + 25 * int(9 * fence) - 100 * j, 640)}, kinds=("grip", "relaxed")), ex="eager", th=30, k=0.9, seed=j)
            bamboo(cv, 140, 700, 200, -80)
            bamboo(cv, 180, 700, 200, -84)
        else:
            st(cv, "psu", 560, 700, pose=reach("psu", 560, 700, 30, 1.0, {"R": (700, 560), "L": (680, 580)}, kinds=("grip", "grip")), ex="deadpan", th=30, k=1.0)
    elif k == 7:
        nest(cv, fence=1.0, net_=1.0, sign=ease(fr(t, BE, 7, 0.3, 0.7)))
        st(cv, "silpa", 520, 700, pose=reach("silpa", 520, 700, 30, 1.0, {"R": (880, 520)}, kinds=("grip", "relaxed")), ex="aha", th=30, k=1.0, mouth=mouth_of(t, B[7] + 0.5, B[8] - 0.8, 1))
        for j, w in enumerate(("kaset", "kku", "psu")):
            st(cv, w, 140 + j * 100, 705, pose=REST, ex="aha", th=30, k=0.62, seed=j)
    elif k == 8:
        nest(cv, fence=1.0, net_=1.0, sign=1.0)
        monkey(cv, 330, 700, 1.0, "sit", t)
        ov.append(("•", 330, 560, 1, (255, 255, 255), 0.0))
        st(cv, "kku", 560, 700, pose=reach("kku", 560, 700, 30, 1.0, {"R": (380, 690)}, kinds=("grip", "relaxed")), ex="happy", th=-30, flip=False, k=0.9)
        cv.stroke(spline([(380, 700), (400, 690), (430, 700)], n=2), (60, 130, 80), 6)
    else:
        nest(cv, fence=1.0, net_=1.0, sign=1.0)
        a = ease(fr(t, BE, 9, 0.2, 0.9))
        cv.fill([(0, 0), (W, 0), (W, 400), (0, 400)], (60, 70, 100), ink=None, alpha=int(150 * a))
        for q in range(12):
            x = (q * 113 + t * 220) % W
            y = (t * 700 + q * 77) % 500
            cv.stroke([(x, y), (x - 10, y + 36)], (220, 236, 250), 2, alpha=int(180 * a))
        for j, w in enumerate(("kaset", "kku", "psu", "silpa")):
            st(cv, w, 160 + j * 100, 705, pose=HEADS if j == 0 else REST, ex="yikes", th=30, k=0.62, seed=j)
        ov.append(("!", 400, 380, 90, (255, 255, 255), 0.8))
    cv.pop()
    pulse_ov(ov, t)
