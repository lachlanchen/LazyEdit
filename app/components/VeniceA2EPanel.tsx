import React, { useMemo, useState } from 'react';
import {
  ActivityIndicator,
  Image,
  Platform,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';

const DEFAULT_NEGATIVE_PROMPT =
  'blurry, low quality, chaotic, deformed, watermark, bad anatomy, shaky camera view point';

type StatusTone = 'neutral' | 'good' | 'bad';
type EventEntry = { ts: string; stage: string; message: string };

type VeniceA2EPanelProps = {
  apiUrl: string;
};

const chipOptions = {
  aspectRatio: [
    { value: '9:16', label: '9:16' },
    { value: '16:9', label: '16:9' },
    { value: '1:1', label: '1:1' },
    { value: '4:3', label: '4:3' },
    { value: '3:4', label: '3:4' },
  ],
  videoTime: [
    { value: '5', label: '5s' },
    { value: '10', label: '10s' },
    { value: '15', label: '15s' },
    { value: '20', label: '20s' },
  ],
  audioLanguage: [
    { value: 'auto', label: 'Auto' },
    { value: 'en', label: 'EN' },
    { value: 'zh', label: 'ZH' },
    { value: 'ja', label: 'JA' },
    { value: 'ko', label: 'KO' },
    { value: 'vi', label: 'VI' },
    { value: 'fr', label: 'FR' },
    { value: 'es', label: 'ES' },
    { value: 'ar', label: 'AR' },
  ],
};

const toneStyle = (tone: StatusTone) =>
  tone === 'good' ? styles.statusGood : tone === 'bad' ? styles.statusBad : styles.statusNeutral;

export default function VeniceA2EPanel({ apiUrl }: VeniceA2EPanelProps) {
  const [idea, setIdea] = useState('');
  const [imagePrompt, setImagePrompt] = useState('');
  const [videoPrompt, setVideoPrompt] = useState('');
  const [audioText, setAudioText] = useState('');
  const [aspectRatio, setAspectRatio] = useState('9:16');
  const [videoTime, setVideoTime] = useState('10');
  const [audioLanguage, setAudioLanguage] = useState('auto');
  const [negativePrompt, setNegativePrompt] = useState(DEFAULT_NEGATIVE_PROMPT);
  const [events, setEvents] = useState<EventEntry[]>([]);
  const [status, setStatus] = useState('');
  const [statusTone, setStatusTone] = useState<StatusTone>('neutral');
  const [busyPrompts, setBusyPrompts] = useState(false);
  const [busyRun, setBusyRun] = useState(false);
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [videoUrl, setVideoUrl] = useState<string | null>(null);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [talkingVideoUrl, setTalkingVideoUrl] = useState<string | null>(null);

  const canGenerate = idea.trim().length > 0;
  const canRun =
    busyRun ||
    idea.trim().length > 0 ||
    (imagePrompt.trim().length > 0 && videoPrompt.trim().length > 0 && audioText.trim().length > 0);

  const runPromptGeneration = async () => {
    if (busyPrompts) return;
    if (!idea.trim()) {
      setStatus('Add an idea prompt first.');
      setStatusTone('bad');
      return;
    }
    setBusyPrompts(true);
    setStatus('Generating prompts with Venice...');
    setStatusTone('neutral');
    try {
      const resp = await fetch(`${apiUrl}/api/venice-a2e/prompts`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          idea: idea.trim(),
          audio_language: audioLanguage,
        }),
      });
      const json = await resp.json();
      if (!resp.ok) {
        setStatus(`Prompt generation failed: ${json.error || json.details || resp.statusText}`);
        setStatusTone('bad');
        return;
      }
      setImagePrompt(json.image_prompt || '');
      setVideoPrompt(json.video_prompt || '');
      setAudioText(json.audio_text || '');
      setEvents(json.events || []);
      setStatus('Prompts ready. Review and run the pipeline.');
      setStatusTone('good');
    } catch (err: any) {
      setStatus(`Prompt generation failed: ${err?.message || String(err)}`);
      setStatusTone('bad');
    } finally {
      setBusyPrompts(false);
    }
  };

  const runPipeline = async () => {
    if (busyRun) return;
    if (!idea.trim() && !(imagePrompt.trim() && videoPrompt.trim() && audioText.trim())) {
      setStatus('Add an idea prompt or fill all three prompts.');
      setStatusTone('bad');
      return;
    }
    setBusyRun(true);
    setStatus('Running Venice + A2E pipeline. This can take a few minutes...');
    setStatusTone('neutral');
    setImageUrl(null);
    setVideoUrl(null);
    setAudioUrl(null);
    setTalkingVideoUrl(null);
    try {
      const resp = await fetch(`${apiUrl}/api/venice-a2e/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          idea: idea.trim(),
          image_prompt: imagePrompt.trim() || undefined,
          video_prompt: videoPrompt.trim() || undefined,
          audio_text: audioText.trim() || undefined,
          audio_language: audioLanguage,
          aspect_ratio: aspectRatio,
          video_time: parseInt(videoTime, 10),
          negative_prompt: negativePrompt.trim() || undefined,
        }),
      });
      const json = await resp.json();
      if (!resp.ok) {
        setStatus(`Pipeline failed: ${json.error || json.details || resp.statusText}`);
        setStatusTone('bad');
        return;
      }
      setImageUrl(json.image_url || null);
      setVideoUrl(json.video_url || null);
      setAudioUrl(json.audio_url || null);
      setTalkingVideoUrl(json.talking_video_url || null);
      if (json.image_prompt) setImagePrompt(json.image_prompt);
      if (json.video_prompt) setVideoPrompt(json.video_prompt);
      if (json.audio_text) setAudioText(json.audio_text);
      setEvents(json.events || []);
      setStatus('Pipeline complete.');
      setStatusTone('good');
    } catch (err: any) {
      setStatus(`Pipeline failed: ${err?.message || String(err)}`);
      setStatusTone('bad');
    } finally {
      setBusyRun(false);
    }
  };

  const outputItems = useMemo(
    () => [
      { label: 'Image', url: imageUrl, kind: 'image' as const },
      { label: 'Video', url: videoUrl, kind: 'video' as const },
      { label: 'Audio', url: audioUrl, kind: 'audio' as const },
      { label: 'Talking Video', url: talkingVideoUrl, kind: 'video' as const },
    ],
    [imageUrl, videoUrl, audioUrl, talkingVideoUrl],
  );

  return (
    <View style={styles.wrapper}>
      <Text style={styles.title}>Venice + A2E</Text>
      <Text style={styles.subtitle}>
        Generate prompts with Venice, then create image, video, and audio with A2E.
      </Text>

      <View style={styles.card}>
        <Text style={styles.sectionTitle}>Idea</Text>
        <TextInput
          style={styles.textArea}
          value={idea}
          onChangeText={setIdea}
          placeholder="Describe the story, vibe, and characters."
          multiline
        />

        <View style={styles.inlineRow}>
          <View style={styles.inlineBlock}>
            <Text style={styles.label}>Aspect ratio</Text>
            <View style={styles.chipRow}>
              {chipOptions.aspectRatio.map((option) => {
                const active = aspectRatio === option.value;
                return (
                  <Pressable
                    key={option.value}
                    style={[styles.chip, active && styles.chipActive]}
                    onPress={() => setAspectRatio(option.value)}
                  >
                    <Text style={[styles.chipText, active && styles.chipTextActive]}>{option.label}</Text>
                  </Pressable>
                );
              })}
            </View>
          </View>
          <View style={styles.inlineBlock}>
            <Text style={styles.label}>Video length</Text>
            <View style={styles.chipRow}>
              {chipOptions.videoTime.map((option) => {
                const active = videoTime === option.value;
                return (
                  <Pressable
                    key={option.value}
                    style={[styles.chip, active && styles.chipActive]}
                    onPress={() => setVideoTime(option.value)}
                  >
                    <Text style={[styles.chipText, active && styles.chipTextActive]}>{option.label}</Text>
                  </Pressable>
                );
              })}
            </View>
          </View>
        </View>

        <View style={styles.inlineRow}>
          <View style={styles.inlineBlock}>
            <Text style={styles.label}>Audio language</Text>
            <View style={styles.chipRow}>
              {chipOptions.audioLanguage.map((option) => {
                const active = audioLanguage === option.value;
                return (
                  <Pressable
                    key={option.value}
                    style={[styles.chip, active && styles.chipActive]}
                    onPress={() => setAudioLanguage(option.value)}
                  >
                    <Text style={[styles.chipText, active && styles.chipTextActive]}>{option.label}</Text>
                  </Pressable>
                );
              })}
            </View>
          </View>
        </View>

        <View style={styles.buttonRow}>
          <Pressable
            style={[styles.primaryButton, (!canGenerate || busyPrompts) && styles.buttonDisabled]}
            onPress={runPromptGeneration}
            disabled={!canGenerate || busyPrompts}
          >
            <View style={styles.buttonContent}>
              {busyPrompts && <ActivityIndicator color="white" style={{ marginRight: 8 }} />}
              <Text style={styles.primaryButtonText}>Generate prompts</Text>
            </View>
          </Pressable>
          <Pressable
            style={[styles.secondaryButton, (!canRun || busyRun) && styles.buttonDisabled]}
            onPress={runPipeline}
            disabled={!canRun || busyRun}
          >
            <View style={styles.buttonContent}>
              {busyRun && <ActivityIndicator color="white" style={{ marginRight: 8 }} />}
              <Text style={styles.secondaryButtonText}>Run pipeline</Text>
            </View>
          </Pressable>
        </View>

        {status ? <Text style={[styles.status, toneStyle(statusTone)]}>{status}</Text> : null}
      </View>

      <View style={styles.card}>
        <Text style={styles.sectionTitle}>Prompts</Text>
        <Text style={styles.label}>Image prompt</Text>
        <TextInput
          style={styles.textArea}
          value={imagePrompt}
          onChangeText={setImagePrompt}
          placeholder="Still image prompt."
          multiline
        />
        <Text style={styles.label}>Video prompt</Text>
        <TextInput
          style={styles.textArea}
          value={videoPrompt}
          onChangeText={setVideoPrompt}
          placeholder="Motion prompt."
          multiline
        />
        <Text style={styles.label}>Audio text</Text>
        <TextInput
          style={styles.textArea}
          value={audioText}
          onChangeText={setAudioText}
          placeholder="Short narration."
          multiline
        />
        <Text style={styles.label}>Negative prompt</Text>
        <TextInput
          style={styles.textArea}
          value={negativePrompt}
          onChangeText={setNegativePrompt}
          placeholder="Things to avoid."
          multiline
        />
      </View>

      <View style={styles.card}>
        <Text style={styles.sectionTitle}>Events</Text>
        <ScrollView style={styles.eventList}>
          {events.length === 0 ? (
            <Text style={styles.eventEmpty}>No events yet.</Text>
          ) : (
            events.map((event, idx) => (
              <Text key={`${event.ts}-${idx}`} style={styles.eventItem}>
                [{event.stage}] {event.message}
              </Text>
            ))
          )}
        </ScrollView>
      </View>

      <View style={styles.card}>
        <Text style={styles.sectionTitle}>Outputs</Text>
        {outputItems.map((item) => (
          <View key={item.label} style={styles.outputRow}>
            <Text style={styles.outputLabel}>{item.label}</Text>
            {item.url ? (
              item.kind === 'image' ? (
                <Image source={{ uri: item.url }} style={styles.outputImage} />
              ) : Platform.OS === 'web' ? (
                React.createElement(item.kind === 'audio' ? 'audio' : 'video', {
                  src: item.url,
                  controls: true,
                  style: { width: '100%', borderRadius: 12 },
                })
              ) : (
                <Text style={styles.outputLink}>{item.url}</Text>
              )
            ) : (
              <Text style={styles.outputEmpty}>Not ready.</Text>
            )}
          </View>
        ))}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  wrapper: {
    gap: 16,
  },
  title: {
    fontSize: 20,
    fontWeight: '700',
    color: '#141414',
  },
  subtitle: {
    fontSize: 14,
    color: '#5b5b5b',
    marginBottom: 4,
  },
  card: {
    backgroundColor: '#ffffff',
    borderRadius: 16,
    padding: 16,
    borderWidth: 1,
    borderColor: '#ebe7df',
    shadowColor: '#000',
    shadowOpacity: 0.04,
    shadowRadius: 8,
    shadowOffset: { width: 0, height: 2 },
    elevation: 1,
  },
  sectionTitle: {
    fontSize: 15,
    fontWeight: '600',
    color: '#1d1d1d',
    marginBottom: 10,
  },
  label: {
    fontSize: 12,
    color: '#4c4c4c',
    marginBottom: 6,
    marginTop: 12,
  },
  textArea: {
    borderWidth: 1,
    borderColor: '#e0ddd6',
    borderRadius: 12,
    padding: 12,
    minHeight: 80,
    textAlignVertical: 'top',
    backgroundColor: '#fbfaf7',
  },
  inlineRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
  },
  inlineBlock: {
    flexGrow: 1,
    minWidth: 200,
  },
  chipRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  chip: {
    paddingVertical: 6,
    paddingHorizontal: 10,
    borderRadius: 999,
    borderWidth: 1,
    borderColor: '#dad3c7',
    backgroundColor: '#f8f6f2',
  },
  chipActive: {
    borderColor: '#2f6cff',
    backgroundColor: '#2f6cff',
  },
  chipText: {
    fontSize: 12,
    color: '#464646',
  },
  chipTextActive: {
    color: '#fff',
    fontWeight: '600',
  },
  buttonRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
    marginTop: 16,
  },
  primaryButton: {
    backgroundColor: '#2f6cff',
    borderRadius: 999,
    paddingVertical: 10,
    paddingHorizontal: 16,
  },
  secondaryButton: {
    backgroundColor: '#0f172a',
    borderRadius: 999,
    paddingVertical: 10,
    paddingHorizontal: 16,
  },
  buttonDisabled: {
    opacity: 0.5,
  },
  buttonContent: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  primaryButtonText: {
    color: '#ffffff',
    fontWeight: '600',
  },
  secondaryButtonText: {
    color: '#ffffff',
    fontWeight: '600',
  },
  status: {
    marginTop: 12,
    fontSize: 13,
  },
  statusNeutral: {
    color: '#5b5b5b',
  },
  statusGood: {
    color: '#15803d',
  },
  statusBad: {
    color: '#b91c1c',
  },
  eventList: {
    maxHeight: 160,
  },
  eventItem: {
    fontSize: 12,
    color: '#2e2e2e',
    marginBottom: 6,
  },
  eventEmpty: {
    fontSize: 12,
    color: '#7b7b7b',
  },
  outputRow: {
    marginBottom: 14,
  },
  outputLabel: {
    fontSize: 12,
    color: '#6a6a6a',
    marginBottom: 6,
  },
  outputEmpty: {
    fontSize: 12,
    color: '#9a9a9a',
  },
  outputLink: {
    fontSize: 12,
    color: '#2f6cff',
  },
  outputImage: {
    width: '100%',
    height: 200,
    borderRadius: 12,
  },
});
