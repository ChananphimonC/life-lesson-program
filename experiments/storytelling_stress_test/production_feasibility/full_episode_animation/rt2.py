"""Red thread, scene 2 (v2): year one, the snack-passing game; Bam and Orn bring Pin to Ta's friends and Ta takes her for 'Mew' (again); everyone sighs 'Mew is at Khao Yai';
then the years in the same section, and Em: 'Ta, that is PIN, we are in year two!'"""
from rt_common import *  # noqa: F401,F403

NAME, I = "rt2", 2
DUR = scene_dur(I)
CAPS = []
MARK = ["ปีหนึ่ง ช่วงพักเที่ยง", "แบมกับอรถามต้าว่า", "ทุกคนถอนหายใจพร้อมกัน", "ปีแล้วปีเล่า", "เอมเพื่อนซี้ของต้า"]
B = beats(I, MARK)
BE = B + [DUR - TAIL]
CUES = [(B[0] + 3.0, "pop", 0.5), (B[0] + 6.0, "laugh", 0.4), (B[1] + 6.0, "ding", 0.4), (B[2] + 0.5, "sigh", 0.6), (B[3] + 2.0, "whoosh", 0.4), (B[4] + 3.0, "sigh", 0.4), (B[4] + 6.0, "ding", 0.5)]


def glasses_icon(cv, x, y, s=1.0):
    for dx in (-21, 21):
        cv.ellipse(x + dx * s, y, 17 * s, 15 * s, (255, 255, 255), ink=INK, lw=3.2, alpha=0)
    cv.stroke([(x - 4 * s, y - 2 * s), (x + 4 * s, y - 2 * s)], INK, 3.0)
    cv.stroke([(x - 38 * s, y - 4 * s), (x - 48 * s, y - 8 * s)], INK, 3.0)
    cv.stroke([(x + 38 * s, y - 4 * s), (x + 48 * s, y - 8 * s)], INK, 3.0)


def khaoyai_icon(cv, x, y, s=1.0):
    cv.fill([(x - 46 * s, y + 24 * s), (x - 14 * s, y - 24 * s), (x + 16 * s, y + 24 * s)], (110, 170, 120), ink=INK, lw=2.0)
    cv.fill([(x - 10 * s, y + 24 * s), (x + 22 * s, y - 14 * s), (x + 50 * s, y + 24 * s)], (140, 190, 130), ink=INK, lw=2.0)
    cv.ellipse(x + 36 * s, y - 30 * s, 8 * s, 8 * s, (255, 220, 110), ink=None)


