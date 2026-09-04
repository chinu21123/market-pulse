from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from app.schemas.engine import AttentionScoreBreakdown

class LLMExplanation(BaseModel):
    headline: str
    why_it_matters: str
    key_observation: str

class StockFeedItem(BaseModel):
    symbol: str
    company_name: str
    current_price: float
    snapshot_price: float
    delta_pct: float
    delta_abs: float
    day_pct_change: float
    volume: float
    attention: AttentionScoreBreakdown
    gemini_explanation: Optional[LLMExplanation] = None
    freshness: str
    data_timestamp: str

class DataConfidenceStatus(BaseModel):
    provider: str
    status: str  # LIVE, DELAYED, STALE, CONFLICTING
    confidence_score: int  # 0 to 100
    latency_ms: int
    last_updated: str
    discrepancy_detected: bool = False
    discrepancy_details: Optional[str] = None

class WhileYouWereAwayResponse(BaseModel):
    user_id: str
    last_snapshot_at: Optional[str] = None
    elapsed_minutes: int
    elapsed_human: str
    total_watched: int
    meaningful_count: int
    attention_required_count: int
    normal_count: int
    market_story_headline: str
    market_story_summary: str
    meaningful_stocks: List[StockFeedItem]
    normal_stocks: List[StockFeedItem]
    data_confidence: DataConfidenceStatus
