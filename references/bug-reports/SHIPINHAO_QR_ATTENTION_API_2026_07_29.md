# Bug Report: Shipinhao QR Was Not Available Through LazyEdit

Date: 2026-07-29

## Status

Fixed in AutoPublish and LazyEdit. The successful publication that exposed this
defect was not retried.

## Observed Behavior

AutoPublish correctly detected a Shipinhao login requirement, refreshed expired
QR codes, saved screenshots, and sent email. However:

- `/publish/queue` continued to report only `status: running`;
- LazyEdit could not distinguish active publishing from a human login wait;
- an agent transport had no supported way to fetch the QR for the exact job;
- downstream code had to inspect bounded terminal output and remote temporary
  files;
- repeated login log lines could push the job identifier outside the inspected
  log window.

This made QR forwarding unreliable even though the publisher itself worked.

## Root Cause

Human attention was represented as console text and an implementation-private
temporary file rather than part of the publish job state.

## Resolution

AutoPublish now owns a versioned, job-scoped attention contract:

```json
{
  "platform": "shipinhao",
  "kind": "login_qr",
  "status": "required",
  "revision": 1,
  "artifact_url": "/publish/jobs/JOB_ID/attention/1",
  "media_type": "image/png"
}
```

- QR changes increment `revision`.
- Repeated identical QR content is deduplicated.
- Successful login resolves the event.
- Terminal jobs also resolve outstanding attention.
- The artifact is unavailable after resolution.

LazyEdit:

- preserves a sanitized `attention` object while merging local and remote jobs;
- rewrites the artifact URL to a local LazyEdit endpoint;
- verifies the exact remote job and revision;
- proxies only a bounded PNG from the configured AutoPublish origin.

LabCanvas can now poll only LazyEdit, fetch the exact QR, send each revision once
to the originating chat, and continue terminal queue verification after the
scan. It does not need AutoPublish SSH access, log parsing, or `/tmp` discovery
for QR delivery.

## API

Inspect:

```bash
curl -fsS http://127.0.0.1:18787/api/autopublish/queue | jq .
```

Fetch the URL reported in `job.attention.artifact_url`:

```text
GET /api/autopublish/jobs/JOB_ID/attention/REVISION
```

Email remains a fallback and is independent from this contract.

## Maintenance Rule

New platform interventions should use the same generic fields:

- `platform`
- `kind`
- `status`
- `message`
- `revision`
- `media_type`
- `artifact_url`

Do not add platform-specific log scrapers to LazyEdit or chat clients. Platform
code emits attention; AutoPublish stores it; LazyEdit proxies it; the caller's
agent decides the concise human-facing response.
