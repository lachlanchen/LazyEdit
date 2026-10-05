#!/usr/bin/env python
"""Inspect or attach an exact platform-specific Studio build to private TestFlight."""
import argparse
import json
from pathlib import Path

if __package__:
    from .macos_store import Apple, APP, BUNDLE
else:
    from macos_store import Apple, APP, BUNDLE

GROUP = "6ce2e6a9-2d38-4bef-a317-bdd5564cb717"


def select_build(api, number, platform, version):
    builds = api.call("GET", "builds", params={
        "filter[app]": APP, "filter[version]": number, "limit": 200})["data"]
    matches = []
    for build in builds:
        pre = api.call("GET", "builds/" + build["id"] + "/preReleaseVersion")["data"]["attributes"]
        if (build["attributes"]["version"] == number
                and pre["platform"] == platform and pre["version"] == version):
            matches.append(build)
    if len(matches) > 1:
        raise RuntimeError("Ambiguous build for the requested platform and version")
    return matches[0] if matches else None


def operate(api, action, number, platform, version, notes_text):
    app = api.call("GET", "apps/" + APP)["data"]
    if app["attributes"]["bundleId"] != BUNDLE:
        raise RuntimeError("App identity mismatch")
    groups = api.call("GET", "apps/" + APP + "/betaGroups")["data"]
    group = next((item for item in groups if item["id"] == GROUP), None)
    if not group or not group["attributes"]["isInternalGroup"]:
        raise RuntimeError("Expected this app's private internal group")
    build = select_build(api, number, platform, version)
    if action == "attach":
        if (not build or build["attributes"]["processingState"] != "VALID"
                or build["attributes"]["expired"]):
            raise RuntimeError("Exact platform build must be VALID and unexpired")
        if not notes_text or len(notes_text) > 4000:
            raise RuntimeError("Beta notes must contain 1–4000 characters")
        identifier = build["id"]
        notes = api.call("GET", "builds/" + identifier + "/betaBuildLocalizations")["data"]
        if not any(item["attributes"]["locale"] == "en-US" for item in notes):
            api.call("POST", "betaBuildLocalizations", json={"data": {
                "type": "betaBuildLocalizations",
                "attributes": {"locale": "en-US", "whatsNew": notes_text},
                "relationships": {"build": {"data": {"type": "builds", "id": identifier}}}}})
        attached = api.call("GET", "betaGroups/" + GROUP + "/relationships/builds")["data"]
        if not any(item["id"] == identifier for item in attached):
            # Add only this build; never replace the group's iOS/Mac build set.
            # Reconcile an uncertain request with status before retrying.
            api.call("POST", "betaGroups/" + GROUP + "/relationships/builds",
                     json={"data": [{"type": "builds", "id": identifier}]})
    attached = api.call("GET", "betaGroups/" + GROUP + "/relationships/builds")["data"]
    testers = api.call("GET", "betaGroups/" + GROUP + "/relationships/betaTesters")["data"]
    result = {"appId": APP, "bundleId": BUNDLE, "groupId": GROUP, "internal": True,
              "platform": platform, "version": version, "buildNumber": number,
              "build": build["id"] if build else None,
              "processingState": build["attributes"]["processingState"] if build else "NOT_VISIBLE",
              "attached": bool(build and any(item["id"] == build["id"] for item in attached)),
              "testerCount": len(testers)}
    if build:
        result["beta"] = api.call("GET", "builds/" + build["id"] + "/buildBetaDetail")["data"]["attributes"]
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["status", "attach"])
    parser.add_argument("--build", required=True, help="Exact numeric candidate build")
    parser.add_argument("--platform", choices=["IOS", "MAC_OS"], default="IOS")
    parser.add_argument("--version", default="1.0", help="Exact marketing version")
    parser.add_argument("--notes-file", type=Path, help="UTF-8 beta What to Test text")
    parser.add_argument("--key", type=Path, default=Path.home()/".config/echomind/private/AuthKey_6SSXT8QU6W.p8")
    args = parser.parse_args()
    if not args.build.isdigit():
        parser.error("--build must be numeric")
    notes = args.notes_file.read_text().strip() if args.notes_file else (
        "Private Studio beta: sign in, upload a video, open the editor, preview output, "
        "and verify reconnect behavior. Social publication requires your explicit action.")
    result = operate(Apple(args.key), args.action, args.build, args.platform, args.version, notes)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
