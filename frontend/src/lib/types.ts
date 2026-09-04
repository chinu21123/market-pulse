export type PersonaLevel = 'beginner' | 'intermediate' | 'advanced';
export type AttentionTier = 'normal' | 'worth_watching' | 'significant' | 'high_attention';

export interface User {
  id: string;
  email: string;
  full_name?: string;
  persona_level: PersonaLevel;
  preferred_language: string;
  sensitivity_threshold: number;
  last_active_at?: string;
  created_at: string;
}

export interface FactorItem {
  name: string;
  label: string;
  weight: number;
  raw_value: number;
  factor_score: number;
  weighted_score: number;
  description: string;
}

export interface AttentionScoreBreakdown {
  total_score: number;
  classification: AttentionTier;
  threshold: number;
  is_meaningful: boolean;
  factors: Record<string, FactorItem>;
}

export interface LLMExplanation {
  headline: string;
  why_it_matters: string;
  key_observation: string;
}

export interface StockFeedItem {
  symbol: string;
  company_name: string;
  current_price: number;
  snapshot_price: number;
  delta_pct: number;
  delta_abs: number;
  day_pct_change: number;
  volume: number;
  attention: AttentionScoreBreakdown;
  gemini_explanation?: LLMExplanation;
  freshness: string;
  data_timestamp: string;
}

export interface DataConfidenceStatus {
  provider: string;
  status: 'LIVE' | 'DELAYED' | 'STALE';
  confidence_score: number;
  latency_ms: number;
  last_updated: string;
  discrepancy_detected: boolean;
  discrepancy_details?: string;
}

export interface WhileYouWereAwayResponse {
  user_id: string;
  last_snapshot_at?: string;
  elapsed_minutes: number;
  elapsed_human: string;
  total_watched: number;
  meaningful_count: number;
  attention_required_count: number;
  normal_count: number;
  market_story_headline: string;
  market_story_summary: string;
  meaningful_stocks: StockFeedItem[];
  normal_stocks: StockFeedItem[];
  data_confidence: DataConfidenceStatus;
}

export interface WhyNotAlertedProof {
  symbol: string;
  company_name: string;
  attention_score: number;
  threshold: number;
  price_delta_pct: number;
  expected_volatility_pct: number;
  volume_ratio: number;
  z_score: number;
  reasons: string[];
  verdict: string;
}

export interface WatchlistItem {
  id: string;
  symbol: string;
  company_name?: string;
  exchange?: string;
  current_price?: number;
  pct_change_24h?: number;
  volume?: number;
  snapshot_price?: number;
  delta_since_snapshot_pct?: number;
  freshness: string;
  data_timestamp?: string;
  created_at: string;
}

export interface StockSearchResult {
  symbol: string;
  name: string;
  exchange?: string;
  type?: string;
}
