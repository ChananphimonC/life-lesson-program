"""AI-assisted YouTube thumbnail studio for the cartoon episodes.

No image-generation API is used. Thumbnails are composed from the same
procedural renderer that draws the episodes themselves (`character.py`,
`art.py`), so every thumbnail automatically matches the channel's actual
illustrated art direction instead of looking like a bolted-on AI-art style.

The only API call in this module is a single Gemini **text** call (the same
`generate_script_text` wrapper already used for episode scripts) that
analyzes the story and proposes 3 distinct thumbnail concepts. All Thai
typography is drawn locally afterward -- never baked in by a model -- so
there is no risk of malformed Thai glyphs.

    from thumbnail_studio import analyze_story, render_concept, compose_text, ...

`thumbnail_app.py` is the local web UI built on top of this module.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Literal

from PIL import Image, ImageDraw, ImageFilter
from pydantic import BaseModel, Field, ValidationError, field_validator

import art
import character as C
from art import INK, Pen, mix, paste
from life_lesson.config import Settings
from life_lesson.errors import PipelineError
from life_lesson.generation.gemini_client import generate_script_text
from scenes import place
from scenes_ep03 import thai_font
import thai_text as TT
import thumbnail_scenes

HERE = Path(__file__).resolve().parent
STORE_DIR = HERE / "output" / "thumbnails"


class ThumbnailError(PipelineError):
    """Raised when the analysis model's output can't be used as-is."""


# --- building blocks reused by every template -------------------------------------

def hexrgb(s: str) -> tuple[int, int, int]:
    s = s.lstrip("#")
    if len(s) != 6 or any(c not in "0123456789abcdefABCDEF" for c in s):
        raise ValueError(f"not a hex color: {s!r}")
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


def _p_stand(view="side", **_):
    return C.stand(look=(1.4, 0.3), view=view)


def _p_sit_phone(**_):
    return C.sit_phone()


def _p_hug_knees(**_):
    return C.hug_knees(look=(1.3, 0.6))


def _p_clutch_chest(**_):
    return C.clutch_chest()


def _p_hold_paper(**_):
    return C.hold_paper()


def _p_phone_up(**_):
    return C.phone_up()


def _p_type_desk(**_):
    return C.type_desk()


def _p_asleep_desk(**_):
    return C.asleep_desk()


def _p_recline_bed(**_):
    return C.recline_bed()


def _p_front_phone(**_):
    return C.front_phone()


def _p_sit_desk_chin(**_):
    return C.sit_desk_chin(look=(1.5, 0.7))


POSES = {
    "stand": _p_stand, "sit_phone": _p_sit_phone, "hug_knees": _p_hug_knees,
    "clutch_chest": _p_clutch_chest, "hold_paper": _p_hold_paper, "phone_up": _p_phone_up,
    "type_desk": _p_type_desk, "asleep_desk": _p_asleep_desk, "recline_bed": _p_recline_bed,
    "front_phone": _p_front_phone, "sit_desk_chin": _p_sit_desk_chin,
}

PALETTES = {"MAIN": C.MAIN, "IDEAL": C.IDEAL, "OTHER": C.OTHER,
            **{f"OTHERS{i}": p for i, p in enumerate(C.OTHERS)}}

TIME_GRAD = {
    "day": [(0, (168, 202, 232)), (0.55, (234, 220, 198)), (1, (220, 198, 170))],
    "dusk": [(0, (72, 62, 116)), (0.48, (198, 104, 102)), (1, (236, 170, 116))],
    "night": [(0, (16, 18, 40)), (0.55, (32, 34, 64)), (1, (46, 46, 76))],
}
GROUND_COLOR = {"day": (196, 172, 140), "dusk": (90, 70, 90), "night": (30, 30, 48)}


def _sky(w, h, time):
    return art.vgradient(w, h, TIME_GRAD[time])


def _ground_band(pen, w, h, time):
    y0 = int(h * 0.82)
    pen.rect(0, y0, w, h, GROUND_COLOR[time])
    pen.rect(0, y0 - 4, w, y0 + 4, INK)
    return y0


def _stage(concept, w, h, time=None):
    """The backdrop Pen for a concept: the chosen setting, or the default sky + ground."""
    time = time or concept.time
    if concept.scene != "default":
        return Pen(w, h, base=thumbnail_scenes.scene_image(concept.scene, w, h, time, _sky(w, h, time)))
    pen = Pen(w, h, base=_sky(w, h, time))
    _ground_band(pen, w, h, time)
    return pen


# A pose's apparent on-screen height as a fraction of a standing figure's --
# `_char_scale` assumes full standing height, so seated/crouched poses are
# compensated here or they'd render much smaller than intended.
HEIGHT_FRAC = {"stand": 1.0, "front_phone": 1.0, "hold_paper": 1.0, "phone_up": 1.0,
               "clutch_chest": 0.95, "sit_phone": 0.6, "sit_desk_chin": 0.6, "type_desk": 0.6,
               "recline_bed": 0.55, "hug_knees": 0.42, "asleep_desk": 0.35}


def _char_scale(h, frac, pose_name):
    return h * frac / C.ORIGIN_Y / HEIGHT_FRAC[pose_name]


def _place_char(canvas, pose, pal, scale, x, ground_y, facing):
    spr = C.render(pose, pal, scale, facing)
    place(canvas, spr, x, ground_y, scale, facing)


def _vignette(img, strength=0.5):
    w, h = img.size
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).ellipse((-w * 0.15, -h * 0.25, w * 1.15, h * 1.25), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(min(w, h) * 0.16))
    dark = Image.new("RGB", (w, h), (8, 6, 14))
    vignetted = Image.composite(img, dark, mask)
    return Image.blend(img, vignetted, strength)


# --- symbolic props: drawn directly at whatever size is needed, so they stay crisp
# even scaled up large in "object_hero" (no raster upscaling). ----------------------

def _sym_coin(size=220):
    pen = Pen(size, int(size * 0.78))
    cx, cy = size / 2, pen.h * 0.66
    for dy in (0.12, 0.06, 0.0):
        pen.ellipse(cx, cy - dy * size, size * 0.42, size * 0.18, (236, 196, 98))
    pen.ellipse(cx, cy - 0.15 * size, size * 0.42, size * 0.18, (250, 216, 122))
    pen.circle(cx, cy - 0.15 * size, size * 0.14, (220, 176, 80))
    return art.inked(pen.result(), max(2.0, size * 0.016))


def _sym_envelope(size=220):
    w, h = size, int(size * 0.68)
    pen = Pen(w, h)
    pen.rect(6, 6, w - 6, h - 6, (252, 250, 244), radius=8)
    pen.line([(6, 8), (w / 2, h * 0.62), (w - 6, 8)], (190, 184, 180), max(2, w * 0.02))
    pen.circle(w / 2, h * 0.58, h * 0.14, (214, 90, 80))
    return art.inked(pen.result(), max(2.0, w * 0.016))


def _sym_heart(size=220):
    pen = Pen(size, size)
    s = size / 140
    pen.circle(46 * s, 50 * s, 32 * s, (230, 96, 112))
    pen.circle(94 * s, 50 * s, 32 * s, (230, 96, 112))
    pen.poly([(14 * s, 62 * s), (126 * s, 62 * s), (70 * s, 128 * s)], (230, 96, 112))
    return art.inked(pen.result(), max(2.0, size * 0.02))


def _sym_clock(size=220):
    pen = Pen(size, size)
    r = size * 0.42
    pen.circle(size / 2, size / 2, r, (250, 248, 240))
    pen.line([(size / 2, size / 2), (size / 2, size / 2 - r * 0.55)], INK, size * 0.035)
    pen.line([(size / 2, size / 2), (size / 2 + r * 0.4, size / 2 + r * 0.1)], INK, size * 0.035)
    return art.inked(pen.result(), max(2.0, size * 0.02))


def _sym_bag(size=220):
    pen = Pen(size, size)
    pen.arc(size / 2, size * 0.28, size * 0.2, size * 0.16, 180, 360, INK, size * 0.035)
    pen.rect(size * 0.14, size * 0.3, size * 0.86, size * 0.92, (196, 132, 92), radius=size * 0.04)
    return art.inked(pen.result(), max(2.0, size * 0.018))


def _sym_document(size=220):
    w, h = size, int(size * 1.24)
    pen = Pen(w, h)
    pen.rect(10, 10, w - 10, h - 10, (252, 250, 244), radius=8)
    for i, y in enumerate(range(int(h * 0.24), int(h * 0.82), max(1, int(h * 0.11)))):
        pen.rect(w * 0.14, y, (w * 0.86 if i % 2 else w * 0.7), y + h * 0.045, (205, 200, 198))
    return art.inked(pen.result(), max(2.0, w * 0.018))


def _sym_phone(size=220):
    w, h = int(size * 0.56), size
    pen = Pen(w, h)
    pen.rect(6, 6, w - 6, h - 6, (40, 42, 56), radius=w * 0.18)
    pen.rect(w * 0.12, h * 0.08, w * 0.88, h * 0.9, (236, 240, 246), radius=w * 0.08)
    return art.inked(pen.result(), max(2.0, w * 0.03))


def _sym_hourglass(size=220):
    w, h = int(size * 0.62), size
    pen = Pen(w, h)
    pen.rect(0, 0, w, h * 0.08, INK, radius=w * 0.08)
    pen.rect(0, h * 0.92, w, h, INK, radius=w * 0.08)
    pen.poly([(w * 0.12, h * 0.08), (w * 0.88, h * 0.08), (w * 0.56, h * 0.5), (w * 0.88, h * 0.92),
              (w * 0.12, h * 0.92), (w * 0.44, h * 0.5)], (236, 196, 98))
    return art.inked(pen.result(), max(2.0, w * 0.025))


SYMBOLS = {"coin": _sym_coin, "envelope": _sym_envelope, "heart": _sym_heart, "clock": _sym_clock,
           "bag": _sym_bag, "document": _sym_document, "phone": _sym_phone, "hourglass": _sym_hourglass}


# --- the 4 composition templates ----------------------------------------------------

def tpl_portrait(concept, w, h):
    """One large expressive character, rule-of-thirds, a lit prop on the empty side."""
    time = concept.time
    pen = _stage(concept, w, h)
    accent = hexrgb(concept.accent)
    side_right = concept.side == "right"
    cx = w * 0.72 if side_right else w * 0.28
    img = art.add_glow(pen.result(), cx, h * 0.5, h * 0.62, accent, 0.3)
    canvas = img.convert("RGBA")
    scale = _char_scale(h, 0.78, concept.pose)
    pose = POSES[concept.pose](view=concept.view)
    facing = -1 if side_right else 1
    _place_char(canvas, pose, PALETTES[concept.palette], scale, cx, h * 0.97, facing)
    if concept.prop:
        px, py = (w * 0.26 if side_right else w * 0.74), h * 0.36
        sym = SYMBOLS[concept.prop](size=int(h * 0.26))
        glow = art.glow_sprite(int(h * 0.22), accent, 170)
        paste(canvas, glow, px - glow.width / 2, py - glow.height / 2)
        paste(canvas, sym, px - sym.width / 2, py - sym.height / 2)
    return _vignette(canvas.convert("RGB"), 0.45)


def tpl_wide_symbolic(concept, w, h):
    """The character small and distant inside a big atmospheric scene."""
    time = concept.time
    in_scene = concept.scene != "default"
    pen = _stage(concept, w, h) if in_scene else Pen(w, h, base=_sky(w, h, time))
    accent = hexrgb(concept.accent)
    y0 = int(h * 0.82)
    if in_scene:
        pass
    elif time == "night":
        art.stars(pen, 0, 0, w, int(y0 * 0.7), max(20, w // 22), seed=len(concept.name) + 1)
        art.city_skyline(pen, 0, w, y0, (26, 28, 50), lit=0.3, max_h=int(h * 0.42), seed=3)
    else:
        art.hills(pen, 0, w, int(h * 0.68), int(h * 0.05),
                  mix(TIME_GRAD[time][-1][1], (60, 90, 60), 0.5), period=w * 0.4)
    if not in_scene:
        pen.rect(0, y0, w, h, GROUND_COLOR[time])
    gx = w * 0.72 if concept.side == "right" else w * 0.28
    img = art.add_glow(pen.result(), gx, int(h * 0.55), int(h * 0.5), accent, 0.5)
    canvas = img.convert("RGBA")
    scale = _char_scale(h, 0.3, concept.pose)
    pose = POSES[concept.pose](view=concept.view)
    _place_char(canvas, pose, PALETTES[concept.palette], scale, w * 0.5, y0 + h * 0.005, 1)
    return _vignette(canvas.convert("RGB"), 0.6)


def tpl_contrast_split(concept, w, h):
    """The frame split in two, showing the contradiction directly."""
    accent = hexrgb(concept.accent)
    if concept.scene != "default":
        left = _stage(concept, w, h, "day").result().convert("RGB").crop((0, 0, w // 2, h))
        right = _stage(concept, w, h, "night").result().convert("RGB").crop((w // 2, 0, w, h))
    else:
        left = art.vgradient(w // 2, h, TIME_GRAD["dusk"])
        right = art.vgradient(w - w // 2, h, TIME_GRAD["night"])
    canvas = Image.new("RGB", (w, h))
    canvas.paste(left, (0, 0))
    canvas.paste(right, (w // 2, 0))
    canvas = art.add_glow(canvas, int(w * 0.25), int(h * 0.5), int(h * 0.55), accent, 0.25 if concept.scene != "default" else 0.4)
    canvas = art.add_glow(canvas, int(w * 0.75), int(h * 0.5), int(h * 0.5), (40, 40, 60), 0.3).convert("RGBA")
    ImageDraw.Draw(canvas).line((w / 2, 0, w / 2, h), fill=(*INK, 160), width=max(2, int(w * 0.004)))
    scale = _char_scale(h, 0.5, concept.pose)
    pose_view = "front" if concept.pose == "stand" else concept.view
    pose = POSES[concept.pose](view=pose_view)
    _place_char(canvas, pose, PALETTES[concept.palette], scale, w / 2, h * 0.95, 1)
    if concept.prop:
        sym = SYMBOLS[concept.prop](size=int(h * 0.2))
        paste(canvas, sym, w * 0.22 - sym.width / 2, h * 0.3)
        r, g, b, a = sym.split()
        dim = Image.merge("RGBA", (r.point(lambda v: int(v * 0.5)), g.point(lambda v: int(v * 0.5)),
                                   b.point(lambda v: int(v * 0.6)), a))
        paste(canvas, dim, w * 0.78 - dim.width / 2, h * 0.3)
    return _vignette(canvas.convert("RGB"), 0.35)


def tpl_object_hero(concept, w, h):
    """A single symbolic object, large and dominant; the character small beneath it."""
    time = concept.time
    pen = _stage(concept, w, h)
    accent = hexrgb(concept.accent)
    img = art.add_glow(pen.result(), w / 2, h * 0.42, h * 0.6, accent, 0.55)
    canvas = img.convert("RGBA")
    sym = SYMBOLS[concept.prop or "coin"](size=int(h * 0.62))
    paste(canvas, sym, w / 2 - sym.width / 2, h * 0.08)
    scale = _char_scale(h, 0.26, concept.pose)
    pose = POSES[concept.pose](view=concept.view)
    _place_char(canvas, pose, PALETTES[concept.palette], scale, w * 0.5, h * 0.95, 1)
    return _vignette(canvas.convert("RGB"), 0.5)


TEMPLATES = {"portrait": tpl_portrait, "wide_symbolic": tpl_wide_symbolic,
             "contrast_split": tpl_contrast_split, "object_hero": tpl_object_hero}


# --- Gemini analysis: text only, reuses the already-approved script-generation call --

class ThumbnailConcept(BaseModel):
    name: str = Field(min_length=1)
    visual_hook: str = Field(min_length=1)
    template: Literal["portrait", "wide_symbolic", "contrast_split", "object_hero"]
    pose: str
    view: Literal["side", "front"] = "side"
    mood: Literal["calm", "pensive"] = "pensive"
    palette: str = "MAIN"
    time: Literal["day", "dusk", "night"] = "dusk"
    scene: Literal["default", "train_station", "office", "bedroom", "street", "studio"] = "default"
    prop: str | None = None
    side: Literal["left", "right"] = "right"
    accent: str = "#E0A043"
    thai_text: str = Field(min_length=1)
    rationale: str = ""
    risks: str = ""

    @field_validator("pose")
    @classmethod
    def _pose_known(cls, v):
        if v not in POSES:
            raise ValueError(f"unknown pose {v!r}; must be one of {sorted(POSES)}")
        return v

    @field_validator("palette")
    @classmethod
    def _palette_known(cls, v):
        if v not in PALETTES:
            raise ValueError(f"unknown palette {v!r}; must be one of {sorted(PALETTES)}")
        return v

    @field_validator("prop")
    @classmethod
    def _prop_known(cls, v):
        if v is not None and v not in SYMBOLS:
            raise ValueError(f"unknown prop {v!r}; must be one of {sorted(SYMBOLS)} or null")
        return v

    @field_validator("accent")
    @classmethod
    def _accent_hex(cls, v):
        hexrgb(v)
        return v


class StoryAnalysis(BaseModel):
    primary_emotion: str
    central_conflict: str
    visual_moment: str
    hook_question: str
    audience_fit: str
    concepts: list[ThumbnailConcept] = Field(min_length=3, max_length=3)

    @field_validator("concepts")
    @classmethod
    def _distinct_templates(cls, v):
        templates = [c.template for c in v]
        if len(set(templates)) != len(templates):
            raise ValueError("the 3 concepts must use 3 different templates, got "
                              f"{templates}")
        return v


def _strip_fence(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        stripped = "\n".join(lines).strip()
    return stripped


LIFE_LESSON_INTRO = """You are a YouTube thumbnail strategist and creative director for a Thai \
channel of short, cinematic animated life-reflection stories (loneliness in \
crowded cities, feeling behind in life, sacrificing health and time for \
money, regret, relationships, the meaning of life). The audience is adults \
who relate to these emotional and philosophical themes -- this is not \
children's content even though it is animated. The goal is to improve the \
probability of a relevant viewer clicking, not to chase clicks with \
misleading claims.

