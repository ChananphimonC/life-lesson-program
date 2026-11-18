"""Episode formats: Shorts (9:16), standard (3-5 min) and long-form (15-40 min).

See docs/STYLE_GUIDE.md §4. All three share the same 4-phase philosophy
(hook / exploration / shift / outro); formats only change length, chapter
granularity and aspect ratio.
"""

from __future__ import annotations

from dataclasses import dataclass

from life_lesson.errors import ScriptValidationError


@dataclass(frozen=True)
class FormatSpec:
    name: str
    label_th: str
    min_seconds: int
    max_seconds: int
    width: int
    height: int
    min_blocks: int
    max_blocks: int
    needs_chapter_titles: bool
    # Rough ceiling on spoken Thai characters (~12-13 chars/sec) so a "short"
    # can't silently turn into a 3-minute script. None = no hard cap.
    max_chars: int | None

    @property
    def is_vertical(self) -> bool:
        return self.height > self.width


FORMATS: dict[str, FormatSpec] = {
    "short": FormatSpec(
        "short", "Shorts", 30, 55, 1080, 1920, 4, 8, False, 900
    ),
    "standard": FormatSpec(
        "standard", "ตอนเดียวจบ", 180, 300, 1920, 1080, 4, 12, False, None
    ),
    "long": FormatSpec(
        "long", "เรื่องยาว", 900, 2400, 1920, 1080, 12, 80, True, None
    ),
}
DEFAULT_FORMAT = "standard"


def get_format(name: str | None) -> FormatSpec:
    key = name or DEFAULT_FORMAT
    try:
        return FORMATS[key]
    except KeyError:
        raise ScriptValidationError(
            f"Unknown episode format {key!r}; expected one of {sorted(FORMATS)}"
        ) from None
