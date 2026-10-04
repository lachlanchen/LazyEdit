"""Mac release selection must never alter a pending iOS submission."""
import copy
import sys

import pytest

from scripts.studio import macos_store as store


def candidate(identifier, platform, state="VALID", expired=False):
    return {"id": identifier, "attributes": {"version": "12", "processingState": state,
                                              "expired": expired}, "platform": platform}


class AppleFixture:
    def __init__(self, pending=False, foreign_item=False):
        self.calls = []
        self.foreign_item = foreign_item
        self.builds = [candidate("ios-build", "IOS"), candidate("mac-build", "MAC_OS")]
        self.version_data = [
            {"id": "ios", "attributes": {"platform": "IOS", "versionString": "1.0",
                                            "appStoreState": "WAITING_FOR_REVIEW"}},
            {"id": "mac", "attributes": {"platform": "MAC_OS", "versionString": "1.0",
                                            "appStoreState": "WAITING_FOR_REVIEW" if pending else "PREPARE_FOR_SUBMISSION"}},
        ]

    def versions(self):
        return copy.deepcopy(self.version_data)

    def call(self, method, path, **kwargs):
        self.calls.append((method, path, kwargs))
        if path.startswith("builds?"):
            return {"data": self.builds}
        if path.startswith("builds/"):
            item = next(b for b in self.builds if b["id"] == path.split("/")[1])
            return {"data": {"attributes": {"platform": item["platform"], "version": "1.0"}}}
        if path.endswith("/reviewSubmissions"):
            return {"data": [{"id": "submission", "attributes": {"platform": "MAC_OS", "state": "READY_FOR_REVIEW"}}]}
        if path.endswith("/items?include=appStoreVersion"):
            return {"data": [{"id": "item", "relationships": {"appStoreVersion": {"data": {"id": "foreign"}}}}] if self.foreign_item else []}
        if path == "reviewSubmissions/submission":
            return {"data": {"attributes": {"state": "WAITING_FOR_REVIEW"}}}
        return {"data": {"id": "item"}}


def test_exact_mac_build_ignores_same_number_ios_build():
    api = AppleFixture()
    assert store.qualified_build(api, api.builds, "12", "1.0")["id"] == "mac-build"


@pytest.mark.parametrize("state,expired", [("PROCESSING", False), ("VALID", True), ("INVALID", False)])
def test_unready_candidate_is_never_submitted(state, expired):
    api = AppleFixture()
    api.builds[1]["attributes"].update(processingState=state, expired=expired)
    with pytest.raises(ValueError, match="unexpired VALID"):
        store.qualified_build(api, api.builds, "12", "1.0")
    assert all(method == "GET" for method, _, _ in api.calls)


def run(monkeypatch, api):
    monkeypatch.setattr(store, "Apple", lambda key: api)
    monkeypatch.setattr(sys, "argv", ["macos_store", "submit", "--build", "12"])
    store.main()


def test_submission_only_changes_mac_version_and_mac_review(monkeypatch):
    api = AppleFixture()
    run(monkeypatch, api)
    changes = [(method, path, args) for method, path, args in api.calls if method != "GET"]
    assert changes[0][1] == "appStoreVersions/mac/relationships/build"
    assert changes[0][2]["json"]["data"]["id"] == "mac-build"
    assert changes[-1][1] == "reviewSubmissions/submission"
    assert not any("ios" in path for _, path, _ in changes)
    assert api.version_data[0]["attributes"]["appStoreState"] == "WAITING_FOR_REVIEW"


def test_pending_review_is_reconciled_without_resubmitting(monkeypatch):
    api = AppleFixture(pending=True)
    run(monkeypatch, api)
    assert api.calls == []


def test_foreign_review_item_prevents_build_attachment(monkeypatch):
    api = AppleFixture(foreign_item=True)
    with pytest.raises(ValueError, match="Preserve other review items"):
        run(monkeypatch, api)
    assert all(method == "GET" for method, _, _ in api.calls)
