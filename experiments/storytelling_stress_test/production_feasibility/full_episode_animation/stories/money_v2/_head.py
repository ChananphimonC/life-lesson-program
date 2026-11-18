"""stories/money_v2/story.json : "วิธีมีเงินล้านใน 2 ปี" v2 - rewritten as a friend telling a story (first-person narrator "ผม"), new cast (ตังค์ / จิน / พี่นุ่น / โค้ชทอง), reviewed by Gemini twice before any voice or picture was made
(critique.md, critique_round2.md). Facts and sources as in money_million (savings-bond rate, average household debt, 1207, emergency fund); the story is fiction."""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
STYLE = ("เล่าเรื่องให้เพื่อนฟังตอนกินข้าวด้วยน้ำเสียงผู้ชายสบาย ๆ กวนนิด ๆ เป็นกันเอง เหมือนกำลังนึกขำเรื่องที่ตัวเองเล่า จังหวะพูดเร็วช้าไม่เท่ากัน หยุดนิดก่อนคำตลก "
         "พากย์ตัวละครให้ต่างกัน ตังค์เสียงเหนื่อย ๆ สงสารตัวเอง จินมั่นใจเกินเหตุ พี่นุ่นนิ่งแห้ง ๆ โค้ชทองเสียงดังโอเวอร์ ออกเสียงคำไทยให้ชัด")


def C(who, x, ex="neutral", pose="REST", y=700, k=0.95, flip=None, talk=False, th=None, **kw):
    flip = (x >= 640) if flip is None else flip
    d = dict(who=who, x=x, y=y, k=k, th=th if th is not None else (-30 if flip else 30), flip=flip, ex=ex, pose=pose, talk=talk)
    d.update(kw)
    return d


def P(prop, x, y, s=1.0, at=0.0, z="back", **kw):
    return dict(k=prop, x=x, y=y, s=s, at=at, z=z, kw=kw)


def O(text, x, y, size=80, col=(255, 244, 200), at=0.1):
    return dict(text=text, x=x, y=y, size=size, col=list(col), at=at)


def Bt(at, bg, chars=(), props=(), ov=(), sfx=None, **bgkw):
    b = dict(bg=bg, chars=list(chars), props=list(props), ov=list(ov))
    if at:
        b["at"] = at
    if sfx:
        b["sfx"] = sfx
    if bgkw:
        b["bgkw"] = bgkw
    return b


RED, GRN, GLD, WHT = (255, 110, 100), (130, 235, 150), (255, 220, 100), (255, 255, 255)
T, B, N, K = "tang", "beam", "nun", "coach"
