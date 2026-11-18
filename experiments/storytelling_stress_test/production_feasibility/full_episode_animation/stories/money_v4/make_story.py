"""stories/money_v4/story.json : EP12 "เงินล้านใน 2 ปี ทำได้จริงไหม (แบบไม่โดนหลอก)" v4 - a DIALOGUE episode: no narrator, every character speaks in their own voice
(Tang = Umbriel male, Jin = Zephyr female, Nun = Gacrux female, Coach = Orus male). One scene = one Gemini multi-speaker request (max two voices per request), so each
scene has two speakers. Changes from v3 (user review 2026-11-16): Jin is now a woman with a new look (lavender bob, butterfly clips); nothing narrates gestures or outfits;
the 'แวะไปทักทายใคร' line and other AI-sounding lines are gone; numbers are self-consistent (savings-bond rate ~1.8%/yr: 10,000 THB a month for 24 months earns about 4,300 THB);
on-screen text is white and static. Facts/sources as in money_million; the story is fiction."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
VOICES = {"Tang": "Umbriel", "Jin": "Zephyr", "Nun": "Gacrux", "Coach": "Orus"}
WHO = {"Tang": "tang", "Jin": "jin", "Nun": "nun", "Coach": "coach"}
STYLE = "Thai dialogue, natural spoken delivery with real emotion"


def C(who, x, ex="neutral", pose="REST", y=700, k=0.95, flip=None, talk=False, th=None, **kw):
    flip = (x >= 640) if flip is None else flip
    d = dict(who=who, x=x, y=y, k=k, th=th if th is not None else (-30 if flip else 30), flip=flip, ex=ex, pose=pose, talk=talk)
    d.update(kw)
    return d


def P(prop, x, y, s=1.0, at=0.0, z="back", **kw):
    return dict(k=prop, x=x, y=y, s=s, at=at, z=z, kw=kw)


def O(text, x, y, size=64, at=0.1):
    return dict(text=text, x=x, y=y, size=size, col=[255, 255, 255], at=at)


def Bt(at, bg, chars=(), props=(), ov=(), sfx=None, **bgkw):
    b = dict(bg=bg, chars=list(chars), props=list(props), ov=list(ov))
    if at:
        b["at"] = at
    if sfx:
        b["sfx"] = sfx
    if bgkw:
        b["bgkw"] = bgkw
    return b


def L(spk, text, ex="neutral", pose="REST", lis_ex="deadpan", lis_pose="REST", ov=(), props=None, bg=None, bgkw=None, sfx=None):
    return dict(spk=spk, text=text, ex=ex, pose=pose, lis_ex=lis_ex, lis_pose=lis_pose, ov=list(ov), props=props, bg=bg, bgkw=bgkw or {}, sfx=sfx)


def scene(name, direction, bg, cast, base_props, lines, bgkw=None, extra_chars=()):
    """cast: {"Tang": x, ...} two speakers. One stage beat per line (very short lines such as 'อืม' ride on the previous beat)."""
    text = " ".join(l["text"] for l in lines)
    stage, used = [], []
    for i, l in enumerate(lines):
        if i and len(l["text"]) < 7:
            continue
        chars = []
        for who, x in cast.items():
            sp = who == l["spk"]
            chars.append(C(WHO[who], x, ex=l["ex"] if sp else l["lis_ex"], pose=l["pose"] if sp else l["lis_pose"], talk=sp))
        chars += list(extra_chars)
        marker = ""
        if stage:
            for n in range(14, 40):
                marker = l["text"][:n]
                if text.count(marker) == 1:
                    break
            assert text.count(marker) == 1 and len(marker) >= 6, (name, l["text"])
        b = Bt(marker, l["bg"] or bg, chars, l["props"] if l["props"] is not None else base_props, l["ov"], sfx=l["sfx"], **({**(bgkw or {}), **l["bgkw"]}))
        stage.append(b)
    return dict(name=name, direction=direction, lines=[dict(speaker=l["spk"], text=l["text"], say=l["text"]) for l in lines], stage=stage)


SC = []
RED, GRN = None, None

# ------------------------------------------------------------------------------------------------------------------------------------- 1 cafe: broke
SC.append(scene("1 broke",
    "Read this as a natural, funny Thai conversation between two best friends at a cafe, with real emotion and everyday speech rhythm, never like reading aloud. "
    "Tang is a broke 24-year-old guy: tired, self-pitying, dry humor. Jin is his bubbly best friend, a young woman: fast, confident, easily excited. Pronounce every Thai word clearly.",
    "cafe", {"Tang": 330, "Jin": 950}, [P("tea", 640, 660, 1.6)], [
    L("Jin", "เฮ้ย ตังค์ เงินเดือนเพิ่งออกเมื่อวานไม่ใช่เหรอ วันนี้เลี้ยงข้าวหน่อยดิ", "eager", "POINT_FWD", "deadpan", sfx="pop", ov=[O("เงินเดือนออกเมื่อวาน", 640, 120, 60, 0.2)]),
    L("Tang", "เลี้ยงไม่ได้ ฉันเพิ่งเปิดแอปธนาคาร เหลือสามร้อยแปดสิบเจ็ดบาท", "worried", "HEADS", "gape", ov=[O("387 บาท", 640, 130, 110, 0.3)], sfx="sigh"),
    L("Jin", "หา! เมื่อวานเพิ่งออกนะ หายไปไหนหมดอะ", "gape", "SHRUG", "worried"),
    L("Tang", "ฉันนั่งไล่ดูเมื่อเช้า ค่าห้อง ค่าผ่อนมือถือ ค่าเน็ต แล้วก็ชานมที่ฉันไม่รู้ว่าซื้อตอนไหน", "plead", "SHRUG", "think"),
    L("Jin", "ชานมวันละแก้ว ก็เดือนละพันแปดแล้วนะ", "aha", "POINT_UP", "yikes", ov=[O("ชานมวันละแก้ว = 1,800 / เดือน", 640, 120, 54, 0.2)]),
    L("Tang", "อย่าคิดเลขต่อหน้าฉัน ฉันเศร้าอยู่", "worried", "HEADS", "laugh", sfx="laugh"),
    L("Jin", "งั้นทำไงอะ จะจนไปตลอดเลยเหรอ", "worried", "REST", "worried"),
    L("Tang", "ไม่ ฉันตัดสินใจแล้ว ฉันจะมีเงินล้านภายในสองปี", "eager", "POINT_UP", "gape", ov=[O("เงินล้านใน 2 ปี", 640, 120, 90, 0.2)], sfx="ding"),
    L("Jin", "เออ! ตรงกับที่ฉันเจอพอดี เสาร์นี้มีสัมมนา ล้านแรกสามสิบวัน เข้าฟรีด้วย", "shout", "ARMS_UP", "gape", ov=[O("ล้านแรก 30 วัน  เข้าฟรี", 640, 120, 66, 0.2)], sfx="cheer"),
    L("Tang", "สามสิบวันเนี่ยนะ แล้วเธอรู้ได้ไงว่ามันได้จริง", "think", "THINK", "eager"),
    L("Jin", "ฉันศึกษามาแล้วนะ คลิปสี่สิบห้าวินาที ดูไปสามรอบ", "smug", "POINT_UP", "deadpan", ov=[O("คลิป 45 วินาที ดู 3 รอบ", 640, 120, 62, 0.2)], sfx="pop"),
    L("Tang", "...ฟรีใช่ไหม ไปก็ได้", "deadpan", "CROSS", "laugh")]))

# ------------------------------------------------------------------------------------------------------------------------------------- 2 seminar
SC.append(scene("2 seminar",
    "A loud, over-the-top get-rich-quick seminar. Coach is a hyped, smooth-talking man shouting like a TV host, dodging every question. Tang is a tired, polite, skeptical young man asking short questions. "
    "Natural comedic timing, clear Thai pronunciation.",
    "conference", {"Tang": 330, "Coach": 950}, [P("spotlight", 950, 0), P("board", 640, 340, 1.4)], [
    L("Coach", "สวัสดีครับพี่น้อง! ใครอยากรวยยกมือขึ้น!", "shout", "ARMS_UP", "deadpan", ov=[O("สัมมนาฟรี!", 640, 110, 90, 0.2)], sfx="cheer"),
    L("Coach", "ล้านแรกสามสิบวัน ผลตอบแทนการันตี! แล้วถ้าชวนเพื่อนมาอีกคน ได้ค่าแนะนำด้วย!", "shout", "ARMS_UP", "worried",
      ov=[O("ล้านแรก 30 วัน", 640, 100, 66, 0.1), O("ผลตอบแทนการันตี", 640, 180, 66, 0.4), O("ชวนเพื่อน = ได้ค่าแนะนำ", 640, 260, 54, 0.65)], sfx="pop"),
    L("Tang", "ขอถามหน่อยครับพี่", "neutral", "POINT_UP", "smug"),
    L("Coach", "ถามได้เลยน้องชาย พี่เปิดกว้าง", "smug", "SPREAD", "deadpan"),
    L("Tang", "ถ้าผลตอบแทนการันตีขนาดนี้ ทำไมพี่ไม่ลงทุนเองคนเดียวเลยล่ะครับ", "think", "POINT_UP", "smug", ov=[O("ทำไมพี่ไม่ลงทุนเองคนเดียว?", 640, 110, 56, 0.2)]),
    L("Coach", "ฮ่า ๆ ๆ เพราะพี่อยากแบ่งปันโอกาสให้ทุกคนไงครับ", "laugh", "SHRUG", "deadpan", sfx="laugh"),
    L("Tang", "อ๋อ แล้วพี่แบ่งกำไรให้พวกผมด้วยไหมครับ", "smug", "CROSS", "worried", ov=[O("แบ่งกำไรให้ด้วยไหม?", 640, 110, 60, 0.2)]),
    L("Coach", "...ทุกท่านครับ! วันนี้โอนวันนี้ ลดครึ่งราคา!", "shout", "ARMS_UP", "deadpan", ov=[O("โอนวันนี้ ลดครึ่งราคา!", 640, 110, 66, 0.2)], sfx="gasp"),
    L("Tang", "พี่ครับ ผมถามเรื่องกำไร", "plead", "POINT_FWD", "shout"),
    L("Coach", "โอนวันนี้ลดครึ่งราคาครับ! ทุกท่านปรบมือ!", "shout", "CHEER", "yikes", sfx="cheer")]))

# ------------------------------------------------------------------------------------------------------------------------------------- 3 red flags
SC.append(scene("3 red flags",
    "Two friends walking out of a seminar, on the street. Tang is calm, counting things dryly, a bit alarmed. Jin is a bubbly young woman who believed everything and is getting defensive, then sheepish. "
    "Natural, quick, funny, clear Thai pronunciation.",
    "street", {"Tang": 330, "Jin": 950}, [], [
    L("Tang", "จิน เมื่อกี้พี่เขาพูดคำว่า การันตี ไปสิบสองรอบ", "worried", "POINT_UP", "eager", ov=[O("'การันตี' 12 รอบ", 640, 120, 70, 0.2)]),
    L("Jin", "ก็ดีสิ แปลว่าชัวร์", "smug", "SHRUG", "deadpan"),
    L("Tang", "ฉันนับธงแดงได้สามผืน การันตีผลตอบแทน ได้เร็วเกินจริง แล้วยังให้ชวนเพื่อน", "shout", "POINT_FWD", "gape",
      props=[P("flag", 560, 620, 1.8), P("flag", 680, 620, 1.4), P("flag", 800, 620, 1.8)], ov=[O("ธงแดง x 3", 640, 120, 100, 0.2)], sfx="ding"),
    L("Jin", "แต่ฉันจองคอร์สไปแล้วนะ สามหมื่นบาท", "plead", "HEADS", "yikes", ov=[O("จองแล้ว 30,000 บาท", 640, 120, 66, 0.2)]),
    L("Tang", "หา! แล้วทำไมเพิ่งบอก", "gape", "HEADS", "worried", sfx="gasp"),
    L("Jin", "ก็เขาบอกว่าถ้าบอกคนอื่นก่อนโอน โชคจะไม่มา", "plead", "SHRUG", "deadpan"),
    L("Tang", "...นั่นธงแดงผืนที่สี่", "deadpan", "CROSS", "worried", props=[P("flag", 520, 620, 1.8), P("flag", 640, 620, 1.4), P("flag", 760, 620, 1.8), P("flag", 880, 620, 1.4)], ov=[O("ธงแดง x 4", 640, 120, 100, 0.2)], sfx="laugh"),
    L("Tang", "ก่อนโอนอะไร เช็กใบอนุญาตกับ ก.ล.ต. ก่อนนะ หรือโทรหนึ่งสองศูนย์เจ็ด", "aha", "POINT_UP", "worried",
      props=[P("shield", 640, 600, 1.8)], ov=[O("เช็กใบอนุญาต ก.ล.ต.", 640, 110, 60, 0.2), O("สายด่วน 1207", 640, 190, 70, 0.5)], sfx="chime"),
    L("Jin", "ก็ได้ แต่ถ้าสัมมนาจริง ฉันจะไม่คุยกับเธอสามวัน", "plead", "CROSS", "smug", sfx="laugh")]))

# ------------------------------------------------------------------------------------------------------------------------------------- 4 napkin
SC.append(scene("4 napkin",
    "A dry, deadpan older cousin who works at a bank (Nun) and her broke young cousin (Tang) eating at a pork-and-garlic rice shop. Nun speaks in short flat sentences with almost no emotion, a quiet dry sense of humor. "
    "Tang is tired and anxious. Natural conversation, clear Thai pronunciation, numbers spoken clearly.",
    "grill", {"Tang": 330, "Nun": 950}, [P("steam", 640, 470, 1.6)], [
    L("Tang", "พี่นุ่นครับ ผมมีปัญหาเรื่องเงิน", "plead", "SHRUG", "deadpan", ov=[O("ปัญหาเรื่องเงิน", 640, 120, 66, 0.2)]),
    L("Nun", "พี่ก็มี ต้องมานั่งกินข้าวกับแกนี่แหละ", "gloat", "CROSS", "gape", sfx="laugh"),
    L("Tang", "ร้านเดิมนะครับ ข้าวหมูกระเทียมหน้าธนาคาร", "neutral", "REST", "deadpan"),
    L("Nun", "ใครเลี้ยง", "deadpan", "POINT_FWD", "plead", ov=[O("ใครเลี้ยง?", 640, 120, 80, 0.2)]),
    L("Tang", "ผมมีสามร้อยแปดสิบเจ็ดบาทครับ", "worried", "HEADS", "deadpan", ov=[O("387 บาท", 640, 120, 100, 0.2)]),
    L("Nun", "พอ หนึ่งล้านบาท หารยี่สิบสี่เดือน เท่ากับสี่หมื่นหนึ่งพันหกร้อยหกสิบเจ็ดบาทต่อเดือน", "deadpan", "WRITE_A", "worried", bg="calc",
      props=[], ov=[O("1,000,000 ÷ 24 เดือน", 800, 190, 62, 0.15), O("= 41,667 บาท / เดือน", 800, 300, 76, 0.5)], sfx="ding"),
    L("Tang", "ผมเงินเดือนสองหมื่น ต่อให้ไม่กินไม่ใช้ ก็ได้แค่ครึ่งเดียว", "yikes", "HEADS", "deadpan", ov=[O("เงินเดือน 20,000  ได้แค่ครึ่งเดียว", 640, 120, 56, 0.2)]),
    L("Nun", "อืม", "deadpan", "CROSS", "worried"),
    L("Tang", "งั้นให้ดอกเบี้ยช่วยได้ไหมครับ", "eager", "POINT_UP", "deadpan"),
    L("Nun", "พันธบัตรออมทรัพย์ตอนนี้ดอกเบี้ยประมาณหนึ่งจุดแปดต่อปี ถ้าแกเก็บเดือนละหนึ่งหมื่นทุกเดือน สองปี ดอกเบี้ยรวมได้ประมาณสี่พันสามร้อยบาท", "deadpan", "POINT_UP", "gape", bg="calc",
      props=[], ov=[O("พันธบัตร ≈ 1.8% / ปี", 800, 150, 56, 0.1), O("เก็บเดือนละ 10,000 นาน 2 ปี", 800, 240, 52, 0.35), O("ดอกเบี้ยรวม ≈ 4,300 บาท", 800, 340, 66, 0.65)], sfx="chime"),
    L("Tang", "สี่พันกว่าบาท ในสองปี", "gape", "HEADS", "deadpan"),
    L("Nun", "ชานมไข่มุกประมาณเจ็ดสิบแก้ว", "gloat", "POINT_FWD", "yikes", props=[P("tea", 640, 660, 1.5), P("tea", 740, 660, 1.5)], ov=[O("ชานมไข่มุก ≈ 70 แก้ว", 640, 120, 66, 0.2)], sfx="laugh"),
    L("Tang", "...ผมสั่งเดือนละสามสิบแก้วอยู่แล้วครับ", "worried", "SHRUG", "gloat"),
    L("Nun", "ล้านแรกไม่ได้มาจากดอกเบี้ย มันมาจากการเก็บให้ได้เยอะ กับหาให้ได้เพิ่ม", "deadpan", "POINT_UP", "aha", bg="calc", props=[],
      ov=[O("เก็บให้ได้เยอะ", 800, 200, 76, 0.1), O("+ หาให้ได้เพิ่ม", 800, 310, 76, 0.5)], sfx="chime")]))

# ------------------------------------------------------------------------------------------------------------------------------------- 5 leaks
SC.append(scene("5 leaks",
    "Nun (dry, deadpan, older cousin working at a bank, short flat sentences) reviews the spending of Tang (tired, embarrassed, a little defensive but honest) over a rice dish. "
    "Quiet dry humor, natural pacing, clear Thai pronunciation.",
    "grill", {"Tang": 330, "Nun": 950}, [P("steam", 640, 470, 1.6)], [
    L("Nun", "เปิดรายจ่ายเดือนที่แล้วมาดู", "deadpan", "POINT_FWD", "worried"),
    L("Tang", "ชานมวันละแก้ว สั่งข้าวมากินแทบทุกวัน แล้วก็ผ่อนมือถือเครื่องใหม่ ศูนย์เปอร์เซ็นต์สิบเดือน", "worried", "HEADS", "deadpan", bg="mall",
      props=[P("tea", 700, 660, 2.0), P("box", 900, 660, 1.6), P("phone", 1080, 660, 1.2)], ov=[O("ผ่อน 0% 10 เดือน", 640, 120, 70, 0.4)]),
    L("Nun", "ผ่อนเดือนละเท่าไหร่", "deadpan", "POINT_FWD", "plead"),
    L("Tang", "สามพันครับ แต่ไม่มีดอกเบี้ยนะพี่", "plead", "SHRUG", "deadpan", ov=[O("3,000 / เดือน  ไม่มีดอกเบี้ย", 640, 120, 56, 0.2)]),
    L("Nun", "ไม่มีดอกเบี้ย แต่ต้องจ่ายสามพันทุกเดือนเหมือนกัน", "gloat", "POINT_FWD", "yikes", ov=[O("ไม่มีดอกเบี้ย  แต่ต้องจ่ายทุกเดือน", 640, 120, 54, 0.2)], sfx="laugh"),
    L("Tang", "...ผมไม่เคยคิดแบบนี้เลย", "worried", "HEADS", "deadpan"),
    L("Nun", "ไม่เป็นไร พี่เขียนกฎให้ สามข้อ หนึ่ง ลบแอปช้อปปิ้ง สอง ของที่อยากได้ ให้รอสามวัน ถ้าสามวันแล้วยังอยากได้ค่อยซื้อ ถ้าสามวันแล้วยังไม่มีเงิน ก็จบ สาม เงินเดือนออกวันไหน โอนเก็บก่อนวันนั้นเลย",
      "deadpan", "WRITE_A", "worried", bg="calc", props=[],
      ov=[O("1 ลบแอปช้อปปิ้ง", 800, 150, 62, 0.1), O("2 ของที่อยากได้ รอ 3 วัน", 800, 250, 56, 0.35), O("3 เงินเดือนออก โอนเก็บก่อน", 800, 350, 54, 0.65)], sfx="ding"),
    L("Tang", "ลบแอปเลยเหรอครับ ตอนนี้เลย", "plead", "POINT_UP", "deadpan"),
    L("Nun", "ตอนนี้", "deadpan", "POINT_FWD", "plead"),
    L("Tang", "...แอปมันถามว่า จะทิ้งโปรสิบเอ็ดสิบเอ็ดจริงเหรอคะ", "worried", "HEADS", "deadpan", bg="bedroom", props=[P("phone", 900, 560, 1.4, screen=(250, 120, 90))],
      ov=[O("จะทิ้งโปร 11.11 จริงเหรอคะ?", 640, 120, 56, 0.2)], bgkw=dict(night=0.6)),
    L("Nun", "กดตกลง", "deadpan", "STOP", "plead", ov=[O("กดตกลง", 640, 120, 90, 0.2)]),
    L("Tang", "กดแล้วครับ ...มือสั่น", "yikes", "HEADS", "gloat", sfx="thump")]))

# ------------------------------------------------------------------------------------------------------------------------------------- 6 levels
SC.append(scene("6 levels",
    "At a table, Jin (a bubbly young woman who learns money rules from short videos, proud and quick-talking, then gets embarrassed) talks with Nun (dry, deadpan older cousin working at a bank, short flat sentences, quiet humor). "
    "Natural conversation, clear Thai pronunciation, numbers clearly.",
    "grill", {"Jin": 330, "Nun": 950}, [P("steam", 640, 470, 1.6)], [
    L("Jin", "เฮ้ย ฉันมีวิธีรวยใหม่! กฎห้าสิบสามสิบยี่สิบ ห้าสิบใช้จ่าย สามสิบของที่อยากได้ ยี่สิบเก็บ ทำตามนี้ก็รวยแล้ว", "eager", "POINT_UP", "deadpan", ov=[O("กฎ 50 / 30 / 20", 640, 120, 80, 0.2)], sfx="pop"),
    L("Nun", "ยี่สิบเปอร์เซ็นต์ของสองหมื่น คือเดือนละสี่พัน สองปีได้เก้าหมื่นหกพัน", "deadpan", "WRITE_A", "aha", bg="calc", props=[],
      ov=[O("20% x 20,000 = 4,000", 800, 190, 62, 0.1), O("x 24 เดือน = 96,000", 800, 300, 66, 0.45)]),
    L("Jin", "ก็เกือบแสนแล้วนะ!", "shout", "CHEER", "deadpan", sfx="cheer"),
    L("Nun", "แล้วล้านล่ะ", "deadpan", "POINT_FWD", "plead", ov=[O("แล้วล้านล่ะ?", 640, 120, 100, 0.2)], sfx="gasp"),
    L("Jin", "เอ่อ... ก็ค่อย ๆ โตไง", "plead", "SHRUG", "deadpan"),
    L("Nun", "สูตรนี้ดีนะ แต่มันไม่ได้เสกเงินให้เพิ่ม เก็บเดือนละสี่พัน อีกสองปีก็ยังไม่ถึงล้าน", "deadpan", "POINT_UP", "worried", ov=[O("เก็บเดือนละ 4,000  อีก 2 ปีก็ยังไม่ถึงล้าน", 640, 120, 50, 0.2)]),
    L("Nun", "ถามหน่อย เธอมีเงินสำรองฉุกเฉินหรือยัง", "deadpan", "POINT_FWD", "eager", ov=[O("เงินสำรองฉุกเฉิน?", 640, 120, 66, 0.2)]),
    L("Jin", "มีค่ะ!", "happy", "CHEER", "deadpan"),
    L("Nun", "เท่าไหร่", "deadpan", "CROSS", "smug"),
    L("Jin", "สองร้อยห้าสิบบาท", "plead", "SHRUG", "deadpan", ov=[O("250 บาท", 640, 120, 100, 0.2)]),
    L("Nun", "นั่นเงินสำรอง หรือค่าข้าวพรุ่งนี้", "gloat", "POINT_FWD", "yikes", sfx="laugh"),
    L("Jin", "...ค่าข้าว", "worried", "HEADS", "gloat"),
    L("Nun", "เก็บเงินสำรองก่อน อย่างน้อยค่าใช้จ่ายสามเดือน เคลียร์หนี้ดอกแพงก่อน แล้วที่เหลือค่อยกระจายลงทุน", "deadpan", "POINT_UP", "worried", bg="desk",
      props=[P("lock", 860, 620, 1.8)], ov=[O("เงินสำรอง ≥ 3 เดือนก่อน", 640, 110, 56, 0.1), O("เคลียร์หนี้ดอกแพง", 640, 190, 56, 0.4), O("ที่เหลือค่อยกระจายลงทุน", 640, 270, 54, 0.65)], bgkw=dict(dusk=0.3)),
    L("Jin", "ถ้าฉันเอาทั้งหมดไปซื้อหุ้นที่เพื่อนแนะนำล่ะ", "plead", "POINT_UP", "deadpan"),
    L("Nun", "ก็เตรียมได้เพื่อนใหม่", "gloat", "POINT_FWD", "gape"),
    L("Jin", "ใครอะ", "gape", "SHRUG", "gloat"),
    L("Nun", "เจ้าหนี้", "deadpan", "CROSS", "yikes", ov=[O("เจ้าหนี้", 640, 120, 110, 0.2)], sfx="laugh")]))

# ------------------------------------------------------------------------------------------------------------------------------------- 7 income + AI
SC.append(scene("7 income",
    "Nun (dry, deadpan older cousin at a bank, short flat sentences, quiet humor) pushes Tang (tired but now determined, a little proud, self-mocking) to earn more. "
    "Natural, a bit funny, real emotion in Tang's story about fixing a bad machine translation until 2 a.m. Clear Thai pronunciation.",
    "cowork", {"Tang": 330, "Nun": 950}, [], [
    L("Nun", "ตังค์ เก็บเก่งอย่างเดียวไม่พอ เงินเดือนสองหมื่นไม่มีทางไปถึงล้านภายในสองปี ต้องหารายได้เพิ่ม", "deadpan", "POINT_UP", "worried", ov=[O("เก็บเก่งอย่างเดียวไม่พอ", 640, 120, 62, 0.2)]),
    L("Nun", "แกทำอะไรเป็นบ้าง ที่คนอื่นยอมจ่ายเงินให้", "deadpan", "POINT_FWD", "think"),
    L("Tang", "ผมแปลภาษาได้ ทำสไลด์เป็น แล้วก็ต้มมาม่าไม่ให้แฉะ", "think", "THINK", "deadpan", ov=[O("แปลภาษา", 640, 110, 70, 0.2), O("ทำสไลด์", 640, 190, 70, 0.45)], sfx="ding"),
    L("Nun", "เอาสองอย่างแรกก่อน", "deadpan", "CROSS", "laugh"),
    L("Tang", "คืนนั้นผมรับงานแปลมาหนึ่งชิ้น ใช้เอไอช่วยร่าง แล้วนั่งตรวจทีละประโยค", "eager", "WRITE_A", "deadpan", bg="desk", props=[P("laptop", 700, 590, 1.6, z="front"), P("robot", 1000, 640, 1.6)], bgkw=dict(dusk=1.0),
      ov=[O("เอไอร่าง → ตังค์ตรวจทีละประโยค", 640, 110, 46, 0.2)]),
    L("Tang", "เจอประโยคหนึ่ง เอไอแปลผิดจนความหมายกลับตาลปัตร ถ้าผมส่งไปแบบนั้น ลูกค้าคงไม่จ้างแปล คงจ้างทนายแทน", "yikes", "HEADS", "deadpan", bg="desk",
      props=[P("laptop", 700, 590, 1.6, z="front"), P("robot", 1000, 640, 1.6, mood="worried")], bgkw=dict(dusk=1.0), ov=[O("เอไอแปลผิด!", 640, 110, 90, 0.2)], sfx="gasp"),
    L("Nun", "แล้วทำไง", "deadpan", "POINT_FWD", "plead"),
    L("Tang", "นั่งแก้ทีละประโยคจนตีสอง ส่งตอนเช้า ลูกค้าจ่ายสามพันบาท", "happy", "CHEER", "deadpan", bg="calc", props=[P("bills", 900, 600, 2.0, n=3)], ov=[O("ตี 2 ยังแก้งานอยู่", 640, 110, 56, 0.1), O("+3,000 บาท", 640, 210, 100, 0.5)], sfx="chime"),
    L("Nun", "โอนเข้าบัญชีเก็บ ทั้งก้อน", "deadpan", "POINT_FWD", "plead"),
    L("Tang", "ผมอยากซื้อรองเท้านะพี่", "plead", "SHRUG", "deadpan"),
    L("Nun", "อยากมีรองเท้า หรืออยากมีเงิน", "gloat", "POINT_UP", "yikes", ov=[O("อยากมีรองเท้า หรืออยากมีเงิน?", 640, 120, 54, 0.2)]),
    L("Tang", "...อยากมีเงิน ตอนนี้", "smug", "POINT_FWD", "gloat", bg="desk", props=[P("piggy", 860, 600, 1.8)], bgkw=dict(dusk=0.8), ov=[O("อยากมีเงินมากกว่าอยากมีของ", 640, 120, 54, 0.2)], sfx="pop")]))

# ------------------------------------------------------------------------------------------------------------------------------------- 8 one year later
SC.append(scene("8 one year later",
    "Tang (now calmer, quietly proud, dry humor, a little teasing) and his bubbly best friend Jin (a young woman who is still easily tempted, defensive then sheepish) talk over the phone and in person, one year later. "
    "Natural, warm, funny, clear Thai pronunciation. Tang ends by talking to the audience.",
    "bedroom", {"Tang": 330, "Jin": 950}, [P("phone", 640, 560, 1.4, screen=(40, 190, 120))], [
    L("Tang", "จิน ผ่านมาหนึ่งปีแล้ว ฉันเก็บได้สองแสนกว่า เงินสำรองครบ ผ่อนมือถือหมดแล้ว", "happy", "CHEER", "eager", bg="calc", props=[P("calendar", 900, 600, 1.8)], ov=[O("1 ปีผ่านไป  เก็บได้ 200,000+", 640, 110, 60, 0.2)], sfx="chime"),
    L("Jin", "แล้วล้านล่ะ", "plead", "SHRUG", "smug", ov=[O("แล้วล้านล่ะ?", 640, 110, 90, 0.2)]),
    L("Tang", "ยังห่างอยู่ แต่ปีที่สองงานเสริมโตขึ้น รวมสองปีเก็บได้ห้าแสนกว่า ถ้าเก็บแบบนี้ต่อ ล้านแรกน่าจะมาในสามปีครึ่ง", "aha", "POINT_UP", "worried", bg="calc",
      props=[P("chart", 900, 600, 2.0, kind="up")], ov=[O("2 ปี ≈ 500,000+", 640, 110, 66, 0.15), O("ถึงล้าน ≈ 3 ปีครึ่ง", 640, 200, 66, 0.5)], sfx="chime"),
    L("Jin", "ช้าจัง! ฉันเจอสัมมนาใหม่ รวยในสิบห้าวัน ถูกกว่าเดิมครึ่งราคา", "shout", "ARMS_UP", "yikes", ov=[O("รวยใน 15 วัน  ครึ่งราคา!", 640, 110, 66, 0.2)], sfx="cheer"),
    L("Tang", "จิน ใครรายได้สูงอยู่แล้ว หรือหารายได้เพิ่มได้เร็ว สองปีก็เป็นไปได้จริง แต่ถ้าใครบอกว่าไม่ต้องมีรายได้ ล้านใน สามสิบวัน นั่นแหละธงแดงสามผืนเดิม", "deadpan", "POINT_FWD", "plead", bg="street",
      props=[P("flag", 560, 620, 1.8), P("flag", 680, 620, 1.4), P("flag", 800, 620, 1.8)], ov=[O("ธงแดง x 3", 640, 110, 100, 0.4)]),
    L("Jin", "โอ๊ย ก็ได้ ฉันจะไม่โอน วันนี้", "plead", "CROSS", "smug"),
    L("Tang", "วันนี้ก็ไม่ควรโอนนะ", "deadpan", "POINT_UP", "worried", sfx="laugh"),
    L("Jin", "ก็ได้ ๆ", "worried", "HEADS", "laugh"),
    L("Tang", "เมื่อก่อนเหลือในบัญชีสามร้อย ตอนนี้เหลือสามพันสี่ร้อย อย่างน้อยตอนนี้เงินอยู่กับฉันเกินหนึ่งอาทิตย์", "laugh", "CHEER", "gloat", bg="bedroom",
      props=[P("phone", 640, 560, 1.5, screen=(40, 190, 120))], ov=[O("3,400 บาท", 640, 120, 100, 0.2)], bgkw=dict(night=0.7), sfx="ding"),
    L("Tang", "ใครอยู่จุดเริ่มต้นแบบฉัน บอกเป้าหมายเก็บเงินของคุณไว้ในคอมเมนต์ได้เลย", "happy", "POINT_FWD", "laugh", bg="dream", props=[P("piggy", 640, 650, 2.0)],
      ov=[O("เป้าหมายเก็บเงินของคุณคือเท่าไหร่?", 640, 110, 56, 0.2), O("เรื่องสมมติเพื่อความบันเทิง ไม่ใช่คำแนะนำการลงทุน", 640, 640, 40, 0.4)], sfx="cheer")]))

SOURCES = json.loads((HERE.parent / "money_million" / "story.json").read_text(encoding="utf-8"))["sources"]
cover = dict(bg="dream", chars=[C("tang", 420, "laugh", "CHEER", k=1.3, y=720), C("jin", 880, "aha", "ARMS_UP", k=1.3, y=720)],
             props=[P("moneybag", 640, 690, 2.6), P("coins", 150, 700, 2.4, n=7), P("piggy", 1130, 700, 2.0)], text="เงินล้านใน 2 ปี" + chr(10) + "ทำได้จริงไหม?")
doc = dict(id="know_money_v4", title="เงินล้านใน 2 ปี ทำได้จริงไหม (แบบไม่โดนหลอก)", aspect="16:9", playlist="knowledge", subtitles=False, version=1,
           chunks=[[i] for i in range(1, len(SC) + 1)], style=STYLE, voices=VOICES,
           note="ตัวละครและเรื่องราวเป็นเรื่องสมมติเพื่อความบันเทิง ไม่ใช่คำแนะนำการลงทุน ตัวเลขดอกเบี้ย/หนี้ครัวเรือนอ้างอิงข่าวปี 2569 ตามแหล่งใน sources",
           scenes=SC, sources=SOURCES, cover=cover, theme="เงินและ AI",
           topic="ตังค์อยากมีเงินล้านใน 2 ปี เกือบโดนสัมมนารวยเร็วหลอก แล้วพี่นุ่นสอนตัวเลขจริง (เรื่องสมมติเพื่อความบันเทิง ตัวละครพูดกันเอง ไม่มีผู้เล่า)")
(HERE / "story.json").write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
for s in SC:
    txt = " ".join(l["text"] for l in s["lines"])
    print(s["name"], len(s["lines"]), "lines", len(s["stage"]), "beats", len(txt), "chars")
print("total chars", sum(len(l["text"]) for s in SC for l in s["lines"]))
