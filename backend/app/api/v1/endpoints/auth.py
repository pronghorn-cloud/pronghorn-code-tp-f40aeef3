"""Authentication Endpoints

Handles user authentication, token management, and MFA.
"""

from datetime import datetime, timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.core.config import settings
from app.schemas.user import (
    UserLogin,
    TokenResponse,
    UserResponse,
    RefreshTokenRequest,
    PasswordChange,
    MFASetup,
    MFAVerify,
)
from app.schemas.common import SuccessResponse, ErrorResponse
from app.services.user_service import UserService
from app.services.audit_service import AuditService
from app.models.audit import AuditAction

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Dependency to get current authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_token(token)
    if payload is None:
        raise credentials_exception
    
    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    user_service = UserService(db)
    user = await user_service.get_by_id(user_id)
    
    if user is None:
        raise credentials_exception
    
    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is not active"
        )
    
    return user


@router.post("/login", response_model=TokenResponse)
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """Authenticate user and return access tokens."""
    user_service = UserService(db)
    audit_service = AuditService(db)
    
    # Find user by email
    user = await user_service.get_by_email(form_data.username)
    
    if not user or not verify_password(form_data.password, user.password_hash):
        # Log failed attempt
        await audit_service.log(
            action=AuditAction.USER_LOGIN_FAILED,
            user_id=user.id if user else None,
            ip_address=request.client.host if request.client else None,
            metadata={"email": form_data.username}
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if MFA is enabled
    if user.mfa_enabled:
        # Return partial token that requires MFA verification
        mfa_token = create_access_token(
            subject=str(user.id),
            expires_delta=timedelta(minutes=5),
            additional_claims={"mfa_required": True}
        )
        return {
            "access_token": mfa_token,
            "refresh_token": "",
            "token_type": "bearer",
            "expires_in": 300,
            "mfa_required": True,
            "user": UserResponse.model_validate(user)
        }
    
    # Create tokens
    access_token = create_access_token(subject=str(user.id))
    refresh_token = create_refresh_token(subject=str(user.id))
    
    # Update last login
    await user_service.update_last_login(user.id)
    
    # Log successful login
    await audit_service.log(
        action=AuditAction.USER_LOGIN,
        user_id=user.id,
        ip_address=request.client.host if request.client else None,
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": UserResponse.model_validate(user)
    }


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """Refresh access token using refresh token."""
    payload = decode_token(request.refresh_token)
    
    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user_id = payload.get("sub")
    user_service = UserService(db)
    user = await user_service.get_by_id(user_id)
    
    if not user or user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Create new tokens
    access_token = create_access_token(subject=str(user.id))
    new_refresh_token = create_refresh_token(subject=str(user.id))
    
    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": UserResponse.model_validate(user)
    }


@router.post("/logout", response_model=SuccessResponse)
async def logout(
    request: Request,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Logout user and invalidate tokens."""
    audit_service = AuditService(db)
    
    # Log logout
    await audit_service.log(
        action=AuditAction.USER_LOGOUT,
        user_id=current_user.id,
        ip_address=request.client.host if request.client else None,
    )
    
    # In a production system, you would also invalidate the token
    # by adding it to a blacklist in Redis
    
    return SuccessResponse(message="Successfully logged out")


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: dict = Depends(get_current_user)
):
    """Get current authenticated user information."""
    return UserResponse.model_validate(current_user)


@router.post("/change-password", response_model=SuccessResponse)
async def change_password(
    request: Request,
    password_data: PasswordChange,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Change user password."""
    user_service = UserService(db)
    audit_service = AuditService(db)
    
    # Verify current password
    if not verify_password(password_data.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Update password
    await user_service.change_password(current_user.id, password_data.new_password)
    
    # Log password change
    await audit_service.log(
        action=AuditAction.PASSWORD_CHANGED,
        user_id=current_user.id,
        ip_address=request.client.host if request.client else None,
    )
    
    return SuccessResponse(message="Password changed successfully")


@router.post("/mfa/setup", response_model=MFASetup)
async def setup_mfa(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Setup MFA for user."""
    user_service = UserService(db)
    
    if current_user.mfa_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA is already enabled"
        )
    
    # Generate MFA secret and QR code
    mfa_data = await user_service.setup_mfa(current_user.id)
    
    return mfa_data


@router.post("/mfa/verify", response_model=SuccessResponse)
async def verify_mfa(
    request: Request,
    mfa_data: MFAVerify,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Verify and enable MFA."""
    user_service = UserService(db)
    audit_service = AuditService(db)
    
    # Verify the MFA code
    is_valid = await user_service.verify_mfa_code(current_user.id, mfa_data.code)
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid MFA code"
        )
    
    # Enable MFA
    await user_service.enable_mfa(current_user.id)
    
    # Log MFA enabled
    await audit_service.log(
        action=AuditAction.MFA_ENABLED,
        user_id=current_user.id,
        ip_address=request.client.host if request.client else None,
    )
    
    return SuccessResponse(message="MFA enabled successfully")
