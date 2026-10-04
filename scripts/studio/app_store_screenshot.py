#!/usr/bin/env python
"""Upload a reviewed Studio screenshot without replacing assets or submitting review."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import time
from urllib.parse import urlsplit

import jwt
import requests

APP = "6814061525"
BUNDLE = "art.lazying.lazyedit"
SIZES = {"APP_IPHONE_67": {(1320, 2868), (1290, 2796), (1260, 2736)},
         "APP_IPAD_PRO_3GEN_129": {(2064, 2752), (2048, 2732)},
         "APP_DESKTOP": {(1280, 800), (1440, 900), (2560, 1600), (2880, 1800)}}


def editable_version(versions, platform, number):
    candidates = [v for v in versions if v["attributes"]["platform"] == platform
                  and v["attributes"]["versionString"] == number]
    if len(candidates) != 1 or candidates[0]["attributes"]["appStoreState"] != "PREPARE_FOR_SUBMISSION":
        raise ValueError("Preserve an existing review; expected an editable version of the requested platform")
    return candidates[0]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", type=Path)
    parser.add_argument("--sha256", required=True)
    parser.add_argument("--display", choices=SIZES, required=True)
    parser.add_argument("--locale", default="en-US")
    parser.add_argument("--platform", choices=["IOS", "MAC_OS"], default="IOS")
    parser.add_argument("--version", default="1.0")
    parser.add_argument("--wait-seconds", type=int, default=120,
                        help="Bounded wait for Apple's asynchronous asset processing")
    parser.add_argument("--key", type=Path, default=Path.home()/".config/echomind/private/AuthKey_6SSXT8QU6W.p8")
    args = parser.parse_args()
    if not 0 <= args.wait_seconds <= 300:
        parser.error("--wait-seconds must be between 0 and 300")
    if args.file.is_symlink() or not args.file.is_file():
        raise ValueError("Require a regular reviewed screenshot")
    raw = args.file.read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    if not 1000 < len(raw) < 20_000_000 or sha != args.sha256 or raw[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("Screenshot digest, size or PNG signature mismatch")
    if struct.unpack(">II", raw[16:24]) not in SIZES[args.display]:
        raise ValueError("Screenshot dimensions do not match this device class")
    if (args.platform == "MAC_OS") != (args.display == "APP_DESKTOP"):
        raise ValueError("Screenshot display does not match the platform")
    checksum = hashlib.md5(raw).hexdigest()
    session = requests.Session()
    session.headers["Authorization"] = "Bearer " + jwt.encode(
        {"iss": "741adba6-ef89-4e36-8a69-ff43ebfa9ecc", "iat": int(time.time()),
         "exp": int(time.time())+300, "aud": "appstoreconnect-v1"},
        args.key.read_text(), algorithm="ES256", headers={"kid": "6SSXT8QU6W"})

    def api(method, path, **kwargs):
        r = session.request(method, "https://api.appstoreconnect.apple.com/v1/"+path, timeout=45, **kwargs)
        r.raise_for_status()
        return r.json() if r.content else {}

    app = api("GET", "apps/"+APP)["data"]
    if app["attributes"]["bundleId"] != BUNDLE:
        raise ValueError("App identity mismatch")
    versions = api("GET", "apps/"+APP+"/appStoreVersions")["data"]
    version = editable_version(versions, args.platform, args.version)
    loc = api("GET", "appStoreVersions/"+version["id"]+"/appStoreVersionLocalizations")["data"]
    loc = [v for v in loc if v["attributes"]["locale"] == args.locale]
    if len(loc) != 1:
        raise ValueError("Expected exactly one existing localization")
    sets = api("GET", "appStoreVersionLocalizations/"+loc[0]["id"]+"/appScreenshotSets")["data"]
    sets = [v for v in sets if v["attributes"]["screenshotDisplayType"] == args.display]
    if len(sets) > 1:
        raise ValueError("Ambiguous screenshot set")
    if not sets:
        sets = [api("POST", "appScreenshotSets", json={"data": {"type": "appScreenshotSets",
            "attributes": {"screenshotDisplayType": args.display}, "relationships": {
                "appStoreVersionLocalization": {"data": {"type": "appStoreVersionLocalizations", "id": loc[0]["id"]}}}}})["data"]]
    assets = api("GET", "appScreenshotSets/"+sets[0]["id"]+"/appScreenshots")["data"]
    same = [v for v in assets if v["attributes"]["fileName"] == args.file.name]
    if len(same) > 1:
        raise ValueError("Duplicate asset names; reconcile before retrying")
    asset = same[0] if same else api("POST", "appScreenshots", json={"data": {
        "type": "appScreenshots", "attributes": {"fileName": args.file.name, "fileSize": len(raw)},
        "relationships": {"appScreenshotSet": {"data": {"type": "appScreenshotSets", "id": sets[0]["id"]}}}}})["data"]
    a = asset["attributes"]
    if a["fileSize"] != len(raw) or a.get("sourceFileChecksum") not in (None, checksum):
        raise ValueError("Existing asset differs; it will not be overwritten")
    if a["assetDeliveryState"]["state"] == "AWAITING_UPLOAD":
        offset = 0
        operations = sorted(a["uploadOperations"], key=lambda x: x["offset"])
        for op in operations:
            u = urlsplit(op["url"])
            if (op["method"] != "PUT" or u.scheme != "https" or u.username or u.password
                    or u.port not in (None, 443) or not (u.hostname or "").endswith(".apple.com")
                    or op["offset"] != offset or op["length"] <= 0 or offset+op["length"] > len(raw)
                    or any(h["name"].lower() in ("authorization", "cookie") for h in op["requestHeaders"])):
                raise ValueError("Unexpected Apple upload target, headers or byte ranges")
            offset += op["length"]
        if offset != len(raw):
            raise ValueError("Upload operations do not cover the complete file")
        for op in operations:
            # Never forward the App Store API token to an asset-upload host.
            try:
                r = requests.put(op["url"], data=raw[op["offset"]:op["offset"]+op["length"]],
                    headers={h["name"]: h["value"] for h in op["requestHeaders"]},
                    timeout=45, allow_redirects=False)
            except requests.RequestException:
                # A network exception can contain the private signed upload URL.
                raise RuntimeError("Asset transfer interrupted; reconcile this asset before retrying") from None
            if not 200 <= r.status_code < 300:
                raise RuntimeError("Asset upload incomplete; reconcile this asset before retrying")
        api("PATCH", "appScreenshots/"+asset["id"], json={"data": {"type": "appScreenshots", "id": asset["id"],
            "attributes": {"uploaded": True, "sourceFileChecksum": checksum}}})
    elif a["assetDeliveryState"]["state"] not in ("COMPLETE", "UPLOAD_COMPLETE"):
        raise ValueError("Existing asset is not uploadable; reconcile before retrying")
    deadline = time.monotonic() + args.wait_seconds
    while True:
        after = api("GET", "appScreenshots/"+asset["id"])["data"]["attributes"]
        delivery = after["assetDeliveryState"]["state"]
        if delivery == "COMPLETE":
            if after.get("sourceFileChecksum") != checksum:
                raise ValueError("Completed asset checksum mismatch; reconcile before retrying")
            break
        if delivery not in ("UPLOAD_COMPLETE", "PROCESSING"):
            raise RuntimeError("Apple did not accept the asset; reconcile before retrying")
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            break
        time.sleep(min(3, remaining))
    print(json.dumps({"assetId": asset["id"], "file": args.file.name, "sha256": sha,
        "checksumMatches": after.get("sourceFileChecksum") == checksum,
        "complete": delivery == "COMPLETE", "delivery": after["assetDeliveryState"]}))


if __name__ == "__main__":
    main()
