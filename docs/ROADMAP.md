# Project Roadmap

## MVP v0.1: Core Pipeline + Persistence
- **Goal:** Prove the text-to-video programmatic flow with real state tracking from day one.
- **Features:**
  - Stand up SQLite (episodes, topics, scripts, critic_attempts, prompt_versions) — no Postgres.
  - Hardcoded/CLI topic input, orchestrator writes state transitions to SQLite.
  - Call Gemini API for script generation, logging prompt version per attempt.
  - Call one TTS provider (provisional choice, pending the benchmark below) for audio.
  - FFmpeg to stitch audio over 1 random background video, 16:9.
  - Output raw MP4.

## MVP v0.2: TTS Benchmark (moved earlier)
- **Goal:** Choose a TTS approach based on evidence before building further provider-specific behavior around it.
- **Features:**
  - Systematically test Gemini TTS vs. Google Cloud TTS vs. open-source Thai TTS for: Thai pronunciation accuracy, natural pause/pacing support, voice quality/naturalness, cost at daily-episode volume.
  - Decide pause-marker handling per provider (native support vs. post-processing silence insertion fallback).
  - Keep the resulting integration as a thin wrapper function, not a heavy abstraction layer.
  - Re-confirm or switch the v0.1 provisional TTS choice based on results.

## MVP v0.3: The Critic & Sensitive-Topic Safeguards
- **Goal:** Enforce the full Content Philosophy, not just part of it.
- **Features:**
  - Implement the Critic prompt covering all seven prohibited categories (religious/Buddhist teaching, quotes/attributed statements, derivative motivational content, therapy/diagnosis/clinical claims, prescriptive advice, generic clichés, manipulative/preachy language).
  - Implement the bounded rewrite loop: max 3 attempts, then `FAILED_REVIEW` state requiring human handling.
  - Implement the sensitive-topic pre-filter at topic generation (self-harm, suicide, severe mental-health crisis, abuse, medical/clinical claims) plus the corresponding Critic category as a second check.
  - Enforce JSON output parsing, including `phase` and `prompt_version` fields.

## MVP v0.4: Accessibility & Subtitles
- **Goal:** Add captions without introducing transcription drift.
- **Features:**
  - Implement forced alignment of the known script text against TTS audio to produce `.srt`/`.vtt`.
  - Implement Whisper/faster-whisper as a fallback path only, for providers/outputs where alignment isn't available.
  - FFmpeg burns subtitles into the video.

## MVP v0.5: Human-in-the-Loop Dashboard
- **Goal:** Usability for the single human reviewer.
- **Features:**
  - Streamlit app (single-user) to replace CLI.
  - View topic, script, Critic results (per-category pass/fail) side by side.
  - Approve/regenerate buttons; explicit handling view for `FAILED_REVIEW` episodes.
  - Play audio preview before rendering video.

## Version 1.0: Production Ready
- **Goal:** Full scale, once MVP content quality and pipeline reliability are proven.
- **Features:**
  - Automated YouTube API integration (Draft upload & Schedule) — replaces manual upload.
  - Introduce PostgreSQL + `pgvector` for cross-episode semantic similarity search (own-catalog repetition, AI_DESIGN.md §5.A), alongside or migrating from SQLite depending on operational needs at that point.
  - Expansion to 10-15 minute episodes based on viewer retention data.
  - Revisit Shorts/vertical format if warranted by audience data.

## Explicitly Deferred (not MVP, not yet scheduled)
- External plagiarism/corpus-matching system against religious texts, books, or the wider internet (AI_DESIGN.md §5.B remains Critic-level only).
- Multi-reviewer workflows / dashboard access control.
- Microservices or distributed infrastructure of any kind.
