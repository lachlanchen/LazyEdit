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


def _unique_child_path(directory: Path, filename: str) -> Path:
    target = directory / filename
    if not target.exists():
        return target
    stem = target.stem
    suffix = target.suffix
    for index in range(2, 1000):
        candidate = directory / f"{stem}-{index}{suffix}"
        if not candidate.exists():
            return candidate
    raise RuntimeError(f"Could not create a unique filename for {filename}")


def _read_text(path: str | Path | None) -> str:
    if not path:
        return ""
    return Path(path).expanduser().resolve().read_text(encoding="utf-8", errors="ignore").strip()


def _format_lrc_timestamp(seconds: object) -> str | None:
    try:
        value = float(seconds)
    except (TypeError, ValueError):
        return None
    if value < 0:
        value = 0.0
    minutes = int(value // 60)
    remainder = value - minutes * 60
    return f"{minutes:02d}:{remainder:05.2f}"


def _strip_lrc_timestamps(text: str) -> str:
    output: list[str] = []
    for line in (text or "").splitlines():
        stripped = re.sub(r"^\s*(?:\[[0-9]{1,3}:[0-9]{2}(?:\.[0-9]{1,3})?\])+\s*", "", line).strip()
        if stripped:
            output.append(stripped)
    return "\n".join(output)


def _looks_like_lrc(text: str) -> bool:
    return bool(re.search(r"^\s*\[[0-9]{1,3}:[0-9]{2}(?:\.[0-9]{1,3})?\]", text or "", re.MULTILINE))


def lyrics_from_json(path: str | Path | None, *, lyrics_format: str = "plain") -> str:
    if not path:
        return ""
    if lyrics_format not in {"plain", "lrc", "auto"}:
        raise ValueError("lyrics_format must be 'plain', 'lrc', or 'auto'")
    payload = json.loads(Path(path).expanduser().resolve().read_text(encoding="utf-8"))
    lines = payload.get("lines") if isinstance(payload, dict) else None
    if not isinstance(lines, list):
        return ""
    use_lrc = lyrics_format == "lrc" or (
        lyrics_format == "auto"
        and any(isinstance(line, dict) and line.get("start") is not None for line in lines)
    )
    output: list[str] = []
    for line in lines:
        if not isinstance(line, dict):
            continue
        text = str(line.get("singableText") or line.get("text") or "").strip()
        if not text:
            continue
        if use_lrc:
            timestamp = _format_lrc_timestamp(line.get("start"))
            if timestamp:
                output.append(f"[{timestamp}]{text}")
                continue
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


def _ffprobe_audio_bitrate(path: Path) -> int | None:
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "a:0",
            "-show_entries",
            "stream=bit_rate",
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
        return int(float((result.stdout or "").strip()))
    except ValueError:
        return None


def _prepare_shipinhao_audio(source: Path, package_dir: Path) -> Path:
    """Return a package-local audio file that satisfies Shipinhao's bitrate rule."""
    suffix = source.suffix.lower()
    bitrate = _ffprobe_audio_bitrate(source)
    needs_transcode = suffix == ".mp3" and (bitrate is None or bitrate < 256_000)
    if not needs_transcode:
        target = package_dir / _safe_arcname(source)
        if target != source:
            shutil.copy2(source, target)
        return target

    target = package_dir / f"{_safe_slug(source.stem, fallback='song')}_shipinhao_320k.mp3"
    result = subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(source),
            "-vn",
            "-ac",
            "2",
            "-ar",
            "44100",
            "-codec:a",
            "libmp3lame",
            "-b:a",
            "320k",
            str(target),
        ],
        check=False,
        capture_output=True,
        text=True,
        timeout=180,
    )
    if result.returncode != 0 or not target.exists():
        raise RuntimeError((result.stderr or result.stdout or "ffmpeg audio transcode failed").strip())
    return target


