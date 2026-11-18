"""Island, scene 12 (hour 72): the ferry horn in the fog, signals (mirror, three fires, the sail), the captain, 'who is the leader' answered by ten voices and a monkey, the captain from Ramkhamhaeng,
the monkey waves goodbye, everyone argues again who boards first, the closing question."""
from isl_common import *  # noqa: F401,F403

NAME, I = "isl12", 12
DUR = scene_dur(I)
CAPS = []
MARK = ["ชั่วโมงที่เจ็ดสิบสอง", "ลาดกระบังชูกระจก", "กัปตันที่ยืนอยู่หัวเรือ", "สิบเสียงตอบพร้อมกัน", "ขึ้นมาก่อนเถอะ", "ผมจบรามคำแหง", "ประธานกระโดดลงจากไหล่", "พอขึ้นเรือเรียบร้อย", "เจ็ดสิบสองชั่วโมงที่ผ่านมา",
        "ถ้าคุณต้องไปติดเกาะ"]
B = beats(I, MARK)
BE = B + [DUR - TAIL]
CUES = [(B[0] + 1.0, "whoosh", 0.5), (B[1] + 2.0, "ding", 0.6), (B[2] + 1.0, "chime", 0.5), (B[3] + 0.5, "cheer", 0.5), (B[6] + 0.5, "pop", 0.4), (B[7] + 1.0, "laugh", 0.5), (B[8] + 1.0, "chime", 0.5)]


def signal_fires(cv, t, n=3):
    for j in range(n):
        x = 260 + 120 * j
        y = 640 - 50 * (1 if j == 1 else 0)
        campfire(cv, x, y, t, 0.7)
        for q in range(4):
            u = (t * 0.4 + q / 4 + j * 0.2) % 1.0
            cv.ellipse(x + 20 * math.sin(u * 5 + j), y - 120 - 280 * u, 20 + 36 * u, 16 + 30 * u, (230, 230, 236), ink=None, alpha=int(190 * (1 - u)))


