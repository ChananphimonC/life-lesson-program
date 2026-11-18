"""Scene 6 - the festival kitchen (script: ฉาก 6). Aunt Uean brings the bowls in doubling groups 1, 2, 4 ... 128 (255 in all); the high shot shows
the eight full crates and the ninth holding 155 of 256 slots (101 empty); Ton pleads, Uean answers "ล้าง", Uncle Chok arrives with bamboo. ~72 s."""
from acting import *  # noqa: F401,F403
from props import *   # noqa: F401,F403

NAME, DUR = "s6", 72.0
CAPS = [
    (20.0, 21.6, "ton", "ป้า… นี่มัน"),
    (21.8, 22.8, "uean", "(ไม่มองหน้า) ล้าง"),
    (47.0, 51.5, "ton", "ป้า ถ้าผมพับชามได้สี่สิบสองครั้ง…"),
    (51.8, 52.8, "uean", "ล้าง"),
    (58.0, 61.0, "chok", "ล้างเสร็จมาหาผม"),
]

# deliveries: (arrival time, destination x, destination y (base), bowls in the tower, carrier, group id)
EV = [(3.0, 420, 466, 1, "uean", 1), (6.8, 500, 466, 2, "uean", 2), (10.4, 575, 466, 4, "uean", 4), (14.0, 660, 466, 8, "uean", 8),
      (17.4, 750, 466, 8, 0, 16), (18.4, 810, 466, 8, 1, 16)]
EV += [(21.0 + 0.8 * i, 890 + 62 * i, 466, 8, i, 32) for i in range(4)]
EV += [(25.0 + 0.45 * i, 380 + 78 * i, 636, 8, i + 4, 64) for i in range(8)]
EV += [(29.0 + 0.45 * i, 140 + 140 * i, 712, 16, i + 8, 128) for i in range(8)]
CUES = [(e[0], "clink", 0.5 if e[3] < 8 else 0.7) for e in EV] + [(e[0] - 1.6 + 0.4 * k, "step", 0.22) for e in EV[:6] for k in range(4)] + [
    (21.0, "gasp", 0.5), (22.0, "thump", 0.5), (34.0, "pop", 0.4), (40.0, "ding", 0.5), (47.0, "plead", 0.0), (56.0, "step", 0.3), (56.5, "step", 0.3),
    (57.0, "step", 0.3), (57.5, "step", 0.3), (62.0, "bamboo", 0.7), (66.0, "water", 0.5)]
CUES += [(34.2 + 0.1 * k, "pop", 0.35) for k in range(0, 100, 7)]


def stool(cv, x, y):
    """A 2 m x 10 cm paper beam used as a low step (to scale at this zoom: 221 px per metre)."""
    w, h = 440, 24
    cv.fill([(x - w / 2, y), (x + w / 2, y), (x + w / 2 + 10, y - 14), (x - w / 2 + 10, y - 14)], PAPER, ink=INK, lw=2.0, shade_col=PAPER_SH)
    rect(cv, x - w / 2, y, x + w / 2, y + h, (240, 238, 228), lw=2.0)
    for k in range(1, 6):
        cv.stroke([(x - w / 2 + 2, y + h * k / 6), (x + w / 2 - 2, y + h * k / 6)], (206, 204, 194), 1.0)


def tower_at(cv, x, y, n, t, wob=0.0):
    w = 40 if n < 16 else 46
    bowl_tower(cv, x, y, w, n, wob=wob, t=t)


def placed_and_carried(cv, t, ov):
    """Draw every delivered tower (static, with a landing bounce) and every tower currently being carried in."""
    carried = []
    for (ta, dx, dy, n, carrier, g) in EV:
        walk = 2.3 if carrier == "uean" else 1.9
        if t >= ta:
            bounce = 5 * math.exp(-(t - ta) * 5) * math.sin((t - ta) * 24) if t - ta < 0.8 else 0
            if n == 1:
                bowl_side(cv, dx, dy + bounce, 44)
            else:
                tower_at(cv, dx, dy + bounce, n, t, wob=1.2 if t > ta + 3 and n >= 8 else 0)
        elif t >= ta - walk:
            u = seg(t, ta - walk, ta)
            x_start = 1360 if dy < 600 else 1400
            carried.append((u, x_start, dx, dy, n, carrier, g))
    return carried


