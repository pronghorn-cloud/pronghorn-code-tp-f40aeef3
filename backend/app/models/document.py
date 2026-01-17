"""Document Model

Supporting documents attached to claims.
"""

import enum
from sqlalchemy import Column, String, Enum, ForeignKey, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class DocumentType(str, enum.Enum):
    """Document type categories."""
    MEDICAL_RECORD = "medical_record"
    LAB_RESULT = "lab_result"
    PRESCRIPTION = "prescription"
    REFERRAL = "referral"
    AUTHORIZATION = "authorization"
    INVOICE = "invoice"
    OTHER = "other"


class DocumentStatus(str, enum.Enum):
    """Document status."""
    PENDING = "pending"
    UPLOADED = "uploaded"
    VERIFIED = "verified"
    REJECTED = "rejected"
    DELETED = "deleted"


class Document(BaseModel):
    """Document attachment model."""
    __tablename__ = "documents"
    
    # Claim relationship
    claim_id = Column(
        UUID(as_uuid=True),
        ForeignKey("claims.id"),
        nullable=False,
        index=True
    )
    
    # File information
    original_filename = Column(String(255), nullable=False)
    file_reference = Column(String(500), nullable=False)  # S3 key or path
    file_type = Column(String(100), nullable=False)  # MIME type
    file_size = Column(Integer, nullable=False)  # Size in bytes
    
    # Document metadata
    document_type = Column(
        Enum(DocumentType),
        nullable=False,
        default=DocumentType.OTHER
    )
    description = Column(String(500), nullable=True)
    
    # Status
    status = Column(
        Enum(DocumentStatus),
        nullable=False,
        default=DocumentStatus.PENDING
    )
    
    # Upload tracking
    uploaded_at = Column(DateTime(timezone=True), nullable=True)
    uploaded_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True
    )
    
    # Verification
    verified_at = Column(DateTime(timezone=True), nullable=True)
    verified_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True
    )
    
    # Security
    checksum = Column(String(64), nullable=True)  # SHA-256 hash
    virus_scan_result = Column(String(50), nullable=True)
    virus_scan_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    claim = relationship("Claim", back_populates="documents")
    uploader = relationship("User", foreign_keys=[uploaded_by])
    verifier = relationship("User", foreign_keys=[verified_by])
    
    def __repr__(self):
        return f"<Document {self.original_filename}>"
