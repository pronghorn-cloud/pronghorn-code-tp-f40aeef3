"""Adjudication Result Model

Results of automated and manual claim adjudication.
"""

import enum
from sqlalchemy import Column, String, Enum, ForeignKey, Numeric, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class AdjudicationStatus(str, enum.Enum):
    """Adjudication result status."""
    PENDING = "pending"
    PROCESSING = "processing"
    APPROVED = "approved"
    DENIED = "denied"
    PARTIAL_APPROVAL = "partial_approval"
    FLAGGED = "flagged"
    MANUAL_REVIEW = "manual_review"
    ERROR = "error"


class AdjudicationResult(BaseModel):
    """Claim adjudication result."""
    __tablename__ = "adjudication_results"
    
    # Claim relationship
    claim_id = Column(
        UUID(as_uuid=True),
        ForeignKey("claims.id"),
        nullable=False,
        unique=True,
        index=True
    )
    
    # Result status
    status = Column(
        Enum(AdjudicationStatus),
        nullable=False,
        default=AdjudicationStatus.PENDING,
        index=True
    )
    
    # Financial results
    submitted_amount = Column(Numeric(10, 2), nullable=True)
    approved_amount = Column(Numeric(10, 2), nullable=True)
    adjustment_amount = Column(Numeric(10, 2), nullable=True)
    
    # Payment details
    payment_amount = Column(Numeric(10, 2), nullable=True)
    payment_date = Column(DateTime(timezone=True), nullable=True)
    
    # Decision details
    denial_reason = Column(Text, nullable=True)
    denial_code = Column(String(50), nullable=True)
    flag_reason = Column(Text, nullable=True)
    
    # Rules applied (JSON array of rule executions)
    rules_applied = Column(JSONB, nullable=True, default=list)
    
    # Processing information
    processed_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True
    )
    processed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Manual review (if applicable)
    reviewed_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True
    )
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    review_notes = Column(Text, nullable=True)
    
    # Additional details
    line_item_results = Column(JSONB, nullable=True, default=list)
    metadata = Column(JSONB, nullable=True, default=dict)
    
    # Relationships
    claim = relationship("Claim", back_populates="adjudication_result")
    processor = relationship("User", foreign_keys=[processed_by])
    reviewer = relationship("User", foreign_keys=[reviewed_by])
    
    def __repr__(self):
        return f"<AdjudicationResult {self.claim_id}: {self.status.value}>"
