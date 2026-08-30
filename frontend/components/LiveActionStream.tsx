'use client';

import React from 'react';
import { CheckCircle, AlertTriangle, XCircle, ExternalLink } from 'lucide-react';

export interface ActionStreamItem {
  action_id: string;
  amount: number;
  currency: string;
  counterparty_id: string;
  destination_account: string;
  decision: 'ALLOW' | 'REVIEW' | 'BLOCK';
  risk_score: number;
  blockchain_tx: string;
  explorer_url?: string;
  policy_violations: string[];
}

interface Props {
  actions: ActionStreamItem[];
  onSelectAction: (actionId: string) => void;
  onOpenReview: (actionId: string) => void;
}

export default function LiveActionStream({ actions, onSelectAction, onOpenReview }: Props) {
  return (
    <div className="glass-panel rounded-xl p-5 flex flex-col h-full">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-base font-bold text-white flex items-center gap-2">
            <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse"></span>
            Live Authorization Control Stream
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">Real-time evaluation stream from Circuit Breaker engine</p>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto space-y-3 pr-1">
        {actions.length === 0 ? (
          <div className="text-center py-12 text-slate-500 text-sm">
            No live authorization stream events recorded yet. Run `python scripts/run_demo.py` or trigger actions via API.
          </div>
        ) : (
          actions.map((item) => {
            const isAllow = item.decision === 'ALLOW';
            const isReview = item.decision === 'REVIEW';
            const isBlock = item.decision === 'BLOCK';
            const hasTx = item.blockchain_tx && item.blockchain_tx !== 'NONE';

            return (
              <div
                key={item.action_id}
                onClick={() => onSelectAction(item.action_id)}
                className={`p-3.5 rounded-lg border transition-all cursor-pointer hover:border-slate-600 ${
                  isAllow
                    ? 'bg-emerald-950/20 border-emerald-500/30 hover:bg-emerald-950/30'
                    : isReview
                    ? 'bg-amber-950/20 border-amber-500/30 hover:bg-amber-950/30'
                    : 'bg-rose-950/20 border-rose-500/30 hover:bg-rose-950/30'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    {isAllow && <CheckCircle className="w-5 h-5 text-emerald-400 shrink-0" />}
                    {isReview && <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0" />}
                    {isBlock && <XCircle className="w-5 h-5 text-rose-400 shrink-0" />}

                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-sm font-bold text-white">
                          ${item.amount.toLocaleString(undefined, { minimumFractionDigits: 2 })} {item.currency}
                        </span>
                        <span className="text-xs text-slate-400">→ {item.counterparty_id}</span>
                      </div>
                      <span className="text-xs font-mono text-slate-500">{item.action_id}</span>
                    </div>
                  </div>

                  <div className="flex items-center gap-3">
                    {isReview && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onOpenReview(item.action_id);
                        }}
                        className="px-2.5 py-1 text-xs font-medium rounded bg-amber-500/20 text-amber-300 border border-amber-500/40 hover:bg-amber-500/30"
                      >
                        Human Intercept
                      </button>
                    )}

                    <span
                      className={`px-2.5 py-1 text-xs font-bold rounded-md font-mono ${
                        isAllow
                          ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40'
                          : isReview
                          ? 'bg-amber-500/20 text-amber-400 border border-amber-500/40'
                          : 'bg-rose-500/20 text-rose-400 border border-rose-500/40'
                      }`}
                    >
                      {item.decision}
                    </span>
                  </div>
                </div>

                <div className="mt-2.5 pt-2 border-t border-slate-800/80 flex items-center justify-between text-xs font-mono">
                  <div className="text-slate-400 flex items-center gap-2">
                    <span>TX:</span>
                    <span className={hasTx ? 'text-emerald-400' : 'text-rose-400 font-bold'}>
                      {hasTx ? item.blockchain_tx.slice(0, 16) + '...' : 'NONE (Execution Blocked)'}
                    </span>
                    {hasTx && item.explorer_url && (
                      <a
                        href={item.explorer_url}
                        target="_blank"
                        rel="noreferrer"
                        onClick={(e) => e.stopPropagation()}
                        className="inline-flex items-center gap-1 text-blue-400 hover:text-blue-300 hover:underline font-sans text-[11px]"
                      >
                        VIEW ON EXPLORER <ExternalLink className="w-3 h-3" />
                      </a>
                    )}
                  </div>
                  <div className="text-slate-400">
                    Risk: <span className={item.risk_score > 0.8 ? 'text-rose-400 font-bold' : 'text-slate-300'}>{item.risk_score.toFixed(2)}</span>
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
