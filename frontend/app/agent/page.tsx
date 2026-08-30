'use client';

import { useState } from 'react';
import SiteNav from '@/components/SiteNav';
import { Bot, User, Shield, CheckCircle, AlertOctagon, Terminal, ExternalLink, ArrowRight, Lock, Key, Server, Cpu } from 'lucide-react';

export default function AgentPage() {
  const [inputPrompt, setInputPrompt] = useState('Send 1 MON to 0xa7c965820d4933dBe9F71fE665A4D0adAE98aD06');
  const [pipelineState, setPipelineState] = useState<'IDLE' | 'RUNNING' | 'COMPLETE'>('COMPLETE');

  const [messages] = useState<any[]>([
    { sender: 'user', text: 'Send 0.01 MON to 0xa7c965820d4933dBe9F71fE665A4D0adAE98aD06' },
    { sender: 'agent', text: "I will query wallet capabilities over FastMCP and submit your transfer request to Circuit Breaker for deterministic policy evaluation." },
    {
      sender: 'tool',
      tool: 'get_wallet_address',
      result: { configured_address: '0xa7c965820d4933dBe9F71fE665A4D0adAE98aD06', network: 'Monad Testnet', asset: 'MON', private_key_exposed: false }
    },
    {
      sender: 'tool',
      tool: 'get_wallet_balance',
      result: { address: '0xa7c965820d4933dBe9F71fE665A4D0adAE98aD06', balance: 10.915018, asset: 'MON', network: 'Monad Testnet' }
    },
    {
      sender: 'tool',
      tool: 'estimate_transfer',
      result: { destination_account: '0x57d1Cf3D387de087Eda90a1cC81eAc608F7a8f55', amount: 0.01, asset: 'MON', estimated_fee: 0.0000315, total_cost: 0.0100315 }
    },
    {
      sender: 'circuit_breaker',
      title: 'Circuit Breaker Security Decision',
      decision: 'ALLOW',
      risk_score: 0.10,
      token: 'TOKEN-LIVE-4ef4ef',
      detail: 'Policy Checked: Max Transfer PASS | Velocity Limit PASS | Duplicate Detection PASS | Prompt Injection NONE'
    },
    {
      sender: 'tool',
      tool: 'execute_payment',
      result: {
        success: true,
        transaction: {
          tx_hash: '0x2d900118d58606204d0cf9a257f4f889203f6eee40198d000f98b20927ff446c',
          block_number: 57687057,
          status: 'CONFIRMED',
          amount: 0.01,
          currency: 'MON',
          network: 'Monad Testnet',
          explorer_url: 'https://testnet.monadexplorer.com/tx/0x2d900118d58606204d0cf9a257f4f889203f6eee40198d000f98b20927ff446c'
        }
      }
    },
    {
      sender: 'agent',
      text: 'Payment completed successfully! 0.01 MON transferred on Monad Testnet (Chain ID 10143). Confirmed in block #57687057.'
    }
  ]);

  const pipelineStages = [
    { name: 'USER INTENT', status: 'PASSED', detail: '0.01 MON to 0x57d1...' },
    { name: 'TRUEFORGE v0.1.4', status: 'PASSED', detail: 'http://localhost:8790' },
    { name: 'MCP DISCOVERY', status: 'PASSED', detail: '19 Financial Tools' },
    { name: 'CIRCUIT BREAKER', status: 'PASSED', detail: 'Policy Engine' },
    { name: 'RISK ANALYSIS', status: 'PASSED', detail: 'Risk Score: 0.10' },
    { name: 'POLICY DECISION', status: 'ALLOW', detail: 'All Rules Passed' },
    { name: 'HMAC AUTHORIZATION', status: 'PASSED', detail: 'TOKEN-LIVE-4ef4ef' },
    { name: 'EXECUTION GATE', status: 'PASSED', detail: 'Single-Use Lock' },
    { name: 'MONAD TESTNET', status: 'CONFIRMED', detail: 'Block #57687057' },
  ];

  return (
    <div className="min-h-screen bg-[#07080c] text-slate-100 antialiased">
      <SiteNav />
      <main className="mx-auto max-w-7xl px-4 py-8 space-y-8">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between pb-6 border-b border-white/10 gap-4">
          <div>
            <div className="flex items-center gap-2 text-xs font-mono text-orange-400 uppercase tracking-widest font-semibold">
              <Bot className="h-4 w-4" /> TrueForge v0.1.4 Agent Control Plane
            </div>
            <h1 className="text-3xl font-black text-white mt-1">TrueForge Agent Session</h1>
            <p className="text-sm text-slate-400 mt-1">
              &quot;The agent can be fooled. The money doesn&apos;t have to be.&quot;
            </p>

          </div>
          <div className="flex items-center gap-3">
            <span className="flex items-center gap-2 rounded-full border border-emerald-500/40 bg-emerald-500/10 px-3 py-1 text-xs font-semibold text-emerald-400">
              <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
              Monad Testnet (10143) Connected
            </span>
          </div>
        </div>

        {/* Real-Time Security Pipeline Banner */}
        <div className="glass-panel rounded-xl p-6 border border-orange-500/30">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xs font-mono uppercase tracking-widest text-orange-400 font-bold flex items-center gap-2">
              <Cpu className="h-4 w-4" /> End-to-End Real-Time Security Pipeline
            </h2>
            <span className="text-[11px] font-mono text-slate-400">Execution Model: Deterministic Policy Gate</span>
          </div>
          <div className="grid gap-2 grid-cols-2 sm:grid-cols-3 md:grid-cols-5 lg:grid-cols-9">
            {pipelineStages.map((stage, idx) => (
              <div key={idx} className="bg-black/50 rounded-lg p-2.5 border border-white/10 text-center flex flex-col justify-between">
                <span className="text-[10px] font-mono text-slate-400 block font-semibold truncate">{stage.name}</span>
                <span className={`text-xs font-bold my-1 ${
                  stage.status === 'ALLOW' || stage.status === 'CONFIRMED' || stage.status === 'PASSED'
                    ? 'text-emerald-400'
                    : 'text-orange-400'
                }`}>
                  {stage.status}
                </span>
                <span className="text-[9px] font-mono text-slate-500 truncate">{stage.detail}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Verified Live Monad Transaction Card */}
        <div className="glass-panel rounded-xl p-6 border-l-4 border-l-emerald-500 bg-emerald-950/10">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <div className="flex items-center gap-2">
                <CheckCircle className="h-5 w-5 text-emerald-400" />
                <h3 className="text-base font-bold text-white">Verified Monad Testnet Transaction</h3>
                <span className="bg-emerald-500/20 text-emerald-300 text-xs px-2.5 py-0.5 rounded border border-emerald-500/40 font-mono font-bold">
                  CONFIRMED
                </span>
              </div>
              <p className="text-xs text-slate-300 mt-1">
                Real EVM transaction executed via TrueForge → FastMCP → Circuit Breaker → MonadTestnetAdapter.
              </p>
            </div>
            <a
              href="https://testnet.monadexplorer.com/tx/0x2d900118d58606204d0cf9a257f4f889203f6eee40198d000f98b20927ff446c"
              target="_blank"
              rel="noreferrer"
              className="focus-ring inline-flex items-center gap-2 rounded-lg bg-emerald-600 px-4 py-2 text-xs font-bold text-white hover:bg-emerald-500"
            >
              View on Monad Explorer <ExternalLink className="h-3.5 w-3.5" />
            </a>
          </div>
          <div className="grid gap-3 sm:grid-cols-2 md:grid-cols-4 mt-4 pt-4 border-t border-white/10 text-xs font-mono">
            <div>
              <span className="text-slate-400 block text-[10px] uppercase">Transaction Hash</span>
              <span className="text-slate-200 text-[11px] truncate block font-bold">0x2d900118d5860620...ff446c</span>
            </div>
            <div>
              <span className="text-slate-400 block text-[10px] uppercase">Block Number</span>
              <span className="text-slate-200 text-[11px] font-bold">#57687057</span>
            </div>
            <div>
              <span className="text-slate-400 block text-[10px] uppercase">Transfer Value</span>
              <span className="text-emerald-400 text-[11px] font-bold">0.01 MON</span>
            </div>
            <div>
              <span className="text-slate-400 block text-[10px] uppercase">Chain / RPC</span>
              <span className="text-slate-200 text-[11px] font-bold">Monad Testnet (10143)</span>
            </div>
          </div>
        </div>

        {/* Main Agent Grid */}
        <div className="grid gap-8 lg:grid-cols-12">
          {/* Conversation & Tool Trace */}
          <div className="lg:col-span-8 space-y-4">
            {messages.map((m, idx) => (
              <div key={idx} className="flex gap-4 items-start">
                <div className={`mt-1 flex h-8 w-8 items-center justify-center rounded-lg text-xs font-bold ${
                  m.sender === 'user' ? 'bg-blue-500/20 text-blue-400 border border-blue-500/40' :
                  m.sender === 'agent' ? 'bg-orange-500/20 text-orange-400 border border-orange-500/40' :
                  m.sender === 'circuit_breaker' ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40' :
                  'bg-purple-500/20 text-purple-400 border border-purple-500/40'
                }`}>
                  {m.sender === 'user' ? <User className="h-4 w-4" /> :
                   m.sender === 'agent' ? <Bot className="h-4 w-4" /> :
                   m.sender === 'circuit_breaker' ? <Shield className="h-4 w-4" /> :
                   <Terminal className="h-4 w-4" />}
                </div>

                <div className="flex-1 glass-panel rounded-xl p-4">
                  {m.sender === 'user' && <p className="text-sm font-semibold text-white">{m.text}</p>}
                  {m.sender === 'agent' && <p className="text-sm text-slate-200">{m.text}</p>}
                  {m.sender === 'tool' && (
                    <div>
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-xs font-mono text-purple-400 font-bold flex items-center gap-1">
                          <Terminal className="h-3.5 w-3.5" /> FastMCP Tool: {m.tool}()
                        </span>
                        <span className="text-[10px] font-mono text-slate-500">stdio transport</span>
                      </div>
                      <pre className="mt-1 text-xs font-mono bg-black/70 p-3 rounded-lg text-slate-300 overflow-x-auto border border-white/5">
                        {JSON.stringify(m.result, null, 2)}
                      </pre>
                    </div>
                  )}
                  {m.sender === 'circuit_breaker' && (
                    <div>
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-bold text-emerald-400 uppercase tracking-wider flex items-center gap-1.5">
                          <Shield className="h-4 w-4" /> {m.title}
                        </span>
                        <span className="text-xs font-bold bg-emerald-500/20 text-emerald-300 px-2.5 py-0.5 rounded border border-emerald-500/40">
                          {m.decision} (Risk: {m.risk_score})
                        </span>
                      </div>
                      <p className="text-xs text-slate-300 mt-2 font-mono">{m.detail}</p>
                      <div className="mt-2 text-[11px] font-mono text-emerald-400/80">HMAC SHA-256 Token: {m.token}</div>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>

          {/* Circuit Breaker Security Panel */}
          <div className="lg:col-span-4 space-y-4">
            <div className="glass-panel rounded-xl p-6 sticky top-24 border border-orange-500/30">
              <h3 className="text-sm font-bold text-white flex items-center justify-between border-b border-white/10 pb-3 mb-4">
                <span className="flex items-center gap-2">
                  <Shield className="h-4 w-4 text-orange-400" /> Circuit Breaker Security Panel
                </span>
                <span className="text-[10px] font-mono bg-orange-500/20 text-orange-300 px-2 py-0.5 rounded border border-orange-500/40">
                  AUTHORITATIVE
                </span>
              </h3>

              <div className="space-y-2.5 text-xs font-mono">
                <div className="flex justify-between py-1.5 border-b border-white/5">
                  <span className="text-slate-400">POLICY DECISION</span>
                  <span className="font-bold text-emerald-400 bg-emerald-500/20 px-2 py-0.5 rounded">ALLOW</span>
                </div>
                <div className="flex justify-between py-1.5 border-b border-white/5">
                  <span className="text-slate-400">RISK SCORE</span>
                  <span className="font-bold text-emerald-400">0.10 (LOW RISK)</span>
                </div>
                <div className="flex justify-between py-1.5 border-b border-white/5">
                  <span className="text-slate-400">VELOCITY CHECK</span>
                  <span className="font-bold text-emerald-400">PASS</span>
                </div>
                <div className="flex justify-between py-1.5 border-b border-white/5">
                  <span className="text-slate-400">DUPLICATE DETECTOR</span>
                  <span className="font-bold text-emerald-400">PASS</span>
                </div>
                <div className="flex justify-between py-1.5 border-b border-white/5">
                  <span className="text-slate-400">PROMPT INJECTION</span>
                  <span className="font-bold text-emerald-400">NONE DETECTED</span>
                </div>
                <div className="flex justify-between py-1.5 border-b border-white/5">
                  <span className="text-slate-400">FRAUDGRAPH SIGNAL</span>
                  <span className="font-bold text-emerald-400">LOW RISK</span>
                </div>
                <div className="flex justify-between py-1.5 border-b border-white/5">
                  <span className="text-slate-400">HMAC TOKEN</span>
                  <span className="font-bold text-emerald-400">ISSUED</span>
                </div>
                <div className="flex justify-between py-1.5 border-b border-white/5">
                  <span className="text-slate-400">EXECUTION GATE</span>
                  <span className="font-bold text-emerald-400">SINGLE-USE LOCK</span>
                </div>
                <div className="flex justify-between py-1.5">
                  <span className="text-slate-400">PRIVATE KEY ISOLATION</span>
                  <span className="font-bold text-emerald-400">BACKEND ISOLATED</span>
                </div>
              </div>

              <div className="mt-5 pt-4 border-t border-white/10 bg-black/40 p-3 rounded-lg text-[11px] text-slate-300 font-mono">
                <span className="text-orange-400 font-bold block mb-1">Architecture Guarantee:</span>
                TrueForge orchestrates tools. Circuit Breaker independently evaluates policy & holds execution authority.
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
