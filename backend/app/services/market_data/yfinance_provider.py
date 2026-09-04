import time
import logging
from typing import Dict, List, Optional
from datetime import datetime, timezone
import yfinance as yf
import pandas as pd
import numpy as np

from app.services.market_data.base import MarketDataProvider, MarketQuote
from app.services.market_data.confidence import evaluate_data_freshness

logger = logging.getLogger(__name__)

POPULAR_STOCKS = [
    {"symbol": "NVDA", "name": "NVIDIA Corporation", "exchange": "NASDAQ", "type": "EQUITY"},
    {"symbol": "AAPL", "name": "Apple Inc.", "exchange": "NASDAQ", "type": "EQUITY"},
    {"symbol": "MSFT", "name": "Microsoft Corporation", "exchange": "NASDAQ", "type": "EQUITY"},
    {"symbol": "AMZN", "name": "Amazon.com, Inc.", "exchange": "NASDAQ", "type": "EQUITY"},
    {"symbol": "GOOGL", "name": "Alphabet Inc.", "exchange": "NASDAQ", "type": "EQUITY"},
    {"symbol": "TSLA", "name": "Tesla, Inc.", "exchange": "NASDAQ", "type": "EQUITY"},
    {"symbol": "META", "name": "Meta Platforms, Inc.", "exchange": "NASDAQ", "type": "EQUITY"},
    {"symbol": "AMD", "name": "Advanced Micro Devices, Inc.", "exchange": "NASDAQ", "type": "EQUITY"},
    {"symbol": "NFLX", "name": "Netflix, Inc.", "exchange": "NASDAQ", "type": "EQUITY"},
    {"symbol": "SPY", "name": "SPDR S&P 500 ETF Trust", "exchange": "NYSE Arca", "type": "ETF"},
    {"symbol": "QQQ", "name": "Invesco QQQ Trust", "exchange": "NASDAQ", "type": "ETF"},
    {"symbol": "JPM", "name": "JPMorgan Chase & Co.", "exchange": "NYSE", "type": "EQUITY"},
    {"symbol": "V", "name": "Visa Inc.", "exchange": "NYSE", "type": "EQUITY"},
    {"symbol": "WMT", "name": "Walmart Inc.", "exchange": "NYSE", "type": "EQUITY"},
    {"symbol": "DIS", "name": "The Walt Disney Company", "exchange": "NYSE", "type": "EQUITY"},
]

