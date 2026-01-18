import React, { useCallback, useEffect, useMemo, useState } from 'react';
import {
  ActivityIndicator,
  Image,
  Modal,
  Platform,
  Pressable,
  ScrollView,
  StyleSheet,
  Switch,
  TextInput,
  Text,
  View,
} from 'react-native';
import { useFocusEffect } from '@react-navigation/native';
import { Stack, useLocalSearchParams, useRouter } from 'expo-router';

const API_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8787';

type VideoDetail = {
  id: number;
  title: string | null;
  file_path: string;
  media_url?: string | null;
  preview_media_url?: string | null;
  created_at?: string;
};

type TranscriptionDetail = {
  id: number;
  status: string;
  preview_text?: string | null;
  md_url?: string | null;
  srt_url?: string | null;
  json_url?: string | null;
  primary_language?: string | null;
  language_summary?: { language: string; count: number }[];
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

type MetadataWord = {
  word: string;
  timestamp_range: {
    start: string;
    end: string;
  };
};

type MetadataPayload = {
  title: string;
  brief_description: string;
  middle_description: string;
  long_description: string;
  tags: string[];
  english_words_to_learn: MetadataWord[];
  teaser: { start: string; end: string };
  cover: string;
};

type MetadataDetail = {
  id: number;
  status: string;
  language_code: 'zh' | 'en';
  metadata?: MetadataPayload | null;
  json_url?: string | null;
  error?: string | null;
  created_at?: string | null;
};

type TranslateLang = 'ja' | 'en' | 'ar' | 'vi' | 'ko' | 'es' | 'fr' | 'ru' | 'yue' | 'zh-Hant' | 'zh-Hans';

const formatTimestamp = (value?: string | null) =>
  value ? value.slice(0, 19).replace('T', ' ') : 'Unknown time';

const TRANSLATE_LANG_LABELS: Record<TranslateLang, string> = {
  ja: 'Japanese',
  en: 'English',
  ar: 'Arabic',
  vi: 'Vietnamese',
  ko: 'Korean',
  es: 'Spanish',
  fr: 'French',
  ru: 'Russian',
  yue: 'Cantonese',
  'zh-Hant': 'Chinese (Traditional)',
  'zh-Hans': 'Chinese (Simplified)',
};

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

const normalizeTranslateLang = (value: string): TranslateLang | null => {
  const lowered = value.trim().toLowerCase();
  if (lowered === 'ja') return 'ja';
  if (lowered === 'en') return 'en';
  if (lowered === 'ar' || lowered === 'arabic') return 'ar';
  if (lowered === 'vi' || lowered === 'vietnamese') return 'vi';
  if (lowered === 'ko' || lowered === 'korean') return 'ko';
  if (lowered === 'es' || lowered === 'spanish') return 'es';
  if (lowered === 'fr' || lowered === 'french') return 'fr';
  if (lowered === 'ru' || lowered === 'russian') return 'ru';
  if (lowered === 'yue' || lowered === 'cantonese' || lowered === 'zh-yue') return 'yue';
  if (['zh', 'zh-hant', 'zh_hant', 'zh-tw', 'zh-hk', 'zh-mo'].includes(lowered)) {
    return 'zh-Hant';
  }
  if (['zh-hans', 'zh_hans', 'zh-cn'].includes(lowered)) {
    return 'zh-Hans';
  }
  return null;
};

const MAIN_TABS = ['captions', 'subtitles', 'metadata'] as const;
const MAIN_TAB_LABELS: Record<typeof MAIN_TABS[number], string> = {
  captions: 'Captions',
  subtitles: 'Subtitles',
  metadata: 'Metadata',
};

export default function VideoDetailScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const router = useRouter();
  const [video, setVideo] = useState<VideoDetail | null>(null);
  const [proxyStatus, setProxyStatus] = useState('');
  const [loading, setLoading] = useState(true);
  const [transcription, setTranscription] = useState<TranscriptionDetail | null>(null);
  const [transcriptionLoading, setTranscriptionLoading] = useState(true);
  const [transcribing, setTranscribing] = useState(false);
  const [transcribeStatus, setTranscribeStatus] = useState('');
  const [transcribeTone, setTranscribeTone] = useState<'neutral' | 'good' | 'bad'>('neutral');
  const [polishNotes, setPolishNotes] = useState('');
  const [polishNotesTouched, setPolishNotesTouched] = useState(false);
  const [polishSettingsLoaded, setPolishSettingsLoaded] = useState(false);
  const [polishDetail, setPolishDetail] = useState<TranscriptionDetail | null>(null);
  const [polishLoading, setPolishLoading] = useState(true);
  const [polishing, setPolishing] = useState(false);
  const [polishStatus, setPolishStatus] = useState('');
  const [polishTone, setPolishTone] = useState<'neutral' | 'good' | 'bad'>('neutral');
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
  const [metadataNotes, setMetadataNotes] = useState('');
  const [metadataZh, setMetadataZh] = useState<MetadataDetail | null>(null);
  const [metadataEn, setMetadataEn] = useState<MetadataDetail | null>(null);
  const [metadataLoading, setMetadataLoading] = useState(true);
  const [metadataGenerating, setMetadataGenerating] = useState<Record<'zh' | 'en', boolean>>({
    zh: false,
    en: false,
  });
  const [metadataGeneratingAll, setMetadataGeneratingAll] = useState(false);
  const [metadataStatus, setMetadataStatus] = useState('');
  const [metadataTone, setMetadataTone] = useState<'neutral' | 'good' | 'bad'>('neutral');
  const [metadataTab, setMetadataTab] = useState<'zh' | 'en'>('zh');
  const [activeMainTab, setActiveMainTab] = useState<typeof MAIN_TABS[number]>('captions');
  const [selectedTranslateLangs, setSelectedTranslateLangs] = useState<TranslateLang[]>([
    'ja',
    'en',
    'zh-Hant',
    'fr',
  ]);
  const [previewLang, setPreviewLang] = useState<TranslateLang>('ja');
  const [translateLangsLoaded, setTranslateLangsLoaded] = useState(false);
  const [lightbox, setLightbox] = useState<{ url: string; label?: string } | null>(null);

  const mediaSrc = useMemo(() => {
    const path = video?.preview_media_url || video?.media_url;
    if (!path) return null;
    if (path.startsWith('http://') || path.startsWith('https://')) return path;
    return `${API_URL}${path}`;
  }, [video]);

  const loadVideo = async () => {
    if (!id) return;
    try {
      const resp = await fetch(`${API_URL}/api/videos/${id}`);
      const json = await resp.json();
      if (!resp.ok) {
        setVideo(null);
      } else {
        setVideo(json);
      }
    } catch (_err) {
      setVideo(null);
    }
  };

  const createProxyPreview = async () => {
    if (!id) return;
    setProxyStatus('Creating preview proxy…');
    try {
      const resp = await fetch(`${API_URL}/api/videos/${id}/proxy`, { method: 'POST' });
      const json = await resp.json();
      if (!resp.ok) {
        const details = json.details ? `: ${json.details}` : '';
        setProxyStatus(`Proxy failed: ${json.error || json.message || resp.statusText}${details}`);
        return;
      }
      setProxyStatus('Proxy ready.');
      await loadVideo();
    } catch (err: any) {
      setProxyStatus(`Proxy failed: ${err?.message || String(err)}`);
    }
  };

  const headerTitle = video?.title ? video.title : 'Video';
  const captionFrameItems = caption?.frames || [];
  const translateLangOptions: Array<{ code: TranslateLang; label: string }> = [
    { code: 'en', label: TRANSLATE_LANG_LABELS.en },
    { code: 'zh-Hant', label: TRANSLATE_LANG_LABELS['zh-Hant'] },
    { code: 'zh-Hans', label: TRANSLATE_LANG_LABELS['zh-Hans'] },
    { code: 'yue', label: TRANSLATE_LANG_LABELS.yue },
    { code: 'ja', label: TRANSLATE_LANG_LABELS.ja },
    { code: 'ar', label: TRANSLATE_LANG_LABELS.ar },
    { code: 'vi', label: TRANSLATE_LANG_LABELS.vi },
    { code: 'ko', label: TRANSLATE_LANG_LABELS.ko },
    { code: 'es', label: TRANSLATE_LANG_LABELS.es },
    { code: 'fr', label: TRANSLATE_LANG_LABELS.fr },
    { code: 'ru', label: TRANSLATE_LANG_LABELS.ru },
  ];
  const previewTranslation = translations.find((item) => item.language_code === previewLang) || null;
  const previewLabel = TRANSLATE_LANG_LABELS[previewLang] || previewLang;
  const transcriptionLanguages = useMemo(() => {
    if (!transcription) return null;
    if (transcription.primary_language) {
      return `Language: ${formatAudioLanguage(transcription.primary_language)}`;
    }
    const summary = transcription.language_summary || [];
    if (!summary.length) return null;
    const labels = summary.map((item) => formatAudioLanguage(item.language));
    return `Languages: ${labels.join(', ')}`;
  }, [transcription]);
  const metadataTabs: Array<{ code: 'zh' | 'en'; label: string }> = [
    { code: 'zh', label: 'Chinese social' },
    { code: 'en', label: 'English YouTube' },
  ];
  const activeMetadata = metadataTab === 'zh' ? metadataZh : metadataEn;
  const activeMetadataLabel = metadataTab === 'zh' ? 'Chinese social' : 'English YouTube';
  const polishSeedText = useMemo(() => {
    const source = caption?.preview_text || transcription?.preview_text || video?.title || '';
    const cleaned = source.replace(/\s+/g, ' ').trim();
    if (!cleaned) return '';
    return cleaned.length > 240 ? `${cleaned.slice(0, 240)}…` : cleaned;
  }, [caption?.preview_text, transcription?.preview_text, video?.title]);

  useEffect(() => {
    if (!selectedTranslateLangs.length) return;
    if (!selectedTranslateLangs.includes(previewLang)) {
      setPreviewLang(selectedTranslateLangs[0]);
    }
  }, [selectedTranslateLangs, previewLang]);


  const loadTranscription = useCallback(async () => {
    if (!id) return;
    setTranscriptionLoading(true);
    try {
      const resp = await fetch(`${API_URL}/api/videos/${id}/transcription`, { cache: 'no-store' });
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
  }, [id]);

  const loadSubtitlePolish = useCallback(async () => {
    if (!id) return;
    setPolishLoading(true);
    try {
      const resp = await fetch(`${API_URL}/api/videos/${id}/polish-subtitles`, { cache: 'no-store' });
      if (resp.status === 404) {
        setPolishDetail(null);
        return;
      }
      const json = await resp.json();
      if (!resp.ok) {
        setPolishStatus(json.error || 'Failed to load polished subtitles');
        setPolishTone('bad');
        setPolishDetail(null);
        return;
      }
      setPolishDetail(json);
    } catch (e: any) {
      setPolishStatus(e?.message || 'Failed to load polished subtitles');
      setPolishTone('bad');
      setPolishDetail(null);
    } finally {
      setPolishLoading(false);
    }
  }, [id]);

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

  const loadTranslations = useCallback(async (): Promise<TranslationDetail[]> => {
    if (!id) return [];
    setTranslationsLoading(true);
    try {
      const resp = await fetch(`${API_URL}/api/videos/${id}/translations`, { cache: 'no-store' });
      const json = await resp.json();
      if (!resp.ok) {
        setTranslateStatus(json.error || 'Failed to load translations');
        setTranslateTone('bad');
        setTranslations([]);
        return [];
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
      return normalizedItems;
    } catch (e: any) {
      setTranslateStatus(e?.message || 'Failed to load translations');
      setTranslateTone('bad');
      setTranslations([]);
      return [];
    } finally {
      setTranslationsLoading(false);
    }
  }, [id]);

  const loadMetadata = async (lang: 'zh' | 'en') => {
    if (!id) return null;
    try {
      const resp = await fetch(`${API_URL}/api/videos/${id}/metadata?lang=${lang}`);
      if (resp.status === 404) {
        if (lang === 'zh') setMetadataZh(null);
        if (lang === 'en') setMetadataEn(null);
        return null;
      }
      const json = await resp.json();
      if (!resp.ok) {
        return null;
      }
      if (lang === 'zh') setMetadataZh(json);
      if (lang === 'en') setMetadataEn(json);
      return json as MetadataDetail;
    } catch (_err) {
      return null;
    }
  };

  const loadAllMetadata = async () => {
    if (!id) return;
    setMetadataLoading(true);
    await Promise.all([loadMetadata('zh'), loadMetadata('en')]);
    setMetadataLoading(false);
  };

  useEffect(() => {
    if (!id) return;
    (async () => {
      setLoading(true);
      try {
        await loadVideo();
      } catch (e: any) {
        setVideo(null);
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
    (async () => {
      try {
        const resp = await fetch(`${API_URL}/api/ui-settings/subtitle_polish`);
        const json = await resp.json();
        if (resp.ok && json.value && typeof json.value.notes === 'string') {
          setPolishNotes(json.value.notes);
        }
      } catch (_err) {
        // ignore load failures
      } finally {
        setPolishSettingsLoaded(true);
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
    if (!polishSettingsLoaded) return;
    if (polishNotesTouched || polishNotes) return;
    if (!polishSeedText) return;
    setPolishNotes(`the subtitles is not well recognized the contents of this video is about:\n\n${polishSeedText}`);
  }, [polishSettingsLoaded, polishNotesTouched, polishNotes, polishSeedText]);

  useEffect(() => {
    if (!polishSettingsLoaded) return;
    const timeout = setTimeout(async () => {
      try {
        await fetch(`${API_URL}/api/ui-settings/subtitle_polish`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ notes: polishNotes }),
        });
      } catch (_err) {
        // ignore save failures
      }
    }, 200);
    return () => clearTimeout(timeout);
  }, [polishNotes, polishSettingsLoaded]);

  useEffect(() => {
    loadTranscription();
    loadSubtitlePolish();
    loadCaption();
    loadKeyframes();
    loadTranslations();
    loadAllMetadata();
  }, [id]);

  useFocusEffect(
    useCallback(() => {
      loadTranscription();
      loadSubtitlePolish();
      loadTranslations();
      return undefined;
    }, [loadTranscription, loadSubtitlePolish, loadTranslations]),
  );

  const openProcessPage = () => {
    if (!video) return;
    router.push({ pathname: '/video/[id]/process', params: { id: String(video.id) } });
  };

  const runTranscription = async (): Promise<boolean> => {
    if (!video || transcribing) return false;
    setTranscribing(true);
    setTranscribeStatus('Transcribing... this can take a few minutes.');
    setTranscribeTone('neutral');
    try {
      const resp = await fetch(`${API_URL}/api/videos/${video.id}/transcribe`, { method: 'POST' });
      const json = await resp.json();
      if (!resp.ok) {
        setTranscribeStatus(json.error || json.details || 'Transcription failed');
        setTranscribeTone('bad');
        return false;
      }
      setTranscription(json);
      if (json.status === 'no_audio') {
        setTranscribeStatus('No audio detected in this video.');
        setTranscribeTone('bad');
        return false;
      }
      setTranscribeStatus('Transcription complete.');
      setTranscribeTone('good');
      return true;
    } catch (e: any) {
      setTranscribeStatus(`Transcription failed: ${e?.message || String(e)}`);
      setTranscribeTone('bad');
      return false;
    } finally {
      setTranscribing(false);
    }
  };

  const ensureTranscription = async (): Promise<boolean> => {
    if (transcription?.status === 'completed') {
      setTranscribeStatus('Transcription already complete.');
      setTranscribeTone('good');
      return true;
    }
    if (transcription?.status === 'no_audio') {
      setTranscribeStatus('No audio detected in this video.');
      setTranscribeTone('bad');
      return false;
    }
    return runTranscription();
  };

  const runTranslations = async (languages: TranslateLang[]): Promise<boolean> => {
    if (!video || translating) return false;
    if (!languages.length) {
      setTranslateStatus('Select at least one language.');
      setTranslateTone('bad');
      return false;
    }
    setTranslating(true);
    setTranslateStatus('Starting translations...');
    setTranslateTone('neutral');
    try {
      for (let i = 0; i < languages.length; i += 1) {
        const lang = languages[i];
        const label = TRANSLATE_LANG_LABELS[lang] || lang;
        setTranslateStatus(`Translating ${label} (${i + 1}/${languages.length})...`);
        const resp = await fetch(`${API_URL}/api/videos/${video.id}/translate`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ language: lang, use_cache: !disableTranslateCache }),
        });
        const json = await resp.json();
        if (!resp.ok) {
          setTranslateStatus(json.error || json.details || `Translation failed for ${label}`);
          setTranslateTone('bad');
          return false;
        }
        await loadTranslations();
      }
      setTranslateStatus('Translations complete.');
      setTranslateTone('good');
      return true;
    } catch (e: any) {
      setTranslateStatus(`Translation failed: ${e?.message || String(e)}`);
      setTranslateTone('bad');
      return false;
    } finally {
      setTranslating(false);
    }
  };

  const ensureTranslationsReady = async (languages: TranslateLang[]): Promise<boolean> => {
    if (!languages.length) {
      setTranslateStatus('Select at least one language.');
      setTranslateTone('bad');
      return false;
    }
    const existing = await loadTranslations();
    const completed = new Set(
      existing.filter((item) => item.status === 'completed').map((item) => item.language_code)
    );
    const pending = languages.filter((lang) => !completed.has(lang));
    if (!pending.length) {
      setTranslateStatus('Translations already complete.');
      setTranslateTone('good');
      return true;
    }
    return runTranslations(pending);
  };

  const transcribeVideo = async () => {
    await runTranscription();
  };

  const translateSubtitles = async () => {
    await runTranslations(selectedTranslateLangs);
  };

  const runPolishSubtitles = async () => {
    if (!video || polishing) return;
    const ready = await ensureTranscription();
    if (!ready) return;
    setPolishing(true);
    setPolishStatus('Polishing subtitles... this can take a few minutes.');
    setPolishTone('neutral');
    try {
      const resp = await fetch(`${API_URL}/api/videos/${video.id}/polish-subtitles`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ notes: polishNotes }),
      });
      const json = await resp.json();
      if (!resp.ok) {
        setPolishStatus(json.error || json.details || 'Subtitle polish failed');
        setPolishTone('bad');
        return;
      }
      setPolishDetail(json);
      await loadTranscription();
      setPolishStatus('Subtitle polish complete.');
      setPolishTone('good');
    } catch (e: any) {
      setPolishStatus(`Subtitle polish failed: ${e?.message || String(e)}`);
      setPolishTone('bad');
    } finally {
      setPolishing(false);
    }
  };

  const openBurnPage = async () => {
    if (!video) return;
    const transcriptionReady = await ensureTranscription();
    if (!transcriptionReady) return;
    const translationsReady = await ensureTranslationsReady(selectedTranslateLangs);
    if (!translationsReady) return;
    router.push({ pathname: '/video/[id]/burn-subtitles', params: { id: String(video.id) } });
  };

  const transcribeStatusStyle =
    transcribeTone === 'good' ? styles.statusGood : transcribeTone === 'bad' ? styles.statusBad : styles.statusNeutral;
  const captionStatusStyle =
    captionTone === 'good' ? styles.statusGood : captionTone === 'bad' ? styles.statusBad : styles.statusNeutral;
  const keyframesStatusStyle =
    keyframesTone === 'good' ? styles.statusGood : keyframesTone === 'bad' ? styles.statusBad : styles.statusNeutral;
  const translateStatusStyle =
    translateTone === 'good' ? styles.statusGood : translateTone === 'bad' ? styles.statusBad : styles.statusNeutral;
  const polishStatusStyle =
    polishTone === 'good' ? styles.statusGood : polishTone === 'bad' ? styles.statusBad : styles.statusNeutral;
  const metadataStatusStyle =
    metadataTone === 'good' ? styles.statusGood : metadataTone === 'bad' ? styles.statusBad : styles.statusNeutral;

  const runCaptionFrames = async (): Promise<boolean> => {
    if (!video || captioning) return false;
    setCaptioning(true);
    setCaptionStatus('Captioning frames... this can take a few minutes.');
    setCaptionTone('neutral');
    try {
      const resp = await fetch(`${API_URL}/api/videos/${video.id}/caption`, { method: 'POST' });
      const json = await resp.json();
      if (!resp.ok) {
        setCaptionStatus(json.error || json.details || 'Captioning failed');
        setCaptionTone('bad');
        return false;
      }
      setCaption(json);
      if (json.status === 'not_configured') {
        setCaptionStatus(json.error || 'Captioner not configured.');
        setCaptionTone('bad');
        return false;
      }
      if (json.status === 'failed') {
        setCaptionStatus(json.error || 'Captioning failed.');
        setCaptionTone('bad');
        return false;
      }
      if (json.status === 'empty') {
        setCaptionStatus('No captions generated for this video.');
        setCaptionTone('bad');
        return false;
      }
      setCaptionStatus('Captioning complete.');
      setCaptionTone('good');
      return true;
    } catch (e: any) {
      setCaptionStatus(`Captioning failed: ${e?.message || String(e)}`);
      setCaptionTone('bad');
      return false;
    } finally {
      setCaptioning(false);
    }
  };

  const ensureCaptionReady = async (): Promise<boolean> => {
    if (caption?.status === 'completed') {
      setCaptionStatus('Captions already complete.');
      setCaptionTone('good');
      return true;
    }
    const keyframesReady = await ensureKeyframesReady();
    if (!keyframesReady) return false;
    return runCaptionFrames();
  };

  const captionFrames = async () => {
    await ensureCaptionReady();
  };

  const ensureMetadataDependencies = async (): Promise<boolean> => {
    const transcriptionReady = await ensureTranscription();
    if (!transcriptionReady) return false;
    const captionReady = await ensureCaptionReady();
    if (!captionReady) return false;
    return true;
  };

  const generateMetadata = async (lang: 'zh' | 'en', options?: { skipDeps?: boolean }) => {
    if (!video || metadataGenerating[lang]) return false;
    if (!options?.skipDeps) {
      const depsReady = await ensureMetadataDependencies();
      if (!depsReady) return false;
    }
    setMetadataGenerating((prev) => ({ ...prev, [lang]: true }));
    setMetadataStatus(
      lang === 'zh' ? 'Generating Chinese social metadata...' : 'Generating English YouTube metadata...'
    );
    setMetadataTone('neutral');
    try {
      const resp = await fetch(`${API_URL}/api/videos/${video.id}/metadata`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ lang, notes: metadataNotes }),
      });
      const json = await resp.json();
      if (!resp.ok) {
        const details = json.details ? `${json.error || 'Metadata generation failed'}: ${json.details}` : null;
        setMetadataStatus(details || json.error || 'Metadata generation failed');
        setMetadataTone('bad');
        return false;
      }
      if (lang === 'zh') setMetadataZh(json);
      if (lang === 'en') setMetadataEn(json);
      setMetadataTab(lang);
      setMetadataStatus('Metadata generated.');
      setMetadataTone('good');
      return true;
    } catch (err: any) {
      setMetadataStatus(err?.message || 'Metadata generation failed');
      setMetadataTone('bad');
      return false;
    } finally {
      setMetadataGenerating((prev) => ({ ...prev, [lang]: false }));
    }
  };

  const generateMetadataAll = async () => {
    if (metadataGeneratingAll || !video) return;
    setMetadataGeneratingAll(true);
    const depsReady = await ensureMetadataDependencies();
    if (!depsReady) {
      setMetadataGeneratingAll(false);
      return;
    }
    await generateMetadata('zh', { skipDeps: true });
    await generateMetadata('en', { skipDeps: true });
    setMetadataGeneratingAll(false);
  };

  const renderMetadataContent = (detail: MetadataDetail | null) => {
    if (!detail) {
      return <Text style={styles.previewEmpty}>No metadata yet for {activeMetadataLabel}. Tap generate.</Text>;
    }
    const data = detail.metadata;
    return (
      <>
        <Text style={styles.sectionMeta}>Status: {detail.status}</Text>
        {data ? (
          <>
            <Text style={styles.metadataTitle}>{data.title}</Text>
            <Text style={styles.metadataLabel}>Brief</Text>
            <Text style={styles.metadataText}>{data.brief_description}</Text>
            <Text style={styles.metadataLabel}>Middle</Text>
            <Text style={styles.metadataText}>{data.middle_description}</Text>
            <Text style={styles.metadataLabel}>Long</Text>
            <Text style={styles.metadataText}>{data.long_description}</Text>
            <Text style={styles.metadataLabel}>Tags</Text>
            <View style={styles.tagRow}>
              {(data.tags || []).map((tag, idx) => (
                <View key={`${tag}-${idx}`} style={styles.tagChip}>
                  <Text style={styles.tagChipText}>{tag}</Text>
                </View>
              ))}
            </View>
            <View style={styles.metadataInlineRow}>
              <View style={styles.metadataInlineItem}>
                <Text style={styles.metadataInlineLabel}>Teaser</Text>
                <Text style={styles.metadataInlineValue}>
                  {data.teaser?.start} → {data.teaser?.end}
                </Text>
              </View>
              <View style={styles.metadataInlineItem}>
                <Text style={styles.metadataInlineLabel}>Cover</Text>
                <Text style={styles.metadataInlineValue}>{data.cover}</Text>
              </View>
            </View>
            <Text style={styles.metadataLabel}>Word list</Text>
            <View style={styles.wordList}>
              {(data.english_words_to_learn || []).map((item, idx) => (
                <View key={`${item.word}-${idx}`} style={styles.wordItem}>
                  <Text style={styles.wordItemTitle}>{item.word}</Text>
                  <Text style={styles.wordItemTime}>
                    {item.timestamp_range?.start} → {item.timestamp_range?.end}
                  </Text>
                </View>
              ))}
            </View>
          </>
        ) : (
          <Text style={styles.previewEmpty}>Metadata payload not available.</Text>
        )}
        {detail.error ? <Text style={styles.previewError}>{detail.error}</Text> : null}
      </>
    );
  };

  const runKeyframes = async (): Promise<boolean> => {
    if (!video || extractingKeyframes) return false;
    setExtractingKeyframes(true);
    setKeyframesStatus('Extracting key frames...');
    setKeyframesTone('neutral');
    try {
      const resp = await fetch(`${API_URL}/api/videos/${video.id}/keyframes`, { method: 'POST' });
      const json = await resp.json();
      if (!resp.ok) {
        setKeyframesStatus(json.error || json.details || 'Keyframe extraction failed');
        setKeyframesTone('bad');
        return false;
      }
      setKeyframes(json);
      setKeyframesStatus('Keyframes ready.');
      setKeyframesTone('good');
      return true;
    } catch (e: any) {
      setKeyframesStatus(`Keyframe extraction failed: ${e?.message || String(e)}`);
      setKeyframesTone('bad');
      return false;
    } finally {
      setExtractingKeyframes(false);
    }
  };

  const ensureKeyframesReady = async (): Promise<boolean> => {
    if (keyframes?.status === 'completed') {
      setKeyframesStatus('Keyframes already ready.');
      setKeyframesTone('good');
      return true;
    }
    return runKeyframes();
  };

  const extractKeyframes = async () => {
    await runKeyframes();
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
          style={[styles.btn, styles.btnAccentPrimary]}
          onPress={openProcessPage}
        >
          <View style={styles.btnContent}>
            <Text style={styles.btnText}>Process pipeline</Text>
          </View>
        </Pressable>

        <Pressable style={[styles.btnSecondary, styles.btnCenter]} onPress={createProxyPreview}>
          <View style={styles.btnContent}>
            <Text style={styles.btnText}>Create preview proxy (fix black iPhone videos)</Text>
          </View>
        </Pressable>
        {proxyStatus ? <Text style={styles.statusNeutral}>{proxyStatus}</Text> : null}

        <View style={styles.mainTabs}>
          {MAIN_TABS.map((tab) => {
            const isActive = activeMainTab === tab;
            return (
              <Pressable
                key={tab}
                style={[styles.mainTab, isActive && styles.mainTabActive]}
                onPress={() => setActiveMainTab(tab)}
              >
                <Text style={[styles.mainTabText, isActive && styles.mainTabTextActive]}>
                  {MAIN_TAB_LABELS[tab]}
                </Text>
              </Pressable>
            );
          })}
        </View>

        {activeMainTab === 'subtitles' ? (
        <View style={styles.groupCard}>
          <View style={styles.groupHeader}>
            <Text style={styles.groupTitle}>Subtitles</Text>
            <Text style={styles.groupHint}>Transcribe → polish → translate → burn subtitles.</Text>
          </View>
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
                {transcriptionLanguages ? (
                  <Text style={styles.sectionMeta}>{transcriptionLanguages}</Text>
                ) : null}
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

          <View style={styles.sectionCard}>
            <Text style={styles.sectionTitle}>Polish subtitles</Text>
            <Text style={styles.sectionMeta}>Use captions + transcription + your notes to refine the subtitles.</Text>
            <TextInput
              style={styles.polishInput}
              value={polishNotes}
              onChangeText={(value) => {
                if (!polishNotesTouched) setPolishNotesTouched(true);
                setPolishNotes(value);
              }}
              placeholder="The subtitles are not well recognized. The contents of this video are about..."
              placeholderTextColor="#94a3b8"
              multiline
              textAlignVertical="top"
            />
            <Pressable
              style={[styles.btnSecondaryAlt, polishing && styles.btnDisabled]}
              onPress={runPolishSubtitles}
              disabled={polishing}
            >
              <View style={styles.btnContent}>
                {polishing && <ActivityIndicator color="white" style={{ marginRight: 8 }} />}
                <Text style={styles.btnText}>{polishing ? 'Polishing...' : 'Polish subtitles'}</Text>
              </View>
            </Pressable>
            {polishStatus ? <Text style={[styles.status, polishStatusStyle]}>{polishStatus}</Text> : null}
          </View>

          <View style={styles.sectionCard}>
            <Text style={styles.sectionTitle}>Polished subtitles preview</Text>
            {polishLoading ? (
              <ActivityIndicator />
            ) : polishDetail ? (
              <>
                <Text style={styles.sectionMeta}>Status: {polishDetail.status}</Text>
                {polishDetail.preview_text ? (
                  <Text style={styles.previewText}>{polishDetail.preview_text}</Text>
                ) : (
                  <Text style={styles.previewEmpty}>No preview available.</Text>
                )}
                {polishDetail.error ? <Text style={styles.previewError}>{polishDetail.error}</Text> : null}
                <Pressable
                  style={styles.previewBtn}
                  onPress={() =>
                    router.push({ pathname: '/video/[id]/transcription', params: { id: String(video.id) } })
                  }
                >
                  <Text style={styles.previewBtnText}>Preview polished subtitles</Text>
                </Pressable>
              </>
            ) : (
              <Text style={styles.previewEmpty}>No polished subtitles yet. Tap Polish subtitles.</Text>
            )}
          </View>

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
                  onPress={() =>
                    router.push({ pathname: '/video/[id]/translations', params: { id: String(video.id) } })
                  }
                >
                  <Text style={styles.previewBtnText}>View translations</Text>
                </Pressable>
              </>
            ) : (
              <Text style={styles.previewEmpty}>No translations yet for {previewLabel}. Tap Translate to generate.</Text>
            )}
          </View>

          {translateStatus ? <Text style={[styles.status, translateStatusStyle]}>{translateStatus}</Text> : null}

          <Pressable style={[styles.btnAccent, styles.btnCenter]} onPress={openBurnPage}>
            <View style={styles.btnContent}>
              <Text style={styles.btnText}>Burn subtitles</Text>
            </View>
          </Pressable>
        </View>
        ) : null}

        {activeMainTab === 'captions' ? (
        <View style={styles.groupCard}>
          <View style={styles.groupHeader}>
            <Text style={styles.groupTitle}>Captions</Text>
            <Text style={styles.groupHint}>Extract key frames → caption frames.</Text>
          </View>
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
        </View>
        ) : null}

        {activeMainTab === 'metadata' ? (
          <>
            <View style={styles.sectionCard}>
              <Text style={styles.sectionTitle}>Metadata generator</Text>
              <Text style={styles.sectionMeta}>
                Use the transcription and keyframe captions to draft metadata for Chinese social platforms and YouTube.
              </Text>
              <TextInput
                style={styles.metadataInput}
                value={metadataNotes}
                onChangeText={setMetadataNotes}
                placeholder="Add optional notes about the video (context, tone, audience, keywords)."
                placeholderTextColor="#94a3b8"
                multiline
                textAlignVertical="top"
              />
              <View style={styles.metaButtonRow}>
                <Pressable
                  style={[styles.btnSecondary, styles.metaButton, metadataGenerating.zh && styles.btnDisabled]}
                  onPress={() => generateMetadata('zh')}
                  disabled={metadataGenerating.zh}
                >
                  <View style={styles.btnContent}>
                    {metadataGenerating.zh && <ActivityIndicator color="white" style={{ marginRight: 8 }} />}
                    <Text style={styles.btnText}>
                      {metadataGenerating.zh ? 'Generating...' : 'Generate Chinese metadata'}
                    </Text>
                  </View>
                </Pressable>
                <Pressable
                  style={[
                    styles.btnSecondaryAlt,
                    styles.metaButton,
                    { marginRight: 0 },
                    metadataGenerating.en && styles.btnDisabled,
                  ]}
                  onPress={() => generateMetadata('en')}
                  disabled={metadataGenerating.en}
                >
                  <View style={styles.btnContent}>
                    {metadataGenerating.en && <ActivityIndicator color="white" style={{ marginRight: 8 }} />}
                    <Text style={styles.btnText}>
                      {metadataGenerating.en ? 'Generating...' : 'Generate English metadata'}
                    </Text>
                  </View>
                </Pressable>
              </View>
              <Pressable
                style={[
                  styles.btnAccent,
                  styles.metaButtonFull,
                  styles.btnCenter,
                  metadataGeneratingAll && styles.btnDisabled,
                ]}
                onPress={generateMetadataAll}
                disabled={metadataGeneratingAll}
              >
                <View style={styles.btnContent}>
                  {metadataGeneratingAll && <ActivityIndicator color="white" style={{ marginRight: 8 }} />}
                  <Text style={styles.btnText}>
                    {metadataGeneratingAll ? 'Generating metadata...' : 'Generate metadata'}
                  </Text>
                </View>
              </Pressable>
              <View style={styles.metadataPreviewHeader}>
                <Text style={styles.sectionTitle}>Metadata preview</Text>
              </View>
              <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.langTabs}>
                {metadataTabs.map((tab) => {
                  const isActive = metadataTab === tab.code;
                  return (
                    <Pressable
                      key={tab.code}
                      style={[styles.langTab, isActive && styles.langTabActive]}
                      onPress={() => setMetadataTab(tab.code)}
                    >
                      <Text style={[styles.langTabText, isActive && styles.langTabTextActive]}>{tab.label}</Text>
                    </Pressable>
                  );
                })}
              </ScrollView>
              {metadataLoading ? <ActivityIndicator /> : renderMetadataContent(activeMetadata)}
            </View>

            {metadataStatus ? (
              <Text style={[styles.status, metadataStatusStyle]}>{metadataStatus}</Text>
            ) : null}
          </>
        ) : null}
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
    backgroundColor: '#1d4ed8',
    paddingVertical: 12,
    paddingHorizontal: 18,
    borderRadius: 12,
    alignSelf: 'flex-start',
  },
  btnAccentPrimary: {
    backgroundColor: '#a855f7',
  },
  btnDisabled: { opacity: 0.6 },
  btnContent: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center' },
  btnText: { color: 'white', fontWeight: '600' },
  btnSecondary: {
    marginTop: 10,
    backgroundColor: '#1d4ed8',
    paddingVertical: 12,
    paddingHorizontal: 18,
    borderRadius: 12,
    alignSelf: 'flex-start',
  },
  btnAccent: {
    marginTop: 10,
    backgroundColor: '#06b6d4',
    paddingVertical: 12,
    paddingHorizontal: 18,
    borderRadius: 12,
    alignSelf: 'center',
  },
  btnCenter: {
    alignSelf: 'center',
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
  langTabActive: { backgroundColor: '#1d4ed8', borderColor: '#1d4ed8' },
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
  langCheckBoxActive: { backgroundColor: '#1d4ed8', borderColor: '#1d4ed8' },
  langCheckMark: { color: 'white', fontSize: 10, fontWeight: '700' },
  langCheckLabel: { fontSize: 12, fontWeight: '600', color: '#0f172a' },
  mainTabs: {
    marginTop: 16,
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  mainTab: {
    paddingHorizontal: 14,
    paddingVertical: 8,
    borderRadius: 999,
    borderWidth: 1,
    borderColor: '#e2e8f0',
    marginRight: 10,
    marginBottom: 8,
    backgroundColor: '#f8fafc',
  },
  mainTabActive: {
    backgroundColor: '#1d4ed8',
    borderColor: '#1d4ed8',
  },
  mainTabText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#0f172a',
  },
  mainTabTextActive: { color: '#f8fafc' },
  sectionCard: {
    marginTop: 16,
    padding: 14,
    borderRadius: 14,
    borderWidth: 1,
    borderColor: '#e2e8f0',
    backgroundColor: 'white',
  },
  groupCard: {
    marginTop: 16,
    padding: 14,
    borderRadius: 16,
    borderWidth: 1,
    borderColor: '#e2e8f0',
    backgroundColor: '#f8fafc',
  },
  groupHeader: { marginBottom: 10 },
  groupTitle: { fontSize: 16, fontWeight: '700', color: '#0f172a' },
  groupHint: { fontSize: 12, color: '#64748b', marginTop: 4 },
  sectionTitle: { fontSize: 14, fontWeight: '700', color: '#0f172a', marginBottom: 6 },
  sectionMeta: { fontSize: 12, color: '#475569', marginBottom: 8 },
  metadataInput: {
    borderWidth: 1,
    borderColor: '#cbd5f5',
    borderRadius: 12,
    padding: 10,
    minHeight: 80,
    fontSize: 12,
    color: '#0f172a',
    backgroundColor: '#f8fafc',
  },
  polishInput: {
    borderWidth: 1,
    borderColor: '#cbd5f5',
    borderRadius: 12,
    padding: 10,
    minHeight: 90,
    fontSize: 12,
    color: '#0f172a',
    backgroundColor: '#f8fafc',
  },
  metaButtonRow: {
    marginTop: 12,
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  metaButton: {
    flexGrow: 1,
    minWidth: 200,
    marginRight: 12,
  },
  metaButtonFull: { marginTop: 10, width: '100%' },
  metadataPreviewHeader: {
    marginTop: 12,
  },
  metadataTitle: {
    fontSize: 16,
    fontWeight: '700',
    color: '#0f172a',
    marginBottom: 8,
  },
  metadataLabel: {
    fontSize: 12,
    fontWeight: '700',
    color: '#0f172a',
    marginTop: 8,
  },
  metadataText: { fontSize: 12, color: '#1e293b', marginTop: 4 },
  tagRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginTop: 6,
  },
  tagChip: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 999,
    backgroundColor: '#e2e8f0',
    marginRight: 6,
    marginBottom: 6,
  },
  tagChipText: { fontSize: 11, fontWeight: '600', color: '#1e293b' },
  metadataInlineRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginTop: 10,
  },
  metadataInlineItem: { marginRight: 16, marginBottom: 6 },
  metadataInlineLabel: { fontSize: 11, color: '#64748b' },
  metadataInlineValue: { fontSize: 12, fontWeight: '600', color: '#0f172a', marginTop: 2 },
  wordList: { marginTop: 6 },
  wordItem: {
    paddingVertical: 6,
    borderBottomWidth: 1,
    borderBottomColor: '#e2e8f0',
  },
  wordItemTitle: { fontSize: 12, fontWeight: '600', color: '#0f172a' },
  wordItemTime: { fontSize: 11, color: '#64748b', marginTop: 2 },
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
