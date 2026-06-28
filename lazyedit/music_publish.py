from __future__ import annotations

import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import time
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import zipfile


DEFAULT_AUTHOR = "Musia 慕莎"
DEFAULT_LANGUAGE = "中文"


def _safe_slug(value: str, *, fallback: str = "music") -> str:
    text = (value or "").strip()
    text = re.sub(r"[^\w\u4e00-\u9fff\u3040-\u30ff.-]+", "-", text, flags=re.UNICODE)
    text = re.sub(r"-+", "-", text).strip("-.")
    return text[:120] or fallback


def _safe_arcname(path: Path) -> str:
    return path.name.replace("/", "_").replace("\\", "_")


def _read_text(path: str | Path | None) -> str:
    if not path:
        return ""
    return Path(path).expanduser().resolve().read_text(encoding="utf-8", errors="ignore").strip()


def lyrics_from_json(path: str | Path | None) -> str:
    if not path:
        return ""
    payload = json.loads(Path(path).expanduser().resolve().read_text(encoding="utf-8"))
    lines = payload.get("lines") if isinstance(payload, dict) else None
    if not isinstance(lines, list):
        return ""
    output: list[str] = []
    for line in lines:
        if not isinstance(line, dict):
            continue
        text = str(line.get("singableText") or line.get("text") or "").strip()
        if text:
            output.append(text)
    return "\n".join(output)


def _ffprobe_duration(path: Path) -> float | None:
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )
    if result.returncode != 0:
        return None
    try:
        return float((result.stdout or "").strip())
    except ValueError:
        return None


def _extract_cover_frames(video_path: Path, output_dir: Path, *, count: int, prefix: str) -> list[Path]:
    if count <= 0:
        return []
    duration = _ffprobe_duration(video_path) or 0
    if duration <= 0:
        raise RuntimeError(f"Could not determine duration for cover extraction: {video_path}")
    output_dir.mkdir(parents=True, exist_ok=True)
    start = min(1.0, max(0.0, duration * 0.05))
    end = max(start, duration * 0.95)
    if count == 1:
        timestamps = [(start + end) / 2]
    else:
        timestamps = [start + (end - start) * index / (count - 1) for index in range(count)]
    covers: list[Path] = []
    for index, timestamp in enumerate(timestamps, start=1):
        target = output_dir / f"{prefix}_auto_cover_{index:02d}.jpg"
        result = subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-ss",
                f"{timestamp:.3f}",
                "-i",
                str(video_path),
                "-frames:v",
                "1",
                "-vf",
                "scale=1440:-2",
                "-q:v",
                "3",
                str(target),
            ],
            check=False,
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode != 0 or not target.exists():
            raise RuntimeError((result.stderr or result.stdout or "ffmpeg cover extraction failed").strip())
        covers.append(target)
    return covers


def build_music_metadata(
    *,
    audio_name: str,
    cover_names: list[str],
    title: str,
    author: str = DEFAULT_AUTHOR,
    artist: str | None = None,
    language: str = DEFAULT_LANGUAGE,
    genre: str = "",
    lyrics: str = "",
    story: str = "",
    description: str = "",
    metadata_override: dict | None = None,
) -> dict:
    story_text = story or description or ""
    metadata = {
        "package_type": "shipinhao_music",
        "music_filename": audio_name,
        "audio_filename": audio_name,
        "cover_filename": cover_names[0] if cover_names else None,
        "cover_filenames": cover_names,
        "background_image_filenames": cover_names,
        "title": title,
        "song_title": title,
        "lyrics": lyrics,
        "song_lyrics": lyrics,
        "music_story": story_text,
        "brief_description": description or story_text,
        "middle_description": story_text,
        "long_description": description or story_text,
        "author": author,
        "artist": artist or author,
        "language": language,
        "genre": genre,
        "declare_original": False,
    }
    if metadata_override:
        metadata.update({key: value for key, value in metadata_override.items() if value is not None})
    return metadata


