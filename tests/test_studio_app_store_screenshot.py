"""Exercise asset reconciliation without a store key or provider requests."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

from PIL import Image
import pytest
import requests


@pytest.fixture
def upload(monkeypatch, tmp_path):
    spec = importlib.util.spec_from_file_location(
        "studio_screenshot", Path(__file__).parents[1]/"scripts/studio/app_store_screenshot.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    file = tmp_path/"reviewed.png"
    Image.new("RGB", (1320, 2868), "blue").save(file)
    raw = file.read_bytes()
    key = tmp_path/"test-key"
    key.write_text("test-only-placeholder")
    monkeypatch.setattr(sys, "argv", ["upload", str(file), "--sha256",
        hashlib.sha256(raw).hexdigest(), "--display", "APP_IPHONE_67", "--key", str(key)])
    monkeypatch.setattr(module.jwt, "encode", lambda *args, **kwargs: "test-only-token")
    monkeypatch.setattr(module.time, "sleep", lambda seconds: None)
    asset = {"id": "asset", "attributes": {"fileName": file.name, "fileSize": len(raw),
        "sourceFileChecksum": hashlib.md5(raw).hexdigest(),
        "assetDeliveryState": {"state": "COMPLETE"}}}
    calls = []
    deliveries = []

    class Response:
        content = b"{}"

        def __init__(self, data):
            self.data = data

        def raise_for_status(self):
            pass

        def json(self):
            return self.data

    class Session:
        headers = {}

        def request(self, method, url, **kwargs):
            calls.append((method, url))
            path = url.split("/v1/")[1]
            data = {
                "apps/6814061525": {"attributes": {"bundleId": "art.lazying.lazyedit"}},
                "apps/6814061525/appStoreVersions": [{"id": "version", "attributes": {
                    "platform": "IOS", "versionString": "1.0", "appStoreState": "PREPARE_FOR_SUBMISSION"}}],
                "appStoreVersions/version/appStoreVersionLocalizations": [{"id": "locale", "attributes": {"locale": "en-US"}}],
                "appStoreVersionLocalizations/locale/appScreenshotSets": [{"id": "set", "attributes": {"screenshotDisplayType": "APP_IPHONE_67"}}],
                "appScreenshotSets/set/appScreenshots": [asset],
                "appScreenshots/asset": asset,
            }[path]
            if path == "appScreenshots/asset" and deliveries:
                data = {**asset, "attributes": {**asset["attributes"],
                    "assetDeliveryState": {"state": deliveries.pop(0)}}}
            return Response({"data": data})

    monkeypatch.setattr(module.requests, "Session", Session)
    return module, asset, calls, deliveries, raw


def test_reuses_complete_asset_without_upload(upload, capsys):
    module, asset, calls, _, _ = upload
    module.main()
    receipt = json.loads(capsys.readouterr().out)
    assert receipt["complete"] and receipt["checksumMatches"]
    assert receipt["assetId"] == "asset"
    assert all(method == "GET" for method, _ in calls)


def test_rejects_mac_display_on_ios_before_provider_request(upload, monkeypatch):
    module, _, calls, _, _ = upload
    monkeypatch.setattr(sys, "argv", [*sys.argv, "--platform", "MAC_OS"])
    with pytest.raises(ValueError, match="does not match the platform"):
        module.main()
    assert calls == []


def test_mac_assets_do_not_select_or_change_pending_ios_review(upload):
    module, _, calls, _, _ = upload
    ios = {"id": "ios", "attributes": {"platform": "IOS", "versionString": "1.0", "appStoreState": "WAITING_FOR_REVIEW"}}
    mac = {"id": "mac", "attributes": {"platform": "MAC_OS", "versionString": "1.0", "appStoreState": "PREPARE_FOR_SUBMISSION"}}
    assert module.editable_version([ios, mac], "MAC_OS", "1.0") is mac
    with pytest.raises(ValueError, match="Preserve"):
        module.editable_version([ios, mac], "IOS", "1.0")
    assert ios["attributes"]["appStoreState"] == "WAITING_FOR_REVIEW"
    assert calls == []


def test_reconciles_async_processing_without_reupload(upload, capsys):
    module, asset, calls, deliveries, _ = upload
    asset["attributes"]["assetDeliveryState"]["state"] = "UPLOAD_COMPLETE"
    deliveries.extend(["UPLOAD_COMPLETE", "COMPLETE"])
    module.main()
    assert json.loads(capsys.readouterr().out)["complete"]
    assert all(method == "GET" for method, _ in calls)


def test_bounded_wait_reports_pending_without_reupload(upload, capsys, monkeypatch):
    module, asset, calls, _, _ = upload
    monkeypatch.setattr(sys, "argv", [*sys.argv, "--wait-seconds", "0"])
    asset["attributes"]["assetDeliveryState"]["state"] = "UPLOAD_COMPLETE"
    module.main()
    assert not json.loads(capsys.readouterr().out)["complete"]
    assert all(method == "GET" for method, _ in calls)


def test_rejects_conflicting_existing_asset(upload):
    module, asset, calls, _, _ = upload
    asset["attributes"]["sourceFileChecksum"] = "different"
    with pytest.raises(ValueError, match="will not be overwritten"):
        module.main()
    assert all(method == "GET" for method, _ in calls)


def test_transfer_error_redacts_signed_url_and_does_not_forward_token(upload, monkeypatch):
    module, asset, calls, _, raw = upload
    asset["attributes"].update({"sourceFileChecksum": None,
        "assetDeliveryState": {"state": "AWAITING_UPLOAD"}, "uploadOperations": [{
            "url": "https://upload.apple.com/asset?secret=private-signature", "method": "PUT",
            "offset": 0, "length": len(raw), "requestHeaders": []}]})

    def fail(url, **kwargs):
        assert "Authorization" not in kwargs["headers"]
        assert "Cookie" not in kwargs["headers"]
        assert not kwargs["allow_redirects"]
        raise requests.ConnectionError(url)

    monkeypatch.setattr(module.requests, "put", fail)
    with pytest.raises(RuntimeError, match="reconcile this asset") as exc:
        module.main()
    assert "private-signature" not in str(exc.value)
    assert exc.value.__suppress_context__
    assert all(method == "GET" for method, _ in calls)
