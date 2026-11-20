"""Scene-based video assembly (STYLE_GUIDE.md §11).

Each chapter becomes one scene: its own background clip (rotated so the same
clip never plays twice in a row), a consistent colour grade + vignette, a
short chapter title card, and dip-to-black fades between scenes. Scenes are
rendered separately, concatenated, then muxed with the narration.

Backgrounds are still the pre-curated stock folder; `visual_cue` is recorded
on each scene (and in the shot list) so a future image/video generator can
replace the stock clips scene-by-scene without changing this module's shape.
"""

from __future__ import annotations

import json
import logging
import subprocess
import tempfile
from dataclasses import dataclass, asdict
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from life_lesson.errors import VideoAssemblyError
from life_lesson.generation.atmosphere import BlockMood, grade_filter, rain_chain, rain_opacity
from life_lesson.generation.schema import ScriptOutput
from life_lesson.video.illustrator import SETTINGS, character_colors, illustrate_scene
from life_lesson.video.scene_kb import is_worker, props_from_cue, retrieve_recipe
from life_lesson.publish.fonts import find_thai_font

logger = logging.getLogger(__name__)

FADE_S = 0.5
CARD_SECONDS = 4.0
MIN_SCENE_MS = 3000
VIDEO_EXTENSIONS = {".mp4", ".mov", ".mkv", ".webm"}


@dataclass(frozen=True)
class Scene:
    index: int
    start_ms: int
    end_ms: int
    title: str | None
    time_label: str | None
    visual_cue: str | None
    mood: BlockMood | None = None
    setting: str = "room"
    looks: tuple = ()  # character colour dicts for the illustrator
    character_names: tuple = ()
    recipe_id: str = ""
    ref_palette: tuple = ()
    props: tuple = ()
    speaker: str | None = None

    @property
    def duration_s(self) -> float:
        return (self.end_ms - self.start_ms) / 1000


def plan_scenes(script: ScriptOutput, block_starts_ms: list[int], total_ms: int) -> list[Scene]:
    """One scene per run of blocks sharing a chapter_title (one scene total
    when no titles exist). Scenes shorter than 3s merge into the previous one,
    and the scenes tile [0, total_ms] with no gaps."""
    if len(block_starts_ms) != len(script.script_blocks):
        raise ValueError("block_starts_ms must have one entry per script block")

    groups: list[dict] = []
    for block, start in zip(script.script_blocks, block_starts_ms):
        title = (block.chapter_title or "").strip() or None
        same_title = title is None or title == groups[-1]["title"] if groups else False
        # a change of place inside one chapter is a new scene (the dark alley is not the stall)
        same_place = not (block.setting and groups and groups[-1]["place"] and block.setting != groups[-1]["place"])
        same_speaker = not groups or block.speaker == groups[-1]["speaker"]   # a speaking line gets its own close-up scene
        if groups and same_title and same_place and same_speaker:
            if block.setting and not groups[-1]["place"]:
                groups[-1]["place"] = block.setting
            continue
        groups.append(
            {"start": start, "title": title, "time_label": block.time_label, "place": block.setting,
             "cue": block.visual_cue, "moods": [], "cues": [], "settings": [], "speaker": block.speaker}
        )
    if not groups:
        return []
    groups[0]["start"] = 0
    # attach every block's mood to the scene it falls in; the scene is graded
    # by its most tense block (the moment the picture must carry).
    gi = 0
    for block, start in zip(script.script_blocks, block_starts_ms):
        while gi + 1 < len(groups) and start >= groups[gi + 1]["start"]:
            gi += 1
        if block.mood is not None:
            groups[gi]["moods"].append(block.mood)
        groups[gi]["cues"].append(block.visual_cue or "")
        if block.setting:
            groups[gi]["settings"].append(block.setting)

    merged: list[dict] = [groups[0]]
    for g in groups[1:]:
        if g["start"] - merged[-1]["start"] < MIN_SCENE_MS or total_ms - g["start"] < MIN_SCENE_MS:
            continue
        merged.append(g)

    scenes = []
    for i, g in enumerate(merged):
        end = merged[i + 1]["start"] if i + 1 < len(merged) else total_ms
        mood = max(g["moods"], key=lambda m: m.tension) if g["moods"] else None
        cue_text = " ".join(g["cues"])
        explicit = g["settings"][0] if g["settings"] else None
        recipe = retrieve_recipe(cue_text, explicit)
        setting = explicit if explicit in SETTINGS else recipe.setting
        present = [c for c in script.characters if c.name and c.name in cue_text] or script.characters[:1]
        scene_props = props_from_cue(cue_text)
        lamp = ("headlamp",) if "ไฟคาดหัว" in cue_text else ()
        looks = tuple(
            character_colors(
                c.outfit, c.palette, c.name,
                extra_items=(recipe.wardrobe if is_worker(recipe, c.role, c.name, c.outfit) else ())
                + (lamp if "ไฟคาดหัว" in f"{c.signature_item} {c.outfit}" else ())
                + (("seated",) if "นั่ง" in (c.role or "") else ()),
                sleeve=recipe.sleeve if is_worker(recipe, c.role, c.name, c.outfit) else None,
                hair=c.hair, gender=c.gender, age=c.age_range,
            )
            for c in present
        )
        scenes.append(Scene(i, g["start"], end, g["title"], g["time_label"], g["cue"], mood,
                            setting, looks, tuple(c.name for c in present), recipe.id, (), scene_props, g["speaker"]))
    return scenes


