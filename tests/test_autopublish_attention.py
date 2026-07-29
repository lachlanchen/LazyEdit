from lazyedit.autopublish_attention import (
    find_remote_attention_artifact,
    same_origin_attention_url,
    sanitize_remote_attention,
)


def test_required_attention_is_rewritten_to_lazyedit_proxy():
    result = sanitize_remote_attention(
        "job-123",
        {
            "platform": "shipinhao",
            "kind": "login_qr",
            "status": "required",
            "message": "Scan",
            "revision": 2,
            "artifact_url": "/publish/jobs/job-123/attention/2",
            "media_type": "image/png",
        },
    )
    assert result["artifact_url"] == (
        "/api/autopublish/jobs/job-123/attention/2"
    )
    assert result["revision"] == 2


def test_remote_artifact_must_match_exact_job_and_revision():
    jobs = [
        {
            "id": "job-123",
            "attention": {
                "status": "required",
                "revision": 2,
                "artifact_url": "/publish/jobs/job-123/attention/2",
            },
        }
    ]
    assert find_remote_attention_artifact(jobs, "job-123", 2) == (
        "/publish/jobs/job-123/attention/2"
    )
    assert find_remote_attention_artifact(jobs, "job-123", 1) is None
    assert find_remote_attention_artifact(jobs, "job-other", 2) is None


def test_attention_proxy_rejects_cross_origin_urls():
    base = "http://lazyingart:8081/publish"
    assert same_origin_attention_url(
        base,
        "/publish/jobs/job-123/attention/2",
    ) == "http://lazyingart:8081/publish/jobs/job-123/attention/2"
    assert same_origin_attention_url(
        base,
        "https://example.com/publish/jobs/job-123/attention/2",
    ) is None