def _render_youtube_music_video(audio: Path, cover: Path | None, package_dir: Path, *, slug: str) -> Path:
    """Render an art-track MP4 for YouTube from one audio file and optional cover art."""
    target = package_dir / f"{slug}_youtube_music.mp4"
    duration = _ffprobe_duration(audio)
    if duration is None or duration <= 0:
        duration = 3600.0

    if cover and cover.exists():
        command = [
            "ffmpeg",
            "-y",
            "-loop",
            "1",
            "-i",
            str(cover),
            "-i",
            str(audio),
            "-t",
            f"{duration:.3f}",
            "-vf",
            "scale=1920:1080:force_original_aspect_ratio=decrease,"
            "pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=0x111827,setsar=1",
            "-r",
            "30",
            "-c:v",
            "libx264",
            "-tune",
            "stillimage",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-shortest",
            "-movflags",
            "+faststart",
            str(target),
        ]
    else:
        command = [
            "ffmpeg",
            "-y",
            "-f",
            "lavfi",
            "-i",
            "color=c=0x111827:s=1920x1080:r=30",
            "-i",
            str(audio),
            "-t",
            f"{duration:.3f}",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-shortest",
            "-movflags",
            "+faststart",
            str(target),
        ]

    result = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
        timeout=max(180, min(1800, int(duration * 4) + 120)),
    )
    if result.returncode != 0 or not target.exists():
        raise RuntimeError((result.stderr or result.stdout or "ffmpeg YouTube music video render failed").strip())
    return target


def _square_cover_image(source: Path, output_dir: Path, *, prefix: str, index: int) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    target = output_dir / f"{prefix}_cover_{index:02d}_square.jpg"
    result = subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(source),
            "-frames:v",
            "1",
            "-vf",
            "scale=1440:1440:force_original_aspect_ratio=increase,crop=1440:1440,setsar=1",
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
        raise RuntimeError((result.stderr or result.stdout or "ffmpeg square cover conversion failed").strip())
    return target


def _extract_cover_frames(
    video_path: Path,
    output_dir: Path,
    *,
    count: int,
    prefix: str,
    cover_shape: str = "square",
) -> list[Path]:
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
        vf = "scale=1440:-2"
        if cover_shape == "square":
            vf = "scale=1440:1440:force_original_aspect_ratio=increase,crop=1440:1440,setsar=1"
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
                vf,
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


def _copy_proof_file(source: str | Path, proof_dir: Path, *, name_hint: str | None = None) -> Path:
    path = Path(source).expanduser().resolve()
    if not path.exists():
        raise FileNotFoundError(path)
    suffix = path.suffix or ".bin"
    filename = f"{name_hint}{suffix}" if name_hint else _safe_arcname(path)
    target = _unique_child_path(proof_dir, filename)
    shutil.copy2(path, target)
    return target


