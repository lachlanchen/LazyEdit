# Apple 4.3 / 4.2.6 clarification - 6 October 2026

Apple rejected both platforms of LazyEdit Studio with the same questionnaire:
iOS 1.0 build 9 and macOS 1.0 build 12. The message names spam, indistinguishable
variants and commercial app-generation services. It does not identify a
runtime failure or a specific duplicated application.

The correct action for this notice is a substantive reply to all nine
questions. Apple explicitly instructed an app that already complies **not to
resubmit unchanged**, but to answer in the existing conversation. A new build
number, arbitrary UI changes, or another submission would not answer the
rejection. Neither the latest submitted binaries nor their TestFlight groups
were replaced for this clarification.

## Response and evidence

- [Full response](2026-10-06-apple-review-response.md): product workflow,
  concrete audience/differentiation, honest beta scope and applied feedback,
  comparison with other developer records, shared components, third-party
  dependencies and first-party ownership.
- [Exact Console message](2026-10-06-apple-review-message.txt): 3,786 characters,
  within the observed 4,000-character reply limit, sent to the iOS thread. It summarizes all nine
  answers and references the complete attachment.
- PDF: `output/pdf/LazyEdit-App-Review-Response-20261006.pdf`, five pages,
  222,109 bytes; SHA-256
  `9dd538b533d3732c93b83e565dc572c418ad1f1c9f4f32073c899c7eda213cc2`.
  All five pages were rendered and visually inspected. The screenshots are
  existing genuine Mac 12 captures, not newly fabricated marketing images.
- Current read-only reviewer qualification: login HTTP 200, three private
  sample videos, `editing=true`, `publishing=false`, completed sample metadata
  in zh/en/ja, HTTP 206 range playback and complete rendered-file SHA match.
  No processing job, social post, account reset or workspace restart.
- Read-only audit of the actual iOS 9 and Mac 12 archives: Apple system and
  Swift dynamic dependencies, no embedded third-party framework directory.
  The active project starts `NativeStudioRoot`; historical Capacitor resources
  are disclosed rather than deleted to obscure the project's history.
- Whole-file native source comparison covered tracked Swift in eight related
  repositories. No full-file matches were found. This does **not** establish
  that no helper, algorithm, branding or backend infrastructure is shared.

## Provider identities and release-state discipline

| Platform | Version ID | Existing submission | Attached build |
| --- | --- | --- | --- |
| iOS | `5097e8ff-f535-489b-b4c3-ef01561b8e9a` | `38267310-a95e-435f-9008-1349611c9307` | 9 |
| macOS | `75ec2713-0287-46a7-a556-e588ed57a2c7` | `68643764-845a-4dd1-ada8-95f7a01dc1e7` | 12 |

Both builds remain Apple `VALID`; the versions are `REJECTED`, with submissions
`UNRESOLVED_ISSUES`. Posting a reply is not a resubmission, approval, or an
automatic transition to `WAITING_FOR_REVIEW`. Record the reply readback in
`store/studio/release.json`; retain the original submitted timestamps as
history. The previous October 4/5 release notes describe their observation
dates, not today's review state.

**Both responses are posted and read back.** iOS received the summary and full
PDF at 06:05 HKT. The Mac upload remained `UPLOAD_COMPLETE` without an error
or a completed asset after several minutes and one saved-draft reload. It
blocked Reply, so its unfinished attachment was removed from our draft and
the complete response was sent as five numbered text parts, within the 4,000
character limit. The PDF and existing Mac listing retain the genuine screenshot
evidence. No missing-attachment claim was sent in the Mac text response.

Mac parts 1-5 were recorded by Apple from `2026-10-05T22:13:30.272Z` through
`2026-10-05T22:13:43.423Z` (06:13 HKT on October 6). The thread now contains six
messages including Apple's original. Every part's full `messageBody` matched
its prepared text through the provider readback. The iOS thread contains two
messages including Apple's original, with the PDF listed as a downloadable
attachment. Downloading that exact Apple-hosted attachment returned the same
SHA-256 as the reviewed local PDF. No draft was mistaken for a delivered reply.

## Reproduce the attachment

Use the LazyEdit conda interpreter. The documentation-only renderer needs
`reportlab`; `pypdf` is useful for checking headings/page count. These are not
runtime app or server dependencies.

```sh
python scripts/studio/render_review_response.py \
  references/studio/2026-10-06-apple-review-response.md \
  output/pdf/LazyEdit-App-Review-Response-20261006.pdf
pdftoppm -png output/pdf/LazyEdit-App-Review-Response-20261006.pdf /tmp/studio-review
```

The generator supports the curated source's paragraphs, headings, bullets,
images and explicit page breaks. Inspect every rendered page after edits.
Regeneration changes the PDF creation timestamp and therefore its byte hash;
retain the exact submitted file and update evidence only for a new attachment.

## Store workflow and caveats

Reuse the existing store browser and app-owned tab; do not relaunch the desktop
or clear its login. `scripts/studio/cdp.py` attaches to the observed page.
Inspect the exact platform/submission/build before **Reply to App Review**.
Set the real textarea value with its normal input/change events, attach the
reviewed PDF through the actual file input, and wait for provider processing.
The same PDF can finish quickly for one platform and remain `UPLOAD_COMPLETE`
with no error while another is processing. Do not resend the upload or click
Reply while disabled. Preserve a draft if an interrupted session requires it.
If the attachment service remains stuck after readback and one saved-draft
reload, send all answers as clearly numbered text parts below the observed
limit. Remove only that unfinished attachment, retain the exact local evidence
and verify every posted body. Do not disable Apple's button or forge an asset's
completion state. Document which thread actually has the attachment.

Click Reply only once; then require the message count, complete message text,
attachment filename and timestamp to appear in the correct thread. After any
uncertain response, reconcile that thread before retrying. Review messages
and private account checks stay outside Git; the curated answer, sanitized
release receipt and reproducible renderer can be committed.

The ASC API helpers provide independent build/version/submission readback.
Keep iOS 9 and Mac 12 distinct; Mac's larger build number is not a newer iOS
release. No unrelated Apple app, Google release or Microsoft enrollment needs
to change for this response. Ordinary invited members and Apple receive the
same editing permissions; never supply owner social accounts to compensate
for a review concern.

If Apple identifies a concrete deficiency, fix that behavior, qualify the
affected platform and then submit its exact new build. If it maintains the
policy rejection after clarification, use the normal review appeal process
with this evidence rather than repeatedly submitting unchanged binaries.

Official guidance:
[reply before appealing](https://developer.apple.com/help/app-review/after-submitting-for-review/appeal-to-the-app-review-board),
[review states and resubmission](https://developer.apple.com/help/app-review/after-submitting-for-review/review-status),
[App Review Guidelines](https://developer.apple.com/app-store/review/guidelines/).
