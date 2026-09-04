from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

class SnapshotCreate(BaseModel):
    trigger_type: Optional[str] = "manual"  # manual, session_exit, simulated
    notes: Optional[str] = None

class SnapshotItemSummary(BaseModel):
    symbol: str
    price: float
    volume: Optional[float] = None
    market_timestamp: Optional[datetime] = None
    freshness: str = "LIVE"

class SnapshotResponse(BaseModel):
    id: str
    user_id: str
    trigger_type: str
    captured_at: datetime
    notes: Optional[str] = None
    item_count: int
    items: Optional[List[SnapshotItemSummary]] = None

    model_config = {"from_attributes": True}

class SimulateAwayRequest(BaseModel):
    minutes_away: int = 263  # 4h 23m by default
    scenario: Optional[str] = "tech_divergence"  # tech_divergence, calm_market, high_volatility
