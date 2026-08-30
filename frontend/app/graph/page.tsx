'use client';

import { useEffect, useState } from 'react';
import SiteNav from '@/components/SiteNav';
import FraudGraphView from '@/components/FraudGraphView';
import { api, ApiError } from '@/lib/api';

export default function GraphPage() {
  const [graph, setGraph] = useState<any>({ nodes: [], edges: [] });
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        setGraph(await api('/api/graph'));
      } catch (e) {
        setError(e instanceof ApiError ? e.message : 'Graph load failed');
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  return (
    <div className="cb-grid min-h-screen">
      <SiteNav compact />
      <main className="mx-auto max-w-6xl px-4 py-8">
        <h1 className="text-2xl font-black text-white">FraudGraph</h1>
        <p className="mt-2 text-sm text-slate-400">Live export from the backend NetworkX graph. Not invented in the browser.</p>
        {error && <p role="alert" className="mt-3 text-rose-300">{error}</p>}
        {loading && <p className="mt-3 text-slate-400">Loading graph…</p>}
        <div className="mt-6 h-[640px]">
          <FraudGraphView graphData={graph} />
        </div>
      </main>
    </div>
  );
}
