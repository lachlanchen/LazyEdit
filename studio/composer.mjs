// Native owner UI only. The established LazyEdit pipeline still owns all work.
import {fail} from './auth.mjs';

export const CHANNELS = ['shipinhao', 'instagram', 'youtube', 'douyin', 'xiaohongshu', 'bilibili'];
export const LANGUAGES = ['en', 'ja', 'zh-Hant', 'zh-Hans', 'fr'];
const copy = value => structuredClone(value || {});
const number = (v, min, max, name) => {
  if (typeof v !== 'number' || !Number.isFinite(v) || v < min || v > max) fail(400, `Invalid ${name}`);
  return v;
};
const text = (v, max) => {
  if (typeof v !== 'string' || v.length > max) fail(400, 'Context is too long or invalid');
  return v.trim();
};
export function composerDefaults(settings) {
  const options = settings.publish_options || {}, layout = settings.burn_layout || {}, logo = settings.logo_settings || {};
  const languages = (options.translationLanguages || settings.translation_languages || ['zh-Hant', 'ja', 'en']).filter(l => LANGUAGES.includes(l));
  const platforms = CHANNELS.filter(p => settings.publish_platforms?.[p]);
  return {
    burnSubtitles: options.burnSubtitles !== false, languages,
    lift: layout.liftRatio ?? 0, rows: Math.max(layout.rows || 4, languages.length), fontScale: layout.fontScale || 1,
    fontBold: layout.fontBold !== false, outlineBold: layout.outlineBold !== false,
    background: layout.portraitBlurFill?.enabled ? (layout.portraitBlurFill.mode === 'center' ? 'center' : 'bottom') : 'off',
    bottomSpace: layout.portraitBlurFill?.bottomSpaceRatio ?? 0.4,
    logo: logo.enabled !== false, logoPosition: logo.position || 'top-right',
    category: options.publishCategory || '', platforms: platforms.length ? platforms : CHANNELS.slice(0, 4),
    context: '', metadataDirection: '', correct: true, contextForMetadata: true,
    mode: 'new', sessionID: 0,
  };
}

export function validateForm(value) {
  if (!value || typeof value !== 'object' || Array.isArray(value)) fail(400, 'Publish choices required');
  const f = copy(value);
  const fields = Object.keys(composerDefaults({}));
  if (Object.keys(f).some(k => !fields.includes(k)) || fields.some(k => !Object.hasOwn(f, k))) fail(400, 'Unknown or missing publish choice');
  for (const key of ['burnSubtitles', 'fontBold', 'outlineBold', 'logo', 'correct', 'contextForMetadata']) {
    if (typeof f[key] !== 'boolean') fail(400, `Invalid ${key}`);
  }
  for (const [key, allowed] of [['languages', LANGUAGES], ['platforms', CHANNELS]]) {
    if (!Array.isArray(f[key]) || new Set(f[key]).size !== f[key].length || f[key].some(v => !allowed.includes(v))) fail(400, `Invalid ${key}`);
  }
  if (f.burnSubtitles && !f.languages.length) fail(400, 'Choose at least one subtitle language');
  number(f.lift, 0, 0.4, 'subtitle lift'); number(f.rows, 1, 8, 'reserved rows');
  if (!Number.isInteger(f.rows) || f.rows < f.languages.length) fail(400, 'Reserve at least one row per language');
  number(f.fontScale, 0.6, 2.5, 'font size'); number(f.bottomSpace, 0, 0.8, 'bottom space');
  if (!['off', 'bottom', 'center'].includes(f.background)) fail(400, 'Invalid background layout');
  if (!['top-left', 'top-right', 'bottom-left', 'bottom-right'].includes(f.logoPosition)) fail(400, 'Invalid logo position');
  if (!['', 'simplelife', 'lazyingart', 'lalachan', 'musia', 'lalamv'].includes(f.category)) fail(400, 'Invalid category');
  if (!['new', 'reuse'].includes(f.mode)) fail(400, 'Invalid run mode');
  if (!Number.isSafeInteger(f.sessionID) || f.sessionID < 0) fail(400, 'Invalid run');
  f.context = text(f.context, 16000); f.metadataDirection = text(f.metadataDirection, 4000);
  return f;
}

