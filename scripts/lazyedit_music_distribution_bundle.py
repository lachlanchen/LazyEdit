#!/usr/bin/env python3
"""Export a music release bundle for Bandcamp or distributor upload.

This does not post to third-party platforms. It repackages an existing
LazyEdit music publish folder into a clean release folder with audio, cover,
lyrics, JSON/CSV metadata, and platform notes.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config import UPLOAD_FOLDER  # noqa: E402


def _safe_slug(value: str, fallback: str = "music-release") -> str:
    import re

    text = (value or "").strip()
    text = re.sub(r"[^\w\u4e00-\u9fff\u3040-\u30ff.-]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-.")
    return text[:120] or fallback


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _copy(src: Path, dst_dir: Path, name: str | None = None) -> Path:
    dst_dir.mkdir(parents=True, exist_ok=True)
    dst = dst_dir / (name or src.name)
    shutil.copy2(src, dst)
    return dst


def _make_wav(src: Path, dst: Path) -> bool:
    dst.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(src),
            "-vn",
            "-ac",
            "2",
            "-ar",
            "44100",
            "-sample_fmt",
            "s16",
            str(dst),
        ],
        check=False,
        capture_output=True,
        text=True,
        timeout=240,
    )
    return result.returncode == 0 and dst.exists() and dst.stat().st_size > 0


def _write_metadata_csv(path: Path, metadata: dict) -> None:
    fields = [
        "title",
        "artist",
        "author",
        "singer",
        "lyricist",
        "composer",
        "producer",
        "language",
        "genre",
        "brief_description",
        "long_description",
        "tags",
        "source_url",
        "copyright_line",
        "release_date",
        "explicit",
        "isrc",
        "upc",
    ]
    row = {}
    for field in fields:
        value = metadata.get(field, "")
        if isinstance(value, list):
            value = ", ".join(str(item) for item in value)
        row[field] = value
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerow(row)


def _platform_notes(metadata: dict, *, audio_name: str, wav_name: str | None, cover_name: str | None) -> str:
    title = metadata.get("title") or metadata.get("song_title") or ""
    artist = metadata.get("artist") or metadata.get("author") or ""
    lyrics = metadata.get("plain_lyrics") or metadata.get("lyrics") or ""
    tags = metadata.get("tags") or []
    if isinstance(tags, list):
        tags_text = ", ".join(str(item) for item in tags)
    else:
        tags_text = str(tags)
    return f"""# Music Release Upload Notes

## Release

- Title: {title}
- Artist: {artist}
- Language: {metadata.get("language", "")}
- Genre: {metadata.get("genre", "")}
- Explicit: {metadata.get("explicit", "no")}
- Source URL: {metadata.get("source_url", "")}
- Tags: {tags_text}

## Assets

- Primary audio: `audio/{audio_name}`
- Distributor WAV: `{f"audio/{wav_name}" if wav_name else "not generated"}`
- Cover: `{f"cover/{cover_name}" if cover_name else "not included"}`
- Lyrics: `lyrics/lyrics.txt`
- Metadata JSON: `metadata/release.json`
- Metadata CSV: `metadata/release.csv`

## Bandcamp

Use the WAV if present. Paste the short description and corrected lyrics from
this bundle. Bandcamp is useful for direct fan sales and does not replace
distribution to Spotify/Apple/YouTube Music.

## Distributor Upload

Use the WAV/lossless master where possible, square cover, release metadata CSV,
and corrected lyrics. If the source audio was only MP3, treat the generated WAV
as a compatibility derivative, not a true lossless master. Prefer exporting a
real WAV/FLAC master from Musia for paid DSP distribution.

## SoundCloud

Use the original MP3 or WAV and paste the same title, artist, description, and
tags. SoundCloud monetization/distribution requires the account/subscription
workflow; this bundle is only the upload package.

## Corrected Lyrics

