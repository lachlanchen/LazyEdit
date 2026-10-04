import React, { useState } from 'react';
import { ActivityIndicator, Modal, Pressable, ScrollView, Text, TextInput, View } from 'react-native';
import type { SubtitleLanguage } from '@/lib/subtitleLanguages';
import { useI18n } from '@/components/I18nProvider';

export default function SubtitleLanguagePicker({ selected, languages, onChange, resolve, error = '', disabled = false, reservedRows }: {
  selected: string[];
  languages: SubtitleLanguage[];
  onChange: (codes: string[]) => void;
  resolve: (code: string) => Promise<string>;
  error?: string;
  disabled?: boolean;
  reservedRows?: number;
}) {
  const { t } = useI18n();
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState('');
  const [problem, setProblem] = useState('');
  const [busy, setBusy] = useState(false);
  const add = async (code: string) => {
    if (disabled || busy) return;
    setBusy(true); setProblem('');
    try {
      const canonical = await resolve(code);
      if (!selected.includes(canonical)) onChange([...selected, canonical]);
      setOpen(false); setQuery('');
    } catch (e: any) { setProblem(e.message || 'Unsupported subtitle language'); }
    finally { setBusy(false); }
  };
  const choices = languages.filter((item) => !selected.includes(item.code)
    && `${item.name} ${item.code}`.toLowerCase().includes(query.toLowerCase()));
  return <View style={{ gap: 8 }}>
    <Text>{t('subtitle_languages_order')}</Text>
    <View style={{ flexDirection: 'row', flexWrap: 'wrap', gap: 8 }}>
      {selected.map((code, index) => <Pressable key={code}
        accessibilityLabel={t('subtitle_languages_remove', { value: languages.find((l) => l.code === code)?.name || code })}
        disabled={disabled || busy}
        onPress={() => onChange(selected.filter((item) => item !== code))}
        style={{ padding: 10, borderRadius: 10, backgroundColor: '#dbeafe' }}>
        <Text>{reservedRows ? `${Math.max(reservedRows, selected.length) - index} · ` : ''}{languages.find((l) => l.code === code)?.name || code} ×</Text>
      </Pressable>)}
      <Pressable disabled={disabled || busy} onPress={() => setOpen(true)} style={{ padding: 10, borderRadius: 10, backgroundColor: '#e2e8f0' }}><Text>{t('subtitle_languages_add')}</Text></Pressable>
    </View>
    {error ? <Text style={{ color: '#b91c1c' }}>{error}</Text> : null}
    {languages.filter((item) => selected.includes(item.code) && item.renderingWarning).map((item) =>
      <Text key={item.code} style={{ color: '#92400e' }}>{item.name}: {item.renderingWarning}</Text>)}
    <Modal transparent visible={open} animationType="fade" onRequestClose={() => !busy && setOpen(false)}>
      <View style={{ flex: 1, backgroundColor: '#0006', justifyContent: 'center', padding: 24 }}>
        <View style={{ backgroundColor: 'white', padding: 20, borderRadius: 16, gap: 12, maxHeight: '80%' }}>
          <Text>{t('publish_option_language_count_title')}</Text>
          <TextInput placeholder={t('subtitle_languages_search')} value={query} onChangeText={setQuery} autoCapitalize="none" autoCorrect={false}
            style={{ borderWidth: 1, borderColor: '#cbd5e1', borderRadius: 8, padding: 12 }} />
          {problem ? <Text style={{ color: '#b91c1c' }}>{problem}</Text> : null}
          {busy ? <ActivityIndicator /> : <>
            <ScrollView style={{ maxHeight: 300 }}>{choices.map((item) => <Pressable key={item.code} onPress={() => void add(item.code)} style={{ paddingVertical: 10 }}><Text>{item.name} · {item.code}</Text></Pressable>)}</ScrollView>
            {query.trim() ? <Pressable onPress={() => void add(query)}><Text>{t('subtitle_languages_use')}</Text></Pressable> : null}
            <Pressable onPress={() => setOpen(false)}><Text>{t('button_cancel')}</Text></Pressable>
          </>}
        </View>
      </View>
    </Modal>
  </View>;
}
