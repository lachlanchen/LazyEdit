import React, { useEffect, useMemo, useState } from 'react';
import FontAwesome from '@expo/vector-icons/FontAwesome';
import {
  ActivityIndicator,
  Modal,
  Platform,
  Pressable,
  ScrollView,
  StyleSheet,
  Switch,
  Text,
  TextInput,
  View,
} from 'react-native';
import * as DocumentPicker from 'expo-document-picker';
import * as FileSystem from 'expo-file-system';

import { useI18n } from '@/components/I18nProvider';

const API_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8787';

const formatBytes = (bytes?: number | null) => {
  if (bytes === undefined || bytes === null) return 'Unknown size';
  if (bytes === 0) return '0 B';
  const units = ['B', 'KB', 'MB', 'GB'];
  let size = bytes;
  let unitIndex = 0;
  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024;
    unitIndex += 1;
  }
  const decimals = size >= 10 || unitIndex === 0 ? 0 : 1;
  return `${size.toFixed(decimals)} ${units[unitIndex]}`;
};

const DEFAULT_MODEL = 'sora-2';
const normalizeModel = (model?: string) => (model === 'sora-2' || model === 'sora-2-pro' ? model : DEFAULT_MODEL);
const clampSecondsForModel = (seconds: number | null | undefined, model: string) => {
  if (seconds === null || seconds === undefined || Number.isNaN(seconds)) return undefined;
  const max = model === 'sora-2-pro' ? 25 : 12;
  const min = 4;
  return Math.min(Math.max(Math.trunc(seconds), min), max);
};
const parseSeconds = (value: unknown) => {
  if (typeof value === 'number') return value;
  if (typeof value === 'string') {
    const num = parseInt(value, 10);
    return Number.isNaN(num) ? undefined : num;
  }
  return undefined;
};
const sizeForAspectRatio = (aspectRatio?: string) => {
  if (aspectRatio === '9:16') return '720x1280';
  return '1280x720';
};

const DEFAULT_PROMPT_SPEC = {
  autoTitle: false,
  title: 'Epic Vision',
  subject: 'A fictional protagonist in a vast imagined world',
  action: 'They confront a revelation that changes their journey',
  environment: 'An epic, timeless setting (mythic history or distant planet) with sweeping scale',
  camera: 'Cinematic movement that reveals scale and detail',
  lighting: 'Atmospheric, dramatic lighting with soft volumetric depth',
  mood: 'Epic, awe-inspiring, contemplative',
  style: 'Cinematic, richly detailed, timeless tone',
  model: DEFAULT_MODEL,
  aspectRatio: '16:9',
  durationSeconds: '12',
  audioLanguage: 'auto',
  sceneCount: '',
  spokenWords: 'Include a short original philosophical line of dialogue.',
  extraRequirements: 'Let the model invent distinct moments and symbolism while keeping a coherent arc.',
  negative: 'no text, no logos, no gore, no real people',
};

type PromptSpec = typeof DEFAULT_PROMPT_SPEC;
type HistoryKey = keyof typeof DEFAULT_PROMPT_HISTORY;
type HistoryState = typeof DEFAULT_PROMPT_HISTORY;

const SelectControl = ({
  label,
  value,
  options,
  onChange,
  hideIfSingle = false,
}: {
  label: string;
  value: string;
  options: { value: string; label: string }[];
  onChange: (value: string) => void;
  hideIfSingle?: boolean;
}) => {
  const [open, setOpen] = useState(false);
  const current = options.find((option) => option.value === value) || options[0];
  if (hideIfSingle && options.length <= 1) return null;
  return (
    <>
      <Pressable style={styles.selectRow} onPress={() => setOpen(true)}>
        <Text style={styles.selectLabel}>{label}</Text>
        <Text style={styles.selectValue}>{current?.label}</Text>
      </Pressable>
      <Modal transparent animationType="fade" visible={open} onRequestClose={() => setOpen(false)}>
        <Pressable style={styles.modalBackdrop} onPress={() => setOpen(false)}>
          <Pressable style={styles.modalCard} onPress={() => {}}>
            <Text style={styles.modalTitle}>{label}</Text>
            <ScrollView style={{ maxHeight: 260 }}>
              {options.map((option) => {
                const active = option.value === value;
                return (
                  <Pressable
                    key={option.value}
                    style={[styles.modalOption, active && styles.modalOptionActive]}
                    onPress={() => {
                      onChange(option.value);
                      setOpen(false);
                    }}
                  >
                    <Text style={[styles.modalOptionText, active && styles.modalOptionTextActive]}>
                      {option.label}
                    </Text>
                  </Pressable>
                );
              })}
            </ScrollView>
          </Pressable>
        </Pressable>
      </Modal>
    </>
  );
};

const HistorySelect = ({
  label,
  value,
  options,
  onChange,
  hideIfSingle = true,
}: {
  label: string;
  value: string;
  options: { value: string; label: string }[];
  onChange: (value: string) => void;
  hideIfSingle?: boolean;
}) => (
  <SelectControl label={label} value={value} options={options} onChange={onChange} hideIfSingle={hideIfSingle} />
);

const ResetButton = ({ onPress }: { onPress: () => void }) => (
  <Pressable style={styles.resetButton} onPress={onPress} accessibilityLabel="Reset">
    <FontAwesome name="undo" size={14} style={styles.resetButtonIcon} />
  </Pressable>
);

const DEFAULT_PROMPT_HISTORY = {
  title: [],
  subject: [],
  action: [],
  environment: [],
  camera: [],
  lighting: [],
  mood: [],
  style: [],
  model: [],
  audioLanguage: [],
  sceneCount: [],
  spokenWords: [],
  extraRequirements: [],
  negative: [],
};

