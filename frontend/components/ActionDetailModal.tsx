'use client';

import React from 'react';
import { X, ShieldCheck, ShieldAlert, Cpu } from 'lucide-react';

interface Props {
  actionId: string;
  data: any;
  onClose: () => void;
}

export default function ActionDetailModal({ actionId, data, onClose }: Props) {
  if (!data) return null;

  const action = data.action || {};
  const decision = data.decision || {};
  const token = data.token;
  const isBlock = decision.decision === 'BLOCK';
  const isAllow = decision.decision === 'ALLOW';

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4">
      <div className="glass-panel w-full max-w-2xl rounded-2xl p-6 border border-slate-700 shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
        <div className="flex items-center justify-between pb-4 border-b border-slate-800">
          <div>
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              Action Inspector: {actionId}
            </h3>
            <p className="text-xs text-slate-400">Complete end-to-end evaluation & execution trace</p>
          </div>
          <button onClick={onClose} className="p-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto space-y-4 py-4 font-mono text-xs">
          {data.error && (
            <div className="rounded-lg border border-rose-500/40 bg-rose-950/40 p-3 text-rose-300">{data.error}</div>
          )}

          <div className="grid grid-cols-2 gap-3">
            <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
              <span className="text-slate-500 block">Proposed Amount:</span>
              <span className="text-white font-bold text-base">
                ${action.amount ? action.amount.toLocaleString() : '0'} {action.currency}
              </span>
            </div>

            <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
              <span className="text-slate-500 block">Decision Result:</span>
              <span className={`font-bold text-base ${isAllow ? 'text-emerald-400' : isBlock ? 'text-rose-400' : 'text-amber-400'}`}>
                {decision.decision}
              </span>
            </div>
          </div>

          <div className="bg-slate-950 p-3.5 rounded-lg border border-slate-800 space-y-2">
            <div className="flex justify-between"><span className="text-slate-500">Agent ID:</span><span className="text-slate-200">{action.agent_id}</span></div>
            <div className="flex justify-between"><span className="text-slate-500">Invoice ID:</span><span className="text-slate-200">{action.invoice_id || 'N/A'}</span></div>
            <div className="flex justify-between"><span className="text-slate-500">Counterparty:</span><span className="text-slate-200">{action.counterparty_id}</span></div>
            <div className="flex justify-between"><span className="text-slate-500">Destination Account:</span><span className="text-slate-200">{action.destination_account}</span></div>
          </div>

          <div>
            <span className="text-slate-400 font-bold block mb-1.5">Policy Evaluation & Violations:</span>
            {decision.violations && decision.violations.length > 0 ? (
              <div className="space-y-1.5">
                {decision.violations.map((v: any, idx: number) => (
                  <div key={idx} className="p-2.5 rounded bg-rose-950/40 border border-rose-500/40 text-rose-300">
                    <span className="font-bold">[{v.policy_id}]</span> {v.message}
                  </div>
                ))}
              </div>
            ) : (
              <div className="p-2.5 rounded bg-emerald-950/40 border border-emerald-500/40 text-emerald-300">
                ✓ All business policies passed without violation.
              </div>
            )}
          </div>

          <div className="bg-slate-950 p-3.5 rounded-lg border border-slate-800 space-y-2">
            <div className="text-slate-400 font-bold">Security decision</div>
            <div className="flex justify-between"><span className="text-slate-500">Policy:</span><span>{decision.decision || '—'}</span></div>
            <div className="flex justify-between"><span className="text-slate-500">Risk:</span><span>{Number(decision.risk_score || 0).toFixed(2)}</span></div>
            <div className="flex justify-between"><span className="text-slate-500">Human approval:</span><span>{data.human_approval ? (data.human_approval.approved ? 'GRANTED' : 'REJECTED') : (decision.requires_human_approval ? 'REQUIRED' : 'N/A')}</span></div>
            <div className="flex justify-between"><span className="text-slate-500">Authorization:</span><span>{token ? 'TOKEN ISSUED' : 'NONE'}</span></div>
            <div className="flex justify-between"><span className="text-slate-500">Execution:</span><span>{data.transaction?.blockchain_tx_hash || 'NONE'}</span></div>
            <div className="flex justify-between"><span className="text-slate-500">Token lifecycle:</span><span>{data.token_lifecycle || '—'}</span></div>
          </div>

          <div className="bg-slate-950 p-3.5 rounded-lg border border-slate-800">
            <span className="text-slate-400 font-bold block mb-1">Cryptographic Authorization Token:</span>
            {token ? (
              <div className="text-[11px] text-emerald-400 break-all space-y-1">
                <div>Token ID: {token.token_id}</div>
                <div>Action Hash: {token.action_hash}</div>
                <div>Issued: {token.issued_at}</div>
              </div>
            ) : (
              <div className="text-rose-400 font-bold">NONE (Action was BLOCKED or not authorized)</div>
            )}
          </div>
        </div>

        <div className="pt-3 border-t border-slate-800 flex justify-end">
          <button onClick={onClose} className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold rounded-lg">
            Close Inspector
          </button>
        </div>
      </div>
    </div>
  );
}
