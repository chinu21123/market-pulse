from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.feed import WhileYouWereAwayResponse
from app.services.feed_service import FeedService

router = APIRouter(prefix="/feed", tags=["While You Were Away Feed"])

@router.get("/while-you-were-away", response_model=WhileYouWereAwayResponse)
def get_feed(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return FeedService.get_while_you_were_away_feed(user=current_user, db=db)
