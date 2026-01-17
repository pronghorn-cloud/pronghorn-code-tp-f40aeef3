"""Form Service

Business logic for form definitions and templates.
"""

from typing import Optional, Tuple, List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.form import FormDefinition, FormTemplate
from app.schemas.form import (
    FormDefinitionCreate,
    FormDefinitionUpdate,
    FormTemplateCreate,
    FormTemplateUpdate,
)


class FormService:
    """Service for form management operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # ==================== Form Definitions ====================
    
    async def create_definition(
        self,
        data: FormDefinitionCreate,
        created_by: UUID
    ) -> FormDefinition:
        """Create a new form definition."""
        form = FormDefinition(
            form_name=data.form_name,
            form_code=data.form_code,
            description=data.description,
            field_definitions=[f.model_dump() for f in data.field_definitions],
            validation_rules=data.validation_rules,
            layout_config=data.layout_config,
            category=data.category,
            claim_type=data.claim_type,
            is_active=True,
            created_by=created_by,
        )
        
        self.db.add(form)
        await self.db.flush()
        await self.db.refresh(form)
        
        return form
    
    async def get_definition_by_id(self, form_id: UUID) -> Optional[FormDefinition]:
        """Get form definition by ID."""
        result = await self.db.execute(
            select(FormDefinition).where(FormDefinition.id == form_id)
        )
        return result.scalar_one_or_none()
    
    async def get_definition_by_code(self, form_code: str) -> Optional[FormDefinition]:
        """Get form definition by code."""
        result = await self.db.execute(
            select(FormDefinition).where(FormDefinition.form_code == form_code)
        )
        return result.scalar_one_or_none()
    
    async def list_definitions(
        self,
        is_active: Optional[bool] = None,
        category: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[FormDefinition], int]:
        """List form definitions."""
        query = select(FormDefinition)
        count_query = select(func.count(FormDefinition.id))
        
        if is_active is not None:
            query = query.where(FormDefinition.is_active == is_active)
            count_query = count_query.where(FormDefinition.is_active == is_active)
        
        if category:
            query = query.where(FormDefinition.category == category)
            count_query = count_query.where(FormDefinition.category == category)
        
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        query = query.order_by(FormDefinition.form_name)
        
        result = await self.db.execute(query)
        forms = result.scalars().all()
        
        return list(forms), total
    
    async def update_definition(
        self,
        form_id: UUID,
        data: FormDefinitionUpdate
    ) -> Optional[FormDefinition]:
        """Update form definition."""
        form = await self.get_definition_by_id(form_id)
        
        if not form:
            return None
        
        update_data = data.model_dump(exclude_unset=True)
        
        if "field_definitions" in update_data:
            update_data["field_definitions"] = [
                f.model_dump() if hasattr(f, 'model_dump') else f
                for f in update_data["field_definitions"]
            ]
        
        for field, value in update_data.items():
            setattr(form, field, value)
        
        await self.db.flush()
        await self.db.refresh(form)
        
        return form
    
    # ==================== Form Templates ====================
    
    async def create_template(
        self,
        data: FormTemplateCreate,
        created_by: UUID
    ) -> FormTemplate:
        """Create a new form template."""
        template = FormTemplate(
            form_id=data.form_id,
            template_name=data.template_name,
            version=1,
            field_overrides=data.field_overrides,
            additional_fields=[
                f.model_dump() for f in data.additional_fields
            ] if data.additional_fields else None,
            metadata=data.metadata,
            notes=data.notes,
            is_default=data.is_default,
            is_active=True,
            created_by=created_by,
        )
        
        self.db.add(template)
        await self.db.flush()
        await self.db.refresh(template)
        
        return template
    
    async def get_template_by_id(self, template_id: UUID) -> Optional[FormTemplate]:
        """Get template by ID."""
        result = await self.db.execute(
            select(FormTemplate).where(FormTemplate.id == template_id)
        )
        return result.scalar_one_or_none()
    
    async def list_templates(
        self,
        form_id: Optional[UUID] = None,
        is_active: Optional[bool] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[FormTemplate], int]:
        """List form templates."""
        query = select(FormTemplate)
        count_query = select(func.count(FormTemplate.id))
        
        if form_id:
            query = query.where(FormTemplate.form_id == form_id)
            count_query = count_query.where(FormTemplate.form_id == form_id)
        
        if is_active is not None:
            query = query.where(FormTemplate.is_active == is_active)
            count_query = count_query.where(FormTemplate.is_active == is_active)
        
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        query = query.order_by(FormTemplate.template_name)
        
        result = await self.db.execute(query)
        templates = result.scalars().all()
        
        return list(templates), total
    
    async def update_template(
        self,
        template_id: UUID,
        data: FormTemplateUpdate
    ) -> Optional[FormTemplate]:
        """Update template (creates new version)."""
        template = await self.get_template_by_id(template_id)
        
        if not template:
            return None
        
        # Increment version
        template.version += 1
        
        update_data = data.model_dump(exclude_unset=True)
        
        if "additional_fields" in update_data and update_data["additional_fields"]:
            update_data["additional_fields"] = [
                f.model_dump() if hasattr(f, 'model_dump') else f
                for f in update_data["additional_fields"]
            ]
        
        for field, value in update_data.items():
            setattr(template, field, value)
        
        await self.db.flush()
        await self.db.refresh(template)
        
        return template
    
    async def duplicate_template(
        self,
        template_id: UUID,
        new_name: str,
        notes: Optional[str],
        created_by: UUID
    ) -> Optional[FormTemplate]:
        """Duplicate a template."""
        original = await self.get_template_by_id(template_id)
        
        if not original:
            return None
        
        new_template = FormTemplate(
            form_id=original.form_id,
            template_name=new_name,
            version=1,
            field_overrides=original.field_overrides,
            additional_fields=original.additional_fields,
            metadata=original.metadata,
            notes=notes or f"Duplicated from {original.template_name}",
            is_default=False,
            is_active=True,
            created_by=created_by,
        )
        
        self.db.add(new_template)
        await self.db.flush()
        await self.db.refresh(new_template)
        
        return new_template
    
    async def get_template_versions(
        self,
        template_id: UUID,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[FormTemplate], int]:
        """Get template version history."""
        # In a real implementation, this would query a versions table
        # For now, return the current template
        template = await self.get_template_by_id(template_id)
        
        if not template:
            return [], 0
        
        return [template], 1
