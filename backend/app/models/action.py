import hashlib
import json
import math
from datetime import datetime
from decimal import Decimal, InvalidOperation
from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field, field_validator

class ActionType(str, Enum):
    TRANSFER = "TRANSFER"
    INVOICE_PAYMENT = "INVOICE_PAYMENT"
    REFUND = "REFUND"

class StructuredFinancialAction(BaseModel):
    action_id: str = Field(..., description="Unique action identifier")
    agent_id: str = Field(default="trueforge-finance-agent", description="ID of proposing agent")
    type: ActionType = Field(default=ActionType.TRANSFER, description="Type of financial operation")
    amount: float = Field(..., description="Positive finite amount with at most 2 decimal places")
    currency: str = Field(default="USD", description="3-letter currency code")
    source_account: str = Field(..., min_length=1, description="Origin account ID")
    destination_account: str = Field(..., min_length=1, description="Destination account ID")
    counterparty_id: str = Field(..., min_length=1, description="Counterparty identifier")
    invoice_id: Optional[str] = Field(default=None, description="Linked invoice ID if applicable")
    reference: Optional[str] = Field(default=None, description="Payment memo or reference text")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    reason: Optional[str] = Field(default=None, description="Agent explanation for action")
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: float) -> float:
        if v is None or isinstance(v, bool):
            raise ValueError("Amount must be a numeric value")
        try:
            number = float(v)
        except (TypeError, ValueError) as exc:
            raise ValueError("Amount must be a numeric value") from exc
        if not math.isfinite(number):
            raise ValueError("Amount must be a finite number")
        if number <= 0:
            raise ValueError("Amount must be greater than zero")
        if number > 1_000_000_000_000:
            raise ValueError("Amount exceeds maximum allowed value")
        try:
            decimal_amount = Decimal(str(number))
        except (InvalidOperation, ValueError) as exc:
            raise ValueError("Amount is not a valid decimal") from exc
        if decimal_amount.as_tuple().exponent < -2:
            raise ValueError("Amount precision cannot exceed 2 decimal places")
        return float(decimal_amount)

    @field_validator("source_account", "destination_account", "counterparty_id")
    @classmethod
    def validate_account_id(cls, v: str) -> str:
        cleaned = (v or "").strip()
        if not cleaned or len(cleaned) > 64:
            raise ValueError("Account identifiers must be 1–64 characters")
        return cleaned

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, v: str) -> str:
        v_upper = v.upper().strip()
        if len(v_upper) != 3 or not v_upper.isalpha():
            raise ValueError("Currency must be a 3-letter ISO code")
        return v_upper

    def canonical_json(self) -> str:
        """Returns deterministic, key-sorted JSON string representation."""
        data = self.model_dump()
        return json.dumps(data, sort_keys=True, separators=(",", ":"))

    def compute_hash(self) -> str:
        """Computes SHA-256 digest of canonical action string."""
        return hashlib.sha256(self.canonical_json().encode("utf-8")).hexdigest()
