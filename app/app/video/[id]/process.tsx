import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import {
  ActivityIndicator,
  Image,
  Platform,
  Pressable,
  ScrollView,
  StyleSheet,
  Switch,
  Text,
  TextInput,
  View,
} from 'react-native';
import { Stack, useLocalSearchParams } from 'expo-router';
import * as DocumentPicker from 'expo-document-picker';
import * as FileSystem from 'expo-file-system';

const API_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8787';

type StepKey =
  | 'keyframes'
  | 'caption'
  | 'transcribe'
  | 'polish'
  | 'translate'
  | 'burn'
  | 'metadataZh'
  | 'metadataEn';

type StepState = 'idle' | 'working' | 'done' | 'skipped' | 'error';

type BurnSlot = {
  slot: number;
  language: string | null;
};

type BurnLayout = {
  slots?: BurnSlot[];
  heightRatio?: number;
  rows?: number;
  cols?: number;
  liftRatio?: number;
  rubySpacing?: number;
};

type LogoSettings = {
  logoPath?: string | null;
  logoUrl?: string | null;
  heightRatio?: number;
  position?: string;
  bgOpacity?: number;
  bgShape?: string;
  enabled?: boolean;
};

type TranslationDetail = {
  language_code: string;
  status: string;
};

const STEP_ORDER: StepKey[] = [
  'keyframes',
  'caption',
  'transcribe',
  'polish',
  'translate',
  'burn',
  'metadataZh',
  'metadataEn',
];

const STEP_LABELS: Record<StepKey, string> = {
  keyframes: 'Extract key frames',
  caption: 'Caption frames',
  transcribe: 'Transcribe',
  polish: 'Polish subtitles',
  translate: 'Translate',
  burn: 'Burn subtitles',
  metadataZh: 'Generate Chinese metadata',
  metadataEn: 'Generate English metadata',
};

