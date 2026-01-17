"""Rule Model

Adjudication rules and rule versions for claims processing.
"""

import enum
from sqlalchemy import Column, String, Enum, ForeignKey, Integer, Boolean, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class RuleType(str, enum.Enum):
    """Rule type categories."""
    VALIDATION = "validation"
    ADJUDICATION = "adjudication"
    CALCULATION = "calculation"
    NOTIFICATION = "notification"


class ActionType(str, enum.Enum):
    """Rule action types."""
    APPROVE = "approve"
    DENY = "deny"
    FLAG = "flag"
    CALCULATE = "calculate"
    NOTIFY = "notify"
    TRANSFORM = "transform"


class Rule(BaseModel):
    """Adjudication rule model."""
    __tablename__ = "rules"
    
    # Rule identification
    rule_name = Column(String(255), nullable=False)
    rule_code = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Rule type and action
    rule_type = Column(
        Enum(RuleType),
        nullable=False,
        default=RuleType.VALIDATION,
        index=True
    )
    action_type = Column(
        Enum(ActionType),
        nullable=False,
        default=ActionType.FLAG
    )
    
    # Rule logic (JSON structure for conditions)
    condition_logic = Column(JSONB, nullable=False, default=dict)
    
    # Priority (lower number = higher priority)
    priority = Column(Integer, nullable=False, default=100)
    
    # Status
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    
    # Effective dates
    effective_from = Column(DateTime(timezone=True), nullable=True)
    effective_to = Column(DateTime(timezone=True), nullable=True)
    
    # Configuration
    denial_reason_template = Column(Text, nullable=True)
    flag_reason_template = Column(Text, nullable=True)
    
    # Metadata
    category = Column(String(100), nullable=True)
    tags = Column(JSONB, nullable=True, default=list)
    
    # Audit
    created_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True
    )
    last_modified_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True
    )
    
    # Relationships
    versions = relationship("RuleVersion", back_populates="rule", cascade="all, delete-orphan")
    creator = relationship("User", foreign_keys=[created_by])
    modifier = relationship("User", foreign_keys=[last_modified_by])
    audit_logs = relationship("AuditLog", back_populates="rule")
    
    def __repr__(self):
        return f"<Rule {self.rule_code}: {self.rule_name}>"


class RuleVersion(BaseModel):
    """Rule version history for audit trail."""
    __tablename__ = "rule_versions"
    
    # Rule relationship
    rule_id = Column(
        UUID(as_uuid=True),
        ForeignKey("rules.id"),
        nullable=False,
        index=True
    )
    
    # Version number
    version_number = Column(Integer, nullable=False)
    
    # Snapshot of rule at this version
    rule_name = Column(String(255), nullable=False)
    rule_type = Column(Enum(RuleType), nullable=False)
    action_type = Column(Enum(ActionType), nullable=False)
    condition_logic = Column(JSONB, nullable=False)
    priority = Column(Integer, nullable=False)
    
    # Version metadata
    change_description = Column(Text, nullable=True)
    effective_from = Column(DateTime(timezone=True), nullable=True)
    
    # Audit
    created_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True
    )
    
    # Relationships
    rule = relationship("Rule", back_populates="versions")
    creator = relationship("User")
    
    def __repr__(self):
        return f"<RuleVersion {self.rule_id} v{self.version_number}>"
