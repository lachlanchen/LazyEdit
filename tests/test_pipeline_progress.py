from lazyedit.pipeline_progress import PipelineProgress


def test_duplicate_preparation_is_refused_until_the_first_finishes():
    progress = PipelineProgress()
    key = (1, None)
    assert progress.start(key)
    progress.step(key, "caption", "working", "Captioning")
    assert not progress.start(key)
    assert progress.get(key)["steps"]["caption"]["status"] == "working"
    progress.finish(key, False, "caption failed")
    assert progress.get(key)["status"] == "error"
    assert progress.start(key)
    assert progress.get(key)["steps"] == {}


def test_sessions_are_independent_and_retention_preserves_active_work():
    progress = PipelineProgress(limit=2)
    assert progress.start((1, 1))
    assert progress.start((1, 2))
    progress.finish((1, 2), True)
    assert progress.start((2, None))
    assert progress.get((1, 1))["status"] == "working"
    assert progress.get((1, 2)) is None
    assert not progress.start((3, None))


def test_operation_identity_and_step_checkpoint_times_are_visible():
    progress = PipelineProgress()
    key = (2, None)
    assert progress.start(key, "original-preparation-operation")
    progress.step(key, "transcribe", "done", "Completed")
    row = progress.get(key)
    assert row["operation_id"] == "original-preparation-operation"
    assert row["steps"]["transcribe"]["updated_at"] == row["updated_at"]
