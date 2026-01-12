import React, { useCallback, useEffect, useMemo, useState } from 'react';
import FontAwesome from '@expo/vector-icons/FontAwesome';
import { FlatList, Modal, Platform, Pressable, RefreshControl, StyleSheet, Text, View } from 'react-native';
import { useRouter } from 'expo-router';

import { useI18n } from '@/components/I18nProvider';
import { subscribeStudioRefresh, triggerStudioRefresh } from '@/lib/studioRefresh';

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
  const [menuVideo, setMenuVideo] = useState<Video | null>(null);
  const [confirmVideo, setConfirmVideo] = useState<Video | null>(null);
  const [deletePending, setDeletePending] = useState(false);
  const [deleteError, setDeleteError] = useState<string | null>(null);
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

  const confirmDelete = useCallback(async () => {
    if (!confirmVideo) return;
    setDeletePending(true);
    setDeleteError(null);
    try {
      const res = await fetch(`${API_URL}/api/videos/${confirmVideo.id}`, { method: 'DELETE' });
      if (!res.ok) {
        const payload = await res.json().catch(() => ({}));
        throw new Error(payload.error || 'Delete failed');
      }
      setConfirmVideo(null);
      await load(true);
      triggerStudioRefresh();
    } catch (err) {
      setDeleteError(err instanceof Error ? err.message : 'Delete failed');
    } finally {
      setDeletePending(false);
    }
  }, [confirmVideo, load]);

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
              <Pressable
                style={styles.menuButton}
                onPress={(event) => {
                  event.stopPropagation?.();
                  setMenuVideo(item);
                }}
              >
                <FontAwesome name="ellipsis-h" size={16} color="#0f172a" />
              </Pressable>
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
      <Modal transparent animationType="fade" visible={!!menuVideo} onRequestClose={() => setMenuVideo(null)}>
        <Pressable style={styles.menuBackdrop} onPress={() => setMenuVideo(null)}>
          <Pressable style={styles.menuCard} onPress={() => {}}>
            <Pressable
              style={styles.menuAction}
              onPress={() => {
                setConfirmVideo(menuVideo);
                setDeleteError(null);
                setMenuVideo(null);
              }}
            >
              <Text style={styles.menuDeleteText}>{t('library_menu_delete')}</Text>
            </Pressable>
            <Pressable style={styles.menuAction} onPress={() => setMenuVideo(null)}>
              <Text style={styles.menuActionText}>{t('library_menu_cancel')}</Text>
            </Pressable>
          </Pressable>
        </Pressable>
      </Modal>
      <Modal transparent animationType="fade" visible={!!confirmVideo} onRequestClose={() => setConfirmVideo(null)}>
        <Pressable style={styles.menuBackdrop} onPress={() => setConfirmVideo(null)}>
          <Pressable style={styles.confirmCard} onPress={() => {}}>
            <Text style={styles.confirmTitle}>{t('library_delete_title')}</Text>
            <Text style={styles.confirmBody}>{t('library_delete_body')}</Text>
            {deleteError ? <Text style={styles.confirmError}>{deleteError}</Text> : null}
            <View style={styles.confirmActions}>
              <Pressable
                style={styles.confirmButton}
                onPress={() => {
                  if (!deletePending) setConfirmVideo(null);
                  if (!deletePending) setDeleteError(null);
                }}
              >
                <Text style={styles.confirmCancelText}>{t('library_menu_cancel')}</Text>
              </Pressable>
              <Pressable
                style={[styles.confirmButton, styles.confirmDeleteButton]}
                onPress={confirmDelete}
                disabled={deletePending}
              >
                <Text style={styles.confirmDeleteText}>
                  {deletePending ? t('library_delete_pending') : t('library_delete_confirm')}
                </Text>
              </Pressable>
            </View>
          </Pressable>
        </Pressable>
      </Modal>
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
  menuButton: {
    paddingHorizontal: 8,
    paddingVertical: 6,
    marginLeft: 6,
    borderRadius: 10,
  },
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
  menuBackdrop: {
    flex: 1,
    backgroundColor: 'rgba(15, 23, 42, 0.35)',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 24,
  },
  menuCard: {
    width: '100%',
    maxWidth: 320,
    borderRadius: 16,
    backgroundColor: 'white',
    paddingVertical: 8,
    borderWidth: 1,
    borderColor: '#e2e8f0',
  },
  menuAction: {
    paddingHorizontal: 16,
    paddingVertical: 12,
  },
  menuActionText: { fontSize: 14, fontWeight: '600', color: '#0f172a' },
  menuDeleteText: { fontSize: 14, fontWeight: '700', color: '#dc2626' },
  confirmCard: {
    width: '100%',
    maxWidth: 360,
    borderRadius: 16,
    backgroundColor: 'white',
    padding: 18,
    borderWidth: 1,
    borderColor: '#e2e8f0',
  },
  confirmTitle: { fontSize: 16, fontWeight: '700', color: '#0f172a', marginBottom: 8 },
  confirmBody: { fontSize: 13, color: '#475569', marginBottom: 12 },
  confirmError: { fontSize: 12, color: '#dc2626', marginBottom: 10 },
  confirmActions: { flexDirection: 'row', justifyContent: 'flex-end', gap: 10 },
  confirmButton: {
    paddingHorizontal: 14,
    paddingVertical: 8,
    borderRadius: 999,
    borderWidth: 1,
    borderColor: '#cbd5f5',
  },
  confirmDeleteButton: {
    borderColor: '#dc2626',
    backgroundColor: '#fee2e2',
  },
  confirmCancelText: { fontSize: 12, fontWeight: '700', color: '#0f172a' },
  confirmDeleteText: { fontSize: 12, fontWeight: '700', color: '#b91c1c' },
});
