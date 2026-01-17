"""Audit Log Model

HIPAA-compliant audit trail for all system actions.
"""

import enum
from sqlalchemy import Column, String, Enum, ForeignKey, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB, INET
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class AuditAction(str, enum.Enum):
    """Audit action types."""
    # Authentication
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    USER_LOGIN_FAILED = "user_login_failed"
    PASSWORD_CHANGED = "password_changed"
    MFA_ENABLED = "mfa_enabled"
    MFA_DISABLED = "mfa_disabled"
    
    # Claims
    CLAIM_CREATED = "claim_created"
    CLAIM_UPDATED = "claim_updated"
    CLAIM_SUBMITTED = "claim_submitted"
    CLAIM_ADJUDICATED = "claim_adjudicated"
    CLAIM_APPROVED = "claim_approved"
    CLAIM_DENIED = "claim_denied"
    CLAIM_DELETED = "claim_deleted"
    
    # PHI Access
    PHI_ACCESSED = "phi_accessed"
    PHI_EXPORTED = "phi_exported"
    
    # Documents
    DOCUMENT_UPLOADED = "document_uploaded"
    DOCUMENT_DOWNLOADED = "document_downloaded"
    DOCUMENT_DELETED = "document_deleted"
    
    # Rules
    RULE_CREATED = "rule_created"
    RULE_UPDATED = "rule_updated"
    RULE_DELETED = "rule_deleted"
    RULE_EXECUTED = "rule_executed"
    
    # Forms
    FORM_CREATED = "form_created"
    FORM_UPDATED = "form_updated"
    TEMPLATE_CREATED = "template_created"
    TEMPLATE_UPDATED = "template_updated"
    
    # Admin
    USER_CREATED = "user_created"
    USER_UPDATED = "user_updated"
    USER_DELETED = "user_deleted"
    SETTINGS_CHANGED = "settings_changed"


class AuditLog(BaseModel):
    """Audit log entry for HIPAA compliance."""
    __tablename__ = "audit_logs"
    
    # Action details
    action = Column(Enum(AuditAction), nullable=False, index=True)
    action_description = Column(Text, nullable=True)
    
    # Related entities
    claim_id = Column(
        UUID(as_uuid=True),
        ForeignKey("claims.id"),
        nullable=True,
        index=True
    )
    rule_id = Column(
        UUID(as_uuid=True),
        ForeignKey("rules.id"),
        nullable=True
    )
    document_id = Column(
        UUID(as_uuid=True),
        ForeignKey("documents.id"),
        nullable=True
    )
    
    # User who performed action
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
        index=True
    )
    
    # Execution details (for rules)
    execution_result = Column(String(50), nullable=True)
    decision_rationale = Column(Text, nullable=True)
    
    # Request context
    ip_address = Column(INET, nullable=True)
    user_agent = Column(String(500), nullable=True)
    correlation_id = Column(String(100), nullable=True, index=True)
    
    # PHI tracking
    phi_accessed = Column(Boolean, default=False)
    masked_fields = Column(JSONB, nullable=True, default=list)
    
    # Additional context
    metadata = Column(JSONB, nullable=True, default=dict)
    before_state = Column(JSONB, nullable=True)  # State before change
    after_state = Column(JSONB, nullable=True)   # State after change
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")
    claim = relationship("Claim", back_populates="audit_logs")
    rule = relationship("Rule", back_populates="audit_logs")
    
    def __repr__(self):
        return f"<AuditLog {self.action.value} by {self.user_id}>"