"""


def _build_analysis_prompt(title: str, summary: str, channel: str | None = None, tone: str | None = None) -> str:
    pose_list = ", ".join(sorted(POSES))
    palette_list = ", ".join(sorted(PALETTES))
    prop_list = ", ".join(sorted(SYMBOLS))
    scene_list = ", ".join(f'"{n}"' for n in thumbnail_scenes.SCENE_NAMES)
    tone_line = f"Tone of the video (the cover must match it): {tone}\n" if tone else ""
    return f"""\
{(channel and f'You are a YouTube thumbnail strategist and creative director for {channel}. The goal is to improve the probability of a relevant viewer clicking, not to chase clicks with misleading claims.' + chr(10) + chr(10)) or LIFE_LESSON_INTRO}Episode title: {title}
{tone_line}Story summary or transcript: {summary}

STEP 1 -- Analyze (1-2 sentences each):
- primary_emotion: the main emotion the viewer should feel
- central_conflict: the central conflict or contradiction in the story
- visual_moment: the single most visually compelling moment or metaphor
- hook_question: the unanswered question that could make a relevant viewer click
- audience_fit: who this resonates with and why

STEP 2 -- Propose exactly 3 GENUINELY DIFFERENT thumbnail concepts (not \
minor variations of the same shot). Each concept must use a different \
"template" value out of these four:
- "portrait": one large expressive character close-up, rule-of-thirds, a \
symbolic object softly lit on the empty side.
- "wide_symbolic": the character small and distant inside a big atmospheric \
scene (skyline, open space) -- scale and environment carry the emotion, not \
a face.
- "contrast_split": the frame visually split in two (warm/cold, light/dark) \
with the character and/or a symbolic object showing the contradiction \
directly.
- "object_hero": one symbolic object rendered large and dominant, the \
character small beneath it looking up -- the object IS the metaphor.

