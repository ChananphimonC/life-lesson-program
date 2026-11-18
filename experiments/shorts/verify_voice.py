"""Check Gemini TTS output by transcribing it back with the Gemini text model (separate, larger free quota).

    python verify_voice.py scripts/know_mbti.json            # every Gemini-voiced line that is cached
    python verify_voice.py scripts/know_mbti.json --line 1   # one line

Prints what was actually said next to the script, and flags lines where the tone instruction (the part before ':'
in "say") seems to have been read aloud, or where the transcript drifts far from the script.
"""

from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
from pathlib import Path

from google import genai
from google.genai import types

import character_art as CA
import gemini_guard
import tts
from life_lesson.config import get_settings


def _norm(s: str) -> str:
    return re.sub(r"[\s\"'“”.,!?…ๆ:;()\-]+", "", s)


def transcribe(wav: Path) -> str:
    s = get_settings()
    client = genai.Client(api_key=s.gemini_api_key)
    prompt = ("ถอดเสียงภาษาไทยในไฟล์เสียงนี้ให้ตรงกับที่ได้ยินจริงทุกคำ ห้ามแก้ ห้ามสรุป "
              "ตอบเฉพาะข้อความที่ถอดได้เท่านั้น")
    resp = gemini_guard.guarded("text", lambda: client.models.generate_content(
        model=s.gemini_script_model,
        contents=[types.Part.from_bytes(data=wav.read_bytes(), mime_type="audio/wav"), prompt]))
    return (resp.text or "").strip()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("script", type=Path)
    ap.add_argument("--line", type=int)
    args = ap.parse_args()
    data = json.loads(args.script.read_text(encoding="utf-8"))
    n, bad = 0, 0
    for sc in data["scenes"]:
        for line in sc.get("lines", []):
            n += 1
            if line.get("sfx_voice") or (args.line and n != args.line):
                continue
            ch = CA.load_character(line["speaker"])
            say = line.get("say", line["text"])
            wav = tts.find_cached(data["id"], n, ch, say, "gemini")
            if not wav:
                print(f"line {n}: not voiced by Gemini yet")
                continue
            heard = transcribe(wav)
            style, _, spoken = say.partition(": ") if ": " in say else ("", "", say)
            style_read = bool(style) and _norm(style)[:12] in _norm(heard)
            ratio = difflib.SequenceMatcher(None, _norm(spoken), _norm(heard)).ratio()
            flag = "STYLE READ ALOUD" if style_read else ("CHECK" if ratio < 0.85 else "ok")
            bad += flag != "ok"
            print(f"line {n}: {flag}  similarity {ratio:.2f}\n  script: {spoken}\n  heard : {heard}\n")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
