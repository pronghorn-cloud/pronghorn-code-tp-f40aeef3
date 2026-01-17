"""AHCIP Code Model

Alberta Health Care Insurance Plan procedure codes and fee schedules.
"""

from sqlalchemy import Column, String, Numeric, Date, Boolean, Text
from sqlalchemy.dialects.postgresql import JSONB

from app.models.base import BaseModel


class AHCIPCode(BaseModel):
    """AHCIP procedure code with fee schedule."""
    __tablename__ = "ahcip_codes"
    
    # Code identification
    procedure_code = Column(String(20), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=False)
    short_description = Column(String(255), nullable=True)
    
    # Categorization
    category = Column(String(100), nullable=True, index=True)
    subcategory = Column(String(100), nullable=True)
    
    # Fee information
    fee_amount = Column(Numeric(10, 2), nullable=False)
    unit_type = Column(String(50), nullable=True)  # per visit, per unit, etc.
    
    # Effective dates
    effective_date = Column(Date, nullable=False, index=True)
    expiration_date = Column(Date, nullable=True)
    
    # Status
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    is_deprecated = Column(Boolean, nullable=False, default=False)
    
    # Replacement code (if deprecated)
    replacement_code = Column(String(20), nullable=True)
    
    # Additional information
    notes = Column(Text, nullable=True)
    requirements = Column(JSONB, nullable=True, default=list)  # Required documentation
    modifiers = Column(JSONB, nullable=True, default=list)  # Applicable modifiers
    
    # Search optimization
    search_terms = Column(JSONB, nullable=True, default=list)
    
    def __repr__(self):
        return f"<AHCIPCode {self.procedure_code}: {self.short_description or self.description[:50]}>"
