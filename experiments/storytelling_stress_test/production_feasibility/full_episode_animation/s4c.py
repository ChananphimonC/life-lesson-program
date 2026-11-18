"""Scene 4c - folds 7-10, the 11th that will not turn, and what Ton works out (script: ฉาก 4, second half). Oblique close-up of a 2 m wide
strip (production choice: the script's 0.30 m wide roll would end as a brick-sized block, see FINAL_PRODUCTION_REPORT). ~84 s."""
from acting import *  # noqa: F401,F403
from props import *   # noqa: F401,F403

NAME, DUR = "s4c", 84.0
S = 290.0
G = 600
FOLDS = [(0.6, 3.4, 7), (4.6, 8.4, 8), (9.6, 12.4, 9), (13.4, 17.4, 10)]
CAPS = [
    (0.0, 1.0, "ton", "(ตะโกน ยังมั่นใจ) เจ็ดแล้ว!"),
    (4.2, 5.4, "chok", "แปด!"), (9.2, 11.0, "chok", "เก้า!"), (13.0, 14.6, "chok", "สิบ!"),
    (17.9, 19.4, "ton", "(เสียงเหวอ) แผนผมพังหมดแล้ว"),
    (20.6, 24.0, "chok", "ต่ออีกครั้งไหวไหม พับสิบเอ็ด!"),
    (30.6, 32.4, "ton", "หยุด!"), (32.5, 35.4, "ton", "อย่าฉีกม้วนลุงโชค!"),
    (38.0, 42.6, "chok", "กระดาษเขาไม่ยอมงอเป็นมุมแหลม เขาต้องอ้อมเป็นวง ก้อนหนาเท่านี้ วงมันกว้างเท่าหมอน"),
    (42.8, 46.2, "chok", "ชั้นนอกสุดต้องอ้อมไกลกว่าชั้นในสุด"),
    (46.8, 50.4, "ton", "ถ้าก้อนหนาขึ้นเท่าตัว วงก็ใหญ่ขึ้นเท่าตัว ชั้นที่ต้องอ้อมก็เยอะขึ้นเท่าตัว"),
    (50.6, 54.6, "ton", "กระดาษที่ต้องใช้ก็… สี่เท่า ครั้งที่สิบเอ็ดต้องสองร้อยเมตรกว่า เรามีร้อยเดียว"),
    (55.0, 56.4, "chok", "(พยักหน้า ช้า) ฟังเข้าท่า"),
    (58.0, 62.0, "ton", "ยาย ถ้าจะพับสี่สิบสองครั้ง กระดาษต้องยาวเท่าไหร่"),
    (62.2, 65.4, "kaew", "ตัวเลขพวกนั้น เอ็งหาเอง ฉันไม่เฉลย"),
    (65.6, 67.0, "ton", "ยาย บอกที"),
    (67.2, 72.6, "kaew", "แสงที่วิ่งเร็วที่สุดในจักรวาล วิ่งตามกระดาษแผ่นนั้น หนึ่งแสนปีกว่า"),
    (77.0, 79.4, "ton", "(เสียงแผ่ว) งั้นพับไม่ได้จริง ๆ"),
    (79.8, 83.6, "kaew", "ซองไม่ได้ถามว่าพับได้ไหม"),
]
CUES = [(1.0, "thump", 0.6), (5.0, "thump", 0.7), (7.0, "thump", 1.0), (10.0, "thump", 0.8), (14.0, "thump", 0.9), (16.2, "thump", 1.0), (17.0, "cheer", 0.6),
        (24.6, "grunt", 0.5), (27.0, "rip", 0.5), (28.4, "boing", 0.9), (29.0, "thump", 0.8), (31.0, "whoosh", 0.6), (33.0, "gasp", 0.5), (37.5, "paper", 0.5),
        (52.0, "scribble", 0.6), (54.0, "ding", 0.6), (68.0, "whoosh", 0.4), (72.2, "gasp", 0.5), (82.0, "ding", 0.4)]