For each concept give exactly these fields:
- name: a short concept name
- visual_hook: the hook in one sentence
- template: one of the four keys above (each concept MUST use a different one)
- pose: one of [{pose_list}]
- view: "side" or "front"
- mood: "calm" or "pensive"
- palette: one of [{palette_list}] ("MAIN" is the protagonist; "IDEAL" is a \
soft glowing idealized figure; "OTHER"/"OTHERSn" are muted background figures)
- time: "day", "dusk", or "night"
- scene: one of ["default", {scene_list}] -- the setting behind the character ("default" = open sky / skyline / ground)
- prop: one of [{prop_list}], or null if the concept needs none
- side: "left" or "right" -- which side of frame the character/object sits on
- accent: one hex color (e.g. "#E0A043") used for the key light/glow
- thai_text: 2-5 short Thai words for the on-thumbnail text
- rationale: one sentence on why this concept may attract the intended viewer
- risks: one sentence on its potential weakness

Rules for every concept:
- One dominant focal point, one primary emotional message, legible at small \
mobile size.
- Never use misleading tragedy, fake numbers, fabricated events, or a visual \
promise absent from the actual story.
- No religious references, and no quoted or paraphrased sayings attributed \
to anyone.
- No generic "never give up" / motivational-poster language in thai_text.
- Do not force "portrait" (a face close-up) if "wide_symbolic" or \
"object_hero" would tell the story more powerfully -- genuinely vary which \
template fits each concept best.
- The cover must look like the video: a bright, colourful video gets a bright cover (time "day", \
warm accent, friendly pose), a calm or heavy video gets a muted one. Never make a bright video look gloomy.
- If the episode title names a key term (a test, a concept, a number, a product name such as MBTI), \
thai_text or visual_hook must contain that term exactly as written in the title (Latin letters are fine). \
A viewer who searched for the term must recognise the video at once.

