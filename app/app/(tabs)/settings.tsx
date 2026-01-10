import React from 'react';
import { StyleSheet, Text, View } from 'react-native';

import { useI18n } from '@/components/I18nProvider';

const API_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8787';

export default function SettingsScreen() {
  const { t } = useI18n();

  return (
    <View style={styles.container}>
      <Text style={styles.title}>{t('settings_title')}</Text>
      <Text style={styles.backend}>{t('settings_backend_label', { value: API_URL })}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16, backgroundColor: '#fbfdff' },
  title: { fontSize: 22, fontWeight: '700', color: '#0f172a' },
  backend: { marginTop: 12, color: '#64748b', fontSize: 12 },
});
