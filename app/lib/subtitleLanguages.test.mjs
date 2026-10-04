import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { stripTypeScriptTypes } from 'node:module';

const source = await readFile(new URL('./subtitleLanguages.ts', import.meta.url), 'utf8');
const { mergeSubtitleLanguages, resolveSubtitleLanguage } = await import(
  'data:text/javascript;base64,' + Buffer.from(stripTypeScriptTypes(source)).toString('base64')
);

test('saved and imported targets survive the common catalogue without mutation', () => {
  const catalogue = [{ code: 'ja', name: 'Japanese' }, { code: 'ko', name: 'Korean', reading: 'hanja' }];
  const merged = mergeSubtitleLanguages(catalogue, ['eo', 'pt-BR', 'eo', 'ja', '']);
  assert.deepEqual(merged.map(row => row.code), ['ja', 'ko', 'eo', 'pt-BR']);
  assert.equal(merged[1].reading, 'hanja');
  assert.equal(merged[2].requiresPreview, true);
  assert.equal(catalogue.length, 2);
});

test('custom addition asks the backend to canonicalize without saving preferences', async t => {
  const calls = [];
  t.mock.method(globalThis, 'fetch', async (url, options) => {
    calls.push({ url, options });
    return new Response(JSON.stringify({ languages: [{ code: 'pt-BR', name: 'Portuguese (Brazil)' }] }));
  });
  assert.equal((await resolveSubtitleLanguage('https://studio.test', ' pt-br ')).code, 'pt-BR');
  assert.equal(calls.length, 1);
  assert.equal(calls[0].url, 'https://studio.test/api/languages');
  assert.deepEqual(JSON.parse(calls[0].options.body), { languages: ['pt-br'] });
});

test('unknown targets and malformed replies produce errors instead of defaults', async t => {
  t.mock.method(globalThis, 'fetch', async () => new Response(JSON.stringify({ error: 'Unsupported subtitle language: zz' }), { status: 400 }));
  await assert.rejects(resolveSubtitleLanguage('https://studio.test', 'zz'), /Unsupported subtitle language/);
  globalThis.fetch.mock.mockImplementation(async () => new Response(JSON.stringify({ languages: [{ code: 'eo', name: { invalid: true } }] })));
  await assert.rejects(resolveSubtitleLanguage('https://studio.test', 'eo'), /Invalid language reply/);
});

test('new picker messages cover all eleven UI locales with the same keys', async () => {
  const messages = JSON.parse(await readFile(new URL('../locales/subtitle-languages.json', import.meta.url), 'utf8'));
  assert.deepEqual(Object.keys(messages).sort(), ['en', 'zh-Hans', 'zh-Hant', 'ja', 'ko', 'vi', 'ar', 'fr', 'es', 'de', 'ru'].sort());
  for (const table of Object.values(messages)) {
    assert.deepEqual(Object.keys(table), Object.keys(messages.en));
    assert.ok(Object.values(table).every(value => typeof value === 'string' && value.length));
    assert.ok(table.subtitle_languages_remove.includes('{{value}}'));
  }
});
