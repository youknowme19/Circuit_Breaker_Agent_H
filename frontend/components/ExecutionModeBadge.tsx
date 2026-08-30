'use client';

import React from 'react';
import { ShieldCheck, Cpu } from 'lucide-react';

interface Props {
  isTestnet: boolean;
}

export default function ExecutionModeBadge({ isTestnet }: Props) {
  return (
    <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-900/90 border border-slate-800 text-xs font-mono">
      {isTestnet ? (
        <>
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
          </span>
          <Cpu className="w-3.5 h-3.5 text-emerald-400" />
          <span className="text-emerald-400 font-semibold">EXECUTION: SEPOLIA TESTNET</span>
        </>
      ) : (
        <>
          <span className="relative flex h-2 w-2">
            <span className="relative inline-flex rounded-full h-2 w-2 bg-blue-500"></span>
          </span>
          <ShieldCheck className="w-3.5 h-3.5 text-blue-400" />
          <span className="text-blue-400 font-semibold">EXECUTION: MOCK (DEMO-SAFE MODE)</span>
        </>
      )}
    </div>
  );
}
