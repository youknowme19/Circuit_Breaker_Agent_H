'use client';

import SiteNav from '@/components/SiteNav';
import { Terminal, Shield, CheckCircle, Lock, AlertTriangle, Cpu, ShieldAlert, ArrowRight } from 'lucide-react';

const all19Tools = [
  // Read Only
  { name: 'get_wallet_address', category: 'READ ONLY', auth: 'NO', movesFunds: 'NO', desc: 'Queries public sender wallet address. Private keys are NEVER returned.' },
  { name: 'get_wallet_balance', category: 'READ ONLY', auth: 'NO', movesFunds: 'NO', desc: 'Queries native testnet MON balance via RPC provider.' },
  { name: 'get_supported_networks', category: 'READ ONLY', auth: 'NO', movesFunds: 'NO', desc: 'Lists supported financial networks (Monad Testnet, Sepolia).' },
  { name: 'get_transaction_status', category: 'READ ONLY', auth: 'NO', movesFunds: 'NO', desc: 'Queries transaction ledger status & blockchain explorer links.' },
  { name: 'verify_audit_chain', category: 'READ ONLY', auth: 'NO', movesFunds: 'NO', desc: 'Validates SHA-256 tamper-evident cryptographic audit log.' },
  { name: 'get_action_details', category: 'READ ONLY', auth: 'NO', movesFunds: 'NO', desc: 'Retrieves action status and policy decision parameters.' },
  { name: 'get_policy_rules', category: 'READ ONLY', auth: 'NO', movesFunds: 'NO', desc: 'Inspects active velocity limits, daily caps, and risk thresholds.' },
  { name: 'get_counterparty_risk', category: 'READ ONLY', auth: 'NO', movesFunds: 'NO', desc: 'Queries FraudGraph signals for counterparty trust scores.' },
  { name: 'get_pending_approvals', category: 'READ ONLY', auth: 'NO', movesFunds: 'NO', desc: 'Lists actions queued for operator human approval (REVIEW).' },
  { name: 'get_system_health', category: 'READ ONLY', auth: 'NO', movesFunds: 'NO', desc: 'Monitors Circuit Breaker policy engine & RPC connectivity.' },
  { name: 'get_fraud_graph_edges', category: 'READ ONLY', auth: 'NO', movesFunds: 'NO', desc: 'Inspects transaction layering and risk graph relationships.' },

  // Preparation
  { name: 'estimate_transfer', category: 'PREPARATION', auth: 'NO', movesFunds: 'NO', desc: 'Calculates gas fee limit, priority fee, and total cost estimate.' },
  { name: 'prepare_transfer', category: 'PREPARATION', auth: 'NO', movesFunds: 'NO', desc: 'Constructs structured action payload ready for policy evaluation.' },
  { name: 'request_transfer', category: 'PREPARATION', auth: 'NO', movesFunds: 'NO', desc: 'Submits payment action to Circuit Breaker Policy Engine.' },
  { name: 'propose_payment', category: 'PREPARATION', auth: 'NO', movesFunds: 'NO', desc: 'Evaluates policy rules, velocity limits, and prompt injection.' },
  { name: 'simulate_transfer', category: 'PREPARATION', auth: 'NO', movesFunds: 'NO', desc: 'Runs zero-cost sandbox simulation of transaction execution.' },
  { name: 'approve_action_human', category: 'PREPARATION', auth: 'NO', movesFunds: 'NO', desc: 'Operator action approving a queued REVIEW decision.' },

  // Execution (Gated Boundary)
  { name: 'execute_payment', category: 'EXECUTION', auth: 'MANDATORY HMAC TOKEN', movesFunds: 'YES (GATED)', desc: 'Executes transaction via Execution Gate. Strictly requires HMAC token & atomic lock.' }
];

