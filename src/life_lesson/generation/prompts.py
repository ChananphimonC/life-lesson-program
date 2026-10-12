"""Script-generation prompt template.

The full Critic system (AI_DESIGN.md §4) is a v0.3 feature and is NOT
implemented here. But per the v0.1 implementation brief, the core content
constraints from PRODUCT.md §3.2 must still be embedded directly in the
generation prompt itself -- this is a best-effort constraint at generation
time, not a substitute for the Critic's later verification pass.
"""

from __future__ import annotations

SCRIPT_PROMPT_NAME = "script_generation"
SCRIPT_PROMPT_STAGE = "script"
SCRIPT_PROMPT_VERSION = "script-v0.1.0"

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

_JSON_INSTRUCTIONS = """\
Respond with ONLY a single JSON object (no markdown fences, no commentary) \
matching exactly this structure:

{{
  "topic_id": "{topic_id}",
  "title": "<short Thai title>",
  "metadata": {{
    "mood": "<short mood description>",
    "estimated_duration_seconds": <int, target 180-300>
  }},
  "script_blocks": [
    {{
      "sequence": 1,
      "phase": "hook",
      "text": "<Thai text>",
      "pause_after_ms": <int, e.g. 1000-2500>
    }},
    {{
      "sequence": 2,
      "phase": "exploration",
      "text": "<Thai text>",
      "pause_after_ms": <int>
    }},
    {{
      "sequence": 3,
      "phase": "shift",
      "text": "<Thai text>",
      "pause_after_ms": <int>
    }},
    {{
      "sequence": 4,
      "phase": "outro",
      "text": "<Thai text>",
      "pause_after_ms": <int>
    }}
  ]
}}

The four phases (hook, exploration, shift, outro) must each appear at least \
once, in that order, matching AI_DESIGN.md's 4-phase script structure. You \
may split a phase into more than one block if needed (e.g. two "exploration" \
blocks back to back), but never skip a phase.\
"""


def build_script_prompt(topic_id: str, topic_text: str, theme: str | None = None) -> str:
    theme_line = f"Broad theme: {theme}\n" if theme else ""
    return (
        f"{_CONTENT_CONSTRAINTS}\n\n"
        f"{theme_line}"
        f"Specific situation to reflect on: {topic_text}\n\n"
        f"Write a 3-5 minute Thai life-reflection script about this situation, "
        f"following the 4-phase structure (hook, exploration, shift, outro).\n\n"
        f"{_JSON_INSTRUCTIONS.format(topic_id=topic_id)}"
    )
