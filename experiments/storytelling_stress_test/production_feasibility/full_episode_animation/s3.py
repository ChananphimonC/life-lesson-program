"""Scene 3 - the kite string (script: ฉาก 3). Twenty doublings on a calculator while Aunt Uean bangs a pot, the 105 m string across the
field, Ton works out the growth in a sketch, finds 42, and remembers what he wrote in the cup. ~95 s."""
from acting import *  # noqa: F401,F403
from props import *   # noqa: F401,F403

NAME, DUR = "s3", 95.0
T_CALC0, T_CALC1 = 11.0, 19.0          # calculator doubling: 20 taps
T_FIELD0, T_FIELD1 = 25.0, 44.0
T_SK0, T_SK1 = 58.0, 80.0              # Ton's sketch
CAPS = [
    (0.5, 5.4, "kaew", "ทายเล่น ๆ ก่อนเปิดซอง ถ้าพับยี่สิบครั้ง สูงเท่าไหร่ เขียนลงเศษกระดาษ"),
    (5.8, 10.4, "chok", "ผมไม่เชื่อตัวเลข ผมเชื่อสายว่าว ใครรู้ ผมปล่อยสายให้ดู"),
    (10.6, 12.6, "ton", "ง่ายจะตาย คูณสอง ยี่สิบรอบ"),
    (19.6, 22.6, "ton", "(เลื่อนจุดทศนิยม) …ทำไมยาวขนาดนี้"),
    (22.8, 24.8, "chok", "ผมขอดูด้วยตา ตามมา"),
    (38.0, 39.4, "chok", "ถึงแล้ว!"),
    (45.2, 49.0, "uean", "นี่… กระดาษแผ่นเดียวเหรอ"),
    (49.2, 51.2, "ton", "(เบา) ผมเขียนเท่าร้านนี้"),
    (51.4, 53.0, "uean", "ฉันเขียนต้นมะม่วง"),
    (53.2, 54.6, "chok", "ผมไม่ได้เขียน"),
    (54.8, 56.0, "uean", "โกง"),
    (62.0, 68.0, "ton", "(พึมพำ) ที่นี่… ถ้ายาวขนาดนี้… อีกสิบครั้ง… ป้า! ทุกสิบครั้ง ยาวขึ้นราวพันเท่า!"),
    (73.0, 74.6, "chok", "ดวงจันทร์ล่ะ"),
    (77.0, 79.6, "ton", "สี่สิบสอง! คำตอบคือสี่สิบสอง!"),
    (80.4, 83.0, "uean", "แล้วเอ็งเขียนอะไรหย่อนไป"),
    (86.0, 87.4, "ton", "ล้านครั้ง"),
    (88.6, 89.8, "ton", "ยาย ขอแก้คำตอบ"),
    (89.9, 91.0, "kaew", "ส่งแล้วส่งเลย"),
    (91.1, 92.4, "ton", "แต่ผมรู้แล้วนะ!"),
    (92.5, 93.3, "kaew", "ตอนนี้"),
    (93.4, 95.0, "uean", "หลานฉลาด แต่ฉลาดทีหลัง"),
]
CUES = [(T_CALC0 + 0.4 * i, "tap", 0.5) for i in range(20)] + [(T_CALC0 + 0.4 * i + 0.05, "bang", 0.55) for i in range(20)] + [
    (19.4, "ding", 0.6), (38.0, "whoosh", 0.5), (47.0, "gasp", 0.6), (56.0, "boing", 0.5), (62.0, "scribble", 0.6), (66.0, "scribble", 0.6),
    (77.0, "boing", 0.7), (86.0, "crickets", 0.6), (93.8, "laugh", 0.6), (94.4, "ladle", 0.6)]
for t0_, t1_ in ((25.0, 38.0), (0.0, 0.1)):
    CUES += [(t0_ + k * 0.45, "step", 0.25) for k in range(int((t1_ - t0_) / 0.45))]

BANG = mk(((-80, 100, 10), (-50, 40, 60)))
BANG_LO = mk(((-70, 150, 20), (-30, 150, 100)))


