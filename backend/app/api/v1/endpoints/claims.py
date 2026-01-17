"""Claims Endpoints

Handles claim creation, submission, and status tracking.
"""

from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.schemas.claim import (
    ClaimCreate,
    ClaimUpdate,
    ClaimResponse,
    ClaimDetailResponse,
    ClaimListResponse,
    ClaimSubmit,
    ClaimStatusUpdate,
    ClaimSearchParams,
)
from app.schemas.common import SuccessResponse, PaginationMeta
from app.services.claim_service import ClaimService
from app.services.audit_service import AuditService
from app.models.audit import AuditAction
from app.models.claim import ClaimStatus
from app.models.user import UserRole

router = APIRouter()


def check_admin_or_adjudicator(user):
    """Check if user has admin or adjudicator role."""
    if user.role not in [UserRole.ADMIN, UserRole.ADJUDICATOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )


@router.post("", response_model=ClaimResponse, status_code=status.HTTP_201_CREATED)
async def create_claim(
    claim_data: ClaimCreate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new claim (draft)."""
    claim_service = ClaimService(db)
    audit_service = AuditService(db)
    
    # Create claim
    claim = await claim_service.create(
        provider_id=current_user.provider_id,
        data=claim_data,
        created_by=current_user.id
    )
    
    # Log claim creation
    await audit_service.log(
        action=AuditAction.CLAIM_CREATED,
        user_id=current_user.id,
        claim_id=claim.id,
    )
    
    return ClaimResponse.model_validate(claim)


@router.get("", response_model=ClaimListResponse)
async def list_claims(
    status: Optional[ClaimStatus] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: str = "created_at",
    sort_order: str = "desc",
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List claims for the current provider."""
    claim_service = ClaimService(db)
    
    # Determine provider filter based on role
    provider_id = None
    if current_user.role == UserRole.PROVIDER:
        provider_id = current_user.provider_id
    
    # Get claims
    claims, total = await claim_service.list(
        provider_id=provider_id,
        status=status,
        date_from=date_from,
        date_to=date_to,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    
    total_pages = (total + page_size - 1) // page_size
    
    return ClaimListResponse(
        data=[ClaimResponse.model_validate(c) for c in claims],
        meta=PaginationMeta(
            page=page,
            page_size=page_size,
            total_items=total,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1,
        )
    )


@router.get("/{claim_id}", response_model=ClaimDetailResponse)
async def get_claim(
    claim_id: UUID,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get claim details."""
    claim_service = ClaimService(db)
    audit_service = AuditService(db)
    
    claim = await claim_service.get_by_id(claim_id)
    
    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Claim not found"
        )
    
    # Check access
    if current_user.role == UserRole.PROVIDER:
        if claim.provider_id != current_user.provider_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    # Log PHI access
    await audit_service.log(
        action=AuditAction.PHI_ACCESSED,
        user_id=current_user.id,
        claim_id=claim.id,
        phi_accessed=True,
    )
    
    return ClaimDetailResponse.model_validate(claim)


@router.put("/{claim_id}/draft", response_model=ClaimResponse)
async def save_draft(
    claim_id: UUID,
    claim_data: ClaimUpdate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Save claim as draft."""
    claim_service = ClaimService(db)
    audit_service = AuditService(db)
    
    # Get existing claim
    claim = await claim_service.get_by_id(claim_id)
    
    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Claim not found"
        )
    
    # Check ownership
    if current_user.role == UserRole.PROVIDER:
        if claim.provider_id != current_user.provider_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    # Check if claim can be edited
    if claim.status != ClaimStatus.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only draft claims can be edited"
        )
    
    # Update claim
    updated_claim = await claim_service.update(claim_id, claim_data)
    
    # Log update
    await audit_service.log(
        action=AuditAction.CLAIM_UPDATED,
        user_id=current_user.id,
        claim_id=claim.id,
    )
    
    return ClaimResponse.model_validate(updated_claim)


@router.post("/{claim_id}/submit", response_model=ClaimResponse)
async def submit_claim(
    claim_id: UUID,
    submit_data: ClaimSubmit,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Submit claim for adjudication."""
    claim_service = ClaimService(db)
    audit_service = AuditService(db)
    
    # Get claim
    claim = await claim_service.get_by_id(claim_id)
    
    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Claim not found"
        )
    
    # Check ownership
    if current_user.role == UserRole.PROVIDER:
        if claim.provider_id != current_user.provider_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    # Check if claim can be submitted
    if claim.status != ClaimStatus.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only draft claims can be submitted"
        )
    
    # Validate claim completeness
    validation_errors = await claim_service.validate_for_submission(claim_id)
    if validation_errors:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "Claim validation failed", "errors": validation_errors}
        )
    
    # Submit claim
    submitted_claim = await claim_service.submit(claim_id)
    
    # Log submission
    await audit_service.log(
        action=AuditAction.CLAIM_SUBMITTED,
        user_id=current_user.id,
        claim_id=claim.id,
    )
    
    return ClaimResponse.model_validate(submitted_claim)


@router.get("/{claim_id}/status", response_model=dict)
async def get_claim_status(
    claim_id: UUID,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get claim status history."""
    claim_service = ClaimService(db)
    
    claim = await claim_service.get_by_id(claim_id)
    
    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Claim not found"
        )
    
    # Check access
    if current_user.role == UserRole.PROVIDER:
        if claim.provider_id != current_user.provider_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    # Get status history
    history = await claim_service.get_status_history(claim_id)
    
    return {
        "current_status": claim.status,
        "history": history
    }


@router.put("/{claim_id}/status", response_model=ClaimResponse)
async def update_claim_status(
    claim_id: UUID,
    status_update: ClaimStatusUpdate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update claim status (admin/adjudicator only)."""
    check_admin_or_adjudicator(current_user)
    
    claim_service = ClaimService(db)
    audit_service = AuditService(db)
    
    claim = await claim_service.get_by_id(claim_id)
    
    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Claim not found"
        )
    
    # Update status
    updated_claim = await claim_service.update_status(
        claim_id,
        status_update.status,
        reason=status_update.reason,
        notes=status_update.notes,
        user_id=current_user.id
    )
    
    # Determine audit action based on new status
    action_map = {
        ClaimStatus.APPROVED: AuditAction.CLAIM_APPROVED,
        ClaimStatus.DENIED: AuditAction.CLAIM_DENIED,
        ClaimStatus.ADJUDICATED: AuditAction.CLAIM_ADJUDICATED,
    }
    audit_action = action_map.get(status_update.status, AuditAction.CLAIM_UPDATED)
    
    await audit_service.log(
        action=audit_action,
        user_id=current_user.id,
        claim_id=claim.id,
        metadata={"new_status": status_update.status.value, "reason": status_update.reason}
    )
    
    return ClaimResponse.model_validate(updated_claim)


@router.delete("/{claim_id}", response_model=SuccessResponse)
async def delete_claim(
    claim_id: UUID,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a draft claim."""
    claim_service = ClaimService(db)
    audit_service = AuditService(db)
    
    claim = await claim_service.get_by_id(claim_id)
    
    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Claim not found"
        )
    
    # Check ownership
    if current_user.role == UserRole.PROVIDER:
        if claim.provider_id != current_user.provider_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    # Only drafts can be deleted
    if claim.status != ClaimStatus.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only draft claims can be deleted"
        )
    
    # Delete claim
    await claim_service.delete(claim_id)
    
    # Log deletion
    await audit_service.log(
        action=AuditAction.CLAIM_DELETED,
        user_id=current_user.id,
        claim_id=claim_id,
    )
    
    return SuccessResponse(message="Claim deleted successfully")
