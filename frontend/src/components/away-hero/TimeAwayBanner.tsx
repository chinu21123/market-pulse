import React from 'react';
import { Clock, AlertTriangle, ShieldCheck, TrendingUp, Sparkles } from 'lucide-react';

interface TimeAwayBannerProps {
  elapsedHuman: string;
  totalWatched: number;
  meaningfulCount: number;
  attentionCount: number;
  normalCount: number;
  lastSnapshotAt?: string;
}

export function TimeAwayBanner({
  elapsedHuman,
  totalWatched,
  meaningfulCount,
  attentionCount,
  normalCount,
  lastSnapshotAt,
}: TimeAwayBannerProps) {
  return (
    <div className="relative overflow-hidden rounded-2xl border border-slate-800 bg-gradient-to-b from-slate-900/90 to-[#0c121e] p-6 shadow-xl">
      {/* Decorative gradient blur */}
      <div className="pointer-events-none absolute -top-24 -right-24 h-72 w-72 rounded-full bg-blue-500/10 blur-3xl" />
      <div className="pointer-events-none absolute -bottom-24 -left-24 h-72 w-72 rounded-full bg-cyan-500/10 blur-3xl" />

      <div className="relative z-10 flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
        <div>
          <div className="inline-flex items-center gap-2 rounded-full border border-blue-500/30 bg-blue-500/10 px-3 py-1 text-xs font-semibold text-blue-300">
            <Sparkles className="h-3.5 w-3.5 text-blue-400" />
            <span>Market Memory Active</span>
          </div>

          <h1 className="mt-3 text-2xl font-extrabold tracking-tight text-white sm:text-3xl">
            You were away for <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-cyan-300">{elapsedHuman}</span>.
          </h1>

          <p className="mt-2 text-sm text-slate-300 max-w-2xl leading-relaxed">
            <strong className="text-white">{meaningfulCount} stocks</strong> changed meaningfully since your last checkpoint.
            {attentionCount > 0 ? (
              <> <span className="text-amber-400 font-semibold">{attentionCount} require your immediate attention</span>, while </>
            ) : (
              ' None require urgent intervention, and '
            )}
            <span className="text-emerald-400 font-medium">{normalCount} showed only standard background movement</span>.
          </p>
        </div>

        {/* Quick KPI Stat Pills */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {/* Time Away */}
          <div className="flex flex-col rounded-xl border border-slate-800/80 bg-slate-950/60 p-3">
            <div className="flex items-center gap-1.5 text-xs text-slate-400">
              <Clock className="h-3.5 w-3.5 text-blue-400" />
              <span>Time Away</span>
            </div>
            <span className="mt-1 text-xl font-bold tracking-tight text-white tabular-nums">{elapsedHuman}</span>
          </div>

          {/* Meaningful Changes */}
          <div className="flex flex-col rounded-xl border border-amber-900/40 bg-amber-950/20 p-3">
            <div className="flex items-center gap-1.5 text-xs text-amber-400">
              <TrendingUp className="h-3.5 w-3.5" />
              <span>Meaningful</span>
            </div>
            <span className="mt-1 text-xl font-bold tracking-tight text-amber-300 tabular-nums">
              {meaningfulCount} <span className="text-xs font-normal text-amber-400/80">/ {totalWatched}</span>
            </span>
          </div>

          {/* Needs Attention */}
          <div className="flex flex-col rounded-xl border border-rose-900/40 bg-rose-950/20 p-3">
            <div className="flex items-center gap-1.5 text-xs text-rose-400">
              <AlertTriangle className="h-3.5 w-3.5" />
              <span>Attention</span>
            </div>
            <span className="mt-1 text-xl font-bold tracking-tight text-rose-300 tabular-nums">
              {attentionCount}
            </span>
          </div>

          {/* Normal Movement */}
          <div className="flex flex-col rounded-xl border border-emerald-900/40 bg-emerald-950/20 p-3">
            <div className="flex items-center gap-1.5 text-xs text-emerald-400">
              <ShieldCheck className="h-3.5 w-3.5" />
              <span>Normal Noise</span>
            </div>
            <span className="mt-1 text-xl font-bold tracking-tight text-emerald-300 tabular-nums">
              {normalCount}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
