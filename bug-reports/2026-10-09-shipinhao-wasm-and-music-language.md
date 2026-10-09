# Shipinhao Cover/Audio CDN Failure and Music Language Selector

## Evidence

Musia's Home on the Breeze recording decoded correctly at 2160x3840. Douyin,
Instagram and YouTube confirmed publication. Shipinhao video remained at cover
generation, and its music form left audio processing at zero percent. The
publisher disk still had about 30 GB available; deleting data was not the fix.

Browser resource timing showed repeated roughly 30-second failures fetching
Tencent's public `rhino_video.wasm` / `vts.wasm` dependencies. Verified HTTPS
retrieval through the authorized cloud host succeeded. The downloaded original
WASM binaries are cached privately with SHA-256 validation, outside Git.

The music language dropdown contained Japanese, but the selector dispatched two
clicks, toggling it open and closed. A single-click, asynchronous polling fix
successfully selected Japanese and verified the value on a subsequent poll.
The old "option not found" log did not prove the platform lacked Japanese.

## Fixes

AutoPublish commits `c50eae5` and `3439576`:

- Optional allowlisted, integrity-checked public WASM cache. Browser-level CDP
  Fetch is required because downloads occur inside dedicated workers, whose
  individual CDP targets do not implement Fetch. No authentication requests,
  platform validation, TLS checks or success responses are bypassed.
- Correct music-language selection and committed-value readback.
- Default durable queue journal and verified-published staging cleanup. Failed
  or active jobs remain retryable. Canonical workstation and Nutstore media are
  not removed. Metadata, corrected lyrics, covers, proofs and receipts remain.

The normal generated Chinese video description also embedded Japanese quotations
that the existing China-platform sanitizer damaged. A documented Shipinhao-only
metadata recovery replaced those quotations with natural Chinese prose. This did
not replace the 4K video or trigger duplicate posts on successful platforms.

## Verification

Ten retention unit tests and two cache-validation unit tests passed. Two browser
tests passed: asynchronous language selection and a dedicated worker fetching
the exact cached asset bytes. All temporary test browsers exited afterward.

The broader unittest run had 84 passes and two pre-existing Instagram caption
test failures. An isolated run reproduced both failures without modifying the
Instagram code/tests. The real Instagram submission in this release confirmed
the saved caption and post URL; these unit failures are not evidence that the
post failed.

Deployment/retry receipts and final publication status are in Musia's
`handoff/lazyedit/aya-home-on-the-breeze/README.md`. Do not replay all four video
platforms to debug the remaining Shipinhao targets.
