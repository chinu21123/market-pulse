import React, { useState } from 'react';
import { StockFeedItem } from '@/lib/types';
import { formatCurrency, formatPercent, formatVolume } from '@/lib/utils';
import { AttentionScoreBadge } from './AttentionScoreBadge';
import { FactorBreakdownBar } from '../trust/FactorBreakdownBar';
import { Sparkles, TrendingUp, TrendingDown, ChevronDown, ChevronUp, Clock, AlertCircle } from 'lucide-react';

interface FlaggedStockCardProps {
  stock: StockFeedItem;
}

export function FlaggedStockCard({ stock }: FlaggedStockCardProps) {
  const [showDetails, setShowDetails] = useState(false);
  const isPositive = stock.delta_pct >= 0;

  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5 shadow-lg hover:border-slate-700 transition duration-200">
      {/* Top row: Symbol, prices, and Attention Badge */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="flex items-center gap-3">
            <h3 className="text-xl font-bold text-white tracking-tight">{stock.symbol}</h3>
            <span className="text-xs text-slate-400 font-medium truncate max-w-[200px]">
              {stock.company_name}
            </span>
            <span className="rounded bg-slate-800 px-1.5 py-0.5 text-[10px] font-mono text-slate-300">
              {stock.freshness}
            </span>
          </div>

          <div className="mt-2 flex items-baseline gap-3">
            <span className="text-2xl font-extrabold text-white tabular-nums">
              {formatCurrency(stock.current_price)}
            </span>

            {/* Delta since last snapshot */}
            <div
              className={`flex items-center gap-1 text-sm font-bold ${
                isPositive ? 'text-emerald-400' : 'text-rose-400'
              }`}
            >
              {isPositive ? <TrendingUp className="h-4 w-4" /> : <TrendingDown className="h-4 w-4" />}
              <span>{formatPercent(stock.delta_pct)}</span>
              <span className="text-xs font-normal opacity-80">
                ({isPositive ? '+' : ''}{formatCurrency(stock.delta_abs)})
              </span>
            </div>

            <span className="text-xs text-slate-400">since last check</span>
          </div>
        </div>

        {/* Attention Score Badge & Baseline Snapshot */}
        <div className="flex flex-col sm:items-end gap-2">
          <AttentionScoreBadge
            score={stock.attention.total_score}
            classification={stock.attention.classification}
            size="lg"
          />

          <div className="text-xs text-slate-400 font-mono">
            Checkpoint Price: <span className="text-slate-300">{formatCurrency(stock.snapshot_price)}</span>
          </div>
        </div>
      </div>

      {/* Gemini AI explanation box */}
      {stock.gemini_explanation ? (
        <div className="mt-4 rounded-xl border border-blue-900/40 bg-gradient-to-r from-blue-950/30 to-slate-900/40 p-3.5">
          <div className="flex items-center gap-2 text-xs font-semibold text-blue-400">
            <Sparkles className="h-3.5 w-3.5" />
            <span>Why This Deserves Attention</span>
          </div>

          <h4 className="mt-1 text-sm font-semibold text-slate-100">
            {stock.gemini_explanation.headline}
          </h4>

          <p className="mt-1 text-xs text-slate-300 leading-relaxed">
            {stock.gemini_explanation.why_it_matters}
          </p>

          <div className="mt-2 text-[11px] font-medium text-cyan-300/90 border-t border-blue-900/30 pt-1.5 flex items-center gap-1.5">
            <span className="font-semibold text-slate-400">Key Takeaway:</span>
            <span>{stock.gemini_explanation.key_observation}</span>
          </div>
        </div>
      ) : (
        <div className="mt-4 rounded-xl border border-slate-800 bg-slate-900/40 p-3 text-xs text-slate-400">
          Composite score reached {stock.attention.total_score}/100 based on quantitative factor expansion.
        </div>
      )}

      {/* Collapsible Factor Breakdown */}
      <div className="mt-4 border-t border-slate-800/80 pt-3">
        <button
          onClick={() => setShowDetails(!showDetails)}
          className="flex w-full items-center justify-between text-xs font-medium text-slate-400 hover:text-slate-200 transition"
        >
          <span>Inspection: 5-Factor Quantitative Breakdown</span>
          {showDetails ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
        </button>

        {showDetails && (
          <div className="mt-3">
            <FactorBreakdownBar factors={stock.attention.factors} />
          </div>
        )}
      </div>
    </div>
  );
}
