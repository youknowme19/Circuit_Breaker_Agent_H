'use client';

import React, { useCallback, useEffect, useState } from 'react';
import Link from 'next/link';
import SiteNav from '@/components/SiteNav';
import ExecutionModeBadge from '@/components/ExecutionModeBadge';
import MetricsBar from '@/components/MetricsBar';
import LiveActionStream, { ActionStreamItem } from '@/components/LiveActionStream';
import FraudGraphView from '@/components/FraudGraphView';
import AuditChainView from '@/components/AuditChainView';
import HumanApprovalModal from '@/components/HumanApprovalModal';
import ActionDetailModal from '@/components/ActionDetailModal';
import { api, ApiError } from '@/lib/api';

type LoadState = 'idle' | 'loading' | 'ok' | 'error';

export default function ConsolePage() {
  const [metrics, setMetrics] = useState({ allowed: 0, review: 0, blocked: 0, highRisk: 0 });
  const [actions, setActions] = useState<ActionStreamItem[]>([]);
  const [auditEvents, setAuditEvents] = useState<any[]>([]);
  const [timeline, setTimeline] = useState<any[]>([]);
  const [graph, setGraph] = useState<{ nodes: any[]; edges: any[] }>({ nodes: [], edges: [] });
  const [mode, setMode] = useState<'MOCK' | 'SEPOLIA'>('MOCK');
  const [backendError, setBackendError] = useState<string | null>(null);
  const [selectedActionId, setSelectedActionId] = useState<string | null>(null);
  const [selectedActionData, setSelectedActionData] = useState<any | null>(null);
  const [reviewTarget, setReviewTarget] = useState<ActionStreamItem | null>(null);
  const [demoState, setDemoState] = useState<LoadState>('idle');
  const [demoResult, setDemoResult] = useState<any>(null);
  const [demoError, setDemoError] = useState<string | null>(null);
  const [approvalBusy, setApprovalBusy] = useState(false);

  const refresh = useCallback(async () => {
    try {
      const [m, cfg, listed, audit, tl, g] = await Promise.all([
        api<any>('/api/metrics'),
        api<any>('/api/config'),
        api<any[]>('/api/actions/feed'),
        api<any[]>('/api/audit'),
        api<any[]>('/api/timeline'),
        api<any>('/api/graph'),
      ]);
      setMetrics({ allowed: m.allowed, review: m.review, blocked: m.blocked, highRisk: m.high_risk });
      setMode(cfg.enable_testnet_execution ? 'SEPOLIA' : 'MOCK');
      setActions(
        (listed || []).map((row: any) => ({
          action_id: row.action?.action_id,
          amount: row.action?.amount,
          currency: row.action?.currency || 'USD',
          counterparty_id: row.action?.counterparty_id,
          destination_account: row.action?.destination_account,
          decision: row.decision?.decision,
          risk_score: row.decision?.risk_score || 0,
          blockchain_tx: row.transaction?.blockchain_tx_hash || 'NONE',
          explorer_url: row.transaction?.explorer_url,
          policy_violations: (row.decision?.violations || []).map((v: any) => `${v.policy_id}: ${v.message}`),
          invoice_id: row.action?.invoice_id,
        }))
      );
      setAuditEvents(audit || []);
      setTimeline(tl || []);
      setGraph(g || { nodes: [], edges: [] });
      setBackendError(null);
    } catch (e) {
      setBackendError(e instanceof ApiError ? e.message : 'Backend unreachable');
    }
  }, []);

  useEffect(() => {
    refresh();
    const id = setInterval(refresh, 4000);
    return () => clearInterval(id);
  }, [refresh]);

  const handleSelectAction = async (actionId: string) => {
    setSelectedActionId(actionId);
    try {
      const data = await api<any>(`/api/actions/${actionId}`);
      setSelectedActionData(data);
    } catch (e) {
      setSelectedActionData({ error: e instanceof ApiError ? e.message : 'Failed to load action' });
    }
  };

  const handleApprove = async (actionId: string) => {
    setApprovalBusy(true);
    try {
      const data = await api<any>(`/api/actions/${actionId}/approve`, {
        method: 'POST',
        body: JSON.stringify({ approver: 'security-chief' }),
      });
      await api(`/api/actions/${actionId}/execute`, {
        method: 'POST',
        body: JSON.stringify({ token_id: data.token_id }),
      });
      setReviewTarget(null);
      await refresh();
    } catch (e) {
      alert(e instanceof ApiError ? e.message : 'Approval failed');
    } finally {
      setApprovalBusy(false);
    }
  };

  const handleReject = async (actionId: string) => {
    setApprovalBusy(true);
    try {
      await api(`/api/actions/${actionId}/reject`, {
        method: 'POST',
        body: JSON.stringify({ approver: 'security-chief' }),
      });
      setReviewTarget(null);
      await refresh();
    } catch (e) {
      alert(e instanceof ApiError ? e.message : 'Reject failed');
    } finally {
      setApprovalBusy(false);
    }
  };

  const runDemo = async () => {
    setDemoState('loading');
    setDemoError(null);
    try {
      const res = await api<any>('/api/demo/run', { method: 'POST', body: JSON.stringify({ reset: true }) });
      setDemoResult(res);
      setDemoState('ok');
      await refresh();
    } catch (e) {
      setDemoState('error');
      setDemoError(e instanceof ApiError ? e.message : 'Demo failed');
    }
  };

  return (
    <div className="cb-grid min-h-screen">
      <SiteNav compact />
      <main className="mx-auto flex max-w-[1600px] flex-col gap-6 p-4 md:p-6">
        {backendError && (
          <div role="alert" className="rounded-lg border border-rose-500/40 bg-rose-950/50 px-4 py-3 text-sm text-rose-200">
            {backendError}
          </div>
        )}

        <div className="flex flex-col justify-between gap-4 md:flex-row md:items-center">
          <div>
            <p className="font-mono text-[10px] uppercase tracking-[0.2em] text-orange-400">System status: PROTECTED</p>
            <h1 className="text-2xl font-black text-white">Security Console</h1>
          </div>
          <div className="flex flex-wrap items-center gap-3">
            <ExecutionModeBadge isTestnet={mode === 'SEPOLIA'} />
            <button
              id="demo"
              type="button"
              onClick={runDemo}
              disabled={demoState === 'loading'}
              className="focus-ring rounded-lg bg-orange-600 px-4 py-2 text-xs font-bold text-white hover:bg-orange-500 disabled:opacity-50"
            >
              {demoState === 'loading' ? 'Running demo…' : 'Run Security Demo'}
            </button>
            <Link href="/attacks" className="focus-ring rounded-lg border border-white/15 px-4 py-2 text-xs font-bold text-slate-200">
              Attack Lab
            </Link>
          </div>
        </div>

        {demoError && (
          <div role="alert" className="rounded-lg border border-rose-500/40 bg-rose-950/40 p-3 text-sm text-rose-200">
            {demoError}
          </div>
        )}
        {demoState === 'ok' && demoResult && (
          <div className={`rounded-lg border p-3 font-mono text-xs ${demoResult.passed ? 'border-emerald-500/40 text-emerald-300' : 'border-rose-500/40 text-rose-300'}`}>
            DEMO {demoResult.passed ? 'PASS' : 'FAIL'} — {demoResult.scenes?.length || 0} scenes from live engine
          </div>
        )}

        <MetricsBar allowed={metrics.allowed} review={metrics.review} blocked={metrics.blocked} highRisk={metrics.highRisk} />

        <div className="grid grid-cols-1 gap-6 lg:grid-cols-12">
          <div className="h-[640px] lg:col-span-7">
            <LiveActionStream
              actions={actions}
              onSelectAction={handleSelectAction}
              onOpenReview={(id) => setReviewTarget(actions.find((a) => a.action_id === id) || null)}
            />
          </div>
          <div className="flex min-h-[640px] flex-col gap-6 lg:col-span-5">
            <div className="h-[300px]">
              <FraudGraphView graphData={graph} />
            </div>
            <div className="min-h-[300px] flex-1">
              <AuditChainView
                events={auditEvents}
                onVerify={async () => api('/api/audit/verify', { method: 'POST' })}
                onTamperSimulate={async (eventId) => {
                  await api('/api/audit/tamper-simulate', {
                    method: 'POST',
                    body: JSON.stringify({ event_id: eventId, new_decision: 'TAMPERED_ALLOW' }),
                  });
                  refresh();
                }}
              />
            </div>
          </div>
        </div>

        <section className="glass-panel rounded-xl p-5">
          <h2 className="text-sm font-bold text-white">Security timeline</h2>
          <ol className="mt-3 max-h-56 space-y-2 overflow-y-auto font-mono text-xs">
            {timeline.length === 0 && <li className="text-slate-500">No events yet. Run the demo or Attack Lab.</li>}
            {[...timeline].reverse().slice(0, 40).map((ev, i) => (
              <li key={`${ev.timestamp}-${i}`} className="flex gap-3 border-l-2 border-orange-500/30 pl-3">
                <span className="text-slate-500">{String(ev.timestamp).slice(11, 19)}</span>
                <span className="text-orange-300">{ev.event_type}</span>
                <span className="text-slate-300">{ev.message}</span>
              </li>
            ))}
          </ol>
        </section>
      </main>

      {selectedActionId && selectedActionData && (
        <ActionDetailModal
          actionId={selectedActionId}
          data={selectedActionData}
          onClose={() => {
            setSelectedActionId(null);
            setSelectedActionData(null);
          }}
        />
      )}

      {reviewTarget && (
        <HumanApprovalModal
          actionId={reviewTarget.action_id}
          amount={reviewTarget.amount}
          currency={reviewTarget.currency}
          counterpartyId={reviewTarget.counterparty_id}
          destinationAccount={reviewTarget.destination_account}
          riskScore={reviewTarget.risk_score}
          violations={reviewTarget.policy_violations.map((v) => ({ policy_id: v.split(':')[0], message: v }))}
          busy={approvalBusy}
          onApprove={handleApprove}
          onReject={handleReject}
          onClose={() => setReviewTarget(null)}
        />
      )}
    </div>
  );
}
