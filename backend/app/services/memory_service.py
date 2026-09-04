from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict
from sqlalchemy.orm import Session

from app.models.snapshot import WatchlistSnapshot, SnapshotItem
from app.models.watchlist import WatchlistItem
from app.services.market_data.yfinance_provider import market_provider

class MarketMemoryService:
    @staticmethod
    def capture_snapshot(
        user_id: str,
        db: Session,
        trigger_type: str = "manual",
        notes: Optional[str] = None
    ) -> WatchlistSnapshot:
        """Captures the current market state for all items in the user's watchlist."""
        watched_items = db.query(WatchlistItem).filter(WatchlistItem.user_id == user_id).all()
        now_utc = datetime.now(timezone.utc)

        snapshot = WatchlistSnapshot(
            user_id=user_id,
            trigger_type=trigger_type,
            captured_at=now_utc,
            notes=notes
        )
        db.add(snapshot)
        db.flush()  # to obtain snapshot.id

        if watched_items:
            symbols = [item.symbol for item in watched_items]
            quotes = market_provider.get_quotes(symbols)

            for item in watched_items:
                quote = quotes.get(item.symbol)
                if quote:
                    snap_item = SnapshotItem(
                        snapshot_id=snapshot.id,
                        symbol=item.symbol,
                        price=quote.price,
                        volume=quote.volume,
                        avg_volume_20d=quote.avg_volume_20d,
                        day_high=quote.day_high,
                        day_low=quote.day_low,
                        atr_14d=quote.atr_14d,
                        market_timestamp=quote.market_timestamp,
                        data_source=quote.data_source,
                        freshness=quote.freshness
                    )
                    db.add(snap_item)

        db.commit()
        db.refresh(snapshot)
        return snapshot

    @staticmethod
    def get_latest_snapshot(user_id: str, db: Session) -> Optional[WatchlistSnapshot]:
        """Retrieves the user's most recent snapshot."""
        return (
            db.query(WatchlistSnapshot)
            .filter(WatchlistSnapshot.user_id == user_id)
            .order_by(WatchlistSnapshot.captured_at.desc())
            .first()
        )

    @staticmethod
    def simulate_away(
        user_id: str,
        db: Session,
        minutes_away: int = 263,
        scenario: str = "tech_divergence"
    ) -> WatchlistSnapshot:
        """
        Creates a calibrated historical snapshot from `minutes_away` minutes ago.
        This provides an instant, reproducible demonstration of Market Memory
        for hackathon presentations and judges.
        """
        watched_items = db.query(WatchlistItem).filter(WatchlistItem.user_id == user_id).all()
        if not watched_items:
            # Seed default demo stocks if user watchlist is empty
            default_symbols = [
                ("NVDA", "NVIDIA Corporation"),
                ("AAPL", "Apple Inc."),
                ("TSLA", "Tesla, Inc."),
                ("MSFT", "Microsoft Corporation"),
                ("AMD", "Advanced Micro Devices, Inc.")
            ]
            for sym, comp in default_symbols:
                item = WatchlistItem(user_id=user_id, symbol=sym, company_name=comp, exchange="NASDAQ")
                db.add(item)
            db.commit()
            watched_items = db.query(WatchlistItem).filter(WatchlistItem.user_id == user_id).all()

        symbols = [item.symbol for item in watched_items]
        quotes = market_provider.get_quotes(symbols)

        simulated_time = datetime.now(timezone.utc) - timedelta(minutes=minutes_away)
        snapshot = WatchlistSnapshot(
            user_id=user_id,
            trigger_type="simulated",
            captured_at=simulated_time,
            notes=f"Simulated {minutes_away} minutes away ({scenario})"
        )
        db.add(snapshot)
        db.flush()

        # Define simulated delta offsets based on scenario
        delta_map: Dict[str, float] = {}
        if scenario == "tech_divergence":
            delta_map = {
                "NVDA": -0.058,  # Price was 5.8% lower, so it surged +6.1% since then!
                "TSLA": 0.042,   # Price was 4.2% higher, so it fell -4.0% since then!
                "AMD": -0.035,   # Price was 3.5% lower, so it surged +3.6%
                "AAPL": 0.003,   # Baseline noise (+0.3%)
                "MSFT": -0.002,  # Baseline noise (-0.2%)
            }
        elif scenario == "high_volatility":
            delta_map = {s: (-0.05 if i % 2 == 0 else 0.05) for i, s in enumerate(symbols)}
        else:
            delta_map = {s: 0.001 for s in symbols}

        for item in watched_items:
            quote = quotes.get(item.symbol)
            if quote:
                offset = delta_map.get(item.symbol, 0.002)
                base_price = round(quote.price * (1.0 + offset), 2)
                snap_item = SnapshotItem(
                    snapshot_id=snapshot.id,
                    symbol=item.symbol,
                    price=base_price,
                    volume=round(quote.volume * 0.4, 0),
                    avg_volume_20d=quote.avg_volume_20d,
                    day_high=round(base_price * 1.01, 2),
                    day_low=round(base_price * 0.99, 2),
                    atr_14d=quote.atr_14d,
                    market_timestamp=simulated_time,
                    data_source="yfinance_simulated",
                    freshness="LIVE"
                )
                db.add(snap_item)

        db.commit()
        db.refresh(snapshot)
        return snapshot