def calc(cv, x, y, text):
    rect(cv, x - 46, y - 74, x + 46, y, (60, 64, 76), lw=2.4)
    rect(cv, x - 38, y - 66, x + 38, y - 44, (170, 220, 190), lw=1.4)
    for r in range(3):
        for c in range(3):
            cv.ellipse(x - 26 + c * 26, y - 34 + r * 12, 6, 4.5, (220, 226, 236), ink=None)


def shop_set(cv, t):
    courtyard(cv, 300, "day", gate_x=150, gate_s=0.6, t=t)
    shop(cv, t, 760, 600, 1.3)


def part_table(cv, t, ov):
    """0-25 s and 44-58 s, 80-95 s: the table in front of the shop."""
    shop_set(cv, t)
    n = clamp((t - T_CALC0) / 0.4, 0, 20)
    nt = int(n)
    banging = T_CALC0 <= t < T_CALC1 + 0.4
    ph = ((t - T_CALC0) % 0.4) / 0.4 if banging else 1.0
    pose_u = REST
    if banging:
        pose_u = pl(BANG, BANG_LO, ease(min(1.0, ph * 2.2))) if ph < 0.45 else pl(BANG_LO, BANG, seg(ph, 0.45, 1.0))
    elif 44 <= t < 49:
        pose_u = pl(REST, mk(((-84, 130, 20), (-62, 90, 50))), seg(t, 45, 46))
    ex_u = "shout" if banging else ("gape" if 44 <= t < 52 else ("shout" if 80 < t < 83 or t > 93 else ("laugh" if t > 93 else "gloat")))
    ux = 1130
    actor(cv, "uean", ux, 600, -35, pose_u, ex_u, k=0.88, mouth=max(talk(t, 45.2, 49.0, 5), talk(t, 51.4, 53.0, 5), talk(t, 54.8, 56, 6), talk(t, 80.4, 83.0, 6),
                                                                   talk(t, 93.4, 95.0, 7)), blink_v=blink(t, .2),
          lean=(5 * math.sin(t * 22) if t > 93.4 else 0))
    mk_k = max(talk(t, 0.5, 5.4, 1), talk(t, 89.9, 91.0, 2), talk(t, 92.5, 93.3, 3))
    actor(cv, "kaew", 960, 600, -40, REST if t > 5.4 else pl(REST, POINT_FWD, seg(t, 3.2, 3.8)), "smug", k=0.95, mouth=mk_k, blink_v=blink(t, .7))
    shop_counter(cv, 760, 600, 1.3)
    if banging:
        pot(cv, 1010, 560, 60)
        cv.stroke([(1010, 520), (1010 + 10 * math.sin(t * 30), 508)], (255, 255, 255), 0)
    TOP, PXC = 520, 640
    # Ton behind the table with the calculator
    ton_pose = REST
    ex_t = "eager"
    if T_CALC0 - 1.0 < t < T_CALC1 + 0.4:
        ton_pose = pl(REST, WRITE_A, seg(t, T_CALC0 - 0.6, T_CALC0 - 0.2))
        ton_pose = dict(ton_pose, R=(ton_pose["R"][0], (ton_pose["R"][1][0] + 4 * math.sin(t * 15.7), ton_pose["R"][1][1], ton_pose["R"][1][2])))
        ex_t = "eager"
    elif 19.4 < t < 24.0:
        ex_t = "gape"
    elif t >= 44:
        ex_t = "deadpan" if t < 57 else "think"
    if t < 25.0 or t >= 80.0 or 44.0 <= t < 58.0:
        if 80 <= t < 86:
            u = seg(t, 80.4, 86.0)
            th_ton = 8 - 70 * ease(seg(t, 82.5, 85.0)) if t > 82.5 else 8
            actor(cv, "ton", PXC, 655, th_ton, pl(CHEER, REST, seg(t, 80, 81.5)), "gape" if t < 83 else "worried", k=1.15, mouth=talk(t, 77.0, 79.6, 4),
                  blink_v=blink(t, .3))
        elif t >= 86:
            actor(cv, "ton", PXC, 655, -62, REST, "plead" if 88.6 < t < 92.4 else "worried", k=1.15, mouth=max(talk(t, 86.0, 87.4, 4), talk(t, 88.6, 89.8, 5), talk(t, 91.1, 92.4, 6)),
                  blink_v=blink(t, .3))
        else:
            actor(cv, "ton", PXC, 655, 8, ton_pose, ex_t, k=1.15, mouth=max(talk(t, 10.6, 12.6, 4), talk(t, 19.6, 22.6, 5), talk(t, 49.2, 51.2, 6)),
                  blink_v=blink(t, .3))
        table(cv, PXC, TOP, 560, 60, 60)
        calc(cv, PXC - 150, TOP + 38, "")
        sheet(cv, PXC + 120, TOP + 42, 70, 22, 4)
        if t < 25:
            ov.append((f"{0.1 * 2 ** nt:,.1f} มม." if nt else "0.1 มม.", PXC + 20, 215, 44, (200, 255, 210), seg(t, T_CALC0 - 0.3, T_CALC0 + 0.1)))
            if nt:
                ov.append((f"{nt}", PXC + 20, 150, 64, (255, 224, 120), seg(t, T_CALC0, T_CALC0 + 0.2)))
    # Chok
    if t < 25.0:
        if t > 0:
            actor(cv, "chok", 340, 660, 50, pl(REST, mk(((-60, 150, 30), (-30, 130, 70))), seg(t, 6.0, 7.0)) if t > 6 else REST, "think" if t > 5.8 else "neutral",
                  k=1.1, mouth=talk(t, 5.8, 10.4, 7), blink_v=blink(t, .4))
            if t > 5.8:
                spool(cv, 392, 560, 26, t * 3)
    elif 44.0 <= t < 58.0:
        actor(cv, "chok", 340, 660, 50, SHRUG if 53 < t < 54.8 else REST, "neutral" if t < 53 else "smug", k=1.1, mouth=talk(t, 53.2, 54.6, 7), blink_v=blink(t, .4))
    elif t >= 80:
        actor(cv, "chok", 340, 660, 50, REST, "neutral", k=1.1, blink_v=blink(t, .4))


