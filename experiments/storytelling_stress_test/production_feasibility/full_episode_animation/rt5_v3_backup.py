"""Red thread, scene 5 (v3): Pin messages Ta to clear the air, Ta brings a slice of bread and learns her name, comforts her through the years, then asks what "ปิ่น" means
(a hairpin, not a tiffin carrier: ปิ่นโต!), buys her a hairpin, Pin buys bubble tea and Ta steals half of it, and the invisible thread shortens."""
from rt_common import *  # noqa: F401,F403
import uni_chars

NAME, I = "rt5", 5
DUR = scene_dur(I)
CAPS = []
MARK = ["ร้องจนพอแล้ว", "ปิ่นหัวเราะทั้งน้ำตา", "จากวันนั้น ต้าก็ช่วยปลอบใจ", "พอถึงช่วงจัดกิจกรรมคณะ", "แล้วบ่นเสียงอ่อย", "แล้วก็วิ่งไปเรียกเพื่อน", "ขนของไปถึงห้องเก็บของ", "เลยนั่งกับพื้นกินก๋วยเตี๋ยวแห้ง",
        "ต้าเขี่ยผักชีออก", "แล้วทั้งคู่ก็แพคของกันต่อ", "จนวันหนึ่งต้าถามขึ้นมาว่า", "ปิ่นปักผมไงล่ะ", "ต้าทำหน้าเหวอ", "ปิ่นหัวเราะจนน้ำตาเล็ด", "วันรุ่งขึ้น ต้าเดินผ่านร้านขายปิ่น", "ปิ่นดีใจมาก",
        "ส่วนปิ่นก็ไปซื้อชานมไข่มุก", "ต้าเดินเข้ามาทำหน้าซื่อ", "ตรงนั้นเอง"]
B = beats(I, MARK)
BE = B + [DUR - TAIL]
CUES = [(B[0] + 4.0, "beep", 0.4), (B[0] + 9.0, "beep", 0.4), (B[1] + 2.0, "ding", 0.4), (B[2] + 3.0, "step", 0.4), (B[3] + 4.0, "chime", 0.6), (B[3] + 6.0, "laugh", 0.5), (B[4] + 3.0, "clink", 0.4),
        (B[5] + 1.0, "pop", 0.4), (B[6] + 1.0, "ding", 0.5), (B[7] + 1.0, "boing", 0.5), (B[8] + 1.0, "laugh", 0.5), (B[9] + 3.0, "coin", 0.4), (B[10] + 2.0, "chime", 0.6), (B[11] + 4.0, "spit", 0.4),
        (B[11] + 6.0, "gasp", 0.5), (B[12] + 2.0, "chime", 0.6)]


def bread(cv, x, y, s=1.0):
    cv.fill(spline([(x - 22 * s, y + 18 * s), (x - 24 * s, y - 6 * s), (x - 12 * s, y - 20 * s), (x + 12 * s, y - 20 * s), (x + 24 * s, y - 6 * s), (x + 22 * s, y + 18 * s)], closed=True, n=3),
            (244, 214, 150), ink=INK, lw=2.4, shade_col=(214, 174, 106), depth=4)
    cv.fill(spline([(x - 16 * s, y + 12 * s), (x - 17 * s, y - 4 * s), (x - 8 * s, y - 13 * s), (x + 8 * s, y - 13 * s), (x + 17 * s, y - 4 * s), (x + 16 * s, y + 12 * s)], closed=True, n=3), (252, 236, 196), ink=None)


