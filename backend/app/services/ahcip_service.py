"""AHCIP Service

Business logic for AHCIP code lookup and fee schedule management.
"""

from typing import Optional, Tuple, List
from uuid import UUID
from datetime import date
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_

from app.models.ahcip import AHCIPCode
from app.schemas.ahcip import AHCIPCodeCreate, AHCIPCodeUpdate
from app.core.cache import cache, CacheKeys


class AHCIPService:
    """Service for AHCIP code lookup and management."""
    
    # Cache TTL for AHCIP codes (24 hours - codes don't change often)
    CACHE_TTL = 86400
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, data: AHCIPCodeCreate) -> AHCIPCode:
        """Create a new AHCIP code."""
        code = AHCIPCode(
            procedure_code=data.procedure_code,
            description=data.description,
            short_description=data.short_description,
            category=data.category,
            subcategory=data.subcategory,
            fee_amount=data.fee_amount,
            unit_type=data.unit_type,
            effective_date=data.effective_date,
            expiration_date=data.expiration_date,
            is_active=data.is_active if data.is_active is not None else True,
            is_deprecated=False,
            notes=data.notes,
            requirements=data.requirements or [],
            modifiers=data.modifiers or [],
            search_terms=self._generate_search_terms(data),
        )
        
        self.db.add(code)
        await self.db.flush()
        await self.db.refresh(code)
        
        # Invalidate cache
        await cache.delete(CacheKeys.AHCIP_CODES)
        
        return code
    
    async def get_by_id(self, code_id: UUID) -> Optional[AHCIPCode]:
        """Get AHCIP code by ID."""
        result = await self.db.execute(
            select(AHCIPCode).where(AHCIPCode.id == code_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_procedure_code(self, procedure_code: str) -> Optional[AHCIPCode]:
        """Get AHCIP code by procedure code."""
        # Try cache first
        cache_key = f"{CacheKeys.AHCIP_CODES}:{procedure_code}"
        cached = await cache.get(cache_key)
        if cached:
            return cached
        
        result = await self.db.execute(
            select(AHCIPCode).where(AHCIPCode.procedure_code == procedure_code)
        )
        code = result.scalar_one_or_none()
        
        if code:
            await cache.set(cache_key, code, ttl=self.CACHE_TTL)
        
        return code
    
    async def list(
        self,
        category: Optional[str] = None,
        is_active: Optional[bool] = None,
        effective_date: Optional[date] = None,
        page: int = 1,
        page_size: int = 50,
        sort_by: str = "procedure_code",
        sort_order: str = "asc"
    ) -> Tuple[List[AHCIPCode], int]:
        """List AHCIP codes with filtering and pagination."""
        query = select(AHCIPCode)
        count_query = select(func.count(AHCIPCode.id))
        
        # Apply filters
        if category:
            query = query.where(AHCIPCode.category == category)
            count_query = count_query.where(AHCIPCode.category == category)
        
        if is_active is not None:
            query = query.where(AHCIPCode.is_active == is_active)
            count_query = count_query.where(AHCIPCode.is_active == is_active)
        
        if effective_date:
            query = query.where(
                and_(
                    AHCIPCode.effective_date <= effective_date,
                    or_(
                        AHCIPCode.expiration_date == None,
                        AHCIPCode.expiration_date >= effective_date
                    )
                )
            )
            count_query = count_query.where(
                and_(
                    AHCIPCode.effective_date <= effective_date,
                    or_(
                        AHCIPCode.expiration_date == None,
                        AHCIPCode.expiration_date >= effective_date
                    )
                )
            )
        
        # Get total count
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Apply sorting
        sort_column = getattr(AHCIPCode, sort_by, AHCIPCode.procedure_code)
        if sort_order == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())
        
        # Apply pagination
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        
        result = await self.db.execute(query)
        codes = result.scalars().all()
        
        return list(codes), total
    
    async def search(
        self,
        query_text: str,
        category: Optional[str] = None,
        limit: int = 20
    ) -> List[AHCIPCode]:
        """Search AHCIP codes by text."""
        search_pattern = f"%{query_text.lower()}%"
        
        query = select(AHCIPCode).where(
            and_(
                AHCIPCode.is_active == True,
                or_(
                    func.lower(AHCIPCode.procedure_code).like(search_pattern),
                    func.lower(AHCIPCode.description).like(search_pattern),
                    func.lower(AHCIPCode.short_description).like(search_pattern),
                )
            )
        )
        
        if category:
            query = query.where(AHCIPCode.category == category)
        
        query = query.order_by(AHCIPCode.procedure_code).limit(limit)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_categories(self) -> List[str]:
        """Get all unique categories."""
        result = await self.db.execute(
            select(AHCIPCode.category)
            .where(AHCIPCode.category != None)
            .distinct()
            .order_by(AHCIPCode.category)
        )
        return [row[0] for row in result.fetchall()]
    
    async def update(
        self,
        code_id: UUID,
        data: AHCIPCodeUpdate
    ) -> Optional[AHCIPCode]:
        """Update AHCIP code."""
        code = await self.get_by_id(code_id)
        
        if not code:
            return None
        
        # Update fields
        if data.description is not None:
            code.description = data.description
        if data.short_description is not None:
            code.short_description = data.short_description
        if data.category is not None:
            code.category = data.category
        if data.subcategory is not None:
            code.subcategory = data.subcategory
        if data.fee_amount is not None:
            code.fee_amount = data.fee_amount
        if data.unit_type is not None:
            code.unit_type = data.unit_type
        if data.effective_date is not None:
            code.effective_date = data.effective_date
        if data.expiration_date is not None:
            code.expiration_date = data.expiration_date
        if data.is_active is not None:
            code.is_active = data.is_active
        if data.notes is not None:
            code.notes = data.notes
        if data.requirements is not None:
            code.requirements = data.requirements
        if data.modifiers is not None:
            code.modifiers = data.modifiers
        
        # Regenerate search terms
        code.search_terms = self._generate_search_terms_from_code(code)
        
        await self.db.flush()
        await self.db.refresh(code)
        
        # Invalidate cache
        await cache.delete(f"{CacheKeys.AHCIP_CODES}:{code.procedure_code}")
        
        return code
    
    async def deprecate(
        self,
        code_id: UUID,
        replacement_code: Optional[str] = None
    ) -> Optional[AHCIPCode]:
        """Deprecate an AHCIP code."""
        code = await self.get_by_id(code_id)
        
        if not code:
            return None
        
        code.is_deprecated = True
        code.is_active = False
        code.replacement_code = replacement_code
        
        await self.db.flush()
        await self.db.refresh(code)
        
        # Invalidate cache
        await cache.delete(f"{CacheKeys.AHCIP_CODES}:{code.procedure_code}")
        
        return code
    
    async def delete(self, code_id: UUID) -> bool:
        """Delete AHCIP code."""
        code = await self.get_by_id(code_id)
        
        if not code:
            return False
        
        procedure_code = code.procedure_code
        
        await self.db.delete(code)
        await self.db.flush()
        
        # Invalidate cache
        await cache.delete(f"{CacheKeys.AHCIP_CODES}:{procedure_code}")
        
        return True
    
    async def get_fee(
        self,
        procedure_code: str,
        service_date: Optional[date] = None
    ) -> Optional[Decimal]:
        """Get fee amount for a procedure code on a specific date."""
        check_date = service_date or date.today()
        
        result = await self.db.execute(
            select(AHCIPCode.fee_amount).where(
                and_(
                    AHCIPCode.procedure_code == procedure_code,
                    AHCIPCode.is_active == True,
                    AHCIPCode.effective_date <= check_date,
                    or_(
                        AHCIPCode.expiration_date == None,
                        AHCIPCode.expiration_date >= check_date
                    )
                )
            )
        )
        fee = result.scalar_one_or_none()
        return fee
    
    async def validate_codes(self, codes: List[str], service_date: Optional[date] = None) -> dict:
        """Validate multiple procedure codes.
        
        Returns a dict with valid codes, invalid codes, and deprecated codes.
        """
        check_date = service_date or date.today()
        
        result = {
            "valid": [],
            "invalid": [],
            "deprecated": [],
        }
        
        for code in codes:
            ahcip_code = await self.get_by_procedure_code(code)
            
            if not ahcip_code:
                result["invalid"].append(code)
            elif ahcip_code.is_deprecated:
                result["deprecated"].append({
                    "code": code,
                    "replacement": ahcip_code.replacement_code,
                })
            elif not ahcip_code.is_active:
                result["invalid"].append(code)
            elif ahcip_code.effective_date > check_date:
                result["invalid"].append(code)
            elif ahcip_code.expiration_date and ahcip_code.expiration_date < check_date:
                result["invalid"].append(code)
            else:
                result["valid"].append(code)
        
        return result
    
    def _generate_search_terms(self, data: AHCIPCodeCreate) -> List[str]:
        """Generate search terms from code data."""
        terms = set()
        
        # Add procedure code
        terms.add(data.procedure_code.lower())
        
        # Add words from description
        if data.description:
            terms.update(data.description.lower().split())
        
        # Add words from short description
        if data.short_description:
            terms.update(data.short_description.lower().split())
        
        # Add category
        if data.category:
            terms.add(data.category.lower())
        
        return list(terms)
    
    def _generate_search_terms_from_code(self, code: AHCIPCode) -> List[str]:
        """Generate search terms from existing code."""
        terms = set()
        
        terms.add(code.procedure_code.lower())
        
        if code.description:
            terms.update(code.description.lower().split())
        
        if code.short_description:
            terms.update(code.short_description.lower().split())
        
        if code.category:
            terms.add(code.category.lower())
        
        return list(terms)