export default function HomeScreen() {
  const { t } = useI18n();
  const [picked, setPicked] = useState<DocumentPicker.DocumentPickerAsset | null>(null);
  const [status, setStatus] = useState<string>('');
  const [statusTone, setStatusTone] = useState<'neutral' | 'good' | 'bad'>('neutral');
  const [uploading, setUploading] = useState(false);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'upload' | 'generate' | 'remix'>(() => {
    if (Platform.OS !== 'web') return 'upload';
    try {
      const saved = localStorage.getItem('lazyedit:homeTab');
      if (saved === 'upload' || saved === 'generate' || saved === 'remix') return saved;
    } catch (_err) {
      // ignore storage errors
    }
    return 'upload';
  });
  const [remixPicked, setRemixPicked] = useState<DocumentPicker.DocumentPickerAsset | null>(null);
  const [remixStatus, setRemixStatus] = useState('');
  const [remixTone, setRemixTone] = useState<'neutral' | 'good' | 'bad'>('neutral');
  const [remixUploading, setRemixUploading] = useState(false);
  const [remixPreviewUrl, setRemixPreviewUrl] = useState<string | null>(null);
  const [remixNotes, setRemixNotes] = useState('');
  const [promptSpec, setPromptSpec] = useState(DEFAULT_PROMPT_SPEC);
  const [promptResult, setPromptResult] = useState<{
    title?: string;
    prompt?: string;
    negativePrompt?: string;
    size?: string;
    seconds?: number;
  } | null>(null);
  const [promptResultHistory, setPromptResultHistory] = useState<string[]>([]);
  const [specHistoryList, setSpecHistoryList] = useState<string[]>([]);
  const [promptTextHistory, setPromptTextHistory] = useState<string[]>([]);
  const [ideaHistory, setIdeaHistory] = useState<string[]>([]);
  const [selectedSpecHistory, setSelectedSpecHistory] = useState('');
  const [selectedPromptTextHistory, setSelectedPromptTextHistory] = useState('');
  const [selectedPromptResultHistory, setSelectedPromptResultHistory] = useState('');
  const [selectedIdeaHistory, setSelectedIdeaHistory] = useState('');
  const [promptOutput, setPromptOutput] = useState<string>('');
  const [prompting, setPrompting] = useState(false);
  const [promptStatus, setPromptStatus] = useState<string>('');
  const [promptTone, setPromptTone] = useState<'neutral' | 'good' | 'bad'>('neutral');
  const [promptSpecLoaded, setPromptSpecLoaded] = useState(false);
  const [specHistoryLoaded, setSpecHistoryLoaded] = useState(false);
  const [promptTextHistoryLoaded, setPromptTextHistoryLoaded] = useState(false);
  const [promptResultHistoryLoaded, setPromptResultHistoryLoaded] = useState(false);
  const [ideaHistoryLoaded, setIdeaHistoryLoaded] = useState(false);
  const [promptHistory, setPromptHistory] = useState(DEFAULT_PROMPT_HISTORY);
  const [promptHistoryLoaded, setPromptHistoryLoaded] = useState(false);
  const [ideaPrompt, setIdeaPrompt] = useState('');
  const [specGenerating, setSpecGenerating] = useState(false);
  const [specStatus, setSpecStatus] = useState('');
  const [specTone, setSpecTone] = useState<'neutral' | 'good' | 'bad'>('neutral');
  const [generatingVideo, setGeneratingVideo] = useState(false);
  const [videoStatus, setVideoStatus] = useState<string>('');
  const [videoTone, setVideoTone] = useState<'neutral' | 'good' | 'bad'>('neutral');
  const [generatedVideoUrl, setGeneratedVideoUrl] = useState<string | null>(null);
  const [videoModel, setVideoModel] = useState(DEFAULT_MODEL);
  const [videoSize, setVideoSize] = useState(sizeForAspectRatio(DEFAULT_PROMPT_SPEC.aspectRatio));
  const [videoSeconds, setVideoSeconds] = useState(DEFAULT_PROMPT_SPEC.durationSeconds);
  const aspectOptions = useMemo(
    () => [
      { value: '16:9', label: t('aspect_ratio_landscape') },
      { value: '9:16', label: t('aspect_ratio_portrait') },
      { value: 'auto', label: t('aspect_ratio_auto') },
    ],
    [t],
  );
  const sizeOptions = useMemo(
    () => [
      { value: '1280x720', label: '1280x720' },
      { value: '1920x1080', label: '1920x1080' },
      { value: '1024x576', label: '1024x576' },
      { value: '720x1280', label: '720x1280' },
      { value: '1080x1920', label: '1080x1920' },
    ],
    [],
  );
  const modelOptions = useMemo(
    () => [
      { value: 'sora-2', label: t('model_sora2') },
      { value: 'sora-2-pro', label: t('model_sora2_pro') },
    ],
    [t],
  );
  const audioLanguageOptions = useMemo(
    () => [
      { value: 'auto', label: t('audio_language_auto') },
      { value: 'en', label: t('audio_language_en') },
      { value: 'zh', label: t('audio_language_zh') },
      { value: 'ja', label: t('audio_language_ja') },
      { value: 'ko', label: t('audio_language_ko') },
      { value: 'vi', label: t('audio_language_vi') },
      { value: 'ar', label: t('audio_language_ar') },
      { value: 'fr', label: t('audio_language_fr') },
      { value: 'es', label: t('audio_language_es') },
    ],
    [t],
  );

  useEffect(() => {
    if (Platform.OS !== 'web') return;
    if (!picked) {
      setPreviewUrl(null);
      return;
    }
    const file = (picked as any).file as File | undefined;
    if (!file) {
      setPreviewUrl(null);
      return;
    }
    const url = URL.createObjectURL(file);
    setPreviewUrl(url);
    return () => URL.revokeObjectURL(url);
  }, [picked]);

  useEffect(() => {
    if (Platform.OS !== 'web') return;
    if (!remixPicked) {
      setRemixPreviewUrl(null);
      return;
    }
    const file = (remixPicked as any).file as File | undefined;
    if (!file) {
      setRemixPreviewUrl(null);
      return;
    }
    const url = URL.createObjectURL(file);
    setRemixPreviewUrl(url);
    return () => URL.revokeObjectURL(url);
  }, [remixPicked]);

  const fileLabel = useMemo(() => {
    if (!picked) return null;
    return picked.name || 'Untitled video';
  }, [picked]);

  const fileMeta = useMemo(() => {
    if (!picked) return null;
    const size = formatBytes(picked.size);
    const type = picked.mimeType || 'video';
    return `${size} · ${type}`;
  }, [picked]);

  const remixFileLabel = useMemo(() => {
    if (!remixPicked) return null;
    return remixPicked.name || 'Untitled video';
  }, [remixPicked]);

  const remixFileMeta = useMemo(() => {
    if (!remixPicked) return null;
    const size = formatBytes(remixPicked.size);
    const type = remixPicked.mimeType || 'video';
    return `${size} · ${type}`;
  }, [remixPicked]);

  const pick = async () => {
    const res = await DocumentPicker.getDocumentAsync({
      multiple: false,
      type: ['video/*'],
    });
    if (res.canceled) return;
    setPicked(res.assets[0]);
    setStatus('Selected. Ready to upload.');
    setStatusTone('neutral');
  };

  const upload = async () => {
    if (!picked || uploading) return;
    setUploading(true);
    setStatus(t('home_uploading'));
    setStatusTone('neutral');
    try {
      if (Platform.OS === 'web') {
        // Web: the asset is a File object already
        const file = picked as any; // has .file property in web
        const form = new FormData();
        form.append('video', (file.file as File) ?? (file as any), picked.name || 'video.mp4');
        const resp = await fetch(`${API_URL}/upload`, { method: 'POST', body: form as any });
        const json = await resp.json();
        if (!resp.ok) {
          setStatus(`Upload failed: ${json.error || json.message || resp.statusText}`);
          setStatusTone('bad');
          return;
        }
        const label = json.file_path || json.message || 'Upload complete';
        const id = json.video_id ? ` (id: ${json.video_id})` : '';
        setStatus(`Uploaded: ${label}${id}`);
        setStatusTone('good');
      } else {
        // Native: use FileSystem upload for reliability
        const resp = await FileSystem.uploadAsync(`${API_URL}/upload`, picked.uri, {
          fieldName: 'video',
          httpMethod: 'POST',
          uploadType: 'multipart' as any,
          parameters: { filename: picked.name || 'video.mp4' },
        });
        const json = JSON.parse(resp.body);
        if (resp.status >= 400) {
          setStatus(`Upload failed: ${json.error || json.message || `HTTP ${resp.status}`}`);
          setStatusTone('bad');
          return;
        }
        const label = json.file_path || json.message || 'Upload complete';
        const id = json.video_id ? ` (id: ${json.video_id})` : '';
        setStatus(`Uploaded: ${label}${id}`);
        setStatusTone('good');
      }
    } catch (e: any) {
      setStatus(`Upload failed: ${e?.message || String(e)}`);
      setStatusTone('bad');
    } finally {
      setUploading(false);
    }
  };

  const pickRemix = async () => {
    const res = await DocumentPicker.getDocumentAsync({
      multiple: false,
      type: ['video/*'],
    });
    if (res.canceled) return;
    setRemixPicked(res.assets[0]);
    setRemixStatus('Selected. Ready to upload for remix.');
    setRemixTone('neutral');
  };

  const uploadRemix = async () => {
    if (!remixPicked || remixUploading) return;
    setRemixUploading(true);
    setRemixStatus(t('remix_uploading'));
    setRemixTone('neutral');
    const notes = remixNotes.trim();
    try {
      if (Platform.OS === 'web') {
        const file = remixPicked as any;
        const form = new FormData();
        form.append('video', (file.file as File) ?? (file as any), remixPicked.name || 'video.mp4');
        if (notes) {
          form.append('remix_notes', notes);
        }
        const resp = await fetch(`${API_URL}/upload`, { method: 'POST', body: form as any });
        const json = await resp.json();
        if (!resp.ok) {
          setRemixStatus(`Upload failed: ${json.error || json.message || resp.statusText}`);
          setRemixTone('bad');
          return;
        }
        const label = json.file_path || json.message || 'Upload complete';
        const id = json.video_id ? ` (id: ${json.video_id})` : '';
        setRemixStatus(`Uploaded: ${label}${id}. Remix pipeline will run once connected.`);
        setRemixTone('good');
      } else {
        const resp = await FileSystem.uploadAsync(`${API_URL}/upload`, remixPicked.uri, {
          fieldName: 'video',
          httpMethod: 'POST',
          uploadType: 'multipart' as any,
          parameters: {
            filename: remixPicked.name || 'video.mp4',
            ...(notes ? { remix_notes: notes } : {}),
          },
        });
        const json = JSON.parse(resp.body);
        if (resp.status >= 400) {
          setRemixStatus(`Upload failed: ${json.error || json.message || `HTTP ${resp.status}`}`);
          setRemixTone('bad');
          return;
        }
        const label = json.file_path || json.message || 'Upload complete';
        const id = json.video_id ? ` (id: ${json.video_id})` : '';
        setRemixStatus(`Uploaded: ${label}${id}. Remix pipeline will run once connected.`);
        setRemixTone('good');
      }
    } catch (e: any) {
      setRemixStatus(`Upload failed: ${e?.message || String(e)}`);
      setRemixTone('bad');
    } finally {
      setRemixUploading(false);
    }
  };

  const toneStyle = (tone: 'neutral' | 'good' | 'bad') =>
    tone === 'good' ? styles.statusGood : tone === 'bad' ? styles.statusBad : styles.statusNeutral;

  const statusStyle = toneStyle(statusTone);
  const remixStatusStyle = toneStyle(remixTone);

  const updateSpec = (key: keyof typeof DEFAULT_PROMPT_SPEC, value: string | boolean) => {
    setPromptSpec((prev) => ({ ...prev, [key]: value }));
  };

  const resetSpec = (key: keyof typeof DEFAULT_PROMPT_SPEC) => {
    setPromptSpec((prev) => ({ ...prev, [key]: DEFAULT_PROMPT_SPEC[key] }));
  };

  const buildPromptSpecPayload = () => {
    const payload: Record<string, string | number> = {};
    const assign = (key: string, value: string) => {
      if (!value) return;
      const cleaned = value.trim();
      if (!cleaned) return;
      payload[key] = cleaned;
    };
    if (!promptSpec.autoTitle) {
      assign('title', promptSpec.title);
    }
    assign('subject', promptSpec.subject);
    assign('action', promptSpec.action);
    assign('environment', promptSpec.environment);
    assign('camera', promptSpec.camera);
    assign('lighting', promptSpec.lighting);
    assign('mood', promptSpec.mood);
    assign('style', promptSpec.style);
    assign('negative', promptSpec.negative);
    assign('spoken_words', promptSpec.spokenWords);
    assign('extra_requirements', promptSpec.extraRequirements);
    const model = normalizeModel(promptSpec.model);
    payload.model = model;
    const duration = clampSecondsForModel(parseInt(promptSpec.durationSeconds, 10), model);
    if (duration !== undefined) {
      payload.duration_seconds = duration;
    }
    if (promptSpec.audioLanguage) {
      payload.audio_language = promptSpec.audioLanguage;
    }
    const sceneCount = parseInt(promptSpec.sceneCount, 10);
    if (!Number.isNaN(sceneCount)) {
      payload.scene_count = sceneCount;
    }
    if (promptSpec.aspectRatio !== 'auto') {
      payload.aspect_ratio = promptSpec.aspectRatio;
    }
    return payload;
  };

  const loadPromptHistory = async () => {
    try {
      const resp = await fetch(`${API_URL}/api/ui-settings/video_prompt_history`);
      const json = await resp.json();
      if (!resp.ok) return;
      if (json.value) {
        setPromptHistory({ ...DEFAULT_PROMPT_HISTORY, ...json.value });
      }
    } catch (_err) {
      // ignore
    } finally {
      setPromptHistoryLoaded(true);
    }
  };

  const pushHistoryValue = (history: HistoryState, key: HistoryKey, value: string) => {
    const cleaned = value.trim();
    if (!cleaned) return history;
    const current = history[key] || [];
    const next = [cleaned, ...current.filter((item) => item !== cleaned)].slice(0, 20);
    return { ...history, [key]: next };
  };

  const recordHistory = () => {
    let next = { ...promptHistory };
    if (!promptSpec.autoTitle) {
      next = pushHistoryValue(next, 'title', promptSpec.title);
    }
    next = pushHistoryValue(next, 'subject', promptSpec.subject);
    next = pushHistoryValue(next, 'action', promptSpec.action);
    next = pushHistoryValue(next, 'environment', promptSpec.environment);
    next = pushHistoryValue(next, 'camera', promptSpec.camera);
    next = pushHistoryValue(next, 'lighting', promptSpec.lighting);
    next = pushHistoryValue(next, 'mood', promptSpec.mood);
    next = pushHistoryValue(next, 'style', promptSpec.style);
    next = pushHistoryValue(next, 'model', promptSpec.model);
    next = pushHistoryValue(next, 'audioLanguage', promptSpec.audioLanguage);
    next = pushHistoryValue(next, 'sceneCount', promptSpec.sceneCount);
    next = pushHistoryValue(next, 'spokenWords', promptSpec.spokenWords);
    next = pushHistoryValue(next, 'extraRequirements', promptSpec.extraRequirements);
    next = pushHistoryValue(next, 'negative', promptSpec.negative);
    setPromptHistory(next);
    if (!promptHistoryLoaded) return;
    fetch(`${API_URL}/api/ui-settings/video_prompt_history`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(next),
    }).catch(() => {});
  };

  const recordHistoryForSpec = (spec: typeof DEFAULT_PROMPT_SPEC) => {
    let next = { ...promptHistory };
    if (!spec.autoTitle) {
      next = pushHistoryValue(next, 'title', spec.title);
    }
    next = pushHistoryValue(next, 'subject', spec.subject);
    next = pushHistoryValue(next, 'action', spec.action);
    next = pushHistoryValue(next, 'environment', spec.environment);
    next = pushHistoryValue(next, 'camera', spec.camera);
    next = pushHistoryValue(next, 'lighting', spec.lighting);
    next = pushHistoryValue(next, 'mood', spec.mood);
    next = pushHistoryValue(next, 'style', spec.style);
    next = pushHistoryValue(next, 'model', spec.model);
    next = pushHistoryValue(next, 'audioLanguage', spec.audioLanguage);
    next = pushHistoryValue(next, 'sceneCount', spec.sceneCount);
    next = pushHistoryValue(next, 'spokenWords', spec.spokenWords);
    next = pushHistoryValue(next, 'extraRequirements', spec.extraRequirements);
    next = pushHistoryValue(next, 'negative', spec.negative);
    setPromptHistory(next);
    if (!promptHistoryLoaded) return;
    fetch(`${API_URL}/api/ui-settings/video_prompt_history`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(next),
    }).catch(() => {});
  };

  const historyOptions = (items: string[]) => [
    { value: '', label: t('history_select') },
    ...items.map((item) => ({
      value: item,
      label: item.length > 60 ? `${item.slice(0, 60)}…` : item,
    })),
  ];

  const renderHistory = (key: HistoryKey, onPick: (value: string) => void) => {
    const items = promptHistory[key] || [];
    if (!items.length) return null;
    return <HistorySelect label={t('history_label')} value="" options={historyOptions(items)} onChange={onPick} />;
  };

  const specHistoryOptions = useMemo(() => {
    const options: { value: string; label: string }[] = [];
    specHistoryList.forEach((item, idx) => {
      let label = '';
      try {
        const parsed = JSON.parse(item);
        const payload =
          parsed && typeof parsed === 'object' && (parsed as any).response && typeof (parsed as any).response === 'object'
            ? (parsed as any).response
            : parsed;
        if (payload && typeof payload === 'object' && (payload as any).title) {
          label = String((payload as any).title);
        }
      } catch (_err) {
        // ignore parse errors
      }
      if (!label || !label.trim()) {
        label = `Spec ${idx + 1}`;
      }
      if (label.length > 60) label = `${label.slice(0, 60)}…`;
      options.push({ value: item, label });
    });
    if (!options.length) return [{ value: '', label: t('history_select') }];
    return [{ value: '', label: t('history_select') }, ...options];
  }, [specHistoryList, t]);
  const promptTextHistoryOptions = historyOptions(promptTextHistory);
  const ideaHistoryOptions = historyOptions(ideaHistory);
  const promptResultHistoryOptions = useMemo(() => {
    const options: { value: string; label: string }[] = [];
    promptResultHistory.forEach((item, idx) => {
      let label = '';
      try {
        const parsed = JSON.parse(item);
        if (parsed && typeof parsed === 'object' && parsed.title) {
          label = String(parsed.title);
        }
      } catch (_err) {
        // ignore
      }
      if (!label || !label.trim()) {
        label = `Prompt ${idx + 1}`;
      }
      if (label.length > 60) label = `${label.slice(0, 60)}…`;
      options.push({ value: item, label });
    });
    if (!options.length) return [{ value: '', label: t('history_select') }];
    return [{ value: '', label: t('history_select') }, ...options];
  }, [promptResultHistory, t]);

