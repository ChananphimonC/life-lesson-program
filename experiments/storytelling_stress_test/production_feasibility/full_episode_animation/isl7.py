"""Island, scene 7 (hour 16, night): the glowing sea and fireflies, the campfire circle, everyone says what they will do first when they get home, Chula's secret card,
Mahidol's quiet sentence, the engineers shake hands."""
from isl_common import *  # noqa: F401,F403

NAME, I = "isl7", 7
DUR = scene_dur(I)
CAPS = []
MARK = ["ชั่วโมงที่สิบหก", "แล้วเชียงใหม่ก็เอ่ยขึ้นเบา", "ศิลปากรบอก ส่งงาน", "เกษตรบอก ไปดูว่าผัก", "ขอนแก่นบอก กินข้าวเหนียว", "ธรรมศาสตร์ที่ปกติพูดเก่งที่สุด", "จุฬากำมือแน่น", "แล้วบางมดก็พูดเรียบ",
        "มหิดลที่นั่งนิ่งมาตลอด", "ลาดกระบังกับบางมดมองหน้ากัน", "แต่พอรุ่งเช้า"]
B = beats(I, MARK)
BE = B + [DUR - TAIL]
CUES = [(B[1] + 0.5, "chime", 0.4), (B[2] + 1.5, "laugh", 0.4), (B[6] + 1.0, "sigh", 0.4), (B[8] + 1.0, "chime", 0.5), (B[9] + 2.0, "ding", 0.5), (B[10] + 0.5, "whoosh", 0.4)]
CIRCLE = [("chula", 380, 40), ("thamma", 500, 40), ("mahidol", 600, 20), ("kaset", 700, 0), ("kmitl", 800, -20), ("kmutt", 890, -30), ("silpa", 980, -40), ("cmu", 1060, -40), ("kku", 1130, -40), ("psu", 1190, -40)]
SEAT = {"chula": (270, 40), "thamma": (400, 40), "mahidol": (520, 30), "kaset": (770, -30), "kmitl": (870, -40), "kmutt": (960, -40), "silpa": (1060, -40), "cmu": (150, 40), "kku": (1160, -40), "psu": (60, 40)}


def circle(cv, t, ex_map=None, say=None, glow=1.0):
    night_beach(cv, t, glow)
    fireflies(cv, t, 36, 760, 1280, 330, 640)
    campfire(cv, 640, 690, t, 1.0)
    ex_map = ex_map or {}
    for w, (x, th) in SEAT.items():
        k = 0.62
        pose = REST
        st(cv, w, x, 706 + 6 * (len(w) % 2), pose=pose, ex=ex_map.get(w, "neutral"), th=th, flip=th < 0, k=k, seed=len(w))
    # warm firelight on the faces
    cv.ellipse(640, 600, 420, 120, (255, 160, 70), ink=None, alpha=28)


