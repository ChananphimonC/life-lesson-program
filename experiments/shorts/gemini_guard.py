"""Quota counter + retry/backoff around every Gemini call made by the Shorts pipeline.

The free tier shares one quota across scripts, TTS and cover text, and Gemini TTS is the
tightest (about 10 requests/day was observed). This guard:
  * counts every request attempt per kind per day (output/gemini_usage.json),
  * refuses to call once the configured daily limit is reached (-> QuotaExhausted, caller falls back),
  * on a per-minute 429 waits the server's suggested delay, then retries,
  * on 503/500/timeouts and the occasional "model tried to generate text" 400 backs off exponentially,
  * on a per-day 429 pauses further calls for an hour (then tries again), so one bad classification can't block a day.
Limits come from env: GEMINI_TTS_DAILY_LIMIT (default 10), GEMINI_TEXT_DAILY_LIMIT (default 200).
"""

from __future__ import annotations

import json
import os
import random
import re
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

USAGE_FILE = Path(__file__).resolve().parent / "output" / "gemini_usage.json"
DEFAULT_LIMITS = {"tts": 10, "text": 200}


class QuotaExhausted(RuntimeError):
    """Daily quota is (or is assumed to be) used up; the caller should use a fallback."""


def _today() -> str:
    # Google resets free-tier daily quotas at midnight Pacific time (PDT in summer, so 14:00 in Thailand; PST = 15:00).
    # A fixed UTC-8 was an hour late in summer and let a whole session be counted on the wrong day.
    try:
        from zoneinfo import ZoneInfo
        return datetime.now(ZoneInfo("America/Los_Angeles")).strftime("%Y-%m-%d")
    except Exception:
        return datetime.now(timezone(timedelta(hours=-7))).strftime("%Y-%m-%d")


def _load() -> dict:
    try:
        return json.loads(USAGE_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _save(data: dict) -> None:
    USAGE_FILE.parent.mkdir(parents=True, exist_ok=True)
    USAGE_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def limit_for(kind: str) -> int:
    return int(os.environ.get(f"GEMINI_{kind.upper()}_DAILY_LIMIT", DEFAULT_LIMITS.get(kind, 50)))


def used_today(kind: str) -> int:
    return _load().get(_today(), {}).get(kind, 0)


def _bump(kind: str) -> None:
    data = _load()
    day = data.setdefault(_today(), {})
    day[kind] = day.get(kind, 0) + 1
    for old in sorted(data)[:-7]:  # keep a week
        data.pop(old)
    _save(data)


def _mark_exhausted(kind: str) -> None:
    data = _load()
    data.setdefault(_today(), {})[f"{kind}_exhausted_at"] = time.time()
    _save(data)


def _recently_exhausted(kind: str, hold_s: float = 3600.0) -> bool:
    """A quota error blocks further calls for an hour, then we simply try again (the API is the judge)."""
    ts = _load().get(_today(), {}).get(f"{kind}_exhausted_at")
    return bool(ts) and time.time() - ts < hold_s


def _retry_delay(msg: str) -> float | None:
    m = re.search(r"retry(?:Delay)?\D{0,12}(\d+(?:\.\d+)?)\s*s", msg, re.I)
    return float(m.group(1)) if m else None


def _classify(exc: Exception) -> str:
    msg = str(exc)
    low = msg.lower()
    if "429" in msg or "resource_exhausted" in low:
        return "daily" if re.search(r"per ?day|perday|daily", low) else "rate"
    if any(s in low for s in ("503", "500", "unavailable", "timed out", "timeout", "overloaded",
                              "model tried to generate text", "no audio data", "connection")):
        return "transient"
    return "fatal"


def guarded(kind: str, fn, *, retries: int = 3, sleep=time.sleep):
    """Run `fn()` (one Gemini request) under the quota counter and backoff policy."""
    limit = limit_for(kind)
    if _recently_exhausted(kind):
        raise QuotaExhausted(f"{kind}: the API reported its daily quota is used up within the last hour")
    last: Exception | None = None
    for attempt in range(retries + 1):
        if used_today(kind) >= limit:
            raise QuotaExhausted(f"{kind}: {used_today(kind)}/{limit} requests used today (local counter)")
        _bump(kind)
        try:
            return fn()
        except Exception as exc:  # noqa: BLE001 - external API call
            last, how = exc, _classify(exc)
            if how == "fatal":
                raise
            if how == "daily":
                _mark_exhausted(kind)
                raise QuotaExhausted(f"{kind}: Gemini reports the daily quota is exhausted") from exc
            if attempt == retries:
                break
            wait = (_retry_delay(str(exc)) or 2.0 * 2 ** attempt) if how == "rate" else 2.0 * 2 ** attempt
            wait = min(wait, 60.0) + random.uniform(0, 0.5)
            print(f"  gemini {kind}: {how} error, retry {attempt + 1}/{retries} in {wait:.0f}s "
                  f"({used_today(kind)}/{limit} used)", flush=True)
            sleep(wait)
    raise last  # type: ignore[misc]


def summary() -> str:
    day = _load().get(_today(), {})
    return ", ".join(f"{k}: {day.get(k, 0)}/{limit_for(k)}" for k in DEFAULT_LIMITS)