def build_music_metadata(
    *,
    audio_name: str,
    youtube_video_name: str | None = None,
    cover_names: list[str],
    proof_names: list[str] | None = None,
    proof_zip_name: str | None = None,
    website_screenshot_name: str | None = None,
    webapp_screenshot_name: str | None = None,
    title: str,
    author: str = DEFAULT_AUTHOR,
    artist: str | None = None,
    language: str = DEFAULT_LANGUAGE,
    genre: str = "",
    lyrics: str = "",
    plain_lyrics: str = "",
    story: str = "",
    description: str = "",
    cover_model: str = "",
    aginti_cover_count: int = 0,
    codex_cover_count: int = 0,
    metadata_override: dict | None = None,
) -> dict:
    story_text = story or description or ""
    readable_lyrics = plain_lyrics.strip() or _strip_lrc_timestamps(lyrics)
    lrc_lyrics = lyrics.strip() if _looks_like_lrc(lyrics) else ""
    tags = [
        value
        for value in [
            "Musia",
            "LazyingArt",
            "AI music",
            title,
            genre,
            language,
        ]
        if value
    ]
    metadata = {
        "package_type": "music_publish",
        "music_filename": audio_name,
        "audio_filename": audio_name,
        "youtube_music_video_filename": youtube_video_name,
        "video_filename": youtube_video_name,
        "cover_filename": cover_names[0] if cover_names else None,
        "cover_filenames": cover_names,
        "background_image_filenames": cover_names,
        "proof_filenames": proof_names or [],
        "original_proof_filename": proof_zip_name,
        "proof_zip_filename": proof_zip_name,
        "website_screenshot_filename": website_screenshot_name,
        "webapp_screenshot_filename": webapp_screenshot_name,
        "title": title,
        "song_title": title,
        "lyrics": lyrics,
        "song_lyrics": lyrics,
        "lrc_lyrics": lrc_lyrics,
        "timed_lyrics": lrc_lyrics,
        "plain_lyrics": readable_lyrics,
        "readable_lyrics": readable_lyrics,
        "music_story": story_text,
        "brief_description": description or story_text,
        "middle_description": story_text,
        "long_description": description or story_text,
        "tags": tags,
        "author": author,
        "artist": artist or author,
        "singer": artist or author,
        "lyricist": author,
        "composer": author,
        "producer": author,
        "language": language,
        "genre": genre,
        "publish_category": "musia",
        "youtube_playlist": "Musia",
        "shipinhao_collection": "Musia",
        "cover_generation": {
            "model": cover_model,
            "aginti_count": aginti_cover_count,
            "codex_count": codex_cover_count,
            "total_count": len(cover_names),
        },
        "declare_original": False,
    }
    metadata["english_version"] = {
        "title": title,
        "long_description": description or story_text,
        "brief_description": description or story_text,
        "middle_description": story_text,
        "tags": tags,
        "publish_category": "musia",
        "youtube_playlist": "Musia",
        "shipinhao_collection": "Musia",
    }
    if metadata_override:
        metadata.update({key: value for key, value in metadata_override.items() if value is not None})
    return metadata