const LANG_LABELS: Record<string, string> = {
  en: 'English',
  ja: 'Japanese',
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

const LOGO_POSITION_LABELS: Record<string, string> = {
  'top-right': 'Top right',
  'top-left': 'Top left',
  'bottom-right': 'Bottom right',
  'bottom-left': 'Bottom left',
  center: 'Center',
};
const LOGO_POSITION_OPTIONS = [
  { value: 'top-right', label: 'Top right' },
  { value: 'top-left', label: 'Top left' },
  { value: 'bottom-right', label: 'Bottom right' },
  { value: 'bottom-left', label: 'Bottom left' },
  { value: 'center', label: 'Center' },
];
const LOGO_BG_SHAPE_LABELS: Record<string, string> = {
  circle: 'Circle',
  square: 'Square',
};
const LOGO_BG_SHAPE_OPTIONS = [
  { value: 'circle', label: 'Circle' },
  { value: 'square', label: 'Square' },
];

const STORAGE_PREFIX = 'lazyedit_process_state';

const defaultStepState = STEP_ORDER.reduce((acc, key) => {
  acc[key] = 'idle';
  return acc;
}, {} as Record<StepKey, StepState>);

const defaultSelections: Record<StepKey, boolean> = {
  transcribe: true,
  polish: false,
  translate: true,
  burn: true,
  keyframes: true,
  caption: true,
  metadataZh: true,
  metadataEn: true,
};

const SliderControl = ({
  label,
  value,
  min,
  max,
  step,
  onChange,
  formatValue,
}: {
  label: string;
  value: number;
  min: number;
  max: number;
  step: number;
  onChange: (value: number) => void;
  formatValue?: (value: number) => string;
}) => {
  const [trackWidth, setTrackWidth] = useState(1);
  const ratio = Math.min(Math.max((value - min) / (max - min), 0), 1);

  const updateFromEvent = (event: any) => {
    const { locationX, offsetX } = event.nativeEvent || {};
    const x = typeof locationX === 'number' ? locationX : offsetX;
    if (typeof x !== 'number') return;
    const nextRatio = Math.min(Math.max(x / trackWidth, 0), 1);
    const raw = min + nextRatio * (max - min);
    const stepped = Math.round(raw / step) * step;
    onChange(Number(stepped.toFixed(2)));
  };

  return (
    <View style={styles.sliderRow}>
      <View style={styles.sliderHeader}>
        <Text style={styles.sliderLabel}>{label}</Text>
        <Text style={styles.sliderValue}>{formatValue ? formatValue(value) : value.toFixed(2)}</Text>
      </View>
      <View
        style={styles.sliderTrack}
        onLayout={(event) => setTrackWidth(event.nativeEvent.layout.width)}
        onStartShouldSetResponder={() => true}
        onResponderMove={updateFromEvent}
        onResponderRelease={updateFromEvent}
        onResponderGrant={updateFromEvent}
      >
        <View style={[styles.sliderFill, { width: `${ratio * 100}%` }]} />
        <View style={[styles.sliderThumb, { left: `${ratio * 100}%` }]} />
      </View>
    </View>
  );
};

const formatPercent = (value?: number, fallback = 0) =>
  `${Math.round((typeof value === 'number' ? value : fallback) * 100)}%`;

const formatLanguages = (codes: string[]) =>
  codes.map((code) => LANG_LABELS[code] || code).join(', ');

type VideoDetail = {
  id: number;
  title: string | null;
  media_url?: string | null;
  preview_media_url?: string | null;
};

const LOG_TABS = ['captions', 'subtitles', 'metadata'] as const;
const LOG_TAB_LABELS: Record<typeof LOG_TABS[number], string> = {
  captions: 'Captions',
  subtitles: 'Subtitles',
  metadata: 'Metadata',
};
const PREVIEW_HEIGHT = 220;

const buildStorageKey = (videoId?: string) => {
  if (typeof window === 'undefined' || !videoId) return null;
  return `${STORAGE_PREFIX}_${videoId}`;
};

const readStoredProcessState = (videoId?: string) => {
  const key = buildStorageKey(videoId);
  if (!key) return null;
  try {
    const raw = window.localStorage.getItem(key);
    if (!raw) return null;
    return JSON.parse(raw);
  } catch (_err) {
    return null;
  }
};

export default function ProcessVideoScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const [selectedSteps, setSelectedSteps] = useState<Record<StepKey, boolean>>(defaultSelections);
  const [stepStatus, setStepStatus] = useState<Record<StepKey, StepState>>(defaultStepState);
  const [stepDetail, setStepDetail] = useState<Record<StepKey, string>>({});
  const [running, setRunning] = useState(false);
  const [message, setMessage] = useState('');
  const [proxyStatus, setProxyStatus] = useState('');
  const [loading, setLoading] = useState(true);
  const [translationLanguages, setTranslationLanguages] = useState<string[]>([]);
  const [burnLayout, setBurnLayout] = useState<BurnLayout | null>(null);
  const [logoSettings, setLogoSettings] = useState<LogoSettings | null>(null);
  const [logoEnabled, setLogoEnabled] = useState(true);
  const [logoPick, setLogoPick] = useState<DocumentPicker.DocumentPickerAsset | null>(null);
  const [logoPickPreviewUrl, setLogoPickPreviewUrl] = useState<string | null>(null);
  const [logoUploading, setLogoUploading] = useState(false);
  const [logoStatus, setLogoStatus] = useState('');
  const [logoTone, setLogoTone] = useState<'neutral' | 'good' | 'bad'>('neutral');
  const [logoHeightInput, setLogoHeightInput] = useState('10');
  const [logoAspectRatio, setLogoAspectRatio] = useState<number | null>(null);
  const [video, setVideo] = useState<VideoDetail | null>(null);
  const [burnPreviewUrl, setBurnPreviewUrl] = useState<string | null>(null);
  const [proxyPreviewUrl, setProxyPreviewUrl] = useState<string | null>(null);
  const [activeLogTab, setActiveLogTab] = useState<typeof LOG_TABS[number]>('captions');
  const processStateRef = useRef({
    stepStatus: defaultStepState,
    stepDetail: {} as Record<StepKey, string>,
    message: '',
    burnPreviewUrl: null as string | null,
    selectedSteps: defaultSelections,
    running: false,
  });
  const syncInFlightRef = useRef(false);

  const persistProcessState = () => {
    const key = buildStorageKey(id);
    if (!key || typeof window === 'undefined') return;
    try {
      window.localStorage.setItem(key, JSON.stringify(processStateRef.current));
    } catch (_err) {
      // ignore
    }
  };

  const updateStoredMessage = (text: string) => {
    setMessage(text);
    processStateRef.current.message = text;
    persistProcessState();
  };

  const updateBurnPreview = (url: string | null) => {
    setBurnPreviewUrl(url);
    processStateRef.current.burnPreviewUrl = url;
    persistProcessState();
  };

  const setRunningState = (value: boolean) => {
    setRunning(value);
    processStateRef.current.running = value;
    persistProcessState();
  };

  const setSelectedStepsState = (value: Record<StepKey, boolean>) => {
    setSelectedSteps(value);
    processStateRef.current.selectedSteps = value;
    persistProcessState();
  };

  const burnSummary = useMemo(() => {
    const layout = burnLayout || {};
    const rows = layout.rows ?? 4;
    const cols = layout.cols ?? 1;
    const heightRatio = formatPercent(layout.heightRatio, 0.5);
    const liftRatio = formatPercent(layout.liftRatio, 0.1);
    const slots = (layout.slots || []).map((slot) => {
      const label = slot.language ? LANG_LABELS[slot.language] || slot.language : 'None';
      return `Slot ${slot.slot}: ${label}`;
    });
    return { rows, cols, heightRatio, liftRatio, slots };
  }, [burnLayout]);

  const logoSummary = useMemo(() => {
    const settings = logoSettings || {};
    const heightRatio = settings.heightRatio ?? 0.1;
    const position = settings.position ?? 'top-right';
    const bgOpacity = typeof settings.bgOpacity === 'number' ? settings.bgOpacity : 0.5;
    const bgShape = settings.bgShape === 'square' ? 'square' : 'circle';
    const heightPercent = formatPercent(heightRatio, 0.1);
    const positionLabel = LOGO_POSITION_LABELS[position] || position;
    const bgLabel = LOGO_BG_SHAPE_LABELS[bgShape] || bgShape;
    const bgPercent = formatPercent(bgOpacity, 0.5);
    const hasLogo = Boolean(settings.logoPath);
    return { heightPercent, positionLabel, bgLabel, bgPercent, hasLogo };
  }, [logoSettings]);

  const logoPreviewUrl = useMemo(() => {
    const url = logoSettings?.logoUrl;
    if (!url) return null;
    return url.startsWith('http') ? url : `${API_URL}${url}`;
  }, [logoSettings?.logoUrl]);

  const previewVideoUrl = useMemo(() => {
    const path = video?.preview_media_url || video?.media_url;
    if (!path) return null;
    if (path.startsWith('http://') || path.startsWith('https://')) return path;
    return `${API_URL}${path}`;
  }, [video]);

  const logoOverlayStyle = useMemo(() => {
    if (!logoSettings?.logoPath) return null;
    const heightRatio = logoSettings.heightRatio ?? 0.1;
    const height = Math.max(16, Math.round(PREVIEW_HEIGHT * heightRatio));
    const width = Math.round(height * (logoAspectRatio || 1));
    const padding = 10;
    const position = logoSettings.position ?? 'top-right';
    const style: Record<string, any> = {
      width,
      height,
    };
    if (position === 'top-left') {
      style.top = padding;
      style.left = padding;
    } else if (position === 'bottom-left') {
      style.bottom = padding;
      style.left = padding;
    } else if (position === 'bottom-right') {
      style.bottom = padding;
      style.right = padding;
    } else if (position === 'center') {
      style.top = '50%';
      style.left = '50%';
      style.transform = [{ translateX: -width / 2 }, { translateY: -height / 2 }];
    } else {
      style.top = padding;
      style.right = padding;
    }
    return style;
  }, [
    logoSettings?.logoPath,
    logoSettings?.heightRatio,
    logoSettings?.position,
    logoAspectRatio,
  ]);

  const logoOverlayBgStyle = useMemo(() => {
    if (!logoOverlayStyle || !logoSettings?.logoPath) return null;
    const bgOpacity = typeof logoSettings.bgOpacity === 'number' ? logoSettings.bgOpacity : 0.5;
    if (bgOpacity <= 0) return null;
    const bgShape = logoSettings.bgShape === 'square' ? 'square' : 'circle';
    const width = Number(logoOverlayStyle.width) || 0;
    const height = Number(logoOverlayStyle.height) || 0;
    if (width <= 0 || height <= 0) return null;
    const diameter = Math.min(width, height);
    const bgWidth = bgShape === 'circle' ? diameter : width;
    const bgHeight = bgShape === 'circle' ? diameter : height;
    return {
      width: bgWidth,
      height: bgHeight,
      borderRadius: bgShape === 'circle' ? bgWidth / 2 : 12,
      backgroundColor: `rgba(255, 255, 255, ${bgOpacity})`,
      left: '50%',
      top: '50%',
      marginLeft: -bgWidth / 2,
      marginTop: -bgHeight / 2,
    };
  }, [logoOverlayStyle, logoSettings?.bgOpacity, logoSettings?.bgShape, logoSettings?.logoPath]);

  const saveLogoSettings = async (next: Partial<LogoSettings>) => {
    const payload: LogoSettings = {
      logoPath: logoSettings?.logoPath ?? null,
      logoUrl: logoSettings?.logoUrl ?? null,
      heightRatio: logoSettings?.heightRatio ?? 0.1,
      position: logoSettings?.position ?? 'top-right',
      bgOpacity: typeof logoSettings?.bgOpacity === 'number' ? logoSettings.bgOpacity : 0.5,
      bgShape: logoSettings?.bgShape ?? 'circle',
      enabled: logoSettings?.enabled ?? logoEnabled,
      ...next,
    };
    setLogoSettings(payload);
    setLogoEnabled(Boolean(payload.enabled));
    try {
      await fetch(`${API_URL}/api/ui-settings/logo_settings`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
    } catch (_err) {
      // ignore
    }
  };

  const pickLogo = async () => {
    const res = await DocumentPicker.getDocumentAsync({
      multiple: false,
      type: ['image/*'],
    });
    if (res.canceled) return;
    setLogoPick(res.assets[0]);
    setLogoStatus('Logo selected. Ready to upload.');
    setLogoTone('neutral');
  };

  const uploadLogo = async () => {
    if (!logoPick || logoUploading) return;
    setLogoUploading(true);
    setLogoStatus('Uploading logo...');
    setLogoTone('neutral');
    try {
      if (Platform.OS === 'web') {
        const file = logoPick as any;
        const form = new FormData();
        form.append('image', (file.file as File) ?? (file as any), logoPick.name || 'logo.png');
        const resp = await fetch(`${API_URL}/upload-logo`, { method: 'POST', body: form as any });
        const json = await resp.json();
        if (!resp.ok) {
          setLogoStatus(`Upload failed: ${json.error || json.message || resp.statusText}`);
          setLogoTone('bad');
          return;
        }
        await saveLogoSettings({
          logoPath: json.file_path || null,
          logoUrl: json.media_url || null,
          enabled: true,
        });
        setLogoStatus('Logo uploaded.');
        setLogoTone('good');
      } else {
        const resp = await FileSystem.uploadAsync(`${API_URL}/upload-logo`, logoPick.uri, {
          fieldName: 'image',
          httpMethod: 'POST',
          uploadType: 'multipart' as any,
          parameters: { filename: logoPick.name || 'logo.png' },
        });
        const json = JSON.parse(resp.body);
        if (resp.status >= 400) {
          setLogoStatus(`Upload failed: ${json.error || json.message || `HTTP ${resp.status}`}`);
          setLogoTone('bad');
          return;
        }
        await saveLogoSettings({
          logoPath: json.file_path || null,
          logoUrl: json.media_url || null,
          enabled: true,
        });
        setLogoStatus('Logo uploaded.');
        setLogoTone('good');
      }
      setLogoPick(null);
    } catch (err: any) {
      setLogoStatus(`Upload failed: ${err?.message || String(err)}`);
      setLogoTone('bad');
    } finally {
      setLogoUploading(false);
    }
  };

  const clearLogo = async () => {
    await saveLogoSettings({ logoPath: null, logoUrl: null, enabled: false });
    setLogoStatus('Logo cleared.');
    setLogoTone('neutral');
  };

  const commitLogoHeight = async () => {
    const raw = logoHeightInput.replace('%', '').trim();
    if (!raw) {
      const ratio = logoSettings?.heightRatio ?? 0.1;
      setLogoHeightInput(String(Math.round(ratio * 100)));
      return;
    }
    const value = Number.parseFloat(raw);
    if (Number.isNaN(value)) {
      const ratio = logoSettings?.heightRatio ?? 0.1;
      setLogoHeightInput(String(Math.round(ratio * 100)));
      return;
    }
    const ratio = Math.min(Math.max(value / 100, 0.02), 0.4);
    await saveLogoSettings({ heightRatio: ratio });
    setLogoHeightInput(String(Math.round(ratio * 100)));
  };

  const updateLogoPosition = async (position: string) => {
    await saveLogoSettings({ position });
  };

  const updateLogoBgShape = async (shape: string) => {
    await saveLogoSettings({ bgShape: shape });
  };

  const updateLogoBgOpacity = async (value: number) => {
    await saveLogoSettings({ bgOpacity: value });
  };

  const updateLogoEnabled = async (value: boolean) => {
    if (!logoSettings?.logoPath) {
      setLogoEnabled(false);
      return;
    }
    await saveLogoSettings({ enabled: value });
  };

  const toneStyle = (tone: 'neutral' | 'good' | 'bad') =>
    tone === 'good' ? styles.statusGood : tone === 'bad' ? styles.statusBad : styles.statusNeutral;

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
      const url = json.media_url
        ? json.media_url.startsWith('http')
          ? json.media_url
          : `${API_URL}${json.media_url}`
        : null;
      setProxyPreviewUrl(url);
      setProxyStatus('Proxy ready.');
    } catch (err: any) {
      setProxyStatus(`Proxy failed: ${err?.message || String(err)}`);
    }
  };

  const refreshBurnPreview = async () => {
    if (!id) return;
    try {
      const resp = await fetch(`${API_URL}/api/videos/${id}/burn-subtitles`);
      if (!resp.ok) return;
      const json = await resp.json();
      if (json?.output_url) {
        updateBurnPreview(`${API_URL}${json.output_url}`);
      }
    } catch (_err) {
      // ignore
    }
  };

  useEffect(() => {
    if (!id) return;
    const stored = readStoredProcessState(id);
    if (stored) {
      const baselineStatus = { ...defaultStepState, ...(stored.stepStatus || {}) };
      const baselineDetail = { ...(stored.stepDetail || {}) };
      const storedSteps = { ...defaultSelections, ...(stored.selectedSteps || {}) };
      const storedRunning = Boolean(stored.running);
      setStepStatus(baselineStatus);
      setStepDetail(baselineDetail);
      setMessage(stored.message || '');
      setBurnPreviewUrl(stored.burnPreviewUrl || null);
      setSelectedSteps(storedSteps);
      setRunning(storedRunning);
      processStateRef.current = {
        stepStatus: baselineStatus,
        stepDetail: baselineDetail,
        message: stored.message || '',
        burnPreviewUrl: stored.burnPreviewUrl || null,
        selectedSteps: storedSteps,
        running: storedRunning,
      };
    }
  }, [id]);

  useEffect(() => {
    if (!id) return;
    (async () => {
      setLoading(true);
      try {
        const [langsResp, layoutResp, logoResp] = await Promise.all([
          fetch(`${API_URL}/api/ui-settings/translation_languages`),
          fetch(`${API_URL}/api/ui-settings/burn_layout`),
          fetch(`${API_URL}/api/ui-settings/logo_settings`),
        ]);
        if (langsResp.ok) {
          const json = await langsResp.json();
          if (Array.isArray(json.value)) {
            setTranslationLanguages(json.value);
          }
        }
        if (layoutResp.ok) {
          const json = await layoutResp.json();
          if (json.value) {
            setBurnLayout(json.value);
          }
        }
        if (logoResp.ok) {
          const json = await logoResp.json();
          if (json.value) {
            const enabledValue =
              typeof json.value.enabled === 'boolean' ? json.value.enabled : Boolean(json.value.logoPath);
            const normalized = {
              ...json.value,
              bgOpacity: typeof json.value.bgOpacity === 'number' ? json.value.bgOpacity : 0.5,
              bgShape: json.value.bgShape === 'square' ? 'square' : 'circle',
              enabled: enabledValue,
            };
            setLogoSettings(normalized);
            setLogoEnabled(Boolean(normalized.enabled));
          }
        }
      } catch (_err) {
        // ignore
      } finally {
        setLoading(false);
      }
    })();
  }, [id]);

  useEffect(() => {
    if (typeof logoSettings?.heightRatio !== 'number') return;
    setLogoHeightInput(String(Math.round(logoSettings.heightRatio * 100)));
  }, [logoSettings?.heightRatio]);

  useEffect(() => {
    if (!logoPreviewUrl) {
      setLogoAspectRatio(null);
      return;
    }
    let cancelled = false;
    Image.getSize(
      logoPreviewUrl,
      (width, height) => {
        if (cancelled || !height) return;
        setLogoAspectRatio(width / height);
      },
      () => {
        if (!cancelled) setLogoAspectRatio(null);
      },
    );
    return () => {
      cancelled = true;
    };
  }, [logoPreviewUrl]);

  useEffect(() => {
    if (!logoSettings?.logoPath) {
      setLogoEnabled(false);
    }
  }, [logoSettings?.logoPath]);

  useEffect(() => {
    if (!logoPick) {
      setLogoPickPreviewUrl(null);
      return;
    }
    if (logoPick.uri) {
      setLogoPickPreviewUrl(logoPick.uri);
      return;
    }
    if (Platform.OS !== 'web' || typeof URL === 'undefined') {
      setLogoPickPreviewUrl(null);
      return;
    }
    const file = (logoPick as any).file;
    if (!file) {
      setLogoPickPreviewUrl(null);
      return;
    }
    const objectUrl = URL.createObjectURL(file as File);
    setLogoPickPreviewUrl(objectUrl);
    return () => {
      URL.revokeObjectURL(objectUrl);
    };
  }, [logoPick]);

  useEffect(() => {
    if (!id) return;
    (async () => {
      try {
        const resp = await fetch(`${API_URL}/api/videos/${id}`);
        if (resp.ok) {
          const json = await resp.json();
          setVideo(json);
        }
      } catch (_err) {
        // ignore
      }
    })();
    refreshBurnPreview();
  }, [id]);

  const slotLanguages = useMemo(() => {
    const slots = burnLayout?.slots || [];
    return slots
      .map((slot) => slot.language)
      .filter((lang): lang is string => Boolean(lang));
  }, [burnLayout]);

  const translationTargetLanguages = useMemo(() => {
    const combined = [...translationLanguages, ...slotLanguages];
    return Array.from(new Set(combined.filter(Boolean)));
  }, [translationLanguages, slotLanguages]);

  const updateStatus = (step: StepKey, status: StepState, detail?: string) => {
    const nextStatus = { ...processStateRef.current.stepStatus, [step]: status };
    processStateRef.current.stepStatus = nextStatus;
    setStepStatus(nextStatus);
    if (detail) {
      const nextDetail = { ...processStateRef.current.stepDetail, [step]: detail };
      processStateRef.current.stepDetail = nextDetail;
      setStepDetail(nextDetail);
    }
    persistProcessState();
  };

  const syncPipelineStatus = useCallback(async () => {
    if (!id || syncInFlightRef.current) return;
    syncInFlightRef.current = true;
    const nextStatus = { ...processStateRef.current.stepStatus };
    const nextDetail = { ...processStateRef.current.stepDetail };
    const runningNow = processStateRef.current.running;
    const needsTranscribe =
      selectedSteps.transcribe ||
      selectedSteps.polish ||
      selectedSteps.translate ||
      selectedSteps.burn ||
      selectedSteps.metadataZh ||
      selectedSteps.metadataEn;
    const needsTranslate = selectedSteps.translate || selectedSteps.burn;
    const needsCaption =
      selectedSteps.caption || selectedSteps.polish || selectedSteps.metadataZh || selectedSteps.metadataEn;

    const mark = (step: StepKey, status: StepState, detail = '') => {
      const current = nextStatus[step];
      if (runningNow) {
        if (current === 'done' && status !== 'done') {
          return;
        }
        if (current === 'error' && status === 'idle') {
          return;
        }
        if (current === 'working' && status === 'idle') {
          return;
        }
      }
      nextStatus[step] = status;
      nextDetail[step] = detail;
    };

    const markIdle = (step: StepKey, needed: boolean) => {
      if (!needed) {
        mark(step, 'skipped', 'Skipped');
        return;
      }
      if (runningNow) {
        mark(step, 'working', 'Queued');
        return;
      }
      mark(step, 'idle', '');
    };

    try {
      try {
        const transcribeResp = await fetch(`${API_URL}/api/videos/${id}/transcription`);
        if (transcribeResp.ok) {
          const json = await transcribeResp.json();
          if (json.status === 'completed') {
            mark('transcribe', 'done', 'Completed');
          } else if (json.status === 'no_audio') {
            mark('transcribe', 'error', 'No audio detected');
          } else if (json.status === 'failed') {
            mark('transcribe', 'error', json.error || 'Failed');
          } else {
            mark('transcribe', 'working', json.status || 'Working');
          }
        } else if (transcribeResp.status === 404) {
          markIdle('transcribe', needsTranscribe);
        }
      } catch (_err) {
        markIdle('transcribe', needsTranscribe);
      }

    if (selectedSteps.polish) {
      try {
        const resp = await fetch(`${API_URL}/api/videos/${id}/polish-subtitles`);
        if (resp.ok) {
          const json = await resp.json();
          if (json.status === 'completed') {
            mark('polish', 'done', 'Completed');
          } else if (json.status === 'failed') {
            mark('polish', 'error', json.error || 'Failed');
          } else {
            mark('polish', 'working', json.status || 'Working');
          }
        } else if (resp.status === 404) {
          markIdle('polish', selectedSteps.polish);
        }
      } catch (_err) {
        markIdle('polish', selectedSteps.polish);
      }
    } else {
      markIdle('polish', false);
    }

    if (!needsTranslate) {
      mark('translate', 'skipped', 'Skipped');
    } else if (!translationTargetLanguages.length) {
      mark('translate', 'skipped', 'No languages selected');
    } else {
      try {
        const resp = await fetch(`${API_URL}/api/videos/${id}/translations`);
        if (resp.ok) {
          const json = await resp.json();
          const items: TranslationDetail[] = json.translations || [];
          const statusByLang = new Map(items.map((item) => [item.language_code, item.status]));
          const failedLangs = translationTargetLanguages.filter((lang) => statusByLang.get(lang) === 'failed');
          const completedCount = translationTargetLanguages.filter(
            (lang) => statusByLang.get(lang) === 'completed',
          ).length;
          const total = translationTargetLanguages.length;
          if (failedLangs.length) {
            mark(
              'translate',
              'error',
              `Failed: ${failedLangs.map((lang) => LANG_LABELS[lang] || lang).join(', ')}`,
            );
          } else if (completedCount >= total && total > 0) {
            mark('translate', 'done', `Completed ${completedCount}/${total}`);
          } else {
            const detail = `Completed ${completedCount}/${total}`;
            if (runningNow) {
              mark('translate', 'working', detail);
            } else if (completedCount > 0) {
              mark('translate', 'working', detail);
            } else {
              mark('translate', 'idle', detail);
            }
          }
        } else if (resp.status === 404) {
          markIdle('translate', needsTranslate);
        }
      } catch (_err) {
        markIdle('translate', needsTranslate);
      }
    }

    if (selectedSteps.burn) {
      try {
        const resp = await fetch(`${API_URL}/api/videos/${id}/burn-subtitles`);
        if (resp.ok) {
          const json = await resp.json();
          if (json.status === 'processing') {
            mark('burn', 'working', 'Rendering');
          } else if (json.status === 'completed') {
            mark('burn', 'done', 'Completed');
            if (json.output_url) {
              updateBurnPreview(`${API_URL}${json.output_url}`);
            }
          } else {
            const errorText = json.error || 'Failed';
            if (errorText.includes('Cancelled')) {
              mark('burn', 'skipped', 'Cancelled');
            } else {
              mark('burn', 'error', errorText);
            }
          }
        } else if (resp.status === 404) {
          markIdle('burn', selectedSteps.burn);
        }
      } catch (_err) {
        markIdle('burn', selectedSteps.burn);
      }
    } else {
      markIdle('burn', false);
    }

    if (selectedSteps.keyframes) {
      try {
        const resp = await fetch(`${API_URL}/api/videos/${id}/keyframes`);
        if (resp.ok) {
          const json = await resp.json();
          if (json.status === 'completed') {
            mark('keyframes', 'done', 'Completed');
          } else if (json.status === 'failed') {
            mark('keyframes', 'error', json.error || 'Failed');
          } else {
            mark('keyframes', 'working', json.status || 'Working');
          }
        } else if (resp.status === 404) {
          markIdle('keyframes', selectedSteps.keyframes);
        }
      } catch (_err) {
        markIdle('keyframes', selectedSteps.keyframes);
      }
    } else {
      markIdle('keyframes', false);
    }

    if (needsCaption) {
      try {
        const resp = await fetch(`${API_URL}/api/videos/${id}/caption`);
        if (resp.ok) {
          const json = await resp.json();
          if (json.status === 'completed') {
            mark('caption', 'done', 'Completed');
          } else if (json.status === 'failed' || json.status === 'not_configured') {
            mark('caption', 'error', json.error || 'Failed');
          } else {
            mark('caption', 'working', json.status || 'Working');
          }
        } else if (resp.status === 404) {
          markIdle('caption', needsCaption);
        }
      } catch (_err) {
        markIdle('caption', needsCaption);
      }
    } else {
      markIdle('caption', false);
    }

    if (selectedSteps.metadataZh) {
      try {
        const resp = await fetch(`${API_URL}/api/videos/${id}/metadata?lang=zh`);
        if (resp.ok) {
          const json = await resp.json();
          if (json.status === 'completed') {
            mark('metadataZh', 'done', 'Completed');
          } else if (json.status === 'failed') {
            mark('metadataZh', 'error', json.error || 'Failed');
          } else {
            mark('metadataZh', 'working', json.status || 'Working');
          }
        } else if (resp.status === 404) {
          markIdle('metadataZh', selectedSteps.metadataZh);
        }
      } catch (_err) {
        markIdle('metadataZh', selectedSteps.metadataZh);
      }
    } else {
      markIdle('metadataZh', false);
    }

    if (selectedSteps.metadataEn) {
      try {
        const resp = await fetch(`${API_URL}/api/videos/${id}/metadata?lang=en`);
        if (resp.ok) {
          const json = await resp.json();
          if (json.status === 'completed') {
            mark('metadataEn', 'done', 'Completed');
          } else if (json.status === 'failed') {
            mark('metadataEn', 'error', json.error || 'Failed');
          } else {
            mark('metadataEn', 'working', json.status || 'Working');
          }
        } else if (resp.status === 404) {
          markIdle('metadataEn', selectedSteps.metadataEn);
        }
      } catch (_err) {
        markIdle('metadataEn', selectedSteps.metadataEn);
      }
    } else {
      markIdle('metadataEn', false);
    }
  } finally {
    processStateRef.current.stepStatus = nextStatus;
    processStateRef.current.stepDetail = nextDetail;
    setStepStatus(nextStatus);
    setStepDetail(nextDetail);
    persistProcessState();

    const hasWorking = Object.values(nextStatus).includes('working');
    if (!runningNow && hasWorking) {
      setRunningState(true);
    }
    const hasError = STEP_ORDER.some(
      (step) => nextStatus[step] === 'error' && (selectedSteps[step] || (step === 'caption' && needsCaption)),
    );
    const pipelineComplete = STEP_ORDER.every((step) => {
      const needed =
        step === 'transcribe'
          ? needsTranscribe
          : step === 'translate'
            ? needsTranslate
            : step === 'caption'
              ? needsCaption
              : step === 'polish'
                ? selectedSteps.polish
              : selectedSteps[step];
      if (!needed) return true;
      return ['done', 'skipped', 'error'].includes(nextStatus[step]);
    });
    if (processStateRef.current.running && pipelineComplete) {
      setRunningState(false);
      updateStoredMessage(hasError ? 'Process finished with errors.' : 'Process complete.');
    }
    syncInFlightRef.current = false;
  }
  }, [id, selectedSteps, translationTargetLanguages]);

  useEffect(() => {
    if (!id) return;
    syncPipelineStatus();
    const interval = setInterval(() => {
      syncPipelineStatus();
    }, 6000);
    return () => clearInterval(interval);
  }, [id, syncPipelineStatus]);

  const logEntries = useMemo(() => {
    return {
      captions: [
        {
          title: 'Key frames',
          status: stepStatus.keyframes,
          detail: stepDetail.keyframes,
        },
        {
          title: 'Captions',
          status: stepStatus.caption,
          detail: stepDetail.caption,
        },
      ],
      subtitles: [
        {
          title: 'Transcribe',
          status: stepStatus.transcribe,
          detail: stepDetail.transcribe,
        },
        {
          title: 'Polish subtitles',
          status: stepStatus.polish,
          detail: stepDetail.polish,
        },
        {
          title: 'Translate',
          status: stepStatus.translate,
          detail:
            stepDetail.translate ||
            (translationTargetLanguages.length
              ? `Languages: ${translationTargetLanguages.join(', ')}`
              : 'No languages selected'),
        },
        {
          title: 'Burn subtitles',
          status: stepStatus.burn,
          detail: stepDetail.burn,
        },
      ],
      metadata: [
        {
          title: 'Chinese metadata',
          status: stepStatus.metadataZh,
          detail: stepDetail.metadataZh,
        },
        {
          title: 'English metadata',
          status: stepStatus.metadataEn,
          detail: stepDetail.metadataEn,
        },
      ],
    };
  }, [stepStatus, stepDetail, translationTargetLanguages]);

  const ensureTranscription = async () => {
    if (!id) return false;
    try {
      const check = await fetch(`${API_URL}/api/videos/${id}/transcription`);
      if (check.ok) {
        const json = await check.json();
        if (json.status === 'completed') {
          updateStatus('transcribe', 'done', 'Already transcribed');
          return true;
        }
        if (json.status === 'no_audio') {
          updateStatus('transcribe', 'error', 'No audio detected');
          return false;
        }
      }
    } catch (_err) {
      // fall through to transcribe
    }

    updateStatus('transcribe', 'working', 'Transcribing audio');
    const resp = await fetch(`${API_URL}/api/videos/${id}/transcribe`, { method: 'POST' });
    const json = await resp.json();
    if (!resp.ok) {
      updateStatus('transcribe', 'error', json.error || json.details || 'Transcription failed');
      return false;
    }
    updateStatus('transcribe', 'done', 'Transcription complete');
    return true;
  };

  const ensureTranslations = async () => {
    if (!id) return true;
    const languages = translationTargetLanguages || [];
    if (!languages.length) {
      updateStatus('translate', 'skipped', 'No languages selected');
      return true;
    }
    updateStatus('translate', 'working', 'Checking translations');
    let existing: TranslationDetail[] = [];
    try {
      const resp = await fetch(`${API_URL}/api/videos/${id}/translations`);
      const json = await resp.json();
      if (resp.ok) {
        existing = json.translations || [];
      }
    } catch (_err) {
      existing = [];
    }
    const completed = new Set(existing.filter((item) => item.status === 'completed').map((item) => item.language_code));
    for (const lang of languages) {
      if (completed.has(lang)) continue;
      updateStatus('translate', 'working', `Translating ${LANG_LABELS[lang] || lang}...`);
      const resp = await fetch(`${API_URL}/api/videos/${id}/translate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ language: lang, use_cache: true }),
      });
      const json = await resp.json();
      if (!resp.ok) {
        updateStatus('translate', 'error', json.error || json.details || `Translation failed for ${lang}`);
        return false;
      }
    }
    updateStatus('translate', 'done', 'Translations ready');
    return true;
  };

  const runBurn = async () => {
    if (!id) return false;
    const layout = burnLayout || {};
    const logoPayload =
      logoEnabled && logoSettings?.logoPath
        ? {
            enabled: true,
            logoPath: logoSettings.logoPath,
            heightRatio: logoSettings.heightRatio ?? 0.1,
            position: logoSettings.position ?? 'top-right',
            bgOpacity: typeof logoSettings.bgOpacity === 'number' ? logoSettings.bgOpacity : 0.5,
            bgShape: logoSettings.bgShape ?? 'circle',
          }
        : null;
    if (logoEnabled && !logoSettings?.logoPath) {
      updateStoredMessage('Upload a logo to burn it.');
    }
    updateStatus('burn', 'working', 'Starting burn');
    const resp = await fetch(`${API_URL}/api/videos/${id}/burn-subtitles`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ layout, ...(logoPayload ? { logo: logoPayload } : {}) }),
    });
    const json = await resp.json();
    if (!resp.ok) {
      updateStatus('burn', 'error', json.error || json.details || 'Burn failed');
      return false;
    }
    updateStatus('burn', 'working', 'Rendering subtitles');
    let done = false;
    while (!done) {
      await new Promise((resolve) => setTimeout(resolve, 2000));
      const statusResp = await fetch(`${API_URL}/api/videos/${id}/burn-subtitles`);
      if (!statusResp.ok) continue;
      const statusJson = await statusResp.json();
      if (statusJson.status === 'processing') {
        continue;
      }
      if (statusJson.status === 'completed') {
        updateStatus('burn', 'done', 'Burn complete');
        if (statusJson.output_url) {
          updateBurnPreview(`${API_URL}${statusJson.output_url}`);
        }
        done = true;
        continue;
      }
      updateStatus('burn', 'error', statusJson.error || 'Burn failed');
      return false;
    }
    return true;
  };

  const runKeyframes = async () => {
    if (!id) return false;
    updateStatus('keyframes', 'working', 'Extracting key frames');
    const resp = await fetch(`${API_URL}/api/videos/${id}/keyframes`, { method: 'POST' });
    const json = await resp.json();
    if (!resp.ok) {
      updateStatus('keyframes', 'error', json.error || json.details || 'Keyframe extraction failed');
      return false;
    }
    updateStatus('keyframes', 'done', 'Key frames ready');
    return true;
  };

  const runCaption = async () => {
    if (!id) return false;
    updateStatus('caption', 'working', 'Captioning frames');
    const resp = await fetch(`${API_URL}/api/videos/${id}/caption`, { method: 'POST' });
    const json = await resp.json();
    if (!resp.ok) {
      updateStatus('caption', 'error', json.error || json.details || 'Captioning failed');
      return false;
    }
    updateStatus('caption', 'done', 'Captions ready');
    return true;
  };

  const runMetadata = async (lang: 'zh' | 'en', step: StepKey) => {
    if (!id) return false;
    updateStatus(step, 'working', `Generating ${lang.toUpperCase()} metadata`);
    const resp = await fetch(`${API_URL}/api/videos/${id}/metadata`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ lang, use_cache: true }),
    });
    const json = await resp.json();
    if (!resp.ok) {
      updateStatus(step, 'error', json.error || json.details || 'Metadata generation failed');
      return false;
    }
    updateStatus(step, 'done', 'Metadata ready');
    return true;
  };

  const renderLogContent = () => {
    const items = logEntries[activeLogTab];
    return items.map((item, index) => (
      <View key={`${item.title}-${index}`} style={styles.logRow}>
        <Text style={styles.logLabel}>{item.title}</Text>
        <Text style={styles.logStatus}>{item.status}</Text>
        {item.detail ? <Text style={styles.logDetail}>{item.detail}</Text> : null}
      </View>
    ));
  };

  const stopPipeline = async () => {
    if (!id) return;
    const nextStatus = { ...stepStatus };
    const nextDetail = { ...stepDetail };
    STEP_ORDER.forEach((step) => {
      if (nextStatus[step] === 'working') {
        nextStatus[step] = step === 'burn' ? 'error' : 'idle';
        nextDetail[step] = step === 'burn' ? 'Cancelled' : '';
      }
    });
    processStateRef.current.stepStatus = nextStatus;
    processStateRef.current.stepDetail = nextDetail;
    setStepStatus(nextStatus);
    setStepDetail(nextDetail);
    setRunningState(false);
    updateStoredMessage('Pipeline stopped.');
    try {
      await fetch(`${API_URL}/api/videos/${id}/burn-subtitles`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ cancel: true }),
      });
    } catch (_err) {
      // ignore
    }
    syncPipelineStatus();
  };

  const runPipeline = async () => {
    if (!id || running) return;
    const needsTranscribe =
      selectedSteps.transcribe ||
      selectedSteps.polish ||
      selectedSteps.translate ||
      selectedSteps.burn ||
      selectedSteps.metadataZh ||
      selectedSteps.metadataEn;
    const needsTranslate = selectedSteps.translate || selectedSteps.burn;
    const needsCaption =
      selectedSteps.caption || selectedSteps.polish || selectedSteps.metadataZh || selectedSteps.metadataEn;

    const stepMap: Record<StepKey, string> = {
      keyframes: 'keyframes',
      caption: 'caption',
      transcribe: 'transcribe',
      polish: 'polish',
      translate: 'translate',
      burn: 'burn',
      metadataZh: 'metadata_zh',
      metadataEn: 'metadata_en',
    };
    const steps = STEP_ORDER.filter((step) => selectedSteps[step]).map((step) => stepMap[step]);
    if (!steps.length) {
      updateStoredMessage('Select at least one step to start.');
      return;
    }
    const logoPayload =
      logoEnabled && logoSettings?.logoPath
        ? {
            enabled: true,
            logoPath: logoSettings.logoPath,
            heightRatio: logoSettings.heightRatio ?? 0.1,
            position: logoSettings.position ?? 'top-right',
            bgOpacity: typeof logoSettings.bgOpacity === 'number' ? logoSettings.bgOpacity : 0.5,
            bgShape: logoSettings.bgShape ?? 'circle',
          }
        : null;
    if (logoEnabled && !logoSettings?.logoPath) {
      updateStoredMessage('Upload a logo to burn it.');
    }

    const nextStatus = { ...defaultStepState };
    const nextDetail: Record<StepKey, string> = {};
    const mark = (step: StepKey, status: StepState, detail = '') => {
      nextStatus[step] = status;
      nextDetail[step] = detail;
    };

    mark('keyframes', selectedSteps.keyframes ? 'working' : 'skipped', selectedSteps.keyframes ? 'Queued' : 'Skipped');
    mark('caption', needsCaption ? 'working' : 'skipped', needsCaption ? 'Queued' : 'Skipped');
    mark('transcribe', needsTranscribe ? 'working' : 'skipped', needsTranscribe ? 'Queued' : 'Skipped');
    mark('polish', selectedSteps.polish ? 'working' : 'skipped', selectedSteps.polish ? 'Queued' : 'Skipped');
    if (needsTranslate) {
      const detail = translationTargetLanguages.length
        ? `Languages: ${translationTargetLanguages.map((lang) => LANG_LABELS[lang] || lang).join(', ')}`
        : 'No languages selected';
      mark('translate', translationTargetLanguages.length ? 'working' : 'skipped', detail);
    } else {
      mark('translate', 'skipped', 'Skipped');
    }
    mark('burn', selectedSteps.burn ? 'working' : 'skipped', selectedSteps.burn ? 'Queued' : 'Skipped');
    mark('metadataZh', selectedSteps.metadataZh ? 'working' : 'skipped', selectedSteps.metadataZh ? 'Queued' : 'Skipped');
    mark('metadataEn', selectedSteps.metadataEn ? 'working' : 'skipped', selectedSteps.metadataEn ? 'Queued' : 'Skipped');

    processStateRef.current.stepStatus = nextStatus;
    processStateRef.current.stepDetail = nextDetail;
    setStepStatus(nextStatus);
    setStepDetail(nextDetail);
    setRunningState(true);
    updateStoredMessage('Pipeline started. You can leave this page; progress will update automatically.');

    try {
      const resp = await fetch(`${API_URL}/api/videos/${id}/process`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ steps, async: true, ...(logoPayload ? { logo: logoPayload } : {}) }),
      });
      const json = await resp.json().catch(() => ({}));
      if (!resp.ok) {
        updateStoredMessage(json.error || 'Failed to start pipeline.');
        setRunningState(false);
        return;
      }
    } catch (err: any) {
      updateStoredMessage(err?.message || 'Failed to start pipeline.');
      setRunningState(false);
      return;
    }
    syncPipelineStatus();
  };

  const translationsSummary = translationLanguages.length
    ? formatLanguages(translationLanguages)
    : 'None selected';

  if (loading) {
    return (
      <View style={styles.container}>
        <Stack.Screen options={{ title: 'Process video', headerBackTitle: 'Video' }} />
        <ActivityIndicator />
        <Text style={styles.loadingText}>Loading pipeline settings...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <Stack.Screen options={{ title: 'Process video', headerBackTitle: 'Video' }} />
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.card}>
          <Text style={styles.title}>Pipeline</Text>
          <Text style={styles.meta}>Select the steps to run. Dependencies are handled automatically.</Text>
          <View style={styles.stepList}>
            {STEP_ORDER.map((step) => (
              <View key={step} style={styles.stepRow}>
                <View style={{ flex: 1 }}>
                  <Text style={styles.stepLabel}>{STEP_LABELS[step]}</Text>
                  {stepDetail[step] ? <Text style={styles.stepHint}>{stepDetail[step]}</Text> : null}
                </View>
                <View style={styles.stepStatusWrap}>
                  <Text style={[styles.stepStatus, styles[`step_${stepStatus[step]}`]]}>
                    {stepStatus[step]}
                  </Text>
                </View>
                <Switch
                  value={selectedSteps[step]}
                  onValueChange={(value) =>
                    setSelectedStepsState({
                      ...selectedSteps,
                      [step]: value,
                    })
                  }
                  trackColor={{ false: '#e2e8f0', true: '#2563eb' }}
                  thumbColor={selectedSteps[step] ? '#f8fafc' : '#f1f5f9'}
                />
              </View>
            ))}
          </View>
        </View>

        <View style={styles.card}>
          <Text style={styles.title}>Current settings</Text>
          <Text style={styles.settingLabel}>Translation languages</Text>
          <Text style={styles.settingValue}>{translationsSummary}</Text>
          <Text style={styles.settingLabel}>Burn layout</Text>
          <Text style={styles.settingValue}>
            {burnSummary.rows} rows · {burnSummary.cols} cols · height {burnSummary.heightRatio} · shift {burnSummary.liftRatio}
          </Text>
          {burnSummary.slots.length ? (
            <View style={{ marginTop: 6 }}>
              {burnSummary.slots.map((slot) => (
                <Text key={slot} style={styles.settingHint}>
                  {slot}
                </Text>
              ))}
            </View>
          ) : (
            <Text style={styles.settingHint}>No slots configured.</Text>
          )}
        </View>

        <Pressable style={styles.btnSecondary} onPress={createProxyPreview}>
          <Text style={styles.btnSecondaryText}>Create preview proxy (fix black iPhone videos)</Text>
        </Pressable>
        {proxyStatus ? <Text style={styles.status}>{proxyStatus}</Text> : null}

        <View style={styles.logoCard}>
          <Text style={styles.sectionTitle}>Video logo</Text>
          <Text style={styles.sectionHint}>Upload a logo to overlay across the full video.</Text>

          {logoPickPreviewUrl || logoPreviewUrl ? (
            <Image
              source={{ uri: logoPickPreviewUrl || logoPreviewUrl || '' }}
              style={styles.logoPreview}
              resizeMode="contain"
            />
          ) : (
            <Text style={styles.emptyText}>No logo uploaded yet.</Text>
          )}

          <View style={styles.buttonRow}>
            <Pressable style={styles.btnSecondarySmall} onPress={pickLogo}>
              <Text style={styles.btnSecondarySmallText}>Pick logo</Text>
            </Pressable>
            <Pressable
              style={[styles.btnPrimarySmall, (!logoPick || logoUploading) && styles.btnDisabled]}
              onPress={uploadLogo}
            >
              <Text style={styles.btnPrimarySmallText}>
                {logoUploading ? 'Uploading...' : 'Upload logo'}
              </Text>
            </Pressable>
            {logoSettings?.logoPath ? (
              <Pressable style={styles.btnDangerSmall} onPress={clearLogo}>
                <Text style={styles.btnDangerSmallText}>Remove logo</Text>
              </Pressable>
            ) : null}
          </View>

          {logoStatus ? <Text style={[styles.status, toneStyle(logoTone)]}>{logoStatus}</Text> : null}

          <View style={styles.fieldRow}>
            <View style={{ flex: 1 }}>
              <Text style={styles.settingLabel}>Height (%)</Text>
              <TextInput
                value={logoHeightInput}
                onChangeText={setLogoHeightInput}
                onBlur={commitLogoHeight}
                onSubmitEditing={commitLogoHeight}
                style={styles.input}
                keyboardType="numeric"
              />
            </View>
          </View>

          <Text style={styles.settingLabel}>Position</Text>
          <View style={styles.chipRow}>
            {LOGO_POSITION_OPTIONS.map((option) => (
              <Pressable
                key={option.value}
                style={[
                  styles.chip,
                  (logoSettings?.position ?? 'top-right') === option.value && styles.chipActive,
                ]}
                onPress={() => updateLogoPosition(option.value)}
              >
                <Text
                  style={[
                    styles.chipText,
                    (logoSettings?.position ?? 'top-right') === option.value && styles.chipTextActive,
                  ]}
                >
                  {option.label}
                </Text>
              </Pressable>
              ))}
          </View>

          <Text style={styles.settingLabel}>Background</Text>
          <View style={styles.chipRow}>
            {LOGO_BG_SHAPE_OPTIONS.map((option) => (
              <Pressable
                key={option.value}
                style={[
                  styles.chip,
                  (logoSettings?.bgShape ?? 'circle') === option.value && styles.chipActive,
                ]}
                onPress={() => updateLogoBgShape(option.value)}
              >
                <Text
                  style={[
                    styles.chipText,
                    (logoSettings?.bgShape ?? 'circle') === option.value && styles.chipTextActive,
                  ]}
                >
                  {option.label}
                </Text>
              </Pressable>
            ))}
          </View>
          <SliderControl
            label="Background opacity"
            value={typeof logoSettings?.bgOpacity === 'number' ? logoSettings.bgOpacity : 0.5}
            min={0}
            max={1}
            step={0.05}
            onChange={updateLogoBgOpacity}
            formatValue={(value) => formatPercent(value, 0.5)}
          />

          <View style={styles.settingRow}>
            <View style={{ flex: 1 }}>
              <Text style={styles.settingLabel}>Burn logo (full video)</Text>
              <Text style={styles.settingValue}>
                {logoSummary.hasLogo ? 'Ready' : 'No logo'} · {logoSummary.positionLabel} · height {logoSummary.heightPercent} · bg {logoSummary.bgLabel} {logoSummary.bgPercent}
              </Text>
              {!logoSummary.hasLogo ? (
                <Text style={styles.settingHint}>Upload a logo to enable.</Text>
              ) : null}
            </View>
            <Switch
              value={logoEnabled && logoSummary.hasLogo}
              onValueChange={updateLogoEnabled}
              disabled={!logoSummary.hasLogo}
              trackColor={{ false: '#e2e8f0', true: '#2563eb' }}
              thumbColor={logoEnabled && logoSummary.hasLogo ? '#f8fafc' : '#f1f5f9'}
            />
          </View>
        </View>

        <Pressable style={[styles.btnPrimary, running && styles.btnDisabled]} onPress={runPipeline}>
          <Text style={styles.btnText}>{running ? 'Processing…' : 'Process video'}</Text>
        </Pressable>
        {running ? (
          <Pressable style={styles.btnDanger} onPress={stopPipeline}>
            <Text style={styles.btnDangerText}>Stop pipeline</Text>
          </Pressable>
        ) : null}
        <View style={styles.previewCard}>
          <Text style={styles.sectionTitle}>Burn preview</Text>
          {(burnPreviewUrl || proxyPreviewUrl || previewVideoUrl) ? (
            <View style={styles.videoWrap}>
              {React.createElement('video', {
                src: burnPreviewUrl || proxyPreviewUrl || previewVideoUrl,
                style: { width: '100%', height: '100%', borderRadius: 12, objectFit: 'contain' },
                controls: true,
                muted: true,
                playsInline: true,
                preload: 'metadata',
              })}
              {logoEnabled && logoPreviewUrl && logoOverlayStyle ? (
                <View style={[styles.logoOverlay, logoOverlayStyle]} pointerEvents="none">
                  {logoOverlayBgStyle ? (
                    <View style={[styles.logoOverlayBg, logoOverlayBgStyle]} />
                  ) : null}
                  <Image
                    source={{ uri: logoPreviewUrl }}
                    style={styles.logoOverlayImage}
                    resizeMode="contain"
                  />
                </View>
              ) : null}
            </View>
          ) : (
            <Text style={styles.previewEmpty}>No burn available yet. Run the pipeline or burn subtitles to see a preview.</Text>
          )}
          <View style={styles.logTabRow}>
            {LOG_TABS.map((tab) => (
              <Pressable
                key={tab}
                style={[
                  styles.logTab,
                  activeLogTab === tab && styles.logTabActive,
                ]}
                onPress={() => setActiveLogTab(tab)}
              >
                <Text
                  style={[
                    styles.logTabText,
                    activeLogTab === tab && styles.logTabTextActive,
                  ]}
                >
                  {LOG_TAB_LABELS[tab]}
                </Text>
              </Pressable>
            ))}
          </View>
          <View style={styles.logContent}>{renderLogContent()}</View>
        </View>
        {message ? <Text style={styles.status}>{message}</Text> : null}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16, backgroundColor: '#fbfdff' },
  scrollContent: { paddingBottom: 24 },
  title: { fontSize: 18, fontWeight: '700', color: '#0f172a' },
  sectionTitle: { fontSize: 16, fontWeight: '700', color: '#0f172a' },
  meta: { fontSize: 12, color: '#475569', marginTop: 4 },
  sectionHint: { marginTop: 4, fontSize: 12, color: '#64748b' },
  loadingText: { marginTop: 12, color: '#475569' },
  card: {
    padding: 14,
    borderRadius: 14,
    borderWidth: 1,
    borderColor: '#e2e8f0',
    backgroundColor: 'white',
    marginBottom: 14,
  },
  logoCard: {
    marginTop: 12,
    padding: 14,
    borderRadius: 14,
    borderWidth: 1,
    borderColor: '#e2e8f0',
    backgroundColor: 'white',
  },
  logoPreview: { marginTop: 12, width: '100%', height: 140, borderRadius: 12, backgroundColor: '#f8fafc' },
  emptyText: { marginTop: 12, fontSize: 12, color: '#94a3b8' },
  buttonRow: { marginTop: 12, flexDirection: 'row', flexWrap: 'wrap', gap: 8 },
  stepList: { marginTop: 12 },
  stepRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#e2e8f0',
  },
  stepLabel: { fontSize: 14, fontWeight: '600', color: '#0f172a' },
  stepHint: { fontSize: 11, color: '#64748b', marginTop: 2 },
  stepStatusWrap: { marginHorizontal: 10 },
  stepStatus: { fontSize: 11, textTransform: 'uppercase', fontWeight: '700' },
  step_idle: { color: '#94a3b8' },
  step_working: { color: '#2563eb' },
  step_done: { color: '#16a34a' },
  step_skipped: { color: '#94a3b8' },
  step_error: { color: '#dc2626' },
  settingLabel: { marginTop: 10, fontSize: 12, fontWeight: '700', color: '#0f172a' },
  settingValue: { fontSize: 12, color: '#475569', marginTop: 4 },
  settingHint: { fontSize: 11, color: '#64748b', marginTop: 2 },
  settingRow: { marginTop: 12, flexDirection: 'row', alignItems: 'center', gap: 12 },
  fieldRow: { marginTop: 8 },
  input: {
    marginTop: 6,
    borderWidth: 1,
    borderColor: '#e2e8f0',
    borderRadius: 10,
    paddingVertical: 8,
    paddingHorizontal: 10,
    fontSize: 13,
    color: '#0f172a',
  },
  chipRow: { marginTop: 8, flexDirection: 'row', flexWrap: 'wrap', gap: 8 },
  chip: {
    paddingVertical: 6,
    paddingHorizontal: 12,
    borderRadius: 999,
    borderWidth: 1,
    borderColor: '#e2e8f0',
    backgroundColor: '#f8fafc',
  },
  chipActive: { backgroundColor: '#1d4ed8', borderColor: '#1d4ed8' },
  chipText: { fontSize: 12, fontWeight: '600', color: '#0f172a' },
  chipTextActive: { color: '#f8fafc' },
  btnPrimary: {
    marginTop: 4,
    backgroundColor: '#a855f7',
    paddingVertical: 12,
    borderRadius: 999,
    alignItems: 'center',
  },
  btnPrimarySmall: {
    paddingVertical: 10,
    paddingHorizontal: 14,
    borderRadius: 999,
    backgroundColor: '#2563eb',
  },
  btnPrimarySmallText: { color: '#f8fafc', fontWeight: '700', fontSize: 12 },
  btnSecondary: {
    marginTop: 10,
    paddingVertical: 12,
    borderRadius: 999,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#e2e8f0',
    backgroundColor: '#ffffff',
  },
  btnSecondaryText: { color: '#0f172a', fontWeight: '700' },
  btnSecondarySmall: {
    paddingVertical: 10,
    paddingHorizontal: 14,
    borderRadius: 999,
    borderWidth: 1,
    borderColor: '#e2e8f0',
    backgroundColor: '#ffffff',
  },
  btnSecondarySmallText: { color: '#0f172a', fontWeight: '700', fontSize: 12 },
  btnDanger: {
    marginTop: 8,
    paddingVertical: 12,
    borderRadius: 999,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#fecaca',
    backgroundColor: '#fee2e2',
  },
  btnDangerText: { color: '#b91c1c', fontWeight: '700' },
  btnDangerSmall: {
    paddingVertical: 10,
    paddingHorizontal: 14,
    borderRadius: 999,
    borderWidth: 1,
    borderColor: '#fecaca',
    backgroundColor: '#fee2e2',
  },
  btnDangerSmallText: { color: '#b91c1c', fontWeight: '700', fontSize: 12 },
  btnDisabled: { opacity: 0.6 },
  btnText: { color: '#f8fafc', fontWeight: '700' },
  status: { marginTop: 10, fontSize: 12, color: '#0f172a' },
  statusNeutral: { color: '#475569' },
  statusGood: { color: '#15803d' },
  statusBad: { color: '#b91c1c' },
  previewCard: {
    marginTop: 16,
    padding: 14,
    borderRadius: 14,
    borderWidth: 1,
    borderColor: '#e2e8f0',
    backgroundColor: 'white',
  },
  videoWrap: {
    marginTop: 8,
    borderRadius: 14,
    overflow: 'hidden',
    height: PREVIEW_HEIGHT,
    backgroundColor: '#0f172a',
    position: 'relative',
  },
  logoOverlay: {
    position: 'absolute',
    zIndex: 2,
    alignItems: 'center',
    justifyContent: 'center',
  },
  logoOverlayBg: {
    position: 'absolute',
  },
  logoOverlayImage: {
    position: 'absolute',
    top: 0,
    left: 0,
    width: '100%',
    height: '100%',
  },
  logTabRow: {
    marginTop: 12,
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  logTab: {
    paddingVertical: 6,
    paddingHorizontal: 12,
    borderRadius: 999,
    borderWidth: 1,
    borderColor: '#e2e8f0',
    backgroundColor: '#f8fafc',
    marginRight: 8,
    marginBottom: 8,
  },
  logTabActive: {
    backgroundColor: '#1d4ed8',
    borderColor: '#1d4ed8',
  },
  logTabText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#0f172a',
  },
  logTabTextActive: {
    color: '#f8fafc',
  },
  logContent: {
    marginTop: 10,
  },
  logRow: {
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#e2e8f0',
  },
  logLabel: { fontSize: 13, fontWeight: '700', color: '#0f172a' },
  logStatus: { fontSize: 11, fontWeight: '600', color: '#0f766e', marginTop: 2 },
  logDetail: { fontSize: 11, color: '#475569', marginTop: 4 },
  sliderRow: { marginTop: 12 },
  sliderHeader: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 6 },
  sliderLabel: { fontSize: 12, color: '#0f172a', fontWeight: '600' },
  sliderValue: { fontSize: 12, color: '#475569' },
  sliderTrack: {
    height: 8,
    borderRadius: 999,
    backgroundColor: '#e2e8f0',
    position: 'relative',
    justifyContent: 'center',
  },
  sliderFill: {
    height: 8,
    borderRadius: 999,
    backgroundColor: '#2563eb',
  },
  sliderThumb: {
    position: 'absolute',
    top: -4,
    width: 16,
    height: 16,
    borderRadius: 8,
    backgroundColor: '#2563eb',
    marginLeft: -8,
  },
});
