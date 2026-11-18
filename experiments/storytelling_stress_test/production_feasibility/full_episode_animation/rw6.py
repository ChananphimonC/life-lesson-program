"""Robot world, scene 6: how Ton and Chok get by. Three proposals (ours, not research): fix and check the robots, learn to give clear orders and verify answers,
make things by hand. Evidence beats: Amazon's one million robots and its staffing claim, WEF's skill ranking, employers upskilling."""
from rw_common import *  # noqa: F401,F403

NAME, I = "rw6", 6
DUR = scene_dur(I)
CAPS = []
MARK = ["คืนนั้นสองคน", "หุ่นยนต์ยิ่งเยอะ", "ส่วนต้นฝึกสั่งงาน", "ซึ่งตรงกับที่นายจ้าง", "ตกเย็น", "ทั้งสามทางนี้", "แต่รายงานเดียวกัน"]
B = beats(I, MARK)
BE = B + [DUR - TAIL]
CUES = [(B[0] + 3.0, "tap", 0.6), (B[0] + 4.0, "tap", 0.6), (B[0] + 6.0, "servo", 0.5), (B[1] + 6.0, "ding", 0.5), (B[2] + 2.0, "bloop", 0.6), (B[2] + 3.5, "typing", 0.5),
        (B[2] + 7.0, "ding", 0.5), (B[3] + 2.0, "chime", 0.5), (B[4] + 3.0, "bamboo", 0.6), (B[4] + 9.0, "clink", 0.5), (B[5] + 1.5, "ding", 0.5), (B[6] + 2.0, "pop", 0.5)]


