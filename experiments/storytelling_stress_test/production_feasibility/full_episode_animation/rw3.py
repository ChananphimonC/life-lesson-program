"""Robot world v2, scene 3: Chok's phone call that never reaches a person (the coins run out), the all-AI call centre, Gartner's forecast (a prediction),
and Klarna's U-turn."""
from rw_common import *  # noqa: F401,F403

NAME, I = "rw3", 3
DUR = scene_dur(I)
CAPS = []
MARK = ["กลับถึงบ้าน", "ลุงอธิบายรอบแรก", "ศูนย์รับสายที่มีแต่", "การ์ทเนอร์", "แต่นั่นคือคำทำนาย", "คลาร์นา", "แต่พอสองพันห้าร้อยหกสิบแปด"]
B = beats(I, MARK)
BE = B + [DUR - TAIL]
CUES = [(B[0] + 2.0, "ding", 0.5), (B[0] + 5.0, "beep", 0.5)] + [(BE[1] + (BE[2] - BE[1]) * f, "beep", 0.45) for f in (0.12, 0.40, 0.68)] \
       + [(BE[1] + (BE[2] - BE[1]) * f, "coin", 0.4) for f in (0.2, 0.3, 0.5, 0.6, 0.8)] + [(BE[1] + (BE[2] - BE[1]) * 0.9, "buzz", 0.5)] \
       + [(B[2] + 0.5, "typing", 0.4), (B[3] + 1.0, "chime", 0.6), (B[3] + 5.0, "bloop", 0.4), (B[5] + 2.0, "swoosh_up", 0.4), (B[6] + 1.5, "ding", 0.5), (B[6] + 4.0, "pop", 0.5)]