CUES += [(21.0 + 0.5 * k, "grunt", 0.3) for k in range(4)]

STOP_P = dict(R=((-36, 140, 50), (-14, 128, 102)), L=((64, 182, -6), (59, 234, 10)), hands=dict(R=("open", 192), L=("relaxed", 0)), late="R")
KNEEL_P = mk(((-70, 182, 30), (-24, 234, 110)), ((70, 182, 30), (24, 234, 110)))
LENS_P = mk(((-70, 110, 20), (-44, 56, 110)), hr="grip")
LENS_P = dict(LENS_P, grip=dict(side="R", item="lens", tip=(-10, 52, 136)), late="R")


def plank(cv, cx, y, w, d, th, flap_u=0.0, col=PAPER, layers=1, cap=0.0):
    """Folded stack (width w along x, depth d from front to back, thickness th); flap_u > 0: the far half is turning over the near half."""
    x0, x1 = cx - w / 2, cx + w / 2
    dx, dy = d * 0.5, d * 0.45
    half = dy / 2
    if flap_u > 0:
        psi = math.pi * ease(flap_u)
        # near half lies flat; far half rises about the hinge at mid-depth and comes over
        cv.fill([(x0, y), (x1, y), (x1 + dx / 2, y - half), (x0 + dx / 2, y - half)], col, ink=INK, lw=2.0, shade_col=PAPER_SH, depth=2)
        hx0, hx1, hy = x0 + dx / 2, x1 + dx / 2, y - half
        far_y = hy - half * math.cos(psi)
        up = half * 1.8 * math.sin(psi)
        cv.fill([(hx0, hy), (hx1, hy), (hx1 + dx / 2 * math.cos(psi), far_y - up), (hx0 + dx / 2 * math.cos(psi), far_y - up)], PAPER_SH if psi > math.pi / 2 else col,
                ink=INK, lw=2.0)
        cv.fill([(x0, y), (x1, y), (x1, y + th), (x0, y + th)], (214, 212, 202), ink=INK, lw=1.8)
        return
    cv.fill([(x1, y + th), (x1 + dx, y - dy + th), (x1 + dx, y - dy), (x1, y)], (222, 220, 210), ink=INK, lw=2.0)
    cv.fill([(x0, y), (x1, y), (x1 + dx, y - dy), (x0 + dx, y - dy)], col, ink=INK, lw=2.0, shade_col=PAPER_SH, depth=2)
    cv.fill([(x0, y), (x1, y), (x1, y + th), (x0, y + th)], (240, 238, 228), ink=INK, lw=2.0)
    for i in range(1, min(layers, 28)):
        yy = y + th * i / min(layers, 28)
        cv.stroke([(x0 + 2, yy), (x1 - 2, yy)], (206, 204, 194), 1.0)
    if cap > 0:
        n = 14
        for i in range(n):
            xx = x0 + w * (i + 0.5) / n
            lob = cap * (8 + 20 * abs(math.sin(i * 1.7 + 0.6))) * (1 if th > 12 else 0.5)
            cv.fill(spline([(xx - w / n * 0.45, y + th), (xx - w / n * 0.3, y + th + lob), (xx + w / n * 0.3, y + th + lob * 0.9), (xx + w / n * 0.45, y + th)],
                           closed=True, n=3), PAPER if i % 2 else (236, 234, 224), ink=INK, lw=1.4)


def fold_state(t):
    """(length m before the current fold, thickness px, fold progress)."""
    ell = 100 / 2 ** 6                          # 1.5625 m after six folds
    for a, b, n in FOLDS:
        if t >= b:
            ell /= 2
    for a, b, n in FOLDS:
        if a <= t < b:
            return ell, seg(t, a, b)
    return ell, 0.0


