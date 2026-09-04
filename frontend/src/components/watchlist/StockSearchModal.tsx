'use client';

import React, { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { StockSearchResult } from '@/lib/types';
import { Search, Plus, X, Check, RefreshCw } from 'lucide-react';

interface StockSearchModalProps {
  isOpen: boolean;
  onClose: () => void;
  onStockAdded: () => void;
  existingSymbols: string[];
}

export function StockSearchModal({
  isOpen,
  onClose,
  onStockAdded,
  existingSymbols,
}: StockSearchModalProps) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<StockSearchResult[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [isAdding, setIsAdding] = useState<string | null>(null);

  useEffect(() => {
    if (!isOpen) return;

    const timer = setTimeout(() => {
      setIsSearching(true);
      api.watchlist
        .search(query)
        .then((data) => {
          setResults(data);
          setIsSearching(false);
        })
        .catch(() => setIsSearching(false));
    }, 250);

    return () => clearTimeout(timer);
  }, [query, isOpen]);

  if (!isOpen) return null;

  const handleAdd = async (symbol: string) => {
    setIsAdding(symbol);
    try {
      await api.watchlist.add(symbol);
      onStockAdded();
      onClose();
    } catch (err: any) {
      alert(err.message || 'Could not add stock');
    } finally {
      setIsAdding(null);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-sm p-4">
      <div className="relative w-full max-w-md rounded-2xl border border-slate-800 bg-[#0c121e] p-6 shadow-2xl">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 rounded-lg p-1.5 text-slate-400 hover:bg-slate-800 hover:text-white transition"
        >
          <X className="h-5 w-5" />
        </button>

        <h3 className="text-lg font-bold text-white">Add Stock to Watchlist</h3>
        <p className="text-xs text-slate-400 mt-0.5">Search by ticker symbol or company name</p>

        {/* Input */}
        <div className="mt-4 relative">
          <Search className="absolute left-3.5 top-3 h-4 w-4 text-slate-400" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="e.g. NVDA, AAPL, MSFT, TSLA..."
            autoFocus
            className="w-full rounded-xl border border-slate-800 bg-slate-900/90 pl-10 pr-4 py-2.5 text-sm text-white placeholder-slate-500 focus:border-blue-500 focus:outline-none"
          />
        </div>

        {/* Results List */}
        <div className="mt-4 max-h-60 overflow-y-auto space-y-1.5 pr-1">
          {isSearching ? (
            <div className="flex items-center justify-center py-8 text-xs text-slate-400 gap-2">
              <RefreshCw className="h-3.5 w-3.5 animate-spin text-blue-400" />
              <span>Searching market catalog...</span>
            </div>
          ) : results.length === 0 ? (
            <div className="text-center py-6 text-xs text-slate-400">
              No ticker matching "{query}". Try a major symbol like AAPL, NVDA, or TSLA.
            </div>
          ) : (
            results.map((stock) => {
              const isAlreadyAdded = existingSymbols.includes(stock.symbol.toUpperCase());
              return (
                <div
                  key={stock.symbol}
                  className="flex items-center justify-between rounded-xl border border-slate-800/60 bg-slate-900/40 p-3 hover:bg-slate-800/60 transition"
                >
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-sm text-white">{stock.symbol}</span>
                      <span className="text-[10px] text-slate-400 font-mono px-1.5 py-0.5 rounded bg-slate-800">
                        {stock.exchange}
                      </span>
                    </div>
                    <p className="text-xs text-slate-400 truncate max-w-[220px]">{stock.name}</p>
                  </div>

                  {isAlreadyAdded ? (
                    <span className="flex items-center gap-1 text-[11px] text-emerald-400 font-medium px-2 py-1 rounded bg-emerald-500/10 border border-emerald-500/20">
                      <Check className="h-3 w-3" />
                      Watched
                    </span>
                  ) : (
                    <button
                      onClick={() => handleAdd(stock.symbol)}
                      disabled={isAdding === stock.symbol}
                      className="flex items-center gap-1 rounded-lg bg-blue-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-blue-500 transition disabled:opacity-50"
                    >
                      {isAdding === stock.symbol ? (
                        <RefreshCw className="h-3.5 w-3.5 animate-spin" />
                      ) : (
                        <Plus className="h-3.5 w-3.5" />
                      )}
                      <span>Add</span>
                    </button>
                  )}
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
}
