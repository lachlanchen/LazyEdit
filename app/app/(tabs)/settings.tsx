import React, { useEffect, useMemo, useState } from 'react';
import { Pressable, ScrollView, StyleSheet, Text, TextInput, View } from 'react-native';

import { useI18n } from '@/components/I18nProvider';

const API_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8787';

type AiProvider = 'deepseek' | 'openai';

type AiModelSettings = {
  defaultProvider: AiProvider;
  defaultModel: string;
  translationProvider: AiProvider;
  translationModel: string;
  correctionProvider: AiProvider;
  correctionModel: string;
  correctionFallbackModel: string;
  correctionMaxRetries: number;
};

const DEFAULT_AI_SETTINGS: AiModelSettings = {
  defaultProvider: 'deepseek',
  defaultModel: 'deepseek-v4-flash',
  translationProvider: 'deepseek',
  translationModel: 'deepseek-v4-flash',
  correctionProvider: 'deepseek',
  correctionModel: 'deepseek-v4-pro',
  correctionFallbackModel: 'deepseek-v4-flash',
  correctionMaxRetries: 1,
};

const PROVIDERS: { value: AiProvider; label: string }[] = [
  { value: 'deepseek', label: 'DeepSeek' },
  { value: 'openai', label: 'OpenAI' },
];

const MODEL_PRESETS = [
  'deepseek-v4-flash',
  'deepseek-v4-pro',
  'gpt-4o-mini',
  'gpt-5.5',
];

export default function SettingsScreen() {
  const { t } = useI18n();
  const [settings, setSettings] = useState<AiModelSettings>(DEFAULT_AI_SETTINGS);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    let cancelled = false;
    const load = async () => {
      try {
        const resp = await fetch(`${API_URL}/api/ui-settings/ai_model_settings`);
        const payload = await resp.json();
        if (!cancelled && payload?.value) {
          setSettings({ ...DEFAULT_AI_SETTINGS, ...payload.value });
        }
      } catch (err) {
        if (!cancelled) setMessage(err instanceof Error ? err.message : 'Failed to load AI settings.');
      } finally {
        if (!cancelled) setLoading(false);
      }
    };
    load();
    return () => {
      cancelled = true;
    };
  }, []);

  const update = <K extends keyof AiModelSettings>(key: K, value: AiModelSettings[K]) => {
    setSettings((prev) => ({ ...prev, [key]: value }));
    setMessage('');
  };

  const save = async () => {
    setSaving(true);
    setMessage('');
    try {
      const resp = await fetch(`${API_URL}/api/ui-settings/ai_model_settings`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(settings),
      });
      const payload = await resp.json();
      if (!resp.ok) throw new Error(payload?.error || 'Failed to save AI settings.');
      setSettings({ ...DEFAULT_AI_SETTINGS, ...payload.value });
      setMessage('Saved.');
    } catch (err) {
      setMessage(err instanceof Error ? err.message : 'Failed to save AI settings.');
    } finally {
      setSaving(false);
    }
  };

  const status = useMemo(
    () =>
      [
        `${settings.defaultProvider}/${settings.defaultModel}`,
        `translate ${settings.translationModel}`,
        `correct ${settings.correctionModel}`,
      ].join(' · '),
    [settings],
  );

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.title}>{t('settings_title')}</Text>
      <Text style={styles.backend}>{t('settings_backend_label', { value: API_URL })}</Text>

      <View style={styles.panel}>
        <View style={styles.panelHeader}>
          <View>
            <Text style={styles.sectionTitle}>AI provider and models</Text>
            <Text style={styles.sectionHint}>{loading ? 'Loading...' : status}</Text>
          </View>
          <Pressable style={[styles.saveButton, saving && styles.buttonDisabled]} onPress={save} disabled={saving || loading}>
            <Text style={styles.saveText}>{saving ? 'Saving...' : 'Save'}</Text>
          </Pressable>
        </View>

        <ModelBlock
          title="Default AI"
          hint="Used by generic structured AI tasks."
          provider={settings.defaultProvider}
          model={settings.defaultModel}
          onProviderChange={(value) => update('defaultProvider', value)}
          onModelChange={(value) => update('defaultModel', value)}
        />
        <ModelBlock
          title="Translation"
          hint="Use V4 Flash for low-cost subtitle translation."
          provider={settings.translationProvider}
          model={settings.translationModel}
          onProviderChange={(value) => update('translationProvider', value)}
          onModelChange={(value) => update('translationModel', value)}
        />
        <ModelBlock
          title="Subtitle correction"
          hint="Use V4 Pro for correction quality; fallback keeps the pipeline running."
          provider={settings.correctionProvider}
          model={settings.correctionModel}
          onProviderChange={(value) => update('correctionProvider', value)}
          onModelChange={(value) => update('correctionModel', value)}
        />

        <View style={styles.fieldGroup}>
          <Text style={styles.label}>Correction fallback</Text>
          <TextInput
            value={settings.correctionFallbackModel}
            onChangeText={(value) => update('correctionFallbackModel', value)}
            autoCapitalize="none"
            style={styles.input}
          />
        </View>

        {message ? <Text style={styles.message}>{message}</Text> : null}
      </View>
    </ScrollView>
  );
}

