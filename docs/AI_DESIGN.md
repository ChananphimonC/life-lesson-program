# AI Design & Prompting Strategy

## 1. Topic Generation
The system uses an LLM to generate unique angles on common themes.
- **Input:** Broad theme (e.g., "The fear of falling behind").
- **Process:** Check the `topics` table in SQLite (see REQUIREMENTS.md §1, ARCHITECTURE.md) for past angles. Prompt the LLM to generate 3 new, highly specific situations (e.g., "Seeing friends buy houses while you are still renting and figuring out your career").
- **Sensitive-topic pre-filter:** Before a generated topic proceeds to scripting, it is screened against the Sensitive Topics list (§6). Topics that touch self-harm, suicide, severe mental-health crisis, abuse, or require medical/clinical framing are rejected at this stage and a new topic is requested — this is cheaper and safer than trying to write a "safe" script around an unsafe topic.

## 2. Script Structure
The prompt forces the LLM to structure the 3-5 minute script into 4 distinct phases:
1. **The Hook (Observation):** Start with a mundane, relatable situation. (e.g., "เคยไหม... เวลานั่งเลื่อนฟีดดูชีวิตคนอื่นตอนดึกๆ แล้วรู้สึกว่าตัวเองกำลังย่ำอยู่กับที่")
2. **The Exploration (Deep Dive):** Validate the feeling. Why does it hurt? How does it manifest? Do not offer a solution yet.
3. **The Shift (Perspective) — highest risk of becoming advice:** Introduce a gentle shift in *how the situation is seen*, not a fix for it.
   - Allowed: naming a different angle, noticing a contradiction, sitting with an unresolved contrast, widening the frame of the observation.
   - Not allowed: telling the listener to do/try/adopt anything; implying that seeing it this way will make the feeling go away; phrasing that reads as a technique or a step; any sentence that could be reworded as "so you should..." without losing meaning.
   - Litmus test written into the prompt: *if this sentence were given as a reply to a friend, would it feel like comfort or like a suggestion? It must feel like comfort.*
   - The Shift must not promise resolution. If the exploration in phase 2 raised a tension, phase 3 is allowed to look at that tension from another side — it is not required (and not allowed) to resolve it.
4. **The Outro (Open Reflection):** Leave a lingering thought. Fade out. (e.g., "บางที... เราอาจไม่จำเป็นต้องหาคำตอบให้ทุกเรื่องในคืนนี้ก็ได้") No summary, no lesson, no call to action.

## 3. Writing Style & Pacing
- Language: Natural, conversational Thai (ภาษาพูด ไม่ใช่ภาษาเขียนเรียงความ).
- Pacing: The LLM must output pacing markers like `[PAUSE_SHORT]`, `[PAUSE_LONG]` between thoughts. Marker support is validated per TTS provider during the TTS benchmark (see ROADMAP.md) before the pipeline depends on it; if a chosen provider cannot honor pause markers, pacing falls back to post-processing silence insertion at the same marker positions during audio assembly.

## 4. The Critic (Anti-Advice / Anti-Derivative System)
Before a script reaches the human reviewer, the system runs a Critic pass covering **all seven** prohibited categories from PRODUCT.md §3.2 — not just advice-language and clichés:

1. **Religious/Buddhist teaching** — does the script teach, reference, or paraphrase religious doctrine?
2. **Quotes or attributed statements** — does it quote or closely paraphrase Buddha, a named or recognizable public figure, or a book, even without attribution?
3. **Copied or derivative motivational content** — does any line closely resemble known motivational-content phrasing rather than an original observation?
4. **Therapy/diagnosis/clinical claims** — does it diagnose, use clinical terminology, or imply professional mental-health guidance?
5. **Prescriptive life advice** — does it contain "ควร", "ต้อง", "จง", "อย่า", or other constructions telling the listener what to do?
6. **Generic motivational clichés** — does it end on or contain a stock inspirational line?
7. **Manipulative or preachy language** — guilt-tripping, urgency pressure, or a tone that pushes the listener toward a conclusion rather than sitting with them.

**Process:**
- The Critic is run as a *separate prompt/pass from generation*, using the full script (not just the flagged phase) as context, so phase 4's checks aren't blind to what phases 1–3 already established.
- *Action if any category is flagged:* rewrite only the offending section to be purely observational, then re-run the full Critic pass against the revised script (a local fix can introduce a new violation elsewhere, e.g. an abrupt tone shift).
- **Loop limit:** maximum **3** rewrite attempts per episode. If the script still fails Critic review after 3 attempts, the episode's state is set to `FAILED_REVIEW` (see REQUIREMENTS.md §1 state list) and generation stops — it is not published, discarded, or retried automatically. `FAILED_REVIEW` episodes require human review (edit manually, discard, or restart topic generation) via the dashboard.
- Every Critic pass (pass/fail per category, rewrite diff, attempt number) is logged against the episode's `generation_attempts` record in SQLite for reproducibility and later prompt tuning.

