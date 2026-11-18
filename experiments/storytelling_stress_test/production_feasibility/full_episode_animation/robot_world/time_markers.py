"""Ask the Gemini text model (audio input; separate, larger free quota than TTS) when each marker phrase starts in the narration of each scene,
then snap that estimate to the nearest pause end found by silencedetect. Writes audio/marks.json {scene: {marker: seconds}}.
The result is only as good as the model's timestamps (about +-1 s), so the pause snap and an ASR spot check follow."""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXP = HERE.parents[3]
sys.path.insert(0, str(EXP / "shorts"))
sys.path.insert(0, str(EXP.parent / "src"))
sys.path.insert(0, str(HERE.parent))
import gemini_guard  # noqa: E402
from google import genai  # noqa: E402
from google.genai import types  # noqa: E402
from life_lesson.config import get_settings  # noqa: E402

import importlib  # noqa: E402

s = get_settings()
client = genai.Client(api_key=s.gemini_api_key)
tim = json.loads((HERE / "audio" / "timing.json").read_text(encoding="utf-8"))
out = {}
for i in range(1, 8):
    m = importlib.import_module(f"rw{i}")
    markers = m.MARK[1:]
    prompt = ("นี่คือเสียงผู้เล่าเรื่องภาษาไทยความยาว {d:.1f} วินาที จงบอกว่าผู้พูดเริ่มพูดแต่ละวลีต่อไปนี้ที่วินาทีเท่าไหร่นับจากต้นไฟล์ "
              "(ทศนิยม 1 ตำแหน่ง) ตอบเป็น JSON ล้วนในรูป {{\"วลี\": วินาที}} ห้ามมีข้อความอื่น\nวลี: {ph}").format(d=tim[str(i)]["dur"], ph=" | ".join(markers))
    wav = (HERE / "audio" / f"r{i}.wav").read_bytes()
    resp = gemini_guard.guarded("text", lambda: client.models.generate_content(
        model=s.gemini_script_model, contents=[types.Part.from_bytes(data=wav, mime_type="audio/wav"), prompt],
        config=types.GenerateContentConfig(response_mime_type="application/json")))
    try:
        d = json.loads(resp.text)
    except Exception:  # noqa: BLE001
        d = {}
    ends = tim[str(i)]["pauses"]
    res = {}
    for mk in markers:
        est = None
        for k, v in d.items():
            if mk[:8] in k or k[:8] in mk:
                est = float(v)
        if est is None:
            continue
        near = min(ends, key=lambda p: abs(p - est)) if ends else est
        res[mk] = dict(est=est, snapped=near if abs(near - est) <= 1.2 else est)
    out[str(i)] = res
    print(i, {k[:10]: (v["est"], v["snapped"]) for k, v in res.items()}, flush=True)
(HERE / "audio" / "marks.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
