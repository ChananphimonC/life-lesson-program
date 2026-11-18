"""Cut a YouTube Short from a finished episode.

The Short is taken from the REAL episode (same picture, voice and sound), not
re-generated: pick the most gripping 30-55 s window that does not spoil the
ending, crop it to 9:16 over a blurred copy of itself, burn Thai captions, and
close with a call-to-action card pointing to the full video on the channel.
"""

from __future__ import annotations

import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from life_lesson.errors import VideoAssemblyError
from life_lesson.generation.atmosphere import scaled_pause_ms
from life_lesson.generation.schema import ScriptOutput
from life_lesson.publish.fonts import find_thai_font

CTA_SECONDS = 3.0
SPOILER_TAIL = 0.12  # never use the last 12% of the episode


@dataclass(frozen=True)
class Window:
    first: int  # first block index
    last: int   # last block index (inclusive)
    start_ms: int
    end_ms: int
    score: float

    @property
    def duration_s(self) -> float:
        return (self.end_ms - self.start_ms) / 1000


def block_end_times(script: ScriptOutput, starts_ms: list[int], total_ms: int) -> list[int]:
    """Speech end of each block = next block's start minus its (mood-scaled) pause."""
    ends = []
    for i, block in enumerate(script.script_blocks):
        nxt = starts_ms[i + 1] if i + 1 < len(starts_ms) else total_ms
        ends.append(max(starts_ms[i] + 500, nxt - scaled_pause_ms(block.pause_after_ms, block.mood)))
    return ends


def _tension(block) -> int:
    return block.mood.tension if block.mood else 2


def pick_teaser_window(
    script: ScriptOutput,
    starts_ms: list[int],
    total_ms: int,
    *,
    min_s: float = 30,
    max_s: float = 55,
    offset: int = 0,
) -> Window:
    """Best teaser window. `offset` picks the Nth best, so several different
    Shorts can be cut from one episode."""
    blocks = script.script_blocks
    ends = block_end_times(script, starts_ms, total_ms)
    limit = total_ms * (1 - SPOILER_TAIL)

    def candidates(strict: bool):
        for i in range(len(blocks)):
            for j in range(i, len(blocks)):
                start, end = starts_ms[i], ends[j]
                dur = (end - start) / 1000
                if dur > max_s:
                    break
                if dur < min_s:
                    continue
                span = blocks[i : j + 1]
                if any(b.phase == "outro" for b in span):
                    continue
                if strict and end > limit:
                    continue
                ts = [_tension(b) for b in span]
                score = (
                    2.0 * sum(ts) / len(ts)
                    + 1.5 * ts[-1]                        # end on a high note (cliffhanger)
                    + (3.0 if span[0].phase == "hook" else 0.0)  # cold open is built to grab
                    + 0.4 * (max(ts) - min(ts))           # movement beats a flat window
                    + (0.8 if span[-1].phase != "shift" else -1.5)  # don't give the turn away
                )
                yield Window(i, j, start, end, score)

    for strict in (True, False):
        ranked = sorted(candidates(strict), key=lambda w: (-w.score, w.start_ms))
        if ranked:
            return ranked[min(offset, len(ranked) - 1)]

    # Very short episodes: take from the top up to max_s, stopping at a block end.
    j = 0
    while j + 1 < len(blocks) and (ends[j + 1] - starts_ms[0]) / 1000 <= max_s:
        j += 1
    return Window(0, j, starts_ms[0], ends[j], 0.0)


# -- captions -----------------------------------------------------------------

