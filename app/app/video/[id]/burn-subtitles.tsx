import React, { useEffect, useMemo, useState } from 'react';
import { ActivityIndicator, Modal, Pressable, ScrollView, StyleSheet, Switch, Text, View } from 'react-native';
import { Stack, useLocalSearchParams } from 'expo-router';

const API_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8787';

type TranslationDetail = {
  id: number;
  language_code: string;
  status: string;
  output_json_path?: string | null;
  error?: string | null;
};

type BurnSlot = {
  slot: number;
  language: string | null;
  fontScale?: number;
  romaji?: boolean;
  pinyin?: boolean;
  ipa?: boolean;
  romaja?: boolean;
  jyutping?: boolean;
  arabicTranslit?: boolean;
};

type BurnStatus = {
  id: number;
  status: string;
  output_url?: string | null;
  progress?: number | null;
  error?: string | null;
  created_at?: string | null;
  config?: { slots?: BurnSlot[]; heightRatio?: number; rows?: number; cols?: number; liftRatio?: number } | null;
};

type SelectOption = {
  value: string;
  label: string;
  available?: boolean;
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

const LANG_SHORT: Record<string, string> = {
  en: 'EN',
  ja: 'JA',
  ar: 'AR',
  vi: 'VI',
  ko: 'KO',
  es: 'ES',
  fr: 'FR',
  ru: 'RU',
  yue: 'YUE',
  'zh-Hant': 'ZH-T',
  'zh-Hans': 'ZH-S',
};

const SLOT_COLORS = ['#22c55e', '#60a5fa', '#f59e0b', '#f472b6', '#a78bfa', '#34d399', '#fb7185', '#38bdf8'];

const DEFAULT_ROWS = 4;
const DEFAULT_COLS = 1;
const DEFAULT_HEIGHT_RATIO = 0.5;
const DEFAULT_LIFT_RATIO = 0.1;
const DEFAULT_ROMAJI = true;
const DEFAULT_PINYIN = true;
const DEFAULT_IPA = true;
const DEFAULT_JYUTPING = false;
const DEFAULT_ROMAJA = false;
const DEFAULT_ARABIC_TRANSLIT = false;

const LANGUAGE_OPTIONS: SelectOption[] = [
  { value: 'en', label: LANG_LABELS.en },
  { value: 'ja', label: LANG_LABELS.ja },
  { value: 'zh-Hant', label: LANG_LABELS['zh-Hant'] },
  { value: 'zh-Hans', label: LANG_LABELS['zh-Hans'] },
  { value: 'yue', label: LANG_LABELS.yue },
  { value: 'ar', label: LANG_LABELS.ar },
  { value: 'vi', label: LANG_LABELS.vi },
  { value: 'ko', label: LANG_LABELS.ko },
  { value: 'es', label: LANG_LABELS.es },
  { value: 'fr', label: LANG_LABELS.fr },
  { value: 'ru', label: LANG_LABELS.ru },
];

const DEFAULT_SLOTS: BurnSlot[] = [
  {
    slot: 1,
    language: 'en',
    fontScale: 1,
    romaji: DEFAULT_ROMAJI,
    pinyin: DEFAULT_PINYIN,
    ipa: DEFAULT_IPA,
    romaja: DEFAULT_ROMAJA,
    jyutping: DEFAULT_JYUTPING,
    arabicTranslit: DEFAULT_ARABIC_TRANSLIT,
  },
  {
    slot: 2,
    language: 'ja',
    fontScale: 1,
    romaji: DEFAULT_ROMAJI,
    pinyin: DEFAULT_PINYIN,
    ipa: DEFAULT_IPA,
    romaja: DEFAULT_ROMAJA,
    jyutping: DEFAULT_JYUTPING,
    arabicTranslit: DEFAULT_ARABIC_TRANSLIT,
  },
  {
    slot: 3,
    language: 'zh-Hant',
    fontScale: 1,
    romaji: DEFAULT_ROMAJI,
    pinyin: DEFAULT_PINYIN,
    ipa: DEFAULT_IPA,
    romaja: DEFAULT_ROMAJA,
    jyutping: DEFAULT_JYUTPING,
    arabicTranslit: DEFAULT_ARABIC_TRANSLIT,
  },
  {
    slot: 4,
    language: 'fr',
    fontScale: 1,
    romaji: DEFAULT_ROMAJI,
    pinyin: DEFAULT_PINYIN,
    ipa: DEFAULT_IPA,
    romaja: DEFAULT_ROMAJA,
    jyutping: DEFAULT_JYUTPING,
    arabicTranslit: DEFAULT_ARABIC_TRANSLIT,
  },
];

const ROW_OPTIONS: SelectOption[] = Array.from({ length: 10 }, (_, idx) => ({
  value: String(idx + 1),
  label: String(idx + 1),
}));

const COL_OPTIONS: SelectOption[] = Array.from({ length: 4 }, (_, idx) => ({
  value: String(idx + 1),
  label: String(idx + 1),
}));

const formatSlotLabel = (slotId: number, rows: number, cols: number) => {
  const col = ((slotId - 1) % cols) + 1;
  const row = Math.floor((slotId - 1) / cols) + 1;
  return `Slot ${slotId} · Row ${row} · Col ${col}`;
};

const isJapanese = (lang?: string | null) => lang === 'ja';
const isChinese = (lang?: string | null) => lang === 'zh' || lang === 'zh-Hant' || lang === 'zh-Hans';
const isIpaLanguage = (lang?: string | null) => lang === 'en' || lang === 'fr';
const isKorean = (lang?: string | null) => lang === 'ko';
const isCantonese = (lang?: string | null) => lang === 'yue';
const isArabic = (lang?: string | null) => lang === 'ar';

const shortLabelForLanguage = (lang?: string | null) => {
  if (!lang) return '—';
  return LANG_SHORT[lang] || lang.slice(0, 3).toUpperCase();
};

const toRgba = (hex: string, alpha: number) => {
  const normalized = hex.replace('#', '');
  const value =
    normalized.length === 3
      ? normalized.split('').map((char) => char + char).join('')
      : normalized;
  if (value.length !== 6) return `rgba(148, 163, 184, ${alpha})`;
  const r = parseInt(value.slice(0, 2), 16);
  const g = parseInt(value.slice(2, 4), 16);
  const b = parseInt(value.slice(4, 6), 16);
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
};

const OptionSelect = ({
  label,
  value,
  options,
  onChange,
}: {
  label: string;
  value: string;
  options: SelectOption[];
  onChange: (next: string) => void;
}) => {
  const [open, setOpen] = useState(false);
  const selected = options.find((opt) => opt.value === value);
  const fallbackLabel = value ? LANG_LABELS[value] || value : 'None';
  const displayLabel = selected?.label || fallbackLabel;
  const isMissing = Boolean(selected && selected.available === false);

  return (
    <>
      <Pressable style={styles.select} onPress={() => setOpen(true)}>
        <Text style={styles.selectLabel}>{label}</Text>
        <Text style={[styles.selectValue, isMissing && styles.selectValueMuted]}>{displayLabel}</Text>
      </Pressable>
      <Modal visible={open} transparent animationType="fade">
        <Pressable style={styles.modalBackdrop} onPress={() => setOpen(false)}>
          <Pressable style={styles.modalCard} onPress={() => {}}>
            <Text style={styles.modalTitle}>Select language</Text>
            <ScrollView style={{ maxHeight: 280 }}>
              {options.map((option) => {
                const active = option.value === value;
                const missing = option.available === false;
                return (
                  <Pressable
                    key={option.value}
                    style={[styles.modalOption, active && styles.modalOptionActive]}
                    onPress={() => {
                      onChange(option.value);
                      setOpen(false);
                    }}
                  >
                    <Text
                      style={[
                        styles.modalOptionText,
                        active && styles.modalOptionTextActive,
                        missing && styles.modalOptionTextMuted,
                      ]}
                    >
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

const formatTimestamp = (value?: string | null) =>
  value ? value.slice(0, 19).replace('T', ' ') : 'Unknown time';

export default function BurnSubtitlesScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const [translations, setTranslations] = useState<TranslationDetail[]>([]);
  const [slots, setSlots] = useState<BurnSlot[]>(DEFAULT_SLOTS);
  const [heightRatio, setHeightRatio] = useState(DEFAULT_HEIGHT_RATIO);
  const [rows, setRows] = useState(DEFAULT_ROWS);
  const [cols, setCols] = useState(DEFAULT_COLS);
  const [liftRatio, setLiftRatio] = useState(DEFAULT_LIFT_RATIO);
  const [videoUrl, setVideoUrl] = useState<string | null>(null);
  const [videoAspect, setVideoAspect] = useState<number | null>(null);
  const [previewWidth, setPreviewWidth] = useState(0);
  const [status, setStatus] = useState<BurnStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [burning, setBurning] = useState(false);
  const [message, setMessage] = useState('');
  const [layoutLoaded, setLayoutLoaded] = useState(false);

  const availableLanguages = useMemo(() => {
    const set = new Set<string>();
    for (const item of translations) {
      if (item.status !== 'completed') continue;
      set.add(item.language_code);
    }
    return set;
  }, [translations]);

  const languageOptions = useMemo(() => {
    const base: SelectOption[] = [{ value: '', label: 'None', available: true }];
    for (const option of LANGUAGE_OPTIONS) {
      base.push({ ...option, available: availableLanguages.has(option.value) });
    }
    return base;
  }, [availableLanguages]);

  const sortedSlots = useMemo(() => [...slots].sort((a, b) => a.slot - b.slot), [slots]);

  const buildSlotList = (current: BurnSlot[], total: number) => {
    const map = new Map<number, BurnSlot>();
    current.forEach((slot) => map.set(slot.slot, slot));
    const next: BurnSlot[] = [];
    for (let slotId = 1; slotId <= total; slotId += 1) {
      const existing = map.get(slotId);
      next.push({
        slot: slotId,
        language: existing?.language ?? null,
        fontScale: existing?.fontScale ?? 1,
        romaji: existing?.romaji ?? DEFAULT_ROMAJI,
        pinyin: existing?.pinyin ?? DEFAULT_PINYIN,
        ipa: existing?.ipa ?? DEFAULT_IPA,
        romaja: existing?.romaja ?? DEFAULT_ROMAJA,
        jyutping: existing?.jyutping ?? DEFAULT_JYUTPING,
        arabicTranslit: existing?.arabicTranslit ?? DEFAULT_ARABIC_TRANSLIT,
      });
    }
    return next;
  };

  const loadTranslations = async () => {
    if (!id) return [];
    try {
      const resp = await fetch(`${API_URL}/api/videos/${id}/translations`);
      const json = await resp.json();
      if (!resp.ok) {
        setTranslations([]);
        return [];
      }
      const items = json.translations || [];
      setTranslations(items);
      return items as TranslationDetail[];
    } catch (_err) {
      setTranslations([]);
      return [];
    }
  };

  const loadVideoDetails = async () => {
    if (!id) return;
    try {
      const resp = await fetch(`${API_URL}/api/videos/${id}`);
      const json = await resp.json();
      if (!resp.ok) return;
      if (json.media_url) {
        setVideoUrl(`${API_URL}${json.media_url}`);
      }
    } catch (_err) {
      // ignore
    }
  };

  const loadLayout = async () => {
    try {
      const resp = await fetch(`${API_URL}/api/ui-settings/burn_layout`);
      const json = await resp.json();
      if (!resp.ok) return;
      const value = json.value;
      const nextRows = typeof value?.rows === 'number' ? value.rows : DEFAULT_ROWS;
      const nextCols = typeof value?.cols === 'number' ? value.cols : DEFAULT_COLS;
      setRows(nextRows);
      setCols(nextCols);
      if (value?.slots && Array.isArray(value.slots)) {
        const normalized = value.slots
          .filter((slot: BurnSlot) => typeof slot.slot === 'number')
          .map((slot: BurnSlot) => ({
            slot: slot.slot,
            language: slot.language || null,
            fontScale: typeof slot.fontScale === 'number' ? slot.fontScale : 1,
            romaji: typeof slot.romaji === 'boolean' ? slot.romaji : DEFAULT_ROMAJI,
            pinyin: typeof slot.pinyin === 'boolean' ? slot.pinyin : DEFAULT_PINYIN,
            ipa: typeof slot.ipa === 'boolean' ? slot.ipa : DEFAULT_IPA,
            romaja: typeof slot.romaja === 'boolean' ? slot.romaja : DEFAULT_ROMAJA,
            jyutping: typeof slot.jyutping === 'boolean' ? slot.jyutping : DEFAULT_JYUTPING,
            arabicTranslit:
              typeof slot.arabicTranslit === 'boolean' ? slot.arabicTranslit : DEFAULT_ARABIC_TRANSLIT,
          }));
        const total = nextRows * nextCols;
        if (normalized.length) setSlots(buildSlotList(normalized, total));
      }
      let nextHeightRatio = heightRatio;
      if (typeof value?.heightRatio === 'number') {
        nextHeightRatio = value.heightRatio;
        setHeightRatio(value.heightRatio);
      }
      if (typeof value?.liftRatio === 'number') {
        setLiftRatio(value.liftRatio);
      } else if (typeof value?.liftSlots === 'number') {
        const ratioFromSlots = (nextHeightRatio / Math.max(nextRows, 1)) * value.liftSlots;
        setLiftRatio(Math.min(Math.max(ratioFromSlots, 0), 0.4));
      }
    } catch (_err) {
      // ignore
    } finally {
      setLayoutLoaded(true);
    }
  };

  const loadBurnStatus = async () => {
    if (!id) return;
    try {
      const resp = await fetch(`${API_URL}/api/videos/${id}/burn-subtitles`);
      if (resp.status === 404) {
        setStatus(null);
        return;
      }
      const json = await resp.json();
      if (!resp.ok) {
        setStatus(null);
        setMessage(json.error || 'Failed to load burn status');
        return;
      }
      setStatus(json);
    } catch (err: any) {
      setMessage(err?.message || 'Failed to load burn status');
    }
  };

  const ensureTranscription = async () => {
    if (!id) return false;
    try {
      const resp = await fetch(`${API_URL}/api/videos/${id}/transcription`);
      if (resp.ok) {
        const json = await resp.json();
        if (json.status === 'completed') {
          return true;
        }
        if (json.status === 'no_audio') {
          setMessage('No audio detected in this video.');
          return false;
        }
      }
    } catch (_err) {
      // fall through to transcribe
    }

    setMessage('Transcribing audio...');
    try {
      const resp = await fetch(`${API_URL}/api/videos/${id}/transcribe`, { method: 'POST' });
      const json = await resp.json();
      if (!resp.ok) {
        setMessage(json.error || json.details || 'Transcription failed');
        return false;
      }
      if (json.status !== 'completed') {
        setMessage(json.error || 'Transcription incomplete');
        return false;
      }
      return true;
    } catch (err: any) {
      setMessage(err?.message || 'Transcription failed');
      return false;
    }
  };

  const ensureTranslations = async (languages: string[]) => {
    if (!id || !languages.length) return true;
    const existing = await loadTranslations();
    const completed = new Set(
      existing.filter((item) => item.status === 'completed').map((item) => item.language_code)
    );
    const pending = languages.filter((lang) => !completed.has(lang));
    for (const lang of pending) {
      setMessage(`Translating ${LANG_LABELS[lang] || lang}...`);
      try {
        const resp = await fetch(`${API_URL}/api/videos/${id}/translate`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ language: lang, use_cache: true }),
        });
        const json = await resp.json();
        if (!resp.ok) {
          setMessage(json.error || json.details || `Translation failed for ${lang}`);
          return false;
        }
      } catch (err: any) {
        setMessage(err?.message || `Translation failed for ${lang}`);
        return false;
      }
    }
    await loadTranslations();
    return true;
  };

  useEffect(() => {
    (async () => {
      setLoading(true);
      await loadVideoDetails();
      await loadTranslations();
      await loadLayout();
      await loadBurnStatus();
      setLoading(false);
    })();
  }, [id]);

  useEffect(() => {
    if (!layoutLoaded) return;
    const payload = { slots, heightRatio, rows, cols, liftRatio };
    const timeout = setTimeout(async () => {
      try {
        await fetch(`${API_URL}/api/ui-settings/burn_layout`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });
      } catch (_err) {
        // ignore
      }
    }, 200);
    return () => clearTimeout(timeout);
  }, [slots, heightRatio, rows, cols, liftRatio, layoutLoaded]);

  useEffect(() => {
    if (!layoutLoaded) return;
    const total = rows * cols;
    setSlots((prev) => buildSlotList(prev, total));
  }, [rows, cols, layoutLoaded]);

  const updateSlot = (slotId: number, language: string) => {
    setSlots((prev) =>
      prev.map((slot) => (slot.slot === slotId ? { ...slot, language: language || null } : slot))
    );
  };

  const updateSlotScale = (slotId: number, scale: number) => {
    setSlots((prev) =>
      prev.map((slot) => (slot.slot === slotId ? { ...slot, fontScale: scale } : slot))
    );
  };

  const updateSlotToggle = (
    slotId: number,
    field: 'romaji' | 'pinyin' | 'ipa' | 'jyutping' | 'romaja' | 'arabicTranslit',
    value: boolean,
  ) => {
    setSlots((prev) =>
      prev.map((slot) => (slot.slot === slotId ? { ...slot, [field]: value } : slot))
    );
  };

  const isProcessing = status?.status === 'processing';
  const progressValue = typeof status?.progress === 'number' ? status.progress : null;
  const aspectRatio = videoAspect && videoAspect > 0 ? videoAspect : 16 / 9;
  const previewStageHeight = previewWidth > 0 ? Math.round(previewWidth / aspectRatio) : 180;
  const previewBandHeight = Math.max(12, Math.round(previewStageHeight * heightRatio));
  const previewCellWidth = `${Math.floor(100 / Math.max(cols, 1))}%`;
  const density = Math.min(1, previewBandHeight / Math.max(rows * 26, 1));
  const previewBandPadding = Math.max(2, Math.round(8 * density));
  const previewRowGap = Math.max(1, Math.round(6 * density));
  const previewColGap = Math.max(1, Math.round(6 * density));
  const availableHeight =
    previewBandHeight - previewBandPadding * 2 - previewRowGap * (Math.max(rows, 1) - 1);
  const previewCellHeight = Math.max(2, Math.floor(availableHeight / Math.max(rows, 1)));
  const previewValueSize = Math.max(7, Math.min(14, Math.round(previewCellHeight * 0.9)));
  const previewLift = Math.min(
    Math.max(0, previewStageHeight - previewBandHeight),
    Math.round(previewStageHeight * liftRatio),
  );

  const burnSubtitles = async () => {
    if (!id || burning) return;
    setBurning(true);
    try {
      setMessage('Checking prerequisites...');
      const transcriptionReady = await ensureTranscription();
      if (!transcriptionReady) {
        setBurning(false);
        return;
      }

      const uniqueLangs = Array.from(
        new Set(slots.map((slot) => slot.language).filter((lang): lang is string => Boolean(lang)))
      );
      const translationsReady = await ensureTranslations(uniqueLangs);
      if (!translationsReady) {
        setBurning(false);
        return;
      }

      setMessage('Burning subtitles... this can take a few minutes.');
      const resp = await fetch(`${API_URL}/api/videos/${id}/burn-subtitles`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ layout: { slots, heightRatio, rows, cols, liftRatio } }),
      });
      const json = await resp.json();
      if (!resp.ok) {
        setMessage(json.error || json.details || 'Burn failed');
        setBurning(false);
        return;
      }
      setStatus(json);
      setMessage(json.status === 'processing' ? 'Burn started.' : 'Burn complete.');
      await loadBurnStatus();
    } catch (err: any) {
      setMessage(err?.message || 'Burn failed');
    } finally {
      setBurning(false);
    }
  };

  useEffect(() => {
    if (!id) return;
    if (status?.status !== 'processing') return;
    const interval = setInterval(() => {
      loadBurnStatus();
    }, 2000);
    return () => clearInterval(interval);
  }, [id, status?.status]);

  if (loading) {
    return (
      <View style={styles.container}>
        <Stack.Screen options={{ title: 'Burn subtitles', headerBackTitle: 'Video' }} />
        <ActivityIndicator />
        <Text style={styles.loadingText}>Loading burn settings...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <Stack.Screen options={{ title: 'Burn subtitles', headerBackTitle: 'Video' }} />
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.card}>
          <Text style={styles.title}>Burn subtitles</Text>
          <Text style={styles.meta}>Assign languages to the 4-slot bottom grid.</Text>

          <View style={styles.optionRow}>
            <View style={{ flex: 1, marginRight: 10 }}>
              <OptionSelect
                label="Rows"
                value={String(rows)}
                options={ROW_OPTIONS}
                onChange={(value) => setRows(Number(value) || DEFAULT_ROWS)}
              />
            </View>
            <View style={{ flex: 1 }}>
              <OptionSelect
                label="Columns"
                value={String(cols)}
                options={COL_OPTIONS}
                onChange={(value) => setCols(Number(value) || DEFAULT_COLS)}
              />
            </View>
          </View>

          <View style={styles.slotGrid}>
            {sortedSlots.map((slot) => {
              const isAvailable = slot.language ? availableLanguages.has(slot.language) : false;
              const statusText = slot.language
                ? isAvailable
                  ? 'Available'
                  : 'Missing translation'
                : 'No language selected';
              return (
                <View key={slot.slot} style={styles.slotCard}>
                  <Text style={styles.slotTitle}>{formatSlotLabel(slot.slot, rows, cols)}</Text>
                  <OptionSelect
                    label="Language"
                    value={slot.language || ''}
                    options={languageOptions}
                    onChange={(value) => updateSlot(slot.slot, value)}
                  />
                  <Text
                    style={[
                      styles.slotStatus,
                      slot.language ? (isAvailable ? styles.slotStatusReady : styles.slotStatusMissing) : styles.slotStatusMuted,
                    ]}
                  >
                    {statusText}
                  </Text>
                <SliderControl
                  label="Font scale"
                  value={slot.fontScale ?? 1}
                  min={0.6}
                  max={1.6}
                  step={0.05}
                  onChange={(value) => updateSlotScale(slot.slot, value)}
                  formatValue={(value) => `${value.toFixed(2)}x`}
                />
                {isJapanese(slot.language) ? (
                  <View style={styles.slotToggleRow}>
                    <View style={styles.slotToggleText}>
                      <Text style={styles.slotToggleLabel}>Romaji</Text>
                      <Text style={styles.slotToggleHint}>Above kana-only words</Text>
                    </View>
                    <Switch
                      value={slot.romaji ?? DEFAULT_ROMAJI}
                      onValueChange={(value) => updateSlotToggle(slot.slot, 'romaji', value)}
                      trackColor={{ false: '#e2e8f0', true: '#2563eb' }}
                      thumbColor={slot.romaji ?? DEFAULT_ROMAJI ? '#f8fafc' : '#f1f5f9'}
                    />
                  </View>
                ) : null}
                {isChinese(slot.language) ? (
                  <View style={styles.slotToggleRow}>
                    <View style={styles.slotToggleText}>
                      <Text style={styles.slotToggleLabel}>Pinyin</Text>
                      <Text style={styles.slotToggleHint}>Above Chinese text</Text>
                    </View>
                    <Switch
                      value={slot.pinyin ?? DEFAULT_PINYIN}
                      onValueChange={(value) => updateSlotToggle(slot.slot, 'pinyin', value)}
                      trackColor={{ false: '#e2e8f0', true: '#2563eb' }}
                      thumbColor={slot.pinyin ?? DEFAULT_PINYIN ? '#f8fafc' : '#f1f5f9'}
                    />
                  </View>
                ) : null}
                {isIpaLanguage(slot.language) ? (
                  <View style={styles.slotToggleRow}>
                    <View style={styles.slotToggleText}>
                      <Text style={styles.slotToggleLabel}>IPA</Text>
                      <Text style={styles.slotToggleHint}>Pronunciation above words</Text>
                    </View>
                    <Switch
                      value={slot.ipa ?? DEFAULT_IPA}
                      onValueChange={(value) => updateSlotToggle(slot.slot, 'ipa', value)}
                      trackColor={{ false: '#e2e8f0', true: '#2563eb' }}
                      thumbColor={slot.ipa ?? DEFAULT_IPA ? '#f8fafc' : '#f1f5f9'}
                    />
                  </View>
                ) : null}
                {isKorean(slot.language) ? (
                  <View style={styles.slotToggleRow}>
                    <View style={styles.slotToggleText}>
                      <Text style={styles.slotToggleLabel}>Romaja</Text>
                      <Text style={styles.slotToggleHint}>Romanization above Hangul</Text>
                    </View>
                    <Switch
                      value={slot.romaja ?? DEFAULT_ROMAJA}
                      onValueChange={(value) => updateSlotToggle(slot.slot, 'romaja', value)}
                      trackColor={{ false: '#e2e8f0', true: '#2563eb' }}
                      thumbColor={slot.romaja ?? DEFAULT_ROMAJA ? '#f8fafc' : '#f1f5f9'}
                    />
                  </View>
                ) : null}
                {isCantonese(slot.language) ? (
                  <View style={styles.slotToggleRow}>
                    <View style={styles.slotToggleText}>
                      <Text style={styles.slotToggleLabel}>Jyutping</Text>
                      <Text style={styles.slotToggleHint}>Pronunciation above Cantonese</Text>
                    </View>
                    <Switch
                      value={slot.jyutping ?? DEFAULT_JYUTPING}
                      onValueChange={(value) => updateSlotToggle(slot.slot, 'jyutping', value)}
                      trackColor={{ false: '#e2e8f0', true: '#2563eb' }}
                      thumbColor={slot.jyutping ?? DEFAULT_JYUTPING ? '#f8fafc' : '#f1f5f9'}
                    />
                  </View>
                ) : null}
                {isArabic(slot.language) ? (
                  <View style={styles.slotToggleRow}>
                    <View style={styles.slotToggleText}>
                      <Text style={styles.slotToggleLabel}>Transliteration</Text>
                      <Text style={styles.slotToggleHint}>Buckwalter above Arabic</Text>
                    </View>
                    <Switch
                      value={slot.arabicTranslit ?? DEFAULT_ARABIC_TRANSLIT}
                      onValueChange={(value) => updateSlotToggle(slot.slot, 'arabicTranslit', value)}
                      trackColor={{ false: '#e2e8f0', true: '#2563eb' }}
                      thumbColor={slot.arabicTranslit ?? DEFAULT_ARABIC_TRANSLIT ? '#f8fafc' : '#f1f5f9'}
                    />
                  </View>
                ) : null}
              </View>
            );
            })}
          </View>

          <SliderControl
            label="Layout height"
            value={heightRatio}
            min={0.2}
            max={0.6}
            step={0.01}
            onChange={setHeightRatio}
            formatValue={(value) => `${Math.round(value * 100)}%`}
          />
          <SliderControl
            label="Vertical shift"
            value={liftRatio}
            min={0}
            max={0.3}
            step={0.01}
            onChange={setLiftRatio}
            formatValue={(value) => `${Math.round(value * 100)}%`}
          />

          <View style={styles.previewCard}>
            <Text style={styles.previewTitle}>Layout preview</Text>
            <View
              style={[styles.previewStage, { height: previewStageHeight }]}
              onLayout={(event) => setPreviewWidth(event.nativeEvent.layout.width)}
            >
              <View
                style={[
                  styles.previewBand,
                  { height: previewBandHeight, padding: previewBandPadding, bottom: previewLift },
                ]}
              >
                <View style={styles.previewGrid}>
                  {sortedSlots.map((slot) => {
                    const label = shortLabelForLanguage(slot.language);
                    const colIndex = (slot.slot - 1) % Math.max(cols, 1);
                    const isLastCol = colIndex === Math.max(cols, 1) - 1;
                    const rowIndex = Math.floor((slot.slot - 1) / Math.max(cols, 1));
                    const isLastRow = rowIndex === Math.max(rows, 1) - 1;
                    const slotColor = SLOT_COLORS[(slot.slot - 1) % SLOT_COLORS.length];
                    return (
                      <View
                        key={slot.slot}
                        style={[
                          styles.previewCell,
                          {
                            width: previewCellWidth,
                            height: previewCellHeight,
                            marginBottom: isLastRow ? 0 : previewRowGap,
                            marginRight: isLastCol ? 0 : previewColGap,
                            backgroundColor: toRgba(slotColor, slot.language ? 0.32 : 0.12),
                          },
                        ]}
                      >
                        <Text style={[styles.previewCellValue, { fontSize: previewValueSize }]}>{label}</Text>
                      </View>
                    );
                  })}
                </View>
              </View>
            </View>
            <Text style={styles.previewHint}>
              Layout height is the subtitle band as % of full video height: {Math.round(heightRatio * 100)}%.
            </Text>
            <Text style={styles.previewHint}>
              Vertical shift lifts the entire band by % of full video height: {Math.round(liftRatio * 100)}%.
            </Text>
          </View>

          {videoUrl
            ? React.createElement('video', {
                src: videoUrl,
                preload: 'metadata',
                style: { display: 'none' },
                onLoadedMetadata: (event: any) => {
                  const target = event?.target;
                  if (target?.videoWidth && target?.videoHeight) {
                    const ratio = target.videoWidth / target.videoHeight;
                    if (ratio && ratio !== videoAspect) {
                      setVideoAspect(ratio);
                    }
                  }
                },
              })
            : null}

          <Pressable
            style={[styles.btnPrimary, (burning || isProcessing) && styles.btnDisabled]}
            onPress={burnSubtitles}
          >
            <Text style={styles.btnText}>
              {burning ? 'Burning…' : isProcessing ? 'Burning…' : 'Burn subtitles'}
            </Text>
          </Pressable>

          {message ? <Text style={styles.status}>{message}</Text> : null}
        </View>

        <View style={styles.card}>
          <Text style={styles.title}>Latest burn</Text>
          {status ? (
            <>
              <Text style={styles.meta}>Status: {status.status}</Text>
              <Text style={styles.meta}>Updated: {formatTimestamp(status.created_at)}</Text>
              {status.status === 'processing' ? (
                <View style={styles.progressWrap}>
                  <View style={styles.progressTrack}>
                    <View style={[styles.progressFill, { width: `${progressValue ?? 0}%` }]} />
                  </View>
                  <Text style={styles.progressText}>
                    Progress: {progressValue ?? 0}%
                  </Text>
                </View>
              ) : null}
              {status.error ? <Text style={styles.error}>{status.error}</Text> : null}
              {status.output_url ? (
                <View style={styles.previewBox}>
                  {React.createElement('video', {
                    src: `${API_URL}${status.output_url}?t=${status.id}`,
                    controls: true,
                    style: {
                      width: '100%',
                      borderRadius: 12,
                      backgroundColor: '#0f172a',
                    },
                  })}
                </View>
              ) : (
                <Text style={styles.meta}>No output yet.</Text>
              )}
            </>
          ) : (
            <Text style={styles.meta}>No burn output yet.</Text>
          )}
        </View>
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
  slotGrid: {
    marginTop: 12,
  },
  slotCard: {
    padding: 12,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#e2e8f0',
    backgroundColor: '#f8fafc',
    marginBottom: 10,
  },
  slotTitle: { fontSize: 13, fontWeight: '600', color: '#0f172a', marginBottom: 6 },
  slotStatus: { fontSize: 11, marginTop: 6 },
  slotStatusReady: { color: '#0f172a', fontWeight: '600' },
  slotStatusMissing: { color: '#94a3b8' },
  slotStatusMuted: { color: '#cbd5e1' },
  previewCard: {
    marginTop: 12,
    padding: 12,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#e2e8f0',
    backgroundColor: '#f8fafc',
  },
  previewTitle: { fontSize: 13, fontWeight: '700', color: '#0f172a', marginBottom: 8 },
  previewStage: {
    borderRadius: 12,
    backgroundColor: '#0f172a',
    position: 'relative',
    overflow: 'hidden',
  },
  previewBand: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    backgroundColor: 'rgba(148, 163, 184, 0.25)',
    borderTopWidth: 1,
    borderTopColor: 'rgba(148, 163, 184, 0.6)',
    padding: 8,
  },
  previewGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  previewCell: {
    borderWidth: 1,
    borderColor: 'rgba(226, 232, 240, 0.7)',
    borderRadius: 10,
    paddingHorizontal: 8,
    paddingVertical: 4,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 0,
  },
  previewCellValue: { fontSize: 12, color: '#f8fafc', fontWeight: '700', textAlign: 'center' },
  previewHint: { marginTop: 8, fontSize: 11, color: '#64748b' },
  optionRow: {
    marginTop: 12,
    flexDirection: 'row',
  },
  slotToggleRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: 10,
  },
  slotToggleText: { flex: 1, paddingRight: 12 },
  slotToggleLabel: { fontSize: 12, fontWeight: '700', color: '#0f172a' },
  slotToggleHint: { fontSize: 11, color: '#64748b', marginTop: 2 },
  select: {
    borderWidth: 1,
    borderColor: '#cbd5f5',
    borderRadius: 10,
    paddingVertical: 8,
    paddingHorizontal: 12,
    backgroundColor: 'white',
  },
  selectLabel: { fontSize: 11, textTransform: 'uppercase', color: '#64748b', marginBottom: 2 },
  selectValue: { fontSize: 14, color: '#0f172a', fontWeight: '600' },
  selectValueMuted: { color: '#94a3b8' },
  btnPrimary: {
    marginTop: 12,
    backgroundColor: '#1d4ed8',
    paddingVertical: 12,
    borderRadius: 999,
    alignItems: 'center',
  },
  btnDisabled: { opacity: 0.6 },
  btnText: { color: '#f8fafc', fontWeight: '700' },
  status: { marginTop: 10, fontSize: 12, color: '#0f172a' },
  error: { marginTop: 8, color: '#b91c1c', fontSize: 12 },
  progressWrap: { marginTop: 10 },
  progressTrack: {
    height: 8,
    borderRadius: 999,
    backgroundColor: '#e2e8f0',
    overflow: 'hidden',
  },
  progressFill: {
    height: 8,
    borderRadius: 999,
    backgroundColor: '#22c55e',
  },
  progressText: { marginTop: 6, fontSize: 12, color: '#0f172a' },
  previewBox: { marginTop: 12 },
  modalBackdrop: {
    flex: 1,
    backgroundColor: 'rgba(15, 23, 42, 0.5)',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 20,
  },
  modalCard: {
    width: '100%',
    maxWidth: 360,
    backgroundColor: 'white',
    borderRadius: 16,
    padding: 16,
  },
  modalTitle: { fontSize: 14, fontWeight: '700', color: '#0f172a', marginBottom: 8 },
  modalOption: { paddingVertical: 8, borderBottomWidth: 1, borderBottomColor: '#e2e8f0' },
  modalOptionActive: { backgroundColor: '#eff6ff' },
  modalOptionText: { color: '#0f172a', fontSize: 13 },
  modalOptionTextActive: { fontWeight: '700' },
  modalOptionTextMuted: { color: '#94a3b8' },
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
