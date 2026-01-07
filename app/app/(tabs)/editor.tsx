import React, { useEffect, useMemo, useState } from 'react';
import FontAwesome from '@expo/vector-icons/FontAwesome';
import {
  ActivityIndicator,
  Image,
  Platform,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from 'react-native';

import { useI18n } from '@/components/I18nProvider';

const API_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8787';

type Video = {
  id: number;
  title: string | null;
  file_path: string;
  media_url?: string | null;
  created_at?: string;
};

const PLATFORMS = [
  { key: 'douyin', label: 'Douyin' },
  { key: 'xiaohongshu', label: 'Xiaohongshu' },
  { key: 'shipinhao', label: 'Shipinhao' },
  { key: 'bilibili', label: 'Bilibili' },
  { key: 'youtube', label: 'YouTube' },
];

export default function EditorScreen() {
  const [selected, setSelected] = useState<Record<string, boolean>>({
    douyin: false,
    xiaohongshu: true,
    shipinhao: true,
    bilibili: false,
    youtube: true,
  });
  const [videos, setVideos] = useState<Video[]>([]);
  const [loadingVideos, setLoadingVideos] = useState(false);
  const [selectedVideoId, setSelectedVideoId] = useState<number | null>(null);
  const [coverUrl, setCoverUrl] = useState<string | null>(null);
  const [coverStatus, setCoverStatus] = useState('');
  const [coverTone, setCoverTone] = useState<'neutral' | 'good' | 'bad'>('neutral');
  const [coverLoading, setCoverLoading] = useState(false);
  const [publishing, setPublishing] = useState(false);
  const [publishStatus, setPublishStatus] = useState('');
  const [publishTone, setPublishTone] = useState<'neutral' | 'good' | 'bad'>('neutral');
  const [publishZipUrl, setPublishZipUrl] = useState<string | null>(null);
  const { t } = useI18n();

  const selectedList = useMemo(
    () => PLATFORMS.filter((platform) => selected[platform.key]).map((platform) => platform.label),
    [selected],
  );

  const selectedVideo = useMemo(
    () => videos.find((video) => video.id === selectedVideoId) || null,
    [videos, selectedVideoId],
  );

  const toneStyle = (tone: 'neutral' | 'good' | 'bad') =>
    tone === 'good' ? styles.statusGood : tone === 'bad' ? styles.statusBad : styles.statusNeutral;

  const loadVideos = async () => {
    setLoadingVideos(true);
    try {
      const resp = await fetch(`${API_URL}/api/videos`);
      const json = await resp.json();
      const items = json.videos || [];
      setVideos(items);
      if (!selectedVideoId && items.length) {
        setSelectedVideoId(items[0].id);
      }
    } catch (_err) {
      // ignore fetch errors
    } finally {
      setLoadingVideos(false);
    }
  };

  const loadCoverPreview = async (videoId: number) => {
    try {
      const resp = await fetch(`${API_URL}/api/videos/${videoId}/cover`);
      if (!resp.ok) return;
      const json = await resp.json();
      if (json.cover_url) {
        setCoverUrl(`${API_URL}${json.cover_url}`);
      }
    } catch (_err) {
      // ignore
    }
  };

  useEffect(() => {
    loadVideos();
  }, []);

  useEffect(() => {
    if (!selectedVideoId) return;
    setCoverUrl(null);
    setCoverStatus('');
    setCoverTone('neutral');
    setPublishStatus('');
    setPublishTone('neutral');
    setPublishZipUrl(null);
    loadCoverPreview(selectedVideoId);
  }, [selectedVideoId]);

  const extractCover = async () => {
    if (!selectedVideoId || coverLoading) return;
    setCoverLoading(true);
    setCoverStatus(t('publish_cover_extracting'));
    setCoverTone('neutral');
    try {
      const resp = await fetch(`${API_URL}/api/videos/${selectedVideoId}/cover`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ lang: 'zh' }),
      });
      const json = await resp.json();
      if (!resp.ok) {
        setCoverStatus(`${t('publish_cover_failed')}: ${json.error || resp.statusText}`);
        setCoverTone('bad');
        return;
      }
      if (json.cover_url) {
        setCoverUrl(`${API_URL}${json.cover_url}`);
      }
      setCoverStatus(t('publish_cover_ready'));
      setCoverTone('good');
    } catch (err: any) {
      setCoverStatus(`${t('publish_cover_failed')}: ${err?.message || String(err)}`);
      setCoverTone('bad');
    } finally {
      setCoverLoading(false);
    }
  };

  const publishNow = async () => {
    if (!selectedVideoId || publishing) return;
    setPublishing(true);
    setPublishStatus(t('publish_status_sending'));
    setPublishTone('neutral');
    try {
      const resp = await fetch(`${API_URL}/api/videos/${selectedVideoId}/publish`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ platforms: selected }),
      });
      const json = await resp.json();
      if (!resp.ok) {
        setPublishStatus(`${t('publish_status_failed')}: ${json.error || resp.statusText}`);
        setPublishTone('bad');
        return;
      }
      if (json.zip_url) {
        setPublishZipUrl(`${API_URL}${json.zip_url}`);
      }
      if (json.status === 'published') {
        setPublishStatus(t('publish_status_published'));
        setPublishTone('good');
      } else if (json.status === 'queued') {
        setPublishStatus(t('publish_status_queued'));
        setPublishTone('good');
      } else {
        setPublishStatus(t('publish_status_ready'));
        setPublishTone('neutral');
      }
      if (json.warning) {
        setPublishStatus(`${t('publish_status_ready')}: ${json.warning}`);
        setPublishTone('neutral');
      }
    } catch (err: any) {
      setPublishStatus(`${t('publish_status_failed')}: ${err?.message || String(err)}`);
      setPublishTone('bad');
    } finally {
      setPublishing(false);
    }
  };

  return (
    <ScrollView contentContainerStyle={styles.scrollContent}>
      <View style={styles.container}>
        <Text style={styles.title}>{t('publish_title')}</Text>
        <Text style={styles.sub}>{t('publish_subtitle')}</Text>

        <View style={styles.card}>
          <Text style={styles.sectionTitle}>{t('publish_video_select_title')}</Text>
          <Text style={styles.sectionHint}>{t('publish_video_select_hint')}</Text>
          {loadingVideos ? (
            <ActivityIndicator style={{ marginTop: 12 }} />
          ) : videos.length ? (
            <View style={styles.videoList}>
              {videos.map((video) => {
                const mediaSrc = video.media_url ? `${API_URL}${video.media_url}` : null;
                const isActive = selectedVideoId === video.id;
                const title = video.title || t('library_video_fallback', { id: video.id });
                return (
                  <Pressable
                    key={video.id}
                    style={[styles.videoRow, isActive && styles.videoRowActive]}
                    onPress={() => setSelectedVideoId(video.id)}
                  >
                    <View style={styles.videoPreview}>
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
                    <View style={styles.videoMeta}>
                      <Text style={styles.videoTitle} numberOfLines={1}>
                        {title}
                      </Text>
                      <Text style={styles.videoPath} numberOfLines={1}>
                        {video.file_path}
                      </Text>
                      <Text style={styles.videoTime}>
                        {video.created_at?.slice(0, 19).replace('T', ' ')}
                      </Text>
                    </View>
                    <View style={[styles.selectBadge, isActive && styles.selectBadgeActive]}>
                      {isActive ? <FontAwesome name="check" size={12} color="white" /> : null}
                    </View>
                  </Pressable>
                );
              })}
            </View>
          ) : (
            <Text style={styles.empty}>{t('publish_video_empty')}</Text>
          )}
        </View>

        <View style={styles.card}>
          <Text style={styles.sectionTitle}>{t('publish_select_title')}</Text>
          <Text style={styles.sectionHint}>{t('publish_select_hint')}</Text>

          <View style={styles.platformGrid}>
            {PLATFORMS.map((platform) => {
              const isActive = selected[platform.key];
              return (
                <Pressable
                  key={platform.key}
                  style={[styles.platformChip, isActive && styles.platformChipActive]}
                  onPress={() =>
                    setSelected((prev) => ({ ...prev, [platform.key]: !prev[platform.key] }))
                  }
                >
                  <Text style={[styles.platformText, isActive && styles.platformTextActive]}>
                    {platform.label}
                  </Text>
                </Pressable>
              );
            })}
          </View>

          <Text style={styles.selectedText}>
            {t('label_selected', {
              value: selectedList.length ? selectedList.join(', ') : t('label_none'),
            })}
          </Text>
        </View>

        <View style={styles.card}>
          <Text style={styles.sectionTitle}>{t('publish_cover_title')}</Text>
          <Text style={styles.sectionHint}>{t('publish_cover_hint')}</Text>
          <Pressable
            style={[styles.coverButton, (!selectedVideo || coverLoading) && styles.btnDisabled]}
            onPress={extractCover}
            disabled={!selectedVideo || coverLoading}
          >
            <View style={styles.btnContent}>
              {coverLoading && <ActivityIndicator color="white" style={{ marginRight: 8 }} />}
              <Text style={styles.coverButtonText}>{t('publish_cover_button')}</Text>
            </View>
          </Pressable>
          {coverUrl ? (
            <Image source={{ uri: coverUrl }} style={styles.coverPreview} resizeMode="contain" />
          ) : (
            <Text style={styles.empty}>{t('publish_cover_empty')}</Text>
          )}
          {coverStatus ? <Text style={[styles.status, toneStyle(coverTone)]}>{coverStatus}</Text> : null}
        </View>

        <View style={styles.card}>
          <Text style={styles.sectionTitle}>{t('publish_manual_title')}</Text>
          <Text style={styles.sectionHint}>{t('publish_manual_hint')}</Text>
          <Pressable
            style={[styles.publishButton, publishing && styles.btnDisabled]}
            onPress={publishNow}
            disabled={publishing}
          >
            <View style={styles.btnContent}>
              {publishing && <ActivityIndicator color="white" style={{ marginRight: 8 }} />}
              <Text style={styles.publishButtonText}>{t('publish_button')}</Text>
            </View>
          </Pressable>
          {publishStatus ? (
            <Text style={[styles.status, toneStyle(publishTone)]}>{publishStatus}</Text>
          ) : null}
          {publishZipUrl ? (
            <Text style={styles.zipText}>
              {t('publish_zip_ready', { value: publishZipUrl })}
            </Text>
          ) : null}
        </View>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  scrollContent: {
    padding: 16,
    paddingBottom: 32,
  },
  container: {
    flex: 1,
    width: '100%',
    maxWidth: 720,
    alignSelf: 'center',
  },
  title: { fontSize: 22, fontWeight: '700', color: '#0f172a' },
  sub: { marginTop: 8, color: '#334155' },
  card: {
    marginTop: 16,
    padding: 16,
    borderRadius: 16,
    backgroundColor: 'white',
    borderWidth: 1,
    borderColor: '#e2e8f0',
  },
  sectionTitle: { fontSize: 16, fontWeight: '700', color: '#0f172a' },
  sectionHint: { marginTop: 6, fontSize: 12, color: '#64748b' },
  videoList: { marginTop: 12, gap: 12 },
  videoRow: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 10,
    borderRadius: 14,
    borderWidth: 1,
    borderColor: '#e2e8f0',
    backgroundColor: '#f8fafc',
  },
  videoRowActive: {
    borderColor: '#2563eb',
    backgroundColor: '#eff6ff',
  },
  videoPreview: {
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
  videoMeta: { flex: 1 },
  videoTitle: { fontSize: 15, fontWeight: '600', color: '#0f172a' },
  videoPath: { color: '#64748b', fontSize: 11 },
  videoTime: { color: '#334155', fontSize: 11, marginTop: 4 },
  selectBadge: {
    width: 22,
    height: 22,
    borderRadius: 11,
    borderWidth: 1,
    borderColor: '#cbd5f5',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: 'white',
  },
  selectBadgeActive: {
    backgroundColor: '#2563eb',
    borderColor: '#2563eb',
  },
  platformGrid: {
    marginTop: 12,
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 10,
  },
  platformChip: {
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderRadius: 999,
    borderWidth: 1,
    borderColor: '#cbd5f5',
    backgroundColor: '#f8fafc',
  },
  platformChipActive: {
    borderColor: '#0f172a',
    backgroundColor: '#0f172a',
  },
  platformText: { fontSize: 12, fontWeight: '600', color: '#1e293b' },
  platformTextActive: { color: '#f8fafc' },
  selectedText: { marginTop: 12, fontSize: 12, color: '#0f172a' },
  coverButton: {
    marginTop: 12,
    backgroundColor: '#0f172a',
    paddingVertical: 12,
    borderRadius: 12,
    alignItems: 'center',
  },
  coverButtonText: { color: 'white', fontWeight: '700' },
  coverPreview: {
    marginTop: 12,
    width: '100%',
    height: 180,
    borderRadius: 14,
    backgroundColor: '#0f172a',
    overflow: 'hidden',
  },
  empty: { marginTop: 12, color: '#64748b', fontSize: 12 },
  publishButton: {
    marginTop: 12,
    backgroundColor: '#2563eb',
    paddingVertical: 12,
    borderRadius: 12,
    alignItems: 'center',
  },
  publishButtonText: { color: 'white', fontWeight: '700' },
  btnDisabled: { opacity: 0.6 },
  btnContent: { flexDirection: 'row', alignItems: 'center' },
  status: { marginTop: 10, fontSize: 12 },
  statusNeutral: { color: '#0f172a' },
  statusGood: { color: '#15803d' },
  statusBad: { color: '#b91c1c' },
  zipText: { marginTop: 8, fontSize: 12, color: '#475569' },
});
