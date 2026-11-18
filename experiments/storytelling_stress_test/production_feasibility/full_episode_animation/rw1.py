"""Robot world v2, scene 1: Ton and Chok wake to the speaker, the driverless pod, Chok asks the car what to do, the car answers, they board; the 250,000 rides."""
from rw_common import *  # noqa: F401,F403

NAME, I = "rw1", 1
DUR = scene_dur(I)
CAPS = []
MARK = ["เช้านี้", "ลำโพงพูดว่า", "ข้างล่างมีรถ", "รถตอบเสียงใสว่า", "รถแบบนี้ไม่ใช่", "บริษัทเวย์โม", "ต้นกับลุงโชคเป็นตัวละคร"]
B = beats(I, MARK)
BE = B + [DUR - TAIL]
CUES = [(B[1] - 1.0, "chime", 0.7), (B[1] + 0.4, "beep", 0.4), (B[2] + 3.0, "hum", 0.5), (B[3] + 0.5, "bloop", 0.6), (B[3] + 1.2, "beep", 0.4),
        (BE[3] + (BE[4] - BE[3]) * 0.40, "dooropen", 0.6), (BE[3] + (BE[4] - BE[3]) * 0.62, "hum", 0.5), (B[4] + 0.2, "hum", 0.35), (B[5] + 0.5, "ding", 0.5),
        (B[5] + 3.2, "ding", 0.5)]