def boba(cv, x, y, s=1.0, level=1.0, straw_to=None):
    """A bubble-tea cup; level 1..0 = how full; straw_to = where the straw's top points (e.g. to somebody's mouth)."""
    top = y - 30 * s + (1 - level) * 52 * s
    cv.fill([(x - 18 * s, y - 30 * s), (x + 18 * s, y - 30 * s), (x + 13 * s, y + 30 * s), (x - 13 * s, y + 30 * s)], (250, 244, 238), ink=INK, lw=2.4)
    if level > 0.02:
        w_top = 18 * s - (5 * s) * ((top - (y - 30 * s)) / (60 * s))
        cv.fill([(x - w_top, top), (x + w_top, top), (x + 13 * s, y + 30 * s), (x - 13 * s, y + 30 * s)], (214, 170, 130), ink=None)
    for i in range(6):
        cv.ellipse(x - 8 * s + (i % 3) * 8 * s, y + 22 * s - (i // 3) * 8 * s, 3.4 * s, 3.4 * s, (60, 40, 36), ink=None)
    cv.fill([(x - 20 * s, y - 34 * s), (x + 20 * s, y - 34 * s), (x + 18 * s, y - 28 * s), (x - 18 * s, y - 28 * s)], (255, 255, 255), ink=INK, lw=2.0)
    end = straw_to or (x + 12 * s, y - 62 * s)
    cv.stroke([(x + 4 * s, y - 20 * s), end], INK, 6.5 * s)
    cv.stroke([(x + 4 * s, y - 20 * s), end], (240, 100, 130), 4.2 * s)


def book_stack(cv, x, y, s=1.0):
    for i, col in enumerate(((210, 90, 90), (90, 140, 210), (240, 190, 80))):
        rrect(cv, x - 34 * s, y - (i + 1) * 14 * s, x + 34 * s, y - i * 14 * s, 3, col, lw=2.0)


def icon_bubble(cv, x, y, w=170, h=150, tail=(0, 70), alpha=255):
    bubble(cv, x, y, w, h, tail=tail, alpha=alpha)


def draw(cv, t, ov):
    cv.push(0, 0, scale=1.0)
    tick(t)
    k = which(t, B)
    ph = walk_ph(t, 6.5)
    pin_pin = k >= 10                                  # from the gift on, the hairpin stays in Pin's hair
    if pin_pin:
        uni_chars.HAIRPIN.add("bua")
    try:
        _scene(cv, t, ov, k, ph)
    finally:
        uni_chars.HAIRPIN.discard("bua")
    cv.pop()
    pulse_ov(ov, t)


def _scene(cv, t, ov, k, ph):
    if k in (0, 1):
        # a chat across the night: Pin on the left, Ta on the right, the big phone between them
        dorm_night(cv, t)
        lau = k == 1
        st(cv, "bua", 250, 700, pose=REST, ex="laugh" if lau else "plead", th=35, k=0.95, seed=2)
        if lau:
            for j in range(3):
                u = (t * 0.9 + j * 0.33) % 1.0
                tear(cv, 250 + (-20 if j % 2 == 0 else 22), 450 + 70 * u, 0.8, alpha=int(255 * (1 - u)))
        st(cv, "phum", 1030, 700, pose=REST, ex="think" if k == 0 else "happy", th=35, flip=True, k=0.95, seed=1)
        local = t - B[0]
        msgs = [("L", 0.9, 1.0, 0), ("R", 0.7, 5.0, 0), ("L", 0.5, 8.0, 0), ("R", 0.9, (B[1] - B[0]) + 3.0, 1)]
        phone(cv, 640, 400, 1.0, msgs, local)
        tie(cv, "bua", "phum", t, sag=-120)
    elif k in (2, 3):
        # that night on the steps in front of the building: Ta walks up, stands beside her and says it seriously; the moment he says her name a heart blooms
        stairs_night(cv, t)
        arrive = ease(fr(t, BE, 2, 0.0, 0.55)) if k == 2 else 1.0
        tx = 60 + 430 * arrive
        walking = k == 2 and arrive < 0.99
        sp_b = k == 3 and in_(t, BE, 3, 0.05, 0.5)
        laugh = k == 3 and in_(t, BE, 3, 0.55, 1.0)
        st(cv, "phum", tx, 700, pose=walk_pose(ph) if walking else REST, ex="happy" if walking else ("eager" if sp_b else "think"), th=60 if walking else 40, k=0.95, seed=1,
           walk=dict(phase=ph, stride=16, lift=12) if walking else None,
           mouth=mouth_of(t, BE[3] + 0.05 * (BE[4] - BE[3]), BE[3] + 0.5 * (BE[4] - BE[3]), 2) if sp_b else 0)
        st(cv, "bua", 760, 700, pose=REST, ex="laugh" if laugh else ("plead" if k == 2 else "happy"), th=35, flip=True, k=0.95, seed=2)
        if sp_b:
            say_waves(cv, tx + 70, 470, t, BE[3] + 0.05 * (BE[4] - BE[3]), BE[3] + 0.5 * (BE[4] - BE[3]))
        if k == 3:
            bl = ease(fr(t, BE, 3, 0.25, 0.5))
            if bl > 0:
                heart(cv, 600, 270 + 8 * math.sin(t * 3), 64 * bl, PINK, glow=1.0, alpha=int(255 * bl))
                for j in range(8):
                    a = j * math.pi / 4 + t * 0.6
                    r = 100 * bl + 14 * math.sin(t * 4 + j)
                    cv.ellipse(600 + math.cos(a) * r, 270 + math.sin(a) * r * 0.8, 4, 4, (255, 236, 200), ink=None, alpha=int(220 * (1 - bl * 0.3)))
        tie(cv, "phum", "bua", t, sag=50)
    elif k == 4:
        # comforting her through the years: studying side by side
        library(cv, t)
        tp = desk_pose("phum", 520, 730, 30, 0.9, hy=582, spread=36)
        pp = desk_pose("bua", 780, 730, 30, 0.9, hy=582, spread=36)
        st(cv, "phum", 520, 730, pose=tp, ex="think", th=30, k=0.9, seed=1, lean=-2, hide_arms=True)
        st(cv, "bua", 780, 730, pose=pp, ex="happy", th=30, flip=True, k=0.9, seed=2, lean=2, hide_arms=True)
        rect(cv, 300, 590, 980, 620, (190, 146, 104), lw=2.8, shade_col=WOOD_SH)
        book_stack(cv, 650, 590, 1.1)
        rrect(cv, 440, 560, 560, 592, 3, (250, 244, 232), lw=2.0)
        rrect(cv, 720, 560, 850, 592, 3, (250, 244, 232), lw=2.0)
        seated_front(cv, "phum", 520, 730, tp, th=30, k=0.9)
        seated_front(cv, "bua", 780, 730, pp, th=30, k=0.9, flip=True)
        POS["phum"], POS["bua"] = (520, 730), (780, 730)
        tie(cv, "phum", "bua", t, sag=44)
    elif k in (5, 6, 7, 8):
        # "Pin, what does your name mean?" - a hairpin! - "I thought it was the tiffin carrier all along"
        lawn(cv, t, deco=False)
        ask = k == 5 and in_(t, BE, 5, 0.0, 0.7)
        ans = k == 6 and in_(t, BE, 6, 0.0, 0.7)
        oops = k == 7
        laugh = k == 8
        ta_pose = REST
        pin_pose = REST
        if ans:
            hp = head_pos("bua", 760, 700, 0.95, 0.0)
            pin_pose = reach("bua", 760, 700, 40, 0.95, {"L": (hp[0] - 70, hp[1] - 40)}, kinds=("relaxed", "point"), z=70, flip=True)
        st(cv, "phum", 480, 700, pose=ta_pose, ex="gape" if oops else ("think" if k == 5 else ("pant" if laugh else "happy")), th=40, k=0.95, seed=1,
           mouth=mouth_of(t, BE[5], BE[5] + 0.7 * (BE[6] - BE[5]), 2) if ask else 0, lean=(5 * math.sin(t * 6) if laugh else 0))
        st(cv, "bua", 760, 700, pose=pin_pose, ex="laugh" if laugh else ("shout" if ans else ("gape" if k == 5 else "happy")), th=40, flip=True, k=0.95, seed=2,
           mouth=mouth_of(t, BE[6], BE[6] + 0.7 * (BE[7] - BE[6]), 5) if ans else 0, lean=(4 * math.sin(t * 7) if laugh else 0))
        if ask:
            say_waves(cv, 550, 470, t, BE[5], BE[5] + 0.7 * (BE[6] - BE[5]))
            ov.append(("?", 760, 330, 100, (255, 255, 255), 0.7 + 0.3 * math.sin(t * 5)))
        if ans:
            say_waves(cv, 700, 470, t, BE[6], BE[6] + 0.7 * (BE[7] - BE[6]), flip=True)
            a = ease(fr(t, BE, 6, 0.15, 0.4))
            cv.push(700, 260, scale=0.6 + 0.4 * a)
            icon_bubble(cv, 0, 0, 190, 170, tail=(50, 80), alpha=int(255 * a))
            hairpin(cv, 0, -50, 0.9, rot=18, shine=0.7 + 0.3 * math.sin(t * 5))
            cv.pop()
        if oops:
            a = ease(fr(t, BE, 7, 0.08, 0.35))
            cv.push(470, 215, scale=0.6 + 0.4 * a)
            icon_bubble(cv, 0, 0, 220, 230, tail=(0, 120), alpha=int(255 * a))
            tiffin(cv, 0, 88, 0.62)
            cv.pop()
        if laugh:
            for j in range(4):
                u = (t * 0.9 + j * 0.25) % 1.0
                tear(cv, 760 + (-24 if j % 2 == 0 else 26), 450 + 90 * u, 0.9, alpha=int(255 * (1 - u)))
        tie(cv, "phum", "bua", t, sag=50)
    elif k == 9:
        # at a little stall: Ta picks the hairpin out for her
        stall(cv, t)
        w = ease(fr(t, BE, 9, 0.0, 0.4))
        tx = 380 + 160 * w
        walking = 0.01 < w < 0.99
        pick = ease(fr(t, BE, 9, 0.5, 0.8))
        hold = reach("phum", tx, 700, 40, 0.95, {"R": (tx + 90, 520 - 40 * pick)}, kinds=("relaxed", "relaxed"), z=90) if not walking and w >= 0.99 else None
        st(cv, "phum", tx, 700, pose=walk_pose(ph) if walking else (hold or REST), ex="happy", th=60 if walking else 40, k=0.95, seed=1, walk=dict(phase=ph, stride=16, lift=12) if walking else None)
        if pick > 0.2:
            hairpin(cv, tx + 90, 460 - 40 * pick, 0.55, rot=14, shine=pick)
        if pick > 0.6:
            for j in range(5):
                u = (t * 0.4 + j * 0.2) % 1.0
                heart(cv, tx + 20 + j * 24, 330 - 90 * u, 11, PINK, alpha=int(230 * math.sin(math.pi * u)), lw=1.4)
        tie_out(cv, "phum", -1, t, sag=80)
    elif k == 10:
        # the gift: Pin puts the hairpin in her hair
        lawn(cv, t, deco=False)
        give = ease(fr(t, BE, 10, 0.0, 0.35))
        put = ease(fr(t, BE, 10, 0.4, 0.7))
        ta_pose = reach("phum", 480, 700, 40, 0.95, {"R": (590, 540 - 30 * give)}, kinds=("relaxed", "relaxed"), z=90) if give > 0.3 and put < 0.5 else REST
        st(cv, "phum", 480, 700, pose=ta_pose, ex="happy", th=40, k=0.95, seed=1)
        st(cv, "bua", 760, 700, pose=REST, ex="laugh" if put > 0.5 else "gape", th=40, flip=True, k=0.95, seed=2)
        if put < 0.5:
            hairpin(cv, 598, 480 - 30 * give, 0.55, rot=14, shine=1.0)
        for j in range(8):
            a = j * math.pi / 4 + t * 0.8
            r = 70 * put + 10 * math.sin(t * 4 + j)
            cv.ellipse(780 + math.cos(a) * r, 400 + math.sin(a) * r * 0.9, 3.6, 3.6, (255, 236, 200), ink=None, alpha=int(230 * put))
        tie(cv, "phum", "bua", t, sag=46)
    elif k == 11:
        # bubble tea: Pin treats him, he steals sip after sip
        cafe(cv, t)
        rect(cv, 380, 590, 900, 620, (170, 124, 88), lw=2.8, shade_col=(140, 100, 70))
        rect(cv, 400, 620, 420, 700, (140, 100, 70), lw=2.0)
        rect(cv, 860, 620, 880, 700, (140, 100, 70), lw=2.0)
        lean = ease(fr(t, BE, 11, 0.15, 0.4))
        sip = fr(t, BE, 11, 0.3, 0.8)
        shout = in_(t, BE, 11, 0.7, 1.0)
        st(cv, "phum", 480 + 70 * lean, 700, pose=REST, ex="happy", th=40, k=0.95, seed=1, lean=14 * lean)
        st(cv, "bua", 800, 700, pose=REST, ex="shout" if shout else "gape" if sip > 0.4 else "happy", th=40, flip=True, k=0.95, seed=2, mouth=mouth_of(t, BE[11] + 0.7 * (BE[12] - BE[11]), BE[12] - 0.3, 5) if shout else 0)
        hp = head_pos("phum", 480 + 70 * lean, 700, 0.95, 0.0)
        mouth = (hp[0] + 30 + 22 * lean, hp[1] + 52)
        boba(cv, 650, 560, 1.15, level=max(0.0, 1.0 - 0.95 * sip), straw_to=(mouth[0] - 14 * lean, mouth[1] + 4) if lean > 0.5 else None)
        rect(cv, 380, 590, 900, 620, (170, 124, 88), lw=2.8, shade_col=(140, 100, 70))
        if shout:
            say_waves(cv, 740, 470, t, BE[11] + 0.7 * (BE[12] - BE[11]), BE[12] - 0.3, flip=True)
        tie(cv, "phum", "bua", t, sag=44)
    else:
        # the invisible thread winds in: the two come closer until it is one short step
        lawn(cv, t, deco=False)
        w = ease(fr(t, BE, 12, 0.0, 0.75))
        tx = 260 + 250 * w
        walking = 0.01 < w < 0.99
        st(cv, "phum", tx, 700, pose=walk_pose(ph) if walking else REST, ex="happy", th=60 if walking else 40, k=0.95, seed=1, walk=dict(phase=ph, stride=14, lift=10) if walking else None)
        st(cv, "bua", 780, 700, pose=REST, ex="happy", th=40, flip=True, k=0.95, seed=2)
        cv.ellipse((tx + 780) / 2, 560, 80 + 160 * (1 - w), 80, (255, 220, 230), ink=None, alpha=int(60 * (1 - w) + 20))
        tie(cv, "phum", "bua", t, sag=130 * (1 - w) + 22)
        for j in range(8):
            a = j * math.pi / 4 + t
            cv.ellipse((tx + 780) / 2 + math.cos(a) * 120, 480 + math.sin(a) * 60, 4, 4, (255, 236, 200), ink=None, alpha=int(200 * w))
