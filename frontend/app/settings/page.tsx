'use client';

import { useEffect, useState } from 'react';
import SiteNav from '@/components/SiteNav';
import { api, ApiError } from '@/lib/api';

export default function SettingsPage() {
  const [cfg, setCfg] = useState<any>(null);
  const [health, setHealth] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      try {
        setCfg(await api('/api/config'));
        setHealth(await api('/api/health'));
      } catch (e) {
        setError(e instanceof ApiError ? e.message : 'Config load failed');
      }
    })();
  }, []);

  return (
    <div className="cb-grid min-h-screen">
      <SiteNav compact />
      <main className="mx-auto max-w-3xl px-4 py-8">
        <h1 className="text-2xl font-black text-white">Settings</h1>
        <p className="mt-2 text-sm text-slate-400">Public configuration only. Secrets are never returned by the API.</p>
        {error && <p role="alert" className="mt-3 text-rose-300">{error}</p>}
        <pre className="terminal-panel mt-6 overflow-auto rounded-xl p-4 text-xs text-slate-300">
          {JSON.stringify({ health, config: cfg }, null, 2)}
        </pre>
      </main>
    </div>
  );
}
