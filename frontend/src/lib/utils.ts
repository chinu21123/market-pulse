import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";
import { AttentionTier } from "./types";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(amount);
}

export function formatPercent(val: number): string {
  const sign = val > 0 ? '+' : '';
  return `${sign}${val.toFixed(2)}%`;
}

export function formatVolume(num: number): string {
  if (!num || num === 0) return '0';
  if (num >= 1_000_000_000) {
    return `${(num / 1_000_000_000).toFixed(1)}B`;
  }
  if (num >= 1_000_000) {
    return `${(num / 1_000_000).toFixed(1)}M`;
  }
  if (num >= 1_000) {
    return `${(num / 1_000).toFixed(1)}K`;
  }
  return num.toLocaleString();
}

export function getAttentionColor(score: number): {
  bg: string;
  text: string;
  border: string;
  badge: string;
  glow: string;
} {
  if (score <= 30) {
    return {
      bg: 'bg-emerald-950/40',
      text: 'text-emerald-400',
      border: 'border-emerald-800/50',
      badge: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
      glow: 'shadow-emerald-900/20',
    };
  }
  if (score <= 60) {
    return {
      bg: 'bg-amber-950/40',
      text: 'text-amber-400',
      border: 'border-amber-800/50',
      badge: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
      glow: 'shadow-amber-900/20',
    };
  }
  if (score <= 80) {
    return {
      bg: 'bg-orange-950/40',
      text: 'text-orange-400',
      border: 'border-orange-800/50',
      badge: 'bg-orange-500/10 text-orange-400 border-orange-500/30',
      glow: 'shadow-orange-900/30',
    };
  }
  return {
    bg: 'bg-rose-950/40',
    text: 'text-rose-400',
    border: 'border-rose-800/50',
    badge: 'bg-rose-500/10 text-rose-400 border-rose-500/30',
    glow: 'shadow-rose-900/40',
  };
}

export function getAttentionTierLabel(tier: AttentionTier | string): string {
  switch (tier) {
    case 'high_attention':
      return 'High Attention';
    case 'significant':
      return 'Significant';
    case 'worth_watching':
      return 'Worth Watching';
    case 'normal':
    default:
      return 'Normal';
  }
}