def lens_inset(cv, ov, cx, cy, R, u):
    cv.ellipse(cx, cy, R + 12, R + 12, (232, 186, 92), ink=INK, lw=3.4)
    cv.ellipse(cx, cy, R, R, (236, 246, 252), ink=INK, lw=2.4)
    arc = lambda r, f=1.0: [(cx - 20 + r * math.sin(a_ * f), cy - r * math.cos(a_ * f)) for a_ in [j * math.pi / 14 for j in range(0, 15)]]
    nl = 6
    for i in range(nl):
        k = seg(u, 0.05 + 0.1 * i, 0.15 + 0.1 * i)
        if k <= 0:
            continue
        r = 28 + i * 26
        path = [(cx - 190, cy - r), (cx - 20, cy - r)] + arc(r)[1:] + [(cx - 20, cy + r), (cx - 190, cy + r)]
        n_ = max(2, int(len(path) * k))
        cv.stroke(path[:n_], INK, 6)
        cv.stroke(path[:n_], PAPER, 3.6)
    if u > 0.7:
        a = seg(u, 0.7, 0.85)
        cv.stroke(arc(28), STRING, 6, alpha=int(255 * a))
    if u > 0.85:
        cv.stroke(arc(28 + 5 * 26), STRING, 6, alpha=int(255 * seg(u, 0.85, 1.0)))
    cv.stroke([(cx - 140, cy + 150), (cx - 240, cy + 215)], (150, 98, 66), 14)
    cv.stroke([(cx - 140, cy + 150), (cx - 240, cy + 215)], (232, 186, 92), 8)


