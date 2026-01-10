import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import { Platform } from 'react-native';

import { DEFAULT_LOCALE, formatMessage, resolveLocale, SUPPORTED_LANGUAGES, TRANSLATIONS, type Locale } from '@/i18n';

type I18nContextValue = {
  locale: Locale;
  setLocale: (locale: Locale) => void;
  t: (key: string, vars?: Record<string, string | number>) => string;
  languages: typeof SUPPORTED_LANGUAGES;
};

const STORAGE_KEY = 'lazyedit:locale';

const I18nContext = createContext<I18nContextValue | null>(null);

export function I18nProvider({ children }: { children: React.ReactNode }) {
  const [locale, setLocaleState] = useState<Locale>(DEFAULT_LOCALE);

  useEffect(() => {
    if (Platform.OS !== 'web') return;
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      const resolved = resolveLocale(stored);
      setLocaleState(resolved);
    } catch (_err) {
      // ignore storage errors
    }
  }, []);

  useEffect(() => {
    if (Platform.OS !== 'web') return;
    try {
      document.documentElement.lang = locale.startsWith('zh') ? 'zh' : locale;
      document.documentElement.dir = locale === 'ar' ? 'rtl' : 'ltr';
    } catch (_err) {
      // ignore DOM errors
    }
  }, [locale]);

  const setLocale = useCallback((next: Locale) => {
    const resolved = resolveLocale(next);
    setLocaleState(resolved);
    if (Platform.OS !== 'web') return;
    try {
      localStorage.setItem(STORAGE_KEY, resolved);
    } catch (_err) {
      // ignore storage errors
    }
  }, []);

  const t = useCallback(
    (key: string, vars?: Record<string, string | number>) => {
      const table = TRANSLATIONS[locale] || TRANSLATIONS[DEFAULT_LOCALE];
      const template = table[key] || TRANSLATIONS[DEFAULT_LOCALE][key] || key;
      return formatMessage(template, vars);
    },
    [locale],
  );

  const value = useMemo<I18nContextValue>(
    () => ({
      locale,
      setLocale,
      t,
      languages: SUPPORTED_LANGUAGES,
    }),
    [locale, setLocale, t],
  );

  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>;
}

export function useI18n() {
  const ctx = useContext(I18nContext);
  if (!ctx) {
    throw new Error('useI18n must be used within I18nProvider');
  }
  return ctx;
}
