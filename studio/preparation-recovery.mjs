import {randomUUID} from 'node:crypto';
import {fail} from './auth.mjs';

const steps = ['keyframes', 'caption', 'transcribe', 'polish', 'translate', 'burn',
  'metadata_zh', 'metadata_en', 'metadata_ja', 'cover'];
const active = new Set(['working', 'processing', 'queued', 'running', 'pending']);
function selectedSteps(request) {
  const selected = new Set(request.steps?.length ? request.steps : steps);
  if (request.autoCorrectSubtitles && request.autoCorrectPrompt) selected.add('polish');
  if (selected.has('burn') && request.burnSubtitles !== false) selected.add('translate');
  if ([...selected].some(s => s.startsWith('metadata_'))) selected.add('cover');
  return [...selected];
}

// An editing operation, not a publication job. Resuming keeps the original
// intent/key, resolved settings and source identity; it does not reserve minutes
// or acquire publication authority again.
export class PreparationRecovery {
  constructor(db, instance = randomUUID()) {
    this.db = db;
    this.instance = instance;
    db.exec(`CREATE TABLE IF NOT EXISTS studio_preparations (
      id TEXT PRIMARY KEY, owner TEXT NOT NULL, video_id INTEGER NOT NULL,
      request TEXT NOT NULL, source_sha256 TEXT, instance TEXT NOT NULL,
      state TEXT NOT NULL, response TEXT, created INTEGER NOT NULL,
      recoveries INTEGER NOT NULL DEFAULT 0)`);
  }

  register(id, owner, videoId, request, sourceSha256, created = Date.now(), instance = this.instance) {
    if (!request || request.async !== true || request.platforms !== undefined ||
        request.post !== undefined || request.action === 'publish') fail(400, 'Only asynchronous editing preparation can be recovered');
    const selected = selectedSteps(request);
    if (!Array.isArray(selected) || !selected.length || selected.some(s => !steps.includes(s))) fail(400, 'Unsupported preparation steps');
    this.db.prepare('INSERT INTO studio_preparations(id,owner,video_id,request,source_sha256,instance,state,created) VALUES(?,?,?,?,?,?,?,?)')
      .run(id, owner, videoId, JSON.stringify(request), sourceSha256 || null, instance, 'submitting', created);
  }

  accepted(id, result) {
    this.db.prepare("UPDATE studio_preparations SET state='accepted',response=? WHERE id=?")
      .run(JSON.stringify(result), id);
    return {...result, operation_id: id};
  }

  rejected(id, error) {
    if (error.quotaRejected === true) this.db.prepare('DELETE FROM studio_preparations WHERE id=?').run(id);
    else this.db.prepare('UPDATE studio_preparations SET state=? WHERE id=?')
      .run(error.status >= 400 && error.status < 500 ? 'rejected' : 'unknown', id);
  }

  owned(id, owner) {
    const row = this.db.prepare('SELECT * FROM studio_preparations WHERE id=? AND owner=?').get(id, owner);
    if (!row) fail(404, 'Preparation operation not found');
    return row;
  }

  latest(owner, videoId) {
    return this.db.prepare('SELECT * FROM studio_preparations WHERE owner=? AND video_id=? ORDER BY created DESC,rowid DESC LIMIT 1')
      .get(owner, videoId);
  }

  reusable(row, status, name) {
    const step = status.steps?.[name];
    // A previous render/translation is not completion of this new request.
    // Live checkpoints now carry per-step timestamps, just like DB artifacts.
    return step?.status === 'done' && Date.parse(step.updated_at) >= row.created;
  }

  describe(row, status) {
    const request = JSON.parse(row.request), selected = selectedSteps(request);
    let state;
    if (status.pipeline?.operation_id && status.pipeline.operation_id !== row.id) state = 'reconciliation_required';
    else if (row.state === 'unknown' || row.state === 'submitting' || row.state === 'rejected') state = 'reconciliation_required';
    else if ((status.pipeline?.status === 'done' && Date.parse(status.pipeline.updated_at) >= row.created) || selected.every(s => this.reusable(row, status, s))) state = 'done';
    else if (status.pipeline?.status === 'working' || Object.values(status.steps || {}).some(s => active.has(s.status))) state = 'working';
    else if (status.pipeline?.status === 'error') state = 'error';
    else if (row.instance !== this.instance && row.state === 'accepted') state = 'interrupted';
    else state = 'reconciliation_required';
    return {operation_id: row.id, video_id: row.video_id, state,
      recoverable: state === 'interrupted', recoveries: row.recoveries,
      publication_session_id: row.response ? JSON.parse(row.response).publication_session_id ?? null : null};
  }

  async resume(row, {status, verifySource, publicationJobs, dispatch}) {
    const current = this.describe(row, await status(row));
    if (current.state === 'done' || current.state === 'working') return current;
    if (!current.recoverable) fail(409, 'Preparation needs reconciliation; do not create a new key');
    if (!row.source_sha256) fail(409, 'Original source identity unavailable; operator reconciliation required');
    await verifySource(row);
    const jobs = await publicationJobs();
    if (!Array.isArray(jobs)) fail(503, 'Cannot verify publication state');
    if (jobs.some(j => Number(j.video_id) === row.video_id)) fail(409, 'Publication already exists; preparation recovery is blocked');
    const state = await status(row);
    if (!this.describe(row, state).recoverable) fail(409, 'Preparation state changed; check Activity');
    const request = JSON.parse(row.request), selected = selectedSteps(request);
    const remaining = selected.filter(s => !this.reusable(row, state, s));
    if (!remaining.length) return {...current, state: 'done', recoverable: false};
    const receipt = JSON.parse(row.response);
    const resumed = {...request, steps: remaining, async: true, operationId: row.id,
      publicationMode: 'override', publicationSessionId: receipt.publication_session_id ?? null};
    // The pipeline would otherwise add polish back even when its completed
    // checkpoint was reused. Its original correction prompt remains persisted.
    if (!remaining.includes('polish')) resumed.autoCorrectSubtitles = false;
    const claim = this.db.prepare("UPDATE studio_preparations SET state='resuming',instance=?,recoveries=recoveries+1 WHERE id=? AND instance=? AND state='accepted'")
      .run(this.instance, row.id, row.instance);
    if (claim.changes !== 1) fail(409, 'Recovery already claimed; check Activity');
    try {
      const result = await dispatch(row, resumed);
      this.db.prepare("UPDATE studio_preparations SET state='accepted' WHERE id=?").run(row.id);
      return {...current, state: 'working', recoverable: false, recoveries: row.recoveries + 1,
        resumed_steps: remaining, result: {...result, operation_id: row.id}};
    } catch (error) {
      // An unknown dispatch must never be silently sent twice.
      this.db.prepare("UPDATE studio_preparations SET state='unknown' WHERE id=?").run(row.id);
      throw error;
    }
  }
}
