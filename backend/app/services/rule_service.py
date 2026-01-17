"""Rule Service

Business logic for adjudication rules management.
"""

from typing import Optional, Tuple, List
from uuid import UUID
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload

from app.models.rule import Rule, RuleVersion, RuleType, ActionType
from app.schemas.rule import RuleCreate, RuleUpdate
from app.core.cache import cache, CacheKeys


class RuleService:
    """Service for adjudication rules management."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(
        self,
        data: RuleCreate,
        created_by: UUID
    ) -> Rule:
        """Create a new adjudication rule."""
        # Generate unique rule code if not provided
        rule_code = data.rule_code or await self._generate_rule_code(data.rule_type)
        
        rule = Rule(
            rule_name=data.rule_name,
            rule_code=rule_code,
            description=data.description,
            rule_type=data.rule_type,
            action_type=data.action_type,
            condition_logic=data.condition_logic or {},
            priority=data.priority or 100,
            is_active=data.is_active if data.is_active is not None else True,
            effective_from=data.effective_from,
            effective_to=data.effective_to,
            denial_reason_template=data.denial_reason_template,
            flag_reason_template=data.flag_reason_template,
            category=data.category,
            tags=data.tags or [],
            created_by=created_by,
            last_modified_by=created_by,
        )
        
        self.db.add(rule)
        await self.db.flush()
        await self.db.refresh(rule)
        
        # Create initial version
        await self._create_version(rule, created_by, "Initial version")
        
        # Invalidate cache
        await cache.delete(CacheKeys.ACTIVE_RULES)
        
        return rule
    
    async def get_by_id(self, rule_id: UUID) -> Optional[Rule]:
        """Get rule by ID with versions."""
        result = await self.db.execute(
            select(Rule)
            .options(selectinload(Rule.versions))
            .where(Rule.id == rule_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_code(self, rule_code: str) -> Optional[Rule]:
        """Get rule by code."""
        result = await self.db.execute(
            select(Rule).where(Rule.rule_code == rule_code)
        )
        return result.scalar_one_or_none()
    
    async def list(
        self,
        rule_type: Optional[RuleType] = None,
        is_active: Optional[bool] = None,
        category: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
        sort_by: str = "priority",
        sort_order: str = "asc"
    ) -> Tuple[List[Rule], int]:
        """List rules with filtering and pagination."""
        query = select(Rule)
        count_query = select(func.count(Rule.id))
        
        # Apply filters
        if rule_type:
            query = query.where(Rule.rule_type == rule_type)
            count_query = count_query.where(Rule.rule_type == rule_type)
        
        if is_active is not None:
            query = query.where(Rule.is_active == is_active)
            count_query = count_query.where(Rule.is_active == is_active)
        
        if category:
            query = query.where(Rule.category == category)
            count_query = count_query.where(Rule.category == category)
        
        # Get total count
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Apply sorting
        sort_column = getattr(Rule, sort_by, Rule.priority)
        if sort_order == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())
        
        # Apply pagination
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        
        result = await self.db.execute(query)
        rules = result.scalars().all()
        
        return list(rules), total
    
    async def get_active_rules(
        self,
        rule_type: Optional[RuleType] = None
    ) -> List[Rule]:
        """Get all active rules, optionally filtered by type."""
        now = datetime.utcnow()
        
        query = select(Rule).where(
            and_(
                Rule.is_active == True,
                (Rule.effective_from == None) | (Rule.effective_from <= now),
                (Rule.effective_to == None) | (Rule.effective_to >= now)
            )
        )
        
        if rule_type:
            query = query.where(Rule.rule_type == rule_type)
        
        query = query.order_by(Rule.priority.asc())
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def update(
        self,
        rule_id: UUID,
        data: RuleUpdate,
        modified_by: UUID
    ) -> Optional[Rule]:
        """Update rule and create new version."""
        rule = await self.get_by_id(rule_id)
        
        if not rule:
            return None
        
        # Update fields
        if data.rule_name is not None:
            rule.rule_name = data.rule_name
        if data.description is not None:
            rule.description = data.description
        if data.rule_type is not None:
            rule.rule_type = data.rule_type
        if data.action_type is not None:
            rule.action_type = data.action_type
        if data.condition_logic is not None:
            rule.condition_logic = data.condition_logic
        if data.priority is not None:
            rule.priority = data.priority
        if data.is_active is not None:
            rule.is_active = data.is_active
        if data.effective_from is not None:
            rule.effective_from = data.effective_from
        if data.effective_to is not None:
            rule.effective_to = data.effective_to
        if data.denial_reason_template is not None:
            rule.denial_reason_template = data.denial_reason_template
        if data.flag_reason_template is not None:
            rule.flag_reason_template = data.flag_reason_template
        if data.category is not None:
            rule.category = data.category
        if data.tags is not None:
            rule.tags = data.tags
        
        rule.last_modified_by = modified_by
        
        await self.db.flush()
        await self.db.refresh(rule)
        
        # Create new version
        await self._create_version(
            rule, 
            modified_by, 
            data.change_description or "Rule updated"
        )
        
        # Invalidate cache
        await cache.delete(CacheKeys.ACTIVE_RULES)
        
        return rule
    
    async def delete(self, rule_id: UUID) -> bool:
        """Delete rule."""
        rule = await self.get_by_id(rule_id)
        
        if not rule:
            return False
        
        await self.db.delete(rule)
        await self.db.flush()
        
        # Invalidate cache
        await cache.delete(CacheKeys.ACTIVE_RULES)
        
        return True
    
    async def toggle_active(self, rule_id: UUID, is_active: bool, modified_by: UUID) -> Optional[Rule]:
        """Toggle rule active status."""
        rule = await self.get_by_id(rule_id)
        
        if not rule:
            return None
        
        rule.is_active = is_active
        rule.last_modified_by = modified_by
        
        await self.db.flush()
        await self.db.refresh(rule)
        
        # Invalidate cache
        await cache.delete(CacheKeys.ACTIVE_RULES)
        
        return rule
    
    async def get_versions(self, rule_id: UUID) -> List[RuleVersion]:
        """Get all versions of a rule."""
        result = await self.db.execute(
            select(RuleVersion)
            .where(RuleVersion.rule_id == rule_id)
            .order_by(RuleVersion.version_number.desc())
        )
        return list(result.scalars().all())
    
    async def _create_version(
        self,
        rule: Rule,
        created_by: UUID,
        change_description: str
    ) -> RuleVersion:
        """Create a version snapshot of the rule."""
        # Get current max version
        result = await self.db.execute(
            select(func.max(RuleVersion.version_number))
            .where(RuleVersion.rule_id == rule.id)
        )
        max_version = result.scalar() or 0
        
        version = RuleVersion(
            rule_id=rule.id,
            version_number=max_version + 1,
            rule_name=rule.rule_name,
            rule_type=rule.rule_type,
            action_type=rule.action_type,
            condition_logic=rule.condition_logic,
            priority=rule.priority,
            change_description=change_description,
            effective_from=rule.effective_from,
            created_by=created_by,
        )
        
        self.db.add(version)
        await self.db.flush()
        
        return version
    
    async def _generate_rule_code(self, rule_type: RuleType) -> str:
        """Generate unique rule code."""
        prefix_map = {
            RuleType.VALIDATION: "VAL",
            RuleType.ADJUDICATION: "ADJ",
            RuleType.CALCULATION: "CAL",
            RuleType.NOTIFICATION: "NOT",
        }
        prefix = prefix_map.get(rule_type, "RUL")
        
        # Get count of rules with this prefix
        result = await self.db.execute(
            select(func.count(Rule.id))
            .where(Rule.rule_code.like(f"{prefix}-%"))
        )
        count = result.scalar() or 0
        
        return f"{prefix}-{str(count + 1).zfill(4)}"
    
    async def evaluate_rule(self, rule: Rule, context: dict) -> dict:
        """Evaluate a single rule against a context (claim data).
        
        Returns evaluation result with matched status and action.
        """
        # This is a simplified rule evaluation
        # In production, use a proper rules engine like drools or business-rules
        condition = rule.condition_logic
        
        result = {
            "rule_id": str(rule.id),
            "rule_code": rule.rule_code,
            "matched": False,
            "action": None,
            "message": None,
        }
        
        try:
            # Simple condition matching
            if self._evaluate_conditions(condition, context):
                result["matched"] = True
                result["action"] = rule.action_type.value
                
                if rule.action_type == ActionType.DENY:
                    result["message"] = rule.denial_reason_template
                elif rule.action_type == ActionType.FLAG:
                    result["message"] = rule.flag_reason_template
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def _evaluate_conditions(self, conditions: dict, context: dict) -> bool:
        """Evaluate condition logic against context."""
        if not conditions:
            return False
        
        # Support simple field comparisons
        operator = conditions.get("operator", "and")
        rules = conditions.get("rules", [])
        
        if not rules:
            return False
        
        results = []
        for rule in rules:
            field = rule.get("field")
            op = rule.get("operator")
            value = rule.get("value")
            
            context_value = context.get(field)
            
            if op == "equals":
                results.append(context_value == value)
            elif op == "not_equals":
                results.append(context_value != value)
            elif op == "greater_than":
                results.append(context_value > value if context_value else False)
            elif op == "less_than":
                results.append(context_value < value if context_value else False)
            elif op == "contains":
                results.append(value in context_value if context_value else False)
            elif op == "in":
                results.append(context_value in value if context_value else False)
            else:
                results.append(False)
        
        if operator == "and":
            return all(results)
        elif operator == "or":
            return any(results)
        
        return False
