"""Scene 4a - the challenge (script: ฉาก 4, first part). Ton bargains for the roll, calls the village over the temple loudspeaker, the village
arrives and the roll gets away down the courtyard. ~52 s."""
from acting import *  # noqa: F401,F403
from props import *   # noqa: F401,F403

NAME, DUR = "s4a", 52.0
CAPS = [
    (0.4, 4.4, "ton", "ยาย ถ้าผมพิสูจน์ได้ว่าไม่มีใครพับสี่สิบสองครั้งได้ เกมนี้ก็ไม่ต้องนับสิ"),
    (4.6, 6.0, "kaew", "(ไม่ขยับ) เชิญพิสูจน์"),
    (6.4, 8.4, "ton", "ลุงโชค ผมขอม้วนกระดาษทำว่าว"),
    (8.6, 11.4, "chok", "ม้วนนี้ทำว่าวงานพรุ่งนี้ ยาวร้อยเมตร"),
    (11.6, 15.6, "ton", "ผมขอแค่คืนนี้ ถ้าเสีย ผมช่วยลุงทำว่าวใหม่ทั้งคืน หลังล้างจานเสร็จ"),
    (16.0, 20.6, "chok", "ได้ แต่พับทางเดียว ให้ยาวที่สุดเท่าที่ทำได้ ยกปลายข้ามไปทับ แล้วกดตรงกลาง"),
    (24.0, 29.0, "ton", "(เสียงก้องจากลำโพง) ชาวบ้านทุกคน มาที่ลานวัดด่วน! ผมจะพิสูจน์ว่าพับไม่ได้!"),
    (48.4, 51.4, "chok", "(เสียงแบบครูพละ) พร้อม… พับหนึ่ง!"),
]
CUES = [(20.8, "whoosh", 0.4), (24.2, "mic", 0.5), (24.4, "whoosh", 0.5), (40.0, "paper", 0.8), (41.0, "paper", 0.8), (45.0, "cheer", 0.4), (48.6, "whistle", 0.6)]
CUES += [(21.0 + 0.4 * k, "step", 0.35) for k in range(8)]
CUES += [(30.0 + 0.5 * k, "step", 0.2) for k in range(20)] + [(40.0 + 0.3 * k, "step", 0.15) for k in range(8)]

N_VILL = 14


