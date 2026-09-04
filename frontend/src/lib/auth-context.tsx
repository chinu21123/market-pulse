'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';
import { User, PersonaLevel } from './types';
import { api } from './api';

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  login: (email: string, pass: string) => Promise<void>;
  register: (email: string, pass: string, name?: string, persona?: PersonaLevel) => Promise<void>;
  logout: () => void;
  updatePersona: (level: PersonaLevel) => Promise<void>;
  updateLanguage: (lang: string) => Promise<void>;
  updateThreshold: (threshold: number) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    async function initAuth() {
      const token = localStorage.getItem('market_pulse_token');
      if (token) {
        try {
          const profile = await api.auth.getMe();
          setUser(profile);
          setIsLoading(false);
          return;
        } catch {
          localStorage.removeItem('market_pulse_token');
        }
      }

      setIsLoading(false);
    }

    initAuth();
  }, []);

  const login = async (email: string, pass: string) => {
    setIsLoading(true);
    try {
      const res = await api.auth.login({ email, password: pass });
      localStorage.setItem('market_pulse_token', res.access_token);
      setUser(res.user);
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (email: string, pass: string, name?: string, persona: PersonaLevel = 'intermediate') => {
    setIsLoading(true);
    try {
      const res = await api.auth.register({
        email,
        password: pass,
        full_name: name,
        persona_level: persona,
      });
      localStorage.setItem('market_pulse_token', res.access_token);
      setUser(res.user);
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('market_pulse_token');
    setUser(null);
  };

  const updatePersona = async (level: PersonaLevel) => {
    if (!user) return;
    const updated = await api.auth.updatePreferences({ persona_level: level });
    setUser(updated);
  };

  const updateLanguage = async (lang: string) => {
    if (!user) return;
    const updated = await api.auth.updatePreferences({ preferred_language: lang });
    setUser(updated);
  };

  const updateThreshold = async (threshold: number) => {
    if (!user) return;
    const updated = await api.auth.updatePreferences({ sensitivity_threshold: threshold });
    setUser(updated);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        login,
        register,
        logout,
        updatePersona,
        updateLanguage,
        updateThreshold,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