def draw(cv, t, ov):
    cv.push(0, 0, scale=1.0)
    courtyard(cv, 330, "gold", gate_x=1100, gate_s=0.7, t=t, show_flags=(t < 36))
    PX, PY = 640, 640
    ell, fu = fold_state(t)
    ph = t * 9
    if t < 37.0:
        th_mm = 2 ** 6 * 0.1 * (2 ** sum(1 for a, b, n in FOLDS if t >= b))
        th_px = max(th_mm / 1000 * S, 4.0)
        d_px = ell * S * 1.1
        w_px = 2.0 * S
        cap = 0.0
        if t >= 24.5:
            cap = ease(seg(t, 24.5, 28.0)) * (1 - 0.6 * seg(t, 31.0, 33.0))
        if fu > 0:
            plank(cv, PX, PY, w_px, d_px, th_px, flap_u=fu)
        else:
            plank(cv, PX, PY, w_px, d_px, th_px, layers=int(th_px / 2 + 2), cap=cap)
        # cast around it
        pose_push = lambda: pl(REST, PUSH, 0.5 + 0.5 * math.sin(t * 7))
        if t < 18.2:
            moving = fu > 0
            ex_c = "pant" if t > 8 else "shout"
            actor(cv, "chok", 190, 690, 40, pl(REST, PUSH, 0.5 + 0.5 * math.sin(t * 7)) if t > 1 else REST, ex_c, k=1.1, mouth=max(talk(t, 4.2, 5.4, 1), talk(t, 9.2, 11, 2),
                                                                                                                          talk(t, 13.0, 14.6, 3)), blink_v=blink(t, .4))
            actor(cv, "uean", 1090, 700, 40, pl(REST, PUSH, 0.5 + 0.5 * math.sin(t * 7 + 1)), "pant" if t > 5 else "shout", k=1.05, flip=True,
                  blink_v=blink(t, .2))
            for j, x_ in enumerate((60, 330, 960, 1210)):
                mini(cv, x_, 640 + 12 * (j % 2), 1.6, j + 2, arms="forward", flip=x_ > 640, squash=0.25 if j % 2 else 0, expr="o", moving=False)
        if t < 17.4:
            if 4.6 <= t < 8.4:
                u = seg(t, 4.6, 8.4)
                ty = keys([(4.6, 700), (5.4, 560), (6.0, 330), (6.8, 560), (7.1, 628), (7.4, 618)], t) if t < 7.4 else 618
                tx = keys([(4.6, 330), (6.8, 600)], t) if t < 6.8 else 600
                if t > 7.4:
                    puff(cv, 600, 600, 20, seg(t, 7.2, 8.4))
                actor(cv, "ton", tx, ty, 20, pl(REST, CHEER, seg(t, 4.8, 5.8)), "shout", k=1.25, shadow=False, lean=-6)
            elif 8.4 <= t < 17.4:
                actor(cv, "ton", 600, 618 if t < 13.4 else 600 - 8 * abs(math.sin(t * 7)), 20,
                      pl(CHEER, REST, seg(t, 8.4, 9.2)) if t < 13.4 else CHEER, "pant" if t < 13.4 else "gape", k=1.25, shadow=False)
            else:
                actor(cv, "ton", 330, 700, 40, pl(REST, PUSH, 0.5 + 0.5 * math.sin(t * 7)), "determined", k=1.25, mouth=talk(t, 0.0, 1.0, 4), blink_v=blink(t, .1))
        else:
            # Ton stands on the finished beam (fold 10), then falls into despair; then everyone tries the 11th
            if t < 20.0:
                actor(cv, "ton", 640, 616, 20, pl(CHEER, SLUMP_C, seg(t, 17.6, 19.4)), "gape" if t < 19 else "deadpan", k=1.25, shadow=False,
                      mouth=talk(t, 17.9, 19.4, 4))
                for j, x_ in enumerate((60, 330, 960, 1210)):
                    mini(cv, x_, 640, 1.6, j + 2, arms="cheer", phase=t * 8 + j, moving=False, expr="grin")
                actor(cv, "chok", 190, 690, 40, HIP, "pant", k=1.1, blink_v=blink(t, .4))
                actor(cv, "uean", 1090, 700, 40, CROSS, "pant", k=1.05, flip=True, blink_v=blink(t, .2))
            else:
                # 11th fold attempt 20-31: pushing along the edge, Uean jumps and is thrown off
                push = 0.5 + 0.5 * math.sin(t * 8)
                actor(cv, "chok", 300, 700, 40, pl(REST, PUSH, push), "yikes", k=1.2, lean=10 * push, mouth=talk(t, 20.6, 24.0, 5), blink_v=blink(t, .4))
                for j, x_ in enumerate((430, 520, 760, 850)):
                    mini(cv, x_, 700, 1.6, j + 4, arms="forward", flip=x_ > 640, moving=False, expr="o", squash=0.15 * push)
                if t < 25.4:
                    actor(cv, "uean", 1000, 700, 40, pl(REST, PUSH, push), "shout", k=1.15, flip=True, lean=8 * push)
                else:
                    ut = seg(t, 25.4, 29.0)
                    ux = keys([(25.4, 1000), (27.0, 700), (29.0, 520)], t)
                    uy = keys([(25.4, 700), (26.4, 480), (27.2, 440), (28.4, 190), (29.0, 700)], t) if t < 29.0 else 700
                    actor(cv, "uean", ux, uy, 40, ARMS_UP_C2, "gape", k=1.15, flip=True, lean=-18 + 30 * ut, shadow=False)
                    if 26.8 < t < 27.8:
                        puff(cv, 700, 630, 22, seg(t, 26.8, 27.8))
                if 29.0 <= t < 31.0:
                    puff(cv, 520, 700, 24, seg(t, 29.0, 31.0))
                if t >= 30.0:
                    actor(cv, "ton", 1000, 705, 40, pl(HEADS, STOP_P, seg(t, 30.4, 31.0)) if t < 36 else STOP_P, "shout", k=1.3, flip=True, mouth=max(talk(t, 30.6, 32.4, 6), talk(t, 32.5, 35.4, 7)))
                else:
                    actor(cv, "ton", 1000, 705, 40, HEADS, "gape", k=1.3, flip=True)
    else:
        # the explanation: Ton kneels by the beam with the lens inset; then the calculation; then Kaew's answer
        u_l = seg(t, 37.4, 47.0)
        if t < 56.5:
            lens_inset(cv, ov, 620, 270, 220, u_l)
            plank(cv, 1000, 690, 380, 120, 29, layers=30)
            actor(cv, "ton", 230, 720, 20, LENS_P, "aha" if t > 46 else "think", k=1.2, lean=8, mouth=talk(t, 46.8, 54.6, 8), blink_v=blink(t, .1))
            actor(cv, "chok", 1130, 715, 40, SHRUG if 42.8 < t < 46.2 else (HIP if t > 55 else REST), "think" if t < 55 else "smug", k=0.9, flip=True,
                  mouth=talk(t, 38.0, 46.2, 9), blink_v=blink(t, .4))
            if 50.6 < t < 56:
                ov.append(("× 4", 960, 440, 72, (255, 224, 120), seg(t, 51.0, 51.8) * (1 - seg(t, 55.0, 56.0))))
        else:
            if t < 73.0:
                band(cv, -200, 330, (138, 200, 236), (255, 236, 196), 14)
                rect(cv, -300, 330, W + 300, 900, (212, 184, 138), ink=None)
                actor(cv, "ton", 330, 700, 20, THINK if t > 68 else REST, "plead" if 65.6 < t < 67 else "think", k=1.25, mouth=max(talk(t, 58.0, 62.0, 8), talk(t, 65.6, 67.0, 9)),
                      blink_v=blink(t, .1))
                kx = keys([(56.0, 1500), (58.0, 920)], t)
                if t < 58.0:
                    phk = walk_ph(t, 5.5)
                    actor(cv, "kaew", kx, 705, 45, walk_pose(phk), "smug", k=1.15, flip=True, walk=dict(phase=phk, stride=12, lift=9))
                else:
                    actor(cv, "kaew", 920, 705, 45, pl(REST, POINT_UP, seg(t, 66.2, 67.0)) if 66 < t < 73 else REST, "gloat", k=1.15, flip=True,
                          mouth=max(talk(t, 62.2, 65.4, 10), talk(t, 67.2, 72.6, 11)), blink_v=blink(t, .7))
                if 67.0 < t < 73.0:
                    # a hair-thin line of paper streaks up and away past the Moon and the stars
                    a = seg(t, 67.4, 72.8)
                    moon(cv, 1100, 120, 36, 0.5)
                    cv.stroke([(640, 700), (640 + 360 * a, 700 - 800 * a)], PAPER, 4)
                    cv.stroke([(640, 700), (640 + 360 * a, 700 - 800 * a)], INK, 1.2)
            else:
                # evening: sky dark with stars; the line goes on beyond the frame; Ton deflates, Kaew twirls the envelope
                courtyard(cv, 330, "dusk", gate_x=1100, gate_s=0.7, t=t, show_flags=False)
                a = seg(t, 73.0, 76.0)
                rnd = random.Random(5)
                for _ in range(26):
                    cv.ellipse(rnd.uniform(0, W), rnd.uniform(10, 280), 2, 2, (255, 255, 235), ink=None, alpha=int(200 * a))
                cv.stroke([(640, 700), (1000, -100)], PAPER, 4)
                actor(cv, "ton", 400, 710, 20, SLUMP_C, "deadpan", k=1.25, mouth=talk(t, 77.0, 79.4, 8), blink_v=blink(t, .1), lean=4)
                spin = math.sin(t * 5) * 18
                actor(cv, "kaew", 880, 710, 45, mk(((-70, 130, 30), (-40, 100, 90))), "gloat", k=1.15, flip=True, mouth=talk(t, 79.8, 83.6, 11), blink_v=blink(t, .7))
                envelope(cv, 790, 520, 70, spin)
    cv.pop()


SLUMP_C = mk(((-60, 190, -10), (-52, 240, 0)), ((60, 190, -10), (52, 240, 0)))
ARMS_UP_C2 = mk(((-84, 90, 0), (-60, 22, 20)), ((84, 90, 0), (60, 22, 20)))
import random  # noqa: E402
