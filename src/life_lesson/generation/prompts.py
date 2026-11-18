"""Script-generation prompt template.

The full Critic system (AI_DESIGN.md §4) is a v0.3 feature and is NOT
implemented here. But per the v0.1 implementation brief, the core content
constraints from PRODUCT.md §3.2 must still be embedded directly in the
generation prompt itself -- this is a best-effort constraint at generation
time, not a substitute for the Critic's later verification pass.
"""

from __future__ import annotations

from life_lesson.generation.formats import FormatSpec, get_format

SCRIPT_PROMPT_NAME = "script_generation"
SCRIPT_PROMPT_STAGE = "script"
SCRIPT_PROMPT_VERSION = "script-v0.4.1"

_CONTENT_CONSTRAINTS = """\
This is a LIFE REFLECTION, not life advice or motivational content.

It must NOT:
- Teach religion or reference/paraphrase Buddhist or any religious teaching.
- Quote or attribute statements to Buddha, famous people, authors, or books \
(even paraphrased, even without a name attached).
- Reproduce or lightly reword existing motivational content.
- Give therapy, diagnose, or make any clinical/psychological claim.
- Give prescriptive advice or tell the listener what they "should", "must", \
or "need to" do.
- Promise that a particular mindset or perspective will solve the listener's \
problem.
- Use generic motivational clichés (e.g. "never give up", "tomorrow is a new day").
- Use manipulative, guilt-tripping, or preachy language.

It MUST:
- Observe a specific, grounded human experience without rushing to resolve it.
- Explore the feeling honestly -- why it hurts, how it shows up.
- In the "shift" phase, offer a different angle or perspective ONLY -- never \
a fix, technique, or instruction. If a sentence could be reworded as \
"so you should...", it is wrong.
- End on an open, unresolved reflection -- no summary, no lesson, no call to \
action.
- Be written in natural, spoken, conversational Thai (ภาษาพูด).\
"""

_STYLE_RULES = """\
STYLE (see docs/STYLE_GUIDE.md):
- Narrate in second person, present tense ("คุณนั่งอยู่ตรงนั้น..."): place the \
listener inside the scene. This is a way of telling, never a way of instructing.
- Show before you explain: concrete things the listener can SEE and HEAR \
(a clock reading 23:47, a cold cup of tea) come before any feeling is named.
- Use specific, everyday numbers (times, prices, distances, counts). Never \
invent statistics or cite studies you cannot name.
- Short spoken sentences. One longer sentence per chapter at most, for breath.
- Choose ONE small recurring motif (an object or a sound). Let it appear at \
least 3 times and return in the outro WITHOUT explaining what it means.
- Open with the moment of most tension or quiet (a cold open), not a greeting \
and not an introduction.
- Every block of narration must pass this test: said to a friend, it feels \
like comfort, not like a suggestion. The ending stays open.
- Separate real from invented: put real-world facts you rely on in "facts" \
(claim, source_hint as a TYPE of source, confidence). Characters, events and \
places you invent are fiction and must not appear in "facts".
- STORY CRAFT: give the main character a specific, ordinary want in the first \
30 seconds; plant a small open question early and answer it only partly; end \
each chapter on a concrete image or a line that makes the listener lean in, \
never on a moral.
- CHARACTERS: invent at most 3 people. For each, fix ONE outfit and ONE \
signature item and list them in "characters" (name, role, age_range, outfit, \
signature_item, palette). Keep the outfit identical in every visual_cue. Never \
base a character on a real person.
- ATMOSPHERE: give EVERY block a "mood" so picture, sound and voice agree. \
Use only these values: light (bright|dim|dark|golden|neon|flicker), weather \
(clear|rain|storm|fog|wind), color (warm|cool|teal|amber|mono|green), voice \
(calm|hushed|warm|wistful|tense|urgent), sounds (any of rain|thunder|wind|\
waves|room_tone|heartbeat|clock|silence), tension (integer 1-5). \
Shape a TENSION CURVE: start low or with one sharp image, climb across the \
exploration, peak at the start of the shift, then let it fall (not to 1) in \
the outro so the ending stays open. Change light/weather at turning points; \
let weather mirror the feeling without naming it (rain when plans fall \
apart, fog when nobody is sure, a flickering lamp when money is short). \
Match voice to tension (hushed for secrets, tense/urgent only at peaks).
- SETTING & WARDROBE: give every block a "setting" (room|office|street|city|sea|\
island|forest|night_sky|food_stall) and mention concrete props in visual_cue \
(e.g. wok on a flame, plastic stools, menu board). Say what each person wears \
in their "outfit" including accessories that fit the place and the job (apron, \
hairnet, raincoat hood, backpack, lanyard, glasses) and whether sleeves are \
short or long. Keep each person's base outfit identical across scenes.
- TITLE: write "title" as two short Thai phrases separated by ONE space \
(2-4 words each, e.g. "กะเพรา จานสุดท้าย"); they become the two thumbnail \
lines, so never rely on a long unbroken string.
- Never describe violence, injury, death or any crisis topic.\
"""


