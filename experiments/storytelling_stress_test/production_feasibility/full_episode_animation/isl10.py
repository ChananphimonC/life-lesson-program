"""Island, scene 10 (hour 44): building the raft - bamboo and coconut-fibre rope, the engineers' numbers match, Silpakorn's sail made of everybody's shirts, Chula's night rota, Mahidol checks feet."""
from isl_common import *  # noqa: F401,F403

NAME, I = "isl10", 10
DUR = scene_dur(I)
CAPS = []
MARK = ["ชั่วโมงที่สี่สิบสี่", "เกษตรกับสงขลานครินทร์ตัดไผ่", "ลาดกระบังกับบางมดคำนวณ", "ส่วนศิลปากรขอเสื้อ", "ทุกคนถามว่า ทำไมต้องสีฉูดฉาด", "จุฬาจัดเวรทำงาน", "มหิดลเดินตรวจเท้า", "ทุกอย่างพร้อมแล้ว"]
B = beats(I, MARK)
BE = B + [DUR - TAIL]
CUES = [(B[1] + 2.0, "thump", 0.5), (B[2] + 3.0, "ding", 0.5), (B[3] + 2.0, "whoosh", 0.4), (B[4] + 1.0, "pop", 0.4), (B[6] + 1.0, "sigh", 0.4), (B[7] + 1.0, "chime", 0.5)]


