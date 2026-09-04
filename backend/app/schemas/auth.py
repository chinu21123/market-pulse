from datetime import datetime
from typing import Optional
from pydantic import BaseModel, field_validator

class UserRegister(BaseModel):
    email: str
    password: str
    full_name: Optional[str] = None
    persona_level: Optional[str] = "intermediate"  # beginner, intermediate, advanced
    preferred_language: Optional[str] = "en"

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        cleaned = value.strip().lower()
        if "@" not in cleaned or "." not in cleaned.rsplit("@", 1)[-1]:
            raise ValueError("Please provide a valid email address.")
        return cleaned

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if len(value) < 8 or not any(char.isalpha() for char in value) or not any(char.isdigit() for char in value):
            raise ValueError("Password must be at least 8 characters and include a letter and a number.")
        return value

    @field_validator("persona_level")
    @classmethod
    def validate_persona(cls, value: Optional[str]) -> Optional[str]:
        if value is not None and value not in {"beginner", "intermediate", "advanced"}:
            raise ValueError("Invalid persona level.")
        return value

class UserLogin(BaseModel):
    email: str
    password: str

class UserPreferences(BaseModel):
    persona_level: Optional[str] = None
    preferred_language: Optional[str] = None
    sensitivity_threshold: Optional[int] = None
    sensitivity_tier: Optional[str] = None

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: Optional[str] = None
    persona_level: str
    preferred_language: str
    sensitivity_threshold: int
    sensitivity_tier: str = "balanced"
    last_active_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
