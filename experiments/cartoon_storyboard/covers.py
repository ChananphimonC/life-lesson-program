"""Per-episode cover (YouTube thumbnail), stored next to the video:

    output/videos/EP01 - <title>/cover.jpg       1920x1080 JPEG, < 2 MB
                                /cover.json      3 AI concepts, the chosen one, the cover text,
                                                 history of the creator's "จุดที่อยากแก้" notes
                                /cover_base.jpg  (optional) the picture WITHOUT text, e.g. a still from the video; while
                                                 cover.json has "base" set, every edit of the text is drawn on this picture

Built on thumbnail_studio: one Gemini text call proposes 3 concepts, the art is
drawn procedurally and the Thai text is drawn locally, so it never comes out garbled.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime

from PIL import Image

from life_lesson.config import get_settings
from life_lesson.generation.gemini_client import generate_script_text

import library
import playlists
import shorts_lib
import thumbnail_host
import thumbnail_studio as T
from scenes_ep03 import thai_font

W, H = 1920, 1080
TEXT_SIZE = 120
BASE_NAME = "cover_base.jpg"
MAX_TEXT = 80                        # characters on the whole cover


SIZES = {"16:9": (1920, 1080), "9:16": (1080, 1920), "1:1": (1080, 1080)}
# A cover must look like its video: each playlist sets the channel description and the tone the AI designs for.
SERIES = {
    "life_lesson": {"channel": None,  # the default Life Lesson description inside thumbnail_studio
                    "tone": "calm and reflective; muted cinematic light, usually dusk or night; never cheerful"},
    "knowledge": {"channel": ("a bright, friendly Thai explainer series 'รู้หรือไม่ / ทำไม' where one fun narrator "
                              "tells a fact-checked story and cartoon characters act it out"),
                  "tone": "bright, colourful, curious and friendly; scene 'studio' or time 'day', warm accent; "
                          "darken only if the topic itself is spooky or sad",
                  "host_cover": True},
    "shorts": {"channel": "a Thai cartoon YouTube channel with family-friendly comedy Shorts",
               "tone": "bright, playful and funny; warm colours, expressive; never gloomy"},
}


def series_of(folder: str) -> dict:
    entry = _entry(folder)
    short = folder.startswith("short:")
    item = {"key": folder if short else f"ep:{entry['episode_id']}", "kind": "short" if short else "ep", "entry": entry}
    return SERIES.get(playlists.playlist_of(item), SERIES["shorts" if short else "life_lesson"])


def _dir(key: str):
    if key.startswith("short:"):
        return shorts_lib.SHORTS_DIR / key[len("short:"):]
    return library.LIB_DIR / key


def _paths(folder: str):
    d = _dir(folder)
    return d / "cover.json", d / "cover.jpg"


def cover_path(key: str):
    return _paths(key)[1]


def base_path(key: str):
    return _dir(key) / BASE_NAME


def has_base(key: str) -> bool:
    return base_path(key).is_file()


def download_name(key: str) -> str:
    entry = _entry(key)
    return f"{library.safe_title(entry['title'])} - cover.jpg"


def _size(key: str):
    if key.startswith("short:"):
        return SIZES.get(_entry(key).get("aspect", "9:16"), SIZES["16:9"])
    return SIZES["16:9"]


def load(folder: str) -> dict | None:
    meta, _ = _paths(folder)
    return json.loads(meta.read_text(encoding="utf-8")) if meta.is_file() else None


def _save(folder: str, data: dict):
    meta, _ = _paths(folder)
    meta.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _entry(folder: str) -> dict:
    if folder.startswith("short:"):
        entry = shorts_lib.find(folder[len("short:"):])
        if entry is None:
            raise KeyError(folder)
        return {**entry, "topic": entry["title"], "episode_id": None}
    entry = library.find(folder)
    if entry is None:
        raise KeyError(folder)
    return entry


def _fallback_concept(title: str) -> dict:
    return T.ThumbnailConcept(
        name="พื้นฐาน (ไม่ใช้ AI)", visual_hook="ตัวละครยืนนิ่งท่ามกลางแสงเย็น",
        template="wide_symbolic", pose="stand", time="dusk", thai_text=title[:24],
    ).model_dump()


def _fit_size(text: str, width: int = W) -> int:
    """Largest size (<= TEXT_SIZE) whose longest line fits 86% of the width."""
    size = TEXT_SIZE
    while size > 48:
        f = thai_font(size, True)
        if max(f.getlength(ln) for ln in text.split("\n")) <= width * 0.86:
            break
        size -= 6
    return size


def render(folder: str) -> dict:
    data = load(folder)
    if data is None:
        raise KeyError(folder)
    concept = T.ThumbnailConcept.model_validate(data["concepts"][data["choice"]])
    w, h = _size(folder)
    if data.get("base") and has_base(folder):          # a picture from the video: only the text changes, the picture stays
        img = Image.open(base_path(folder)).convert("RGB").resize((w, h), Image.LANCZOS)
    elif series_of(folder).get("host_cover"):  # explainer series: the host + topic graphics, as in the video
        kind = (shorts_lib.script_for(folder[len("short:"):]) or {}).get("cover", "host") if folder.startswith("short:") else "host"
        img = thumbnail_host.render(w, h, _entry(folder)["title"], T.hexrgb(concept.accent), kind)
    else:
        img = T.render_concept(concept, w, h)
    text = data["text"]
    img = T.compose_text(img, text, size=_fit_size(text, w), anchor="top-center")
    _, jpg = _paths(folder)
    T.export_image(img, jpg)
    return data


def _remember(data: dict, action: str, note: str) -> None:
    """Per-episode history of the creator's notes, newest first, for reuse."""
    note = note.strip()
    if not note:
        return
    history = [h for h in data.get("history", []) if h["note"] != note]
    history.insert(0, {"note": note, "action": action, "at": datetime.now().isoformat(timespec="seconds")})
    data["history"] = history[:15]