def write_shot_list(scenes: list[Scene], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for sc in scenes:
        row = asdict(sc)
        row["mood"] = sc.mood.model_dump() if sc.mood else None  # pydantic, not a dataclass
        row.pop("looks", None)  # drawing colours are derived data; names are kept
        rows.append(row)
    path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def list_backgrounds(background_dir: Path) -> list[Path]:
    if not background_dir.is_dir():
        raise VideoAssemblyError(f"Background video directory does not exist: {background_dir}")
    clips = sorted(p for p in background_dir.iterdir() if p.suffix.lower() in VIDEO_EXTENSIONS)
    if not clips:
        raise VideoAssemblyError(
            f"No background video files found in {background_dir} "
            f"(expected one of {sorted(VIDEO_EXTENSIONS)})"
        )
    return clips


def assign_backgrounds(scene_count: int, clips: list[Path], offset: int = 0) -> list[Path]:
    """Round-robin so consecutive scenes never share a clip when >1 clip exists."""
    return [clips[(offset + i) % len(clips)] for i in range(scene_count)]


def render_chapter_card(
    scene: Scene, size: tuple[int, int], out_path: Path, *, font_path: str | None = None
) -> Path | None:
    """Transparent lower-third PNG: time label (red tag) + chapter title."""
    if not scene.title and not scene.time_label:
        return None
    w, h = size
    u = min(w, h) / 720
    font_file = find_thai_font(font_path)
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    margin = int(56 * u)
    y = int(h * 0.56) if w >= h else int(h * 0.60)   # landscape: above the caption band
    if scene.time_label:
        f = ImageFont.truetype(str(font_file), int(30 * u))
        tw = d.textlength(scene.time_label, font=f)
        pad = int(12 * u)
        d.rounded_rectangle([margin, y, margin + tw + 2 * pad, y + int(46 * u)], radius=int(10 * u), fill=(214, 52, 41, 235))
        d.text((margin + pad, y + int(4 * u)), scene.time_label, font=f, fill=(255, 255, 255, 255))
        y += int(58 * u)
    if scene.title:
        f = ImageFont.truetype(str(font_file), int(54 * u))
        d.text((margin + 3, y + 3), scene.title, font=f, fill=(0, 0, 0, 200))
        d.text((margin, y), scene.title, font=f, fill=(255, 255, 255, 255))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path)
    return out_path


def _run(command: list[str], what: str) -> None:
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=False)
    except FileNotFoundError as exc:
        raise VideoAssemblyError(f"ffmpeg binary not found ('{command[0]}')") from exc
    if result.returncode != 0:
        raise VideoAssemblyError(f"ffmpeg failed while {what}: {result.stderr[-1500:]}")


ANIM_FPS = 6          # character animation steps per second (flat 2D "limited animation")
_BREATH = (0.0, 0.6, 1.0, 0.6, 0.0, -0.6, -1.0, -0.6)   # one breath cycle, 8 steps (~1.3 s)


def anim_schedule(scene: Scene, steps: int) -> list[tuple[int, bool, int]]:
    """Per-step (phase 0-7, blink, mouth). `phase` drives breathing, the cook's stir-fry and the walking cycle;
    the speaker's mouth works open / half / closed with it while the line is being said."""
    mouth = (1, 2, 0, 1, 1, 2, 0, 2)     # open, half, shut ... irregular, like speech
    out = []
    for i in range(steps):
        ph = i % 8
        blink = i % 24 == 21
        out.append((ph, blink, mouth[ph] if scene.speaker else 0))
    return out


