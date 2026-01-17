"""Provider Model

Healthcare providers who submit claims.
"""

import enum
from sqlalchemy import Column, String, Enum, Text
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class ProviderStatus(str, enum.Enum):
    """Provider status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING_VERIFICATION = "pending_verification"


class Provider(BaseModel):
    """Healthcare provider model."""
    __tablename__ = "providers"
    
    # NPI - National Provider Identifier
    npi_number = Column(String(20), unique=True, nullable=False, index=True)
    
    # Provider information
    provider_name = Column(String(255), nullable=False)
    organization = Column(String(255), nullable=True)
    
    # Contact information
    address_line1 = Column(String(255), nullable=True)
    address_line2 = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    province = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    country = Column(String(100), default="Canada")
    
    contact_email = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=True)
    fax = Column(String(50), nullable=True)
    
    # Status
    status = Column(
        Enum(ProviderStatus),
        nullable=False,
        default=ProviderStatus.PENDING_VERIFICATION
    )
    
    # Additional information
    specialty = Column(String(100), nullable=True)
    license_number = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    users = relationship("User", back_populates="provider")
    claims = relationship("Claim", back_populates="provider")
    
    def __repr__(self):
        return f"<Provider {self.provider_name} ({self.npi_number})>"
