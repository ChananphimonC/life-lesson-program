"""Red thread, scene 7 (v2): graduation photo (black gowns and black mortarboards, a bouquet and a teddy bear each, Em shouts, Bam and Orn smirk), the old man winds the thread in until it is one
step long, and the closing question to the viewer (hiding from someone? the thread is already coming round the corner)."""
from rt_common import *  # noqa: F401,F403
import uni_chars

NAME, I = "rt7", 7
DUR = scene_dur(I)
CAPS = []
MARK = ["วันรับปริญญา", "เอมตะโกนจากข้างหลังว่า", "แบมกับอรยืนยิ้มเจ้าเล่ห์", "ส่วนบนฟ้า", "ถ้าตอนนี้คุณกำลังหลบใคร"]
B = beats(I, MARK)
BE = B + [DUR - TAIL]
CUES = [(B[0] + 5.0, "pop", 0.5), (B[1] + 0.5, "cheer", 0.5), (B[1] + 3.0, "laugh", 0.4), (B[2] + 3.0, "ding", 0.4), (B[3] + 2.0, "whoosh", 0.4), (B[3] + 7.0, "ding", 0.5), (B[4] + 3.0, "chime", 0.5)]
GROUP = {"phum", "bua", "em", "bam", "manao"}


def cap(cv, who, x, tl=0.0, k=1.0):
    hx, hy = head_pos(who, x, 700, k * KS.get(who, 1.0) / 1.0, -98 * (SCALE_OF.get(who, 0.9) / 0.9))
    mortarboard(cv, hx, hy, 1.5 * SCALE_OF.get(who, 0.9) / 0.9, tilt=tl)


SCALE_OF = {"phum": 0.92, "bua": 0.9, "em": 0.9, "bam": 0.9, "manao": 0.88}


def lawn_photo(cv, t):
    lawn(cv, t)


