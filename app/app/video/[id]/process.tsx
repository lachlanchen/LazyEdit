import React, { useEffect, useMemo, useRef, useState } from 'react';
import { ActivityIndicator, Pressable, ScrollView, StyleSheet, Switch, Text, View } from 'react-native';
import { Stack, useLocalSearchParams } from 'expo-router';

const API_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8787';

type StepKey =
  | 'transcribe'
  | 'translate'
  | 'burn'
  | 'keyframes'
  | 'caption'
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
};

type TranslationDetail = {
  language_code: string;
  status: string;
};

const STEP_ORDER: StepKey[] = [
  'transcribe',
  'translate',
  'burn',
  'keyframes',
  'caption',
  'metadataZh',
  'metadataEn',
];

const STEP_LABELS: Record<StepKey, string> = {
  transcribe: 'Transcribe',
  translate: 'Translate',
  burn: 'Burn subtitles',
  keyframes: 'Extract key frames',
  caption: 'Caption frames',
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

const STORAGE_PREFIX = 'lazyedit_process_state';

const defaultStepState = STEP_ORDER.reduce((acc, key) => {
  acc[key] = 'idle';
  return acc;
}, {} as Record<StepKey, StepState>);

const defaultSelections: Record<StepKey, boolean> = {
  transcribe: true,
  translate: true,
  burn: true,
  keyframes: true,
  caption: true,
  metadataZh: true,
  metadataEn: true,
};

const formatPercent = (value?: number, fallback = 0) =>
  `${Math.round((typeof value === 'number' ? value : fallback) * 100)}%`;

const formatLanguages = (codes: string[]) =>
  codes.map((code) => LANG_LABELS[code] || code).join(', ');

type VideoDetail = {
  id: number;
  title: string | null;
  media_url?: string | null;
};

const LOG_TABS = ['transcription', 'translations', 'captions', 'metadata'] as const;
const LOG_TAB_LABELS: Record<typeof LOG_TABS[number], string> = {
  transcription: 'Transcriptions',
  translations: 'Translations',
  captions: 'Captions',
  metadata: 'Metadata',
};

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
  const [video, setVideo] = useState<VideoDetail | null>(null);
  const [burnPreviewUrl, setBurnPreviewUrl] = useState<string | null>(null);
  const [proxyPreviewUrl, setProxyPreviewUrl] = useState<string | null>(null);
  const [activeLogTab, setActiveLogTab] = useState<typeof LOG_TABS[number]>('transcription');
  const processStateRef = useRef({
    stepStatus: defaultStepState,
    stepDetail: {} as Record<StepKey, string>,
    message: '',
    burnPreviewUrl: null as string | null,
  });

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

  const previewVideoUrl = useMemo(() => {
    if (!video?.media_url) return null;
    return `${API_URL}${video.media_url}`;
  }, [video]);

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
      const url = json.media_url ? `${API_URL}${json.media_url}` : null;
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
      setStepStatus(baselineStatus);
      setStepDetail(baselineDetail);
      setMessage(stored.message || '');
      setBurnPreviewUrl(stored.burnPreviewUrl || null);
      processStateRef.current = {
        stepStatus: baselineStatus,
        stepDetail: baselineDetail,
        message: stored.message || '',
        burnPreviewUrl: stored.burnPreviewUrl || null,
      };
    }
  }, [id]);

  useEffect(() => {
    if (!id) return;
    (async () => {
      setLoading(true);
      try {
        const [langsResp, layoutResp] = await Promise.all([
          fetch(`${API_URL}/api/ui-settings/translation_languages`),
          fetch(`${API_URL}/api/ui-settings/burn_layout`),
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
    } catch (_err) {
      // ignore
    } finally {
      setLoading(false);
    }
  })();
}, [id]);

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

  const logEntries = useMemo(() => {
    return {
      transcription: [
        {
          title: 'Transcribe',
          status: stepStatus.transcribe,
          detail: stepDetail.transcribe,
        },
      ],
      translations: [
        {
          title: 'Translate',
          status: stepStatus.translate,
          detail:
            stepDetail.translate ||
            (translationTargetLanguages.length
              ? `Languages: ${translationTargetLanguages.join(', ')}`
              : 'No languages selected'),
        },
      ],
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
    updateStatus('burn', 'working', 'Starting burn');
    const resp = await fetch(`${API_URL}/api/videos/${id}/burn-subtitles`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ layout }),
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

  const runPipeline = async () => {
    if (!id || running) return;
    setRunning(true);
    updateStoredMessage('');
    setStepStatus(defaultStepState);
    setStepDetail({});

    const needsTranscribe =
      selectedSteps.transcribe ||
      selectedSteps.translate ||
      selectedSteps.burn ||
      selectedSteps.metadataZh ||
      selectedSteps.metadataEn;
    const needsTranslate = selectedSteps.translate || selectedSteps.burn;
    const needsCaption = selectedSteps.caption || selectedSteps.metadataZh || selectedSteps.metadataEn;

    try {
      if (needsTranscribe) {
        const ok = await ensureTranscription();
        if (!ok) {
          updateStoredMessage('Stopped: transcription failed.');
          return;
        }
      } else {
        updateStatus('transcribe', 'skipped', 'Skipped');
      }

      if (needsTranslate) {
        const ok = await ensureTranslations();
        if (!ok) {
          updateStoredMessage('Stopped: translation failed.');
          return;
        }
      } else {
        updateStatus('translate', 'skipped', 'Skipped');
      }

      if (selectedSteps.burn) {
        const ok = await runBurn();
        if (!ok) {
          updateStoredMessage('Stopped: burn failed.');
          return;
        }
        await refreshBurnPreview();
      } else {
        updateStatus('burn', 'skipped', 'Skipped');
      }

      if (selectedSteps.keyframes) {
        const ok = await runKeyframes();
        if (!ok) {
          updateStoredMessage('Stopped: keyframe extraction failed.');
          return;
        }
      } else {
        updateStatus('keyframes', 'skipped', 'Skipped');
      }

      if (needsCaption) {
        const ok = await runCaption();
        if (!ok) {
          updateStoredMessage('Stopped: captioning failed.');
          return;
        }
      } else {
        updateStatus('caption', 'skipped', 'Skipped');
      }

      if (selectedSteps.metadataZh) {
        const ok = await runMetadata('zh', 'metadataZh');
        if (!ok) {
          updateStoredMessage('Stopped: Chinese metadata failed.');
          return;
        }
      } else {
        updateStatus('metadataZh', 'skipped', 'Skipped');
      }

      if (selectedSteps.metadataEn) {
        const ok = await runMetadata('en', 'metadataEn');
        if (!ok) {
          updateStoredMessage('Stopped: English metadata failed.');
          return;
        }
      } else {
        updateStatus('metadataEn', 'skipped', 'Skipped');
      }

      updateStoredMessage('Process complete.');
    } finally {
      setRunning(false);
    }
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
                    setSelectedSteps((prev) => ({
                      ...prev,
                      [step]: value,
                    }))
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

        <Pressable style={[styles.btnPrimary, running && styles.btnDisabled]} onPress={runPipeline}>
          <Text style={styles.btnText}>{running ? 'Processing…' : 'Process video'}</Text>
        </Pressable>
        <Pressable style={styles.btnSecondary} onPress={createProxyPreview}>
          <Text style={styles.btnSecondaryText}>Create preview proxy (fix black iPhone videos)</Text>
        </Pressable>
        {proxyStatus ? <Text style={styles.status}>{proxyStatus}</Text> : null}
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
  meta: { fontSize: 12, color: '#475569', marginTop: 4 },
  loadingText: { marginTop: 12, color: '#475569' },
  card: {
    padding: 14,
    borderRadius: 14,
    borderWidth: 1,
    borderColor: '#e2e8f0',
    backgroundColor: 'white',
    marginBottom: 14,
  },
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
  btnPrimary: {
    marginTop: 4,
    backgroundColor: '#a855f7',
    paddingVertical: 12,
    borderRadius: 999,
    alignItems: 'center',
  },
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
  btnDisabled: { opacity: 0.6 },
  btnText: { color: '#f8fafc', fontWeight: '700' },
  status: { marginTop: 10, fontSize: 12, color: '#0f172a' },
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
    height: 220,
    backgroundColor: '#0f172a',
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
});