def part_field(cv, t, ov):
    u = seg(t, T_FIELD0, T_FIELD1)
    band(cv, -200, 330, (138, 200, 236), (255, 236, 196), 20)
    moon(cv, 1090, 110, 36, 0.5)
    for i in range(16):
        cv.ellipse(i * 100 - 60, 322, 70, 34 + (i % 3) * 8, (122, 170, 112), ink=None)
    # temple gate far right
    gx = 1150
    rect(cv, gx - 40, 230, gx - 22, 340, (196, 70, 60)); rect(cv, gx + 22, 230, gx + 40, 340, (196, 70, 60))
    cv.fill([(gx - 60, 232), (gx, 190), (gx + 60, 232)], (236, 168, 60), ink=INK, lw=2.2)
    # rice field: terraces
    for i in range(10):
        tt = i / 9
        rect(cv, -300, 330 + 420 * tt ** 1.5, W + 300, 330 + 420 * ((i + 1) / 9) ** 1.5 + 2, mix((150, 196, 110), (96, 160, 80), tt), ink=None)
    for i in range(0, 1400, 70):
        cv.stroke([(i, 360), (i - 60, 700)], (128, 180, 96), 2, alpha=140)
    if u > 0.5:                                                                                      # football pitch overlay
        a = int(180 * seg(t, T_FIELD0 + 0.5 * (T_FIELD1 - T_FIELD0) + 4, T_FIELD1 - 2))
        if a > 0:
            cv.fill([(170, 430), (1110, 430), (1160, 640), (130, 640)], (70, 150, 80), ink=(255, 255, 255), lw=3, alpha=a)
            cv.stroke([(640, 430), (640, 640)], (255, 255, 255), 3, alpha=a)
            cv.ellipse(640, 535, 48, 28, (255, 255, 255), ink=None, alpha=0)
    # string, kids, Chok at the spool
    run = ease(seg(t, T_FIELD0 + 1.5, 37.2))
    lead = (200 + (1085 - 200) * run, 575 - 30 * run)
    sp = (190, 530)
    sag = 22 * (1 - run * 0.8)
    pts = [(sp[0] + (lead[0] - sp[0]) * s, sp[1] + (lead[1] - sp[1]) * s + sag * math.sin(math.pi * s)) for s in [i / 24 for i in range(25)]]
    if t > T_FIELD0 + 1.5:
        cv.stroke(pts, STRING, 5)
        for k in range(1, 12):                                                                        # knots slide out along the string
            s = ((k / 12 + (t - T_FIELD0) * 0.35) % 1.0)
            i = int(s * 24)
            cv.ellipse(pts[i][0], pts[i][1], 5, 5, (200, 120, 30), ink=INK, lw=1.2)
    for j in range(4):
        sx = 190 + 40 * j
        kx = sx + (lead[0] - sx - 30 * j) * run
        ky = 590 + 30 * j + (40 * j) * 0
        ph = t * 11 + j * 1.3
        mini(cv, kx if j else lead[0], (ky if j else lead[1] + 40), 1.5 - 0.1 * j, j * 3 + 1, arms="swing" if j else "up", moving=run < 0.99, phase=ph, flip=False, expr="grin")
    spool(cv, *sp, r=28, turn=t * (6 if run < 1 else 0))
    actor(cv, "chok", 150, 650, 40, pl(REST, mk(((-70, 130, 30), (-34, 120, 90))), seg(t, T_FIELD0, T_FIELD0 + 1.0)), "shout" if 37.8 < t < 39.6 else "neutral", k=1.0,
          mouth=talk(t, 38.0, 39.4, 8), blink_v=blink(t, .4))
    if 38.0 < t < 41.0:
        burst(cv, 1040, 520, seg(t, 38.0, 41.0))


