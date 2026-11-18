"""Ask Gemini to tear a draft script apart BEFORE any voice/animation is made (the user's rule: review first, then produce).

    python critique.py <draft.txt> [--out critique.md] [--model gemini-3.8-flash] [--prompt-file prompt.txt]

Also writes PROMPT_FOR_GPT.md next to the draft: the same prompt + script, ready to paste into ChatGPT (no OpenAI key is available to Claude, so GPT's opinion has to be pasted back by the user).
"""
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "shorts"))
sys.path.insert(0, str(HERE.parents[3] / "src"))

PROMPT = """คุณคือบรรณาธิการบทคลิปตลกภาษาไทยสายโหด เคยทำงานกับนักเล่าเรื่อง สแตนด์อัพคอมเมดี้ และช่อง YouTube คนดูหลักล้าน
ผู้สร้างช่องบอกว่าบทเวอร์ชันก่อน "ไม่สนุกเลย แปลกมาก ฟังแล้วรู้ว่า AI เขียน" (เช่น บรรยายสีหน้าตัวละครว่า "ยิ้มเจ้าเล่ห์", บอกว่าตัวละครใส่แว่นดำ, ใช้คำว่าไฟแดงครบชุด, สรุปเป็นข้อ ๆ แบบรายงาน)
บทต่อไปนี้เป็นเวอร์ชันแก้ใหม่ เล่าเป็นเสียงคนเดียว (ผู้ชาย) ที่เล่าให้เพื่อนฟัง พากย์ตัวละครทุกคนเอง ภาพการ์ตูนประกอบเป็นอีกส่วนหนึ่ง จึงไม่ต้องบรรยายหน้าตา/เสื้อผ้า

ช่วยวิจารณ์อย่างตรงไปตรงมา ไม่ต้องเกรงใจ ตอบภาษาไทย เป็นข้อสั้น ๆ มีตัวอย่างอ้างบรรทัดจริง:
1. ช่วงไหนน่าเบื่อ/ยืดเยื้อ (อ้างประโยค) และควรตัดหรือบีบอย่างไร
2. ประโยค/โครงสร้างไหนที่ฟังแล้วรู้สึกว่า AI เขียน (จังหวะสม่ำเสมอ ภาษาทางการ ตัวเลขแน่นเกิน สรุปแบบสูตร ฯลฯ) และคนจริงจะพูดว่าอะไรแทน
3. มุกไหนไม่ขึ้น เพราะอะไร (setup/punchline ผิดที่ คำตลกไม่ได้อยู่ท้ายประโยค อธิบายมุกเอง ฯลฯ) พร้อมเสนอมุกแทน
4. ตัวละครและบทสนทนา: ใครพูดเหมือนกันหมด, ใครแบนเกินไป, ใส่ลักษณะพูดเฉพาะตัวอย่างไร
5. จังหวะและการเปิด/ปิดเรื่อง: ฮุค 10 วินาทีแรกพอไหม ปมค้างระหว่างฉาก payoff ตอนจบ
6. เขียนใหม่ให้ดู 3 ช่วงที่แย่ที่สุด (ภาษาพูดจริง เหมือนคนเล่าให้เพื่อนฟังตอนกินข้าว)
7. สรุป 5 ข้อที่ต้องแก้ก่อนทำคลิป เรียงตามความสำคัญ

บท:
"""


def main():
    draft = Path(sys.argv[1])
    arg = lambda k, d=None: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else d
    out = Path(arg("--out", str(draft.parent / "critique.md")))
    text = draft.read_text(encoding="utf-8")
    prompt = Path(arg("--prompt-file")).read_text(encoding="utf-8") if arg("--prompt-file") else PROMPT
    (draft.parent / "PROMPT_FOR_GPT.md").write_text(prompt + text, encoding="utf-8")
    import gemini_guard
    from life_lesson.config import get_settings
    from google import genai
    from google.genai import types
    s = get_settings()
    client = genai.Client(api_key=s.gemini_api_key)
    models = [m for m in (arg("--model"), "gemini-3.8-flash", s.gemini_script_model) if m]
    res = None
    for model in models:
        try:
            r = gemini_guard.guarded("text", lambda: client.models.generate_content(model=model, contents=prompt + text))
            res = (model, r.text)
            break
        except Exception as exc:  # noqa: BLE001
            print("model", model, "failed:", str(exc)[:120])
    if not res:
        print("no model answered")
        sys.exit(1)
    out.write_text(f"# วิจารณ์บทโดย Gemini ({res[0]})\n\n{res[1]}\n", encoding="utf-8")
    print("saved", out, "by", res[0])


if __name__ == "__main__":
    main()
