import React, { useMemo, useState } from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';

import { useI18n } from '@/components/I18nProvider';

const PLATFORMS = [
  { key: 'douyin', label: 'Douyin' },
  { key: 'xiaohongshu', label: 'Xiaohongshu' },
  { key: 'shipinhao', label: 'Shipinhao' },
  { key: 'bilibili', label: 'Bilibili' },
  { key: 'youtube', label: 'YouTube' },
];

export default function EditorScreen() {
  const [selected, setSelected] = useState<Record<string, boolean>>({
    douyin: true,
    xiaohongshu: false,
    shipinhao: false,
    bilibili: false,
    youtube: false,
  });
  const { t } = useI18n();

  const selectedList = useMemo(
    () => PLATFORMS.filter((platform) => selected[platform.key]).map((platform) => platform.label),
    [selected],
  );

  return (
    <View style={styles.container}>
      <Text style={styles.title}>{t('publish_title')}</Text>
      <Text style={styles.sub}>{t('publish_subtitle')}</Text>

      <View style={styles.card}>
        <Text style={styles.sectionTitle}>{t('publish_select_title')}</Text>
        <Text style={styles.sectionHint}>{t('publish_select_hint')}</Text>

        <View style={styles.platformGrid}>
          {PLATFORMS.map((platform) => {
            const isActive = selected[platform.key];
            return (
              <Pressable
                key={platform.key}
                style={[styles.platformChip, isActive && styles.platformChipActive]}
                onPress={() =>
                  setSelected((prev) => ({ ...prev, [platform.key]: !prev[platform.key] }))
                }
              >
                <Text style={[styles.platformText, isActive && styles.platformTextActive]}>
                  {platform.label}
                </Text>
              </Pressable>
            );
          })}
        </View>

        <Text style={styles.selectedText}>
          {t('label_selected', {
            value: selectedList.length ? selectedList.join(', ') : t('label_none'),
          })}
        </Text>
      </View>

      <View style={styles.card}>
        <Text style={styles.sectionTitle}>{t('publish_manual_title')}</Text>
        <Text style={styles.sectionHint}>{t('publish_manual_hint')}</Text>
        <Pressable style={styles.publishButton}>
          <Text style={styles.publishButtonText}>{t('publish_button')}</Text>
        </Pressable>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16, backgroundColor: '#fbfdff' },
  title: { fontSize: 22, fontWeight: '700', color: '#0f172a' },
  sub: { marginTop: 8, color: '#334155' },
  card: {
    marginTop: 16,
    padding: 16,
    borderRadius: 16,
    backgroundColor: 'white',
    borderWidth: 1,
    borderColor: '#e2e8f0',
  },
  sectionTitle: { fontSize: 16, fontWeight: '700', color: '#0f172a' },
  sectionHint: { marginTop: 6, fontSize: 12, color: '#64748b' },
  platformGrid: {
    marginTop: 12,
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 10,
  },
  platformChip: {
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderRadius: 999,
    borderWidth: 1,
    borderColor: '#cbd5f5',
    backgroundColor: '#f8fafc',
  },
  platformChipActive: {
    borderColor: '#0f172a',
    backgroundColor: '#0f172a',
  },
  platformText: { fontSize: 12, fontWeight: '600', color: '#1e293b' },
  platformTextActive: { color: '#f8fafc' },
  selectedText: { marginTop: 12, fontSize: 12, color: '#0f172a' },
  publishButton: {
    marginTop: 12,
    backgroundColor: '#2563eb',
    paddingVertical: 12,
    borderRadius: 12,
    alignItems: 'center',
  },
  publishButtonText: { color: 'white', fontWeight: '700' },
});
