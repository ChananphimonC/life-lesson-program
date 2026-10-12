# Life Lesson Program

AI-generated Thai "life reflection" episodes. See [`docs/`](docs/) for the
full product, AI-design, requirements, architecture, and roadmap
specifications.

This is **MVP v0.1**: a CLI-driven pipeline that turns one topic into a raw
16:9 MP4 (script generation -> validation -> TTS -> FFmpeg assembly). No
Streamlit dashboard, Critic, subtitles, or PostgreSQL yet -- see
[`docs/ROADMAP.md`](docs/ROADMAP.md) for what's next.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -e ".[dev]"
copy .env.example .env        # then fill in GEMINI_API_KEY
```

You also need:
- **FFmpeg** installed and on `PATH` (or set `FFMPEG_BINARY` in `.env` to its
  full path).
- At least one 16:9 background video file in `assets/backgrounds/` (see the
  README there).

## Running the pipeline

```bash
python -m life_lesson.cli "Seeing friends buy houses while you are still renting"
```

This creates a topic + episode row in the SQLite database (`data/life_lesson.db`
by default), generates and validates a script via Gemini, synthesizes audio
per script block via Gemini TTS, concatenates it with pause gaps, and
assembles a raw MP4 in `output/video/`.

## Tests

```bash
pytest
```

Tests cover schema validation, the SQLite repository layer, prompt content,
and pipeline orchestration/state transitions using fakes for the Gemini and
TTS calls (no network access or API key required to run the test suite).
