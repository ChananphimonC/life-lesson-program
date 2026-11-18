"""Red thread, scene 4 (v2): the tangled thread (seen from above it is one big heart), Ta is dumped before year two, AA dumps Pin before year three ('I don't like you, I don't feel
anything for you any more, let's break up'), Pin goes to the restroom and cries."""
from rt_common import *  # noqa: F401,F403

NAME, I = "rt4", 4
DUR = scene_dur(I)
CAPS = []
MARK = ["ด้ายแดงเส้นนั้นล่ะ", "แต่พอมองจากข้างบน", "ปิดเทอมก่อนขึ้นปีสอง", "ปิดเทอมก่อนขึ้นปีสาม", "ปิ่นอ้าปากจะพูด", "เธอเดินไปที่ห้องน้ำ"]
B = beats(I, MARK)
BE = B + [DUR - TAIL]
CUES = [(B[0] + 2.0, "whoosh", 0.4), (B[1] + 2.0, "chime", 0.5), (B[2] + 3.0, "beep", 0.5), (B[2] + 6.5, "crack", 0.6), (B[3] + 6.0, "crack", 0.7), (B[4] + 1.0, "sigh", 0.5), (B[5] + 2.0, "step", 0.4)]


def draw(cv, t, ov):
    cv.push(0, 0, scale=1.0)
    tick(t)
    k = which(t, B)
    ph = walk_ph(t, 7.0)
    if k == 0:
        corridor(cv, t)
        # the thread winds round a pillar, a bench leg and the restroom door knob on its way from Ta to Pin
        rect(cv, 590, 130, 650, 450, (206, 200, 190), lw=2.8)
        rect(cv, 760, 560, 940, 590, (190, 146, 104), lw=2.8, shade_col=WOOD_SH)
        rect(cv, 780, 590, 796, 660, (150, 108, 76), lw=2.0)
        st(cv, "phum", 170, 700, pose=REST, ex="happy", th=35, k=0.95, seed=1)
        st(cv, "bua", 1180, 700, pose=REST, ex="neutral", th=-35, flip=True, k=0.95, seed=2)
        a = ease(fr(t, BE, 0, 0.0, 0.5))
        pa = pinky_of("phum", toward_x=1000)
        pb = pinky_of("bua", toward_x=0)
        way = [(620, 300), (800, 620), (1086, 292)]
        shown = max(1, int(1 + a * 2.99))
        yarn_loops(cv, way[:shown], t, alpha=255)
        link(cv, pa, (way[0][0] - 26, way[0][1]), t, sag=60, tie=True, spark=False)
        if shown >= 2:
            link(cv, (way[0][0] + 26, way[0][1] + 10), (way[1][0] - 26, way[1][1]), t, sag=70, tie=False, spark=False)
        if shown >= 3:
            link(cv, (way[1][0] + 26, way[1][1]), (way[2][0] - 26, way[2][1]), t, sag=-50, tie=False, spark=False)
        link(cv, (way[min(shown, 3) - 1][0] + 26, way[min(shown, 3) - 1][1]), pb, t, sag=50, tie=True, spark=False)
        ov.append(("?", 640, 100, 80, (255, 255, 255), 0.5 + 0.5 * math.sin(t * 3)))
    elif k == 1:
        # seen from above: the whole tangle is one big heart, Ta and Pin small at the bottom corners with their threads running up into it
        band(cv, 0, H, (252, 244, 238), (246, 226, 222), n=12, x0=0, x1=W)
        a = ease(fr(t, BE, 1, 0.0, 0.3))
        sc = 0.7 + 0.3 * a
        tangle_heart(cv, 640, 330, 250 * sc, t, strands=11, alpha=int(255 * a))
        st(cv, "phum", 190, 700, pose=REST, ex="happy", th=35, k=0.7, seed=1)
        st(cv, "bua", 1090, 700, pose=REST, ex="happy", th=-35, flip=True, k=0.7, seed=2)
        pa = pinky_of("phum", toward_x=640)
        pb = pinky_of("bua", toward_x=640)
        link(cv, pa, (470, 470), t, sag=50, alpha=int(255 * a), spark=True)
        link(cv, pb, (810, 470), t, sag=50, alpha=int(255 * a), spark=True)
        beat = max(0.0, math.sin(t * 3.0)) ** 3
        cv.ellipse(640, 340, 270 + 40 * beat, 230 + 34 * beat, (250, 130, 150), ink=None, alpha=int(34 * a * beat))
    elif k == 2:
        # Ta alone on a bench with his phone: the message arrives, his small heart cracks in two
        dorm_night(cv, t)
        rect(cv, 340, 600, 760, 632, (176, 132, 96), lw=2.8, shade_col=WOOD_SH)
        rect(cv, 370, 632, 386, 700, (140, 100, 70), lw=2.0)
        rect(cv, 710, 632, 726, 700, (140, 100, 70), lw=2.0)
        sad = ease(fr(t, BE, 2, 0.35, 0.6))
        pose = reach("phum", 560, 700, 30, 0.95, {"R": (528, 540), "L": (592, 540)}, kinds=("relaxed", "relaxed"), z=80)
        st(cv, "phum", 560, 700, pose=pose, ex="plead" if sad > 0.5 else "neutral", th=30, k=0.95, seed=1, lean=-2)
        rect(cv, 340, 600, 760, 632, (176, 132, 96), lw=2.8, shade_col=WOOD_SH)
        # the phone in his hands and the message bubble above it
        rrect(cv, 536, 492, 586, 568, 8, (44, 48, 66), lw=2.4)
        rrect(cv, 541, 500, 581, 560, 4, (150, 220, 255), lw=1.0)
        u = ease(fr(t, BE, 2, 0.12, 0.3))
        if u > 0:
            cv.push(700, 330, scale=0.6 + 0.4 * u)
            bubble(cv, 0, 0, 130, 74, tail=(-60, 46), alpha=int(255 * u))
            cv.pop()
            if u > 0.7:
                cv.stroke([(645, 318), (740, 318)], (170, 176, 190), 3)
                cv.stroke([(645, 336), (712, 336)], (170, 176, 190), 3)
        split = ease(fr(t, BE, 2, 0.5, 0.95))
        heart_broken(cv, 880, 320 + 50 * split * split, 62, split=split, alpha=int(255 * ease(fr(t, BE, 2, 0.4, 0.5))))
        tie_out(cv, "phum", 1, t, sag=80)
    elif k == 3:
        # dusk on the steps: AA says it, the heart between them cracks
        stairs_night(cv, t)
        say = in_(t, BE, 3, 0.18, 0.62)
        st(cv, "bua", 420, 700, pose=REST, ex="gape" if fr(t, BE, 3, 0.55, 1.0) > 0 else "neutral", th=35, k=0.95, seed=2)
        st(cv, "kong", 860, 700, pose=CROSS, ex="deadpan", th=35, flip=True, k=0.98, seed=4,
           mouth=mouth_of(t, BE[3] + 0.18 * (BE[4] - BE[3]), BE[3] + 0.62 * (BE[4] - BE[3]), 6) if say else 0)
        if say:
            say_waves(cv, 800, 470, t, BE[3] + 0.18 * (BE[4] - BE[3]), BE[3] + 0.62 * (BE[4] - BE[3]), flip=True)
        cr = ease(fr(t, BE, 3, 0.5, 0.95))
        heart_broken(cv, 640, 330 + 40 * cr * cr, 66, split=cr, alpha=int(255 * ease(fr(t, BE, 3, 0.12, 0.3))))
        tie_out(cv, "bua", -1, t, sag=80)
    elif k == 4:
        # Pin opens her mouth but nothing comes out, then she walks (+x) for the restroom
        corridor(cv, t)
        go = fr(t, BE, 4, 0.45, 1.0)
        px = 300 + 700 * ease(go)
        walking = go > 0
        st(cv, "bua", px, 700, pose=walk_pose(ph) if walking else REST, ex="plead" if not walking else "worried", th=60 if walking else 40, k=0.95, seed=2,
           walk=dict(phase=ph, stride=14, lift=10) if walking else None, mouth=0.7 * abs(math.sin(t * 3)) if not walking else 0)
        if not walking:
            ov.append(("...", px + 50, 380, 70, (255, 255, 255), 0.6 + 0.4 * math.sin(t * 3)))
        tie_out(cv, "bua", -1, t, sag=70)
    else:
        # the restroom: she cries quietly, shoulders shaking, tears falling
        restroom(cv, t)
        cx = 700
        face = ease(fr(t, BE, 5, 0.15, 0.4))
        sob = 3.0 * math.sin(t * 9.0)
        s = 0.9 * 0.95
        hp = head_pos("bua", cx, 700, 0.95, 0.0)
        pose = reach("bua", cx, 700, 10, 0.95, {"R": (cx - 40, hp[1] + 40 + sob), "L": (cx + 40, hp[1] + 40 + sob)}, kinds=("relaxed", "relaxed"), z=90)
        st(cv, "bua", cx, 700, pose=pl(REST, pose, face), ex="plead", th=10, k=0.95, seed=2, lean=sob * 0.6)
        for j in range(5):
            u = (t * 0.9 + j * 0.2) % 1.0
            side = -1 if j % 2 == 0 else 1
            tear(cv, cx + side * 26 * s, hp[1] + 16 + 150 * u * u, 1.0, alpha=int(255 * (1 - u)))
        tie_out(cv, "bua", -1, t, sag=70)
    cv.pop()
    pulse_ov(ov, t)
