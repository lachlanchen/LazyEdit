from lazyedit.publish_dispatch import find_uncertain_dispatch_receipt


LOCAL = dict(source="local", status="failed", filename="clip.zip",
             platforms=["douyin", "youtube"], error="Read timed out. (read timeout=60)",
             started_at="2026-11-08 20:01:27", finished_at="2026-11-08 20:02:33")
REMOTE = dict(remote_job_id="job-1", filename="clip.zip", platforms=["youtube", "douyin"],
              status="done", created_at="2026-11-08 20:02:39")


def test_lost_acknowledgment_matches_existing_completed_job():
    assert find_uncertain_dispatch_receipt(LOCAL, [REMOTE]) == REMOTE


def test_new_unknown_dispatch_matches_running_job():
    local = dict(LOCAL, status="running", remote_status="dispatch_unknown", error=None)
    remote = dict(REMOTE, status="running")
    assert find_uncertain_dispatch_receipt(local, [remote]) == remote


def test_old_wrong_platform_and_ambiguous_receipts_are_not_adopted():
    for remote in [dict(REMOTE, created_at="2026-11-08 19:00:00"),
                   dict(REMOTE, created_at="2026-11-08 21:00:00"),
                   dict(REMOTE, platforms=["youtube"]),
                   dict(REMOTE, filename="another.zip")]:
        assert find_uncertain_dispatch_receipt(LOCAL, [remote]) is None
    assert find_uncertain_dispatch_receipt(LOCAL, [REMOTE, dict(REMOTE, remote_job_id="job-2")]) is None


def test_known_job_or_unrelated_failure_is_never_rebound():
    assert find_uncertain_dispatch_receipt(dict(LOCAL, remote_job_id="known"), [REMOTE]) is None
    assert find_uncertain_dispatch_receipt(dict(LOCAL, error="subtitle failed"), [REMOTE]) is None
    assert find_uncertain_dispatch_receipt(dict(LOCAL, source="remote"), [REMOTE]) is None
