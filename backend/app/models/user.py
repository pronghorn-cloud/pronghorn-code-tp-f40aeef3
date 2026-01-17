"""User Model

User accounts for providers, administrators, adjudicators, and auditors.
"""

import enum
from sqlalchemy import Column, String, Boolean, Enum, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class UserRole(str, enum.Enum):
    """User roles for RBAC."""
    PROVIDER = "provider"
    ADMIN = "admin"
    ADJUDICATOR = "adjudicator"
    AUDITOR = "auditor"


class UserStatus(str, enum.Enum):
    """User account status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"


class User(BaseModel):
    """User model for authentication and authorization."""
    __tablename__ = "users"
    
    # Core fields
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    
    # Profile
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    
    # Role and status
    role = Column(Enum(UserRole), nullable=False, default=UserRole.PROVIDER)
    status = Column(Enum(UserStatus), nullable=False, default=UserStatus.PENDING)
    
    # Provider association (for provider users)
    provider_id = Column(
        UUID(as_uuid=True),
        ForeignKey("providers.id"),
        nullable=True
    )
    
    # Security
    mfa_enabled = Column(Boolean, default=False)
    mfa_secret = Column(String(255), nullable=True)
    last_login = Column(DateTime(timezone=True), nullable=True)
    failed_login_attempts = Column(String(10), default="0")
    locked_until = Column(DateTime(timezone=True), nullable=True)
    
    # Password management
    password_changed_at = Column(DateTime(timezone=True), nullable=True)
    must_change_password = Column(Boolean, default=False)
    
    # Relationships
    provider = relationship("Provider", back_populates="users")
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user")
    
    @property
    def full_name(self) -> str:
        """Get user's full name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.email
    
    def __repr__(self):
        return f"<User {self.email}>"
