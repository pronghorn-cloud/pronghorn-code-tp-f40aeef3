"""Session Model

User session management for security and audit.
"""

from sqlalchemy import Column, String, ForeignKey, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID, INET
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class Session(BaseModel):
    """User session model."""
    __tablename__ = "sessions"
    
    # User relationship
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )
    
    # Token information
    token_hash = Column(String(255), nullable=False, index=True)
    refresh_token_hash = Column(String(255), nullable=True)
    
    # Session timing
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    last_activity = Column(DateTime(timezone=True), nullable=True)
    
    # Client information
    ip_address = Column(INET, nullable=True)
    user_agent = Column(String(500), nullable=True)
    device_info = Column(String(255), nullable=True)
    
    # Session status
    is_active = Column(Boolean, nullable=False, default=True)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    revoke_reason = Column(String(255), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    
    def __repr__(self):
        return f"<Session {self.user_id} active={self.is_active}>"
