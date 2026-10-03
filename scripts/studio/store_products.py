#!/usr/bin/env python
"""Reconcile only LazyEdit's own Apple monthly product drafts.

Preparation/configuration is not billing activation or review submission. Only
an exact USD price point is accepted; no replacement amount is silently chosen.
"""
import argparse
from decimal import Decimal
import json
from pathlib import Path
import time

import jwt
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

APP = "6814061525"
BUNDLE = "art.lazying.lazyedit"
GROUP = "LazyEdit Studio Monthly"
PLANS = [("starter", "Starter", "2.99", 3), ("plus", "Plus", "14.99", 2),
         ("studio", "Studio", "29.90", 1)]
MINUTES = {"starter": 10, "plus": 60, "studio": 150}
DESCRIPTIONS = {
    "en-US": "Process {n} video min per UTC calendar month.",
    "zh-Hans": "每UTC自然月处理{n}分钟源视频。",
    "zh-Hant": "每UTC自然月處理{n}分鐘來源影片。",
    "ja": "UTC暦月ごとに元動画{n}分を処理。",
    "ko": "UTC 달력 기준 매월 원본 동영상 {n}분 처리.",
    "vi": "Xử lý {n} phút video mỗi tháng theo lịch UTC.",
    "ar-SA": "معالجة {n} دقيقة فيديو كل شهر تقويمي بتوقيت UTC.",
    "fr-FR": "{n} min de vidéo par mois calendaire UTC.",
    "es-ES": "{n} min de vídeo por mes natural UTC.",
    "de-DE": "{n} Videominuten pro UTC-Kalendermonat.",
    "ru": "{n} минут видео за календарный месяц UTC.",
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["status", "prepare", "configure"])
    parser.add_argument("--key", type=Path, default=Path.home()/".config/echomind/private/AuthKey_6SSXT8QU6W.p8")
    args = parser.parse_args()
    session = requests.Session()
    session.mount("https://", HTTPAdapter(max_retries=Retry(total=2, connect=2, read=0,
        backoff_factor=0.5, allowed_methods={"GET"})))
    session.headers["Authorization"] = "Bearer " + jwt.encode(
        {"iss": "741adba6-ef89-4e36-8a69-ff43ebfa9ecc", "iat": int(time.time()),
         "exp": int(time.time())+900, "aud": "appstoreconnect-v1"},
        args.key.read_text(), algorithm="ES256", headers={"kid": "6SSXT8QU6W"})
    base = "https://api.appstoreconnect.apple.com/v1/"

    def api(method, path, **kwargs):
        try:
            response = session.request(method, base+path, timeout=(10, 35), **kwargs)
        except requests.RequestException as exc:
            # Do not replay a mutating request whose result is unknown. Re-run
            # reconciliation, which reads each existing product first.
            raise RuntimeError(f"Apple {method} {path.split('?')[0]} unavailable; reconcile before retrying") from None
        if not response.ok:
            # Never dump a request, Authorization header or arbitrary response.
            try:
                errors = response.json().get("errors", [])
                reasons = "; ".join(str(error.get("code", "")) + ": " + str(error.get("detail", ""))[:300]
                    for error in errors[:3])
            except ValueError:
                reasons = ""
            raise RuntimeError(f"Apple {method} {path.split('?')[0]} failed: {response.status_code} {reasons}")
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
    if not matches and args.action in ("prepare", "configure"):
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
        if not found and args.action in ("prepare", "configure"):
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
        if product["attributes"]["state"] not in ("MISSING_METADATA", "READY_TO_SUBMIT", "DEVELOPER_ACTION_NEEDED") and args.action != "status":
            raise RuntimeError("Preserve an active or reviewed subscription")
        points = rows(f"subscriptions/{product['id']}/pricePoints?filter[territory]=USA&limit=200")
        exact = [point for point in points if Decimal(point["attributes"]["customerPrice"]) == Decimal(price)]
        if len(exact) > 1:
            raise RuntimeError("Ambiguous exact USD price")
        schedule_changed = False
        price_path = f"subscriptions/{product['id']}/prices?filter[territory]=USA&include=subscriptionPricePoint,territory&limit=200"
        prices = rows(price_path)
        locales = rows(f"subscriptions/{product['id']}/subscriptionLocalizations?limit=200")
        if args.action == "configure":
            if not exact:
                raise RuntimeError("Approved exact USA price is unavailable; preserve the draft")
            # Current Apple catalog requires availability for a plan before a
            # territory accepts its price. UPFRONT here is the ordinary
            # one-month product, not MONTHLY's 12-month instalment commitment.
            availability = rows(f"subscriptions/{product['id']}/planAvailabilities?limit=200")
            upfront = [a for a in availability if a["attributes"]["planType"] == "UPFRONT"]
            if len(upfront) > 1:
                raise RuntimeError("Ambiguous existing UPFRONT availability")
            if not upfront:
                api("POST", "subscriptionPlanAvailabilities", json={"data": {
                    "type": "subscriptionPlanAvailabilities", "attributes": {
                        "planType": "UPFRONT", "availableInNewTerritories": False},
                    "relationships": {
                        "subscription": {"data": {"type": "subscriptions", "id": product["id"]}},
                        "availableTerritories": {"data": [{"type": "territories", "id": "USA"}]}}}})
            if any(p["relationships"]["subscriptionPricePoint"]["data"]["id"] != exact[0]["id"] for p in prices):
                raise RuntimeError("Preserve an existing different price schedule; reconcile it first")
            if not prices:
                api("POST", "subscriptionPrices", json={"data": {"type": "subscriptionPrices",
                    "attributes": {"startDate": None, "preserveCurrentPrice": True, "planType": "UPFRONT"},
                    "relationships": {
                        "subscription": {"data": {"type": "subscriptions", "id": product["id"]}},
                        "subscriptionPricePoint": {"data": {"type": "subscriptionPricePoints", "id": exact[0]["id"]}},
                        "territory": {"data": {"type": "territories", "id": "USA"}}}}})
                prices = rows(price_path)
                if not prices or any(p["relationships"]["subscriptionPricePoint"]["data"]["id"] != exact[0]["id"] for p in prices):
                    raise RuntimeError("USA draft price readback mismatch")
                schedule_changed = True
            for locale, template in DESCRIPTIONS.items():
                attributes = {"name": "LazyEdit "+name, "locale": locale,
                    "description": template.format(n=MINUTES[plan])}
                if len(attributes["description"]) > 55:
                    raise RuntimeError("Localized subscription description exceeds store limit")
                found_locale = [item for item in locales if item["attributes"]["locale"] == locale]
                if len(found_locale) > 1:
                    raise RuntimeError("Ambiguous subscription localization")
                if not found_locale:
                    api("POST", "subscriptionLocalizations", json={"data": {
                        "type": "subscriptionLocalizations", "attributes": attributes,
                        "relationships": {"subscription": {"data": {"type": "subscriptions", "id": product["id"]}}}}})
                elif any(found_locale[0]["attributes"].get(key) != value for key, value in attributes.items()):
                    raise RuntimeError("Preserve existing different localization; reconcile it first")
            locales = rows(f"subscriptions/{product['id']}/subscriptionLocalizations?limit=200")
        result["products"].append({"id": product["id"], "productId": product_id,
            "state": product["attributes"]["state"], "requestedUSD": price,
            "exactUSDPricePointAvailable": bool(exact), "priceScheduleChanged": schedule_changed,
            "usaPriceScheduleMatches": bool(exact and prices and all(
                p["relationships"]["subscriptionPricePoint"]["data"]["id"] == exact[0]["id"] for p in prices)),
            "localizedBenefits": sorted(item["attributes"]["locale"] for item in locales),
            "nearestAvailableUSD": [] if exact else [str(value) for value in sorted(
                {Decimal(p["attributes"]["customerPrice"]) for p in points},
                key=lambda value: (abs(value-Decimal(price)), value))[:3]]})
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
