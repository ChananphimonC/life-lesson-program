"""Scene 1 - folding by hand (script: ฉาก 1). Seven folds of an A4 sheet; the effort escalates until Ton can do no more. ~41 s."""
from acting import *  # noqa: F401,F403
from props import *   # noqa: F401,F403

NAME, DUR = "s1", 41.0
CAPS = [
    (0.6, 3.0, "ton", "ล้านครั้งก็เหมือนกัน ผมพับให้ดูเลย"),
    (17.6, 19.8, "ton", "(หอบ) เจ็ด… ไม่ไหวแล้ว…"),
    (19.9, 22.4, "uean", "เจ็ดครั้งก็ไม่ไหว ล้านครั้งเหรอ"),
    (22.5, 25.6, "ton", "งั้นพับไม่ได้ก็ไม่ต้องนับ! ยกเลิกเกม!"),
    (25.8, 29.6, "kaew", "ซองไม่ได้ถามว่าพับได้ไหม ซองถามว่า “ถ้าพับ” กี่ครั้ง"),
    (29.8, 31.0, "ton", "ไม่ยุติธรรม"),
    (31.1, 35.0, "kaew", "ยุติธรรมตรงที่ทุกคนทายโดยไม่รู้คำตอบ"),
    (35.4, 40.6, "chok", "เขาไม่ชอบถูกกด แต่ไม่ได้แปลว่าพับต่อไม่ได้"),
]
FOLDS = [(1.6, 2.7), (3.3, 4.5), (5.0, 6.6), (7.2, 9.0), (9.6, 11.8), (12.4, 14.6), (15.2, 17.4)]     # start, end of each fold
CUES = [(1.8, "paper", 0.8), (3.5, "paper", 0.8), (5.6, "thump", 0.7), (8.0, "thump", 0.8), (10.8, "thump", 0.9), (13.6, "thump", 0.9),
        (15.0, "whoosh", 0.5), (16.8, "thump", 1.0), (17.4, "boing", 0.5), (23.5, "cheer", 0.0), (35.8, "paper", 0.5), (21.0, "sigh", 0.5)]

SLUMP = mk(((-60, 190, -10), (-52, 240, 0)), ((60, 190, -10), (52, 240, 0)))
FLAIL_A = mk(((-100, 90, 0), (-80, 20, 20)), ((100, 130, 0), (110, 100, 30)))
FLAIL_B = mk(((-100, 130, 0), (-110, 100, 30)), ((100, 90, 0), (80, 20, 20)))
CTR_Y = 507                                  # counter top (screen y) behind which the paper lies


K, FY = 1.28, 655                            # Ton's scale and floor line (he stands behind the table)
PW, PH, DEP = 240, 339, 0.2                  # A4 sheet on the table (px), foreshortened depth
PCX, PCY = 585, 500                          # where the sheet starts; the stack then drifts to wherever each flap lands
TABLE_TOP, TON_ON_TABLE_Y = 452, 515


def box(n):
    """Centre and size of the stack after n folds (matches props.table_paper(drift=True))."""
    cx, cy, cw, ch = PCX, PCY, PW, PH
    for k in range(n):
        if k % 2 == 0:
            cx += cw / 4
            cw /= 2
        else:
            cy += ch * DEP / 4
            ch /= 2
    return cx, cy, cw, ch


def lerp(p, q, u):
    return (p[0] + (q[0] - p[0]) * u, p[1] + (q[1] - p[1]) * u)


def press_pts(n):
    cx, cy, cw, ch = box(n)
    return (cx - cw * 0.22, cy + 2), (cx + cw * 0.22, cy + 2)


