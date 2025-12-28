import React, { useState } from 'react';
import { View, Text, StyleSheet, Pressable, Platform } from 'react-native';
import * as DocumentPicker from 'expo-document-picker';
import * as FileSystem from 'expo-file-system';

const API_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8787';

export default function HomeScreen() {
  const [picked, setPicked] = useState<DocumentPicker.DocumentPickerAsset | null>(null);
  const [status, setStatus] = useState<string>('');

  const pick = async () => {
    const res = await DocumentPicker.getDocumentAsync({
      multiple: false,
      type: ['video/*'],
    });
    if (res.canceled) return;
    setPicked(res.assets[0]);
    setStatus('Ready to upload');
  };

  const upload = async () => {
    if (!picked) return;
    setStatus('Uploading...');
    try {
      if (Platform.OS === 'web') {
        // Web: the asset is a File object already
        const file = picked as any; // has .file property in web
        const form = new FormData();
        form.append('video', (file.file as File) ?? (file as any), picked.name || 'video.mp4');
        const resp = await fetch(`${API_URL}/upload`, { method: 'POST', body: form as any });
        const json = await resp.json();
        if (!resp.ok) {
          setStatus(`Upload failed: ${json.error || json.message || resp.statusText}`);
          return;
        }
        const label = json.file_path || json.message || 'Upload complete';
        const id = json.video_id ? ` (id: ${json.video_id})` : '';
        setStatus(`Uploaded: ${label}${id}`);
      } else {
        // Native: use FileSystem upload for reliability
        const resp = await FileSystem.uploadAsync(`${API_URL}/upload`, picked.uri, {
          fieldName: 'video',
          httpMethod: 'POST',
          uploadType: 'multipart' as any,
          parameters: { filename: picked.name || 'video.mp4' },
        });
        const json = JSON.parse(resp.body);
        if (resp.status >= 400) {
          setStatus(`Upload failed: ${json.error || json.message || `HTTP ${resp.status}`}`);
          return;
        }
        const label = json.file_path || json.message || 'Upload complete';
        const id = json.video_id ? ` (id: ${json.video_id})` : '';
        setStatus(`Uploaded: ${label}${id}`);
      }
    } catch (e: any) {
      setStatus(`Upload failed: ${e?.message || String(e)}`);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>LazyEdit</Text>
      <Text style={styles.subtitle}>Multilingual Video Editor</Text>
      <View style={{ height: 16 }} />
      <Pressable style={styles.btnPrimary} onPress={pick}>
        <Text style={styles.btnText}>{picked ? 'Pick another video' : 'Pick a video'}</Text>
      </Pressable>
      <View style={{ height: 8 }} />
      <Pressable disabled={!picked} style={[styles.btnSecondary, !picked && styles.btnDisabled]} onPress={upload}>
        <Text style={styles.btnText}>Upload</Text>
      </Pressable>
      <View style={{ height: 16 }} />
      <Text style={styles.status}>{status}</Text>
      <View style={{ height: 24 }} />
      <Text style={styles.help}>Backend: {API_URL}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    padding: 24,
    backgroundColor: '#fbfdff',
  },
  title: {
    fontSize: 28,
    fontWeight: '700',
    color: '#111827',
  },
  subtitle: {
    fontSize: 16,
    color: '#334155',
  },
  btnPrimary: {
    backgroundColor: '#3b82f6',
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderRadius: 12,
  },
  btnSecondary: {
    backgroundColor: '#fc8eac',
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderRadius: 12,
  },
  btnDisabled: {
    opacity: 0.5,
  },
  btnText: {
    color: 'white',
    fontWeight: '600',
  },
  status: {
    color: '#0f172a',
  },
  help: { color: '#64748b', fontSize: 12 },
});
