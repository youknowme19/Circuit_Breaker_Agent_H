'use client';

import React from 'react';
import { AlertTriangle, CheckCircle, XCircle } from 'lucide-react';

interface Props {
  actionId: string;
  amount: number;
  currency: string;
  counterpartyId: string;
  destinationAccount: string;
  riskScore: number;
  violations: any[];
  busy?: boolean;
  onApprove: (actionId: string) => Promise<void>;
  onReject: (actionId: string) => Promise<void>;
  onClose: () => void;
}

export default function HumanApprovalModal({
  actionId,
  amount,
  currency,
  counterpartyId,
  destinationAccount,
  riskScore,
  violations,
  busy = false,
  onApprove,
  onReject,
  onClose
}: Props) {
  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4">
      <div className="glass-panel w-full max-w-lg rounded-2xl p-6 border border-amber-500/40 shadow-2xl">
        <div className="flex items-center gap-3 text-amber-400 mb-4">
          <AlertTriangle className="w-7 h-7 shrink-0 animate-bounce" />
          <div>
            <h3 className="text-lg font-bold text-white">HUMAN APPROVAL INTERCEPT REQUIRED</h3>
            <p className="text-xs text-amber-300">Action flagged for human authorization by Circuit Breaker</p>
          </div>
        </div>

        <div className="bg-slate-950/80 rounded-xl p-4 border border-slate-800 space-y-3 font-mono text-xs">
          <div className="flex justify-between border-b border-slate-800 pb-2">
            <span className="text-slate-400">Action ID:</span>
            <span className="text-white font-bold">{actionId}</span>
          </div>

          <div className="flex justify-between border-b border-slate-800 pb-2">
            <span className="text-slate-400">Proposed Amount:</span>
            <span className="text-emerald-400 font-bold text-sm">
              ${amount.toLocaleString(undefined, { minimumFractionDigits: 2 })} {currency}
            </span>
          </div>

          <div className="flex justify-between border-b border-slate-800 pb-2">
            <span className="text-slate-400">Destination Vendor:</span>
            <span className="text-white">{counterpartyId} ({destinationAccount})</span>
          </div>

          <div className="flex justify-between border-b border-slate-800 pb-2">
            <span className="text-slate-400">FraudGraph Risk Score:</span>
            <span className={riskScore > 0.8 ? 'text-rose-400 font-bold' : 'text-amber-400'}>{riskScore.toFixed(2)}</span>
          </div>

          <div>
            <span className="text-slate-400 block mb-1">Policy Review Triggers:</span>
            <div className="space-y-1">
              {violations.length === 0 ? (
                <div className="text-amber-300">• NEW_COUNTERPARTY_REVIEW: High-value transfer to unverified vendor</div>
              ) : (
                violations.map((v, idx) => (
                  <div key={idx} className="text-amber-300">• [{v.policy_id}] {v.message}</div>
                ))
              )}
            </div>
          </div>
        </div>

        <div className="mt-6 flex items-center justify-end gap-3">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold"
          >
            Cancel
          </button>
          <button
            onClick={() => onReject(actionId)}
            disabled={busy}
            className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-rose-600 hover:bg-rose-500 text-white text-xs font-semibold disabled:opacity-50"
          >
            <XCircle className="w-4 h-4" />
            REJECT
          </button>
          <button
            onClick={() => onApprove(actionId)}
            disabled={busy}
            className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold disabled:opacity-50"
          >
            <CheckCircle className="w-4 h-4" />
            {busy ? 'WORKING…' : 'APPROVE'}
          </button>
        </div>
      </div>
    </div>
  );
}
