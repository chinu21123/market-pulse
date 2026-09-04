from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class WatchlistAdd(BaseModel):
    symbol: str

class WatchlistItemResponse(BaseModel):
    id: str
    symbol: str
    company_name: Optional[str] = None
    exchange: Optional[str] = None
    current_price: Optional[float] = None
    pct_change_24h: Optional[float] = None
    volume: Optional[float] = None
    snapshot_price: Optional[float] = None
    delta_since_snapshot_pct: Optional[float] = None
    freshness: str = "LIVE"
    data_timestamp: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}

class StockSearchResult(BaseModel):
    symbol: str
    name: str
    exchange: Optional[str] = None
    type: Optional[str] = "EQUITY"