def draw_carried(cv, t, carried):
    for (u, xs, xd, yd, n, carrier, g) in carried:
        x = lerp(xs, xd, u)
        ph = t * 9 + (carrier if isinstance(carrier, int) else 0)
        if carrier == "uean":
            actor(cv, "uean", x, 700, 20, mk(((-70, 110, 20), (-46, 50, 80)), ((70, 110, 20), (46, 50, 80))), "smug", k=1.0, flip=True,
                  walk=dict(phase=ph, stride=18, lift=14))
            wx = x
            tower_at(cv, wx, 700 - 275 * 1.0, n, t)
        else:
            mini(cv, x, 640 + (carrier % 3) * 10, 1.7, carrier + 3, arms="up", moving=True, phase=ph, flip=True, expr="o")
            tower_at(cv, x, 640 + (carrier % 3) * 10 - 150, n, t, wob=3.0)


def kitchen_view(cv, t, ov):
    kitchen(cv, t)
    counter(cv, 470)
    sink(cv, 215, 470, 300, t=t)
    carried = placed_and_carried(cv, t, ov)
    draw_carried(cv, t, carried)
    # Ton on the paper beam at the sink, scrubbing; his expression follows what he sees
    ph = math.sin(t * 7) * 0.5 + 0.5
    scrub = pl(SCRUB, mk(((-70, 150, 24), (-30, 160, 96)), ((70, 150, 24), (30, 140, 80))), ph)
    n_done = sum(1 for e in EV if t >= e[0])
    ex_t = "deadpan" if t < 9 else ("yikes" if t < 17 else ("gape" if t < 28 else "pant"))
    if 20.0 < t < 21.6:
        ex_t = "plead"
    stool(cv, 215, 700)
    actor(cv, "ton", 215, 690, 25, scrub, ex_t, k=1.15, mouth=talk(t, 20.0, 21.6, 3), blink_v=blink(t, .1), lean=3 * ph)
    # Uean between deliveries
    if not any(c[5] == "uean" for c in carried):
        ux = 1130 if t < 30 else 1130
        pose = HIP if t > 21 else REST
        if 21.8 < t < 22.8:
            pose = pl(HIP, LADLE_POINT, seg(t, 21.8, 22.3))
        actor(cv, "uean", ux, 700, 20, pose, "gloat", k=1.0, flip=True, mouth=talk(t, 21.8, 22.8, 4), blink_v=blink(t, .2))


def crates_view(cv, t, ov, u):
    kitchen(cv, t)
    cv.fill([(0, 150), (W, 150), (W, H), (0, H)], (150, 112, 82), ink=None)
    s = 18
    seq = [(1, 1, 1), (2, 1, 2), (2, 2, 4), (4, 2, 8), (4, 4, 16), (8, 4, 32), (8, 8, 64)]
    x = 26
    for idx, (cols, rows, n) in enumerate(seq):
        a = seg(u, 0.03 * idx, 0.03 * idx + 0.08)
        if a > 0:
            w, h = crate(cv, x, 175, cols, rows, int(n * a))
        else:
            w = cols * s
        x += w + 28
    a128 = seg(u, 0.22, 0.34)
    if a128 > 0:
        crate(cv, 26, 330, 16, 8, int(128 * a128))
    a9 = seg(u, 0.38, 0.92)
    nine = int(155 * a9)
    pop = (nine, (a9 * 155) % 1.0) if a9 < 1 else None
    if a9 > 0:
        crate(cv, 400, 330, 16, 16, nine, pop=pop, dashed=True)
    return a9


