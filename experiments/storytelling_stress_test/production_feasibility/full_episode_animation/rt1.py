"""Red thread, scene 1 (v2): day one in the tech faculty (Ta dozes, Pin's pen lands on his foot, he forgets her name), the thread nobody can see (a close-up of two pinkies),
the old man under the moon with the book of couples, and the thread's one habit: it never says when."""
from rt_common import *  # noqa: F401,F403

NAME, I = "rt1", 1
DUR = scene_dur(I)
CAPS = []
MARK = ["วันแรกของเทอมแรก", "แต่สิ่งที่สองคนนี้มองไม่เห็น", "ตำนานด้ายแดงเล่ากันมา", "ฟังดูโรแมนติกใช่ไหมคะ"]
B = beats(I, MARK)
BE = B + [DUR - TAIL]
CUES = [(BE[0] + (BE[1] - BE[0]) * 0.40, "clink", 0.5), (BE[0] + (BE[1] - BE[0]) * 0.50, "gasp", 0.4), (B[1] + 1.0, "chime", 0.6), (B[2] + 1.0, "whoosh", 0.4),
        (B[2] + 9.0, "ding", 0.4), (B[3] + 3.0, "boing", 0.4)]
TX, PX = 470, 740                     # Ta and Pin at the front desk
SY, SK = 730, 0.82                    # seated: feet line behind the desk, scale


def room(cv, t, flash=0.0):
    lecture(cv, t)
    desks(cv, 470, laptops=False, t=t)


