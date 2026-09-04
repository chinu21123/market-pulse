import React from 'react';
import { getAttentionColor, getAttentionTierLabel } from '@/lib/utils';
import { AttentionTier } from '@/lib/types';

interface AttentionScoreBadgeProps {
  score: number;
  classification: AttentionTier | string;
  size?: 'sm' | 'md' | 'lg';
}

export function AttentionScoreBadge({
  score,
  classification,
  size = 'md',
}: AttentionScoreBadgeProps) {
  const colors = getAttentionColor(score);
  const tierLabel = getAttentionTierLabel(classification);

  const sizeClasses = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-2.5 py-1 text-xs',
    lg: 'px-3.5 py-1.5 text-sm font-semibold',
  };

  return (
    <div
      className={`inline-flex items-center gap-1.5 rounded-full border ${colors.badge} ${sizeClasses[size]} backdrop-blur-sm shadow-sm ${colors.glow}`}
    >
      <span className="font-bold tabular-nums">{score}</span>
      <span className="text-[10px] opacity-60">/100</span>
      <span className="h-1 w-1 rounded-full bg-current opacity-70" />
      <span className="font-medium">{tierLabel}</span>
    </div>
  );
}