function ModelBlock({
  title,
  hint,
  provider,
  model,
  onProviderChange,
  onModelChange,
}: {
  title: string;
  hint: string;
  provider: AiProvider;
  model: string;
  onProviderChange: (value: AiProvider) => void;
  onModelChange: (value: string) => void;
}) {
  return (
    <View style={styles.modelBlock}>
      <Text style={styles.blockTitle}>{title}</Text>
      <Text style={styles.blockHint}>{hint}</Text>
      <View style={styles.segment}>
        {PROVIDERS.map((option) => (
          <Pressable
            key={option.value}
            onPress={() => onProviderChange(option.value)}
            style={[styles.segmentButton, provider === option.value && styles.segmentButtonActive]}
          >
            <Text style={[styles.segmentText, provider === option.value && styles.segmentTextActive]}>{option.label}</Text>
          </Pressable>
        ))}
      </View>
      <View style={styles.presetRow}>
        {MODEL_PRESETS.map((preset) => (
          <Pressable
            key={preset}
            onPress={() => onModelChange(preset)}
            style={[styles.chip, model === preset && styles.chipActive]}
          >
            <Text style={[styles.chipText, model === preset && styles.chipTextActive]}>{preset}</Text>
          </Pressable>
        ))}
      </View>
      <TextInput value={model} onChangeText={onModelChange} autoCapitalize="none" style={styles.input} />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f8fafc' },
  content: { padding: 16, gap: 14 },
  title: { fontSize: 22, fontWeight: '700', color: '#0f172a' },
  backend: { color: '#64748b', fontSize: 12 },
  panel: {
    backgroundColor: '#ffffff',
    borderColor: '#d9e2ec',
    borderRadius: 8,
    borderWidth: 1,
    padding: 14,
    gap: 14,
  },
  panelHeader: { alignItems: 'flex-start', flexDirection: 'row', gap: 12, justifyContent: 'space-between' },
  sectionTitle: { color: '#0f172a', fontSize: 16, fontWeight: '700' },
  sectionHint: { color: '#64748b', fontSize: 12, marginTop: 4 },
  saveButton: { backgroundColor: '#2563eb', borderRadius: 6, paddingHorizontal: 14, paddingVertical: 9 },
  buttonDisabled: { opacity: 0.55 },
  saveText: { color: '#ffffff', fontSize: 13, fontWeight: '700' },
  modelBlock: { borderTopColor: '#e5e7eb', borderTopWidth: 1, gap: 9, paddingTop: 14 },
  blockTitle: { color: '#111827', fontSize: 14, fontWeight: '700' },
  blockHint: { color: '#64748b', fontSize: 12 },
  segment: { alignSelf: 'flex-start', backgroundColor: '#eef2f7', borderRadius: 8, flexDirection: 'row', padding: 3 },
  segmentButton: { borderRadius: 6, paddingHorizontal: 12, paddingVertical: 7 },
  segmentButtonActive: { backgroundColor: '#ffffff' },
  segmentText: { color: '#475569', fontSize: 12, fontWeight: '700' },
  segmentTextActive: { color: '#1d4ed8' },
  presetRow: { flexDirection: 'row', flexWrap: 'wrap', gap: 8 },
  chip: { borderColor: '#cbd5e1', borderRadius: 999, borderWidth: 1, paddingHorizontal: 10, paddingVertical: 6 },
  chipActive: { backgroundColor: '#dbeafe', borderColor: '#60a5fa' },
  chipText: { color: '#475569', fontSize: 12 },
  chipTextActive: { color: '#1d4ed8', fontWeight: '700' },
  fieldGroup: { gap: 8 },
  label: { color: '#334155', fontSize: 13, fontWeight: '700' },
  input: {
    backgroundColor: '#ffffff',
    borderColor: '#cbd5e1',
    borderRadius: 6,
    borderWidth: 1,
    color: '#0f172a',
    fontSize: 13,
    paddingHorizontal: 10,
    paddingVertical: 8,
  },
  message: { color: '#334155', fontSize: 12 },
});
