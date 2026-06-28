#!/usr/bin/env python3
"""Build a LazyEdit music publish ZIP for AutoPublish/Shipinhao music."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config import AUTOPUBLISH_URL, UPLOAD_FOLDER  # noqa: E402
from lazyedit.music_publish import package_music_publish, post_music_package_to_autopublish  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Package a music/audio publish ZIP through LazyEdit.")
    parser.add_argument("--audio", required=True, help="Song audio file, usually MP3 or WAV.")
    parser.add_argument("--title", required=True, help="Song title.")
    parser.add_argument("--author", default="Musia 慕莎")
    parser.add_argument("--artist")
    parser.add_argument("--language", default="中文")
    parser.add_argument("--genre", default="")
    parser.add_argument("--story", default="", help="Short music story / 音乐人说.")
    parser.add_argument("--description", default="", help="Longer public metadata description.")
    parser.add_argument("--lyrics-file")
    parser.add_argument("--lyrics-json")
    parser.add_argument("--lyrics-text", default="")
    parser.add_argument("--metadata-json", help="Optional metadata JSON override.")
    parser.add_argument("--cover", action="append", default=[], help="Cover candidate image. Can be repeated.")
    parser.add_argument("--cover-video", help="Video used to extract additional cover candidates.")
    parser.add_argument("--cover-count", type=int, default=9)
    parser.add_argument("--output-slug", help="Stable package folder/zip slug.")
    parser.add_argument("--output-root", default=str(Path(UPLOAD_FOLDER) / "music_publish"))
    parser.add_argument("--post", action="store_true", help="Post package to AutoPublish after building.")
    parser.add_argument("--autopublish-url", default=AUTOPUBLISH_URL)
    parser.add_argument("--test", action="store_true")
    args = parser.parse_args(argv)

    result = package_music_publish(
        audio_path=args.audio,
        title=args.title,
        output_root=args.output_root,
        output_slug=args.output_slug,
        cover_paths=args.cover,
        cover_video_path=args.cover_video,
        cover_count=args.cover_count,
        lyrics_file=args.lyrics_file,
        lyrics_json=args.lyrics_json,
        lyrics_text=args.lyrics_text,
        metadata_json=args.metadata_json,
        author=args.author,
        artist=args.artist,
        language=args.language,
        genre=args.genre,
        story=args.story,
        description=args.description,
    )

    if args.post:
        result["autopublish_response"] = post_music_package_to_autopublish(
            result["zip_path"],
            args.autopublish_url,
            test=args.test,
        )

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
