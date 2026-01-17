"""User Management Endpoints

Handles user CRUD operations (admin only).
"""

from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
)
from app.schemas.common import SuccessResponse, PaginationMeta
from app.services.user_service import UserService
from app.services.audit_service import AuditService
from app.models.audit import AuditAction
from app.models.user import UserRole, UserStatus

router = APIRouter()


def check_admin(user):
    """Check if user has admin role."""
    if user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new user (admin only)."""
    check_admin(current_user)
    
    user_service = UserService(db)
    audit_service = AuditService(db)
    
    # Check for duplicate email
    existing = await user_service.get_by_email(user_data.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user
    user = await user_service.create(user_data)
    
    # Log creation
    await audit_service.log(
        action=AuditAction.USER_CREATED,
        user_id=current_user.id,
        metadata={"created_user_id": str(user.id), "email": user.email}
    )
    
    return UserResponse.model_validate(user)


@router.get("", response_model=dict)
async def list_users(
    role: Optional[UserRole] = None,
    status: Optional[UserStatus] = None,
    provider_id: Optional[UUID] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List users (admin only)."""
    check_admin(current_user)
    
    user_service = UserService(db)
    
    users, total = await user_service.list(
        role=role,
        status=status,
        provider_id=provider_id,
        search=search,
        page=page,
        page_size=page_size
    )
    
    total_pages = (total + page_size - 1) // page_size
    
    return {
        "data": [UserResponse.model_validate(u) for u in users],
        "meta": PaginationMeta(
            page=page,
            page_size=page_size,
            total_items=total,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1,
        )
    }


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user details."""
    # Users can view their own profile, admins can view anyone
    if current_user.role != UserRole.ADMIN and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    user_service = UserService(db)
    
    user = await user_service.get_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse.model_validate(user)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    user_data: UserUpdate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update user (admin only, or self for limited fields)."""
    user_service = UserService(db)
    audit_service = AuditService(db)
    
    user = await user_service.get_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check permissions
    if current_user.role != UserRole.ADMIN:
        if current_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        # Non-admins can only update name
        user_data = UserUpdate(
            first_name=user_data.first_name,
            last_name=user_data.last_name
        )
    
    # Update user
    updated_user = await user_service.update(user_id, user_data)
    
    # Log update
    await audit_service.log(
        action=AuditAction.USER_UPDATED,
        user_id=current_user.id,
        metadata={"updated_user_id": str(user_id)}
    )
    
    return UserResponse.model_validate(updated_user)


@router.delete("/{user_id}", response_model=SuccessResponse)
async def delete_user(
    user_id: UUID,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete user (admin only). Soft delete - sets status to inactive."""
    check_admin(current_user)
    
    user_service = UserService(db)
    audit_service = AuditService(db)
    
    user = await user_service.get_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Can't delete yourself
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    # Soft delete
    await user_service.delete(user_id)
    
    # Log deletion
    await audit_service.log(
        action=AuditAction.USER_DELETED,
        user_id=current_user.id,
        metadata={"deleted_user_id": str(user_id), "email": user.email}
    )
    
    return SuccessResponse(message="User deleted successfully")


@router.post("/{user_id}/activate", response_model=UserResponse)
async def activate_user(
    user_id: UUID,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Activate a user account (admin only)."""
    check_admin(current_user)
    
    user_service = UserService(db)
    
    user = await user_service.get_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    activated_user = await user_service.update(
        user_id,
        UserUpdate(status=UserStatus.ACTIVE)
    )
    
    return UserResponse.model_validate(activated_user)


@router.post("/{user_id}/suspend", response_model=UserResponse)
async def suspend_user(
    user_id: UUID,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Suspend a user account (admin only)."""
    check_admin(current_user)
    
    user_service = UserService(db)
    
    user = await user_service.get_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Can't suspend yourself
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot suspend your own account"
        )
    
    suspended_user = await user_service.update(
        user_id,
        UserUpdate(status=UserStatus.SUSPENDED)
    )
    
    return UserResponse.model_validate(suspended_user)
