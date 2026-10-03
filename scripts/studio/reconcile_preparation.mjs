#!/usr/bin/env node
// Operator-only migration for an accepted capture request from an older worker.
// Run inside the exact private cell; no browser, token rotation or social post.
import {readFileSync, realpathSync, statSync, createReadStream} from 'node:fs';
import {sep} from 'node:path';
import {createHash} from 'node:crypto';
import {AuthStore, digest, fail} from '../../studio/auth.mjs';
import {capturePreparation, CAPTURE_PRESET} from '../../studio/preparation.mjs';
import {PreparationRecovery} from '../../studio/preparation-recovery.mjs';

const options = new Map();
for (let i = 2; i < process.argv.length; i++) {
  const flag = process.argv[i];
  if (!['--video-id', '--key', '--brief', '--apply'].includes(flag)) throw Error('Unsupported option');
  options.set(flag, flag === '--apply' ? true : process.argv[++i]);
}
const videoId = Number(options.get('--video-id')), key = options.get('--key');
if (!Number.isSafeInteger(videoId) || videoId < 1 || !key || !options.get('--brief')) throw Error('Use --video-id ID --key ORIGINAL_KEY --brief PRIVATE_JSON [--apply]');
const auth = new AuthStore('/state/studio/accounts.sqlite');
try {
  const intent = auth.db.prepare('SELECT * FROM intents WHERE key=?').get(key);
  if (!intent || intent.state !== 'submitted' || !intent.response) fail(409, 'Original accepted intent unavailable');
  const brief = JSON.parse(readFileSync(options.get('--brief'), 'utf8'));
  if (brief.preparationPreset !== CAPTURE_PRESET || intent.fingerprint !== digest(JSON.stringify({path: `/api/videos/${videoId}/process`, data: brief}))) fail(409, 'Original request fingerprint mismatch');
  const receipt = JSON.parse(intent.response);
  if (receipt.video_id !== videoId || receipt.status !== 'started' || receipt.publication_session_id) fail(409, 'Only the original current-output capture can be migrated');
  const media = auth.db.prepare('SELECT * FROM media WHERE owner=? AND video_id=?').get(intent.owner, videoId);
  if (!media?.sha256) fail(403, 'Original owned source unavailable');
  const request = async (path, data) => {
    const response = await fetch('http://127.0.0.1:18787' + path, {
      method: data === undefined ? 'GET' : 'POST', headers: {'content-type': 'application/json'},
      body: data === undefined ? undefined : JSON.stringify(data), signal: AbortSignal.timeout(60000),
    });
    const reply = await response.json();
    if (!response.ok) fail(response.status, 'Private preparation request failed');
    return reply;
  };
  const status = () => request(`/api/videos/${videoId}/process-status`);
  const before = await status();
  const video = await request(`/api/videos/${videoId}`), source = realpathSync(video.file_path);
  if (!source.startsWith(realpathSync('/state/data') + sep)) fail(403, 'Source outside this workspace');
  const verifySource = async () => {
    const hash = createHash('sha256'); for await (const b of createReadStream(source)) hash.update(b);
    if (hash.digest('hex') !== media.sha256) fail(409, 'Source identity changed');
  };
  await verifySource();
  const jobs = () => request('/api/autopublish/queue').then(value => value.jobs);
  const currentJobs = await jobs();
  if (!Array.isArray(currentJobs) || currentJobs.some(j => Number(j.video_id) === videoId)) fail(409, 'Publication must be absent');
  const ledger = new PreparationRecovery(auth.db, 'operator-recovery-' + intent.id);
  let row = auth.db.prepare('SELECT * FROM studio_preparations WHERE id=?').get(intent.id);
  if (!row) {
    if (before.pipeline !== null || Object.values(before.steps || {}).some(s => ['working','processing','queued','running'].includes(s.status))) fail(409, 'This operation is not proven interrupted');
    if (Object.values(before.steps || {}).every(s => ['done','skipped'].includes(s.status))) fail(409, 'Do not restart a completed preparation');
    if (!options.get('--apply')) {
      console.log(JSON.stringify({video_id: videoId, operation_id: intent.id, state: 'interrupted',
        source_sha256: media.sha256, source_bytes: statSync(source).size, apply_required: true, publication_jobs: currentJobs.length}));
      process.exitCode = 0;
    } else {
      const settings = await request('/api/ui-settings/logo_settings');
      // Legacy workers did not persist resolved settings. Preserve the exact
      // capture preset and original brief; migration verifies the configured
      // logo instead of accepting any replacement setting from a client.
      const resolved = capturePreparation(brief, settings.value);
      ledger.register(intent.id, intent.owner, videoId, resolved, media.sha256, intent.created, 'legacy-interrupted');
      ledger.accepted(intent.id, receipt);
      row = ledger.owned(intent.id, intent.owner);
    }
  }
  if (row) {
    if (!options.get('--apply')) console.log(JSON.stringify(ledger.describe(row, before)));
    else console.log(JSON.stringify(await ledger.resume(row, {status, verifySource,
      publicationJobs: jobs, dispatch: (_row, data) => request(`/api/videos/${videoId}/process`, data)})));
  }
} finally { auth.db.close(); }
