"""Island, scene 9 (hour 34): rain, the cave, Chula's meeting (this time a good idea), the classroom in the cave where everybody teaches one skill, the rota, the monkey chairman refuses to lead."""
from isl_common import *  # noqa: F401,F403

NAME, I = "isl9", 9
DUR = scene_dur(I)
CAPS = []
MARK = ["ชั่วโมงที่สามสิบสี่", "เชียงใหม่ยิ้ม ถ้ำเย็นดีเนอะ", "ฝนตกทั้งบ่าย", "จุฬายกมือขึ้นอย่างภูมิใจ", "เกษตรสอนฟั่นเชือก", "สงขลานครินทร์สอนผูกปม", "มหิดลสอนปฐมพยาบาล", "บางมดกับลาดกระบังสอน",
        "ขอนแก่นสอนทำอาหาร", "ศิลปากรสอนผสมสี", "เชียงใหม่สอนวิธีหายใจ", "ธรรมศาสตร์ก็สอนอย่างหนึ่ง", "คนแรกที่ได้นำคือประธาน"]
B = beats(I, MARK)
BE = B + [DUR - TAIL]
CUES = [(B[0] + 1.0, "whoosh", 0.4), (B[2] + 1.0, "sigh", 0.4), (B[3] + 1.0, "ding", 0.5), (B[5] + 1.0, "pop", 0.3), (B[8] + 1.0, "pop", 0.3), (B[11] + 2.0, "chime", 0.4), (B[12] + 1.0, "laugh", 0.5)]
SEATS = {"chula": 160, "thamma": 260, "mahidol": 360, "kaset": 460, "kmitl": 560, "kmutt": 660, "silpa": 760, "cmu": 860, "kku": 960, "psu": 1060}


def cave_room(cv, t, fire=1.0):
    cave(cv, t, 1.0, fire)
    campfire(cv, 420, 690, t, 0.9, 0.8)


