import { useCallback, useEffect, useMemo, useState } from 'react';
import { isSubtitleLanguage, mergeSubtitleLanguages, resolveSubtitleLanguage, type SubtitleLanguage } from './subtitleLanguages';

export function useSubtitleLanguages(api: string, extraCodes: string[] = []) {
  const [catalogue, setCatalogue] = useState<SubtitleLanguage[]>([]);
  const [error, setError] = useState('');
  useEffect(() => {
    let active = true;
    (async () => {
      try {
        const response = await fetch(`${api}/api/languages`);
        const data = await response.json();
        if (!response.ok || !Array.isArray(data.languages) || !data.languages.every(isSubtitleLanguage)) throw new Error(data.error || 'Could not load subtitle languages');
        if (active) { setCatalogue(data.languages); setError(''); }
      } catch (e: any) { if (active) setError(e.message || 'Could not load subtitle languages'); }
    })();
    return () => { active = false; };
  }, [api]);
  const resolve = useCallback(async (code: string) => {
    const language = await resolveSubtitleLanguage(api, code);
    setCatalogue((current) => mergeSubtitleLanguages([...current, language], []));
    return language.code;
  }, [api]);
  const languages = useMemo(() => mergeSubtitleLanguages(catalogue, extraCodes), [catalogue, extraCodes]);
  return { languages, error, resolve };
}
