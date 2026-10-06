# Google public release and Apple follow-up — 2026-10-07

## Verified release state

Read-only audit used the existing authorized store browser (CDP 9497), the
repository's `scripts/studio/cdp.py`, the official App Store Connect API via
`scripts/studio/macos_store.py`, and unauthenticated public-page HTTP checks.
No browser profile, credentials, owner media or private review account was
copied into this record.

Google Play Console for `art.lazying.lazyedit` shows:

- Production **1.0 (6) — Private Studio editing**: **Available on Google Play**,
  **Full rollout**, **173 countries/regions**.
- Publishing overview: managed publishing **off**, last published **October 6,
  2026**; no pending manual release action observed.
- Release overview timestamp: **Oct 6, 2026, 6:38 PM**, as displayed by Console;
  its timezone was not independently verified.
- Latest uploaded bundle: **6**. The internal track also retains build 6.
- [Public US listing](https://play.google.com/store/apps/details?id=art.lazying.lazyedit&hl=en&gl=US)
  returns HTTP200 and identifies LazyEdit Studio by LazyingArt LLC. Its buy
  button and structured offer both show **USD 0.99**, with availability InStock.
- The public description discloses invitation and internet requirements,
  private editing, optional operator-enabled social publication, and that
  subscriptions are not offered in this pilot.

No purchase, device installation, new upload or new submission was made during
this audit. Crash/ANR data was unavailable, which is not evidence of zero crashes.

## Post-approval work

- Add the public Play download link to the existing `docs/index.html` landing
  page and point Open Studio at `https://edit.lazying.art`.
- Explain the hosted invitation requirement beside the download link so people
  can arrange access before paying. This release does not enable public signup,
  billing, platform access or the owner's Pi for ordinary users.
- Update `store/studio/release.json`, `store/studio/listing.json`, and the native
  testing guide to distinguish public Android from internal Apple testing and
  unresolved Apple review.
- Preserve all signed artifacts, signing keys and current runtime services.
  Publishing these static docs requires no workspace/backend/Pi restart.

The landing page deploys through GitHub Pages from `main:/docs` at
`https://studio.lazying.art`. Check the Pages build and live download link after
pushing; a local commit alone is not deployment evidence.

## Is there a newer build to submit?

**No newer qualified Android bundle is ready.** The checked-in version code and
latest signed outputs remain 6. Their hashes match the release manifest:

| Artifact | SHA256 |
| --- | --- |
| `mobile/android/app/build/outputs/bundle/release/app-release.aab` | `1232df09acf819af759086600f4d8e92a7ea7f4a20e470df550f7e2b027184d3` |
| `mobile/android/app/build/outputs/apk/release/app-release.apk` | `7b24e55257007e4ba16973c632b627735232ef39fc2f9d30c27ab69f1faa902b` |

Two runtime source improvements postdate that signed build:

- `e572f54`: native composer language picker using the backend language list.
- `66708d1`: account-scoped publishing capability fallback for older owner
  endpoint responses. This must retain ordinary-member publication isolation.

These changes need a new version code, signing and focused device/emulator QA
before any later update submission. Do not call them part of the public bundle 6.
Server-side subtitle and AutoPublish changes do not by themselves require a new
mobile binary. The latest Apple builds are iOS 9 and universal Mac 12.

Console's edge-to-edge and R8 recommendations remain follow-ups for the next
Android qualification. Version 6 is unminified; do not manufacture a mapping file
or rebuild solely for the nonblocking deobfuscation warning.

## Did we reply to Apple?

**Yes, both replies are posted, not drafts.** The existing review pages still
show our answers and no newer Apple response:

- iOS9: Messages(2), including our **October 6, 06:05 HKT** response and full
  PDF attachment.
- Mac12: Messages(6), including our five full-answer text parts posted
  **October 6, 06:13 HKT**.

Both versions remain **REJECTED / UNRESOLVED_ISSUES**. Apple requested answers
to its 4.3/4.2.6 clarification in those threads and explicitly instructed against
unchanged resubmission. Preserve the current builds and threads while awaiting
its response; do not duplicate the replies or create an unchanged submission.

Exact message receipts and attachment verification are in
`store/studio/release.json` and
[the rejection resolution record](2026-10-06-apple-rejection-resolution.md).
