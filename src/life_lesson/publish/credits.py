"""Credits and channel call-to-action lines shared by the pipeline and the library."""

from __future__ import annotations

from life_lesson.config import Settings


def channel_line(settings: Settings) -> str:
    return f"ดูเรื่องเต็มและเรื่องใหม่ได้ที่ช่อง {settings.channel_handle}\n{settings.channel_url}"


def build_credits(settings: Settings) -> list[str]:
    lines = [
        f"เสียงบรรยาย: {settings.gemini_tts_model} (voice: {settings.gemini_tts_voice})",
        "เสียงบรรยากาศ: สังเคราะห์ด้วยซอฟต์แวร์",
    ]
    path = settings.credits_file
    if path is not None and path.is_file():
        lines += [ln.strip() for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]
    else:
        lines.append("วิดีโอพื้นหลัง/ดนตรี: ระบุแหล่งที่มาและใบอนุญาตก่อนเผยแพร่ (assets/credits.txt)")
    return lines
