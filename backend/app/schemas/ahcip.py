"""AHCIP Code Schemas

Pydantic models for AHCIP code lookup API.
"""

from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import date
from uuid import UUID
from decimal import Decimal

from app.schemas.common import BaseSchema, PaginationMeta


class AHCIPCodeResponse(BaseSchema):
    """AHCIP code response schema."""
    id: UUID
    procedure_code: str
    description: str
    short_description: Optional[str]
    category: Optional[str]
    subcategory: Optional[str]
    fee_amount: Decimal
    unit_type: Optional[str]
    effective_date: date
    expiration_date: Optional[date]
    is_active: bool
    is_deprecated: bool
    replacement_code: Optional[str]
    notes: Optional[str]
    requirements: Optional[List[str]]
    modifiers: Optional[List[str]]


class AHCIPCodeSearchResponse(BaseModel):
    """AHCIP code search results."""
    data: List[AHCIPCodeResponse]
    meta: PaginationMeta


class AHCIPCodeSearchParams(BaseModel):
    """Search parameters for AHCIP codes."""
    query: Optional[str] = Field(None, min_length=2, max_length=100)
    category: Optional[str] = None
    include_deprecated: bool = False
    effective_date: Optional[date] = None


class AHCIPFeeScheduleResponse(BaseModel):
    """Fee schedule for a specific code."""
    procedure_code: str
    description: str
    fee_amount: Decimal
    effective_date: date
    expiration_date: Optional[date]
    unit_type: Optional[str]
    modifiers_applicable: List[dict] = []


class AHCIPCodeCreate(BaseModel):
    """Schema for creating a new AHCIP code."""
    procedure_code: str = Field(..., max_length=20)
    description: str
    short_description: Optional[str] = Field(None, max_length=255)
    category: Optional[str] = Field(None, max_length=100)
    subcategory: Optional[str] = Field(None, max_length=100)
    fee_amount: Decimal = Field(..., ge=0)
    unit_type: Optional[str] = Field(None, max_length=50)
    effective_date: date
    expiration_date: Optional[date] = None
    is_active: Optional[bool] = True
    notes: Optional[str] = None
    requirements: Optional[List[str]] = None
    modifiers: Optional[List[str]] = None


class AHCIPCodeUpdate(BaseModel):
    """Schema for updating an AHCIP code."""
    description: Optional[str] = None
    short_description: Optional[str] = Field(None, max_length=255)
    category: Optional[str] = Field(None, max_length=100)
    subcategory: Optional[str] = Field(None, max_length=100)
    fee_amount: Optional[Decimal] = Field(None, ge=0)
    unit_type: Optional[str] = Field(None, max_length=50)
    effective_date: Optional[date] = None
    expiration_date: Optional[date] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None
    requirements: Optional[List[str]] = None
    modifiers: Optional[List[str]] = None