const pushListValue = (list: string[], value: string) => {
  const cleaned = value.trim();
  if (!cleaned) return list;
  const next = [cleaned, ...list.filter((item) => item !== cleaned)];
  return next.slice(0, 20);
};
const mergeHistory = (primary: string[], secondary: string[]) => {
  const seen = new Set<string>();
  const merged: string[] = [];
  [...primary, ...secondary].forEach((item) => {
    if (seen.has(item) || !item?.trim()) return;
    seen.add(item);
    merged.push(item);
  });
  return merged.slice(0, 50);
};

const HISTORY_KEYS = {
  spec: 'video_spec_history',
  promptText: 'video_prompt_text_history',
  promptResult: 'video_prompt_result_history',
  idea: 'video_idea_history',
} as const;

  const loadPromptSettings = async () => {
    try {
      const resp = await fetch(`${API_URL}/api/ui-settings/video_prompt`);
      const json = await resp.json();
      if (!resp.ok) return;
      if (json.value) {
        setPromptSpec({ ...DEFAULT_PROMPT_SPEC, ...json.value });
      }
    } catch (_err) {
      // ignore
    } finally {
      setPromptSpecLoaded(true);
    }
  };

  useEffect(() => {
    loadPromptSettings();
    loadPromptHistory();
    (async () => {
      const loadLocal = (key: string) => {
        if (Platform.OS !== 'web') return [];
        try {
          const raw = localStorage.getItem(`lazyedit:${key}`);
          if (!raw) return [];
          const parsed = JSON.parse(raw);
          return Array.isArray(parsed) ? parsed : [];
        } catch (_err) {
          return [];
        }
      };
      try {
        const resp = await fetch(`${API_URL}/api/ui-settings/video_spec_history`);
        const json = await resp.json();
        const local = loadLocal(HISTORY_KEYS.spec);
        if (resp.ok && Array.isArray(json.value)) {
          setSpecHistoryList(mergeHistory(json.value, local));
        } else {
          setSpecHistoryList(local);
        }
      } catch (_err) {
        // ignore
      } finally {
        setSpecHistoryLoaded(true);
      }
      try {
        const resp = await fetch(`${API_URL}/api/ui-settings/video_prompt_text_history`);
        const json = await resp.json();
        const local = loadLocal(HISTORY_KEYS.promptText);
        if (resp.ok && Array.isArray(json.value)) {
          setPromptTextHistory(mergeHistory(json.value, local));
        } else {
          setPromptTextHistory(local);
        }
      } catch (_err) {
        // ignore
      } finally {
        setPromptTextHistoryLoaded(true);
      }
      try {
        const resp = await fetch(`${API_URL}/api/ui-settings/video_prompt_result_history`);
        const json = await resp.json();
        const local = loadLocal(HISTORY_KEYS.promptResult);
        if (resp.ok && Array.isArray(json.value)) {
          setPromptResultHistory(mergeHistory(json.value, local));
        } else {
          setPromptResultHistory(local);
        }
      } catch (_err) {
        // ignore
      } finally {
        setPromptResultHistoryLoaded(true);
      }
      try {
        const resp = await fetch(`${API_URL}/api/ui-settings/video_idea_history`);
        const json = await resp.json();
        const local = loadLocal(HISTORY_KEYS.idea);
        if (resp.ok && Array.isArray(json.value)) {
          setIdeaHistory(mergeHistory(json.value, local));
        } else {
          setIdeaHistory(local);
        }
      } catch (_err) {
        // ignore
      } finally {
        setIdeaHistoryLoaded(true);
      }
    })();
  }, []);

  const applySpecHistory = (value: string) => {
    if (!value) return;
    setSelectedSpecHistory(value);
    try {
      const parsed = JSON.parse(value);
      const payload = parsed && typeof parsed === 'object' ? ((parsed as any).response && typeof (parsed as any).response === 'object' ? (parsed as any).response : parsed) : null;
      if (payload && typeof payload === 'object') {
        const parsedSeconds = parseSeconds((payload as any).durationSeconds);
        const requestedModel = normalizeModel((payload as any).model);
        let model = normalizeModel(promptSpec.model);
        if (requestedModel === 'sora-2-pro') {
          model = 'sora-2-pro';
        } else if (requestedModel === 'sora-2' && model !== 'sora-2-pro') {
          model = 'sora-2';
        }
        if (parsedSeconds && parsedSeconds > 12) {
          model = 'sora-2-pro';
        }
        const seconds =
          clampSecondsForModel(parsedSeconds, model) ??
          clampSecondsForModel(parseSeconds(promptSpec.durationSeconds), model) ??
          8;
        const aspectRatio = (payload as any).aspectRatio || promptSpec.aspectRatio;
        const merged = { ...DEFAULT_PROMPT_SPEC, ...payload, model, durationSeconds: String(seconds), aspectRatio };
        setPromptSpec(merged);
        setPromptResult(null);
        setVideoModel(model);
        setVideoSize(sizeForAspectRatio(aspectRatio));
        if (seconds) setVideoSeconds(String(seconds));
      }
    } catch (_err) {
      // ignore malformed history
    }
  };

  const applyPromptHistory = (value: string) => {
    if (!value) return;
    setSelectedPromptTextHistory(value);
    setPromptOutput(value);
  };

  const applyPromptResultHistory = (value: string) => {
    if (!value) return;
    setSelectedPromptResultHistory(value);
    try {
      const parsed = JSON.parse(value);
      if (parsed && typeof parsed === 'object') {
        setPromptResult(parsed);
        if (parsed.prompt) setPromptOutput(parsed.prompt);
        if (parsed.size) setVideoSize(parsed.size);
        if (parsed.seconds) setVideoSeconds(String(parsed.seconds));
      }
    } catch (_err) {
      // ignore malformed
    }
  };

  const applyIdeaHistory = (value: string) => {
    if (!value) return;
    setSelectedIdeaHistory(value);
    setIdeaPrompt(value);
  };

  useEffect(() => {
    if (promptResult) return;
    const model = normalizeModel(promptSpec.model);
    const seconds = clampSecondsForModel(parseSeconds(promptSpec.durationSeconds), model) ?? promptSpec.durationSeconds;
    setVideoSize(sizeForAspectRatio(promptSpec.aspectRatio));
    setVideoSeconds(String(seconds));
    setVideoModel(model);
  }, [promptResult, promptSpec]);

  useEffect(() => {
    if (!promptResult) return;
    const model = normalizeModel(promptSpec.model);
    const seconds = clampSecondsForModel(promptResult.seconds, model) ?? parseSeconds(videoSeconds);
    setVideoSize(promptResult.size || sizeForAspectRatio(promptSpec.aspectRatio));
    if (seconds) setVideoSeconds(String(seconds));
    setVideoModel((prev) => (prev ? prev : model));
  }, [promptResult]);

  useEffect(() => {
    if (Platform.OS !== 'web') return;
    try {
      localStorage.setItem('lazyedit:homeTab', activeTab);
    } catch (_err) {
      // ignore storage errors
    }
  }, [activeTab]);

  useEffect(() => {
    if (!promptSpecLoaded) return;
    const timeout = setTimeout(() => {
      fetch(`${API_URL}/api/ui-settings/video_prompt`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(promptSpec),
      }).catch(() => {});
    }, 300);
    return () => clearTimeout(timeout);
  }, [promptSpec, promptSpecLoaded]);

  const generatePrompt = async () => {
    if (prompting) return;
    recordHistory();
    setPrompting(true);
    setPromptStatus(t('generate_prompt_progress'));
    setPromptTone('neutral');
    try {
      const resp = await fetch(`${API_URL}/api/video-prompts`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt_spec: buildPromptSpecPayload() }),
      });
      const json = await resp.json();
      if (!resp.ok) {
        setPromptStatus(`Prompt failed: ${json.error || json.message || resp.statusText}`);
        setPromptTone('bad');
        return;
      }
      const result = json.result || json;
      const promptText = result.prompt || json.prompt || '';
      const selectedModel = normalizeModel(videoModel || promptSpec.model);
      const specSeconds = clampSecondsForModel(parseSeconds(promptSpec.durationSeconds), selectedModel);
      const rawSeconds = parseSeconds(result.seconds ?? json.seconds);
      const seconds = clampSecondsForModel(rawSeconds ?? specSeconds, selectedModel) ?? specSeconds ?? 8;
      const size = result.size || json.size || sizeForAspectRatio(promptSpec.aspectRatio);
      setPromptOutput(promptText);
      setPromptResult({
        title: result.title || json.title,
        prompt: promptText,
        negativePrompt: result.negative_prompt || json.negative_prompt,
        size,
        seconds,
      });
      if (specHistoryLoaded) {
        const { model: _model, ...specOnly } = promptSpec as any;
        const next = pushListValue(specHistoryList, JSON.stringify(specOnly));
        setSpecHistoryList(next);
        fetch(`${API_URL}/api/ui-settings/video_spec_history`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(next),
        }).catch(() => {});
        if (Platform.OS === 'web') {
          try {
            localStorage.setItem(`lazyedit:${HISTORY_KEYS.spec}`, JSON.stringify(next));
          } catch (_err) {
            // ignore
          }
        }
      }
      if (promptTextHistoryLoaded) {
        const nextPromptHistory = pushListValue(promptTextHistory, promptText);
        setPromptTextHistory(nextPromptHistory);
        fetch(`${API_URL}/api/ui-settings/video_prompt_text_history`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(nextPromptHistory),
        }).catch(() => {});
        if (Platform.OS === 'web') {
          try {
            localStorage.setItem(`lazyedit:${HISTORY_KEYS.promptText}`, JSON.stringify(nextPromptHistory));
          } catch (_err) {
            // ignore
          }
        }
      }
      if (promptResultHistoryLoaded) {
        const toStore = JSON.stringify({
          title: result.title || json.title,
          prompt: promptText,
          negativePrompt: result.negative_prompt || json.negative_prompt,
          size,
          seconds,
        });
        const nextPromptResultHistory = pushListValue(promptResultHistory, toStore);
        setPromptResultHistory(nextPromptResultHistory);
        fetch(`${API_URL}/api/ui-settings/video_prompt_result_history`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(nextPromptResultHistory),
        }).catch(() => {});
        if (Platform.OS === 'web') {
          try {
            localStorage.setItem(`lazyedit:${HISTORY_KEYS.promptResult}`, JSON.stringify(nextPromptResultHistory));
          } catch (_err) {
            // ignore
          }
        }
      }
      setVideoSize(size);
      setVideoSeconds(String(seconds));
      setPromptStatus('Prompt ready. You can edit before generating.');
      setPromptTone('good');
    } catch (e: any) {
      setPromptStatus(`Prompt failed: ${e?.message || String(e)}`);
      setPromptTone('bad');
    } finally {
      setPrompting(false);
    }
  };

  const generateSpecs = async () => {
    if (specGenerating) return;
    setSpecGenerating(true);
    setSpecStatus(t('generate_specs_progress'));
    setSpecTone('neutral');
    try {
      const resp = await fetch(`${API_URL}/api/video-specs`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ idea: ideaPrompt }),
      });
      const json = await resp.json();
      if (!resp.ok) {
        setSpecStatus(json.error || json.details || 'Spec generation failed');
        setSpecTone('bad');
        return;
      }
      const spec = json.spec || json.result || {};
      const merged = { ...DEFAULT_PROMPT_SPEC, ...spec };
      setPromptSpec(merged);
      recordHistoryForSpec(merged);
      if (ideaHistoryLoaded) {
        const nextIdeaHistory = pushListValue(ideaHistory, ideaPrompt);
        setIdeaHistory(nextIdeaHistory);
        fetch(`${API_URL}/api/ui-settings/video_idea_history`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(nextIdeaHistory),
        }).catch(() => {});
        if (Platform.OS === 'web') {
          try {
            localStorage.setItem(`lazyedit:${HISTORY_KEYS.idea}`, JSON.stringify(nextIdeaHistory));
          } catch (_err) {
            // ignore
          }
        }
      }
      if (specHistoryLoaded) {
        const { model: _model, ...specOnly } = merged as any;
        const nextSpecHistory = pushListValue(specHistoryList, JSON.stringify(specOnly));
        setSpecHistoryList(nextSpecHistory);
        fetch(`${API_URL}/api/ui-settings/video_spec_history`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(nextSpecHistory),
        }).catch(() => {});
        if (Platform.OS === 'web') {
          try {
            localStorage.setItem(`lazyedit:${HISTORY_KEYS.spec}`, JSON.stringify(nextSpecHistory));
          } catch (_err) {
            // ignore
          }
        }
      }
      setSpecStatus('Specs generated. Review and adjust as needed.');
      setSpecTone('good');
    } catch (e: any) {
      setSpecStatus(e?.message || 'Spec generation failed');
      setSpecTone('bad');
    } finally {
      setSpecGenerating(false);
    }
  };

  const generateVideo = async () => {
    if (generatingVideo) return;
    if (!promptOutput.trim()) {
      setVideoStatus('Add a prompt first.');
      setVideoTone('bad');
      return;
    }
    recordHistory();
    setGeneratingVideo(true);
    setVideoStatus(t('generate_video_progress'));
    setVideoTone('neutral');
    try {
      const spec = buildPromptSpecPayload();
      const title = promptResult?.title || (promptSpec.autoTitle ? 'Generated video' : spec.title || 'Generated video');
      const selectedModel = normalizeModel(promptSpec.model);
      const seconds =
        clampSecondsForModel(parseSeconds(videoSeconds) ?? parseSeconds(promptSpec.durationSeconds), selectedModel) ??
        (selectedModel === 'sora-2-pro' ? 12 : 8);
      const size = videoSize || sizeForAspectRatio(promptSpec.aspectRatio);
      const resp = await fetch(`${API_URL}/api/videos/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt: promptOutput.trim(),
          model: selectedModel,
          size,
          seconds,
          title,
        }),
      });
      const json = await resp.json();
      if (!resp.ok) {
        const details = json.details ? `: ${json.details}` : '';
        setVideoStatus(`Generation failed: ${json.error || json.message || resp.statusText}${details}`);
        setVideoTone('bad');
        return;
      }
      const mediaUrl = json.media_url ? `${API_URL}${json.media_url}` : null;
      setGeneratedVideoUrl(mediaUrl);
      const idLabel = json.video_id ? ` (id: ${json.video_id})` : '';
      setVideoStatus(`Video ready${idLabel}. Added to library.`);
      setVideoTone('good');
    } catch (e: any) {
      setVideoStatus(`Generation failed: ${e?.message || String(e)}`);
      setVideoTone('bad');
    } finally {
      setGeneratingVideo(false);
    }
  };

  return (
    <View style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.content}>
          <Text style={styles.title}>LazyEdit Studio</Text>

          <View style={styles.tabRow}>
            {[
              { key: 'upload', label: t('home_tab_upload') },
              { key: 'generate', label: t('home_tab_generate') },
              { key: 'remix', label: t('home_tab_remix') },
            ].map((tab) => {
              const isActive = activeTab === tab.key;
              return (
                <Pressable
                  key={tab.key}
                  style={[styles.tabButton, isActive && styles.tabButtonActive]}
                  onPress={() => setActiveTab(tab.key as 'upload' | 'generate' | 'remix')}
                >
                  <Text style={[styles.tabButtonText, isActive && styles.tabButtonTextActive]}>{tab.label}</Text>
                </Pressable>
              );
            })}
          </View>

          {activeTab === 'upload' ? (
            <>
              <View style={styles.stepRow}>
                <View style={styles.stepBadge}>
                  <Text style={styles.stepText}>1</Text>
                </View>
                <Text style={styles.stepLabel}>{t('home_step_pick')}</Text>
              </View>

              <Pressable style={styles.btnPrimary} onPress={pick}>
                <Text style={styles.btnText}>
                  {picked ? t('home_pick_another') : t('home_pick_button')}
                </Text>
              </Pressable>

              <View style={styles.card}>
                {picked ? (
                  <>
                    <Text style={styles.cardTitle}>{t('home_selected_video')}</Text>
                    <Text style={styles.fileName} numberOfLines={1}>
                      {fileLabel}
                    </Text>
                    <Text style={styles.fileMeta}>{fileMeta}</Text>
                    {Platform.OS === 'web' && previewUrl ? (
                      <View style={styles.previewBox}>
                        {React.createElement('video', {
                          src: previewUrl,
                          style: { width: '100%', borderRadius: 12, maxHeight: 260 },
                          controls: true,
                          preload: 'metadata',
                        })}
                      </View>
                    ) : (
                      <Text style={styles.previewHint}>{t('home_preview_web')}</Text>
                    )}
                  </>
                ) : (
                  <>
                    <Text style={styles.cardTitle}>{t('home_no_video')}</Text>
                    <Text style={styles.previewHint}>{t('home_pick_hint')}</Text>
                  </>
                )}
              </View>

              <View style={styles.stepRow}>
                <View style={styles.stepBadge}>
                  <Text style={styles.stepText}>2</Text>
                </View>
                <Text style={styles.stepLabel}>{t('home_upload_step')}</Text>
              </View>

              <Pressable
                disabled={!picked || uploading}
                style={[styles.btnSecondary, (!picked || uploading) && styles.btnDisabled]}
                onPress={upload}
              >
                <View style={styles.btnContent}>
                  {uploading && <ActivityIndicator color="white" style={{ marginRight: 8 }} />}
                  <Text style={styles.btnText}>{uploading ? t('home_uploading') : t('home_upload_button')}</Text>
                </View>
              </Pressable>

              {status ? <Text style={[styles.status, statusStyle]}>{status}</Text> : null}
            </>
          ) : null}

          {activeTab === 'generate' ? (
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>{t('generate_title')}</Text>
              <Text style={styles.sectionSubtitle}>{t('generate_subtitle')}</Text>

            <View style={styles.panel}>
              <View style={styles.panelHeader}>
                <Text style={styles.stageBadge}>{t('stage_a_label')}</Text>
                <Text style={styles.panelTitle}>{t('stage_a_title')}</Text>
              </View>
              <Text style={styles.panelHint}>{t('stage_a_hint')}</Text>

              <Text style={styles.fieldLabel}>{t('idea_prompt_label')}</Text>
              <TextInput
                style={styles.textArea}
                value={ideaPrompt}
                onChangeText={setIdeaPrompt}
                placeholder={t('idea_prompt_placeholder')}
                multiline
              />
              {ideaHistoryOptions.length > 1 ? (
                <HistorySelect
                  label={t('history_ai_idea')}
                  value={selectedIdeaHistory}
                  options={ideaHistoryOptions}
                  onChange={applyIdeaHistory}
                />
              ) : null}

              <Pressable style={styles.btnAccent} onPress={generateSpecs} disabled={specGenerating}>
                <View style={styles.btnContent}>
                  {specGenerating && <ActivityIndicator color="white" style={{ marginRight: 8 }} />}
                  <Text style={styles.btnText}>
                    {specGenerating ? t('generate_specs_progress') : t('generate_specs_button')}
                  </Text>
                </View>
              </Pressable>

              {specStatus ? (
                <Text style={[styles.status, toneStyle(specTone)]}>{specStatus}</Text>
              ) : null}
            </View>

            <View style={styles.panel}>
              <View style={styles.panelHeader}>
                <Text style={styles.stageBadge}>{t('stage_b_label')}</Text>
                <Text style={styles.panelTitle}>{t('stage_b_title')}</Text>
              </View>
              <Text style={styles.panelHint}>{t('stage_b_hint')}</Text>
              <HistorySelect
                label={t('history_ai_specs')}
                value={selectedSpecHistory}
                options={specHistoryOptions}
                onChange={applySpecHistory}
                hideIfSingle={false}
              />

              <Text style={styles.fieldLabel}>{t('field_title')}</Text>
              <View style={[styles.inputRow, styles.inputRowTop]}>
                <TextInput
                  style={[styles.input, styles.inputFlex, promptSpec.autoTitle && styles.inputDisabled]}
                  value={promptSpec.title}
                  onChangeText={(v) => updateSpec('title', v)}
                  editable={!promptSpec.autoTitle}
                />
                <ResetButton onPress={() => resetSpec('title')} />
              </View>
              <View style={styles.toggleRow}>
                <View>
                  <Text style={styles.toggleLabel}>{t('field_auto_title')}</Text>
                  <Text style={styles.toggleHint}>{t('field_auto_title_hint')}</Text>
                </View>
                <Switch
                  value={promptSpec.autoTitle}
                  onValueChange={(value) => updateSpec('autoTitle', value)}
                  trackColor={{ false: '#e2e8f0', true: '#2563eb' }}
                  thumbColor={promptSpec.autoTitle ? '#f8fafc' : '#f1f5f9'}
                />
              </View>
              {!promptSpec.autoTitle ? renderHistory('title', (value) => updateSpec('title', value)) : null}

              <Text style={styles.fieldLabel}>{t('field_audio_language')}</Text>
              <View style={styles.inputRow}>
                <View style={styles.inputFlex}>
                  <SelectControl
                    label={t('field_audio_language')}
                    value={promptSpec.audioLanguage}
                    options={audioLanguageOptions}
                    onChange={(value) => updateSpec('audioLanguage', value)}
                  />
                </View>
                <ResetButton onPress={() => resetSpec('audioLanguage')} />
              </View>
              {renderHistory('audioLanguage', (value) => updateSpec('audioLanguage', value))}

              <Text style={styles.fieldLabel}>{t('field_subject')}</Text>
              <View style={[styles.inputRow, styles.inputRowTop]}>
                <TextInput
                  style={[styles.textArea, styles.inputFlex]}
                  value={promptSpec.subject}
                  onChangeText={(v) => updateSpec('subject', v)}
                  multiline
                />
                <ResetButton onPress={() => resetSpec('subject')} />
              </View>
              {renderHistory('subject', (value) => updateSpec('subject', value))}

              <Text style={styles.fieldLabel}>{t('field_action')}</Text>
              <View style={[styles.inputRow, styles.inputRowTop]}>
                <TextInput
                  style={[styles.textArea, styles.inputFlex]}
                  value={promptSpec.action}
                  onChangeText={(v) => updateSpec('action', v)}
                  multiline
                />
                <ResetButton onPress={() => resetSpec('action')} />
              </View>
              {renderHistory('action', (value) => updateSpec('action', value))}

              <Text style={styles.fieldLabel}>{t('field_environment')}</Text>
              <View style={[styles.inputRow, styles.inputRowTop]}>
                <TextInput
                  style={[styles.textArea, styles.inputFlex]}
                  value={promptSpec.environment}
                  onChangeText={(v) => updateSpec('environment', v)}
                  multiline
                />
                <ResetButton onPress={() => resetSpec('environment')} />
              </View>
              {renderHistory('environment', (value) => updateSpec('environment', value))}

              <Text style={styles.fieldLabel}>{t('field_camera')}</Text>
              <View style={styles.inputRow}>
                <TextInput
                  style={[styles.input, styles.inputFlex]}
                  value={promptSpec.camera}
                  onChangeText={(v) => updateSpec('camera', v)}
                />
                <ResetButton onPress={() => resetSpec('camera')} />
              </View>
              {renderHistory('camera', (value) => updateSpec('camera', value))}

              <Text style={styles.fieldLabel}>{t('field_lighting')}</Text>
              <View style={styles.inputRow}>
                <TextInput
                  style={[styles.input, styles.inputFlex]}
                  value={promptSpec.lighting}
                  onChangeText={(v) => updateSpec('lighting', v)}
                />
                <ResetButton onPress={() => resetSpec('lighting')} />
              </View>
              {renderHistory('lighting', (value) => updateSpec('lighting', value))}

              <Text style={styles.fieldLabel}>{t('field_mood')}</Text>
              <View style={styles.inputRow}>
                <TextInput
                  style={[styles.input, styles.inputFlex]}
                  value={promptSpec.mood}
                  onChangeText={(v) => updateSpec('mood', v)}
                />
                <ResetButton onPress={() => resetSpec('mood')} />
              </View>
              {renderHistory('mood', (value) => updateSpec('mood', value))}

              <Text style={styles.fieldLabel}>{t('field_style')}</Text>
              <View style={[styles.inputRow, styles.inputRowTop]}>
                <TextInput
                  style={[styles.textArea, styles.inputFlex]}
                  value={promptSpec.style}
                  onChangeText={(v) => updateSpec('style', v)}
                  multiline
                />
                <ResetButton onPress={() => resetSpec('style')} />
              </View>
              {renderHistory('style', (value) => updateSpec('style', value))}

              <Text style={styles.fieldLabel}>{t('field_spoken_words')}</Text>
              <View style={[styles.inputRow, styles.inputRowTop]}>
                <TextInput
                  style={[styles.textArea, styles.inputFlex]}
                  value={promptSpec.spokenWords}
                  onChangeText={(v) => updateSpec('spokenWords', v)}
                  multiline
                />
                <ResetButton onPress={() => resetSpec('spokenWords')} />
              </View>
              {renderHistory('spokenWords', (value) => updateSpec('spokenWords', value))}

              <Text style={styles.fieldLabel}>{t('field_scene_count')}</Text>
              <View style={styles.inputRow}>
                <TextInput
                  style={[styles.input, styles.inputFlex]}
                  value={promptSpec.sceneCount}
                  onChangeText={(value) => updateSpec('sceneCount', value.replace(/[^\d]/g, ''))}
                  keyboardType="numeric"
                />
                <ResetButton onPress={() => resetSpec('sceneCount')} />
              </View>
              {renderHistory('sceneCount', (value) => updateSpec('sceneCount', value))}

              <Text style={styles.fieldLabel}>{t('field_extra_requirements')}</Text>
              <View style={[styles.inputRow, styles.inputRowTop]}>
                <TextInput
                  style={[styles.textArea, styles.inputFlex]}
                  value={promptSpec.extraRequirements}
                  onChangeText={(v) => updateSpec('extraRequirements', v)}
                  multiline
                />
                <ResetButton onPress={() => resetSpec('extraRequirements')} />
              </View>
              {renderHistory('extraRequirements', (value) => updateSpec('extraRequirements', value))}

              <Text style={styles.fieldLabel}>{t('field_negative_prompt')}</Text>
              <View style={[styles.inputRow, styles.inputRowTop]}>
                <TextInput
                  style={[styles.textArea, styles.inputFlex]}
                  value={promptSpec.negative}
                  onChangeText={(v) => updateSpec('negative', v)}
                  multiline
                />
                <ResetButton onPress={() => resetSpec('negative')} />
              </View>
              {renderHistory('negative', (value) => updateSpec('negative', value))}
            </View>

            <View style={styles.panel}>
              <View style={styles.panelHeader}>
                <Text style={styles.stageBadge}>{t('stage_b_label')}</Text>
                <Text style={styles.panelTitle}>{t('controls_title')}</Text>
              </View>
              <Text style={styles.panelHint}>{t('controls_hint')}</Text>

              <SelectControl
                label={t('field_model')}
                value={promptSpec.model}
                options={modelOptions}
                onChange={(value) => updateSpec('model', normalizeModel(value))}
              />

              <Text style={styles.fieldLabel}>{t('field_aspect_ratio')}</Text>
              <View style={[styles.inputRow, styles.inputRowTop]}>
                <View style={[styles.chipRow, styles.inputFlex]}>
                  {aspectOptions.map((option) => {
                    const isActive = promptSpec.aspectRatio === option.value;
                    return (
                      <Pressable
                        key={option.value}
                        style={[styles.chip, isActive && styles.chipActive]}
                        onPress={() => updateSpec('aspectRatio', option.value)}
                      >
                        <Text style={[styles.chipText, isActive && styles.chipTextActive]}>{option.label}</Text>
                      </Pressable>
                    );
                  })}
                </View>
                <ResetButton onPress={() => resetSpec('aspectRatio')} />
              </View>

              <Text style={styles.fieldLabel}>{t('field_length_seconds')}</Text>
              <View style={styles.inputRow}>
                <TextInput
                  style={[styles.input, styles.inputFlex]}
                  value={promptSpec.durationSeconds}
                  onChangeText={(value) => updateSpec('durationSeconds', value.replace(/[^\d]/g, ''))}
                  keyboardType="numeric"
                />
                <ResetButton onPress={() => resetSpec('durationSeconds')} />
              </View>
            </View>

            <View style={styles.panel}>
              <View style={styles.panelHeader}>
                <Text style={styles.stageBadge}>{t('stage_b_label')}</Text>
                <Text style={styles.panelTitle}>{t('stage_b_generate_title')}</Text>
              </View>
              <Text style={styles.panelHint}>{t('stage_b_generate_hint')}</Text>

              <Pressable style={styles.btnAccent} onPress={generatePrompt} disabled={prompting}>
                <View style={styles.btnContent}>
                  {prompting && <ActivityIndicator color="white" style={{ marginRight: 8 }} />}
                  <Text style={styles.btnText}>
                    {prompting ? t('generate_prompt_progress') : t('generate_prompt_button')}
                  </Text>
                </View>
              </Pressable>
              <Pressable
                style={[styles.btnGhost, { marginTop: 8 }]}
                onPress={() => {
                  if (!promptOutput.trim() || !promptTextHistoryLoaded) return;
                  const nextPromptHistory = pushListValue(promptTextHistory, promptOutput);
                  setPromptTextHistory(nextPromptHistory);
                  fetch(`${API_URL}/api/ui-settings/video_prompt_text_history`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(nextPromptHistory),
                  }).catch(() => {});
                }}
              >
                <Text style={styles.btnGhostText}>{t('save_prompt_history')}</Text>
              </Pressable>

              {promptStatus ? (
                <Text style={[styles.status, toneStyle(promptTone)]}>{promptStatus}</Text>
              ) : null}
            </View>

            <View style={styles.panel}>
              <View style={styles.panelHeader}>
                <Text style={styles.stageBadge}>{t('stage_c_label')}</Text>
                <Text style={styles.panelTitle}>{t('stage_c_title')}</Text>
              </View>
              <Text style={styles.panelHint}>{t('stage_c_hint')}</Text>
              <HistorySelect
                label={t('history_ai_prompt_result')}
                value={selectedPromptResultHistory}
                options={promptResultHistoryOptions}
                onChange={applyPromptResultHistory}
                hideIfSingle={false}
              />

              <SelectControl
                label={t('field_video_size')}
                value={videoSize}
                options={sizeOptions}
                onChange={setVideoSize}
              />

              <SelectControl
                label={t('field_model')}
                value={videoModel}
                options={modelOptions}
                onChange={(value) => setVideoModel(normalizeModel(value))}
              />

              <Text style={styles.fieldLabel}>{t('field_length_seconds')}</Text>
              <View style={styles.inputRow}>
                <TextInput
                  style={[styles.input, styles.inputFlex]}
                  value={videoSeconds}
                  onChangeText={(value) => setVideoSeconds(value.replace(/[^\d]/g, ''))}
                  keyboardType="numeric"
                />
                <ResetButton onPress={() => setVideoSeconds(promptSpec.durationSeconds)} />
              </View>

              <Text style={styles.fieldLabel}>{t('field_generated_prompt')}</Text>
              <TextInput
                style={styles.textAreaLarge}
                value={promptOutput}
                onChangeText={setPromptOutput}
                placeholder={t('prompt_placeholder')}
                multiline
              />
              <HistorySelect
                label={t('history_ai_prompt')}
                value={selectedPromptTextHistory}
                options={promptTextHistoryOptions}
                onChange={applyPromptHistory}
                hideIfSingle={false}
              />

              {promptResult?.model || promptResult?.size || promptResult?.seconds ? (
                <Text style={styles.metaText}>
                  Suggested settings: {promptResult?.model || 'sora-2'} · {promptResult?.size || '1280x720'} ·{' '}
                  {promptResult?.seconds || 8}s
                </Text>
              ) : null}
              {promptResult?.title ? (
                <Text style={styles.metaText}>Suggested title: {promptResult.title}</Text>
              ) : null}
              {promptResult?.negativePrompt ? (
                <Text style={styles.metaText}>Negative: {promptResult.negativePrompt}</Text>
              ) : null}

              <Pressable
                style={[styles.btnSuccess, generatingVideo && styles.btnDisabled]}
                onPress={generateVideo}
                disabled={generatingVideo}
              >
                <View style={styles.btnContent}>
                  {generatingVideo && <ActivityIndicator color="white" style={{ marginRight: 8 }} />}
                  <Text style={styles.btnText}>
                    {generatingVideo ? t('generate_video_progress') : t('generate_video_button')}
                  </Text>
                </View>
              </Pressable>

              {videoStatus ? (
                <Text style={[styles.status, toneStyle(videoTone)]}>{videoStatus}</Text>
              ) : null}

              {generatedVideoUrl ? (
                <View style={styles.card}>
                  <Text style={styles.cardTitle}>{t('generated_video_preview')}</Text>
                  {Platform.OS === 'web' ? (
                    <View style={styles.previewBox}>
                      {React.createElement('video', {
                        src: generatedVideoUrl,
                        style: { width: '100%', borderRadius: 12, maxHeight: 300 },
                        controls: true,
                        preload: 'metadata',
                      })}
                    </View>
                  ) : (
                    <Text style={styles.previewHint}>{t('preview_web_generic')}</Text>
                  )}
                </View>
              ) : null}
            </View>
          </View>
          ) : null}

          {activeTab === 'remix' ? (
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>{t('remix_title')}</Text>
              <Text style={styles.sectionSubtitle}>{t('remix_subtitle')}</Text>

              <View style={styles.stepRow}>
                <View style={styles.stepBadge}>
                  <Text style={styles.stepText}>1</Text>
                </View>
                <Text style={styles.stepLabel}>{t('remix_pick_step')}</Text>
              </View>

              <Pressable style={styles.btnPrimary} onPress={pickRemix}>
                <Text style={styles.btnText}>
                  {remixPicked ? t('remix_pick_another') : t('remix_pick_button')}
                </Text>
              </Pressable>

              <View style={styles.card}>
                {remixPicked ? (
                  <>
                    <Text style={styles.cardTitle}>{t('remix_selected_video')}</Text>
                    <Text style={styles.fileName} numberOfLines={1}>
                      {remixFileLabel}
                    </Text>
                    <Text style={styles.fileMeta}>{remixFileMeta}</Text>
                    {Platform.OS === 'web' && remixPreviewUrl ? (
                      <View style={styles.previewBox}>
                        {React.createElement('video', {
                          src: remixPreviewUrl,
                          style: { width: '100%', borderRadius: 12, maxHeight: 260 },
                          controls: true,
                          preload: 'metadata',
                        })}
                      </View>
                    ) : (
                      <Text style={styles.previewHint}>{t('home_preview_web_remix')}</Text>
                    )}
                  </>
                ) : (
                  <>
                    <Text style={styles.cardTitle}>{t('remix_no_video')}</Text>
                    <Text style={styles.previewHint}>{t('remix_pick_hint')}</Text>
                  </>
                )}
              </View>

              <Text style={styles.fieldLabel}>{t('remix_directions_label')}</Text>
              <TextInput
                style={styles.textArea}
                value={remixNotes}
                onChangeText={setRemixNotes}
                placeholder={t('remix_directions_placeholder')}
                multiline
              />

              <View style={styles.stepRow}>
                <View style={styles.stepBadge}>
                  <Text style={styles.stepText}>2</Text>
                </View>
                <Text style={styles.stepLabel}>{t('remix_upload_step')}</Text>
              </View>

              <Pressable
                disabled={!remixPicked || remixUploading}
                style={[styles.btnSecondary, (!remixPicked || remixUploading) && styles.btnDisabled]}
                onPress={uploadRemix}
              >
                <View style={styles.btnContent}>
                  {remixUploading && <ActivityIndicator color="white" style={{ marginRight: 8 }} />}
                  <Text style={styles.btnText}>
                    {remixUploading ? t('remix_uploading') : t('remix_upload_button')}
                  </Text>
                </View>
              </Pressable>

              {remixStatus ? <Text style={[styles.status, remixStatusStyle]}>{remixStatus}</Text> : null}
            </View>
          ) : null}
        </View>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 24,
    backgroundColor: '#fbfdff',
  },
  scrollContent: {
    paddingBottom: 32,
  },
  content: {
    flex: 1,
    width: '100%',
    maxWidth: 680,
    alignSelf: 'center',
  },
  title: {
    fontSize: 28,
    fontWeight: '700',
    color: '#111827',
  },
  subtitle: {
    fontSize: 16,
    color: '#334155',
  },
  tabRow: {
    marginTop: 16,
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  tabButton: {
    paddingHorizontal: 14,
    paddingVertical: 8,
    borderRadius: 999,
    borderWidth: 1,
    borderColor: '#cbd5f5',
    backgroundColor: 'white',
  },
  tabButtonActive: {
    backgroundColor: '#0f172a',
    borderColor: '#0f172a',
  },
  tabButtonText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#1e293b',
  },
  tabButtonTextActive: {
    color: 'white',
  },
  stepRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 18,
    marginBottom: 8,
  },
  stepBadge: {
    width: 24,
    height: 24,
    borderRadius: 12,
    backgroundColor: '#0f172a',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 8,
  },
  stepText: { color: 'white', fontSize: 12, fontWeight: '700' },
  stepLabel: { color: '#0f172a', fontWeight: '600' },
  btnPrimary: {
    backgroundColor: '#3b82f6',
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderRadius: 12,
    alignSelf: 'flex-start',
  },
  btnSecondary: {
    backgroundColor: '#fc8eac',
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderRadius: 12,
    alignSelf: 'flex-start',
  },
  btnAccent: {
    marginTop: 10,
    backgroundColor: '#0ea5e9',
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderRadius: 12,
    alignSelf: 'flex-start',
  },
  btnSuccess: {
    marginTop: 10,
    backgroundColor: '#16a34a',
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderRadius: 12,
    alignSelf: 'flex-start',
  },
  btnDisabled: {
    opacity: 0.5,
  },
  btnContent: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  btnText: {
    color: 'white',
    fontWeight: '600',
  },
  card: {
    marginTop: 14,
    padding: 16,
    borderRadius: 16,
    backgroundColor: 'white',
    borderWidth: 1,
    borderColor: '#e2e8f0',
  },
  cardTitle: {
    fontSize: 14,
    fontWeight: '700',
    color: '#0f172a',
    marginBottom: 6,
  },
  fileName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#111827',
  },
  fileMeta: {
    marginTop: 2,
    color: '#475569',
    fontSize: 12,
  },
  previewBox: {
    marginTop: 12,
    borderRadius: 14,
    overflow: 'hidden',
    backgroundColor: '#0f172a',
  },
  previewHint: {
    marginTop: 8,
    color: '#475569',
    fontSize: 12,
  },
  section: {
    marginTop: 28,
    paddingTop: 18,
    borderTopWidth: 1,
    borderTopColor: '#e2e8f0',
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: '#0f172a',
  },
  sectionSubtitle: {
    marginTop: 4,
    fontSize: 13,
    color: '#475569',
  },
  fieldLabel: {
    marginTop: 14,
    fontSize: 12,
    fontWeight: '600',
    color: '#0f172a',
  },
  input: {
    marginTop: 8,
    minHeight: 44,
    borderWidth: 1,
    borderColor: '#e2e8f0',
    borderRadius: 12,
    paddingHorizontal: 12,
    paddingVertical: 10,
    backgroundColor: 'white',
    color: '#111827',
  },
  inputDisabled: {
    backgroundColor: '#f1f5f9',
    color: '#94a3b8',
  },
  textArea: {
    marginTop: 8,
    minHeight: 80,
    borderWidth: 1,
    borderColor: '#e2e8f0',
    borderRadius: 12,
    padding: 12,
    backgroundColor: 'white',
    color: '#111827',
    textAlignVertical: 'top',
  },
  textAreaLarge: {
    marginTop: 8,
    minHeight: 140,
    borderWidth: 1,
    borderColor: '#e2e8f0',
    borderRadius: 12,
    padding: 12,
    backgroundColor: 'white',
    color: '#111827',
    textAlignVertical: 'top',
  },
  metaText: {
    marginTop: 8,
    fontSize: 12,
    color: '#475569',
  },
  panel: {
    marginTop: 16,
    padding: 16,
    borderRadius: 16,
    borderWidth: 1,
    borderColor: '#e2e8f0',
    backgroundColor: '#f8fafc',
  },
  panelTitle: {
    fontSize: 14,
    fontWeight: '700',
    color: '#0f172a',
  },
  panelHint: {
    marginTop: 4,
    fontSize: 12,
    color: '#64748b',
  },
  panelHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  stageBadge: {
    fontSize: 11,
    fontWeight: '700',
    color: '#0f172a',
    backgroundColor: '#e2e8f0',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 999,
  },
  inputRow: {
    marginTop: 8,
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
  },
  inputRowTop: {
    alignItems: 'flex-start',
  },
  inputFlex: {
    flex: 1,
  },
  selectRow: {
    paddingVertical: 10,
    paddingHorizontal: 12,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#e2e8f0',
    backgroundColor: 'white',
  },
  selectLabel: {
    fontSize: 11,
    fontWeight: '600',
    color: '#64748b',
  },
  selectValue: {
    fontSize: 12,
    color: '#0f172a',
    marginTop: 4,
  },
  modalBackdrop: {
    flex: 1,
    backgroundColor: 'rgba(15, 23, 42, 0.45)',
    justifyContent: 'center',
    padding: 24,
  },
  modalCard: {
    borderRadius: 16,
    backgroundColor: '#fff',
    padding: 16,
  },
  modalTitle: {
    fontSize: 14,
    fontWeight: '700',
    color: '#0f172a',
    marginBottom: 8,
  },
  modalOption: {
    paddingVertical: 10,
    paddingHorizontal: 12,
    borderRadius: 10,
  },
  modalOptionActive: {
    backgroundColor: '#0f172a',
  },
  modalOptionText: {
    fontSize: 13,
    color: '#0f172a',
  },
  modalOptionTextActive: {
    color: 'white',
  },
  resetButton: {
    width: 34,
    height: 34,
    borderRadius: 17,
    borderWidth: 1,
    borderColor: '#cbd5f5',
    backgroundColor: 'white',
    alignItems: 'center',
    justifyContent: 'center',
    alignSelf: 'center',
  },
  resetButtonIcon: {
    color: '#1e293b',
  },
  chipRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginTop: 8,
  },
  chip: {
    paddingVertical: 6,
    paddingHorizontal: 12,
    borderRadius: 999,
    borderWidth: 1,
    borderColor: '#cbd5f5',
    backgroundColor: 'white',
    marginRight: 8,
    marginBottom: 8,
  },
  chipActive: {
    backgroundColor: '#0f172a',
    borderColor: '#0f172a',
  },
  chipText: {
    fontSize: 12,
    color: '#1e293b',
    fontWeight: '600',
  },
  chipTextActive: {
    color: 'white',
  },
  toggleRow: {
    marginTop: 8,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  toggleLabel: {
    fontSize: 12,
    fontWeight: '600',
    color: '#0f172a',
  },
  toggleHint: {
    fontSize: 11,
    color: '#64748b',
  },
  status: {
    marginTop: 14,
    fontSize: 12,
  },
  statusNeutral: { color: '#0f172a' },
  statusGood: { color: '#15803d' },
  statusBad: { color: '#b91c1c' },
  help: { color: '#64748b', fontSize: 12, alignSelf: 'center' },
});
