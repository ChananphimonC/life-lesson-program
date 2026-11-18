"""Scene 0 - opening (script: ฉาก 0). The question, the stakes and the first guesses. ~43 s."""
from acting import *  # noqa: F401,F403
from props import *   # noqa: F401,F403

NAME, DUR = "s0", 43.0
SPEED = 7.0
CAPS = [
    (5.0, 9.6, "kaew", "กระดาษแผ่นนี้ พับครึ่งไปเรื่อย ๆ พับกี่ครั้งถึงจะสูงถึงดวงจันทร์"),
    (10.8, 12.6, "ton", "(สำลักน้ำแข็ง) ถามเล่นป่ะ"),
    (13.0, 16.4, "kaew", "คนที่ทายห่างที่สุด ล้างจานงานวัดทั้งคืน"),
    (16.4, 19.2, "kaew", "คำตอบอยู่ในซอง ปิดผนึกตั้งแต่เมื่อวาน"),
    (20.0, 23.0, "uean", "ล้างจานทั้งงาน สี่ร้อยชามเลยนะยายแก้ว"),
    (23.0, 25.0, "kaew", "สี่ร้อยสิบ ป้าเอื้อนเล่นไหม"),
    (33.4, 35.2, "ton", "ล้านครั้ง!"),
    (35.4, 36.8, "uean", "ห้าร้อย"),
    (37.0, 38.6, "chok", "ผมขอไม่บอกก่อน"),
    (38.7, 39.8, "kaew", "ห้ามไม่บอก"),
    (40.2, 42.4, "chok", "(คิด) แปดสิบ"),
]
CUES = [(1.0, "spoon", 0.5), (2.0, "spoon", 0.5), (3.2, "spoon", 0.5), (4.6, "paper", 0.7), (4.9, "tap", 0.6), (7.9, "whoosh", 0.4), (10.5, "spit", 0.9),
        (10.7, "gasp", 0.5), (17.9, "tap", 0.6), (19.8, "pop", 0.7), (22.0, "ladle", 0.6), (26.0, "scribble", 0.6), (27.0, "scribble", 0.5),
        (29.6, "scribble", 0.5), (31.0, "paper", 0.5), (32.0, "plop", 0.8), (32.5, "plop", 0.8), (32.9, "plop", 0.8), (33.4, "cheer", 0.6),
        (35.5, "ladle", 0.8), (42.0, "ding", 0.4)]


def steps(t0, t1, per=0.45):
    out, t = [], t0
    while t < t1:
        out.append((t, "step", 0.35))
        t += per
    return out


CUES += steps(0.2, 4.6) + steps(23.4, 25.4) + steps(27.0, 30.6)


def ice_spray(cv, x, y, u):
    for k in range(10):
        a = -0.9 + k * 0.2
        d = 70 * u * (0.6 + 0.4 * ((k * 37) % 10) / 10)
        cv.ellipse(x + math.cos(a) * d, y + math.sin(a) * d * 0.7 + 90 * u * u, 5 * (1 - u * 0.5), 5 * (1 - u * 0.5), (240, 250, 255), ink=None, alpha=int(255 * (1 - u)))


