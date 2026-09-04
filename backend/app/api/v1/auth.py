from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_access_token, get_current_user
from app.models.user import User
from app.schemas.auth import UserRegister, UserLogin, UserPreferences, UserResponse, TokenResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=TokenResponse)
def register(payload: UserRegister, db: Session = Depends(get_db)):
    email_clean = payload.email

    existing = db.query(User).filter(User.email == email_clean).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists. Please sign in."
        )

    user = User(
        email=email_clean,
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name,
        persona_level=payload.persona_level or "intermediate",
        preferred_language=payload.preferred_language or "en"
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(data={"sub": user.id})
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )

@router.post("/login", response_model=TokenResponse)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    email_clean = payload.email.strip().lower()
    user = db.query(User).filter(User.email == email_clean).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password."
        )

    token = create_access_token(data={"sub": user.id})
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)

@router.patch("/preferences", response_model=UserResponse)
def update_preferences(
    payload: UserPreferences,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if payload.persona_level:
        if payload.persona_level not in ["beginner", "intermediate", "advanced"]:
            raise HTTPException(status_code=400, detail="Invalid persona level.")
        current_user.persona_level = payload.persona_level

    if payload.preferred_language:
        current_user.preferred_language = payload.preferred_language

    if payload.sensitivity_tier:
        tier = payload.sensitivity_tier.lower()
        if tier not in ["conservative", "balanced", "aggressive"]:
            raise HTTPException(status_code=400, detail="Invalid sensitivity tier.")
        current_user.sensitivity_tier = tier
        if tier == "conservative":
            current_user.sensitivity_threshold = 75
        elif tier == "balanced":
            current_user.sensitivity_threshold = 60
        elif tier == "aggressive":
            current_user.sensitivity_threshold = 45

    if payload.sensitivity_threshold is not None:
        if not (10 <= payload.sensitivity_threshold <= 90):
            raise HTTPException(status_code=400, detail="Sensitivity must be between 10 and 90.")
        current_user.sensitivity_threshold = payload.sensitivity_threshold

    db.commit()
    db.refresh(current_user)
    return UserResponse.model_validate(current_user)