def final_view(cv, t, ov):
    kitchen(cv, t)
    counter(cv, 520)
    sink(cv, 500, 520, 420, moon_on=True, t=t)
    for i in range(8):
        bowl_tower(cv, 790 + i * 56, 516, 36, 8)
    stool(cv, 500, 690)
    ph = math.sin(t * 7) * 0.5 + 0.5
    scrub = pl(SCRUB, mk(((-70, 150, 24), (-30, 160, 96)), ((70, 150, 24), (30, 140, 80))), ph)
    actor(cv, "ton", 500, 680, 25, scrub, "deadpan", k=1.15, blink_v=blink(t, .1), lean=3 * ph)
    kx = keys([(53.6, 1500), (57.4, 1090)], t)
    if t > 53.6:
        phk = t * 6.5
        # bamboo bundle on his shoulder (drawn behind him)
        for i in range(4):
            cv.stroke([(kx - 40 + i * 12, 700), (kx - 150 + i * 28, 300)], (186, 168, 96), 9)
            cv.stroke([(kx - 40 + i * 12, 700), (kx - 150 + i * 28, 300)], (216, 196, 120), 5)
        if t < 57.4:
            actor(cv, "chok", kx, 700, 40, walk_pose(phk), "smug", k=1.05, flip=True, walk=dict(phase=phk, stride=16, lift=12))
        else:
            actor(cv, "chok", 1090, 700, 40, HIP, "gloat", k=1.05, flip=True, mouth=talk(t, 58.0, 61.0, 6), blink_v=blink(t, .4))
    # Uean fades out of the story: she exits
    ux = keys([(50, 1160), (53, 1500)], t)
    if t < 54.5:
        actor(cv, "uean", ux, 700, 20, REST, "gloat", k=1.0, flip=False if t < 50 else True, blink_v=blink(t, .2))


def draw(cv, t, ov):
    cv.push(0, 0, scale=1.0)
    if t < 32.0:
        kitchen_view(cv, t, ov)
    elif t < 47.0:
        u = seg(t, 32.0, 45.0)
        a9 = crates_view(cv, t, ov, u)
        actor(cv, "ton", 840, 715, 25, pl(REST, HEADS, seg(t, 34, 35)), "gape" if t < 44 else "yikes", k=0.8, flip=True, blink_v=blink(t, .1))
        actor(cv, "uean", 1050, 715, 25, CROSS, "gloat", k=0.8, flip=True, blink_v=blink(t, .2))
        if a9 >= 1.0:
            pass
    elif t < 53:
        kitchen(cv, t)
        counter(cv, 560)
        sink(cv, 190, 560, 280, t=t)
        for i in range(10):
            bowl_tower(cv, 400 + i * 66, 556, 40, 8)
        for i in range(9):
            bowl_tower(cv, 433 + i * 66, 640, 40, 8)
        bowl_tower(cv, 433 + 9 * 66, 640, 40, 3)
        stool(cv, 190, 700)
        actor(cv, "ton", 190, 690, 25, pl(SCRUB, mk(((-84, 130, 20), (-62, 100, 70)), ((84, 130, 20), (62, 100, 70))), seg(t, 47.0, 47.6)), "plead", k=1.15,
              mouth=talk(t, 47.0, 51.5, 7), blink_v=blink(t, .1))
        actor(cv, "uean", 1060, 715, 20, pl(HIP, LADLE_POINT, seg(t, 51.6, 52.0)), "gloat", k=1.1, flip=True, mouth=talk(t, 51.8, 52.8, 8), blink_v=blink(t, .2))
    else:
        final_view(cv, t, ov)
    # fade to black at the very end
    if t > DUR - 2.0:
        cv.fill([(-10, -10), (W + 10, -10), (W + 10, H + 10), (-10, H + 10)], (0, 0, 0), ink=None, alpha=int(255 * seg(t, DUR - 2.0, DUR - 0.2)))
    cv.pop()
