"""Claim Model

Healthcare claims with fields and status tracking.
"""

import enum
from sqlalchemy import Column, String, Enum, ForeignKey, DateTime, Numeric, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class ClaimStatus(str, enum.Enum):
    """Claim status values."""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    IN_REVIEW = "in_review"
    ADJUDICATED = "adjudicated"
    APPROVED = "approved"
    DENIED = "denied"
    PAID = "paid"
    APPEALED = "appealed"
    CANCELLED = "cancelled"


class Claim(BaseModel):
    """Healthcare claim model."""
    __tablename__ = "claims"
    
    # Provider relationship
    provider_id = Column(
        UUID(as_uuid=True),
        ForeignKey("providers.id"),
        nullable=False,
        index=True
    )
    
    # Claim reference number (human-readable)
    claim_number = Column(String(50), unique=True, nullable=False, index=True)
    
    # Patient information (encrypted/hashed for HIPAA)
    patient_id_hash = Column(String(64), nullable=True, index=True)
    patient_info_encrypted = Column(Text, nullable=True)  # Encrypted PHI
    
    # Service information
    service_date = Column(DateTime(timezone=True), nullable=True)
    service_end_date = Column(DateTime(timezone=True), nullable=True)
    
    # Form template used
    template_id = Column(
        UUID(as_uuid=True),
        ForeignKey("form_templates.id"),
        nullable=True
    )
    
    # Claim status
    status = Column(
        Enum(ClaimStatus),
        nullable=False,
        default=ClaimStatus.DRAFT,
        index=True
    )
    
    # Financial
    total_amount = Column(Numeric(10, 2), nullable=True)
    approved_amount = Column(Numeric(10, 2), nullable=True)
    
    # Service lines (stored as JSON for flexibility)
    service_lines = Column(JSONB, nullable=True, default=list)
    
    # Timestamps
    submitted_at = Column(DateTime(timezone=True), nullable=True, index=True)
    adjudicated_at = Column(DateTime(timezone=True), nullable=True)
    paid_at = Column(DateTime(timezone=True), nullable=True)
    
    # Notes and reasons
    denial_reason = Column(Text, nullable=True)
    internal_notes = Column(Text, nullable=True)
    
    # Relationships
    provider = relationship("Provider", back_populates="claims")
    template = relationship("FormTemplate")
    fields = relationship("ClaimField", back_populates="claim", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="claim", cascade="all, delete-orphan")
    adjudication_result = relationship("AdjudicationResult", back_populates="claim", uselist=False)
    audit_logs = relationship("AuditLog", back_populates="claim")
    
    def __repr__(self):
        return f"<Claim {self.claim_number} ({self.status.value})>"


class ClaimField(BaseModel):
    """Individual field values for a claim."""
    __tablename__ = "claim_fields"
    
    # Claim relationship
    claim_id = Column(
        UUID(as_uuid=True),
        ForeignKey("claims.id"),
        nullable=False,
        index=True
    )
    
    # Field definition reference
    field_definition_id = Column(String(100), nullable=False)
    field_name = Column(String(255), nullable=False)
    
    # Field value (stored as text, type determined by field definition)
    field_value = Column(Text, nullable=True)
    field_value_encrypted = Column(Text, nullable=True)  # For PHI fields
    
    # Metadata
    is_phi = Column(String(5), default="false")  # Flag for PHI fields
    
    # Relationships
    claim = relationship("Claim", back_populates="fields")
    
    def __repr__(self):
        return f"<ClaimField {self.field_name}>"
