"""Dog + room test sheets -> stories/dog_day/sheet_dog.png, sheet_rooms.png"""
from pathlib import Path
from PIL import Image
import pup_props as PP
from acting import *  # noqa: F401,F403

OUT = Path(__file__).resolve().parent / "stories" / "dog_day"
OUT.mkdir(parents=True, exist_ok=True)

def render(draw, size=(640, 360)):
    cv = new_canvas(ss=1)
    draw(cv)
    return cv.result().convert("RGB").resize(size)

poses = [("sit", "happy"), ("sit", "sad"), ("stand", "alert"), ("walk", "neutral"), ("run", "joy"), ("lie", "sad"), ("sleep", "sleepy"), ("jump", "joy"), ("beg", "happy"), ("sit", "worry"), ("lie", "sulk"), ("stand", "joy")]
tiles = []
for i, (p, e) in enumerate(poses):
    def d(cv, p=p, e=e, i=i):
        cv.fill([(0, 0), (1280, 0), (1280, 720), (0, 720)], (250, 240, 224), ink=None)
        PP.dog(cv, 640, 560, 3.2, 1.3 + i * 0.1, pose=p, ex=e, hold="unicorn" if i == 9 else None)
    tiles.append(render(d))
sheet = Image.new("RGB", (640 * 4, 360 * 3))
for i, im in enumerate(tiles):
    sheet.paste(im, ((i % 4) * 640, (i // 4) * 360))
sheet.save(OUT / "sheet_dog.png")
rooms = ["pup_bedroom", "pup_living", "pup_rain", "pup_under_bed", "pup_table", "pup_night", "pup_soi"]
import fin_props as FP
tiles = []
for r in rooms:
    def d(cv, r=r):
        FP.REG_BG[r](cv, 1.0)
        if r == "pup_rain":
            PP.bolt(cv, 700, 80, 1.0, 0.05)
        PP.dog(cv, 640, 640, 2.2, 1.0, pose="sit" if r != "pup_under_bed" else "lie", ex="sad" if r in ("pup_rain", "pup_under_bed") else "happy", hold="unicorn" if r == "pup_under_bed" else None)
        if r == "pup_living":
            PP.bowl(cv, 300, 640, 1.6, 1.0); PP.ball(cv, 420, 650, 1.4, 1.0)
        if r == "pup_bedroom":
            PP.unicorn(cv, 960, 640, 1.8, 1.0)
        if r == "pup_soi":
            PP.bike(cv, 420, 620, 1.8, 1.0)
    tiles.append(render(d))
sheet = Image.new("RGB", (640 * 4, 360 * 2))
for i, im in enumerate(tiles):
    sheet.paste(im, ((i % 4) * 640, (i // 4) * 360))
sheet.save(OUT / "sheet_rooms.png")
print("ok")
