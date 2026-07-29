"""Sanitize and proxy AutoPublish operator-attention events."""

from __future__ import annotations

from typing import Any
from urllib.parse import quote, urljoin, urlsplit


ALLOWED_ATTENTION_STATUSES = {"required", "resolved"}
MAX_ATTENTION_TEXT = 500


def sanitize_remote_attention(
    remote_job_id: str | None,
    value: Any,
) -> dict[str, Any] | None:
    if not remote_job_id or not isinstance(value, dict):
        return None
    status = str(value.get("status") or "").strip().lower()
    kind = str(value.get("kind") or "").strip()[:80]
    platform = str(value.get("platform") or "").strip()[:80]
    try:
        revision = int(value.get("revision") or 0)
    except (TypeError, ValueError):
        return None
    if status not in ALLOWED_ATTENTION_STATUSES or not kind or revision < 1:
        return None

    result = {
        "platform": platform,
        "kind": kind,
        "status": status,
        "message": str(value.get("message") or "")[:MAX_ATTENTION_TEXT],
        "revision": revision,
        "created_at": value.get("created_at"),
        "updated_at": value.get("updated_at"),
        "media_type": str(value.get("media_type") or "")[:100],
    }
    if status == "required":
        encoded_job_id = quote(str(remote_job_id), safe="")
        result["artifact_url"] = (
            f"/api/autopublish/jobs/{encoded_job_id}/attention/{revision}"
        )
    return result


def find_remote_attention_artifact(
    jobs: list[dict[str, Any]],
    remote_job_id: str,
    revision: int,
) -> str | None:
    for job in jobs:
        if str(job.get("id") or job.get("job_id") or "") != str(remote_job_id):
            continue
        attention = job.get("attention")
        if not isinstance(attention, dict):
            return None
        try:
            current_revision = int(attention.get("revision") or 0)
        except (TypeError, ValueError):
            return None
        if (
            str(attention.get("status") or "").lower() != "required"
            or current_revision != int(revision)
        ):
            return None
        artifact_url = str(attention.get("artifact_url") or "").strip()
        parsed = urlsplit(artifact_url)
        if (
            not artifact_url.startswith("/")
            or parsed.scheme
            or parsed.netloc
            or not parsed.path.startswith("/publish/jobs/")
            or "/attention/" not in parsed.path
        ):
            return None
        return artifact_url
    return None


def same_origin_attention_url(
    autopublish_url: str,
    artifact_path: str,
) -> str | None:
    base = urlsplit(str(autopublish_url or ""))
    if base.scheme not in {"http", "https"} or not base.netloc:
        return None
    candidate = urlsplit(urljoin(autopublish_url, artifact_path))
    if (
        candidate.scheme != base.scheme
        or candidate.netloc != base.netloc
        or not candidate.path.startswith("/publish/jobs/")
        or "/attention/" not in candidate.path
    ):
        return None
    return candidate.geturl()
