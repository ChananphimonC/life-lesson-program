"""CLI entrypoint for v0.1: `python -m life_lesson.cli "<topic text>"`.

Per ROADMAP.md v0.1 ("hardcoded topic input via CLI"), this takes the
specific situation to reflect on directly as text -- no LLM-driven topic
generation yet (that's a later milestone).
"""

from __future__ import annotations

import argparse
import sys

from life_lesson.config import get_settings
from life_lesson.errors import PipelineError
from life_lesson.logging_setup import configure_logging
from life_lesson.pipeline import run_pipeline


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate one life-reflection episode from a topic."
    )
    parser.add_argument(
        "topic",
        help="The specific situation to reflect on, e.g. "
        "'Seeing friends buy houses while you are still renting'.",
    )
    parser.add_argument(
        "--theme", default=None, help="Optional broad theme label for this topic."
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    settings = get_settings()
    configure_logging(settings.log_level)

    try:
        result = run_pipeline(args.topic, args.theme, settings=settings)
    except PipelineError as exc:
        print(f"Pipeline failed before an episode record could be created: {exc}", file=sys.stderr)
        return 1

    print(f"episode_id: {result.episode_id}")
    print(f"state: {result.state}")
    if result.audio_path:
        print(f"audio: {result.audio_path}")
    if result.video_path:
        print(f"video: {result.video_path}")
    if result.error_message:
        print(f"error: {result.error_message}", file=sys.stderr)

    return 0 if result.state == "DONE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
