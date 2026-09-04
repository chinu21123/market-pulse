'use client';

import React, { useEffect, useState } from 'react';
import { CheckCircle2, AlertTriangle } from 'lucide-react';
import { api } from '@/lib/api';

export function SystemStatus() {
  const [status, setStatus] = useState<'HEALTHY' | 'DEGRADED'>('HEALTHY');
  const [details, setDetails] = useState<Record<string, { status: string; detail?: string }>>({});

  useEffect(() => {
    let active = true;
    api.health.get().then((result) => {
      if (active) {
        setStatus(result.status === 'HEALTHY' ? 'HEALTHY' : 'DEGRADED');
        setDetails(result.dependencies);
      }
    }).catch(() => active && setStatus('DEGRADED'));
    return () => { active = false; };
  }, []);

  const marketStatus = details.market_data?.status === 'HEALTHY' ? 'LIVE' : 'DELAYED';
  const aiStatus = details.gemini?.status === 'HEALTHY' ? 'AVAILABLE' : 'FALLBACK';

  return (
    <details className="relative text-[11px]">
      <summary className="flex cursor-pointer list-none items-center gap-1.5 text-slate-400 hover:text-slate-200">
        {status === 'HEALTHY' ? <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" /> : <AlertTriangle className="h-3.5 w-3.5 text-amber-400" />}
        <span>{status === 'HEALTHY' ? 'All systems operational' : 'Some services are degraded'}</span>
      </summary>
      <div className="absolute bottom-6 right-0 z-50 w-52 rounded-xl border border-slate-700 bg-[#0c121e] p-3 shadow-xl">
        <p className="mb-2 font-semibold text-slate-200">System status</p>
        <p className="flex justify-between text-slate-400"><span>Market data</span><span className="text-slate-200">{marketStatus}</span></p>
        <p className="mt-1 flex justify-between text-slate-400"><span>AI insights</span><span className="text-slate-200">{aiStatus}</span></p>
        <p className="mt-1 flex justify-between text-slate-400"><span>Database</span><span className="text-slate-200">{details.database?.status || 'HEALTHY'}</span></p>
      </div>
    </details>
  );
}
