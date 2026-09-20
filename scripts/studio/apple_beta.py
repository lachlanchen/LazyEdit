#!/usr/bin/env python
"""Inspect this Studio beta; attach only the exact VALID build to its internal group."""
import argparse
import json
from pathlib import Path
import time

import jwt
import requests

APP = "6814061525"
BUNDLE = "art.lazying.lazyedit"
GROUP = "6ce2e6a9-2d38-4bef-a317-bdd5564cb717"
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("action", choices=["status", "attach"])
parser.add_argument("--build", default="4")
parser.add_argument("--notes-file", type=Path, help="UTF-8 beta What to Test text for a new build")
parser.add_argument("--key", type=Path, default=Path.home()/".config/echomind/private/AuthKey_6SSXT8QU6W.p8")
args = parser.parse_args()
token = jwt.encode(
    {"iss": "741adba6-ef89-4e36-8a69-ff43ebfa9ecc", "iat": int(time.time()),
     "exp": int(time.time())+300, "aud": "appstoreconnect-v1"},
    args.key.read_text(), algorithm="ES256", headers={"kid": "6SSXT8QU6W"})
session = requests.Session()
session.headers["Authorization"] = "Bearer "+token


def api(method, path, **kwargs):
    response = session.request(method, "https://api.appstoreconnect.apple.com/v1/"+path,
                               timeout=45, **kwargs)
    response.raise_for_status()
    return response.json() if response.content else {}


app = api("GET", "apps/"+APP)["data"]
if app["attributes"]["bundleId"] != BUNDLE:
    raise RuntimeError("App identity mismatch")
group = api("GET", "betaGroups/"+GROUP)["data"]
if not group["attributes"]["isInternalGroup"]:
    raise RuntimeError("Expected a private internal group")
builds = api("GET", "builds", params={"filter[app]": APP, "filter[version]": args.build})["data"]
if len(builds) > 1:
    raise RuntimeError("Ambiguous build")
build = builds[0] if builds else None
if args.action == "attach":
    if not build or build["attributes"]["processingState"] != "VALID" or build["attributes"]["expired"]:
        raise RuntimeError("Exact build must be VALID and unexpired")
    identifier = build["id"]
    notes_text = args.notes_file.read_text().strip() if args.notes_file else (
        "Private owner beta: sign in, upload a video, open the editor, preview output, "
        "and verify reconnect behavior. Social publication requires your explicit action.")
    if not notes_text or len(notes_text) > 4000:
        raise RuntimeError("Beta notes must contain 1–4000 characters")
    notes = api("GET", "builds/"+identifier+"/betaBuildLocalizations")["data"]
    if not any(item["attributes"]["locale"] == "en-US" for item in notes):
        api("POST", "betaBuildLocalizations", json={"data": {
            "type": "betaBuildLocalizations",
            "attributes": {"locale": "en-US", "whatsNew": notes_text},
            "relationships": {"build": {"data": {"type": "builds", "id": identifier}}}}})
    attached = api("GET", "betaGroups/"+GROUP+"/relationships/builds")["data"]
    if not any(item["id"] == identifier for item in attached):
        api("POST", "betaGroups/"+GROUP+"/relationships/builds",
            json={"data": [{"type": "builds", "id": identifier}]})
attached = api("GET", "betaGroups/"+GROUP+"/relationships/builds")["data"]
testers = api("GET", "betaGroups/"+GROUP+"/relationships/betaTesters")["data"]
result = {"appId": APP, "bundleId": BUNDLE, "groupId": GROUP, "internal": True,
          "buildNumber": args.build, "build": build["id"] if build else None,
          "processingState": build["attributes"]["processingState"] if build else "NOT_VISIBLE",
          "attached": bool(build and any(item["id"] == build["id"] for item in attached)),
          "testerCount": len(testers)}
if build:
    result["beta"] = api("GET", "builds/"+build["id"]+"/buildBetaDetail")["data"]["attributes"]
print(json.dumps(result, indent=2))
