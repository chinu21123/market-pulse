from datetime import datetime, timezone
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.watchlist import WatchlistItem
from app.services.market_data.yfinance_provider import market_provider
from app.services.market_data.confidence import build_confidence_report
from app.services.engine.scoring import MeaningfulChangeEngine
from app.services.engine.trust_proof import TrustProofEngine
from app.services.memory_service import MarketMemoryService
from app.services.intelligence.gemini_client import gemini_service
from app.schemas.feed import (
    WhileYouWereAwayResponse,
    StockFeedItem,
    LLMExplanation,
    DataConfidenceStatus
)
from app.core.health import health_registry

class FeedService:
    @staticmethod
    def get_while_you_were_away_feed(user: User, db: Session) -> WhileYouWereAwayResponse:
        """
        Executes the full Market Memory + Meaningful Change + AI Intelligence pipeline.
        """
        now_utc = datetime.now(timezone.utc)
        
        # 1. Fetch user's watched items
        watched_items = db.query(WatchlistItem).filter(WatchlistItem.user_id == user.id).all()
        if not watched_items:
            # Seed default demo stocks if user has none
            default_stocks = [
                ("NVDA", "NVIDIA Corporation"),
                ("AAPL", "Apple Inc."),
                ("TSLA", "Tesla, Inc."),
                ("MSFT", "Microsoft Corporation"),
                ("AMD", "Advanced Micro Devices, Inc.")
            ]
            for s, n in default_stocks:
                db.add(WatchlistItem(user_id=user.id, symbol=s, company_name=n, exchange="NASDAQ"))
            db.commit()
            watched_items = db.query(WatchlistItem).filter(WatchlistItem.user_id == user.id).all()

        symbols = [item.symbol for item in watched_items]

        # 2. Get latest snapshot or capture one if none exists
        latest_snapshot = MarketMemoryService.get_latest_snapshot(user.id, db)
        if not latest_snapshot:
            # Automatically create first baseline snapshot
            latest_snapshot = MarketMemoryService.capture_snapshot(
                user_id=user.id,
                db=db,
                trigger_type="initial_baseline",
                notes="Initial baseline snapshot upon registration"
            )

        # 3. Calculate elapsed time
        snap_time = latest_snapshot.captured_at
        if snap_time.tzinfo is None:
            snap_time = snap_time.replace(tzinfo=timezone.utc)

        elapsed_seconds = max(0, (now_utc - snap_time).total_seconds())
        elapsed_minutes = int(elapsed_seconds / 60)
        
        hours = elapsed_minutes // 60
        mins = elapsed_minutes % 60
        if hours > 0:
            elapsed_human = f"{hours}h {mins}m"
        else:
            elapsed_human = f"{mins}m"

        # 4. Map snapshot prices by symbol
        snapshot_prices: Dict[str, float] = {}
        for item in latest_snapshot.items:
            snapshot_prices[item.symbol] = item.price

        # 5. Fetch fresh live quotes
        quotes = market_provider.get_quotes(symbols)
        if quotes:
            health_registry.mark("market_data", "HEALTHY")
        else:
            health_registry.mark("market_data", "DEGRADED", "No verified quotes were available")
        benchmark_delta = market_provider.get_benchmark_delta()

        # 6. Run Meaningful Change Engine on each stock
        meaningful_items: List[StockFeedItem] = []
        normal_items: List[StockFeedItem] = []
        flagged_facts_for_llm: List[Dict[str, Any]] = []

        for item in watched_items:
            quote = quotes.get(item.symbol)
            if not quote:
                continue

            snap_price = snapshot_prices.get(item.symbol, quote.price)
            if snap_price <= 0:
                snap_price = quote.price

            delta_pct = ((quote.price - snap_price) / snap_price) * 100.0
            delta_abs = quote.price - snap_price

            # Deterministic scoring
            attention_breakdown = MeaningfulChangeEngine.calculate_attention_score(
                current_price=quote.price,
                snapshot_price=snap_price,
                volume=quote.volume,
                avg_volume_20d=quote.avg_volume_20d,
                atr_14d=quote.atr_14d,
                day_high=quote.day_high,
                day_low=quote.day_low,
                benchmark_delta_pct=benchmark_delta,
                user_sensitivity_threshold=user.sensitivity_threshold
            )

            feed_item = StockFeedItem(
                symbol=item.symbol,
                company_name=item.company_name or item.symbol,
                current_price=quote.price,
                snapshot_price=snap_price,
                delta_pct=round(delta_pct, 2),
                delta_abs=round(delta_abs, 2),
                day_pct_change=quote.change_pct,
                volume=quote.volume,
                attention=attention_breakdown,
                freshness=quote.freshness,
                data_timestamp=quote.market_timestamp.isoformat()
            )

            if attention_breakdown.is_meaningful:
                meaningful_items.append(feed_item)
                # Prepare verified facts for Gemini
                factor_dict = {
                    k: {"raw_value": v.raw_value, "score": v.factor_score}
                    for k, v in attention_breakdown.factors.items()
                }
                flagged_facts_for_llm.append({
                    "symbol": item.symbol,
                    "company_name": item.company_name or item.symbol,
                    "snapshot_price": snap_price,
                    "current_price": quote.price,
                    "delta_pct": round(delta_pct, 2),
                    "attention_score": attention_breakdown.total_score,
                    "classification": attention_breakdown.classification,
                    "factors": factor_dict
                })
            else:
                normal_items.append(feed_item)

        # Sort meaningful stocks by attention score descending
        meaningful_items.sort(key=lambda x: x.attention.total_score, reverse=True)
        # Sort normal items by absolute change ascending
        normal_items.sort(key=lambda x: abs(x.delta_pct))

        total_watched = len(symbols)
        meaningful_count = len(meaningful_items)
        attention_count = sum(1 for x in meaningful_items if x.attention.classification in ["significant", "high_attention"])
        normal_count = len(normal_items)

        # 7. Generate Gemini Market Narrative using verified facts only
        story_result = gemini_service.generate_story(
            elapsed_time_human=elapsed_human,
            total_watched=total_watched,
            meaningful_count=meaningful_count,
            attention_count=attention_count,
            normal_count=normal_count,
            persona=user.persona_level,
            language=user.preferred_language,
            flagged_stocks=flagged_facts_for_llm
        )

        headline = story_result.get("story_headline", "Market Pulse Report")
        summary = story_result.get("story_summary", f"Summary for your {elapsed_human} away.")

        # Attach explanations to individual stock feed items
        explanations_map = {
            exp["symbol"]: exp
            for exp in story_result.get("stock_explanations", [])
            if "symbol" in exp
        }
        for item in meaningful_items:
            if item.symbol in explanations_map:
                exp_data = explanations_map[item.symbol]
                item.gemini_explanation = LLMExplanation(
                    headline=exp_data.get("headline", ""),
                    why_it_matters=exp_data.get("why_it_matters", ""),
                    key_observation=exp_data.get("key_observation", "")
                )

        # 8. Data confidence status
        confidence = build_confidence_report("Yahoo Finance Engine", latest_timestamp=now_utc)

        return WhileYouWereAwayResponse(
            user_id=user.id,
            last_snapshot_at=snap_time.isoformat(),
            elapsed_minutes=elapsed_minutes,
            elapsed_human=elapsed_human,
            total_watched=total_watched,
            meaningful_count=meaningful_count,
            attention_required_count=attention_count,
            normal_count=normal_count,
            market_story_headline=headline,
            market_story_summary=summary,
            meaningful_stocks=meaningful_items,
            normal_stocks=normal_items,
            data_confidence=confidence
        )
