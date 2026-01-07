import React, { useEffect, useMemo, useState } from 'react';
import { ActivityIndicator, Platform, Pressable, ScrollView, StyleSheet, Text, TextInput, View } from 'react-native';
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
  negative: 'no text, no logos, no gore',
};

const ASPECT_OPTIONS = [
  { value: '16:9', label: '16:9 Landscape' },
  { value: '9:16', label: '9:16 Portrait' },
  { value: 'auto', label: 'Auto' },
];

export default function HomeScreen() {
  const [picked, setPicked] = useState<DocumentPicker.DocumentPickerAsset | null>(null);
  const [status, setStatus] = useState<string>('');
  const [statusTone, setStatusTone] = useState<'neutral' | 'good' | 'bad'>('neutral');
  const [uploading, setUploading] = useState(false);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [promptSpec, setPromptSpec] = useState(DEFAULT_PROMPT_SPEC);
  const [promptResult, setPromptResult] = useState<{
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

  const updateSpec = (key: keyof typeof DEFAULT_PROMPT_SPEC, value: string) => {
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
    assign('title', promptSpec.title);
    assign('subject', promptSpec.subject);
    assign('action', promptSpec.action);
    assign('environment', promptSpec.environment);
    assign('camera', promptSpec.camera);
    assign('lighting', promptSpec.lighting);
    assign('mood', promptSpec.mood);
    assign('style', promptSpec.style);
    assign('negative', promptSpec.negative);
    const duration = parseInt(promptSpec.durationSeconds, 10);
    if (!Number.isNaN(duration)) {
      payload.duration_seconds = duration;
    }
    if (promptSpec.aspectRatio !== 'auto') {
      payload.aspect_ratio = promptSpec.aspectRatio;
    }
    return payload;
  };

  const generatePrompt = async () => {
    if (prompting) return;
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
    setGeneratingVideo(true);
    setVideoStatus('Generating video... this can take a few minutes.');
    setVideoTone('neutral');
    try {
      const spec = buildPromptSpecPayload();
      const title = spec.title || 'Generated video';
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
              <TextInput style={styles.input} value={promptSpec.title} onChangeText={(v) => updateSpec('title', v)} />

              <Text style={styles.fieldLabel}>Subject</Text>
              <TextInput
                style={styles.textArea}
                value={promptSpec.subject}
                onChangeText={(v) => updateSpec('subject', v)}
                multiline
              />

              <Text style={styles.fieldLabel}>Action</Text>
              <TextInput
                style={styles.textArea}
                value={promptSpec.action}
                onChangeText={(v) => updateSpec('action', v)}
                multiline
              />

              <Text style={styles.fieldLabel}>Environment</Text>
              <TextInput
                style={styles.textArea}
                value={promptSpec.environment}
                onChangeText={(v) => updateSpec('environment', v)}
                multiline
              />

              <Text style={styles.fieldLabel}>Camera</Text>
              <TextInput style={styles.input} value={promptSpec.camera} onChangeText={(v) => updateSpec('camera', v)} />

              <Text style={styles.fieldLabel}>Lighting</Text>
              <TextInput
                style={styles.input}
                value={promptSpec.lighting}
                onChangeText={(v) => updateSpec('lighting', v)}
              />

              <Text style={styles.fieldLabel}>Mood</Text>
              <TextInput style={styles.input} value={promptSpec.mood} onChangeText={(v) => updateSpec('mood', v)} />

              <Text style={styles.fieldLabel}>Style</Text>
              <TextInput
                style={styles.textArea}
                value={promptSpec.style}
                onChangeText={(v) => updateSpec('style', v)}
                multiline
              />

              <Text style={styles.fieldLabel}>Negative prompt</Text>
              <TextInput
                style={styles.textArea}
                value={promptSpec.negative}
                onChangeText={(v) => updateSpec('negative', v)}
                multiline
              />
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
  status: {
    marginTop: 14,
    fontSize: 12,
  },
  statusNeutral: { color: '#0f172a' },
  statusGood: { color: '#15803d' },
  statusBad: { color: '#b91c1c' },
  help: { color: '#64748b', fontSize: 12, alignSelf: 'center' },
});
