'use client';

import React from 'react';
import { CheckCircle2, AlertTriangle, XCircle, ShieldAlert } from 'lucide-react';

interface MetricsProps {
  allowed: number;
  review: number;
  blocked: number;
  highRisk: number;
}

export default function MetricsBar({ allowed, review, blocked, highRisk }: MetricsProps) {
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div className="glass-panel p-4 rounded-xl border-l-4 border-l-emerald-500">
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">ALLOWED</span>
          <CheckCircle2 className="w-5 h-5 text-emerald-400" />
        </div>
        <div className="mt-2 flex items-baseline">
          <span className="text-3xl font-extrabold text-white">{allowed}</span>
          <span className="ml-2 text-xs text-emerald-400 font-medium">Executed Safely</span>
        </div>
      </div>

      <div className="glass-panel p-4 rounded-xl border-l-4 border-l-amber-500">
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">REVIEW</span>
          <AlertTriangle className="w-5 h-5 text-amber-400" />
        </div>
        <div className="mt-2 flex items-baseline">
          <span className="text-3xl font-extrabold text-white">{review}</span>
          <span className="ml-2 text-xs text-amber-400 font-medium">Human Intercept</span>
        </div>
      </div>

      <div className="glass-panel p-4 rounded-xl border-l-4 border-l-rose-500">
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">BLOCKED</span>
          <XCircle className="w-5 h-5 text-rose-400" />
        </div>
        <div className="mt-2 flex items-baseline">
          <span className="text-3xl font-extrabold text-white">{blocked}</span>
          <span className="ml-2 text-xs text-rose-400 font-medium">Policy Enforced</span>
        </div>
      </div>

      <div className="glass-panel p-4 rounded-xl border-l-4 border-l-purple-500">
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">HIGH RISK</span>
          <ShieldAlert className="w-5 h-5 text-purple-400" />
        </div>
        <div className="mt-2 flex items-baseline">
          <span className="text-3xl font-extrabold text-white">{highRisk}</span>
          <span className="ml-2 text-xs text-purple-400 font-medium">FraudGraph Signal</span>
        </div>
      </div>
    </div>
  );
}