def fold_pts(i, u):
    """Where the two hands are while fold i is under way: they grip the free edge and carry it over, then press the stack flat."""
    cx, cy, cw, ch = box(i)
    x0, x1, y0, y1 = cx - cw / 2, cx + cw / 2, cy - ch * DEP / 2, cy + ch * DEP / 2
    pR, pL = press_pts(i + 1)
    a = math.pi * u
    if i % 2 == 0:                                       # left half carried over to the right half
        fx = cx + (x0 - cx) * math.cos(a)
        lift = math.sin(a) * ch * 0.2
        e0, e1 = y0 - lift * 1.1, y1 - lift * 1.1
        edge = (fx, e0 + (e1 - e0) * 0.5)
        R = edge if u < 0.5 else lerp(edge, pR, ease(seg(u, 0.5, 0.75)))
        hold = (x1 - cw * 0.12, y0 + (y1 - y0) * 0.55)
        L = lerp(hold, edge, ease(seg(u, 0.3, 0.55))) if u < 0.55 else edge
        L = L if u < 0.8 else lerp(edge, pL, ease(seg(u, 0.8, 1.0)))
    else:                                                # far half folded over the near half
        fy = cy + (y0 - cy) * math.cos(a)
        lift = math.sin(a) * cw * 0.12
        R = (x0 + cw * 0.18, fy - lift)
        L = (x1 - cw * 0.18, fy - lift)
        if u > 0.75:
            R, L = lerp(R, pR, ease(seg(u, 0.75, 1.0))), lerp(L, pL, ease(seg(u, 0.75, 1.0)))
    if u > 0.9:                                          # smoothing it flat: a little press
        dip = math.sin((u - 0.9) / 0.1 * math.pi) * 3
        R, L = (R[0], R[1] + dip), (L[0], L[1] + dip)
    return R, L


def grip_start(i):
    return fold_pts(i, 0.0)


def hand_targets(t):
    if t < FOLDS[0][0]:
        return grip_start(0)
    for i, (a, b) in enumerate(FOLDS[:6]):
        if a <= t < b:
            return fold_pts(i, seg(t, a, b))
        if i < 5 and b <= t < FOLDS[i + 1][0]:
            return tuple(lerp(p, q, ease(seg(t, b, FOLDS[i + 1][0]))) for p, q in zip(fold_pts(i, 1.0), grip_start(i + 1)))
    return fold_pts(5, 1.0)


def ton_hands(t, th=8):
    R, L = hand_targets(t)
    return reach("ton", PXC, FY, th, K, dict(R=R, L=L), z=60)


PXC = 640