def draw(cv, t, ov):
    cv.push(0, 0, scale=1.0)
    tick(t)
    k = which(t, B)
    if k == 0:
        ferry_dawn(cv, t, 1.0)
        raft(cv, 780, 610, 420, t, building=1.0, sail_on=True, wind=0.7, rock=0.6)
        u = ease(fr(t, BE, 0, 0.0, 1.0))
        ferry(cv, 1500 - 1000 * u, 420, 0.45 + 0.1 * u, t, flip=False)
        for j, w in enumerate(("psu", "kaset", "kku", "chula")):
            st(cv, w, 640 + 100 * j, 620 + 6 * (j % 2), pose=REST, ex="gape", th=0, k=0.4, seed=j)
        ov.append(("•", 100, 100, 1, (255, 255, 255), 0.0))
    elif k == 1:
        ferry_dawn(cv, t, 0.6)
        ferry(cv, 520, 420, 0.7, t)
        st(cv, "kmitl", 640, 700, pose=reach("kmitl", 640, 700, -20, 1.0, {"R": (760, 470)}, kinds=("grip", "relaxed")), ex="eager", th=-20, flip=False, k=1.0)
        cv.ellipse(766, 470, 22, 22, (200, 230, 250), ink=INK, lw=2.4)
        mirror_flash(cv, 766, 470, t, 1.5)
        for q in range(3):
            x0 = 766 - (t * 220 + q * 110) % 360
            cv.stroke([(x0, 456 - (766 - x0) * 0.02), (x0 - 40, 454 - (766 - x0) * 0.02)], (255, 255, 230), 5, alpha=210)
        signal_fires(cv, t)
    elif k == 2:
        ferry_dawn(cv, t, 0.2)
        raft(cv, 520, 610, 460, t, building=1.0, sail_on=True, wind=0.9, rock=0.4)
        ferry(cv, 1040, 440, 0.62, t, flip=False)
        st(cv, "captain", 1060, 330, pose=reach("captain", 1060, 330, -20, 0.5, {"R": (990, 250)}, kinds=("point", "relaxed")), ex="gape", th=-20, flip=True, k=0.5, mouth=mouth_of(t, B[2] + 0.4, B[3] - 0.6, 1))
        say_waves(cv, 1020, 220, t, B[2] + 0.4, B[3] - 0.6, flip=True)
        ov.append(("?", 1040, 150, 70, (255, 255, 255), 0.7))
    elif k == 3:
        ferry_dawn(cv, t, 0.2)
        raft(cv, 400, 660, 560, t, building=1.0, sail_on=True, wind=0.9, rock=0.3)
        ferry(cv, 1020, 420, 0.8, t)
        for j, w in enumerate(ORDER10):
            x = 220 + 60 * j
            st(cv, w, x, 640 + 6 * (j % 2), pose=ARMS_UP if j % 2 else POINT_UP, ex="shout", th=-30 if False else 30, k=0.46, seed=j, mouth=mouth_of(t, B[3] + 0.3, B[4] - 0.4, j))
        monkey(cv, 440, 530, 0.8, "arms_up", t, mouth=True)
        ov.append(("ฉัน! ผม! เรา!", 640, 140, 70, (255, 244, 200), 0.9))
    elif k == 4:
        ferry_dawn(cv, t, 0.2)
        ferry(cv, 640, 470, 1.0, t)
        st(cv, "captain", 640, 330, pose=reach("captain", 640, 330, 0, 0.6, {"R": (720, 270)}, kinds=("open", "relaxed")), ex="happy", th=0, k=0.6, mouth=mouth_of(t, B[4] + 0.3, B[5] - 0.5, 2))
        ov.append(("•", 100, 100, 1, (255, 255, 255), 0.0))
    elif k == 5:
        ferry_dawn(cv, t, 0.2)
        ferry(cv, 640, 470, 1.0, t)
        st(cv, "captain", 640, 330, pose=reach("captain", 640, 330, 0, 0.7, {"R": (560, 260)}, kinds=("open", "relaxed")), ex="laugh", th=0, k=0.7, mouth=mouth_of(t, B[5] + 0.3, B[5] + 4.0, 3))
        for j, w in enumerate(ORDER10):
            st(cv, w, 150 + 105 * j, 705 + 6 * (j % 2), pose=REST, ex="aha", th=30 if j < 5 else -30, flip=j >= 5, k=0.48, seed=j)
        for q in range(8):                                                       # a night-class lamp icon: a little glowing book and a sun/moon pair
            pass
    elif k == 6:
        ferry_dawn(cv, t, 0.2)
        a = ease(fr(t, BE, 6, 0.2, 0.9))
        palm(cv, 1100, 700, 360, t, -50, 1.0)
        monkey(cv, 1100 - 40 * a, 700, 1.3, "sit" if a < 0.5 else "arms_up", t, mouth=True)
        ov.append(("•", 100, 100, 1, (255, 255, 255), 0.0))
        for j, w in enumerate(("kaset", "kku", "psu", "cmu")):
            st(cv, w, 300 + 100 * j, 705, pose=REST if j else CHEER, ex="happy", th=-30, flip=True, k=0.62, seed=j)
        ferry(cv, 400, 380, 0.5, t, smoke=False)
    elif k == 7:
        ferry_dawn(cv, t, 0.2)
        ferry(cv, 640, 480, 1.15, t)
        a = in_(t, BE, 7, 0.3, 0.95)
        st(cv, "chula", 500, 330, pose=POINT_FWD if a else REST, ex="shout" if a else "happy", th=30, k=0.5, mouth=mouth_of(t, B[7] + 1.0, B[8] - 0.5, 2) if a else 0)
        st(cv, "thamma", 780, 330, pose=POINT_FWD if a else REST, ex="shout" if a else "happy", th=-30, flip=True, k=0.55, mouth=mouth_of(t, B[7] + 1.4, B[8] - 0.4, 3) if a else 0)
        for j, w in enumerate(("mahidol", "kaset", "kmitl", "kmutt", "silpa", "cmu", "kku", "psu")):
            st(cv, w, 330 + 80 * j, 330, pose=HEADS if j == 0 else REST, ex="laugh", th=0, k=0.46, seed=j)
        st(cv, "captain", 1000, 330, pose=HEADS, ex="yikes", th=-30, flip=True, k=0.6)
    else:
        ferry_dawn(cv, t, 0.0)
        ferry(cv, 640, 480, 1.15, t)
        for j, w in enumerate(ORDER10):
            st(cv, w, 250 + 80 * j, 330, pose=CHEER if j % 2 else REST, ex="happy", th=0, k=0.5, seed=j)
        # the ten scarves in a row on the screen at the end: one colour each
        cols = [ACC[x] for x in ("chula", "thamma", "mahidol", "kaset", "kmitl", "kmutt", "silpa", "cmu", "kku", "psu")]
        for j, c in enumerate(cols):
            cv.ellipse(300 + 70 * j, 70, 20, 20, c, ink=INK, lw=2.4)
        ov.append(("คุณคือมหาวิทยาลัยไหน?", 640, 130, 62, (255, 244, 200), ease(fr(t, BE, 9, 0.2, 0.5))))
    cv.pop()
    pulse_ov(ov, t)
