"""Optional reference lookup before drawing (opt-in: REFERENCE_SEARCH=1).

Searches Openverse for openly licensed photos matching a scene recipe's query
(e.g. "thai street food stall pad kaprao wok flame night"), downloads only the
small thumbnails, and extracts their dominant colours so the drawing's
atmosphere follows real-world lighting and palette. No photo is copied into the
video; attribution lines are still returned so they can be added to the
description credits (CC licences ask for it).

Only the generic scene query leaves the machine -- never script text, titles or
anything about the channel. Network failures return [] (best effort).
"""

from __future__ import annotations

import hashlib
import json
import logging
import urllib.parse
import urllib.request
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Callable

from PIL import Image

logger = logging.getLogger(__name__)

OPENVERSE_API = "https://api.openverse.org/v1/images/"
USER_AGENT = "life-lesson-program/0.1 (scene-reference lookup)"


@dataclass(frozen=True)
class Reference:
    title: str
    creator: str
    license: str
    url: str
    palette: tuple[tuple[int, int, int], ...]

    @property
    def credit_line(self) -> str:
        who = f" by {self.creator}" if self.creator else ""
        return f"Reference photo \"{self.title}\"{who} ({self.license}) {self.url}"


def default_fetch(url: str, timeout: float = 15.0) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310 - fixed https hosts
        return resp.read()


def dominant_palette(image_bytes: bytes, colors: int = 5) -> tuple[tuple[int, int, int], ...]:
    img = Image.open(BytesIO(image_bytes)).convert("RGB").resize((64, 64))
    q = img.quantize(colors=colors, method=Image.Quantize.MEDIANCUT)
    pal = q.getpalette()[: colors * 3]
    counts = sorted(q.getcolors() or [], reverse=True)  # (count, index)
    return tuple((pal[i * 3], pal[i * 3 + 1], pal[i * 3 + 2]) for _, i in counts)


def search_references(
    query: str,
    *,
    limit: int = 3,
    fetch: Callable[[str], bytes] = default_fetch,
    cache_dir: Path | None = None,
) -> list[Reference]:
    key = hashlib.md5(f"{query}|{limit}".encode()).hexdigest()
    cache_file = cache_dir / f"{key}.json" if cache_dir else None
    if cache_file and cache_file.is_file():
        try:
            return [
                Reference(r["title"], r["creator"], r["license"], r["url"], tuple(tuple(c) for c in r["palette"]))
                for r in json.loads(cache_file.read_text(encoding="utf-8"))
            ]
        except (OSError, ValueError, KeyError):
            pass

    params = urllib.parse.urlencode(
        {"q": query, "page_size": limit, "license_type": "commercial", "mature": "false"}
    )
    out: list[Reference] = []
    try:
        data = json.loads(fetch(f"{OPENVERSE_API}?{params}"))
        for item in data.get("results", [])[:limit]:
            thumb = item.get("thumbnail") or item.get("url")
            if not thumb:
                continue
            lic = f"{item.get('license', '').upper()} {item.get('license_version', '')}".strip()
            out.append(
                Reference(
                    title=item.get("title") or "untitled",
                    creator=item.get("creator") or "",
                    license=lic,
                    url=item.get("foreign_landing_url") or item.get("url") or "",
                    palette=dominant_palette(fetch(thumb)),
                )
            )
    except Exception as exc:  # noqa: BLE001 - best effort: never block an episode on this
        logger.warning("Reference lookup failed for %r: %s", query, exc)
        return []

    if cache_file and out:
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        cache_file.write_text(
            json.dumps([{"title": r.title, "creator": r.creator, "license": r.license, "url": r.url,
                         "palette": [list(c) for c in r.palette]} for r in out], ensure_ascii=False),
            encoding="utf-8",
        )
    return out


def blended_palette(refs: list[Reference], n: int = 4) -> tuple[tuple[int, int, int], ...]:
    """Dominant colours across all references (first palette entries first)."""
    seen: list[tuple[int, int, int]] = []
    for rank in range(n):
        for r in refs:
            if rank < len(r.palette) and r.palette[rank] not in seen:
                seen.append(r.palette[rank])
    return tuple(seen[:n])
