"""topic -> story.json with Gemini (research with Google Search grounding -> funny script + staging JSON -> validation loop). Used by daily_runner.py.

    python make_story_llm.py <story_id> "<topic / brief>" [--minutes 7] [--theme "เงินและ AI"]

Rules baked into the prompt: facts only from the research bundle (with sources), money/finance safety (no guaranteed returns, no naming products to buy, disclaimer in the last scene),
numbers written as Thai words in the narration, the fixed cast and the fixed vocabulary of backgrounds / props / poses / expressions of story_engine, markers that really occur in the text.
Gemini free tier: ~4 text requests per story (research, script, up to 2 repairs); the daily text limit is 200.
"""
import json
import re
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[2] / "shorts"))
sys.path.insert(0, str(HERE.parents[3] / "src"))

STYLE = ("เล่านิทานตลกให้เพื่อนฟังด้วยน้ำเสียงผู้ชายสนุกสนาน กวนนิด ๆ มีอารมณ์ร่วม เปลี่ยนโทนเสียงตามเหตุการณ์ ทำเสียงตัวละครให้ต่างกันนิดหน่อย "
         "ไม่พูดเรียบ ๆ ไม่ช้าเอื่อย ออกเสียงคำไทยให้ชัด")
RISKY = {"ราว": "ประมาณ", "ฝั่ง": "ด้าน"}
DIG = ["ศูนย์", "หนึ่ง", "สอง", "สาม", "สี่", "ห้า", "หก", "เจ็ด", "แปด", "เก้า"]


def thai_int(n):
    """123456 -> หนึ่งแสนสองหมื่นสามพันสี่ร้อยห้าสิบหก (good enough for narration)."""
    if n == 0:
        return "ศูนย์"
    if n >= 1_000_000:
        a, b = divmod(n, 1_000_000)
        return thai_int(a) + "ล้าน" + (thai_int(b) if b else "")
    out = ""
    for unit, name in ((100000, "แสน"), (10000, "หมื่น"), (1000, "พัน"), (100, "ร้อย"), (10, "สิบ"), (1, "")):
        d, n = divmod(n, unit)
        if not d:
            continue
        if unit == 10 and d == 1:
            out += "สิบ"
        elif unit == 10 and d == 2:
            out += "ยี่สิบ"
        elif unit == 1 and d == 1 and out:
            out += "เอ็ด"
        else:
            out += DIG[d] + name
    return out


def spell_numbers(text):
    """Digits in the narration -> Thai words (TTS reads digits unpredictably). 12,500 / 1.8 / 50%"""
    def dec(m):
        a, b = m.group(1).replace(",", ""), m.group(2)
        return thai_int(int(a)) + "จุด" + "".join(DIG[int(ch)] for ch in b)

    text = re.sub(r"(\d[\d,]*)\.(\d+)", dec, text)
    text = re.sub(r"(\d[\d,]*)\s*%", lambda m: thai_int(int(m.group(1).replace(",", ""))) + "เปอร์เซ็นต์", text)
    text = re.sub(r"\d[\d,]*", lambda m: thai_int(int(m.group(0).replace(",", ""))), text)
    return text


def lint_text(text):
    text = spell_numbers(text)
    for a, b in RISKY.items():
        text = text.replace(a, b)
    return text


def gen(client, model, prompt, tools=None, json_out=False, retries=3):
    import gemini_guard
    from google.genai import types
    cfg = dict(tools=tools) if tools else {}
    if json_out:
        cfg["response_mime_type"] = "application/json"
    last = None
    for a in range(retries):
        try:
            r = gemini_guard.guarded("text", lambda: client.models.generate_content(model=model, contents=prompt, config=types.GenerateContentConfig(**cfg)))
            return r
        except Exception as exc:  # noqa: BLE001
            last = exc
            time.sleep(5 * (a + 1))
    raise last


def research(client, model, brief):
    from google.genai import types
    prompt = (f"ค้นหาข้อมูลจริงล่าสุดเกี่ยวกับหัวข้อนี้สำหรับทำคลิปความรู้สนุก ๆ: {brief}\n"
              "สรุปเป็นข้อ ๆ 8-12 ข้อ แต่ละข้อมี: ข้อเท็จจริง/ตัวเลขที่ยืนยันได้ + ชื่อแหล่ง + วันที่ข้อมูล ห้ามเดาตัวเลข ถ้าหาไม่เจอให้บอกว่าไม่พบ "
              "แยกให้ชัดว่าอะไรเป็นข้อเท็จจริง อะไรเป็นความเห็น ตอบภาษาไทย")
    r = gen(client, model, prompt, tools=[types.Tool(google_search=types.GoogleSearch())])
    facts = r.text or ""
    srcs = []
    try:
        gm = r.candidates[0].grounding_metadata
        for ch in (gm.grounding_chunks or []):
            if ch.web and ch.web.uri:
                srcs.append(dict(name=ch.web.title or ch.web.uri[:60], url=ch.web.uri, supports="ข้อมูลที่ค้นเมื่อสร้างตอนนี้ (ตรวจกับต้นฉบับก่อนเผยแพร่)"))
    except Exception:  # noqa: BLE001
        pass
    return facts, srcs[:8]


