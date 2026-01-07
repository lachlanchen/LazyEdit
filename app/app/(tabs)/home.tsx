import React, { useEffect, useMemo, useState } from 'react';
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

const DEFAULT_PROMPT_SPEC = {
  autoTitle: true,
  title: 'Epic Vision',
  subject: 'A fictional protagonist in a vast imagined world',
  action: 'They confront a revelation that changes their journey',
  environment: 'An epic, timeless setting (mythic history or distant planet) with sweeping scale',
  camera: 'Cinematic movement that reveals scale and detail',
  lighting: 'Atmospheric, dramatic lighting with soft volumetric depth',
  mood: 'Epic, awe-inspiring, contemplative',
  style: 'Cinematic, richly detailed, timeless tone',
  aspectRatio: '16:9',
  durationSeconds: '10',
  audioLanguage: 'auto',
  sceneCount: '',
  spokenWords: 'Include a short original philosophical line of dialogue.',
  extraRequirements: 'Let the model invent distinct moments and symbolism while keeping a coherent arc.',
  negative: 'no text, no logos, no gore, no real people',
};

const ASPECT_OPTIONS = [
  { value: '16:9', label: '16:9 Landscape' },
  { value: '9:16', label: '9:16 Portrait' },
  { value: 'auto', label: 'Auto' },
];
const AUDIO_LANGUAGE_OPTIONS = [
  { value: 'auto', label: 'Auto (model decides)' },
  { value: 'en', label: 'English' },
  { value: 'zh', label: 'Chinese' },
  { value: 'ja', label: 'Japanese' },
  { value: 'ko', label: 'Korean' },
  { value: 'vi', label: 'Vietnamese' },
  { value: 'ar', label: 'Arabic' },
  { value: 'fr', label: 'French' },
  { value: 'es', label: 'Spanish' },
];

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
}: {
  label: string;
  value: string;
  options: { value: string; label: string }[];
  onChange: (value: string) => void;
}) => (
  <SelectControl label={label} value={value} options={options} onChange={onChange} hideIfSingle />
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
  audioLanguage: [],
  sceneCount: [],
  spokenWords: [],
  extraRequirements: [],
  negative: [],
};

