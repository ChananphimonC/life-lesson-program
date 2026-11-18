"""Configuration through environment variables (REQUIREMENTS.md NFR: no
hardcoded config). Values are read lazily via `get_settings()` so importing
this module never requires an API key to be set -- only code paths that
actually need it (e.g. the Gemini client) enforce its presence.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Settings:
    gemini_api_key: str | None
    gemini_script_model: str
    gemini_tts_model: str
    gemini_tts_voice: str
    db_path: Path
    background_video_dir: Path
    output_dir: Path
    ffmpeg_binary: str
    log_level: str
    thai_font_path: str | None = None
    music_dir: Path | None = None
    credits_file: Path | None = None
    tts_style_directives: bool = True
    channel_handle: str = "@SakidJai_สะกิดใจ"
    channel_url: str = "https://www.youtube.com/@SakidJai_%E0%B8%AA%E0%B8%B0%E0%B8%81%E0%B8%B4%E0%B8%94%E0%B9%83%E0%B8%88"
    export_dir: Path | None = None
    visual_mode: str = "illustrated"
    reference_search: bool = False
    punchup_threshold: int = 75
    preview_scale: float = 1.0
    cache_dir: Path | None = None

    @property
    def audio_output_dir(self) -> Path:
        return self.output_dir / "audio"

    @property
    def video_output_dir(self) -> Path:
        return self.output_dir / "video"


def _resolve_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else PROJECT_ROOT / path


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings(
        gemini_api_key=os.environ.get("GEMINI_API_KEY") or None,
        gemini_script_model=os.environ.get("GEMINI_SCRIPT_MODEL", "gemini-2.5-flash"),
        gemini_tts_model=os.environ.get("GEMINI_TTS_MODEL", "gemini-2.5-flash-preview-tts"),
        gemini_tts_voice=os.environ.get("GEMINI_TTS_VOICE", "Kore"),
        db_path=_resolve_path(os.environ.get("LIFE_LESSON_DB_PATH", "data/life_lesson.db")),
        background_video_dir=_resolve_path(os.environ.get("BACKGROUND_VIDEO_DIR", "assets/backgrounds")),
        output_dir=_resolve_path(os.environ.get("OUTPUT_DIR", "output")),
        ffmpeg_binary=os.environ.get("FFMPEG_BINARY", "ffmpeg"),
        log_level=os.environ.get("LOG_LEVEL", "INFO"),
        thai_font_path=os.environ.get("THAI_FONT_PATH") or None,
        music_dir=_resolve_path(os.environ.get("MUSIC_DIR", "assets/music")),
        credits_file=_resolve_path(os.environ.get("CREDITS_FILE", "assets/credits.txt")),
        channel_handle=os.environ.get("CHANNEL_HANDLE", "@SakidJai_สะกิดใจ"),
        channel_url=os.environ.get("CHANNEL_URL", "https://www.youtube.com/@SakidJai_%E0%B8%AA%E0%B8%B0%E0%B8%81%E0%B8%B4%E0%B8%94%E0%B9%83%E0%B8%88"),
        visual_mode=os.environ.get("VISUAL_MODE", "illustrated").lower(),
        punchup_threshold=int(os.environ.get("PUNCHUP_THRESHOLD", "75")),
        reference_search=os.environ.get("REFERENCE_SEARCH", "0").lower() in ("1", "true", "yes"),
        cache_dir=_resolve_path(os.environ.get("CACHE_DIR", "output/cache")),
        export_dir=_resolve_path(os.environ.get("EXPORT_DIR", "output/export")),
        tts_style_directives=os.environ.get("TTS_STYLE_DIRECTIVES", "1").lower() not in ("0", "false", "no"),
    )
