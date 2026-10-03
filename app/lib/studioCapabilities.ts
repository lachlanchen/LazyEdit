import { useEffect, useState } from 'react';

/** The authenticated server sets this before the bundle loads. Fail closed,
 * and defer reading it until mount so static export and hydration agree. */
export function useStudioCapabilities() {
  const remote = process.env.EXPO_PUBLIC_REMOTE_STUDIO === '1';
  const [publishing, setPublishing] = useState(!remote);
  useEffect(() => {
    setPublishing(!remote || (globalThis as any).__studioContext?.capabilities?.publishing === true);
  }, [remote]);
  return { editing: true, publishing };
}
