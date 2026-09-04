import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.core.database import Base

class WatchlistSnapshot(Base):
    __tablename__ = "market_snapshots"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    trigger_type = Column(String(30), default="manual", nullable=False)  # session_exit, manual, simulated
    captured_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    notes = Column(Text, nullable=True)

    user = relationship("User", back_populates="snapshots")
    items = relationship("SnapshotItem", back_populates="snapshot", cascade="all, delete-orphan")

class SnapshotItem(Base):
    __tablename__ = "snapshot_items"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    snapshot_id = Column(String(36), ForeignKey("market_snapshots.id", ondelete="CASCADE"), nullable=False, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    price = Column(Float, nullable=False)
    volume = Column(Float, nullable=True)
    avg_volume_20d = Column(Float, nullable=True)
    day_high = Column(Float, nullable=True)
    day_low = Column(Float, nullable=True)
    atr_14d = Column(Float, nullable=True)
    market_timestamp = Column(DateTime, nullable=True)
    data_source = Column(String(50), default="yfinance", nullable=False)
    freshness = Column(String(20), default="LIVE", nullable=False)  # LIVE, DELAYED, STALE

    snapshot = relationship("WatchlistSnapshot", back_populates="items")
