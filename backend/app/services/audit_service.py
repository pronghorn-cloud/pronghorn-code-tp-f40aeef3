"""Audit Service

Business logic for audit logging and compliance reporting.
"""

from typing import Optional, Tuple, List, Any
from uuid import UUID
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload

from app.models.audit import AuditLog, AuditAction


class AuditService:
    """Service for audit logging and compliance reporting."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def log(
        self,
        action: AuditAction,
        user_id: Optional[UUID] = None,
        claim_id: Optional[UUID] = None,
        rule_id: Optional[UUID] = None,
        document_id: Optional[UUID] = None,
        description: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        correlation_id: Optional[str] = None,
        phi_accessed: bool = False,
        masked_fields: Optional[List[str]] = None,
        metadata: Optional[dict] = None,
        before_state: Optional[dict] = None,
        after_state: Optional[dict] = None,
        execution_result: Optional[str] = None,
        decision_rationale: Optional[str] = None,
    ) -> AuditLog:
        """Create an audit log entry."""
        log_entry = AuditLog(
            action=action,
            action_description=description,
            user_id=user_id,
            claim_id=claim_id,
            rule_id=rule_id,
            document_id=document_id,
            ip_address=ip_address,
            user_agent=user_agent,
            correlation_id=correlation_id,
            phi_accessed=phi_accessed,
            masked_fields=masked_fields or [],
            metadata=metadata or {},
            before_state=before_state,
            after_state=after_state,
            execution_result=execution_result,
            decision_rationale=decision_rationale,
        )
        
        self.db.add(log_entry)
        await self.db.flush()
        await self.db.refresh(log_entry)
        
        return log_entry
    
    async def get_by_id(self, log_id: UUID) -> Optional[AuditLog]:
        """Get audit log entry by ID."""
        result = await self.db.execute(
            select(AuditLog)
            .options(
                selectinload(AuditLog.user),
                selectinload(AuditLog.claim),
                selectinload(AuditLog.rule)
            )
            .where(AuditLog.id == log_id)
        )
        return result.scalar_one_or_none()
    
    async def list(
        self,
        user_id: Optional[UUID] = None,
        claim_id: Optional[UUID] = None,
        action: Optional[AuditAction] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        phi_accessed: Optional[bool] = None,
        correlation_id: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
        sort_order: str = "desc"
    ) -> Tuple[List[AuditLog], int]:
        """List audit logs with filtering and pagination."""
        query = select(AuditLog)
        count_query = select(func.count(AuditLog.id))
        
        # Apply filters
        if user_id:
            query = query.where(AuditLog.user_id == user_id)
            count_query = count_query.where(AuditLog.user_id == user_id)
        
        if claim_id:
            query = query.where(AuditLog.claim_id == claim_id)
            count_query = count_query.where(AuditLog.claim_id == claim_id)
        
        if action:
            query = query.where(AuditLog.action == action)
            count_query = count_query.where(AuditLog.action == action)
        
        if date_from:
            query = query.where(AuditLog.created_at >= date_from)
            count_query = count_query.where(AuditLog.created_at >= date_from)
        
        if date_to:
            query = query.where(AuditLog.created_at <= date_to)
            count_query = count_query.where(AuditLog.created_at <= date_to)
        
        if phi_accessed is not None:
            query = query.where(AuditLog.phi_accessed == phi_accessed)
            count_query = count_query.where(AuditLog.phi_accessed == phi_accessed)
        
        if correlation_id:
            query = query.where(AuditLog.correlation_id == correlation_id)
            count_query = count_query.where(AuditLog.correlation_id == correlation_id)
        
        # Get total count
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Apply sorting (always by created_at)
        if sort_order == "desc":
            query = query.order_by(AuditLog.created_at.desc())
        else:
            query = query.order_by(AuditLog.created_at.asc())
        
        # Apply pagination
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        
        result = await self.db.execute(query)
        logs = result.scalars().all()
        
        return list(logs), total
    
    async def get_user_activity(
        self,
        user_id: UUID,
        days: int = 30
    ) -> List[AuditLog]:
        """Get user activity for the specified number of days."""
        date_from = datetime.utcnow() - timedelta(days=days)
        
        result = await self.db.execute(
            select(AuditLog)
            .where(
                and_(
                    AuditLog.user_id == user_id,
                    AuditLog.created_at >= date_from
                )
            )
            .order_by(AuditLog.created_at.desc())
        )
        return list(result.scalars().all())
    
    async def get_claim_history(self, claim_id: UUID) -> List[AuditLog]:
        """Get complete audit history for a claim."""
        result = await self.db.execute(
            select(AuditLog)
            .options(selectinload(AuditLog.user))
            .where(AuditLog.claim_id == claim_id)
            .order_by(AuditLog.created_at.asc())
        )
        return list(result.scalars().all())
    
    async def get_phi_access_report(
        self,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        user_id: Optional[UUID] = None
    ) -> List[dict]:
        """Generate PHI access report for HIPAA compliance."""
        query = select(AuditLog).where(AuditLog.phi_accessed == True)
        
        if date_from:
            query = query.where(AuditLog.created_at >= date_from)
        if date_to:
            query = query.where(AuditLog.created_at <= date_to)
        if user_id:
            query = query.where(AuditLog.user_id == user_id)
        
        query = query.order_by(AuditLog.created_at.desc())
        
        result = await self.db.execute(query)
        logs = result.scalars().all()
        
        return [
            {
                "timestamp": log.created_at.isoformat(),
                "user_id": str(log.user_id) if log.user_id else None,
                "action": log.action.value,
                "claim_id": str(log.claim_id) if log.claim_id else None,
                "masked_fields": log.masked_fields,
                "ip_address": str(log.ip_address) if log.ip_address else None,
            }
            for log in logs
        ]
    
    async def get_action_summary(
        self,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> List[dict]:
        """Get summary of actions by type."""
        query = select(
            AuditLog.action,
            func.count(AuditLog.id).label("count")
        ).group_by(AuditLog.action)
        
        if date_from:
            query = query.where(AuditLog.created_at >= date_from)
        if date_to:
            query = query.where(AuditLog.created_at <= date_to)
        
        result = await self.db.execute(query)
        rows = result.fetchall()
        
        return [
            {
                "action": row[0].value,
                "count": row[1]
            }
            for row in rows
        ]
    
    async def get_failed_login_attempts(
        self,
        since: Optional[datetime] = None,
        ip_address: Optional[str] = None
    ) -> List[AuditLog]:
        """Get failed login attempts for security monitoring."""
        query = select(AuditLog).where(
            AuditLog.action == AuditAction.USER_LOGIN_FAILED
        )
        
        if since:
            query = query.where(AuditLog.created_at >= since)
        if ip_address:
            query = query.where(AuditLog.ip_address == ip_address)
        
        query = query.order_by(AuditLog.created_at.desc())
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_rule_execution_report(
        self,
        rule_id: Optional[UUID] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> dict:
        """Get rule execution statistics."""
        query = select(AuditLog).where(
            AuditLog.action == AuditAction.RULE_EXECUTED
        )
        
        if rule_id:
            query = query.where(AuditLog.rule_id == rule_id)
        if date_from:
            query = query.where(AuditLog.created_at >= date_from)
        if date_to:
            query = query.where(AuditLog.created_at <= date_to)
        
        result = await self.db.execute(query)
        logs = result.scalars().all()
        
        # Calculate statistics
        total = len(logs)
        approved = sum(1 for log in logs if log.execution_result == "approve")
        denied = sum(1 for log in logs if log.execution_result == "deny")
        flagged = sum(1 for log in logs if log.execution_result == "flag")
        
        return {
            "total_executions": total,
            "approved": approved,
            "denied": denied,
            "flagged": flagged,
            "approval_rate": (approved / total * 100) if total > 0 else 0,
            "denial_rate": (denied / total * 100) if total > 0 else 0,
        }
    
    async def cleanup_old_logs(
        self,
        retention_days: int = 2555  # ~7 years for HIPAA
    ) -> int:
        """Archive or delete old audit logs beyond retention period.
        
        Note: This should be handled carefully with proper archival strategy.
        For HIPAA compliance, logs should be archived, not deleted.
        """
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
        
        # Count logs to be archived
        result = await self.db.execute(
            select(func.count(AuditLog.id))
            .where(AuditLog.created_at < cutoff_date)
        )
        count = result.scalar()
        
        # In production, implement archival to cold storage
        # For now, just return the count of logs that would be archived
        
        return count
    
    # Convenience methods for common audit actions
    
    async def log_login(
        self,
        user_id: UUID,
        ip_address: str,
        user_agent: str,
        success: bool = True
    ) -> AuditLog:
        """Log user login attempt."""
        action = AuditAction.USER_LOGIN if success else AuditAction.USER_LOGIN_FAILED
        return await self.log(
            action=action,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            description=f"User {'logged in successfully' if success else 'login failed'}",
        )
    
    async def log_phi_access(
        self,
        user_id: UUID,
        claim_id: UUID,
        accessed_fields: List[str],
        ip_address: Optional[str] = None,
        correlation_id: Optional[str] = None
    ) -> AuditLog:
        """Log PHI access for HIPAA compliance."""
        return await self.log(
            action=AuditAction.PHI_ACCESSED,
            user_id=user_id,
            claim_id=claim_id,
            phi_accessed=True,
            masked_fields=accessed_fields,
            ip_address=ip_address,
            correlation_id=correlation_id,
            description=f"PHI fields accessed: {', '.join(accessed_fields)}",
        )
    
    async def log_claim_action(
        self,
        action: AuditAction,
        claim_id: UUID,
        user_id: UUID,
        before_state: Optional[dict] = None,
        after_state: Optional[dict] = None,
        description: Optional[str] = None,
        correlation_id: Optional[str] = None
    ) -> AuditLog:
        """Log claim-related action."""
        return await self.log(
            action=action,
            claim_id=claim_id,
            user_id=user_id,
            before_state=before_state,
            after_state=after_state,
            description=description,
            correlation_id=correlation_id,
        )
    
    async def log_rule_execution(
        self,
        rule_id: UUID,
        claim_id: UUID,
        result: str,
        rationale: str,
        correlation_id: Optional[str] = None
    ) -> AuditLog:
        """Log rule execution for audit trail."""
        return await self.log(
            action=AuditAction.RULE_EXECUTED,
            rule_id=rule_id,
            claim_id=claim_id,
            execution_result=result,
            decision_rationale=rationale,
            correlation_id=correlation_id,
            description=f"Rule executed with result: {result}",
        )
