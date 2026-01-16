import React, { useCallback, useEffect, useMemo, useState } from 'react';
import FontAwesome from '@expo/vector-icons/FontAwesome';
import {
  ActivityIndicator,
  FlatList,
  Image,
  Platform,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from 'react-native';

import { useI18n } from '@/components/I18nProvider';
import { subscribeStudioRefresh } from '@/lib/studioRefresh';

const API_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8787';
const PAGE_SIZE = 8;

type Video = {
  id: number;
  title: string | null;
  file_path: string;
  media_url?: string | null;
  preview_media_url?: string | null;
  created_at?: string;
};

type PublishJob = {
  id?: string;
  filename?: string;
  status?: string;
  created_at?: string;
  updated_at?: string;
  platforms?: string[];
  error?: string;
};

type ProcessStep = {
  status?: string;
  detail?: string;
  updated_at?: string;
  progress?: number;
};

const PLATFORMS = [
  { key: 'douyin', label: 'Douyin' },
  { key: 'xiaohongshu', label: 'Xiaohongshu' },
  { key: 'shipinhao', label: 'Shipinhao' },
  { key: 'bilibili', label: 'Bilibili' },
  { key: 'youtube', label: 'YouTube' },
  { key: 'instagram', label: 'Instagram' },
];
const withCacheBust = (url: string) => `${url}${url.includes('?') ? '&' : '?'}t=${Date.now()}`;

export default function EditorScreen() {
  const defaultPublishSelection = useMemo(
    () => ({
      douyin: false,
      xiaohongshu: true,
      shipinhao: true,
      bilibili: false,
      youtube: true,
      instagram: true,
    }),
    [],
  );
  const [selected, setSelected] = useState<Record<string, boolean>>(defaultPublishSelection);
  const [videos, setVideos] = useState<Video[]>([]);
  const [visibleCount, setVisibleCount] = useState(PAGE_SIZE);
  const [listHeight, setListHeight] = useState(0);
  const [listContentHeight, setListContentHeight] = useState(0);
  const [loadingVideos, setLoadingVideos] = useState(false);
  const [selectedVideoId, setSelectedVideoId] = useState<number | null>(null);
  const [coverUrl, setCoverUrl] = useState<string | null>(null);
  const [coverStatus, setCoverStatus] = useState('');
  const [coverTone, setCoverTone] = useState<'neutral' | 'good' | 'bad'>('neutral');
  const [coverLoading, setCoverLoading] = useState(false);
  const [processRunning, setProcessRunning] = useState(false);
  const [processStatus, setProcessStatus] = useState('');
  const [processTone, setProcessTone] = useState<'neutral' | 'good' | 'bad'>('neutral');
  const [processSteps, setProcessSteps] = useState<Record<string, ProcessStep> | null>(null);
  const [processUpdatedAt, setProcessUpdatedAt] = useState<string | null>(null);
  const [processReadyForCover, setProcessReadyForCover] = useState(false);
  const [processReadyForPublish, setProcessReadyForPublish] = useState(false);
  const [processStatusLoading, setProcessStatusLoading] = useState(false);
  const [processStatusError, setProcessStatusError] = useState('');
  const [publishing, setPublishing] = useState(false);
  const [publishStatus, setPublishStatus] = useState('');
  const [publishTone, setPublishTone] = useState<'neutral' | 'good' | 'bad'>('neutral');
  const [publishZipUrl, setPublishZipUrl] = useState<string | null>(null);
  const [publishQueue, setPublishQueue] = useState<PublishJob[]>([]);
  const [queueLoading, setQueueLoading] = useState(false);
  const [queueError, setQueueError] = useState('');
  const [publishSettingsLoaded, setPublishSettingsLoaded] = useState(false);
  const { t } = useI18n();

  const processStepDefinitions = useMemo(
    () => [
      { key: 'transcribe', label: t('publish_step_transcribe') },
      { key: 'polish', label: t('publish_step_polish') },
      { key: 'translate', label: t('publish_step_translate') },
      { key: 'burn', label: t('publish_step_burn') },
      { key: 'keyframes', label: t('publish_step_keyframes') },
      { key: 'caption', label: t('publish_step_caption') },
      { key: 'metadata_zh', label: t('publish_step_metadata_zh') },
      { key: 'metadata_en', label: t('publish_step_metadata_en') },
    ],
    [t],
  );

  const processStatusLabel = useCallback(
    (status?: string) => {
      const key = String(status || '').toLowerCase();
      if (key === 'done') return t('publish_step_status_done');
      if (key === 'working') return t('publish_step_status_working');
      if (key === 'error') return t('publish_step_status_error');
      if (key === 'skipped') return t('publish_step_status_skipped');
      if (key === 'idle') return t('publish_step_status_idle');
      return status || t('publish_step_status_idle');
    },
    [t],
  );

  const selectedList = useMemo(
    () => PLATFORMS.filter((platform) => selected[platform.key]).map((platform) => platform.label),
    [selected],
  );

  const selectedVideo = useMemo(
    () => videos.find((video) => video.id === selectedVideoId) || null,
    [videos, selectedVideoId],
  );
  const previewVideoUrl = useMemo(() => {
    if (!selectedVideo) return null;
    const raw = selectedVideo.preview_media_url || selectedVideo.media_url;
    if (!raw) return null;
    return raw.startsWith('http') ? raw : `${API_URL}${raw}`;
  }, [selectedVideo]);
  const visibleVideos = useMemo(() => videos.slice(0, visibleCount), [videos, visibleCount]);
  const hasMoreVideos = visibleCount < videos.length;

  const loadMoreVideos = useCallback(() => {
    if (!hasMoreVideos) return;
    setVisibleCount((prev) => Math.min(prev + PAGE_SIZE, videos.length));
  }, [hasMoreVideos, videos.length]);

  const toneStyle = (tone: 'neutral' | 'good' | 'bad') =>
    tone === 'good' ? styles.statusGood : tone === 'bad' ? styles.statusBad : styles.statusNeutral;

  const processToneStyle = (status?: string) => {
    const key = String(status || '').toLowerCase();
    if (key === 'done') return styles.statusGood;
    if (key === 'error') return styles.statusBad;
    if (key === 'working') return styles.statusWarning;
    return styles.statusNeutral;
  };

  const formatTimestamp = (value?: string | null) => {
    if (!value) return '';
    try {
      return new Date(value).toLocaleString();
    } catch (_err) {
      return value;
    }
  };

  const queueStatusLabel = (status?: string) => {
    const key = String(status || '').toLowerCase();
    if (key === 'queued') return t('publish_queue_status_queued');
    if (key === 'running') return t('publish_queue_status_running');
    if (key === 'done' || key === 'completed') return t('publish_queue_status_done');
    if (key === 'failed' || key === 'error') return t('publish_queue_status_failed');
    return status || t('publish_queue_status_queued');
  };

  const normalizePublishSelection = useCallback(
    (value: unknown) => {
      const next = { ...defaultPublishSelection };
      if (value && typeof value === 'object' && !Array.isArray(value)) {
        Object.keys(next).forEach((key) => {
          if (key in (value as Record<string, unknown>)) {
            next[key] = Boolean((value as Record<string, unknown>)[key]);
          }
        });
      }
      return next;
    },
    [defaultPublishSelection],
  );

  const loadVideos = useCallback(async (silent?: boolean) => {
    if (!silent) setLoadingVideos(true);
    try {
      const resp = await fetch(`${API_URL}/api/videos`);
      const json = await resp.json();
      const items = json.videos || [];
      setVideos(items);
      setVisibleCount(Math.min(PAGE_SIZE, items.length));
      if (!selectedVideoId && items.length) {
        setSelectedVideoId(items[0].id);
      }
    } catch (_err) {
      // ignore fetch errors
    } finally {
      if (!silent) setLoadingVideos(false);
    }
  }, [selectedVideoId]);

  const loadPublishSettings = useCallback(async () => {
    try {
      const resp = await fetch(`${API_URL}/api/ui-settings/publish_platforms`);
      const json = await resp.json();
      if (resp.ok) {
        setSelected(normalizePublishSelection(json?.value));
      }
    } catch (_err) {
      // ignore
    } finally {
      setPublishSettingsLoaded(true);
    }
  }, [normalizePublishSelection]);

  const loadPublishQueue = useCallback(async (silent?: boolean) => {
    if (!silent) setQueueLoading(true);
    try {
      const resp = await fetch(`${API_URL}/api/autopublish/queue`);
      const json = await resp.json();
      if (!resp.ok) {
        setQueueError(`${t('publish_queue_failed')}: ${json?.error || resp.statusText}`);
        return;
      }
      if (json?.status === 'unavailable') {
        setPublishQueue([]);
        setQueueError(t('publish_queue_unavailable'));
        return;
      }
      const jobs = Array.isArray(json?.jobs) ? json.jobs : [];
      setPublishQueue(jobs);
      setQueueError('');
    } catch (_err) {
      setQueueError(t('publish_queue_failed'));
    } finally {
      if (!silent) setQueueLoading(false);
    }
  }, [t]);

  const loadCoverPreview = async (videoId: number) => {
    try {
      const resp = await fetch(`${API_URL}/api/videos/${videoId}/cover`);
      if (!resp.ok) return;
      const json = await resp.json();
      if (json.cover_url) {
        setCoverUrl(withCacheBust(`${API_URL}${json.cover_url}`));
      }
    } catch (_err) {
      // ignore
    }
  };

  const loadProcessStatus = useCallback(
    async (videoId: number, silent?: boolean) => {
      if (!silent) setProcessStatusLoading(true);
      try {
        const resp = await fetch(`${API_URL}/api/videos/${videoId}/process-status`);
        const json = await resp.json().catch(() => ({}));
        if (!resp.ok) {
          setProcessStatusError(json?.error || resp.statusText);
          setProcessSteps(null);
          setProcessUpdatedAt(null);
          setProcessReadyForCover(false);
          setProcessReadyForPublish(false);
          return;
        }
        setProcessSteps(json?.steps || null);
        setProcessUpdatedAt(json?.updated_at || null);
        setProcessReadyForCover(Boolean(json?.ready_for_cover));
        setProcessReadyForPublish(Boolean(json?.ready_for_publish));
        setProcessStatusError('');
      } catch (err: any) {
        setProcessStatusError(err?.message || String(err));
        setProcessSteps(null);
        setProcessUpdatedAt(null);
        setProcessReadyForCover(false);
        setProcessReadyForPublish(false);
      } finally {
        if (!silent) setProcessStatusLoading(false);
      }
    },
    [],
  );

  useEffect(() => {
    loadVideos();
  }, [loadVideos]);

  useEffect(() => {
    loadPublishSettings();
  }, [loadPublishSettings]);

  useEffect(() => {
    if (!publishSettingsLoaded) return;
    const persist = async () => {
      try {
        await fetch(`${API_URL}/api/ui-settings/publish_platforms`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(selected),
        });
      } catch (_err) {
        // ignore
      }
    };
    persist();
  }, [publishSettingsLoaded, selected]);

  useEffect(() => {
    loadPublishQueue();
    const interval = setInterval(() => {
      loadPublishQueue(true);
    }, 5000);
    return () => clearInterval(interval);
  }, [loadPublishQueue]);

  useEffect(() => {
    const unsubscribe = subscribeStudioRefresh(() => {
      loadVideos(true);
    });
    return unsubscribe;
  }, [loadVideos]);

  useEffect(() => {
    if (!hasMoreVideos) return;
    if (!listHeight || !listContentHeight) return;
    if (listContentHeight <= listHeight) {
      loadMoreVideos();
    }
  }, [hasMoreVideos, listHeight, listContentHeight, loadMoreVideos]);

  useEffect(() => {
    if (!selectedVideoId) return;
    setCoverUrl(null);
    setCoverStatus('');
    setCoverTone('neutral');
    setProcessStatus('');
    setProcessTone('neutral');
    setProcessRunning(false);
    setProcessSteps(null);
    setProcessUpdatedAt(null);
    setProcessReadyForCover(false);
    setProcessReadyForPublish(false);
    setProcessStatusError('');
    setPublishStatus('');
    setPublishTone('neutral');
    setPublishZipUrl(null);
    loadCoverPreview(selectedVideoId);
    loadProcessStatus(selectedVideoId, true);
  }, [selectedVideoId, loadProcessStatus]);

  useEffect(() => {
    if (!selectedVideoId) return;
    loadProcessStatus(selectedVideoId, true);
    const interval = setInterval(() => {
      loadProcessStatus(selectedVideoId, true);
    }, 5000);
    return () => clearInterval(interval);
  }, [selectedVideoId, loadProcessStatus]);

  const startProcess = async () => {
    if (!selectedVideoId || processRunning) return;
    setProcessRunning(true);
    setProcessStatus(t('publish_process_starting'));
    setProcessTone('neutral');
    try {
      const resp = await fetch(`${API_URL}/api/videos/${selectedVideoId}/process`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ async: true }),
      });
      const json = await resp.json().catch(() => ({}));
      if (!resp.ok) {
        setProcessStatus(`${t('publish_process_failed')}: ${json.error || resp.statusText}`);
        setProcessTone('bad');
        return;
      }
      setProcessStatus(t('publish_process_started'));
      setProcessTone('good');
      loadProcessStatus(selectedVideoId, true);
    } catch (err: any) {
      setProcessStatus(`${t('publish_process_failed')}: ${err?.message || String(err)}`);
      setProcessTone('bad');
    } finally {
      setProcessRunning(false);
    }
  };

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
        setCoverUrl(withCacheBust(`${API_URL}${json.cover_url}`));
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
    loadPublishQueue(true);
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
            <FlatList
              data={visibleVideos}
              keyExtractor={(video) => String(video.id)}
              style={styles.videoListScroll}
              contentContainerStyle={styles.videoList}
              onEndReached={() => {
                if (hasMoreVideos) loadMoreVideos();
              }}
              onEndReachedThreshold={0.4}
              onLayout={(event) => setListHeight(event.nativeEvent.layout.height)}
              onContentSizeChange={(_width, height) => setListContentHeight(height)}
              nestedScrollEnabled
              renderItem={({ item: video }) => {
                const previewUrl = video.preview_media_url || video.media_url;
                const mediaSrc = previewUrl ? `${API_URL}${previewUrl}` : null;
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
              }}
              ListFooterComponent={
                hasMoreVideos ? (
                  <Pressable style={styles.moreButton} onPress={loadMoreVideos}>
                    <Text style={styles.moreButtonText}>{t('list_more')}</Text>
                  </Pressable>
                ) : (
                  <View style={styles.footerSpacer} />
                )
              }
            />
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
          <Text style={styles.sectionTitle}>{t('publish_process_title')}</Text>
          <Text style={styles.sectionHint}>{t('publish_process_hint')}</Text>
          <Pressable
            style={[styles.processButton, (!selectedVideo || processRunning) && styles.btnDisabled]}
            onPress={startProcess}
            disabled={!selectedVideo || processRunning}
          >
            <View style={styles.btnContent}>
              {processRunning && <ActivityIndicator color="white" style={{ marginRight: 8 }} />}
              <Text style={styles.processButtonText}>{t('publish_process_button')}</Text>
            </View>
          </Pressable>
          {processStatus ? (
            <Text style={[styles.status, toneStyle(processTone)]}>{processStatus}</Text>
          ) : null}
          <View style={styles.processPreviewBlock}>
            <Text style={styles.processPreviewTitle}>{t('publish_process_preview_title')}</Text>
            {previewVideoUrl ? (
              <View style={styles.processPreviewVideoWrap}>
                {Platform.OS === 'web' ? (
                  React.createElement('video', {
                    src: previewVideoUrl,
                    style: { width: '100%', height: '100%', borderRadius: 12, objectFit: 'contain' },
                    controls: true,
                    muted: true,
                    playsInline: true,
                    preload: 'metadata',
                  })
                ) : (
                  <Image source={{ uri: previewVideoUrl }} style={styles.processPreviewImage} />
                )}
              </View>
            ) : (
              <Text style={styles.empty}>{t('publish_process_preview_empty')}</Text>
            )}
          </View>
          <View style={styles.processStatusBlock}>
            <View style={styles.processStatusHeader}>
              <Text style={styles.processStatusTitle}>{t('publish_process_status_title')}</Text>
              {processUpdatedAt ? (
                <Text style={styles.processStatusUpdated}>
                  {t('publish_process_status_updated', { value: formatTimestamp(processUpdatedAt) })}
                </Text>
              ) : null}
            </View>
            {processStatusLoading ? <ActivityIndicator style={{ marginTop: 8 }} /> : null}
            {processStatusError ? (
              <Text style={[styles.status, styles.statusBad]}>{processStatusError}</Text>
            ) : null}
            {processSteps ? (
              processStepDefinitions.map(({ key, label }) => {
                const step = processSteps[key];
                const status = step?.status || 'idle';
                const detail = step?.detail;
                return (
                  <View key={key} style={styles.processRow}>
                    <View style={styles.processRowHeader}>
                      <Text style={styles.processStepLabel}>{label}</Text>
                      <Text style={[styles.processStepStatus, processToneStyle(status)]}>
                        {processStatusLabel(status)}
                      </Text>
                    </View>
                    {detail ? <Text style={styles.processStepDetail}>{detail}</Text> : null}
                  </View>
                );
              })
            ) : (
              !processStatusLoading && !processStatusError ? (
                <Text style={styles.empty}>{t('publish_process_status_empty')}</Text>
              ) : null
            )}
          </View>
        </View>

        <View style={styles.card}>
          <Text style={styles.sectionTitle}>{t('publish_cover_title')}</Text>
          <Text style={styles.sectionHint}>{t('publish_cover_hint')}</Text>
          <Pressable
            style={[
              styles.coverButton,
              (!selectedVideo || coverLoading || !processReadyForCover) && styles.btnDisabled,
            ]}
            onPress={extractCover}
            disabled={!selectedVideo || coverLoading || !processReadyForCover}
          >
            <View style={styles.btnContent}>
              {coverLoading && <ActivityIndicator color="white" style={{ marginRight: 8 }} />}
              <Text style={styles.coverButtonText}>{t('publish_cover_button')}</Text>
            </View>
          </Pressable>
          {selectedVideo && !processReadyForCover ? (
            <Text style={styles.helperText}>{t('publish_cover_disabled_hint')}</Text>
          ) : null}
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
            style={[
              styles.publishButton,
              (!selectedVideo || publishing || !processReadyForPublish) && styles.btnDisabled,
            ]}
            onPress={publishNow}
            disabled={!selectedVideo || publishing || !processReadyForPublish}
          >
            <View style={styles.btnContent}>
              {publishing && <ActivityIndicator color="white" style={{ marginRight: 8 }} />}
              <Text style={styles.publishButtonText}>{t('publish_button')}</Text>
            </View>
          </Pressable>
          {selectedVideo && !processReadyForPublish ? (
            <Text style={styles.helperText}>{t('publish_publish_disabled_hint')}</Text>
          ) : null}
          {publishStatus ? (
            <Text style={[styles.status, toneStyle(publishTone)]}>{publishStatus}</Text>
          ) : null}
          {publishZipUrl ? (
            <Text style={styles.zipText}>
              {t('publish_zip_ready', { value: publishZipUrl })}
            </Text>
          ) : null}
          <View style={styles.queueBlock}>
            <Text style={styles.queueTitle}>{t('publish_queue_title')}</Text>
            <Text style={styles.queueHint}>{t('publish_queue_hint')}</Text>
            {queueLoading ? <ActivityIndicator style={{ marginTop: 8 }} /> : null}
            {queueError ? (
              <Text style={[styles.status, styles.statusBad]}>{queueError}</Text>
            ) : null}
            {publishQueue.length ? (
              publishQueue.map((job) => {
                const name = (job.filename || '').replace(/\.zip$/i, '') || t('library_video_fallback', { id: job.id || '?' });
                const metaParts = [queueStatusLabel(job.status)];
                if (job.platforms?.length) metaParts.push(job.platforms.join(', '));
                if (job.updated_at || job.created_at) metaParts.push(job.updated_at || job.created_at || '');
                return (
                  <View key={job.id || name} style={styles.queueRow}>
                    <Text style={styles.queueName} numberOfLines={1}>{name}</Text>
                    <Text style={styles.queueMeta} numberOfLines={2}>{metaParts.filter(Boolean).join(' · ')}</Text>
                    {job.error ? <Text style={styles.queueError}>{job.error}</Text> : null}
                  </View>
                );
              })
            ) : !queueLoading && !queueError ? (
              <Text style={styles.empty}>{t('publish_queue_empty')}</Text>
            ) : null}
          </View>
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
  videoListScroll: {
    marginTop: 12,
    maxHeight: 420,
  },
  videoList: { gap: 12, paddingBottom: 4 },
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
  moreButton: {
    marginTop: 4,
    marginBottom: 4,
    alignSelf: 'center',
    paddingHorizontal: 18,
    paddingVertical: 8,
    borderRadius: 999,
    borderWidth: 1,
    borderColor: '#cbd5f5',
    backgroundColor: '#f8fafc',
  },
  moreButtonText: { fontSize: 12, fontWeight: '700', color: '#0f172a' },
  footerSpacer: { height: 8 },
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
  processButton: {
    marginTop: 12,
    backgroundColor: '#0f172a',
    paddingVertical: 12,
    borderRadius: 12,
    alignItems: 'center',
  },
  processButtonText: { color: 'white', fontWeight: '700' },
  processPreviewBlock: {
    marginTop: 12,
    padding: 12,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#e2e8f0',
    backgroundColor: '#f8fafc',
  },
  processPreviewTitle: { fontSize: 13, fontWeight: '600', color: '#0f172a' },
  processPreviewVideoWrap: {
    marginTop: 8,
    width: '100%',
    height: 200,
    borderRadius: 12,
    overflow: 'hidden',
    backgroundColor: '#0f172a',
  },
  processPreviewImage: { width: '100%', height: '100%' },
  processStatusBlock: {
    marginTop: 12,
    padding: 12,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#e2e8f0',
    backgroundColor: '#f8fafc',
  },
  processStatusHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  processStatusTitle: { fontSize: 13, fontWeight: '600', color: '#0f172a' },
  processStatusUpdated: { fontSize: 11, color: '#64748b' },
  processRow: { marginTop: 10 },
  processRowHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  processStepLabel: { fontSize: 12, fontWeight: '600', color: '#0f172a' },
  processStepStatus: { fontSize: 11, fontWeight: '600' },
  processStepDetail: { marginTop: 4, fontSize: 11, color: '#64748b' },
  empty: { marginTop: 12, color: '#64748b', fontSize: 12 },
  helperText: { marginTop: 8, fontSize: 12, color: '#64748b' },
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
  statusWarning: { color: '#b45309' },
  zipText: { marginTop: 8, fontSize: 12, color: '#475569' },
  queueBlock: {
    marginTop: 16,
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: '#e2e8f0',
  },
  queueTitle: { fontSize: 14, fontWeight: '700', color: '#0f172a' },
  queueHint: { marginTop: 6, fontSize: 12, color: '#64748b' },
  queueRow: {
    marginTop: 10,
    padding: 10,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#e2e8f0',
    backgroundColor: '#f8fafc',
  },
  queueName: { fontSize: 12, fontWeight: '600', color: '#0f172a' },
  queueMeta: { marginTop: 4, fontSize: 11, color: '#475569' },
  queueError: { marginTop: 4, fontSize: 11, color: '#b91c1c' },
});
