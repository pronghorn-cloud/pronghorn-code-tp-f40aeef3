"""Rule Schemas

Pydantic models for rules engine API.
"""

from typing import Optional, List, Any
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID

from app.schemas.common import BaseSchema, PaginationMeta
from app.models.rule import RuleType, ActionType


class ConditionLogic(BaseModel):
    """Rule condition logic structure."""
    type: str = Field(..., pattern=r"^(AND|OR|NOT|COMPARISON)$")
    conditions: Optional[List["ConditionLogic"]] = None
    field: Optional[str] = None
    operator: Optional[str] = Field(None, pattern=r"^(=|!=|>|<|>=|<=|IN|NOT_IN|CONTAINS|STARTS_WITH|ENDS_WITH)$")
    value: Optional[Any] = None


# Enable self-referencing
ConditionLogic.model_rebuild()


class RuleCreate(BaseModel):
    """Schema for creating a new rule."""
    rule_name: str = Field(..., max_length=255)
    rule_code: str = Field(..., max_length=50, pattern=r"^[A-Z0-9_]+$")
    description: Optional[str] = None
    rule_type: RuleType = RuleType.VALIDATION
    action_type: ActionType = ActionType.FLAG
    condition_logic: ConditionLogic
    priority: int = Field(default=100, ge=1, le=1000)
    effective_from: Optional[datetime] = None
    effective_to: Optional[datetime] = None
    denial_reason_template: Optional[str] = None
    flag_reason_template: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None


class RuleUpdate(BaseModel):
    """Schema for updating a rule."""
    rule_name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    rule_type: Optional[RuleType] = None
    action_type: Optional[ActionType] = None
    condition_logic: Optional[ConditionLogic] = None
    priority: Optional[int] = Field(None, ge=1, le=1000)
    is_active: Optional[bool] = None
    effective_from: Optional[datetime] = None
    effective_to: Optional[datetime] = None
    denial_reason_template: Optional[str] = None
    flag_reason_template: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    change_description: Optional[str] = None  # Description of the change for versioning


class RuleResponse(BaseSchema):
    """Rule response schema."""
    id: UUID
    rule_name: str
    rule_code: str
    description: Optional[str]
    rule_type: RuleType
    action_type: ActionType
    condition_logic: dict
    priority: int
    is_active: bool
    effective_from: Optional[datetime]
    effective_to: Optional[datetime]
    category: Optional[str]
    tags: Optional[List[str]]
    created_at: datetime
    updated_at: datetime


class RuleListResponse(BaseModel):
    """Paginated rule list response."""
    data: List[RuleResponse]
    meta: PaginationMeta


class RuleVersionResponse(BaseSchema):
    """Rule version response schema."""
    id: UUID
    rule_id: UUID
    version_number: int
    rule_name: str
    rule_type: RuleType
    action_type: ActionType
    condition_logic: dict
    priority: int
    change_description: Optional[str]
    effective_from: Optional[datetime]
    created_at: datetime


class RuleTestRequest(BaseModel):
    """Schema for testing rules."""
    rule_ids: Optional[List[UUID]] = None  # If None, test all active rules
    claim_data: Optional[dict] = None  # Test claim data
    scenario: Optional[str] = None  # Predefined test scenario
    dry_run: bool = True


class RuleExecutionTrace(BaseModel):
    """Rule execution trace for debugging."""
    rule_id: UUID
    rule_code: str
    rule_name: str
    evaluated: bool
    condition_results: List[dict]
    matched: bool
    action_taken: Optional[str]
    execution_time_ms: float


class RuleTestResult(BaseModel):
    """Rule test execution result."""
    passed: bool
    total_rules_tested: int
    rules_matched: int
    final_outcome: Optional[str]
    execution_trace: List[RuleExecutionTrace]
    total_execution_time_ms: float
    errors: Optional[List[str]] = None
