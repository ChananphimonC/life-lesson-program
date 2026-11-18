"""Scene 5 - opening the envelope (script: ฉาก 5). Dusk, festival lights. 42; the guesses laid on a chalk line; Ton's last objection is
answered by his own calculation; he puts on the apron himself. ~46 s."""
from acting import *  # noqa: F401,F403
from props import *   # noqa: F401,F403

NAME, DUR = "s5", 46.0
CAPS = [
    (6.4, 8.6, "kaew", "(อ่าน) สี่สิบสอง"),
    (13.2, 15.2, "uean", "ลุงโชคใกล้สุด"),
    (15.4, 17.2, "chok", "(เขิน) ผมชนะเหรอ"),
    (18.2, 24.0, "ton", "(ฮึดสุดท้าย) ดวงจันทร์ไม่ได้อยู่ที่เดิมนะ! ทีใกล้ทีไกล สี่สิบสองอาจไม่ถึงก็ได้!"),
    (24.4, 26.8, "kaew", "(ยื่นกระดาษเปล่า) เอ็งคำนวณเองสิ"),
    (33.0, 37.4, "ton", "สี่สิบเอ็ด… ไม่ถึงแม้ตอนใกล้สุด สี่สิบสอง… เกินแม้ตอนไกลสุด"),
    (37.6, 38.8, "kaew", "ว่าไง"),
    (39.0, 41.4, "ton", "…คำตอบมีอย่างเดียว"),
]
CUES = [(0.5, "step", 0.3), (1.0, "step", 0.3), (3.5, "rip", 0.8), (5.0, "paper", 0.6), (6.2, "ding", 0.5), (8.8, "crowd", 0.6), (9.4, "plop", 0.7), (10.2, "plop", 0.7), (11.0, "plop", 0.7),
        (28.2, "scribble", 0.5), (29.0, "scribble", 0.5), (33.4, "ding", 0.5), (36.0, "ding", 0.5), (41.8, "whoosh", 0.6), (43.4, "thump", 0.5), (44.4, "cheer", 0.4)]


def apron(cv, x, y, a=1.0):
    pts = [(x - 40, y - 62), (x + 40, y - 62), (x + 52, y + 74), (x - 52, y + 74)]
    cv.fill(pts, (250, 244, 224), ink=INK, lw=2.4, shade_col=(228, 220, 196), alpha=int(255 * a))
    cv.stroke([(x - 40, y - 62), (x - 18, y - 118)], INK, 2.0, alpha=int(255 * a))
    cv.stroke([(x + 40, y - 62), (x + 18, y - 118)], INK, 2.0, alpha=int(255 * a))
    cv.fill([(x - 28, y + 6), (x + 28, y + 6), (x + 28, y + 40), (x - 28, y + 40)], (236, 120, 100), ink=INK, lw=1.8, alpha=int(255 * a))


def bars(cv, ov, u):
    """Distance bars: 41 folds stop short of the Moon's nearest distance; 42 pass its farthest. Shown as bars against a shaded Moon band."""
    x0, x1 = 160, 1120
    sc = (x1 - x0) / 480000.0
    near, far = 356400 * sc, 406700 * sc
    rect(cv, 130, 120, 1150, 360, (250, 250, 244), lw=3.0)
    cv.fill([(x0 + near, 130), (x0 + far, 130), (x0 + far, 350), (x0 + near, 350)], (250, 226, 150), ink=None)
    cv.stroke([(x0 + near, 130), (x0 + near, 350)], (214, 150, 40), 3)
    cv.stroke([(x0 + far, 130), (x0 + far, 350)], (214, 150, 40), 3)
    moon(cv, x0 + (near + far) / 2, 160, 22, 0.5)
    a = seg(u, 0.0, 0.5)
    b = seg(u, 0.5, 1.0)
    h41, h42 = 219902 * sc, 439805 * sc
    cv.fill([(x0, 200), (x0 + h41 * a, 200), (x0 + h41 * a, 250), (x0, 250)], (120, 190, 130), ink=INK, lw=2.4)
    cv.fill([(x0, 280), (x0 + h42 * b, 280), (x0 + h42 * b, 330), (x0, 330)], (236, 120, 100), ink=INK, lw=2.4)
    if a > 0.95:
        ov.append(("41", 100, 225, 44, (255, 255, 255), 1.0))
    if b > 0:
        ov.append(("42", 100, 305, 44, (255, 255, 255), 1.0))


