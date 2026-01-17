"""Claim Schemas

Pydantic models for claims API.
"""

from typing import Optional, List, Any
from pydantic import BaseModel, Field, field_validator
from datetime import datetime, date
from uuid import UUID
from decimal import Decimal

from app.schemas.common import BaseSchema, PaginationMeta
from app.models.claim import ClaimStatus


class ServiceLine(BaseModel):
    """Service line item for a claim."""
    procedure_code: str = Field(..., pattern=r"^[A-Z0-9]{3,10}$")
    description: Optional[str] = None
    service_date: date
    quantity: int = Field(default=1, ge=1)
    unit_price: Decimal = Field(..., ge=0)
    modifiers: Optional[List[str]] = None
    diagnosis_codes: Optional[List[str]] = None
    
    @property
    def total(self) -> Decimal:
        return self.unit_price * self.quantity


class PatientInfo(BaseModel):
    """Patient information (PHI - will be encrypted)."""
    patient_id: str
    first_name: str = Field(..., max_length=100)
    last_name: str = Field(..., max_length=100)
    date_of_birth: date
    gender: Optional[str] = Field(None, pattern=r"^(M|F|O)$")
    address: Optional[str] = None
    city: Optional[str] = None
    province: Optional[str] = None
    postal_code: Optional[str] = None
    phone: Optional[str] = None
    health_card_number: Optional[str] = None


class ClaimCreate(BaseModel):
    """Schema for creating a new claim."""
    template_id: Optional[UUID] = None
    patient_info: Optional[PatientInfo] = None
    service_date: Optional[date] = None
    service_end_date: Optional[date] = None
    service_lines: List[ServiceLine] = Field(default_factory=list)
    additional_fields: Optional[dict] = None
    
    @field_validator("service_end_date")
    @classmethod
    def validate_end_date(cls, v, info):
        if v and info.data.get("service_date") and v < info.data["service_date"]:
            raise ValueError("End date must be after start date")
        return v


class ClaimUpdate(BaseModel):
    """Schema for updating a claim."""
    patient_info: Optional[PatientInfo] = None
    service_date: Optional[date] = None
    service_end_date: Optional[date] = None
    service_lines: Optional[List[ServiceLine]] = None
    additional_fields: Optional[dict] = None
    internal_notes: Optional[str] = None


class ClaimSubmit(BaseModel):
    """Schema for submitting a claim."""
    confirm: bool = Field(..., description="Confirmation that claim is ready to submit")
    
    @field_validator("confirm")
    @classmethod
    def must_confirm(cls, v):
        if not v:
            raise ValueError("Must confirm submission")
        return v


class ClaimResponse(BaseSchema):
    """Claim response schema."""
    id: UUID
    claim_number: str
    provider_id: UUID
    template_id: Optional[UUID]
    status: ClaimStatus
    service_date: Optional[datetime]
    service_end_date: Optional[datetime]
    service_lines: List[dict]
    total_amount: Optional[Decimal]
    approved_amount: Optional[Decimal]
    submitted_at: Optional[datetime]
    adjudicated_at: Optional[datetime]
    denial_reason: Optional[str]
    created_at: datetime
    updated_at: datetime


class ClaimDetailResponse(ClaimResponse):
    """Detailed claim response with related data."""
    patient_info: Optional[dict] = None  # Decrypted only for authorized users
    documents: List[dict] = []
    adjudication_result: Optional[dict] = None
    status_history: List[dict] = []


class ClaimListResponse(BaseModel):
    """Paginated claim list response."""
    data: List[ClaimResponse]
    meta: PaginationMeta


class ClaimStatusUpdate(BaseModel):
    """Schema for manually updating claim status (admin/adjudicator)."""
    status: ClaimStatus
    reason: Optional[str] = None
    notes: Optional[str] = None


class ClaimSearchParams(BaseModel):
    """Claim search parameters."""
    status: Optional[ClaimStatus] = None
    provider_id: Optional[UUID] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    claim_number: Optional[str] = None
    min_amount: Optional[Decimal] = None
    max_amount: Optional[Decimal] = None
