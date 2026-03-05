import React, { createContext, useCallback, useContext, useMemo, useRef, useState } from 'react';

const ToastContext = createContext(null);

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);
  const idRef = useRef(0);

  const remove = useCallback((id) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const push = useCallback((partial) => {
    const id = ++idRef.current;
    const toast = {
      id,
      title: partial.title || '',
      description: partial.description || '',
      variant: partial.variant || 'info',
      duration: partial.duration ?? 4000,
    };
    setToasts((prev) => [...prev, toast]);
    if (toast.duration > 0) {
      setTimeout(() => remove(id), toast.duration);
    }
    return id;
  }, [remove]);

  const api = useMemo(() => ({
    push,
    success: (opts) => push({ ...opts, variant: 'success' }),
    error: (opts) => push({ ...opts, variant: 'error' }),
    info: (opts) => push({ ...opts, variant: 'info' }),
    remove,
  }), [push, remove]);

  return (
    <ToastContext.Provider value={api}>
      {children}
      <div className="fixed bottom-4 right-4 z-[60] space-y-3">
        {toasts.map((t) => (
          <div
            key={t.id}
            className={`min-w-[260px] max-w-sm rounded-xl p-4 shadow-lg border animate-slide-up bg-white ${
              t.variant === 'success' ? 'border-green-200' : t.variant === 'error' ? 'border-red-200' : 'border-gray-200'
            }`}
          >
            <div className="flex items-start gap-3">
              <div className={`h-2 w-2 mt-2 rounded-full ${
                t.variant === 'success' ? 'bg-green-500' : t.variant === 'error' ? 'bg-red-500' : 'bg-blue-500'
              }`} />
              <div className="flex-1">
                {t.title ? <div className="font-semibold text-gray-900">{t.title}</div> : null}
                {t.description ? <div className="text-sm text-gray-600 mt-0.5">{t.description}</div> : null}
              </div>
              <button
                aria-label="Close notification"
                className="text-gray-400 hover:text-gray-600"
                onClick={() => remove(t.id)}
              >
                ×
              </button>
            </div>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}

export function useToast() {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error('useToast must be used within ToastProvider');
  return ctx;
}