def caption_chunks(text: str, start_ms: int, end_ms: int, max_chars: int = 26) -> list[tuple[str, int, int]]:
    """Split narration into short on-screen captions, timed by character count."""
    pieces: list[str] = []
    for part in text.replace("\n", " ").split():
        while len(part) > max_chars:
            pieces.append(part[:max_chars])
            part = part[max_chars:]
        if part:
            pieces.append(part)
    chunks: list[str] = []
    cur = ""
    for piece in pieces:
        if cur and len(cur) + 1 + len(piece) > max_chars:
            chunks.append(cur)
            cur = piece
        else:
            cur = f"{cur} {piece}".strip()
    if cur:
        chunks.append(cur)
    if not chunks:
        return []
    total = sum(len(c) for c in chunks)
    out, t = [], start_ms
    for c in chunks:
        dur = int((end_ms - start_ms) * len(c) / total)
        out.append((c, t, t + dur))
        t += dur
    out[-1] = (out[-1][0], out[-1][1], end_ms)
    return out


def _png_text(text: str, size: tuple[int, int], font_path: Path, font_px: int, *, box: bool, fg=(255, 255, 255), y_frac: float = 0.70) -> Image.Image:
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    font = ImageFont.truetype(str(font_path), font_px)
    while d.textlength(text, font=font) > size[0] * 0.88 and font_px > 20:
        font_px -= 2
        font = ImageFont.truetype(str(font_path), font_px)
    tw = d.textlength(text, font=font)
    x = (size[0] - tw) / 2
    y = size[1] * y_frac
    if box:
        pad = font_px * 0.35
        d.rounded_rectangle([x - pad, y - pad * 0.5, x + tw + pad, y + font_px * 1.25 + pad * 0.3], radius=font_px * 0.3, fill=(0, 0, 0, 150))
    d.text((x + 2, y + 2), text, font=font, fill=(0, 0, 0, 220))
    d.text((x, y), text, font=font, fill=fg)
    return img


def _cta_card(size, font_path: Path, handle: str) -> Image.Image:
    w, h = size
    img = Image.new("RGBA", size, (8, 10, 18, 215))
    d = ImageDraw.Draw(img)
    f1 = ImageFont.truetype(str(font_path), int(w * 0.075))
    f2 = ImageFont.truetype(str(font_path), int(w * 0.062))
    for text, font, y, col in (
        ("ดูเรื่องเต็มได้ที่ช่อง", f1, h * 0.42, (255, 255, 255)),
        (handle, f2, h * 0.50, (255, 214, 10)),
        ("กดติดตามไว้ ตอนใหม่มาแน่", f1, h * 0.60, (200, 235, 190)),
    ):
        fnt = font
        while d.textlength(text, font=fnt) > w * 0.9 and fnt.size > 16:
            fnt = ImageFont.truetype(str(font_path), fnt.size - 2)
        d.text(((w - d.textlength(text, font=fnt)) / 2, y), text, font=fnt, fill=col)
    return img


