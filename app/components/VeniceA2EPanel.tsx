import React, { useCallback, useEffect, useMemo, useState } from 'react';
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
type HistoryEntry = {
  id: number;
  step: string;
  idea?: string | null;
  title?: string | null;
  image_prompt?: string | null;
  video_prompt?: string | null;
  audio_text?: string | null;
  negative_prompt?: string | null;
  aspect_ratio?: string | null;
  video_time?: number | null;
  audio_language?: string | null;
  venice_model?: string | null;
  image_url?: string | null;
  video_url?: string | null;
  audio_url?: string | null;
  talking_video_url?: string | null;
  queue_id?: string | null;
  image_source_url?: string | null;
  video_source_url?: string | null;
  audio_source_url?: string | null;
  talking_source_url?: string | null;
  image_media_url?: string | null;
  video_media_url?: string | null;
  audio_media_url?: string | null;
  talking_media_url?: string | null;
  created_at?: string | null;
};

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

const veniceTextModels = [
  { value: 'venice-uncensored', label: 'Venice Uncensored 1.1' },
  { value: 'qwen3-4b', label: 'Venice Small (qwen3-4b)' },
  { value: 'mistral-31-24b', label: 'Venice Medium (mistral-31-24b)' },
  { value: 'zai-org-glm-4.7', label: 'GLM 4.7 (zai-org-glm-4.7)' },
  { value: 'qwen3-235b-a22b-instruct-2507', label: 'Qwen 3 235B Instruct' },
  { value: 'qwen3-235b-a22b-thinking-2507', label: 'Qwen 3 235B Thinking' },
  { value: 'qwen3-next-80b', label: 'Qwen 3 Next 80B' },
  { value: 'qwen3-coder-480b-a35b-instruct', label: 'Qwen 3 Coder 480B' },
  { value: 'llama-3.3-70b', label: 'Llama 3.3 70B' },
  { value: 'llama-3.2-3b', label: 'Llama 3.2 3B' },
  { value: 'deepseek-v3.2', label: 'DeepSeek V3.2' },
  { value: 'kimi-k2-thinking', label: 'Kimi K2 Thinking' },
  { value: 'openai-gpt-52', label: 'GPT-5.2' },
  { value: 'openai-gpt-52-codex', label: 'GPT-5.2 Codex' },
  { value: 'claude-sonnet-45', label: 'Claude Sonnet 4.5' },
  { value: 'claude-opus-45', label: 'Claude Opus 4.5' },
  { value: 'grok-41-fast', label: 'Grok 4.1 Fast' },
  { value: 'gemini-3-flash-preview', label: 'Gemini 3 Flash Preview' },
  { value: 'gemini-3-pro-preview', label: 'Gemini 3 Pro Preview' },
  { value: 'openai-gpt-oss-120b', label: 'OpenAI GPT OSS 120B' },
  { value: 'minimax-m21', label: 'MiniMax M2.1' },
  { value: 'grok-code-fast-1', label: 'Grok Code Fast 1' },
];

const wanOptions = {
  model: [
    { value: 'wan2.6-i2v', label: 'Wan 2.6 (i2v)' },
    { value: 'wan2.6-i2v-flash', label: 'Wan 2.6 Flash (i2v)' },
    { value: 'wan2.5-i2v-preview', label: 'Wan 2.5 Preview (i2v)' },
  ],
  duration: [
    { value: '5', label: '5s' },
    { value: '10', label: '10s' },
    { value: '15', label: '15s' },
  ],
  resolution: [
    { value: '720p', label: '720p' },
    { value: '1080p', label: '1080p' },
    { value: '480p', label: '480p' },
  ],
  audio: [
    { value: true, label: 'On' },
    { value: false, label: 'Off' },
  ],
};

const toneStyle = (tone: StatusTone) =>
  tone === 'good' ? styles.statusGood : tone === 'bad' ? styles.statusBad : styles.statusNeutral;