Respond with ONLY a single JSON object (no markdown fences, no commentary) \
matching exactly this structure:
{{
  "primary_emotion": "...", "central_conflict": "...", "visual_moment": "...",
  "hook_question": "...", "audience_fit": "...",
  "concepts": [
    {{"name": "...", "visual_hook": "...", "template": "...", "pose": "...",
      "view": "...", "mood": "...", "palette": "...", "time": "...",
      "prop": "..." , "side": "...", "accent": "#RRGGBB", "thai_text": "...",
      "rationale": "...", "risks": "..."}},
    ... (exactly 3, each a different template)
  ]
}}"""


def build_edit_prompt(concept: dict, text: str, note: str) -> str:
    scenes = "\n".join(f'- "{k}": {v}' for k, v in thumbnail_scenes.SCENE_HELP.items())
    return f"""\
You edit ONE thumbnail concept for a Thai life-reflection YouTube channel. The picture is drawn by code from the fields
below; you cannot paint arbitrary pixels, only choose these fields.

Current concept (JSON): {json.dumps(concept, ensure_ascii=False)}
Current Thai text on the thumbnail: {text}

Creator's instruction (may be in Thai): {note}

Allowed values:
- template: portrait | wide_symbolic | contrast_split | object_hero
- pose: {", ".join(sorted(POSES))}
- view: side | front;  mood: calm | pensive;  time: day | dusk | night;  side: left | right
- palette: {", ".join(sorted(PALETTES))}
- prop: {", ".join(sorted(SYMBOLS))} or null
- accent: a hex color like "#E0A043"
- scene: "default" or one of
{scenes}

