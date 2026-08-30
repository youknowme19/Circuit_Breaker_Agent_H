from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

class PolicySeverity(str, Enum):
    ALLOW = "ALLOW"
    REVIEW = "REVIEW"
    BLOCK = "BLOCK"

class PolicyViolation(BaseModel):
    policy_id: str = Field(..., description="ID of violating policy e.g. MAX_TRANSFER")
    severity: PolicySeverity = Field(..., description="Severity of violation: REVIEW or BLOCK")
    message: str = Field(..., description="Human-readable violation message")
    actual: Optional[Any] = Field(default=None, description="Observed value")
    limit: Optional[Any] = Field(default=None, description="Configured limit threshold")
    details: Dict[str, Any] = Field(default_factory=dict)

class PolicyConfig(BaseModel):
    id: str
    enabled: bool = True
    severity: PolicySeverity = PolicySeverity.BLOCK
    description: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
