"""
Sora 2 Video API helpers.

Usage (CLI):
  python agi/video_requests.py \
    --prompt "Wide tracking shot of a teal coupe driving through a desert highway" \
    --model sora-2 \
    --size 1280x720 \
    --seconds 8 \
    --output out.mp4

Requires environment variable OPENAI_API_KEY to be set.
"""
from __future__ import annotations

import argparse
import os
import shutil
import sys
import time
from typing import Optional
import hashlib
import json

from openai import OpenAI
import httpx
from lazyedit import db as ldb


def _have_sdk_videos(client: OpenAI) -> bool:
    return hasattr(client, "videos") and hasattr(client.videos, "create")


def create_video(
    client: OpenAI,
    *,
    prompt: str,
    model: str = "sora-2",
    size: Optional[str] = None,
    seconds: Optional[int] = None,
    input_reference: Optional[str] = None,
):
    payload: dict = {"model": model, "prompt": prompt}
    if size:
        payload["size"] = size
    if seconds:
        payload["seconds"] = str(seconds)
    if input_reference:
        payload["input_reference"] = input_reference

    if _have_sdk_videos(client):
        return client.videos.create(**payload)

    # Fallback: raw HTTP (multipart form)
    token = os.getenv("OPENAI_API_KEY")
    if not token:
        raise RuntimeError("OPENAI_API_KEY not set for HTTP fallback")
    form = {k: (None, v) for k, v in payload.items()}
    headers = {"Authorization": f"Bearer {token}"}
    project = os.getenv("OPENAI_PROJECT") or os.getenv("OPENAI_PROJECT_ID")
    if project:
        headers["OpenAI-Project"] = project
    with httpx.Client(timeout=60.0) as s:
        r = s.post("https://api.openai.com/v1/videos", headers=headers, files=form)
        if r.status_code >= 400:
            raise RuntimeError(f"POST /videos {r.status_code}: {r.text}")
        return r.json()


def retrieve_status(client: OpenAI, video_id: str):
    if _have_sdk_videos(client):
        return client.videos.retrieve(video_id)
    token = os.getenv("OPENAI_API_KEY")
    if not token:
        raise RuntimeError("OPENAI_API_KEY not set for HTTP fallback")
    headers = {"Authorization": f"Bearer {token}"}
    project = os.getenv("OPENAI_PROJECT") or os.getenv("OPENAI_PROJECT_ID")
    if project:
        headers["OpenAI-Project"] = project
    with httpx.Client(timeout=60.0) as s:
        r = s.get(f"https://api.openai.com/v1/videos/{video_id}", headers=headers)
        if r.status_code >= 400:
            raise RuntimeError(f"GET /videos/{video_id} {r.status_code}: {r.text}")
        return r.json()


def download_video(client: OpenAI, video_id: str, out_path: str, variant: str = "video") -> str:
    if _have_sdk_videos(client) and hasattr(client.videos, "download_content"):
        content = client.videos.download_content(video_id, variant=variant)
        try:
            content.write_to_file(out_path)
            return out_path
        except AttributeError:
            body = content.array_buffer()
            with open(out_path, "wb") as f:
                f.write(body)
            return out_path

    # Fallback: raw HTTP download
    token = os.getenv("OPENAI_API_KEY")
    if not token:
        raise RuntimeError("OPENAI_API_KEY not set for HTTP fallback")
    headers = {"Authorization": f"Bearer {token}"}
    project = os.getenv("OPENAI_PROJECT") or os.getenv("OPENAI_PROJECT_ID")
    if project:
        headers["OpenAI-Project"] = project
    with httpx.Client(timeout=None) as s:
        r = s.get(f"https://api.openai.com/v1/videos/{video_id}/content", headers=headers, params={"variant": variant} if variant else None)
        if r.status_code >= 400:
            raise RuntimeError(f"GET /videos/{video_id}/content {r.status_code}: {r.text}")
        with open(out_path, "wb") as f:
            for chunk in r.iter_bytes():
                f.write(chunk)
    return out_path


