#!/usr/bin/env python
"""Reconcile only LazyEdit's own Apple monthly product drafts.

Preparation is not billing activation or review submission. Only an exact USD
price point is accepted; no replacement amount is chosen for a missing point.
"""
import argparse
from decimal import Decimal
import json
from pathlib import Path
import time

import jwt
import requests

APP = "6814061525"
BUNDLE = "art.lazying.lazyedit"
GROUP = "LazyEdit Studio Monthly"
PLANS = [("starter", "Starter", "2.99", 3), ("plus", "Plus", "14.99", 2),
         ("studio", "Studio", "29.89", 1)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["status", "prepare"])
    parser.add_argument("--key", type=Path, default=Path.home()/".config/echomind/private/AuthKey_6SSXT8QU6W.p8")
    args = parser.parse_args()
    session = requests.Session()
    session.headers["Authorization"] = "Bearer " + jwt.encode(
        {"iss": "741adba6-ef89-4e36-8a69-ff43ebfa9ecc", "iat": int(time.time()),
         "exp": int(time.time())+900, "aud": "appstoreconnect-v1"},
        args.key.read_text(), algorithm="ES256", headers={"kid": "6SSXT8QU6W"})
    base = "https://api.appstoreconnect.apple.com/v1/"

    def api(method, path, **kwargs):
        response = session.request(method, base+path, timeout=45, **kwargs)
        if not response.ok:
            # Never dump a request, Authorization header or arbitrary response.
            raise RuntimeError(f"Apple {method} {path.split('?')[0]} failed: {response.status_code}")
        return response.json() if response.content else {}

    def rows(path):
        values = []
        for _ in range(25):
            data = api("GET", path)
            values.extend(data["data"])
            next_url = data.get("links", {}).get("next")
            if not next_url:
                return values
            if not next_url.startswith(base):
                raise RuntimeError("Unexpected Apple pagination origin")
            path = next_url[len(base):]
        raise RuntimeError("Apple pagination limit reached; reconcile before mutation")

    app = api("GET", "apps/"+APP)["data"]
    if app["attributes"]["bundleId"] != BUNDLE:
        raise RuntimeError("App identity mismatch")
    groups = rows("apps/"+APP+"/subscriptionGroups?limit=200")
    matches = [g for g in groups if g["attributes"]["referenceName"] == GROUP]
    if len(matches) > 1:
        raise RuntimeError("Ambiguous own subscription group")
    if not matches and groups:
        raise RuntimeError("Reconcile an existing group before creating another")
    if not matches and args.action == "prepare":
        matches = [api("POST", "subscriptionGroups", json={"data": {
            "type": "subscriptionGroups", "attributes": {"referenceName": GROUP},
            "relationships": {"app": {"data": {"type": "apps", "id": APP}}}}})["data"]]
    result = {"appId": APP, "groupId": matches[0]["id"] if matches else None,
              "products": [], "billingActivated": False, "reviewSubmitted": False}
    if not matches:
        print(json.dumps(result, indent=2))
        return
    group = matches[0]["id"]
    existing = rows(f"subscriptionGroups/{group}/subscriptions?limit=200")
    for plan, name, price, level in PLANS:
        product_id = f"{BUNDLE}.{plan}.monthly"
        found = [p for p in existing if p["attributes"]["productId"] == product_id]
        if len(found) > 1:
            raise RuntimeError("Ambiguous monthly product")
        if not found and args.action == "prepare":
            found = [api("POST", "subscriptions", json={"data": {
                "type": "subscriptions", "attributes": {"name": "LazyEdit "+name,
                    "productId": product_id, "subscriptionPeriod": "ONE_MONTH",
                    "familySharable": False, "groupLevel": level},
                "relationships": {"group": {"data": {"type": "subscriptionGroups", "id": group}}}}})["data"]]
        if not found:
            result["products"].append({"productId": product_id, "exists": False})
            continue
        product = found[0]
        if product["attributes"].get("subscriptionPeriod") != "ONE_MONTH":
            raise RuntimeError("Preserve an existing non-monthly product; reconcile it first")
        if product["attributes"]["state"] not in ("MISSING_METADATA", "READY_TO_SUBMIT", "DEVELOPER_ACTION_NEEDED") and args.action == "prepare":
            raise RuntimeError("Preserve an active or reviewed subscription")
        points = rows(f"subscriptions/{product['id']}/pricePoints?filter[territory]=USA&limit=200")
        exact = [point for point in points if Decimal(point["attributes"]["customerPrice"]) == Decimal(price)]
        if len(exact) > 1:
            raise RuntimeError("Ambiguous exact USD price")
        # Availability is recorded without changing an existing price schedule.
        result["products"].append({"id": product["id"], "productId": product_id,
            "state": product["attributes"]["state"], "requestedUSD": price,
            "exactUSDPricePointAvailable": bool(exact), "priceScheduleChanged": False,
            "nearestAvailableUSD": [] if exact else [str(value) for value in sorted(
                {Decimal(p["attributes"]["customerPrice"]) for p in points},
                key=lambda value: (abs(value-Decimal(price)), value))[:3]]})
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
