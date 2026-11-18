"""Red thread, scene 6 (v2): the thread is longer than we think: a Thai woman and an American man who met on a dating app (night here, morning there; he flies over),
a couple of different faiths who sit down to tea, the threads across the map, and a thread that stretches, tangles and ties itself in a knot but never breaks."""
from rt_common import *  # noqa: F401,F403

NAME, I = "rt6", 6
DUR = scene_dur(I)
CAPS = []
MARK = ["ด้ายแดงยาวกว่าที่เราคิดเสมอ", "คู่หนึ่งเป็นสาวไทย", "จนวันหนึ่งเขาซื้อตั๋วบินมาหา", "อีกคู่นับถือศาสนาต่างกัน", "แต่พอได้นั่งดื่มชาคุยกัน", "ฟังดูเหมือนด้ายเส้นเดียวกัน", "ว่ากันว่าด้ายเส้นนี้ยืดได้"]
B = beats(I, MARK)
BE = B + [DUR - TAIL]
CUES = [(B[0] + 2.0, "whoosh", 0.4), (B[1] + 3.0, "beep", 0.4), (B[1] + 7.0, "ding", 0.4), (B[2] + 2.0, "whoosh", 0.4), (B[3] + 2.0, "sigh", 0.4), (B[4] + 3.0, "clink", 0.5), (B[4] + 6.0, "chime", 0.5),
        (B[5] + 3.0, "whoosh", 0.4), (B[6] + 4.0, "boing", 0.4), (B[6] + 8.0, "ding", 0.5)]


def arc(cv, a, b, u, t, lift=300, alpha=255):
    """A long thread arching from a to b (drawn on from a, u 0..1) with a spark running along it."""
    pts = []
    n = 60
    for i in range(int(n * max(0.02, min(1.0, u))) + 1):
        f = i / n
        x = a[0] + (b[0] - a[0]) * f
        y = a[1] + (b[1] - a[1]) * f - lift * math.sin(math.pi * f) + 4 * math.sin(t * 2.4 + f * 9)
        pts.append((x, y))
    if len(pts) > 2:
        sp = spline(pts, n=2)
        cv.stroke(sp, RED_GLOW, 11, alpha=int(60 * alpha / 255))
        cv.stroke(sp, RED, 4, alpha=alpha)
        x, y = pts[int((t * 18) % len(pts))]
        cv.ellipse(x, y, 4, 4, (255, 240, 240), ink=None, alpha=int(200 * alpha / 255))
    return pts