def draw(cv, t, ov):
    cv.push(0, 0, scale=1.0)
    courtyard(cv, 300, "day", gate_x=150, gate_s=0.6, t=t)
    shop(cv, t, 760, 600, 1.3)
    nf = sum(1 for a, b in FOLDS if t >= b)
    cur = next(((i, seg(t, a, b)) for i, (a, b) in enumerate(FOLDS) if a <= t < b), None)
    folds_done, prog = (cur[0], cur[1]) if cur else (nf, 0.0)

    mk_k = talk(t, 25.8, 29.6, 1) or talk(t, 31.1, 35.0, 2)
    actor(cv, "kaew", 960, 600, -40, CROSS if 25 < t < 36 else REST, "smug" if t > 24 else "gloat", k=0.95, mouth=mk_k, blink_v=blink(t, .7))
    mouth_u = talk(t, 19.9, 22.4, 5)
    actor(cv, "uean", 1130, 600, -35, pl(REST, HAMMER, seg(t, 19.6, 20.0)) if 19.6 < t < 24 else REST,
          "shout" if 19.9 < t < 22.4 else ("laugh" if 22.4 < t < 25 else "gloat"), k=0.85, mouth=mouth_u, blink_v=blink(t, .2))
    shop_counter(cv, 760, 600, 1.3)

    ton_on_table = t >= 15.2
    hands = {}

    def paper():
        n, p = (folds_done, prog) if t < 17.0 else (7, 0.0)
        table_paper(cv, PCX, PCY, PW, PH, n, p, depth=DEP, lift_k=0.2, drift=True)

    def ton_fn():
        if t < 15.2:
            by = 0.0
            if cur:
                i, u = cur
                ex_t = ["determined", "determined", "eager", "yikes", "yikes", "pant"][min(i, 5)]
                lean = [1.5, 2, 3, 4, 5, 6][min(i, 5)] * math.sin(u * math.pi)
                effort = [0.0, 0.0, 0.3, 0.6, 0.9, 1.0][min(i, 5)]
                by = effort * 3 * math.sin(u * math.pi * 2)             # the shoulders heave with the effort
                pose = ton_hands(t)
            else:
                ex_t = "determined" if t > 0.4 else "neutral"
                lean = 0.0
                pose = ton_hands(t)
                if t < 1.6:
                    pose = pl(REST, pose, ease(seg(t, 0.7, 1.5)))
                elif cur is None and nf:                                # between folds: look at the work
                    ex_t = ["determined", "determined", "eager", "yikes", "yikes", "pant"][min(nf - 1, 5)]
            actor(cv, "ton", PXC, FY - by, 8, pose, ex_t, k=K, lean=lean, mouth=talk(t, 0.6, 3.0, 3), blink_v=blink(t, 0.1))
            hands.update(pose=pose, lean=lean, by=by)
            return
        if t < 17.4:
            ty = keys([(15.2, FY), (15.9, 590), (16.5, 380), (17.0, 500), (17.2, TON_ON_TABLE_Y), (17.4, TON_ON_TABLE_Y)], t)
            start = ton_hands(15.19)
            actor(cv, "ton", PXC, ty, 8, pl(start, CHEER, seg(t, 15.4, 16.4)), "shout", k=K, lean=-4, shadow=False)
            return
        u = seg(t, 17.4, 19.4)
        if t < 22.5:
            actor(cv, "ton", PXC, TON_ON_TABLE_Y, 8, pl(CHEER, SLUMP, u), "pant", k=K, lean=-3 + 6 * u, mouth=talk(t, 17.6, 19.8, 3) * 0.5, shadow=False)
        elif t < 25.6:
            fl = pl(FLAIL_A, FLAIL_B, 0.5 + 0.5 * math.sin(t * 9))
            actor(cv, "ton", PXC, TON_ON_TABLE_Y, 8, fl, "shout", k=K, mouth=talk(t, 22.5, 25.6, 3), shadow=False, lean=3 * math.sin(t * 9))
        else:
            ex_t = "plead" if 29.8 < t < 31 else "deadpan"
            actor(cv, "ton", PXC, TON_ON_TABLE_Y, 8, pl(FLAIL_A, SLUMP, seg(t, 25.6, 26.6)) if t < 26.6 else SLUMP, ex_t, k=K, mouth=talk(t, 29.8, 31.0, 4),
                  blink_v=blink(t, 0.1), shadow=False)

    if not ton_on_table:
        ton_fn()
    table(cv, PXC, TABLE_TOP, 560, 110, 60)
    paper()
    if not ton_on_table:
        front_arms(cv, "ton", PXC, FY - hands["by"], 8, hands["pose"], k=K, lean=hands["lean"])
    if ton_on_table:
        ton_fn()
        if t >= 17.0:
            puff(cv, PXC, 505, 22, seg(t, 16.9, 18.2))

    if t > 33.0:
        cx_ = keys([(33.0, -60), (35.0, 330)], t)
        if t < 35.0:
            ph = walk_ph(t, 6.5)
            actor(cv, "chok", cx_, 660, 50, walk_pose(ph), "neutral", k=1.1, walk=dict(phase=ph, stride=16, lift=12))
        else:
            pose = pl(REST, mk(((-60, 170, 30), (-30, 186, 100))), seg(t, 35.0, 35.8))
            actor(cv, "chok", 330, 660, 50, pose, "think", k=1.1, mouth=talk(t, 35.4, 40.6, 5), blink_v=blink(t, 0.4))
    cv.pop()
