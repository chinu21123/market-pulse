from typing import Dict, Any, List, Optional
from pydantic import BaseModel

class FactorItem(BaseModel):
    name: str
    label: str
    weight: float
    raw_value: float
    factor_score: float  # 0 to 100
    weighted_score: float
    description: str

class AttentionScoreBreakdown(BaseModel):
    total_score: int  # 0 to 100
    classification: str  # normal, worth_watching, significant, high_attention
    threshold: int
    is_meaningful: bool
    factors: Dict[str, FactorItem]

class WhyNotAlertedProof(BaseModel):
    symbol: str
    company_name: str
    attention_score: int
    threshold: int
    price_delta_pct: float
    expected_volatility_pct: float
    volume_ratio: float
    z_score: float
    reasons: List[str]
    verdict: str
