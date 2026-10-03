import test from 'node:test';
import assert from 'node:assert/strict';
import http from 'node:http';
import {mkdtempSync, mkdirSync, writeFileSync, symlinkSync, rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {createCell} from './cell.mjs';
import {SCOPES} from '../studio/auth.mjs';

test('hosted music preserves own assets and rejects runtime paths before backend dispatch', async t => {
  const dir = mkdtempSync(join(tmpdir(), 'studio-music-isolation-')), media = join(dir, 'media');
  mkdirSync(media); writeFileSync(join(media, 'song.mp3'), 'harmless audio fixture');
  writeFileSync(join(media, 'proof.txt'), 'own originality proof');
  const outside = join(dir, 'operator-fixture.txt'); writeFileSync(outside, 'not a real credential');
  symlinkSync(outside, join(media, 'escape.txt'));
  const token = join(dir, 'transport'); writeFileSync(token, 'test-transport');
  const received = [], sockets = new Set();
  const backend = http.createServer(async (req, res) => {
    let body = ''; for await (const bytes of req) body += bytes;
    received.push({path:req.url, body:JSON.parse(body)});
    res.setHeader('content-type', 'application/json'); res.end(JSON.stringify({status:'packaged'}));
  });
  await new Promise(r => backend.listen(0, '127.0.0.1', r));
  const owner = 'a'.repeat(24), cell = createCell({host:'member.test', database:join(dir, 'member.sqlite'),
    upstreamSecretFile:token, dataRoot:media, backendPort:backend.address().port,
    webRoot:dir, staticRoot:dir}, {owner, username:'member', password:'test-only-hash'});
  cell.server.on('connection', socket => {sockets.add(socket);socket.once('close',()=>sockets.delete(socket));});
  await new Promise(r => cell.server.listen(0, '127.0.0.1', r));
  t.after(()=>{for(const s of sockets)s.destroy();cell.server.closeAllConnections();cell.server.close();
    backend.closeAllConnections();backend.close();cell.auth.db.close();rmSync(dir,{recursive:true,force:true});});
  const grant = cell.auth.issue(owner, SCOPES, 'test browser', 'browser');
  async function post(body, authenticated = true) {
    const response = await fetch(`http://127.0.0.1:${cell.server.address().port}/studio/bridge`, {
      method:'POST', headers:{authorization:'Bearer test-transport','x-studio-path':'/api/music/package',
        origin:'https://member.test','content-type':'application/json',
        ...(authenticated ? {cookie:`__Host-studio=${grant.access_token}`} : {})}, body:JSON.stringify(body)});
    await response.body.cancel(); return response.status;
  }
  const input = {audio:'song.mp3', title:'Song', proof:['proof.txt'], lyrics:'実際の歌詞', post:false};
  assert.equal(await post(input), 200);
  assert.equal(received[0].path, '/api/music/package');
  assert.equal(received[0].body.audio, join(media, 'song.mp3'));
  assert.deepEqual(received[0].body.proof, [join(media, 'proof.txt')]);
  assert.equal(received[0].body.lyrics, input.lyrics);
  assert.equal(await post(input, false), 401);
  for (const body of [
    {...input, proof:[outside]}, {...input, proof:['../operator-fixture.txt']}, {...input, proof:['escape.txt']},
    {...input, lyricsJson:outside}, {...input, metadata_json:outside},
    {...input, websiteScreenshot:outside}, {...input, bandcampAudio:outside},
    {...input, audio:join(dir,'media-other/song.mp3')},
  ]) assert.equal(await post(body), 403);
  assert.equal(await post({...input, autopublish_url:'http://another-worker:8081'}), 400);
  assert.equal(received.length, 1, 'rejected paths/publisher overrides never reach the backend');
});