def draw(cv, t, ov):
    cv.push(0, 0, scale=1.0)
    tick(t)
    k = which(t, B)
    ph = walk_ph(t, 6.0)
    if k == 0:
        world_threads(cv, t)
        u = ease(fr(t, BE, 0, 0.1, 0.8))
        a, b = (120, 520), (1160, 520)
        arc(cv, a, b, u, t, 360)
        heart(cv, 120, 500, 20, PINK, glow=1.0, lw=2.0)
        heart(cv, 1160, 500, 20, PINK, glow=1.0 * ease(fr(t, BE, 0, 0.75, 0.9)), alpha=int(255 * ease(fr(t, BE, 0, 0.7, 0.85))), lw=2.0)
    elif k == 1:
        split_world(cv, t)
        # night in Thailand, morning in America: two people, one phone chat in the middle
        st(cv, "faa", 250, 700, pose=REST, ex="happy", th=35, k=1.05, seed=1)
        st(cv, "jake", 1030, 700, pose=REST, ex="laugh", th=35, flip=True, k=1.0, seed=2)
        local = t - B[1]
        phone(cv, 640, 400, 0.95, [("L", 0.7, 1.0, 0), ("R", 0.9, 3.0, 0), ("L", 0.6, 5.0, 0), ("R", 0.8, 7.0, 1), ("L", 0.9, 9.0, 1)], local, glow=False)
        tie(cv, "faa", "jake", t, sag=-150)
    elif k == 2:
        airport(cv, t)
        # he lands (+x) with his suitcase and walks over to her; the thread is already round both little fingers
        w = ease(fr(t, BE, 2, 0.05, 0.62))
        jx = 140 + 520 * w
        walking = 0.01 < w < 0.99
        st(cv, "faa", 800, 690, pose=REST, ex="gape" if w < 0.9 else "laugh", th=35, flip=True, k=1.0, seed=1)
        st(cv, "jake", jx, 690, pose=walk_pose(ph) if walking else REST, ex="happy", th=60 if walking else 35, k=1.0, seed=2, walk=dict(phase=ph, stride=16, lift=12) if walking else None)
        suitcase(cv, jx - 74, 690, 1.0)
        tie(cv, "jake", "faa", t, sag=36)
        if w > 0.9:
            for j in range(5):
                u = (t * 0.5 + j * 0.2) % 1.0
                heart(cv, 640 + (j - 2) * 40, 440 - 120 * u, 12, PINK, alpha=int(220 * math.sin(math.pi * u)), lw=1.4)
    elif k in (3, 4):
        # a pretty tea pavilion: the two stand behind a low table, worried at first; when they sit down and talk everything softens and they clink their cups
        tea_garden(cv, t)
        calm = k == 4
        u = ease(fr(t, BE, 4, 0.18, 0.55)) if calm else 0.0
        MX, OX, K, FY = 440, 840, 1.32, 730
        cup_m = (560 + 70 * u, 612 - 118 * u)
        cup_o = (720 - 70 * u, 612 - 118 * u)
        pm = reach("mariam", MX, FY, 25, K, {"L": (cup_m[0], cup_m[1] - 14) if calm else (632, 604), "R": (MX - 56, 608)}, kinds=("relaxed", "relaxed"), z=90)
        po = reach("omar", OX, FY, 25, K, {"L": (cup_o[0], cup_o[1] - 14) if calm else (676, 604), "R": (OX + 56, 608)}, kinds=("relaxed", "relaxed"), z=90, flip=True)
        st(cv, "mariam", MX, FY, pose=pm, ex="happy" if calm else "worried", th=25, k=K, seed=1, hide_arms=True)
        st(cv, "omar", OX, FY, pose=po, ex="happy" if calm else "worried", th=25, flip=True, k=K, seed=2, hide_arms=True)
        tea_table(cv, 360, 940, 614)
        teapot(cv, 650, 614, 1.0)
        sweets(cv, 650, 620, 0.95)
        if not calm:
            teacup(cv, 560, 616, 1.0, steam=1.0, t=t)
            teacup(cv, 720, 616, 1.0, steam=1.0, t=t)
        seated_front(cv, "mariam", MX, FY, pm, th=25, k=K)
        seated_front(cv, "omar", OX, FY, po, th=25, k=K, flip=True)
        if calm:
            teacup(cv, cup_m[0], cup_m[1] + 18, 1.0, steam=1.0, t=t)
            teacup(cv, cup_o[0], cup_o[1] + 18, 1.0, steam=1.0, t=t)
            if u > 0.95:                                         # the clink
                a = (t * 2.0) % 1.0
                for j in range(6):
                    ang = j * math.pi / 3 + 0.4
                    r = 18 + 26 * a
                    cv.ellipse(642 + math.cos(ang) * r, 478 + math.sin(ang) * r, 3.6 * (1 - a * 0.5), 3.6 * (1 - a * 0.5), (255, 244, 190), ink=None, alpha=int(255 * (1 - a)))
            for j in range(7):                                   # hearts drift up in the gap between the two of them
                v = (t * 0.28 + j * 0.143) % 1.0
                heart(cv, 590 + (j % 3) * 46 + 8 * math.sin(t * 2 + j), 470 - 250 * v, 13, PINK, alpha=int(230 * math.sin(math.pi * v)), lw=1.4)
        else:
            # two worried thought bubbles, one over each of them
            for bx, bs in ((410, 1), (880, -1)):
                bubble(cv, bx, 250, 160, 96, tail=(60 * bs, 70))
                for j in range(3):
                    cv.ellipse(bx - 30 + j * 30, 250, 6, 6, (130, 130, 150), ink=None)
        tie(cv, "mariam", "omar", t, sag=22)
    elif k == 5:
        world_threads(cv, t)
        # three couples, three long threads over the map: all one colour, all one thread
        for j, (a, b, lift) in enumerate((((120, 540), (1160, 540), 400), ((200, 520), (980, 520), 300), ((330, 500), (1180, 500), 220))):
            u = ease(fr(t, BE, 5, 0.08 + 0.22 * j, 0.55 + 0.22 * j))
            arc(cv, a, b, u, t + j, lift)
            heart(cv, a[0], a[1] - 18, 14, PINK, glow=0.8, lw=1.8)
            heart(cv, b[0], b[1] - 18, 14, PINK, glow=0.8 * u, alpha=int(255 * u), lw=1.8)
    else:
        band(cv, 0, H, (254, 246, 238), (248, 230, 222), n=12, x0=0, x1=W)
        ambient(cv, t, 20, (255, 200, 210), seed=7)
        # the thread between two hands stretches far, tangles and ties a knot, but never breaks
        stretch = 0.5 + 0.5 * math.sin(t * 0.9)
        d = 250 + 120 * stretch
        lx, rx = 640 - d, 640 + d
        yb = 560
        a = hand_pinky(cv, lx - 40, yb, 1.1, flip=False, hook=1.0, sleeve_len=60)
        b = hand_pinky(cv, rx + 40, yb, 1.1, flip=True, hook=1.0, sleeve_len=60)
        a = (lx - 40 + 40 * 1.1, yb - 130 * 1.1)
        b = (rx + 40 - 40 * 1.1, yb - 130 * 1.1)
        ring(cv, a, 1.3)
        ring(cv, b, 1.3)
        link(cv, (a[0] + 6, a[1]), (b[0] - 6, b[1]), t, sag=70 - 60 * stretch, tie=False, w=4.0)
        knot(cv, 640, a[1] + 30 + (70 - 60 * stretch) * 0.6, 1.1 + 0.3 * math.sin(t * 2))
    cv.pop()
    pulse_ov(ov, t)
