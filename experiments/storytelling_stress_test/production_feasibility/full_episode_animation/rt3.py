"""Red thread, scene 3 (v2): AA's jealousy, Pin hides from Ta (restroom, library), Orn catches her ('twenty minutes to class!') and they run back, and Ta thinks she dislikes him.
Everybody walks and runs towards +x (forward), never backwards."""
from rt_common import *  # noqa: F401,F403

NAME, I = "rt3", 3
DUR = scene_dur(I)
CAPS = []
MARK = ["ส่วนปิ่นมีแฟนชื่อเอ", "วันไหนต้าเดินมาถามเรื่องงานกลุ่ม", "วันหนึ่งใกล้เข้าคาบเรียน", "อีกวันก็ไปแอบนั่งหลับ", "อรเพื่อนสนิทเดินมาเจอ", "อรร้อง", "ส่วนต้าก็เข้าใจว่า"]
B = beats(I, MARK)
BE = B + [DUR - TAIL]
CUES = [(B[1] + 2.0, "grunt", 0.4), (B[2] + 3.0, "step", 0.4), (B[2] + 6.0, "thump", 0.5), (B[3] + 2.0, "sigh", 0.4), (B[4] + 1.5, "step", 0.4), (B[5] + 1.0, "gasp", 0.5),
        (B[5] + 3.0, "step", 0.4), (B[6] + 3.0, "sigh", 0.5)]


def clock(cv, cx, cy, t, r=52):
    cv.ellipse(cx, cy, r, r, (252, 252, 254), ink=INK, lw=3.0)
    cv.stroke([(cx, cy), (cx + math.cos(t * 3) * r * 0.7, cy + math.sin(t * 3) * r * 0.7)], INK, 3)
    cv.stroke([(cx, cy), (cx, cy - r * 0.5)], INK, 4)


