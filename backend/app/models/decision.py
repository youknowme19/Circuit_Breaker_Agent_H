from enum import Enum
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from backend.app.models.policy import PolicyViolation

class DecisionType(str, Enum):
    ALLOW = "ALLOW"
    REVIEW = "REVIEW"
    BLOCK = "BLOCK"

class AuthorizationDecision(BaseModel):
    decision_id: str = Field(..., description="Unique decision ID e.g. DEC-1001")
    action_id: str = Field(..., description="Target action ID")
    decision: DecisionType = Field(..., description="Final authorization outcome")
    risk_score: float = Field(default=0.0, ge=0.0, le=1.0, description="FraudGraph risk score")
    requires_human_approval: bool = Field(default=False, description="True if REVIEW decision")
    violations: List[PolicyViolation] = Field(default_factory=list, description="Policy violations")
    risk_signals: List[str] = Field(default_factory=list, description="Risk signal warning codes")
    evaluated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    authorization_token: Optional[str] = Field(default=None, description="Signed token string if ALLOW or APPROVED")
