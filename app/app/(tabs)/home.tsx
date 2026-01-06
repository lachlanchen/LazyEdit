import React, { useEffect, useMemo, useState } from 'react';
import { ActivityIndicator, Platform, Pressable, StyleSheet, Text, View } from 'react-native';
import * as DocumentPicker from 'expo-document-picker';
import * as FileSystem from 'expo-file-system';

const API_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8787';

const formatBytes = (bytes?: number | null) => {
  if (bytes === undefined || bytes === null) return 'Unknown size';
  if (bytes === 0) return '0 B';
  const units = ['B', 'KB', 'MB', 'GB'];
  let size = bytes;
  let unitIndex = 0;
  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024;
    unitIndex += 1;
  }
  const decimals = size >= 10 || unitIndex === 0 ? 0 : 1;
  return `${size.toFixed(decimals)} ${units[unitIndex]}`;
};

export default function HomeScreen() {
  const [picked, setPicked] = useState<DocumentPicker.DocumentPickerAsset | null>(null);
  const [status, setStatus] = useState<string>('');
  const [statusTone, setStatusTone] = useState<'neutral' | 'good' | 'bad'>('neutral');
  const [uploading, setUploading] = useState(false);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);

  useEffect(() => {
    if (Platform.OS !== 'web') return;
    if (!picked) {
      setPreviewUrl(null);
      return;
    }
    const file = (picked as any).file as File | undefined;
    if (!file) {
      setPreviewUrl(null);
      return;
    }
    const url = URL.createObjectURL(file);
    setPreviewUrl(url);
    return () => URL.revokeObjectURL(url);
  }, [picked]);

  const fileLabel = useMemo(() => {
    if (!picked) return null;
    return picked.name || 'Untitled video';
  }, [picked]);

  const fileMeta = useMemo(() => {
    if (!picked) return null;
    const size = formatBytes(picked.size);
    const type = picked.mimeType || 'video';
    return `${size} · ${type}`;
  }, [picked]);

  const pick = async () => {
    const res = await DocumentPicker.getDocumentAsync({
      multiple: false,
      type: ['video/*'],
    });
    if (res.canceled) return;
    setPicked(res.assets[0]);
    setStatus('Selected. Ready to upload.');
    setStatusTone('neutral');
  };

  const upload = async () => {
    if (!picked || uploading) return;
    setUploading(true);
    setStatus('Uploading...');
    setStatusTone('neutral');
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
          setStatusTone('bad');
          return;
        }
        const label = json.file_path || json.message || 'Upload complete';
        const id = json.video_id ? ` (id: ${json.video_id})` : '';
        setStatus(`Uploaded: ${label}${id}`);
        setStatusTone('good');
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
          setStatusTone('bad');
          return;
        }
        const label = json.file_path || json.message || 'Upload complete';
        const id = json.video_id ? ` (id: ${json.video_id})` : '';
        setStatus(`Uploaded: ${label}${id}`);
        setStatusTone('good');
      }
    } catch (e: any) {
      setStatus(`Upload failed: ${e?.message || String(e)}`);
      setStatusTone('bad');
    } finally {
      setUploading(false);
    }
  };

  const statusStyle =
    statusTone === 'good' ? styles.statusGood : statusTone === 'bad' ? styles.statusBad : styles.statusNeutral;

  return (
    <View style={styles.container}>
      <View style={styles.content}>
        <Text style={styles.title}>LazyEdit</Text>
        <Text style={styles.subtitle}>Multilingual Video Editor</Text>

        <View style={styles.stepRow}>
          <View style={styles.stepBadge}>
            <Text style={styles.stepText}>1</Text>
          </View>
          <Text style={styles.stepLabel}>Pick a video</Text>
        </View>

        <Pressable style={styles.btnPrimary} onPress={pick}>
          <Text style={styles.btnText}>{picked ? 'Pick another video' : 'Pick a video'}</Text>
        </Pressable>

        <View style={styles.card}>
          {picked ? (
            <>
              <Text style={styles.cardTitle}>Selected video</Text>
              <Text style={styles.fileName} numberOfLines={1}>
                {fileLabel}
              </Text>
              <Text style={styles.fileMeta}>{fileMeta}</Text>
              {Platform.OS === 'web' && previewUrl ? (
                <View style={styles.previewBox}>
                  {React.createElement('video', {
                    src: previewUrl,
                    style: { width: '100%', borderRadius: 12, maxHeight: 260 },
                    controls: true,
                    preload: 'metadata',
                  })}
                </View>
              ) : (
                <Text style={styles.previewHint}>Preview available on web. Ready to upload.</Text>
              )}
            </>
          ) : (
            <>
              <Text style={styles.cardTitle}>No video selected</Text>
              <Text style={styles.previewHint}>Pick a video to preview and upload.</Text>
            </>
          )}
        </View>

        <View style={styles.stepRow}>
          <View style={styles.stepBadge}>
            <Text style={styles.stepText}>2</Text>
          </View>
          <Text style={styles.stepLabel}>Upload to backend</Text>
        </View>

        <Pressable
          disabled={!picked || uploading}
          style={[styles.btnSecondary, (!picked || uploading) && styles.btnDisabled]}
          onPress={upload}
        >
          <View style={styles.btnContent}>
            {uploading && <ActivityIndicator color="white" style={{ marginRight: 8 }} />}
            <Text style={styles.btnText}>{uploading ? 'Uploading...' : 'Upload'}</Text>
          </View>
        </Pressable>

        {status ? <Text style={[styles.status, statusStyle]}>{status}</Text> : null}
      </View>
      <Text style={styles.help}>Backend: {API_URL}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 24,
    backgroundColor: '#fbfdff',
  },
  content: {
    flex: 1,
    width: '100%',
    maxWidth: 680,
    alignSelf: 'center',
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
  stepRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 18,
    marginBottom: 8,
  },
  stepBadge: {
    width: 24,
    height: 24,
    borderRadius: 12,
    backgroundColor: '#0f172a',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 8,
  },
  stepText: { color: 'white', fontSize: 12, fontWeight: '700' },
  stepLabel: { color: '#0f172a', fontWeight: '600' },
  btnPrimary: {
    backgroundColor: '#3b82f6',
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderRadius: 12,
    alignSelf: 'flex-start',
  },
  btnSecondary: {
    backgroundColor: '#fc8eac',
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderRadius: 12,
    alignSelf: 'flex-start',
  },
  btnDisabled: {
    opacity: 0.5,
  },
  btnContent: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  btnText: {
    color: 'white',
    fontWeight: '600',
  },
  card: {
    marginTop: 14,
    padding: 16,
    borderRadius: 16,
    backgroundColor: 'white',
    borderWidth: 1,
    borderColor: '#e2e8f0',
  },
  cardTitle: {
    fontSize: 14,
    fontWeight: '700',
    color: '#0f172a',
    marginBottom: 6,
  },
  fileName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#111827',
  },
  fileMeta: {
    marginTop: 2,
    color: '#475569',
    fontSize: 12,
  },
  previewBox: {
    marginTop: 12,
    borderRadius: 14,
    overflow: 'hidden',
    backgroundColor: '#0f172a',
  },
  previewHint: {
    marginTop: 8,
    color: '#475569',
    fontSize: 12,
  },
  status: {
    marginTop: 14,
    fontSize: 12,
  },
  statusNeutral: { color: '#0f172a' },
  statusGood: { color: '#15803d' },
  statusBad: { color: '#b91c1c' },
  help: { color: '#64748b', fontSize: 12, alignSelf: 'center' },
});
