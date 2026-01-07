import React, { useEffect, useMemo, useState } from 'react';
import { FlatList, Pressable, StyleSheet, Text, View } from 'react-native';

import { useI18n } from '@/components/I18nProvider';

const API_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8787';

type Lang = { code: string; name: string; plugin: string; rtl?: boolean };

export default function SettingsScreen() {
  const [langs, setLangs] = useState<Lang[]>([]);
  const [selected, setSelected] = useState<Record<string, boolean>>({});
  const { t } = useI18n();
  const preferred = useMemo(
    () => ['en', 'zh-Hant', 'zh-Hans', 'ja', 'ko', 'vi', 'ar', 'fr', 'es', 'ru'],
    [],
  );
  const selectedList = useMemo(() => Object.keys(selected).filter((k) => selected[k]), [selected]);
  const orderedLangs = useMemo(() => {
    const byCode = new Map(langs.map((lang) => [lang.code, lang]));
    const ordered: Lang[] = [];
    preferred.forEach((code) => {
      const item = byCode.get(code);
      if (item) ordered.push(item);
    });
    langs.forEach((lang) => {
      if (!preferred.includes(lang.code)) ordered.push(lang);
    });
    return ordered;
  }, [langs, preferred]);

  useEffect(() => {
    (async () => {
      try {
        const r = await fetch(`${API_URL}/api/languages`);
        const j = await r.json();
        const arr: Lang[] = j.languages || [];
        setLangs(arr);
        // default select English + Japanese
        const init: Record<string, boolean> = {};
        for (const l of arr) init[l.code] = l.code === 'en' || l.code === 'ja';
        setSelected(init);
      } catch {}
    })();
  }, []);

  return (
    <View style={styles.container}>
      <Text style={styles.title}>{t('settings_title')}</Text>
      <Text style={styles.sub}>{t('settings_subtitle')}</Text>

      <FlatList
        style={{ marginTop: 12 }}
        data={orderedLangs}
        keyExtractor={(x) => x.code}
        renderItem={({ item }) => (
          <Pressable
            style={styles.row}
            onPress={() => setSelected((s) => ({ ...s, [item.code]: !s[item.code] }))}
          >
            <View style={[styles.checkbox, selected[item.code] && styles.checkboxChecked]}>
              {selected[item.code] ? <View style={styles.checkboxDot} /> : null}
            </View>
            <View style={{ flex: 1 }}>
              <Text style={styles.langName}>{item.name}</Text>
              <Text style={styles.langCode}>{item.code}{item.rtl ? ' · RTL' : ''}</Text>
            </View>
          </Pressable>
        )}
        ListEmptyComponent={<Text style={styles.empty}>{t('settings_loading')}</Text>}
      />

      <Text style={styles.selected}>
        {t('label_selected', { value: selectedList.join(', ') || t('label_none') })}
      </Text>
      <Text style={styles.backend}>{t('settings_backend_label', { value: API_URL })}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16, backgroundColor: '#fbfdff' },
  title: { fontSize: 22, fontWeight: '700', color: '#0f172a' },
  sub: { marginTop: 8, color: '#334155' },
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 10,
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderBottomColor: '#e2e8f0',
  },
  checkbox: {
    width: 22,
    height: 22,
    borderRadius: 6,
    borderWidth: 2,
    borderColor: '#94a3b8',
    marginRight: 12,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#f8fafc',
  },
  checkboxChecked: {
    borderColor: '#2563eb',
    backgroundColor: '#dbeafe',
  },
  checkboxDot: {
    width: 10,
    height: 10,
    borderRadius: 3,
    backgroundColor: '#2563eb',
  },
  langName: { fontSize: 16, fontWeight: '600', color: '#0f172a' },
  langCode: { fontSize: 12, color: '#64748b' },
  empty: { marginTop: 16, color: '#64748b' },
  selected: { marginTop: 12, color: '#0f172a' },
  backend: { marginTop: 12, color: '#64748b', fontSize: 12 },
});
