from scripts.lazyedit_publish import (
    process_errors_after_start,
    requested_process_ready,
    should_defer_processing_to_publish_queue,
)


def test_unchanged_historical_burn_error_is_ignored():
    old_burn = {
        "status": "error",
        "detail": "old ffmpeg failure",
        "updated_at": "2026-07-14T00:23:51+08:00",
        "progress": 0,
    }
    payload = {"steps": {"translate": {"status": "working"}, "burn": dict(old_burn)}}

    assert process_errors_after_start(
        payload,
        baseline_steps={"burn": old_burn},
        requested_steps=["translate", "burn"],
        burn_subtitles=True,
    ) == []


def test_new_error_with_same_message_is_reported_by_timestamp():
    baseline = {
        "status": "error",
        "detail": "translation failed",
        "updated_at": "2026-07-14T00:23:51+08:00",
    }
    current = dict(baseline, updated_at="2026-07-14T00:45:21+08:00")

    assert process_errors_after_start(
        {"steps": {"translate": current}},
        baseline_steps={"translate": baseline},
        requested_steps=["burn"],
        burn_subtitles=True,
    ) == ["translate: translation failed"]


def test_selective_process_waits_only_for_requested_steps_and_dependencies():
    payload = {
        "steps": {
            "transcribe": {"status": "error"},
            "translate": {"status": "done"},
            "burn": {"status": "done"},
            "metadata_zh": {"status": "idle"},
        }
    }

    assert requested_process_ready(
        payload,
        requested_steps=["burn"],
        burn_subtitles=True,
        logo_enabled=True,
    )


def test_no_wait_process_publish_is_owned_by_serial_queue():
    assert should_defer_processing_to_publish_queue(process=True, publish=True, wait=False)
    assert not should_defer_processing_to_publish_queue(process=True, publish=False, wait=False)
    assert not should_defer_processing_to_publish_queue(process=True, publish=True, wait=True)
