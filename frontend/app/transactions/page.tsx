'use client';

import { useEffect, useState } from 'react';
import SiteNav from '@/components/SiteNav';
import { api, ApiError } from '@/lib/api';

export default function TransactionsPage() {
  const [rows, setRows] = useState<any[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const feed = await api<any[]>('/api/actions/feed');
        setRows(feed);
      } catch (e) {
        setError(e instanceof ApiError ? e.message : 'Failed to load');
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const statusOf = (row: any) => {
    if (row.transaction) return 'EXECUTED';
    return row.decision?.decision || 'UNKNOWN';
  };

  return (
    <div className="cb-grid min-h-screen">
      <SiteNav compact />
      <main className="mx-auto max-w-7xl px-4 py-8">
        <h1 className="text-2xl font-black text-white">Live transaction monitor</h1>
        {error && <p role="alert" className="mt-3 text-rose-300">{error}</p>}
        {loading && <p className="mt-3 text-slate-400">Loading…</p>}
        <div className="mt-6 overflow-x-auto rounded-xl border border-white/10">
          <table className="min-w-full text-left text-xs">
            <thead className="bg-white/5 font-mono uppercase text-slate-400">
              <tr>
                {['Time', 'Action ID', 'Source', 'Destination', 'Amount', 'Decision', 'Authorization', 'Execution', 'Risk', 'Status'].map((h) => (
                  <th key={h} className="px-3 py-2">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => {
                const st = statusOf(row);
                return (
                  <tr key={row.action?.action_id} className="border-t border-white/5">
                    <td className="px-3 py-2 font-mono text-slate-400">{String(row.action?.timestamp || '').slice(11, 19)}</td>
                    <td className="px-3 py-2 font-mono">{row.action?.action_id}</td>
                    <td className="px-3 py-2">{row.action?.source_account}</td>
                    <td className="px-3 py-2">{row.action?.destination_account}</td>
                    <td className="px-3 py-2">${Number(row.action?.amount || 0).toLocaleString()}</td>
                    <td className="px-3 py-2">{row.decision?.decision}</td>
                    <td className="px-3 py-2">{row.decision?.authorization_token || 'NONE'}</td>
                    <td className="px-3 py-2">{row.transaction?.blockchain_tx_hash || 'NONE'}</td>
                    <td className="px-3 py-2">{Number(row.decision?.risk_score || 0).toFixed(2)}</td>
                    <td className="px-3 py-2">
                      <span className={`status-pill rounded px-2 py-0.5 ${
                        st === 'EXECUTED' || st === 'ALLOW' ? 'bg-emerald-500/20 text-emerald-300' :
                        st === 'BLOCK' ? 'bg-rose-500/20 text-rose-300' : 'bg-amber-500/20 text-amber-300'
                      }`}>{st}</span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
          {!loading && rows.length === 0 && <p className="p-6 text-slate-500">No actions yet.</p>}
        </div>
      </main>
    </div>
  );
}