export default function ToolsBoundaryPage() {
  const readOnlyCount = all19Tools.filter(t => t.category === 'READ ONLY').length;
  const prepCount = all19Tools.filter(t => t.category === 'PREPARATION').length;
  const execCount = all19Tools.filter(t => t.category === 'EXECUTION').length;

  return (
    <div className="min-h-screen bg-[#07080c] text-slate-100 antialiased">
      <SiteNav />
      <main className="mx-auto max-w-7xl px-4 py-8 space-y-8">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between pb-6 border-b border-white/10 gap-4">
          <div>
            <div className="flex items-center gap-2 text-xs font-mono text-orange-400 uppercase tracking-widest font-semibold">
              <Terminal className="h-4 w-4" /> FastMCP Tool Boundary Inspector
            </div>
            <h1 className="text-3xl font-black text-white mt-1">19 FastMCP Financial Tools Surface</h1>
            <p className="text-sm text-slate-400 mt-1">
              TrueForge discovers 19 MCP tools, but only <code className="text-orange-300 font-mono">1 tool</code> can execute money movement.
            </p>
          </div>
          <div className="flex items-center gap-3">
            <span className="flex items-center gap-2 rounded-full border border-orange-500/40 bg-orange-500/10 px-3 py-1 text-xs font-mono font-bold text-orange-300">
              19 Tools Registered
            </span>
          </div>
        </div>

        {/* Security Boundary Banner */}
        <div className="glass-panel rounded-xl p-6 border-l-4 border-l-orange-500 bg-orange-950/10">
          <div className="grid gap-6 md:grid-cols-3">
            <div className="bg-black/50 p-4 rounded-lg border border-white/10">
              <span className="text-xs font-mono uppercase text-slate-400 font-bold block">1. Read Only Tools</span>
              <span className="text-2xl font-black text-white mt-1 block">{readOnlyCount} Tools</span>
              <span className="text-[11px] text-slate-400 mt-1 block">Balances, networks, risk scores, audit verification.</span>
            </div>
            <div className="bg-black/50 p-4 rounded-lg border border-white/10">
              <span className="text-xs font-mono uppercase text-slate-400 font-bold block">2. Preparation Tools</span>
              <span className="text-2xl font-black text-white mt-1 block">{prepCount} Tools</span>
              <span className="text-[11px] text-slate-400 mt-1 block">Gas estimation, payload construction, policy submission.</span>
            </div>
            <div className="bg-emerald-950/40 p-4 rounded-lg border border-emerald-500/40">
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono uppercase text-emerald-400 font-bold">3. Financial Execution Tool</span>
                <Lock className="h-4 w-4 text-emerald-400" />
              </div>
              <span className="text-2xl font-black text-emerald-300 mt-1 block">1 Gated Tool</span>
              <span className="text-[11px] text-emerald-200 mt-1 block">
                <code className="font-mono bg-emerald-900/60 px-1 rounded">execute_payment</code> strictly requires HMAC authorization.
              </span>
            </div>
          </div>
        </div>

        {/* Table of Tools */}
        <div className="glass-panel rounded-xl p-6">
          <h2 className="text-base font-bold text-white mb-4 flex items-center gap-2">
            <Shield className="h-4 w-4 text-orange-400" /> Complete 19 Tool Capabilities & Security Boundary
          </h2>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300 font-mono">
              <thead className="bg-white/5 uppercase text-slate-400 border-b border-white/10">
                <tr>
                  <th className="px-4 py-3">Tool Name</th>
                  <th className="px-4 py-3">Category</th>
                  <th className="px-4 py-3">Authorization Requirement</th>
                  <th className="px-4 py-3">Can Execute Funds</th>
                  <th className="px-4 py-3">Description</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/10 bg-black/30">
                {all19Tools.map((t) => (
                  <tr key={t.name} className={t.category === 'EXECUTION' ? 'bg-emerald-950/20 border-l-2 border-l-emerald-400' : 'hover:bg-white/5'}>
                    <td className="px-4 py-3 font-bold text-orange-300">{t.name}()</td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        t.category === 'EXECUTION' ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40' :
                        t.category === 'PREPARATION' ? 'bg-blue-500/20 text-blue-300 border border-blue-500/40' :
                        'bg-white/10 text-slate-300'
                      }`}>
                        {t.category}
                      </span>
                    </td>
                    <td className="px-4 py-3 font-bold">
                      {t.auth.includes('HMAC') ? (
                        <span className="text-emerald-400 flex items-center gap-1"><Lock className="h-3.5 w-3.5" /> HMAC TOKEN MANDATORY</span>
                      ) : (
                        <span className="text-slate-500">Unrestricted Read / Prepare</span>
                      )}
                    </td>
                    <td className="px-4 py-3 font-bold">
                      {t.movesFunds.includes('YES') ? (
                        <span className="text-emerald-400 bg-emerald-500/20 px-2 py-0.5 rounded border border-emerald-500/40">
                          YES (GATED GATE)
                        </span>
                      ) : (
                        <span className="text-slate-500">NO</span>
                      )}
                    </td>
                    <td className="px-4 py-3 text-slate-400 font-sans">{t.desc}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </main>
    </div>
  );
}
