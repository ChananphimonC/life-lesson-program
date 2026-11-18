"""Scene 2 - the ream and the ruler (script: ฉาก 2). Measure one sheet, then the 6-fold and 7-fold stacks. Drawn to scale at the table:
1 mm = 1.43 px (an A4 sheet is 300 px wide). ~29 s."""
from acting import *  # noqa: F401,F403
from props import *   # noqa: F401,F403

NAME, DUR = "s2", 29.0
CAPS = [
    (5.2, 7.2, "kaew", "แผ่นเดียวหนาเท่าไหร่"),
    (7.6, 10.0, "ton", "(กดเครื่องคิดเลข) ศูนย์จุดหนึ่งมิล"),
    (10.4, 14.4, "kaew", "ทีนี้เอาก้อนที่พับหกครั้ง กับเจ็ดครั้ง มาวัด"),
    (20.2, 22.0, "ton", "(มองไม้บรรทัดสองครั้ง) เท่าตัวพอดี"),
    (22.2, 23.2, "uean", "แล้วไง"),
    (23.4, 26.6, "ton", "พับเพิ่มครั้งเดียว มันหนาเพิ่มเท่าตัวเลย"),
    (26.8, 28.8, "chok", "(เบา) เพราะมันซ้อนทับตัวเอง"),
]
CUES = [(0.4, "step", 0.3), (0.85, "step", 0.3), (1.3, "step", 0.3), (1.75, "step", 0.3), (2.2, "step", 0.3), (3.0, "step", 0.3), (3.7, "thump", 0.9),
        (8.0, "tap", 0.6), (8.4, "tap", 0.6), (8.8, "tap", 0.6), (9.2, "ding", 0.5), (15.0, "paper", 0.7), (16.0, "thump", 0.6), (16.4, "ding", 0.5),
        (18.0, "paper", 0.7), (18.8, "thump", 0.6), (19.2, "ding", 0.5), (23.6, "pop", 0.3)]
TOP, PXC, PY = 520, 640, 566
S = 1.43


def ream(cv, x, y, h_mm=50, lift=0.0):
    h = h_mm * S
    w, d = 300, 180
    x0, x1 = x - w / 2, x + w / 2
    yy = y - lift
    cv.fill([(x0, yy), (x1, yy), (x1 + 0, yy + 0)], PAPER, ink=None)
    cv.fill([(x0 + d * 0.3, yy - h - d * 0.45), (x1 + d * 0.3, yy - h - d * 0.45), (x1, yy - h), (x0, yy - h)], PAPER, ink=INK, lw=2.2, shade_col=PAPER_SH)
    rect(cv, x0, yy - h, x1, yy, (246, 244, 236), shade_col=(222, 220, 212))
    for i in range(1, 24):
        cv.stroke([(x0 + 3, yy - h * i / 24), (x1 - 3, yy - h * i / 24)], (214, 212, 202), 1.2)
    cv.fill([(x1, yy), (x1 + d * 0.3, yy - d * 0.45), (x1 + d * 0.3, yy - h - d * 0.45), (x1, yy - h)], (226, 224, 214), ink=INK, lw=2.2)
    rect(cv, x0 + 80, yy - h + 4, x1 - 80, yy - 4, (60, 120, 190), lw=1.6)


def ruler(cv, x, y0, mm, col=(236, 200, 120)):
    """Vertical ruler standing on the table at (x, y0) showing `mm` millimetres of height (1.43 px / mm)."""
    L = mm * S + 50
    rect(cv, x - 14, y0 - L, x + 14, y0, col, lw=2.0)
    for m in range(0, int(mm) + 30, 1):
        yy = y0 - m * S
        if yy < y0 - L:
            break
        ln = 14 if m % 10 == 0 else (9 if m % 5 == 0 else 5)
        cv.stroke([(x - 14, yy), (x - 14 + ln, yy)], INK, 1.2)


