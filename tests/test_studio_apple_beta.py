"""TestFlight must deliver the native Mac build rather than an iOS build."""
import copy

import pytest

from scripts.studio import apple_beta as beta


class AppleFixture:
    def __init__(self):
        self.calls = []
        self.builds = [
            {"id": "ios", "attributes": {"version": "12", "processingState": "VALID", "expired": False}},
            {"id": "mac", "attributes": {"version": "12", "processingState": "VALID", "expired": False}},
        ]
        self.platforms = {"ios": "IOS", "mac": "MAC_OS"}
        self.attached = [{"type": "builds", "id": "ios"}]
        self.groups = [{"id": beta.GROUP, "attributes": {"isInternalGroup": True}}]

    def call(self, method, path, **kwargs):
        self.calls.append((method, path, kwargs))
        if path == "apps/" + beta.APP:
            return {"data": {"attributes": {"bundleId": beta.BUNDLE}}}
        if path.endswith("/betaGroups"):
            return {"data": self.groups}
        if path == "builds":
            return {"data": self.builds}
        if path.endswith("/preReleaseVersion"):
            return {"data": {"attributes": {"platform": self.platforms[path.split("/")[1]], "version": "1.0"}}}
        if path.endswith("/betaBuildLocalizations"):
            return {"data": [{"attributes": {"locale": "en-US"}}]}
        if path.endswith("/relationships/builds"):
            if method == "POST":
                self.attached += kwargs["json"]["data"]
            return {"data": copy.deepcopy(self.attached)}
        if path.endswith("/relationships/betaTesters"):
            return {"data": [{"id": "private-tester"}]}
        if path.endswith("/buildBetaDetail"):
            return {"data": {"attributes": {"internalBuildState": "IN_BETA_TESTING"}}}
        raise AssertionError((method, path))


def test_same_build_number_selects_mac_and_preserves_ios():
    api = AppleFixture()
    result = beta.operate(api, "attach", "12", "MAC_OS", "1.0", "Test both Mac architectures.")
    assert result["build"] == "mac" and result["attached"]
    assert api.attached == [{"type": "builds", "id": "ios"}, {"type": "builds", "id": "mac"}]
    assert [(m, p) for m, p, _ in api.calls if m != "GET"] == [
        ("POST", "betaGroups/" + beta.GROUP + "/relationships/builds")]
    api.calls.clear()
    beta.operate(api, "attach", "12", "MAC_OS", "1.0", "Same candidate.")
    assert all(method == "GET" for method, _, _ in api.calls)


@pytest.mark.parametrize("state,expired", [("PROCESSING", False), ("INVALID", False), ("VALID", True)])
def test_unready_mac_cannot_attach_ios_instead(state, expired):
    api = AppleFixture()
    api.builds[1]["attributes"].update(processingState=state, expired=expired)
    with pytest.raises(RuntimeError, match="VALID and unexpired"):
        beta.operate(api, "attach", "12", "MAC_OS", "1.0", "Test Mac.")
    assert all(method == "GET" for method, _, _ in api.calls)


def test_missing_marketing_version_never_falls_back():
    api = AppleFixture()
    assert beta.select_build(api, "12", "MAC_OS", "2.0") is None


def test_duplicate_mac_candidate_is_rejected_before_attachment():
    api = AppleFixture()
    duplicate = copy.deepcopy(api.builds[1]); duplicate["id"] = "other-mac"
    api.builds.append(duplicate); api.platforms["other-mac"] = "MAC_OS"
    with pytest.raises(RuntimeError, match="Ambiguous build"):
        beta.operate(api, "attach", "12", "MAC_OS", "1.0", "Test Mac.")
    assert all(method == "GET" for method, _, _ in api.calls)


def test_foreign_or_external_group_cannot_receive_build():
    for groups in [[], [{"id": beta.GROUP, "attributes": {"isInternalGroup": False}}]]:
        api = AppleFixture(); api.groups = groups
        with pytest.raises(RuntimeError, match="this app's private internal group"):
            beta.operate(api, "attach", "12", "MAC_OS", "1.0", "Test Mac.")
        assert all(method == "GET" for method, _, _ in api.calls)


def test_status_does_not_change_provider_state():
    api = AppleFixture()
    result = beta.operate(api, "status", "12", "MAC_OS", "1.0", "")
    assert result["build"] == "mac" and not result["attached"]
    assert all(method == "GET" for method, _, _ in api.calls)
