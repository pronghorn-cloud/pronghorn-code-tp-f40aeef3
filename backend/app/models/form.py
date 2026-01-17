"""Form and Template Models

Form definitions and templates for claim submissions.
"""

from sqlalchemy import Column, String, Boolean, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class FormDefinition(BaseModel):
    """Form definition with field configurations."""
    __tablename__ = "form_definitions"
    
    # Form identification
    form_name = Column(String(255), nullable=False)
    form_code = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Field definitions (JSON schema)
    field_definitions = Column(JSONB, nullable=False, default=list)
    
    # Validation rules (JSON)
    validation_rules = Column(JSONB, nullable=True, default=list)
    
    # Layout configuration
    layout_config = Column(JSONB, nullable=True, default=dict)
    
    # Status
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    
    # Categorization
    category = Column(String(100), nullable=True)
    claim_type = Column(String(100), nullable=True)  # Type of claims this form handles
    
    # Metadata
    created_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True
    )
    
    # Relationships
    templates = relationship("FormTemplate", back_populates="form_definition")
    creator = relationship("User")
    
    def __repr__(self):
        return f"<FormDefinition {self.form_code}: {self.form_name}>"


class FormTemplate(BaseModel):
    """Versioned form template."""
    __tablename__ = "form_templates"
    
    # Form definition relationship
    form_id = Column(
        UUID(as_uuid=True),
        ForeignKey("form_definitions.id"),
        nullable=False,
        index=True
    )
    
    # Template identification
    template_name = Column(String(255), nullable=False)
    version = Column(Integer, nullable=False, default=1)
    
    # Template configuration (can override form definition)
    field_overrides = Column(JSONB, nullable=True, default=dict)
    additional_fields = Column(JSONB, nullable=True, default=list)
    
    # Metadata
    metadata = Column(JSONB, nullable=True, default=dict)
    notes = Column(Text, nullable=True)
    
    # Status
    is_active = Column(Boolean, nullable=False, default=True)
    is_default = Column(Boolean, nullable=False, default=False)
    
    # Audit
    created_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True
    )
    
    # Relationships
    form_definition = relationship("FormDefinition", back_populates="templates")
    creator = relationship("User")
    
    def __repr__(self):
        return f"<FormTemplate {self.template_name} v{self.version}>"
