# Experiment: cartoon storyboard visuals

Zero-cost prototype of the cartoon visual pipeline. It reuses an episode's
**already-generated narration WAV** and validated script from SQLite and
replaces the stock background with illustrated scenes that follow what the
narration is saying. No API calls; only Pillow and ffmpeg.

```bash
cd experiments/cartoon_storyboard
python render.py --preview            # keyframes + contact sheet in output/_work/preview/
python render.py                      # latest storyboarded episode -> output/videos/EPxx - <title>/
python render.py --episode <id>       # a specific episode
python preview.py                     # library manager: watch, save, rename, delete (or open_preview.bat)
```

Output layout:

```
output/videos/EP01 - <title>/EP01 - <title>.mp4
                            /info.json        episode id, topic, theme, duration, render time
                            /cover.jpg        YouTube cover, 1920x1080, < 2 MB
                            /cover.json       3 AI concepts, the chosen one, the cover text
output/_work/                                 ffmpeg logs, timeline.json, keyframe previews
```

- `library.py` owns that layout (numbering, naming, rename, delete);
  `preview.py` serves it at http://127.0.0.1:52101/ (local only).
- `covers.py` makes each episode's cover: `render.py` creates it automatically
  after a video finishes (1 Gemini text call; a plain local cover if AI is
  unavailable). In the library: pick one of 3 styles, edit the cover text,
  ask AI to rewrite it ("shorter", "more curious"...), regenerate, download.
  `python covers.py` fills in covers for episodes that lack one.
- `timing.py` finds block boundaries (the pipeline's inserted exact-zero
  pauses) and phrase pauses in the WAV, then aligns phrases to the text so
  scene cuts and on-screen events land when their phrase is spoken.
- `storyboard.py` holds one hand-authored storyboard per episode: scenes per
  script block, each starting at an anchor phrase, plus timed events.
- `character.py` is a skeletal character drawn in the sheets' style (warm
  brown outline, tapered limbs, sweater details, 3/4 face, soft shading), so
  the same design is reused in every pose. `scenes.py` has the EP01 scenes,
  `scenes_epNN.py` the scenes of each later episode.
- A new episode: `python make_episode.py new "<topic>" --theme "<theme>"`
  (script + narration with a per-block TTS cache; if the free daily quota
  runs out, `python make_episode.py voice <id> --render` resumes later), add
  its storyboard and scenes, then `python render.py --episode <id>`.
- `extract_assets.py` / `scenes_stickers.py` are the earlier sticker-sheet
  style (`--style stickers`), kept for reference.

Not part of the main pipeline yet; `src/` is untouched.

## Thumbnail Studio

```bash
python thumbnail_app.py               # http://127.0.0.1:52102/ (or open_thumbnail_studio.bat)
```

Pick an episode (or type a title/summary) → one Gemini **text** call analyzes
the story and proposes 3 genuinely different thumbnail concepts → render →
edit the Thai text/crop live → export a PNG/JPEG sized for YouTube. No
image-generation API: `thumbnail_studio.py` composes thumbnails from the same
procedural renderer that draws the episodes (`character.py`, `art.py`), so
every thumbnail automatically matches the channel's actual art direction, and
Thai text is drawn locally (never by a model), so it can't come out garbled.

- `thumbnail_studio.py`: the 4 composition templates (`portrait`,
  `wide_symbolic`, `contrast_split`, `object_hero`), the analysis prompt +
  pydantic schema, crop/focal-point, the editable text overlay, JPEG export
  that iterates quality/size to stay under YouTube's 2 MB limit, and a
  `output/thumbnails/<key>/studio.json` store per project (concepts, crop/text
  settings, exported files, and manually-recorded CTR/impressions/watch-time
  outcomes -- never fabricated or inferred, only what you typed in).
- `thumbnail_app.py`: the local web UI on top of it, same stdlib-only style
  as `preview.py`.
