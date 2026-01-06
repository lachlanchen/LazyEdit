import React, { useEffect, useMemo, useState } from 'react';
import { FlatList, Platform, Pressable, RefreshControl, StyleSheet, Text, View } from 'react-native';
import { useRouter } from 'expo-router';

const API_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8787';

type Video = {
  id: number;
  title: string | null;
  file_path: string;
  media_url?: string | null;
  created_at?: string;
};

export default function LibraryScreen() {
  const [items, setItems] = useState<Video[]>([]);
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const load = async () => {
    setLoading(true);
    try {
      const r = await fetch(`${API_URL}/api/videos`);
      const j = await r.json();
      setItems(j.videos || []);
    } catch (e) {
      // noop
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  return (
    <View style={styles.container}>
      <FlatList
        data={items}
        keyExtractor={(x) => String(x.id)}
        refreshControl={<RefreshControl refreshing={loading} onRefresh={load} />}
        renderItem={({ item }) => {
          const mediaSrc = item.media_url ? `${API_URL}${item.media_url}` : null;
          const title = item.title || `Video #${item.id}`;
          return (
            <Pressable
              style={styles.row}
              onPress={() => router.push({ pathname: '/video/[id]', params: { id: String(item.id) } })}
            >
              <View style={styles.preview}>
                {Platform.OS === 'web' && mediaSrc ? (
                  React.createElement('video', {
                    src: mediaSrc,
                    style: { width: '100%', height: '100%', borderRadius: 10, objectFit: 'cover' },
                    muted: true,
                    playsInline: true,
                    preload: 'metadata',
                  })
                ) : (
                  <Text style={styles.previewLabel}>Preview</Text>
                )}
              </View>
              <View style={styles.meta}>
                <Text style={styles.title} numberOfLines={1}>{title}</Text>
                <Text style={styles.sub} numberOfLines={1}>{item.file_path}</Text>
                <Text style={styles.time}>{item.created_at?.slice(0, 19).replace('T', ' ')}</Text>
              </View>
            </Pressable>
          );
        }}
        ListEmptyComponent={<Text style={styles.empty}>No videos yet. Upload one from Home.</Text>}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16, backgroundColor: '#fbfdff' },
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
    paddingHorizontal: 10,
    borderRadius: 14,
    borderWidth: 1,
    borderColor: '#e2e8f0',
    marginBottom: 12,
    backgroundColor: 'white',
  },
  preview: {
    width: 110,
    height: 70,
    borderRadius: 10,
    backgroundColor: '#0f172a',
    marginRight: 12,
    justifyContent: 'center',
    alignItems: 'center',
    overflow: 'hidden',
  },
  previewLabel: { color: '#cbd5f5', fontSize: 11, fontWeight: '600' },
  meta: { flex: 1 },
  title: { fontSize: 16, fontWeight: '600', color: '#0f172a' },
  sub: { color: '#64748b', fontSize: 12 },
  time: { color: '#334155', fontSize: 12, marginTop: 4 },
  empty: { textAlign: 'center', marginTop: 30, color: '#64748b' },
});