def draw(cv, t, ov):
    cv.push(0, 0, scale=1.0)
    if t < 21:
        courtyard(cv, 300, "gold", gate_x=150, gate_s=0.6, t=t)
        shop(cv, t, 760, 600, 1.3)
        # Kaew and Uean behind the counter; Ton paces in front, bargains with Chok
        actor(cv, "kaew", 960, 600, -40, REST, "smug", k=0.95, mouth=talk(t, 4.6, 6.0, 1), blink_v=blink(t, .7))
        actor(cv, "uean", 1130, 600, -35, CROSS, "deadpan", k=0.85, blink_v=blink(t, .2))
        shop_counter(cv, 760, 600, 1.3)
        # Ton: pacing 0-6, then turns to Chok
        pace = 560 + 120 * math.sin(t * 1.3) if t < 6.0 else 560
        moving = t < 5.8
        ph = t * 7.0
        if moving:
            facing = 40 if math.cos(t * 1.3) > 0 else 40
            actor(cv, "ton", pace, 665, 40, walk_pose(ph), "determined", k=1.15, walk=dict(phase=ph, stride=10, lift=8), flip=math.cos(t * 1.3) < 0,
                  mouth=talk(t, 0.4, 4.4, 2), blink_v=blink(t, .1))
        else:
            ex_t = "plead" if 11.6 < t < 15.6 else "eager"
            pose = pl(REST, mk(((-84, 130, 20), (-62, 100, 70)), ((84, 130, 20), (62, 100, 70))), seg(t, 11.6, 12.4)) if 11.6 < t < 15.6 else REST
            hands_ = pl(pose, REST, seg(t, 15.6, 16.2)) if t >= 15.6 else pose
            actor(cv, "ton", 560, 665, -35 if False else 40, hands_, ex_t, k=1.15, flip=True, mouth=max(talk(t, 6.4, 8.4, 3), talk(t, 11.6, 15.6, 4)),
                  blink_v=blink(t, .1))
        # Chok arrives with the roll at ~6 s and bargains; they shake hands at 16-18
        cx_ = keys([(5.0, -100), (6.2, 330)], t)
        if t < 6.2:
            ph2 = walk_ph(t, 6.5)
            actor(cv, "chok", cx_, 665, 50, walk_pose(ph2), "neutral", k=1.1, walk=dict(phase=ph2, stride=14, lift=10))
        else:
            pose = SHRUG if 8.6 < t < 11.4 else (mk(((-60, 150, 30), (-26, 150, 100))) if 16.0 < t < 20.0 else REST)
            actor(cv, "chok", 330, 665, 50, pose, "yikes" if 8.6 < t < 11.4 else "smug", k=1.1, mouth=max(talk(t, 8.6, 11.4, 5), talk(t, 16.0, 20.6, 6)),
                  blink_v=blink(t, .4))
        if t > 6.0:
            # the paper roll beside Chok: a big white cylinder
            rx, ry = 215, 640
            cv.ellipse(rx, ry, 52, 52, PAPER, ink=INK, lw=2.6, shade_col=PAPER_SH)
            for kk in (0.72, 0.46, 0.2):
                cv.ellipse(rx, ry, 52 * kk, 52 * kk, PAPER, ink=(190, 188, 178), lw=1.2)
        if 16.0 < t < 20.0:
            u = seg(t, 17.0, 17.8)
            burst(cv, 450, 520, u, 7, 12, 40, (255, 220, 120))                           # a shake on it
    elif t < 34:
        # Ton dashes to the temple speaker; sound rings spread; villagers stream in
        courtyard(cv, 300, "gold", gate_x=150, gate_s=0.6, t=t)
        rect(cv, 900, 160, 920, 650, (150, 108, 76), lw=2.0)                           # speaker pole
        cv.fill([(880, 190), (960, 140), (960, 240), (880, 210)], (200, 200, 208), ink=INK, lw=2.6, shade_col=(168, 168, 176))
        u = seg(t, 24.0, 33.0)
        for k in range(4):
            rr = ((u * 6 + k * 0.25) % 1.0)
            cv.ellipse(930, 190, 30 + 280 * rr, 30 + 280 * rr, (255, 255, 255), ink=(255, 255, 255), lw=3, alpha=0) if False else cv.stroke(
                ellipse_pts(930, 190, 60 + 330 * rr, 60 + 330 * rr, n=40, a0=-70, a1=70), (255, 255, 255), 5, alpha=int(200 * (1 - rr)))
        if t < 24.0:
            tx = keys([(20.8, 560), (23.6, 840)], t)
            ph = t * 11
            actor(cv, "ton", tx, 665, 40, walk_pose(ph), "eager", k=1.15, walk=dict(phase=ph, stride=26, lift=24), lean=12)
        else:
            actor(cv, "ton", 835, 665, 40, pl(REST, mk(((-62, 150, 20), (-30, 120, 100))), seg(t, 23.6, 24.4)), "shout", k=1.15, mouth=talk(t, 24.0, 29.0, 3),
                  blink_v=blink(t, .1))
        for i in range(N_VILL):
            t_in = 25.0 + 0.45 * i
            if t < t_in:
                continue
            side = -1 if i % 2 == 0 else 1
            x_start = -80 if side < 0 else W + 80
            x_end = 150 + (i * 53) % 560
            if i % 2:
                x_end = 680 + (i * 41) % 480
            x = keys([(t_in, x_start), (t_in + 7.0 - (i % 3), x_end)], t, lambda u: u)
            moving = t < t_in + 7.0 - (i % 3)
            mini(cv, x, 580 + (i % 4) * 22, 1.45, i, arms="swing", moving=moving, phase=t * 9 + i, flip=side > 0, expr="grin")
    else:
        # the roll gets away: Chok pushes it, it unrolls the whole length of the courtyard, the village runs after it
        courtyard(cv, 300, "gold", gate_x=1100, gate_s=0.7, t=t)
        u = ease(seg(t, 34.0, 44.0))
        x0, x1, y_ = 140, 1150, 612
        rx = x0 + (x1 - x0) * u
        if u > 0:
            cv.fill([(x0, y_ + 6), (rx, y_ + 6), (rx, y_ - 6), (x0, y_ - 6)], PAPER, ink=INK, lw=2.2)
            for k in range(0, int(rx - x0), 60):
                cv.stroke([(x0 + k, y_ - 6), (x0 + k, y_ + 6)], (214, 212, 202), 1.2)
        ang = (rx - x0) / 40
        cv.ellipse(rx, y_ - 40, 46, 46, PAPER, ink=INK, lw=2.6, shade_col=PAPER_SH)
        for kk in (0.72, 0.46, 0.2):
            cv.ellipse(rx, y_ - 40, 46 * kk, 46 * kk, PAPER, ink=(190, 188, 178), lw=1.2)
        cv.stroke([(rx, y_ - 40), (rx + 40 * math.cos(ang), y_ - 40 + 40 * math.sin(ang))], (200, 198, 188), 2.2)
        if u < 1:
            puff(cv, rx - 20, y_ + 4, 16, (t * 4) % 1.0)
        # runners: Chok, Ton, Uean follow it; villagers fill in along the strip after it stops
        ph = t * 9
        run_x = lambda off: min(rx - off, 1100)
        if u < 1:
            actor(cv, "chok", run_x(150), 690, 50, walk_pose(ph), "yikes", k=0.9, walk=dict(phase=ph, stride=28, lift=26), lean=14)
            actor(cv, "ton", run_x(260), 690, 50, walk_pose(ph + 1), "shout", k=0.9, walk=dict(phase=ph + 1, stride=28, lift=26), lean=14)
            actor(cv, "uean", run_x(380), 690, 50, walk_pose(ph + 2), "gape", k=0.8, walk=dict(phase=ph + 2, stride=26, lift=24), lean=10)
        else:
            wave_ = 0.5 + 0.5 * math.sin(t * 4.2)                                   # the waiting crowd never freezes: breathing, blinks, hops
            chok_arms = pl(pl(REST, ARMS_UP, seg(t, 44.0, 44.6)), CHEER, wave_ * seg(t, 46.0, 46.8)) if t > 46.0 else pl(REST, ARMS_UP, seg(t, 44.0, 44.6))
            actor(cv, "chok", 980, 690, 50, chok_arms, "shout" if t > 48.2 else "smug", k=0.9, mouth=talk(t, 48.4, 51.4, 5), blink_v=blink(t, .4),
                  lean=1.5 * math.sin(t * 2.0), bob=2 * abs(math.sin(t * 4.2)))
            actor(cv, "ton", 840, 690, 50, pl(REST, HEADS, seg(t, 44.0, 44.6)), "gape" if t < 47.0 else "yikes", k=0.9, blink_v=blink(t, .1),
                  lean=1.2 * math.sin(t * 2.6 + 1), bob=1.5 * abs(math.sin(t * 3.1)))
            actor(cv, "uean", 700, 690, 50, pl(REST, CROSS, seg(t, 44.0, 44.8)), "smug", k=0.8, blink_v=blink(t, .2), lean=1.0 * math.sin(t * 2.2 + 2))
        for i in range(N_VILL):
            frac = (i + 1) / (N_VILL + 1)
            vx = x0 + (x1 - x0) * frac
            if vx < rx - 30 or True:
                vx_now = min(vx, rx - 40) if u < 1 else vx
                if t > 34 + 1.2 * frac:
                    hop = 0.0 if u < 1 else 7 * abs(math.sin(t * 5.5 + i * 1.7)) * seg(t, 45.0, 46.0)                      # cheering hops
                    mini(cv, vx_now - 20 * (i % 2), 636 + 14 * (i % 3) - hop, 1.1, i, arms="up" if u >= 1 else "swing", moving=u < 1, phase=t * 10 + i, expr="grin")
    cv.pop()
