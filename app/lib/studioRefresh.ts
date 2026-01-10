type StudioRefreshListener = () => void;

const listeners = new Set<StudioRefreshListener>();

export const subscribeStudioRefresh = (listener: StudioRefreshListener) => {
  listeners.add(listener);
  return () => {
    listeners.delete(listener);
  };
};

export const triggerStudioRefresh = () => {
  for (const listener of Array.from(listeners)) {
    try {
      listener();
    } catch (_err) {
      // ignore listener errors
    }
  }
};