def package_music_publish(
    *,
    audio_path: str | Path,
    title: str | None = None,
    output_root: str | Path,
    output_slug: str | None = None,
    cover_paths: list[str | Path] | None = None,
    cover_video_path: str | Path | None = None,
    cover_count: int = 9,
    lyrics_file: str | Path | None = None,
    lyrics_json: str | Path | None = None,
    lyrics_text: str = "",
    metadata_json: str | Path | None = None,
    author: str = DEFAULT_AUTHOR,
    artist: str | None = None,
    language: str = DEFAULT_LANGUAGE,
    genre: str = "",
    story: str = "",
    description: str = "",
) -> dict:
    audio = Path(audio_path).expanduser().resolve()
    if not audio.exists():
        raise FileNotFoundError(audio)

    package_title = (title or audio.stem).strip()
    slug = _safe_slug(output_slug or package_title or audio.stem, fallback=audio.stem)
    package_dir = Path(output_root).expanduser().resolve() / slug
    covers_dir = package_dir / "covers"
    package_dir.mkdir(parents=True, exist_ok=True)
    covers_dir.mkdir(parents=True, exist_ok=True)

    copied_audio = package_dir / _safe_arcname(audio)
    if copied_audio != audio:
        shutil.copy2(audio, copied_audio)

    resolved_covers: list[Path] = []
    for cover in cover_paths or []:
        cover_path = Path(cover).expanduser().resolve()
        if not cover_path.exists():
            raise FileNotFoundError(cover_path)
        target = covers_dir / _safe_arcname(cover_path)
        if target != cover_path:
            shutil.copy2(cover_path, target)
        resolved_covers.append(target)

    missing_count = max(0, int(cover_count) - len(resolved_covers))
    if missing_count and cover_video_path:
        extracted = _extract_cover_frames(
            Path(cover_video_path).expanduser().resolve(),
            covers_dir,
            count=missing_count,
            prefix=slug,
        )
        resolved_covers.extend(extracted)
    resolved_covers = resolved_covers[: max(1, int(cover_count))]

    lyrics = lyrics_text.strip() or _read_text(lyrics_file) or lyrics_from_json(lyrics_json)
    metadata_override = None
    if metadata_json:
        metadata_override = json.loads(Path(metadata_json).expanduser().resolve().read_text(encoding="utf-8"))
        if not isinstance(metadata_override, dict):
            metadata_override = None

    cover_names = [f"covers/{cover.name}" for cover in resolved_covers]
    metadata = build_music_metadata(
        audio_name=copied_audio.name,
        cover_names=cover_names,
        title=package_title,
        author=author,
        artist=artist,
        language=language,
        genre=genre,
        lyrics=lyrics,
        story=story,
        description=description,
        metadata_override=metadata_override,
    )

    metadata_name = f"{slug}_metadata.json"
    metadata_path = package_dir / metadata_name
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    lyrics_path = package_dir / f"{slug}_lyrics.txt"
    lyrics_path.write_text(lyrics, encoding="utf-8")
    manifest_path = package_dir / f"{slug}_manifest.json"
    manifest = {
        "package_type": "lazyedit_music_publish",
        "created_at": int(time.time()),
        "title": package_title,
        "audio": copied_audio.name,
        "metadata": metadata_name,
        "lyrics": lyrics_path.name,
        "covers": cover_names,
        "cover_count": len(cover_names),
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    zip_path = package_dir / f"{slug}.zip"
    with zipfile.ZipFile(zip_path, "w") as zipf:
        zipf.write(copied_audio, arcname=copied_audio.name)
        zipf.write(metadata_path, arcname=metadata_name)
        zipf.write(lyrics_path, arcname=lyrics_path.name)
        zipf.write(manifest_path, arcname=manifest_path.name)
        for cover in resolved_covers:
            zipf.write(cover, arcname=f"covers/{cover.name}")

    return {
        "status": "ready",
        "package_dir": str(package_dir),
        "zip_path": str(zip_path),
        "metadata_path": str(metadata_path),
        "lyrics_path": str(lyrics_path),
        "manifest_path": str(manifest_path),
        "audio_path": str(copied_audio),
        "cover_paths": [str(path) for path in resolved_covers],
        "cover_count": len(resolved_covers),
        "metadata": metadata,
    }


def post_music_package_to_autopublish(
    zip_path: str | Path,
    autopublish_url: str,
    *,
    test: bool = False,
    timeout: int = 120,
) -> dict:
    zip_file = Path(zip_path).expanduser().resolve()
    params = {
        'filename': zip_file.name,
        'publish_shipinhao_music': 'true',
        'test': str(bool(test)).lower(),
    }
    endpoint = f"{autopublish_url}?{urlencode(params)}"
    request = Request(
        endpoint,
        data=zip_file.read_bytes(),
        method="POST",
        headers={"Content-Type": "application/octet-stream"},
    )
    with urlopen(request, timeout=timeout) as response:
        raw = response.read().decode("utf-8", errors="replace")
    try:
        return json.loads(raw or "{}")
    except json.JSONDecodeError:
        return {"raw": raw}
