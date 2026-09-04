'use client';

import React from 'react';
import { useAuth } from '@/lib/auth-context';
import { PersonaLevel } from '@/lib/types';
import { Activity, Clock, RefreshCw, LogOut } from 'lucide-react';

interface NavbarProps {
  lastSnapshotHuman?: string;
  onRefreshFeed: () => void;
  onSaveCheckpoint: () => void;
  isSavingCheckpoint?: boolean;
}

export function Navbar({
  lastSnapshotHuman = 'Recently',
  onRefreshFeed,
  onSaveCheckpoint,
  isSavingCheckpoint = false,
}: NavbarProps) {
  const { user, updatePersona, updateLanguage, logout } = useAuth();

  return (
    <header className="sticky top-0 z-40 w-full border-b border-slate-800/80 bg-[#090d16]/90 backdrop-blur-md">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        {/* Brand */}
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-tr from-blue-600 to-cyan-500 text-white shadow-lg shadow-blue-500/20">
            <Activity className="h-5 w-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-lg font-bold tracking-tight text-white">Market Pulse</span>
            </div>
            <p className="text-[11px] text-slate-400">The watchlist that remembers, understands and keeps working.</p>
          </div>
        </div>

        {/* Center: Market Memory Pill & Demo Simulation */}
        <div className="hidden md:flex items-center gap-2">
          {/* Market Memory Pill */}
          <div className="flex items-center gap-2 rounded-full border border-slate-800 bg-slate-900/80 px-3.5 py-1.5 text-xs text-slate-300">
            <Clock className="h-3.5 w-3.5 text-cyan-400" />
            <span>Memory Checkpoint:</span>
            <span className="font-semibold text-cyan-300">{lastSnapshotHuman}</span>
            <button
              onClick={onSaveCheckpoint}
              disabled={isSavingCheckpoint}
              title="Save current state as new memory checkpoint"
              className="ml-1.5 flex items-center gap-1 rounded bg-slate-800 px-2 py-0.5 text-[11px] font-medium text-slate-200 hover:bg-slate-700 hover:text-white transition disabled:opacity-50"
            >
              <RefreshCw className={`h-3 w-3 ${isSavingCheckpoint ? 'animate-spin text-cyan-400' : ''}`} />
              <span>Snapshot</span>
            </button>
          </div>

        </div>

        {/* Right: Persona & Language & Profile */}
        <div className="flex items-center gap-3">
          {/* Persona Selector */}
          <div className="flex items-center rounded-lg border border-slate-800 bg-slate-900/60 p-0.5">
            {(['beginner', 'intermediate', 'advanced'] as PersonaLevel[]).map((level) => (
              <button
                key={level}
                onClick={() => updatePersona(level)}
                className={`rounded-md px-2.5 py-1 text-xs font-medium capitalize transition ${
                  user?.persona_level === level
                    ? 'bg-blue-600 text-white shadow-sm'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                {level}
              </button>
            ))}
          </div>

          {/* Language Selector */}
          <div className="relative">
            <select
              value={user?.preferred_language || 'en'}
              onChange={(e) => updateLanguage(e.target.value)}
              aria-label="Language selection"
              className="appearance-none rounded-lg border border-slate-800 bg-slate-900/80 px-2.5 py-1.5 pr-6 text-xs text-slate-300 hover:border-slate-700 focus:border-blue-500 focus:outline-none"
            >
              <option value="en">🇺🇸 EN</option>
              <option value="es">🇪🇸 ES</option>
              <option value="fr">🇫🇷 FR</option>
              <option value="hi">🇮🇳 HI</option>
              <option value="zh">🇨🇳 ZH</option>
            </select>
          </div>

          {/* User / Logout */}
          <div className="flex items-center gap-2 border-l border-slate-800 pl-3">
            <div className="hidden lg:flex flex-col text-right">
              <span className="text-xs font-medium text-slate-200">
                {user?.full_name || user?.email?.split('@')[0] || 'Trader'}
              </span>
              <span className="text-[10px] text-slate-400">Personal market view</span>
            </div>
            <button
              onClick={logout}
              title="Logout"
              className="rounded-lg p-2 text-slate-400 hover:bg-slate-800 hover:text-slate-200 transition"
            >
              <LogOut className="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}