def draw(cv, t, ov):
    cv.push(0, 0, scale=1.0)
    tick(t)
    k = which(t, B)
    if k == 0:
        forest(cv, t, dim=0.55)
        for q in range(70):
            x = (q * 97 + t * 50) % W
            y = ((t * 900 + q * 53) % 760) - 20
            cv.stroke([(x, y), (x - 22, y + 56)], (214, 230, 244), 2, alpha=170)
        run = fr(t, BE, 0, 0.0, 1.0)
        for j, w in enumerate(ORDER10):
            walker(cv, w, -60 + 1300 * run - j * 90, 700 + 8 * (j % 2), t, speed=11, stride=18, lift=14, ex="yikes", k=0.6, seed=j)
    elif k == 1:
        cave_room(cv, t)
        for j, w in enumerate(ORDER10):
            if w == "cmu":
                continue
            st(cv, w, 170 + 100 * j, 700 + 6 * (j % 2), pose=REST, ex="pant", th=30, k=0.6, seed=j)
        st(cv, "cmu", 640, 700, pose=reach("cmu", 640, 700, 0, 1.0, {"R": (700, 460)}, kinds=("open", "relaxed")), ex="happy", th=0, k=1.0, mouth=mouth_of(t, B[1] + 0.5, B[2] - 0.6, 1))
    elif k == 2:
        cave_room(cv, t)
        for j, w in enumerate(ORDER10):
            st(cv, w, 150 + 105 * j, 700 + 6 * (j % 2), pose=REST, ex="deadpan", th=0 if j % 2 else 30, k=0.62, seed=j)
        bats(cv, t, 8, 220, 600, 120)
    elif k == 3:
        cave_room(cv, t)
        for j, w in enumerate(ORDER10):
            if w != "chula":
                st(cv, w, 480 + 70 * (j % 9), 705 + 8 * (j % 2), pose=REST, ex="deadpan", th=-30, flip=True, k=0.55, seed=j)
        st(cv, "chula", 280, 700, pose=POINT_UP, ex="eager", th=30, k=1.0, mouth=mouth_of(t, B[3] + 0.5, B[4] - 0.8, 2))
        rrect(cv, 150, 250, 410, 400, 8, (252, 252, 254), lw=2.4)
        for r in range(5):
            cv.stroke([(176, 284 + r * 24), (380, 284 + r * 24)], (180, 190, 210), 3)
        ov.append(("!", 280, 230, 90, (255, 214, 120), ease(fr(t, BE, 3, 0.5, 0.7))))
    else:
        cave_room(cv, t)
        teach = {4: ("kaset", "rope"), 5: ("psu", "knot"), 6: ("mahidol", "first aid"), 7: ("kmitl", "calc"), 8: ("kku", "cook"), 9: ("silpa", "paint"), 10: ("cmu", "breath"), 11: ("thamma", "listen")}
        if k in teach:
            who, what = teach[k]
            x0 = 300
            # the teacher at the front (left), the others sit and watch
            others = [w for w in ORDER10 if w != who]
            for j, w in enumerate(others):
                st(cv, w, 640 + 70 * (j % 5) + 20 * (j // 5), 700 + 14 * (j // 5), pose=REST, ex="aha" if (j + k) % 3 == 0 else "happy", th=-30, flip=True, k=0.52, seed=j)
            if what == "rope":
                st(cv, who, 330, 700, pose=reach(who, 330, 700, 30, 1.0, {"R": (450, 590), "L": (430, 610)}, kinds=("grip", "grip")), ex="eager", th=30, k=1.0)
                for q in range(4):
                    cv.stroke(spline([(440, 600 + 8 * q), (480 + 10 * q, 610 + 4 * math.sin(t * 3 + q)), (520, 600 + 8 * q)], n=3), (170, 130, 80), 5)
            elif what == "knot":
                st(cv, who, 330, 700, pose=reach(who, 330, 700, 30, 1.0, {"R": (450, 580), "L": (440, 600)}, kinds=("grip", "grip")), ex="deadpan", th=30, k=1.0)
                cv.stroke(spline([(420, 600), (470, 570), (500, 610), (460, 640)], n=3), (230, 220, 190), 5)
                ov.append(("OK", 540, 440, 60, (120, 230, 150), 0.6))
            elif what == "first aid":
                st(cv, who, 330, 700, pose=reach(who, 330, 700, 30, 1.0, {"R": (440, 640)}, kinds=("point", "relaxed")), ex="deadpan", th=30, k=1.0)
                rrect(cv, 470, 620, 540, 670, 6, (250, 250, 252), lw=2.4)
                cv.stroke([(505, 630), (505, 660)], (230, 60, 70), 8)
                cv.stroke([(490, 645), (520, 645)], (230, 60, 70), 8)
            elif what == "calc":
                st(cv, who, 300, 700, pose=reach(who, 300, 700, 30, 1.0, {"R": (440, 500)}, kinds=("point", "relaxed")), ex="eager", th=30, k=1.0)
                st(cv, "kmutt", 520, 700, pose=reach("kmutt", 520, 700, 30, 1.0, {"R": (460, 500)}, kinds=("point", "relaxed")), ex="eager", th=-30, flip=True, k=1.0, seed=3) if False else None
                rrect(cv, 380, 300, 640, 450, 8, (252, 252, 254), lw=2.4)
                cv.stroke([(410, 420), (480, 340), (560, 420)], (60, 90, 150), 4)
                cv.stroke([(560, 420), (410, 420)], (60, 90, 150), 4)
                ov.append(("12°", 560, 330, 60, (200, 60, 60), 0.9))
            elif what == "cook":
                st(cv, who, 330, 700, pose=reach(who, 330, 700, 30, 1.0, {"R": (440, 620)}, kinds=("grip", "relaxed")), ex="laugh", th=30, k=1.0)
                bowl_leaf(cv, 470, 700, 1.2)
            elif what == "paint":
                st(cv, who, 330, 700, pose=reach(who, 330, 700, 30, 1.0, {"R": (470, 440)}, kinds=("grip", "relaxed")), ex="aha", th=30, k=1.0)
                rect(cv, 440, 300, 640, 480, (238, 220, 180), lw=2.4)
                cv.ellipse(540, 390, 40, 40, (236, 92, 54), ink=None)
                cv.stroke(spline([(450, 460), (540, 400), (630, 440)], n=3), (255, 200, 80), 8)
            elif what == "breath":
                st(cv, who, 330, 700, pose=reach(who, 330, 700, 20, 1.0, {"R": (400, 470), "L": (260, 470)}, kinds=("open", "open")), ex="happy", th=20, k=1.0)
                u = 0.5 + 0.5 * math.sin(t * 2)
                cv.ellipse(330, 520, 70 + 40 * u, 70 + 40 * u, (180, 220, 255), ink=None, alpha=int(70 + 50 * u))
            else:
                st(cv, who, 330, 700, pose=reach(who, 330, 700, 30, 1.0, {"R": (460, 520)}, kinds=("open", "relaxed")), ex="smug", th=30, k=1.0)
                for q in range(3):
                    cv.ellipse(500 + q * 50, 470 - q * 4, 20, 14, (255, 255, 255), ink=INK, lw=1.8)
            say_waves(cv, 400, 480, t, B[k] + 0.4, B[k] + min(4.0, (BE[k + 1] - BE[k]) - 0.6))
        else:
            for j, w in enumerate(ORDER10):
                st(cv, w, 150 + 100 * j, 700 + 6 * (j % 2), pose=REST, ex="laugh", th=30 if j < 5 else -30, flip=j >= 5, k=0.6, seed=j)
            monkey(cv, 1180, 700, 1.2, "sit", t, hold="coconut")
            ov.append(("•_•", 1180, 560, 36, (255, 255, 255), 0.6))
    cv.pop()
    pulse_ov(ov, t)
