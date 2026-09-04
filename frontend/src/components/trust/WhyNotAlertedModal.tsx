'use client';

import React, { useEffect, useState } from 'react';
import { WhyNotAlertedProof } from '@/lib/types';
import { api } from '@/lib/api';
import { ShieldCheck, X, CheckCircle2, AlertCircle, RefreshCw, BarChart3 } from 'lucide-react';

interface WhyNotAlertedModalProps {
  symbol: string | null;
  onClose: () => void;
}

export function WhyNotAlertedModal({ symbol, onClose }: WhyNotAlertedModalProps) {
  const [proof, setProof] = useState<WhyNotAlertedProof | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!symbol) return;
    setIsLoading(true);
    setError(null);

    api.stocks
      .getWhyNotAlerted(symbol)
      .then((data) => {
        setProof(data);
        setIsLoading(false);
      })
      .catch((err) => {
        setError(err.message || 'Failed to generate trust audit');
        setIsLoading(false);
      });
  }, [symbol]);

  if (!symbol) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
      <div className="relative w-full max-w-lg rounded-2xl border border-slate-800 bg-[#0c121e] p-6 shadow-2xl">
        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 rounded-lg p-1.5 text-slate-400 hover:bg-slate-800 hover:text-white transition"
        >
          <X className="h-5 w-5" />
        </button>

        {/* Header */}
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <ShieldCheck className="h-5 w-5" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-white">
              Why Wasn't I Alerted on {symbol}?
            </h3>
            <p className="text-xs text-slate-400">Deterministic Trust & Verification Audit</p>
          </div>
        </div>

        {isLoading ? (
          <div className="flex items-center justify-center py-12 gap-2 text-sm text-slate-400">
            <RefreshCw className="h-4 w-4 animate-spin text-emerald-400" />
            <span>Calculating statistical bounds and volume baseline...</span>
          </div>
        ) : error ? (
          <div className="mt-4 rounded-xl border border-rose-900/50 bg-rose-950/20 p-4 text-xs text-rose-300">
            {error}
          </div>
        ) : proof ? (
          <div className="mt-5 space-y-4">
            {/* Quick Metrics Strip */}
            <div className="grid grid-cols-3 gap-2 text-center">
              <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-2.5">
                <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Attention Score</span>
                <span className="text-lg font-bold text-emerald-400 font-mono">
                  {proof.attention_score}<span className="text-xs font-normal text-slate-400">/{proof.threshold}</span>
                </span>
              </div>

              <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-2.5">
                <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Price Move</span>
                <span className="text-lg font-bold text-slate-200 font-mono">
                  {proof.price_delta_pct > 0 ? '+' : ''}{proof.price_delta_pct}%
                </span>
              </div>

              <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-2.5">
                <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Volume Pace</span>
                <span className="text-lg font-bold text-slate-200 font-mono">
                  {proof.volume_ratio}x
                </span>
              </div>
            </div>

            {/* Objective Reasons Checklist */}
            <div className="rounded-xl border border-slate-800/80 bg-slate-900/40 p-4 space-y-2.5">
              <span className="text-xs font-semibold text-slate-300 block">Verification Criteria</span>
              {proof.reasons.map((reason, idx) => (
                <div key={idx} className="flex items-start gap-2.5 text-xs text-slate-300 leading-relaxed">
                  <CheckCircle2 className="h-4 w-4 text-emerald-400 mt-0.5 flex-shrink-0" />
                  <span>{reason}</span>
                </div>
              ))}
            </div>

            {/* Final Verdict Banner */}
            <div className="rounded-xl border border-emerald-900/40 bg-emerald-950/20 p-3.5 text-xs text-emerald-300 leading-relaxed">
              <strong className="block font-semibold text-emerald-200 mb-1">Product Principle in Action:</strong>
              {proof.verdict}
            </div>

            <div className="pt-2 flex justify-end">
              <button
                onClick={onClose}
                className="rounded-lg bg-slate-800 px-4 py-2 text-xs font-semibold text-slate-200 hover:bg-slate-700 hover:text-white transition"
              >
                Close Audit
              </button>
            </div>
          </div>
        ) : null}
      </div>
    </div>
  );
}
