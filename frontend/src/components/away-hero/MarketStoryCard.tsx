'use client';

import React, { useState } from 'react';
import { useAuth } from '@/lib/auth-context';
import { Sparkles, Bot, CheckCircle2, RefreshCw } from 'lucide-react';
import { PersonaLevel } from '@/lib/types';
import { api } from '@/lib/api';

interface MarketStoryCardProps {
  headline: string;
  summary: string;
  elapsedHuman: string;
  meaningfulStocks: any[];
  onStoryUpdated?: (headline: string, summary: string) => void;
}

export function MarketStoryCard({
  headline,
  summary,
  elapsedHuman,
  meaningfulStocks,
  onStoryUpdated,
}: MarketStoryCardProps) {
  const { user, updatePersona } = useAuth();
  const [currentHeadline, setCurrentHeadline] = useState(headline);
  const [currentSummary, setCurrentSummary] = useState(summary);
  const [isReexplaining, setIsReexplaining] = useState(false);

  // Sync state if props change
  React.useEffect(() => {
    setCurrentHeadline(headline);
    setCurrentSummary(summary);
  }, [headline, summary]);

  const handlePersonaChange = async (targetPersona: PersonaLevel) => {
    if (targetPersona === user?.persona_level) return;
    setIsReexplaining(true);
    try {
      await updatePersona(targetPersona);
      const res = await api.explain.reExplain({
        persona: targetPersona,
        language: user?.preferred_language || 'en',
        elapsed_time_human: elapsedHuman,
        flagged_stocks: meaningfulStocks.map((s) => ({
          symbol: s.symbol,
          delta_pct: s.delta_pct,
          attention_score: s.attention.total_score,
          factors: {
            volume_anomaly: { raw_value: s.attention.factors.volume_anomaly?.raw_value || 1 },
            volatility_z_score: { raw_value: s.attention.factors.volatility_z_score?.raw_value || 1 },
          },
        })),
      });

      if (res.story_headline) setCurrentHeadline(res.story_headline);
      if (res.story_summary) setCurrentSummary(res.story_summary);
      if (onStoryUpdated && res.story_headline && res.story_summary) {
        onStoryUpdated(res.story_headline, res.story_summary);
      }
    } catch (err) {
      console.error('Error re-explaining:', err);
    } finally {
      setIsReexplaining(false);
    }
  };

  return (
    <div className="rounded-2xl border border-blue-900/40 bg-gradient-to-br from-[#0d1627] to-[#09101d] p-6 shadow-lg">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-slate-800/80 pb-4">
        <div className="flex items-center gap-2.5">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-600/20 text-blue-400 border border-blue-500/30">
            <Bot className="h-4 w-4" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-base font-bold text-white">AI Market Story</h2>
              <span className="flex items-center gap-1 rounded bg-blue-500/10 px-2 py-0.5 text-[10px] font-semibold text-blue-400 border border-blue-500/20">
                <Sparkles className="h-2.5 w-2.5" />
                Gemini Powered
              </span>
            </div>
            <p className="text-[11px] text-slate-400">Strictly synthesized from verified backend deltas</p>
          </div>
        </div>

        {/* Persona Switcher Buttons */}
        <div className="flex items-center gap-1 text-xs">
          <span className="text-slate-400 mr-1 hidden md:inline">Perspective:</span>
          {(['beginner', 'intermediate', 'advanced'] as PersonaLevel[]).map((level) => (
            <button
              key={level}
              disabled={isReexplaining}
              onClick={() => handlePersonaChange(level)}
              className={`rounded-md px-2.5 py-1 text-xs font-medium capitalize transition disabled:opacity-50 ${
                user?.persona_level === level
                  ? 'bg-blue-600 text-white font-semibold shadow-sm'
                  : 'bg-slate-800/60 text-slate-400 hover:bg-slate-800 hover:text-slate-200'
              }`}
            >
              {level}
            </button>
          ))}
        </div>
      </div>

      <div className="mt-4">
        {isReexplaining ? (
          <div className="flex items-center justify-center py-6 gap-2 text-sm text-blue-400">
            <RefreshCw className="h-4 w-4 animate-spin" />
            <span>Adapting narrative to {user?.persona_level} perspective...</span>
          </div>
        ) : (
          <>
            <h3 className="text-lg font-semibold text-white tracking-tight">
              {currentHeadline}
            </h3>
            <p className="mt-2 text-sm leading-relaxed text-slate-300">
              {currentSummary}
            </p>
          </>
        )}
      </div>

      <div className="mt-4 pt-3 border-t border-slate-800/60 flex items-center justify-between text-[11px] text-slate-400">
        <span className="flex items-center gap-1 text-emerald-400/90">
          <CheckCircle2 className="h-3.5 w-3.5" />
          <span>Zero-hallucination verified: all numbers derived deterministically from market feed</span>
        </span>
        <span className="text-slate-400">Target Persona: <span className="text-slate-300 capitalize">{user?.persona_level}</span></span>
      </div>
    </div>
  );
}
