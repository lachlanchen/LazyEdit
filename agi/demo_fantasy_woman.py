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
try:
    from agi.video_requests import create_poll_and_download
except ModuleNotFoundError:
    # Allow execution via `python agi/demo_fantasy_woman.py` by adding repo root
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).resolve().parents[1]))
    from agi.video_requests import create_poll_and_download


PROMPT = (
    "A fictional adult woman known as the Oracle of the Mist Valley stands on a wind-swept cliff at dawn. "
    "Her silver robe glows faintly under the rising sun as mist drifts through crystalline forests below. "
    "She closes her eyes, sensing faint tremors in the air — echoes of a future she alone can hear. "
    "The camera glides slowly around her, revealing vast floating isles beyond the valley and the glint of ancient ruins half-buried in the fog. "
    "The mood is serene, mysterious, and filled with quiet purpose — a world poised on the edge of awakening. "
    "Not a real person; entirely fictional and fully clothed in tasteful, non-revealing attire."
)


def _parse(argv: list[str]):
    p = argparse.ArgumentParser(description="Run Sora 2 demo: elegant fantasy woman scene")
    p.add_argument("--model", default="sora-2", choices=["sora-2", "sora-2-pro"], help="Video model")
    p.add_argument("--prompt", default=PROMPT, help="Override the default story prompt")
    p.add_argument("--size", default="1280x720", help="Resolution, e.g. 1280x720")
    p.add_argument("--seconds", type=int, default=8, help="Length in seconds")
    p.add_argument("--output", default="DATA/sora_fantasy_demo.mp4", help="Output mp4 path")
    return p.parse_args(argv)


def main(argv: list[str]) -> int:
    args = _parse(argv)
    create_poll_and_download(
        prompt=args.prompt or PROMPT,
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
