"""Silent stand-in voice for storyboard previews (no API key, no quota).

Produces silence whose length follows the text (~12 Thai characters per
second, the pacing the scripts are written for), so chapters, scene cuts,
captions and the whole video timeline can be reviewed before spending any
real voice quota.
"""

from __future__ import annotations

import io
import wave

CHARS_PER_SECOND = 12.0
SAMPLE_RATE = 24_000


class SilentTTSProvider:
    cacheable = False  # silence must never be stored as if it were a real voice

    def synthesize(self, text: str) -> bytes:
        seconds = max(0.8, len(text) / CHARS_PER_SECOND)
        buf = io.BytesIO()
        with wave.open(buf, "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(SAMPLE_RATE)
            w.writeframes(b"\x00\x00" * int(SAMPLE_RATE * seconds))
        return buf.getvalue()