def draw(cv, t, ov):
    cv.push(0, 0, scale=1.0)
    tick(t)
    k = which(t, B)
    ph = walk_ph(t, 6.0)
    if k in (0,):
        workshop(cv, t)
        # a robot on the bench with its panel open; Chok with a wrench, Ton passing parts
        service_bot(cv, 880, 400, 1.6, t=t, mood="sorry" if t < B[0] + 7 else "happy")
        for j in range(3):
            cv.stroke([(870 + j * 14, 330 - 6 * j), (880 + j * 14 + 6 * math.sin(t * 20 + j), 310 - 12 * j)], (255, 220, 100), 3, alpha=int(200 * (1 if t < B[0] + 7 else 0))) if (int(t * 6) % 2 == 0) else None
        swing = math.sin(t * 6) * 0.5 + 0.5
        wpose = pl(mk(((-70, 150, 40), (-36, 150, 110))), mk(((-66, 130, 40), (-24, 112, 124))), swing)
        chok(cv, 700, 690, wpose, "determined", th=60, k=1.2, flip=False, blink_v=blink(t, .4))
        wp = wrist_pos("chok", 700, 690, 60, wpose, "R", 1.2)
        wrench(cv, wp[0] + 14, wp[1] - 4, 1.1, -30 + 30 * swing)
        ton(cv, 1090, 690, CARRY, "eager", th=40, k=1.15, flip=True, blink_v=blink(t, .1))
    elif k == 1:
        rect(cv, 0, 0, W, H, (34, 44, 82), ink=None)
        ambient(cv, t, 30, (130, 170, 240))
        n = int(80 * ease(seg(t, B[1] + 0.8, B[1] + 5.0)))
        for i in range(n):
            r, c = divmod(i, 16)
            x, y = 150 + c * 62, 120 + r * 70
            service_bot(cv, x, y + 40 + 3 * math.sin(t * 3 + i * 0.5), 0.42, t=t + i * 0.2, mood="happy", wave=0.5 + 0.5 * math.sin(t * 2 + i) if i % 7 == 0 else 0.0)
        ov.append(("1,000,000", 640, 600, 84, (255, 255, 255), ease(seg(t, B[1] + 3.5, B[1] + 4.5))))
        wrench(cv, 1080, 640, 1.6, -35) if t > B[1] + 6.0 else None
        ov.append(("+30%", 1180, 640, 54, (255, 214, 110), ease(seg(t, B[1] + 6.0, B[1] + 7.0))))
    elif k in (2, 3):
        # Ton at a desk giving a clear instruction, checking the answer with a lens
        rect(cv, 0, 0, W, 460, (232, 240, 248), ink=None)
        rect(cv, 0, 460, W, H, (206, 190, 164), ink=None)
        rect(cv, 300, 480, 980, 520, (160, 124, 92), lw=2.6)
        laptop(cv, 760, 480, 1.7, t)
        service_bot(cv, 1090, 560, 1.6, t=t, mood="happy" if t < B[2] + 6 else "think")
        sp = B[2] + 1.5 < t < B[2] + 3.4
        ton(cv, 480, 700, POINT_FWD if sp else (THINK if t > B[2] + 5 else REST), "determined", th=40, k=1.2, mouth=mouth_of(t, B[2] + 1.5, B[2] + 3.4, 2) if sp else 0, blink_v=blink(t, .1))
        say_waves(cv, 535, 520, t, B[2] + 1.5, B[2] + 3.4)
        # the answer: a checklist; Ton's lens passes down it; one red cross becomes a tick
        a = ease(seg(t, B[2] + 3.6, B[2] + 5.0))
        rrect(cv, 640, 120, 900, 400, 18, (250, 252, 255), lw=2.6, alpha=int(255 * a))
        for j in range(4):
            yy = 170 + j * 58
            cv.stroke([(700, yy), (860, yy)], (190, 196, 214), 6, alpha=int(255 * a))
            if t > B[2] + 5.4 + j * 0.8:
                if j == 2 and t < B[2] + 9.0:
                    cross_mark(cv, 670, yy, 0.8)
                else:
                    check_mark(cv, 670, yy, 0.8)
        lx = keys([(B[2] + 5.2, 560), (B[2] + 9.0, 760)], t)
        ly = keys([(B[2] + 5.2, 180), (B[2] + 9.0, 340)], t)
        if t > B[2] + 5.2:
            lens_icon(cv, lx, ly, 1.3)
        if k == 3:
            # the three skills the employers rank highest (as icons)
            cv.fill([(0, 0), (W, 0), (W, H), (0, H)], (34, 44, 82), ink=None, alpha=int(235 * ease(seg(t, B[3], B[3] + 0.8))))
            for j, x in enumerate((260, 640, 1020)):
                a2 = ease(seg(t, B[3] + 1.0 + j * 1.8, B[3] + 1.8 + j * 1.8))
                if a2 <= 0:
                    continue
                if j == 0:
                    lens_icon(cv, x - 10, 320, 1.6)
                elif j == 1:
                    cv.stroke(spline([(x - 70, 380), (x - 20, 270), (x + 30, 330), (x + 80, 250)], n=5), (120, 200, 255), 10)
                    arrow(cv, x + 80, 240, 50, True, (120, 200, 255), 18)
                else:
                    bulb(cv, x, 320, 2.2)
                ov.append((["#1", "top 5", "top 5"][j], x, 520, 52, (255, 220, 120), a2))
    elif k == 4:
        rect(cv, 0, 0, W, 460, (250, 240, 222), ink=None)
        rect(cv, 0, 460, W, H, (190, 150, 108), ink=None)
        # Chok bending bamboo for a kite; Ton serving tea to a customer; a robot watches
        kite(cv, 270, 250, 1.6, -0.3, (236, 100, 96), tail=True, t=t)
        swing = math.sin(t * 3) * 0.5 + 0.5
        chok(cv, 300, 700, pl(mk(((-70, 150, 40), (-40, 150, 100))), mk(((-70, 140, 40), (-34, 120, 110))), swing), "happy", th=50, k=1.15, blink_v=blink(t, .4))
        rect(cv, 760, 560, 1060, 580, (150, 116, 84), lw=2.4)
        for lx in (780, 1030):
            rect(cv, lx, 580, lx + 14, 700, (124, 94, 66), lw=2.0)
        teapot_cup(cv, 840, 560, 1.4, 1.0, t)
        teapot_cup(cv, 960, 560, 1.1, 1.0, t)
        ton(cv, 640, 700, CARRY, "happy", th=40, k=1.15, flip=False, blink_v=blink(t, .1))
        mini(cv, 1140, 680, 2.2, 4, arms="up" if int(t * 2) % 2 else "down", expr="grin")
        service_bot(cv, 1000, 450, 1.0, t=t, mood="think", wave=0.0) if False else service_bot(cv, 520, 470, 0.9, t=t, mood="think")
    elif k == 5:
        rect(cv, 0, 0, W, H, (34, 44, 82), ink=None)
        ambient(cv, t, 30, (130, 170, 240))
        a = ease(seg(t, B[5], B[5] + 1.0))
        dashed_rect(cv, 140, 120, 1140, 520, (255, 214, 110), 4.0, alpha=int(255 * a))
        wrench(cv, 330, 330 + 10 * math.sin(t * 2), 2.6, -35 + 10 * math.sin(t * 1.6))
        lens_icon(cv, 640 + 14 * math.sin(t * 1.4), 320 + 10 * math.sin(t * 2.2), 2.2)
        kite(cv, 960, 330 + 12 * math.sin(t * 1.8), 1.7, 0.2 + 0.18 * math.sin(t * 1.5), (236, 100, 96), tail=True, t=t)
        bulb(cv, 1140, 100, 1.2, on=1.0 if int(t * 2) % 2 else 0.0)
    else:
        rect(cv, 0, 0, W, H, (34, 44, 82), ink=None)
        ambient(cv, t, 30, (130, 170, 240))
        # four employers' staff: three of four start learning next to a robot
        for j in range(4):
            x = 230 + j * 270
            col = (96, 196, 132) if j < 3 else (150, 160, 180)
            u = ease(seg(t, B[6] + 1.0 + j * 0.8, B[6] + 1.8 + j * 0.8))
            by_ = 5 * math.sin(t * 2.4 + j)
            cv.ellipse(x, 300 + by_, 46, 46, col, ink=INK, lw=2.4)
            cv.fill(spline([(x - 62, 470), (x - 50, 360 + by_), (x + 50, 360 + by_), (x + 62, 470)], closed=True, n=3), col, ink=INK, lw=2.4)
            if j < 3 and u > 0:
                rrect(cv, x - 34, 400 - 20 * u, x + 34, 450 - 20 * u, 6, (250, 244, 228), lw=2.2)
                service_bot(cv, x + 90, 560, 0.7, t=t, mood="happy")
        ov.append(("3/4", 640, 120, 100, (255, 255, 255), ease(seg(t, B[6] + 3.0, B[6] + 4.0))))
    pulse_ov(ov, t)
    cv.pop()
