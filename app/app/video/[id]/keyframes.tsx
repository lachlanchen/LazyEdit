import React, { useEffect, useMemo, useState } from 'react';
import { ActivityIndicator, Image, Modal, Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';
import { Stack, useLocalSearchParams } from 'expo-router';

const API_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8787';

type KeyframesDetail = {
  id: number;
  status: string;
  frame_urls?: string[];
  frame_count?: number;
  error?: string | null;
  created_at?: string | null;
};

const formatTimestamp = (value?: string | null) =>
  value ? value.slice(0, 19).replace('T', ' ') : 'Unknown time';

export default function KeyframesScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const [keyframes, setKeyframes] = useState<KeyframesDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');
  const [lightbox, setLightbox] = useState<{ url: string; label?: string } | null>(null);

  const headerTitle = useMemo(() => 'Key Frames', []);

  useEffect(() => {
    if (!id) return;
    (async () => {
      setLoading(true);
      try {
        const resp = await fetch(`${API_URL}/api/videos/${id}/keyframes`);
        const json = await resp.json();
        if (!resp.ok) {
          setError(json.error || 'Failed to load keyframes');
          setKeyframes(null);
          return;
        }
        setKeyframes(json);
      } catch (e: any) {
        setError(e?.message || 'Failed to load keyframes');
        setKeyframes(null);
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
        <Text style={styles.loadingText}>Loading key frames...</Text>
      </View>
    );
  }

  if (!keyframes) {
    return (
      <View style={styles.container}>
        <Stack.Screen options={{ title: headerTitle, headerBackTitle: 'Video' }} />
        <Text style={styles.title}>Key frames not available</Text>
        {error ? <Text style={styles.error}>{error}</Text> : null}
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <Stack.Screen options={{ title: headerTitle, headerBackTitle: 'Video' }} />
      <Text style={styles.title}>Key Frames</Text>
      <Text style={styles.meta}>Status: {keyframes.status}</Text>
      <Text style={styles.meta}>Created: {formatTimestamp(keyframes.created_at)}</Text>
      <Text style={styles.meta}>Frames: {keyframes.frame_count ?? keyframes.frame_urls?.length ?? 0}</Text>
      {keyframes.error ? <Text style={styles.error}>{keyframes.error}</Text> : null}
      <ScrollView style={styles.gallery} contentContainerStyle={{ paddingBottom: 24 }}>
        <View style={styles.grid}>
          {(keyframes.frame_urls || []).map((url, idx) => (
            <Pressable
              key={url}
              style={styles.frameItem}
              onPress={() => setLightbox({ url: `${API_URL}${url}`, label: `Key frame ${idx + 1}` })}
            >
              <Image source={{ uri: `${API_URL}${url}` }} style={styles.frame} />
              <View style={styles.frameOverlay}>
                <Text style={styles.frameOverlayText}>{`Key frame ${idx + 1}`}</Text>
              </View>
            </Pressable>
          ))}
        </View>
      </ScrollView>
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
  gallery: {
    marginTop: 12,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#e2e8f0',
    backgroundColor: 'white',
    padding: 12,
  },
  grid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  frameItem: {
    width: 150,
    height: 100,
    borderRadius: 12,
    marginRight: 10,
    marginBottom: 10,
    overflow: 'hidden',
    backgroundColor: '#0f172a',
  },
  frame: {
    width: '100%',
    height: '100%',
  },
  frameOverlay: {
    position: 'absolute',
    left: 6,
    bottom: 6,
    backgroundColor: 'rgba(15, 23, 42, 0.72)',
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 6,
  },
  frameOverlayText: { color: '#f8fafc', fontSize: 10, fontWeight: '600' },
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
  loadingText: { marginTop: 8, color: '#475569' },
});
