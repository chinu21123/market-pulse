'use client';

import React, { useEffect, useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth-context';
import { api } from '@/lib/api';
import { WhileYouWereAwayResponse, StockFeedItem } from '@/lib/types';
import { Navbar } from '@/components/layout/Navbar';
import { Footer } from '@/components/layout/Footer';
import { TimeAwayBanner } from '@/components/away-hero/TimeAwayBanner';
import { MarketStoryCard } from '@/components/away-hero/MarketStoryCard';
import { FlaggedStockCard } from '@/components/away-hero/FlaggedStockCard';
import { WatchlistTable } from '@/components/watchlist/WatchlistTable';
import { StockSearchModal } from '@/components/watchlist/StockSearchModal';
import { WhyNotAlertedModal } from '@/components/trust/WhyNotAlertedModal';
import {
  AlertTriangle,
  Eye,
  ShieldCheck,
  ListFilter,
  Plus,
  RefreshCw,
  Sparkles,
} from 'lucide-react';

export default function DashboardPage() {
  const { user, isLoading: authLoading } = useAuth();
  const router = useRouter();
  const [feed, setFeed] = useState<WhileYouWereAwayResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'attention' | 'watching' | 'normal' | 'all'>('attention');

  // Modals
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [inspectSymbol, setInspectSymbol] = useState<string | null>(null);
  const [isSavingCheckpoint, setIsSavingCheckpoint] = useState(false);

  const fetchFeed = useCallback(async () => {
    setIsLoading(true);
    try {
      const data = await api.feed.getWhileYouWereAway();
      setFeed(data);
    } catch (err) {
      console.error('Failed to fetch While You Were Away feed:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    if (!authLoading && !user) {
      router.replace('/login');
    } else if (!authLoading && user) {
      fetchFeed();
    }
  }, [authLoading, user, fetchFeed, router]);

  if (!authLoading && !user) {
    return <div className="flex min-h-screen items-center justify-center bg-[#070b13] text-sm text-slate-400">Redirecting to sign in...</div>;
  }

  const handleSaveCheckpoint = async () => {
    setIsSavingCheckpoint(true);
    try {
      await api.memory.saveCheckpoint('Manual user checkpoint');
      await fetchFeed();
    } catch (err) {
      console.error('Error saving checkpoint:', err);
    } finally {
      setIsSavingCheckpoint(false);
    }
  };

  const handleRemoveStock = async (symbol: string) => {
    try {
      await api.watchlist.remove(symbol);
      await fetchFeed();
    } catch (err) {
      console.error('Error removing stock:', err);
    }
  };

  if (authLoading || (isLoading && !feed)) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center bg-[#070b13] text-white">
        <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-blue-600/20 text-blue-400 border border-blue-500/30">
          <RefreshCw className="h-6 w-6 animate-spin text-blue-400" />
        </div>
        <p className="mt-4 text-sm font-medium text-slate-300">
          Retrieving Market Memory & Calculating Meaningful Changes...
        </p>
        <p className="mt-1 text-xs text-slate-400">Comparing current prices against your last snapshot</p>
      </div>
    );
  }

  // Filter stocks based on activeTab
  const allStocks = [...(feed?.meaningful_stocks || []), ...(feed?.normal_stocks || [])];
  const urgentAttentionStocks = feed?.meaningful_stocks.filter(
    (s) => s.attention.classification === 'significant' || s.attention.classification === 'high_attention'
  ) || [];
  const worthWatchingStocks = feed?.meaningful_stocks.filter(
    (s) => s.attention.classification === 'worth_watching'
  ) || [];
  const normalStocks = feed?.normal_stocks || [];

  return (
    <div className="min-h-screen bg-[#070b13] flex flex-col justify-between">
      <div>
        <Navbar
          lastSnapshotHuman={feed?.elapsed_human ? `${feed.elapsed_human} ago` : 'Recently'}
          onRefreshFeed={fetchFeed}
          onSaveCheckpoint={handleSaveCheckpoint}
          isSavingCheckpoint={isSavingCheckpoint}
        />

        <main className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 pt-6 pb-12 space-y-6">
          {/* Hero: While You Were Away Banner */}
          <TimeAwayBanner
            elapsedHuman={feed?.elapsed_human || '0m'}
            totalWatched={feed?.total_watched || 0}
            meaningfulCount={feed?.meaningful_count || 0}
            attentionCount={feed?.attention_required_count || 0}
            normalCount={feed?.normal_count || 0}
            lastSnapshotAt={feed?.last_snapshot_at}
          />

          {/* Gemini AI Market Story Narrative */}
          <MarketStoryCard
            headline={feed?.market_story_headline || 'Market Pulse Summary'}
            summary={feed?.market_story_summary || 'No meaningful changes detected.'}
            elapsedHuman={feed?.elapsed_human || 'recently'}
            meaningfulStocks={feed?.meaningful_stocks || []}
          />

          {/* Main Content Area: Attention Tabs & Watchlist */}
          <div className="space-y-4">
            {/* Tab Controls & Add Stock Button */}
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 border-b border-slate-800 pb-3">
              <div className="flex flex-wrap items-center gap-1.5">
                <button
                  onClick={() => setActiveTab('attention')}
                  className={`flex items-center gap-2 rounded-xl px-3.5 py-2 text-xs font-semibold transition ${
                    activeTab === 'attention'
                      ? 'bg-rose-500/10 border border-rose-500/30 text-rose-300'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  <AlertTriangle className="h-3.5 w-3.5" />
                  <span>Needs Attention</span>
                  <span className="rounded-full bg-rose-500/20 px-1.5 py-0.2 text-[10px] font-mono text-rose-400">
                    {urgentAttentionStocks.length}
                  </span>
                </button>

                <button
                  onClick={() => setActiveTab('watching')}
                  className={`flex items-center gap-2 rounded-xl px-3.5 py-2 text-xs font-semibold transition ${
                    activeTab === 'watching'
                      ? 'bg-amber-500/10 border border-amber-500/30 text-amber-300'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  <Eye className="h-3.5 w-3.5" />
                  <span>Worth Watching</span>
                  <span className="rounded-full bg-amber-500/20 px-1.5 py-0.2 text-[10px] font-mono text-amber-400">
                    {worthWatchingStocks.length}
                  </span>
                </button>

                <button
                  onClick={() => setActiveTab('normal')}
                  className={`flex items-center gap-2 rounded-xl px-3.5 py-2 text-xs font-semibold transition ${
                    activeTab === 'normal'
                      ? 'bg-emerald-500/10 border border-emerald-500/30 text-emerald-300'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  <ShieldCheck className="h-3.5 w-3.5" />
                  <span>Normal Movement</span>
                  <span className="rounded-full bg-emerald-500/20 px-1.5 py-0.2 text-[10px] font-mono text-emerald-400">
                    {normalStocks.length}
                  </span>
                </button>

                <button
                  onClick={() => setActiveTab('all')}
                  className={`flex items-center gap-2 rounded-xl px-3.5 py-2 text-xs font-semibold transition ${
                    activeTab === 'all'
                      ? 'bg-slate-800 border border-slate-700 text-white'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  <ListFilter className="h-3.5 w-3.5" />
                  <span>All Stocks ({allStocks.length})</span>
                </button>
              </div>

              {/* Action: Add Stock */}
              <button
                onClick={() => setIsSearchOpen(true)}
                className="flex items-center gap-1.5 rounded-xl bg-blue-600 px-3.5 py-2 text-xs font-semibold text-white hover:bg-blue-500 transition shadow-sm shadow-blue-500/20"
              >
                <Plus className="h-3.5 w-3.5" />
                <span>Add Stock</span>
              </button>
            </div>

            {/* Tab 1: Needs Attention */}
            {activeTab === 'attention' && (
              <div className="space-y-4">
                {urgentAttentionStocks.length === 0 ? (
                  <div className="rounded-2xl border border-slate-800 bg-slate-900/30 p-8 text-center">
                    <ShieldCheck className="mx-auto h-8 w-8 text-emerald-400" />
                    <h3 className="mt-2 text-sm font-semibold text-white">All Clear</h3>
                    <p className="mt-1 text-xs text-slate-400">
                      No stocks crossed your high attention threshold while you were away.
                    </p>
                  </div>
                ) : (
                  urgentAttentionStocks.map((stock) => (
                    <FlaggedStockCard key={stock.symbol} stock={stock} />
                  ))
                )}
              </div>
            )}

            {/* Tab 2: Worth Watching */}
            {activeTab === 'watching' && (
              <div className="space-y-4">
                {worthWatchingStocks.length === 0 ? (
                  <div className="rounded-2xl border border-slate-800 bg-slate-900/30 p-8 text-center">
                    <p className="text-sm text-slate-400">No stocks in the Worth Watching tier.</p>
                  </div>
                ) : (
                  worthWatchingStocks.map((stock) => (
                    <FlaggedStockCard key={stock.symbol} stock={stock} />
                  ))
                )}
              </div>
            )}

            {/* Tab 3: Normal Movement (with "Why wasn't I alerted?") */}
            {activeTab === 'normal' && (
              <div className="space-y-3">
                <div className="rounded-xl border border-emerald-900/30 bg-emerald-950/10 p-3.5 text-xs text-slate-300 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <ShieldCheck className="h-4 w-4 text-emerald-400 flex-shrink-0" />
                    <span>
                      These {normalStocks.length} stocks stayed within statistical volatility bounds. Click <strong>"Why wasn't I alerted?"</strong> to inspect the exact mathematical audit.
                    </span>
                  </div>
                </div>

                <WatchlistTable
                  stocks={normalStocks}
                  onRemove={handleRemoveStock}
                  onInspectWhyNotAlerted={(sym) => setInspectSymbol(sym)}
                />
              </div>
            )}

            {/* Tab 4: All Stocks Table */}
            {activeTab === 'all' && (
              <WatchlistTable
                stocks={allStocks}
                onRemove={handleRemoveStock}
                onInspectWhyNotAlerted={(sym) => setInspectSymbol(sym)}
              />
            )}
          </div>
        </main>
      </div>

      <Footer confidence={feed?.data_confidence} />

      {/* Modals */}
      <StockSearchModal
        isOpen={isSearchOpen}
        onClose={() => setIsSearchOpen(false)}
        onStockAdded={fetchFeed}
        existingSymbols={allStocks.map((s) => s.symbol)}
      />


      <WhyNotAlertedModal
        symbol={inspectSymbol}
        onClose={() => setInspectSymbol(null)}
      />
    </div>
  );
}