def sketch_panel(cv, t, ov, u):
    """Ton's imagination bubble: the doubling grows from a village to the Earth to the Moon (world-to-scale sketch)."""
    cx, cy = 700, 270
    cv.ellipse(cx, cy + 8, 480, 218, (252, 250, 240), ink=INK, lw=3.2)
    for k, (dx, dy, r) in enumerate(((-440, 205, 18), (-470, 260, 12), (-500, 305, 8))):
        cv.ellipse(cx + dx + 160, cy + dy - 20, r, r, (252, 250, 240), ink=INK, lw=2.4)
    # village (left) and temple
    for i, (hx, hy) in enumerate(((330, 380), (370, 370), (410, 382))):
        cv.fill([(hx - 18, hy), (hx + 18, hy), (hx + 18, hy - 22), (hx, hy - 36), (hx - 18, hy - 22)], (232, 150, 100), ink=INK, lw=2)
    s1 = seg(u, 0.0, 0.2)                                                                              # 20 folds: field-length string
    s2 = seg(u, 0.22, 0.45)                                                                            # 30: past the town
    s3 = seg(u, 0.5, 0.74)                                                                             # 40: wraps the Earth
    s4 = seg(u, 0.78, 1.0)                                                                             # 41, 42: to the Moon
    path = [(440, 372)]
    if s1 > 0:
        cv.stroke([(440, 372), (440 + 120 * s1, 372)], STRING, 5)
        ov.append(("20", 520, 420, 44, (255, 224, 120), s1))
    if s2 > 0:
        cv.stroke([(560, 372), (560 + 130 * s2, 360 - 30 * s2)], STRING, 5)
        for i in range(3):
            cv.fill([(640 + i * 24, 350 - 30 * s2), (664 + i * 24, 350 - 30 * s2), (664 + i * 24, 322 - 30 * s2), (640 + i * 24, 322 - 30 * s2)], (170, 170, 190),
                    ink=INK, lw=1.6, alpha=int(255 * s2))
        ov.append(("30", 640, 410, 44, (255, 224, 120), s2))
    ex_, ey_, er = 880, 300, 92
    if s3 > 0:
        cv.ellipse(ex_, ey_, er, er, (90, 150, 220), ink=INK, lw=2.6, alpha=int(255 * min(1, s3 * 3)))
        cv.fill(ellipse_pts(ex_ - 20, ey_ - 10, 40, 30, n=20), (120, 190, 110), ink=None, alpha=int(255 * min(1, s3 * 3)))
        turns = 2.74 * s3
        for k in range(3):
            if turns > k:
                fr = min(1.0, turns - k)
                yy = ey_ - 30 + k * 30
                a1, a2 = 180, 180 + 360 * fr
                cv.stroke(ellipse_pts(ex_, yy, er * 1.04, er * 0.28, n=60, a0=a1, a1=a2), STRING, 5)
        ov.append(("40", ex_, 420, 44, (255, 224, 120), s3))
    if s4 > 0:
        mxx, myy = 1090, 215
        moon(cv, mxx, myy, 34, 0.5)
        cv.stroke([(ex_ + er, ey_ - 20), (ex_ + er + (mxx - ex_ - er) * s4, ey_ - 20 + (myy - ey_ + 20) * s4)], STRING, 5)
        if s4 > 0.55:
            ov.append(("42", 1010, 150, 70, (255, 255, 255), seg(s4, 0.55, 0.8)))


