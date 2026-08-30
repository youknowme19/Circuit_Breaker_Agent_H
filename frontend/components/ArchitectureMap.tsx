'use client';

import { useState } from 'react';

const NODES = [
  { id: 'agent', title: 'Untrusted Agent', body: 'LLM output, invoices, and prompts are never trusted as authorization.' },
  { id: 'tf', title: 'TrueForge', body: 'Harness loop, MCP binding, sandbox, session. Orchestration — not a bank.' },
  { id: 'mcp', title: 'MCP Financial Tools', body: 'Capability interface. execute_payment still needs a Circuit Breaker token.' },
  { id: 'norm', title: 'Action Normalizer', body: 'Independent structured action. Canonical JSON. SHA-256 hash.' },
  { id: 'policy', title: 'Policy Engine', body: 'Deterministic Python rules. The model is never asked if money may move.' },
  { id: 'vel', title: 'Velocity Tracker', body: '24h cumulative spend including in-flight reservations.' },
  { id: 'dup', title: 'Duplicate Detector', body: 'Same invoice or vendor+amount inside the window is blocked.' },
  { id: 'fg', title: 'FraudGraph', body: 'Account relationship and layering signals. Advisory into REVIEW/BLOCK.' },
  { id: 'tok', title: 'Authorization Token', body: 'HMAC-SHA256 token bound to action id + canonical hash + expiry.' },
  { id: 'hum', title: 'Human Approval', body: 'REVIEW cannot execute until an operator approves. Agent cannot override.' },
  { id: 'gate', title: 'Execution Gate', body: 'Fail closed. One reservation. One execution. Replay dies here.' },
  { id: 'adp', title: 'Payment Adapter', body: 'Mock (mock-tx-*, no explorer) or opt-in Sepolia after real broadcast.' },
  { id: 'aud', title: 'Audit Chain', body: 'SHA-256 hash chain. Tamper-evident, not consensus.' },
];

export default function ArchitectureMap() {
  const [active, setActive] = useState(NODES[2].id);
  const current = NODES.find((n) => n.id === active) || NODES[0];
  return (
    <div className="grid gap-4 lg:grid-cols-3">
      <div className="lg:col-span-2 grid grid-cols-2 sm:grid-cols-3 gap-2">
        {NODES.map((n) => (
          <button
            key={n.id}
            type="button"
            onClick={() => setActive(n.id)}
            className={`focus-ring rounded-lg border px-3 py-3 text-left text-xs font-semibold transition ${
              active === n.id
                ? 'border-orange-500 bg-orange-500/15 text-white'
                : 'border-white/10 bg-white/[0.03] text-slate-300 hover:border-orange-500/40'
            }`}
            aria-pressed={active === n.id}
          >
            {n.title}
          </button>
        ))}
      </div>
      <aside className="glass-panel rounded-xl p-4" aria-live="polite">
        <h3 className="text-sm font-bold text-orange-200">{current.title}</h3>
        <p className="mt-2 text-sm leading-relaxed text-slate-300">{current.body}</p>
      </aside>
    </div>
  );
}
