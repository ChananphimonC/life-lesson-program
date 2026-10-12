# System Architecture

## MVP Simplicity Principle
This project is primarily an AI content-generation system, not an infrastructure showcase. The architecture below is intentionally a single Python backend + single SQLite database + a single-user Streamlit dashboard. No microservices, message queues, or distributed infrastructure are introduced until a specific, demonstrated need requires them (e.g., cross-episode semantic search motivating PostgreSQL/pgvector — see ROADMAP.md). Provider abstractions (LLM, TTS) are kept as thin wrapper functions, not plugin frameworks, until the TTS benchmark shows what actually needs to vary.

## High-Level Pipeline

                    ┌───────────────┐
                    │   Dashboard   │
                    │  (Streamlit,  │
                    │ single-user)  │
                    └───────┬───────┘
                            │ (Human triggers & approves)
                            ▼
                 ┌────────────────────┐
                 │ Episode Orchestrator│◄──────────────┐
                 │      (Python)      │                │
                 └─────────┬──────────┘                │
                            │                           │
                            ▼                           │
                     SQLite (episodes, topics,          │
                     scripts, critic_attempts,           │
                     prompt_versions)                    │
                            │                           │
          ┌─────────────────┼─────────────────┐          │
          ▼                 ▼                 ▼          │
     Topic Engine     Sensitive-Topic     Script Engine   │
          │             Pre-Filter             │          │
          │           (reject & retry)          │          │
          └─────────────────┼─────────────────┘          │
                            ▼                              │
                 Google Gemini API (topic/script)          │
                            │                              │
                            ▼                              │
                      QA Engine (Critic)                   │
                 checks all 7 prohibited                   │
                 categories (PRODUCT.md §3.2)               │
                            │                              │
                 ┌──────────┴──────────┐                   │
                 ▼                     ▼                   │
             PASS                  FAIL ─────► attempt < 3 ┘
                 │                     │        (rewrite offending
                 │                     │         section, re-check)
                 │                     ▼
                 │              attempt == 3
                 │                     │
                 │                     ▼
                 │           FAILED_REVIEW state
                 │           (human handles manually
                 │            via dashboard; pipeline
                 │            stops for this episode)
                 ▼
        [Approved Script JSON]
                 │
                 ▼
     TTS Provider (evaluated via benchmark —
     see ROADMAP.md; provider chosen based on
     Thai pronunciation, pacing, naturalness, cost)
                 │
                 ▼
            Audio (.wav)
                 │
      ┌──────────┴──────────┐
      ▼                     ▼
Forced Alignment      Background Video (Stock,
(script text ↔          pre-curated, 16:9)
 audio; primary)              │
      │                       │
      ▼ (fallback only if     │
   alignment unavailable)      │
Whisper / faster-whisper       │
 (subtitle fallback)            │
      │                       │
      └───────────┬───────────┘
                   ▼
      FFmpeg (Python `subprocess` / `moviepy`)
                   │
                   ▼
          Final MP4 (16:9 long-form)
                   │
                   ▼
    [Human Final Review] (single reviewer,
      via Streamlit dashboard)
                   │
                   ▼
            Manual Upload (YouTube)

## Notes on Deferred Components
- **PostgreSQL + pgvector:** not present in MVP architecture. Introduced only when cross-episode semantic similarity search (AI_DESIGN.md §5.A) becomes necessary — at that point it runs alongside, not instead of, SQLite (SQLite continues to hold operational/episode state; pgvector holds embeddings for similarity search), or SQLite is migrated wholesale if operational complexity justifies it. That decision is deferred until the need is real.
- **YouTube API integration:** not present in MVP architecture; manual upload is the pipeline's terminal step.
- **External plagiarism/corpus-matching system:** not present in MVP or near-term architecture; originality-vs-external-material is handled at the generation/Critic layer (AI_DESIGN.md §5.B), not as a separate infrastructure component.
- **Provider abstraction layer:** not a distinct architectural component in MVP — LLM and TTS access are thin function-level wrappers inside the Episode Orchestrator, not a separate service or plugin system.
