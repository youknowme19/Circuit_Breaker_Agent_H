'use client';

import React, { useState } from 'react';
import { Network, AlertCircle } from 'lucide-react';

interface Node {
  id: string;
  label: string;
  type: string;
}

interface Edge {
  source: string;
  target: string;
  amount: number;
}

interface GraphData {
  nodes: Node[];
  edges: Edge[];
}

interface Props {
  graphData: GraphData;
}

export default function FraudGraphView({ graphData }: Props) {
  const [selectedNode, setSelectedNode] = useState<string | null>(null);

  const nodes = graphData.nodes || [];
  const edges = graphData.edges || [];

  return (
    <div className="glass-panel rounded-xl p-5 flex flex-col h-full">
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-base font-bold text-white flex items-center gap-2">
          <Network className="w-5 h-5 text-purple-400" />
          FraudGraph Behavioral Intelligence
        </h2>
        <span className="text-xs font-mono px-2 py-0.5 rounded bg-purple-950/60 text-purple-300 border border-purple-800/50">
          NetworkX Graph Topology
        </span>
      </div>

      <div className="bg-slate-950/80 rounded-lg p-4 border border-slate-800 flex-1 relative flex flex-col items-center justify-center min-h-[220px]">
        {nodes.length === 0 ? (
          <p className="text-sm text-slate-500">No graph data from backend yet.</p>
        ) : (
        <div className="flex items-center gap-6 flex-wrap justify-center my-4">
          {nodes.map((n, idx) => {
            const isSuspicious = (n as any).suspicious || n.id === 'ACC-991';
            const isSelected = selectedNode === n.id;

            return (
              <div
                key={n.id}
                role="button"
                tabIndex={0}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') setSelectedNode(n.id);
                }}
                onClick={() => setSelectedNode(n.id)}
                className={`p-3 rounded-xl border transition-all cursor-pointer text-center font-mono ${
                  isSuspicious
                    ? 'bg-rose-950/40 border-rose-500/60 text-rose-300 hover:bg-rose-900/50'
                    : 'bg-slate-900 border-slate-700 text-slate-200 hover:bg-slate-800'
                } ${isSelected ? 'ring-2 ring-purple-500 scale-105' : ''}`}
              >
                <div className="text-xs font-bold">{n.id}</div>
                <div className="text-[10px] text-slate-400 mt-0.5">
                  {(n as any).transaction_count ?? 0} tx · risk {(n as any).risk_score ?? '—'}
                </div>
              </div>
            );
          })}
        </div>
        )}

        <div className="w-full mt-2 pt-2 border-t border-slate-800/80 flex items-center justify-between text-xs font-mono text-slate-400">
          <div className="flex items-center gap-1.5 text-amber-400">
            <AlertCircle className="w-3.5 h-3.5" />
            <span>Edges: {edges.length} · click a node to inspect</span>
          </div>
          <span className="text-rose-400 font-bold">
            {selectedNode || 'select node'}
          </span>
        </div>
      </div>
    </div>
  );
}
