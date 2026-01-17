"""Rules Engine Endpoints

Handles rule definition, testing, and execution.
"""

from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.schemas.rule import (
    RuleCreate,
    RuleUpdate,
    RuleResponse,
    RuleListResponse,
    RuleVersionResponse,
    RuleTestRequest,
    RuleTestResult,
)
from app.schemas.common import SuccessResponse, PaginationMeta
from app.services.rule_service import RuleService
from app.services.audit_service import AuditService
from app.models.audit import AuditAction
from app.models.user import UserRole
from app.models.rule import RuleType

router = APIRouter()


def check_admin(user):
    """Check if user has admin role."""
    if user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )


@router.post("", response_model=RuleResponse, status_code=status.HTTP_201_CREATED)
async def create_rule(
    rule_data: RuleCreate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new rule (admin only)."""
    check_admin(current_user)
    
    rule_service = RuleService(db)
    audit_service = AuditService(db)
    
    # Check for duplicate code
    existing = await rule_service.get_by_code(rule_data.rule_code)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rule code already exists"
        )
    
    # Create rule
    rule = await rule_service.create(rule_data, created_by=current_user.id)
    
    # Log creation
    await audit_service.log(
        action=AuditAction.RULE_CREATED,
        user_id=current_user.id,
        rule_id=rule.id,
        metadata={"rule_code": rule.rule_code}
    )
    
    return RuleResponse.model_validate(rule)


@router.get("", response_model=RuleListResponse)
async def list_rules(
    rule_type: Optional[RuleType] = None,
    is_active: Optional[bool] = None,
    category: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: str = "priority",
    sort_order: str = "asc",
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List rules."""
    rule_service = RuleService(db)
    
    rules, total = await rule_service.list(
        rule_type=rule_type,
        is_active=is_active,
        category=category,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    
    total_pages = (total + page_size - 1) // page_size
    
    return RuleListResponse(
        data=[RuleResponse.model_validate(r) for r in rules],
        meta=PaginationMeta(
            page=page,
            page_size=page_size,
            total_items=total,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1,
        )
    )


@router.get("/{rule_id}", response_model=RuleResponse)
async def get_rule(
    rule_id: UUID,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get rule details."""
    rule_service = RuleService(db)
    
    rule = await rule_service.get_by_id(rule_id)
    
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rule not found"
        )
    
    return RuleResponse.model_validate(rule)


@router.put("/{rule_id}", response_model=RuleResponse)
async def update_rule(
    rule_id: UUID,
    rule_data: RuleUpdate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update rule (admin only). Creates a new version."""
    check_admin(current_user)
    
    rule_service = RuleService(db)
    audit_service = AuditService(db)
    
    rule = await rule_service.get_by_id(rule_id)
    
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rule not found"
        )
    
    # Update rule (creates new version)
    updated_rule = await rule_service.update(rule_id, rule_data, modified_by=current_user.id)
    
    # Log update
    await audit_service.log(
        action=AuditAction.RULE_UPDATED,
        user_id=current_user.id,
        rule_id=rule.id,
        metadata={"rule_code": rule.rule_code}
    )
    
    return RuleResponse.model_validate(updated_rule)


@router.delete("/{rule_id}", response_model=SuccessResponse)
async def delete_rule(
    rule_id: UUID,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete rule (admin only). Soft delete - marks as inactive."""
    check_admin(current_user)
    
    rule_service = RuleService(db)
    audit_service = AuditService(db)
    
    rule = await rule_service.get_by_id(rule_id)
    
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rule not found"
        )
    
    # Soft delete
    await rule_service.delete(rule_id)
    
    # Log deletion
    await audit_service.log(
        action=AuditAction.RULE_DELETED,
        user_id=current_user.id,
        rule_id=rule_id,
        metadata={"rule_code": rule.rule_code}
    )
    
    return SuccessResponse(message="Rule deleted successfully")


@router.get("/{rule_id}/versions", response_model=List[RuleVersionResponse])
async def get_rule_versions(
    rule_id: UUID,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get rule version history."""
    rule_service = RuleService(db)
    
    rule = await rule_service.get_by_id(rule_id)
    
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rule not found"
        )
    
    versions = await rule_service.get_versions(rule_id)
    
    return [RuleVersionResponse.model_validate(v) for v in versions]


@router.post("/{rule_id}/rollback/{version_id}", response_model=RuleResponse)
async def rollback_rule(
    rule_id: UUID,
    version_id: UUID,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Rollback rule to a previous version (admin only)."""
    check_admin(current_user)
    
    rule_service = RuleService(db)
    audit_service = AuditService(db)
    
    rule = await rule_service.get_by_id(rule_id)
    
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rule not found"
        )
    
    # Rollback
    rolled_back_rule = await rule_service.rollback(rule_id, version_id, modified_by=current_user.id)
    
    # Log rollback
    await audit_service.log(
        action=AuditAction.RULE_UPDATED,
        user_id=current_user.id,
        rule_id=rule_id,
        metadata={"action": "rollback", "to_version": str(version_id)}
    )
    
    return RuleResponse.model_validate(rolled_back_rule)


@router.post("/test", response_model=RuleTestResult)
async def test_rules(
    test_request: RuleTestRequest,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Test rules against sample data."""
    check_admin(current_user)
    
    rule_service = RuleService(db)
    
    # Execute test
    result = await rule_service.test_rules(
        rule_ids=test_request.rule_ids,
        claim_data=test_request.claim_data,
        scenario=test_request.scenario,
        dry_run=test_request.dry_run
    )
    
    return result


@router.post("/execute", response_model=RuleTestResult)
async def execute_rules(
    claim_id: UUID,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Execute rules against a specific claim (admin/adjudicator only)."""
    if current_user.role not in [UserRole.ADMIN, UserRole.ADJUDICATOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    rule_service = RuleService(db)
    audit_service = AuditService(db)
    
    # Execute rules
    result = await rule_service.execute_for_claim(claim_id)
    
    # Log execution
    await audit_service.log(
        action=AuditAction.RULE_EXECUTED,
        user_id=current_user.id,
        claim_id=claim_id,
        execution_result=result.final_outcome,
        metadata={"rules_matched": result.rules_matched}
    )
    
    return result
