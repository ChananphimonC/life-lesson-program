"""Island, scene 11 (hour 66): launch in the dark morning, the first wave, Songkhla at the tiller, the engineers jump to the sides, Thammasat calls the beat, Kasetsart and Khon Kaen retie knots,
Chula reads the rota, Silpakorn hugs the mast, Chiang Mai calms everybody, Mahidol counts the breathing."""
from isl_common import *  # noqa: F401,F403

NAME, I = "isl11", 11
DUR = scene_dur(I)
CAPS = []
MARK = ["ชั่วโมงที่หกสิบหก", "ทุกคนลากแพลงน้ำ", "แต่คลื่นลูกแรก", "สงขลานครินทร์นั่งหัวแพ", "ลาดกระบังกับบางมดกระโดด", "ธรรมศาสตร์ตะโกนนับจังหวะ", "เกษตรกับขอนแก่นนั่งแก้ปม", "ศิลปากรกอดเสาใบเรือ",
        "ส่วนเชียงใหม่ที่ตัวเปียกโชก", "แล้วมหิดลก็ตะโกนบอก"]
B = beats(I, MARK)
BE = B + [DUR - TAIL]
CUES = [(B[1] + 1.0, "thump", 0.5), (B[1] + 5.0, "cheer", 0.4), (B[2] + 0.5, "whoosh", 0.6), (B[4] + 1.0, "thump", 0.5), (B[5] + 2.0, "step", 0.4), (B[7] + 1.0, "gasp", 0.4), (B[9] + 1.0, "ding", 0.4)]
DECK_Y = 600


def on_raft(cv, t, ph=0.0, rock=1.0, wind=1.0, tear=0.0, building=1.0):
    storm_sea(cv, t, flash=max(0.0, math.sin(t * 1.3 + ph)) ** 14 * 0.9, rain=1.0)
    raft(cv, 640, 650, 540, t, tilt=0.0, building=building, wind=wind, tear=tear, rock=rock)


