import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

export default function EditorScreen() {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Manual Editor</Text>
      <Text style={styles.sub}>
        Coming soon: adjust subtitles, language mix, line breaks, and font sizes with live preview.
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16, backgroundColor: '#fbfdff' },
  title: { fontSize: 22, fontWeight: '700', color: '#0f172a' },
  sub: { marginTop: 8, color: '#334155' },
});