def package_music_publish(
    *,
    audio_path: str | Path,
    bandcamp_audio_path: str | Path | None = None,
    title: str | None = None,
    output_root: str | Path,
    output_slug: str | None = None,
    cover_paths: list[str | Path] | None = None,
    cover_video_path: str | Path | None = None,
    cover_count: int = 9,
    cover_shape: str = "square",
    cover_model: str = "",
    aginti_cover_count: int = 0,
    codex_cover_count: int = 0,
    proof_paths: list[str | Path] | None = None,
    website_screenshot_path: str | Path | None = None,
    webapp_screenshot_path: str | Path | None = None,
    lyrics_file: str | Path | None = None,
    lyrics_json: str | Path | None = None,
    lyrics_format: str = "plain",
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
    proof_dir = package_dir / "proof"
    package_dir.mkdir(parents=True, exist_ok=True)

    # These subdirectories are generated from the current package inputs. Reset
    # them so repeated builds of the same output slug stay deterministic instead
    # of accumulating website-screenshot-2.png / proof-3.json style leftovers.
    for generated_dir in (covers_dir, proof_dir):
        if generated_dir.exists():
            shutil.rmtree(generated_dir)
    covers_dir.mkdir(parents=True, exist_ok=True)
    if cover_shape not in {"square", "original"}:
        raise ValueError("cover_shape must be 'square' or 'original'")

    copied_audio = _prepare_shipinhao_audio(audio, package_dir)
    bandcamp_audio: Path | None = None
    if bandcamp_audio_path:
        candidate = Path(bandcamp_audio_path).expanduser().resolve()
        if not candidate.exists():
            raise FileNotFoundError(candidate)
        if candidate.suffix.lower() not in {".wav", ".aif", ".aiff", ".flac"}:
            raise ValueError("Bandcamp audio must be a real WAV, AIFF, or FLAC master.")
        target = package_dir / _safe_arcname(candidate)
        if target != candidate:
            shutil.copy2(candidate, target)
        bandcamp_audio = target
    elif copied_audio.suffix.lower() in {".wav", ".aif", ".aiff", ".flac"}:
        bandcamp_audio = copied_audio

    resolved_covers: list[Path] = []
    for cover_index, cover in enumerate(cover_paths or [], start=1):
        cover_path = Path(cover).expanduser().resolve()
        if not cover_path.exists():
            raise FileNotFoundError(cover_path)
        if cover_shape == "square":
            target = _square_cover_image(cover_path, covers_dir, prefix=slug, index=cover_index)
        else:
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
            cover_shape=cover_shape,
        )
        resolved_covers.extend(extracted)
    resolved_covers = resolved_covers[: max(1, int(cover_count))]
    youtube_video = _render_youtube_music_video(
        copied_audio,
        resolved_covers[0] if resolved_covers else None,
        package_dir,
        slug=slug,
    )

    resolved_proofs: list[Path] = []
    website_screenshot: Path | None = None
    webapp_screenshot: Path | None = None
    if website_screenshot_path or webapp_screenshot_path or proof_paths:
        proof_dir.mkdir(parents=True, exist_ok=True)
    if website_screenshot_path:
        website_screenshot = _copy_proof_file(
            website_screenshot_path,
            proof_dir,
            name_hint="website-screenshot",
        )
        resolved_proofs.append(website_screenshot)
    if webapp_screenshot_path:
        webapp_screenshot = _copy_proof_file(
            webapp_screenshot_path,
            proof_dir,
            name_hint="webapp-screenshot",
        )
        resolved_proofs.append(webapp_screenshot)
    for proof in proof_paths or []:
        copied = _copy_proof_file(proof, proof_dir)
        if copied not in resolved_proofs:
            resolved_proofs.append(copied)

    proof_readme_path: Path | None = None
    proof_zip_path: Path | None = None
    if resolved_proofs:
        proof_readme_path = proof_dir / "README.txt"
        proof_readme_path.write_text(
            "\n".join(
                [
                    "Original proof / 原创证明",
                    "",
                    f"Song title: {package_title}",
                    f"Author: {author}",
                    f"Artist: {artist or author}",
                    "This package contains screenshots and source artifacts showing",
                    "that the song belongs to the Musia / LazyingArt workflow.",
                ]
            ),
            encoding="utf-8",
        )
        proof_zip_path = proof_dir / f"{slug}_original_proof.zip"
        with zipfile.ZipFile(proof_zip_path, "w") as proof_zip:
            proof_zip.write(proof_readme_path, arcname=proof_readme_path.name)
            for proof in resolved_proofs:
                proof_zip.write(proof, arcname=proof.name)

    if lyrics_format not in {"plain", "lrc", "auto"}:
        raise ValueError("lyrics_format must be 'plain', 'lrc', or 'auto'")
    explicit_lyrics = lyrics_text.strip() or _read_text(lyrics_file)
    json_lyrics = lyrics_from_json(lyrics_json, lyrics_format=lyrics_format)
    plain_lyrics = lyrics_from_json(lyrics_json, lyrics_format="plain")
    lyrics = explicit_lyrics or json_lyrics
    if explicit_lyrics and not plain_lyrics:
        plain_lyrics = _strip_lrc_timestamps(explicit_lyrics)
    metadata_override = None
    if metadata_json:
        metadata_override = json.loads(Path(metadata_json).expanduser().resolve().read_text(encoding="utf-8"))
        if not isinstance(metadata_override, dict):
            metadata_override = None

    cover_names = [f"covers/{cover.name}" for cover in resolved_covers]
    proof_names = [f"proof/{proof.name}" for proof in resolved_proofs]
    if proof_readme_path:
        proof_names.insert(0, f"proof/{proof_readme_path.name}")
    proof_zip_name = f"proof/{proof_zip_path.name}" if proof_zip_path else None
    metadata = build_music_metadata(
        audio_name=copied_audio.name,
        youtube_video_name=youtube_video.name,
        cover_names=cover_names,
        proof_names=proof_names,
        proof_zip_name=proof_zip_name,
        website_screenshot_name=f"proof/{website_screenshot.name}" if website_screenshot else None,
        webapp_screenshot_name=f"proof/{webapp_screenshot.name}" if webapp_screenshot else None,
        title=package_title,
        author=author,
        artist=artist,
        language=language,
        genre=genre,
        lyrics=lyrics,
        plain_lyrics=plain_lyrics,
        story=story,
        description=description,
        cover_model=cover_model,
        aginti_cover_count=aginti_cover_count,
        codex_cover_count=codex_cover_count,
        metadata_override=metadata_override,
    )
    if bandcamp_audio:
        metadata["bandcamp_audio_filename"] = bandcamp_audio.name
        metadata["bandcamp_ready"] = True
    else:
        metadata["bandcamp_ready"] = False
        metadata["bandcamp_note"] = "Bandcamp needs a real lossless WAV/AIFF/FLAC source; do not upload a derived WAV from MP3."

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
        "bandcamp_audio": bandcamp_audio.name if bandcamp_audio else None,
        "metadata": metadata_name,
        "lyrics": lyrics_path.name,
        "covers": cover_names,
        "cover_count": len(cover_names),
        "cover_shape": cover_shape,
        "cover_model": cover_model,
        "aginti_cover_count": aginti_cover_count,
        "codex_cover_count": codex_cover_count,
        "youtube_music_video": youtube_video.name,
        "proof_files": proof_names,
        "proof_zip": proof_zip_name,
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    zip_path = package_dir / f"{slug}.zip"
    with zipfile.ZipFile(zip_path, "w") as zipf:
        zipf.write(copied_audio, arcname=copied_audio.name)
        if bandcamp_audio and bandcamp_audio != copied_audio:
            zipf.write(bandcamp_audio, arcname=bandcamp_audio.name)
        zipf.write(youtube_video, arcname=youtube_video.name)
        zipf.write(metadata_path, arcname=metadata_name)
        zipf.write(lyrics_path, arcname=lyrics_path.name)
        zipf.write(manifest_path, arcname=manifest_path.name)
        for cover in resolved_covers:
            zipf.write(cover, arcname=f"covers/{cover.name}")
        if proof_readme_path:
            zipf.write(proof_readme_path, arcname=f"proof/{proof_readme_path.name}")
        for proof in resolved_proofs:
            zipf.write(proof, arcname=f"proof/{proof.name}")
        if proof_zip_path:
            zipf.write(proof_zip_path, arcname=f"proof/{proof_zip_path.name}")

    return {
        "status": "ready",
        "package_dir": str(package_dir),
        "zip_path": str(zip_path),
        "metadata_path": str(metadata_path),
        "lyrics_path": str(lyrics_path),
        "manifest_path": str(manifest_path),
        "audio_path": str(copied_audio),
        "bandcamp_audio_path": str(bandcamp_audio) if bandcamp_audio else None,
        "youtube_video_path": str(youtube_video),
        "cover_paths": [str(path) for path in resolved_covers],
        "cover_count": len(resolved_covers),
        "proof_paths": [str(path) for path in resolved_proofs],
        "proof_zip_path": str(proof_zip_path) if proof_zip_path else None,
        "metadata": metadata,
    }


def post_music_package_to_autopublish(
    zip_path: str | Path,
    autopublish_url: str,
    *,
    publish_shipinhao_music: bool = True,
    publish_youtube_music: bool = False,
    publish_bandcamp_music: bool = False,
    test: bool = False,
    timeout: int = 120,
) -> dict:
    zip_file = Path(zip_path).expanduser().resolve()
    params = {
        'filename': zip_file.name,
        'publish_shipinhao_music': str(bool(publish_shipinhao_music)).lower(),
        'publish_youtube_music': str(bool(publish_youtube_music)).lower(),
        'publish_bandcamp_music': str(bool(publish_bandcamp_music)).lower(),
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