def _format_rules(spec: FormatSpec) -> str:
    base = (
        f"FORMAT: {spec.name} ({spec.label_th}). Target spoken length "
        f"{spec.min_seconds}-{spec.max_seconds} seconds; "
        f"{spec.min_blocks}-{spec.max_blocks} script blocks. "
    )
    if spec.name == "short":
        return base + (
            "This is a YouTube Short (vertical). The FIRST sentence must be a "
            "concrete image or situation within 2 seconds -- no greeting, no "
            "channel intro. Keep the whole script under "
            f"{spec.max_chars} Thai characters. The final line should be able "
            "to loop back into the first line, or stay as an image -- no call "
            "to action. Still include all four phases."
        )
    if spec.name == "long":
        return base + (
            "This is a long-form episode told as continuous scenes. Give EVERY "
            "block a short Thai chapter_title (blocks that belong to the same "
            "scene share the same chapter_title). Start with a cold open "
            "(phase hook), then scenes (exploration), then one or two blocks "
            "that change how the situation is SEEN (shift), then an outro that "
            "returns to the motif. Each scene is one place and one time."
        )
    return base + "Standard single episode."


_JSON_INSTRUCTIONS = """\
Respond with ONLY a single JSON object (no markdown fences, no commentary) \
matching exactly this structure:

{{
  "topic_id": "{topic_id}",
  "title": "<short Thai title>",
  "summary": "<1-2 Thai sentences for the video description: the situation, no promises>",
  "metadata": {{
    "mood": "<short mood description>",
    "estimated_duration_seconds": <int, within the target range>,
    "format": "{format_name}",
    "motif": "<the recurring object/sound>"
  }},
  "characters": [
    {{"name": "<invented name>", "role": "<role>", "age_range": "<e.g. 20s>", "outfit": "<one fixed outfit>", "signature_item": "<one item>", "palette": ["<2-3 colors>"], "want": "<what they want, ordinary and specific>", "fear": "<what they fear losing>", "stakes": "<what happens if they fail, non-violent>"}}
  ],
  "facts": [
    {{"claim": "<real-world fact used>", "source_hint": "<type of source>", "confidence": "high|medium|low"}}
  ],
  "script_blocks": [
    {{
      "sequence": 1,
      "phase": "hook",
      "chapter_title": "<short Thai chapter title>",
      "time_label": "<in-story time such as 23:47, or null>",
      "visual_cue": "<what the viewer sees, one sentence>",
      "setting": "<one of the allowed settings>",
      "mood": {{"light": "dim", "weather": "clear", "color": "cool", "voice": "calm", "sounds": ["room_tone"], "tension": 2}},
      "text": "<Thai text>",
      "pause_after_ms": <int>
    }},
    {{"sequence": 2, "phase": "exploration", "chapter_title": "...", "time_label": null, "visual_cue": "...", "mood": {{...}}, "text": "<Thai text>", "pause_after_ms": <int>}},
    {{"sequence": 3, "phase": "shift", "chapter_title": "...", "time_label": null, "visual_cue": "...", "mood": {{...}}, "text": "<Thai text>", "pause_after_ms": <int>}},
    {{"sequence": 4, "phase": "outro", "chapter_title": "...", "time_label": null, "visual_cue": "...", "mood": {{...}}, "text": "<Thai text>", "pause_after_ms": <int>}}
  ]
}}

The four phases (hook, exploration, shift, outro) must each appear at least \
once, in that order, matching AI_DESIGN.md's 4-phase script structure. You \
may split a phase into more than one block, but never skip a phase. \
Pauses: ~300-600 ms between sentences, 1000-1800 ms between thoughts, \
2000-3500 ms at the end of a chapter.\
"""


def build_script_prompt(
    topic_id: str,
    topic_text: str,
    theme: str | None = None,
    episode_format: str | None = None,
) -> str:
    spec = get_format(episode_format)
    theme_line = f"Broad theme: {theme}\n" if theme else ""
    return (
        f"{_CONTENT_CONSTRAINTS}\n\n"
        f"{_STYLE_RULES}\n\n"
        f"{_format_rules(spec)}\n\n"
        f"{theme_line}"
        f"Specific situation to reflect on: {topic_text}\n\n"
        f"Write a Thai life-reflection script about this situation, "
        f"following the 4-phase structure (hook, exploration, shift, outro).\n\n"
        f"{_JSON_INSTRUCTIONS.format(topic_id=topic_id, format_name=spec.name)}"
    )
