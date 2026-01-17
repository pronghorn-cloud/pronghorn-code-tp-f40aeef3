"""Forms & Templates Endpoints

Handles form definitions and template management.
"""

from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.schemas.form import (
    FormDefinitionCreate,
    FormDefinitionUpdate,
    FormDefinitionResponse,
    FormDefinitionListResponse,
    FormTemplateCreate,
    FormTemplateUpdate,
    FormTemplateResponse,
    FormTemplateListResponse,
    FormTemplateDuplicate,
)
from app.schemas.common import SuccessResponse, PaginationMeta
from app.services.form_service import FormService
from app.services.audit_service import AuditService
from app.models.audit import AuditAction
from app.models.user import UserRole

router = APIRouter()


def check_admin(user):
    """Check if user has admin role."""
    if user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )


# ==================== Form Definitions ====================

@router.post("/definitions", response_model=FormDefinitionResponse, status_code=status.HTTP_201_CREATED)
async def create_form_definition(
    form_data: FormDefinitionCreate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new form definition (admin only)."""
    check_admin(current_user)
    
    form_service = FormService(db)
    audit_service = AuditService(db)
    
    # Check for duplicate code
    existing = await form_service.get_definition_by_code(form_data.form_code)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Form code already exists"
        )
    
    # Create form definition
    form = await form_service.create_definition(form_data, created_by=current_user.id)
    
    # Log creation
    await audit_service.log(
        action=AuditAction.FORM_CREATED,
        user_id=current_user.id,
        metadata={"form_code": form.form_code}
    )
    
    return FormDefinitionResponse.model_validate(form)


@router.get("/definitions", response_model=FormDefinitionListResponse)
async def list_form_definitions(
    is_active: Optional[bool] = None,
    category: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List form definitions."""
    form_service = FormService(db)
    
    forms, total = await form_service.list_definitions(
        is_active=is_active,
        category=category,
        page=page,
        page_size=page_size
    )
    
    total_pages = (total + page_size - 1) // page_size
    
    return FormDefinitionListResponse(
        data=[FormDefinitionResponse.model_validate(f) for f in forms],
        meta=PaginationMeta(
            page=page,
            page_size=page_size,
            total_items=total,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1,
        )
    )


@router.get("/definitions/{form_id}", response_model=FormDefinitionResponse)
async def get_form_definition(
    form_id: UUID,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get form definition details."""
    form_service = FormService(db)
    
    form = await form_service.get_definition_by_id(form_id)
    
    if not form:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Form definition not found"
        )
    
    return FormDefinitionResponse.model_validate(form)


@router.put("/definitions/{form_id}", response_model=FormDefinitionResponse)
async def update_form_definition(
    form_id: UUID,
    form_data: FormDefinitionUpdate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update form definition (admin only)."""
    check_admin(current_user)
    
    form_service = FormService(db)
    audit_service = AuditService(db)
    
    form = await form_service.get_definition_by_id(form_id)
    
    if not form:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Form definition not found"
        )
    
    # Update form
    updated_form = await form_service.update_definition(form_id, form_data)
    
    # Log update
    await audit_service.log(
        action=AuditAction.FORM_UPDATED,
        user_id=current_user.id,
        metadata={"form_code": form.form_code}
    )
    
    return FormDefinitionResponse.model_validate(updated_form)


# ==================== Form Templates ====================

@router.post("/templates", response_model=FormTemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(
    template_data: FormTemplateCreate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new form template (admin only)."""
    check_admin(current_user)
    
    form_service = FormService(db)
    audit_service = AuditService(db)
    
    # Verify form definition exists
    form = await form_service.get_definition_by_id(template_data.form_id)
    if not form:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Form definition not found"
        )
    
    # Create template
    template = await form_service.create_template(template_data, created_by=current_user.id)
    
    # Log creation
    await audit_service.log(
        action=AuditAction.TEMPLATE_CREATED,
        user_id=current_user.id,
        metadata={"template_name": template.template_name}
    )
    
    return FormTemplateResponse.model_validate(template)


@router.get("/templates", response_model=FormTemplateListResponse)
async def list_templates(
    form_id: Optional[UUID] = None,
    is_active: Optional[bool] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List form templates."""
    form_service = FormService(db)
    
    templates, total = await form_service.list_templates(
        form_id=form_id,
        is_active=is_active,
        page=page,
        page_size=page_size
    )
    
    total_pages = (total + page_size - 1) // page_size
    
    return FormTemplateListResponse(
        data=[FormTemplateResponse.model_validate(t) for t in templates],
        meta=PaginationMeta(
            page=page,
            page_size=page_size,
            total_items=total,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1,
        )
    )


@router.get("/templates/{template_id}", response_model=FormTemplateResponse)
async def get_template(
    template_id: UUID,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get template details."""
    form_service = FormService(db)
    
    template = await form_service.get_template_by_id(template_id)
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    return FormTemplateResponse.model_validate(template)


@router.put("/templates/{template_id}", response_model=FormTemplateResponse)
async def update_template(
    template_id: UUID,
    template_data: FormTemplateUpdate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update template (admin only)."""
    check_admin(current_user)
    
    form_service = FormService(db)
    audit_service = AuditService(db)
    
    template = await form_service.get_template_by_id(template_id)
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    # Update template (creates new version)
    updated_template = await form_service.update_template(template_id, template_data)
    
    # Log update
    await audit_service.log(
        action=AuditAction.TEMPLATE_UPDATED,
        user_id=current_user.id,
        metadata={"template_name": template.template_name, "new_version": updated_template.version}
    )
    
    return FormTemplateResponse.model_validate(updated_template)


@router.post("/templates/{template_id}/duplicate", response_model=FormTemplateResponse)
async def duplicate_template(
    template_id: UUID,
    duplicate_data: FormTemplateDuplicate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Duplicate a template (admin only)."""
    check_admin(current_user)
    
    form_service = FormService(db)
    
    template = await form_service.get_template_by_id(template_id)
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    # Duplicate template
    new_template = await form_service.duplicate_template(
        template_id,
        new_name=duplicate_data.new_template_name,
        notes=duplicate_data.notes,
        created_by=current_user.id
    )
    
    return FormTemplateResponse.model_validate(new_template)


@router.get("/templates/{template_id}/versions", response_model=FormTemplateListResponse)
async def get_template_versions(
    template_id: UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get template version history."""
    form_service = FormService(db)
    
    versions, total = await form_service.get_template_versions(
        template_id,
        page=page,
        page_size=page_size
    )
    
    total_pages = (total + page_size - 1) // page_size
    
    return FormTemplateListResponse(
        data=[FormTemplateResponse.model_validate(v) for v in versions],
        meta=PaginationMeta(
            page=page,
            page_size=page_size,
            total_items=total,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1,
        )
    )
