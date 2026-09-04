import React from 'react';
import { FactorItem } from '@/lib/types';

interface FactorBreakdownBarProps {
  factors: Record<string, FactorItem>;
}

export function FactorBreakdownBar({ factors }: FactorBreakdownBarProps) {
  const factorList = Object.values(factors);

  const getScoreColor = (score: number) => {
    if (score <= 30) return 'bg-emerald-500';
    if (score <= 60) return 'bg-amber-500';
    if (score <= 80) return 'bg-orange-500';
    return 'bg-rose-500';
  };

  return (
    <div className="space-y-2.5">
      <div className="flex items-center justify-between text-xs font-semibold text-slate-300">
        <span>Deterministic Scoring Signals</span>
        <span className="text-[11px] text-slate-400 font-normal">Weight-Adjusted</span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-2">
        {factorList.map((factor) => {
          const barColor = getScoreColor(factor.factor_score);

          return (
            <div
              key={factor.name}
              className="flex flex-col justify-between rounded-lg border border-slate-800/80 bg-slate-900/50 p-2.5"
            >
              <div>
                <div className="flex items-center justify-between text-[11px]">
                  <span className="font-medium text-slate-300 truncate" title={factor.label}>
                    {factor.label}
                  </span>
                  <span className="text-slate-400 font-mono text-[10px]">
                    {(factor.weight * 100).toFixed(0)}%
                  </span>
                </div>

                {/* Progress bar */}
                <div className="mt-2 h-1.5 w-full overflow-hidden rounded-full bg-slate-800">
                  <div
                    className={`h-full ${barColor} transition-all duration-500`}
                    style={{ width: `${Math.min(100, Math.max(5, factor.factor_score))}%` }}
                  />
                </div>
              </div>

              <div className="mt-2 flex items-baseline justify-between text-[11px]">
                <span className="font-mono text-slate-200 font-medium">
                  {typeof factor.raw_value === 'number' ? factor.raw_value : factor.raw_value}
                </span>
                <span className="text-[10px] text-slate-400 font-mono">
                  Score: {factor.factor_score}
                </span>
              </div>

              <p className="mt-1 text-[10px] text-slate-400 line-clamp-1" title={factor.description}>
                {factor.description}
              </p>
            </div>
          );
        })}
      </div>
    </div>
  );
}