def part_sketch(cv, t, ov):
    courtyard(cv, 300, "day", gate_x=150, gate_s=0.6, t=t, show_flags=False)
    shop(cv, t, 760, 600, 1.3)
    shop_counter(cv, 760, 600, 1.3)
    u = seg(t, 62.0, 76.0)
    actor(cv, "uean", 1130, 600, -35, REST, "think", k=0.88, blink_v=blink(t, .2))
    actor(cv, "kaew", 960, 600, -40, REST, "smug", k=0.95, blink_v=blink(t, .7))
    # Ton squats and draws on the ground with a stick; the bubble shows what he works out
    draw_t = 58.2 < t < 77.0
    pose = mk(((-70, 180, 30), (-26, 230, 110)))
    if draw_t:
        pose = dict(pose, R=(pose["R"][0], (pose["R"][1][0] + 18 * math.sin(t * 6), pose["R"][1][1] + 6, pose["R"][1][2])))
    actor(cv, "ton", 330, 690, 40, pose, "think" if t < 76 else "aha", k=1.15, lean=22 if draw_t else 6, mouth=max(talk(t, 62.0, 68.0, 4), talk(t, 77.0, 79.6, 5)),
          blink_v=blink(t, .3))
    cv.stroke([(375, 650), (420, 690)], (150, 108, 70), 5)
    if t > 62.0:
        n0 = len(ov)
        cv.push(0, -52)
        sketch_panel(cv, t, ov, seg(t, 62.0, 77.0))
        cv.pop()
        for i in range(n0, len(ov)):
            x_, y_, *rest_ = ov[i][1:]
            ov[i] = (ov[i][0], ov[i][1], ov[i][2] - 52) + ov[i][3:]
    chok_pose = pl(REST, THINK, seg(t, 72.5, 73.2)) if 72.5 < t < 76 else REST
    actor(cv, "chok", 1130, 700, -40, chok_pose, "think" if t > 72 else "neutral", k=1.1, mouth=talk(t, 73.0, 74.6, 7), blink_v=blink(t, .4))
    if t >= 77.0:
        burst(cv, 330, 360, seg(t, 77.0, 78.4), 10, 20, 90)


def draw(cv, t, ov):
    cv.push(0, 0, scale=1.0)
    if T_FIELD0 <= t < T_FIELD1:
        part_field(cv, t, ov)
    elif 58.0 <= t < 80.0:
        part_sketch(cv, t, ov)
    else:
        part_table(cv, t, ov)
    cv.pop()
