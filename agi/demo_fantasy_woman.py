"""
Demo: Request a short fantasy story clip featuring an attractive (tastefully portrayed) fictional woman.

Notes:
- Conforms to content restrictions: fictional adult character, non-revealing attire, no copyrighted characters, safe for under-18 audiences.
- Uses the Sora 2 model via the OpenAI Videos API.

Usage:
  python agi/demo_fantasy_woman.py --seconds 8 --size 1280x720 --output DATA/sora_fantasy_demo.mp4
"""
from __future__ import annotations

import argparse
from agi.video_requests import create_poll_and_download


PROMPT = (
    "Cinematic fantasy sequence of an entirely fictional adult woman (over 21) in a flowing sapphire gown, "
    "walking gracefully through a moonlit elven forest. Soft volumetric lighting, gentle breeze moving her hair, "
    "tasteful, non-revealing attire; elegant and confident presence. The camera begins with a medium shot and slowly "
    "dollies to a three-quarter shot, subtle parallax through trees, shallow depth of field, bokeh fireflies in the background. "
    "High production value, teal-and-amber color grading, warm highlights, cinematic composition. Not a real person; entirely fictional."
)


def _parse(argv: list[str]):
    p = argparse.ArgumentParser(description="Run Sora 2 demo: elegant fantasy woman scene")
    p.add_argument("--model", default="sora-2", choices=["sora-2", "sora-2-pro"], help="Video model")
    p.add_argument("--size", default="1280x720", help="Resolution, e.g. 1280x720")
    p.add_argument("--seconds", type=int, default=8, help="Length in seconds")
    p.add_argument("--output", default="DATA/sora_fantasy_demo.mp4", help="Output mp4 path")
    return p.parse_args(argv)


def main(argv: list[str]) -> int:
    args = _parse(argv)
    create_poll_and_download(
        prompt=PROMPT,
        model=args.model,
        size=args.size,
        seconds=args.seconds,
        output=args.output,
        poll_interval=10.0,
        timeout_seconds=30 * 60,
    )
    return 0


if __name__ == "__main__":
    import sys
    raise SystemExit(main(sys.argv[1:]))

