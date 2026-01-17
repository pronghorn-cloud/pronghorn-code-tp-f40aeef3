"""Claim Service

Business logic for claims management.
"""

from typing import Optional, Tuple, List
from uuid import UUID
from datetime import datetime
from decimal import Decimal
import json

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.models.claim import Claim, ClaimField, ClaimStatus
from app.schemas.claim import ClaimCreate, ClaimUpdate
from app.core.security import phi_encryption, hash_patient_id
from app.core.cache import cache, CacheKeys


class ClaimService:
    """Service for claims management operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(
        self,
        provider_id: UUID,
        data: ClaimCreate,
        created_by: UUID
    ) -> Claim:
        """Create a new claim."""
        # Generate claim number
        claim_number = await self._generate_claim_number()
        
        # Calculate total from service lines
        total_amount = sum(
            line.unit_price * line.quantity
            for line in data.service_lines
        ) if data.service_lines else Decimal("0.00")
        
        # Encrypt patient info if provided
        patient_id_hash = None
        patient_info_encrypted = None
        
        if data.patient_info:
            patient_id_hash = hash_patient_id(data.patient_info.patient_id)
            patient_info_encrypted = phi_encryption.encrypt(
                json.dumps(data.patient_info.model_dump(), default=str)
            )
        
        # Create claim
        claim = Claim(
            provider_id=provider_id,
            claim_number=claim_number,
            template_id=data.template_id,
            patient_id_hash=patient_id_hash,
            patient_info_encrypted=patient_info_encrypted,
            service_date=datetime.combine(data.service_date, datetime.min.time()) if data.service_date else None,
            service_end_date=datetime.combine(data.service_end_date, datetime.min.time()) if data.service_end_date else None,
            service_lines=[line.model_dump() for line in data.service_lines] if data.service_lines else [],
            total_amount=total_amount,
            status=ClaimStatus.DRAFT,
        )
        
        self.db.add(claim)
        await self.db.flush()
        await self.db.refresh(claim)
        
        return claim
    
    async def get_by_id(self, claim_id: UUID) -> Optional[Claim]:
        """Get claim by ID with related data."""
        result = await self.db.execute(
            select(Claim)
            .options(
                selectinload(Claim.fields),
                selectinload(Claim.documents),
                selectinload(Claim.adjudication_result)
            )
            .where(Claim.id == claim_id)
        )
        return result.scalar_one_or_none()
    
    async def list(
        self,
        provider_id: Optional[UUID] = None,
        status: Optional[ClaimStatus] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> Tuple[List[Claim], int]:
        """List claims with filtering and pagination."""
        query = select(Claim)
        count_query = select(func.count(Claim.id))
        
        # Apply filters
        if provider_id:
            query = query.where(Claim.provider_id == provider_id)
            count_query = count_query.where(Claim.provider_id == provider_id)
        
        if status:
            query = query.where(Claim.status == status)
            count_query = count_query.where(Claim.status == status)
        
        if date_from:
            query = query.where(Claim.created_at >= date_from)
            count_query = count_query.where(Claim.created_at >= date_from)
        
        if date_to:
            query = query.where(Claim.created_at <= date_to)
            count_query = count_query.where(Claim.created_at <= date_to)
        
        # Get total count
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Apply sorting
        sort_column = getattr(Claim, sort_by, Claim.created_at)
        if sort_order == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())
        
        # Apply pagination
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        
        result = await self.db.execute(query)
        claims = result.scalars().all()
        
        return list(claims), total
    
    async def update(self, claim_id: UUID, data: ClaimUpdate) -> Optional[Claim]:
        """Update claim."""
        claim = await self.get_by_id(claim_id)
        
        if not claim:
            return None
        
        # Update patient info if provided
        if data.patient_info:
            claim.patient_id_hash = hash_patient_id(data.patient_info.patient_id)
            claim.patient_info_encrypted = phi_encryption.encrypt(
                json.dumps(data.patient_info.model_dump(), default=str)
            )
        
        # Update other fields
        if data.service_date:
            claim.service_date = datetime.combine(data.service_date, datetime.min.time())
        
        if data.service_end_date:
            claim.service_end_date = datetime.combine(data.service_end_date, datetime.min.time())
        
        if data.service_lines is not None:
            claim.service_lines = [line.model_dump() for line in data.service_lines]
            # Recalculate total
            claim.total_amount = sum(
                Decimal(str(line.unit_price)) * line.quantity
                for line in data.service_lines
            )
        
        if data.internal_notes:
            claim.internal_notes = data.internal_notes
        
        await self.db.flush()
        await self.db.refresh(claim)
        
        return claim
    
    async def submit(self, claim_id: UUID) -> Optional[Claim]:
        """Submit claim for adjudication."""
        claim = await self.get_by_id(claim_id)
        
        if not claim:
            return None
        
        claim.status = ClaimStatus.SUBMITTED
        claim.submitted_at = datetime.utcnow()
        
        await self.db.flush()
        await self.db.refresh(claim)
        
        # TODO: Trigger adjudication workflow via event bus
        
        return claim
    
    async def update_status(
        self,
        claim_id: UUID,
        status: ClaimStatus,
        reason: Optional[str] = None,
        notes: Optional[str] = None,
        user_id: Optional[UUID] = None
    ) -> Optional[Claim]:
        """Update claim status."""
        claim = await self.get_by_id(claim_id)
        
        if not claim:
            return None
        
        claim.status = status
        
        if status == ClaimStatus.DENIED and reason:
            claim.denial_reason = reason
        
        if status == ClaimStatus.ADJUDICATED:
            claim.adjudicated_at = datetime.utcnow()
        
        if notes:
            claim.internal_notes = notes
        
        await self.db.flush()
        await self.db.refresh(claim)
        
        return claim
    
    async def delete(self, claim_id: UUID) -> bool:
        """Delete claim (only drafts)."""
        claim = await self.get_by_id(claim_id)
        
        if not claim:
            return False
        
        await self.db.delete(claim)
        await self.db.flush()
        
        return True
    
    async def validate_for_submission(self, claim_id: UUID) -> List[str]:
        """Validate claim is complete for submission."""
        errors = []
        
        claim = await self.get_by_id(claim_id)
        
        if not claim:
            return ["Claim not found"]
        
        if not claim.patient_info_encrypted:
            errors.append("Patient information is required")
        
        if not claim.service_date:
            errors.append("Service date is required")
        
        if not claim.service_lines or len(claim.service_lines) == 0:
            errors.append("At least one service line is required")
        
        # TODO: Add more validation rules based on form template
        
        return errors
    
    async def get_status_history(self, claim_id: UUID) -> List[dict]:
        """Get claim status history from audit logs."""
        # This would query the audit log for status changes
        # For now, return a simple structure
        claim = await self.get_by_id(claim_id)
        
        if not claim:
            return []
        
        history = [
            {
                "status": ClaimStatus.DRAFT.value,
                "timestamp": claim.created_at.isoformat(),
                "description": "Claim created"
            }
        ]
        
        if claim.submitted_at:
            history.append({
                "status": ClaimStatus.SUBMITTED.value,
                "timestamp": claim.submitted_at.isoformat(),
                "description": "Claim submitted for adjudication"
            })
        
        if claim.adjudicated_at:
            history.append({
                "status": claim.status.value,
                "timestamp": claim.adjudicated_at.isoformat(),
                "description": f"Claim {claim.status.value}"
            })
        
        return history
    
    async def _generate_claim_number(self) -> str:
        """Generate unique claim number."""
        # Format: CLM-YYYYMMDD-XXXXX
        today = datetime.utcnow().strftime("%Y%m%d")
        
        # Get count of claims created today
        result = await self.db.execute(
            select(func.count(Claim.id))
            .where(Claim.claim_number.like(f"CLM-{today}-%"))
        )
        count = result.scalar() or 0
        
        return f"CLM-{today}-{str(count + 1).zfill(5)}"
