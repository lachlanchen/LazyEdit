#!/usr/bin/env python3
"""Build a direct AutoPublish ZIP from an already approved video/audio package.

This helper is for Musia/LALACHAN recovery paths where the MP4 has already been
inspected and should not be resized, recomposed, or re-encoded by LazyEdit.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import zipfile
from pathlib import Path


def _probe_media(path: Path) -> dict:
    if not shutil.which("ffprobe"):
        return {"path": str(path), "probe": "ffprobe-not-found"}
    command = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration:stream=codec_type,width,height",
        "-of",
        "json",
        str(path),
    ]
    try:
        result = subprocess.run(command, check=True, text=True, capture_output=True)
        return json.loads(result.stdout or "{}")
    except Exception as exc:
        return {"path": str(path), "probe_error": str(exc)}


def _load_metadata(path: Path | None, args: argparse.Namespace) -> dict:
    if path:
        with path.open("r", encoding="utf-8") as handle:
            metadata = json.load(handle)
    else:
        title = args.title or args.stem
        metadata = {
            "title": title,
            "song_title": title,
            "artist": args.artist,
            "brief_description": args.description or title,
            "middle_description": args.description or title,
            "long_description": args.description or title,
            "tags": [tag for tag in args.tag if tag],
            "publish_category": args.publish_category,
        }
    metadata["video_filename"] = f"{args.stem}_highlighted.mp4"
    metadata["cover_filename"] = f"{args.stem}_cover{args.cover.suffix.lower()}"
    return metadata


def build_package(args: argparse.Namespace) -> Path:
    video = args.video.expanduser().resolve()
    cover = args.cover.expanduser().resolve()
    metadata_json = args.metadata_json.expanduser().resolve() if args.metadata_json else None
    if not video.exists():
        raise FileNotFoundError(f"Video not found: {video}")
    if not cover.exists():
        raise FileNotFoundError(f"Cover not found: {cover}")
    if metadata_json and not metadata_json.exists():
        raise FileNotFoundError(f"Metadata JSON not found: {metadata_json}")

    output_dir = args.output_dir.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    video_name = f"{args.stem}_highlighted.mp4"
    cover_name = f"{args.stem}_cover{cover.suffix.lower()}"
    metadata_name = f"{args.stem}_metadata.json"
    zip_name = f"{args.stem}.zip"

    video_out = output_dir / video_name
    cover_out = output_dir / cover_name
    metadata_out = output_dir / metadata_name
    zip_out = output_dir / zip_name

    shutil.copy2(video, video_out)
    shutil.copy2(cover, cover_out)
    metadata = _load_metadata(metadata_json, args)
    metadata_out.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if zip_out.exists():
        zip_out.unlink()
    with zipfile.ZipFile(zip_out, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.write(video_out, arcname=video_name)
        archive.write(cover_out, arcname=cover_name)
        archive.write(metadata_out, arcname=metadata_name)

    print(json.dumps({
        "status": "ok",
        "zip": str(zip_out),
        "video": str(video_out),
        "cover": str(cover_out),
        "metadata": str(metadata_out),
        "media_probe": _probe_media(video_out),
    }, ensure_ascii=False, indent=2))
    return zip_out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--video", type=Path, required=True, help="Approved MP4 to package without reprocessing.")
    parser.add_argument("--cover", type=Path, required=True, help="Cover image to include.")
    parser.add_argument("--metadata-json", type=Path, help="Existing listener-facing metadata JSON.")
    parser.add_argument("--output-dir", type=Path, required=True, help="Directory to write copied assets and ZIP.")
    parser.add_argument("--stem", required=True, help="ZIP/internal filename stem. Must match AutoPublish package contract.")
    parser.add_argument("--title", help="Fallback title when --metadata-json is not supplied.")
    parser.add_argument("--artist", default="Musia", help="Fallback artist when --metadata-json is not supplied.")
    parser.add_argument("--description", help="Fallback listener-facing description.")
    parser.add_argument("--tag", action="append", default=[], help="Fallback tag; repeat for multiple tags.")
    parser.add_argument("--publish-category", default="musia", help="Fallback LazyEdit publish category.")
    args = parser.parse_args()
    build_package(args)


if __name__ == "__main__":
    main()
