"""Robot world, scene 7: dusk on the roof. Ton asks Chok if he is afraid; what can be prepared; the kite goes up; the next question (who will buy things?)."""
from rw_common import *  # noqa: F401,F403

NAME, I = "rw7", 7
DUR = scene_dur(I)
CAPS = []
MARK = ["ค่ำนั้น", "โลกที่มีแต่หุ่นยนต์", "ลุงโชคส่งว่าว", "แต่ต้นมองหุ่นยนต์"]
B = beats(I, MARK)
BE = B + [DUR - TAIL]
CUES = [(B[0] + 8.0, "sigh", 0.4), (B[2] + 5.0, "whoosh", 0.5), (B[2] + 6.0, "bamboo", 0.5), (B[3] + 3.0, "chime", 0.5), (B[3] + 7.0, "buzz", 0.3)]


def draw(cv, t, ov):
    cv.push(0, 0, scale=1.0)
    tick(t)
    k = which(t, B)
    if k <= 2:
        rooftop(cv, t)
        # the two of them at the parapet, talking (their words are the narrator's; here only mouths and gestures)
        rect(cv, 300, 560, 980, 600, (150, 146, 168), lw=2.6, shade_col=(124, 120, 146))
        asking = B[0] + 1.0 < t < B[0] + 4.2
        answering = B[0] + 5.0 < t < B[0] + 8.5
        ton(cv, 480, 760, POINT_FWD if asking else REST, "plead" if asking else "think", th=40, k=1.3, mouth=mouth_of(t, B[0] + 1.0, B[0] + 4.2, 1) if asking else 0,
            blink_v=blink(t, .1))
        chok(cv, 780, 760, SHRUG if answering else CROSS, "shout" if answering else "deadpan", th=40, k=1.25, flip=True, mouth=mouth_of(t, B[0] + 5.0, B[0] + 8.5, 2) if answering else 0,
             blink_v=blink(t, .4))
        if k == 2:
            u = seg(t, B[2] + 4.0, B[2] + 11.0)
            kite(cv, 640 + 420 * u, 520 - 330 * ease(u), 1.6, 0.2 + 0.1 * math.sin(t * 2), (236, 100, 96), tail=True, t=t)
            cv.stroke([(780, 470), (640 + 420 * u, 520 - 330 * ease(u))], (240, 220, 160), 2)
    else:
        # a robot shop: shelves full, door open, nobody comes in; an empty purse
        rect(cv, 0, 0, W, 470, (240, 232, 220), ink=None)
        rect(cv, 0, 470, W, H, (190, 176, 160), ink=None)
        for sx in (60, 360):
            rect(cv, sx, 150, sx + 250, 440, (236, 238, 244), lw=2.6, shade_col=(214, 218, 230))
            for r in range(3):
                for j in range(5):
                    rect(cv, sx + 14 + j * 46, 190 + r * 80, sx + 50 + j * 46, 236 + r * 80, [(240, 120, 110), (250, 200, 90), (120, 190, 130), (110, 160, 220), (190, 140, 220)][(j + r) % 5], lw=1.4)
        service_bot(cv, 660, 560, 1.6, t=t, mood="happy", wave=0.5 + 0.5 * math.sin(t * 3))
        # an open door and nobody coming in
        rect(cv, 940, 180, 1200, 560, (200, 230, 250), lw=3.0)
        rect(cv, 940, 560, 1200, 580, (150, 130, 110), lw=2.4)
        a = ease(seg(t, B[3] + 3.0, B[3] + 4.0))
        # a purse with nothing in it
        cv.ellipse(820, 640, 40, 34, (190, 120, 80), ink=INK, lw=2.6, shade_col=(160, 96, 62))
        cv.fill([(796, 612), (844, 612), (836, 598), (804, 598)], (190, 120, 80), ink=INK, lw=2.2)
        ov.append(("?", 1070, 330, 150, (255, 255, 255), a))
        ton(cv, 220, 700, POINT_FWD if t < B[3] + 6 else THINK, "think", th=40, k=1.1, blink_v=blink(t, .1))
        chok(cv, 360, 700, CROSS, "think", th=50, k=1.05, blink_v=blink(t, .4))
    cv.pop()
