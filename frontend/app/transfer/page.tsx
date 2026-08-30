'use client';

import { useState } from 'react';
import SiteNav from '@/components/SiteNav';
import { Send, CheckCircle, XCircle, Clock, Play, ExternalLink } from 'lucide-react';
import { api, ApiError } from '@/lib/api';

export default function TransferPage() {
  const [network, setNetwork] = useState('Monad Testnet');
  const [fromAddress, setFromAddress] = useState('0xa7c965820d4933dBe9F71fE665A4D0adAE98aD06');
  const [toAddress, setToAddress] = useState('0x57d1Cf3D387de087Eda90a1cC81eAc608F7a8f55');
  const [amount, setAmount] = useState('1');
  const [asset, setAsset] = useState('MON');
  const [reason, setReason] = useState('Monad Testnet payment transfer');

  const [submitting, setSubmitting] = useState(false);
  const [timeline, setTimeline] = useState<any[]>([]);
  const [result, setResult] = useState<any>(null);

  const handleRequestTransfer = async (e: React.FormEvent) => {
    e.preventDefault();
    if (submitting) return;

    setSubmitting(true);
    setResult(null);
    setTimeline([
      { title: 'Payment Intent Created', status: 'done', detail: `Transfer ${amount} ${asset} to ${toAddress.slice(0, 10)}...` },
      { title: 'Submitting to Circuit Breaker', status: 'running', detail: 'Evaluating policy, velocity & FraudGraph...' }
    ]);

    try {
      const actId = `ACT-${Math.random().toString(36).substring(2, 8).toUpperCase()}`;
      const payload = {
        action_id: actId,
        agent_id: 'trueforge-financial-operator',
        source_account: fromAddress,
        destination_account: toAddress,
        counterparty_id: toAddress,
        amount: parseFloat(amount),
        currency: asset,
        reason: reason
      };

      const data = await api<any>('/api/actions/propose', {
        method: 'POST',
        body: JSON.stringify({ action: payload })
      });

      const dec = data.decision;

      if (dec === 'BLOCK') {
        const violationMsg = data.violations?.[0]?.message || 'Limit exceeded';
        setTimeline([
          { title: 'Payment Intent Created', status: 'done', detail: `Transfer ${amount} ${asset} to ${toAddress.slice(0, 10)}...` },
          { title: 'Policy Engine Check', status: 'failed', detail: `BLOCKED: Policy violation (${violationMsg})` }
        ]);
        setResult({ status: 'BLOCKED', data });
        return;
      }

      setTimeline([
        { title: 'Payment Intent Created', status: 'done', detail: `Transfer ${amount} ${asset} to ${toAddress.slice(0, 10)}...` },
        { title: 'Policy Engine Check', status: 'done', detail: `Decision: ${dec}` },
        { title: 'Issuing Cryptographic HMAC Token', status: 'running', detail: 'Signing canonical action hash...' }
      ]);

      // Extract authorization token string (e.g. "AUTH-0001")
      const tokenId = typeof data.authorization_token === 'string'
        ? data.authorization_token
        : (data.authorization_token?.token_id || `TOKEN-${actId}`);

      const execData = await api<any>(`/api/actions/${actId}/execute`, {
        method: 'POST',
        body: JSON.stringify({ token_id: tokenId })
      });

      setTimeline([
        { title: 'Payment Intent Created', status: 'done', detail: `Transfer ${amount} ${asset} to ${toAddress.slice(0, 10)}...` },
        { title: 'Policy Engine Check', status: 'done', detail: `Decision: ${dec}` },
        { title: 'HMAC Authorization Token Issued', status: 'done', detail: `Token ID: ${tokenId}` },
        { title: 'Atomic Execution Gate Broadcast', status: 'done', detail: execData.message || 'Transaction executed' }
      ]);

      setResult({ status: execData.success ? 'EXECUTED' : 'FAILED', execData });
    } catch (e: any) {
      const errorMsg = e instanceof ApiError ? e.message : (e.message || 'API Connection Failed');
      setTimeline((prev) => [
        ...prev.map(item => item.status === 'running' ? { ...item, status: 'failed', detail: `FAILED: ${errorMsg}` } : item),
      ]);
      setResult({ status: 'FAILED', errorMsg });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#07080c] text-slate-100 antialiased">
      <SiteNav />
      <main className="mx-auto max-w-7xl px-4 py-8">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between pb-6 border-b border-white/10 gap-4">
          <div>
            <div className="flex items-center gap-2 text-xs font-mono text-orange-400 uppercase tracking-wider">
              <Send className="h-4 w-4" /> Real-Time Execution Console
            </div>
            <h1 className="text-3xl font-black text-white mt-1">Transfer Console</h1>
            <p className="text-sm text-slate-400 mt-1">
              Submit testnet financial requests. Circuit Breaker evaluates policies before the Execution Gate moves funds.
            </p>
          </div>
        </div>

        <div className="grid gap-8 lg:grid-cols-12 mt-8">
          <div className="lg:col-span-5">
            <form onSubmit={handleRequestTransfer} className="glass-panel rounded-xl p-6 space-y-4">
              <h2 className="text-lg font-bold text-white mb-4">New Payment Request</h2>
              
              <div>
                <label className="block text-xs font-bold text-slate-400 uppercase mb-1">Network</label>
                <select
                  value={network}
                  onChange={(e) => setNetwork(e.target.value)}
                  className="w-full rounded-lg border border-white/15 bg-black/50 px-3 py-2 text-sm text-white focus:outline-none focus:ring-1 focus:ring-orange-500"
                >
                  <option value="Monad Testnet">Monad Testnet (Chain ID 10143)</option>
                  <option value="Ethereum Sepolia">Ethereum Sepolia (Chain ID 11155111)</option>
                  <option value="Safe Mock Network">Safe Mock Network (Demo)</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-400 uppercase mb-1">From Address (Configured Wallet)</label>
                <input
                  type="text"
                  value={fromAddress}
                  onChange={(e) => setFromAddress(e.target.value)}
                  className="w-full rounded-lg border border-white/15 bg-black/50 px-3 py-2 text-sm font-mono text-slate-300 focus:outline-none focus:ring-1 focus:ring-orange-500"
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-400 uppercase mb-1">To Recipient Address</label>
                <input
                  type="text"
                  value={toAddress}
                  onChange={(e) => setToAddress(e.target.value)}
                  className="w-full rounded-lg border border-white/15 bg-black/50 px-3 py-2 text-sm font-mono text-slate-300 focus:outline-none focus:ring-1 focus:ring-orange-500"
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-slate-400 uppercase mb-1">Amount</label>
                  <input
                    type="number"
                    step="0.0001"
                    value={amount}
                    onChange={(e) => setAmount(e.target.value)}
                    className="w-full rounded-lg border border-white/15 bg-black/50 px-3 py-2 text-sm font-mono text-white focus:outline-none focus:ring-1 focus:ring-orange-500"
                    required
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-slate-400 uppercase mb-1">Asset</label>
                  <select
                    value={asset}
                    onChange={(e) => setAsset(e.target.value)}
                    className="w-full rounded-lg border border-white/15 bg-black/50 px-3 py-2 text-sm text-white focus:outline-none focus:ring-1 focus:ring-orange-500"
                  >
                    <option value="MON">MON</option>
                    <option value="ETH">ETH</option>
                    <option value="USD">USD</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-400 uppercase mb-1">Reason / Reference</label>
                <input
                  type="text"
                  value={reason}
                  onChange={(e) => setReason(e.target.value)}
                  className="w-full rounded-lg border border-white/15 bg-black/50 px-3 py-2 text-sm text-slate-300 focus:outline-none focus:ring-1 focus:ring-orange-500"
                />
              </div>

              <button
                type="submit"
                disabled={submitting}
                className="w-full rounded-lg bg-orange-600 px-4 py-2.5 text-sm font-bold text-white hover:bg-orange-500 disabled:opacity-50 flex items-center justify-center gap-2 mt-4"
              >
                {submitting ? <Clock className="h-4 w-4 animate-spin" /> : <Play className="h-4 w-4" />}
                {submitting ? 'Evaluating Circuit Breaker...' : 'REQUEST TRANSFER'}
              </button>
            </form>
          </div>

          <div className="lg:col-span-7">
            <div className="glass-panel rounded-xl p-6">
              <h2 className="text-lg font-bold text-white mb-6">Live Execution Pipeline</h2>
              
              {timeline.length === 0 ? (
                <div className="text-center py-12 text-slate-500 text-sm">
                  Submit a transfer request to observe Circuit Breaker authorization in real time.
                </div>
              ) : (
                <div className="space-y-6">
                  {timeline.map((step, idx) => (
                    <div key={idx} className="flex gap-4 items-start">
                      <div className={`mt-0.5 flex h-6 w-6 items-center justify-center rounded-full text-xs font-bold ${
                        step.status === 'done' ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40' :
                        step.status === 'failed' ? 'bg-red-500/20 text-red-400 border border-red-500/40' :
                        'bg-orange-500/20 text-orange-400 border border-orange-500/40 animate-pulse'
                      }`}>
                        {step.status === 'done' ? '✓' : step.status === 'failed' ? '✕' : idx + 1}
                      </div>
                      <div>
                        <h4 className="text-sm font-bold text-white">{step.title}</h4>
                        <p className="text-xs text-slate-400 mt-0.5">{step.detail}</p>
                      </div>
                    </div>
                  ))}

                  {result && (
                    <div className={`mt-8 rounded-xl p-4 border ${
                      result.status === 'EXECUTED' ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300' :
                      result.status === 'BLOCKED' ? 'bg-red-500/10 border-red-500/30 text-red-300' :
                      'bg-orange-500/10 border-orange-500/30 text-orange-300'
                    }`}>
                      <h3 className="text-sm font-bold flex items-center gap-2">
                        {result.status === 'EXECUTED' && <CheckCircle className="h-4 w-4" />}
                        {result.status === 'BLOCKED' && <XCircle className="h-4 w-4" />}
                        Result: {result.status}
                      </h3>
                      {result.execData?.transaction?.explorer_url && (
                        <a
                          href={result.execData.transaction.explorer_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="mt-3 inline-flex items-center gap-1.5 text-xs font-bold underline hover:opacity-80"
                        >
                          View Blockchain Explorer <ExternalLink className="h-3 w-3" />
                        </a>
                      )}
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