def create_poll_and_download(
    *,
    prompt: str,
    model: str = "sora-2",
    size: str = "1280x720",
    seconds: int = 8,
    output: str = "video.mp4",
    input_reference: Optional[str] = None,
    poll_interval: float = 10.0,
    timeout_seconds: int = 30 * 60,
    use_cache: bool = True,
) -> str:
    client = OpenAI()
    # Ensure output directory exists
    out_dir = os.path.dirname(output)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    def _hash_reference(value: Optional[str]) -> Optional[str]:
        if not value:
            return None
        if os.path.exists(value):
            hasher = hashlib.sha256()
            with open(value, "rb") as handle:
                for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                    hasher.update(chunk)
            return f"file:{hasher.hexdigest()}"
        return value

    def _prepare_reference(value: Optional[str]) -> Optional[str]:
        if not value:
            return None
        if os.path.exists(value):
            with open(value, "rb") as handle:
                uploaded = client.files.create(file=handle, purpose="vision")
            ref_id = getattr(uploaded, "id", None) or (uploaded.get("id") if isinstance(uploaded, dict) else None)
            if not ref_id:
                raise RuntimeError("OpenAI file upload did not return an id")
            return ref_id
        return value

    # Compute request hash and attempt cache
    payload = {"model": model, "prompt": prompt, "size": size, "seconds": seconds}
    reference_hash = _hash_reference(input_reference)
    if reference_hash:
        payload["input_reference"] = reference_hash
    key = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    rhash = hashlib.sha256(key.encode("utf-8")).hexdigest()
    rcode = rhash[:12]
    print(f"Request code: {rcode}")
    if use_cache:
        try:
            row = ldb.find_generated_by_hash(rhash)
            if row:
                job_id, status, progress, file_path, error, created_at, completed_at = row
                if status == "completed" and file_path and os.path.exists(file_path):
                    if output and os.path.abspath(file_path) != os.path.abspath(output):
                        out_dir = os.path.dirname(output)
                        if out_dir:
                            os.makedirs(out_dir, exist_ok=True)
                        if not os.path.exists(output):
                            shutil.copy2(file_path, output)
                        try:
                            ldb.update_generated_video(job_id=job_id, file_path=output)
                        except Exception:
                            pass
                        print(f"Cache hit for code {rcode}; returning {output}")
                        return output
                    print(f"Cache hit for code {rcode}; returning {file_path}")
                    return file_path
        except Exception as e:
            print(f"Cache lookup error (non-fatal): {e}")

    resolved_reference = _prepare_reference(input_reference)
    video = create_video(
        client,
        prompt=prompt,
        model=model,
        size=size,
        seconds=seconds,
        input_reference=resolved_reference,
    )
    vid0 = getattr(video, "id", None) or (video.get("id") if isinstance(video, dict) else None)
    status0 = getattr(video, "status", None) or (video.get("status") if isinstance(video, dict) else "queued")
    progress0 = getattr(video, "progress", None) or (video.get("progress") if isinstance(video, dict) else 0)
    seconds0 = getattr(video, "seconds", None) or (video.get("seconds") if isinstance(video, dict) else seconds)
    size0 = getattr(video, "size", None) or (video.get("size") if isinstance(video, dict) else size)
    model0 = getattr(video, "model", None) or (video.get("model") if isinstance(video, dict) else model)
    print(f"Video generation started: id={vid0} model={model0} size={size0} seconds={seconds0} status={status0}")

    # Record job in Postgres cache
    try:
        ldb.record_generated_video(
            job_id=str(vid0),
            model=model,
            prompt=prompt,
            size=size,
            seconds=seconds,
            status=str(status0),
            progress=int(progress0) if isinstance(progress0, (int, float)) else 0,
            request_hash=rhash,
        )
    except Exception as e:
        print(f"DB record error (non-fatal): {e}")

    start = time.time()
    # Normalize response across SDK/HTTP
    progress = (getattr(video, "progress", None) or (video.get("progress") if isinstance(video, dict) else 0) or 0)
    bar_len = 30
    interactive = sys.stdout.isatty()
    last_status = None
    last_progress_int = None

    def _status(v):
        return getattr(v, "status", None) or (v.get("status") if isinstance(v, dict) else None)

    while _status(video) in ("queued", "in_progress"):
        if time.time() - start > timeout_seconds:
            raise TimeoutError("Timed out waiting for video to complete")

        status_txt = "Queued" if _status(video) == "queued" else "Processing"
        try:
            progress_float = float(progress)
        except Exception:
            progress_float = 0.0
        progress_int = int(progress_float)
        if interactive:
            filled = int((progress_float / 100.0) * bar_len)
            bar = "=" * filled + "-" * (bar_len - filled)
            sys.stdout.write(f"\r{status_txt}: [{bar}] {progress_float:.1f}%")
            sys.stdout.flush()
        else:
            if status_txt != last_status or progress_int != last_progress_int:
                print(f"{status_txt}: {progress_int}%")
                last_status = status_txt
                last_progress_int = progress_int

        time.sleep(poll_interval)
        vid = getattr(video, "id", None) or (video.get("id") if isinstance(video, dict) else None)
        video = retrieve_status(client, vid)
        progress = (getattr(video, "progress", None) or (video.get("progress") if isinstance(video, dict) else 0) or 0)
        try:
            ldb.update_generated_video(
                job_id=str(vid),
                status=str(_status(video)) if _status(video) else None,
                progress=int(progress) if isinstance(progress, (int, float)) else None,
            )
        except Exception as e:
            print(f"DB update error (non-fatal): {e}")

    # end of loop – newline for cleanliness (TTY only)
    if interactive:
        sys.stdout.write("\n")

    if _status(video) == "failed":
        err = None
        if isinstance(video, dict):
            err = (video.get("error") or {}).get("message")
        else:
            err = getattr(getattr(video, "error", None), "message", None)
        err = err or "unknown error"
        try:
            ldb.update_generated_video(job_id=str(vid), status="failed", error=str(err))
        except Exception:
            pass
        raise RuntimeError(f"Video generation failed: {err}")

    print("Video generation completed:", video)
    print("Downloading video content…")
    vid = getattr(video, "id", None) or (video.get("id") if isinstance(video, dict) else None)
    path = download_video(client, vid, out_path=output, variant="video")
    print(f"Wrote {path}")
    try:
        completed = getattr(video, "completed_at", None) or (video.get("completed_at") if isinstance(video, dict) else None)
        ldb.update_generated_video(
            job_id=str(vid),
            status="completed",
            progress=100,
            file_path=path,
            completed_at=str(completed) if completed else None,
        )
    except Exception as e:
        print(f"DB finalize error (non-fatal): {e}")
    return path


