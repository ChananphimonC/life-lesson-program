"""Robot world, scene 5: Chok remembers the ATM (sepia memory): tellers did not vanish at once because cheaper branches multiplied; the phone app came later."""
from rw_common import *  # noqa: F401,F403
import rw_common as _rc

NAME, I = "rw5", 5
DUR = scene_dur(I)
CAPS = []
MARK = ["เย็นนั้น", "แต่ข้อมูลในอเมริกา", "ธนาคารเลยเปิดสาขา", "สิ่งที่ทำให้ลดจริง", "ตัวเลขที่รายงานกันต่อ", "ต้นสรุปว่า"]
B = beats(I, MARK)
BE = B + [DUR - TAIL]
CUES = [(B[0] + 5.0, "thump", 0.5), (B[0] + 6.0, "ding", 0.5), (B[1] + 1.0, "buzz", 0.3), (B[2] + 1.0, "pop", 0.5), (B[2] + 2.0, "pop", 0.5), (B[2] + 3.0, "pop", 0.5),
        (B[2] + 4.0, "pop", 0.5), (B[3] + 2.0, "chime", 0.6), (B[4] + 1.0, "beep", 0.4), (B[4] + 6.0, "beep", 0.4), (B[5] + 2.0, "sigh", 0.4)]


def teller(cv, x, y, i=0, worried=0.0, s=1.5):
    rect(cv, x - 40, y - 20, x + 40, y + 24, (186, 150, 108), lw=2.0)
    mini(cv, x, y + 10, s * 0.9, i, arms="swing", phase=_rc._T[0] * (5 if worried > 0.5 else 2) + i, squash=0.04 * math.sin(_rc._T[0] * 2 + i), expr="o" if worried > 0.5 else "grin")


def draw(cv, t, ov):
    cv.push(0, 0, scale=1.0)
    tick(t)
    k = which(t, B)
    ph = walk_ph(t, 6.0)
    if k <= 1:
        bank(cv, t)
        # tellers behind the window, a queue in front
        for j, x in enumerate((620, 780, 940, 1100)):
            teller(cv, x, 330, j, worried=1.0 if k == 1 else 0.0)
        for j in range(3):
            mini(cv, 380 + j * 90, 650, 1.6, j + 2, arms="swing", phase=t * 2 + j, squash=0.03 * math.sin(t * 2 + j), moving=False)
        # the ATM rolls in on a little cart
        ax = keys([(B[0] + 3.0, -200), (B[0] + 6.0, 210)], t)
        atm(cv, ax, 640, 1.5, t, use=0.0)
        if t > B[0] + 6.0:
            burst(cv, 210, 470, seg(t, B[0] + 6.0, B[0] + 7.4), 8, 30, 90, (255, 235, 140))
        if k == 1:
            for j, x in enumerate((620, 780, 940, 1100)):
                cross_mark(cv, x, 250, 0.9, a=ease(seg(t, B[1] + 0.8 + j * 0.3, B[1] + 1.2 + j * 0.3)) * (1 - ease(seg(t, B[1] + 6.0, B[1] + 6.8))))
        chok(cv, 1130, 700, THINK, "think", k=1.0, flip=True, blink_v=blink(t, .4))
    elif k == 2:
        rect(cv, 0, 0, W, 470, (240, 230, 208), ink=None)
        rect(cv, 0, 470, W, H, (196, 176, 148), ink=None)
        rect(cv, 0, 466, W, 478, (170, 150, 124), ink=None)
        n = int(1 + 6 * ease(seg(t, B[2] + 0.6, B[2] + 5.4)))
        for j in range(n):
            u = ease(seg(t, B[2] + 0.6 + j * 0.8, B[2] + 1.4 + j * 0.8))
            bank_building(cv, 130 + j * 170, 470, 1.6, pop=u)
            mini(cv, 130 + j * 170, 560, 1.3, j, arms="down")
            atm(cv, 130 + j * 170 + 70, 600, 0.5, t) if u > 0.9 else None
        chok(cv, 1130, 700, SPREAD if t > B[2] + 3 else REST, "eager", k=1.0, flip=True, blink_v=blink(t, .4))
    elif k == 3:
        bank(cv, t)
        # the phone: a big phone with a bank app; the queue leaves into it, the window empties
        u = ease(seg(t, B[3] + 1.5, B[3] + 5.0))
        for j, x in enumerate((620, 780, 940, 1100)):
            if u < 0.25 * (j + 1):
                teller(cv, x, 330, j)
        for j in range(3):
            xx = 380 + j * 90 + 260 * u
            if u < 0.9:
                mini(cv, xx, 650, 1.6, j + 2, arms="down", moving=u > 0.05 and u < 0.9, phase=t * 8 + j, flip=False)
        rrect(cv, 1010, 380, 1160, 640, 22, (56, 62, 84), lw=3.0)
        rect(cv, 1022, 404, 1148, 614, (90, 170, 220), ink=None)
        bank_building(cv, 1085, 520, 1.4, pop=1.0)
        coin(cv, 1085, 440, 16)
        chok(cv, 200, 700, REST, "think", k=1.0, blink_v=blink(t, .4))
    else:
        rect(cv, 0, 0, W, H, (240, 230, 208), ink=None)
        # two blocks of people: 560 -> 360 (each tile = ten thousand people)
        a = ease(seg(t, B[4] + 0.5, B[4] + 2.5))
        b = ease(seg(t, B[4] + 3.5, B[4] + 6.0))
        for side, (cx, n, col) in enumerate(((330, 56, (96, 150, 200)), (900, 36, (236, 130, 96)))):
            vis = a if side == 0 else b
            for i in range(n):
                if i / n > vis:
                    break
                r, c = divmod(i, 8)
                x, y = cx - 150 + c * 40, 150 + r * 56 + 2.4 * math.sin(t * 3 + i * 0.4)
                cv.ellipse(x, y - 8, 9, 9, col, ink=INK, lw=1.3)
                cv.fill(spline([(x - 11, y + 12), (x - 8, y), (x + 8, y), (x + 11, y + 12)], closed=True, n=3), col, ink=INK, lw=1.3)
        ov.append(("560,000", 330, 470, 54, (60, 90, 150), a))
        ov.append(("360,000", 900, 470, 54, (190, 80, 50), b))
        arrow(cv, 620, 280, 70, False, (150, 150, 160), 18, alpha=int(255 * b)) if False else None
        cv.fill([(590, 300), (680, 300), (680, 280), (730, 330), (680, 380), (680, 360), (590, 360)], (170, 160, 150), ink=INK, lw=2.4, alpha=int(255 * b))
        if k == 5:
            ton(cv, 90, 710, REST, "think", k=0.9, blink_v=blink(t, .2))
            chok(cv, 1190, 710, SHRUG, "plead", k=0.9, flip=True, blink_v=blink(t, .4))
    # sepia memory wash while Chok remembers (not at the end)
    if k <= 3:
        cv.fill([(0, 0), (W, 0), (W, H), (0, H)], (150, 110, 60), ink=None, alpha=52)
    pulse_ov(ov, t)
    cv.pop()