def draw(cv, t, ov):
    cv.push(0, 0, scale=1.0)
    tick(t)
    k = which(t, B)
    tod = 0.2 + 0.1 * ((t - B[0]) / (B[7] - B[0] + 1e-6)) if k < 6 else (0.7 if k == 6 else 1.0)
    raft_yard(cv, t, min(1.0, tod + (0.5 if k >= 5 else 0.0)))
    nbuilt = [0.0, 0.0, 0.4, 0.8, 1.0, 1.0, 1.0, 1.0][k] + (0.4 * fr(t, BE, k, 0.0, 1.0) if k in (1, 2) else 0.0)
    if k in (0, 1):
        st_ = fr(t, BE, 1, 0.0, 1.0) if k == 1 else 0.0
        for q in range(4):
            bamboo(cv, 140 + q * 30, 700 - 10 * q, 240, -10, w=15)
        raft(cv, 760, 650, 440, t, building=min(1.0, 0.1 + 0.7 * st_) if k == 1 else 0.0, sail_on=False)
        pa = ["kaset", "psu"]
        for j, w in enumerate(pa):
            st(cv, w, 420 + 100 * j, 705, pose=reach(w, 420 + 100 * j, 705, 30, 0.95, {"R": (560 + 30 * j, 640)}, kinds=("grip", "relaxed")), ex="eager", th=30, k=0.95, seed=j, lean=6 * math.sin(t * 5 + j))
        for q in range(5):                                                  # coconut-husk rope being twisted
            cv.stroke(spline([(300, 700 - 8 * q), (330, 690 - 8 * q + 3 * math.sin(t * 4 + q)), (360, 700 - 8 * q)], n=3), (170, 130, 80), 5)
    elif k in (2, 3):
        raft(cv, 760, 650, 440, t, building=0.85 + 0.15 * fr(t, BE, 2, 0.3, 1.0) if k == 2 else 1.0, sail_on=False)
        if k == 2:
            st(cv, "kmitl", 380, 705, pose=reach("kmitl", 380, 705, 30, 0.95, {"R": (520, 560)}, kinds=("point", "relaxed")), ex="eager", th=30, k=0.95, mouth=mouth_of(t, B[2] + 0.5, B[3] - 0.5, 2))
            st(cv, "kmutt", 1140, 705, pose=reach("kmutt", 1140, 705, -30, 0.95, {"R": (1000, 560)}, kinds=("point", "relaxed")), ex="eager", th=-30, flip=True, k=0.95, mouth=mouth_of(t, B[2] + 1.5, B[3] - 0.3, 3))
            u = ease(fr(t, BE, 2, 0.55, 0.7))
            ov.append(("= ", 760, 440, 120, (120, 230, 150), u))
            ov.append(("!", 380, 380, 80, (255, 255, 255), u))
        else:
            # Silpakorn at a table of sewn shirts, the sail still flat on the sand
            cv.fill(spline([(300, 690), (640, 650), (980, 690), (900, 720), (360, 720)], closed=True, n=3), (236, 92, 54), ink=INK, lw=2.6, shade_col=(196, 60, 40))
            for j, w in enumerate(("silpa", "chula", "mahidol", "kku")):
                st(cv, w, 320 + 170 * j, 705, pose=reach(w, 320 + 170 * j, 705, 30, 0.8, {"R": (360 + 170 * j, 676)}, kinds=("grip", "relaxed")), ex="eager" if j == 0 else "happy", th=30, k=0.8, seed=j, lean=6 * math.sin(t * 4 + j))
            cv.ellipse(640, 668, 50, 22, (255, 214, 90), ink=INK, lw=2.0)
    elif k == 4:
        raft(cv, 760, 650, 440, t, building=1.0, sail_on=True, wind=0.8)
        st(cv, "silpa", 400, 705, pose=POINT_UP, ex="smug", th=30, k=1.0, mouth=mouth_of(t, B[4] + 0.6, B[5] - 0.6, 4))
        for j, w in enumerate(("chula", "thamma", "kaset", "kmitl", "kmutt")):
            st(cv, w, 130 + 90 * j, 705 + 5 * (j % 2), pose=REST, ex="gape", th=30, k=0.55, seed=j)
        ov.append(("?", 300, 420, 90, (255, 255, 255), 0.7))
    elif k == 5:
        raft(cv, 760, 650, 440, t, building=1.0, sail_on=True, wind=0.8)
        campfire(cv, 280, 700, t, 0.8)
        st(cv, "chula", 440, 705, pose=reach("chula", 440, 705, 30, 0.95, {"R": (500, 560)}, kinds=("point", "relaxed")), ex="eager", th=30, k=0.95)
        rrect(cv, 480, 420, 640, 520, 6, (252, 252, 254), lw=2.4)
        for r in range(4):
            cv.stroke([(498, 446 + r * 20), (620, 446 + r * 20)], (180, 190, 210), 3)
            cv.ellipse(492, 446 + r * 20, 3, 3, ACC["chula"], ink=None)
        for j, w in enumerate(("kaset", "psu", "kku")):
            st(cv, w, 1080 + 60 * j - 40, 705, pose=reach(w, 1040 + 60 * j, 705, -30, 0.7, {"R": (1000, 640)}, kinds=("grip", "relaxed")), ex="happy", th=-30, flip=True, k=0.7, seed=j, lean=5 * math.sin(t * 4 + j))
    elif k == 6:
        raft(cv, 760, 650, 440, t, building=1.0, sail_on=True, wind=0.8)
        campfire(cv, 280, 700, t, 0.8)
        st(cv, "mahidol", 440, 705, pose=reach("mahidol", 440, 705, 30, 0.95, {"R": (520, 690)}, kinds=("relaxed", "relaxed")), ex="deadpan", th=30, k=0.95, lean=12)
        for j, w in enumerate(("kmitl", "kmutt", "kaset")):
            lying(cv, w, 620 + 150 * j, 650, 0.5, flip=False)
        ov.append(("z", 520, 520, 50, (255, 255, 255), 0.5 + 0.5 * math.sin(t * 2)))
    else:
        raft(cv, 760, 650, 440, t, building=1.0, sail_on=True, wind=1.0)
        for j, w in enumerate(ORDER10):
            st(cv, w, 100 + 108 * j, 705 + 6 * (j % 2), pose=CHEER if j % 2 else REST, ex="happy", th=30, k=0.5, seed=j)
        ov.append(("•", 100, 100, 1, (255, 255, 255), 0.0))
    cv.pop()
    pulse_ov(ov, t)
