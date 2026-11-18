"""Robot world, scene 4: the numbers. A data wall of 100 little people: WEF (new vs displaced, an employer forecast), IMF (exposed is not lost), ILO for Thailand."""
from rw_common import *  # noqa: F401,F403

NAME, I = "rw4", 4
DUR = scene_dur(I)
CAPS = []
MARK = ["ต้นพาลุงโชค", "ลุงโชคนับนิ้ว", "แต่อย่าเพิ่งดีใจ", "ส่วนไอเอ็มเอฟ", "แต่ต้นบอกว่า", "ลุงถามว่า แล้วบ้านเรา", "กลุ่มเสี่ยงสูงสุด"]
B = beats(I, MARK)
BE = B + [DUR - TAIL]
CUES = [(B[0] + 4.0, "swoosh_up", 0.4), (B[0] + 7.0, "swoosh_up", 0.4), (B[1] + 1.0, "beep", 0.4), (B[1] + 3.0, "beep", 0.4), (B[3] + 1.5, "chime", 0.5),
        (B[5] + 1.5, "chime", 0.5), (B[6] + 1.5, "beep", 0.5)]


def wall(cv, t=0.0):
    rect(cv, 0, 0, W, H, (34, 44, 82), ink=None)
    ambient(cv, t, 34, (130, 170, 240))
    rrect(cv, 380, 40, 1240, 560, 26, (46, 60, 108), lw=3.0)
    cv.fill([(0, 600), (W, 600), (W, H), (0, H)], (28, 36, 68), ink=None)


def grid_pts(cols=10, rows=10, x0=520, y0=110, step=50):
    return x0, y0, step


def people(cv, t, new=0, gone=0, hi=0, hi_col=(255, 196, 80), deep=0, reveal=1.0, x0=470, y0=120, step=44):
    """100 people. gone (red) first, new (green) last; hi (amber) = a set 'touched by AI'; deep (dark red) = the highest-risk few inside hi."""
    for i in range(100):
        if i / 100 > reveal:
            break
        r, c = divmod(i, 10)
        x, y = x0 + c * step * 1.3, y0 + r * step + 2.6 * math.sin(t * 3.2 + i * 0.37)
        col = (176, 188, 208)
        if gone and i < gone:
            col = (236, 96, 88)
        elif new and i >= 100 - new:
            col = (96, 196, 132)
        elif hi and i < hi:
            col = hi_col
        if deep and i < deep:
            col = (214, 56, 70)
        pr = 1.0 + (0.14 * math.sin(t * 4 + i * 0.5) if col != (176, 188, 208) else 0.0)
        cv.ellipse(x, y - 10, 9 * pr, 9 * pr, col, ink=INK, lw=1.4)
        cv.fill(spline([(x - 12, y + 14), (x - 9, y), (x + 9, y), (x + 12, y + 14)], closed=True, n=3), col, ink=INK, lw=1.4)


