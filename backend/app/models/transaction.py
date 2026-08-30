from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class TransactionRecord(BaseModel):
    transaction_id: str = Field(..., description="Ledger transaction ID")
    action_id: str = Field(..., description="Source action ID")
    source_account: str
    destination_account: str
    counterparty_id: str
    amount: float
    currency: str = "USD"
    invoice_id: Optional[str] = None
    reference: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    status: str = "EXECUTED"  # EXECUTED, BLOCKED, PENDING
    blockchain_tx_hash: Optional[str] = None
    execution_mode: str = "MOCK"  # MOCK or SEPOLIA
    chain_network: str = "Mock Execution Ledger"
    block_number: Optional[int] = 5891024
    explorer_url: Optional[str] = None
