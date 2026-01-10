import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { FlatList, Platform, Pressable, RefreshControl, StyleSheet, Text, View } from 'react-native';
import { useRouter } from 'expo-router';

import { useI18n } from '@/components/I18nProvider';
import { subscribeStudioRefresh } from '@/lib/studioRefresh';

const API_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8787';
const PAGE_SIZE = 12;

type Video = {
  id: number;
  title: string | null;
  file_path: string;
  media_url?: string | null;
  preview_media_url?: string | null;
  created_at?: string;
};

export default function LibraryScreen() {
  const [items, setItems] = useState<Video[]>([]);
  const [visibleCount, setVisibleCount] = useState(PAGE_SIZE);
  const [loading, setLoading] = useState(false);
  const [containerHeight, setContainerHeight] = useState(0);
  const [contentHeight, setContentHeight] = useState(0);
  const router = useRouter();
  const { t } = useI18n();

  const load = useCallback(async (silent?: boolean) => {
    if (!silent) setLoading(true);
    try {
      const r = await fetch(`${API_URL}/api/videos`);
      const j = await r.json();
      const nextItems = j.videos || [];
      setItems(nextItems);
      setVisibleCount(Math.min(PAGE_SIZE, nextItems.length));
    } catch (e) {
      // noop
    } finally {
      if (!silent) setLoading(false);
    }
  }, []);

  const visibleItems = useMemo(() => items.slice(0, visibleCount), [items, visibleCount]);
  const hasMore = visibleCount < items.length;

  const loadMore = useCallback(() => {
    if (!hasMore) return;
    setVisibleCount((prev) => Math.min(prev + PAGE_SIZE, items.length));
  }, [hasMore, items.length]);

  useEffect(() => {
    load();
  }, [load]);

  useEffect(() => {
    const unsubscribe = subscribeStudioRefresh(() => {
      load(true);
    });
    return unsubscribe;
  }, [load]);

  useEffect(() => {
    if (!hasMore) return;
    if (!containerHeight || !contentHeight) return;
    if (contentHeight <= containerHeight) {
      loadMore();
    }
  }, [contentHeight, containerHeight, hasMore, loadMore]);

  return (
    <View style={styles.container}>
      <FlatList
        data={visibleItems}
        keyExtractor={(x) => String(x.id)}
        refreshControl={<RefreshControl refreshing={loading} onRefresh={() => load()} />}
        onEndReached={() => {
          if (hasMore) loadMore();
        }}
        onEndReachedThreshold={0.4}
        onLayout={(event) => setContainerHeight(event.nativeEvent.layout.height)}
        onContentSizeChange={(_width, height) => setContentHeight(height)}
        renderItem={({ item }) => {
          const mediaPath = item.preview_media_url || item.media_url;
          const mediaSrc = mediaPath ? `${API_URL}${mediaPath}` : null;
          const title = item.title || t('library_video_fallback', { id: item.id });
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
                  <Text style={styles.previewLabel}>{t('library_preview')}</Text>
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
        ListEmptyComponent={<Text style={styles.empty}>{t('library_empty')}</Text>}
        ListFooterComponent={
          hasMore ? (
            <Pressable style={styles.moreButton} onPress={loadMore}>
              <Text style={styles.moreButtonText}>{t('list_more')}</Text>
            </Pressable>
          ) : (
            <View style={styles.footerSpacer} />
          )
        }
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
  moreButton: {
    marginTop: 8,
    marginBottom: 20,
    alignSelf: 'center',
    paddingHorizontal: 18,
    paddingVertical: 8,
    borderRadius: 999,
    borderWidth: 1,
    borderColor: '#cbd5f5',
    backgroundColor: '#f8fafc',
  },
  moreButtonText: { fontSize: 12, fontWeight: '700', color: '#0f172a' },
  footerSpacer: { height: 12 },
});
