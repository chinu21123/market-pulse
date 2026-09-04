from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.security import get_current_user
from app.models.user import User
from app.services.intelligence.gemini_client import gemini_service

router = APIRouter(prefix="/explain", tags=["AI Explanations"])

class ReExplainRequest(BaseModel):
    persona: str = "intermediate"  # beginner, intermediate, advanced
    language: str = "en"
    elapsed_time_human: str = "4h 23m"
    flagged_stocks: List[Dict[str, Any]] = []

@router.post("/re-explain")
def re_explain(
    payload: ReExplainRequest,
    current_user: User = Depends(get_current_user)
):
    result = gemini_service.generate_story(
        elapsed_time_human=payload.elapsed_time_human,
        total_watched=len(payload.flagged_stocks) + 5,
        meaningful_count=len(payload.flagged_stocks),
        attention_count=len(payload.flagged_stocks),
        normal_count=5,
        persona=payload.persona,
        language=payload.language,
        flagged_stocks=payload.flagged_stocks
    )
    return result
