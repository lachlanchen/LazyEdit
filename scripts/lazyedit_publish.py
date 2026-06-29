#!/usr/bin/env python3
"""CLI client for publishing videos through the LazyEdit HTTP API.

This script is intentionally dependency-free so other repositories can call it
from a Codex session without installing a client package first.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout
import hashlib
import http.client
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from typing import Any
from urllib.parse import urlencode, urlsplit
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


DEFAULT_API_URL = os.getenv("LAZYEDIT_API_URL", "http://127.0.0.1:18787")
DEFAULT_LANGUAGES = ["zh-Hant", "ja", "en"]
DEFAULT_PLATFORMS: list[str] = []
DEFAULT_REMOTE_QUEUE_URL = os.getenv("LAZYEDIT_REMOTE_QUEUE_URL", "http://lazyingart:8081/publish/queue")
PROCESS_TIMEOUT_SECONDS = 3 * 60 * 60
PUBLISH_TIMEOUT_SECONDS = 2 * 60 * 60
POLL_SECONDS = 5
CHUNK_SIZE = 4 * 1024 * 1024
LALACHAN_VIDEOS_ROOT = Path("/home/lachlan/ProjectsLFS/LALACHAN/Videos")
DOWNLOADS_ROOT = Path.home() / "Downloads"

PLATFORMS = {
    "douyin",
    "xiaohongshu",
    "shipinhao",
    "bilibili",
    "youtube",
    "instagram",
}


class ApiError(RuntimeError):
    def __init__(self, message: str, status: int | None = None, payload: Any | None = None):
        super().__init__(message)
        self.status = status
        self.payload = payload


def parse_csv(value: str | None) -> list[str]:
    if not value:
        return []
    return [part.strip() for part in value.split(",") if part.strip()]


def read_text(path: str | None) -> str:
    if not path:
        return ""
    return Path(path).read_text(encoding="utf-8", errors="ignore").strip()


def print_event(message: str, *, quiet: bool = False) -> None:
    if not quiet:
        print(message, flush=True)


def json_dumps(payload: Any) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def probe_media(path: Path) -> dict[str, Any]:
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration,size",
            "-of",
            "json",
            str(path),
        ],
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )
    if result.returncode != 0:
        raise RuntimeError((result.stderr or result.stdout or "ffprobe failed").strip())
    payload = json.loads(result.stdout or "{}")
    fmt = payload.get("format") if isinstance(payload, dict) else {}
    duration = None
    size = None
    if isinstance(fmt, dict):
        try:
            duration = float(fmt.get("duration")) if fmt.get("duration") is not None else None
        except (TypeError, ValueError):
            duration = None
        try:
            size = int(fmt.get("size")) if fmt.get("size") is not None else None
        except (TypeError, ValueError):
            size = None
    return {"duration": duration, "size": size}


def path_is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def latest_download_final_video() -> Path | None:
    if not DOWNLOADS_ROOT.exists():
        return None
    candidates = [
        path
        for path in DOWNLOADS_ROOT.glob("final_video*.mp4")
        if path.is_file()
    ]
    if not candidates:
        return None
    return max(candidates, key=lambda item: item.stat().st_mtime)


def source_preflight(args: argparse.Namespace, *, quiet: bool) -> dict[str, Any]:
    if not args.video:
        return {}
    path = Path(args.video).expanduser().resolve()
    if not path.exists():
        raise FileNotFoundError(path)
    stat = path.stat()
    media = probe_media(path)
    digest = file_sha256(path)
    duration = media.get("duration")
    size = media.get("size") or stat.st_size
    info = {
        "path": str(path),
        "duration": duration,
        "size": size,
        "sha256": digest,
    }
    duration_text = f"{duration:.3f}s" if isinstance(duration, (int, float)) else "unknown"
    print_event(
        "Source preflight: "
        f"path={path} duration={duration_text} size={size / 1024 / 1024:.1f}MB sha256={digest}",
        quiet=quiet,
    )

    if args.expect_sha256 and digest.lower() != args.expect_sha256.lower():
        raise ValueError(
            "source sha256 mismatch: "
            f"expected {args.expect_sha256.lower()}, got {digest.lower()}"
        )
    if args.expect_duration is not None and duration is not None:
        tolerance = max(0.0, float(args.duration_tolerance))
        if abs(float(duration) - float(args.expect_duration)) > tolerance:
            raise ValueError(
                "source duration mismatch: "
                f"expected {args.expect_duration:.3f}s +/- {tolerance:.3f}s, got {duration:.3f}s"
            )
    if args.expect_min_size_mb is not None:
        min_bytes = float(args.expect_min_size_mb) * 1024 * 1024
        if size < min_bytes:
            raise ValueError(
                f"source file is smaller than expected: {size / 1024 / 1024:.1f}MB "
                f"< {args.expect_min_size_mb:.1f}MB"
            )
    if args.expect_max_size_mb is not None:
        max_bytes = float(args.expect_max_size_mb) * 1024 * 1024
        if size > max_bytes:
            raise ValueError(
                f"source file is larger than expected: {size / 1024 / 1024:.1f}MB "
                f"> {args.expect_max_size_mb:.1f}MB"
            )

    if (
        path_is_relative_to(path, LALACHAN_VIDEOS_ROOT)
        and not args.allow_stale_lalachan_copy
    ):
        latest = latest_download_final_video()
        if latest:
            latest_stat = latest.stat()
            # The Xiaoyunque browser workflow often saves the authoritative
            # render as Downloads/final_video*.mp4 before copying into Videos/.
            # If a newer final_video exists and differs, make the caller choose
            # explicitly instead of silently publishing the stale copy.
            if latest_stat.st_mtime > stat.st_mtime and latest_stat.st_mtime - stat.st_mtime < 24 * 60 * 60:
                latest_hash = file_sha256(latest)
                if latest_hash != digest:
                    latest_media = probe_media(latest)
                    latest_duration = latest_media.get("duration")
                    latest_duration_text = (
                        f"{latest_duration:.3f}s"
                        if isinstance(latest_duration, (int, float))
                        else "unknown"
                    )
                    raise ValueError(
                        "possible stale LALACHAN Videos copy: "
                        f"{path} differs from newer download {latest} "
                        f"(download duration={latest_duration_text}, "
                        f"size={latest_stat.st_size / 1024 / 1024:.1f}MB, "
                        f"sha256={latest_hash}). Use --video with the download path "
                        "or pass --allow-stale-lalachan-copy if this is intentional."
                    )
    return info


def request_url_json(url: str, timeout: int = 20) -> dict[str, Any]:
    request = Request(url, method="GET", headers={"Accept": "application/json"})
    with urlopen(request, timeout=timeout) as response:
        raw = response.read().decode("utf-8", errors="replace")
        return json.loads(raw or "{}")


class LazyEditClient:
    def __init__(self, base_url: str, timeout: int = 300, quiet: bool = False):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.quiet = quiet

    def _url(self, path: str, query: dict[str, Any] | None = None) -> str:
        if not path.startswith("/"):
            path = "/" + path
        url = self.base_url + path
        if query:
            clean_query = {k: v for k, v in query.items() if v is not None}
            if clean_query:
                url += "?" + urlencode(clean_query)
        return url

    def request_json(
        self,
        method: str,
        path: str,
        payload: dict[str, Any] | None = None,
        query: dict[str, Any] | None = None,
        timeout: int | None = None,
    ) -> dict[str, Any]:
        body = None
        headers = {"Accept": "application/json"}
        if payload is not None:
            body = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"
        request = Request(self._url(path, query), data=body, method=method.upper(), headers=headers)
        try:
            with urlopen(request, timeout=timeout or self.timeout) as response:
                raw = response.read().decode("utf-8", errors="replace")
                return json.loads(raw or "{}")
        except HTTPError as exc:
            raw = exc.read().decode("utf-8", errors="replace")
            try:
                payload_out = json.loads(raw or "{}")
            except json.JSONDecodeError:
                payload_out = {"error": raw}
            message = payload_out.get("error") or payload_out.get("details") or raw or str(exc)
            raise ApiError(message, status=exc.code, payload=payload_out) from exc
        except URLError as exc:
            raise ApiError(f"LazyEdit API request failed: {exc}") from exc

    def upload_stream(
        self,
        video_path: Path,
        *,
        title: str | None,
        filename: str | None,
        source: str,
    ) -> dict[str, Any]:
        video_path = video_path.resolve()
        if not video_path.exists():
            raise FileNotFoundError(video_path)
        upload_name = filename or video_path.name
        query = urlencode({
            "filename": upload_name,
            "title": title or video_path.stem,
            "source": source,
        })
        parsed = urlsplit(f"{self.base_url}/upload-stream?{query}")
        target = parsed.path + (("?" + parsed.query) if parsed.query else "")
        conn_cls = http.client.HTTPSConnection if parsed.scheme == "https" else http.client.HTTPConnection
        port = parsed.port
        conn = conn_cls(parsed.hostname, port=port, timeout=self.timeout)
        size = video_path.stat().st_size
        print_event(f"Uploading {video_path} ({size / 1024 / 1024:.1f} MB)", quiet=self.quiet)
        try:
            conn.putrequest("PUT", target)
            conn.putheader("Content-Type", "application/octet-stream")
            conn.putheader("Content-Length", str(size))
            conn.endheaders()
            with video_path.open("rb") as handle:
                while True:
                    chunk = handle.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    conn.send(chunk)
            response = conn.getresponse()
            raw = response.read().decode("utf-8", errors="replace")
        finally:
            conn.close()
        try:
            payload = json.loads(raw or "{}")
        except json.JSONDecodeError:
            payload = {"error": raw}
        if response.status >= 400:
            raise ApiError(payload.get("error") or raw or response.reason, response.status, payload)
        return payload


def platform_flags(platforms: list[str]) -> dict[str, bool]:
    flags = {platform: False for platform in PLATFORMS}
    for platform in platforms:
        normalized = platform.strip().lower()
        if normalized not in PLATFORMS:
            raise ValueError(f"unsupported platform: {platform}")
        flags[normalized] = True
    return flags


def current_ui_settings(client: LazyEditClient) -> dict[str, Any]:
    settings: dict[str, Any] = {}
    for key in ("publish_options", "translation_languages", "burn_layout", "logo_settings"):
        try:
            payload = client.request_json("GET", f"/api/ui-settings/{key}", timeout=30)
            settings[key] = payload.get("value")
        except Exception as exc:
            print_event(f"Warning: failed to load Studio setting {key}: {exc}", quiet=client.quiet)
    return settings


def current_logo_settings(client: LazyEditClient) -> dict[str, Any]:
    try:
        payload = client.request_json("GET", "/api/ui-settings/logo_settings", timeout=30)
        value = payload.get("value")
        return value if isinstance(value, dict) else {}
    except Exception as exc:
        print_event(f"Warning: failed to load Studio logo settings: {exc}", quiet=client.quiet)
        return {}


def apply_logo_overrides(args: argparse.Namespace, logo_settings: dict[str, Any] | None) -> dict[str, Any] | None:
    if not isinstance(logo_settings, dict):
        return logo_settings
    if args.logo_position is None and args.logo_enabled_override is None:
        return logo_settings
    logo_settings = dict(logo_settings)
    if args.logo_position:
        logo_settings["position"] = args.logo_position
    if args.logo_enabled_override is not None:
        logo_settings["enabled"] = bool(args.logo_enabled_override)
    return logo_settings


def first_present(*values: Any) -> Any:
    for value in values:
        if value is not None:
            return value
    return None


def build_options(
    args: argparse.Namespace,
    correction_prompt: str,
    metadata_prompt: str,
    settings: dict[str, Any] | None = None,
) -> dict[str, Any]:
    settings = settings or {}
    current_publish = settings.get("publish_options")
    if not isinstance(current_publish, dict):
        current_publish = {}
    current_layout = settings.get("burn_layout")
    if not isinstance(current_layout, dict):
        current_layout = current_publish.get("burnLayout") if isinstance(current_publish.get("burnLayout"), dict) else {}
    current_languages = current_publish.get("translationLanguages") or settings.get("translation_languages")

    languages = parse_csv(args.languages) or current_languages or DEFAULT_LANGUAGES
    burn_subtitles = first_present(args.burn_subtitles, current_publish.get("burnSubtitles"), True)
    use_polished = first_present(args.use_polished, current_publish.get("usePolishedSubtitles"), True)
    use_polished = bool(use_polished) or bool(correction_prompt)

    burn_layout: dict[str, Any] = dict(current_layout or {})
    layout_overrides = {
        "liftRatio": args.subtitle_lift_ratio,
        "rows": args.subtitle_rows,
        "fontScale": args.subtitle_font_scale,
        "fontBold": args.subtitle_font_bold,
        "fontColor": args.subtitle_font_color,
        "outlineBold": args.subtitle_outline_bold,
        "outlineColor": args.subtitle_outline_color,
    }
    for key, value in layout_overrides.items():
        if value is not None:
            burn_layout[key] = value
    portrait_overrides = {
        "enabled": args.portrait_blur_fill,
        "mode": args.portrait_blur_mode,
        "foregroundY": args.portrait_foreground_y,
        "centerShiftRatio": args.portrait_center_shift_ratio,
        "bottomSpaceRatio": args.portrait_bottom_space_ratio,
        "foregroundWidth": args.portrait_foreground_width,
        "width": args.portrait_width,
        "height": args.portrait_height,
        "blur": args.portrait_blur,
        "crf": args.portrait_crf,
        "preset": args.portrait_preset,
    }
    portrait_overrides = {key: value for key, value in portrait_overrides.items() if value is not None}
    if portrait_overrides:
        current_portrait = burn_layout.get("portraitBlurFill")
        if not isinstance(current_portrait, dict):
            current_portrait = {}
        burn_layout["portraitBlurFill"] = {**current_portrait, **portrait_overrides}

    publication_mode = "new" if args.new_run else str(current_publish.get("publicationMode") or "override")
    if publication_mode not in {"new", "override"}:
        publication_mode = "override"

    publish_category = args.publish_category
    if not publish_category and args.video:
        try:
            if path_is_relative_to(Path(args.video).expanduser().resolve(), LALACHAN_VIDEOS_ROOT):
                publish_category = "lalachan"
        except Exception:
            publish_category = None

    options = {
        "burnSubtitles": bool(burn_subtitles),
        "translationLanguages": languages,
        "usePolishedSubtitles": use_polished,
        "subtitleSourceVersion": "polished" if use_polished else "original",
        "publicationMode": publication_mode,
        "publicationSessionId": args.publication_session_id,
        "autoCorrectSubtitles": False,
        "autoCorrectPrompt": "",
        "useCorrectionPromptForMetadata": bool(metadata_prompt),
        "metadataPrompt": metadata_prompt,
        "notes": metadata_prompt,
        "burnLayout": burn_layout,
        "persistSettings": args.persist_settings,
    }
    if publish_category:
        options["publishCategory"] = publish_category
    if args.youtube_playlist:
        options["youtubePlaylist"] = args.youtube_playlist
    if args.shipinhao_collection:
        options["shipinhaoCollection"] = args.shipinhao_collection
    return options


def logo_overlay_enabled(logo_settings: dict[str, Any] | None) -> bool:
    return bool(
        isinstance(logo_settings, dict)
        and logo_settings.get("enabled")
        and logo_settings.get("logoPath")
    )


def portrait_blurfill_enabled(burn_layout: dict[str, Any] | None) -> bool:
    if not isinstance(burn_layout, dict):
        return False
    config = burn_layout.get("portraitBlurFill")
    if not isinstance(config, dict):
        return False
    value = config.get("enabled")
    if isinstance(value, bool):
        return value
    return str(value or "").strip().lower() in {"1", "true", "yes", "y", "on"}


def default_steps(
    burn_subtitles: bool,
    logo_enabled: bool = False,
    portrait_enabled: bool = False,
) -> list[str]:
    if burn_subtitles:
        return ["keyframes", "caption", "transcribe", "translate", "burn", "metadata_zh", "metadata_en", "cover"]
    if logo_enabled or portrait_enabled:
        return ["keyframes", "caption", "transcribe", "burn", "metadata_zh", "metadata_en", "cover"]
    return ["keyframes", "caption", "transcribe", "metadata_zh", "metadata_en", "cover"]


def step_summary(payload: dict[str, Any]) -> str:
    steps = payload.get("steps") or {}
    if not isinstance(steps, dict):
        return "no step status"
    parts = []
    for name in ("transcribe", "polish", "translate", "burn", "keyframes", "caption", "metadata_zh", "metadata_en", "cover"):
        step = steps.get(name)
        if isinstance(step, dict):
            detail = step.get("detail") or step.get("progress")
            parts.append(f"{name}:{step.get('status')}" + (f"({detail})" if detail else ""))
    return " ".join(parts)


def process_ready_with_options(payload: dict[str, Any], *, burn_subtitles: bool, logo_enabled: bool) -> bool:
    if payload.get("ready_for_publish"):
        return True
    steps = payload.get("steps") or {}
    if not isinstance(steps, dict):
        return False

    required = ["transcribe", "polish", "keyframes", "caption", "metadata_zh", "metadata_en", "cover"]
    if burn_subtitles:
        required.append("translate")
    if burn_subtitles or logo_enabled:
        required.append("burn")

    for name in required:
        status = (steps.get(name) or {}).get("status")
        if status not in {"done", "skipped"}:
            return False
    return True


def request_with_heartbeat(
    client: LazyEditClient,
    method: str,
    path: str,
    payload: dict[str, Any],
    *,
    timeout: int,
    label: str,
    interval: int,
    quiet: bool,
) -> dict[str, Any]:
    """Run a blocking API call while emitting lightweight progress heartbeats."""
    heartbeat = max(10, int(interval))
    start = time.monotonic()
    next_print = start + heartbeat
    with ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(client.request_json, method, path, payload, None, timeout)
        while True:
            try:
                return future.result(timeout=1)
            except FutureTimeout:
                now = time.monotonic()
                if now >= next_print:
                    elapsed = int(now - start)
                    print_event(f"{label}: waiting {elapsed}s", quiet=quiet)
                    next_print = now + heartbeat


def wait_for_process(
    client: LazyEditClient,
    video_id: int,
    session_id: int | None,
    timeout: int,
    interval: int,
    *,
    burn_subtitles: bool,
    logo_enabled: bool,
) -> dict[str, Any]:
    deadline = time.monotonic() + timeout
    last = ""
    while time.monotonic() < deadline:
        payload = client.request_json(
            "GET",
            f"/api/videos/{video_id}/process-status",
            query={"publicationSessionId": session_id},
            timeout=60,
        )
        summary = step_summary(payload)
        if summary != last:
            print_event(f"Process status: {summary}", quiet=client.quiet)
            last = summary
        steps = payload.get("steps") or {}
        errors = [
            f"{name}: {step.get('detail') or 'error'}"
            for name, step in steps.items()
            if isinstance(step, dict) and step.get("status") == "error"
        ]
        if errors:
            raise ApiError("process failed: " + "; ".join(errors), payload=payload)
        if process_ready_with_options(payload, burn_subtitles=burn_subtitles, logo_enabled=logo_enabled):
            return payload
        time.sleep(interval)
    raise TimeoutError(f"process did not become ready within {timeout} seconds")


def find_remote_job(queue_url: str, remote_job_id: str | None, filename: str | None) -> dict[str, Any] | None:
    if not queue_url or (not remote_job_id and not filename):
        return None
    payload = request_url_json(queue_url, timeout=20)
    jobs = payload.get("jobs") if isinstance(payload, dict) else []
    if not isinstance(jobs, list):
        return None
    for job in jobs:
        if not isinstance(job, dict):
            continue
        if remote_job_id and str(job.get("id") or job.get("job_id") or "") == str(remote_job_id):
            return job
        if not remote_job_id and filename and str(job.get("filename") or "") == str(filename):
            if str(job.get("status") or "").lower() in {"queued", "running"}:
                return job
    return None


def same_local_job_id(value: Any, job_id: int) -> bool:
    try:
        return int(value) == int(job_id)
    except (TypeError, ValueError):
        return False


def run_remote_log_command(command: str, *, quiet: bool) -> None:
    if not command:
        return
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=False,
            capture_output=True,
            text=True,
            timeout=20,
        )
    except Exception as exc:
        print_event(f"Remote log command failed: {exc}", quiet=quiet)
        return
    output = (result.stdout or result.stderr or "").strip()
    if output:
        print_event("Remote AutoPublish log tail:\n" + output, quiet=quiet)


def publish_message(job_id: int, job: dict[str, Any]) -> str:
    status = job.get("status")
    detail = job.get("detail") or ""
    remote_status = job.get("remote_status") or ""
    remote_job_id = job.get("remote_job_id") or ""
    parts = [f"Publish job {job_id}: {status}"]
    if remote_status:
        parts.append(f"remote={remote_status}")
    if remote_job_id:
        parts.append(f"remote_id={remote_job_id}")
    if detail:
        parts.append(str(detail))
    return " ".join(parts).strip()


def wait_for_publish(
    client: LazyEditClient,
    job_id: int,
    timeout: int,
    interval: int,
    *,
    guided_monitor: bool = False,
    remote_queue_url: str | None = None,
    remote_log_command: str | None = None,
    remote_log_seconds: int = 60,
) -> dict[str, Any]:
    deadline = time.monotonic() + timeout
    last = ""
    last_remote = ""
    next_remote_log = time.monotonic() + max(30, remote_log_seconds)
    while time.monotonic() < deadline:
        payload = client.request_json("GET", "/api/autopublish/queue", timeout=60)
        jobs = payload.get("jobs") if isinstance(payload, dict) else []
        match = None
        if isinstance(jobs, list):
            for job in jobs:
                if isinstance(job, dict) and same_local_job_id(job.get("id"), job_id):
                    match = job
                    break
        if match:
            status = match.get("status")
            message = publish_message(job_id, match)
            if message != last:
                print_event(message, quiet=client.quiet)
                last = message
            if guided_monitor and remote_queue_url:
                remote_job_id = str(match.get("remote_job_id") or "")
                remote_filename = str(match.get("remote_filename") or match.get("filename") or "")
                try:
                    remote = find_remote_job(remote_queue_url, remote_job_id, remote_filename)
                except Exception as exc:
                    remote = {"status": "unknown", "error": f"remote queue failed: {exc}"}
                if remote:
                    remote_message = (
                        f"Remote AutoPublish: {remote.get('status')}"
                        f" id={remote.get('id') or remote_job_id}"
                        f" file={remote.get('filename') or remote_filename}"
                    )
                    if remote.get("detail"):
                        remote_message += f" detail={remote.get('detail')}"
                    if remote.get("error"):
                        remote_message += f" error={remote.get('error')}"
                    if remote_message != last_remote:
                        print_event(remote_message, quiet=client.quiet)
                        last_remote = remote_message
                    if remote.get("status") == "failed":
                        raise ApiError(remote.get("error") or "remote publish failed", payload=remote)
            if guided_monitor and remote_log_command and time.monotonic() >= next_remote_log:
                run_remote_log_command(remote_log_command, quiet=client.quiet)
                next_remote_log = time.monotonic() + max(30, remote_log_seconds)
            if status == "done":
                return match
            if status == "failed":
                raise ApiError(match.get("error") or "publish failed", payload=match)
        time.sleep(interval)
    raise TimeoutError(f"publish job {job_id} did not finish within {timeout} seconds")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Upload, correct subtitles, process, and publish a video through LazyEdit.",
    )
    parser.add_argument("--api-url", default=DEFAULT_API_URL)
    parser.add_argument("--video", help="Path to a local video to upload.")
    parser.add_argument("--video-id", type=int, help="Existing LazyEdit video id to reuse.")
    parser.add_argument("--expect-sha256", help="Fail if --video does not match this SHA-256.")
    parser.add_argument("--expect-duration", type=float, help="Fail if --video duration differs from this value.")
    parser.add_argument("--duration-tolerance", type=float, default=0.75)
    parser.add_argument("--expect-min-size-mb", type=float)
    parser.add_argument("--expect-max-size-mb", type=float)
    parser.add_argument(
        "--allow-stale-lalachan-copy",
        action="store_true",
        help="Allow publishing a LALACHAN Videos/ copy even when a newer differing Downloads/final_video*.mp4 exists.",
    )
    parser.add_argument("--title", help="Title stored in LazyEdit. Defaults to video filename stem.")
    parser.add_argument("--filename", help="Upload filename. Defaults to source filename.")
    parser.add_argument("--source", default="api")
    parser.add_argument("--platforms", default=",".join(DEFAULT_PLATFORMS), help="Comma-separated target platforms.")
    parser.add_argument("--platform", action="append", default=[], help="Target platform; may be repeated.")
    parser.add_argument(
        "--publish-category",
        choices=["simplelife", "lazyingart", "musia", "lalachan", "lalamv", "music"],
        help="Override publish routing. Defaults to simplelife, except LALACHAN source videos auto-route to LALACHAN. 'music' is accepted as an alias for musia.",
    )
    parser.add_argument("--youtube-playlist", help="Override YouTube playlist/category for this one publish.")
    parser.add_argument("--shipinhao-collection", help="Override Shipinhao 合集 for this one publish.")
    parser.add_argument("--languages", help="Bottom-to-top subtitle languages.")
    parser.add_argument("--use-current-settings", action="store_true", help="Use current Studio publish and subtitle layout settings as defaults.")
    parser.add_argument("--prompt-file", help="Prompt/story file used for both subtitle correction and metadata.")
    parser.add_argument("--correction-prompt-file", help="Prompt file for AI subtitle correction.")
    parser.add_argument("--metadata-prompt-file", help="Prompt/story file for metadata generation.")
    parser.add_argument("--correct-subtitles", dest="correct_subtitles", action="store_true", default=None)
    parser.add_argument("--no-correct-subtitles", dest="correct_subtitles", action="store_false")
    parser.add_argument("--correction-source", default="polished", choices=["original", "polished"])
    parser.add_argument("--process", dest="process", action="store_true", default=True)
    parser.add_argument("--no-process", dest="process", action="store_false")
    parser.add_argument("--publish", dest="publish", action="store_true", default=True)
    parser.add_argument("--no-publish", dest="publish", action="store_false")
    parser.add_argument("--burn-subtitles", dest="burn_subtitles", action="store_true", default=None)
    parser.add_argument("--no-burn-subtitles", dest="burn_subtitles", action="store_false")
    parser.add_argument("--use-polished", dest="use_polished", action="store_true", default=None)
    parser.add_argument("--use-original", dest="use_polished", action="store_false")
    parser.add_argument("--new-run", action="store_true", help="Create a new publication run instead of overriding current output.")
    parser.add_argument("--publication-session-id", type=int)
    parser.add_argument("--persist-settings", action="store_true", help="Also update Studio UI publish preferences.")
    parser.add_argument("--subtitle-lift-ratio", type=float)
    parser.add_argument("--subtitle-rows", type=int)
    parser.add_argument("--subtitle-font-scale", type=float)
    parser.add_argument("--subtitle-font-bold", action=argparse.BooleanOptionalAction, default=None)
    parser.add_argument("--subtitle-font-color")
    parser.add_argument("--subtitle-outline-bold", action=argparse.BooleanOptionalAction, default=None)
    parser.add_argument("--subtitle-outline-color")
    parser.add_argument("--portrait-blur-fill", action=argparse.BooleanOptionalAction, default=None)
    parser.add_argument("--portrait-blur-mode", choices=["lalachan", "center", "custom"])
    parser.add_argument("--portrait-foreground-y", type=int)
    parser.add_argument("--portrait-center-shift-ratio", type=float)
    parser.add_argument("--portrait-bottom-space-ratio", type=float)
    parser.add_argument("--portrait-foreground-width", type=int)
    parser.add_argument("--portrait-width", type=int)
    parser.add_argument("--portrait-height", type=int)
    parser.add_argument("--portrait-blur", type=float)
    parser.add_argument("--portrait-crf", type=int)
    parser.add_argument("--portrait-preset")
    parser.add_argument("--logo-position", choices=["top-left", "top-right", "bottom-left", "bottom-right", "center"])
    parser.add_argument("--logo", dest="logo_enabled_override", action="store_true", default=None)
    parser.add_argument("--no-logo", dest="logo_enabled_override", action="store_false")
    parser.add_argument("--steps", help="Comma-separated process steps. Defaults to the publish pipeline.")
    parser.add_argument("--wait", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--process-timeout", type=int, default=PROCESS_TIMEOUT_SECONDS)
    parser.add_argument("--publish-timeout", type=int, default=PUBLISH_TIMEOUT_SECONDS)
    parser.add_argument("--poll-seconds", type=int, default=POLL_SECONDS)
    parser.add_argument(
        "--guided-monitor",
        action="store_true",
        help="Print richer progress for subtitle correction, processing, local queue, and remote AutoPublish.",
    )
    parser.add_argument(
        "--remote-queue-url",
        default=DEFAULT_REMOTE_QUEUE_URL,
        help="Remote AutoPublish queue URL used by --guided-monitor.",
    )
    parser.add_argument(
        "--remote-log-command",
        default=os.getenv("LAZYEDIT_REMOTE_LOG_COMMAND", ""),
        help="Optional command to print a remote publish log tail during --guided-monitor.",
    )
    parser.add_argument(
        "--remote-log-seconds",
        type=int,
        default=int(os.getenv("LAZYEDIT_REMOTE_LOG_SECONDS", "90")),
        help="Minimum seconds between remote log tail checks.",
    )
    parser.add_argument("--json", action="store_true", help="Print final machine-readable JSON.")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args(argv)
    if args.json:
        args.quiet = True

    if not args.video and not args.video_id:
        parser.error("provide --video or --video-id")

    platforms = parse_csv(args.platforms) + list(args.platform or [])
    if args.publish and not platforms:
        parser.error("provide --platforms or --platform when publishing")

    correction_prompt = read_text(args.correction_prompt_file) or read_text(args.prompt_file)
    metadata_prompt = read_text(args.metadata_prompt_file) or read_text(args.prompt_file)
    should_correct = args.correct_subtitles if args.correct_subtitles is not None else bool(correction_prompt)
    if should_correct and not correction_prompt:
        parser.error("--correct-subtitles requires --correction-prompt-file or --prompt-file")

    client = LazyEditClient(args.api_url, quiet=args.quiet)
    final: dict[str, Any] = {"api_url": args.api_url}

    try:
        if args.video_id:
            video_id = args.video_id
            final["video_id"] = video_id
        else:
            final["source_preflight"] = source_preflight(args, quiet=args.quiet)
            upload = client.upload_stream(
                Path(args.video),
                title=args.title,
                filename=args.filename,
                source=args.source,
            )
            video_id = int(upload["video_id"])
            final["upload"] = upload
            final["video_id"] = video_id
            print_event(f"Uploaded video_id={video_id}", quiet=args.quiet)

        if should_correct:
            print_event("Running AI subtitle correction...", quiet=args.quiet)
            correction_payload = {
                "action": "ai",
                "prompt": correction_prompt,
                "sourceVariant": args.correction_source,
                "use_cache": True,
            }
            if args.guided_monitor:
                correction = request_with_heartbeat(
                    client,
                    "POST",
                    f"/api/videos/{video_id}/subtitle-correction",
                    correction_payload,
                    timeout=args.process_timeout,
                    label="Subtitle correction",
                    interval=max(args.poll_seconds, 10),
                    quiet=args.quiet,
                )
            else:
                correction = client.request_json(
                    "POST",
                    f"/api/videos/{video_id}/subtitle-correction",
                    correction_payload,
                    timeout=args.process_timeout,
                )
            final["subtitle_correction"] = {
                "original": correction.get("original", {}).get("path"),
                "polished": correction.get("polished", {}).get("path"),
            }
            print_event("Subtitle correction saved as polished subtitles.", quiet=args.quiet)

        settings = current_ui_settings(client) if args.use_current_settings else {}
        if not args.use_current_settings and (args.logo_position or args.logo_enabled_override is not None):
            settings["logo_settings"] = current_logo_settings(client)
        if settings:
            final["current_settings"] = settings
            print_event("Loaded current Studio publish settings.", quiet=args.quiet)

        options = build_options(args, correction_prompt, metadata_prompt, settings)
        logo_settings = settings.get("logo_settings") if isinstance(settings, dict) else None
        logo_settings = apply_logo_overrides(args, logo_settings)
        logo_enabled = logo_overlay_enabled(logo_settings)
        portrait_enabled = portrait_blurfill_enabled(options.get("burnLayout"))
        final["options"] = {
            "burnSubtitles": options["burnSubtitles"],
            "translationLanguages": options["translationLanguages"],
            "usePolishedSubtitles": options["usePolishedSubtitles"],
            "subtitleSourceVersion": options["subtitleSourceVersion"],
            "publicationMode": options["publicationMode"],
            "burnLayout": options["burnLayout"],
            "persistSettings": options["persistSettings"],
        }
        session_id = args.publication_session_id

        if args.process:
            steps = parse_csv(args.steps) or default_steps(
                bool(options["burnSubtitles"]),
                logo_enabled,
                portrait_enabled,
            )
            print_event(f"Starting LazyEdit process: {', '.join(steps)}", quiet=args.quiet)
            process_payload = {
                **options,
                "async": True,
                "steps": steps,
                "polish_notes": correction_prompt,
                "notes": metadata_prompt,
            }
            if logo_enabled:
                process_payload["logo"] = logo_settings
                final["logo_settings"] = {
                    "logoPath": logo_settings.get("logoPath"),
                    "heightRatio": logo_settings.get("heightRatio"),
                    "position": logo_settings.get("position"),
                    "enabled": logo_settings.get("enabled"),
                }
            process_started = client.request_json(
                "POST",
                f"/api/videos/{video_id}/process",
                process_payload,
                timeout=120,
            )
            final["process_started"] = process_started
            session_id = process_started.get("publication_session_id") or session_id
            final["publication_session_id"] = session_id
            print_event(f"Process started for video_id={video_id}, session={session_id}", quiet=args.quiet)
            if args.wait:
                final["process_status"] = wait_for_process(
                    client,
                    video_id,
                    int(session_id) if session_id else None,
                    args.process_timeout,
                    args.poll_seconds,
                    burn_subtitles=bool(options["burnSubtitles"]),
                    logo_enabled=logo_enabled,
                )

        if args.publish:
            publish_options = {**options, "publicationSessionId": session_id}
            if args.process and args.wait and final.get("process_status", {}).get("ready_for_publish"):
                # The process phase already used the metadata prompt. Do not
                # send it again or the publish worker will rerun processing.
                publish_options["metadataPrompt"] = ""
                publish_options["notes"] = ""
                publish_options["useCorrectionPromptForMetadata"] = False
            publish_payload = {
                "platforms": platform_flags(platforms),
                "options": publish_options,
                "persistSettings": args.persist_settings,
            }
            print_event(f"Queueing publish to: {', '.join(platforms)}", quiet=args.quiet)
            published = client.request_json(
                "POST",
                f"/api/videos/{video_id}/publish",
                publish_payload,
                timeout=120,
            )
            final["publish_started"] = published
            job_id = published.get("job_id") or (published.get("job") or {}).get("id")
            if job_id and args.wait:
                final["publish_job"] = wait_for_publish(
                    client,
                    int(job_id),
                    args.publish_timeout,
                    args.poll_seconds,
                    guided_monitor=args.guided_monitor,
                    remote_queue_url=args.remote_queue_url,
                    remote_log_command=args.remote_log_command,
                    remote_log_seconds=args.remote_log_seconds,
                )

        if args.json:
            print(json_dumps(final))
        else:
            print_event("LazyEdit publish CLI completed.", quiet=args.quiet)
            if not args.quiet:
                print(json_dumps({
                    "video_id": final.get("video_id"),
                    "publication_session_id": final.get("publication_session_id"),
                    "publish_job": final.get("publish_job", final.get("publish_started")),
                }))
        return 0
    except Exception as exc:
        if args.json:
            print(json_dumps({"error": str(exc), "partial": final}), file=sys.stderr)
        else:
            print(f"ERROR: {exc}", file=sys.stderr)
            if isinstance(exc, ApiError) and exc.payload is not None:
                print(json_dumps(exc.payload), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
