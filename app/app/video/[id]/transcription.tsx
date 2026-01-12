import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { ActivityIndicator, Pressable, ScrollView, StyleSheet, Text, TextInput, View } from 'react-native';
import { Stack, useLocalSearchParams } from 'expo-router';

const API_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8787';

type TranscriptionDetail = {
  id: number;
  status: string;
  md_url?: string | null;
  srt_url?: string | null;
  json_url?: string | null;
  primary_language?: string | null;
  language_summary?: { language: string; count: number }[];
  error?: string | null;
  created_at?: string | null;
};

type TranscriptionLine = {
  start: string;
  end: string;
  text: string;
  lang?: string | null;
};

const formatTimestamp = (value?: string | null) =>
  value ? value.slice(0, 19).replace('T', ' ') : 'Unknown time';

const AUDIO_LANG_LABELS: Record<string, string> = {
  en: 'English',
  ja: 'Japanese',
  zh: 'Chinese',
  yue: 'Cantonese',
  ko: 'Korean',
  vi: 'Vietnamese',
  ar: 'Arabic',
  fr: 'French',
  es: 'Spanish',
  ru: 'Russian',
};

const formatAudioLanguage = (code: string) => {
  const label = AUDIO_LANG_LABELS[code] || code.toUpperCase();
  return `${label} (${code})`;
};

