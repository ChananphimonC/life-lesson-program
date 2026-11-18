"""Procedural ambient sound beds driven by each scene's mood (no sample library needed).

Every sound is synthesised with FFmpeg (noise + filters / short expressions):
rain, thunder, wind, waves, room tone, heartbeat, clock. Scenes get one bed each,
cross-faded at the edges and joined into a single track the length of the
narration. The mastering step then ducks this bed under the voice.
"""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

from life_lesson.errors import TTSError
from life_lesson.generation.atmosphere import BlockMood

SR = 44100
EDGE_FADE_S = 0.6

# (source filter template, post filter, level in dB). {d} = duration seconds.
_NOISE = "anoisesrc=color={color}:amplitude=0.6:sample_rate=%d:duration={d}" % SR


def _sound_chain(sound: str, tension: int) -> tuple[str, float] | None:
    """Return (lavfi chain producing mono audio, gain_db) for a sound, or None."""
    if sound == "silence":
        return None
    if sound == "rain":
        return (_NOISE.format(color="pink", d="{d}") + ",highpass=f=1100,lowpass=f=9500", -23.0)
    if sound == "thunder":
        # a low rumble that swells every ~11s and decays
        return (
            _NOISE.format(color="brown", d="{d}")
            + ",lowpass=f=130,volume='if(lt(mod(t,11),3),2.2*exp(-1.1*mod(t,11)),0)':eval=frame",
            -15.0,
        )
    if sound == "wind":
        return (_NOISE.format(color="brown", d="{d}") + ",bandpass=f=420:width_type=h:w=500,tremolo=f=0.22:d=0.55", -22.0)
    if sound == "waves":
        return (_NOISE.format(color="brown", d="{d}") + ",lowpass=f=520,tremolo=f=0.13:d=0.85", -21.0)
    if sound == "room_tone":
        return (_NOISE.format(color="brown", d="{d}") + ",lowpass=f=170", -32.0)
    if sound == "heartbeat":
        period = {1: 1.1, 2: 1.0, 3: 0.9, 4: 0.75, 5: 0.62}[tension]
        e = (
            f"aevalsrc='0.9*sin(2*PI*52*t)*exp(-26*mod(t,{period}))"
            f"+0.6*sin(2*PI*46*t)*exp(-30*mod(t+{period}-{period * 0.32:.3f},{period}))':s={SR}:d={{d}}"
        )
        return (e, -19.0)
    if sound == "engine":  # low diesel rumble with a slight shudder
        return (_NOISE.format(color="brown", d="{d}") + ",lowpass=f=110,tremolo=f=7:d=0.18", -24.0)
    if sound == "clock":
        return ("aevalsrc='0.5*sin(2*PI*1900*t)*exp(-140*mod(t,1))':s=%d:d={d}" % SR, -30.0)
    raise ValueError(f"unknown sound {sound!r}")


def default_sounds(mood: BlockMood | None) -> list[str]:
    """Sounds implied by the mood when the script didn't list any."""
    if mood is None:
        return []
    out: list[str] = []
    if mood.weather == "rain":
        out.append("rain")
    elif mood.weather == "storm":
        out += ["rain", "thunder"]
    elif mood.weather == "wind":
        out.append("wind")
    elif mood.weather == "fog":
        out.append("wind")
    if mood.tension >= 4:
        out.append("heartbeat")
    if not out:
        out.append("room_tone")
    return out


def scene_filtergraph(mood: BlockMood | None, duration_s: float) -> str | None:
    sounds = list(mood.sounds) if mood and mood.sounds else default_sounds(mood)
    tension = mood.tension if mood else 2
    chains: list[str] = []
    for snd in dict.fromkeys(sounds):
        built = _sound_chain(snd, tension)
        if built is None:
            continue
        chain, gain = built
        chains.append(f"{chain.format(d=f'{duration_s:.3f}')},aformat=sample_rates={SR}:channel_layouts=mono,volume={gain}dB")
    if not chains:
        return None
    labels = "".join(f"[s{i}]" for i in range(len(chains)))
    parts = [f"{c}[s{i}]" for i, c in enumerate(chains)]
    fade_out = max(0.0, duration_s - EDGE_FADE_S)
    mix = (
        f"{labels}amix=inputs={len(chains)}:duration=longest:normalize=0,"
        f"afade=t=in:st=0:d={EDGE_FADE_S},afade=t=out:st={fade_out:.3f}:d={EDGE_FADE_S}[out]"
    )
    # each source is a lavfi input, so build as a single -filter_complex on `-f lavfi` via anullsrc-free graph
    return ";".join(parts + [mix])


def _run(command: list[str], what: str) -> None:
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=False)
    except FileNotFoundError as exc:
        raise TTSError(f"ffmpeg binary not found ('{command[0]}')") from exc
    if result.returncode != 0:
        raise TTSError(f"ambient audio failed while {what}: {result.stderr[-1500:]}")


def build_ambient_bed(
    ffmpeg_binary: str,
    scenes,
    total_ms: int,
    output: Path,
    *,
    music: Path | None = None,
    music_gain_db: float = -20.0,
) -> Path | None:
    """Render one bed per scene, join them, optionally mix a music track under.

    Returns None when no scene has any ambient sound and no music was given.
    """
    graphs = [scene_filtergraph(sc.mood, sc.duration_s) for sc in scenes]
    if music is None and all(g is None for g in graphs):
        return None  # nothing audible: skip ffmpeg entirely
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="ambient_") as tmp:
        tmp_dir = Path(tmp)
        parts: list[Path] = []
        for scene, graph in zip(scenes, graphs):
            dur = scene.duration_s
            part = tmp_dir / f"bed{scene.index:03d}.wav"
            if graph is None:
                cmd = [ffmpeg_binary, "-y", "-f", "lavfi", "-i", f"anullsrc=r={SR}:cl=mono", "-t", f"{dur:.3f}", str(part)]
            else:
                # lavfi sources are inlined in the graph, so no -i inputs: use a null input
                cmd = [ffmpeg_binary, "-y", "-filter_complex", graph, "-map", "[out]", "-t", f"{dur:.3f}", "-ar", str(SR), "-ac", "1", str(part)]
            _run(cmd, f"rendering ambient for scene {scene.index}")
            parts.append(part)

        listing = tmp_dir / "list.txt"
        listing.write_text("".join(f"file '{p.as_posix()}'\n" for p in parts), encoding="utf-8")
        joined = tmp_dir / "joined.wav"
        _run([ffmpeg_binary, "-y", "-f", "concat", "-safe", "0", "-i", str(listing), "-c", "copy", str(joined)], "joining ambient beds")

        total_s = f"{total_ms / 1000:.3f}"
        if music is None:
            _run([ffmpeg_binary, "-y", "-i", str(joined), "-t", total_s, "-af", "apad", "-ar", str(SR), "-ac", "1", str(output)], "finalising ambient bed")
        else:
            _run(
                [
                    ffmpeg_binary, "-y", "-i", str(joined), "-stream_loop", "-1", "-i", str(music),
                    "-filter_complex",
                    f"[1:a]volume={music_gain_db}dB,aformat=sample_rates={SR}:channel_layouts=mono[m];"
                    f"[0:a]aformat=sample_rates={SR}:channel_layouts=mono[a];"
                    "[a][m]amix=inputs=2:duration=first:normalize=0[out]",
                    "-map", "[out]", "-t", total_s, "-ar", str(SR), "-ac", "1", str(output),
                ],
                "mixing music under the ambient bed",
            )
    return output