export function composeOptions(form, settings, geometry) {
  const f = validateForm(form);
  const layout = copy(settings.burn_layout), logo = copy(settings.logo_settings);
  if (f.logo && !logo.logoPath) fail(409, 'Configure the existing Studio logo in the full editor first');
  const fill = {...layout.portraitBlurFill, enabled: f.background !== 'off' && !geometry.portrait,
    mode: f.background === 'center' ? 'center' : 'lalachan', bottomSpaceRatio: f.bottomSpace};
  // Recreate slots from selected order: input is bottom-to-top, renderer is top-to-bottom.
  const previous = layout.slots || [];
  Object.assign(layout, {rows: f.rows, cols: 1, liftRatio: f.lift, liftSlots: 0, fontScale: f.fontScale,
    fontBold: f.fontBold, outlineBold: f.outlineBold, romajiEnabled: true, pinyinEnabled: true,
    slots: [...f.languages].reverse().map((language, i) => ({...previous.find(s => s.language === language),
      slot: i + 1, language, fontScale: 1, romaji: true, pinyin: true})), portraitBlurFill: fill});
  const correction = 'Read the full conversation and neighbouring lines. Infer the most plausible spoken wording from the audio/ASR and context. Fix clear recognition errors, names and broken sentences; neither over-edit nor preserve obvious nonsense. Context is reference, not a replacement script. Preserve every cue, order and timestamp; never invent speech.\n\nContext:\n' + f.context;
  const metadata = [
    'Write concise public-facing metadata about what is actually in this video. Background is evidence, not a script to reproduce. Do not expose editing instructions, production notes or private conversation. Follow the requested output language.',
    f.contextForMetadata && f.context ? 'Background:\n' + f.context : '',
    f.metadataDirection ? 'Editorial direction (not facts to quote):\n' + f.metadataDirection : '',
  ].filter(Boolean).join('\n\n');
  return {burnSubtitles: f.burnSubtitles, translationLanguages: f.languages,
    usePolishedSubtitles: true, subtitleSourceVersion: 'polished',
    autoCorrectSubtitles: f.correct, autoCorrectPrompt: f.correct ? correction : '',
    useCorrectionPromptForMetadata: true, metadataPrompt: metadata,
    burnLayout: layout, logo: {...logo, enabled: f.logo, position: f.logoPosition},
    publicationMode: 'new', publicationSessionId: null, ...(f.category ? {publishCategory: f.category} : {})};
}

export function reuseOptions(session, burn, status) {
  if (burn.status !== 'completed' || !burn.output_url || !status.ready_for_publish) fail(409, 'This run is not ready. Finish preparation in the editor first');
  const config = copy(session?.config), render = copy(burn.config);
  if (!Object.keys(render).length) fail(409, 'The saved render settings are missing');
  return {...config, burnLayout: render, logo: render.logo || config.logo || {enabled: false},
    burnSubtitles: render.burnSubtitles ?? config.burnSubtitles ?? true,
    translationLanguages: [...(render.slots || [])].reverse().map(s => s.language).filter(Boolean),
    usePolishedSubtitles: true, subtitleSourceVersion: 'polished', publicationMode: 'override',
    publicationSessionId: session?.id || null, autoCorrectSubtitles: false, autoCorrectPrompt: '',
    metadataPrompt: '', useCorrectionPromptForMetadata: false};
}

export function checkPublicationJobs(jobs, videoId, platforms, publishing) {
  if (!Array.isArray(jobs)) fail(502, 'Publication queue is unavailable');
  const previous = jobs.filter(j => Number(j.video_id) === videoId);
  if (previous.some(j => ['queued', 'processing', 'running', 'publishing', 'submitted'].includes(j.status))) fail(409, 'This video already has an active task. Follow it in Activity');
  if (publishing) {
    for (const job of previous) {
      const channels = Array.isArray(job.platforms) ? job.platforms : Object.keys(job.platforms || {}).filter(k => job.platforms[k]);
      const overlap = platforms.filter(p => channels.includes(p));
      if (overlap.length) fail(409, `Publication history exists for ${overlap.join(', ')}. Check its receipts in the full editor before repeating`);
    }
  }
}
