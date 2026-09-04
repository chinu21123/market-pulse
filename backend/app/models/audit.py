import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.core.database import Base

class AttentionAudit(Base):
    __tablename__ = "attention_audits"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    snapshot_id = Column(String(36), nullable=True)
    symbol = Column(String(20), nullable=False, index=True)
    attention_score = Column(Integer, nullable=False)
    classification = Column(String(30), nullable=False)  # normal, worth_watching, significant, high_attention
    price_delta_pct = Column(Float, nullable=False)
    volatility_z_score = Column(Float, nullable=False)
    volume_ratio = Column(Float, nullable=False)
    gap_pct = Column(Float, nullable=False)
    benchmark_divergence = Column(Float, nullable=False)
    factor_breakdown = Column(Text, nullable=True)  # JSON string
    llm_explanation = Column(Text, nullable=True)
    evaluated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    user = relationship("User", back_populates="audits")
