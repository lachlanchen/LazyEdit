/** Remote-only resumable upload; local Studio keeps its existing upload path. */
export async function uploadRemoteVideo(base: string, blob: Blob, filename: string) {
  const request = async (path: string, init?: RequestInit) => {
    const response = await fetch(base + path, init);
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || `Upload failed (${response.status})`);
    return data;
  };
  const key = `lazyedit-upload:${filename}:${blob.size}:${(blob as File).lastModified || 0}`;
  let uploadId = localStorage.getItem(key), state;
  if (uploadId) {
    try { state = await request('/v1/studio/upload?uploadId=' + uploadId); }
    catch { uploadId = null; }
  }
  if (!uploadId) {
    state = await request('/v1/studio/uploads', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({filename,size:blob.size})});
    uploadId = state.uploadId; localStorage.setItem(key, uploadId!);
  }
  if (state.receipt) { localStorage.removeItem(key); return {resp:{ok:true},json:state.receipt}; }
  let offset = state.offset;
  while (offset < blob.size) {
    const end = Math.min(offset + 8 * 1024 * 1024, blob.size);
    let completed = false;
    for (let attempt = 0; attempt < 3 && !completed; attempt++) {
      try {
        const part = await request('/v1/studio/upload-part?uploadId=' + uploadId, {method:'PUT',headers:{'Upload-Offset':String(offset)},body:blob.slice(offset,end)});
        offset = part.offset; completed = true;
      } catch (error) {
        const current = await request('/v1/studio/upload?uploadId=' + uploadId);
        if (current.offset === end) { offset=end; completed=true; }
        else if (attempt === 2) throw error;
      }
    }
  }
  const json = await request('/v1/studio/upload-complete', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({uploadId})});
  localStorage.removeItem(key); return {resp:{ok:true},json};
}