export default function HomeScreen() {
  const [picked, setPicked] = useState<DocumentPicker.DocumentPickerAsset | null>(null);
  const [status, setStatus] = useState<string>('');
  const [statusTone, setStatusTone] = useState<'neutral' | 'good' | 'bad'>('neutral');
  const [uploading, setUploading] = useState(false);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'upload' | 'generate' | 'remix'>('upload');
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
    model?: string;
    size?: string;
    seconds?: number;
  } | null>(null);
  const [promptOutput, setPromptOutput] = useState<string>('');
  const [prompting, setPrompting] = useState(false);
  const [promptStatus, setPromptStatus] = useState<string>('');
  const [promptTone, setPromptTone] = useState<'neutral' | 'good' | 'bad'>('neutral');
  const [promptSpecLoaded, setPromptSpecLoaded] = useState(false);
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
    setStatus('Uploading...');
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
    setRemixStatus('Uploading for remix...');
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
    const duration = parseInt(promptSpec.durationSeconds, 10);
    if (!Number.isNaN(duration)) {
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
    { value: '', label: 'Select history' },
    ...items.map((item) => ({
      value: item,
      label: item.length > 60 ? `${item.slice(0, 60)}…` : item,
    })),
  ];

  const renderHistory = (key: HistoryKey, onPick: (value: string) => void) => {
    const items = promptHistory[key] || [];
    if (!items.length) return null;
    return <HistorySelect label="History" value="" options={historyOptions(items)} onChange={onPick} />;
  };

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
  }, []);

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
    setPromptStatus('Generating prompt...');
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
      setPromptOutput(promptText);
      setPromptResult({
        title: result.title || json.title,
        prompt: promptText,
        negativePrompt: result.negative_prompt || json.negative_prompt,
        model: result.model || json.model,
        size: result.size || json.size,
        seconds: result.seconds || json.seconds,
      });
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
    setSpecStatus('Generating specs...');
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
    setVideoStatus('Generating video... this can take a few minutes.');
    setVideoTone('neutral');
    try {
      const spec = buildPromptSpecPayload();
      const title = promptResult?.title || (promptSpec.autoTitle ? 'Generated video' : spec.title || 'Generated video');
      const resp = await fetch(`${API_URL}/api/videos/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt: promptOutput.trim(),
          model: promptResult?.model,
          size: promptResult?.size,
          seconds: promptResult?.seconds,
          title,
        }),
      });
      const json = await resp.json();
      if (!resp.ok) {
        setVideoStatus(`Generation failed: ${json.error || json.message || resp.statusText}`);
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
          <Text style={styles.title}>LazyEdit</Text>
          <Text style={styles.subtitle}>Multilingual Video Editor</Text>

          <View style={styles.tabRow}>
            {[
              { key: 'upload', label: 'Upload' },
              { key: 'generate', label: 'Generate' },
              { key: 'remix', label: 'Remix' },
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
          <Text style={styles.stepLabel}>Pick a video</Text>
        </View>

        <Pressable style={styles.btnPrimary} onPress={pick}>
          <Text style={styles.btnText}>{picked ? 'Pick another video' : 'Pick a video'}</Text>
        </Pressable>

        <View style={styles.card}>
          {picked ? (
            <>
              <Text style={styles.cardTitle}>Selected video</Text>
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
                <Text style={styles.previewHint}>Preview available on web. Ready to upload.</Text>
              )}
            </>
          ) : (
            <>
              <Text style={styles.cardTitle}>No video selected</Text>
              <Text style={styles.previewHint}>Pick a video to preview and upload.</Text>
            </>
          )}
        </View>

        <View style={styles.stepRow}>
          <View style={styles.stepBadge}>
            <Text style={styles.stepText}>2</Text>
          </View>
          <Text style={styles.stepLabel}>Upload to backend</Text>
        </View>

        <Pressable
          disabled={!picked || uploading}
          style={[styles.btnSecondary, (!picked || uploading) && styles.btnDisabled]}
          onPress={upload}
        >
          <View style={styles.btnContent}>
            {uploading && <ActivityIndicator color="white" style={{ marginRight: 8 }} />}
            <Text style={styles.btnText}>{uploading ? 'Uploading...' : 'Upload'}</Text>
          </View>
        </Pressable>

              {status ? <Text style={[styles.status, statusStyle]}>{status}</Text> : null}
            </>
          ) : null}

          {activeTab === 'generate' ? (
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>Generate video</Text>
              <Text style={styles.sectionSubtitle}>Build specs, generate a prompt, then render a video.</Text>

            <View style={styles.panel}>
              <View style={styles.panelHeader}>
                <Text style={styles.stageBadge}>Stage A</Text>
                <Text style={styles.panelTitle}>Idea → Specs (optional)</Text>
              </View>
              <Text style={styles.panelHint}>
                Provide a loose idea and let the model draft detailed specs. Skip this if you prefer manual edits.
              </Text>

              <Text style={styles.fieldLabel}>Idea prompt</Text>
              <TextInput
                style={styles.textArea}
                value={ideaPrompt}
                onChangeText={setIdeaPrompt}
                placeholder="Epic fantasy vision in a vast world with poetic dialogue and cinematic scale."
                multiline
              />

              <Pressable style={styles.btnAccent} onPress={generateSpecs} disabled={specGenerating}>
                <View style={styles.btnContent}>
                  {specGenerating && <ActivityIndicator color="white" style={{ marginRight: 8 }} />}
                  <Text style={styles.btnText}>{specGenerating ? 'Generating specs...' : 'Generate specs'}</Text>
                </View>
              </Pressable>

              {specStatus ? (
                <Text style={[styles.status, toneStyle(specTone)]}>{specStatus}</Text>
              ) : null}
            </View>

            <View style={styles.panel}>
              <View style={styles.panelHeader}>
                <Text style={styles.stageBadge}>Stage B</Text>
                <Text style={styles.panelTitle}>Specs</Text>
              </View>
              <Text style={styles.panelHint}>Describe the scene, action, and visual tone.</Text>

              <Text style={styles.fieldLabel}>Title</Text>
              <View style={[styles.inputRow, styles.inputRowTop]}>
                <TextInput
                  style={[styles.input, styles.inputFlex, promptSpec.autoTitle && styles.inputDisabled]}
                  value={promptSpec.title}
                  onChangeText={(v) => updateSpec('title', v)}
                  editable={!promptSpec.autoTitle}
                />
                <Pressable style={styles.resetButton} onPress={() => resetSpec('title')}>
                  <Text style={styles.resetButtonText}>Reset</Text>
                </Pressable>
              </View>
              <View style={styles.toggleRow}>
                <View>
                  <Text style={styles.toggleLabel}>Auto title</Text>
                  <Text style={styles.toggleHint}>Let the model name the scene</Text>
                </View>
                <Switch
                  value={promptSpec.autoTitle}
                  onValueChange={(value) => updateSpec('autoTitle', value)}
                  trackColor={{ false: '#e2e8f0', true: '#2563eb' }}
                  thumbColor={promptSpec.autoTitle ? '#f8fafc' : '#f1f5f9'}
                />
              </View>
              {!promptSpec.autoTitle ? renderHistory('title', (value) => updateSpec('title', value)) : null}

              <Text style={styles.fieldLabel}>Audio language</Text>
              <View style={styles.inputRow}>
                <View style={styles.inputFlex}>
                  <SelectControl
                    label="Audio language"
                    value={promptSpec.audioLanguage}
                    options={AUDIO_LANGUAGE_OPTIONS}
                    onChange={(value) => updateSpec('audioLanguage', value)}
                  />
                </View>
                <Pressable style={styles.resetButton} onPress={() => resetSpec('audioLanguage')}>
                  <Text style={styles.resetButtonText}>Reset</Text>
                </Pressable>
              </View>
              {renderHistory('audioLanguage', (value) => updateSpec('audioLanguage', value))}

              <Text style={styles.fieldLabel}>Subject</Text>
              <View style={[styles.inputRow, styles.inputRowTop]}>
                <TextInput
                  style={[styles.textArea, styles.inputFlex]}
                  value={promptSpec.subject}
                  onChangeText={(v) => updateSpec('subject', v)}
                  multiline
                />
                <Pressable style={styles.resetButton} onPress={() => resetSpec('subject')}>
                  <Text style={styles.resetButtonText}>Reset</Text>
                </Pressable>
              </View>
              {renderHistory('subject', (value) => updateSpec('subject', value))}

              <Text style={styles.fieldLabel}>Action</Text>
              <View style={[styles.inputRow, styles.inputRowTop]}>
                <TextInput
                  style={[styles.textArea, styles.inputFlex]}
                  value={promptSpec.action}
                  onChangeText={(v) => updateSpec('action', v)}
                  multiline
                />
                <Pressable style={styles.resetButton} onPress={() => resetSpec('action')}>
                  <Text style={styles.resetButtonText}>Reset</Text>
                </Pressable>
              </View>
              {renderHistory('action', (value) => updateSpec('action', value))}

              <Text style={styles.fieldLabel}>Environment</Text>
              <View style={[styles.inputRow, styles.inputRowTop]}>
                <TextInput
                  style={[styles.textArea, styles.inputFlex]}
                  value={promptSpec.environment}
                  onChangeText={(v) => updateSpec('environment', v)}
                  multiline
                />
                <Pressable style={styles.resetButton} onPress={() => resetSpec('environment')}>
                  <Text style={styles.resetButtonText}>Reset</Text>
                </Pressable>
              </View>
              {renderHistory('environment', (value) => updateSpec('environment', value))}

              <Text style={styles.fieldLabel}>Camera</Text>
              <View style={styles.inputRow}>
                <TextInput
                  style={[styles.input, styles.inputFlex]}
                  value={promptSpec.camera}
                  onChangeText={(v) => updateSpec('camera', v)}
                />
                <Pressable style={styles.resetButton} onPress={() => resetSpec('camera')}>
                  <Text style={styles.resetButtonText}>Reset</Text>
                </Pressable>
              </View>
              {renderHistory('camera', (value) => updateSpec('camera', value))}

              <Text style={styles.fieldLabel}>Lighting</Text>
              <View style={styles.inputRow}>
                <TextInput
                  style={[styles.input, styles.inputFlex]}
                  value={promptSpec.lighting}
                  onChangeText={(v) => updateSpec('lighting', v)}
                />
                <Pressable style={styles.resetButton} onPress={() => resetSpec('lighting')}>
                  <Text style={styles.resetButtonText}>Reset</Text>
                </Pressable>
              </View>
              {renderHistory('lighting', (value) => updateSpec('lighting', value))}

              <Text style={styles.fieldLabel}>Mood</Text>
              <View style={styles.inputRow}>
                <TextInput
                  style={[styles.input, styles.inputFlex]}
                  value={promptSpec.mood}
                  onChangeText={(v) => updateSpec('mood', v)}
                />
                <Pressable style={styles.resetButton} onPress={() => resetSpec('mood')}>
                  <Text style={styles.resetButtonText}>Reset</Text>
                </Pressable>
              </View>
              {renderHistory('mood', (value) => updateSpec('mood', value))}

              <Text style={styles.fieldLabel}>Style</Text>
              <View style={[styles.inputRow, styles.inputRowTop]}>
                <TextInput
                  style={[styles.textArea, styles.inputFlex]}
                  value={promptSpec.style}
                  onChangeText={(v) => updateSpec('style', v)}
                  multiline
                />
                <Pressable style={styles.resetButton} onPress={() => resetSpec('style')}>
                  <Text style={styles.resetButtonText}>Reset</Text>
                </Pressable>
              </View>
              {renderHistory('style', (value) => updateSpec('style', value))}

              <Text style={styles.fieldLabel}>Spoken words (optional)</Text>
              <View style={[styles.inputRow, styles.inputRowTop]}>
                <TextInput
                  style={[styles.textArea, styles.inputFlex]}
                  value={promptSpec.spokenWords}
                  onChangeText={(v) => updateSpec('spokenWords', v)}
                  multiline
                />
                <Pressable style={styles.resetButton} onPress={() => resetSpec('spokenWords')}>
                  <Text style={styles.resetButtonText}>Reset</Text>
                </Pressable>
              </View>
              {renderHistory('spokenWords', (value) => updateSpec('spokenWords', value))}

              <Text style={styles.fieldLabel}>Scene count (optional)</Text>
              <View style={styles.inputRow}>
                <TextInput
                  style={[styles.input, styles.inputFlex]}
                  value={promptSpec.sceneCount}
                  onChangeText={(value) => updateSpec('sceneCount', value.replace(/[^\d]/g, ''))}
                  keyboardType="numeric"
                />
                <Pressable style={styles.resetButton} onPress={() => resetSpec('sceneCount')}>
                  <Text style={styles.resetButtonText}>Reset</Text>
                </Pressable>
              </View>
              {renderHistory('sceneCount', (value) => updateSpec('sceneCount', value))}

              <Text style={styles.fieldLabel}>Extra requirements</Text>
              <View style={[styles.inputRow, styles.inputRowTop]}>
                <TextInput
                  style={[styles.textArea, styles.inputFlex]}
                  value={promptSpec.extraRequirements}
                  onChangeText={(v) => updateSpec('extraRequirements', v)}
                  multiline
                />
                <Pressable style={styles.resetButton} onPress={() => resetSpec('extraRequirements')}>
                  <Text style={styles.resetButtonText}>Reset</Text>
                </Pressable>
              </View>
              {renderHistory('extraRequirements', (value) => updateSpec('extraRequirements', value))}

              <Text style={styles.fieldLabel}>Negative prompt</Text>
              <View style={[styles.inputRow, styles.inputRowTop]}>
                <TextInput
                  style={[styles.textArea, styles.inputFlex]}
                  value={promptSpec.negative}
                  onChangeText={(v) => updateSpec('negative', v)}
                  multiline
                />
                <Pressable style={styles.resetButton} onPress={() => resetSpec('negative')}>
                  <Text style={styles.resetButtonText}>Reset</Text>
                </Pressable>
              </View>
              {renderHistory('negative', (value) => updateSpec('negative', value))}
            </View>

            <View style={styles.panel}>
              <View style={styles.panelHeader}>
                <Text style={styles.stageBadge}>Stage B</Text>
                <Text style={styles.panelTitle}>Controls</Text>
              </View>
              <Text style={styles.panelHint}>Tune aspect ratio and length.</Text>

              <Text style={styles.fieldLabel}>Aspect ratio</Text>
              <View style={[styles.inputRow, styles.inputRowTop]}>
                <View style={[styles.chipRow, styles.inputFlex]}>
                  {ASPECT_OPTIONS.map((option) => {
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
                <Pressable style={styles.resetButton} onPress={() => resetSpec('aspectRatio')}>
                  <Text style={styles.resetButtonText}>Reset</Text>
                </Pressable>
              </View>

              <Text style={styles.fieldLabel}>Length (seconds)</Text>
              <View style={styles.inputRow}>
                <TextInput
                  style={[styles.input, styles.inputFlex]}
                  value={promptSpec.durationSeconds}
                  onChangeText={(value) => updateSpec('durationSeconds', value.replace(/[^\d]/g, ''))}
                  keyboardType="numeric"
                />
                <Pressable style={styles.resetButton} onPress={() => resetSpec('durationSeconds')}>
                  <Text style={styles.resetButtonText}>Reset</Text>
                </Pressable>
              </View>
            </View>

            <Pressable style={styles.btnAccent} onPress={generatePrompt} disabled={prompting}>
              <View style={styles.btnContent}>
                {prompting && <ActivityIndicator color="white" style={{ marginRight: 8 }} />}
                <Text style={styles.btnText}>{prompting ? 'Generating prompt...' : 'Generate prompt'}</Text>
              </View>
            </Pressable>

            {promptStatus ? (
              <Text style={[styles.status, toneStyle(promptTone)]}>{promptStatus}</Text>
            ) : null}

            <View style={styles.panelHeader}>
              <Text style={styles.stageBadge}>Stage C</Text>
              <Text style={styles.panelTitle}>Video prompt</Text>
            </View>
            <Text style={styles.fieldLabel}>Generated prompt</Text>
            <TextInput
              style={styles.textAreaLarge}
              value={promptOutput}
              onChangeText={setPromptOutput}
              placeholder="Generate a prompt above, then edit it here."
              multiline
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
                <Text style={styles.btnText}>{generatingVideo ? 'Generating video...' : 'Generate video'}</Text>
              </View>
            </Pressable>

            {videoStatus ? (
              <Text style={[styles.status, toneStyle(videoTone)]}>{videoStatus}</Text>
            ) : null}

            {generatedVideoUrl ? (
              <View style={styles.card}>
                <Text style={styles.cardTitle}>Generated video preview</Text>
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
                  <Text style={styles.previewHint}>Preview available on web.</Text>
                )}
              </View>
            ) : null}
          </View>
          ) : null}

          {activeTab === 'remix' ? (
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>Remix video</Text>
              <Text style={styles.sectionSubtitle}>
                Upload a video and provide remix directions for audio and scene changes.
              </Text>

              <View style={styles.stepRow}>
                <View style={styles.stepBadge}>
                  <Text style={styles.stepText}>1</Text>
                </View>
                <Text style={styles.stepLabel}>Pick a video</Text>
              </View>

              <Pressable style={styles.btnPrimary} onPress={pickRemix}>
                <Text style={styles.btnText}>{remixPicked ? 'Pick another video' : 'Pick a video'}</Text>
              </Pressable>

              <View style={styles.card}>
                {remixPicked ? (
                  <>
                    <Text style={styles.cardTitle}>Selected video</Text>
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
                      <Text style={styles.previewHint}>Preview available on web. Ready to remix.</Text>
                    )}
                  </>
                ) : (
                  <>
                    <Text style={styles.cardTitle}>No video selected</Text>
                    <Text style={styles.previewHint}>Pick a video to preview and remix.</Text>
                  </>
                )}
              </View>

              <Text style={styles.fieldLabel}>Remix directions (optional)</Text>
              <TextInput
                style={styles.textArea}
                value={remixNotes}
                onChangeText={setRemixNotes}
                placeholder="Describe changes to audio, dialogue, pacing, or scene style."
                multiline
              />

              <View style={styles.stepRow}>
                <View style={styles.stepBadge}>
                  <Text style={styles.stepText}>2</Text>
                </View>
                <Text style={styles.stepLabel}>Upload for remix</Text>
              </View>

              <Pressable
                disabled={!remixPicked || remixUploading}
                style={[styles.btnSecondary, (!remixPicked || remixUploading) && styles.btnDisabled]}
                onPress={uploadRemix}
              >
                <View style={styles.btnContent}>
                  {remixUploading && <ActivityIndicator color="white" style={{ marginRight: 8 }} />}
                  <Text style={styles.btnText}>{remixUploading ? 'Uploading...' : 'Upload for remix'}</Text>
                </View>
              </Pressable>

              {remixStatus ? <Text style={[styles.status, remixStatusStyle]}>{remixStatus}</Text> : null}
            </View>
          ) : null}
        </View>
        <Text style={styles.help}>Backend: {API_URL}</Text>
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
    paddingVertical: 8,
    paddingHorizontal: 10,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: '#cbd5f5',
    backgroundColor: 'white',
  },
  resetButtonText: {
    fontSize: 11,
    fontWeight: '600',
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