class YFinanceProvider(MarketDataProvider):
    def __init__(self, cache_ttl_seconds: int = 30):
        self.cache_ttl = cache_ttl_seconds
        self._cache: Dict[str, Dict] = {}  # symbol -> { "quote": MarketQuote, "timestamp": float }
        self._benchmark_cache: Optional[Dict] = None

    def _get_from_cache(self, symbol: str) -> Optional[MarketQuote]:
        now = time.time()
        cached = self._cache.get(symbol.upper())
        if cached and (now - cached["timestamp"] < self.cache_ttl):
            return cached["quote"]
        return None

    def _get_cached_any(self, symbol: str) -> Optional[MarketQuote]:
        cached = self._cache.get(symbol.upper())
        return cached["quote"] if cached else None

    def _save_to_cache(self, quote: MarketQuote):
        self._cache[quote.symbol.upper()] = {
            "quote": quote,
            "timestamp": time.time()
        }

    def _compute_atr(self, df: pd.DataFrame, period: int = 14) -> float:
        """Calculate 14-day Average True Range (ATR)."""
        if len(df) < 2:
            return 1.0
        high = df['High'].values
        low = df['Low'].values
        close = df['Close'].values
        
        tr_list = []
        for i in range(1, len(df)):
            tr = max(
                high[i] - low[i],
                abs(high[i] - close[i - 1]),
                abs(low[i] - close[i - 1])
            )
            tr_list.append(tr)
        
        if not tr_list:
            return 1.0
        atr_window = tr_list[-min(period, len(tr_list)):]
        return float(np.mean(atr_window))

    def get_quote(self, symbol: str) -> Optional[MarketQuote]:
        symbol = symbol.upper().strip()
        cached = self._get_from_cache(symbol)
        if cached:
            return cached

        quotes = self.get_quotes([symbol])
        return quotes.get(symbol)

    def get_quotes(self, symbols: List[str]) -> Dict[str, MarketQuote]:
        symbols = [s.upper().strip() for s in symbols if s.strip()]
        result: Dict[str, MarketQuote] = {}
        missing: List[str] = []
        stale_cache: Dict[str, MarketQuote] = {}

        for s in symbols:
            cached = self._get_from_cache(s)
            if cached:
                result[s] = cached
            else:
                missing.append(s)
                previous = self._get_cached_any(s)
                if previous:
                    stale_cache[s] = previous

        if not missing:
            return result

        try:
            # Batch fetch historical candles with bounded retries.
            tickers_str = " ".join(missing)
            data = None
            last_error = None
            for attempt in range(3):
                try:
                    data = yf.download(
                        tickers_str,
                        period="1mo",
                        interval="1d",
                        group_by="ticker",
                        auto_adjust=True,
                        progress=False,
                        timeout=10,
                    )
                    break
                except Exception as error:
                    last_error = error
                    logger.warning("Market data attempt %s failed: %s", attempt + 1, error)
                    if attempt < 2:
                        time.sleep(0.25 * (2 ** attempt))
            if data is None:
                raise RuntimeError(f"Market data unavailable after retries: {last_error}")
            
            for sym in missing:
                try:
                    if len(missing) == 1:
                        df = data
                    else:
                        df = data[sym] if sym in data else pd.DataFrame()

                    if isinstance(df, pd.DataFrame) and isinstance(df.columns, pd.MultiIndex):
                        for level in range(df.columns.nlevels):
                            if sym in df.columns.get_level_values(level):
                                df = df.xs(sym, axis=1, level=level, drop_level=True)
                                break

                    if df.empty or len(df.dropna()) < 2:
                        # Fallback to single ticker info
                        ticker = yf.Ticker(sym)
                        info = ticker.fast_info
                        price = float(getattr(info, 'last_price', 0) or 0)
                        if price <= 0:
                            raise ValueError("Provider returned an impossible price")
                        prev_close = float(getattr(info, 'previous_close', price) or price)
                        day_high = float(getattr(info, 'day_high', price) or price)
                        day_low = float(getattr(info, 'day_low', price) or price)
                        volume = float(getattr(info, 'last_volume', 1000000) or 1000000)
                        avg_vol = float(getattr(info, 'three_month_average_volume', volume) or volume)
                        atr = max(0.5, price * 0.02)
                    else:
                        df_clean = df.dropna()
                        latest_row = df_clean.iloc[-1]
                        prev_row = df_clean.iloc[-2] if len(df_clean) > 1 else latest_row
                        
                        price = float(latest_row['Close'])
                        prev_close = float(prev_row['Close'])
                        day_high = float(latest_row['High'])
                        day_low = float(latest_row['Low'])
                        volume = float(latest_row['Volume'])
                        
                        vol_window = df_clean['Volume'].tail(20)
                        avg_vol = float(vol_window.mean()) if not vol_window.empty else volume
                        atr = self._compute_atr(df_clean, period=14)

                    change_abs = price - prev_close
                    change_pct = (change_abs / prev_close * 100.0) if prev_close != 0 else 0.0

                    if not all(np.isfinite(value) for value in [price, prev_close, day_high, day_low, volume, avg_vol, atr]):
                        raise ValueError("Provider returned non-finite market data")
                    if min(price, prev_close, day_high, day_low, volume, avg_vol, atr) < 0 or day_high < day_low:
                        raise ValueError("Provider returned invalid market data")

                    now_utc = datetime.now(timezone.utc)
                    freshness, conf_score, _ = evaluate_data_freshness(now_utc)

                    # Lookup readable company name
                    comp_name = sym
                    for stock in POPULAR_STOCKS:
                        if stock["symbol"] == sym:
                            comp_name = stock["name"]
                            break

                    quote = MarketQuote(
                        symbol=sym,
                        company_name=comp_name,
                        price=round(price, 2),
                        prev_close=round(prev_close, 2),
                        change_pct=round(change_pct, 2),
                        change_abs=round(change_abs, 2),
                        volume=round(volume, 0),
                        avg_volume_20d=round(avg_vol, 0),
                        day_high=round(day_high, 2),
                        day_low=round(day_low, 2),
                        atr_14d=round(atr, 2),
                        market_timestamp=now_utc,
                        data_source="yfinance",
                        freshness=freshness,
                        confidence_score=conf_score
                    )
                    self._save_to_cache(quote)
                    result[sym] = quote

                except Exception as e:
                    logger.error(f"Error parsing market data for {sym}: {e}")
                    previous = stale_cache.get(sym)
                    if previous:
                        result[sym] = previous.model_copy(update={
                            "freshness": "STALE",
                            "confidence_score": 40,
                        })

        except Exception as batch_err:
            logger.error(f"Batch yfinance download error: {batch_err}")
            for sym, previous in stale_cache.items():
                result[sym] = previous.model_copy(update={
                    "freshness": "STALE",
                    "confidence_score": 40,
                })

        return result

    def search_symbols(self, query: str) -> List[dict]:
        q = query.strip().upper()
        if not q:
            return POPULAR_STOCKS[:6]

        matches = []
        for stock in POPULAR_STOCKS:
            if q in stock["symbol"] or q in stock["name"].upper():
                matches.append(stock)

        # If not matched in catalog, offer query as a valid ticker symbol
        if not any(m["symbol"] == q for m in matches):
            matches.insert(0, {
                "symbol": q,
                "name": f"{q} Ticker",
                "exchange": "US",
                "type": "EQUITY"
            })

        return matches[:8]

    def get_benchmark_delta(self) -> float:
        """Returns SPY % change as market benchmark."""
        now = time.time()
        if self._benchmark_cache and (now - self._benchmark_cache["timestamp"] < 120):
            return self._benchmark_cache["delta"]

        try:
            spy_quote = self.get_quote("SPY")
            delta = spy_quote.change_pct if spy_quote else 0.0
        except Exception:
            delta = 0.0

        self._benchmark_cache = {"delta": delta, "timestamp": now}
        return delta

market_provider = YFinanceProvider()
