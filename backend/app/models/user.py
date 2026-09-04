import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.orm import relationship

from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    persona_level = Column(String(20), default="intermediate", nullable=False)  # beginner, intermediate, advanced
    preferred_language = Column(String(10), default="en", nullable=False)        # en, es, fr, hi, zh, etc.
    sensitivity_threshold = Column(Integer, default=60, nullable=False)         # 0-100 threshold
    sensitivity_tier = Column(String(20), default="balanced", nullable=False)   # conservative, balanced, aggressive
    last_active_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    watchlist_items = relationship("WatchlistItem", back_populates="user", cascade="all, delete-orphan")
    snapshots = relationship("WatchlistSnapshot", back_populates="user", cascade="all, delete-orphan")
    audits = relationship("AttentionAudit", back_populates="user", cascade="all, delete-orphan")
