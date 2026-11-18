"""Scene 4b - folds 1-6 (script: ฉาก 4, the village folds the 100 m roll). Side view, drawn to scale with the camera zooming in as the paper
gets shorter: 100 m -> 50 -> 25 (flat villagers on screen), then 12.5 -> 6.25 -> 3.1 m at human scale with the named characters.
Cartoon licence: the end of the moving half stays at hand height while the strip arches over (a flexible sheet, not a rigid board). ~26 s."""
from acting import *  # noqa: F401,F403
from props import *   # noqa: F401,F403

NAME, DUR = "s4b", 26.0
G = 600
FOLD_T = [(0.2, 3.0), (3.4, 6.2), (6.6, 9.6), (10.2, 13.4), (13.8, 17.4), (17.8, 21.8)]       # fold 1..6 (start, end)
SCALE_S = [10.5, 21.0, 42.0, 84.0, 168.0, 250.0]                                              # px per metre while folding fold k+1
CAPS = [
    (0.0, 2.6, "chok", "พับหนึ่ง!"), (3.3, 5.9, "chok", "พับสอง!"), (6.5, 9.2, "chok", "พับสาม!"),
    (10.1, 12.8, "chok", "พับสี่!"), (13.7, 16.2, "chok", "ห้า!"), (17.7, 20.0, "chok", "หก!"),
    (21.4, 25.4, "ton", "(ตะโกน ยังมั่นใจ) เจ็ดแล้ว! เห็นไหมว่าใกล้หมด!"),
]
CUES = [(0.4, "whoosh", 0.5), (2.5, "thump", 0.6), (3.6, "whoosh", 0.5), (5.8, "thump", 0.6), (6.8, "whoosh", 0.5), (9.2, "thump", 0.7),
        (10.4, "whoosh", 0.5), (13.0, "thump", 0.8), (14.0, "whoosh", 0.5), (17.0, "thump", 0.9), (18.0, "whoosh", 0.5), (21.4, "thump", 1.0),
        (22.0, "cheer", 0.5)]
CUES += [(10.4 + 0.45 * k, "step", 0.25) for k in range(7)] + [(14.0 + 0.45 * k, "step", 0.25) for k in range(7)] + [(18.0 + 0.45 * k, "step", 0.25) for k in range(8)]


def fold_index(t):
    for i, (a, b) in enumerate(FOLD_T):
        if t < b:
            return i, seg(t, a, b)
    return len(FOLD_T) - 1, 1.0


def stack_len(k):
    return 100.0 / 2 ** k


def cam_S(t):
    i, u = fold_index(t)
    # glide the zoom between folds: at the start of fold i we are already at its scale
    if i == 0:
        return SCALE_S[0]
    prev = SCALE_S[i - 1]
    cur = SCALE_S[i]
    a, _ = FOLD_T[i]
    return lerp(prev, cur, ease(seg(t, FOLD_T[i - 1][1] - 0.6, a + 0.2)))


def bez(p0, p1, p2, n=26):
    return [((1 - s) ** 2 * p0[0] + 2 * s * (1 - s) * p1[0] + s * s * p2[0], (1 - s) ** 2 * p0[1] + 2 * s * (1 - s) * p1[1] + s * s * p2[1])
            for s in [i / n for i in range(n + 1)]]


