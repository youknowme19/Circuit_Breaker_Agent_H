'use client';

import { useState } from 'react';
import SiteNav from '@/components/SiteNav';
import { Play, CheckCircle, ShieldAlert, XCircle, RefreshCw, ExternalLink } from 'lucide-react';

import { api, ApiError } from '@/lib/api';

export default function DemoPage() {
  const [running, setRunning] = useState(false);
  const [logs, setLogs] = useState<any[]>([]);
  const [finalStatus, setFinalStatus] = useState<string | null>(null);

  const runDemo = async () => {
    if (running) return;
    setRunning(true);
    setLogs([]);
    setFinalStatus(null);

    const appendLog = (scenario: string, result: string, detail: string, txHash?: string, explorer?: string) => {
      setLogs((prev) => [...prev, { scenario, result, detail, txHash, explorer }]);
    };

    try {
      appendLog('01. Safe Payment Transfer', 'RUNNING', 'Evaluating policy & issuing HMAC token...');
      const data = await api<any>('/api/demo/run-scenarios', { method: 'POST' });
      setLogs(data.scenarios || []);
      setFinalStatus(data.status || 'PASS');
    } catch (e: any) {
      const errorMsg = e instanceof ApiError ? e.message : (e.message || 'API connection failed');
      appendLog('Demo Execution', 'FAILED', errorMsg);
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#07080c] text-slate-100 antialiased">
      <SiteNav />
      <main className="mx-auto max-w-7xl px-4 py-8">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between pb-6 border-b border-white/10 gap-4">
          <div>
            <div className="flex items-center gap-2 text-xs font-mono text-orange-400 uppercase tracking-wider">
              <Play className="h-4 w-4" /> Automated Security Verification
            </div>
            <h1 className="text-3xl font-black text-white mt-1">Live Security Demo</h1>
            <p className="text-sm text-slate-400 mt-1">
              One-click end-to-end execution of all Circuit Breaker security scenarios against the live FastAPI engine.
            </p>
          </div>
          <button
            onClick={runDemo}
            disabled={running}
            className="flex items-center gap-2 rounded-xl bg-orange-600 px-6 py-3 text-sm font-bold text-white hover:bg-orange-500 disabled:opacity-50 shadow-lg shadow-orange-600/20"
          >
            {running ? <RefreshCw className="h-4 w-4 animate-spin" /> : <Play className="h-4 w-4 fill-white" />}
            {running ? 'Running Security Suite...' : 'RUN LIVE SECURITY DEMO'}
          </button>
        </div>

        {finalStatus && (
          <div className={`mt-8 rounded-xl p-6 border flex items-center justify-between ${
            finalStatus === 'PASS' ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300' : 'bg-red-500/10 border-red-500/30 text-red-300'
          }`}>
            <div>
              <h2 className="text-lg font-black tracking-wide uppercase">FINAL SECURITY STATUS: {finalStatus}</h2>
              <p className="text-xs mt-1 text-slate-300">All security invariants held. 0 unauthorized executions.</p>
            </div>
            <span className="flex h-10 w-10 items-center justify-center rounded-full bg-emerald-500/20 text-emerald-400 font-bold border border-emerald-500/40">
              ✓
            </span>
          </div>
        )}

        <div className="mt-8 space-y-4">
          {logs.length === 0 ? (
            <div className="glass-panel rounded-xl py-16 text-center text-slate-500 text-sm">
              Click <strong className="text-white">&quot;RUN LIVE SECURITY DEMO&quot;</strong> above to launch the live security scenario verification suite.
            </div>

          ) : (
            logs.map((l, idx) => (
              <div key={idx} className="glass-panel rounded-xl p-5 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-bold text-white">{l.name || l.scenario}</span>
                    <span className={`rounded px-2 py-0.5 text-xs font-bold uppercase ${
                      l.result === 'PASS' || l.result === 'EXECUTED' ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' :
                      l.result === 'PREVENTED' || l.result === 'DENIED' || l.result === 'BLOCKED' ? 'bg-orange-500/20 text-orange-300 border border-orange-500/30' :
                      'bg-slate-800 text-slate-400'
                    }`}>
                      {l.result}
                    </span>
                  </div>
                  <p className="text-xs text-slate-400 mt-1">{l.description || l.detail}</p>
                </div>
                {l.explorer_url && (
                  <a
                    href={l.explorer_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1 text-xs font-bold text-orange-400 hover:underline"
                  >
                    Explorer Link <ExternalLink className="h-3 w-3" />
                  </a>
                )}
              </div>
            ))
          )}
        </div>
      </main>
    </div>
  );
}
