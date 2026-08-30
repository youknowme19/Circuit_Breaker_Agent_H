from typing import Optional
from datetime import datetime, timedelta
from backend.app.config import settings
from backend.app.models.action import StructuredFinancialAction
from backend.app.models.policy import PolicyViolation, PolicySeverity
from backend.app.storage.repository import repository

class DuplicateDetector:
    """Detects duplicate payment attempts within a sliding time window."""

    def evaluate(self, action: StructuredFinancialAction) -> Optional[PolicyViolation]:
        txs = repository.get_transactions_for_account(action.source_account)
        cutoff = datetime.utcnow() - timedelta(minutes=settings.DUPLICATE_WINDOW_MINUTES)

        for tx in txs:
            if tx.status == "EXECUTED":
                try:
                    tx_time = datetime.fromisoformat(tx.timestamp.replace("Z", "+00:00")).replace(tzinfo=None)
                    if tx_time < cutoff:
                        continue
                except Exception:
                    pass

                # Check duplicate criteria: invoice match OR vendor + amount match
                is_invoice_dup = bool(action.invoice_id and tx.invoice_id and action.invoice_id == tx.invoice_id)
                is_vendor_dup = bool(
                    action.counterparty_id == tx.counterparty_id and
                    abs(action.amount - tx.amount) < 0.01 and
                    action.destination_account == tx.destination_account
                )

                if is_invoice_dup or is_vendor_dup:
                    reason = "Matching Invoice ID" if is_invoice_dup else "Matching Vendor & Amount"
                    return PolicyViolation(
                        policy_id="DUPLICATE_PAYMENT",
                        severity=PolicySeverity.BLOCK,
                        message=f"Duplicate payment detected within {settings.DUPLICATE_WINDOW_MINUTES}m window ({reason})",
                        actual=action.invoice_id or action.amount,
                        limit=settings.DUPLICATE_WINDOW_MINUTES,
                        details={"previous_tx_id": tx.transaction_id, "matching_reason": reason}
                    )

        return None

duplicate_detector = DuplicateDetector()
