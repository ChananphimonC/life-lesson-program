"""Island, scene 4 (hour 9): Songkhla casts a net and catches a pile of fish, Khon Kaen grills and mixes a 'zaep' bowl, Thammasat wants equal shares (nine fish, ten people),
Mahidol's one iron rule, Silpakorn plates the fish as a sunrise, the monkey eats the art."""
from isl_common import *  # noqa: F401,F403

NAME, I = "isl4", 4
DUR = scene_dur(I)
CAPS = []
MARK = ["ชั่วโมงที่เก้า", "สงขลานครินทร์ที่เห็นทะเล", "ทะเลแค่นี้ สบายมาก", "ขอนแก่นรับปลาไปย่าง", "ตะโกนว่า แซ่บ", "ธรรมศาสตร์ยกมือ ปลาเก้าตัว", "มหิดลเตือนกฎเหล็ก", "ส่วนศิลปากรไม่ยอมให้ใครแตะปลา",
        "ศิลปากรถอยออกมาเอียงคอ", "ศิลปากรกรี๊ดสุดเสียง"]
B = beats(I, MARK)
BE = B + [DUR - TAIL]
CUES = [(B[1] + 3.0, "whoosh", 0.5), (B[2] + 1.0, "pop", 0.4), (B[4] + 0.3, "ding", 0.5), (B[5] + 1.0, "pop", 0.3), (B[9] + 0.2, "gasp", 0.6), (B[9] + 1.5, "chime", 0.4)]
FISH_N = 9


