# System Requirements

## 1. Functional Requirements
- **Workflow UI:** Provide a Streamlit dashboard for a single human reviewer to interact with the pipeline (view topics, scripts, Critic results, audio preview, approve/reject, handle `FAILED_REVIEW` episodes). Multi-reviewer workflows are out of scope for MVP.
- **Orchestration:** Python backend to manage the state of each episode through the following states:
  `DRAFT -> TOPIC -> SCRIPT -> CRITIC_REVIEW -> (loop up to 3x) -> AUDIO -> SUBTITLES -> VIDEO -> HUMAN_REVIEW -> PUBLISHED`, with a `FAILED_REVIEW` terminal state reachable from `CRITIC_REVIEW` if the script still fails after 3 rewrite attempts.
- **Persistence:** SQLite database, used from v0.1, storing:
  - episode state and history (state transitions with timestamps),
  - topics (including rejected/sensitive-filtered topics, for traceability),
  - scripts (each generation attempt, not just the final approved one),
  - Critic results per attempt (per-category pass/fail, rewrite diffs),
  - prompt versions used per generation (topic prompt, script prompt, Critic prompt).
  PostgreSQL + `pgvector` is intentionally deferred — introduced only when cross-episode semantic similarity search becomes necessary (see ROADMAP.md), not required for MVP state tracking.
- **Generation:** Connect to Google Gemini API for Topic, Script, and Critic generation. The Critic prompt must check all seven prohibited categories defined in PRODUCT.md §3.2 / AI_DESIGN.md §4.
- **Sensitive-topic filtering:** Screen generated topics before scripting, and re-check during the Critic pass, for self-harm, suicide, severe mental-health crisis, abuse, and medical/clinical-claim content (see PRODUCT.md §5, AI_DESIGN.md §6). Flagged topics are rejected and regenerated rather than "softened."
- **Audio Processing:** Connect to a TTS API and interpret pause markers (or fall back to post-processing silence insertion where a provider doesn't support markers natively) to generate paced audio.
- **Subtitle Generation:** Generate `.srt`/`.vtt` primarily via forced alignment of the known script text against the TTS audio. Fall back to Whisper/faster-whisper transcription only when forced alignment is unavailable for a given provider/output.
- **Video Assembly:** Use FFmpeg to stitch a static/looping background video, the TTS audio, and subtitle files into an MP4, targeting **16:9 long-form** (YouTube standard). Shorts/vertical format is explicitly out of scope for MVP.

## 2. Non-Functional Requirements
- **Modularity (right-sized):** LLM Provider and TTS Provider access should go through a thin wrapper/function boundary so a provider swap doesn't require touching core pipeline logic — but do **not** build a heavy plugin/interface abstraction layer before the TTS benchmark (§ below, AI_DESIGN.md §8) has established what actually varies between providers. Abstraction should follow evidence from the benchmark, not precede it.
- **Reproducibility:** Every generation attempt (topic, script, Critic pass) must be traceable to the exact prompt version and inputs used, via the SQLite `generation_attempts`-style records described in §1. This supports debugging content-quality regressions and comparing prompt revisions.
- **Reliability:** The Critic rewrite loop must be bounded (max 3 attempts) and must never retry indefinitely; failure routes to `FAILED_REVIEW` for human handling, not silent failure or auto-publish.
- **Performance:** Video rendering must happen in the background or show a clear progress state, as FFmpeg operations take time.
- **Cost:** Maximize free tiers (Gemini AI Studio API) and open-source tools (FFmpeg, forced-alignment tooling, local Whisper as fallback).
- **Simplicity:** No microservices, message queues, or distributed infrastructure for MVP — a single Python process/backend driven by the Streamlit dashboard is sufficient at 1 episode/day cadence (see ARCHITECTURE.md §"MVP Simplicity Principle").

## 3. MVP Scope Constraints (v0.1 - v0.5)
- **Duration:** 3-5 minutes per video.
- **Cadence:** 1 episode per day.
- **Format:** 16:9 long-form video for YouTube. No Shorts optimization.
- **Visuals:** Pre-curated folder of stock looping videos (no AI video generation).
- **Persistence:** SQLite from v0.1 (see §1). No PostgreSQL/pgvector in MVP scope.
- **Originality scope:** Critic-level rejection of quotes/attributed/derivative content is in scope for MVP (AI_DESIGN.md §5.B). Cross-episode embedding similarity search (5.A) and any external corpus-matching system are explicitly **not** in MVP scope.
- **Reviewer:** Single human reviewer (project owner); Streamlit remains single-user.
- **Publishing:** System exports MP4. Human manually uploads to YouTube. YouTube API integration remains a future milestone.