def _animated_listing(frames: list[Path], steps: list[int], path: Path) -> Path:
    """ffmpeg concat list that plays frames[steps[i]] for 1/ANIM_FPS s each."""
    lines = []
    for k in steps:
        lines.append(f"file '{frames[k].as_posix()}'\nduration {1 / ANIM_FPS:.5f}\n")
    lines.append(f"file '{frames[steps[-1]].as_posix()}'\n")   # concat demuxer drops the last duration
    path.write_text("".join(lines), encoding="utf-8")
    return path


def _motion_filter(scene: Scene, width: int, height: int, focus: dict | None = None) -> str:
    """Slow camera push-in (stronger when tense) with a gentle sideways drift;
    a speaking line pushes in on the speaker's face instead (a real close-up)."""
    frames = max(2, int(scene.duration_s * 30))
    if focus and "x" in focus:
        fx, fy = focus["x"], focus["y"]
        return (
            f"zoompan=z='1.35+0.45*on/{frames}':"
            f"x='min(max(iw*{fx:.4f}-iw/zoom/2,0),iw-iw/zoom)':y='min(max(ih*{fy:.4f}-ih/zoom/2,0),ih-ih/zoom)':"
            f"d=1:s={width}x{height}:fps=30"
        )
    push = 0.20 if (scene.mood and scene.mood.tension >= 4) else 0.11
    return (
        f"zoompan=z='1.0+{push}*on/{frames}':"
        f"x='(iw-iw/zoom)/2+iw*0.018*sin(on/210)':y='(ih-ih/zoom)/2':"
        f"d=1:s={width}x{height}:fps=30"
    )


