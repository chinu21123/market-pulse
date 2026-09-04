from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel

class MarketQuote(BaseModel):
    symbol: str
    company_name: str
    price: float
    prev_close: float
    change_pct: float
    change_abs: float
    volume: float
    avg_volume_20d: float
    day_high: float
    day_low: float
    atr_14d: float
    market_timestamp: datetime
    data_source: str = "yfinance"
    freshness: str = "LIVE"  # LIVE, DELAYED, STALE, CONFLICTING
    confidence_score: int = 100

class MarketDataProvider(ABC):
    @abstractmethod
    def get_quote(self, symbol: str) -> Optional[MarketQuote]:
        """Fetch quote and metrics for a single symbol."""
        pass

    @abstractmethod
    def get_quotes(self, symbols: List[str]) -> Dict[str, MarketQuote]:
        """Fetch quotes and metrics for multiple symbols."""
        pass

    @abstractmethod
    def search_symbols(self, query: str) -> List[dict]:
        """Search ticker symbols by query."""
        pass

    @abstractmethod
    def get_benchmark_delta(self) -> float:
        """Get benchmark (e.g. SPY) percentage change."""
        pass
