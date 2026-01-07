import React, { useEffect, useMemo, useState } from 'react';
import { ActivityIndicator, ScrollView, StyleSheet, Text, View } from 'react-native';
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
  const [content, setContent] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');

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

  useEffect(() => {
    if (!id) return;
    (async () => {
      setLoading(true);
      try {
        const resp = await fetch(`${API_URL}/api/videos/${id}/transcription`);
        const json = await resp.json();
        if (!resp.ok) {
          setError(json.error || 'Failed to load transcription');
          setTranscription(null);
          return;
        }
        setTranscription(json);

        const url = json.md_url || json.srt_url;
        if (!url) {
          setContent('');
          return;
        }
        const fileResp = await fetch(`${API_URL}${url}`);
        const text = await fileResp.text();
        setContent(text);
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
        <Text style={styles.contentText}>{content || 'No transcription text available.'}</Text>
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
  loadingText: { marginTop: 8, color: '#475569' },
});