def draw(cv, t, ov):
    zoom = keys([(0, 1.0), (5, 1.0), (9.5, 1.1), (12, 1.1), (14, 1.0)], t)
    cx = keys([(0, 640), (5, 640), (9.5, 640), (12, 640), (14, 660)], t)
    cy = keys([(0, 360), (9.5, 330), (12, 330), (14, 360)], t)
    cv.push(W / 2 - cx * zoom, H / 2 - cy * zoom, scale=zoom)
    courtyard(cv, 300, "day", gate_x=150, gate_s=0.6, t=t, moon_pos=(1090, 110))
    shop(cv, t, x=760, y=600, s=1.3)
    # bench (left) where Ton eats
    rect(cv, 90, 560, 330, 584, (176, 128, 92), shade_col=(148, 106, 76))
    for bx in (110, 310):
        rect(cv, bx, 584, bx + 16, 650, (150, 108, 76))

    # ---- Kaew: walks in from the right with the paper and the envelope, places them, speaks
    if t < 4.6:
        kx = keys([(0.0, 1500), (4.4, 780)], t)
        ph = walk_ph(t, 5.5)
        actor(cv, "kaew", kx, 600, 45, walk_pose(ph, carry=CARRY), "neutral", k=1.05, walk=dict(phase=ph, stride=12, lift=9), flip=True)
        wp = wrist_pos("kaew", kx, 600, 45, CARRY, "R", 1.05, True)
        sheet(cv, wp[0], wp[1] - 6, 58, 42, -8)
        envelope(cv, wp[0] - 30, wp[1] + 6, 44, 10)
    else:
        if t < 5.2:
            pose = pl(CARRY, REST, seg(t, 4.4, 5.2))
        elif t < 8.4:
            pose = REST
        elif t < 10.6:
            pose = pl(REST, POINT_UP, seg(t, 8.4, 9.2))
        elif t < 13.0:
            pose = pl(POINT_UP, REST, seg(t, 10.6, 11.4))
        elif t < 19.2:
            pose = pl(REST, HOLD_UP2, seg(t, 16.6, 17.2)) if t > 16.6 else REST
        elif t < 24.0:
            pose = pl(HOLD_UP2, REST, seg(t, 19.2, 19.8))
        elif t < 38.7:
            pose = REST
        else:
            pose = pl(REST, mk(((-60, 150, 30), (-34, 130, 100))), seg(t, 38.6, 39.0))
        ex_k = "gloat" if 5 < t < 9.6 else ("smug" if t < 25 else "gloat" if t < 33 else "smug")
        mouth = max(talk(t, 5, 9.6, 5), talk(t, 13.0, 19.2, 6), talk(t, 23.0, 25.0, 7), talk(t, 38.7, 39.8, 8))
        actor(cv, "kaew", 780, 600, -40, pose, ex_k, k=1.05, mouth=mouth, blink_v=blink(t, 0.7), flip=False)
        # props on the counter
        if t >= 4.6:
            if t < 33.0 or True:
                sheet(cv, 700, 515, 84, 24, -3)
            if not (16.4 < t < 19.2):
                envelope(cv, 790, 508, 52, 6)
            else:
                env = envelope
                env(cv, 790, 440, 52, 12 - 6 * math.sin(t * 6))

    # counter strip in front of Kaew's legs
    shop_counter(cv, 760, 600, 1.3)
    if t >= 4.6:
        None
    # cup for the slips
    if t < 32.4 or False:
        cup(cv, 850, 516, 60, 66, slips=(1 if t > 32.0 else 0) + (1 if t > 32.4 else 0) + (1 if t > 32.8 else 0))

    # ---- Uean: pops up in the noodle-shop window, then writes
    if t > 19.2:
        up = keys([(19.2, 80), (19.9, 0)], t, ease_out)
        pose = (HAMMER if 20.0 < t < 25 else REST)
        if 26 < t < 29.4:
            pose = write_pose(t + 1, 8)
        if 35.4 < t < 36.8:
            pose = pl(REST, HAMMER, seg(t, 35.4, 35.8))
        mouth = max(talk(t, 20.0, 23.0, 9), talk(t, 35.4, 36.8, 10))
        ex_u = "shout" if 20 < t < 23 or 35.4 < t < 36.8 else ("gloat" if t < 26 else "think")
        actor(cv, "uean", 1000, 600 + up, -35, pose, ex_u, k=0.95, mouth=mouth, blink_v=blink(t, 0.2), flip=False)
        if 20.0 < t < 23.0:
            ladle(cv, (968, 470 + up), (940, 430 + up), 10)
    # ---- Ton: eats shaved ice -> tears paper & writes at the counter -> lifts the cup
    walk_t = seg(t, 23.4, 25.6)
    tx = keys([(0, 230), (23.4, 230), (25.6, 540), (60, 540)], t)
    twalk = 23.4 < t < 25.6
    th_ton = 40
    if t < 23.4:
        u = (t % 1.2) / 1.2
        pose = pl(EAT_A, EAT_B, math.sin(u * math.pi) if t < 10.2 else 0.0)
        ex_t = "happy" if t < 10 else exl("surprised", "gape", seg(t, 10.2, 11.0)) if t < 12.4 else "think"
        mouth = talk(t, 10.8, 12.6, 1)
        if 10.2 < t < 10.8:
            pose = pl(EAT_B, STOP, seg(t, 10.2, 10.8))
        elif t >= 10.8:
            pose = pl(STOP, REST, seg(t, 11.0, 13.5))
        actor(cv, "ton", tx, 640, th_ton, pose, ex_t, k=1.15, mouth=mouth, blink_v=blink(t, 0.1))
        if 10.2 <= t < 11.6:
            ice_spray(cv, tx + 28, 520, seg(t, 10.2, 11.6))
    else:
        if twalk:
            ph = walk_ph(t)
            actor(cv, "ton", tx, 640, th_ton, walk_pose(ph), "eager", k=1.15, walk=dict(phase=ph, stride=18, lift=14), lean=5)
        else:
            if t < 29.2:
                pose = write_pose(t) if 26.0 < t < 29.0 else WRITE_A
            elif t < 33.0:
                pose = REST
            else:
                pose = pl(REST, HOLD_UP2, seg(t, 32.8, 33.4))
            ex_t = "think" if t < 29.2 else ("eager" if t < 34 else "shout")
            mouth = talk(t, 33.4, 35.2, 2)
            actor(cv, "ton", tx, 640, th_ton, pose, ex_t, k=1.15, mouth=mouth, blink_v=blink(t, 0.1))
            if t >= 33.0:
                cup(cv, tx + 60, 430 - 20 * seg(t, 33.0, 33.6), 60, 66, slips=3)

    # ---- Chok: walks in carrying a kite frame, strokes the paper, writes, shrugs, thinks
    if t >= 27.0:
        cxk = keys([(27.0, -140), (30.6, 360)], t)
        moving = t < 30.6
        if moving:
            ph = walk_ph(t, 6.5)
            fx = cxk - 150
            cv.stroke([(fx, 470), (fx + 170, 330)], (186, 168, 96), 7)
            cv.fill([(fx + 110, 290), (fx + 160, 345), (fx + 110, 400), (fx + 60, 345)], (250, 244, 232), ink=INK, lw=2.2)
            cv.stroke([(fx + 110, 290), (fx + 110, 400)], (186, 168, 96), 4)
            cv.stroke([(fx + 60, 345), (fx + 160, 345)], (186, 168, 96), 4)
            actor(cv, "chok", cxk, 640, 50, walk_pose(ph, carry=mk(((-62, 150, 10), (-30, 100, 50)))), "neutral", k=1.1,
                  walk=dict(phase=ph, stride=16, lift=12))
        else:
            pose = (pl(REST, WRITE_A, seg(t, 30.8, 31.3)) if t < 31.8 else write_pose(t - 2, 9)) if t < 33.0 else (SHRUG if 36.9 < t < 38.7 else (THINK if t > 40 else REST))
            ex_c = "think" if t < 33 else ("neutral" if t < 36.9 else ("yikes" if t < 38.7 else "think"))
            actor(cv, "chok", 360, 640, 50, pose, ex_c, k=1.1, mouth=talk(t, 37.0, 38.6, 3) or talk(t, 40.2, 42.4, 4), blink_v=blink(t, 0.4))

    cv.pop()