def draw(cv, t, ov):
    cv.push(0, 0, scale=1.0)
    tick(t)
    k = which(t, B)
    ph = walk_ph(t, 6.0)
    if k in (0, 1):
        room(cv, t)
        for (x, who, off) in ((520, "ton", 0.0), (780, "chok", 0.25)):
            if k == 0:
                u = fr(t, BE, 0, 0.55 + off * 0.5, 0.95)           # the speaker's ding wakes them near the end of the beat
                rise = (1 - ease(u)) * 70
                eyes = 1.0 if u < 0.3 else blink(t, 0.2 + off)
                pose = pl(REST, ARMS_UP, fr(t, BE, 0, 0.7 + off * 0.2, 1.0)) if who == "ton" else pl(REST, mk(((-50, 150, 40), (-20, 180, 70)), ((50, 150, 40), (20, 180, 70))), 0.5 + 0.5 * math.sin(t * 2))
                ex_ = "neutral" if u < 0.4 else "gape"
            else:
                rise = 0
                eyes = blink(t, 0.2 + off)
                pose = pl(REST, ARMS_UP if who == "chok" else POINT_FWD, fr(t, BE, 1, 0.15, 0.4))
                ex_ = "yikes" if who == "chok" else "eager"
            fn = ton if who == "ton" else chok
            fn(cv, x, 575 + rise, pose, ex_, k=1.15 if who == "ton" else 1.1, blink_v=eyes)
            rrect(cv, x - 105, 468, x + 105, 600, 16, (122, 168, 214) if who == "ton" else (176, 140, 200), lw=2.6)
            rrect(cv, x - 105, 468, x + 105, 490, 10, (250, 250, 252), lw=2.0)
        if k == 1:
            waves(cv, 1090, 100, fr(t, BE, 1, 0.0, 0.5) * 1.5, n=3, r0=18, dr=14, col=(255, 200, 90), a0=40, a1=140, lw=4)
            bubble(cv, 1010, 200, 210, 70, tail=(20, 36), col=(240, 250, 255), alpha=int(255 * ease(fr(t, BE, 1, 0.05, 0.12))))
            bars_in_bubble(cv, 1010, 200, t, n=8, amp=1.0 if fr(t, BE, 1, 0.05, 0.4) < 1 else 0.0)
            # the pod appears below the window
            a = ease(fr(t, BE, 1, 0.55, 0.8))
            if a > 0:
                pod(cv, 640, 360 + 10 * (1 - a), 0.42, 0.0, t)
    elif k == 2:
        street(cv, t)
        px = keys([(B[2], -480), (B[2] + 3.0, 660)], t)
        pod(cv, px, 690, 2.1, 0.0, t)
        moving = t < B[2] + 3.0
        ask = fr(t, BE, 2, 0.35, 0.85)
        chok(cv, 1010, 690, pl(REST, POINT_FWD, ease(fr(t, BE, 2, 0.3, 0.4))), "think" if ask <= 0 else "shout", flip=True, mouth=mouth_of(t, BE[2] + (BE[3] - BE[2]) * 0.4, BE[3] - 0.4, 1))
        ton(cv, 1160, 700, REST, "gape", flip=True)
        say_waves(cv, 960, 520, t, BE[2] + (BE[3] - BE[2]) * 0.4, BE[3] - 0.4, flip=True)
        if ask > 0:
            ov.append(("?", 1010, 300, 100, (255, 255, 255), ease(fr(t, BE, 2, 0.3, 0.38))))
    elif k == 3:
        street(cv, t)
        L = BE[4] - BE[3]
        reply = in_(t, BE, 3, 0.0, 0.22)
        cmd = in_(t, BE, 3, 0.26, 0.38)
        door = ease(fr(t, BE, 3, 0.40, 0.46)) * (1 - ease(fr(t, BE, 3, 0.66, 0.70)))
        walk_in = fr(t, BE, 3, 0.47, 0.56)
        boarded = fr(t, BE, 3, 0.56, 1.0) > 0.0
        leave = fr(t, BE, 3, 0.66, 0.92)
        px = 660 + 1300 * ease(leave)
        scroll = leave * 600
        if leave > 0:
            street(cv, t, scroll=scroll * 3)
        tx = 1010 - 380 * walk_in
        cx = 1130 - 470 * walk_in
        moving = 0 < walk_in < 1
        if not boarded:
            chok(cv, cx, 690, walk_pose(ph) if moving else REST, "determined", flip=True, walk=dict(phase=ph, stride=12, lift=9) if moving else None)
            ton(cv, tx, 690, (walk_pose(ph + 1) if moving else (POINT_UP if cmd else REST)), "eager", flip=True, mouth=mouth_of(t, BE[3] + L * 0.26, BE[3] + L * 0.38, 2),
                walk=dict(phase=ph + 1, stride=12, lift=9) if moving else None)
            say_waves(cv, tx - 28, 500, t, BE[3] + L * 0.26, BE[3] + L * 0.38, flip=True)
        pod(cv, px, 690, 2.1, door, t, window_people=[(-8, "ton"), (30, "chok")] if boarded else None)
        if reply:
            bubble(cv, px, 330, 230, 76, tail=(0, 40), col=(240, 250, 255))
            bars_in_bubble(cv, px, 330, t, n=9, col=(60, 140, 200))
        if boarded and fr(t, BE, 3, 0.6, 0.72) > 0 and fr(t, BE, 3, 0.6, 0.72) < 1:
            ov.append(("!", px - 200, 380, 90, (255, 255, 255), 1.0))
        if leave > 0 and leave < 1:
            puff(cv, px - 240, 680, 24, ((t * 3) % 1.0))
    elif k == 4:
        scroll = t * 120
        pod_inside(cv, t, scroll)
        ton(cv, 250, 810, REST, "gape", k=1.15, lean=1.5 * math.sin(t * 3), th=60)
        chok(cv, W - 250, 810, SHRUG, "think", k=1.1, flip=True, th=60)
        pod_benches(cv, t)
    elif k == 5:
        street(cv, t, scroll=t * 80, tod="day")
        cv.fill([(0, 0), (W, 0), (W, H), (0, H)], (24, 36, 70), ink=None, alpha=int(190 * ease(seg(t, B[5], B[5] + 0.8))))
        for c, (cx, label) in enumerate(((330, "us"), (950, "cn"))):
            a = ease(seg(t, B[5] + 0.6 + c * 3.4, B[5] + 1.6 + c * 3.4))
            if a <= 0:
                continue
            rrect(cv, cx - 270, 150, cx + 270, 560, 24, (246, 248, 252), lw=3.0, alpha=int(255 * a))
            for q in range(6):
                bx = cx - 200 + q * 70
                bh = 80 + ((q * 37 + c * 23) % 5) * 26 + 6 * math.sin(t * 2 + q)
                cv.fill([(bx, 330), (bx, 330 - bh), (bx + 56, 330 - bh), (bx + 56, 330)], (140 + c * 40, 170, 214 - c * 40), ink=INK, lw=1.8, alpha=int(255 * a))
            for q in range(6):
                pod(cv, cx - 200 + q * 80 + 10 * math.sin(t * 2 + q), 440, 0.28, 0.0, t + q)
            ov.append(("250,000", cx, 500, 64, (44, 62, 100), a))
    else:
        street(cv, t, scroll=t * 140, tod="day")
        for q in range(5):
            x = (q * 420 + t * (180 + 40 * q)) % (W + 500) - 250
            if q == 2:
                continue
            pod(cv, x, 640 + (q % 2) * 6, 1.25, 0.0, t + q, flip=(q % 2 == 1))
        pod(cv, 640, 700, 2.0, 0.0, t, window_people=[(-8, "ton"), (30, "chok")])
        qb = ease(seg(t, B[6] + 2.0, B[6] + 3.0))
        ov.append(("?", 640, 330, 110, (255, 255, 255), qb))
    pulse_ov(ov, t)
    cv.pop()
