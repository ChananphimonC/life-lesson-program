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

Choose a format with `--format`:

```bash
python -m life_lesson.cli "..." --format short      # YouTube Short, 9:16, <=55s
python -m life_lesson.cli "..." --format standard   # 3-5 min (default)
python -m life_lesson.cli "..." --format long       # 15-40 min, chaptered story
```

Besides the MP4, each run writes a publish bundle to
`output/publish/<episode_id>/` (`title.txt`, `description.txt` with chapters /
real facts / credits, `thumbnail.json`, `review_checklist.md`). Channel craft
rules live in [`docs/STYLE_GUIDE.md`](docs/STYLE_GUIDE.md).

Every episode also gets: a sensitive-topic screen, a 7-category Critic with up to
3 rewrites (otherwise state `FAILED_REVIEW` for a human), mood-directed narration
(voice delivery + pacing), per-chapter scenes (colour grade, rain/storm/fog, chapter
cards), a synthesised ambient sound bed, -16 LUFS mastering, and a thumbnail PNG.
Use `--no-critic` only for debugging.

Series and story briefs: `--series reflection|knowledge|story` and `--brief FILE` (see
[`docs/SCRIPT_DOCTOR.md`](docs/SCRIPT_DOCTOR.md) and `stories/*/BRIEF.md`). Every script also goes
through the suspense linter + punch-up rewrite (`--no-punchup` to skip).

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


## Library: manage finished clips

```bash
python -m life_lesson.library list                       # episodes + Shorts
python -m life_lesson.library show <id>                  # ids can be a short prefix
python -m life_lesson.library export <id> [--to DIR]     # copy the MP4 for upload/download
python -m life_lesson.library thumbnail <id> --title "..." --tag "23:47" --frame-at 12
python -m life_lesson.library description <id>           # rebuild title + description
python -m life_lesson.library short <id> --full-url URL  # 30-55 s Short from the real episode
python -m life_lesson.library playlist create "ซีรีส์" ; playlist add "ซีรีส์" <id>...
python -m life_lesson.library delete <id> --yes          # files only inside OUTPUT_DIR
```

Shorts end with a card pointing to the channel (`CHANNEL_HANDLE`, default `@SakidJai_สะกิดใจ`).
Visuals are drawn offline by default (`VISUAL_MODE=illustrated`: no stock footage, no paid API);
`REFERENCE_SEARCH=1` optionally nudges colours from open-licence reference photos (Openverse).
See [`docs/GROWTH_PLAYBOOK.md`](docs/GROWTH_PLAYBOOK.md).
