import os
import time
from datetime import datetime
from typing import Any

import requests


DEFAULT_VIDEO_POLL_INTERVAL = float(os.getenv("VENICE_VIDEO_POLL_INTERVAL_SECONDS", "5"))
DEFAULT_VIDEO_POLL_TIMEOUT = float(os.getenv("VENICE_VIDEO_POLL_TIMEOUT_SECONDS", "1800"))
DEFAULT_VIDEO_POLL_LOG_SECONDS = float(os.getenv("VENICE_VIDEO_POLL_LOG_SECONDS", "15"))


def _utc_timestamp() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


def _log_event(
    events: list[dict[str, Any]],
    stage: str,
    message: str,
    data: dict[str, Any] | None = None,
) -> None:
    payload: dict[str, Any] = {
        "ts": _utc_timestamp(),
        "stage": stage,
        "message": message,
    }
    if data:
        payload["data"] = data
    events.append(payload)
    print(f"[V+Wan] {stage}: {message}")


class VeniceVideoClient:
    def __init__(self) -> None:
        self.api_base = os.getenv("VENICE_API_BASE", "https://api.venice.ai/api/v1").rstrip("/")
        self.api_key = os.getenv("VENICE_API_KEY", "").strip()
        self.queue_endpoint = os.getenv("VENICE_VIDEO_QUEUE_ENDPOINT", "/video/queue")
        self.retrieve_endpoint = os.getenv("VENICE_VIDEO_RETRIEVE_ENDPOINT", "/video/retrieve")
        self.complete_endpoint = os.getenv("VENICE_VIDEO_COMPLETE_ENDPOINT", "/video/complete")
        self.timeout = float(os.getenv("VENICE_VIDEO_TIMEOUT_SECONDS", "60"))
        self.session = requests.Session()
        if self.api_key:
            self.session.headers.update({"Authorization": f"Bearer {self.api_key}"})
        self.session.headers.update({"Content-Type": "application/json"})

    def queue(self, payload: dict[str, Any]) -> dict[str, Any]:
        url = f"{self.api_base}{self.queue_endpoint}"
        response = self.session.post(url, json=payload, timeout=self.timeout)
        if not response.ok:
            raise RuntimeError(f"Venice queue failed ({response.status_code}): {response.text}")
        data = response.json()
        if not isinstance(data, dict) or not data.get("queue_id"):
            raise RuntimeError(f"Venice queue response missing queue_id: {data}")
        return data

    def retrieve(
        self,
        model: str,
        queue_id: str,
        delete_media_on_completion: bool = False,
        stream: bool = False,
    ) -> requests.Response:
        url = f"{self.api_base}{self.retrieve_endpoint}"
        payload = {
            "model": model,
            "queue_id": queue_id,
            "delete_media_on_completion": delete_media_on_completion,
        }
        return self.session.post(url, json=payload, timeout=self.timeout, stream=stream)

    def complete(self, model: str, queue_id: str) -> dict[str, Any]:
        url = f"{self.api_base}{self.complete_endpoint}"
        payload = {"model": model, "queue_id": queue_id}
        response = self.session.post(url, json=payload, timeout=self.timeout)
        if not response.ok:
            raise RuntimeError(f"Venice complete failed ({response.status_code}): {response.text}")
        return response.json()


def poll_venice_video(
    client: VeniceVideoClient,
    model: str,
    queue_id: str,
    output_path: str,
    events: list[dict[str, Any]],
    poll_interval: float | None = None,
    poll_timeout: float | None = None,
    delete_media_on_completion: bool = False,
) -> dict[str, Any]:
    interval = poll_interval if poll_interval is not None else DEFAULT_VIDEO_POLL_INTERVAL
    timeout = poll_timeout if poll_timeout is not None else DEFAULT_VIDEO_POLL_TIMEOUT
    log_every = DEFAULT_VIDEO_POLL_LOG_SECONDS
    start = time.time()
    attempt = 0
    last_log = -1.0
    last_status = None

    while True:
        attempt += 1
        elapsed = time.time() - start
        if elapsed > timeout:
            raise TimeoutError(f"Venice video timed out (elapsed={elapsed:.0f}s)")

        response = client.retrieve(
            model=model,
            queue_id=queue_id,
            delete_media_on_completion=delete_media_on_completion,
            stream=True,
        )
        try:
            if response.status_code >= 400:
                raise RuntimeError(f"Venice retrieve failed ({response.status_code}): {response.text}")

            content_type = (response.headers.get("content-type") or "").split(";")[0].strip().lower()
            if content_type.startswith("video/") or content_type == "application/octet-stream":
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                with open(output_path, "wb") as handle:
                    for chunk in response.iter_content(chunk_size=1024 * 1024):
                        if chunk:
                            handle.write(chunk)
                _log_event(events, "venice_video", "Video ready.", {"queue_id": queue_id})
                return {"status": "ready", "output_path": output_path}

            try:
                payload = response.json()
            except Exception:
                payload = {"raw": response.text}

            status = None
            if isinstance(payload, dict):
                status = payload.get("status")
                last_status = status or last_status

            if log_every and (last_log < 0 or elapsed - last_log >= log_every):
                last_log = elapsed
                info = {"attempt": attempt, "elapsed": round(elapsed, 1)}
                if status:
                    info["status"] = status
                if isinstance(payload, dict):
                    for key in ("average_execution_time", "execution_duration"):
                        if key in payload:
                            info[key] = payload.get(key)
                _log_event(events, "venice_video", "Polling video status.", info)

            if status and str(status).upper() not in {"PROCESSING", "IN_PROGRESS", "QUEUED"}:
                raise RuntimeError(f"Venice video failed: {payload}")
        finally:
            response.close()

        time.sleep(interval)
