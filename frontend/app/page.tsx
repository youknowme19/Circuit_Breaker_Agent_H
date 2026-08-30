'use client';

import Link from 'next/link';
import SiteNav from '@/components/SiteNav';
import PipelineFlow from '@/components/PipelineFlow';
import ArchitectureMap from '@/components/ArchitectureMap';

const controls = [
  { title: 'Policy Engine', body: 'Rules-based deterministic transaction evaluation.' },
  { title: 'Velocity Guard', body: 'Prevents cumulative spending beyond configured limits.' },
  { title: 'Duplicate Detector', body: 'Detects repeated invoice and payment attempts.' },
  { title: 'FraudGraph', body: 'Suspicious transaction relationships and layering paths.' },
  { title: 'Cryptographic Authorization', body: 'HMAC-SHA256 token binding to the action.' },
  { title: 'Canonical Action Hash', body: 'Authorization is bound to the exact payment payload.' },
  { title: 'Replay Protection', body: 'Consumed authorization cannot be reused.' },
  { title: 'Human Approval', body: 'REVIEW actions require an explicit operator decision.' },
  { title: 'Atomic Execution', body: 'Concurrent requests cannot double-execute.' },
  { title: 'Audit Chain', body: 'Tamper-evident SHA-256 chained event log.' },
];

export default function LandingPage() {
  return (
    <div className="cb-grid min-h-screen">
      <SiteNav />
      <main>
        <section className="mx-auto grid max-w-7xl items-center gap-10 px-4 py-16 lg:grid-cols-2">
          <div>
            <p className="font-mono text-[11px] uppercase tracking-[0.25em] text-orange-400">Financial infrastructure for autonomous agents</p>
            <h1 className="mt-4 text-4xl font-black leading-[1.05] tracking-tight text-white sm:text-6xl">
              The agent can be fooled.
              <span className="mt-2 block text-orange-400">The money doesn’t have to be.</span>
            </h1>
            <p className="mt-6 max-w-xl text-lg text-slate-300">
              Circuit Breaker is a deterministic authorization layer between AI agents and financial execution.
              Autonomous agents should reason about money without owning the authority to move it.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link href="/console" className="focus-ring rounded-lg bg-orange-600 px-5 py-3 text-sm font-bold text-white hover:bg-orange-500">
                Launch Security Console
              </Link>
              <Link href="/attacks" className="focus-ring rounded-lg border border-white/20 px-5 py-3 text-sm font-bold text-white hover:bg-white/5">
                Watch the Attack Demo
              </Link>
              <Link href="/console#demo" className="focus-ring rounded-lg px-5 py-3 text-sm font-semibold text-orange-200 hover:text-white">
                Run Security Demo
              </Link>
            </div>
          </div>
          <PipelineFlow />
        </section>

        <section className="border-y border-white/10 bg-black/30 py-16">
          <div className="mx-auto max-w-7xl px-4">
            <h2 className="text-2xl font-black text-white">AI reasoning ≠ authorization</h2>
            <p className="mt-4 max-w-3xl text-slate-300">
              Agents can read invoices, call tools, and process untrusted instructions. LLM reasoning is probabilistic.
              Financial authorization should not be. A malicious invoice can fool the model. Circuit Breaker still sees a
              structured amount, destination, and invoice id — and decides with deterministic policy.
            </p>
            <div className="mt-8 grid gap-4 md:grid-cols-3">
              {[
                ['Problem', 'Prompt injection and tool-calling agents sit next to money movement.'],
                ['Solution', 'Separate reasoning from authorization. MCP is a capability, not a bypass.'],
                ['Result', 'ALLOW / REVIEW / BLOCK from Python. One authorization → exactly one execution.'],
              ].map(([t, b]) => (
                <div key={t} className="glass-panel rounded-xl p-5">
                  <h3 className="font-mono text-xs uppercase tracking-widest text-orange-300">{t}</h3>
                  <p className="mt-2 text-sm text-slate-200">{b}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="mx-auto max-w-7xl px-4 py-16">
          <h2 className="text-2xl font-black text-white">Core architecture</h2>
          <p className="mt-2 text-slate-400">Separate reasoning from authorization. Click a node.</p>
          <div className="mt-8">
            <ArchitectureMap />
          </div>
        </section>

        <section className="border-y border-white/10 bg-black/30 py-16">
          <div className="mx-auto max-w-7xl px-4">
            <h2 className="text-2xl font-black text-white">Security engine</h2>
            <p className="mt-2 text-slate-400">Deterministic policy. Cryptographic authorization. Atomic execution.</p>
            <div className="mt-8 grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
              {controls.map((c) => (
                <article key={c.title} className="glass-panel rounded-xl p-4">
                  <h3 className="text-sm font-bold text-white">{c.title}</h3>
                  <p className="mt-2 text-xs leading-relaxed text-slate-400">{c.body}</p>
                </article>
              ))}
            </div>
          </div>
        </section>

        <section className="mx-auto max-w-7xl px-4 py-16">
          <h2 className="text-2xl font-black text-white">Attack Lab</h2>
          <p className="mt-2 max-w-2xl text-slate-300">Try to break it. Every scenario hits the live backend. The UI never fakes a BLOCK.</p>
          <Link href="/attacks" className="focus-ring mt-6 inline-block rounded-lg border border-orange-500/40 px-5 py-3 text-sm font-bold text-orange-200 hover:bg-orange-500/10">
            Open Attack Lab
          </Link>
        </section>
      </main>
    </div>
  );
}
