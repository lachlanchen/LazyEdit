import http from 'node:http';
import { fail } from '../studio/auth.mjs';

const active = new Set(['queued', 'running', 'processing', 'pending', 'publishing', 'working']);

export async function assertWorkspaceIdle(backendPort = 18787, publisherPort = 8081) {
  async function read(port, path) {
    const response = await fetch(`http://127.0.0.1:${port}${path}`, {signal: AbortSignal.timeout(10000)});
    if (!response.ok) fail(503, 'Cannot verify workspace activity; try again later');
    const text = await response.text();
    if (text.length > 2 * 1024 * 1024) fail(503, 'Workspace activity response is too large');
    return JSON.parse(text);
  }
  for (const [port, path] of [[backendPort, '/api/autopublish/queue'], [publisherPort, '/publish/queue']]) {
    const value = await read(port, path);
    const jobs = Array.isArray(value.jobs) ? value.jobs : value.jobs && typeof value.jobs === 'object' ? Object.values(value.jobs) : null;
    if (!jobs || value.status === 'unavailable') fail(503, 'Cannot verify publication queue');
    if (value.is_publishing || jobs.some(job => active.has(job.status))) fail(409, 'Wait for processing and publication to finish before deleting your account');
  }
  const library = await read(backendPort, '/api/videos');
  if (!Array.isArray(library.videos)) fail(503, 'Cannot verify processing activity');
  // Sequential checks keep deletion from creating a burst on a small worker.
  for (const video of library.videos) {
    if (!Number.isSafeInteger(video.id)) fail(503, 'Cannot verify processing activity');
    const state = await read(backendPort, `/api/videos/${video.id}/process-status`);
    if (!state.steps || typeof state.steps !== 'object') fail(503, 'Cannot verify processing activity');
    if (Object.values(state.steps).some(step => active.has(step.status))) fail(409, 'Wait for processing and publication to finish before deleting your account');
  }
}

// Operator transport only; no caller-supplied address, path or identity.
export function closeCell(config, row, checkOnly = false) {
  return new Promise((resolve, reject) => {
    const request = http.request({hostname: config.workerHost?.(row) || `le-${row.id}-worker`,
      port: typeof config.workerPort === 'function' ? config.workerPort(row) : config.workerPort || 18080,
      path: '/studio/bridge', method: 'POST', headers: {authorization: `Bearer ${row.transport}`,
        'x-studio-path': checkOnly ? '/hosted-check-idle' : '/hosted-close', 'x-hosted-owner': row.owner}}, response => {
      let text = '';
      response.on('data', bytes => {text += bytes; if (text.length > 4096) request.destroy();});
      response.on('end', () => {
        if (response.statusCode === 200) resolve();
        else reject(Object.assign(Error(response.statusCode === 409 ? 'Wait for processing and publication to finish before deleting your account' : 'Could not close the workspace safely; try again later'), {status: response.statusCode === 409 ? 409 : 503}));
      });
    });
    request.setTimeout(60000, () => request.destroy());
    request.on('error', () => reject(Object.assign(Error('Could not close the workspace safely; try again later'), {status: 503})));
    request.end();
  });
}
