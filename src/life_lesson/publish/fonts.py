"""Locate a Thai-capable bold font for rendered text (thumbnails, chapter cards)."""

from __future__ import annotations

from pathlib import Path

from life_lesson.errors import PipelineError

_CANDIDATES = [
    "/usr/share/fonts/opentype/tlwg/Loma-Bold.otf",
    "/usr/share/fonts/truetype/tlwg/Loma-Bold.ttf",
    "/usr/share/fonts/truetype/noto/NotoSansThai-Bold.ttf",
    "/usr/share/fonts/truetype/noto/NotoSansThaiUI-Bold.ttf",
    "/usr/share/fonts/truetype/thai-tlwg/Loma-Bold.ttf",
    "/usr/share/fonts/truetype/google-fonts/Sarabun-Bold.ttf",
    "/Library/Fonts/Thonburi.ttc",
    "/System/Library/Fonts/Supplemental/Ayuthaya.ttf",
    "C:/Windows/Fonts/leelawdb.ttf",
    "C:/Windows/Fonts/tahomabd.ttf",
]


def find_thai_font(preferred: str | None = None) -> Path:
    for candidate in ([preferred] if preferred else []) + _CANDIDATES:
        if candidate and Path(candidate).is_file():
            return Path(candidate)
    raise PipelineError(
        "No Thai-capable font found. Set THAI_FONT_PATH in .env to a .ttf/.otf "
        "file that contains Thai glyphs (e.g. Sarabun or Noto Sans Thai Bold)."
    )