def draw(cv, t, ov):
    cv.push(0, 0, scale=1.0)
    tick(t)
    k = which(t, B)
    ph = walk_ph(t, 7.0)
    if k in (0, 1):
        corridor(cv, t)
        # AA stands over Pin with crossed arms. When Ta walks up to ask about the group project, AA glares and steams.
        u = fr(t, BE, 1, 0.0, 0.55) if k == 1 else 0.0
        tx = -120 + 580 * ease(u)
        walking = k == 1 and u < 1.0
        talk_a = k == 1 and in_(t, BE, 1, 0.55, 0.9)
        glare = ease(fr(t, BE, 1, 0.6, 0.85)) if k == 1 else 0.0
        st(cv, "bua", 640, 700, pose=REST, ex="worried" if glare > 0.2 else "neutral", th=-25, flip=True, k=0.95, seed=2)
        st(cv, "kong", 860, 700, pose=CROSS, ex="shout" if glare > 0.4 else ("deadpan" if k == 1 else "smug"), th=-25, flip=True, k=0.98, seed=4)
        if k == 1:
            st(cv, "phum", tx, 700, pose=walk_pose(ph) if walking else (POINT_FWD if talk_a else REST), ex="happy" if walking else "eager", th=60 if walking else 40, k=0.95,
               walk=dict(phase=ph, stride=16, lift=12) if walking else None,
               mouth=mouth_of(t, BE[1] + 0.55 * (BE[2] - BE[1]), BE[1] + 0.9 * (BE[2] - BE[1]), 2) if talk_a else 0)
            if talk_a:
                say_waves(cv, tx + 70, 470, t, BE[1] + 0.55 * (BE[2] - BE[1]), BE[1] + 0.9 * (BE[2] - BE[1]))
            if glare > 0.2:
                ov.append(("!", 860, 230, 100, (255, 110, 100), glare))
            tie(cv, "bua", "phum", t, sag=70)
        else:
            tie_out(cv, "bua", -1, t, sag=90)
    elif k == 2:
        corridor(cv, t)
        # Ta far down the hall; Pin spots him, spins round and runs (+x) for the restroom door
        run = fr(t, BE, 2, 0.30, 0.72)
        bx = 300 + 640 * ease(run)
        door = ease(fr(t, BE, 2, 0.70, 0.78)) * (1 - ease(fr(t, BE, 2, 0.86, 0.95)))
        enter = ease(fr(t, BE, 2, 0.72, 0.84))
        ph2 = walk_ph(t, 5.0)
        tx = 60 + 360 * fr(t, BE, 2, 0.0, 1.0)
        st(cv, "phum", tx, 610, pose=walk_pose(ph2), ex="happy", th=60, k=0.6, walk=dict(phase=ph2, stride=8, lift=6))
        if door > 0.02:
            rect(cv, 940, 150, 1080, 440, (120, 86, 60), lw=2.0, shade_col=WOOD_SH)
        if enter < 0.98:
            if run <= 0:
                st(cv, "bua", 300, 700, pose=REST, ex="yikes", th=40, k=0.95, seed=2)
            else:
                st(cv, "bua", bx, 700, pose=walk_pose(ph), ex="yikes", th=60, k=0.95, walk=dict(phase=ph, stride=20, lift=14), lean=8)
        ov.append(("!", 300, 330, 90, (255, 255, 255), ease(fr(t, BE, 2, 0.22, 0.32)) * (1 - ease(fr(t, BE, 2, 0.42, 0.52)))))
        tie(cv, "bua", "phum", t, sag=36)
    elif k == 3:
        library(cv, t)
        # Pin hides asleep on her arms over a book, the clock ticking
        pose = desk_pose("bua", 640, 730, 20, 0.9, hy=548, spread=40)
        st(cv, "bua", 640, 730, pose=pose, ex="neutral", th=20, k=0.9, blink_v=1.0, lean=10 + 2 * math.sin(t * 2), hide_arms=True)
        rect(cv, 400, 560, 880, 590, (190, 146, 104), lw=2.8, shade_col=WOOD_SH)
        rrect(cv, 560, 520, 720, 566, 4, (230, 90, 80), lw=2.4)
        seated_front(cv, "bua", 640, 730, pose, th=20, k=0.9)
        for j in range(3):
            ov.append(("z", 740 + j * 36, 430 - j * 46 - 10 * math.sin(t * 2 + j), 44 + j * 14, (255, 255, 255), 0.5 + 0.5 * math.sin(t * 2 + j)))
        clock(cv, 1100, 160, t)
        POS["bua"] = (640, 730)
        tie_out(cv, "bua", -1, t, sag=80)
    elif k in (4, 5):
        library(cv, t)
        # Orn walks in from the left (forward, +x), finds Pin, shouts the time; then both run off to +x towards the classroom
        arrive = ease(fr(t, BE, 4, 0.0, 0.6)) if k == 4 else 1.0
        run = fr(t, BE, 5, 0.55, 1.0) if k == 5 else 0.0
        ox = -100 + 600 * arrive + 900 * ease(run)
        px = 640 + 760 * ease(fr(t, BE, 5, 0.62, 1.0)) if k == 5 else 640
        sp = k == 5 and in_(t, BE, 5, 0.0, 0.5)
        wake = k == 5 and run > 0
        walk_o = (k == 4 and arrive < 0.99) or run > 0
        pose_o = walk_pose(ph) if walk_o else (POINT_FWD if sp else REST)
        if k == 4 and arrive >= 0.99:
            pose_o = REST
        st(cv, "manao", ox, 700, pose=pose_o, ex="shout" if sp else "worried", th=60 if walk_o else 35, k=0.92,
           walk=dict(phase=ph, stride=18, lift=14) if walk_o else None, mouth=mouth_of(t, BE[5], BE[5] + 0.5 * (BE[6] - BE[5]), 6) if sp else 0)
        st(cv, "bua", px, 700, pose=walk_pose(ph + 1) if run > 0.08 else REST, ex="gape" if wake else ("plead" if k == 5 else "neutral"), th=60 if run > 0.08 else -30, flip=run <= 0.08, k=0.92, seed=2,
           walk=dict(phase=ph + 1, stride=18, lift=14) if run > 0.08 else None, mouth=mouth_of(t, BE[4] + 0.6 * (BE[5] - BE[4]), BE[5] - 0.2, 5) if k == 4 else 0)
        clock(cv, 1100, 160, t)
        if k == 5:
            ov.append(("20", 1100, 250, 58, (255, 240, 120), ease(fr(t, BE, 5, 0.12, 0.25))))
            if sp:
                say_waves(cv, ox + 70, 470, t, BE[5], BE[5] + 0.5 * (BE[6] - BE[5]))
        if k == 4 and in_(t, BE, 4, 0.6, 1.0):
            say_waves(cv, px + 80, 470, t, BE[4] + 0.6 * (BE[5] - BE[4]), BE[5] - 0.2)
        tie_out(cv, "bua", 1 if k == 5 and run > 0.2 else -1, t, sag=70 if run <= 0.2 else 20)
    else:
        lecture(cv, t)
        desks(cv, 470, laptops=False, t=t)
        tp = seated(cv, "phum", 470, 730, 0.82, th=35, ex="deadpan", lean=-3, seed=1)
        pp = seated(cv, "bua", 740, 730, 0.82, th=35, flip=True, ex="neutral", blink_v=1.0, lean=10, seed=2)
        desks(cv, 610, t=t)
        seated_front(cv, "phum", 470, 730, tp, th=35, k=0.82)
        seated_front(cv, "bua", 740, 730, pp, th=35, k=0.82, flip=True, lean=10)
        ov.append(("z", 800, 430, 52, (255, 255, 255), 0.6 + 0.4 * math.sin(t * 2)))
        if in_(t, BE, 6, 0.35, 0.95):
            sigh_puff(cv, "phum", 470, 730, t, 0.82, side=1)
        ov.append(("?", 430, 380, 90, (255, 255, 255), ease(fr(t, BE, 6, 0.4, 0.55)) * (1 - ease(fr(t, BE, 6, 0.8, 0.95)))))
        tie(cv, "phum", "bua", t, sag=-44)
    cv.pop()
    pulse_ov(ov, t)
