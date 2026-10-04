#!/usr/bin/env python
"""Operate only Studio's Mac version; preserve every pending iOS submission."""
import argparse
import base64
import json
import os
from pathlib import Path
import time

import jwt
import requests

APP = "6814061525"
BUNDLE = "art.lazying.lazyedit"
PLATFORM = "MAC_OS"


def qualified_build(api, builds, number, version):
    matches = []
    for build in builds:
        pre = api.call('GET', 'builds/' + build['id'] + '/preReleaseVersion')['data']
        if (build['attributes']['version'] == number
                and pre['attributes']['platform'] == PLATFORM
                and pre['attributes']['version'] == version):
            matches.append(build)
    if (len(matches) != 1 or matches[0]['attributes']['processingState'] != 'VALID'
            or matches[0]['attributes'].get('expired', False)):
        raise ValueError('Require exactly one unexpired VALID Mac candidate')
    return matches[0]


class Apple:
    def __init__(self, key):
        self.session = requests.Session()
        self.key = key

    def call(self, method, path, **kwargs):
        now = int(time.time())
        self.session.headers['Authorization'] = 'Bearer ' + jwt.encode(
            {'iss': '741adba6-ef89-4e36-8a69-ff43ebfa9ecc', 'iat': now,
             'exp': now + 300, 'aud': 'appstoreconnect-v1'},
            self.key.read_text(), algorithm='ES256', headers={'kid': '6SSXT8QU6W'})
        r = self.session.request(method, 'https://api.appstoreconnect.apple.com/v1/' + path,
                                 timeout=45, **kwargs)
        if not r.ok:
            errors = r.json().get('errors', [])
            raise RuntimeError(json.dumps([{'code': e.get('code'), 'detail': e.get('detail')}
                                           for e in errors]))
        return r.json() if r.content else {}

    def versions(self):
        app = self.call('GET', 'apps/' + APP)['data']
        if app['attributes']['bundleId'] != BUNDLE:
            raise ValueError('App identity mismatch')
        return self.call('GET', 'apps/' + APP + '/appStoreVersions')['data']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['status', 'profile', 'prepare', 'submit'])
    parser.add_argument('--build', help='Exact uploaded candidate; required for submit')
    parser.add_argument('--version', default='1.0')
    parser.add_argument('--certificate-id')
    parser.add_argument('--profile-output', type=Path)
    parser.add_argument('--review-credentials', type=Path)
    parser.add_argument('--key', type=Path, default=Path.home()/'.config/echomind/private/AuthKey_6SSXT8QU6W.p8')
    args = parser.parse_args()
    if args.action == 'submit' and (not args.build or not args.build.isdigit()):
        parser.error('submit requires an explicit numeric --build')
    os.umask(0o077)
    api = Apple(args.key)
    versions = api.versions()
    mac = [v for v in versions if v['attributes']['platform'] == PLATFORM
           and v['attributes']['versionString'] == args.version]
    if len(mac) > 1:
        raise ValueError('Ambiguous Mac version')
    if args.action == 'profile':
        if not args.certificate_id or not args.profile_output:
            parser.error('profile requires certificate ID and private output path')
        profiles = api.call('GET', 'profiles?limit=200')['data']
        profiles = [p for p in profiles if p['attributes']['name'] == 'LazyEdit Studio Catalyst App Store'
                    and p['attributes']['profileState'] == 'ACTIVE']
        if len(profiles) > 1:
            raise ValueError('Ambiguous Mac profile')
        if not profiles:
            profile = api.call('POST', 'profiles', json={'data': {'type': 'profiles',
                'attributes': {'name': 'LazyEdit Studio Catalyst App Store', 'profileType': 'MAC_CATALYST_APP_STORE'},
                'relationships': {'bundleId': {'data': {'type': 'bundleIds', 'id': '3XKRKU227A'}},
                                  'certificates': {'data': [{'type': 'certificates', 'id': args.certificate_id}]}}}})['data']
        else:
            profile = profiles[0]
        if profile['attributes']['profileType'] != 'MAC_CATALYST_APP_STORE':
            raise ValueError('Wrong profile platform')
        args.profile_output.parent.mkdir(parents=True, exist_ok=True)
        args.profile_output.write_bytes(base64.b64decode(profile['attributes']['profileContent']))
        print(json.dumps({'profileId': profile['id'], 'name': profile['attributes']['name']}))
        return
    if args.action == 'prepare':
        if not mac:
            mac = [api.call('POST', 'appStoreVersions', json={'data': {
                'type': 'appStoreVersions', 'attributes': {'platform': PLATFORM,
                    'versionString': args.version, 'releaseType': 'AFTER_APPROVAL',
                    'copyright': '2026 LazyingArt LLC'},
                'relationships': {'app': {'data': {'type': 'apps', 'id': APP}}}}})['data']]
        version = mac[0]
        if version['attributes']['appStoreState'] != 'PREPARE_FOR_SUBMISSION':
            raise ValueError('Preserve the existing Mac submission')
        listing = json.loads((Path(__file__).resolve().parents[2]/'store/studio/listing.json').read_text())
        description = listing['description'].replace('Photos or Files', 'Files')
        attrs = {k: listing[k] for k in ['keywords', 'supportUrl', 'marketingUrl']}
        attrs.update(locale='en-US', description=description)
        locales = api.call('GET', 'appStoreVersions/' + version['id'] + '/appStoreVersionLocalizations')['data']
        english = [l for l in locales if l['attributes']['locale'] == 'en-US']
        if len(english) > 1:
            raise ValueError('Ambiguous Mac localization')
        if english:
            api.call('PATCH', 'appStoreVersionLocalizations/' + english[0]['id'],
                     json={'data': {'type': 'appStoreVersionLocalizations', 'id': english[0]['id'],
                                    'attributes': {k: v for k, v in attrs.items() if k != 'locale'}}})
        else:
            api.call('POST', 'appStoreVersionLocalizations', json={'data': {
                'type': 'appStoreVersionLocalizations', 'attributes': attrs,
                'relationships': {'appStoreVersion': {'data': {'type': 'appStoreVersions', 'id': version['id']}}}}})
        if args.review_credentials:
            credential = json.loads(args.review_credentials.read_text())
            # Reuse app-owned review contact fields, never disclose owner channels.
            ios = next(v for v in versions if v['attributes']['platform'] == 'IOS')
            original = api.call('GET', 'appStoreVersions/' + ios['id'] + '/appStoreReviewDetail')['data']['attributes']
            attrs = {k: original[k] for k in ['contactFirstName', 'contactLastName', 'contactPhone', 'contactEmail']}
            attrs.update(demoAccountRequired=True, demoAccountName=credential['username'],
                         demoAccountPassword=credential['password'], notes=listing['reviewAccess']['notes'])
            details = api.call('GET', 'appStoreVersions/' + version['id'] + '/appStoreReviewDetail')
            if details.get('data'):
                detail = details['data']
                api.call('PATCH', 'appStoreReviewDetails/' + detail['id'], json={'data': {
                    'type': 'appStoreReviewDetails', 'id': detail['id'], 'attributes': attrs}})
            else:
                api.call('POST', 'appStoreReviewDetails', json={'data': {'type': 'appStoreReviewDetails',
                    'attributes': attrs, 'relationships': {'appStoreVersion': {
                        'data': {'type': 'appStoreVersions', 'id': version['id']}}}}})
    if args.action == 'submit':
        if not mac:
            raise ValueError('Prepare the Mac version first')
        version = mac[0]
        if version['attributes']['appStoreState'] not in ['PREPARE_FOR_SUBMISSION', 'READY_FOR_REVIEW']:
            print(json.dumps({'state': version['attributes']['appStoreState'], 'newSubmission': False}))
            return
        builds = api.call('GET', 'builds?filter[app]=' + APP + '&filter[version]=' + args.build + '&include=preReleaseVersion')['data']
        build = qualified_build(api, builds, args.build, args.version)
        submissions = api.call('GET', 'apps/' + APP + '/reviewSubmissions')['data']
        active = [s for s in submissions if s['attributes']['platform'] == PLATFORM
                  and s['attributes']['state'] not in ['COMPLETE', 'CANCELED']]
        if len(active) > 1:
            raise ValueError('Ambiguous Mac submission; reconcile')
        submission = active[0] if active else api.call('POST', 'reviewSubmissions', json={'data': {
            'type': 'reviewSubmissions', 'attributes': {'platform': PLATFORM},
            'relationships': {'app': {'data': {'type': 'apps', 'id': APP}}}}})['data']
        if submission['attributes']['state'] != 'READY_FOR_REVIEW':
            raise ValueError('Preserve the already submitted Mac review')
        items = api.call('GET', 'reviewSubmissions/' + submission['id'] + '/items?include=appStoreVersion')['data']
        if items and (len(items) != 1 or items[0]['relationships']['appStoreVersion']['data']['id'] != version['id']):
            raise ValueError('Preserve other review items')
        api.call('PATCH', 'appStoreVersions/' + version['id'] + '/relationships/build',
                 json={'data': {'type': 'builds', 'id': build['id']}})
        if not items:
            api.call('POST', 'reviewSubmissionItems', json={'data': {'type': 'reviewSubmissionItems',
                'relationships': {'reviewSubmission': {'data': {'type': 'reviewSubmissions', 'id': submission['id']}},
                                  'appStoreVersion': {'data': {'type': 'appStoreVersions', 'id': version['id']}}}}})
        result = api.call('PATCH', 'reviewSubmissions/' + submission['id'], json={'data': {
            'type': 'reviewSubmissions', 'id': submission['id'], 'attributes': {'submitted': True}}})
        print(json.dumps({'submissionId': submission['id'], 'state': result['data']['attributes']['state']}))
    print(json.dumps([{'id': v['id'], **{k: v['attributes'][k] for k in
                      ['platform', 'versionString', 'appStoreState']}} for v in api.versions()], indent=2))


if __name__ == '__main__':
    main()
