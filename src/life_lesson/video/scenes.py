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
from life_lesson.video.scene_kb import is_worker, retrieve_recipe
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
        if groups and (title is None or title == groups[-1]["title"]):
            continue
        groups.append(
            {"start": start, "title": title, "time_label": block.time_label,
             "cue": block.visual_cue, "moods": [], "cues": [], "settings": []}
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
        looks = tuple(
            character_colors(
                c.outfit, c.palette, c.name,
                extra_items=recipe.wardrobe if is_worker(recipe, c.role, c.name, c.outfit) else (),
                sleeve=recipe.sleeve if is_worker(recipe, c.role, c.name, c.outfit) else None,
            )
            for c in present
        )
        scenes.append(Scene(i, g["start"], end, g["title"], g["time_label"], g["cue"], mood,
                            setting, looks, tuple(c.name for c in present), recipe.id))
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
    y = int(h * 0.74) if w >= h else int(h * 0.60)
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


def _motion_filter(scene: Scene, width: int, height: int) -> str:
    """Slow camera push-in (stronger when tense) with a gentle sideways drift."""
    frames = max(2, int(scene.duration_s * 30))
    push = 0.20 if (scene.mood and scene.mood.tension >= 4) else 0.11
    return (
        f"zoompan=z='1.0+{push}*on/{frames}':"
        f"x='(iw-iw/zoom)/2+iw*0.018*sin(on/210)':y='(ih-ih/zoom)/2':"
        f"d={frames}:s={width}x{height}:fps=30"
    )


def _scene_command(
    ffmpeg: str, clip: Path, card: Path | None, scene: Scene, width: int, height: int, out: Path
) -> list[str]:
    dur = scene.duration_s
    fade_out_at = max(0.0, dur - FADE_S)
    illustrated = clip.suffix.lower() == ".png"
    if illustrated:
        cmd = [ffmpeg, "-y", "-i", str(clip)]
        first = f"[0:v]{_motion_filter(scene, width, height)},setsar=1,"
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

    steps.append(
        f"[{label}]fade=t=in:st=0:d={FADE_S},fade=t=out:st={fade_out_at}:d={FADE_S},format=yuv420p[v]"
    )
    cmd += [
        "-filter_complex", ";".join(steps), "-map", "[v]", "-t", f"{dur:.3f}",
        "-an", "-r", "30", "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
        # rain/noise layers are incompressible: cap the rate so long episodes stay uploadable
        "-maxrate", "6M", "-bufsize", "12M", str(out),
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
            if illustrated:
                clip = tmp_dir / f"art{scene.index:03d}.png"
                # drawn 1.2x larger than the frame so the camera push-in stays sharp
                illustrate_scene(
                    (int(width * 1.2), int(height * 1.2)),
                    setting=scene.setting, mood=scene.mood,
                    characters=[dict(look) for look in scene.looks],
                    seed=f"{scene.index}-{scene.title}", out_path=clip,
                    font_path=font_path, reference_palette=scene.ref_palette,
                )
            else:
                clip = chosen[n]
            card = None
            if show_cards:
                card = render_chapter_card(scene, (width, height), tmp_dir / f"card{scene.index}.png", font_path=font_path)
            part = tmp_dir / f"scene{scene.index:03d}.mp4"
            _run(_scene_command(ffmpeg_binary, clip, card, scene, width, height, part), f"rendering scene {scene.index}")
            parts.append(part)

        listing = tmp_dir / "list.txt"
        listing.write_text("".join(f"file '{p.as_posix()}'\n" for p in parts), encoding="utf-8")
        silent = tmp_dir / "silent.mp4"
        _run([ffmpeg_binary, "-y", "-f", "concat", "-safe", "0", "-i", str(listing), "-c", "copy", str(silent)], "joining scenes")
        _run(
            [
                ffmpeg_binary, "-y", "-i", str(silent), "-i", str(audio_path),
                "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac",
                "-ar", "44100", "-shortest", "-movflags", "+faststart", str(output_path),
            ],
            "muxing audio",
        )
    return output_path
