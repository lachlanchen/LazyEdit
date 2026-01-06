import React, { useEffect, useMemo, useState } from 'react';
import { ActivityIndicator, Modal, ScrollView, StyleSheet, Switch, Text, View, Pressable } from 'react-native';
import { Stack, useLocalSearchParams } from 'expo-router';

const API_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8787';

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

type SrtLine = {
  start: string;
  end: string;
  text: string;
};

type JaLine = {
  start: string;
  end: string;
  ja: string;
  ruby?: string;
  tokens?: JaToken[];
  furigana_pairs?: [string, string][];
};

type JaToken = {
  word: string;
  reading?: string | null;
  type?: string | null;
};

type GrammarPalette = {
  language: string;
  types: Record<string, { color: string; label?: string }>;
};

type SelectOption = {
  value: string;
  label: string;
};

const LANG_LABELS: Record<string, string> = {
  en: 'English',
  'zh-Hant': 'Chinese (Traditional)',
  'zh-Hans': 'Chinese (Simplified)',
  zh: 'Chinese',
  ja: 'Japanese',
  ko: 'Korean',
  vi: 'Vietnamese',
  ar: 'Arabic',
  fr: 'French',
  es: 'Spanish',
  ru: 'Russian',
};

const PALETTE_OPTIONS: SelectOption[] = [
  { value: 'base', label: 'Echomind' },
  { value: 'deep', label: 'Deep contrast' },
  { value: 'soft', label: 'Soft' },
  { value: 'mono', label: 'Mono (white)' },
];

const BG_COLOR_OPTIONS: SelectOption[] = [
  { value: '#000000', label: 'Black' },
  { value: '#ffffff', label: 'White' },
  { value: '#0f172a', label: 'Slate' },
  { value: '#111827', label: 'Charcoal' },
  { value: '#1e293b', label: 'Midnight' },
  { value: '#1f2937', label: 'Graphite' },
  { value: '#dbeafe', label: 'Light blue' },
  { value: '#fef9c3', label: 'Light yellow' },
];

const BG_OPACITY_OPTIONS: SelectOption[] = [
  { value: '0.2', label: '20%' },
  { value: '0.35', label: '35%' },
  { value: '0.5', label: '50%' },
  { value: '0.65', label: '65%' },
  { value: '0.8', label: '80%' },
];

const formatTimestamp = (value?: string | null) =>
  value ? value.slice(0, 19).replace('T', ' ') : 'Unknown time';

const parseSrt = (content: string): SrtLine[] => {
  const blocks = content.split(/\n\s*\n/);
  const lines: SrtLine[] = [];
  for (const block of blocks) {
    const parts = block.split('\n').filter(Boolean);
    if (parts.length < 2) continue;
    const timeLine = parts.find((line) => line.includes('-->'));
    if (!timeLine) continue;
    const [start, end] = timeLine.split('-->').map((v) => v.trim());
    const textLines = parts.filter((line) => line !== timeLine && !/^[0-9]+$/.test(line));
    lines.push({ start, end, text: textLines.join(' ') });
  }
  return lines;
};

const clamp = (value: number) => Math.max(0, Math.min(255, value));

const hexToRgb = (hex: string) => {
  const cleaned = hex.replace('#', '').trim();
  if (cleaned.length === 3) {
    const r = parseInt(cleaned[0] + cleaned[0], 16);
    const g = parseInt(cleaned[1] + cleaned[1], 16);
    const b = parseInt(cleaned[2] + cleaned[2], 16);
    return { r, g, b };
  }
  if (cleaned.length !== 6) return null;
  const r = parseInt(cleaned.slice(0, 2), 16);
  const g = parseInt(cleaned.slice(2, 4), 16);
  const b = parseInt(cleaned.slice(4, 6), 16);
  return { r, g, b };
};

const rgbaFromHex = (hex: string, alpha: number) => {
  const rgb = hexToRgb(hex) || { r: 0, g: 0, b: 0 };
  const a = Math.max(0, Math.min(1, alpha));
  return `rgba(${rgb.r}, ${rgb.g}, ${rgb.b}, ${a})`;
};