def generate(folder: str, note: str = "") -> dict:
    """Ask Gemini for 3 concepts (falls back to a plain local concept if the
    call fails, recording why), then render concept 1 with its suggested text.
    `note` is appended to the analysis prompt; empty = the original prompt."""
    entry = _entry(folder)
    settings = get_settings()
    history = (load(folder) or {}).get("history", [])
    summary = (entry.get("summary") or (T.episode_transcript(settings, entry["episode_id"]) if entry["episode_id"] else "")
               or entry.get("topic") or entry["title"])
    series = series_of(folder)
    try:
        analysis = T.analyze_story(settings, entry["title"], summary, note, channel=series["channel"], tone=series["tone"])
        concepts = [c.model_dump() for c in analysis.concepts]
        data = {"concepts": concepts, "choice": 0, "text": concepts[0]["thai_text"],
                "hook_question": analysis.hook_question, "error": None}
    except Exception as exc:
        if load(folder) is not None and cover_path(folder).is_file():       # a cover exists already: keep it as it is and say why nothing changed
            raise T.ThumbnailError(f"AI ใช้ไม่ได้ตอนนี้ ปกเดิมยังอยู่ครบ ไม่มีอะไรเปลี่ยน ลองใหม่ภายหลัง ({str(exc)[:160]})") from exc
        data = {"concepts": [_fallback_concept(entry["title"])], "choice": 0, "text": entry["title"][:24],
                "hook_question": "", "error": f"AI ใช้ไม่ได้ตอนนี้ จึงใช้แบบพื้นฐานแทน ({exc})"[:300]}
    data["history"] = history
    _remember(data, "generate", note)
    _save(folder, data)
    return render(folder)


def set_base(folder: str, image: Image.Image, text: str, name: str = "ภาพจากตอน") -> dict:
    """Make `image` (no text on it) the picture of this cover and draw `text` on it. Later text edits keep the picture."""
    w, h = _size(folder)
    image.convert("RGB").resize((w, h), Image.LANCZOS).save(base_path(folder), "JPEG", quality=94)
    concept = T.ThumbnailConcept(name=name, visual_hook="ภาพนิ่งจากตัววิดีโอ", template="wide_symbolic", pose="stand", time="dusk",
                                 thai_text=text.replace(chr(10), " ")[:24]).model_dump()
    old = load(folder) or {}
    data = {"concepts": [concept], "choice": 0, "text": text, "hook_question": "", "error": None, "history": old.get("history", []), "base": BASE_NAME}
    _save(folder, data)
    return render(folder)


