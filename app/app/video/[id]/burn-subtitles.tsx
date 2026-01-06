import React, { useEffect, useMemo, useState } from 'react';
import { ActivityIndicator, Modal, Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';
import { Stack, useLocalSearchParams } from 'expo-router';

const API_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8787';

type TranslationDetail = {
  id: number;
  language_code: string;
  status: string;
  output_json_path?: string | null;
  error?: string | null;
};

type BurnSlot = {
  slot: number;
  language: string | null;
};

type BurnStatus = {
  id: number;
  status: string;
  output_url?: string | null;
  error?: string | null;
  created_at?: string | null;
  config?: { slots?: BurnSlot[] } | null;
};

type SelectOption = {
  value: string;
  label: string;
};

const LANG_LABELS: Record<string, string> = {
  en: 'English',
  ja: 'Japanese',
  ar: 'Arabic',
  vi: 'Vietnamese',
  ko: 'Korean',
  es: 'Spanish',
  fr: 'French',
  ru: 'Russian',
  'zh-Hant': 'Chinese (Traditional)',
  'zh-Hans': 'Chinese (Simplified)',
};

const SLOT_LABELS: Record<number, string> = {
  1: 'Slot 1 · Top left',
  2: 'Slot 2 · Top right',
  3: 'Slot 3 · Bottom left',
  4: 'Slot 4 · Bottom right',
};

const DEFAULT_SLOTS: BurnSlot[] = [
  { slot: 1, language: 'en' },
  { slot: 2, language: 'ja' },
  { slot: 3, language: null },
  { slot: 4, language: null },
];

const OptionSelect = ({
  label,
  value,
  options,
  onChange,
}: {
  label: string;
  value: string;
  options: SelectOption[];
  onChange: (next: string) => void;
}) => {
  const [open, setOpen] = useState(false);

  return (
    <>
      <Pressable style={styles.select} onPress={() => setOpen(true)}>
        <Text style={styles.selectLabel}>{label}</Text>
        <Text style={styles.selectValue}>{options.find((opt) => opt.value === value)?.label || 'None'}</Text>
      </Pressable>
      <Modal visible={open} transparent animationType="fade">
        <Pressable style={styles.modalBackdrop} onPress={() => setOpen(false)}>
          <Pressable style={styles.modalCard} onPress={() => {}}>
            <Text style={styles.modalTitle}>Select language</Text>
            <ScrollView style={{ maxHeight: 280 }}>
              {options.map((option) => {
                const active = option.value === value;
                return (
                  <Pressable
                    key={option.value}
                    style={[styles.modalOption, active && styles.modalOptionActive]}
                    onPress={() => {
                      onChange(option.value);
                      setOpen(false);
                    }}
                  >
                    <Text style={[styles.modalOptionText, active && styles.modalOptionTextActive]}>{option.label}</Text>
                  </Pressable>
                );
              })}
            </ScrollView>
          </Pressable>
        </Pressable>
      </Modal>
    </>
  );
};

const formatTimestamp = (value?: string | null) =>
  value ? value.slice(0, 19).replace('T', ' ') : 'Unknown time';

export default function BurnSubtitlesScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const [translations, setTranslations] = useState<TranslationDetail[]>([]);
  const [slots, setSlots] = useState<BurnSlot[]>(DEFAULT_SLOTS);
  const [status, setStatus] = useState<BurnStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [burning, setBurning] = useState(false);
  const [message, setMessage] = useState('');
  const [layoutLoaded, setLayoutLoaded] = useState(false);

  const availableOptions = useMemo(() => {
    const base: SelectOption[] = [{ value: '', label: 'None' }];
    const seen = new Set<string>();
    const available = translations.filter((item) => item.status === 'completed');
    for (const item of available) {
      if (seen.has(item.language_code)) continue;
      seen.add(item.language_code);
      base.push({
        value: item.language_code,
        label: LANG_LABELS[item.language_code] || item.language_code,
      });
    }
    return base;
  }, [translations]);

  const loadTranslations = async () => {
    if (!id) return;
    try {
      const resp = await fetch(`${API_URL}/api/videos/${id}/translations`);
      const json = await resp.json();
      if (!resp.ok) {
        setTranslations([]);
        return;
      }
      setTranslations(json.translations || []);
    } catch (_err) {
      setTranslations([]);
    }
  };

  const loadLayout = async () => {
    try {
      const resp = await fetch(`${API_URL}/api/ui-settings/burn_layout`);
      const json = await resp.json();
      if (!resp.ok) return;
      const value = json.value;
      if (value?.slots && Array.isArray(value.slots)) {
        const normalized = value.slots
          .filter((slot: BurnSlot) => typeof slot.slot === 'number')
          .map((slot: BurnSlot) => ({
            slot: slot.slot,
            language: slot.language || null,
          }));
        if (normalized.length) setSlots(normalized);
      }
    } catch (_err) {
      // ignore
    } finally {
      setLayoutLoaded(true);
    }
  };

  const loadBurnStatus = async () => {
    if (!id) return;
    try {
      const resp = await fetch(`${API_URL}/api/videos/${id}/burn-subtitles`);
      if (resp.status === 404) {
        setStatus(null);
        return;
      }
      const json = await resp.json();
      if (!resp.ok) {
        setStatus(null);
        setMessage(json.error || 'Failed to load burn status');
        return;
      }
      setStatus(json);
    } catch (err: any) {
      setMessage(err?.message || 'Failed to load burn status');
    }
  };

  useEffect(() => {
    (async () => {
      setLoading(true);
      await loadTranslations();
      await loadLayout();
      await loadBurnStatus();
      setLoading(false);
    })();
  }, [id]);

  useEffect(() => {
    if (!layoutLoaded) return;
    const payload = { slots };
    const timeout = setTimeout(async () => {
      try {
        await fetch(`${API_URL}/api/ui-settings/burn_layout`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });
      } catch (_err) {
        // ignore
      }
    }, 200);
    return () => clearTimeout(timeout);
  }, [slots, layoutLoaded]);

  const updateSlot = (slotId: number, language: string) => {
    setSlots((prev) =>
      prev.map((slot) => (slot.slot === slotId ? { ...slot, language: language || null } : slot))
    );
  };

  const burnSubtitles = async () => {
    if (!id || burning) return;
    setBurning(true);
    setMessage('Burning subtitles... this can take a few minutes.');
    try {
      const resp = await fetch(`${API_URL}/api/videos/${id}/burn-subtitles`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ slots }),
      });
      const json = await resp.json();
      if (!resp.ok) {
        setMessage(json.error || json.details || 'Burn failed');
        setBurning(false);
        return;
      }
      setStatus(json);
      setMessage('Burn complete.');
    } catch (err: any) {
      setMessage(err?.message || 'Burn failed');
    } finally {
      setBurning(false);
    }
  };

  if (loading) {
    return (
      <View style={styles.container}>
        <Stack.Screen options={{ title: 'Burn subtitles', headerBackTitle: 'Video' }} />
        <ActivityIndicator />
        <Text style={styles.loadingText}>Loading burn settings...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <Stack.Screen options={{ title: 'Burn subtitles', headerBackTitle: 'Video' }} />
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.card}>
          <Text style={styles.title}>Burn subtitles</Text>
          <Text style={styles.meta}>Assign languages to the 4-slot bottom grid.</Text>

          <View style={styles.slotGrid}>
            {slots.map((slot) => (
              <View key={slot.slot} style={styles.slotCard}>
                <Text style={styles.slotTitle}>{SLOT_LABELS[slot.slot] || `Slot ${slot.slot}`}</Text>
                <OptionSelect
                  label="Language"
                  value={slot.language || ''}
                  options={availableOptions}
                  onChange={(value) => updateSlot(slot.slot, value)}
                />
              </View>
            ))}
          </View>

          <Pressable style={[styles.btnPrimary, burning && styles.btnDisabled]} onPress={burnSubtitles}>
            <Text style={styles.btnText}>{burning ? 'Burning…' : 'Burn subtitles'}</Text>
          </Pressable>

          {message ? <Text style={styles.status}>{message}</Text> : null}
        </View>

        <View style={styles.card}>
          <Text style={styles.title}>Latest burn</Text>
          {status ? (
            <>
              <Text style={styles.meta}>Status: {status.status}</Text>
              <Text style={styles.meta}>Updated: {formatTimestamp(status.created_at)}</Text>
              {status.error ? <Text style={styles.error}>{status.error}</Text> : null}
              {status.output_url ? (
                <View style={styles.previewBox}>
                  {React.createElement('video', {
                    src: `${API_URL}${status.output_url}`,
                    controls: true,
                    style: {
                      width: '100%',
                      borderRadius: 12,
                      backgroundColor: '#0f172a',
                    },
                  })}
                </View>
              ) : (
                <Text style={styles.meta}>No output yet.</Text>
              )}
            </>
          ) : (
            <Text style={styles.meta}>No burn output yet.</Text>
          )}
        </View>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16, backgroundColor: '#fbfdff' },
  scrollContent: { paddingBottom: 24 },
  title: { fontSize: 18, fontWeight: '700', color: '#0f172a' },
  meta: { fontSize: 12, color: '#475569', marginTop: 4 },
  loadingText: { marginTop: 12, color: '#475569' },
  card: {
    padding: 14,
    borderRadius: 14,
    borderWidth: 1,
    borderColor: '#e2e8f0',
    backgroundColor: 'white',
    marginBottom: 14,
  },
  slotGrid: {
    marginTop: 12,
  },
  slotCard: {
    padding: 12,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#e2e8f0',
    backgroundColor: '#f8fafc',
    marginBottom: 10,
  },
  slotTitle: { fontSize: 13, fontWeight: '600', color: '#0f172a', marginBottom: 6 },
  select: {
    borderWidth: 1,
    borderColor: '#cbd5f5',
    borderRadius: 10,
    paddingVertical: 8,
    paddingHorizontal: 12,
    backgroundColor: 'white',
  },
  selectLabel: { fontSize: 11, textTransform: 'uppercase', color: '#64748b', marginBottom: 2 },
  selectValue: { fontSize: 14, color: '#0f172a', fontWeight: '600' },
  btnPrimary: {
    marginTop: 12,
    backgroundColor: '#1d4ed8',
    paddingVertical: 12,
    borderRadius: 999,
    alignItems: 'center',
  },
  btnDisabled: { opacity: 0.6 },
  btnText: { color: '#f8fafc', fontWeight: '700' },
  status: { marginTop: 10, fontSize: 12, color: '#0f172a' },
  error: { marginTop: 8, color: '#b91c1c', fontSize: 12 },
  previewBox: { marginTop: 12 },
  modalBackdrop: {
    flex: 1,
    backgroundColor: 'rgba(15, 23, 42, 0.5)',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 20,
  },
  modalCard: {
    width: '100%',
    maxWidth: 360,
    backgroundColor: 'white',
    borderRadius: 16,
    padding: 16,
  },
  modalTitle: { fontSize: 14, fontWeight: '700', color: '#0f172a', marginBottom: 8 },
  modalOption: { paddingVertical: 8, borderBottomWidth: 1, borderBottomColor: '#e2e8f0' },
  modalOptionActive: { backgroundColor: '#eff6ff' },
  modalOptionText: { color: '#0f172a', fontSize: 13 },
  modalOptionTextActive: { fontWeight: '700' },
});
