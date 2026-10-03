#!/usr/bin/env python
"""Inspect/set only LazyEdit's owner-authorized USD 0.99 download price."""
import argparse
from pathlib import Path
import time
import json
import jwt
import requests

APP = '6814061525'
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('action', choices=['status', 'set'])
parser.add_argument('--key', type=Path, default=Path.home()/'.config/echomind/private/AuthKey_6SSXT8QU6W.p8')
args = parser.parse_args()
session = requests.Session()
session.headers['Authorization'] = 'Bearer ' + jwt.encode(
    {'iss': '741adba6-ef89-4e36-8a69-ff43ebfa9ecc', 'iat': int(time.time()),
     'exp': int(time.time())+300, 'aud': 'appstoreconnect-v1'}, args.key.read_text(),
    algorithm='ES256', headers={'kid': '6SSXT8QU6W'})


def api(method, path, **kwargs):
    response = session.request(method, 'https://api.appstoreconnect.apple.com/v1/'+path, timeout=30, **kwargs)
    if response.status_code == 404 and method == 'GET':
        return None
    response.raise_for_status()
    return response.json()


app = api('GET', 'apps/'+APP)['data']
if app['attributes']['bundleId'] != 'art.lazying.lazyedit':
    raise SystemExit('App identity mismatch')
schedule = api('GET', 'apps/'+APP+'/appPriceSchedule')
points = api('GET', 'apps/'+APP+'/appPricePoints', params={'filter[territory]': 'USA', 'limit': 200})['data']
matches = [p for p in points if p['attributes']['customerPrice'] == '0.99']
if len(matches) != 1:
    raise SystemExit('Exact USD 0.99 price point unavailable or ambiguous')
point = matches[0]['id']
current = api('GET', 'appPriceSchedules/'+schedule['data']['id']+'/manualPrices', params={'include':'appPricePoint,territory'}) if schedule else None
already = current and any(p.get('relationships', {}).get('appPricePoint', {}).get('data', {}).get('id') == point and p.get('attributes', {}).get('endDate') is None for p in current['data'])
if args.action == 'set' and not already:
    if schedule and current:
        raise SystemExit('Existing different price schedule: review it before replacing it')
    body = {'data': {'type': 'appPriceSchedules', 'relationships': {
        'app': {'data': {'type':'apps','id':APP}},
        'baseTerritory': {'data': {'type':'territories','id':'USA'}},
        'manualPrices': {'data':[{'type':'appPrices','id':'${studio-price}'}]}}},
        'included':[{'type':'appPrices','id':'${studio-price}',
                     'attributes':{'startDate':None,'endDate':None},
                     'relationships':{'appPricePoint':{'data':{'type':'appPricePoints','id':point}}}}]}
    # Never retry a write blindly; a later invocation reads the accepted schedule.
    api('POST', 'appPriceSchedules', json=body)
    schedule = api('GET', 'apps/'+APP+'/appPriceSchedule')
    current = api('GET', 'appPriceSchedules/'+schedule['data']['id']+'/manualPrices', params={'include':'appPricePoint,territory'})
    already = any(p.get('relationships', {}).get('appPricePoint', {}).get('data', {}).get('id') == point for p in current['data'])
    if not already:
        raise SystemExit('Store read-back does not confirm the requested price')
print(json.dumps({'appId':APP,'bundleId':'art.lazying.lazyedit','usdPrice':'0.99' if already else 'not_configured',
                  'schedule':schedule['data']['id'] if schedule else None}, indent=2))
