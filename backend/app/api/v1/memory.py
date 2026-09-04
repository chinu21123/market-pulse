from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.memory import SnapshotCreate, SnapshotResponse, SnapshotItemSummary, SimulateAwayRequest
from app.services.memory_service import MarketMemoryService

router = APIRouter(prefix="/memory", tags=["Market Memory"])

@router.post("/checkpoint", response_model=SnapshotResponse)
def save_checkpoint(
    payload: SnapshotCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    snapshot = MarketMemoryService.capture_snapshot(
        user_id=current_user.id,
        db=db,
        trigger_type=payload.trigger_type or "manual",
        notes=payload.notes
    )
    items_summary = [
        SnapshotItemSummary(
            symbol=it.symbol,
            price=it.price,
            volume=it.volume,
            market_timestamp=it.market_timestamp,
            freshness=it.freshness
        )
        for it in snapshot.items
    ]
    return SnapshotResponse(
        id=snapshot.id,
        user_id=snapshot.user_id,
        trigger_type=snapshot.trigger_type,
        captured_at=snapshot.captured_at,
        notes=snapshot.notes,
        item_count=len(snapshot.items),
        items=items_summary
    )

@router.get("/latest", response_model=SnapshotResponse)
def get_latest_checkpoint(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    snapshot = MarketMemoryService.get_latest_snapshot(current_user.id, db)
    if not snapshot:
        # Create an initial one
        snapshot = MarketMemoryService.capture_snapshot(
            user_id=current_user.id,
            db=db,
            trigger_type="initial_baseline",
            notes="Auto-created baseline checkpoint"
        )

    items_summary = [
        SnapshotItemSummary(
            symbol=it.symbol,
            price=it.price,
            volume=it.volume,
            market_timestamp=it.market_timestamp,
            freshness=it.freshness
        )
        for it in snapshot.items
    ]
    return SnapshotResponse(
        id=snapshot.id,
        user_id=snapshot.user_id,
        trigger_type=snapshot.trigger_type,
        captured_at=snapshot.captured_at,
        notes=snapshot.notes,
        item_count=len(snapshot.items),
        items=items_summary
    )

@router.post("/simulate-away", response_model=SnapshotResponse)
def simulate_time_away(
    payload: SimulateAwayRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Hackathon demo accelerator: simulates that the user was away for X minutes
    with a calibrated market move scenario (e.g. 'tech_divergence').
    """
    snapshot = MarketMemoryService.simulate_away(
        user_id=current_user.id,
        db=db,
        minutes_away=payload.minutes_away,
        scenario=payload.scenario or "tech_divergence"
    )
    items_summary = [
        SnapshotItemSummary(
            symbol=it.symbol,
            price=it.price,
            volume=it.volume,
            market_timestamp=it.market_timestamp,
            freshness=it.freshness
        )
        for it in snapshot.items
    ]
    return SnapshotResponse(
        id=snapshot.id,
        user_id=snapshot.user_id,
        trigger_type=snapshot.trigger_type,
        captured_at=snapshot.captured_at,
        notes=snapshot.notes,
        item_count=len(snapshot.items),
        items=items_summary
    )
