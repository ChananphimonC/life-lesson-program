"""Audition male Gemini voices for the storyteller: the same excited fairy-tale passage, one request per voice (Gemini free tier: 10 TTS requests per day)."""
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXP = HERE.parents[3]
sys.path.insert(0, str(EXP / "shorts"))
sys.path.insert(0, str(EXP.parent / "src"))
import tts  # noqa: E402
from life_lesson.config import get_settings  # noqa: E402

STYLE = "เล่านิทานด้วยน้ำเสียงตื่นเต้น สนุกสนาน มีอารมณ์ร่วม เปลี่ยนโทนเสียงตามเหตุการณ์และตัวละคร ไม่พูดเรียบ ๆ ออกเสียงคำไทยให้ชัด"
TEXT = ("เช้านี้ที่บ้านต้นกับลุงโชค ไม่มีเสียงไก่ขัน มีแต่เสียงลำโพงดังติ๊งต่อง รถของคุณมาถึงแล้วค่ะ ลุงโชคลุกพรวด วิ่งออกไปดูหน้าบ้าน แล้วก็อ้าปากค้าง "
        "รถคันขาว ๆ กลม ๆ จอดรออยู่ ไม่มีคนขับ ไม่มีแม้แต่พวงมาลัย ลุงโชคเกาหัวแกรก ๆ ถามรถเสียงดังว่า เอ๊ะ ทำไมรถคันนี้ไม่มีคนขับล่ะ แล้วเราต้องทำยังไง "
        "รถตอบเสียงใสว่า ไม่ต้องทำอะไรเลยค่ะ แค่บอกชื่อกับที่ไป ต้นยกมือทันที ต้นกับลุงโชคค่ะ ไปตลาด")
settings = get_settings()
for v in sys.argv[1:]:
    ch = {"id": f"aud_{v.lower()}", "voice": {"gemini": v, "edge": "th-TH-NiwatNeural", "edge_pitch": "+0Hz", "edge_rate": "+0%"}}
    try:
        path, eng = tts.synth_line(settings, "audition_voices", 1, ch, f"{STYLE}: {TEXT}", mode="gemini")
    except Exception as exc:  # noqa: BLE001
        print(v, "FAILED", str(exc)[:160], flush=True)
        continue
    shutil.copyfile(path, HERE / "audition" / f"{v}.wav")
    print(v, eng, path.name, flush=True)