def draw(cv, t, ov):
    cv.push(0, 0, scale=1.0)
    tick(t)
    k = which(t, B)
    if k in (0, 1, 3):
        room(cv, t)
        pen_u = fr(t, BE, 0, 0.26, 0.46)
        drowse = 1 - fr(t, BE, 0, 0.20, 0.34)
        talk_pin = (BE[0] + (BE[1] - BE[0]) * 0.47, BE[0] + (BE[1] - BE[0]) * 0.66)
        talk_ta = (BE[0] + (BE[1] - BE[0]) * 0.70, BE[0] + (BE[1] - BE[0]) * 0.88)
        woke = k > 0 or fr(t, BE, 0, 0.30, 0.40) > 0.5
        pose_t = seated(cv, "phum", TX, SY, SK, th=35, ex="gape" if (0.3 < pen_u < 0.8 and k == 0) else ("neutral" if k == 0 and drowse > 0.5 else ("think" if k == 0 else "happy")),
                        blink_v=1.0 if drowse > 0.5 and k == 0 else blink(t, 0.3), lean=(9 * drowse * math.sin(t * 1.5) if k == 0 else 3 * math.sin(t * 1.6)),
                        mouth=mouth_of(t, *talk_ta, 3) if k == 0 else 0)
        pose_p = seated(cv, "bua", PX, SY, SK, th=35, flip=True, ex="plead" if (k == 0 and talk_pin[0] < t < talk_pin[1]) else "happy",
                        lean=(4 * math.sin(t * 1.4 + 1.5) if k else 0), mouth=mouth_of(t, *talk_pin, 5) if k == 0 else 0)
        desks(cv, 610, t=t)
        seated_front(cv, "phum", TX, SY, pose_t, th=35, k=SK)
        seated_front(cv, "bua", PX, SY, pose_p, th=35, k=SK, flip=True)
        if k == 0 and 0 < pen_u < 1:
            x = PX - 20 - 230 * pen_u
            y = 560 + 180 * pen_u * pen_u
            cv.push(x, y, rot=pen_u * 540)
            rect(cv, -16, -2, 16, 2, (60, 90, 190), lw=1.4)
            cv.pop()
        if k == 0 and fr(t, BE, 0, 0.70, 0.95) > 0:
            ov.append(("?", TX - 20, 380, 100, (255, 255, 255), ease(fr(t, BE, 0, 0.72, 0.80)) * (1 - ease(fr(t, BE, 0, 0.90, 1.0)))))
        if k == 0 and fr(t, BE, 0, 0.47, 0.66) > 0:
            say_waves(cv, PX - 70, 470, t, talk_pin[0], talk_pin[1], flip=True)
        a = 0.0
        if k == 1:
            a = ease(fr(t, BE, 1, 0.10, 0.30))
        elif k == 3:
            a = 1.0
        if a > 0:
            cv.ellipse((TX + PX) / 2, 600, 190, 70, (255, 255, 255), ink=None, alpha=int(36 * a))
            tie(cv, "phum", "bua", t, sag=-46 if k == 3 else 26, alpha=int(255 * a))
        if k == 1:
            # a close-up of the little fingers (two hands, the thread tied round both)
            u = ease(fr(t, BE, 1, 0.30, 0.5)) * (1 - ease(fr(t, BE, 1, 0.92, 1.0)))
            if u > 0.01:
                cx, cy = 640, 215
                cv.push(cx, cy, scale=0.55 + 0.45 * u)
                cv.ellipse(0, 0, 215, 175, (255, 250, 238), ink=INK, lw=4.0, alpha=int(255 * u))
                cv.ellipse(0, 0, 200, 160, (255, 214, 120), ink=None, alpha=int(70 * u))
                cv.pop()
                if u > 0.55:
                    cv.push(cx, cy, scale=0.78)
                    pinky_hook(cv, 0, 80, 1.0, t, tails=False, sleeve_len=30)
                    cv.pop()
        if k == 3:
            cx, cy = 1090, 440
            cv.ellipse(cx, cy, 44, 44, (252, 252, 254), ink=INK, lw=3.0)
            ang = t * 4
            cv.stroke([(cx, cy), (cx + math.cos(ang) * 30, cy + math.sin(ang) * 30)], INK, 3)
            cv.stroke([(cx, cy), (cx + math.cos(ang / 12) * 20, cy + math.sin(ang / 12) * 20)], INK, 4)
            ov.append(("?", cx, cy - 90, 90, (255, 255, 255), 0.5 + 0.5 * math.sin(t * 3)))
            day = int(t * 3.0)
            rect(cv, 930, 396, 1010, 480, (252, 252, 254), lw=2.6)
            rect(cv, 930, 396, 1010, 414, (230, 90, 90), lw=2.0)
            ov.append((str(1 + day % 30), 970, 452, 42, (40, 40, 60), 1.0))
            u = (t * 3.0) % 1.0
            cv.push(970 + 14 * math.sin(u * 7), 440 + 90 * u, rot=40 * math.sin(u * 6))
            rect(cv, -40, -42, 40, 42, (252, 252, 254), lw=1.8)
            cv.pop()
    else:
        moon_sky(cv, t)
        ambient(cv, t, 18, (255, 240, 200), seed=4)
        cloud(cv, 380, 600, 1.5)
        cloud(cv, 940, 640, 1.7)
        yx = 640
        hold = 0.5 + 0.5 * math.sin(t * 1.2)
        st(cv, "yuelao", yx, 620, pose=pl(REST, mk(((-60, 150, 30), (-30, 130, 90)), ((60, 150, 30), (30, 130, 90))), hold), ex="smug", th=20, k=1.12,
           mouth=mouth_of(t, B[2] + 2, B[2] + 7, 1))
        # the book of couples in his left hand, the walking stick in his right, the sack of red thread beside him
        book(cv, yx + 96, 478, 1.0, rot=-12)
        cv.stroke([(yx - 118, 410), (yx - 112, 640)], (126, 86, 56), 8)
        cv.stroke([(yx - 118, 410), (yx - 112, 640)], (176, 126, 84), 4.5)
        rrect(cv, 770, 540, 870, 630, 22, (190, 140, 96), lw=2.6)
        cv.stroke([(820, 540), (808, 520), (836, 516)], RED, 4)
        spool(cv, 540, 640, 26, turn=t * 2)
        # one red thread leaves his hand, drifts down past the clouds towards two glowing hearts (the two it is meant for)
        a = ease(fr(t, BE, 2, 0.30, 0.55))
        hand = (yx + 70, 520)
        sway = 10 * math.sin(t * 1.4)
        for hx, sg in ((250, -1), (1030, 1)):
            heart(cv, hx, 668 + 6 * math.sin(t * 2 + sg), 26, PINK, glow=0.8 + 0.2 * math.sin(t * 3), alpha=int(255 * a))
            link(cv, hand, (hx, 646), t, sag=60 + sway * sg, alpha=int(255 * a), tie=False, spark=True)
        ring(cv, hand, 1.0, alpha=int(255 * a))
    cv.pop()
    pulse_ov(ov, t)
