import React, { useEffect, useMemo, useState } from 'react';
import { ActivityIndicator, Image, Modal, Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';
import { Stack, useLocalSearchParams } from 'expo-router';

const API_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8787';

type CaptionDetail = {
  id: number;
  status: string;
  md_url?: string | null;
  srt_url?: string | null;
  json_url?: string | null;
  error?: string | null;
  created_at?: string | null;
  frames?: {
    url: string;
    text?: string | null;
    start?: string | null;
    end?: string | null;
  }[];
};

const formatTimestamp = (value?: string | null) =>
  value ? value.slice(0, 19).replace('T', ' ') : 'Unknown time';

export default function CaptionScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const [caption, setCaption] = useState<CaptionDetail | null>(null);
  const [content, setContent] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');
  const [lightbox, setLightbox] = useState<{ url: string; label?: string } | null>(null);

  const headerTitle = useMemo(() => 'Frame Captions', []);

  useEffect(() => {
    if (!id) return;
    (async () => {
      setLoading(true);
      try {
        const resp = await fetch(`${API_URL}/api/videos/${id}/caption`);
        const json = await resp.json();
        if (!resp.ok) {
          setError(json.error || 'Failed to load captions');
          setCaption(null);
          return;
        }
        setCaption(json);

        const url = json.md_url || json.srt_url;
        if (!url) {
          setContent('');
          return;
        }
        const fileResp = await fetch(`${API_URL}${url}`);
        const text = await fileResp.text();
        setContent(text);
      } catch (e: any) {
        setError(e?.message || 'Failed to load captions');
        setCaption(null);
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
        <Text style={styles.loadingText}>Loading captions...</Text>
      </View>
    );
  }

  if (!caption) {
    return (
      <View style={styles.container}>
        <Stack.Screen options={{ title: headerTitle, headerBackTitle: 'Video' }} />
        <Text style={styles.title}>Captions not available</Text>
        {error ? <Text style={styles.error}>{error}</Text> : null}
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <Stack.Screen options={{ title: headerTitle, headerBackTitle: 'Video' }} />
      <Text style={styles.title}>Frame Captions</Text>
      <Text style={styles.meta}>Status: {caption.status}</Text>
      <Text style={styles.meta}>Created: {formatTimestamp(caption.created_at)}</Text>
      {caption.error ? <Text style={styles.error}>{caption.error}</Text> : null}
      <ScrollView style={styles.content} contentContainerStyle={{ paddingBottom: 24 }}>
        <Text style={styles.contentText}>{content || 'No caption text available.'}</Text>
      </ScrollView>
      {caption.frames && caption.frames.length ? (
        <View style={styles.gallery}>
          <Text style={styles.galleryTitle}>Captioned frames</Text>
          <View style={styles.galleryGrid}>
            {caption.frames.map((frame, idx) => (
              <Pressable
                key={`${frame.url}-${idx}`}
                style={styles.galleryItem}
                onPress={() =>
                  setLightbox({ url: `${API_URL}${frame.url}`, label: frame.text || `Frame ${idx + 1}` })
                }
              >
                <Image source={{ uri: `${API_URL}${frame.url}` }} style={styles.galleryImage} />
                <View style={styles.galleryOverlay}>
                  <Text style={styles.galleryOverlayText} numberOfLines={2}>
                    {frame.text || `Frame ${idx + 1}`}
                  </Text>
                </View>
              </Pressable>
            ))}
          </View>
        </View>
      ) : null}
      <Modal transparent visible={!!lightbox} animationType="fade" onRequestClose={() => setLightbox(null)}>
        <Pressable style={styles.lightboxBackdrop} onPress={() => setLightbox(null)}>
          <View style={styles.lightboxCard}>
            {lightbox?.url ? (
              <Image source={{ uri: lightbox.url }} style={styles.lightboxImage} resizeMode="contain" />
            ) : null}
            {lightbox?.label ? <Text style={styles.lightboxLabel}>{lightbox.label}</Text> : null}
          </View>
        </Pressable>
      </Modal>
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
  gallery: { marginTop: 16 },
  galleryTitle: { fontSize: 14, fontWeight: '700', color: '#0f172a', marginBottom: 8 },
  galleryGrid: { flexDirection: 'row', flexWrap: 'wrap' },
  galleryItem: {
    width: 150,
    height: 98,
    borderRadius: 10,
    marginRight: 8,
    marginBottom: 8,
    overflow: 'hidden',
    backgroundColor: '#0f172a',
  },
  galleryImage: { width: '100%', height: '100%' },
  galleryOverlay: {
    position: 'absolute',
    left: 0,
    right: 0,
    bottom: 0,
    paddingHorizontal: 6,
    paddingVertical: 4,
    backgroundColor: 'rgba(15, 23, 42, 0.72)',
  },
  galleryOverlayText: { color: '#f8fafc', fontSize: 10, fontWeight: '600' },
  lightboxBackdrop: {
    flex: 1,
    backgroundColor: 'rgba(15, 23, 42, 0.8)',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 16,
  },
  lightboxCard: {
    width: '100%',
    maxWidth: 720,
    borderRadius: 14,
    overflow: 'hidden',
    backgroundColor: '#0f172a',
  },
  lightboxImage: {
    width: '100%',
    height: 420,
    backgroundColor: '#0f172a',
  },
  lightboxLabel: {
    color: '#f8fafc',
    paddingHorizontal: 12,
    paddingVertical: 10,
    fontSize: 12,
    backgroundColor: 'rgba(15, 23, 42, 0.9)',
  },
});