def draw(cv, t, ov):
    cv.push(0, 0, scale=1.0)
    tick(t)
    k = which(t, B)
    if k == 0:
        night_beach(cv, t, 1.0)
        fireflies(cv, t, 50, 700, 1280, 330, 640)
        for q in range(5):
            fish(cv, 200 + 160 * q + (t * 40) % 80, 470 + 40 * math.sin(t * 2 + q), 0.8, t, col=(120, 240, 255), seed=q)
        st(cv, "cmu", 640, 700, pose=REST, ex="happy", th=20, k=0.8)
        for j, w in enumerate(("chula", "thamma", "mahidol", "kaset")):
            st(cv, w, 160 + j * 110, 705, pose=REST, ex="gape", th=40, k=0.6, seed=j)
        campfire(cv, 900, 690, t, 0.8)
    elif k == 1:
        circle(cv, t, {"cmu": "happy"})
        say_waves(cv, 190, 560, t, B[1] + 0.3, B[2] - 0.6)
        ov.append(("?", 150, 380, 70, (255, 255, 255), 0.7))
    elif k in (2, 3, 4):
        who = {2: "silpa", 3: "kaset", 4: "kku"}[k]
        circle(cv, t, {who: "laugh"})
        x = SEAT[who][0]
        # a thought bubble with a tiny picture of what they miss
        bubble(cv, x, 300, 150, 110, tail=(0, 80), alpha=235)
        if k == 2:
            rrect(cv, x - 40, 270, x + 40, 330, 4, (252, 252, 254), lw=2.0)
            cv.stroke([(x - 28, 290), (x + 28, 290)], (180, 190, 210), 2.4)
            cv.stroke([(x - 28, 304), (x + 10, 304)], (180, 190, 210), 2.4)
        elif k == 3:
            for q in range(3):
                cv.stroke([(x - 30 + q * 30, 330), (x - 30 + q * 30, 296)], (60, 140, 70), 5)
                cv.ellipse(x - 30 + q * 30, 290, 12, 9, (96, 200, 96), ink=INK, lw=1.4)
        else:
            cv.ellipse(x, 312, 36, 22, (252, 248, 236), ink=INK, lw=2.0)
            cv.ellipse(x, 304, 30, 12, (250, 236, 200), ink=None)
    elif k == 5:
        circle(cv, t, {"thamma": "deadpan"})
        x = SEAT["thamma"][0]
        bubble(cv, x, 300, 150, 110, tail=(0, 80), alpha=235)
        rrect(cv, x - 44, 280, x - 4, 330, 3, (190, 140, 100), lw=2.0)
        cv.ellipse(x + 22, 316, 16, 14, (252, 252, 254), ink=INK, lw=2.0)
        cv.stroke([(x + 12, 296), (x + 14, 288)], (255, 255, 255), 3, alpha=180)
    elif k == 6:
        circle(cv, t, {"chula": "plead"})
        # Chula's card
        x = SEAT["chula"][0]
        u = ease(fr(t, BE, 6, 0.1, 0.5))
        rrect(cv, x + 80, 560 - 40 * u, x + 150, 600 - 40 * u, 5, (250, 244, 214), lw=2.4)
        cv.ellipse(x + 100, 580 - 40 * u, 7, 7, (140, 96, 60), ink=INK, lw=1.6)
        cv.stroke([(x + 114, 574 - 40 * u), (x + 140, 574 - 40 * u)], (180, 150, 110), 2.2)
        cv.stroke([(x + 114, 588 - 40 * u), (x + 136, 588 - 40 * u)], (180, 150, 110), 2.2)
        say_waves(cv, x + 50, 500, t, B[6] + 1.0, B[7] - 0.6)
    elif k == 7:
        circle(cv, t, {"chula": "plead", "kmutt": "deadpan"})
        say_waves(cv, SEAT["kmutt"][0] - 40, 500, t, B[7] + 0.6, B[7] + 3.4, flip=True)
    elif k == 8:
        circle(cv, t, {"mahidol": "deadpan"})
        say_waves(cv, SEAT["mahidol"][0] + 50, 500, t, B[8] + 0.8, B[8] + 4.5)
        ov.append(("•", 640, 300, 1, (255, 255, 255), 0.0))
    elif k == 9:
        circle(cv, t, {})
        a = ease(fr(t, BE, 9, 0.4, 0.8))
        # the engineers meet across the fire and shake hands
        cv.ellipse(840, 590, 80, 90, (255, 214, 130), ink=None, alpha=int(70 * a))
    else:
        night_beach(cv, t * 0.5, 0.4)
        # a pale, early morning start: something odd lies on the sand (the turtle tracks)
        dawn = ease(fr(t, BE, 10, 0.2, 1.0))
        cv.fill([(0, 0), (W, 0), (W, H), (0, H)], (255, 190, 180), ink=None, alpha=int(110 * dawn))
        for j, w in enumerate(ORDER10):
            lying(cv, w, 120 + j * 115, 630 + 10 * (j % 2), 0.5, flip=j % 2 == 0)
        ov.append(("?", 640, 330, 100, (255, 255, 255), ease(fr(t, BE, 10, 0.5, 0.7))))
    cv.pop()
    pulse_ov(ov, t)