def fish_pile(cv, x, y, n, s=1.0, t=0.0):
    for i in range(n):
        fish(cv, x + (i % 5) * 40 * s - 80 * s, y - (i // 5) * 20 * s, 1.1 * s, t, col=[(120, 190, 236), (236, 190, 120), (170, 214, 150)][i % 3], dead=True, flip=i % 2 == 0)


def draw(cv, t, ov):
    cv.push(0, 0, scale=1.0)
    tick(t)
    k = which(t, B)
    if k in (0, 1, 2):
        tidepool(cv, t)
        for q in range(3):
            fish(cv, 160 + q * 200 + 20 * math.sin(t + q), 470 + 14 * q, 1.0, t, seed=q)
        thr = ease(fr(t, BE, 1, 0.45, 0.8)) if k == 1 else (1.0 if k == 2 else 0.0)
        pose = reach("psu", 800, 640, 20, 0.7, {"R": (700 - 100 * thr, 470 + 60 * thr)}, kinds=("relaxed", "relaxed"))
        st(cv, "psu", 800, 640, pose=pose if k == 1 else REST, ex="deadpan", th=-50, k=0.7, flip=True)
        if k == 1:
            net(cv, 600 - 40 * (1 - thr), 500 + 60 * thr, 1.0 + 0.8 * thr, t, spread=0.3 + 0.7 * thr)
        if k == 2:
            net(cv, 420, 560, 1.3, t, spread=1.0)
            fish_pile(cv, 860, 700, FISH_N, 1.4, t)
            st(cv, "psu", 640, 700, pose=REST, ex="smug", th=-40, flip=True, k=0.9, mouth=mouth_of(t, B[2] + 0.2, B[3] - 0.6, 5))
            mirror_flash(cv, 880, 560, t, 0.5, on=fr(t, BE, 2, 0.3, 0.5) > 0)
    elif k in (3, 4):
        tidepool(cv, t)
        campfire(cv, 520, 690, t, 0.8)
        for j in range(3):
            fish_on_stick(cv, 470 + j * 50, 610 - j * 4, 1.0, ang=-60)
        fish_pile(cv, 900, 700, FISH_N, 1.2, t)
        st(cv, "kku", 760, 700, pose=reach("kku", 760, 700, -30, 1.0, {"R": (640, 620)}, kinds=("grip", "relaxed")), ex="laugh", th=-30, flip=True, k=1.0, seed=2)
        bowl_leaf(cv, 780, 700, 1.0)
        if k == 4:
            u = ease(fr(t, BE, 4, 0.0, 0.35))
            st(cv, "kku", 760, 700, pose=reach("kku", 760, 700, -30, 1.0, {"R": (790, 600)}, kinds=("grip", "relaxed")), ex="shout", th=-30, flip=True, k=1.0, mouth=mouth_of(t, B[4], B[4] + 2.0, 6))
            ov.append(("แซ่บ!", 700, 340, 80, (255, 220, 100), ease(fr(t, BE, 4, 0.05, 0.2))))
            for j, w in enumerate(("chula", "kaset", "cmu")):
                st(cv, w, 130 + j * 120, 700, pose=REST, ex="gape", th=30, k=0.7, seed=j)
    elif k == 5:
        tidepool(cv, t)
        fish_pile(cv, 640, 560, FISH_N, 1.6, t)
        st(cv, "thamma", 330, 700, pose=POINT_UP, ex="shout", th=40, k=1.0, mouth=mouth_of(t, B[5] + 0.5, B[6] - 0.6, 7))
        say_waves(cv, 400, 470, t, B[5] + 0.5, B[6] - 0.6)
        for j, w in enumerate(ORDER10[2:]):
            st(cv, w, 840 + (j % 4) * 85, 690 + 14 * (j // 4), pose=REST, ex="neutral", th=-30, flip=True, k=0.52, seed=j)
        ov.append(("9", 560, 400, 70, (255, 244, 200), 0.9))
        ov.append(("10", 700, 400, 70, (255, 244, 200), 0.9))
    elif k == 6:
        tidepool(cv, t)
        # Mahidol's iron rule: an X over a strange sea creature (a puffer-like fish)
        cv.ellipse(840, 600, 56, 44, (230, 210, 140), ink=INK, lw=2.6, shade_col=(196, 176, 108))
        for q in range(8):
            a = q * math.pi / 4
            cv.stroke([(840 + math.cos(a) * 52, 600 + math.sin(a) * 40), (840 + math.cos(a) * 66, 600 + math.sin(a) * 52)], INK, 2)
        cv.ellipse(826, 592, 4, 4, (30, 30, 30), ink=None)
        ov.append(("X", 840, 520, 120, (255, 80, 80), ease(fr(t, BE, 6, 0.3, 0.5))))
        st(cv, "mahidol", 520, 700, pose=reach("mahidol", 520, 700, 20, 1.0, {"R": (600, 520)}, kinds=("point", "relaxed")), ex="deadpan", th=20, k=1.0, mouth=mouth_of(t, B[6] + 0.8, B[7] - 0.8, 2))
        for j, w in enumerate(("kaset", "kku")):
            st(cv, w, 200 + j * 120, 700, pose=REST, ex="gape", th=30, k=0.7, seed=j)
    elif k == 7:
        tidepool(cv, t)
        # the plating: a ring of leaves, flowers and a fish sun
        cx, cy = 640, 600
        cv.ellipse(cx, cy, 190, 40, (120, 190, 110), ink=INK, lw=2.4)
        for q in range(12):
            a = q * math.pi / 6
            cv.ellipse(cx + math.cos(a) * 150, cy + math.sin(a) * 28, 8, 6, [(250, 130, 160), (255, 214, 110), (190, 140, 230)][q % 3], ink=INK, lw=1.2)
        for q in range(7):
            a = -math.pi + q * math.pi / 6
            cv.stroke([(cx, cy - 4), (cx + math.cos(a) * 80, cy - 4 + math.sin(a) * 30)], (255, 170, 80), 7)
        cv.ellipse(cx, cy - 6, 26, 12, (255, 214, 120), ink=INK, lw=2.0)
        st(cv, "silpa", 330, 700, pose=reach("silpa", 330, 700, 30, 1.05, {"R": (460, 570)}, kinds=("point", "relaxed")), ex="aha", th=30, k=1.05, mouth=mouth_of(t, B[7] + 0.5, B[8] - 0.8, 3))
        for j, w in enumerate(("chula", "thamma", "kaset", "kku", "cmu")):
            st(cv, w, 880 + j * 80, 705 + 8 * (j % 2), pose=REST, ex="deadpan", th=-30, flip=True, k=0.5, seed=j)
    elif k == 8:
        tidepool(cv, t)
        cx, cy = 640, 620
        cv.ellipse(cx, cy, 190, 40, (120, 190, 110), ink=INK, lw=2.4)
        for q in range(7):
            a = -math.pi + q * math.pi / 6
            cv.stroke([(cx, cy - 4), (cx + math.cos(a) * 80, cy - 4 + math.sin(a) * 30)], (255, 170, 80), 7)
        st(cv, "silpa", 330, 700, pose=reach("silpa", 330, 700, 30, 1.05, {"R": (420, 560)}, kinds=("relaxed", "relaxed")), ex="happy", th=30, k=1.05)
        hy = ease(fr(t, BE, 8, 0.5, 0.95))
        monkey(cv, 1000 - 360 * hy, 720, 1.1, "run", t, flip=True, hold=None)
        pass
    else:
        tidepool(cv, t)
        monkey(cv, 640, 640, 1.5, "sit", t, mouth=True, hold="fish")
        cv.ellipse(640, 640, 190, 36, (120, 190, 110), ink=INK, lw=2.4, alpha=210)
        st(cv, "silpa", 330, 700, pose=ARMS_UP, ex="shout", th=30, k=1.05, mouth=mouth_of(t, B[9], B[9] + 2.0, 4))
        say_waves(cv, 400, 470, t, B[9], B[9] + 2.0)
        for q in range(6):
            hermit_crab(cv, 120 + q * 190, 712 + 6 * (q % 2), 1.0, t, hide=ease(fr(t, BE, 9, 0.1 + 0.05 * q, 0.3 + 0.05 * q)))
        for j, w in enumerate(("chula", "thamma", "mahidol")):
            st(cv, w, 900 + j * 100, 705, pose=REST, ex="gape", th=-30, flip=True, k=0.55, seed=j)
    cv.pop()
    pulse_ov(ov, t)
