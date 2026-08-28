from scripts.lazyedit_publish import (
    default_steps,
    process_errors_after_start,
    process_ready_with_options,
    requested_process_ready,
    should_defer_processing_to_publish_queue,
    sync_burn_layout_languages,
)


def test_default_publish_steps_do_not_require_optional_frame_captioning():
    assert "caption" not in default_steps(True, logo_enabled=True, portrait_enabled=True)
    assert "caption" not in default_steps(False, logo_enabled=True)
    assert "caption" not in default_steps(False)


def test_failed_optional_frame_caption_does_not_block_ready_video():
    payload = {
        "steps": {
            "transcribe": {"status": "done"},
            "polish": {"status": "done"},
            "keyframes": {"status": "done"},
            "caption": {"status": "error", "detail": "caption backend unavailable"},
            "metadata_zh": {"status": "done"},
            "metadata_en": {"status": "done"},
            "cover": {"status": "done"},
            "translate": {"status": "done"},
            "burn": {"status": "done"},
        }
    }

    assert process_ready_with_options(payload, burn_subtitles=True, logo_enabled=True)


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


def test_language_override_updates_visible_slots_in_top_to_bottom_order():
    layout = {
        "rows": 4,
        "slots": [
            {"slot": 1, "language": "en", "fontScale": 1.0},
            {"slot": 2, "language": "ja", "fontScale": 0.9},
            {"slot": 3, "language": "zh-Hant", "fontScale": 0.8},
            {"slot": 4, "language": "fr", "fontScale": 0.7},
        ],
    }

    updated = sync_burn_layout_languages(layout, ["it", "zh-Hant", "ja", "en"])

    assert updated["rows"] == 4
    assert [slot["language"] for slot in updated["slots"]] == [
        "en",
        "ja",
        "zh-Hant",
        "it",
    ]
    assert [slot["fontScale"] for slot in updated["slots"]] == [1.0, 0.9, 0.8, 0.7]