def use_base(folder: str) -> dict:
    """Go back to the picture from the video (cover_base.jpg) after a new AI design replaced it."""
    data = load(folder)
    if data is None or not has_base(folder):
        raise T.ThumbnailError("ไม่มีภาพจากตอนที่เก็บไว้สำหรับตอนนี้")
    data["base"] = BASE_NAME
    data["error"] = None
    _save(folder, data)
    return render(folder)


def choose(folder: str, index: int) -> dict:
    data = load(folder)
    if data is None or not 0 <= index < len(data["concepts"]):
        raise KeyError(folder)
    data["choice"] = index
    if not data.get("base"):            # an AI design brings its own suggested text; a picture from the video keeps the text the creator typed
        data["text"] = data["concepts"][index]["thai_text"]
    _save(folder, data)
    return render(folder)


def set_text(folder: str, text: str) -> dict:
    data = load(folder)
    if data is None:
        raise KeyError(folder)
    text = text.replace("\\n", "\n").strip()
    if not text:
        raise T.ThumbnailError("ข้อความบนปกว่างเปล่า")
    if len(text) > MAX_TEXT:                         # never cut a word in the middle silently
        raise T.ThumbnailError(f"ข้อความยาวเกินไป ({len(text)} ตัวอักษร) ใส่ได้ไม่เกิน {MAX_TEXT} ตัวอักษร")
    w, _ = _size(folder)
    if max(thai_font(48, True).getlength(ln) for ln in text.split("\n")) > w * 0.9:
        raise T.ThumbnailError("มีบรรทัดที่ยาวเกินกว่าจะใส่บนปกได้ ให้พิมพ์ \\n เพื่อขึ้นบรรทัดใหม่ (บรรทัดละไม่เกินประมาณ 35 ตัวอักษร)")
    data["text"] = text
    _save(folder, data)
    return render(folder)


DEFAULT_REWRITE = "ให้สั้นและชวนสงสัยมากขึ้น"


def rewrite_text(folder: str, note: str = "") -> dict:
    """One Gemini text call: rewrite the cover text. The creator's `note` is
    appended to the default instruction (empty = the default alone)."""
    entry, data = _entry(folder), load(folder)
    if data is None:
        raise KeyError(folder)
    instruction = DEFAULT_REWRITE + (f"\nAlso: {note.strip()}" if note.strip() else "")
    prompt = (
        "You write the Thai text overlay for a YouTube thumbnail of "
        + (series_of(folder)["channel"] or
           "a calm, reflective Thai storytelling channel (loneliness, feeling behind in life, money vs. health and time)")
        + ".\n"
        f"Episode title: {entry['title']}\nTopic: {entry.get('topic') or '-'}\n"
        f"Tone of the video: {series_of(folder)['tone']}\n"
        f"Current thumbnail text: {data['text']}\n"
        f"The creator's instruction: {instruction}\n\n"
        "Rules: keep the key term from the title (e.g. MBTI, written as in the title) in the text, "
        "2-6 Thai words besides it, natural spoken Thai, creates honest curiosity, never misleading, "
        "no clickbait exaggeration, no emoji, no quotes, no episode number. You may use one line "
        "break written as \\n if it reads better.\n"
        'Respond with ONLY this JSON: {"text": "<the new thumbnail text>"}'
    )
    raw = T._strip_fence(generate_script_text(get_settings(), prompt))
    try:
        text = json.loads(raw)["text"].strip()
    except (json.JSONDecodeError, KeyError, TypeError, AttributeError) as exc:
        raise T.ThumbnailError(f"AI ตอบกลับในรูปแบบที่อ่านไม่ได้: {raw[:120]}") from exc
    if not text:
        raise T.ThumbnailError("AI ไม่ได้ส่งข้อความกลับมา")
    _remember(data, "rewrite", note)
    _save(folder, data)
    return set_text(folder, text)


