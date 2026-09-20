import {test} from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync, mkdirSync, writeFileSync, rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import http from 'node:http';
import {createWorker} from './server.mjs';
import {CAPTURE_PRESET, CAPTURE_CHANNELS, capturePreparation} from './preparation.mjs';

const brief = {preparationPreset: CAPTURE_PRESET, background: 'A quiet garden', requirements: 'Correct the place name'};
const logo = {enabled: true, logoPath: '/private/logo.png', position: 'top-right'};

test('capture preset separates scene evidence, keeps languages/no lift/logo and never publishes or rotates', () => {
  const p = capturePreparation(brief, logo);
  assert.deepEqual(p.translationLanguages, ['fr', 'zh-Hant', 'ja', 'en']);
  assert.equal(p.burnLayout.liftRatio, 0);
  assert.equal(p.burnLayout.portraitBlurFill.enabled, true);
  assert.equal(p.logo.logoPath, logo.logoPath);
  assert.equal(p.logo.position, 'top-left');
  assert.match(p.autoCorrectPrompt, /every timestamp/);
  assert.match(p.autoCorrectPrompt, /Correct the place name/);
  assert.doesNotMatch(p.notes, /Correct the place name/);
  assert.equal(p.rotate, undefined);
  assert.equal(p.platforms, undefined);
  assert.deepEqual(CAPTURE_CHANNELS, ['douyin', 'shipinhao', 'instagram', 'youtube']);
  for (const invalid of [{...brief, command: 'publish'}, {...brief, requirements: []}, {...brief, background: 'a'.repeat(8001)}]) {
    assert.throws(() => capturePreparation(invalid, logo));
  }
  assert.throws(() => capturePreparation(brief, {enabled: false}));
});

async function fixture(t) {
  const dir = mkdtempSync(join(tmpdir(), 'studio-prepare-test-'));
  const root = join(dir, 'data'); mkdirSync(root);
  writeFileSync(join(root, 'render.mp4'), 'render');
  writeFileSync(join(root, 'cover.jpg'), 'cover');
  writeFileSync(join(dir, 'transport'), 'test-transport');
  const state = {jobs: [], metadata: {title: 'Garden'}, posts: [], logo};
  const backend = http.createServer(async (req, res) => {
    let payload = ''; for await (const b of req) payload += b;
    let reply;
    if (req.method === 'POST') {
      state.posts.push({path: req.url, data: JSON.parse(payload)});
      reply = req.url.endsWith('/publish') ? {job_id: 10} : {status: 'processing', video_id: 1};
    } else if (req.url === '/api/autopublish/queue') reply = {jobs: state.jobs};
    else if (req.url === '/api/ui-settings/logo_settings') reply = {value: state.logo};
    else if (req.url.endsWith('/process-status')) reply = {ready_for_publish: true};
    else if (req.url.endsWith('/burn-subtitles')) reply = {status: 'completed', output_path: join(root, 'render.mp4'), output_url: '/media/render.mp4', config: {logo}};
    else if (req.url.includes('/metadata?lang=')) reply = {status: 'completed', metadata: state.metadata};
    else if (req.url.endsWith('/cover')) reply = {status: 'completed', cover_path: join(root, 'cover.jpg'), cover_url: '/media/cover.jpg'};
    else throw new Error('Unexpected test route ' + req.url);
    res.writeHead(200, {'content-type': 'application/json'}); res.end(JSON.stringify(reply));
  });
  await new Promise(r => backend.listen(0, '127.0.0.1', r));
  const worker = createWorker({database: join(dir, 'accounts.db'), host: 'studio.test', upstreamSecretFile: join(dir, 'transport'),
    dataRoot: root, backendPort: backend.address().port, webRoot: dir, staticRoot: dir});
  await new Promise(r => worker.server.listen(0, '127.0.0.1', r));
  t.after(async () => {
    await new Promise(r => worker.server.close(r)); await new Promise(r => backend.close(r));
    worker.auth.db.close(); rmSync(dir, {recursive: true, force: true});
  });
  const owner = worker.auth.addOwner('owner', 'test-password');
  const token = worker.auth.issue(owner, ['media.read','edit.submit','jobs.read','publication.prepare','publication.publish']);
  worker.auth.db.prepare('INSERT INTO media VALUES(?,?,?,?)').run(1, owner, 'hash', 'clip.mp4');
  const request = (path, body, key = 'test-key', access = token.access_token) => fetch(`http://127.0.0.1:${worker.server.address().port}/studio/bridge`, {
    method: body ? 'POST' : 'GET', headers: {authorization: 'Bearer test-transport', 'x-studio-access': 'Bearer ' + access,
      'x-studio-path': path, 'idempotency-key': key, 'content-type': 'application/json'}, body: body ? JSON.stringify(body) : undefined,
  });
  return {state, worker, owner, request};
}

test('prepare is scoped, owned, retry-stable and never sends publication', async t => {
  const f = await fixture(t);
  const token = f.worker.auth.issue(f.owner, ['media.read']);
  assert.equal((await f.request('/api/videos/1/process', brief, 'k', token.access_token)).status, 403);
  assert.equal((await f.request('/api/videos/2/process', brief)).status, 403);
  f.state.logo = {enabled: false};
  assert.equal((await f.request('/api/videos/1/process', brief)).status, 409);
  f.state.logo = logo;
  assert.equal((await f.request('/api/videos/1/process', brief)).status, 200);
  f.state.logo = {enabled: false};
  assert.equal((await f.request('/api/videos/1/process', brief)).status, 200);
  assert.equal(f.state.posts.length, 1);
  assert.equal(f.state.posts[0].data.logo.logoPath, logo.logoPath);
  assert.equal((await f.request('/api/videos/1/process', {...brief, background: 'Different'})).status, 409);
});

test('review is private, binds render/metadata/cover; multi-target publish is duplicate-safe', async t => {
  const f = await fixture(t);
  const review = await (await f.request('/v1/studio/review?videoId=1')).json();
  assert.match(review.reviewDigest, /^[a-f0-9]{64}$/);
  assert.equal(JSON.stringify(review).includes('/private/'), false);
  assert.equal((await f.request('/v1/studio/review?videoId=2')).status, 403);
  const body = {platforms: CAPTURE_CHANNELS, reviewApproved: true, reviewedVideoId: 1,
    reviewedSha256: review.artifact.sha256, reviewedReviewDigest: review.reviewDigest,
    confirmation: 'PUBLISH_REVIEWED_MEDIA', productionConfirmation: 'PUBLISH_REVIEWED_MEDIA_PRODUCTION'};
  f.state.metadata = {title: 'Changed title'};
  assert.equal((await f.request('/api/videos/1/publish', body)).status, 409);
  f.state.metadata = {title: 'Garden'};
  assert.equal((await f.request('/api/videos/1/publish', body)).status, 200);
  f.state.jobs = [{id: 10, video_id: 1, status: 'failed'}];
  assert.equal((await f.request('/api/videos/1/publish', body)).status, 200);
  assert.equal((await f.request('/api/videos/1/publish', body, 'another-key')).status, 409);
  assert.equal((await f.request('/api/videos/1/process', brief, 'prepare-again')).status, 409);
  assert.equal(f.state.posts.length, 1);
  assert.deepEqual(f.state.posts[0].data.platforms, CAPTURE_CHANNELS);
});