def render_short(
    *,
    ffmpeg_binary: str,
    source_video: Path,
    window: Window,
    script: ScriptOutput,
    starts_ms: list[int],
    ends_ms: list[int],
    output_path: Path,
    channel_handle: str,
    title: str,
    font_path: str | None = None,
    width: int = 1080,
    height: int = 1920,
    layout: str = "fit",
) -> Path:
    """layout "fit": whole 16:9 frame over a blurred copy (nothing cropped);
    "tall": crop the centre 56% of the frame to fill most of the 9:16 screen."""
    if layout not in ("fit", "tall"):
        raise VideoAssemblyError("layout must be 'fit' or 'tall'")
    # fit leaves blurred bands above/below the picture: titles/captions live in the bands
    title_y, cap_y = (0.27, 0.70) if layout == "fit" else (0.06, 0.66)
    font = find_thai_font(font_path)
    dur = window.duration_s
    total = dur + CTA_SECONDS
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="short_") as tmp:
        tmp_dir = Path(tmp)
        inputs: list[str] = ["-ss", f"{window.start_ms / 1000:.3f}", "-t", f"{dur:.3f}", "-i", str(source_video)]
        overlays: list[tuple[Path, float, float]] = []  # png, start_s, end_s

        title_png = tmp_dir / "title.png"
        _png_text(title, (width, height), font, int(width * 0.062), box=True, y_frac=title_y).save(title_png)
        overlays.append((title_png, 0.0, dur))

        n = 0
        for idx in range(window.first, window.last + 1):
            b_start = max(starts_ms[idx], window.start_ms) - window.start_ms
            b_end = min(ends_ms[idx], window.end_ms) - window.start_ms
            for text, a, b in caption_chunks(script.script_blocks[idx].text, b_start, b_end):
                png = tmp_dir / f"cap{n:03d}.png"
                _png_text(text, (width, height), font, int(width * 0.066), box=True, y_frac=cap_y).save(png)
                overlays.append((png, a / 1000, b / 1000))
                n += 1

        cta_png = tmp_dir / "cta.png"
        _cta_card((width, height), font, channel_handle).save(cta_png)
        overlays.append((cta_png, dur, total))

        for png, _, _ in overlays:
            inputs += ["-i", str(png)]

        steps = [
            f"[0:v]tpad=stop_mode=clone:stop_duration={CTA_SECONDS},split[a][b]",
            f"[a]scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height},"
            "gblur=sigma=28,eq=brightness=-0.18[bg]",
            (f"[b]scale={width}:-2[fg]" if layout == "fit"
             else f"[b]crop=iw*0.56:ih,scale={width}:-2[fg]"),
            "[bg][fg]overlay=(W-w)/2:(H-h)/2[v0]",
        ]
        label = "v0"
        for i, (_, a, b) in enumerate(overlays, start=1):
            out = f"v{i}"
            steps.append(f"[{label}][{i}:v]overlay=0:0:enable='between(t,{a:.3f},{b:.3f})'[{out}]")
            label = out
        steps.append(f"[{label}]fade=t=in:st=0:d=0.25,fade=t=out:st={total - 0.4:.3f}:d=0.4,format=yuv420p[vout]")
        steps.append(f"[0:a]apad=pad_dur={CTA_SECONDS},afade=t=in:st=0:d=0.15,afade=t=out:st={total - 0.5:.3f}:d=0.5[aout]")

        cmd = [
            ffmpeg_binary, "-y", *inputs, "-filter_complex", ";".join(steps),
            "-map", "[vout]", "-map", "[aout]", "-t", f"{total:.3f}",
            "-r", "30", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
            "-c:a", "aac", "-ar", "44100", "-movflags", "+faststart", str(output_path),
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        except FileNotFoundError as exc:
            raise VideoAssemblyError(f"ffmpeg binary not found ('{ffmpeg_binary}')") from exc
        if result.returncode != 0:
            raise VideoAssemblyError(f"ffmpeg failed while cutting the Short: {result.stderr[-1500:]}")
    return output_path


# -- metadata -------------------------------------------------------------------

def short_title(script: ScriptOutput, window: Window) -> str:
    first = script.script_blocks[window.first].text.replace("\n", " ").split()
    line = ""
    for word in first:
        if len(line) + len(word) + 1 > 34:
            break
        line = f"{line} {word}".strip()
    line = line or script.title
    return f"{line}…" if len(line) < len(" ".join(first)) else line


def short_description(
    script: ScriptOutput, *, channel_handle: str, channel_url: str, full_url: str | None = None
) -> str:
    from life_lesson.publish.metadata import AI_DISCLOSURE, FICTION_DISCLAIMER

    lines = []
    if script.summary:
        lines.append(script.summary.strip())
    cta = f"ดูเรื่องเต็ม \"{script.title}\" ได้ที่ช่อง {channel_handle}"
    lines.append(cta + (f"\n{full_url}" if full_url else f"\n{channel_url}"))
    lines += [FICTION_DISCLAIMER, AI_DISCLOSURE, "#Shorts #เรื่องเล่า #สะกิดใจ"]
    return "\n\n".join(lines) + "\n"
