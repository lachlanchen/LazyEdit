import React, { useState } from 'react';
import FontAwesome from '@expo/vector-icons/FontAwesome';
import { Modal, Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';

import { useI18n } from '@/components/I18nProvider';

export default function LanguagePicker() {
  const { locale, setLocale, t, languages } = useI18n();
  const [open, setOpen] = useState(false);
  const current = languages.find((item) => item.code === locale) || languages[0];

  return (
    <>
      <Pressable style={styles.trigger} onPress={() => setOpen(true)}>
        <FontAwesome name="globe" size={14} style={styles.triggerIcon} />
        <Text style={styles.triggerLabel}>{t('language_picker_label')}</Text>
        <Text style={styles.triggerValue}>{current.label}</Text>
        <FontAwesome name="chevron-down" size={12} style={styles.triggerChevron} />
      </Pressable>
      <Modal transparent animationType="fade" visible={open} onRequestClose={() => setOpen(false)}>
        <Pressable style={styles.backdrop} onPress={() => setOpen(false)}>
          <Pressable style={styles.card} onPress={() => {}}>
            <Text style={styles.title}>{t('language_picker_label')}</Text>
            <ScrollView style={{ maxHeight: 280 }}>
              {languages.map((language) => {
                const active = language.code === locale;
                return (
                  <Pressable
                    key={language.code}
                    style={[styles.option, active && styles.optionActive]}
                    onPress={() => {
                      setLocale(language.code);
                      setOpen(false);
                    }}
                  >
                    <Text style={[styles.optionText, active && styles.optionTextActive]}>{language.label}</Text>
                    {active ? <FontAwesome name="check" size={14} style={styles.checkIcon} /> : null}
                  </Pressable>
                );
              })}
            </ScrollView>
          </Pressable>
        </Pressable>
      </Modal>
    </>
  );
}

const styles = StyleSheet.create({
  trigger: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 999,
    borderWidth: 1,
    borderColor: '#e2e8f0',
    backgroundColor: 'white',
  },
  triggerIcon: { color: '#0f172a' },
  triggerLabel: { fontSize: 11, color: '#64748b', fontWeight: '600' },
  triggerValue: { fontSize: 11, color: '#0f172a', fontWeight: '600' },
  triggerChevron: { color: '#64748b' },
  backdrop: {
    flex: 1,
    backgroundColor: 'rgba(15, 23, 42, 0.45)',
    justifyContent: 'center',
    padding: 20,
  },
  card: {
    backgroundColor: 'white',
    borderRadius: 16,
    padding: 16,
  },
  title: { fontSize: 14, fontWeight: '700', color: '#0f172a', marginBottom: 8 },
  option: {
    paddingVertical: 10,
    paddingHorizontal: 12,
    borderRadius: 10,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  optionActive: { backgroundColor: '#0f172a' },
  optionText: { fontSize: 13, color: '#0f172a' },
  optionTextActive: { color: 'white' },
  checkIcon: { color: 'white' },
});
