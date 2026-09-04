from datetime import datetime, timezone
from typing import Tuple, Optional
from app.schemas.feed import DataConfidenceStatus

def evaluate_data_freshness(timestamp: datetime) -> Tuple[str, int, int]:
    """
    Evaluates freshness status and confidence score based on data age.
    Returns: (status, confidence_score, age_minutes)
    - LIVE: < 15 minutes old -> 100% confidence
    - DELAYED: 15 to 45 minutes old -> 85% confidence
    - STALE: > 45 minutes old -> 50% confidence
    """
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=timezone.utc)
    
    now = datetime.now(timezone.utc)
    age_seconds = (now - timestamp).total_seconds()
    age_minutes = max(0, int(age_seconds / 60))

    if age_minutes < 15:
        return "LIVE", 100, age_minutes
    elif age_minutes <= 45:
        return "DELAYED", 85, age_minutes
    else:
        return "STALE", 50, age_minutes

def build_confidence_report(
    provider_name: str,
    latest_timestamp: Optional[datetime] = None,
    discrepancy_detected: bool = False,
    discrepancy_details: Optional[str] = None
) -> DataConfidenceStatus:
    if latest_timestamp is None:
        latest_timestamp = datetime.now(timezone.utc)

    status, confidence, age_min = evaluate_data_freshness(latest_timestamp)
    if discrepancy_detected:
        confidence = max(20, confidence - 30)

    return DataConfidenceStatus(
        provider=provider_name,
        status=status,
        confidence_score=confidence,
            latency_ms=180,
        last_updated=latest_timestamp.isoformat(),
        discrepancy_detected=discrepancy_detected,
        discrepancy_details=discrepancy_details
    )
