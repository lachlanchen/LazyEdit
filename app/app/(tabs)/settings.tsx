import React, { useEffect, useMemo, useState } from 'react';
import { Image, Platform, Pressable, StyleSheet, Text, TextInput, View } from 'react-native';
import * as DocumentPicker from 'expo-document-picker';
import * as FileSystem from 'expo-file-system';

import { useI18n } from '@/components/I18nProvider';

const API_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8787';

type LogoSettings = {
  logoPath: string | null;
  logoUrl: string | null;
  heightRatio: number;
  position: string;
};

const DEFAULT_LOGO_SETTINGS: LogoSettings = {
  logoPath: null,
  logoUrl: null,
  heightRatio: 0.1,
  position: 'top-right',
};

const POSITION_OPTIONS = [
  { value: 'top-right', label: 'Top right' },
  { value: 'top-left', label: 'Top left' },
  { value: 'bottom-right', label: 'Bottom right' },
  { value: 'bottom-left', label: 'Bottom left' },
  { value: 'center', label: 'Center' },
];

export default function SettingsScreen() {
  const { t } = useI18n();
  const [logoSettings, setLogoSettings] = useState<LogoSettings>(DEFAULT_LOGO_SETTINGS);
  const [logoHeightInput, setLogoHeightInput] = useState(
    String(Math.round(DEFAULT_LOGO_SETTINGS.heightRatio * 100)),
  );
  const [logoPick, setLogoPick] = useState<DocumentPicker.DocumentPickerAsset | null>(null);
  const [logoUploading, setLogoUploading] = useState(false);
  const [logoStatus, setLogoStatus] = useState('');
  const [logoTone, setLogoTone] = useState<'neutral' | 'good' | 'bad'>('neutral');

  useEffect(() => {
    (async () => {
      try {
        const resp = await fetch(`${API_URL}/api/ui-settings/logo_settings`);
        const json = await resp.json();
        if (resp.ok && json.value) {
          const next = { ...DEFAULT_LOGO_SETTINGS, ...json.value };
          setLogoSettings(next);
          setLogoHeightInput(String(Math.round((next.heightRatio || 0.1) * 100)));
        }
      } catch (_err) {
        // ignore
      }
    })();
  }, []);

  const logoPreviewUrl = useMemo(() => {
    const url = logoSettings.logoUrl;
    if (!url) return null;
    return url.startsWith('http') ? url : `${API_URL}${url}`;
  }, [logoSettings.logoUrl]);

  const saveLogoSettings = async (next: LogoSettings) => {
    setLogoSettings(next);
    try {
      await fetch(`${API_URL}/api/ui-settings/logo_settings`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(next),
      });
    } catch (_err) {
      // ignore
    }
  };

  const pickLogo = async () => {
    const res = await DocumentPicker.getDocumentAsync({
      multiple: false,
      type: ['image/*'],
    });
    if (res.canceled) return;
    setLogoPick(res.assets[0]);
    setLogoStatus('Logo selected. Ready to upload.');
    setLogoTone('neutral');
  };

  const uploadLogo = async () => {
    if (!logoPick || logoUploading) return;
    setLogoUploading(true);
    setLogoStatus('Uploading logo...');
    setLogoTone('neutral');
    try {
      if (Platform.OS === 'web') {
        const file = logoPick as any;
        const form = new FormData();
        form.append('image', (file.file as File) ?? (file as any), logoPick.name || 'logo.png');
        const resp = await fetch(`${API_URL}/upload-logo`, { method: 'POST', body: form as any });
        const json = await resp.json();
        if (!resp.ok) {
          setLogoStatus(`Upload failed: ${json.error || json.message || resp.statusText}`);
          setLogoTone('bad');
          return;
        }
        const next = {
          ...logoSettings,
          logoPath: json.file_path || null,
          logoUrl: json.media_url || null,
        };
        await saveLogoSettings(next);
        setLogoStatus('Logo uploaded.');
        setLogoTone('good');
      } else {
        const resp = await FileSystem.uploadAsync(`${API_URL}/upload-logo`, logoPick.uri, {
          fieldName: 'image',
          httpMethod: 'POST',
          uploadType: 'multipart' as any,
          parameters: { filename: logoPick.name || 'logo.png' },
        });
        const json = JSON.parse(resp.body);
        if (resp.status >= 400) {
          setLogoStatus(`Upload failed: ${json.error || json.message || `HTTP ${resp.status}`}`);
          setLogoTone('bad');
          return;
        }
        const next = {
          ...logoSettings,
          logoPath: json.file_path || null,
          logoUrl: json.media_url || null,
        };
        await saveLogoSettings(next);
        setLogoStatus('Logo uploaded.');
        setLogoTone('good');
      }
      setLogoPick(null);
    } catch (e: any) {
      setLogoStatus(`Upload failed: ${e?.message || String(e)}`);
      setLogoTone('bad');
    } finally {
      setLogoUploading(false);
    }
  };

  const clearLogo = async () => {
    const next = { ...logoSettings, logoPath: null, logoUrl: null };
    await saveLogoSettings(next);
    setLogoStatus('Logo cleared.');
    setLogoTone('neutral');
  };

  const commitLogoHeight = async () => {
    const raw = logoHeightInput.replace('%', '').trim();
    if (!raw) {
      setLogoHeightInput(String(Math.round((logoSettings.heightRatio || 0.1) * 100)));
      return;
    }
    const value = Number.parseFloat(raw);
    if (Number.isNaN(value)) {
      setLogoHeightInput(String(Math.round((logoSettings.heightRatio || 0.1) * 100)));
      return;
    }
    const ratio = Math.min(Math.max(value / 100, 0.02), 0.4);
    await saveLogoSettings({ ...logoSettings, heightRatio: ratio });
    setLogoHeightInput(String(Math.round(ratio * 100)));
  };

  const updateLogoPosition = async (position: string) => {
    await saveLogoSettings({ ...logoSettings, position });
  };

  const toneStyle = (tone: 'neutral' | 'good' | 'bad') =>
    tone === 'good' ? styles.statusGood : tone === 'bad' ? styles.statusBad : styles.statusNeutral;

  return (
    <View style={styles.container}>
      <Text style={styles.title}>{t('settings_title')}</Text>
      <Text style={styles.backend}>{t('settings_backend_label', { value: API_URL })}</Text>

      <View style={styles.card}>
        <Text style={styles.sectionTitle}>{t('settings_logo_title')}</Text>
        <Text style={styles.sectionHint}>{t('settings_logo_hint')}</Text>

        {logoPreviewUrl ? (
          <Image source={{ uri: logoPreviewUrl }} style={styles.logoPreview} resizeMode="contain" />
        ) : (
          <Text style={styles.emptyText}>{t('settings_logo_missing')}</Text>
        )}

        <View style={styles.buttonRow}>
          <Pressable style={styles.btnSecondary} onPress={pickLogo}>
            <Text style={styles.btnSecondaryText}>{t('settings_logo_pick')}</Text>
          </Pressable>
          <Pressable
            style={[styles.btnPrimary, (!logoPick || logoUploading) && styles.btnDisabled]}
            onPress={uploadLogo}
          >
            <Text style={styles.btnPrimaryText}>{logoUploading ? 'Uploading...' : t('settings_logo_upload')}</Text>
          </Pressable>
          {logoSettings.logoPath ? (
            <Pressable style={styles.btnDanger} onPress={clearLogo}>
              <Text style={styles.btnDangerText}>{t('settings_logo_remove')}</Text>
            </Pressable>
          ) : null}
        </View>

        {logoStatus ? <Text style={[styles.status, toneStyle(logoTone)]}>{logoStatus}</Text> : null}

        <View style={styles.fieldRow}>
          <View style={{ flex: 1 }}>
            <Text style={styles.settingLabel}>{t('settings_logo_height')}</Text>
            <TextInput
              value={logoHeightInput}
              onChangeText={setLogoHeightInput}
              onBlur={commitLogoHeight}
              onSubmitEditing={commitLogoHeight}
              style={styles.input}
              keyboardType="numeric"
            />
          </View>
        </View>

        <Text style={styles.settingLabel}>{t('settings_logo_position')}</Text>
        <View style={styles.chipRow}>
          {POSITION_OPTIONS.map((option) => (
            <Pressable
              key={option.value}
              style={[
                styles.chip,
                logoSettings.position === option.value && styles.chipActive,
              ]}
              onPress={() => updateLogoPosition(option.value)}
            >
              <Text
                style={[
                  styles.chipText,
                  logoSettings.position === option.value && styles.chipTextActive,
                ]}
              >
                {option.label}
              </Text>
            </Pressable>
          ))}
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16, backgroundColor: '#fbfdff' },
  title: { fontSize: 22, fontWeight: '700', color: '#0f172a' },
  backend: { marginTop: 12, color: '#64748b', fontSize: 12 },
  card: {
    marginTop: 16,
    padding: 14,
    borderRadius: 14,
    borderWidth: 1,
    borderColor: '#e2e8f0',
    backgroundColor: 'white',
  },
  sectionTitle: { fontSize: 16, fontWeight: '700', color: '#0f172a' },
  sectionHint: { marginTop: 4, fontSize: 12, color: '#64748b' },
  logoPreview: { marginTop: 12, width: '100%', height: 140, borderRadius: 12, backgroundColor: '#f8fafc' },
  emptyText: { marginTop: 12, fontSize: 12, color: '#94a3b8' },
  buttonRow: { marginTop: 12, flexDirection: 'row', flexWrap: 'wrap', gap: 8 },
  btnPrimary: {
    paddingVertical: 10,
    paddingHorizontal: 14,
    borderRadius: 999,
    backgroundColor: '#2563eb',
  },
  btnPrimaryText: { color: '#f8fafc', fontWeight: '700', fontSize: 12 },
  btnSecondary: {
    paddingVertical: 10,
    paddingHorizontal: 14,
    borderRadius: 999,
    borderWidth: 1,
    borderColor: '#e2e8f0',
    backgroundColor: '#ffffff',
  },
  btnSecondaryText: { color: '#0f172a', fontWeight: '700', fontSize: 12 },
  btnDanger: {
    paddingVertical: 10,
    paddingHorizontal: 14,
    borderRadius: 999,
    borderWidth: 1,
    borderColor: '#fecaca',
    backgroundColor: '#fee2e2',
  },
  btnDangerText: { color: '#b91c1c', fontWeight: '700', fontSize: 12 },
  btnDisabled: { opacity: 0.6 },
  status: { marginTop: 10, fontSize: 12 },
  statusNeutral: { color: '#475569' },
  statusGood: { color: '#15803d' },
  statusBad: { color: '#b91c1c' },
  settingLabel: { marginTop: 14, fontSize: 12, fontWeight: '700', color: '#0f172a' },
  fieldRow: { marginTop: 8 },
  input: {
    marginTop: 6,
    borderWidth: 1,
    borderColor: '#e2e8f0',
    borderRadius: 10,
    paddingVertical: 8,
    paddingHorizontal: 10,
    fontSize: 13,
    color: '#0f172a',
  },
  chipRow: { marginTop: 8, flexDirection: 'row', flexWrap: 'wrap', gap: 8 },
  chip: {
    paddingVertical: 6,
    paddingHorizontal: 12,
    borderRadius: 999,
    borderWidth: 1,
    borderColor: '#e2e8f0',
    backgroundColor: '#f8fafc',
  },
  chipActive: { backgroundColor: '#1d4ed8', borderColor: '#1d4ed8' },
  chipText: { fontSize: 12, fontWeight: '600', color: '#0f172a' },
  chipTextActive: { color: '#f8fafc' },
});
