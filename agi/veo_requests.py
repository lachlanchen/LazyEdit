from __future__ import annotations

import hashlib
import json
import os
import time
from typing import Optional

import httpx

from lazyedit import db as ldb


def _get_veo_base_url() -> str:
    base = os.getenv("GRSAI_API_BASE") or os.getenv("VEO_API_BASE")
    if not base:
        raise RuntimeError("GRSAI_API_BASE (or VEO_API_BASE) is not set")
    return base.rstrip("/")


def _get_veo_headers() -> dict[str, str]:
    api_key = os.getenv("GRSAI_API_KEY") or os.getenv("VEO_API_KEY")
    if not api_key:
        raise RuntimeError("GRSAI_API_KEY (or VEO_API_KEY) is not set")
    header_name = os.getenv("GRSAI_API_KEY_HEADER", "Authorization")
    header_value = api_key
    if header_name.lower() == "authorization" and not api_key.lower().startswith("bearer "):
        header_value = f"Bearer {api_key}"
    return {header_name: header_value, "Content-Type": "application/json"}


def _unwrap_response(payload: dict) -> dict:
    if not isinstance(payload, dict):
        return {}
    data = payload.get("data")
    if isinstance(data, dict):
        return data
    return payload


def _raise_for_code(payload: dict, context: str) -> None:
    if not isinstance(payload, dict):
        return
    if "code" not in payload:
        return
    try:
        code_val = int(payload.get("code"))
    except Exception:
        return
    if code_val == 0:
        return
    message = payload.get("msg") or payload.get("error") or "unknown error"
    raise RuntimeError(f"{context} {code_val}: {message}")


def _download_url(url: str, output: str) -> str:
    with httpx.Client(timeout=None) as client:
        resp = client.get(url)
        if resp.status_code >= 400:
            raise RuntimeError(f"Download failed {resp.status_code}: {resp.text}")
        with open(output, "wb") as handle:
            handle.write(resp.content)
    return output


def create_veo_job(
    *,
    prompt: str,
    model: str,
    aspect_ratio: Optional[str] = None,
    reference_url: Optional[str] = None,
) -> dict:
    payload: dict = {"model": model, "prompt": prompt, "webHook": "-1"}
    if aspect_ratio:
        payload["aspectRatio"] = aspect_ratio
    if reference_url:
        payload["urls"] = [reference_url]

    base_url = _get_veo_base_url()
    headers = _get_veo_headers()
    with httpx.Client(timeout=60.0) as client:
        resp = client.post(f"{base_url}/v1/video/veo", headers=headers, json=payload)
    if resp.status_code >= 400:
        raise RuntimeError(f"POST /v1/video/veo {resp.status_code}: {resp.text}")
    parsed = resp.json()
    _raise_for_code(parsed, "POST /v1/video/veo")
    return _unwrap_response(parsed)


def fetch_veo_result(job_id: str) -> dict:
    base_url = _get_veo_base_url()
    headers = _get_veo_headers()
    with httpx.Client(timeout=60.0) as client:
        resp = client.post(f"{base_url}/v1/draw/result", headers=headers, json={"id": job_id})
    if resp.status_code >= 400:
        raise RuntimeError(f"POST /v1/draw/result {resp.status_code}: {resp.text}")
    parsed = resp.json()
    _raise_for_code(parsed, "POST /v1/draw/result")
    return _unwrap_response(parsed)


def create_veo_video_and_download(
    *,
    prompt: str,
    model: str,
    aspect_ratio: str,
    output: str,
    reference_url: Optional[str] = None,
    poll_interval: float = 10.0,
    timeout_seconds: int = 30 * 60,
    use_cache: bool = True,
    size: Optional[str] = None,
    seconds: Optional[int] = None,
) -> str:
    payload = {"model": model, "prompt": prompt, "aspectRatio": aspect_ratio, "reference": reference_url}
    key = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    rhash = hashlib.sha256(key.encode("utf-8")).hexdigest()
    rcode = rhash[:12]
    print(f"Request code: {rcode}")

    if use_cache:
        try:
            row = ldb.find_generated_by_hash(rhash)
            if row:
                job_id, status, _progress, file_path, _error, _created_at, _completed_at = row
                if status == "completed" and file_path and os.path.exists(file_path):
                    if output and os.path.abspath(file_path) != os.path.abspath(output):
                        os.makedirs(os.path.dirname(output), exist_ok=True)
                        if not os.path.exists(output):
                            _download_url(file_path, output) if file_path.startswith("http") else None
                            if not file_path.startswith("http"):
                                import shutil
                                shutil.copy2(file_path, output)
                        try:
                            ldb.update_generated_video(job_id=job_id, file_path=output)
                        except Exception:
                            pass
                        print(f"Cache hit for code {rcode}; returning {output}")
                        return output
                    print(f"Cache hit for code {rcode}; returning {file_path}")
                    return file_path
        except Exception as exc:
            print(f"Cache lookup error (non-fatal): {exc}")

    job = create_veo_job(prompt=prompt, model=model, aspect_ratio=aspect_ratio, reference_url=reference_url)
    job_id = job.get("id")
    if not job_id:
        raise RuntimeError(f"Veo job creation failed: {job}")
    status = job.get("status", "queued")
    progress = int(job.get("progress", 0) or 0)
    print(f"Video generation started: id={job_id} model={model} aspect={aspect_ratio} status={status}")

    try:
        ldb.record_generated_video(
            job_id=str(job_id),
            model=model,
            prompt=prompt,
            size=size,
            seconds=seconds,
            status=str(status),
            progress=progress,
            request_hash=rhash,
        )
    except Exception as exc:
        print(f"DB record error (non-fatal): {exc}")

    start = time.time()
    last_status = None
    last_progress = None
    while True:
        if time.time() - start > timeout_seconds:
            raise RuntimeError("Veo generation timed out.")
        result = fetch_veo_result(str(job_id))
        status = str(result.get("status") or "").lower()
        progress = int(result.get("progress", 0) or 0)
        if status != last_status or progress != last_progress:
            label = status or "unknown"
            print(f"Veo status: {label} {progress}%")
            last_status = status
            last_progress = progress
        try:
            ldb.update_generated_video(job_id=str(job_id), status=status, progress=progress)
        except Exception:
            pass

        if status == "succeeded":
            url = result.get("url")
            if not url:
                raise RuntimeError("Veo succeeded but no url returned.")
            os.makedirs(os.path.dirname(output), exist_ok=True)
            _download_url(url, output)
            try:
                ldb.update_generated_video(job_id=str(job_id), status="completed", progress=100, file_path=output)
            except Exception:
                pass
            return output

        if status == "failed":
            failure_reason = result.get("failure_reason") or result.get("error") or "unknown"
            try:
                ldb.update_generated_video(job_id=str(job_id), status="failed", error=str(failure_reason))
            except Exception:
                pass
            raise RuntimeError(f"Veo generation failed: {failure_reason}")

        time.sleep(poll_interval)
