# Native preparation and publication

The native iOS app now exposes common publish choices directly. It remains a
client of the existing LazyEdit processor and AutoPublish queue. No second
publisher, background agent service, browser session or account is introduced.

## Using it

1. Open a video and choose **Prepare & publish**.
2. Start with the current website defaults, or choose Daily recording,
   LALACHAN story, or Musia recording. Musia has no burned subtitles, an existing
   Studio logo at top-right and original aspect ratio. Daily/story presets use
   English/Japanese/Chinese, top-to-bottom, four reserved rows and no lift.
3. Paste context or import a UTF-8 text/Markdown note. Give names, background,
   song/story references and what was actually said. Correction compares the
   full conversation with this evidence, preserves cue order/timestamps, and
   fixes plausible recognition errors without turning the reference script
   into an invented transcript. Metadata receives context separately from
   editorial direction and is instructed to describe the video concisely.
4. Choose subtitles, order, lift, font size/bold/outline, background layout,
   existing logo position, category and platforms. The language editor lists
   **bottom-to-top**, with a labelled top-to-bottom summary in the main form.
   Japanese readings, kana romanization, Chinese pinyin and existing grammar
   palettes use the established renderer. No logo asset is replaced.
5. Review the settings and layout. **Prepare only** processes without posting;
   **Prepare & queue publication** uses the existing local publish worker, then
   the remote AutoPublish queue. Public publication requires that final action.
6. To send a completed version to another platform, select **Reuse a finished
   run** and the exact run. Preview it before submitting. Its render, logo,
   metadata and cover remain authoritative; correction is not rerun.
7. Activity shows job progress and available login/verification images. Complete
   login, then keep following the same job. Do not submit again just because a
   QR needs scanning. Detailed transcript/metadata/cover editing and exceptional
   recovery remain in **Full editor**.

Choices persist per video in protected app storage, not as global website
settings. Reopening retains them; selecting the website-default preset reloads
the defaults fetched when the composer opened. A context note is editing
evidence, not an instruction to execute tools or publish additional content.

## Background layout

Native portrait sources always keep their original frame. Native requests
cannot force blur-fill onto them, even through a malformed UI state. Landscape
and square inputs can use centred or bottom-space portrait layouts. The latter
defaults to 40% bottom space; the original fits above it without cropping. The
diagram is computed with `lazyedit/portrait_blurfill.py`, the same geometry used
by rendering, including rotation and foreground resizing. It is a geometry
preview, not a claim that a render has already been produced.

The original desktop editor's geometry behavior is unchanged. Native protection
is stricter: every portrait source disables fill, while the existing renderer
also independently rejects unnecessary fill for matching portrait aspect ratios.

## Library removal

Swipe left and choose **Remove**. Full-swipe deletion is disabled. Removal hides
the row from the authenticated remote Studio library; it does not delete media,
transcripts, runs, jobs or social posts. The archive icon opens **Removed videos**
with Restore. This uses a per-owner `hidden_media` table in the Studio account DB.
The original localhost library and linked-client ownership are unaffected.

## Implementation and reliability

- `StudioComposer.swift`: native form, presets, context import, local drafts,
  layout/run preview, review, submission receipts and removed-video view.
- `StudioAPI.swift`: same-origin owner session and optional idempotency header.
- `StudioStore.swift` / `StudioViews.swift`: reversible library actions and
  Activity login images from the existing attention endpoint.
- `studio/composer.mjs`: validates one-shot choices and creates standard
  LazyEdit requests. It reads the configured logo and preserves style defaults.
- `studio/layout_preview.py`: read-only geometry helper using the existing
  conda interpreter and source tree, never a new render implementation.
- `studio/server.mjs`: owner-only composer/plan/submit/submission/visibility
  endpoints under `/v1/studio/videos/{id}/`. Linked-app scopes and LightMind's
  existing preparation/review contracts stay separate and unchanged.

New preparations get a new publication run to preserve earlier outputs.
Publish requests explicitly set `persistSettings:false`, `wait:false` and go
through `/api/videos/{id}/publish`. Preparation uses the existing async process
endpoint. It does not publish. Existing active jobs or an active preparation for
the same video block another submission; other videos use the normal pipeline.

The server hashes reviewed options; changed defaults or changed saved-run
settings require another review. A saved idempotency key is written on the phone
before dispatch. Server intent is persisted before backend dispatch. A timeout
never silently creates a new key. The app queries the receipt and can retry a
request not yet received using the **same** key. An accepted request with an
unknown result stays pending reconciliation rather than being reposted.
Definite pre-dispatch validation errors are marked rejected so choices can be
corrected. The UI prevents double taps while sending.

Existing publication history for a selected platform, including a failed task
that may have partially posted, requires inspection in the full editor. This
is deliberately not an automatic republish/retry-all button. Queue history
checks are supplementary; the server intent protects native request retries.

## Verification and rollout

Run the complete adapter suite with Node 22:

```sh
node --test studio/test.mjs studio/*.test.mjs
```

The new contracts exercise immutable settings, correction/metadata separation,
language ordering/readings, portrait and no-subtitle/logo behavior, run reuse,
duplicate and conflicting queue tasks, scope/CSRF isolation, reversible hiding
and request replay. HTTP tests use an isolated fake backend; they do not post
to real platforms.

`StudioUITests` uses the existing dedicated simulator and a tiny synthetic video
for upload, native choices, review, persistence, remove/restore and full-editor
navigation. No process or publish button is pressed by this UI test. Credentials
belong only in the protected test-runner environment; results/screenshots remain
private. Simulator results do not establish physical-device behavior.

`scripts/studio/promote_worker.py` stages current adapter modules over the exact
live release, preserving deployed web assets. It snapshots the worker unit and
config for rollback, adds the existing conda interpreter/source root, and stages
only the worker. Activate with user-systemd daemon-reload and a worker restart.
It neither bootstraps accounts nor edits/restarts guard, tunnel, backend, Expo
or AutoPublish. Never roll back the account database with application code.

Build 4 uses the existing app identity and private TestFlight group. Release
status and the exact binary hash belong in `store/studio/release.json` after
provider validation; a successful local build alone is not TestFlight delivery.

## Qualification record

- All 21 adapter checks pass, including a backend failure after dispatch: the
  intent stays pending and a second request cannot repost it. A changed review
  digest is explicitly rejected before dispatch and can be corrected safely.
- Final signed simulator test `NativeUI-4d.xcresult`: one test, zero failures
  or skips, 126.728 seconds. It exercised Photos import, staged-upload relaunch,
  real authenticated upload, preview, context entry, keyboard dismissal, native
  review, per-video persistence, full-editor access, swipe removal and restore.
- Earlier simulator runs exposed accessibility hit-point drift in iOS 26 tabs
  and a test gesture scrolling inside the context field. Test taps now use the
  observed tab frame; form scrolling uses the list gutter. The app also offers
  Hide keyboard and dismisses it when opening review. No app navigation bypass
  or insecure session fallback was added for the simulator.
- The live read-only plan used the configured top-right logo, EN/JP/ZH/FR order
  and 40% bottom space for a landscape fixture. A portrait fixture's native
  review disabled fill. Anonymous library access remains HTTP 401.
- Worker release: `studio-433e767e9345`, archive SHA-256
  `433e767e93457f6ab9cd2ea99073077d3943877a0125857d5ed5469bc60262b5`.
  Only the Studio worker restarted. Temporary generated library rows are
  cleaned up after confirming they have no publication jobs. No real social
  post was made as a regression test.
