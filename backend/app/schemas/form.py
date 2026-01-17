"""Form Schemas

Pydantic models for form definitions and templates API.
"""

from typing import Optional, List, Any
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID

from app.schemas.common import BaseSchema, PaginationMeta


class FieldDefinition(BaseModel):
    """Form field definition."""
    field_id: str = Field(..., max_length=100)
    field_name: str = Field(..., max_length=255)
    field_type: str = Field(..., pattern=r"^(text|textarea|number|date|select|checkbox|radio|ahcip_code|file)$")
    label: str
    placeholder: Optional[str] = None
    required: bool = False
    is_phi: bool = False  # Protected Health Information flag
    validation: Optional[dict] = None  # Validation rules
    options: Optional[List[dict]] = None  # For select/radio fields
    default_value: Optional[Any] = None
    help_text: Optional[str] = None
    order: int = 0
    section: Optional[str] = None


class ValidationRule(BaseModel):
    """Field validation rule."""
    type: str = Field(..., pattern=r"^(required|min|max|pattern|email|phone|date|custom)$")
    value: Optional[Any] = None
    message: str


class FormDefinitionCreate(BaseModel):
    """Schema for creating a form definition."""
    form_name: str = Field(..., max_length=255)
    form_code: str = Field(..., max_length=50, pattern=r"^[A-Z0-9_]+$")
    description: Optional[str] = None
    field_definitions: List[FieldDefinition]
    validation_rules: Optional[List[dict]] = None
    layout_config: Optional[dict] = None
    category: Optional[str] = None
    claim_type: Optional[str] = None


class FormDefinitionUpdate(BaseModel):
    """Schema for updating a form definition."""
    form_name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    field_definitions: Optional[List[FieldDefinition]] = None
    validation_rules: Optional[List[dict]] = None
    layout_config: Optional[dict] = None
    is_active: Optional[bool] = None
    category: Optional[str] = None
    claim_type: Optional[str] = None


class FormDefinitionResponse(BaseSchema):
    """Form definition response schema."""
    id: UUID
    form_name: str
    form_code: str
    description: Optional[str]
    field_definitions: List[dict]
    validation_rules: Optional[List[dict]]
    layout_config: Optional[dict]
    is_active: bool
    category: Optional[str]
    claim_type: Optional[str]
    created_at: datetime
    updated_at: datetime


class FormDefinitionListResponse(BaseModel):
    """Paginated form definition list response."""
    data: List[FormDefinitionResponse]
    meta: PaginationMeta


class FormTemplateCreate(BaseModel):
    """Schema for creating a form template."""
    form_id: UUID
    template_name: str = Field(..., max_length=255)
    field_overrides: Optional[dict] = None
    additional_fields: Optional[List[FieldDefinition]] = None
    metadata: Optional[dict] = None
    notes: Optional[str] = None
    is_default: bool = False


class FormTemplateUpdate(BaseModel):
    """Schema for updating a form template."""
    template_name: Optional[str] = Field(None, max_length=255)
    field_overrides: Optional[dict] = None
    additional_fields: Optional[List[FieldDefinition]] = None
    metadata: Optional[dict] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None


class FormTemplateResponse(BaseSchema):
    """Form template response schema."""
    id: UUID
    form_id: UUID
    template_name: str
    version: int
    field_overrides: Optional[dict]
    additional_fields: Optional[List[dict]]
    metadata: Optional[dict]
    notes: Optional[str]
    is_active: bool
    is_default: bool
    created_at: datetime
    updated_at: datetime


class FormTemplateListResponse(BaseModel):
    """Paginated form template list response."""
    data: List[FormTemplateResponse]
    meta: PaginationMeta


class FormTemplateDuplicate(BaseModel):
    """Schema for duplicating a template."""
    new_template_name: str = Field(..., max_length=255)
    notes: Optional[str] = None
