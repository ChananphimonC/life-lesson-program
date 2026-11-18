"""Red thread, scene 5 (v4): Pin messages Ta, he answers 'tell me if anything is wrong', they study together, the activity day (shopping, a pile of water packs, friends carry them, the two of them
eat dry noodles on the storeroom floor while packing, care turning into love), 'what does ปิ่น mean?' (a hairpin, not a tiffin carrier), a hairpin bought just because it will look pretty on her,
bubble tea Pin bought for herself that Ta steals, and the invisible thread shortens. Everybody walks towards +x."""
from rt_common import *  # noqa: F401,F403
import rt_art
import uni_chars

NAME, I = "rt5", 5
DUR = scene_dur(I)
CAPS = []
MARK = ["ร้องจนพอแล้ว", "ปิ่นหัวเราะทั้งน้ำตา", "จากวันนั้น ต้าก็ช่วยปลอบใจ", "พอถึงช่วงจัดกิจกรรมคณะ", "แล้วบ่นเสียงอ่อย", "แล้วก็วิ่งไปเรียกเพื่อน", "ขนของไปถึงห้องเก็บของ", "เลยนั่งกับพื้นกินก๋วยเตี๋ยวแห้ง",
        "ต้าเขี่ยผักชีออก", "แล้วทั้งคู่ก็แพคของกันต่อ", "จนวันหนึ่งต้าถามขึ้นมาว่า", "ปิ่นปักผมไงล่ะ", "ต้าทำหน้าเหวอ", "ปิ่นหัวเราะจนน้ำตาเล็ด", "วันรุ่งขึ้น ต้าเดินผ่านร้านขายปิ่น", "ปิ่นดีใจมาก",
        "ส่วนปิ่นก็ไปซื้อชานมไข่มุก", "ต้าเดินเข้ามาทำหน้าซื่อ", "ตรงนั้นเอง"]
B = beats(I, MARK)
BE = B + [DUR - TAIL]
CUES = [(B[0] + 4.0, "beep", 0.4), (B[0] + 9.0, "beep", 0.4), (B[1] + 2.0, "ding", 0.4), (B[3] + 3.0, "step", 0.3), (B[5] + 2.0, "whoosh", 0.4), (B[6] + 1.0, "thump", 0.4), (B[7] + 2.0, "clink", 0.5),
        (B[8] + 3.0, "ding", 0.5), (B[9] + 4.0, "chime", 0.5), (B[10] + 1.0, "pop", 0.4), (B[11] + 1.0, "ding", 0.5), (B[12] + 1.0, "boing", 0.5), (B[13] + 1.0, "laugh", 0.5), (B[14] + 3.0, "coin", 0.4),
        (B[15] + 2.0, "chime", 0.6), (B[17] + 4.0, "spit", 0.4), (B[17] + 6.0, "gasp", 0.5), (B[18] + 2.0, "chime", 0.6)]


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


def hand_tip(who, near_x=None):
    """Where one of `who`'s hands is on the screen (the hand nearest `near_x`), as recorded when the figure was drawn."""
    recs = rt_art.LAST.get(who) or []
    if not recs:
        return None
    r = min(recs, key=lambda q: abs(q["w"][0] - (near_x if near_x is not None else 0.0)))
    return r["tip"]


def draw(cv, t, ov):
    cv.push(0, 0, scale=1.0)
    tick(t)
    k = which(t, B)
    ph = walk_ph(t, 6.5)
    uni_chars.HAIRPIN.discard("bua")
    if k >= 16 or (k == 15 and in_(t, BE, 15, 0.45, 1.0)):
        uni_chars.HAIRPIN.add("bua")                    # from the gift on, the hairpin stays in Pin's hair
    try:
        _scene(cv, t, ov, k, ph)
    finally:
        uni_chars.HAIRPIN.discard("bua")
    cv.pop()
    pulse_ov(ov, t)


def _bags(cv, who, t, col):
    """A shopping bag hanging from the hand of `who`, swinging as they walk."""
    p = hand_tip(who, 1e6)
    if p:
        shop_bag(cv, p[0] + 4 * math.sin(t * 6), p[1] + 44, 0.62, col)


