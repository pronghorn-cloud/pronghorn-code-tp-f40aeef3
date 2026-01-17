"""Audit & Compliance Endpoints

Handles audit log retrieval and compliance reporting.
"""

from typing import Optional
from datetime import date, datetime
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
import io
import csv

from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.schemas.common import PaginationMeta
from app.services.audit_service import AuditService
from app.models.audit import AuditAction
from app.models.user import UserRole

router = APIRouter()


def check_auditor_access(user):
    """Check if user has auditor or admin role."""
    if user.role not in [UserRole.ADMIN, UserRole.AUDITOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Auditor access required"
        )


@router.get("/logs")
async def get_audit_logs(
    action: Optional[AuditAction] = None,
    user_id: Optional[UUID] = None,
    claim_id: Optional[UUID] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    phi_accessed: Optional[bool] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get audit logs with filtering.
    
    HIPAA-compliant audit trail access (auditor/admin only).
    """
    check_auditor_access(current_user)
    
    audit_service = AuditService(db)
    
    logs, total = await audit_service.get_logs(
        action=action,
        user_id=user_id,
        claim_id=claim_id,
        date_from=date_from,
        date_to=date_to,
        phi_accessed=phi_accessed,
        page=page,
        page_size=page_size
    )
    
    total_pages = (total + page_size - 1) // page_size
    
    return {
        "data": logs,
        "meta": PaginationMeta(
            page=page,
            page_size=page_size,
            total_items=total,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1,
        )
    }


@router.get("/logs/{log_id}")
async def get_audit_log_detail(
    log_id: UUID,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get detailed audit log entry."""
    check_auditor_access(current_user)
    
    audit_service = AuditService(db)
    
    log = await audit_service.get_log_by_id(log_id)
    
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit log not found"
        )
    
    return log


@router.get("/logs/export")
async def export_audit_logs(
    action: Optional[AuditAction] = None,
    user_id: Optional[UUID] = None,
    claim_id: Optional[UUID] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    format: str = Query("csv", pattern="^(csv|json)$"),
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Export audit logs to CSV or JSON.
    
    Maximum 10,000 records per export.
    """
    check_auditor_access(current_user)
    
    audit_service = AuditService(db)
    
    logs, total = await audit_service.get_logs(
        action=action,
        user_id=user_id,
        claim_id=claim_id,
        date_from=date_from,
        date_to=date_to,
        page=1,
        page_size=10000
    )
    
    if format == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            "ID", "Action", "User ID", "Claim ID", "Rule ID",
            "IP Address", "PHI Accessed", "Timestamp", "Details"
        ])
        
        # Data rows
        for log in logs:
            writer.writerow([
                str(log.id),
                log.action.value,
                str(log.user_id) if log.user_id else "",
                str(log.claim_id) if log.claim_id else "",
                str(log.rule_id) if log.rule_id else "",
                str(log.ip_address) if log.ip_address else "",
                log.phi_accessed,
                log.created_at.isoformat(),
                log.action_description or ""
            ])
        
        output.seek(0)
        
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=audit_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            }
        )
    else:
        # JSON format
        return {
            "exported_at": datetime.now().isoformat(),
            "total_records": len(logs),
            "data": logs
        }


@router.get("/reports/phi-access")
async def get_phi_access_report(
    date_from: date,
    date_to: date,
    user_id: Optional[UUID] = None,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Generate PHI access report.
    
    HIPAA-required report of all PHI access within date range.
    """
    check_auditor_access(current_user)
    
    audit_service = AuditService(db)
    
    report = await audit_service.generate_phi_access_report(
        date_from=date_from,
        date_to=date_to,
        user_id=user_id
    )
    
    return report


@router.get("/reports/user-activity")
async def get_user_activity_report(
    date_from: date,
    date_to: date,
    user_id: Optional[UUID] = None,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Generate user activity report."""
    check_auditor_access(current_user)
    
    audit_service = AuditService(db)
    
    report = await audit_service.generate_user_activity_report(
        date_from=date_from,
        date_to=date_to,
        user_id=user_id
    )
    
    return report


@router.get("/reports/claims-summary")
async def get_claims_summary_report(
    date_from: date,
    date_to: date,
    provider_id: Optional[UUID] = None,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Generate claims processing summary report."""
    check_auditor_access(current_user)
    
    audit_service = AuditService(db)
    
    report = await audit_service.generate_claims_summary_report(
        date_from=date_from,
        date_to=date_to,
        provider_id=provider_id
    )
    
    return report


@router.get("/reports/rule-execution")
async def get_rule_execution_report(
    date_from: date,
    date_to: date,
    rule_id: Optional[UUID] = None,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Generate rule execution report."""
    check_auditor_access(current_user)
    
    audit_service = AuditService(db)
    
    report = await audit_service.generate_rule_execution_report(
        date_from=date_from,
        date_to=date_to,
        rule_id=rule_id
    )
    
    return report
