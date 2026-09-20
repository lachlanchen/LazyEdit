# Linked Capture Preparation And Native Review

LightMind owns pairing, recording, wireless import, exact clip selection and
the user's brief. Studio owns transcription, correction, translation, render,
metadata and publishing. No phone-side shell or publisher automation is added.

## Preparation Contract

POST `/api/videos/<id>/process` with `edit.submit` and a saved Idempotency-Key:

```json
{
  "preparationPreset": "lightmind-capture.v1",
  "background": "Factual names, location and what happens in this clip",
  "requirements": "Optional subtitle correction requirements"
}
```

Do not mix preset and legacy options. Background informs concise metadata;
requirements inform subtitle correction, not public scene facts. Cue count and
timestamps must remain intact, and silence must not gain invented speech. The
full pipeline uses EN/JA/ZH-Hant/FR (top to bottom), zero lift, source-aware
portrait fill and the existing configured logo at top-left for personal capture.
Missing logo configuration blocks preparation. Global preferences are not changed.
This preset does not rotate, crop, publish or interpret arbitrary shell commands.

## Native Review And Publication

GET `/v1/studio/review?videoId=<id>` requires `publication.prepare`, `media.read`
and ownership. The response includes render identity, zh/en/ja metadata and
authenticated cover URL/size/digest, with a digest over the review snapshot.
Local filesystem paths and logo paths are omitted. The native client must
actually display the cover/metadata and play the output before confirmation.

POST `/api/videos/<id>/publish` retains the existing scope, two confirmation
strings and artifact digest; `reviewedReviewDigest` additionally rejects changed
metadata/cover. One request accepts multiple selected platforms. LightMind's
default is Douyin, Shipinhao, Instagram and YouTube, not XHS or Bilibili.

Any existing job for that video blocks a new native publication key, even failed
jobs: some destinations may have succeeded. Replaying an accepted key returns
its original receipt. Never blindly retry all channels. Pre-dispatch validation
failures do not create an uncertain dispatch intent; uncertain backend responses
still require reconciliation. Owner editor recovery remains available.

## Limitations

The legacy queue still reads mutable output, and its worker can stop after a
partial platform success. Review digests are submission-time checks, not an
immutable publication bundle. Do not edit queued videos; confirm channel receipts
in Studio. Simultaneous owner-browser changes are not serialized by this facade.
No unattended agent publishing claim is made. Preparation is not publishing consent.

## Tests And Deployment

`node --test studio/*.test.mjs studio/test.mjs` tests presets, ownership, scope,
missing logo recovery, idempotency, changed metadata and existing failed jobs.
Tests use fake upstreams; no social post is made. Promote only a new immutable
worker release; retain the deployed web assets, guard, tunnel and account store.
Document actual promotion and live read-only probes in LightMind's handoff.
