'use client';

import React, { useState } from 'react';
import { ShieldCheck, ShieldAlert, Link as LinkIcon, RefreshCw } from 'lucide-react';

interface AuditEventItem {
  event_id: string;
  timestamp: string;
  action_id: string;
  decision: string;
  risk_score: number;
  previous_hash: string;
  event_hash: string;
}

interface Props {
  events: AuditEventItem[];
  onVerify: () => Promise<{ valid: boolean; broken_at?: string; events_checked?: number; reason?: string }>;
  onTamperSimulate: (eventId: string) => Promise<void>;
}

export default function AuditChainView({ events, onVerify, onTamperSimulate }: Props) {
  const [verificationResult, setVerificationResult] = useState<{ valid: boolean; broken_at?: string; events_checked?: number; reason?: string } | null>(null);
  const [isVerifying, setIsVerifying] = useState(false);

  const handleVerify = async () => {
    setIsVerifying(true);
    const res = await onVerify();
    setVerificationResult(res);
    setIsVerifying(false);
  };

  return (
    <div className="glass-panel rounded-xl p-5 flex flex-col h-full">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-base font-bold text-white flex items-center gap-2">
            <LinkIcon className="w-5 h-5 text-blue-400" />
            Tamper-Evident SHA-256 Audit Chain
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">Cryptographic hash-chained audit evidence log</p>
        </div>

        <button
          onClick={handleVerify}
          disabled={isVerifying}
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold transition-all"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isVerifying ? 'animate-spin' : ''}`} />
          Verify Chain
        </button>
      </div>

      {verificationResult && (
        <div
          className={`mb-4 p-3 rounded-lg border flex items-center justify-between text-xs font-mono ${
            verificationResult.valid
              ? 'bg-emerald-950/40 border-emerald-500/50 text-emerald-300'
              : 'bg-rose-950/40 border-rose-500/50 text-rose-300'
          }`}
        >
          <div className="flex items-center gap-2">
            {verificationResult.valid ? (
              <ShieldCheck className="w-4 h-4 text-emerald-400 shrink-0" />
            ) : (
              <ShieldAlert className="w-4 h-4 text-rose-400 shrink-0" />
            )}
            <span>
              {verificationResult.valid
                ? `AUDIT CHAIN VALID (${verificationResult.events_checked} events)`
                : `AUDIT CHAIN COMPROMISED (${verificationResult.broken_at}: ${verificationResult.reason})`}
            </span>
          </div>
        </div>
      )}

      <div className="flex-1 overflow-y-auto space-y-2 pr-1 font-mono text-xs">
        {events.length === 0 ? (
          <div className="text-center py-8 text-slate-500">No audit events generated yet.</div>
        ) : (
          events.map((evt, idx) => (
            <div key={evt.event_id} className="p-2.5 rounded bg-slate-900/80 border border-slate-800">
              <div className="flex items-center justify-between text-slate-300">
                <span className="font-bold text-blue-400">{evt.event_id}</span>
                <span
                  className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                    evt.decision === 'ALLOW' || evt.decision === 'EXECUTED'
                      ? 'bg-emerald-900/60 text-emerald-300'
                      : evt.decision === 'REVIEW'
                      ? 'bg-amber-900/60 text-amber-300'
                      : 'bg-rose-900/60 text-rose-300'
                  }`}
                >
                  {evt.decision}
                </span>
              </div>
              <div className="mt-1 text-[11px] text-slate-500">
                Action: {evt.action_id} | Risk: {evt.risk_score.toFixed(2)}
              </div>
              <div className="mt-1 text-[10px] text-slate-500 truncate">
                Hash: <span className="text-slate-400">{evt.event_hash.slice(0, 24)}...</span>
              </div>
              {idx === 1 && (
                <button
                  onClick={() => onTamperSimulate(evt.event_id)}
                  className="mt-2 text-[10px] text-rose-400 hover:underline"
                >
                  [Simulate Tampering on {evt.event_id}]
                </button>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