def draw(cv, t, ov):
    cv.push(0, 0, scale=1.0)
    i, u = fold_index(t)
    S = cam_S(t)
    courtyard(cv, 300, "gold", gate_x=1150, gate_s=0.7, t=t, show_flags=(S > 60))
    x0 = 90 if S < 60 else 70
    if i >= 3:
        x0 = 220
    # current state: i folds done before this one (fold i+1 is the one in progress, u in 0..1)
    k = i if t < FOLD_T[i][1] else i + 1
    L = stack_len(i)                                      # stack length before the current fold
    thick_m = 2 ** i * 1e-4
    th = max(thick_m * S, 4.0)
    done = t >= FOLD_T[i][1]
    moving = FOLD_T[i][0] <= t < FOLD_T[i][1]
    psi = math.pi * ease(u) if moving else (math.pi if done else 0.0)
    if done:
        L_draw = L / 2
        th2 = max(2 * thick_m * S, 4.0)
        cv.fill([(x0, G), (x0 + L_draw * S, G), (x0 + L_draw * S, G - th2), (x0, G - th2)], PAPER, ink=INK, lw=2.2)
    else:
        xh = x0 + L / 2 * S
        cv.fill([(x0, G), (xh, G), (xh, G - th), (x0, G - th)], PAPER, ink=INK, lw=2.2)
        if not moving:
            cv.fill([(xh, G), (x0 + L * S, G), (x0 + L * S, G - th), (xh, G - th)], PAPER, ink=INK, lw=2.2)
        else:
            Lh = L / 2
            hand_y = G - 1.65 * S
            lift = math.sin(min(1.0, u * 3)) if u < 0.34 else 1.0
            e_x = xh + Lh * S * math.cos(psi)
            e_y = G - th - (1.65 * S - th) * lift if (u < 0.9) else G - th - (1.65 * S - th) * (1 - seg(u, 0.9, 1.0))
            peak = 0.5 * Lh * math.sin(psi) * S + th
            pts = bez((xh, G - th), ((xh + e_x) / 2, G - th - peak * 1.35), (e_x, e_y))
            cv.stroke(pts, INK, max(th, 3.0) + 3.2)
            cv.stroke(pts, PAPER, max(th, 3.0))
            ex_, ey_ = e_x, e_y
    # people
    sm = max(0.17, 1.5 * min(S, 90) / 90)
    if S < 60:
        n = 26
        for j in range(n):
            f = (j + 0.5) / n
            px = x0 + f * L * S
            if moving and f > 0.5:
                Lh = L / 2
                px = (x0 + L / 2 * S) + (f - 0.5) * L * S * math.cos(psi)
            elif done and f > 0.5:
                px = x0 + (1 - f) * L * S
            py = G + 22 * sm + (j % 3) * 8 * sm
            mini(cv, px, py, sm * 1.0, j, arms="up", moving=moving, phase=t * 8 + j, flip=False, expr="grin")
    else:
        # named characters at human scale; extras behind them, few and small
        kk = S / 192.0
        hinge_x = x0 + L / 2 * S
        end_x = (hinge_x + (L / 2) * S * math.cos(psi)) if moving else (x0 + (L / 2 * S if done else L * S))
        ph = t * 8
        for j in range(5):
            fx = x0 + (j + 0.5) / 5 * max(L, 3) * S * (0.5 if done else 1.0) + 40
            mini(cv, clamp(fx, 40, 1240), G + 6 + (j % 2) * 8, sm * 0.55, j + 3, arms="up" if moving else "swing", moving=moving, phase=t * 8 + j, expr="grin")
        ton_x = clamp(end_x + 40, 100, 1180)
        pose_t = ARMS_UP_C if (moving and 0.05 < u < 0.9) else REST
        actor(cv, "chok", clamp(hinge_x - 130, 90, 1190), G + 30, 40, ARMS_UP_C if moving else HIP, "shout" if moving else "neutral", k=kk * 0.8, flip=True,
              mouth=talk(t, FOLD_T[i][0] - 0.2, FOLD_T[i][0] + 2.4, 5), blink_v=blink(t, .4))
        actor(cv, "uean", clamp(hinge_x + 150, 90, 1190), G + 40, 40, ARMS_UP_C if moving else CROSS, "gape" if moving else "gloat", k=kk * 0.75, blink_v=blink(t, .2))
        actor(cv, "ton", ton_x, G + 44, 40, pose_t, "shout" if moving else "eager", k=kk * 0.8, flip=(psi > math.pi / 2) if moving else False,
              walk=dict(phase=ph, stride=24 * kk, lift=20 * kk) if moving else None, mouth=talk(t, 21.4, 25.4, 3), blink_v=blink(t, .1))
    cv.pop()


ARMS_UP_C = mk(((-84, 90, 0), (-60, 22, 20)), ((84, 90, 0), (60, 22, 20)))
