import hashlib
import json
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class AuditEvent(BaseModel):
    event_id: str = Field(..., description="Unique event identifier e.g. EVT-001")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    action_id: str = Field(..., description="Target action ID")
    decision: str = Field(..., description="Decision result: ALLOW, REVIEW, BLOCK")
    risk_score: float = Field(default=0.0, description="Risk score assigned")
    violations: List[str] = Field(default_factory=list, description="Policy violation codes")
    previous_hash: str = Field(..., description="SHA-256 hash of previous audit event in chain")
    event_hash: str = Field(default="", description="SHA-256 digest of this event")

    def compute_hash(self) -> str:
        payload = f"{self.event_id}:{self.timestamp}:{self.action_id}:{self.decision}:{self.risk_score}:{','.join(sorted(self.violations))}:{self.previous_hash}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def update_hash(self) -> str:
        self.event_hash = self.compute_hash()
        return self.event_hash
