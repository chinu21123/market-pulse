'use client';

import React, { useState } from 'react';
import { api } from '@/lib/api';
import { Zap, Clock, TrendingUp, X, RefreshCw, Sparkles } from 'lucide-react';

interface SimulationModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSimulationComplete: () => void;
}

export function SimulationModal({
  isOpen,
  onClose,
  onSimulationComplete,
}: SimulationModalProps) {
  const [minutes, setMinutes] = useState<number>(263); // 4h 23m
  const [scenario, setScenario] = useState<string>('tech_divergence');
  const [isSimulating, setIsSimulating] = useState<boolean>(false);

  if (!isOpen) return null;

  const handleSimulate = async () => {
    setIsSimulating(true);
    try {
      await api.memory.simulateAway(minutes, scenario);
      onSimulationComplete();
      onClose();
    } catch (err) {
      console.error('Simulation error:', err);
    } finally {
      setIsSimulating(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-sm p-4">
      <div className="relative w-full max-w-md rounded-2xl border border-amber-500/30 bg-[#0c121e] p-6 shadow-2xl">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 rounded-lg p-1.5 text-slate-400 hover:bg-slate-800 hover:text-white transition"
        >
          <X className="h-5 w-5" />
        </button>

        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-amber-500/10 text-amber-400 border border-amber-500/30">
            <Zap className="h-5 w-5" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-white">Time Machine Simulator</h3>
            <p className="text-xs text-slate-400">Explore how your Market Memory responds to changing conditions.</p>
          </div>
        </div>

        <p className="mt-3 text-xs text-slate-300 leading-relaxed">
          Instead of waiting 4 hours in real time, configure your simulated return to instantly test Market Memory and the Meaningful Change Engine.
        </p>

        <div className="mt-5 space-y-4">
          {/* Time away presets */}
          <div>
            <label className="text-xs font-semibold text-slate-300 block mb-2">
              Time Away Duration:
            </label>
            <div className="grid grid-cols-4 gap-2">
              {[
                { label: '45m', val: 45 },
                { label: '4h 23m', val: 263 },
                { label: '1 Day', val: 1440 },
                { label: '3 Days', val: 4320 },
              ].map((item) => (
                <button
                  key={item.val}
                  type="button"
                  onClick={() => setMinutes(item.val)}
                  className={`rounded-lg py-2 text-xs font-semibold border transition ${
                    minutes === item.val
                      ? 'bg-amber-500/20 border-amber-500/50 text-amber-300'
                      : 'bg-slate-900 border-slate-800 text-slate-400 hover:border-slate-700 hover:text-white'
                  }`}
                >
                  {item.label}
                </button>
              ))}
            </div>
          </div>

          {/* Scenario Selection */}
          <div>
            <label className="text-xs font-semibold text-slate-300 block mb-2">
              Market Scenario:
            </label>
            <div className="space-y-2">
              {[
                {
                  id: 'tech_divergence',
                  title: 'Tech Earnings Divergence (Recommended)',
                  desc: 'NVDA surges +6%, TSLA drops -4%, while AAPL & MSFT drift normally.',
                },
                {
                  id: 'high_volatility',
                  title: 'Broad Market Volatility Shock',
                  desc: 'Multi-sigma movements across multiple tickers.',
                },
                {
                  id: 'calm_market',
                  title: 'Calm Market (All Normal)',
                  desc: 'Subdued volume and tight range within standard ATR bounds.',
                },
              ].map((s) => (
                <button
                  key={s.id}
                  type="button"
                  onClick={() => setScenario(s.id)}
                  className={`w-full text-left rounded-xl p-3 border transition ${
                    scenario === s.id
                      ? 'bg-amber-500/10 border-amber-500/40 text-slate-100'
                      : 'bg-slate-900/60 border-slate-800 text-slate-400 hover:border-slate-700 hover:text-slate-200'
                  }`}
                >
                  <div className="flex items-center justify-between text-xs font-semibold">
                    <span>{s.title}</span>
                    {scenario === s.id && <Sparkles className="h-3.5 w-3.5 text-amber-400" />}
                  </div>
                  <p className="text-[11px] text-slate-400 mt-1">{s.desc}</p>
                </button>
              ))}
            </div>
          </div>

          <button
            type="button"
            disabled={isSimulating}
            onClick={handleSimulate}
            className="w-full flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-amber-500 to-amber-600 px-4 py-3 text-sm font-bold text-slate-950 hover:from-amber-400 hover:to-amber-500 transition shadow-lg shadow-amber-500/20 disabled:opacity-50"
          >
            {isSimulating ? (
              <>
                <RefreshCw className="h-4 w-4 animate-spin" />
                <span>Simulating Time Jump...</span>
              </>
            ) : (
              <>
                <Zap className="h-4 w-4" />
                <span>Run Simulation & Refresh Feed</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
