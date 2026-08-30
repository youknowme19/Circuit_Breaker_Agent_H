'use client';

import { useCallback, useEffect, useState } from 'react';
import SiteNav from '@/components/SiteNav';
import AuditChainView from '@/components/AuditChainView';
import { api, ApiError } from '@/lib/api';

export default function AuditPage() {
  const [events, setEvents] = useState<any[]>([]);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      setEvents(await api('/api/audit'));
      setError(null);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : 'Audit load failed');
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  return (
    <div className="cb-grid min-h-screen">
      <SiteNav compact />
      <main className="mx-auto max-w-4xl px-4 py-8">
        <h1 className="text-2xl font-black text-white">Audit chain</h1>
        <p className="mt-2 text-sm text-slate-400">VERIFY CHAIN calls <code>/api/audit/verify</code>. Not simulated.</p>
        {error && <p role="alert" className="mt-3 text-rose-300">{error}</p>}
        <div className="mt-6 h-[720px]">
          <AuditChainView
            events={events}
            onVerify={async () => api('/api/audit/verify', { method: 'POST' })}
            onTamperSimulate={async (eventId) => {
              await api('/api/audit/tamper-simulate', {
                method: 'POST',
                body: JSON.stringify({ event_id: eventId, new_decision: 'TAMPERED_ALLOW' }),
              });
              await load();
            }}
          />
        </div>
      </main>
    </div>
  );
}
