import {realpathSync, statSync} from 'node:fs';
import {resolve, sep} from 'node:path';
import {fail} from '../studio/auth.mjs';

// These are the filesystem arguments accepted by MusicPackageHandler. Hosted
// members may package their own media, never browser profiles/runtime secrets.
const files = [
  'audio', 'audio_path', 'music_path', 'bandcamp_audio', 'bandcampAudio', 'bandcamp_audio_path',
  'covers', 'cover_paths', 'cover', 'cover_path', 'proof', 'proof_paths', 'proof_files',
  'cover_video', 'coverVideo', 'video_path',
  'website_screenshot', 'websiteScreenshot', 'public_page_screenshot', 'publicPageScreenshot',
  'webapp_screenshot', 'webappScreenshot', 'generation_screenshot', 'generationScreenshot',
  'lyrics_file', 'lyricsFile', 'lyrics_json', 'lyricsJson', 'metadata_json', 'metadataJson',
];
const lists = new Set(['covers', 'cover_paths', 'cover', 'cover_path', 'proof', 'proof_paths', 'proof_files']);

export function privateMusicInput(body, dataRoot) {
  if (!body || Array.isArray(body) || typeof body !== 'object') fail(400, 'Invalid music package');
  // The legacy owner tool supports a remote publisher override. A hosted
  // member's package must always use that workspace's configured publisher.
  if (body.autopublish_url) fail(400, 'Use the publisher configured for your private workspace');
  const root = resolve(dataRoot), physicalRoot = realpathSync(root), output = {...body};
  function file(value) {
    if (typeof value !== 'string' || value.length > 4096 || value.includes('\0')) fail(400, 'Invalid music asset path');
    const requested = resolve(root, value);
    if (!requested.startsWith(root + sep)) fail(403, 'Music assets must be inside your private media workspace');
    let physical;
    try {physical = realpathSync(requested);} catch {fail(400, 'Music asset is unavailable in your private workspace');}
    if (!physical.startsWith(physicalRoot + sep) || !statSync(physical).isFile()) fail(403, 'Music assets must be files inside your private media workspace');
    return physical;
  }
  for (const key of files) {
    if (body[key] === undefined || body[key] === null || body[key] === '') continue;
    if (Array.isArray(body[key])) {
      if (!lists.has(key) || body[key].length > 100) fail(400, 'Invalid music asset list');
      output[key] = body[key].map(file);
    } else output[key] = file(body[key]);
  }
  return output;
}
