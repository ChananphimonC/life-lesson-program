import sys
from engine import *
from PIL import Image

out = Image.new("RGB", (4 * 480, 2 * 320), (255, 255, 255))
for n in range(8):
    cv = new_canvas()
    cv.fill([(0, 0), (W, 0), (W, H), (0, H)], (232, 212, 170), ink=None)
    ph = n / 8 * 2 * math.pi
    actor(cv, "ton", 300, 600, 55, walk_pose(ph), "happy", k=1.4, walk=dict(phase=ph, stride=18, lift=14), lean=6)
    actor(cv, "chok", 640, 600, 55, walk_pose(ph + 1), "neutral", k=1.1, walk=dict(phase=ph + 1, stride=16, lift=12))
    actor(cv, "uean", 960, 600, -55, walk_pose(ph * 2), "shout" if False else "eager", k=1.1, flip=True,
          walk=dict(phase=ph * 2, stride=26, lift=22), lean=10)
    im = cv.result().convert("RGB").resize((480, 320))
    out.paste(im, ((n % 4) * 480, (n // 4) * 320))
out.save(sys.argv[1])