def draw(cv, t, ov):
    cv.push(0, 0, scale=1.0)
    tick(t)
    k = which(t, B)
    ph = walk_ph(t, 6.0)
    if k in (0, 1, 2):
        uni_chars.GOWN.update(GROUP)
        try:
            lawn_photo(cv, t)
            shout = k == 1 and in_(t, BE, 1, 0.0, 0.8)
            smirk = k == 2
            orn_say = k == 2 and in_(t, BE, 2, 0.4, 0.9)
            # the photo pair in the middle: outer hand holds a bouquet, a teddy bear tucked in beside it, inner little fingers tied
            ta_pose = reach("phum", 560, 700, 20, 1.0, {"L": (472, 560)}, kinds=("relaxed", "relaxed"), z=80)
            pin_pose = reach("bua", 730, 700, -20, 1.0, {"R": (818, 560)}, kinds=("relaxed", "relaxed"), z=80)
            st(cv, "phum", 560, 700, pose=ta_pose, ex="laugh" if k else "happy", th=20, k=1.0, seed=1)
            st(cv, "bua", 740, 700, pose=pin_pose, ex="happy", th=-20, flip=True, k=1.0, seed=2)
            bouquet(cv, 470, 560, 1.0, sway=3 * math.sin(t * 1.5))
            teddy(cv, 428, 640, 0.62, tilt=-6)
            bouquet(cv, 820, 560, 1.0, sway=-3 * math.sin(t * 1.5 + 1))
            teddy(cv, 862, 640, 0.62, tilt=6)
            cap(cv, "phum", 560, -6)
            cap(cv, "bua", 740, 6)
            st(cv, "em", 290, 700, pose=ARMS_UP if shout else REST, ex="shout" if shout else "laugh", th=40, k=0.95, seed=3, mouth=mouth_of(t, BE[1], BE[1] + 0.8 * (BE[2] - BE[1]), 3) if shout else 0)
            cap(cv, "em", 290, -4, 0.95)
            st(cv, "bam", 1010, 700, pose=CROSS if smirk else REST, ex="smug" if smirk else "happy", th=-35, flip=True, k=0.95, seed=4)
            cap(cv, "bam", 1010, 5, 0.95)
            st(cv, "manao", 1150, 700, pose=CROSS if smirk else REST, ex="smug" if smirk else "happy", th=-35, flip=True, k=0.95, seed=5,
               mouth=mouth_of(t, BE[2] + 0.4 * (BE[3] - BE[2]), BE[2] + 0.9 * (BE[3] - BE[2]), 6) if orn_say else 0)
            cap(cv, "manao", 1150, 4, 0.95)
            tie(cv, "phum", "bua", t, sag=26)
            # flash of the camera at the end of the first beat
            if k == 0:
                fl = max(0.0, 1.0 - abs(fr(t, BE, 0, 0.82, 0.92) * 2 - 1) * 5) if fr(t, BE, 0, 0.82, 0.92) > 0 else 0.0
                if fl > 0:
                    cv.fill([(0, 0), (W, 0), (W, H), (0, H)], (255, 255, 255), ink=None, alpha=int(230 * fl))
            if shout:
                say_waves(cv, 360, 470, t, BE[1], BE[1] + 0.8 * (BE[2] - BE[1]))
            if orn_say:
                say_waves(cv, 1080, 470, t, BE[2] + 0.4 * (BE[3] - BE[2]), BE[2] + 0.9 * (BE[3] - BE[2]), flip=True)
        finally:
            uni_chars.GOWN.clear()
    elif k == 3:
        moon_sky(cv, t)
        ambient(cv, t, 20, (255, 240, 200), seed=6)
        cloud(cv, 380, 600, 1.6)
        cloud(cv, 940, 640, 1.8)
        wind = ease(fr(t, BE, 3, 0.15, 0.85))
        yx = 640
        # the two graduates, small, far below on the campus: Ta walks (+x) towards Pin as the old man winds the thread in
        uni_chars.GOWN.update(GROUP)
        try:
            tx = 330 + 270 * wind
            walking = 0.02 < wind < 0.98
            rect(cv, 220, 690, 1060, 720, (96, 98, 126), ink=None)
            st(cv, "phum", tx, 712, pose=walk_pose(ph) if walking else REST, ex="happy", th=60 if walking else 40, k=0.40, seed=1, walk=dict(phase=ph, stride=7, lift=5) if walking else None)
            st(cv, "bua", 880, 712, pose=REST, ex="happy", th=40, flip=True, k=0.40, seed=2)
        finally:
            uni_chars.GOWN.clear()
        pose = pl(REST, mk(((-60, 150, 30), (-30, 130, 90)), ((60, 150, 30), (30, 130, 90))), 0.5 + 0.5 * math.sin(t * 2))
        st(cv, "yuelao", yx, 560, pose=pose, ex="smug" if wind < 0.9 else "deadpan", th=20, k=1.1, mouth=mouth_of(t, BE[3] + (BE[4] - BE[3]) * 0.6, BE[4] - 0.3, 4))
        spool(cv, 540, 570, 34, turn=-t * 4)
        # the thread runs Ta -> up to the old man's hands -> down to Pin, and shortens as he winds
        hand = (yx + 50, 470)
        pa = pinky_of("phum", toward_x=yx)
        pb = pinky_of("bua", toward_x=yx)
        link(cv, pa, hand, t, sag=20 * (1 - wind), tie=True, spark=True)
        link(cv, hand, pb, t, sag=20 * (1 - wind), tie=True, spark=True)
        if in_(t, BE, 3, 0.85, 1.0):
            sigh_puff(cv, "yuelao", yx, 560, t, 1.1, side=1)
    else:
        corridor(cv, t)
        # closing: Pin half hidden behind a locker, the thread coming round the corner, Ta strolling closer from the far left
        a = ease(fr(t, BE, 4, 0.1, 0.5))
        walk_t = ease(fr(t, BE, 4, 0.1, 0.9))
        tx = 60 + 380 * walk_t
        walking = 0.02 < walk_t < 0.98
        st(cv, "phum", tx, 640, pose=walk_pose(ph) if walking else REST, ex="happy", th=60 if walking else 40, k=0.6, seed=1, walk=dict(phase=ph, stride=10, lift=7) if walking else None)
        st(cv, "bua", 820, 700, pose=HEADS, ex="worried", th=-30, flip=True, k=0.95, seed=2)
        rect(cv, 640, 160, 760, 440, (110, 160, 200), lw=2.4)                   # the locker she hides behind (drawn over half of her)
        rect(cv, 640, 440, 760, 720, (110, 160, 200), lw=2.4)
        tie(cv, "phum", "bua", t, sag=50, alpha=int(255 * a))
        ov.append(("?", 840, 330, 100, (255, 255, 255), 0.6 + 0.4 * math.sin(t * 3)))
    cv.pop()
    pulse_ov(ov, t)
