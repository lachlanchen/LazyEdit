# LazyEdit publish-queue reliability fixes (2026-07-14)

## Scope

This incident was found while preparing videos 475-477 for a normal
SimpleLife publish. The expected flow was polished EN/JP/ZH subtitles, the
configured Studio logo at the per-job position, native portrait output without
blur-fill, then serial AutoPublish jobs.

## Problems and system fixes

1. **A new CLI process could fail immediately on an old step error.**
   Process status is durable, so the first poll after starting a rerun can still
   expose the previous burn/translation error. The CLI now captures the
   pre-run status and ignores only unchanged historical errors. A newer error,
   including the same message with a newer marker, still fails the run.

2. **`--process --publish --no-wait` could launch duplicate processing.**
   The CLI used to start asynchronous processing and immediately enqueue a
   publish job whose worker could start processing again. Fire-and-forget jobs
   now defer processing to the serial LazyEdit publish worker. Waiting CLI runs
   can still process first and publish the verified output afterward.

3. **Queued jobs did not preserve one-shot logo settings.**
   The backend now accepts a sanitized `logo` object in publish-job options and
   uses that object during worker processing. It is intentionally excluded from
   persisted Studio preferences. The webapp's **Publish now** request now sends
   the current logo object too, matching **Process now** and preventing a queue
   worker from falling back to a later global logo position.

4. **A successful long burn could appear stale near completion.**
   Future presence, rather than `Future.done()`, is now the active lifecycle
   signal through completion callbacks. Terminal burn database writes retry
   short interruptions, and worker exceptions are logged and persisted instead
   of disappearing silently.

5. **Transient local translation/metadata HTTP failures stopped a run.**
   Local process orchestration retries transient 408/425/429/500/502/503/504
   responses for translation and metadata up to three attempts. Semantic 4xx
   errors still fail immediately.

## Validation

- `python -m py_compile app.py scripts/lazyedit_publish.py`
- `pytest -q tests/test_lazyedit_publish_cli.py` — 4 passed
- `npx tsc --noEmit` in `app/`
- Direct backend assertions for per-job logo sanitization, non-persistence,
  future lifecycle, and retrying terminal burn writes
- Real 2160x3840 burn for video 475 completed as burn row 656 with progress 100,
  no false stale transition, and a valid H.264/AAC subtitle-logo output
- Videos 475-477 each reached `ready_for_publish=true` before queue submission

## Operational rule

For a one-click webapp publish, enqueue one job and let the serial LazyEdit
worker own any missing processing. AutoPublish remains the cross-client remote
queue. Do not launch a separate asynchronous process for the same fire-and-
forget publish job. Always inspect final platform statuses; a queued ZIP is not
proof of publication.

## Production verification

The repaired flow was verified end to end with three serial jobs. Shipinhao was
explicitly disabled for this run; each job targeted only Douyin, Instagram, and
YouTube.

| Video | Local job | Remote job | Result |
| --- | ---: | --- | --- |
| `IMG_5607_2026_07_13_22_39_27_COMPLETED` | 304 | `job-1783981553789-3` | Douyin, Instagram, and YouTube confirmed; YouTube: `https://youtube.com/shorts/Yjyo7Vrv1_M` |
| `IMG_5603_2026_07_13_22_04_33_COMPLETED` | 305 | `job-1783981588903-4` | Douyin, Instagram, and YouTube confirmed; YouTube: `https://youtube.com/shorts/cLte2sqp5AE` |
| `IMG_5600_2026_07_13_21_33_47_COMPLETED` | 306 | `job-1783981612542-5` | Douyin, Instagram, and YouTube confirmed; YouTube: `https://youtube.com/shorts/Jxer6_PSoeA` |

Final checks showed all six queue records (three local and three remote) in
`done` state with no error, `queue_size=0`, and `is_publishing=false`. Douyin
was verified against its management page, Instagram reached its explicit reel
shared confirmation, and YouTube returned a public video URL for every job.