_FIELD_LABELS = {"scene": "ฉากหลัง", "time": "ช่วงเวลา", "pose": "ท่าทางตัวละคร", "prop": "ของประกอบ", "template": "แนวภาพ",
                "palette": "ตัวละคร", "side": "ตำแหน่ง", "accent": "สีแสง", "view": "มุมมอง", "mood": "อารมณ์"}
_VALUE_LABELS = {"default": "ท้องฟ้า/เมืองเปิดโล่ง", "train_station": "สถานีรถไฟฟ้า", "office": "ออฟฟิศ", "bedroom": "ห้องนอน",
                 "street": "ถนนในเมือง", "day": "กลางวัน", "dusk": "เย็น", "night": "กลางคืน", None: "ไม่มี"}


def _describe_changes(old: dict, new: dict, text_changed: bool) -> str:
    """Plain-Thai summary built from what really changed (never taken from the model's own words)."""
    parts = [f"{label}: {_VALUE_LABELS.get(old.get(k), old.get(k))} → {_VALUE_LABELS.get(new.get(k), new.get(k))}"
             for k, label in _FIELD_LABELS.items() if old.get(k) != new.get(k)]
    parts.append("เปลี่ยนคำบนปก" if text_changed else "คำบนปกคงเดิม")
    return " · ".join(parts) if len(parts) > 1 else "ไม่มีส่วนไหนเปลี่ยน (คำสั่งอาจอยู่นอกสิ่งที่ปกวาดได้) " + parts[0]


def edit_concept(folder: str, note: str) -> dict:
    """Apply the creator's instruction to the CURRENT cover concept only: one Gemini text call returns the edited
    concept fields (setting, time of day, pose, prop, colours...). The Thai text stays exactly as it is unless the
    instruction asks to change the words."""
    note = note.strip()
    if not note:
        raise T.ThumbnailError("พิมพ์สิ่งที่อยากแก้ในช่องก่อน แล้วค่อยกด 'ให้ AI แก้ตามที่พิมพ์'")
    entry, data = _entry(folder), load(folder)
    if data is None:
        raise KeyError(folder)
    if data.get("base"):
        raise T.ThumbnailError("ปกนี้ใช้ภาพจากฉากในวิดีโอ ให้ AI แก้ภาพไม่ได้ ใช้ 'แก้ข้อความบนปก' หรือ 'ให้ AI เขียนคำใหม่' เพื่อเปลี่ยนคำ "
                               "หรือ 'สร้างแบบใหม่ทั้งหมด (AI)' ถ้าอยากเปลี่ยนภาพ")
    current = data["concepts"][data["choice"]]
    raw = T._strip_fence(generate_script_text(get_settings(), T.build_edit_prompt(current, data["text"], note)))
    try:
        reply = json.loads(raw)
        edited = {**current, **reply["concept"]}
        if not reply.get("change_text"):
            edited["thai_text"] = current["thai_text"]
        concept = T.ThumbnailConcept.model_validate(edited)
    except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        raise T.ThumbnailError(f"AI ตอบกลับในรูปแบบที่ใช้ไม่ได้ ({str(exc)[:120]}) ลองพิมพ์ใหม่ให้ชัดขึ้น") from exc
    data["concepts"][data["choice"]] = concept.model_dump()
    if reply.get("change_text"):
        data["text"] = concept.thai_text
    data["last_edit_note"] = _describe_changes(current, concept.model_dump(), bool(reply.get("change_text")))
    data["error"] = None
    _remember(data, "edit", note)
    _save(folder, data)
    return render(folder)


def ensure(folder: str) -> None:
    """Called after a render: create the cover once; keep the user's edits if it exists."""
    if load(folder) is None:
        generate(folder)
    else:
        render(folder)


if __name__ == "__main__":
    # python covers.py            -> make covers for every episode that lacks one
    # python covers.py --all      -> regenerate every cover with fresh AI concepts
    for e in library.episodes():
        if "--all" in sys.argv or load(e["folder"]) is None:
            d = generate(e["folder"])
            print(e["folder"], "->", d["text"].replace("\n", " / "), "|", d["error"] or "ok")
