"""User Schemas

Pydantic models for user authentication and management.
"""

from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime
from uuid import UUID
import re

from app.schemas.common import BaseSchema
from app.models.user import UserRole, UserStatus


class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)


class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str = Field(..., min_length=8, max_length=128)
    role: UserRole = UserRole.PROVIDER
    provider_id: Optional[UUID] = None
    
    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Password must contain at least one special character")
        return v


class UserUpdate(BaseModel):
    """Schema for updating a user."""
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    status: Optional[UserStatus] = None
    role: Optional[UserRole] = None
    mfa_enabled: Optional[bool] = None


class UserResponse(BaseSchema):
    """User response schema."""
    id: UUID
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    role: UserRole
    status: UserStatus
    provider_id: Optional[UUID]
    mfa_enabled: bool
    last_login: Optional[datetime]
    created_at: datetime
    updated_at: datetime


class UserLogin(BaseModel):
    """User login request schema."""
    email: EmailStr
    password: str
    mfa_code: Optional[str] = Field(None, min_length=6, max_length=6)


class TokenResponse(BaseModel):
    """Authentication token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class RefreshTokenRequest(BaseModel):
    """Refresh token request."""
    refresh_token: str


class PasswordChange(BaseModel):
    """Password change request."""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=128)
    
    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        return v


class MFASetup(BaseModel):
    """MFA setup response."""
    secret: str
    qr_code_url: str
    backup_codes: list[str]


class MFAVerify(BaseModel):
    """MFA verification request."""
    code: str = Field(..., min_length=6, max_length=6)
