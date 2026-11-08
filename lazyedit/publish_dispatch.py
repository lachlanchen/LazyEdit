"""Reconcile an uncertain dispatch without sending another publication."""
from datetime import datetime, timedelta


def _local_time(value):
    try:
        value = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return value.astimezone().replace(tzinfo=None) if value.tzinfo else value
    except (TypeError, ValueError):
        return None


def find_uncertain_dispatch_receipt(local, remote_jobs):
    if local.get("source") != "local" or local.get("remote_job_id"):
        return None
    uncertain = local.get("remote_status") == "dispatch_unknown"
    # Recover older records produced before unknown dispatch was distinguished.
    legacy_timeout = (local.get("status") == "failed"
                      and "read timed out" in str(local.get("error") or "").lower())
    if not (uncertain or legacy_timeout) or not local.get("filename"):
        return None
    start = _local_time(local.get("started_at"))
    observed = _local_time(local.get("finished_at") or local.get("updated_at"))
    if start is None or observed is None:
        return None
    platforms = set(local.get("platforms") or [])
    matches = []
    for remote in remote_jobs:
        created = _local_time(remote.get("created_at"))
        if (remote.get("filename") == local["filename"]
                and platforms and set(remote.get("platforms") or []) == platforms
                and remote.get("remote_job_id") and created is not None
                and start <= created <= observed + timedelta(minutes=5)):
            matches.append(remote)
    # Neither an older post nor an ambiguous pair is a receipt for this intent.
    return matches[0] if len(matches) == 1 else None