## 5. Originality Checks

### 5.A Repetition against the project's own catalog
- Deferred until it's actually needed (see ROADMAP.md) — not required for early MVP milestones, since a small back-catalog and human review provide sufficient coverage at low volume.
- When introduced: convert the approved script into text embeddings, store in PostgreSQL (`pgvector`), and calculate cosine similarity against past episodes when generating a new one. If similarity > 0.85 (threshold to be tuned against real episode data once available), force the LLM to take a different angle.
- This system answers "have we said this before," not "does this resemble someone else's copyrighted material" — that is a separate concern, below.

### 5.B Resemblance to external/copyrighted/attributed material
- MVP does **not** build a large external plagiarism-detection system (no corpus-matching against religious texts, published books, or the wider internet).
- Instead, this is handled at the generation and Critic stages: the topic/script prompts explicitly instruct the LLM never to produce quotations or attributed statements, and Critic categories 1–3 (§4) exist specifically to catch recognizable copied phrasing, paraphrased religious teaching, or attributed statements before an episode reaches the human reviewer.
- This is a deliberate scope boundary: the Critic is a first-pass filter, not a guarantee of zero resemblance. The human reviewer remains the final check for this category, same as for tone.

## 6. Sensitive Topics Safeguard
Applies at two points in the pipeline:
- **Topic generation (§1):** candidate topics are screened before scripting begins; topics involving self-harm, suicide, severe mental-health crisis, abuse, or requiring medical/clinical claims are rejected and regenerated.
- **Critic pass (§4, category 4):** acts as a second check in case a sensitive theme emerges during scripting even though the topic itself looked safe (e.g., an example or metaphor drifts into crisis territory).
- The system must never generate self-harm/suicide method detail, never imply it is providing professional or clinical help, and never diagnose. There is no "safe way" to generate this content within the product's scope — the correct behavior is rejection and regeneration with a different topic, not a softened version of the sensitive topic.

## 7. Subtitle Generation Approach
- **Primary approach:** forced alignment of the known, already-approved script text against the generated TTS audio, to produce word/phrase-level timestamps for `.srt`/`.vtt` output. Because the exact script text is already known (it's the source of the TTS input), forced alignment avoids the transcription-drift risk of re-transcribing the audio from scratch.
- **Fallback:** if forced alignment is unavailable or fails for a given TTS provider/output (e.g., no compatible alignment tool for the audio format), fall back to Whisper/faster-whisper transcription for that episode. This is a fallback path, not the default.

## 8. TTS Provider Evaluation
Before any provider-specific behavior (pause-marker handling, voice selection) is implemented in the pipeline, providers are benchmarked against:
- Thai pronunciation accuracy (including tone correctness).
- Natural pause/pacing support (native marker support vs. requiring post-processing silence insertion).
- Voice quality/naturalness for a calm, intimate conversational register.
- Cost at expected daily-episode volume.

This benchmark is moved earlier in the roadmap (see ROADMAP.md) rather than left until after provider-specific code is written, so the pipeline isn't built around a provider that turns out to be unsuitable. See REQUIREMENTS.md §2 for the corresponding "keep it lightweight" implementation note — this is an evaluation exercise, not a trigger to build a heavy provider-abstraction layer up front.

## 9. Expected JSON Output Structure
The LLM must output the final script in this JSON structure for programmatic processing:
```json
{
  "topic_id": "req-123",
  "title": "ความเร็วที่แตกต่างกัน",
  "metadata": {
    "mood": "calm, reflective",
    "estimated_duration_seconds": 240,
    "prompt_version": "script-v1.2",
    "critic_attempt": 1
  },
  "script_blocks": [
    {
      "sequence": 1,
      "phase": "hook",
      "text": "บางครั้งเราก็เผลอมองนาฬิกาของคนอื่น...",
      "pause_after_ms": 1500
    },
    {
      "sequence": 2,
      "phase": "exploration",
      "text": "แล้วกลับมากดดันตัวเองว่า ทำไมเราถึงยังไปไม่ถึงไหน",
      "pause_after_ms": 2000
    }
  ]
}
```
`phase` (hook / exploration / shift / outro) and `prompt_version` are added so the Critic, forced-alignment step, and reproducibility logging (SQLite `generation_attempts`) can all reference which phase and which prompt version produced a given block.
