'use client';

const stages = ['AI AGENT', 'MCP', 'CIRCUIT BREAKER', 'AUTHORIZATION', 'EXECUTION GATE', 'PAYMENT'];

export default function PipelineFlow() {
  return (
    <div className="terminal-panel relative overflow-hidden rounded-2xl p-5" aria-hidden={false} role="img" aria-label="Authorization pipeline from untrusted agent to payment">
      <div className="mb-4 font-mono text-[10px] uppercase tracking-[0.2em] text-orange-300/80">Live architecture</div>
      <div className="flex flex-col gap-2">
        {stages.map((stage, i) => (
          <div key={stage} className="flex flex-col items-stretch">
            <div
              className={`node-live rounded-lg border px-3 py-2 font-mono text-xs font-semibold ${
                i === 2 || i === 4
                  ? 'border-orange-500/50 bg-orange-500/10 text-orange-100'
                  : 'border-white/10 bg-white/5 text-slate-200'
              }`}
            >
              {stage}
            </div>
            {i < stages.length - 1 && (
              <div className="relative mx-auto h-5 w-px bg-gradient-to-b from-orange-500/80 to-orange-500/10">
                <span className="absolute left-1/2 top-0 h-1.5 w-1.5 -translate-x-1/2 rounded-full bg-orange-400 flow-dot" style={{ animationDelay: `${i * 0.45}s` }} />
              </div>
            )}
          </div>
        ))}
      </div>
      <p className="mt-4 font-mono text-[11px] text-slate-400">
        Untrusted reasoning in. Deterministic authorization out. Money only after the gate.
      </p>
    </div>
  );
}
