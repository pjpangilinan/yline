"""CLI entry point for YLine lyric video pipeline."""
from __future__ import annotations

import argparse
import asyncio
import logging
import sys

from dotenv import load_dotenv


def main() -> None:
    """Main CLI entry point."""
    load_dotenv()

    parser = argparse.ArgumentParser(
        prog="yline",
        description="Generate synced lyric videos from a song name",
    )
    parser.add_argument(
        "query",
        type=str,
        help='Song to generate video for (e.g., "Choosin\' Texas by Ella Langley")',
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="Custom output path for the video file",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging",
    )

    parser.add_argument(
        "--test",
        action="store_true",
        help="Run in E2E test mode (truncates processing to 15 seconds)",
    )

    args = parser.parse_args()

    # Configure logging
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    # Run the pipeline
    from yline.graph import run_pipeline

    result = asyncio.run(run_pipeline(args.query, test_mode=args.test))

    # Report results
    if result.get("video_path"):
        print(f"\n[OK] Video created: {result['video_path']}")
    else:
        print("\n[FAIL] Pipeline failed:")
        for err in result.get("errors", []):
            print(f"  - {err}")
        sys.exit(1)

    if result.get("errors"):
        print("\n[WARN] Warnings:")
        for err in result["errors"]:
            print(f"  - {err}")


if __name__ == "__main__":
    main()
