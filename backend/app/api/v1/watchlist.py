from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.watchlist import WatchlistItem
from app.schemas.watchlist import WatchlistAdd, WatchlistItemResponse, StockSearchResult
from app.services.market_data.yfinance_provider import market_provider
from app.services.memory_service import MarketMemoryService

router = APIRouter(prefix="/watchlist", tags=["Watchlist"])

@router.get("", response_model=List[WatchlistItemResponse])
def get_watchlist(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    items = db.query(WatchlistItem).filter(WatchlistItem.user_id == current_user.id).all()
    if not items:
        return []

    symbols = [item.symbol for item in items]
    quotes = market_provider.get_quotes(symbols)

    latest_snapshot = MarketMemoryService.get_latest_snapshot(current_user.id, db)
    snapshot_prices = {}
    if latest_snapshot:
        for s_item in latest_snapshot.items:
            snapshot_prices[s_item.symbol] = s_item.price

    response = []
    for item in items:
        quote = quotes.get(item.symbol)
        snap_price = snapshot_prices.get(item.symbol)
        
        delta_snap_pct = None
        if quote and snap_price and snap_price > 0:
            delta_snap_pct = round(((quote.price - snap_price) / snap_price) * 100.0, 2)

        response.append(WatchlistItemResponse(
            id=item.id,
            symbol=item.symbol,
            company_name=item.company_name or (quote.company_name if quote else item.symbol),
            exchange=item.exchange or "US",
            current_price=quote.price if quote else None,
            pct_change_24h=quote.change_pct if quote else None,
            volume=quote.volume if quote else None,
            snapshot_price=snap_price,
            delta_since_snapshot_pct=delta_snap_pct,
            freshness=quote.freshness if quote else "LIVE",
            data_timestamp=quote.market_timestamp.isoformat() if quote else None,
            created_at=item.created_at
        ))

    return response

@router.post("", response_model=WatchlistItemResponse)
def add_to_watchlist(
    payload: WatchlistAdd,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    sym = payload.symbol.upper().strip()
    if not sym:
        raise HTTPException(status_code=400, detail="Symbol cannot be empty.")

    # Check if already added
    existing = db.query(WatchlistItem).filter(
        WatchlistItem.user_id == current_user.id,
        WatchlistItem.symbol == sym
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"{sym} is already in your watchlist.")

    quote = market_provider.get_quote(sym)
    company_name = quote.company_name if quote else sym

    item = WatchlistItem(
        user_id=current_user.id,
        symbol=sym,
        company_name=company_name,
        exchange="US"
    )
    db.add(item)
    db.commit()
    db.refresh(item)

    return WatchlistItemResponse(
        id=item.id,
        symbol=item.symbol,
        company_name=item.company_name,
        exchange=item.exchange,
        current_price=quote.price if quote else None,
        pct_change_24h=quote.change_pct if quote else None,
        volume=quote.volume if quote else None,
        snapshot_price=quote.price if quote else None,
        delta_since_snapshot_pct=0.0,
        freshness=quote.freshness if quote else "LIVE",
        data_timestamp=quote.market_timestamp.isoformat() if quote else None,
        created_at=item.created_at
    )

@router.delete("/{symbol}", status_code=status.HTTP_204_NO_CONTENT)
def remove_from_watchlist(
    symbol: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    sym = symbol.upper().strip()
    item = db.query(WatchlistItem).filter(
        WatchlistItem.user_id == current_user.id,
        WatchlistItem.symbol == sym
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Symbol not found in watchlist.")

    db.delete(item)
    db.commit()
    return None

@router.get("/search", response_model=List[StockSearchResult])
def search_stocks(q: str = ""):
    results = market_provider.search_symbols(q)
    return [
        StockSearchResult(
            symbol=r["symbol"],
            name=r["name"],
            exchange=r.get("exchange", "US"),
            type=r.get("type", "EQUITY")
        )
        for r in results
    ]