```text
{lyrics}
```
"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Create Bandcamp/distributor bundle from a LazyEdit music package.")
    parser.add_argument("--package-dir", required=True, help="LazyEdit DATA/music_publish/<slug> folder.")
    parser.add_argument("--source-url", default="", help="Optional public song URL.")
    parser.add_argument("--output-root", default=str(Path(UPLOAD_FOLDER) / "music_distribution"))
    parser.add_argument("--output-slug")
    parser.add_argument("--make-wav", action=argparse.BooleanOptionalAction, default=True)
    args = parser.parse_args(argv)

    package_dir = Path(args.package_dir).expanduser().resolve()
    if not package_dir.exists():
        raise FileNotFoundError(package_dir)

    metadata_files = sorted(package_dir.glob("*_metadata.json"))
    manifest_files = sorted(package_dir.glob("*_manifest.json"))
    if not metadata_files or not manifest_files:
        raise FileNotFoundError("Expected *_metadata.json and *_manifest.json in package dir")
    metadata = _read_json(metadata_files[0])
    manifest = _read_json(manifest_files[0])
    if args.source_url:
        metadata["source_url"] = args.source_url

    slug = _safe_slug(args.output_slug or package_dir.name, fallback=package_dir.name)
    out_dir = Path(args.output_root).expanduser().resolve() / slug
    audio_dir = out_dir / "audio"
    cover_dir = out_dir / "cover"
    lyrics_dir = out_dir / "lyrics"
    metadata_dir = out_dir / "metadata"
    out_dir.mkdir(parents=True, exist_ok=True)

    audio_name = manifest.get("audio") or metadata.get("audio_filename") or metadata.get("music_filename")
    if not audio_name:
        raise FileNotFoundError("No audio filename in manifest/metadata")
    source_audio = package_dir / audio_name
    if not source_audio.exists():
        raise FileNotFoundError(source_audio)
    copied_audio = _copy(source_audio, audio_dir)

    wav_name = None
    wav_path = audio_dir / f"{slug}_distribution_44k16.wav"
    if args.make_wav:
        if _make_wav(copied_audio, wav_path):
            wav_name = wav_path.name

    cover_name = None
    cover_value = metadata.get("cover_filename") or (metadata.get("cover_filenames") or [None])[0]
    if cover_value:
        source_cover = package_dir / str(cover_value)
        if source_cover.exists():
            copied_cover = _copy(source_cover, cover_dir)
            cover_name = copied_cover.name

    lyrics_text = metadata.get("plain_lyrics") or metadata.get("lyrics") or ""
    lyrics_dir.mkdir(parents=True, exist_ok=True)
    (lyrics_dir / "lyrics.txt").write_text(lyrics_text.strip() + "\n", encoding="utf-8")

    metadata_dir.mkdir(parents=True, exist_ok=True)
    release_json = {
        "bundle_type": "lazyedit_music_distribution",
        "created_at": int(time.time()),
        "metadata": metadata,
        "source_package": str(package_dir),
        "assets": {
            "audio": f"audio/{copied_audio.name}",
            "wav": f"audio/{wav_name}" if wav_name else None,
            "cover": f"cover/{cover_name}" if cover_name else None,
            "lyrics": "lyrics/lyrics.txt",
        },
    }
    (metadata_dir / "release.json").write_text(json.dumps(release_json, ensure_ascii=False, indent=2), encoding="utf-8")
    _write_metadata_csv(metadata_dir / "release.csv", metadata)
    (out_dir / "UPLOAD_NOTES.md").write_text(
        _platform_notes(metadata, audio_name=copied_audio.name, wav_name=wav_name, cover_name=cover_name),
        encoding="utf-8",
    )

    print(json.dumps({
        "status": "ready",
        "bundle_dir": str(out_dir),
        "audio": str(copied_audio),
        "wav": str(wav_path) if wav_name else None,
        "cover": str(cover_dir / cover_name) if cover_name else None,
        "lyrics": str(lyrics_dir / "lyrics.txt"),
        "metadata_json": str(metadata_dir / "release.json"),
        "metadata_csv": str(metadata_dir / "release.csv"),
        "notes": str(out_dir / "UPLOAD_NOTES.md"),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
