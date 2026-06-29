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
from lazyedit import db as ldb  # noqa: E402
from lazyedit.music_publish import package_music_publish, post_music_package_to_autopublish  # noqa: E402


def _remote_job_id(response: dict | None) -> str | None:
    if not isinstance(response, dict):
        return None
    for key in ("job_id", "id", "remote_job_id"):
        value = response.get(key)
        if value:
            return str(value)
    job = response.get("job")
    if isinstance(job, dict):
        value = job.get("id") or job.get("job_id")
        if value:
            return str(value)
    return None


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
    parser.add_argument("--cover-model", default="", help="Cover generation model note, e.g. aginti/codex/venice.")
    parser.add_argument("--aginti-cover-count", type=int, default=0)
    parser.add_argument("--codex-cover-count", type=int, default=0)
    parser.add_argument("--proof", action="append", default=[], help="Original-proof file. Can be repeated.")
    parser.add_argument("--website-screenshot", help="Screenshot of the public Musia/Fun Lazying Art song page.")
    parser.add_argument("--webapp-screenshot", help="Screenshot of the Musia webapp generation/session context.")
    parser.add_argument("--output-slug", help="Stable package folder/zip slug.")
    parser.add_argument("--output-root", default=str(Path(UPLOAD_FOLDER) / "music_publish"))
    parser.add_argument("--post", action="store_true", help="Post package to AutoPublish after building.")
    parser.add_argument("--platforms", default="shipinhao_music", help="Comma-separated music platforms: shipinhao_music,youtube_music.")
    parser.add_argument("--shipinhao-music", action="store_true", help="Publish to Shipinhao music when --post is used.")
    parser.add_argument("--youtube-music", action="store_true", help="Publish to YouTube as an art-track music video when --post is used.")
    parser.add_argument("--autopublish-url", default=AUTOPUBLISH_URL)
    parser.add_argument("--test", action="store_true")
    parser.add_argument("--source-url", default="", help="Public source URL for tracking, e.g. Fun Lazying Art item URL.")
    parser.add_argument("--no-record", action="store_true", help="Do not insert a LazyEdit music_publish_items row.")
    args = parser.parse_args(argv)

    result = package_music_publish(
        audio_path=args.audio,
        title=args.title,
        output_root=args.output_root,
        output_slug=args.output_slug,
        cover_paths=args.cover,
        cover_video_path=args.cover_video,
        cover_count=args.cover_count,
        cover_model=args.cover_model,
        aginti_cover_count=args.aginti_cover_count,
        codex_cover_count=args.codex_cover_count,
        proof_paths=args.proof,
        website_screenshot_path=args.website_screenshot,
        webapp_screenshot_path=args.webapp_screenshot,
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

    item_id = None
    if not args.no_record:
        try:
            item_id = ldb.add_music_publish_item(
                slug=Path(result["package_dir"]).name,
                title=args.title,
                artist=args.artist or args.author,
                language_code=args.language,
                status="packaged",
                audio_path=result.get("audio_path"),
                zip_path=result.get("zip_path"),
                metadata_path=result.get("metadata_path"),
                manifest_path=result.get("manifest_path"),
                cover_paths=result.get("cover_paths") or [],
                proof_paths=(result.get("proof_paths") or []) + ([result["proof_zip_path"]] if result.get("proof_zip_path") else []),
                source_url=args.source_url,
                metadata=result.get("metadata") or {},
            )
            result["music_publish_item_id"] = item_id
        except Exception as exc:
            result["record_error"] = str(exc)

    if args.post:
        requested_platforms = {
            item.strip().lower()
            for item in (args.platforms or "").split(",")
            if item.strip()
        }
        publish_shipinhao_music = args.shipinhao_music or "shipinhao_music" in requested_platforms or "sph" in requested_platforms
        publish_youtube_music = args.youtube_music or "youtube_music" in requested_platforms or "youtube" in requested_platforms or "y2b" in requested_platforms
        if not publish_shipinhao_music and not publish_youtube_music:
            publish_shipinhao_music = True
        try:
            result["autopublish_response"] = post_music_package_to_autopublish(
                result["zip_path"],
                args.autopublish_url,
                publish_shipinhao_music=publish_shipinhao_music,
                publish_youtube_music=publish_youtube_music,
                test=args.test,
            )
            if item_id:
                response = result.get("autopublish_response")
                ldb.update_music_publish_item(
                    item_id,
                    status="queued",
                    remote_job_id=_remote_job_id(response),
                    remote_filename=Path(result["zip_path"]).name,
                    remote_status="queued",
                    autopublish_response=response if isinstance(response, dict) else {"raw": response},
                )
        except Exception as exc:
            result["autopublish_response"] = {"error": str(exc)}
            if item_id:
                ldb.update_music_publish_item(item_id, status="failed", error=str(exc))

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
