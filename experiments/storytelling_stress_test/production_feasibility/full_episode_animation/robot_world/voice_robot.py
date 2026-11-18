"""Voices know_robot_world.json the way the 'รู้หรือไม่' series is voiced: one narrator (host น้องปิ่น = host_mint), one request per scene,
Gemini TTS (voice Kore) first under gemini_guard's daily limit, edge-tts (Premwadee) only if Gemini is unavailable.
Each voiced scene is cached by the shorts pipeline (cartoon_storyboard/output/_work/tts/know_robot_world/) and copied to robot_world/audio/rN.wav.

    python voice_robot.py            -> voices every scene that is not cached yet and prints which engine did it
"""
import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXP = HERE.parents[3]
sys.path.insert(0, str(EXP / "shorts"))
sys.path.insert(0, str(EXP.parent / "src"))
import character_art as CA  # noqa: E402
import tts  # noqa: E402
from life_lesson.config import get_settings  # noqa: E402

doc = json.loads((HERE / "know_robot_world.json").read_text(encoding="utf-8"))
host = CA.load_character("host_mint")
settings = get_settings()
(HERE / "audio").mkdir(exist_ok=True)
report = []
for n, sc in enumerate(doc["scenes"], 1):
    line = sc["lines"][0]
    try:
        path, engine = tts.synth_line(settings, doc["id"], n, host, line["say"], mode="auto")
    except Exception as exc:  # noqa: BLE001
        print(f"scene {n}: FAILED {str(exc)[:200]}", flush=True)
        report.append(dict(scene=n, engine="none"))
        continue
    shutil.copyfile(path, HERE / "audio" / f"r{n}.wav")
    report.append(dict(scene=n, engine=engine, file=path.name))
    print(f"scene {n}: {engine} -> {path.name}", flush=True)
(HERE / "audio" / "voice_report.json").write_text(json.dumps(report, indent=1), encoding="utf-8")