def _scene_command(
    ffmpeg: str, clip: Path, card: Path | None, scene: Scene, width: int, height: int, out: Path,
    focus: dict | None = None, captions: list[tuple[Path, float, float]] | None = None,
) -> list[str]:
    dur = scene.duration_s
    fade_out_at = max(0.0, dur - FADE_S)
    illustrated = clip.suffix.lower() in (".png", ".txt")
    if illustrated:
        # .txt = concat list of animation frames; each is stretched to 30 fps, then pushed in frame by frame
        cmd = [ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", str(clip)] if clip.suffix.lower() == ".txt" else [ffmpeg, "-y", "-i", str(clip)]
        first = f"[0:v]fps=30,{_motion_filter(scene, width, height, focus)},setsar=1,"
    else:
        cmd = [ffmpeg, "-y", "-stream_loop", "-1", "-i", str(clip)]
        first = "[0:v]"
    steps = [
        f"{first}scale={width}:{height}:force_original_aspect_ratio=increase,"
        f"crop={width}:{height},{grade_filter(scene.mood, illustrated)}[g0]"
    ]
    label, next_input = "g0", 1

    rain = rain_chain(width, height, scene.mood)
    if rain is not None:
        cmd += ["-f", "lavfi", "-i", rain]
        # Keep the blend in planar GBR and convert back explicitly: letting ffmpeg
        # negotiate blend -> yuv420p on its own picks a wrong colour conversion
        # (green collapses, red/blue spike) -- see test_rain_keeps_colours.
        steps.append(
            f"[{label}]format=gbrp[a];"
            f"[a][{next_input}:v]blend=all_mode=screen:all_opacity={rain_opacity(scene.mood)},format=gbrp[g1]"
        )
        label, next_input = "g1", next_input + 1

    if card is not None:
        cmd += ["-loop", "1", "-i", str(card)]
        steps.append(
            f"[{next_input}:v]format=rgba,fade=t=in:st=0.4:d=0.6:alpha=1,"
            f"fade=t=out:st={CARD_SECONDS - 0.6}:d=0.6:alpha=1[card];"
            f"[{label}][card]overlay=0:0:enable='lt(t,{CARD_SECONDS})':shortest=0[g2]"
        )
        label = "g2"

    for png, a_s, b_s in captions or []:   # one burned-in caption per phrase, shown only while it is spoken
        cmd += ["-loop", "1", "-i", str(png)]
        steps.append(
            f"[{next_input}:v]format=rgba[c{next_input}];"
            f"[{label}][c{next_input}]overlay=0:0:enable='between(t,{a_s:.3f},{b_s:.3f})':shortest=0[g{next_input + 10}]"
        )
        label, next_input = f"g{next_input + 10}", next_input + 1

    steps.append(
        f"[{label}]fade=t=in:st=0:d={FADE_S},fade=t=out:st={fade_out_at}:d={FADE_S},format=yuv420p[v]"
    )
    cmd += [
        "-filter_complex", ";".join(steps), "-map", "[v]", "-t", f"{dur:.3f}",
        "-an", "-r", "30", "-c:v", "libx264", "-preset", "veryfast", "-crf", "19",
        # sharp 1080p flat art needs a generous rate; the cap keeps long episodes uploadable
        "-maxrate", "9M", "-bufsize", "18M", "-tune", "animation", str(out),
    ]
    return cmd


def assemble_scene_video(
    *,
    ffmpeg_binary: str,
    scenes: list[Scene],
    background_dir: Path,
    audio_path: Path,
    output_path: Path,
    width: int,
    height: int,
    show_cards: bool = True,
    font_path: str | None = None,
    background_offset: int = 0,
    visual_mode: str = "stock",
    captions: list[tuple[str, int, int]] | None = None,
) -> Path:
    if not scenes:
        raise VideoAssemblyError("No scenes to assemble")
    illustrated = visual_mode == "illustrated"
    if not illustrated:
        clips = list_backgrounds(background_dir)
        chosen = assign_backgrounds(len(scenes), clips, background_offset)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="scenes_") as tmp:
        tmp_dir = Path(tmp)
        parts: list[Path] = []
        for n, scene in enumerate(scenes):
            focus: dict = {}
            if illustrated:
                steps_n = max(2, int(scene.duration_s * ANIM_FPS) + 1)
                schedule = anim_schedule(scene, steps_n)
                variants: dict[tuple, int] = {}
                frames: list[Path] = []
                order: list[int] = []
                walking = "walking" in scene.props
                for step_i, (phase, blink, mouth) in enumerate(schedule):
                    prog = step_i / max(1, len(schedule) - 1) if walking else None
                    key = (phase, blink, mouth, step_i if walking else 0)
                    if key not in variants:
                        variants[key] = len(frames)
                        png = tmp_dir / f"art{scene.index:03d}_{len(frames)}.png"
                        # drawn 1.2x larger than the frame so the camera push-in stays sharp
                        illustrate_scene(
                            (int(width * 1.2), int(height * 1.2)),
                            setting=scene.setting, mood=scene.mood,
                            characters=[dict(look) for look in scene.looks],
                            seed=f"{scene.index}-{scene.title}", out_path=png,
                            font_path=font_path, reference_palette=scene.ref_palette, props=scene.props,
                            speaker=scene.speaker, focus_out=focus,
                            anim={"phase": key[0], "breath": _BREATH[key[0]], "blink": key[1], "mouth": key[2], "prog": prog},
                        )
                        frames.append(png)
                    order.append(variants[key])
                clip = _animated_listing(frames, order, tmp_dir / f"anim{scene.index:03d}.txt")
            else:
                clip = chosen[n]
            card = None
            new_title = n == 0 or scenes[n - 1].title != scene.title
            if show_cards and new_title:
                card = render_chapter_card(scene, (width, height), tmp_dir / f"card{scene.index}.png", font_path=font_path)
            part = tmp_dir / f"scene{scene.index:03d}.mp4"
            scene_caps: list[tuple[Path, float, float]] = []
            if captions:
                from life_lesson.video.subtitles import render_caption
                for k, (text, a_ms, b_ms) in enumerate(captions):
                    if b_ms <= scene.start_ms or a_ms >= scene.end_ms:
                        continue
                    png = tmp_dir / f"cap{scene.index:03d}_{k}.png"
                    render_caption(text, (width, height), Path(find_thai_font(font_path))).save(png)
                    scene_caps.append((png, max(0.0, (a_ms - scene.start_ms) / 1000), (min(b_ms, scene.end_ms) - scene.start_ms) / 1000))
            _run(_scene_command(ffmpeg_binary, clip, card, scene, width, height, part, focus, scene_caps), f"rendering scene {scene.index}")
            parts.append(part)

        listing = tmp_dir / "list.txt"
        listing.write_text("".join(f"file '{p.as_posix()}'\n" for p in parts), encoding="utf-8")
        silent = tmp_dir / "silent.mp4"
        _run([ffmpeg_binary, "-y", "-f", "concat", "-safe", "0", "-i", str(listing), "-c", "copy", str(silent)], "joining scenes")
        _run(
            [
                ffmpeg_binary, "-y", "-i", str(silent), "-i", str(audio_path),
                "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                "-ar", "44100", "-shortest", "-movflags", "+faststart", str(output_path),
            ],
            "muxing audio",
        )
    return output_path
