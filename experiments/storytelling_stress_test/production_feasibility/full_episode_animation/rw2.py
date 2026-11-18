"""Robot world v2, scene 2: the order kiosk, the robot kitchen, the little robot that invites Chok to eat, the cashier-less supermarket, then the reality check
(the drive-thru voice-ordering test that was stopped; the 'Just Walk Out' reports, drawn as a dashed 'reported' cutaway)."""
from rw_common import *  # noqa: F401,F403

NAME, I = "rw2", 2
DUR = scene_dur(I)
CAPS = []
MARK = ["รถพามาถึงตลาด", "ต้นตะโกนใส่ตู้", "ในครัว", "แล้วหุ่นยนต์ตัวเล็ก", "กินเสร็จ", "แต่เวทมนตร์แบบนี้", "ส่วนระบบเดินออก"]
B = beats(I, MARK)
BE = B + [DUR - TAIL]
CUES = [(B[0] + 1.5, "dooropen", 0.5), (B[1] + 0.9, "bloop", 0.6), (B[1] + 2.4, "chime", 0.6), (B[2] + 0.4, "servo", 0.5), (B[2] + 1.8, "sizzle", 0.5),
        (B[3] + 0.8, "bloop", 0.5), (B[3] + 4.0, "clink", 0.5), (B[3] + 5.0, "clink", 0.5), (B[4] + 4.5, "beep", 0.5), (B[5] + 1.2, "bloop", 0.5),
        (B[5] + 2.2, "bloop", 0.5), (B[5] + 3.2, "buzz", 0.6), (B[6] + 1.0, "typing", 0.4)]