const mixColor = (hex: string, mixWith: string, ratio: number) => {
  const base = hexToRgb(hex);
  const mix = hexToRgb(mixWith);
  if (!base || !mix) return hex;
  const r = clamp(Math.round(base.r * (1 - ratio) + mix.r * ratio));
  const g = clamp(Math.round(base.g * (1 - ratio) + mix.g * ratio));
  const b = clamp(Math.round(base.b * (1 - ratio) + mix.b * ratio));
  return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b
    .toString(16)
    .padStart(2, '0')}`;
};

const isDarkColor = (hex: string) => {
  const rgb = hexToRgb(hex);
  if (!rgb) return false;
  const luminance = 0.2126 * rgb.r + 0.7152 * rgb.g + 0.0722 * rgb.b;
  return luminance < 140;
};

const OptionSelect = ({
  label,
  value,
  options,
  onChange,
  containerStyle,
}: {
  label: string;
  value: string;
  options: SelectOption[];
  onChange: (value: string) => void;
  containerStyle?: any;
}) => {
  const [open, setOpen] = useState(false);
  const current = options.find((option) => option.value === value) || options[0];
  return (
    <>
      <Pressable style={[styles.selectRow, containerStyle]} onPress={() => setOpen(true)}>
        <Text style={styles.selectLabel}>{label}</Text>
        <Text style={styles.selectValue}>{current?.label || value}</Text>
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

const SliderControl = ({
  label,
  value,
  min,
  max,
  step,
  onChange,
}: {
  label: string;
  value: number;
  min: number;
  max: number;
  step: number;
  onChange: (value: number) => void;
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
        <Text style={styles.sliderValue}>{value.toFixed(1)}</Text>
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

const isKanaChar = (char: string) => /[\u3040-\u30ff]/.test(char);
const hasKanji = (text: string) => /[\u4e00-\u9faf]/.test(text);

const toHiragana = (text: string) =>
  text.replace(/[\u30a1-\u30f6]/g, (char) =>
    String.fromCharCode(char.charCodeAt(0) - 0x60),
  );

const leadingKana = (word: string) => {
  let idx = 0;
  while (idx < word.length && isKanaChar(word[idx])) {
    idx += 1;
  }
  return word.slice(0, idx);
};

const trailingKana = (word: string) => {
  let idx = word.length - 1;
  while (idx >= 0 && isKanaChar(word[idx])) {
    idx -= 1;
  }
  return word.slice(idx + 1);
};

const normalizeTokens = (tokens?: JaToken[]) =>
  (tokens || [])
    .map((token) => {
      const word = token?.word ? String(token.word) : '';
      if (!word) return null;
      const reading = token?.reading ? String(token.reading) : word;
      const type = token?.type ? String(token.type) : 'other';
      return { word, reading, type };
    })
    .filter(Boolean) as JaToken[];

const tokensFromPairs = (pairs?: [string, string][]) =>
  (pairs || [])
    .map((pair) => {
      if (!pair) return null;
      const word = pair[0] ? String(pair[0]) : '';
      if (!word) return null;
      const reading = pair[1] ? String(pair[1]) : word;
      return { word, reading, type: 'other' };
    })
    .filter(Boolean) as JaToken[];

const splitTokenForRuby = (token: JaToken): JaToken[] => {
  const word = token.word ? String(token.word) : '';
  if (!word) return [];
  const readingRaw = token.reading ? String(token.reading) : '';
  const type = token.type ? String(token.type) : 'other';

  if (!hasKanji(word) || !readingRaw) {
    return [{ word, reading: '', type }];
  }

  const prefix = leadingKana(word);
  const suffix = trailingKana(word);
  if (!prefix && !suffix) {
    return [{ word, reading: toHiragana(readingRaw), type }];
  }

  let reading = toHiragana(readingRaw);
  const prefixNorm = toHiragana(prefix);
  const suffixNorm = toHiragana(suffix);
  if (prefixNorm && reading.startsWith(prefixNorm)) {
    reading = reading.slice(prefixNorm.length);
  }
  if (suffixNorm && reading.endsWith(suffixNorm)) {
    reading = reading.slice(0, Math.max(reading.length - suffixNorm.length, 0));
  }

  const core = word.slice(prefix.length, word.length - suffix.length);
  const segments: JaToken[] = [];
  if (prefix) segments.push({ word: prefix, reading: '', type });
  if (core) segments.push({ word: core, reading, type });
  if (suffix) segments.push({ word: suffix, reading: '', type });
  return segments.length ? segments : [{ word, reading, type }];
};

const buildDisplayTokens = (line: JaLine) => {
  const tokens = line.tokens?.length ? normalizeTokens(line.tokens) : tokensFromPairs(line.furigana_pairs);
  if (!tokens.length) return [];
  return tokens.flatMap(splitTokenForRuby);
};

export default function TranslationsScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const [translations, setTranslations] = useState<TranslationDetail[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeLang, setActiveLang] = useState<string | null>(null);
  const [srtLines, setSrtLines] = useState<SrtLine[]>([]);
  const [jaLines, setJaLines] = useState<JaLine[]>([]);
  const [contentLoading, setContentLoading] = useState(false);
  const [error, setError] = useState<string>('');
  const [palette, setPalette] = useState<GrammarPalette | null>(null);
  const [outlineEnabled, setOutlineEnabled] = useState(true);
  const [shadowEnabled, setShadowEnabled] = useState(true);
  const [outlineThickness, setOutlineThickness] = useState(10);
  const [paletteMode, setPaletteMode] = useState('base');
  const [bgColor, setBgColor] = useState('#000000');
  const [bgOpacity, setBgOpacity] = useState('0.5');
  const [styleLoaded, setStyleLoaded] = useState(false);

  const headerTitle = useMemo(() => 'Translations', []);

  useEffect(() => {
    if (!id) return;
    (async () => {
      setLoading(true);
      try {
        const resp = await fetch(`${API_URL}/api/videos/${id}/translations`);
        const json = await resp.json();
        if (!resp.ok) {
          setError(json.error || 'Failed to load translations');
          setTranslations([]);
          return;
        }
        const items: TranslationDetail[] = json.translations || [];
        setTranslations(items);
        if (!activeLang && items.length) {
          const preferred = items.find((item) => item.language_code === 'ja') || items[0];
          setActiveLang(preferred.language_code);
        }
      } catch (e: any) {
        setError(e?.message || 'Failed to load translations');
        setTranslations([]);
      } finally {
        setLoading(false);
      }
    })();
  }, [id]);

  useEffect(() => {
    if (!activeLang) return;
    const current = translations.find((item) => item.language_code === activeLang);
    if (!current) return;
    (async () => {
      setContentLoading(true);
      setError('');
      setSrtLines([]);
      setJaLines([]);
      try {
        if (activeLang === 'ja' && current.json_url) {
          const resp = await fetch(`${API_URL}${current.json_url}`);
          const json = await resp.json();
          const lines = Array.isArray(json) ? (json as JaLine[]) : [];
          setJaLines(lines);
        } else if (current.srt_url) {
          const resp = await fetch(`${API_URL}${current.srt_url}`);
          const text = await resp.text();
          setSrtLines(parseSrt(text));
        }
      } catch (e: any) {
        setError(e?.message || 'Failed to load translation content');
      } finally {
        setContentLoading(false);
      }
    })();
  }, [activeLang, translations]);

  useEffect(() => {
    if (!activeLang) return;
    (async () => {
      setPalette(null);
      try {
        const resp = await fetch(`${API_URL}/api/grammar-palettes/${activeLang}`);
        if (!resp.ok) return;
        const json = await resp.json();
        setPalette(json as GrammarPalette);
      } catch (_err) {
        setPalette(null);
      }
    })();
  }, [activeLang]);

  useEffect(() => {
    (async () => {
      try {
        const resp = await fetch(`${API_URL}/api/ui-settings/translation_style`);
        const json = await resp.json();
        if (!resp.ok) return;
        const value = json.value || {};
        if (typeof value.outlineEnabled === 'boolean') setOutlineEnabled(value.outlineEnabled);
        if (typeof value.shadowEnabled === 'boolean') setShadowEnabled(value.shadowEnabled);
        if (typeof value.outlineThickness === 'number') setOutlineThickness(value.outlineThickness);
        if (typeof value.paletteMode === 'string') setPaletteMode(value.paletteMode);
        if (typeof value.bgColor === 'string') setBgColor(value.bgColor);
        if (typeof value.bgOpacity === 'number') setBgOpacity(String(value.bgOpacity));
        if (typeof value.bgOpacity === 'string') setBgOpacity(value.bgOpacity);
      } catch (_err) {
        // ignore load failures; keep defaults
      } finally {
        setStyleLoaded(true);
      }
    })();
  }, []);

  useEffect(() => {
    if (!styleLoaded) return;
    const payload = {
      outlineEnabled,
      shadowEnabled,
      outlineThickness,
      paletteMode,
      bgColor,
      bgOpacity: Number(bgOpacity),
    };
    const timeout = setTimeout(async () => {
      try {
        await fetch(`${API_URL}/api/ui-settings/translation_style`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });
      } catch (_err) {
        // ignore save failures
      }
    }, 250);
    return () => clearTimeout(timeout);
  }, [outlineEnabled, shadowEnabled, outlineThickness, paletteMode, bgColor, bgOpacity, styleLoaded]);

  if (loading) {
    return (
      <View style={styles.container}>
        <Stack.Screen options={{ title: headerTitle, headerBackTitle: 'Video' }} />
        <ActivityIndicator />
        <Text style={styles.loadingText}>Loading translations...</Text>
      </View>
    );
  }

  if (!translations.length) {
    return (
      <View style={styles.container}>
        <Stack.Screen options={{ title: headerTitle, headerBackTitle: 'Video' }} />
        <Text style={styles.title}>No translations yet</Text>
        {error ? <Text style={styles.error}>{error}</Text> : null}
      </View>
    );
  }

  const active = translations.find((item) => item.language_code === activeLang) || translations[0];
  const bgAlpha = Number(bgOpacity);
  const useBg = bgAlpha > 0;
  const lineTextColor = useBg && bgAlpha >= 0.35 && isDarkColor(bgColor) ? '#f8fafc' : '#0f172a';

  const applyPaletteMode = (color: string) => {
    if (paletteMode === 'mono') return '#f8fafc';
    if (paletteMode === 'soft') return mixColor(color, '#ffffff', 0.22);
    if (paletteMode === 'deep') return mixColor(color, '#000000', 0.35);
    return color;
  };

  const resolveTokenColor = (tokenType?: string | null) => {
    const base = palette?.types?.[tokenType || '']?.color || palette?.types?.other?.color || '#0f172a';
    return applyPaletteMode(base);
  };

  const outlineColor = 'rgba(0, 0, 0, 0.85)';
  const shadowColor = 'rgba(0, 0, 0, 0.55)';
  const buildTextStyle = (baseStyle: any, color: string) => {
    if (outlineEnabled) {
      return [
        baseStyle,
        {
          color,
          textShadowColor: outlineColor,
          textShadowOffset: { width: 0, height: 0 },
          textShadowRadius: outlineThickness,
        },
      ];
    }
    if (shadowEnabled) {
      return [
        baseStyle,
        {
          color,
          textShadowColor: shadowColor,
          textShadowOffset: { width: 1, height: 1 },
          textShadowRadius: 1,
        },
      ];
    }
    return [baseStyle, { color }];
  };

  return (
    <View style={styles.container}>
      <Stack.Screen options={{ title: headerTitle, headerBackTitle: 'Video' }} />
      <Text style={styles.title}>Translations</Text>
      <Text style={styles.meta}>Updated: {formatTimestamp(active.created_at)}</Text>

      <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.tabs}>
        {translations.map((item) => {
          const isActive = item.language_code === activeLang;
          return (
            <Pressable
              key={item.id}
              style={[styles.tab, isActive && styles.tabActive]}
              onPress={() => setActiveLang(item.language_code)}
            >
              <Text style={[styles.tabText, isActive && styles.tabTextActive]}>
                {LANG_LABELS[item.language_code] || item.language_code}
              </Text>
            </Pressable>
          );
        })}
      </ScrollView>

      <View style={styles.card}>
        <Text style={styles.cardTitle}>{LANG_LABELS[active.language_code] || active.language_code}</Text>
        <Text style={styles.cardMeta}>Status: {active.status}</Text>
        {active.error ? <Text style={styles.error}>{active.error}</Text> : null}

        <View style={styles.displayCard}>
          <Text style={styles.displayTitle}>Display options</Text>
          <View style={styles.optionGrid}>
            <View style={styles.optionItem}>
              <View style={styles.toggleRowCompact}>
                <View style={styles.toggleText}>
                  <Text style={styles.toggleLabel}>Outline</Text>
                  <Text style={styles.toggleHint}>Sharp black edge</Text>
                </View>
                <Switch
                  value={outlineEnabled}
                  onValueChange={setOutlineEnabled}
                  trackColor={{ false: '#e2e8f0', true: '#2563eb' }}
                  thumbColor={outlineEnabled ? '#f8fafc' : '#f1f5f9'}
                />
              </View>
            </View>
            <View style={styles.optionItem}>
              <View style={styles.toggleRowCompact}>
                <View style={styles.toggleText}>
                  <Text style={styles.toggleLabel}>Shadow</Text>
                  <Text style={styles.toggleHint}>Subtitle drop shadow</Text>
                </View>
                <Switch
                  value={shadowEnabled}
                  onValueChange={setShadowEnabled}
                  trackColor={{ false: '#e2e8f0', true: '#2563eb' }}
                  thumbColor={shadowEnabled ? '#f8fafc' : '#f1f5f9'}
                />
              </View>
            </View>
            <OptionSelect
              label="Palette"
              value={paletteMode}
              options={PALETTE_OPTIONS}
              onChange={setPaletteMode}
              containerStyle={styles.optionItem}
            />
            <OptionSelect
              label="Background"
              value={bgColor}
              options={BG_COLOR_OPTIONS}
              onChange={setBgColor}
              containerStyle={styles.optionItem}
            />
            <OptionSelect
              label="Opacity"
              value={bgOpacity}
              options={BG_OPACITY_OPTIONS}
              onChange={setBgOpacity}
              containerStyle={styles.optionItem}
            />
          </View>
          <SliderControl
            label="Outline thickness"
            value={outlineThickness}
            min={0}
            max={20}
            step={1}
            onChange={setOutlineThickness}
          />
        </View>

        {contentLoading ? (
          <ActivityIndicator style={{ marginTop: 12 }} />
        ) : active.language_code === 'ja' ? (
          <ScrollView style={styles.content} contentContainerStyle={{ paddingBottom: 16 }}>
            {jaLines.length ? (
              jaLines.map((line, idx) => {
                const displayTokens = buildDisplayTokens(line);
                const lineBlockStyle = [
                  styles.lineBlock,
                  useBg && styles.lineBlockWithBg,
                  useBg && { backgroundColor: rgbaFromHex(bgColor, bgAlpha) },
                ];
                const lineTimeColor = useBg && isDarkColor(bgColor) ? '#e2e8f0' : '#64748b';
                return (
                  <View key={`${line.start}-${idx}`} style={lineBlockStyle}>
                    <Text style={[styles.lineTime, { color: lineTimeColor }]}>{line.start} → {line.end}</Text>
                    {displayTokens.length ? (
                      <View style={styles.furiganaLine}>
                        {displayTokens.map((token, pIdx) => {
                          const word = token.word || '';
                          const reading = token.reading || '';
                          const showReading = !!reading && hasKanji(word);
                          const tokenColor = resolveTokenColor(token.type);
                          return (
                            <View key={`${line.start}-${pIdx}`} style={styles.furiganaToken}>
                              <Text style={buildTextStyle(styles.furiganaText, showReading ? tokenColor : 'transparent')}>
                                {showReading ? reading : ' '}
                              </Text>
                              <Text style={buildTextStyle(styles.jaText, tokenColor)}>{word}</Text>
                            </View>
                          );
                        })}
                      </View>
                    ) : (
                      <Text style={buildTextStyle(styles.jaText, lineTextColor)}>{line.ja}</Text>
                    )}
                  </View>
                );
              })
            ) : (
              <Text style={styles.empty}>No Japanese lines available.</Text>
            )}
          </ScrollView>
        ) : (
          <ScrollView style={styles.content} contentContainerStyle={{ paddingBottom: 16 }}>
            {srtLines.length ? (
              srtLines.map((line, idx) => {
                const lineBlockStyle = [
                  styles.lineBlock,
                  useBg && styles.lineBlockWithBg,
                  useBg && { backgroundColor: rgbaFromHex(bgColor, bgAlpha) },
                ];
                const lineTimeColor = useBg && isDarkColor(bgColor) ? '#e2e8f0' : '#64748b';
                return (
                  <View key={`${line.start}-${idx}`} style={lineBlockStyle}>
                    <Text style={[styles.lineTime, { color: lineTimeColor }]}>{line.start} → {line.end}</Text>
                    <Text style={buildTextStyle(styles.lineText, lineTextColor)}>{line.text}</Text>
                  </View>
                );
              })
            ) : (
              <Text style={styles.empty}>No subtitle lines available.</Text>
            )}
          </ScrollView>
        )}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16, backgroundColor: '#fbfdff' },
  title: { fontSize: 20, fontWeight: '700', color: '#0f172a' },
  meta: { fontSize: 12, color: '#475569', marginTop: 4 },
  tabs: { marginTop: 12, flexGrow: 0 },
  tab: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 999,
    borderWidth: 1,
    borderColor: '#e2e8f0',
    marginRight: 8,
    backgroundColor: '#f8fafc',
  },
  tabActive: { backgroundColor: '#1d4ed8', borderColor: '#1d4ed8' },
  tabText: { fontSize: 12, fontWeight: '600', color: '#0f172a' },
  tabTextActive: { color: '#f8fafc' },
  card: {
    marginTop: 12,
    padding: 14,
    borderRadius: 14,
    borderWidth: 1,
    borderColor: '#e2e8f0',
    backgroundColor: 'white',
    flex: 1,
  },
  cardTitle: { fontSize: 16, fontWeight: '700', color: '#0f172a' },
  cardMeta: { fontSize: 12, color: '#475569', marginTop: 4 },
  displayCard: {
    marginTop: 12,
    padding: 12,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#e2e8f0',
    backgroundColor: '#f8fafc',
  },
  displayTitle: { fontSize: 12, fontWeight: '700', color: '#0f172a', marginBottom: 8 },
  optionGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  optionItem: {
    width: '48%',
    marginBottom: 8,
  },
  toggleRowCompact: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  toggleText: { flex: 1, marginRight: 12 },
  toggleLabel: { fontSize: 12, fontWeight: '600', color: '#0f172a' },
  toggleHint: { fontSize: 11, color: '#64748b', marginTop: 2 },
  selectRow: {
    paddingVertical: 10,
    paddingHorizontal: 12,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: '#e2e8f0',
    backgroundColor: 'white',
  },
  selectLabel: { fontSize: 11, color: '#64748b' },
  selectValue: { fontSize: 13, fontWeight: '600', color: '#0f172a', marginTop: 4 },
  content: { marginTop: 10 },
  lineBlock: { marginBottom: 12 },
  lineBlockWithBg: { paddingVertical: 8, paddingHorizontal: 10, borderRadius: 10 },
  lineTime: { fontSize: 11, color: '#64748b', marginBottom: 4 },
  lineText: { fontSize: 14, color: '#0f172a' },
  furiganaLine: { flexDirection: 'row', flexWrap: 'wrap', alignItems: 'flex-end' },
  furiganaToken: { alignItems: 'center', marginRight: 4, marginBottom: 2 },
  furiganaText: {
    fontSize: 9,
    color: '#1d4ed8',
    lineHeight: 10,
    minHeight: 10,
  },
  jaText: {
    fontSize: 14,
    color: '#0f172a',
  },
  modalBackdrop: {
    flex: 1,
    backgroundColor: 'rgba(15, 23, 42, 0.55)',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 16,
  },
  modalCard: {
    width: '100%',
    maxWidth: 360,
    borderRadius: 14,
    padding: 16,
    backgroundColor: 'white',
  },
  modalTitle: { fontSize: 14, fontWeight: '700', color: '#0f172a', marginBottom: 10 },
  modalOption: {
    paddingVertical: 10,
    paddingHorizontal: 12,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: '#e2e8f0',
    marginBottom: 8,
  },
  modalOptionActive: { backgroundColor: '#1d4ed8', borderColor: '#1d4ed8' },
  modalOptionText: { fontSize: 13, color: '#0f172a', fontWeight: '600' },
  modalOptionTextActive: { color: '#f8fafc' },
  sliderRow: { marginTop: 8 },
  sliderHeader: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', marginBottom: 6 },
  sliderLabel: { fontSize: 11, color: '#64748b' },
  sliderValue: { fontSize: 11, fontWeight: '600', color: '#0f172a' },
  sliderTrack: {
    height: 8,
    borderRadius: 999,
    backgroundColor: '#e2e8f0',
    overflow: 'hidden',
    justifyContent: 'center',
  },
  sliderFill: {
    position: 'absolute',
    left: 0,
    top: 0,
    bottom: 0,
    backgroundColor: '#0f766e',
  },
  sliderThumb: {
    position: 'absolute',
    width: 18,
    height: 18,
    borderRadius: 999,
    backgroundColor: '#0f766e',
    borderWidth: 2,
    borderColor: 'white',
    top: -5,
    marginLeft: -9,
  },
  empty: { color: '#64748b', marginTop: 8 },
  error: { fontSize: 12, color: '#b91c1c', marginTop: 8 },
  loadingText: { marginTop: 8, color: '#475569' },
});
