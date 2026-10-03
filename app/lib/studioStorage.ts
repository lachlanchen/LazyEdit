/** Account + workspace scoped browser drafts. Never read the old shared cache. */
function key(value: string): string | null {
  if (process.env.EXPO_PUBLIC_REMOTE_STUDIO !== '1') return value;
  const scope = (globalThis as any).__studioContext?.scope;
  return typeof scope === 'string' && /^[a-f0-9]{32}$/.test(scope) ? `studio:${scope}:${value}` : null;
}
export const studioStorage = {
  getItem(value: string) { const scoped = key(value); return scoped ? localStorage.getItem(scoped) : null; },
  setItem(value: string, data: string) { const scoped = key(value); if (scoped) localStorage.setItem(scoped, data); },
  removeItem(value: string) { const scoped = key(value); if (scoped) localStorage.removeItem(scoped); },
};
