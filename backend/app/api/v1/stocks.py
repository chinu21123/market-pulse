from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.watchlist import WatchlistItem
from app.schemas.engine import WhyNotAlertedProof
from app.services.market_data.yfinance_provider import market_provider
from app.services.engine.scoring import MeaningfulChangeEngine
from app.services.engine.trust_proof import TrustProofEngine
from app.services.memory_service import MarketMemoryService

router = APIRouter(prefix="/stocks", tags=["Stock Details & Trust Proof"])

@router.get("/{symbol}/why-not-alerted", response_model=WhyNotAlertedProof)
def why_not_alerted(
    symbol: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    sym = symbol.upper().strip()
    watched = db.query(WatchlistItem).filter(
        WatchlistItem.user_id == current_user.id,
        WatchlistItem.symbol == sym,
    ).first()
    if not watched:
        raise HTTPException(status_code=404, detail="Stock is not in your watchlist.")
    quote = market_provider.get_quote(sym)
    if not quote:
        raise HTTPException(status_code=404, detail="Stock data not found.")

    latest_snapshot = MarketMemoryService.get_latest_snapshot(current_user.id, db)
    snap_price = quote.price
    if latest_snapshot:
        for s_item in latest_snapshot.items:
            if s_item.symbol == sym:
                snap_price = s_item.price
                break

    benchmark_delta = market_provider.get_benchmark_delta()
    breakdown = MeaningfulChangeEngine.calculate_attention_score(
        current_price=quote.price,
        snapshot_price=snap_price,
        volume=quote.volume,
        avg_volume_20d=quote.avg_volume_20d,
        atr_14d=quote.atr_14d,
        day_high=quote.day_high,
        day_low=quote.day_low,
        benchmark_delta_pct=benchmark_delta,
        user_sensitivity_threshold=current_user.sensitivity_threshold
    )

    proof = TrustProofEngine.generate_proof(
        symbol=sym,
        company_name=quote.company_name,
        breakdown=breakdown,
        current_price=quote.price,
        snapshot_price=snap_price,
        atr_14d=quote.atr_14d,
        volume=quote.volume,
        avg_volume_20d=quote.avg_volume_20d
    )

    return proof
