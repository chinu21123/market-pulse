'use client';

import React from 'react';
import { StockFeedItem } from '@/lib/types';
import { formatCurrency, formatPercent } from '@/lib/utils';
import { AttentionScoreBadge } from '../away-hero/AttentionScoreBadge';
import { Trash2, HelpCircle, TrendingUp, TrendingDown } from 'lucide-react';

interface WatchlistTableProps {
  stocks: StockFeedItem[];
  onRemove: (symbol: string) => void;
  onInspectWhyNotAlerted: (symbol: string) => void;
}

export function WatchlistTable({
  stocks,
  onRemove,
  onInspectWhyNotAlerted,
}: WatchlistTableProps) {
  if (stocks.length === 0) {
    return (
      <div className="rounded-2xl border border-slate-800 bg-slate-900/40 p-8 text-center">
        <p className="text-sm text-slate-400">No stocks in this category.</p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto rounded-2xl border border-slate-800 bg-slate-900/50 shadow-md">
      <table className="w-full text-left text-sm">
        <thead className="border-b border-slate-800 bg-slate-950/60 text-xs font-semibold uppercase tracking-wider text-slate-400">
          <tr>
            <th className="py-3.5 px-4">Asset</th>
            <th className="py-3.5 px-4">Live Price</th>
            <th className="py-3.5 px-4">Since Last Check</th>
            <th className="py-3.5 px-4">Today's Total</th>
            <th className="py-3.5 px-4">Attention Score</th>
            <th className="py-3.5 px-4 text-right">Actions</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-800/60 text-slate-200">
          {stocks.map((stock) => {
            const isSnapPositive = stock.delta_pct >= 0;
            const isDayPositive = stock.day_pct_change >= 0;

            return (
              <tr key={stock.symbol} className="hover:bg-slate-800/40 transition">
                {/* Asset */}
                <td className="py-3.5 px-4">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-white">{stock.symbol}</span>
                    <span className="text-xs text-slate-400 truncate max-w-[140px]">
                      {stock.company_name}
                    </span>
                    <span className="text-[9px] font-mono px-1 py-0.2 rounded bg-slate-800 text-slate-400">
                      {stock.freshness}
                    </span>
                  </div>
                </td>

                {/* Live Price */}
                <td className="py-3.5 px-4 font-mono font-semibold text-white tabular-nums">
                  {formatCurrency(stock.current_price)}
                </td>

                {/* Since Last Check */}
                <td className="py-3.5 px-4 font-mono tabular-nums">
                  <div
                    className={`inline-flex items-center gap-1 font-semibold ${
                      isSnapPositive ? 'text-emerald-400' : 'text-rose-400'
                    }`}
                  >
                    {isSnapPositive ? (
                      <TrendingUp className="h-3.5 w-3.5" />
                    ) : (
                      <TrendingDown className="h-3.5 w-3.5" />
                    )}
                    <span>{formatPercent(stock.delta_pct)}</span>
                  </div>
                  <div className="text-[11px] text-slate-400">
                    from {formatCurrency(stock.snapshot_price)}
                  </div>
                </td>

                {/* Today's Total */}
                <td className="py-3.5 px-4 font-mono tabular-nums text-xs">
                  <span className={isDayPositive ? 'text-emerald-400' : 'text-rose-400'}>
                    {formatPercent(stock.day_pct_change)}
                  </span>
                </td>

                {/* Attention Score */}
                <td className="py-3.5 px-4">
                  <AttentionScoreBadge
                    score={stock.attention.total_score}
                    classification={stock.attention.classification}
                    size="sm"
                  />
                </td>

                {/* Actions */}
                <td className="py-3.5 px-4 text-right">
                  <div className="flex items-center justify-end gap-2">
                    {/* "Why Wasn't I Alerted?" button for normal stocks */}
                    {stock.attention.classification === 'normal' && (
                      <button
                        onClick={() => onInspectWhyNotAlerted(stock.symbol)}
                        className="inline-flex items-center gap-1 rounded-lg border border-emerald-500/30 bg-emerald-500/10 px-2.5 py-1 text-xs font-medium text-emerald-300 hover:bg-emerald-500/20 transition"
                        title="Inspect why this movement was classified as normal noise"
                      >
                        <HelpCircle className="h-3.5 w-3.5" />
                        <span>Why wasn't I alerted?</span>
                      </button>
                    )}

                    {/* Delete button */}
                    <button
                      onClick={() => onRemove(stock.symbol)}
                      className="rounded-lg p-1.5 text-slate-400 hover:bg-rose-950/40 hover:text-rose-400 transition"
                      title="Remove from watchlist"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
