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
import sys
import time
from typing import Optional

from openai import OpenAI
import httpx


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
    with httpx.Client(timeout=60.0) as s:
        r = s.post(
            "https://api.openai.com/v1/videos",
            headers={"Authorization": f"Bearer {token}"},
            files=form,
        )
        r.raise_for_status()
        return r.json()


def retrieve_status(client: OpenAI, video_id: str):
    if _have_sdk_videos(client):
        return client.videos.retrieve(video_id)
    token = os.getenv("OPENAI_API_KEY")
    if not token:
        raise RuntimeError("OPENAI_API_KEY not set for HTTP fallback")
    with httpx.Client(timeout=60.0) as s:
        r = s.get(
            f"https://api.openai.com/v1/videos/{video_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        r.raise_for_status()
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
    with httpx.Client(timeout=None) as s:
        r = s.get(
            f"https://api.openai.com/v1/videos/{video_id}/content",
            headers={"Authorization": f"Bearer {token}"},
            params={"variant": variant} if variant else None,
        )
        r.raise_for_status()
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
    poll_interval: float = 10.0,
    timeout_seconds: int = 30 * 60,
) -> str:
    client = OpenAI()
    # Ensure output directory exists
    out_dir = os.path.dirname(output)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    video = create_video(client, prompt=prompt, model=model, size=size, seconds=seconds)
    print("Video generation started:", video)

    start = time.time()
    # Normalize response across SDK/HTTP
    progress = (getattr(video, "progress", None) or (video.get("progress") if isinstance(video, dict) else 0) or 0)
    bar_len = 30

    def _status(v):
        return getattr(v, "status", None) or (v.get("status") if isinstance(v, dict) else None)

    while _status(video) in ("queued", "in_progress"):
        if time.time() - start > timeout_seconds:
            raise TimeoutError("Timed out waiting for video to complete")

        # progress bar
        filled = int((float(progress) / 100.0) * bar_len)
        bar = "=" * filled + "-" * (bar_len - filled)
        status_txt = "Queued" if _status(video) == "queued" else "Processing"
        sys.stdout.write(f"\r{status_txt}: [{bar}] {progress:.1f}%")
        sys.stdout.flush()

        time.sleep(poll_interval)
        vid = getattr(video, "id", None) or (video.get("id") if isinstance(video, dict) else None)
        video = retrieve_status(client, vid)
        progress = (getattr(video, "progress", None) or (video.get("progress") if isinstance(video, dict) else 0) or 0)

    # end of loop – newline for cleanliness
    sys.stdout.write("\n")

    if _status(video) == "failed":
        err = None
        if isinstance(video, dict):
            err = (video.get("error") or {}).get("message")
        else:
            err = getattr(getattr(video, "error", None), "message", None)
        err = err or "unknown error"
        raise RuntimeError(f"Video generation failed: {err}")

    print("Video generation completed:", video)
    print("Downloading video content…")
    vid = getattr(video, "id", None) or (video.get("id") if isinstance(video, dict) else None)
    path = download_video(client, vid, out_path=output, variant="video")
    print(f"Wrote {path}")
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
        )
        return 0
    except Exception as e:
        print(f"Failed: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