export default function TranscriptionScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const [transcription, setTranscription] = useState<TranscriptionDetail | null>(null);
  const [lines, setLines] = useState<TranscriptionLine[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');
  const [editingIndex, setEditingIndex] = useState<number | null>(null);
  const [editValue, setEditValue] = useState('');
  const [editOriginal, setEditOriginal] = useState('');
  const [editSaving, setEditSaving] = useState(false);
  const [editError, setEditError] = useState('');
  const skipAutoSaveRef = useRef(false);
  const lastTapRef = useRef<{ key: string; time: number } | null>(null);

  const headerTitle = useMemo(() => 'Transcription', []);
  const languageLine = useMemo(() => {
    if (!transcription) return null;
    if (transcription.primary_language) {
      return `Language: ${formatAudioLanguage(transcription.primary_language)}`;
    }
    const summary = transcription.language_summary || [];
    if (!summary.length) return null;
    const labels = summary.map((item) => formatAudioLanguage(item.language));
    return `Languages: ${labels.join(', ')}`;
  }, [transcription]);

  const parseTranscriptionPayload = useCallback((payload: any): TranscriptionLine[] => {
    if (!payload) return [];
    const items = Array.isArray(payload)
      ? payload
      : payload.items || payload.subtitles || payload.segments || [];
    if (!Array.isArray(items)) return [];
    return items
      .map((item: any) => ({
        start: String(item?.start || ''),
        end: String(item?.end || ''),
        text: item?.text ? String(item.text) : '',
        lang: item?.lang ? String(item.lang) : null,
      }))
      .filter((item: TranscriptionLine) => item.start && item.end);
  }, []);

  const startEditing = useCallback((index: number, text: string) => {
    setEditingIndex(index);
    setEditValue(text);
    setEditOriginal(text);
    setEditError('');
  }, []);

  const handleLinePress = useCallback(
    (key: string, index: number, text: string) => {
      const now = Date.now();
      if (lastTapRef.current && lastTapRef.current.key === key && now - lastTapRef.current.time < 320) {
        lastTapRef.current = null;
        startEditing(index, text);
        return;
      }
      lastTapRef.current = { key, time: now };
    },
    [startEditing],
  );

  const saveEdit = useCallback(async () => {
    if (editingIndex === null || !id) return;
    const trimmed = editValue.trim();
    if (trimmed === editOriginal.trim()) {
      setEditingIndex(null);
      return;
    }
    setEditSaving(true);
    setEditError('');
    try {
      const resp = await fetch(`${API_URL}/api/videos/${id}/transcription`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ index: editingIndex, text: editValue }),
      });
      const json = await resp.json().catch(() => ({}));
      if (!resp.ok) {
        throw new Error(json.error || 'Save failed');
      }
      setLines((prev) =>
        prev.map((line, idx) => (idx === editingIndex ? { ...line, text: trimmed } : line)),
      );
      setEditingIndex(null);
    } catch (e: any) {
      setEditError(e?.message || 'Save failed');
    } finally {
      setEditSaving(false);
    }
  }, [editingIndex, editValue, editOriginal, id]);

  const cancelEdit = useCallback(() => {
    skipAutoSaveRef.current = true;
    setEditingIndex(null);
    setEditValue('');
    setEditOriginal('');
    setEditError('');
  }, []);

  useEffect(() => {
    if (!id) return;
    (async () => {
      setLoading(true);
      try {
        const resp = await fetch(`${API_URL}/api/videos/${id}/transcription`, { cache: 'no-store' });
        const json = await resp.json();
        if (!resp.ok) {
          setError(json.error || 'Failed to load transcription');
          setTranscription(null);
          return;
        }
        setTranscription(json);
        const url = json.json_url;
        if (!url) {
          setLines([]);
          return;
        }
        const fileResp = await fetch(`${API_URL}${url}?t=${Date.now()}`);
        const payload = await fileResp.json();
        setLines(parseTranscriptionPayload(payload));
      } catch (e: any) {
        setError(e?.message || 'Failed to load transcription');
        setTranscription(null);
      } finally {
        setLoading(false);
      }
    })();
  }, [id]);

  if (loading) {
    return (
      <View style={styles.container}>
        <Stack.Screen options={{ title: headerTitle, headerBackTitle: 'Video' }} />
        <ActivityIndicator />
        <Text style={styles.loadingText}>Loading transcription...</Text>
      </View>
    );
  }

  if (!transcription) {
    return (
      <View style={styles.container}>
        <Stack.Screen options={{ title: headerTitle, headerBackTitle: 'Video' }} />
        <Text style={styles.title}>Transcription not available</Text>
        {error ? <Text style={styles.error}>{error}</Text> : null}
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <Stack.Screen options={{ title: headerTitle, headerBackTitle: 'Video' }} />
      <Text style={styles.title}>Transcription</Text>
      <Text style={styles.meta}>Status: {transcription.status}</Text>
      {languageLine ? <Text style={styles.meta}>{languageLine}</Text> : null}
      <Text style={styles.meta}>Created: {formatTimestamp(transcription.created_at)}</Text>
      {transcription.error ? <Text style={styles.error}>{transcription.error}</Text> : null}
      <ScrollView style={styles.content} contentContainerStyle={{ paddingBottom: 24 }}>
        {lines.length ? (
          lines.map((line, idx) => {
            const isEditing = editingIndex === idx;
            const key = `${line.start}-${line.end}-${idx}`;
            return (
              <Pressable
                key={key}
                style={styles.lineBlock}
                onPress={() => handleLinePress(key, idx, line.text)}
                onLongPress={() => startEditing(idx, line.text)}
              >
                <Text style={styles.lineTime}>{line.start} → {line.end}</Text>
                {line.lang ? <Text style={styles.lineLang}>{line.lang.toUpperCase()}</Text> : null}
                {isEditing ? (
                  <>
                    <TextInput
                      style={styles.editInput}
                      value={editValue}
                      onChangeText={setEditValue}
                      multiline
                      onBlur={() => {
                        if (editingIndex !== idx) return;
                        if (skipAutoSaveRef.current) {
                          skipAutoSaveRef.current = false;
                          return;
                        }
                        saveEdit();
                      }}
                    />
                    {editError ? <Text style={styles.editError}>{editError}</Text> : null}
                    <View style={styles.editActions}>
                      <Pressable style={styles.actionButton} onPress={cancelEdit}>
                        <Text style={styles.actionText}>Cancel</Text>
                      </Pressable>
                      <Pressable
                        style={[styles.actionButton, styles.actionPrimary]}
                        onPress={saveEdit}
                        disabled={editSaving}
                      >
                        <Text style={styles.actionPrimaryText}>{editSaving ? 'Saving...' : 'Save'}</Text>
                      </Pressable>
                    </View>
                  </>
                ) : (
                  <Text style={styles.lineText}>{line.text || '—'}</Text>
                )}
              </Pressable>
            );
          })
        ) : (
          <Text style={styles.contentText}>No transcription text available.</Text>
        )}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16, backgroundColor: '#fbfdff' },
  title: { fontSize: 20, fontWeight: '700', color: '#0f172a' },
  meta: { fontSize: 12, color: '#475569', marginTop: 4 },
  error: { fontSize: 12, color: '#b91c1c', marginTop: 8 },
  content: {
    marginTop: 12,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#e2e8f0',
    backgroundColor: 'white',
    padding: 12,
    maxHeight: '80%',
  },
  contentText: { fontSize: 12, color: '#0f172a', lineHeight: 18 },
  lineBlock: {
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#e2e8f0',
  },
  lineTime: { fontSize: 11, color: '#64748b', marginBottom: 4 },
  lineLang: { fontSize: 10, color: '#94a3b8', marginBottom: 6 },
  lineText: { fontSize: 13, color: '#0f172a', lineHeight: 18 },
  editInput: {
    borderWidth: 1,
    borderColor: '#cbd5f5',
    borderRadius: 8,
    padding: 8,
    fontSize: 13,
    color: '#0f172a',
    minHeight: 44,
  },
  editActions: { flexDirection: 'row', justifyContent: 'flex-end', marginTop: 8 },
  actionButton: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 999,
    borderWidth: 1,
    borderColor: '#cbd5f5',
    marginLeft: 8,
  },
  actionText: { fontSize: 12, fontWeight: '600', color: '#0f172a' },
  actionPrimary: { backgroundColor: '#1d4ed8', borderColor: '#1d4ed8' },
  actionPrimaryText: { fontSize: 12, fontWeight: '700', color: '#f8fafc' },
  editError: { fontSize: 11, color: '#b91c1c', marginTop: 6 },
  loadingText: { marginTop: 8, color: '#475569' },
});