def draw(cv, t, ov):
    cv.push(0, 0, scale=1.0)
    courtyard(cv, 300, "day", gate_x=150, gate_s=0.6, t=t)
    shop(cv, t, 760, 600, 1.3)
    if t >= 3.7:
      actor(cv, "kaew", 960, 600, -40, REST if t > 5 else REST, "gloat", k=0.95, mouth=max(talk(t, 5.2, 7.2, 1), talk(t, 10.4, 14.4, 2)), blink_v=blink(t, .7))
    actor(cv, "uean", 1130, 600, -35, REST, "think" if t < 22 else "shout", k=0.85, mouth=talk(t, 22.2, 23.2, 5), blink_v=blink(t, .2))
    shop_counter(cv, 760, 600, 1.3)

    # Ton behind the table; Kaew carries the ream in and puts it down (she is in front of the table while she does)
    ton_pose = REST
    if 7.6 < t < 10.0:
        ton_pose = pl(REST, PRESS_C, seg(t, 7.6, 8.0))
    elif 14.4 < t < 16.4 or 17.4 < t < 19.0:
        ton_pose = PRESS_C
    elif 20 < t < 21:
        ton_pose = THINK
    ex_t = "think" if 7.6 < t < 10 else ("eager" if 14 < t < 19.6 else ("aha" if 20 < t < 22 else ("shout" if 23.4 < t < 26.6 else "neutral")))
    actor(cv, "ton", PXC, 655, 8, ton_pose, ex_t, k=1.15, mouth=max(talk(t, 7.6, 10.0, 3), talk(t, 20.2, 22.0, 4), talk(t, 23.4, 26.6, 5)), blink_v=blink(t, .1))
    table(cv, PXC, TOP, 560, 60, 60)

    # table content
    if t < 3.7:
        pass
    else:
        if t < 14.4:
            ream(cv, PXC, PY + 8, 50, lift=0 if t > 3.8 else 40 * (3.8 - t) / 0.1)
            sheet_h = 0.1 * S
        if 10.0 <= t < 14.4:
            pass
    if t < 3.7:
        # Kaew carrying the ream across in front of the table
        kx = keys([(0.0, 1500), (3.0, 960)], t)
        ph = walk_ph(t, 5.5)
        actor(cv, "kaew", kx, 665, 45, walk_pose(ph, carry=CARRY), "neutral", k=1.05, walk=dict(phase=ph, stride=12, lift=9), flip=True)
        wp = wrist_pos("kaew", kx, 665, 45, CARRY, "R", 1.05, True)
        rect(cv, wp[0] - 60, wp[1] - 22, wp[0] + 40, wp[1] + 10, (246, 244, 236), lw=2.0)
    if t >= 3.7 and t < 14.4:
        ruler(cv, PXC + 190, PY + 8, 55)
        if t > 5.5:
            # ream measured: 50 mm brace appears
            a = seg(t, 5.8, 6.4)
            ov.append(("50 มม.", PXC + 300, PY - 110, 56, (255, 224, 120), a))
        if t > 8.4:
            ov.append(("50 ÷ 500 = 0.1 มม.", PXC, 300, 52, (255, 255, 255), seg(t, 8.4, 9.2) * (1 if t < 12 else 1 - seg(t, 12, 12.6))))
    if 14.4 <= t:
        # the 6-fold then the 7-fold stack, to scale, with a ruler
        folds = 6 if t < 17.4 else 7
        f_anim = seg(t, 14.6, 15.6) if folds == 6 else seg(t, 17.6, 18.6)
        table_paper(cv, PXC - 40, PY, 300, 424, folds - 1 if f_anim < 1 else folds, f_anim if f_anim < 1 else 0.0)
        ruler(cv, PXC + 190, PY, 20)
        if t > 16.2 and t < 20.6 and folds == 6:
            ov.append(("6.4 มม.", PXC + 290, PY - 100, 60, (255, 224, 120), seg(t, 16.2, 16.8)))
        if t > 19.2:
            ov.append(("12.8 มม.", PXC + 290, PY - 100, 60, (255, 224, 120), seg(t, 19.2, 19.8)))
    # Chok murmurs
    if t > 25.5:
        cx_ = keys([(25.5, -60), (27.0, 330)], t)
        if t < 27.0:
            ph = walk_ph(t, 6.5)
            actor(cv, "chok", cx_, 665, 50, walk_pose(ph), "neutral", k=1.1, walk=dict(phase=ph, stride=16, lift=12))
        else:
            actor(cv, "chok", 330, 665, 50, REST, "think", k=1.1, mouth=talk(t, 26.8, 28.8, 5), blink_v=blink(t, .4))
    cv.pop()


PRESS_C = mk(((-64, 168, 40), (-26, 214, 104)), ((64, 168, 40), (26, 214, 104)))
