import React, { useEffect, useMemo, useState } from 'react';
import { View, Text, StyleSheet, Switch, FlatList } from 'react-native';

const API_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8787';

type Lang = { code: string; name: string; plugin: string; rtl?: boolean };

export default function SettingsScreen() {
  const [langs, setLangs] = useState<Lang[]>([]);
  const [selected, setSelected] = useState<Record<string, boolean>>({});
  const selectedList = useMemo(() => Object.keys(selected).filter((k) => selected[k]), [selected]);

  useEffect(() => {
    (async () => {
      try {
        const r = await fetch(`${API_URL}/api/languages`);
        const j = await r.json();
        const arr: Lang[] = j.languages || [];
        setLangs(arr);
        // default select English + Japanese
        const init: Record<string, boolean> = {};
        for (const l of arr) init[l.code] = l.code === 'en' || l.code === 'ja';
        setSelected(init);
      } catch {}
    })();
  }, []);

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Settings</Text>
      <Text style={styles.sub}>Select target languages for subtitles and features.</Text>

      <FlatList
        style={{ marginTop: 12 }}
        data={langs}
        keyExtractor={(x) => x.code}
        renderItem={({ item }) => (
          <View style={styles.row}>
            <View style={{ flex: 1 }}>
              <Text style={styles.langName}>{item.name}</Text>
              <Text style={styles.langCode}>{item.code}{item.rtl ? ' · RTL' : ''}</Text>
            </View>
            <Switch
              value={!!selected[item.code]}
              onValueChange={(v) => setSelected((s) => ({ ...s, [item.code]: v }))}
            />
          </View>
        )}
        ListEmptyComponent={<Text style={styles.empty}>Loading languages...</Text>}
      />

      <Text style={styles.selected}>Selected: {selectedList.join(', ') || 'none'}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16, backgroundColor: '#fbfdff' },
  title: { fontSize: 22, fontWeight: '700', color: '#0f172a' },
  sub: { marginTop: 8, color: '#334155' },
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 10,
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderBottomColor: '#e2e8f0',
  },
  langName: { fontSize: 16, fontWeight: '600', color: '#0f172a' },
  langCode: { fontSize: 12, color: '#64748b' },
  empty: { marginTop: 16, color: '#64748b' },
  selected: { marginTop: 12, color: '#0f172a' },
});
