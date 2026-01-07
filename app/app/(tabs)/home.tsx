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
  title: 'Mist Valley Oracle',
  subject: 'A fictional oracle in a silver robe, fully clothed',
  action: 'She senses the future as mist drifts through the valley',
  environment: 'Dawn light, floating isles, ancient ruins in fog',
  camera: 'Slow orbit, smooth tracking, 35mm lens',
  lighting: 'Soft sunrise glow, volumetric mist',
  mood: 'Serene, mysterious, hopeful',
  style: 'Cinematic, high detail, natural color grading',
  aspectRatio: '16:9',
  durationSeconds: '8',
  audioLanguage: 'auto',
  sceneCount: '',
  spokenWords: '',
  extraRequirements: '',
  negative: 'no text, no logos, no gore',
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

  const toneStyle = (tone: 'neutral' | 'good' | 'bad') =>
    tone === 'good' ? styles.statusGood : tone === 'bad' ? styles.statusBad : styles.statusNeutral;

  const statusStyle = toneStyle(statusTone);

  const updateSpec = (key: keyof typeof DEFAULT_PROMPT_SPEC, value: string | boolean) => {
    setPromptSpec((prev) => ({ ...prev, [key]: value }));
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

          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Generate video</Text>
            <Text style={styles.sectionSubtitle}>Draft a Sora prompt, edit it, then render a video.</Text>

            <View style={styles.panel}>
              <Text style={styles.panelTitle}>Video content</Text>
              <Text style={styles.panelHint}>Describe the scene, action, and visual tone.</Text>

              <Text style={styles.fieldLabel}>Title</Text>
              <TextInput
                style={[styles.input, promptSpec.autoTitle && styles.inputDisabled]}
                value={promptSpec.title}
                onChangeText={(v) => updateSpec('title', v)}
                editable={!promptSpec.autoTitle}
              />
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
              <SelectControl
                label="Audio language"
                value={promptSpec.audioLanguage}
                options={AUDIO_LANGUAGE_OPTIONS}
                onChange={(value) => updateSpec('audioLanguage', value)}
              />
              {renderHistory('audioLanguage', (value) => updateSpec('audioLanguage', value))}

              <Text style={styles.fieldLabel}>Subject</Text>
              <TextInput
                style={styles.textArea}
                value={promptSpec.subject}
                onChangeText={(v) => updateSpec('subject', v)}
                multiline
              />
              {renderHistory('subject', (value) => updateSpec('subject', value))}

              <Text style={styles.fieldLabel}>Action</Text>
              <TextInput
                style={styles.textArea}
                value={promptSpec.action}
                onChangeText={(v) => updateSpec('action', v)}
                multiline
              />
              {renderHistory('action', (value) => updateSpec('action', value))}

              <Text style={styles.fieldLabel}>Environment</Text>
              <TextInput
                style={styles.textArea}
                value={promptSpec.environment}
                onChangeText={(v) => updateSpec('environment', v)}
                multiline
              />
              {renderHistory('environment', (value) => updateSpec('environment', value))}

              <Text style={styles.fieldLabel}>Camera</Text>
              <TextInput style={styles.input} value={promptSpec.camera} onChangeText={(v) => updateSpec('camera', v)} />
              {renderHistory('camera', (value) => updateSpec('camera', value))}

              <Text style={styles.fieldLabel}>Lighting</Text>
              <TextInput
                style={styles.input}
                value={promptSpec.lighting}
                onChangeText={(v) => updateSpec('lighting', v)}
              />
              {renderHistory('lighting', (value) => updateSpec('lighting', value))}

              <Text style={styles.fieldLabel}>Mood</Text>
              <TextInput style={styles.input} value={promptSpec.mood} onChangeText={(v) => updateSpec('mood', v)} />
              {renderHistory('mood', (value) => updateSpec('mood', value))}

              <Text style={styles.fieldLabel}>Style</Text>
              <TextInput
                style={styles.textArea}
                value={promptSpec.style}
                onChangeText={(v) => updateSpec('style', v)}
                multiline
              />
              {renderHistory('style', (value) => updateSpec('style', value))}

              <Text style={styles.fieldLabel}>Spoken words (optional)</Text>
              <TextInput
                style={styles.textArea}
                value={promptSpec.spokenWords}
                onChangeText={(v) => updateSpec('spokenWords', v)}
                multiline
              />
              {renderHistory('spokenWords', (value) => updateSpec('spokenWords', value))}

              <Text style={styles.fieldLabel}>Scene count (optional)</Text>
              <TextInput
                style={styles.input}
                value={promptSpec.sceneCount}
                onChangeText={(value) => updateSpec('sceneCount', value.replace(/[^\d]/g, ''))}
                keyboardType="numeric"
              />
              {renderHistory('sceneCount', (value) => updateSpec('sceneCount', value))}

              <Text style={styles.fieldLabel}>Extra requirements</Text>
              <TextInput
                style={styles.textArea}
                value={promptSpec.extraRequirements}
                onChangeText={(v) => updateSpec('extraRequirements', v)}
                multiline
              />
              {renderHistory('extraRequirements', (value) => updateSpec('extraRequirements', value))}

              <Text style={styles.fieldLabel}>Negative prompt</Text>
              <TextInput
                style={styles.textArea}
                value={promptSpec.negative}
                onChangeText={(v) => updateSpec('negative', v)}
                multiline
              />
              {renderHistory('negative', (value) => updateSpec('negative', value))}
            </View>

            <View style={styles.panel}>
              <Text style={styles.panelTitle}>Controls</Text>
              <Text style={styles.panelHint}>Tune aspect ratio and length.</Text>

              <Text style={styles.fieldLabel}>Aspect ratio</Text>
              <View style={styles.chipRow}>
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

              <Text style={styles.fieldLabel}>Length (seconds)</Text>
              <TextInput
                style={styles.input}
                value={promptSpec.durationSeconds}
                onChangeText={(value) => updateSpec('durationSeconds', value.replace(/[^\d]/g, ''))}
                keyboardType="numeric"
              />
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
  selectRow: {
    marginTop: 8,
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