Rules:
- Change ONLY what the instruction asks for and keep every other field exactly as it is.
- The Thai text must stay exactly the same unless the instruction explicitly asks to change the words.
- If the requested setting is not in the list, pick the closest scene and say so in "note" (in Thai, one short sentence).
- A setting such as a metro / BTS / skytrain / MRT station or platform means scene "train_station".

Respond with ONLY this JSON:
{{"concept": {{...the full concept with your edits...}}, "change_text": false, "note": "what you changed, in Thai"}}
"""


def analyze_story(settings: Settings, title: str, summary: str, note: str = "",
                  channel: str | None = None, tone: str | None = None) -> StoryAnalysis:
    prompt = _build_analysis_prompt(title, summary, channel, tone)
    if note.strip():
        prompt += ("\n\nCreator's extra request (apply it to the concepts and the Thai text; the art is "
                   "drawn procedurally from the fields above, so treat it as a concept/text instruction, "
                   f"not a pixel edit). Still follow every rule above:\n{note.strip()}")
    for attempt in range(3):  # the model sometimes returns slightly broken JSON; asking again almost always fixes it
        raw = generate_script_text(settings, prompt)
        try:
            data = json.loads(_strip_fence(raw))
            break
        except json.JSONDecodeError as exc:
            if attempt == 2:
                raise ThumbnailError(f"model output is not valid JSON: {exc}") from exc
    try:
        return StoryAnalysis.model_validate(data)
    except ValidationError as exc:
        raise ThumbnailError(f"model output failed schema validation: {exc}") from exc


def render_concept(concept: ThumbnailConcept, w: int = 1920, h: int = 1080) -> Image.Image:
    return TEMPLATES[concept.template](concept, w, h)


# --- crop / focal point + editable Thai text overlay ---------------------------------

def apply_crop(image: Image.Image, fx: float = 0.5, fy: float = 0.5, zoom: float = 1.0) -> Image.Image:
    zoom = max(1.0, min(zoom, 2.5))
    w, h = image.size
    cw, ch = w / zoom, h / zoom
    cx, cy = max(0.0, min(1.0, fx)) * w, max(0.0, min(1.0, fy)) * h
    x0 = min(max(0.0, cx - cw / 2), w - cw)
    y0 = min(max(0.0, cy - ch / 2), h - ch)
    return image.resize((w, h), Image.LANCZOS, box=(x0, y0, x0 + cw, y0 + ch))


def compose_text(image: Image.Image, text: str, *, size: int = 96, bold: bool = True,
                  color: str = "#FFFFFF", outline: bool = True, outline_color: str = "#2B2016",
                  shadow: bool = True, scrim: bool = True, anchor: str = "bottom-center",
                  margin_frac: float = 0.06) -> Image.Image:
    """`anchor` is "<top|center|bottom>-<left|center|right>". `text` may
    contain explicit "\\n" line breaks (Thai has no reliable auto word-wrap
    without a tokenizer, so the editor lets the user place breaks by hand)."""
    img = image.convert("RGBA")
    w, h = img.size
    if not text.strip():
        return img.convert("RGB")
    lines = text.split("\n")
    f = thai_font(size, bold)
    line_h = int(size * 1.25)
    total_h = line_h * len(lines)
    mx, my = int(w * margin_frac), int(h * margin_frac)
    vert, horiz = anchor.split("-")
    y0 = {"top": my, "center": (h - total_h) // 2, "bottom": h - my - total_h}[vert]
    x = {"left": mx, "center": w // 2, "right": w - mx}[horiz]
    h_anchor = {"left": "l", "center": "m", "right": "r"}[horiz]

    if scrim:
        band_h = total_h + 2 * my
        by = {"top": 0, "center": max(0, y0 - my), "bottom": h - band_h}[vert]
        band = Image.new("L", (w, band_h), 0)
        bd = ImageDraw.Draw(band)
        for i in range(band_h):
            if vert == "bottom":
                a = int(150 * (i / band_h))
            elif vert == "top":
                a = int(150 * (1 - i / band_h))
            else:
                a = 100
            bd.line((0, i, w, i), fill=a)
        layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
        layer.paste((10, 8, 14, 255), (0, by), band)
        img = Image.alpha_composite(img, layer)

    ow = max(2, size // 13)
    if shadow:
        shadow_layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
        sd = ImageDraw.Draw(shadow_layer)
        yy = y0
        for ln in lines:
            TT.draw_line(sd, (x + 5, yy + 7), ln, f, (0, 0, 0, 190), anchor=h_anchor + "a")
            yy += line_h
        shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(size * 0.045))
        img = Image.alpha_composite(img, shadow_layer)

    draw = ImageDraw.Draw(img)
    yy = y0
    for ln in lines:
        TT.draw_line(draw, (x, yy), ln, f, hexrgb(color), anchor=h_anchor + "a",
                     stroke_width=ow if outline else 0,
                     stroke_fill=hexrgb(outline_color) if outline else None)
        yy += line_h
    return img.convert("RGB")


def export_image(image: Image.Image, path: Path, fmt: str = "jpeg", max_bytes: int = 2_000_000) -> Path:
    """Saves within YouTube's upload size limit (2 MB), lowering JPEG quality
    (then as a last resort downscaling) until it fits."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if fmt == "png":
        image.save(path, "PNG", optimize=True)
        return path
    quality, img = 95, image.convert("RGB")
    while True:
        img.save(path, "JPEG", quality=quality, optimize=True)
        if path.stat().st_size <= max_bytes or (quality <= 40 and img.width <= 960):
            return path
        if quality > 40:
            quality -= 10
        else:
            img = img.resize((int(img.width * 0.85), int(img.height * 0.85)), Image.LANCZOS)