def draw(cv, t, ov):
    cv.push(0, 0, scale=1.0)
    tick(t)
    k = which(t, B)
    ph = walk_ph(t, 6.0)
    if k in (0, 1, 2):
        courtyard(cv, t)
        u1 = fr(t, BE, 1, 0.0, 0.26) if k == 1 else (1.0 if k == 2 else 0.0)
        walking = k == 1 and u1 < 1.0
        dx = 90 * ease(u1)
        pos = {"bam": 240 + dx, "manao": 440 + dx, "bua": 660 + dx}
        W_ = dict(walk=dict(phase=ph, stride=12, lift=9)) if walking else {}
        th_ = 60 if walking else 0
        wp = walk_pose(ph) if walking else None
        # friends in the back left pass the snack along (the game); it ends in Pin's hands
        spk = {"bam": (BE[1] + (BE[1] - BE[0]) * 0.0, BE[1] + (BE[2] - BE[1]) * 0.26 + 0.0)}
        q = (BE[1] + (BE[2] - BE[1]) * 0.28, BE[1] + (BE[2] - BE[1]) * 0.52)
        who_say = k == 1 and BE[1] + (BE[2] - BE[1]) * 0.26 < t < BE[1] + (BE[2] - BE[1]) * 0.52
        ta_say = k == 1 and BE[1] + (BE[2] - BE[1]) * 0.52 < t < BE[1] + (BE[2] - BE[1]) * 0.76
        pin_say = k == 1 and BE[1] + (BE[2] - BE[1]) * 0.76 < t < BE[2] - 0.2
        sigh = k == 2
        st(cv, "bam", pos["bam"], 700, pose=wp or (POINT_FWD if who_say else REST), ex="laugh" if k == 0 else ("shout" if who_say else ("deadpan" if sigh else "happy")), th=th_ if walking else 30, k=0.95, seed=1,
           mouth=mouth_of(t, q[0], q[1], 1) if who_say else 0, **W_)
        st(cv, "manao", pos["manao"], 700, pose=wp or (POINT_FWD if who_say else REST), ex="happy" if k == 0 else ("shout" if who_say else ("deadpan" if sigh else "happy")), th=th_ if walking else 30, k=0.95, seed=2,
           mouth=mouth_of(t, q[0], q[1], 3) if who_say else 0, **W_)
        st(cv, "bua", pos["bua"], 700, pose=wp or REST, ex="happy" if k == 0 else ("plead" if (pin_say or sigh) else "neutral"), th=th_ if walking else 20, k=0.95, seed=3,
           mouth=mouth_of(t, BE[1] + (BE[2] - BE[1]) * 0.76, BE[2] - 0.2, 5) if pin_say else 0, **W_)
        if k == 0:
            # Ta and Em chat further right
            st(cv, "phum", 1000, 700, pose=REST, ex="happy", th=35, flip=True, k=0.95, seed=4)
            st(cv, "em", 1150, 700, pose=REST, ex="laugh", th=35, flip=True, k=0.95, seed=5)
            # the pouch flies along the line Bam -> Orn -> Pin (arcs over their heads)
            c = (t * 0.7) % 2.0
            i0 = int(c)
            f = c - i0
            xs = [pos["bam"], pos["manao"], pos["bua"]]
            x = xs[i0] + (xs[i0 + 1] - xs[i0]) * f
            y = 470 - 90 * math.sin(math.pi * f)
            snack(cv, x, y, 1.0, (240, 110, 90), rot=360 * f)
            snack(cv, pos["bua"] + 30, 560, 0.8, (250, 200, 80), rot=-8)
        else:
            st(cv, "phum", 1000, 700, pose=(POINT_FWD if ta_say else REST), ex="smug" if ta_say else ("deadpan" if sigh else "happy"), th=35, flip=True, k=0.95, seed=4,
               mouth=mouth_of(t, BE[1] + (BE[2] - BE[1]) * 0.52, BE[1] + (BE[2] - BE[1]) * 0.76, 2) if ta_say else 0)
            st(cv, "em", 1150, 700, pose=REST, ex="deadpan" if sigh else "happy", th=35, flip=True, k=0.95, seed=5)
            if who_say:
                say_waves(cv, 760, 470, t, q[0], q[1])
            if ta_say:
                bubble(cv, 900, 340, 190, 110, tail=(30, 60), alpha=255)
                glasses_icon(cv, 900, 340, 1.2)
                ov.append(("?", 1010, 300, 70, (80, 90, 120), 0.9))
            if k == 2:
                bubble(cv, 640, 300, 250, 120, tail=(0, 70))
                khaoyai_icon(cv, 575, 306, 1.3)
                glasses_icon(cv, 715, 312, 0.9)
            if sigh:
                for who, px in (("bam", 330), ("manao", 530), ("bua", 750), ("phum", 1000), ("em", 1150)):
                    sigh_puff(cv, who, px, 700, t, 0.95, seed=px * 0.001, side=1 if px < 900 else -1)
        tie(cv, "bua", "phum", t, sag=60)
    else:
        lecture(cv, t)
        desks(cv, 470, laptops=False, t=t)
        em_say = k == 4 and in_(t, BE, 4, 0.05, 0.55)
        tp = seated(cv, "phum", 560, SY := 730, 0.82, th=35, ex="gape" if (k == 4 and in_(t, BE, 4, 0.55, 0.8)) else ("think" if k == 4 else "neutral"), seed=1)
        pp = seated(cv, "bua", 830, 730, 0.82, th=35, flip=True, ex="happy", seed=2)
        ep = seated(cv, "em", 290, 730, 0.82, th=35, ex="shout" if em_say else "neutral", seed=3, lean=(10 * math.sin(t * 3) if em_say else 0),
                    mouth=mouth_of(t, BE[4], BE[4] + (BE[5] - BE[4]) * 0.55, 4) if k == 4 else 0)
        desks(cv, 610, t=t)
        seated_front(cv, "phum", 560, 730, tp, th=35, k=0.82)
        seated_front(cv, "bua", 830, 730, pp, th=35, k=0.82, flip=True)
        seated_front(cv, "em", 290, 730, ep, th=35, k=0.82)
        tie(cv, "phum", "bua", t, sag=-44)
        if k == 3:
            # the years go by: a wall calendar flips fast and the light in the windows changes
            u = (t * 2.0) % 1.0
            rect(cv, 1010, 190, 1110, 300, (252, 252, 254), lw=2.8)
            rect(cv, 1010, 190, 1110, 214, (230, 90, 90), lw=2.0)
            ov.append((str(1 + int(t * 2.0) % 30), 1060, 262, 52, (40, 40, 60), 1.0))
            cv.push(1060 + 16 * math.sin(u * 7), 250 + 110 * u, rot=36 * math.sin(u * 6))
            rect(cv, -48, -50, 48, 50, (252, 252, 254), lw=1.8)
            cv.pop()
        if k == 4:
            if em_say:
                say_waves(cv, 380, 480, t, BE[4], BE[4] + (BE[5] - BE[4]) * 0.55)
            if in_(t, BE, 4, 0.55, 0.85):
                ov.append(("?", 540, 380, 100, (255, 255, 255), 0.6 + 0.4 * math.sin(t * 5)))
            if in_(t, BE, 4, 0.82, 1.0):
                ov.append(("!", 695, 470, 80, (255, 120, 120), 0.5 + 0.5 * math.sin(t * 7)))
                cv.ellipse(695, 612, 130, 44, (255, 150, 160), ink=None, alpha=int(80 + 50 * math.sin(t * 8)))
    cv.pop()
    pulse_ov(ov, t)