def draw(cv, t, ov):
    cv.push(0, 0, scale=1.0)
    courtyard(cv, 300, "dusk", gate_x=150, gate_s=0.6, t=t)
    # crowd (minis) around, reacting
    gasp_t = seg(t, 6.6, 8.8)
    for j in range(12):
        x_ = 40 + j * 105 + (j % 3) * 18
        arms = "cheer" if 8.8 < t < 10.4 else ("up" if 6.6 < t < 8.8 else "swing")
        mini(cv, x_ if not (330 < x_ < 560) else x_ + 330, 560 + (j % 3) * 20, 1.5, j, arms=arms, moving=False, phase=t * 6 + j, expr="o" if gasp_t > 0 else "grin")
    # Kaew on a chair
    chair_y = 0
    if t < 3.2:
        kx = keys([(0, 1350), (1.4, 810)], t)
        ph = walk_ph(t, 5.5)
        if t < 1.4:
            actor(cv, "kaew", kx, 650, 45, walk_pose(ph, carry=CARRY), "smug", k=1.1, walk=dict(phase=ph, stride=12, lift=9), flip=True)
            envelope(cv, kx - 30, 520, 52, 10)
        else:
            chair_y = -50 * ease(seg(t, 1.6, 2.6))
            rect(cv, 770, 640, 850, 660, (96, 140, 200), lw=2.0)
            rect(cv, 776, 660, 786, 700, (96, 140, 200), lw=1.6); rect(cv, 834, 660, 844, 700, (96, 140, 200), lw=1.6)
            actor(cv, "kaew", 810, 690 + chair_y, 20, pl(CARRY, REST, seg(t, 1.4, 2.4)), "smug", k=1.1, flip=True)
    else:
        rect(cv, 770, 640, 850, 660, (96, 140, 200), lw=2.0)
        rect(cv, 776, 660, 786, 700, (96, 140, 200), lw=1.6); rect(cv, 834, 660, 844, 700, (96, 140, 200), lw=1.6)
        pose = mk(((-62, 150, 30), (-30, 130, 100)), ((62, 150, 30), (30, 130, 100)))
        if 3.0 <= t < 6.0:
            pose = pl(REST, pose, seg(t, 3.0, 3.5))
        elif t >= 6.0:
            pose = pl(pose, POINT_UP if t > 20 and t < 22 else REST, seg(t, 6.0, 6.6)) if t < 24 else REST
        actor(cv, "kaew", 810, 636, 20, pose, "gloat" if t < 6 else "smug", k=1.1, flip=True, mouth=max(talk(t, 6.4, 8.6, 1), talk(t, 24.4, 26.8, 2), talk(t, 37.6, 38.8, 3)),
              blink_v=blink(t, .7))
        if t < 6.4:
            envelope(cv, 730, 540, 56, 6, open_amt=seg(t, 3.4, 4.6), sealed=t < 3.4)
            if t > 4.6:
                sheet(cv, 730, 540 - 40 * seg(t, 4.6, 5.8), 40, 28, 0)
        elif t < 10.0:
            sheet(cv, 730, 480, 60, 40, -4)
        if t >= 6.4 and t < 9.8:
            ov.append(("42", 810, 230, 150, (255, 230, 110), ease(seg(t, 6.4, 7.1)) * (1 - seg(t, 9.0, 9.8))))
    # Uean, Chok
    actor(cv, "uean", 1120, 700, 40, mk(((-70, 140, 30), (-34, 150, 90)), ((70, 140, 30), (34, 150, 90))) if 8.8 < t < 11.4 else (HIP if t > 22 else REST),
          "gloat" if t < 8 else "shout" if 13.2 < t < 15.2 else "smug", k=1.0, flip=True, mouth=talk(t, 13.2, 15.2, 4), blink_v=blink(t, .2))
    actor(cv, "chok", 330, 700, 40, SHRUG if 15.4 < t < 17.2 else REST, "yikes" if 15.4 < t < 17.2 else "neutral", k=1.0, mouth=talk(t, 15.4, 17.2, 5), blink_v=blink(t, .4))
    # the chalk number line and the slips
    if 9.0 <= t < 28.0:
        a = seg(t, 9.2, 10.6)
        y_ = 728
        cv.stroke([(60, y_), (60 + 1160 * a, y_)], CHALK, 5)
        if a >= 1:
            cv.fill([(700 - 16, y_ - 8), (700 + 16, y_ - 8), (700 + 24, y_ - 30), (700, y_ - 46), (700 - 24, y_ - 30)], (255, 214, 60), ink=INK, lw=2.2)
            for sx, nm, tt in ((1240, "ton", 10.2), (420, "uean", 10.8), (646, "chok", 11.4)):
                u = seg(t, tt, tt + 0.7)
                yy = keys([(tt, 520), (tt + 0.7, y_ - 16)], t)
                if sx > 1200:
                    cv.fill([(1150, y_ - 28), (1196, y_ - 28), (1196, y_ - 40), (1220, y_ - 20), (1196, y_ - 0), (1196, y_ - 12), (1150, y_ - 12)], (255, 170, 90), ink=INK, lw=1.8,
                            alpha=int(255 * u))
                else:
                    sheet(cv, sx, yy, 40, 30, -8 + 4 * math.sin(t * 3), alpha=int(255 * max(0.0, u)))
    # Ton
    ton_pose = REST
    ex_t = "shout"
    mouth = talk(t, 18.2, 24.0, 6)
    th_t = 40
    tx = 470
    ph = t * 7
    if t < 9:
        ex_t, ton_pose = "eager", REST
        mouth = 0
    elif t < 18.2:
        ex_t, ton_pose = "gape", HEADS
    elif t < 24.4:
        ex_t, ton_pose = "shout", pl(REST, POINT_UP, seg(t, 18.4, 19.4))
    elif t < 33.0:
        ex_t, ton_pose = ("think", pl(POINT_UP, WRITE_A, seg(t, 24.6, 26.4)))
        if 27.4 < t < 32.6:
            ton_pose = write_pose(t, 9)
        mouth = 0
    elif t < 37.4:
        ex_t, ton_pose, mouth = "think", REST, talk(t, 33.0, 37.4, 7)
    elif t < 41.4:
        ex_t, ton_pose, mouth = "deadpan", REST, talk(t, 39.0, 41.4, 8)
    else:
        ex_t, ton_pose = "deadpan", REST
    actor(cv, "ton", 560, 700, 40, ton_pose, ex_t, k=1.2, mouth=mouth, blink_v=blink(t, .1))
    if t >= 41.8:
        a = seg(t, 41.8, 43.6)
        ax_ = keys([(41.8, 1050), (43.2, 560)], t)
        ay_ = keys([(41.8, 520), (42.5, 380), (43.2, 570)], t)
        if t < 43.2:
            apron(cv, ax_, ay_, 1.0)
        else:
            apron(cv, 560, 570, 1.0)
        if t >= 43.2:
            burst(cv, 560, 520, seg(t, 43.2, 44.6), 8, 30, 90, (255, 235, 140))
    if 27.0 < t < 38.0:
        pass
    if 28.0 < t < 38.6:
        bars(cv, ov, seg(t, 29.5, 36.0))
    cv.pop()
