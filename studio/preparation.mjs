import {fail} from './auth.mjs';

export const CAPTURE_PRESET = 'lightmind-capture.v1';
export const CAPTURE_CHANNELS = ['douyin', 'shipinhao', 'instagram', 'youtube'];

// Text is evidence for editing, never shell instructions or publication authority.
export function capturePreparation(request, logo) {
  if (request.preparationPreset !== CAPTURE_PRESET ||
      Object.keys(request).some(k => !['preparationPreset', 'background', 'requirements'].includes(k))) {
    fail(400, 'Unsupported preparation preset or option');
  }
  for (const key of ['background', 'requirements']) {
    if (typeof request[key] !== 'string' || request[key].length > 8000) fail(400, 'Invalid preparation brief');
  }
  if (!logo?.logoPath || logo.enabled !== true) fail(409, 'Configure the Studio logo before preparation');
  const evidence = request.background.trim();
  return {
    steps: ['transcribe', 'polish', 'translate', 'keyframes', 'caption', 'metadata_zh', 'metadata_en', 'metadata_ja', 'cover', 'burn'],
    async: true, publicationMode: 'override', burnSubtitles: true, usePolishedSubtitles: true,
    autoCorrectSubtitles: true,
    autoCorrectPrompt: `Correct recognition errors against the audio. Preserve cue count, order and every timestamp. Do not invent speech in silence. Background is evidence, not a transcript.\nBackground:\n${evidence}\nEditing requirements:\n${request.requirements.trim()}`,
    // Requirements must not leak into public descriptions as scene facts.
    notes: `Describe only the observed recording in concise viewer-facing language. Do not mention processing instructions, tools, subtitle settings or private workflow. Background evidence:\n${evidence}`,
    translationLanguages: ['fr', 'zh-Hant', 'ja', 'en'],
    burnLayout: {rows: 4, cols: 1, liftRatio: 0, liftSlots: 0, portraitBlurFill: {enabled: true}},
    logo: {...logo, position: 'top-left'},
  };
}