def _scene(cv, t, ov, k, ph):
    if k in (0, 1):
        # a chat across the night: Pin on the left, Ta on the right, the big phone between them; his answer pops up with a heart
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
    elif k == 2:
        # comforting her through the days: studying side by side
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
    elif k == 3:
        # shopping for the activity: a golden-hour lane, both walking (+x) with bags in their hands
        market_street(cv, t)
        w = ease(fr(t, BE, 3, 0.04, 0.96))
        wx = 90 + 760 * w
        st(cv, "phum", wx, 700, pose=walk_pose(ph), ex="happy", th=60, k=0.95, seed=1, walk=dict(phase=ph, stride=15, lift=11))
        st(cv, "bua", wx + 200, 700, pose=walk_pose(ph + 1), ex="happy", th=60, k=0.95, seed=2, walk=dict(phase=ph + 1, stride=15, lift=11))
        _bags(cv, "phum", t, (250, 214, 200))
        _bags(cv, "bua", t, (200, 224, 250))
        tie(cv, "phum", "bua", t, sag=40)
    elif k == 4:
        # a pile of water packs as tall as her head
        market_street(cv, t)
        water_pile(cv, 1000, 690, layers=4, s=1.0)
        st(cv, "phum", 520, 700, pose=REST, ex="gape", th=40, k=0.95, seed=1)
        st(cv, "bua", 720, 700, pose=REST, ex="plead", th=40, k=0.95, seed=2, mouth=mouth_of(t, BE[4] + 0.25 * (BE[5] - BE[4]), BE[5] - 0.4, 5))
        ov.append(("?", 720, 300, 100, (255, 255, 255), 0.7 + 0.3 * math.sin(t * 4)))
        tear(cv, 760, 410 + 4 * math.sin(t * 4), 0.8, alpha=210)
        tie(cv, "phum", "bua", t, sag=44)
    elif k == 5:
        # Ta runs off (+x) to fetch friends; Em, Bam and Orn walk in (+x), pick up the packs and carry them away
        market_street(cv, t)
        pile = 4 - int(3.99 * ease(fr(t, BE, 5, 0.6, 1.0)))
        water_pile(cv, 1000, 690, layers=max(1, pile), s=1.0)
        run = ease(fr(t, BE, 5, 0.0, 0.32))
        tx = 520 + 900 * run
        if tx < 1380:
            st(cv, "phum", tx, 700, pose=walk_pose(ph * 1.6), ex="shout", th=60, k=0.95, seed=1, walk=dict(phase=ph * 1.6, stride=22, lift=16), lean=6)
        st(cv, "bua", 720, 700, pose=REST, ex="happy" if run > 0.3 else "gape", th=40, k=0.95, seed=2)
        for i, who in enumerate(("em", "bam", "manao")):
            fx = -260 + 1330 * ease(fr(t, BE, 5, 0.2, 1.0)) - i * 230
            if -140 < fx < 1420:
                st(cv, who, fx, 700, pose=walk_pose(ph + i), ex="happy", th=60, k=0.95, seed=3 + i, walk=dict(phase=ph + i, stride=15, lift=11))
                if fx > 700:
                    waterpack(cv, fx + 54, 600, 0.6)
        if tx < 1380:
            tie(cv, "phum", "bua", t, sag=50)
        else:
            tie_out(cv, "bua", 1, t, sag=40)
    elif k == 6:
        # the storeroom: they start packing the supplies for the activity
        storeroom(cv, t, 0.0)
        FY = 730
        sw = math.sin(t * 3.2)
        pt = reach("phum", 470, FY, 25, 1.2, {"R": (430, 612), "L": (560 + 14 * sw, 610)}, kinds=("relaxed", "relaxed"), z=90)
        pb = reach("bua", 810, FY, 25, 1.2, {"L": (860, 612), "R": (720 - 14 * sw, 610)}, kinds=("relaxed", "relaxed"), z=90, flip=True)
        st(cv, "phum", 470, FY, pose=pt, ex="happy", th=25, k=1.2, seed=1, hide_arms=True)
        st(cv, "bua", 810, FY, pose=pb, ex="happy", th=25, flip=True, k=1.2, seed=2, hide_arms=True)
        rect(cv, 380, 628, 900, 664, (200, 156, 112), lw=2.8, shade_col=(170, 126, 90))
        carton(cv, 520, 628, 0.9)
        carton(cv, 700, 628, 0.8, col=(196, 150, 110))
        tape_roll(cv, 612, 616, 0.9)
        scissors(cv, 770, 620, 0.9, rot=-10)
        seated_front(cv, "phum", 470, FY, pt, th=25, k=1.2)
        seated_front(cv, "bua", 810, FY, pb, th=25, k=1.2, flip=True)
        tie(cv, "phum", "bua", t, sag=26)
    elif k in (7, 8):
        # sitting on the storeroom floor with a bowl of dry noodles each, boxes all around; in k8 Ta picks the coriander out of her bowl
        storeroom(cv, t, 0.15)
        FY = 868
        K = 1.22
        u = fr(t, BE, 8, 0.0, 1.0) if k == 8 else 0.0
        reach_p = ease(min(1.0, u / 0.3))
        away = ease(max(0.0, min(1.0, (u - 0.5) / 0.3)))
        back = ease(max(0.0, min(1.0, (u - 0.82) / 0.18)))
        hx = 560 + (730 - 560) * reach_p * (1 - away) + (650 - 560) * away * (1 - back) + (560 - 650) * back * away
        hy = 626 - 18 * reach_p * (1 - away) - 8 * away * (1 - back)
        eat = k == 7
        sw = math.sin(t * 2.6)
        tgt_t = (560 + 8 * sw, 622 - 14 * max(0.0, sw)) if eat else (hx, hy)
        pt = reach("phum", 470, FY, 25, K, {"L": tgt_t, "R": (440, 650)}, kinds=("relaxed", "relaxed"), z=90)
        pb = reach("bua", 830, FY, 25, K, {"L": (736, 622 - 12 * max(0.0, -sw)), "R": (880, 650)}, kinds=("relaxed", "relaxed"), z=90, flip=True)
        pin_ex = "happy" if (k == 7 or u < 0.35) else ("laugh" if u > 0.6 else "gape")
        st(cv, "phum", 470, FY, pose=pt, ex="happy", th=25, k=K, seed=1, hide_arms=True)
        st(cv, "bua", 830, FY, pose=pb, ex=pin_ex, th=25, flip=True, k=K, seed=2, hide_arms=True)
        # the low box they use as a table, with the two bowls on it
        rect(cv, 400, 650, 900, 720, (214, 170, 116), lw=2.8, shade_col=(176, 134, 92))
        rect(cv, 400, 650, 900, 664, (236, 200, 150), ink=None)
        noodle_bowl(cv, 560, 652, 0.95, t, leaf=True)
        noodle_bowl(cv, 740, 652, 0.95, t, leaf=(k == 7 or u < 0.45))
        cv.ellipse(650, 646, 26, 7, (252, 248, 240), ink=INK, lw=2.0)                  # the little saucer for the coriander
        if k == 8 and away > 0.05:
            sprig(cv, hx + 4, hy - 8, 0.9, rot=-10)
        seated_front(cv, "phum", 470, FY, pt, th=25, k=K)
        seated_front(cv, "bua", 830, FY, pb, th=25, k=K, flip=True)
        if k == 8:
            p = hand_tip("phum", 520)                                                   # chopsticks from Ta's hand to where he is picking
            if p:
                cv.stroke([(p[0] - 6, p[1] - 2), (hx + 6, hy - 8)], INK, 5)
                cv.stroke([(p[0] - 3, p[1] + 4), (hx + 10, hy - 4)], INK, 5)
                cv.stroke([(p[0] - 6, p[1] - 2), (hx + 6, hy - 8)], (214, 170, 116), 3)
                cv.stroke([(p[0] - 3, p[1] + 4), (hx + 10, hy - 4)], (214, 170, 116), 3)
            if u > 0.55:
                for j in range(5):
                    v = (t * 0.35 + j * 0.2) % 1.0
                    heart(cv, 790 + (j % 3) * 22, 520 - 140 * v, 11, PINK, alpha=int(230 * math.sin(math.pi * v)), lw=1.4)
        tie(cv, "phum", "bua", t, sag=24)
    elif k == 9:
        # packing on into the night: the window turns dark blue, fairy lights glow, tape and scissors are handed over without a word, little hearts rise
        night = ease(fr(t, BE, 9, 0.0, 0.45))
        storeroom(cv, t, night)
        FY = 730
        pas = 0.5 + 0.5 * math.sin(t * 1.6)
        pt = reach("phum", 470, FY, 25, 1.2, {"R": (430, 612), "L": (560 + 70 * pas, 608)}, kinds=("relaxed", "relaxed"), z=90)
        pb = reach("bua", 810, FY, 25, 1.2, {"L": (860, 612), "R": (740 - 70 * (1 - pas), 608)}, kinds=("relaxed", "relaxed"), z=90, flip=True)
        st(cv, "phum", 470, FY, pose=pt, ex="happy", th=25, k=1.2, seed=1, hide_arms=True, lean=-2)
        st(cv, "bua", 810, FY, pose=pb, ex="happy", th=25, flip=True, k=1.2, seed=2, hide_arms=True, lean=2)
        rect(cv, 380, 628, 900, 664, (200, 156, 112), lw=2.8, shade_col=(170, 126, 90))
        carton(cv, 520, 628, 0.9)
        carton(cv, 700, 628, 0.8, col=(196, 150, 110))
        tape_roll(cv, 600 + 70 * pas, 612, 0.9)
        scissors(cv, 770 - 60 * (1 - pas), 620, 0.9, rot=-10)
        seated_front(cv, "phum", 470, FY, pt, th=25, k=1.2)
        seated_front(cv, "bua", 810, FY, pb, th=25, k=1.2, flip=True)
        for j in range(7):
            v = (t * 0.28 + j * 0.143) % 1.0
            heart(cv, 600 + (j % 3) * 46 + 8 * math.sin(t * 2 + j), 500 - 260 * v, 13, PINK, alpha=int(230 * math.sin(math.pi * v)), lw=1.4)
        tie(cv, "phum", "bua", t, sag=22)
    elif k in (10, 11, 12, 13):
        # under the blossoms: 'what does your name mean?' - a hairpin! - 'I thought it was the tiffin carrier all along'
        sakura_tree(cv, t)
        ask = k == 10 and in_(t, BE, 10, 0.0, 0.7)
        ans = k == 11 and in_(t, BE, 11, 0.0, 0.7)
        oops = k == 12
        laugh = k == 13
        pin_pose = REST
        if ans:
            hp = head_pos("bua", 820, 700, 0.95, 0.0)
            pin_pose = reach("bua", 820, 700, 40, 0.95, {"L": (hp[0] - 70, hp[1] - 40)}, kinds=("relaxed", "point"), z=70, flip=True)
        st(cv, "phum", 540, 700, pose=REST, ex="gape" if oops else ("think" if k == 10 else ("pant" if laugh else "happy")), th=40, k=0.95, seed=1,
           mouth=mouth_of(t, BE[10], BE[10] + 0.7 * (BE[11] - BE[10]), 2) if ask else 0, lean=(5 * math.sin(t * 6) if laugh else 0))
        st(cv, "bua", 820, 700, pose=pin_pose, ex="laugh" if laugh else ("shout" if ans else ("gape" if k == 10 else "happy")), th=40, flip=True, k=0.95, seed=2,
           mouth=mouth_of(t, BE[11], BE[11] + 0.7 * (BE[12] - BE[11]), 5) if ans else 0, lean=(4 * math.sin(t * 7) if laugh else 0))
        if ask:
            say_waves(cv, 610, 470, t, BE[10], BE[10] + 0.7 * (BE[11] - BE[10]))
            ov.append(("?", 820, 330, 100, (255, 255, 255), 0.7 + 0.3 * math.sin(t * 5)))
        if ans:
            say_waves(cv, 760, 470, t, BE[11], BE[11] + 0.7 * (BE[12] - BE[11]), flip=True)
            a = ease(fr(t, BE, 11, 0.15, 0.4))
            cv.push(760, 260, scale=0.6 + 0.4 * a)
            icon_bubble(cv, 0, 0, 190, 170, tail=(50, 80), alpha=int(255 * a))
            hairpin(cv, 0, -50, 0.9, rot=18, shine=0.7 + 0.3 * math.sin(t * 5))
            cv.pop()
        if oops:
            a = ease(fr(t, BE, 12, 0.08, 0.35))
            cv.push(530, 215, scale=0.6 + 0.4 * a)
            icon_bubble(cv, 0, 0, 220, 230, tail=(0, 120), alpha=int(255 * a))
            tiffin(cv, 0, 88, 0.62)
            cv.pop()
        if laugh:
            for j in range(4):
                u = (t * 0.9 + j * 0.25) % 1.0
                tear(cv, 820 + (-24 if j % 2 == 0 else 26), 450 + 90 * u, 0.9, alpha=int(255 * (1 - u)))
        tie(cv, "phum", "bua", t, sag=50)
    elif k == 14:
        # the next day: Ta walks past a little stall of hairpins and thinks how pretty one would look on her
        stall(cv, t)
        petals(cv, t, 12)
        w = ease(fr(t, BE, 14, 0.0, 0.4))
        tx = 380 + 160 * w
        walking = 0.01 < w < 0.99
        pick = ease(fr(t, BE, 14, 0.5, 0.8))
        hold = reach("phum", tx, 700, 40, 0.95, {"R": (tx + 90, 520 - 40 * pick)}, kinds=("relaxed", "relaxed"), z=90) if not walking and w >= 0.99 else None
        st(cv, "phum", tx, 700, pose=walk_pose(ph) if walking else (hold or REST), ex="happy", th=60 if walking else 40, k=0.95, seed=1, walk=dict(phase=ph, stride=16, lift=12) if walking else None)
        if pick > 0.2:
            hairpin(cv, tx + 90, 460 - 40 * pick, 0.55, rot=14, shine=pick)
            a = ease(fr(t, BE, 14, 0.55, 0.8))
            cv.push(tx - 10, 250, scale=0.6 + 0.4 * a)
            icon_bubble(cv, 0, 0, 190, 150, tail=(30, 70), alpha=int(255 * a))
            hairpin(cv, -30, -40, 0.7, rot=18, shine=0.8 + 0.2 * math.sin(t * 6))
            heart(cv, 40, -8, 22, PINK, alpha=int(255 * a), lw=1.6)
            cv.pop()
        tie_out(cv, "phum", -1, t, sag=80)
    elif k == 15:
        # the gift under the cherry tree: she puts the hairpin in her hair
        sakura_tree(cv, t)
        give = ease(fr(t, BE, 15, 0.0, 0.35))
        put = ease(fr(t, BE, 15, 0.4, 0.7))
        ta_pose = reach("phum", 540, 700, 40, 0.95, {"R": (650, 540 - 30 * give)}, kinds=("relaxed", "relaxed"), z=90) if give > 0.3 and put < 0.5 else REST
        st(cv, "phum", 540, 700, pose=ta_pose, ex="happy", th=40, k=0.95, seed=1)
        st(cv, "bua", 820, 700, pose=REST, ex="laugh" if put > 0.5 else "gape", th=40, flip=True, k=0.95, seed=2)
        if put < 0.5:
            hairpin(cv, 658, 480 - 30 * give, 0.55, rot=14, shine=1.0)
        for j in range(8):
            a = j * math.pi / 4 + t * 0.8
            r = 70 * put + 10 * math.sin(t * 4 + j)
            cv.ellipse(840 + math.cos(a) * r, 400 + math.sin(a) * r * 0.9, 3.6, 3.6, (255, 236, 200), ink=None, alpha=int(230 * put))
        tie(cv, "phum", "bua", t, sag=46)
    elif k in (16, 17):
        # bubble tea she bought for herself, in the pretty tea pavilion; Ta walks up (+x), makes his innocent face and drinks half of it
        tea_garden(cv, t)
        if k == 16:
            sip = 0.5 + 0.5 * math.sin(t * 2.0)
            hp = head_pos("bua", 800, 700, 0.95, 0.0)
            pose_b = reach("bua", 800, 700, 40, 0.95, {"L": (hp[0] - 34, hp[1] + 60 - 8 * sip)}, kinds=("relaxed", "relaxed"), z=80, flip=True)
            st(cv, "bua", 800, 700, pose=pose_b, ex="happy", th=40, flip=True, k=0.95, seed=2)
            boba(cv, hp[0] - 32, hp[1] + 96 - 8 * sip, 1.0, level=1.0, straw_to=(hp[0] - 12, hp[1] + 52))
            tea_table(cv, 360, 940, 640)
            tie_out(cv, "bua", -1, t, sag=70)
        else:
            enter = ease(fr(t, BE, 17, 0.0, 0.3))
            walking = 0.01 < enter < 0.99
            tx = 120 + 350 * enter
            lean = ease(fr(t, BE, 17, 0.4, 0.55))
            sip = fr(t, BE, 17, 0.45, 0.85)
            shout = in_(t, BE, 17, 0.72, 1.0)
            tx2 = tx + 70 * lean
            st(cv, "phum", tx2, 700, pose=walk_pose(ph) if walking else REST, ex="happy", th=60 if walking else 40, k=0.95, seed=1, lean=14 * lean, walk=dict(phase=ph, stride=14, lift=10) if walking else None)
            hp = head_pos("bua", 800, 700, 0.95, 0.0)
            pose_b = reach("bua", 800, 700, 40, 0.95, {"L": (hp[0] - 34, hp[1] + 60)}, kinds=("relaxed", "relaxed"), z=80, flip=True)
            st(cv, "bua", 800, 700, pose=pose_b, ex="shout" if shout else ("gape" if sip > 0.3 else "happy"), th=40, flip=True, k=0.95, seed=2,
               mouth=mouth_of(t, BE[17] + 0.72 * (BE[18] - BE[17]), BE[18] - 0.3, 5) if shout else 0)
            hq = head_pos("phum", tx2, 700, 0.95, 0.0)
            mouth = (hq[0] + 30 + 22 * lean, hq[1] + 52)
            boba(cv, hp[0] - 32, hp[1] + 96, 1.0, level=max(0.0, 1.0 - 0.95 * sip), straw_to=(mouth[0], mouth[1] + 4) if lean > 0.5 else (hp[0] - 12, hp[1] + 52))
            tea_table(cv, 360, 940, 640)
            if shout:
                say_waves(cv, 740, 470, t, BE[17] + 0.72 * (BE[18] - BE[17]), BE[18] - 0.3, flip=True)
            tie(cv, "phum", "bua", t, sag=44)
    else:
        # the invisible thread winds in under the blossoms until it is one short step
        sakura_tree(cv, t)
        w = ease(fr(t, BE, 18, 0.0, 0.75))
        tx = 300 + 250 * w
        walking = 0.01 < w < 0.99
        st(cv, "phum", tx, 700, pose=walk_pose(ph) if walking else REST, ex="happy", th=60 if walking else 40, k=0.95, seed=1, walk=dict(phase=ph, stride=14, lift=10) if walking else None)
        st(cv, "bua", 820, 700, pose=REST, ex="happy", th=40, flip=True, k=0.95, seed=2)
        cv.ellipse((tx + 820) / 2, 560, 80 + 160 * (1 - w), 80, (255, 220, 230), ink=None, alpha=int(60 * (1 - w) + 20))
        tie(cv, "phum", "bua", t, sag=130 * (1 - w) + 22)
        for j in range(8):
            a = j * math.pi / 4 + t
            cv.ellipse((tx + 820) / 2 + math.cos(a) * 120, 480 + math.sin(a) * 60, 4, 4, (255, 236, 200), ink=None, alpha=int(200 * w))
