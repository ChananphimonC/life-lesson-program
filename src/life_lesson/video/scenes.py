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
from life_lesson.generation.schema import ScriptOutput
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
            {"start": start, "title": title, "time_label": block.time_label, "cue": block.visual_cue}
        )
    if not groups:
        return []
    groups[0]["start"] = 0

    merged: list[dict] = [groups[0]]
    for g in groups[1:]:
        if g["start"] - merged[-1]["start"] < MIN_SCENE_MS or total_ms - g["start"] < MIN_SCENE_MS:
            continue
        merged.append(g)

    scenes = []
    for i, g in enumerate(merged):
        end = merged[i + 1]["start"] if i + 1 < len(merged) else total_ms
        scenes.append(Scene(i, g["start"], end, g["title"], g["time_label"], g["cue"]))
    return scenes


def write_shot_list(scenes: list[Scene], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps([asdict(s) for s in scenes], ensure_ascii=False, indent=2), encoding="utf-8"
    )
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


def _scene_command(
    ffmpeg: str, clip: Path, card: Path | None, scene: Scene, width: int, height: int, out: Path
) -> list[str]:
    dur = scene.duration_s
    fade_out_at = max(0.0, dur - FADE_S)
    base = (
        f"[0:v]scale={width}:{height}:force_original_aspect_ratio=increase,"
        f"crop={width}:{height},eq=brightness=-0.06:saturation=0.9,vignette=PI/5"
    )
    cmd = [ffmpeg, "-y", "-stream_loop", "-1", "-i", str(clip)]
    if card is not None:
        cmd += ["-loop", "1", "-i", str(card)]
        graph = (
            f"{base}[bg];"
            f"[1:v]format=rgba,fade=t=in:st=0.4:d=0.6:alpha=1,"
            f"fade=t=out:st={CARD_SECONDS - 0.6}:d=0.6:alpha=1[card];"
            f"[bg][card]overlay=0:0:enable='lt(t,{CARD_SECONDS})':shortest=0,"
            f"fade=t=in:st=0:d={FADE_S},fade=t=out:st={fade_out_at}:d={FADE_S},format=yuv420p[v]"
        )
    else:
        graph = (
            f"{base},fade=t=in:st=0:d={FADE_S},"
            f"fade=t=out:st={fade_out_at}:d={FADE_S},format=yuv420p[v]"
        )
    cmd += [
        "-filter_complex", graph, "-map", "[v]", "-t", f"{dur:.3f}",
        "-an", "-r", "30", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", str(out),
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
) -> Path:
    if not scenes:
        raise VideoAssemblyError("No scenes to assemble")
    clips = list_backgrounds(background_dir)
    chosen = assign_backgrounds(len(scenes), clips, background_offset)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="scenes_") as tmp:
        tmp_dir = Path(tmp)
        parts: list[Path] = []
        for scene, clip in zip(scenes, chosen):
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
