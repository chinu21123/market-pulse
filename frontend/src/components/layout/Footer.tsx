import React from 'react';
import { DataConfidenceStatus } from '@/lib/types';
import { ShieldCheck, AlertCircle, Database, CheckCircle } from 'lucide-react';
import { SystemStatus } from './SystemStatus';

interface FooterProps {
  confidence?: DataConfidenceStatus;
}

export function Footer({ confidence }: FooterProps) {
  const isLive = confidence?.status === 'LIVE';

  return (
    <footer className="mt-12 border-t border-slate-800/80 bg-[#070b13] py-6 text-xs text-slate-400">
      <div className="mx-auto flex max-w-7xl flex-col items-center justify-between gap-4 px-4 sm:flex-row sm:px-6 lg:px-8">
        <div className="flex items-center gap-2">
          <span className="font-semibold text-slate-300">Market Pulse</span>
          <span className="italic text-slate-400">"Show users what deserves their attention."</span>
        </div>

        {/* Data Confidence Strip */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5 rounded-full border border-slate-800 bg-slate-900/60 px-3 py-1">
            <span
              className={`h-2 w-2 rounded-full ${
                isLive ? 'bg-emerald-400 animate-pulse' : 'bg-amber-400'
              }`}
            />
            <span className="font-semibold text-slate-200">
              {confidence?.status || 'LIVE'}
            </span>
            <span className="text-slate-400">
              ({confidence?.confidence_score ?? 100}% Confidence)
            </span>
          </div>

          <div className="hidden sm:flex items-center gap-1 text-slate-400">
            <Database className="h-3.5 w-3.5 text-blue-400" />
            <span>Source: {confidence?.provider || 'Yahoo Finance'}</span>
          </div>
          <SystemStatus />
        </div>
      </div>
    </footer>
  );
}
