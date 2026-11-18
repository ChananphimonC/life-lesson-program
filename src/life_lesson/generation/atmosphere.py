"""Per-block atmosphere: light, colour, weather, sound, tension and voice delivery.

One `BlockMood` drives four things so picture, sound and narration always agree:
  * the narration's delivery directive (TTS style),
  * pause length (tension speeds the rhythm up, calm slows it down),
  * the scene's colour grade / rain / fog / lightning (video),
  * the ambient sound bed (audio).
See docs/STYLE_GUIDE.md §15.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

Light = Literal["bright", "dim", "dark", "golden", "neon", "flicker"]
Weather = Literal["clear", "rain", "storm", "fog", "wind"]
Color = Literal["warm", "cool", "teal", "amber", "mono", "green"]
Voice = Literal["calm", "hushed", "warm", "wistful", "tense", "urgent"]
Sound = Literal["rain", "thunder", "wind", "waves", "room_tone", "heartbeat", "clock", "silence"]


class BlockMood(BaseModel):
    light: Light = "dim"
    weather: Weather = "clear"
    color: Color = "cool"
    tension: int = Field(default=2, ge=1, le=5)
    voice: Voice = "calm"
    sounds: list[Sound] = Field(default_factory=list)


VOICE_DIRECTIVES: dict[str, str] = {
    "calm": "Say in a calm, steady, intimate voice",
    "hushed": "Say in a close, hushed, almost whispered voice, slowly",
    "warm": "Say warmly and gently",
    "wistful": "Say softly, with quiet wistfulness",
    "tense": "Say in a low, controlled, tense voice, a little faster",
    "urgent": "Say urgently but without shouting, with short breaths",
}

# tension -> multiplier on pause_after_ms (more tension = tighter rhythm)
PAUSE_FACTOR = {1: 1.25, 2: 1.0, 3: 0.9, 4: 0.7, 5: 0.55}
MIN_PAUSE_MS = 150


def styled_text(text: str, mood: BlockMood | None) -> str:
    """Prefix the narration with a delivery directive for the TTS model."""
    if mood is None:
        return text
    return f"{VOICE_DIRECTIVES[mood.voice]}: {text}"


def scaled_pause_ms(pause_ms: int, mood: BlockMood | None) -> int:
    if mood is None or pause_ms <= 0:
        return pause_ms
    return max(MIN_PAUSE_MS, int(pause_ms * PAUSE_FACTOR[mood.tension]))


# -- video grade ---------------------------------------------------------------

_LIGHT_EQ = {
    "bright": "eq=brightness=0.03:contrast=1.05:saturation=1.05",
    "dim": "eq=brightness=-0.06:contrast=1.05:saturation=0.9",
    "dark": "eq=brightness=-0.17:contrast=1.18:saturation=0.85",
    "golden": "eq=brightness=-0.02:contrast=1.08:saturation=1.1",
    "neon": "eq=brightness=-0.08:contrast=1.15:saturation=1.5",
    "flicker": "eq=brightness='-0.09+0.06*sin(t*37)*sin(t*11)':contrast=1.1:eval=frame",
}
_COLOR_BALANCE = {
    "warm": "colorbalance=rs=0.08:gs=0.02:bs=-0.08:rm=0.05:bm=-0.05",
    "cool": "colorbalance=rs=-0.05:bs=0.08:rm=-0.03:bm=0.05",
    "teal": "colorbalance=rs=-0.12:gs=0.03:bs=0.1:rm=-0.06:bm=0.06",
    "amber": "colorbalance=rs=0.13:gs=0.05:bs=-0.15:rm=0.08:bm=-0.08",
    "mono": "eq=saturation=0.12",
    "green": "colorbalance=rs=-0.05:gs=0.09:bs=-0.03",
}


def grade_filter(mood: BlockMood | None) -> str:
    """ffmpeg video filter chain (no labels) for this mood; '' when no mood."""
    if mood is None:
        return "vignette=PI/5"
    parts = [_LIGHT_EQ[mood.light], _COLOR_BALANCE[mood.color]]
    if mood.weather == "fog":
        parts += ["curves=all='0/0.14 1/0.88'", "gblur=sigma=1.6"]
    if mood.weather == "storm":
        # lightning: a ~0.12s white flash every 7s, evaluated per frame
        parts.append("eq=brightness='if(lt(mod(t,7),0.12),0.45,0)':eval=frame")
    angle = f"PI/{2.8 + 0.7 * mood.tension:.1f}"
    parts.append(f"vignette={angle}")
    return ",".join(parts)


def rain_chain(width: int, height: int, mood: BlockMood | None) -> str | None:
    """lavfi source + filters producing sparse vertical rain streaks, or None.

    Built from mid-grey temporal noise (so every frame differs), blurred
    vertically into streaks, then thresholded so only the brightest ~8-12%
    survive -- black elsewhere, so a 'screen' blend leaves the picture intact.
    """
    if mood is None or mood.weather not in ("rain", "storm"):
        return None
    sigma_v, cut_lo, cut_hi = (9, 0.84, 0.91) if mood.weather == "rain" else (13, 0.79, 0.87)
    return (
        f"color=c=gray:s={width}x{height}:r=30,"
        f"noise=alls=100:allf=t,format=gray,gblur=sigma=0.5:sigmaV={sigma_v},eq=contrast=7,"
        f"curves=all='0/0 {cut_lo}/0 {cut_hi}/0.9 1/1',format=gbrp"
    )


def rain_opacity(mood: BlockMood) -> float:
    return 0.3 if mood.weather == "rain" else 0.42
