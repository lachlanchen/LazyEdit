export type SubtitleLanguage = {
  code: string;
  name: string;
  reading?: string | null;
  rtl?: boolean;
  requiresPreview?: boolean;
  renderingWarning?: string;
};

export function isSubtitleLanguage(value: unknown): value is SubtitleLanguage {
  if (!value || typeof value !== 'object') return false;
  const row = value as Partial<SubtitleLanguage>;
  return typeof row.code === 'string' && !!row.code && typeof row.name === 'string' && !!row.name;
}

// The API is authoritative. Imported translations and saved choices must not
// disappear simply because they are absent from its common-language catalogue.
export function mergeSubtitleLanguages(catalogue: SubtitleLanguage[], codes: string[]): SubtitleLanguage[] {
  const result = new Map(catalogue.map((item) => [item.code, item]));
  for (const code of codes) {
    if (code && !result.has(code)) result.set(code, { code, name: code, requiresPreview: true });
  }
  return [...result.values()];
}

export async function resolveSubtitleLanguage(api: string, value: string): Promise<SubtitleLanguage> {
  const response = await fetch(`${api}/api/languages`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ languages: [value.trim()] }),
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || 'Unsupported subtitle language');
  if (!Array.isArray(data.languages) || data.languages.length !== 1 || !isSubtitleLanguage(data.languages[0])) throw new Error('Invalid language reply');
  return data.languages[0];
}