def draw(cv, t, ov):
    cv.push(0, 0, scale=1.0)
    tick(t)
    k = which(t, B)
    ph = walk_ph(t, 6.0)
    if k == 0:
        street(cv, t, tod="day")
        kiosk(cv, 930, 640, 1.5, t)
        px = keys([(0, -520), (3.0, 330)], t)
        pod(cv, px, 690, 1.6, ease(seg(t, 3.0, 3.8)), t)
        out = fr(t, BE, 0, 0.45, 0.8)
        if out > 0:
            cx_t = 330 + 560 * out
            gr = fr(t, BE, 0, 0.8, 1.0)
            ton(cv, 330 + 420 * out, 700, walk_pose(ph + 1) if out < 1 else POINT_FWD, "worried", walk=dict(phase=ph + 1, stride=12, lift=9) if out < 1 else None, k=1.1)
            chok(cv, 330 + 260 * out, 700, walk_pose(ph) if out < 1 else REST, "think", walk=dict(phase=ph, stride=12, lift=9) if out < 1 else None, k=1.05)
    elif k == 1:
        street(cv, t, tod="day")
        L = BE[2] - BE[1]
        ls = ease(fr(t, BE, 1, 0.35, 0.5)) * (1 - ease(fr(t, BE, 1, 0.7, 0.78)))
        ok = ease(fr(t, BE, 1, 0.74, 0.9))
        kiosk(cv, 930, 660, 1.5, t, listening=ls, ok=ok)
        belly = mk(((-50, 170, 40), (-14, 186, 74)), ((50, 170, 40), (14, 186, 74)))
        ton(cv, 640, 700, pl(belly, POINT_FWD, fr(t, BE, 1, 0.3, 0.45)), "eager" if ok < 0.5 else "happy", mouth=mouth_of(t, BE[1] + L * 0.38, BE[1] + L * 0.7, 3), k=1.15)
        say_waves(cv, 700, 480, t, BE[1] + L * 0.38, BE[1] + L * 0.7)
        chok(cv, 420, 700, REST, "think", k=1.05)
    elif k == 2:
        robot_kitchen(cv, t)
        arm_robot(cv, 640, 410, 1.5, t, (t - B[2]) * 3.0, tool="spatula")
        cv.ellipse(780, 392, 54, 12, (60, 66, 84), ink=INK, lw=2.4)
        for j in range(5):
            f = ((t - B[2]) * 0.8 + j * 0.2) % 1.0
            cv.ellipse(760 + j * 14, 380 - 80 * math.sin(math.pi * f), 8, 6, (236, 190, 120), ink=INK, lw=1.4)
        px = 900 + 260 * fr(t, BE, 2, 0.5, 1.0)
        plate(cv, px, 440, 1.5, steam=1.0, t=t)
        kiosk(cv, 1140, 600, 1.0, t, ok=1.0)
        service_bot(cv, 160, 560, 1.0, t=t, mood="happy")
        ton(cv, 1180, 710, REST, "gape", flip=True, k=1.0)
        chok(cv, 1050, 710, CROSS, "think", flip=True, k=0.95)
    elif k == 3:
        # the little robot rolls the plate to the table and invites Chok; they sit and eat together
        street(cv, t, tod="day")
        rect(cv, 420, 560, 900, 584, (176, 132, 96), lw=2.4)
        for lx in (450, 860):
            rect(cv, lx, 584, lx + 16, 690, (140, 104, 76), lw=2.0)
        rx = keys([(B[3], 120), (B[3] + (BE[4] - B[3]) * 0.3, 560)], t)
        arrived = t > B[3] + (BE[4] - B[3]) * 0.3
        eat = fr(t, BE, 3, 0.6, 1.0)
        bite = 0.5 + 0.5 * math.sin(t * 5)
        service_bot(cv, rx, 690, 1.35, t=t, mood="happy", wave=1.0 if arrived and eat < 0.2 else 0.0, carry="tray" if not arrived else None, ph=t * 6, moving=not arrived)
        plate(cv, 640, 560, 1.4, steam=1.0, t=t)
        chok(cv, 780, 700, pl(CROSS, EAT_A, ease(fr(t, BE, 3, 0.45, 0.6))) if t > B[3] + 2 else CROSS,
             "plead" if eat <= 0 else "happy", k=1.05, flip=True)
        ton(cv, 520, 700, pl(REST, pl(EAT_A, EAT_B, bite), ease(eat)), "happy" if eat > 0 else "eager", k=1.1)
    elif k == 4:
        supermarket(cv, t, gate_open=1.0 if fr(t, BE, 4, 0.7, 1.0) > 0.1 else 0.0)
        wk = fr(t, BE, 4, 0.05, 0.55)
        cx = 150 + 760 * wk
        moving = 0 < wk < 1
        pose = walk_pose(ph, carry=CARRY) if moving else CARRY
        chok(cv, cx, 700, pose, "think" if wk >= 1 else "happy", walk=dict(phase=ph, stride=12, lift=9) if moving else None, k=1.0)
        wp = wrist_pos("chok", cx, 700, 50, pose, "R", 1.0)
        rect(cv, wp[0] - 14, wp[1] - 24, wp[0] + 14, wp[1] + 2, (240, 180, 90), lw=1.8)
        ton(cv, 560, 700, REST, "eager", k=1.05)
        service_bot(cv, 760, 640, 0.9, t=t, mood="happy")
        rect(cv, 760, 530, 880, 548, (190, 196, 210), lw=2.0)
        rect(cv, 780, 548, 790, 600, (150, 156, 172), lw=1.6)
        if wk >= 1:
            ov.append(("?", cx, 420, 90, (255, 255, 255), ease(fr(t, BE, 4, 0.55, 0.62)) * (1 - ease(fr(t, BE, 4, 0.78, 0.86)))))
    elif k == 5:
        street(cv, t, tod="day")
        kiosk(cv, 980, 640, 1.5, t, listening=0.0, ok=0.0)
        pod(cv, 440, 690, 1.9, 0.0, t, window_people=[(0, "ton")])
        n = int(min(9, max(0, (t - B[5] - 1.0) * 1.6)))
        rrect(cv, 1180, 300, 1270, 480, 14, NAVY, lw=2.6)
        for j in range(n):
            cv.ellipse(1198 + (j % 3) * 28, 330 + (j // 3) * 42, 12, 10, (236, 190, 110), ink=INK, lw=1.4)
        if n >= 9:
            cross_mark(cv, 1225, 430, 1.2)
        service_bot(cv, 800, 640, 1.0, t=t, mood="sorry" if t > B[5] + 3.2 else "happy")
        say_waves(cv, 560, 520, t, B[5] + 0.8, B[5] + 2.0)
        if t > B[5] + 3.2:
            ov.append(("?", 700, 330, 90, (255, 255, 255), ease(seg(t, B[5] + 3.2, B[5] + 3.8))))
    else:
        supermarket(cv, t, gate_open=1.0)
        a = ease(seg(t, B[6] + 0.4, B[6] + 1.2))
        cv.fill([(430, 90), (1230, 90), (1230, 330), (430, 330)], (30, 40, 70), ink=None, alpha=int(235 * a))
        dashed_rect(cv, 430, 90, 1230, 330, (255, 214, 110), 3.4, alpha=int(255 * a))
        for r in range(2):
            for c in range(9):
                x, y = 500 + c * 80, 170 + r * 90
                if (r * 9 + c) / 18 > seg(t, B[6] + 1.0, B[6] + 4.0):
                    continue
                rect(cv, x - 22, y - 8, x + 22, y + 14, (70, 150, 200), ink=INK, lw=1.4)
                mini(cv, x, y + 40, 0.55, r * 9 + c, arms="swing", phase=t * 7 + c, squash=0.03 * math.sin(t * 2 + c), expr="grin")
        ov.append(("~1,000", 470, 120, 36, (255, 214, 110), a))
        wk = seg(t, B[6] + 2.0, B[6] + 10.0)
        chok(cv, 150 + 1250 * wk, 700, walk_pose(ph, carry=CARRY) if 0 < wk < 1 else CARRY, "think", walk=dict(phase=ph, stride=12, lift=9) if 0 < wk < 1 else None, k=1.0)
    pulse_ov(ov, t)
    cv.pop()