def draw(cv, t, ov):
    cv.push(0, 0, scale=1.0)
    tick(t)
    k = which(t, B)
    sway = 3 * math.sin(t * 1.4)
    if k == 0:
        beach_morning(cv, t, wreck=False)
        cv.fill([(0, 0), (W, 0), (W, H), (0, H)], (18, 24, 56), ink=None, alpha=130)
        for q in range(50):
            x = (q * 97 + t * 80) % W
            y = ((t * 800 + q * 53) % 760) - 20
            cv.stroke([(x, y), (x - 22, y + 56)], (214, 230, 244), 2, alpha=170)
        raft(cv, 640, 560, 480, t, building=1.0, sail_on=True, wind=0.6)
        for j, w in enumerate(ORDER10):
            st(cv, w, 160 + 105 * j, 705, pose=PUSH, ex="shout", th=30, k=0.5, seed=j, lean=8)
    elif k == 1:
        beach_morning(cv, t, wreck=False)
        cv.fill([(0, 0), (W, 0), (W, H), (0, H)], (18, 24, 56), ink=None, alpha=130)
        u = ease(fr(t, BE, 1, 0.1, 0.8))
        raft(cv, 480 + 380 * u, 560 + 40 * u, 480, t, building=1.0, sail_on=True, wind=0.8, rock=u)
        for j, w in enumerate(ORDER10):
            walker(cv, w, 90 + 90 * j * (1 - 0.5 * u) + 200 * u, 710, t, speed=7, stride=12, lift=9, ex="happy", k=0.5, seed=j) if u < 0.4 else None
        ov.append(("3 2 1", 640, 160, 90, (255, 244, 200), 0.9 if u < 0.2 else 0.0))
        if u > 0.9:
            ov.append(("•", 640, 200, 1, (255, 255, 255), 0.0))
    elif k == 2:
        on_raft(cv, t, 0.0, wind=1.0, tear=0.0)
        a = ease(fr(t, BE, 2, 0.2, 0.7))
        cv.push(0, 0, rot=-6 * a * math.sin(t * 3), pivot=(640, 600))
        for j, w in enumerate(ORDER10[:5]):
            st(cv, w, 380 + 110 * j, DECK_Y + 20, pose=CHEER if j % 2 else HEADS, ex="yikes", th=30, k=0.5, seed=j, lean=10 * a)
        cv.pop()
        ov.append(("!", 640, 220, 120, (255, 255, 255), ease(fr(t, BE, 2, 0.1, 0.3))))
    elif k == 3:
        on_raft(cv, t, 1.0, wind=1.0)
        st(cv, "psu", 520, DECK_Y + 28, pose=reach("psu", 520, DECK_Y + 28, 40, 0.8, {"R": (610, 560), "L": (590, 580)}, kinds=("grip", "grip")), ex="deadpan", th=40, k=0.8, mouth=mouth_of(t, B[3] + 0.8, B[4] - 0.5, 2), lean=8)
        cv.stroke([(610, 600), (690, 640)], (150, 106, 70), 8)
        say_waves(cv, 590, 460, t, B[3] + 0.8, B[4] - 0.5)
    elif k == 4:
        on_raft(cv, t, 2.0, wind=1.0)
        j2 = ease(fr(t, BE, 4, 0.1, 0.5))
        st(cv, "kmitl", 420 - 40 * j2, DECK_Y + 24 - 50 * math.sin(math.pi * j2), pose=ARMS_UP, ex="shout", th=40, k=0.7, seed=1)
        st(cv, "kmutt", 860 + 40 * j2, DECK_Y + 24 - 50 * math.sin(math.pi * j2), pose=ARMS_UP, ex="shout", th=-40, flip=True, k=0.7, seed=2)
        st(cv, "psu", 640, DECK_Y + 28, pose=REST, ex="deadpan", th=0, k=0.7, lean=6)
        ov.append(("OK", 640, 250, 100, (120, 230, 150), ease(fr(t, BE, 4, 0.5, 0.7))))
    elif k == 5:
        on_raft(cv, t, 3.0, wind=1.0)
        beat = math.sin(t * 6)
        st(cv, "thamma", 380, DECK_Y + 28, pose=reach("thamma", 380, DECK_Y + 28, 40, 0.8, {"R": (480, 520 - 14 * beat)}, kinds=("point", "relaxed")), ex="shout", th=40, k=0.8, mouth=mouth_of(t, B[5] + 0.5, B[6] - 0.5, 3), lean=6)
        say_waves(cv, 450, 440, t, B[5] + 0.5, B[6] - 0.5)
        for j, w in enumerate(("chula", "kku", "cmu", "silpa", "mahidol")):
            st(cv, w, 620 + 100 * j, DECK_Y + 28 + 3 * (j % 2), pose=reach(w, 620 + 100 * j, DECK_Y + 28, -40, 0.62, {"R": (600 + 100 * j, 630 + 20 * math.sin(t * 6 + j))}, kinds=("grip", "relaxed")), ex="pant", th=-30, flip=True, k=0.62, seed=j)
        ov.append(("1 2  1 2", 640, 200, 70, (255, 244, 200), 0.8))
    elif k == 6:
        on_raft(cv, t, 4.0, wind=1.0)
        for j, w in enumerate(("kaset", "kku")):
            st(cv, w, 500 + 150 * j, DECK_Y + 40, pose=reach(w, 500 + 150 * j, DECK_Y + 40, 30, 0.8, {"R": (560 + 150 * j, 640), "L": (590 + 150 * j, 650)}, kinds=("grip", "grip")), ex="eager", th=30, k=0.8, seed=j, lean=12 + 3 * math.sin(t * 6))
        st(cv, "chula", 900, DECK_Y + 28, pose=reach("chula", 900, DECK_Y + 28, -30, 0.7, {"R": (860, 540)}, kinds=("point", "relaxed")), ex="shout", th=-30, flip=True, k=0.7, mouth=mouth_of(t, B[6] + 1.0, B[7] - 0.6, 4))
        ov.append(("10", 860, 420, 70, (255, 244, 200), 0.9))
        say_waves(cv, 830, 440, t, B[6] + 1.0, B[7] - 0.6, flip=True)
    elif k == 7:
        on_raft(cv, t, 5.0, wind=1.0, tear=ease(fr(t, BE, 7, 0.2, 0.6)))
        st(cv, "silpa", 480, DECK_Y + 30, pose=reach("silpa", 480, DECK_Y + 30, 40, 0.8, {"R": (556, 430), "L": (540, 450)}, kinds=("grip", "grip")), ex="plead", th=40, k=0.8, mouth=mouth_of(t, B[7] + 0.5, B[8] - 0.6, 5), lean=14)
        ov.append(("•", 100, 100, 1, (255, 255, 255), 0.0))
    elif k == 8:
        on_raft(cv, t, 6.0, wind=1.0)
        st(cv, "cmu", 640, DECK_Y + 30, pose=reach("cmu", 640, DECK_Y + 30, 0, 0.9, {"R": (730, 470), "L": (550, 470)}, kinds=("open", "open")), ex="happy", th=0, k=0.9, mouth=mouth_of(t, B[8] + 0.8, B[9] - 0.6, 6))
        u = 0.5 + 0.5 * math.sin(t * 2)
        cv.ellipse(640, 480, 150 + 50 * u, 90 + 30 * u, (180, 220, 255), ink=None, alpha=int(50 + 40 * u))
        for j, w in enumerate(("chula", "thamma", "kaset", "kku")):
            st(cv, w, 190 + 100 * j + (480 if j > 1 else 0), DECK_Y + 36, pose=REST, ex="happy" if int(t * 0.5 + j) % 2 else "neutral", th=30, k=0.55, seed=j)
    else:
        on_raft(cv, t, 7.0, wind=1.0)
        st(cv, "mahidol", 640, DECK_Y + 30, pose=reach("mahidol", 640, DECK_Y + 30, 0, 0.9, {"R": (730, 440)}, kinds=("point", "relaxed")), ex="shout", th=0, k=0.9, mouth=mouth_of(t, B[9] + 0.3, B[9] + 3.0, 7))
        say_waves(cv, 700, 420, t, B[9] + 0.3, B[9] + 3.0)
        for j in range(8):
            ov.append(("•", 100, 100, 1, (255, 255, 255), 0.0))
        cv.ellipse(640, 330, 20, 20, (255, 255, 255), ink=None, alpha=int(60 * (0.5 + 0.5 * math.sin(t * 3))))
    cv.pop()
    pulse_ov(ov, t)