def prompt_script(brief, facts, minutes, theme, vocab, errors=None, previous=None):
    chars = "phum(ต้า พระเอก ใส่แว่น) em(เอม เพื่อนซี้ ขี้ตื่นเต้น) manao(อร เพื่อนเรียบร้อย) bua(ปิ่น) kong(ก้อง) guru(กูรูหลอกลวง ใส่แว่นดำสูท) bam jake faa mariam omar"
    ex = ('{"at":"วลีในบทที่ตรงตัวอักษร (ว่างสำหรับ beat แรก)","bg":"desk","bgkw":{"dusk":0.5},"chars":[{"who":"phum","x":380,"y":700,"k":0.95,"ex":"worried","pose":"HEADS","talk":true},'
          '{"who":"em","x":900,"y":700,"k":0.95,"ex":"smug"}],"props":[{"k":"phone","x":800,"y":560,"s":1.4}],"ov":[{"text":"387 บาท","x":800,"y":300,"size":64,"col":[255,110,100],"at":0.4}],"sfx":"ding"}')
    p = f"""คุณเป็นนักเขียนบท+ผู้กำกับคลิปการ์ตูนตลกภาษาไทยสำหรับช่อง "รู้หรือไม่" ธีม: {theme}
หัวข้อ/โจทย์: {brief}
ความยาวเสียงเล่าประมาณ {minutes} นาที (≈ {int(minutes * 60 * 12)} ตัวอักษรไทย) แบ่งเป็น 6-9 ฉาก ฉากละ 500-800 ตัวอักษร

ข้อเท็จจริงที่ใช้ได้ (มาจากการค้นหา ใช้เฉพาะที่นี่เท่านั้น ห้ามแต่งตัวเลข/สถิติเพิ่ม):
{facts}

กติกาเนื้อหา
- เล่าเป็นนิทานตลก มีตัวละคร (ต้าเป็นพระเอก) พูดโต้ตอบกัน ผู้เล่าชายคนเดียวพากย์ทุกตัว เขียนภาษาพูดไทยธรรมชาติ มุกมาจากสถานการณ์ ไม่เสียดสีคนกลุ่มใด
- เปิดเรื่องด้วยประโยคที่ขัดความคาดหมาย (hook ภายใน 10 วินาที) ทุกฉากจบด้วยปมค้างให้อยากดูต่อ มี payoff ย้อนกลับ
- เรื่องเงิน/ลงทุน: ห้ามรับประกันผลตอบแทน ห้ามแนะนำสินค้าการเงิน/หุ้น/คริปโตตัวใดโดยเฉพาะ ห้ามชวนกู้หรือผ่อน ใส่คำเตือนสั้น ๆ ในฉากสุดท้ายว่าเป็นเรื่องสมมติเพื่อความบันเทิง ไม่ใช่คำแนะนำการลงทุน และตัวเลขอาจเปลี่ยน
- ตัวเลขในบทเล่า (text) เขียนเป็นคำอ่านไทยเสมอ (เช่น สองหมื่น ไม่ใช่ 20,000) ส่วน ov (ข้อความบนจอ) ใช้ตัวเลขอารบิกได้
- เลี่ยงคำที่ TTS มักอ่านเพี้ยน: ราว, ฝั่ง; คำแรกของแต่ละฉากเป็นคำง่าย

ตัวละคร (who): {chars}; ท่า pose: {', '.join(vocab['poses'])}; สีหน้า ex: {', '.join(vocab['ex'])}
ฉากหลัง bg: {', '.join(vocab['bg'])} (bgkw: bedroom{{night:0-1}}, desk{{dusk:0-1}})
ของประกอบ props k: {', '.join(vocab['props'])} (ต้อง kw เฉพาะบางอัน: chart{{kind:up|down|flat|bars|bars_up}}, bills{{n,fan}}, coins{{n}}, phone{{screen:[r,g,b]}}, tea{{level}})
sfx: pop, ding, chime, cheer, gasp, laugh, whoosh, thump, sigh, step

รูปแบบฉาก: ทุกฉากมี stage = รายการ beat 6-10 อัน ภาพเปลี่ยนทุก 4-8 วินาที beat แรกไม่มี "at" beat ถัดไปมี "at" = วลีสั้น ๆ (6-30 ตัวอักษร) ที่ปรากฏตามตัวอักษรในบทของฉากนั้นตามลำดับ
ผังพิกัดภาพ 1280x720: ตัวละครยืนที่ y=700; พระเอกซ้าย x≈330-420 หันขวา (ไม่ต้องใส่ th), ตัวอื่นขวา x≈880-950 (หันซ้ายอัตโนมัติถ้า x>=640 และใส่ flip:true); k=0.9-1.0; ของประกอบ y≈560-650; ov วางที่ y 140-300 ไม่ทับหน้า
ตัวอย่าง beat: {ex}

ตอบเป็น JSON เดียว: {{"title":"ชื่อคลิป","cover_text":"ข้อความบนปก 2 บรรทัด (คั่นด้วย \\n)","cover":{{"bg":"dream","chars":[{{"who":"phum","x":420,"y":720,"k":1.3,"ex":"laugh","pose":"CHEER"}}],"props":[{{"k":"moneybag","x":640,"y":690,"s":2.6}}]}},"scenes":[{{"name":"1 hook","text":"...","stage":[...]}}]}}"""
    if errors:
        p += "\n\nรอบก่อนมีข้อผิดพลาดต่อไปนี้ แก้ให้ครบแล้วส่ง JSON ฉบับสมบูรณ์ใหม่:\n" + "\n".join(errors[:25]) + "\n\nJSON เดิม:\n" + (previous or "")[:60000]
    return p


