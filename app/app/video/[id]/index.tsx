import React, { useEffect, useMemo, useState } from 'react';
import {
  ActivityIndicator,
  Image,
  Modal,
  Platform,
  Pressable,
  ScrollView,
  StyleSheet,
  Switch,
  Text,
  View,
} from 'react-native';
import { Stack, useLocalSearchParams, useRouter } from 'expo-router';

const API_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8787';

type VideoDetail = {
  id: number;
  title: string | null;
  file_path: string;
  media_url?: string | null;
  created_at?: string;
};

type TranscriptionDetail = {
  id: number;
  status: string;
  preview_text?: string | null;
  md_url?: string | null;
  srt_url?: string | null;
  json_url?: string | null;
  error?: string | null;
  created_at?: string | null;
};

type CaptionDetail = {
  id: number;
  status: string;
  preview_text?: string | null;
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

type KeyframesDetail = {
  id: number;
  status: string;
  frame_urls?: string[];
  frame_count?: number;
  error?: string | null;
  created_at?: string | null;
};

type TranslationDetail = {
  id: number;
  language_code: string;
  status: string;
  preview_text?: string | null;
  json_url?: string | null;
  srt_url?: string | null;
  ass_url?: string | null;
  error?: string | null;
  created_at?: string | null;
};

type TranslateLang = 'ja' | 'en' | 'ar' | 'zh-Hant' | 'zh-Hans';

const formatTimestamp = (value?: string | null) =>
  value ? value.slice(0, 19).replace('T', ' ') : 'Unknown time';

const TRANSLATE_LANG_LABELS: Record<TranslateLang, string> = {
  ja: 'Japanese',
  en: 'English',
  ar: 'Arabic',
  'zh-Hant': 'Chinese (Traditional)',
  'zh-Hans': 'Chinese (Simplified)',
};

const normalizeTranslateLang = (value: string): TranslateLang | null => {
  const lowered = value.trim().toLowerCase();
  if (lowered === 'ja') return 'ja';
  if (lowered === 'en') return 'en';
  if (lowered === 'ar' || lowered === 'arabic') return 'ar';
  if (['zh', 'zh-hant', 'zh_hant', 'zh-tw', 'zh-hk', 'zh-mo'].includes(lowered)) {
    return 'zh-Hant';
  }
  if (['zh-hans', 'zh_hans', 'zh-cn'].includes(lowered)) {
    return 'zh-Hans';
  }
  return null;
};

export default function VideoDetailScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const router = useRouter();
  const [video, setVideo] = useState<VideoDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);
  const [processStatus, setProcessStatus] = useState<string>('');
  const [processTone, setProcessTone] = useState<'neutral' | 'good' | 'bad'>('neutral');
  const [transcription, setTranscription] = useState<TranscriptionDetail | null>(null);
  const [transcriptionLoading, setTranscriptionLoading] = useState(true);
  const [transcribing, setTranscribing] = useState(false);
  const [transcribeStatus, setTranscribeStatus] = useState('');
  const [transcribeTone, setTranscribeTone] = useState<'neutral' | 'good' | 'bad'>('neutral');
  const [caption, setCaption] = useState<CaptionDetail | null>(null);
  const [captionLoading, setCaptionLoading] = useState(true);
  const [captioning, setCaptioning] = useState(false);
  const [captionStatus, setCaptionStatus] = useState('');
  const [captionTone, setCaptionTone] = useState<'neutral' | 'good' | 'bad'>('neutral');
  const [keyframes, setKeyframes] = useState<KeyframesDetail | null>(null);
  const [keyframesLoading, setKeyframesLoading] = useState(true);
  const [extractingKeyframes, setExtractingKeyframes] = useState(false);
  const [keyframesStatus, setKeyframesStatus] = useState('');
  const [keyframesTone, setKeyframesTone] = useState<'neutral' | 'good' | 'bad'>('neutral');
  const [translations, setTranslations] = useState<TranslationDetail[]>([]);
  const [translationsLoading, setTranslationsLoading] = useState(true);
  const [translating, setTranslating] = useState(false);
  const [translateStatus, setTranslateStatus] = useState('');
  const [translateTone, setTranslateTone] = useState<'neutral' | 'good' | 'bad'>('neutral');
  const [disableTranslateCache, setDisableTranslateCache] = useState(false);
  const [selectedTranslateLangs, setSelectedTranslateLangs] = useState<TranslateLang[]>([
    'ja',
    'en',
    'zh-Hant',
    'zh-Hans',
  ]);
  const [previewLang, setPreviewLang] = useState<TranslateLang>('ja');
  const [translateLangsLoaded, setTranslateLangsLoaded] = useState(false);
  const [lightbox, setLightbox] = useState<{ url: string; label?: string } | null>(null);

  const mediaSrc = useMemo(() => {
    if (!video?.media_url) return null;
    return `${API_URL}${video.media_url}`;
  }, [video]);

  const headerTitle = video?.title ? video.title : 'Video';
  const captionFrameItems = caption?.frames || [];
  const translateLangOptions: Array<{ code: TranslateLang; label: string }> = [
    { code: 'ja', label: TRANSLATE_LANG_LABELS.ja },
    { code: 'en', label: TRANSLATE_LANG_LABELS.en },
    { code: 'ar', label: TRANSLATE_LANG_LABELS.ar },
    { code: 'zh-Hant', label: TRANSLATE_LANG_LABELS['zh-Hant'] },
    { code: 'zh-Hans', label: TRANSLATE_LANG_LABELS['zh-Hans'] },
  ];
  const previewTranslation = translations.find((item) => item.language_code === previewLang) || null;
  const previewLabel = TRANSLATE_LANG_LABELS[previewLang] || previewLang;

  useEffect(() => {
    if (!selectedTranslateLangs.length) return;
    if (!selectedTranslateLangs.includes(previewLang)) {
      setPreviewLang(selectedTranslateLangs[0]);
    }
  }, [selectedTranslateLangs, previewLang]);


  const loadTranscription = async () => {
    if (!id) return;
    setTranscriptionLoading(true);
    try {
      const resp = await fetch(`${API_URL}/api/videos/${id}/transcription`);
      if (resp.status === 404) {
        setTranscription(null);
        return;
      }
      const json = await resp.json();
      if (!resp.ok) {
        setTranscribeStatus(json.error || 'Failed to load transcription');
        setTranscribeTone('bad');
        setTranscription(null);
        return;
      }
      setTranscription(json);
    } catch (e: any) {
      setTranscribeStatus(e?.message || 'Failed to load transcription');
      setTranscribeTone('bad');
      setTranscription(null);
    } finally {
      setTranscriptionLoading(false);
    }
  };

  const loadCaption = async () => {
    if (!id) return;
    setCaptionLoading(true);
    try {
      const resp = await fetch(`${API_URL}/api/videos/${id}/caption`);
      if (resp.status === 404) {
        setCaption(null);
        return;
      }
      const json = await resp.json();
      if (!resp.ok) {
        setCaptionStatus(json.error || 'Failed to load captions');
        setCaptionTone('bad');
        setCaption(null);
        return;
      }
      setCaption(json);
    } catch (e: any) {
      setCaptionStatus(e?.message || 'Failed to load captions');
      setCaptionTone('bad');
      setCaption(null);
    } finally {
      setCaptionLoading(false);
    }
  };

  const loadKeyframes = async () => {
    if (!id) return;
    setKeyframesLoading(true);
    try {
      const resp = await fetch(`${API_URL}/api/videos/${id}/keyframes`);
      if (resp.status === 404) {
        setKeyframes(null);
        return;
      }
      const json = await resp.json();
      if (!resp.ok) {
        setKeyframesStatus(json.error || 'Failed to load keyframes');
        setKeyframesTone('bad');
        setKeyframes(null);
        return;
      }
      setKeyframes(json);
    } catch (e: any) {
      setKeyframesStatus(e?.message || 'Failed to load keyframes');
      setKeyframesTone('bad');
      setKeyframes(null);
    } finally {
      setKeyframesLoading(false);
    }
  };

  const loadTranslations = async () => {
    if (!id) return;
    setTranslationsLoading(true);
    try {
      const resp = await fetch(`${API_URL}/api/videos/${id}/translations`);
      const json = await resp.json();
      if (!resp.ok) {
        setTranslateStatus(json.error || 'Failed to load translations');
        setTranslateTone('bad');
        setTranslations([]);
        return;
      }
      const items: TranslationDetail[] = Array.isArray(json.translations) ? json.translations : [];
      const hasZhHant = items.some((item) => item.language_code === 'zh-Hant');
      const normalizedItems = items.map((item) => {
        if (item.language_code === 'zh' && !hasZhHant) {
          return { ...item, language_code: 'zh-Hant' };
        }
        return item;
      });
      setTranslations(normalizedItems);
    } catch (e: any) {
      setTranslateStatus(e?.message || 'Failed to load translations');
      setTranslateTone('bad');
      setTranslations([]);
    } finally {
      setTranslationsLoading(false);
    }
  };

  useEffect(() => {
    if (!id) return;
    (async () => {
      setLoading(true);
      try {
        const resp = await fetch(`${API_URL}/api/videos/${id}`);
        const json = await resp.json();
        if (!resp.ok) {
          setProcessStatus(json.error || 'Failed to load video');
          setProcessTone('bad');
          setVideo(null);
        } else {
          setVideo(json);
        }
      } catch (e: any) {
        setProcessStatus(e?.message || 'Failed to load video');
        setProcessTone('bad');
      } finally {
        setLoading(false);
      }
    })();
  }, [id]);

  useEffect(() => {
    (async () => {
      try {
        const resp = await fetch(`${API_URL}/api/ui-settings/translation_languages`);
        const json = await resp.json();
        if (!resp.ok) return;
        const value = Array.isArray(json.value) ? json.value : [];
        const cleaned: TranslateLang[] = [];
        value.forEach((item) => {
          const normalized = normalizeTranslateLang(String(item));
          if (normalized && !cleaned.includes(normalized)) {
            cleaned.push(normalized);
          }
        });
        if (cleaned.length) {
          setSelectedTranslateLangs(cleaned);
          if (!cleaned.includes(previewLang)) {
            setPreviewLang(cleaned[0]);
          }
        }
      } catch (_err) {
        // ignore load failures; keep defaults
      } finally {
        setTranslateLangsLoaded(true);
      }
    })();
  }, []);

  useEffect(() => {
    if (!translateLangsLoaded) return;
    const payload = selectedTranslateLangs;
    const timeout = setTimeout(async () => {
      try {
        await fetch(`${API_URL}/api/ui-settings/translation_languages`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });
      } catch (_err) {
        // ignore save failures
      }
    }, 200);
    return () => clearTimeout(timeout);
  }, [selectedTranslateLangs, translateLangsLoaded]);

  useEffect(() => {
    loadTranscription();
    loadCaption();
    loadKeyframes();
    loadTranslations();
  }, [id]);

  const processVideo = async () => {
    if (!video || processing) return;
    setProcessing(true);
    setProcessStatus('Processing... this can take several minutes.');
    setProcessTone('neutral');
    try {
      const body = new URLSearchParams({ file_path: video.file_path });
      const resp = await fetch(`${API_URL}/video-processing`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: body.toString(),
      });
      if (!resp.ok) {
        const errText = await resp.text();
        setProcessStatus(`Processing failed: ${errText}`);
        setProcessTone('bad');
        return;
      }
      if (Platform.OS === 'web') {
        const blob = await resp.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `lazyedit_${video.id}.zip`;
        a.click();
        URL.revokeObjectURL(url);
        setProcessStatus('Processing complete. Download started.');
        setProcessTone('good');
      } else {
        setProcessStatus('Processing complete.');
        setProcessTone('good');
      }
    } catch (e: any) {
      setProcessStatus(`Processing failed: ${e?.message || String(e)}`);
      setProcessTone('bad');
    } finally {
      setProcessing(false);
    }
  };

  const transcribeVideo = async () => {
    if (!video || transcribing) return;
    setTranscribing(true);
    setTranscribeStatus('Transcribing... this can take a few minutes.');
    setTranscribeTone('neutral');
    try {
      const resp = await fetch(`${API_URL}/api/videos/${video.id}/transcribe`, { method: 'POST' });
      const json = await resp.json();
      if (!resp.ok) {
        setTranscribeStatus(json.error || json.details || 'Transcription failed');
        setTranscribeTone('bad');
        return;
      }
      setTranscription(json);
      if (json.status === 'no_audio') {
        setTranscribeStatus('No audio detected in this video.');
        setTranscribeTone('bad');
      } else {
        setTranscribeStatus('Transcription complete.');
        setTranscribeTone('good');
      }
    } catch (e: any) {
      setTranscribeStatus(`Transcription failed: ${e?.message || String(e)}`);
      setTranscribeTone('bad');
    } finally {
      setTranscribing(false);
    }
  };

  const translateSubtitles = async () => {
    if (!video || translating) return;
    if (!selectedTranslateLangs.length) {
      setTranslateStatus('Select at least one language.');
      setTranslateTone('bad');
      return;
    }
    setTranslating(true);
    setTranslateStatus('Starting translations...');
    setTranslateTone('neutral');
    try {
      for (let i = 0; i < selectedTranslateLangs.length; i += 1) {
        const lang = selectedTranslateLangs[i];
        const label = TRANSLATE_LANG_LABELS[lang] || lang;
        setTranslateStatus(`Translating ${label} (${i + 1}/${selectedTranslateLangs.length})...`);
        const resp = await fetch(`${API_URL}/api/videos/${video.id}/translate`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ language: lang, use_cache: !disableTranslateCache }),
        });
        const json = await resp.json();
        if (!resp.ok) {
          setTranslateStatus(json.error || json.details || `Translation failed for ${label}`);
          setTranslateTone('bad');
          return;
        }
        await loadTranslations();
      }
      setTranslateStatus('Translations complete.');
      setTranslateTone('good');
    } catch (e: any) {
      setTranslateStatus(`Translation failed: ${e?.message || String(e)}`);
      setTranslateTone('bad');
    } finally {
      setTranslating(false);
    }
  };

  const processStatusStyle =
    processTone === 'good' ? styles.statusGood : processTone === 'bad' ? styles.statusBad : styles.statusNeutral;
  const transcribeStatusStyle =
    transcribeTone === 'good' ? styles.statusGood : transcribeTone === 'bad' ? styles.statusBad : styles.statusNeutral;
  const captionStatusStyle =
    captionTone === 'good' ? styles.statusGood : captionTone === 'bad' ? styles.statusBad : styles.statusNeutral;
  const keyframesStatusStyle =
    keyframesTone === 'good' ? styles.statusGood : keyframesTone === 'bad' ? styles.statusBad : styles.statusNeutral;
  const translateStatusStyle =
    translateTone === 'good' ? styles.statusGood : translateTone === 'bad' ? styles.statusBad : styles.statusNeutral;

  const captionFrames = async () => {
    if (!video || captioning) return;
    setCaptioning(true);
    setCaptionStatus('Captioning frames... this can take a few minutes.');
    setCaptionTone('neutral');
    try {
      const resp = await fetch(`${API_URL}/api/videos/${video.id}/caption`, { method: 'POST' });
      const json = await resp.json();
      if (!resp.ok) {
        setCaptionStatus(json.error || json.details || 'Captioning failed');
        setCaptionTone('bad');
        return;
      }
      setCaption(json);
      if (json.status === 'not_configured') {
        setCaptionStatus(json.error || 'Captioner not configured.');
        setCaptionTone('bad');
      } else if (json.status === 'failed') {
        setCaptionStatus(json.error || 'Captioning failed.');
        setCaptionTone('bad');
      } else if (json.status === 'empty') {
        setCaptionStatus('No captions generated for this video.');
        setCaptionTone('bad');
      } else {
        setCaptionStatus('Captioning complete.');
        setCaptionTone('good');
      }
    } catch (e: any) {
      setCaptionStatus(`Captioning failed: ${e?.message || String(e)}`);
      setCaptionTone('bad');
    } finally {
      setCaptioning(false);
    }
  };

  const extractKeyframes = async () => {
    if (!video || extractingKeyframes) return;
    setExtractingKeyframes(true);
    setKeyframesStatus('Extracting key frames...');
    setKeyframesTone('neutral');
    try {
      const resp = await fetch(`${API_URL}/api/videos/${video.id}/keyframes`, { method: 'POST' });
      const json = await resp.json();
      if (!resp.ok) {
        setKeyframesStatus(json.error || json.details || 'Keyframe extraction failed');
        setKeyframesTone('bad');
        return;
      }
      setKeyframes(json);
      setKeyframesStatus('Keyframes ready.');
      setKeyframesTone('good');
    } catch (e: any) {
      setKeyframesStatus(`Keyframe extraction failed: ${e?.message || String(e)}`);
      setKeyframesTone('bad');
    } finally {
      setExtractingKeyframes(false);
    }
  };

  if (loading) {
    return (
      <View style={styles.container}>
        <Stack.Screen options={{ title: headerTitle, headerBackTitle: 'Videos' }} />
        <ActivityIndicator />
        <Text style={styles.loadingText}>Loading video...</Text>
      </View>
    );
  }

  if (!video) {
    return (
      <View style={styles.container}>
        <Stack.Screen options={{ title: headerTitle, headerBackTitle: 'Videos' }} />
        <Text style={styles.title}>Video not found</Text>
        {processStatus ? <Text style={[styles.status, processStatusStyle]}>{processStatus}</Text> : null}
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <Stack.Screen options={{ title: headerTitle, headerBackTitle: 'Videos' }} />
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.card}>
          <Text style={styles.title}>{video.title || `Video #${video.id}`}</Text>
          <Text style={styles.meta}>{video.file_path}</Text>
          <Text style={styles.meta}>{formatTimestamp(video.created_at)}</Text>
          <View style={styles.preview}>
            {Platform.OS === 'web' && mediaSrc ? (
              React.createElement('video', {
                src: mediaSrc,
                style: { width: '100%', height: '100%', borderRadius: 14, objectFit: 'contain' },
                controls: true,
                muted: true,
                playsInline: true,
                preload: 'metadata',
              })
            ) : (
              <Text style={styles.previewLabel}>Preview</Text>
            )}
          </View>
        </View>

        <Pressable
          style={[styles.btn, processing && styles.btnDisabled]}
          onPress={processVideo}
          disabled={processing}
        >
          <View style={styles.btnContent}>
            {processing && <ActivityIndicator color="white" style={{ marginRight: 8 }} />}
            <Text style={styles.btnText}>{processing ? 'Processing...' : 'Process video'}</Text>
          </View>
        </Pressable>

        {processStatus ? <Text style={[styles.status, processStatusStyle]}>{processStatus}</Text> : null}

        <Pressable
          style={[styles.btnSecondary, transcribing && styles.btnDisabled]}
          onPress={transcribeVideo}
          disabled={transcribing}
        >
          <View style={styles.btnContent}>
            {transcribing && <ActivityIndicator color="white" style={{ marginRight: 8 }} />}
            <Text style={styles.btnText}>{transcribing ? 'Transcribing...' : 'Transcribe'}</Text>
          </View>
        </Pressable>

        <View style={styles.sectionCard}>
          <Text style={styles.sectionTitle}>Transcription preview</Text>
          {transcriptionLoading ? (
            <ActivityIndicator />
          ) : transcription ? (
            <>
              <Text style={styles.sectionMeta}>
                Status: {transcription.status}
              </Text>
              {transcription.preview_text ? (
                <Text style={styles.previewText}>{transcription.preview_text}</Text>
              ) : (
                <Text style={styles.previewEmpty}>No preview available.</Text>
              )}
              {transcription.error ? <Text style={styles.previewError}>{transcription.error}</Text> : null}
              <Pressable
                style={styles.previewBtn}
                onPress={() =>
                  router.push({ pathname: '/video/[id]/transcription', params: { id: String(video.id) } })
                }
              >
                <Text style={styles.previewBtnText}>Preview transcription</Text>
              </Pressable>
            </>
          ) : (
            <Text style={styles.previewEmpty}>No transcription yet. Tap Transcribe.</Text>
          )}
        </View>

        {transcribeStatus ? <Text style={[styles.status, transcribeStatusStyle]}>{transcribeStatus}</Text> : null}

        <View style={styles.toggleRowInline}>
          <Switch
            value={disableTranslateCache}
            onValueChange={setDisableTranslateCache}
            trackColor={{ false: '#e2e8f0', true: '#2563eb' }}
            thumbColor={disableTranslateCache ? '#f8fafc' : '#f1f5f9'}
          />
          <View style={styles.toggleInlineText}>
            <Text style={styles.toggleTitle}>Bypass cache</Text>
            <Text style={styles.toggleHint}>Force a fresh translation</Text>
          </View>
        </View>

        <View style={styles.langChecklist}>
          {translateLangOptions.map((option) => {
            const isChecked = selectedTranslateLangs.includes(option.code);
            return (
              <Pressable
                key={option.code}
                style={styles.langCheckItem}
                onPress={() => {
                  setSelectedTranslateLangs((prev) => {
                    if (prev.includes(option.code)) {
                      return prev.filter((lang) => lang !== option.code);
                    }
                    return [...prev, option.code];
                  });
                }}
              >
                <View style={[styles.langCheckBox, isChecked && styles.langCheckBoxActive]}>
                  {isChecked ? <Text style={styles.langCheckMark}>✓</Text> : null}
                </View>
                <Text style={styles.langCheckLabel}>{option.label}</Text>
              </Pressable>
            );
          })}
        </View>

        <Pressable
          style={[styles.btnSecondaryAlt, translating && styles.btnDisabled]}
          onPress={translateSubtitles}
          disabled={translating}
        >
          <View style={styles.btnContent}>
            {translating && <ActivityIndicator color="white" style={{ marginRight: 8 }} />}
            <Text style={styles.btnText}>{translating ? 'Translating...' : 'Translate'}</Text>
          </View>
        </Pressable>

        <View style={styles.sectionCard}>
          <Text style={styles.sectionTitle}>Translation preview</Text>
          <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.langTabs}>
            {translateLangOptions.map((option) => {
              const isActive = previewLang === option.code;
              return (
                <Pressable
                  key={option.code}
                  style={[styles.langTab, isActive && styles.langTabActive]}
                  onPress={() => setPreviewLang(option.code)}
                >
                  <Text style={[styles.langTabText, isActive && styles.langTabTextActive]}>{option.label}</Text>
                </Pressable>
              );
            })}
          </ScrollView>
          {translationsLoading ? (
            <ActivityIndicator />
          ) : previewTranslation ? (
            <>
              <Text style={styles.sectionMeta}>Status: {previewTranslation.status}</Text>
              {previewTranslation.preview_text ? (
                <Text style={styles.previewText}>{previewTranslation.preview_text}</Text>
              ) : (
                <Text style={styles.previewEmpty}>No preview available.</Text>
              )}
              {previewTranslation.error ? <Text style={styles.previewError}>{previewTranslation.error}</Text> : null}
              <Pressable
                style={styles.previewBtn}
                onPress={() => router.push({ pathname: '/video/[id]/translations', params: { id: String(video.id) } })}
              >
                <Text style={styles.previewBtnText}>View translations</Text>
              </Pressable>
            </>
          ) : (
            <Text style={styles.previewEmpty}>No translations yet for {previewLabel}. Tap Translate to generate.</Text>
          )}
        </View>

        {translateStatus ? <Text style={[styles.status, translateStatusStyle]}>{translateStatus}</Text> : null}

        <Pressable
          style={[styles.btnSecondaryAlt, extractingKeyframes && styles.btnDisabled]}
          onPress={extractKeyframes}
          disabled={extractingKeyframes}
        >
          <View style={styles.btnContent}>
            {extractingKeyframes && <ActivityIndicator color="white" style={{ marginRight: 8 }} />}
            <Text style={styles.btnText}>{extractingKeyframes ? 'Extracting...' : 'Extract key frames'}</Text>
          </View>
        </Pressable>

        <View style={styles.sectionCard}>
          <Text style={styles.sectionTitle}>Key frames preview</Text>
          {keyframesLoading ? (
            <ActivityIndicator />
          ) : keyframes ? (
            <>
              <Text style={styles.sectionMeta}>Status: {keyframes.status}</Text>
              <View style={styles.keyframeGrid}>
                {(keyframes.frame_urls || []).slice(0, 6).map((url, idx) => (
                  <Pressable
                    key={url}
                    style={styles.keyframeItem}
                    onPress={() => setLightbox({ url: `${API_URL}${url}`, label: `Key frame ${idx + 1}` })}
                  >
                    <Image source={{ uri: `${API_URL}${url}` }} style={styles.keyframeImage} />
                    <View style={styles.keyframeLabel}>
                      <Text style={styles.keyframeLabelText}>{`Key frame ${idx + 1}`}</Text>
                    </View>
                  </Pressable>
                ))}
              </View>
              {keyframes.error ? <Text style={styles.previewError}>{keyframes.error}</Text> : null}
              <Pressable
                style={styles.previewBtn}
                onPress={() => router.push({ pathname: '/video/[id]/keyframes', params: { id: String(video.id) } })}
              >
                <Text style={styles.previewBtnText}>View all key frames</Text>
              </Pressable>
            </>
          ) : (
            <Text style={styles.previewEmpty}>No keyframes yet. Tap Extract key frames.</Text>
          )}
        </View>

        {keyframesStatus ? <Text style={[styles.status, keyframesStatusStyle]}>{keyframesStatus}</Text> : null}

        <Pressable
          style={[styles.btnSecondary, captioning && styles.btnDisabled]}
          onPress={captionFrames}
          disabled={captioning}
        >
          <View style={styles.btnContent}>
            {captioning && <ActivityIndicator color="white" style={{ marginRight: 8 }} />}
            <Text style={styles.btnText}>{captioning ? 'Captioning...' : 'Caption frames'}</Text>
          </View>
        </Pressable>

        <View style={styles.sectionCard}>
          <Text style={styles.sectionTitle}>Frame captions preview</Text>
          {captionLoading ? (
            <ActivityIndicator />
          ) : caption ? (
            <>
              <Text style={styles.sectionMeta}>Status: {caption.status}</Text>
              {caption.preview_text ? (
                <Text style={styles.previewText}>{caption.preview_text}</Text>
              ) : (
                <Text style={styles.previewEmpty}>No preview available.</Text>
              )}
              {captionFrameItems.length ? (
                <View style={styles.captionGrid}>
                  {captionFrameItems.slice(0, 6).map((frame, idx) => (
                    <Pressable
                      key={`${frame.url}-${idx}`}
                      style={styles.captionItem}
                      onPress={() =>
                        setLightbox({ url: `${API_URL}${frame.url}`, label: frame.text || `Frame ${idx + 1}` })
                      }
                    >
                      <Image source={{ uri: `${API_URL}${frame.url}` }} style={styles.captionImage} />
                      <View style={styles.captionOverlay}>
                        <Text style={styles.captionOverlayText} numberOfLines={2}>
                          {frame.text || `Frame ${idx + 1}`}
                        </Text>
                      </View>
                    </Pressable>
                  ))}
                </View>
              ) : null}
              {caption.error ? <Text style={styles.previewError}>{caption.error}</Text> : null}
              <Pressable
                style={styles.previewBtn}
                onPress={() => router.push({ pathname: '/video/[id]/caption', params: { id: String(video.id) } })}
              >
                <Text style={styles.previewBtnText}>Preview captions</Text>
              </Pressable>
            </>
          ) : (
            <Text style={styles.previewEmpty}>No captions yet. Tap Caption frames.</Text>
          )}
        </View>

        {captionStatus ? <Text style={[styles.status, captionStatusStyle]}>{captionStatus}</Text> : null}
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
  scrollContent: { paddingBottom: 32 },
  card: {
    backgroundColor: 'white',
    borderRadius: 16,
    borderWidth: 1,
    borderColor: '#e2e8f0',
    padding: 16,
  },
  title: { fontSize: 20, fontWeight: '700', color: '#0f172a' },
  meta: { color: '#475569', fontSize: 12, marginTop: 4 },
  preview: {
    marginTop: 14,
    height: 260,
    borderRadius: 14,
    backgroundColor: '#0f172a',
    justifyContent: 'center',
    alignItems: 'center',
    overflow: 'hidden',
  },
  previewLabel: { color: '#cbd5f5', fontSize: 12, fontWeight: '600' },
  btn: {
    marginTop: 16,
    backgroundColor: '#3b82f6',
    paddingVertical: 12,
    paddingHorizontal: 18,
    borderRadius: 12,
    alignSelf: 'flex-start',
  },
  btnDisabled: { opacity: 0.6 },
  btnContent: { flexDirection: 'row', alignItems: 'center' },
  btnText: { color: 'white', fontWeight: '600' },
  btnSecondary: {
    marginTop: 10,
    backgroundColor: '#0f172a',
    paddingVertical: 12,
    paddingHorizontal: 18,
    borderRadius: 12,
    alignSelf: 'flex-start',
  },
  btnSecondaryAlt: {
    marginTop: 10,
    backgroundColor: '#1d4ed8',
    paddingVertical: 12,
    paddingHorizontal: 18,
    borderRadius: 12,
    alignSelf: 'flex-start',
  },
  toggleRowInline: {
    marginTop: 10,
    flexDirection: 'row',
    alignItems: 'center',
  },
  toggleInlineText: { marginLeft: 12 },
  toggleTitle: { fontSize: 12, fontWeight: '600', color: '#0f172a' },
  toggleHint: { fontSize: 11, color: '#64748b', marginTop: 2 },
  langTabs: { marginTop: 10, flexGrow: 0 },
  langTab: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 999,
    borderWidth: 1,
    borderColor: '#e2e8f0',
    marginRight: 8,
    backgroundColor: '#f8fafc',
  },
  langTabActive: { backgroundColor: '#0f766e', borderColor: '#0f766e' },
  langTabText: { fontSize: 12, fontWeight: '600', color: '#0f172a' },
  langTabTextActive: { color: '#f8fafc' },
  langChecklist: {
    marginTop: 10,
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  langCheckItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 6,
    paddingHorizontal: 10,
    borderRadius: 999,
    borderWidth: 1,
    borderColor: '#e2e8f0',
    backgroundColor: '#f8fafc',
    marginRight: 10,
    marginBottom: 10,
  },
  langCheckBox: {
    width: 16,
    height: 16,
    borderRadius: 4,
    borderWidth: 1,
    borderColor: '#94a3b8',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 6,
    backgroundColor: 'white',
  },
  langCheckBoxActive: { backgroundColor: '#0f766e', borderColor: '#0f766e' },
  langCheckMark: { color: 'white', fontSize: 10, fontWeight: '700' },
  langCheckLabel: { fontSize: 12, fontWeight: '600', color: '#0f172a' },
  sectionCard: {
    marginTop: 16,
    padding: 14,
    borderRadius: 14,
    borderWidth: 1,
    borderColor: '#e2e8f0',
    backgroundColor: 'white',
  },
  sectionTitle: { fontSize: 14, fontWeight: '700', color: '#0f172a', marginBottom: 6 },
  sectionMeta: { fontSize: 12, color: '#475569', marginBottom: 8 },
  previewText: { fontSize: 12, color: '#0f172a' },
  previewEmpty: { fontSize: 12, color: '#64748b' },
  previewError: { fontSize: 12, color: '#b91c1c', marginTop: 6 },
  previewBtn: {
    marginTop: 10,
    alignSelf: 'flex-start',
    backgroundColor: '#e2e8f0',
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderRadius: 10,
  },
  previewBtnText: { fontSize: 12, fontWeight: '600', color: '#0f172a' },
  keyframeGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginTop: 8,
  },
  keyframeItem: {
    width: 110,
    height: 70,
    borderRadius: 10,
    marginRight: 8,
    marginBottom: 8,
    overflow: 'hidden',
    backgroundColor: '#0f172a',
  },
  keyframeImage: {
    width: '100%',
    height: '100%',
  },
  keyframeLabel: {
    position: 'absolute',
    left: 6,
    bottom: 6,
    backgroundColor: 'rgba(15, 23, 42, 0.75)',
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 6,
  },
  keyframeLabelText: { color: '#f8fafc', fontSize: 10, fontWeight: '600' },
  captionGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginTop: 10,
  },
  captionItem: {
    width: 140,
    height: 90,
    borderRadius: 10,
    marginRight: 8,
    marginBottom: 8,
    overflow: 'hidden',
    backgroundColor: '#0f172a',
  },
  captionImage: { width: '100%', height: '100%' },
  captionOverlay: {
    position: 'absolute',
    left: 0,
    right: 0,
    bottom: 0,
    paddingHorizontal: 6,
    paddingVertical: 4,
    backgroundColor: 'rgba(15, 23, 42, 0.72)',
  },
  captionOverlayText: { color: '#f8fafc', fontSize: 10, fontWeight: '600' },
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
  status: { marginTop: 12, fontSize: 12 },
  statusNeutral: { color: '#0f172a' },
  statusGood: { color: '#15803d' },
  statusBad: { color: '#b91c1c' },
  loadingText: { marginTop: 8, color: '#475569' },
});