def _parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Create a Sora 2 video and download the result")
    p.add_argument("--prompt", required=True, help="Text prompt describing the video")
    p.add_argument("--model", default="sora-2", choices=["sora-2", "sora-2-pro"], help="Video model")
    p.add_argument("--size", default="1280x720", help="Resolution, e.g. 1280x720 or 720x1280")
    p.add_argument("--seconds", type=int, default=8, help="Video length in seconds")
    p.add_argument("--output", default="video.mp4", help="Output mp4 path")
    p.add_argument("--interval", type=float, default=10.0, help="Polling interval seconds")
    p.add_argument("--timeout", type=int, default=1800, help="Timeout seconds")
    p.add_argument("--no-cache", action="store_true", help="Disable DB cache; always create a new job")
    return p.parse_args(argv)


def main(argv: list[str]) -> int:
    # Ensure API key is present
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY is not set in the environment", file=sys.stderr)
        return 2
    args = _parse_args(argv)
    try:
        create_poll_and_download(
            prompt=args.prompt,
            model=args.model,
            size=args.size,
            seconds=args.seconds,
            output=args.output,
            poll_interval=args.interval,
            timeout_seconds=args.timeout,
            use_cache=not args.no_cache,
        )
        return 0
    except Exception as e:
        print(f"Failed: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
