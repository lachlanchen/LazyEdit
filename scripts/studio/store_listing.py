#!/usr/bin/env python
"""Read or prepare only LazyEdit's existing editable Apple store listing."""
import argparse
import json
from pathlib import Path
import time

import jwt
import requests

APP = "6814061525"
BUNDLE = "art.lazying.lazyedit"
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("action", choices=["status", "prepare"])
parser.add_argument("--listing", type=Path, default=Path(__file__).resolve().parents[2]/"store/studio/listing.json")
parser.add_argument("--key", type=Path, default=Path.home()/".config/echomind/private/AuthKey_6SSXT8QU6W.p8")
args = parser.parse_args()
session = requests.Session()
session.headers["Authorization"] = "Bearer " + jwt.encode(
    {"iss": "741adba6-ef89-4e36-8a69-ff43ebfa9ecc", "iat": int(time.time()),
     "exp": int(time.time())+300, "aud": "appstoreconnect-v1"},
    args.key.read_text(), algorithm="ES256", headers={"kid": "6SSXT8QU6W"})


def api(method, path, **kwargs):
    response = session.request(method, "https://api.appstoreconnect.apple.com/v1/"+path, timeout=45, **kwargs)
    response.raise_for_status()
    return response.json() if response.content else {}


def localization(resource, relation, kind, owner, attrs):
    items = api("GET", resource+"/"+owner+"/"+relation)["data"]
    found = [i for i in items if i["attributes"]["locale"] == attrs["locale"]]
    if len(found) > 1:
        raise RuntimeError("Ambiguous localization")
    if found:
        identifier = found[0]["id"]
        api("PATCH", relation+"/"+identifier, json={"data": {"type": relation, "id": identifier,
            "attributes": {k: v for k, v in attrs.items() if k != "locale"}}})
    else:
        identifier = api("POST", relation, json={"data": {"type": relation, "attributes": attrs,
            "relationships": {kind: {"data": {"type": resource, "id": owner}}}}})["data"]["id"]
    return identifier


app = api("GET", "apps/"+APP)["data"]
if app["attributes"]["bundleId"] != BUNDLE:
    raise RuntimeError("App identity mismatch")
versions = api("GET", "apps/"+APP+"/appStoreVersions")["data"]
selected = [v for v in versions if v["attributes"]["versionString"] == "1.0" and v["attributes"]["platform"] == "IOS"]
if len(selected) != 1:
    raise RuntimeError("Expected exact existing iOS 1.0 record")
version = selected[0]
infos = api("GET", "apps/"+APP+"/appInfos")["data"]
editable = [i for i in infos if i["attributes"]["appStoreState"] == "PREPARE_FOR_SUBMISSION"]
if args.action == "prepare":
    if version["attributes"]["appStoreState"] != "PREPARE_FOR_SUBMISSION" or len(editable) != 1:
        raise RuntimeError("Preserve existing review; listing is not uniquely editable")
    listing = json.loads(args.listing.read_text())
    api("PATCH", "appStoreVersions/"+version["id"], json={"data": {
        "type": "appStoreVersions", "id": version["id"], "attributes": {"copyright": listing["copyright"]}}})
    localization("appStoreVersions", "appStoreVersionLocalizations", "appStoreVersion", version["id"], {
        "locale": listing["appleLocale"], "description": listing["description"], "keywords": listing["keywords"],
        "supportUrl": listing["supportUrl"], "marketingUrl": listing["marketingUrl"]})
    localization("appInfos", "appInfoLocalizations", "appInfo", editable[0]["id"], {
        "locale": listing["appleLocale"], "name": listing["app"], "subtitle": listing["subtitle"],
        "privacyPolicyUrl": listing["privacyUrl"]})
print(json.dumps({"appId": APP, "bundleId": BUNDLE, "version": version["id"],
    "state": version["attributes"]["appStoreState"],
    "locales": [{"locale": i["attributes"]["locale"], "descriptionPresent": bool(i["attributes"].get("description"))}
                for i in api("GET", "appStoreVersions/"+version["id"]+"/appStoreVersionLocalizations")["data"]],
    "operationSubmitsReview": False}, indent=2))