def main():
    import story_engine as S
    from life_lesson.config import get_settings
    from google import genai
    sid, brief = sys.argv[1], sys.argv[2]
    minutes = float(sys.argv[sys.argv.index("--minutes") + 1]) if "--minutes" in sys.argv else 7.0
    theme = sys.argv[sys.argv.index("--theme") + 1] if "--theme" in sys.argv else "เงินและ AI"
    s = get_settings()
    client = genai.Client(api_key=s.gemini_api_key)
    out = HERE / "stories" / sid
    out.mkdir(parents=True, exist_ok=True)
    facts, srcs = research(client, s.gemini_script_model, brief)
    (out / "research.txt").write_text(facts + "\n\nSOURCES\n" + "\n".join(f"{x['name']} {x['url']}" for x in srcs), encoding="utf-8")
    vocab = dict(poses=list(S.POSES_BY_NAME), ex=S.EXPRESSIONS, bg=sorted(S.REG_BG), props=sorted(S.REG_PROP))
    errors, previous, doc = None, None, None
    for attempt in range(3):
        r = gen(client, s.gemini_script_model, prompt_script(brief, facts, minutes, theme, vocab, errors, previous), json_out=True)
        previous = r.text or ""
        try:
            data = json.loads(previous)
        except json.JSONDecodeError as exc:
            errors = [f"JSON parse error: {exc}"]
            continue
        scenes = []
        for sc in data["scenes"]:
            text = lint_text(sc["text"])
            stage = sc["stage"]
            if stage and "at" in stage[0]:
                stage[0].pop("at")
            for b in stage:                       # markers are matched against the spelled-out text; digits/risky words in markers are rewritten the same way
                if "at" in b:
                    b["at"] = lint_text(b["at"])
            scenes.append(dict(name=sc["name"], lines=[dict(speaker="host_mint", text=text, say=f"{STYLE}: {text}")], stage=stage))
        n = len(scenes)
        chunks = [[i, i + 1] if i + 1 <= n else [i] for i in range(1, n + 1, 2)]
        cover = data.get("cover", {})
        cover.setdefault("bg", "dream")
        cover["text"] = (data.get("cover_text") or data["title"]).replace("\\n", "\n")
        doc = dict(id=f"know_{sid}", title=data["title"], aspect="16:9", playlist="knowledge", subtitles=False, version=1, chunks=chunks, style=STYLE,
                   note="ตัวละครและเรื่องราวเป็นเรื่องสมมติเพื่อความบันเทิง ข้อเท็จจริงอ้างอิงจากการค้นหาอัตโนมัติ (ดู research.txt และ sources) ควรตรวจกับต้นฉบับก่อนเผยแพร่",
                   scenes=scenes, sources=srcs, cover=cover, theme=theme, topic=brief)
        (out / "story.json").write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
        errors = S.validate(doc)
        if not errors:
            break
        print("repair", attempt + 1, errors[:3])
    if errors:
        print("FAILED validate:", errors[:6])
        sys.exit(2)
    print("story ok:", doc["title"], sum(len(x["lines"][0]["text"]) for x in doc["scenes"]), "chars,", len(doc["scenes"]), "scenes")


if __name__ == "__main__":
    main()
