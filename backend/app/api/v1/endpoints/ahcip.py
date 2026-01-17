"""AHCIP Code Lookup Endpoints

Handles procedure code search and fee schedule lookups.
"""

from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.schemas.ahcip import (
    AHCIPCodeResponse,
    AHCIPCodeSearchResponse,
    AHCIPFeeScheduleResponse,
)
from app.schemas.common import PaginationMeta
from app.services.ahcip_service import AHCIPService

router = APIRouter()


@router.get("/search", response_model=AHCIPCodeSearchResponse)
async def search_codes(
    query: Optional[str] = Query(None, min_length=2, max_length=100),
    category: Optional[str] = None,
    include_deprecated: bool = False,
    effective_date: Optional[date] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Search AHCIP procedure codes.
    
    Search by code or description. Returns matching codes with fee amounts.
    Results are cached for performance (24-hour TTL).
    """
    ahcip_service = AHCIPService(db)
    
    # Use today's date if not specified
    if not effective_date:
        effective_date = date.today()
    
    codes, total = await ahcip_service.search(
        query=query,
        category=category,
        include_deprecated=include_deprecated,
        effective_date=effective_date,
        page=page,
        page_size=page_size
    )
    
    total_pages = (total + page_size - 1) // page_size
    
    return AHCIPCodeSearchResponse(
        data=[AHCIPCodeResponse.model_validate(c) for c in codes],
        meta=PaginationMeta(
            page=page,
            page_size=page_size,
            total_items=total,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1,
        )
    )


@router.get("/categories", response_model=list[str])
async def get_categories(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get list of all AHCIP code categories."""
    ahcip_service = AHCIPService(db)
    
    categories = await ahcip_service.get_categories()
    
    return categories


@router.get("/{procedure_code}", response_model=AHCIPCodeResponse)
async def get_code(
    procedure_code: str,
    effective_date: Optional[date] = None,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get details for a specific procedure code.
    
    Returns the code details including current fee amount.
    """
    ahcip_service = AHCIPService(db)
    
    if not effective_date:
        effective_date = date.today()
    
    code = await ahcip_service.get_by_code(procedure_code, effective_date)
    
    if not code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Procedure code not found"
        )
    
    return AHCIPCodeResponse.model_validate(code)


@router.get("/{procedure_code}/fee", response_model=AHCIPFeeScheduleResponse)
async def get_fee_schedule(
    procedure_code: str,
    effective_date: Optional[date] = None,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get fee schedule for a specific procedure code.
    
    Returns the fee amount and any applicable modifiers.
    """
    ahcip_service = AHCIPService(db)
    
    if not effective_date:
        effective_date = date.today()
    
    fee_schedule = await ahcip_service.get_fee_schedule(procedure_code, effective_date)
    
    if not fee_schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fee schedule not found for this code"
        )
    
    return fee_schedule


@router.post("/bulk-lookup", response_model=list[AHCIPCodeResponse])
async def bulk_lookup(
    procedure_codes: list[str],
    effective_date: Optional[date] = None,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Bulk lookup multiple procedure codes.
    
    Efficiently retrieves multiple codes in a single request.
    Maximum 50 codes per request.
    """
    if len(procedure_codes) > 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 50 codes per request"
        )
    
    ahcip_service = AHCIPService(db)
    
    if not effective_date:
        effective_date = date.today()
    
    codes = await ahcip_service.bulk_lookup(procedure_codes, effective_date)
    
    return [AHCIPCodeResponse.model_validate(c) for c in codes]