# --- JSON persistence, mirroring library.py's info.json pattern ----------------------

def slug_for(title: str) -> str:
    return "adhoc-" + hashlib.sha1(title.encode("utf-8")).hexdigest()[:10]


def store_dir(key: str) -> Path:
    d = STORE_DIR / key
    d.mkdir(parents=True, exist_ok=True)
    return d


def load_store(key: str) -> dict:
    p = store_dir(key) / "studio.json"
    if p.is_file():
        return json.loads(p.read_text(encoding="utf-8"))
    return {"key": key, "episode_id": None, "title": None, "analysis": None, "concepts": [],
            "concept_settings": {}, "exports": [], "outcomes": []}


def save_store(key: str, data: dict) -> None:
    (store_dir(key) / "studio.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


# --- episode source material ----------------------------------------------------------

def episode_options() -> list[dict]:
    import library
    return [{"key": e["episode_id"], "label": f"EP{e['ep']:02d} - {e['title']}",
             "title": e["title"], "topic": e.get("topic") or "", "theme": e.get("theme") or ""}
            for e in library.episodes()]


def episode_transcript(settings: Settings, episode_id: str) -> str:
    """The full narration transcript for an episode, joined from its
    validated script blocks -- the richest "story summary" input available."""
    conn = sqlite3.connect(settings.db_path)
    conn.row_factory = sqlite3.Row
    row = conn.execute(
        "SELECT raw_json FROM scripts WHERE episode_id = ? AND validated = 1 "
        "ORDER BY id DESC LIMIT 1", (episode_id,)).fetchone()
    if row is None:
        return ""
    data = json.loads(row["raw_json"])
    return "\n".join(b["text"] for b in data.get("script_blocks", []))
