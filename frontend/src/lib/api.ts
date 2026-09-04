import {
  User,
  WhileYouWereAwayResponse,
  WhyNotAlertedProof,
  WatchlistItem,
  StockSearchResult,
  PersonaLevel
} from './types';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000/api/v1';
const SERVER_BASE = API_BASE.replace(/\/api\/v1\/?$/, '');

function getAuthHeader(): Record<string, string> {
  if (typeof window === 'undefined') return {};
  const token = localStorage.getItem('market_pulse_token');
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const url = path.startsWith('http') ? path : `${API_BASE}${path}`;
  const headers = {
    'Content-Type': 'application/json',
    ...getAuthHeader(),
    ...options.headers,
  };

  const response = await fetch(url, { ...options, headers });
  
  if (!response.ok) {
    let errorMsg = `HTTP Error ${response.status}`;
    try {
      const errorData = await response.json();
      errorMsg = errorData.detail || errorMsg;
    } catch {
      // ignore json parse error
    }
    throw new Error(errorMsg);
  }

  if (response.status === 204) {
    return {} as T;
  }

  return response.json();
}

export const api = {
  health: {
    get: () => request<{ status: string; dependencies: Record<string, { status: string; detail?: string }> }>(`${SERVER_BASE}/health/dependencies`),
  },
  auth: {
    login: (payload: { email: string; password: string }) =>
      request<{ access_token: string; token_type: string; user: User }>('/auth/login', {
        method: 'POST',
        body: JSON.stringify(payload),
      }),
    register: (payload: { email: string; password: string; full_name?: string; persona_level?: string }) =>
      request<{ access_token: string; token_type: string; user: User }>('/auth/register', {
        method: 'POST',
        body: JSON.stringify(payload),
      }),
    getMe: () => request<User>('/auth/me'),
    updatePreferences: (payload: { persona_level?: PersonaLevel; preferred_language?: string; sensitivity_threshold?: number }) =>
      request<User>('/auth/preferences', {
        method: 'PATCH',
        body: JSON.stringify(payload),
      }),
  },
  watchlist: {
    getAll: () => request<WatchlistItem[]>('/watchlist'),
    add: (symbol: string) =>
      request<WatchlistItem>('/watchlist', {
        method: 'POST',
        body: JSON.stringify({ symbol }),
      }),
    remove: (symbol: string) =>
      request<void>(`/watchlist/${encodeURIComponent(symbol)}`, {
        method: 'DELETE',
      }),
    search: (query: string) =>
      request<StockSearchResult[]>(`/watchlist/search?q=${encodeURIComponent(query)}`),
  },
  memory: {
    saveCheckpoint: (notes?: string) =>
      request<any>('/memory/checkpoint', {
        method: 'POST',
        body: JSON.stringify({ trigger_type: 'manual', notes }),
      }),
    getLatest: () => request<any>('/memory/latest'),
    simulateAway: (minutes_away: number, scenario: string = 'tech_divergence') =>
      request<any>('/memory/simulate-away', {
        method: 'POST',
        body: JSON.stringify({ minutes_away, scenario }),
      }),
  },
  feed: {
    getWhileYouWereAway: () => request<WhileYouWereAwayResponse>('/feed/while-you-were-away'),
  },
  stocks: {
    getWhyNotAlerted: (symbol: string) =>
      request<WhyNotAlertedProof>(`/stocks/${encodeURIComponent(symbol)}/why-not-alerted`),
  },
  explain: {
    reExplain: (payload: {
      persona: string;
      language: string;
      elapsed_time_human: string;
      flagged_stocks: any[];
    }) =>
      request<any>('/explain/re-explain', {
        method: 'POST',
        body: JSON.stringify(payload),
      }),
  },
};