def draw(cv, t, ov):
    cv.push(0, 0, scale=1.0)
    tick(t)
    k = which(t, B)
    wall(cv, t)
    ph = t * 2
    if k == 0:
        # two growing bars: 170 up, 92 down (the employers' forecast for 2030)
        g = ease(seg(t, B[0] + 3.5, B[0] + 8.0))
        r = ease(seg(t, B[0] + 6.5, B[0] + 10.0))
        rect(cv, 520, 520 - 360 * g, 760, 520, (96, 196, 132), lw=3.0)
        rect(cv, 860, 520 - 360 * r * 92 / 170, 1100, 520, (236, 96, 88), lw=3.0)
        arrow(cv, 640, 520 - 360 * g - 24, 56, True, (96, 196, 132), 16)
        arrow(cv, 980, 520 - 360 * r * 92 / 170 - 70, 56, False, (236, 96, 88), 16)
        ov.append(("170", 640, 580, 56, (170, 240, 190), g))
        ov.append(("92", 980, 580, 56, (255, 170, 160), r))
        crystal_ball(cv, 1170, 110, 0.9, t)
    else:
        if k == 1:
            u = ease(seg(t, B[1], B[1] + 4.0))
            people(cv, t, new=14, gone=8, reveal=u)
            ov.append(("14", 1090, 170, 70, (170, 240, 190), ease(seg(t, B[1] + 2.0, B[1] + 3.0))))
            ov.append(("8", 1090, 290, 70, (255, 170, 160), ease(seg(t, B[1] + 3.0, B[1] + 4.0))))
        elif k == 2:
            people(cv, t, new=14, gone=8)
            dashed_rect(cv, 440, 80, 1140, 560, (255, 214, 110), 4.0, alpha=int(255 * ease(seg(t, B[2], B[2] + 1.0))))
            crystal_ball(cv, 1170, 110, 0.9, t)
        elif k == 3:
            people(cv, t, hi=40, reveal=1.0)
            ov.append(("40%", 1130, 170, 80, (255, 220, 120), ease(seg(t, B[3] + 1.0, B[3] + 2.0))))
        elif k == 4:
            people(cv, t, hi=40)
            u = t - B[4]
            for j in range(4):
                x, y = 470 + (j % 2) * 130, 120 + (j // 2) * 44
            arrow(cv, 1130, 330, 60, True, (96, 196, 132), 14, alpha=int(255 * ease(seg(u, 1.0, 2.0))))
            coin(cv, 1130, 190, 18)
            arrow(cv, 1130, 220, 40, False, (236, 96, 88), 12, alpha=int(255 * ease(seg(u, 2.0, 3.0))))
        elif k == 5:
            people(cv, t, hi=21, hi_col=(255, 196, 80))
            ov.append(("20%", 1130, 170, 80, (255, 220, 120), ease(seg(t, B[5] + 1.0, B[5] + 2.0))))
        else:
            people(cv, t, hi=21, hi_col=(255, 196, 80), deep=int(4 * ease(seg(t, B[6] + 0.5, B[6] + 2.0))))
            rect(cv, 1070, 290, 1120, 340, (252, 250, 244), lw=2.4)
            for j in range(3):
                cv.stroke([(1078, 302 + j * 12), (1112, 302 + j * 12)], (170, 170, 190), 3)
            ov.append(("3-4%", 1140, 230, 70, (255, 160, 160), ease(seg(t, B[6] + 0.5, B[6] + 2.0))))
    # the two of them at the wall: Chok asks, Ton reads, Chok panics and relaxes
    asking = in_(t, BE, 0, 0.12, 0.35) or in_(t, BE, 5, 0.0, 0.2)
    sweat = k == 3 and fr(t, BE, 3, 0.35, 1.0) > 0
    relief = k == 6 and fr(t, BE, 6, 0.55, 1.0) > 0
    ton(cv, 170, 690, POINT_FWD if k in (0, 1, 3, 5) else (STOP if k == 2 else REST), "determined" if k != 2 else "shout", th=40, k=1.0,
        mouth=mouth_of(t, BE[0] + 6.0, BE[1] - 0.5, 4) if k == 0 and t > B[0] + 6.0 else (mouth_of(t, BE[4] + 0.2, BE[5] - 0.5, 5) if k == 4 else 0))
    chok(cv, 300, 690, (HEADS if sweat and not relief else (SPREAD if relief else (SHRUG if k == 4 else CROSS))),
         "yikes" if sweat and not relief else ("happy" if relief else ("plead" if asking else "deadpan")), th=40, k=0.95,
         mouth=mouth_of(t, BE[0] + 2.0, BE[0] + 5.0, 6) if k == 0 and t < B[0] + 5.5 else (mouth_of(t, BE[5], BE[5] + 2.5, 7) if k == 5 else 0))
    pulse_ov(ov, t)
    cv.pop()
