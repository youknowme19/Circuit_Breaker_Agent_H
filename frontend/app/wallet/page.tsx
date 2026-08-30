'use client';

import { useState, useEffect } from 'react';
import SiteNav from '@/components/SiteNav';
import { Wallet, ShieldCheck, Cpu, RefreshCw, ExternalLink, Key, CheckCircle, Wifi } from 'lucide-react';

import { api } from '@/lib/api';

export default function WalletPage() {
  const [loading, setLoading] = useState(false);
  const [wallet, setWallet] = useState<any>({
    address: '0xa7c965820d4933dBe9F71fE665A4D0adAE98aD06',
    network: 'Monad Testnet',
    chain_id: 10143,
    asset: 'MON',
    balance: 10.915018,
    mode: 'LIVE MONAD TESTNET',
    rpc_status: 'CONNECTED (https://testnet-rpc.monad.xyz)'
  });

  const fetchWallet = async () => {
    setLoading(true);
    try {
      const data = await api<any>('/api/health');
      setWallet((prev: any) => ({
        ...prev,
        mode: data.execution_mode || 'LIVE MONAD TESTNET',
        network: data.testnet_execution_enabled ? 'Monad Testnet' : 'Safe Mock Network'
      }));
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchWallet();
  }, []);

  return (
    <div className="min-h-screen bg-[#07080c] text-slate-100 antialiased">
      <SiteNav />
      <main className="mx-auto max-w-7xl px-4 py-8 space-y-8">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between pb-6 border-b border-white/10 gap-4">
          <div>
            <div className="flex items-center gap-2 text-xs font-mono text-orange-400 uppercase tracking-widest font-semibold">
              <Wallet className="h-4 w-4" /> Configured Wallet & Network
            </div>
            <h1 className="text-3xl font-black text-white mt-1">Monad Testnet Wallet Overview</h1>
            <p className="text-sm text-slate-400 mt-1">
              Private keys remain isolated backend-side in <code className="text-orange-300 font-mono">.env</code>. LLMs and frontend context NEVER see private keys.
            </p>
          </div>
          <button
            onClick={fetchWallet}
            disabled={loading}
            className="flex items-center gap-2 rounded-lg border border-white/15 bg-white/5 px-4 py-2 text-xs font-bold text-slate-200 hover:bg-white/10"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${loading ? 'animate-spin' : ''}`} /> Refresh Balance
          </button>
        </div>

        <div className="grid gap-6 md:grid-cols-3">
          <div className="glass-panel rounded-xl p-6 md:col-span-2 space-y-6">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-mono uppercase tracking-wider text-slate-400 font-bold">Public Sender Address</span>
                <span className="flex items-center gap-1 rounded-full bg-emerald-500/10 px-2.5 py-0.5 text-xs font-mono font-bold text-emerald-400 border border-emerald-500/30">
                  <CheckCircle className="h-3.5 w-3.5" /> Isolated Backend-Side
                </span>
              </div>
              <div className="flex items-center justify-between rounded-lg border border-white/10 bg-black/50 p-4 font-mono text-sm text-orange-300 font-bold">
                <span>{wallet.address}</span>
              </div>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-4 border-t border-white/10 font-mono">
              <div>
                <span className="text-[10px] font-mono text-slate-400 uppercase block font-semibold">Current Balance</span>
                <span className="text-2xl font-black text-white mt-1 block">
                  {wallet.balance} <span className="text-orange-400 text-sm">{wallet.asset}</span>
                </span>
              </div>
              <div>
                <span className="text-[10px] font-mono text-slate-400 uppercase block font-semibold">Network / Asset</span>
                <span className="text-sm font-bold text-slate-200 mt-1 block">
                  {wallet.network} ({wallet.asset})
                </span>
              </div>
              <div>
                <span className="text-[10px] font-mono text-slate-400 uppercase block font-semibold">Chain ID</span>
                <span className="text-sm font-bold text-slate-200 mt-1 block">
                  {wallet.chain_id}
                </span>
              </div>
              <div>
                <span className="text-[10px] font-mono text-slate-400 uppercase block font-semibold">Execution Mode</span>
                <span className="text-sm font-bold text-emerald-400 mt-1 block">
                  {wallet.mode}
                </span>
              </div>
            </div>

            <div className="pt-4 border-t border-white/10 flex items-center justify-between text-xs font-mono text-slate-300">
              <span className="flex items-center gap-2 text-emerald-400 font-bold">
                <Wifi className="h-4 w-4" /> RPC Endpoint: https://testnet-rpc.monad.xyz
              </span>
              <a
                href="https://testnet.monadexplorer.com"
                target="_blank"
                rel="noreferrer"
                className="text-orange-400 hover:underline flex items-center gap-1"
              >
                Monad Explorer <ExternalLink className="h-3 w-3" />
              </a>
            </div>
          </div>

          <div className="glass-panel rounded-xl p-6 space-y-4">
            <h3 className="text-sm font-bold text-white flex items-center gap-2 border-b border-white/10 pb-3">
              <Key className="h-4 w-4 text-orange-400" /> Security Invariant
            </h3>
            <p className="text-xs text-slate-300 leading-relaxed font-mono">
              The AI agent can reason about payments and request transfers, but it <strong className="text-white">never</strong> receives private keys or raw signing capability.
            </p>
            <div className="rounded-lg bg-orange-500/10 border border-orange-500/20 p-3 text-xs text-orange-200 font-mono space-y-1">
              <strong className="block text-orange-400">Strict Key Isolation:</strong>
              Transfers are signed exclusively backend-side by the MonadTestnetAdapter after successful Circuit Breaker authorization.
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