export default function VeniceA2EPanel({ apiUrl }: VeniceA2EPanelProps) {
  const [engine, setEngine] = useState<'a2e' | 'wan'>('a2e');
  const [idea, setIdea] = useState('');
  const [title, setTitle] = useState('');
  const [imagePrompt, setImagePrompt] = useState('');
  const [videoPrompt, setVideoPrompt] = useState('');
  const [audioText, setAudioText] = useState('');
  const [veniceModel, setVeniceModel] = useState('venice-uncensored');
  const [aspectRatio, setAspectRatio] = useState('9:16');
  const [videoTime, setVideoTime] = useState('10');
  const [wanDuration, setWanDuration] = useState('10');
  const [wanModel, setWanModel] = useState('wan2.6-i2v');
  const [wanResolution, setWanResolution] = useState('720p');
  const [wanAudio, setWanAudio] = useState(true);
  const [wanQueueId, setWanQueueId] = useState<string | null>(null);
  const [wanQueueStatus, setWanQueueStatus] = useState('');
  const [wanQueueTone, setWanQueueTone] = useState<StatusTone>('neutral');
  const [audioLanguage, setAudioLanguage] = useState('auto');
  const [negativePrompt, setNegativePrompt] = useState(DEFAULT_NEGATIVE_PROMPT);
  const [events, setEvents] = useState<EventEntry[]>([]);
  const [status, setStatus] = useState('');
  const [statusTone, setStatusTone] = useState<StatusTone>('neutral');
  const [imageStatus, setImageStatus] = useState('');
  const [imageTone, setImageTone] = useState<StatusTone>('neutral');
  const [videoStatus, setVideoStatus] = useState('');
  const [videoTone, setVideoTone] = useState<StatusTone>('neutral');
  const [audioStatus, setAudioStatus] = useState('');
  const [audioTone, setAudioTone] = useState<StatusTone>('neutral');
  const [busyPrompts, setBusyPrompts] = useState(false);
  const [busyImage, setBusyImage] = useState(false);
  const [busyVideo, setBusyVideo] = useState(false);
  const [busyAudio, setBusyAudio] = useState(false);
  const [busyRun, setBusyRun] = useState(false);
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [videoUrl, setVideoUrl] = useState<string | null>(null);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [talkingVideoUrl, setTalkingVideoUrl] = useState<string | null>(null);
  const [imageSourceUrl, setImageSourceUrl] = useState<string | null>(null);
  const [videoSourceUrl, setVideoSourceUrl] = useState<string | null>(null);
  const [modelMenuOpen, setModelMenuOpen] = useState(false);
  const [historyItems, setHistoryItems] = useState<HistoryEntry[]>([]);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [historyError, setHistoryError] = useState('');

  const isWan = engine === 'wan';
  const canGenerate = idea.trim().length > 0;
  const canRun = isWan
    ? idea.trim().length > 0 || (imagePrompt.trim().length > 0 && videoPrompt.trim().length > 0)
    : idea.trim().length > 0 ||
      (imagePrompt.trim().length > 0 && videoPrompt.trim().length > 0 && audioText.trim().length > 0);
  const canGenerateImage = idea.trim().length > 0 || imagePrompt.trim().length > 0;
  const canGenerateVideo = Boolean(imageUrl) && (idea.trim().length > 0 || videoPrompt.trim().length > 0);
  const canGenerateAudio =
    !isWan &&
    Boolean(videoUrl) &&
    (idea.trim().length > 0 || (audioText.trim().length > 0 && videoPrompt.trim().length > 0));
  const resolveMediaUrl = useCallback(
    (value?: string | null) => {
      if (!value) return null;
      if (value.startsWith('http://') || value.startsWith('https://')) return value;
      if (value.startsWith('/media/')) return `${apiUrl}${value}`;
      const normalized = value.replace(/\\/g, '/');
      const marker = '/DATA/';
      const markerIndex = normalized.indexOf(marker);
      if (markerIndex >= 0) {
        const relative = normalized.slice(markerIndex + marker.length);
        return `${apiUrl}/media/${encodeURI(relative)}`;
      }
      return `${apiUrl}${value}`;
    },
    [apiUrl],
  );

  const isRemoteUrl = useCallback((value?: string | null) => {
    if (!value) return false;
    return value.startsWith('http://') || value.startsWith('https://');
  }, []);

  const formatHistoryTimestamp = useCallback((value?: string | null) => {
    if (!value) return '';
    try {
      return new Date(value).toLocaleString();
    } catch (_err) {
      return value;
    }
  }, []);

  const loadHistory = useCallback(async () => {
    setHistoryLoading(true);
    setHistoryError('');
    try {
      const resp = await fetch(`${apiUrl}/api/venice-a2e/history?limit=20`);
      const json = await resp.json();
      if (!resp.ok) {
        throw new Error(json.error || json.details || resp.statusText);
      }
      setHistoryItems(json.items || []);
    } catch (err: any) {
      setHistoryError(err?.message || String(err));
    } finally {
      setHistoryLoading(false);
    }
  }, [apiUrl]);

  const mergeHistoryEntry = useCallback(
    (entry: HistoryEntry) => {
      if (!historyItems.length) return entry;
      const ideaKey = entry.idea?.trim();
      const titleKey = entry.title?.trim();
      if (!ideaKey && !titleKey) return entry;
      const matches = historyItems.filter((item) => {
        if (item.id === entry.id) return false;
        if (ideaKey && item.idea?.trim() === ideaKey) return true;
        if (titleKey && item.title?.trim() === titleKey) return true;
        return false;
      });
      if (!matches.length) return entry;
      const pickField = <K extends keyof HistoryEntry>(key: K) =>
        entry[key] ?? matches.find((item) => item[key])?.[key] ?? null;
      return {
        ...entry,
        image_prompt: pickField('image_prompt'),
        video_prompt: pickField('video_prompt'),
        audio_text: pickField('audio_text'),
        queue_id: pickField('queue_id'),
        negative_prompt: pickField('negative_prompt'),
        aspect_ratio: pickField('aspect_ratio'),
        video_time: pickField('video_time'),
        audio_language: pickField('audio_language'),
        venice_model: pickField('venice_model'),
        image_source_url: pickField('image_source_url'),
        video_source_url: pickField('video_source_url'),
      };
    },
    [historyItems],
  );

  const applyHistory = useCallback(
    (entry: HistoryEntry) => {
      const merged = mergeHistoryEntry(entry);
      if (merged.idea !== undefined && merged.idea !== null) setIdea(merged.idea);
      if (merged.title !== undefined && merged.title !== null) setTitle(merged.title);
      if (merged.image_prompt !== undefined && merged.image_prompt !== null) setImagePrompt(merged.image_prompt);
      if (merged.video_prompt !== undefined && merged.video_prompt !== null) setVideoPrompt(merged.video_prompt);
      if (merged.audio_text !== undefined && merged.audio_text !== null) setAudioText(merged.audio_text);
      if (merged.negative_prompt !== undefined && merged.negative_prompt !== null) {
        setNegativePrompt(merged.negative_prompt);
      }
      if (merged.aspect_ratio) setAspectRatio(merged.aspect_ratio);
      if (merged.audio_language) setAudioLanguage(merged.audio_language);
      if (merged.venice_model) setVeniceModel(merged.venice_model);
      if (merged.video_time) {
        const nextTime = String(merged.video_time);
        setVideoTime(nextTime);
        setWanDuration(nextTime);
      }
      if (merged.image_url !== undefined) setImageUrl(merged.image_url || null);
      if (merged.video_url !== undefined) setVideoUrl(merged.video_url || null);
      if (merged.audio_url !== undefined) setAudioUrl(merged.audio_url || null);
      if (merged.talking_video_url !== undefined) setTalkingVideoUrl(merged.talking_video_url || null);
      if (merged.queue_id !== undefined) setWanQueueId(merged.queue_id || null);
      if (merged.image_source_url !== undefined) setImageSourceUrl(merged.image_source_url || null);
      if (merged.video_source_url !== undefined) setVideoSourceUrl(merged.video_source_url || null);
    },
    [mergeHistoryEntry],
  );

  const appendEvents = useCallback((incoming?: EventEntry[] | null) => {
    if (!incoming || incoming.length === 0) return;
    setEvents((prev) => [...prev, ...incoming]);
  }, []);

  const appendEventsFromPayload = useCallback(
    (payload: any) => {
      if (!payload) return;
      const incoming = Array.isArray(payload.events)
        ? payload.events
        : Array.isArray(payload.details?.events)
          ? payload.details.events
          : [];
      appendEvents(incoming);
    },
    [appendEvents],
  );

  const extractWanQueueId = useCallback((payload: any): string | null => {
    const direct =
      payload?.queue_id ||
      payload?.queueId ||
      payload?.task_id ||
      payload?.taskId ||
      payload?.details?.queue_id ||
      payload?.details?.queueId ||
      payload?.details?.task_id ||
      payload?.details?.taskId ||
      payload?.payload?.task_id;
    if (typeof direct === 'string' && direct.trim()) {
      return direct.trim();
    }
    const data = payload?.payload?.data || payload?.details?.data;
    const dataId = data?._id || data?.id || data?.task_id;
    if (typeof dataId === 'string' && dataId.trim()) {
      return dataId.trim();
    }
    return null;
  }, []);

  const pollWanStatus = useCallback(
    async (queueId?: string | null) => {
      const target = (queueId || wanQueueId || '').trim();
      if (!target) return false;
      try {
        const resp = await fetch(`${apiUrl}/api/venice-a2e/wan/status/${encodeURIComponent(target)}`);
        const json = await resp.json();
        if (!resp.ok) {
          setWanQueueStatus(`Task status failed: ${json.error || json.details || resp.statusText}`);
          setWanQueueTone('bad');
          return false;
        }
        const payload = json.payload || {};
        const data = payload.data || payload;
        const status = String(
          data.current_status || data.status || payload.status || 'unknown',
        ).toLowerCase();
        const failedMessage =
          data.failed_message || data.failedMessage || payload.failed_message || payload.failedMessage;
        const resultUrl = data.result_url || data.resultUrl || payload.result_url || payload.resultUrl;
        let message = `Task status: ${status}`;
        if (resultUrl) message += ' (result ready)';
        if (failedMessage) message += ` - ${failedMessage}`;
        setWanQueueStatus(message);
        if (status.includes('fail') || status.includes('error') || failedMessage) {
          setWanQueueTone('bad');
        } else if (status.includes('ready') || status.includes('success') || resultUrl) {
          setWanQueueTone('good');
        } else {
          setWanQueueTone('neutral');
        }
        return Boolean(
          resultUrl ||
            status.includes('ready') ||
            status.includes('success') ||
            status.includes('fail') ||
            status.includes('error') ||
            status.includes('canceled'),
        );
      } catch (err: any) {
        setWanQueueStatus(`Task status failed: ${err?.message || String(err)}`);
        setWanQueueTone('bad');
        return false;
      }
    },
    [apiUrl, wanQueueId],
  );

  useEffect(() => {
    if (!isWan || !wanQueueId) return;
    let cancelled = false;
    let timer: ReturnType<typeof setInterval> | null = null;
    const poll = async () => {
      if (cancelled) return;
      const done = await pollWanStatus(wanQueueId);
      if (done && timer) {
        clearInterval(timer);
        timer = null;
      }
    };
    poll();
    timer = setInterval(poll, 15000);
    return () => {
      cancelled = true;
      if (timer) clearInterval(timer);
    };
  }, [isWan, pollWanStatus, wanQueueId]);

  useEffect(() => {
    loadHistory();
  }, [loadHistory]);

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
    setEvents([]);
    try {
      const resp = await fetch(`${apiUrl}/api/venice-a2e/prompts`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          idea: idea.trim(),
          title: title.trim() || undefined,
          audio_language: audioLanguage,
          venice_model: veniceModel,
        }),
      });
      const json = await resp.json();
      if (!resp.ok) {
        appendEventsFromPayload(json);
        setStatus(`Prompt generation failed: ${json.error || json.details || resp.statusText}`);
        setStatusTone('bad');
        return;
      }
      if (json.title) {
        setTitle(json.title);
      } else if (json.prompts?.title) {
        setTitle(json.prompts.title);
      }
      setImagePrompt(json.image_prompt || '');
      setVideoPrompt(json.video_prompt || '');
      setAudioText(json.audio_text || '');
      setEvents(json.events || []);
      setStatus('Prompts ready. Generate outputs step by step.');
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
    if (!idea.trim() && !(imagePrompt.trim() && videoPrompt.trim() && (isWan || audioText.trim()))) {
      setStatus(isWan ? 'Add an idea prompt or fill image and video prompts.' : 'Add an idea prompt or fill all three prompts.');
      setStatusTone('bad');
      return;
    }
    setBusyRun(true);
    setStatus(
      isWan
        ? 'Running Venice + Wan pipeline. This can take a few minutes...'
        : 'Running full Venice + A2E pipeline. This can take a few minutes...',
    );
    setStatusTone('neutral');
    if (isWan) {
      setWanQueueStatus('');
      setWanQueueTone('neutral');
    }
    setEvents([]);
    setImageUrl(null);
    setVideoUrl(null);
    setAudioUrl(null);
    setTalkingVideoUrl(null);
    setImageSourceUrl(null);
    setVideoSourceUrl(null);
    setImageStatus('');
    setImageTone('neutral');
    setVideoStatus('');
    setVideoTone('neutral');
    setAudioStatus('');
    setAudioTone('neutral');
    try {
      const resp = await fetch(
        isWan ? `${apiUrl}/api/venice-a2e/wan/run` : `${apiUrl}/api/venice-a2e/run`,
        {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          idea: idea.trim(),
          title: title.trim() || undefined,
          image_prompt: imagePrompt.trim() || undefined,
          video_prompt: videoPrompt.trim() || undefined,
          audio_text: audioText.trim() || undefined,
          audio_language: audioLanguage,
          venice_model: veniceModel,
          aspect_ratio: aspectRatio,
          video_time: parseInt(isWan ? wanDuration : videoTime, 10),
          negative_prompt: negativePrompt.trim() || undefined,
          ...(isWan
            ? {
                wan_model: wanModel,
                resolution: wanResolution,
                audio: wanAudio,
              }
            : {}),
        }),
      },
      );
      const json = await resp.json();
      if (!resp.ok) {
        appendEventsFromPayload(json);
        if (isWan) {
          const queued = extractWanQueueId(json);
          if (queued) {
            setWanQueueId(queued);
          }
        }
        setStatus(`Pipeline failed: ${json.error || json.details || resp.statusText}`);
        setStatusTone('bad');
        return;
      }
      if (json.title) setTitle(json.title);
      if (isWan) {
        const queued = extractWanQueueId(json);
        if (queued) {
          setWanQueueId(queued);
        }
      }
      setImageUrl(json.image_url || null);
      setVideoUrl(json.video_url || null);
      setAudioUrl(json.audio_url || null);
      setTalkingVideoUrl(json.talking_video_url || null);
      if (json.image_source_url) {
        setImageSourceUrl(json.image_source_url);
      } else if (isRemoteUrl(json.image_url)) {
        setImageSourceUrl(json.image_url);
      }
      if (json.video_source_url) {
        setVideoSourceUrl(json.video_source_url);
      } else if (isRemoteUrl(json.video_url)) {
        setVideoSourceUrl(json.video_url);
      }
      if (json.image_url) {
        setImageStatus('Image ready.');
        setImageTone('good');
      }
      if (json.video_url) {
        setVideoStatus('Video ready.');
        setVideoTone('good');
      }
      if (json.audio_url || json.talking_video_url) {
        setAudioStatus('Audio ready.');
        setAudioTone('good');
      }
      if (json.image_prompt) setImagePrompt(json.image_prompt);
      if (json.video_prompt) setVideoPrompt(json.video_prompt);
      if (json.audio_text) setAudioText(json.audio_text);
      setEvents(json.events || []);
      setStatus('Pipeline complete.');
      setStatusTone('good');
      loadHistory();
    } catch (err: any) {
      setStatus(`Pipeline failed: ${err?.message || String(err)}`);
      setStatusTone('bad');
    } finally {
      setBusyRun(false);
    }
  };

  const runImage = async (override?: {
    idea?: string;
    title?: string;
    imagePrompt?: string;
    audioLanguage?: string;
    veniceModel?: string;
    aspectRatio?: string;
  }) => {
    if (busyImage) return;
    const nextIdea = override?.idea !== undefined ? override.idea : idea;
    const nextTitle = override?.title !== undefined ? override.title : title;
    const nextImagePrompt = override?.imagePrompt !== undefined ? override.imagePrompt : imagePrompt;
    const nextAudioLanguage = override?.audioLanguage !== undefined ? override.audioLanguage : audioLanguage;
    const nextVeniceModel = override?.veniceModel !== undefined ? override.veniceModel : veniceModel;
    const nextAspectRatio = override?.aspectRatio !== undefined ? override.aspectRatio : aspectRatio;
    if (override?.idea !== undefined) setIdea(nextIdea);
    if (override?.title !== undefined) setTitle(nextTitle);
    if (override?.imagePrompt !== undefined) setImagePrompt(nextImagePrompt);
    if (override?.audioLanguage !== undefined) setAudioLanguage(nextAudioLanguage);
    if (override?.veniceModel !== undefined) setVeniceModel(nextVeniceModel);
    if (override?.aspectRatio !== undefined) setAspectRatio(nextAspectRatio);
    if (!nextIdea.trim() && !nextImagePrompt.trim()) {
      setImageStatus('Add an idea or image prompt first.');
      setImageTone('bad');
      return;
    }
    setBusyImage(true);
    setImageStatus('Generating image...');
    setImageTone('neutral');
    setImageUrl(null);
    setVideoUrl(null);
    setAudioUrl(null);
    setTalkingVideoUrl(null);
    setImageSourceUrl(null);
    setVideoSourceUrl(null);
    setVideoStatus('');
    setVideoTone('neutral');
    setAudioStatus('');
    setAudioTone('neutral');
    try {
      const resp = await fetch(`${apiUrl}/api/venice-a2e/image`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          idea: nextIdea.trim(),
          title: nextTitle.trim() || undefined,
          image_prompt: nextImagePrompt.trim() || undefined,
          audio_language: nextAudioLanguage,
          venice_model: nextVeniceModel,
          aspect_ratio: nextAspectRatio,
        }),
      });
      const json = await resp.json();
      appendEventsFromPayload(json);
      if (!resp.ok) {
        setImageStatus(`Image failed: ${json.error || json.details?.message || json.details || resp.statusText}`);
        setImageTone('bad');
        return;
      }
      if (json.title) setTitle(json.title);
      if (json.image_prompt) setImagePrompt(json.image_prompt);
      setImageUrl(json.image_url || null);
      if (json.image_source_url) {
        setImageSourceUrl(json.image_source_url);
      } else if (isRemoteUrl(json.image_url)) {
        setImageSourceUrl(json.image_url);
      }
      setImageStatus(json.image_url ? 'Image ready.' : 'Image complete.');
      setImageTone('good');
      loadHistory();
    } catch (err: any) {
      setImageStatus(`Image failed: ${err?.message || String(err)}`);
      setImageTone('bad');
    } finally {
      setBusyImage(false);
    }
  };

  const runVideo = async (override?: {
    idea?: string;
    title?: string;
    imageUrl?: string | null;
    imageSourceUrl?: string | null;
    videoPrompt?: string;
    audioLanguage?: string;
    veniceModel?: string;
    videoTime?: string | number;
    negativePrompt?: string;
  }) => {
    if (busyVideo) return;
    const nextIdea = override?.idea !== undefined ? override.idea : idea;
    const nextTitle = override?.title !== undefined ? override.title : title;
    const nextImageUrl = override?.imageUrl !== undefined ? override.imageUrl : imageUrl;
    const nextImageSourceUrl =
      override?.imageSourceUrl !== undefined ? override.imageSourceUrl : imageSourceUrl;
    const imageForGeneration =
      nextImageSourceUrl || (isRemoteUrl(nextImageUrl) ? nextImageUrl : null) || nextImageUrl;
    const nextVideoPrompt = override?.videoPrompt !== undefined ? override.videoPrompt : videoPrompt;
    const nextAudioLanguage = override?.audioLanguage !== undefined ? override.audioLanguage : audioLanguage;
    const nextVeniceModel = override?.veniceModel !== undefined ? override.veniceModel : veniceModel;
    const nextVideoTime = override?.videoTime !== undefined ? override.videoTime : videoTime;
    const nextNegativePrompt =
      override?.negativePrompt !== undefined ? override.negativePrompt : negativePrompt;
    if (override?.idea !== undefined) setIdea(nextIdea);
    if (override?.title !== undefined) setTitle(nextTitle);
    if (override?.imageUrl !== undefined) setImageUrl(nextImageUrl || null);
    if (override?.videoPrompt !== undefined) setVideoPrompt(nextVideoPrompt);
    if (override?.imageSourceUrl !== undefined) setImageSourceUrl(nextImageSourceUrl || null);
    if (override?.audioLanguage !== undefined) setAudioLanguage(nextAudioLanguage);
    if (override?.veniceModel !== undefined) setVeniceModel(nextVeniceModel);
    if (override?.videoTime !== undefined) setVideoTime(String(nextVideoTime || ''));
    if (override?.negativePrompt !== undefined) setNegativePrompt(nextNegativePrompt);
    if (!nextImageUrl) {
      setVideoStatus('Generate an image first.');
      setVideoTone('bad');
      return;
    }
    if (!nextIdea.trim() && !nextVideoPrompt.trim()) {
      setVideoStatus('Add an idea or video prompt first.');
      setVideoTone('bad');
      return;
    }
    setBusyVideo(true);
    setVideoStatus('Generating video...');
    setVideoTone('neutral');
    setVideoUrl(null);
    setAudioUrl(null);
    setTalkingVideoUrl(null);
    setVideoSourceUrl(null);
    setAudioStatus('');
    setAudioTone('neutral');
    try {
      const resp = await fetch(`${apiUrl}/api/venice-a2e/video`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          idea: nextIdea.trim(),
          title: nextTitle.trim() || undefined,
          image_url: imageForGeneration,
          image_source_url: nextImageSourceUrl || undefined,
          video_prompt: nextVideoPrompt.trim() || undefined,
          audio_language: nextAudioLanguage,
          venice_model: nextVeniceModel,
          video_time: parseInt(String(nextVideoTime || ''), 10),
          negative_prompt: nextNegativePrompt.trim() || undefined,
        }),
      });
      const json = await resp.json();
      appendEventsFromPayload(json);
      if (!resp.ok) {
        setVideoStatus(`Video failed: ${json.error || json.details?.message || json.details || resp.statusText}`);
        setVideoTone('bad');
        return;
      }
      if (json.title) setTitle(json.title);
      if (json.video_prompt) setVideoPrompt(json.video_prompt);
      setVideoUrl(json.video_url || null);
      if (json.video_source_url) {
        setVideoSourceUrl(json.video_source_url);
      } else if (isRemoteUrl(json.video_url)) {
        setVideoSourceUrl(json.video_url);
      }
      setVideoStatus(json.video_url ? 'Video ready.' : 'Video complete.');
      setVideoTone('good');
      loadHistory();
    } catch (err: any) {
      setVideoStatus(`Video failed: ${err?.message || String(err)}`);
      setVideoTone('bad');
    } finally {
      setBusyVideo(false);
    }
  };

  const runWanVideo = async (override?: {
    idea?: string;
    title?: string;
    imageUrl?: string | null;
    imageSourceUrl?: string | null;
    videoPrompt?: string;
    audioText?: string;
    audioLanguage?: string;
    veniceModel?: string;
    videoTime?: string | number;
    negativePrompt?: string;
    wanModel?: string;
    wanResolution?: string;
    wanAudio?: boolean;
    queueId?: string | null;
  }) => {
    if (busyVideo) return;
    const nextIdea = override?.idea !== undefined ? override.idea : idea;
    const nextTitle = override?.title !== undefined ? override.title : title;
    const nextImageUrl = override?.imageUrl !== undefined ? override.imageUrl : imageUrl;
    const nextImageSourceUrl =
      override?.imageSourceUrl !== undefined ? override.imageSourceUrl : imageSourceUrl;
    const imageForGeneration =
      nextImageSourceUrl || (isRemoteUrl(nextImageUrl) ? nextImageUrl : null) || nextImageUrl;
    const nextVideoPrompt = override?.videoPrompt !== undefined ? override.videoPrompt : videoPrompt;
    const nextAudioText = override?.audioText !== undefined ? override.audioText : audioText;
    const nextAudioLanguage = override?.audioLanguage !== undefined ? override.audioLanguage : audioLanguage;
    const nextVeniceModel = override?.veniceModel !== undefined ? override.veniceModel : veniceModel;
    const nextWanDuration =
      override?.videoTime !== undefined ? String(override.videoTime) : wanDuration;
    const nextNegativePrompt =
      override?.negativePrompt !== undefined ? override.negativePrompt : negativePrompt;
    const nextWanModel = override?.wanModel !== undefined ? override.wanModel : wanModel;
    const nextWanResolution =
      override?.wanResolution !== undefined ? override.wanResolution : wanResolution;
    const nextWanAudio = override?.wanAudio !== undefined ? override.wanAudio : wanAudio;
    const nextQueueId =
      override?.queueId !== undefined ? override.queueId : wanQueueId;
    if (override?.idea !== undefined) setIdea(nextIdea);
    if (override?.title !== undefined) setTitle(nextTitle);
    if (override?.imageUrl !== undefined) setImageUrl(nextImageUrl || null);
    if (override?.videoPrompt !== undefined) setVideoPrompt(nextVideoPrompt);
    if (override?.audioText !== undefined) setAudioText(nextAudioText);
    if (override?.imageSourceUrl !== undefined) setImageSourceUrl(nextImageSourceUrl || null);
    if (override?.audioLanguage !== undefined) setAudioLanguage(nextAudioLanguage);
    if (override?.veniceModel !== undefined) setVeniceModel(nextVeniceModel);
    if (override?.videoTime !== undefined) setWanDuration(String(nextWanDuration || ''));
    if (override?.negativePrompt !== undefined) setNegativePrompt(nextNegativePrompt);
    if (override?.wanModel !== undefined) setWanModel(nextWanModel);
    if (override?.wanResolution !== undefined) setWanResolution(nextWanResolution);
    if (override?.wanAudio !== undefined) setWanAudio(nextWanAudio);
    if (nextQueueId) {
      setWanQueueId(nextQueueId || null);
    }
    if (!nextImageUrl && !nextQueueId) {
      setVideoStatus('Generate an image first.');
      setVideoTone('bad');
      return;
    }
    if (!nextQueueId && !nextIdea.trim() && !nextVideoPrompt.trim()) {
      setVideoStatus('Add an idea or video prompt first.');
      setVideoTone('bad');
      return;
    }
    setBusyVideo(true);
    setVideoStatus('Generating Wan video...');
    setVideoTone('neutral');
    setWanQueueStatus('');
    setWanQueueTone('neutral');
    setVideoUrl(null);
    setAudioUrl(null);
    setTalkingVideoUrl(null);
    setVideoSourceUrl(null);
    setAudioStatus('');
    setAudioTone('neutral');
    try {
      const resp = await fetch(`${apiUrl}/api/venice-a2e/wan/video`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          idea: nextIdea.trim(),
          title: nextTitle.trim() || undefined,
          image_url: imageForGeneration,
          image_source_url: nextImageSourceUrl || undefined,
          video_prompt: nextVideoPrompt.trim() || undefined,
          audio_text: nextAudioText.trim() || undefined,
          audio_language: nextAudioLanguage,
          venice_model: nextVeniceModel,
          video_time: parseInt(String(nextWanDuration || ''), 10),
          negative_prompt: nextNegativePrompt.trim() || undefined,
          wan_model: nextWanModel,
          resolution: nextWanResolution,
          audio: nextWanAudio,
          ...(nextQueueId ? { queue_id: nextQueueId } : {}),
        }),
      });
      const json = await resp.json();
      appendEventsFromPayload(json);
      if (!resp.ok) {
        const queued = extractWanQueueId(json);
        if (queued) {
          setWanQueueId(queued);
        }
        setVideoStatus(`Video failed: ${json.error || json.details?.message || json.details || resp.statusText}`);
        setVideoTone('bad');
        return;
      }
      if (json.title) setTitle(json.title);
      if (json.video_prompt) setVideoPrompt(json.video_prompt);
      if (json.audio_text) setAudioText(json.audio_text);
      const queued = extractWanQueueId(json);
      if (queued) {
        setWanQueueId(queued);
      }
      setVideoUrl(json.video_url || null);
      if (json.video_source_url) {
        setVideoSourceUrl(json.video_source_url);
      } else if (isRemoteUrl(json.video_url)) {
        setVideoSourceUrl(json.video_url);
      }
      setVideoStatus(json.video_url ? 'Video ready.' : 'Video complete.');
      setVideoTone('good');
      loadHistory();
    } catch (err: any) {
      setVideoStatus(`Video failed: ${err?.message || String(err)}`);
      setVideoTone('bad');
    } finally {
      setBusyVideo(false);
    }
  };

  const runAudio = async (override?: {
    idea?: string;
    title?: string;
    videoUrl?: string | null;
    videoSourceUrl?: string | null;
    audioText?: string;
    audioUrl?: string | null;
    videoPrompt?: string;
    audioLanguage?: string;
    veniceModel?: string;
    videoTime?: string | number;
    negativePrompt?: string;
  }) => {
    if (busyAudio) return;
    const nextIdea = override?.idea !== undefined ? override.idea : idea;
    const nextTitle = override?.title !== undefined ? override.title : title;
    const nextVideoUrl = override?.videoUrl !== undefined ? override.videoUrl : videoUrl;
    const nextVideoSourceUrl =
      override?.videoSourceUrl !== undefined ? override.videoSourceUrl : videoSourceUrl;
    const videoForGeneration =
      nextVideoSourceUrl || (isRemoteUrl(nextVideoUrl) ? nextVideoUrl : null) || nextVideoUrl;
    const nextAudioText = override?.audioText !== undefined ? override.audioText : audioText;
    const nextAudioUrl = override?.audioUrl !== undefined ? override.audioUrl : null;
    const nextVideoPrompt = override?.videoPrompt !== undefined ? override.videoPrompt : videoPrompt;
    const nextAudioLanguage = override?.audioLanguage !== undefined ? override.audioLanguage : audioLanguage;
    const nextVeniceModel = override?.veniceModel !== undefined ? override.veniceModel : veniceModel;
    const nextVideoTime = override?.videoTime !== undefined ? override.videoTime : videoTime;
    const nextNegativePrompt =
      override?.negativePrompt !== undefined ? override.negativePrompt : negativePrompt;
    if (override?.idea !== undefined) setIdea(nextIdea);
    if (override?.title !== undefined) setTitle(nextTitle);
    if (override?.videoUrl !== undefined) setVideoUrl(nextVideoUrl || null);
    if (override?.audioText !== undefined) setAudioText(nextAudioText);
    if (override?.videoPrompt !== undefined) setVideoPrompt(nextVideoPrompt);
    if (override?.videoSourceUrl !== undefined) setVideoSourceUrl(nextVideoSourceUrl || null);
    if (override?.audioLanguage !== undefined) setAudioLanguage(nextAudioLanguage);
    if (override?.veniceModel !== undefined) setVeniceModel(nextVeniceModel);
    if (override?.videoTime !== undefined) setVideoTime(String(nextVideoTime || ''));
    if (override?.negativePrompt !== undefined) setNegativePrompt(nextNegativePrompt);
    if (!nextVideoUrl) {
      setAudioStatus('Generate a video first.');
      setAudioTone('bad');
      return;
    }
    const hasAudioUrl = Boolean(nextAudioUrl && String(nextAudioUrl).trim());
    if (!nextIdea.trim() && !hasAudioUrl && !(nextAudioText.trim() && nextVideoPrompt.trim())) {
      setAudioStatus('Add an idea, an audio URL, or fill both audio text and video prompt.');
      setAudioTone('bad');
      return;
    }
    setBusyAudio(true);
    setAudioStatus('Generating audio and talking video...');
    setAudioTone('neutral');
    setAudioUrl(null);
    setTalkingVideoUrl(null);
    try {
      const resp = await fetch(`${apiUrl}/api/venice-a2e/audio`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          idea: nextIdea.trim(),
          title: nextTitle.trim() || undefined,
          video_url: videoForGeneration,
          video_source_url: nextVideoSourceUrl || undefined,
          audio_text: nextAudioText.trim() || undefined,
          audio_url: hasAudioUrl ? nextAudioUrl : undefined,
          video_prompt: nextVideoPrompt.trim() || undefined,
          audio_language: nextAudioLanguage,
          venice_model: nextVeniceModel,
          video_time: parseInt(String(nextVideoTime || ''), 10),
          negative_prompt: nextNegativePrompt.trim() || undefined,
        }),
      });
      const json = await resp.json();
      appendEventsFromPayload(json);
      if (!resp.ok) {
        setAudioStatus(`Audio failed: ${json.error || json.details?.message || json.details || resp.statusText}`);
        setAudioTone('bad');
        return;
      }
      if (json.title) setTitle(json.title);
      if (json.audio_text) setAudioText(json.audio_text);
      setAudioUrl(json.audio_url || null);
      setTalkingVideoUrl(json.talking_video_url || null);
      if (json.video_source_url) {
        setVideoSourceUrl(json.video_source_url);
      }
      setAudioStatus(json.audio_url || json.talking_video_url ? 'Audio ready.' : 'Audio complete.');
      setAudioTone('good');
      loadHistory();
    } catch (err: any) {
      setAudioStatus(`Audio failed: ${err?.message || String(err)}`);
      setAudioTone('bad');
    } finally {
      setBusyAudio(false);
    }
  };

  const runImageFromHistory = useCallback(
    (entry: HistoryEntry) => {
      const merged = mergeHistoryEntry(entry);
      applyHistory(merged);
      runImage({
        idea: merged.idea || '',
        title: merged.title || '',
        imagePrompt: merged.image_prompt || '',
        audioLanguage: merged.audio_language || audioLanguage,
        veniceModel: merged.venice_model || veniceModel,
        aspectRatio: merged.aspect_ratio || aspectRatio,
      });
    },
    [applyHistory, audioLanguage, aspectRatio, mergeHistoryEntry, runImage, veniceModel],
  );

  const runVideoFromHistory = useCallback(
    (entry: HistoryEntry) => {
      const merged = mergeHistoryEntry(entry);
      applyHistory(merged);
      const payload = {
        idea: merged.idea || '',
        title: merged.title || '',
        imageUrl: merged.image_url || null,
        imageSourceUrl: merged.image_source_url || null,
        videoPrompt: merged.video_prompt || '',
        audioText: merged.audio_text || '',
        audioLanguage: merged.audio_language || audioLanguage,
        veniceModel: merged.venice_model || veniceModel,
        videoTime: merged.video_time || (isWan ? wanDuration : videoTime),
        negativePrompt: merged.negative_prompt || negativePrompt,
        queueId: merged.queue_id || null,
      };
      if (isWan) {
        runWanVideo(payload);
      } else {
        runVideo(payload);
      }
    },
    [applyHistory, audioLanguage, isWan, mergeHistoryEntry, negativePrompt, runVideo, runWanVideo, veniceModel, videoTime, wanDuration],
  );

  const runAudioFromHistory = useCallback(
    (entry: HistoryEntry) => {
      const merged = mergeHistoryEntry(entry);
      applyHistory(merged);
      runAudio({
        idea: merged.idea || '',
        title: merged.title || '',
        videoUrl: merged.video_url || null,
        videoSourceUrl: merged.video_source_url || null,
        audioText: merged.audio_text || '',
        audioUrl: merged.audio_url || null,
        videoPrompt: merged.video_prompt || '',
        audioLanguage: merged.audio_language || audioLanguage,
        veniceModel: merged.venice_model || veniceModel,
        videoTime: merged.video_time || videoTime,
        negativePrompt: merged.negative_prompt || negativePrompt,
      });
    },
    [applyHistory, audioLanguage, mergeHistoryEntry, negativePrompt, runAudio, veniceModel, videoTime],
  );

  const veniceModelLabel = useMemo(
    () => veniceTextModels.find((model) => model.value === veniceModel)?.label || veniceModel,
    [veniceModel],
  );
  const durationOptions = isWan ? wanOptions.duration : chipOptions.videoTime;
  const durationValue = isWan ? wanDuration : videoTime;
  const setDurationValue = isWan ? setWanDuration : setVideoTime;

  return (
    <View style={styles.wrapper}>
      <Text style={styles.title}>Venice + A2E</Text>
      <Text style={styles.subtitle}>
        {isWan
          ? 'Generate prompts with Venice, then create image and Wan video (audio on by default).'
          : 'Generate prompts with Venice, then create image, video, and audio with A2E.'}
      </Text>

      <View style={styles.subTabRow}>
        {[
          { key: 'a2e', label: 'A2E' },
          { key: 'wan', label: 'Wan' },
        ].map((tab) => {
          const active = engine === tab.key;
          return (
            <Pressable
              key={tab.key}
              style={[styles.subTab, active && styles.subTabActive]}
              onPress={() => setEngine(tab.key as 'a2e' | 'wan')}
            >
              <Text style={[styles.subTabText, active && styles.subTabTextActive]}>{tab.label}</Text>
            </Pressable>
          );
        })}
      </View>

      <View style={styles.card}>
        <Text style={styles.sectionTitle}>Idea</Text>
        <TextInput
          style={styles.textArea}
          value={idea}
          onChangeText={setIdea}
          placeholder="Describe the story, vibe, and characters."
          multiline
        />
        <Text style={styles.label}>Title</Text>
        <TextInput
          style={styles.textInput}
          value={title}
          onChangeText={setTitle}
          placeholder="Short video title."
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
              {durationOptions.map((option) => {
                const active = durationValue === option.value;
                return (
                  <Pressable
                    key={option.value}
                    style={[styles.chip, active && styles.chipActive]}
                    onPress={() => setDurationValue(option.value)}
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

        <View style={styles.inlineRow}>
          <View style={styles.inlineBlock}>
            <Text style={styles.label}>Venice text model</Text>
            <View style={styles.dropdown}>
              <Pressable
                style={styles.dropdownButton}
                onPress={() => setModelMenuOpen((open) => !open)}
              >
                <Text style={styles.dropdownButtonText}>{veniceModelLabel}</Text>
                <Text style={styles.dropdownChevron}>{modelMenuOpen ? '▲' : '▼'}</Text>
              </Pressable>
              {modelMenuOpen && (
                <ScrollView style={styles.dropdownMenu} nestedScrollEnabled>
                  {veniceTextModels.map((option) => {
                    const active = veniceModel === option.value;
                    return (
                      <Pressable
                        key={option.value}
                        style={[styles.dropdownItem, active && styles.dropdownItemActive]}
                        onPress={() => {
                          setVeniceModel(option.value);
                          setModelMenuOpen(false);
                        }}
                      >
                        <Text style={[styles.dropdownItemText, active && styles.dropdownItemTextActive]}>
                          {option.label}
                        </Text>
                      </Pressable>
                    );
                  })}
                </ScrollView>
              )}
            </View>
          </View>
        </View>

        {isWan ? (
          <>
            <View style={styles.inlineRow}>
              <View style={styles.inlineBlock}>
                <Text style={styles.label}>Wan model</Text>
                <View style={styles.chipRow}>
                  {wanOptions.model.map((option) => {
                    const active = wanModel === option.value;
                    return (
                      <Pressable
                        key={option.value}
                        style={[styles.chip, active && styles.chipActive]}
                        onPress={() => setWanModel(option.value)}
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
                <Text style={styles.label}>Video size</Text>
                <View style={styles.chipRow}>
                  {wanOptions.resolution.map((option) => {
                    const active = wanResolution === option.value;
                    return (
                      <Pressable
                        key={option.value}
                        style={[styles.chip, active && styles.chipActive]}
                        onPress={() => setWanResolution(option.value)}
                      >
                        <Text style={[styles.chipText, active && styles.chipTextActive]}>{option.label}</Text>
                      </Pressable>
                    );
                  })}
                </View>
              </View>
              <View style={styles.inlineBlock}>
                <Text style={styles.label}>Audio</Text>
                <View style={styles.chipRow}>
                  {wanOptions.audio.map((option) => {
                    const active = wanAudio === option.value;
                    return (
                      <Pressable
                        key={String(option.value)}
                        style={[styles.chip, active && styles.chipActive]}
                        onPress={() => setWanAudio(option.value)}
                      >
                        <Text style={[styles.chipText, active && styles.chipTextActive]}>
                          {option.label}
                        </Text>
                      </Pressable>
                    );
                  })}
                </View>
              </View>
            </View>
          </>
        ) : null}

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
              <Text style={styles.secondaryButtonText}>
                {isWan ? 'Run Wan pipeline' : 'Run full pipeline'}
              </Text>
            </View>
          </Pressable>
        </View>

        {status ? <Text style={[styles.status, toneStyle(statusTone)]}>{status}</Text> : null}
      </View>

      <View style={styles.card}>
        <Text style={styles.sectionTitle}>Steps</Text>
        <Text style={styles.label}>Image prompt</Text>
        <TextInput
          style={styles.textArea}
          value={imagePrompt}
          onChangeText={setImagePrompt}
          placeholder="Still image prompt."
          multiline
        />
        <Pressable
          style={[styles.primaryButton, styles.stepButton, (!canGenerateImage || busyImage) && styles.buttonDisabled]}
          onPress={runImage}
          disabled={!canGenerateImage || busyImage}
        >
          <View style={styles.buttonContent}>
            {busyImage && <ActivityIndicator color="white" style={{ marginRight: 8 }} />}
            <Text style={styles.primaryButtonText}>Text -> Image</Text>
          </View>
        </Pressable>
        {imageStatus ? <Text style={[styles.status, toneStyle(imageTone)]}>{imageStatus}</Text> : null}
        <Text style={styles.outputLabel}>Image preview</Text>
        <View style={styles.previewFrame}>
          {imageUrl ? (
            <Image source={{ uri: resolveMediaUrl(imageUrl) || imageUrl }} style={styles.previewImage} resizeMode="contain" />
          ) : (
            <Text style={[styles.outputEmpty, styles.previewEmpty]}>Image not ready.</Text>
          )}
        </View>

        <Text style={styles.label}>Video prompt</Text>
        <TextInput
          style={styles.textArea}
          value={videoPrompt}
          onChangeText={setVideoPrompt}
          placeholder="Motion prompt."
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
        <Pressable
          style={[styles.primaryButton, styles.stepButton, (!canGenerateVideo || busyVideo) && styles.buttonDisabled]}
          onPress={isWan ? runWanVideo : runVideo}
          disabled={!canGenerateVideo || busyVideo}
        >
          <View style={styles.buttonContent}>
            {busyVideo && <ActivityIndicator color="white" style={{ marginRight: 8 }} />}
            <Text style={styles.primaryButtonText}>
              {isWan ? 'Image + prompt -> Wan video' : 'Image + prompt -> Video'}
            </Text>
          </View>
        </Pressable>
        {videoStatus ? <Text style={[styles.status, toneStyle(videoTone)]}>{videoStatus}</Text> : null}
        {isWan && wanQueueId ? (
          <>
            <Text style={styles.queueLabel}>Queue id: {wanQueueId}</Text>
            {wanQueueStatus ? (
              <Text style={[styles.status, toneStyle(wanQueueTone)]}>{wanQueueStatus}</Text>
            ) : null}
            <View style={styles.queueActions}>
              <Pressable style={styles.queueButton} onPress={() => pollWanStatus(wanQueueId)}>
                <Text style={styles.queueButtonText}>Poll task</Text>
              </Pressable>
              <Pressable style={styles.queueButton} onPress={() => runWanVideo({ queueId: wanQueueId })}>
                <Text style={styles.queueButtonText}>Resume download</Text>
              </Pressable>
            </View>
          </>
        ) : null}
        <Text style={styles.outputLabel}>Video preview</Text>
        {videoUrl ? (
          Platform.OS === 'web' ? (
            React.createElement('video', {
              src: resolveMediaUrl(videoUrl) || videoUrl,
              controls: true,
              style: { width: '100%', borderRadius: 12 },
            })
          ) : (
            <Text style={styles.outputLink}>{videoUrl}</Text>
          )
        ) : (
          <Text style={styles.outputEmpty}>Video not ready.</Text>
        )}

        <Text style={styles.label}>{isWan ? 'Dialogue text' : 'Audio text'}</Text>
        <TextInput
          style={styles.textArea}
          value={audioText}
          onChangeText={setAudioText}
          placeholder={isWan ? 'Optional spoken line to merge into the video prompt.' : 'Short narration.'}
          multiline
        />
        {isWan ? (
          <Text style={styles.helperText}>Merged into the Wan video prompt for audio.</Text>
        ) : (
          <>
            <Pressable
              style={[styles.primaryButton, styles.stepButton, (!canGenerateAudio || busyAudio) && styles.buttonDisabled]}
              onPress={runAudio}
              disabled={!canGenerateAudio || busyAudio}
            >
              <View style={styles.buttonContent}>
                {busyAudio && <ActivityIndicator color="white" style={{ marginRight: 8 }} />}
                <Text style={styles.primaryButtonText}>Text + video -> Audio</Text>
              </View>
            </Pressable>
            {audioStatus ? <Text style={[styles.status, toneStyle(audioTone)]}>{audioStatus}</Text> : null}
            <Text style={styles.outputLabel}>Audio</Text>
            {audioUrl ? (
              Platform.OS === 'web' ? (
                React.createElement('audio', {
                  src: resolveMediaUrl(audioUrl) || audioUrl,
                  controls: true,
                  style: { width: '100%' },
                })
              ) : (
                <Text style={styles.outputLink}>{audioUrl}</Text>
              )
            ) : (
              <Text style={styles.outputEmpty}>Audio not ready.</Text>
            )}
            <Text style={styles.outputLabel}>Talking video</Text>
            {talkingVideoUrl ? (
              Platform.OS === 'web' ? (
                React.createElement('video', {
                  src: resolveMediaUrl(talkingVideoUrl) || talkingVideoUrl,
                  controls: true,
                  style: { width: '100%', borderRadius: 12 },
                })
              ) : (
                <Text style={styles.outputLink}>{talkingVideoUrl}</Text>
              )
            ) : (
              <Text style={styles.outputEmpty}>Talking video not ready.</Text>
            )}
          </>
        )}
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
        <View style={styles.historyHeader}>
          <Text style={styles.sectionTitle}>History</Text>
          <Pressable onPress={loadHistory} disabled={historyLoading}>
            <Text style={styles.historyLink}>{historyLoading ? 'Loading...' : 'Refresh'}</Text>
          </Pressable>
        </View>
        {historyError ? <Text style={[styles.status, styles.statusBad]}>{historyError}</Text> : null}
        {historyLoading ? (
          <ActivityIndicator style={{ marginTop: 8 }} />
        ) : historyItems.length ? (
          <View style={styles.historyList}>
            {historyItems.map((entry) => {
              const stepLabel =
                entry.step === 'image'
                  ? 'Image'
                  : entry.step === 'video'
                    ? 'Video'
                    : entry.step === 'audio'
                      ? 'Audio'
                      : 'Pipeline';
              const timestamp = formatHistoryTimestamp(entry.created_at);
              const imageSrc = resolveMediaUrl(entry.image_media_url || entry.image_url);
              const videoSrc = resolveMediaUrl(entry.video_media_url || entry.video_url);
              const audioSrc = resolveMediaUrl(entry.audio_media_url || entry.audio_url);
              const talkingSrc = resolveMediaUrl(entry.talking_media_url || entry.talking_video_url);
              const canRegenImage = !busyImage && !!(entry.idea?.trim() || entry.image_prompt?.trim());
              const canRegenVideo =
                !busyVideo && !!entry.image_url && !!(entry.idea?.trim() || entry.video_prompt?.trim());
              const canRegenAudio =
                !isWan &&
                !busyAudio &&
                !!entry.video_url &&
                !!(entry.idea?.trim() || (entry.audio_text?.trim() && entry.video_prompt?.trim()));
              return (
                <View key={entry.id} style={styles.historyItem}>
                  <Text style={styles.historyTitle}>
                    {stepLabel}
                    {timestamp ? ` · ${timestamp}` : ''}
                  </Text>
                  {entry.title ? <Text style={styles.historyPrompt}>Title: {entry.title}</Text> : null}
                  {entry.idea ? <Text style={styles.historyIdea}>{entry.idea}</Text> : null}
                  {entry.image_prompt ? (
                    <Text style={styles.historyPrompt}>Image: {entry.image_prompt}</Text>
                  ) : null}
                  {entry.video_prompt ? (
                    <Text style={styles.historyPrompt}>Video: {entry.video_prompt}</Text>
                  ) : null}
                  {entry.audio_text ? (
                    <Text style={styles.historyPrompt}>Audio: {entry.audio_text}</Text>
                  ) : null}
                  {entry.negative_prompt ? (
                    <Text style={styles.historyPrompt}>Negative: {entry.negative_prompt}</Text>
                  ) : null}
                  {entry.queue_id ? (
                    <Text style={styles.historyPrompt}>Queue: {entry.queue_id}</Text>
                  ) : null}

                  <View style={styles.historyActions}>
                    <Pressable style={styles.historyButton} onPress={() => applyHistory(entry)}>
                      <Text style={styles.historyButtonText}>Load</Text>
                    </Pressable>
                    <Pressable
                      style={[styles.historyButton, !canRegenImage && styles.buttonDisabled]}
                      onPress={() => runImageFromHistory(entry)}
                      disabled={!canRegenImage}
                    >
                      <Text style={styles.historyButtonText}>Regen image</Text>
                    </Pressable>
                    <Pressable
                      style={[styles.historyButton, !canRegenVideo && styles.buttonDisabled]}
                      onPress={() => runVideoFromHistory(entry)}
                      disabled={!canRegenVideo}
                    >
                      <Text style={styles.historyButtonText}>Regen video</Text>
                    </Pressable>
                    <Pressable
                      style={[styles.historyButton, !canRegenAudio && styles.buttonDisabled]}
                      onPress={() => runAudioFromHistory(entry)}
                      disabled={!canRegenAudio}
                    >
                      <Text style={styles.historyButtonText}>Regen audio</Text>
                    </Pressable>
                    {isWan && entry.queue_id ? (
                      <>
                        <Pressable
                          style={styles.historyButton}
                          onPress={() => {
                            setWanQueueId(entry.queue_id || null);
                            pollWanStatus(entry.queue_id || null);
                          }}
                        >
                          <Text style={styles.historyButtonText}>Poll task</Text>
                        </Pressable>
                        <Pressable
                          style={styles.historyButton}
                          onPress={() => runWanVideo({ queueId: entry.queue_id || null })}
                        >
                          <Text style={styles.historyButtonText}>Resume download</Text>
                        </Pressable>
                      </>
                    ) : null}
                  </View>

                  {imageSrc ? (
                    <>
                      <Text style={styles.outputLabel}>Image</Text>
                      <View style={styles.previewFrame}>
                        <Image source={{ uri: imageSrc }} style={styles.previewImage} resizeMode="contain" />
                      </View>
                    </>
                  ) : null}
                  {videoSrc ? (
                    <>
                      <Text style={styles.outputLabel}>Video</Text>
                      {Platform.OS === 'web' ? (
                        React.createElement('video', {
                          src: videoSrc,
                          controls: true,
                          style: { width: '100%', borderRadius: 12 },
                        })
                      ) : (
                        <Text style={styles.outputLink}>{videoSrc}</Text>
                      )}
                    </>
                  ) : null}
                  {audioSrc ? (
                    <>
                      <Text style={styles.outputLabel}>Audio</Text>
                      {Platform.OS === 'web' ? (
                        React.createElement('audio', {
                          src: audioSrc,
                          controls: true,
                          style: { width: '100%' },
                        })
                      ) : (
                        <Text style={styles.outputLink}>{audioSrc}</Text>
                      )}
                    </>
                  ) : null}
                  {talkingSrc ? (
                    <>
                      <Text style={styles.outputLabel}>Talking video</Text>
                      {Platform.OS === 'web' ? (
                        React.createElement('video', {
                          src: talkingSrc,
                          controls: true,
                          style: { width: '100%', borderRadius: 12 },
                        })
                      ) : (
                        <Text style={styles.outputLink}>{talkingSrc}</Text>
                      )}
                    </>
                  ) : null}
                </View>
              );
            })}
          </View>
        ) : (
          <Text style={styles.outputEmpty}>No history yet.</Text>
        )}
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
  subTabRow: {
    flexDirection: 'row',
    gap: 8,
  },
  subTab: {
    borderWidth: 1,
    borderColor: '#d1c8ba',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 999,
    backgroundColor: '#f7f3ea',
  },
  subTabActive: {
    backgroundColor: '#1f4bd1',
    borderColor: '#1f4bd1',
  },
  subTabText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#3b3b3b',
  },
  subTabTextActive: {
    color: '#ffffff',
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
  textInput: {
    borderWidth: 1,
    borderColor: '#e0ddd6',
    borderRadius: 12,
    padding: 10,
    minHeight: 44,
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
  dropdown: {
    position: 'relative',
  },
  dropdownButton: {
    borderWidth: 1,
    borderColor: '#e0ddd6',
    borderRadius: 10,
    paddingVertical: 10,
    paddingHorizontal: 12,
    backgroundColor: '#fbfaf7',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  dropdownButtonText: {
    fontSize: 13,
    color: '#2f2f2f',
    flex: 1,
    paddingRight: 8,
  },
  dropdownChevron: {
    fontSize: 12,
    color: '#6b6b6b',
  },
  dropdownMenu: {
    marginTop: 8,
    borderWidth: 1,
    borderColor: '#e0ddd6',
    borderRadius: 12,
    maxHeight: 220,
    backgroundColor: '#fff',
  },
  dropdownItem: {
    paddingVertical: 8,
    paddingHorizontal: 12,
  },
  dropdownItemActive: {
    backgroundColor: '#eef3ff',
  },
  dropdownItemText: {
    fontSize: 12,
    color: '#333',
  },
  dropdownItemTextActive: {
    fontWeight: '600',
    color: '#1d3a8a',
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
  stepButton: {
    alignSelf: 'flex-start',
    marginTop: 10,
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
  helperText: {
    fontSize: 12,
    color: '#6a6a6a',
    marginTop: 6,
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
  historyHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  historyLink: {
    fontSize: 12,
    color: '#2f6cff',
  },
  historyList: {
    gap: 16,
    marginTop: 8,
  },
  historyItem: {
    borderWidth: 1,
    borderColor: '#e6e1d8',
    borderRadius: 12,
    padding: 12,
    backgroundColor: '#fbfaf7',
  },
  historyTitle: {
    fontSize: 13,
    fontWeight: '600',
    color: '#1d1d1d',
    marginBottom: 6,
  },
  historyIdea: {
    fontSize: 12,
    color: '#2f2f2f',
    marginBottom: 8,
  },
  historyPrompt: {
    fontSize: 12,
    color: '#4c4c4c',
    marginBottom: 6,
  },
  historyActions: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
    marginBottom: 8,
    marginTop: 4,
  },
  queueLabel: {
    fontSize: 12,
    color: '#5b5b5b',
    marginTop: 8,
  },
  queueActions: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
    marginTop: 6,
  },
  queueButton: {
    borderWidth: 1,
    borderColor: '#d7d6f1',
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 999,
    backgroundColor: '#f4f3ff',
  },
  queueButtonText: {
    fontSize: 12,
    color: '#3b33a3',
    fontWeight: '600',
  },
  historyButton: {
    borderWidth: 1,
    borderColor: '#cdd7f8',
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 999,
    backgroundColor: '#ffffff',
  },
  historyButtonText: {
    fontSize: 12,
    color: '#1d3a8a',
    fontWeight: '600',
  },
  outputLabel: {
    fontSize: 12,
    color: '#6a6a6a',
    marginBottom: 6,
    marginTop: 10,
  },
  outputEmpty: {
    fontSize: 12,
    color: '#9a9a9a',
  },
  outputLink: {
    fontSize: 12,
    color: '#2f6cff',
  },
  previewFrame: {
    height: 240,
    borderRadius: 12,
    backgroundColor: '#fbfaf7',
    borderWidth: 1,
    borderColor: '#e0ddd6',
    alignItems: 'center',
    justifyContent: 'center',
    overflow: 'hidden',
  },
  previewImage: {
    width: '100%',
    height: '100%',
  },
  previewEmpty: {
    textAlign: 'center',
    paddingHorizontal: 12,
  },
});