def draw(cv, t, ov):
    cv.push(0, 0, scale=1.0)
    tick(t)
    k = which(t, B)
    if k in (0, 1):
        room(cv, t, tod="day")
        rrect(cv, 300, 470, 720, 640, 26, (206, 120, 110), lw=2.8, shade_col=(178, 96, 90))
        rrect(cv, 300, 430, 720, 500, 22, (222, 140, 128), lw=2.4)
        # the bill on the wall table, a big red up arrow
        rect(cv, 900, 380, 1020, 470, (252, 250, 244), lw=2.4)
        for j in range(3):
            cv.stroke([(912, 396 + j * 14), (1000, 396 + j * 14)], (190, 190, 200), 3)
        arrow(cv, 960, 440, 38, up=True, col=(236, 96, 88), w=12)
        calling = fr(t, BE, 0, 0.45, 1.0) > 0 or k == 1
        tries = [(0.05, 0.28), (0.36, 0.58), (0.66, 0.86)]
        speak = k == 1 and any(in_(t, BE, 1, a, b) for a, b in tries)
        pose = pl(REST, mk(((-60, 120, 30), (-30, 40, 40))), fr(t, BE, 0, 0.35, 0.5)) if calling else REST
        chok(cv, 540, 560, pose, "worried" if calling else "yikes", th=30, k=1.1, mouth=0.7 * abs(math.sin(t * 10)) if speak else 0)
        ton(cv, 880, 600, REST, "eager" if k == 0 else "worried", k=1.05, flip=True)
        if k == 0:
            phone(cv, 420, 430, 1.0, 1.0 if not calling else 0.0, t, -20)
            if calling:
                bubble(cv, 700, 250, 220, 80, tail=(-100, 70), col=(236, 244, 250), alpha=int(255 * ease(fr(t, BE, 0, 0.6, 0.7))))
                bars_in_bubble(cv, 700, 250, t, n=8, amp=ease(fr(t, BE, 0, 0.65, 0.75)))
        else:
            phone(cv, 420, 430, 1.0, 0.0, t, -20)
            n_try = 1 + sum(1 for a, b in tries if in_(t, BE, 1, a, 2) or False and 0)
            n_try = sum(1 for a, b in tries if fr(t, BE, 1, a, a + 0.01) > 0)
            # the machine answers the same thing every time (identical bars)
            bubble(cv, 700, 250, 220, 80, tail=(-100, 70), col=(236, 244, 250))
            bars_in_bubble(cv, 700, 250, t if any(in_(t, BE, 1, b, b + 0.1) for a, b in tries) else 0.0, seed=0, n=8)
            for j in range(3):
                cv.ellipse(610 + j * 40, 345, 9, 9, (255, 210, 70) if j < n_try else (205, 205, 215), ink=INK, lw=1.6)
            # coins fly out of the phone and Ton counts them
            for j in range(12):
                f = ((fr(t, BE, 1, 0.0, 1.0) * 6 + j * 0.31) % 1.0)
                if j / 12 > fr(t, BE, 1, 0.05, 0.95):
                    continue
                coin(cv, 430 + 330 * f, 420 - 140 * math.sin(math.pi * f) - 30 * f, 12 * (1 - 0.3 * f))
            if fr(t, BE, 1, 0.82, 0.95) > 0:
                ov.append(("!", 540, 330, 110, (255, 120, 100), ease(fr(t, BE, 1, 0.82, 0.88))))
    elif k == 2:
        call_center(cv, t, active=1.0)
        chok(cv, 220, 700, mk(((-60, 120, 30), (-30, 40, 40))), "deadpan", th=30, k=0.9)
        service_bot(cv, 760, 620, 1.2, t=t, mood="flat")
        service_bot(cv, 1000, 640, 1.0, t=t, mood="flat")
    elif k in (3, 4):
        rect(cv, 0, 0, W, H, (42, 54, 94), ink=None)
        ambient(cv, t, 34, (160, 200, 255))
        crystal_ball(cv, 230, 380 + 8 * math.sin(t * 1.6), 2.2, t)
        fill = ease(seg(t, B[3] + 1.2, B[3] + 6.0))
        for i in range(100):
            r, c = divmod(i, 10)
            x, y = 520 + c * 52, 150 + r * 46
            solved = i < 80 and i / 80 < fill
            col = (110, 214, 190) if solved else (92, 108, 150)
            if solved and fill >= 1:
                col = mix(col, (230, 255, 240), max(0.0, math.sin(t * 3 - (r + c) * 0.6)) * 0.55)
            rrect(cv, x, y, x + 40, y + 30, 8, col, lw=1.6)
        ov.append(("80%", 330, 130, 90, (255, 236, 150), ease(seg(t, B[3] + 3.0, B[3] + 4.0))))
        if k == 4:
            dashed_rect(cv, 500, 130, 1060, 640, (255, 214, 110), 4.0, alpha=int(255 * ease(seg(t, B[4], B[4] + 1.0))))
            ov.append(("?", 780, 390, 150, (255, 214, 110), 0.85 * ease(seg(t, B[4] + 0.8, B[4] + 1.6))))
        ton(cv, 1090, 740, REST, "eager" if k == 3 else "think", k=0.85, flip=True)
        chok(cv, 1190, 740, CROSS, "think", k=0.8, flip=True)
    else:
        band(cv, 0, 380, (228, 238, 246), (214, 226, 240), n=8, x0=0, x1=W)
        rect(cv, 0, 380, W, H, (206, 214, 226), ink=None)
        gone = ease(seg(t, B[5] + 3.0, B[5] + 6.0))
        back = ease(seg(t, B[6] + 4.0, B[6] + 8.0))
        for b in range(7):
            vis = (1 - gone) if t < B[6] else (back if b < 4 else back * 0.6)
            vis = min(1.0, max(0.0, vis))
            for i in range(25):
                r, c = divmod(i, 5)
                x = 90 + (b % 4) * 230 + c * 36
                y = 170 + (b // 4) * 180 + r * 30 + 1.5 * math.sin(t * 3 + i)
                if vis <= 0:
                    continue
                cv.ellipse(x, y - 8, 7, 7, (96, 150, 200), ink=INK, lw=1.2, alpha=int(255 * vis))
                cv.fill(spline([(x - 9, y + 10), (x - 7, y), (x + 7, y), (x + 9, y + 10)], closed=True, n=3), (96, 150, 200), ink=INK, lw=1.2, alpha=int(255 * vis))
        mood = "happy" if t < B[6] else "sorry"
        service_bot(cv, 1080, 620, 2.0, t=t, mood=mood, wave=0.5 + 0.5 * math.sin(t * 3) if t < B[6] else 0)
        if B[5] + 0.5 < t < B[6]:
            ov.append(("700", 1080, 250, 100, (255, 255, 255), ease(seg(t, B[5] + 0.8, B[5] + 1.6))))
        if t >= B[6]:
            mini(cv, 800, 650, 2.2, 3, arms="swing", phase=t * 3, expr="o")
            ov.append(("?", 800, 380, 90, (255, 255, 255), ease(seg(t, B[6] + 1.0, B[6] + 1.6)) * (1 - ease(seg(t, B[6] + 4.0, B[6] + 4.6)))))
        ton(cv, 160, 700, REST, "think" if t < B[6] + 8 else "happy", k=0.9)
        chok(cv, 330, 700, CROSS if t < B[6] + 6 else SPREAD, "plead" if t < B[6] + 6 else "happy", k=0.9, th=50)
    pulse_ov(ov, t)
    cv.pop()
