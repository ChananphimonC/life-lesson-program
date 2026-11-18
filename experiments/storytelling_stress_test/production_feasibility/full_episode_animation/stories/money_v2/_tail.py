
SOURCES = json.loads((HERE.parent / "money_million" / "story.json").read_text(encoding="utf-8"))["sources"]
scenes = []
for name, text, stage in SC:
    for j, b in enumerate(stage):
        if j:
            assert b["at"] in text, (name, b["at"])
    scenes.append(dict(name=name, lines=[dict(speaker="host_mint", text=text, say=f"{STYLE}: {text}")], stage=stage))
cover = dict(bg="dream", chars=[C(T, 420, "laugh", "CHEER", k=1.3, y=720), C(B, 880, "aha", "ARMS_UP", k=1.3, y=720)],
             props=[P("moneybag", 640, 690, 2.6), P("coins", 150, 700, 2.4, n=7), P("piggy", 1130, 700, 2.0)], text="เงินล้านใน 2 ปี" + chr(10) + "ทำได้จริงไหม?")
doc = dict(id="know_money_v2", title="เงินล้านใน 2 ปี ทำได้จริงไหม (แบบไม่โดนหลอก)", aspect="16:9", playlist="knowledge", subtitles=False, version=3,
           chunks=[[1, 2], [3, 4], [5, 6], [7]], style=STYLE,
           note="ตัวละครและเรื่องราวเป็นเรื่องสมมติเพื่อความบันเทิง ไม่ใช่คำแนะนำการลงทุน ตัวเลขดอกเบี้ย/หนี้ครัวเรือนอ้างอิงข่าวปี 2569 ตามแหล่งใน sources บทผ่านการวิจารณ์โดย Gemini 2 รอบ และ GPT 1 รอบก่อนทำคลิป",
           scenes=scenes, sources=SOURCES, cover=cover, theme="เงินและ AI",
           topic="ตังค์อยากมีเงินล้านใน 2 ปี เกือบโดนกูรูหลอกลงทุน แล้วพี่นุ่นสอนตัวเลขจริง (เรื่องสมมติเพื่อความบันเทิง ผู้เล่าเสียงผู้ชายคนเดียว)")
(HERE / "story.json").write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
tot = sum(len(s["lines"][0]["text"]) for s in scenes)
print({s["name"]: len(s["lines"][0]["text"]) for s in scenes}, tot, "chars ->", round(tot / 12), "s")
