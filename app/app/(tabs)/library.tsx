import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, FlatList, RefreshControl } from 'react-native';

const API_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8081';

type Video = { id: number; title: string | null; file_path: string; created_at?: string };

export default function LibraryScreen() {
  const [items, setItems] = useState<Video[]>([]);
  const [loading, setLoading] = useState(false);

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
        renderItem={({ item }) => (
          <View style={styles.row}>
            <View style={{ flex: 1 }}>
              <Text style={styles.title}>{item.title || `Video #${item.id}`}</Text>
              <Text style={styles.sub}>{item.file_path}</Text>
            </View>
            <Text style={styles.time}>{item.created_at?.slice(0, 19).replace('T', ' ')}</Text>
          </View>
        )}
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
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderBottomColor: '#e2e8f0',
  },
  title: { fontSize: 16, fontWeight: '600', color: '#0f172a' },
  sub: { color: '#64748b', fontSize: 12 },
  time: { color: '#334155', marginLeft: 12, fontSize: 12 },
  empty: { textAlign: 'center', marginTop: 30, color: '#64748b' },
});

