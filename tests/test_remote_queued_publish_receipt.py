"""A remote queued receipt is already dispatched, not fresh local work."""
import ast
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

from lazyedit.publish_dispatch import find_uncertain_dispatch_receipt


def merge_function():
    source = Path(__file__).resolve().parents[1] / "app.py"
    tree = ast.parse(source.read_text())
    namespace = {
        "ldb": SimpleNamespace(update_publish_job=Mock()),
        "find_uncertain_dispatch_receipt": find_uncertain_dispatch_receipt,
        "PUBLISH_QUEUE_HISTORY_LIMIT": 50,
    }
    selected = ast.Module(body=[node for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "_merge_publish_queue_jobs"],
        type_ignores=[])
    exec(compile(selected, str(source), "exec"), namespace)
    return namespace["_merge_publish_queue_jobs"], namespace["ldb"].update_publish_job


def jobs():
    local = dict(id=546, source="local", status="running", internal_status="running",
                 filename="poster.zip", platforms=["shipinhao", "youtube"],
                 remote_job_id=None, error=None)
    remote = dict(id="job-remote", source="remote", status="queued", remote_status="queued",
                  remote_job_id="job-remote", filename="poster.zip",
                  platforms=["shipinhao", "youtube"])
    return local, remote


def test_receipt_keeps_local_worker_busy_while_ui_shows_remote_queue():
    merge, update = merge_function()
    local, remote = jobs()
    result = merge([local], [remote], remote_queue_available=True)
    assert len(result) == 1
    assert result[0]["status"] == "queued"
    assert result[0]["internal_status"] == "running"
    assert update.call_args.kwargs["status"] == "running"
    assert update.call_args.kwargs["remote_job_id"] == "job-remote"
    assert update.call_args.kwargs["remote_status"] == "queued"


def test_matching_receipt_repairs_false_conflict_without_a_new_dispatch():
    merge, update = merge_function()
    local, remote = jobs()
    local.update(status="failed", internal_status="failed", remote_job_id="job-remote",
                 detail="Publish failed", error="Package is used by a queued/running job")
    result = merge([local], [remote], remote_queue_available=True)
    assert result[0]["status"] == "queued"
    assert result[0]["internal_status"] == "running"
    assert result[0]["error"] is None
    assert update.call_args.kwargs["status"] == "running"
    assert update.call_args.kwargs["remote_job_id"] == "job-remote"


def test_native_terminal_failure_is_not_changed_into_running():
    merge, update = merge_function()
    local, remote = jobs()
    local["remote_job_id"] = "job-remote"
    remote.update(status="failed", remote_status="failed", error="native validation failed")
    result = merge([local], [remote], remote_queue_available=True)
    assert result[0]["status"] == "failed"
    assert result[0]["error"] == "native validation failed"
    assert update.call_args.kwargs["status"] == "failed"


def test_completed_native_receipt_still_finishes_the_local_job():
    merge, update = merge_function()
    local, remote = jobs()
    local["remote_job_id"] = "job-remote"
    remote.update(status="done", remote_status="done")
    result = merge([local], [remote], remote_queue_available=True)
    assert result[0]["status"] == "done"
    assert update.call_args.kwargs["status"] == "done"
    assert update.call_args.kwargs["finished"] is True
