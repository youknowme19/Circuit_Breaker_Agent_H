from typing import Optional
from datetime import datetime, timedelta
from backend.app.config import settings
from backend.app.models.action import StructuredFinancialAction
from backend.app.models.policy import PolicyViolation, PolicySeverity
from backend.app.storage.repository import repository

class VelocityEngine:
    """Calculates 24-hour rolling account transaction velocity totals."""

    def evaluate(self, action: StructuredFinancialAction, window_hours: int = 24) -> Optional[PolicyViolation]:
        txs = repository.get_transactions_for_account(action.source_account)
        cutoff = datetime.utcnow() - timedelta(hours=window_hours)
        
        recent_total = 0.0
        for tx in txs:
            if tx.status == "EXECUTED" and tx.source_account == action.source_account:
                try:
                    tx_time = datetime.fromisoformat(tx.timestamp.replace("Z", "+00:00")).replace(tzinfo=None)
                    if tx_time >= cutoff:
                        recent_total += tx.amount
                except Exception:
                    recent_total += tx.amount

        projected_total = recent_total + action.amount

        if projected_total > settings.DAILY_VELOCITY_LIMIT:
            return PolicyViolation(
                policy_id="DAILY_TRANSFER_LIMIT",
                severity=PolicySeverity.BLOCK,
                message=(
                    f"24-hour cumulative velocity total ${projected_total:,.2f} "
                    f"(existing: ${recent_total:,.2f} + proposed: ${action.amount:,.2f}) "
                    f"exceeds daily limit of ${settings.DAILY_VELOCITY_LIMIT:,.2f}"
                ),
                actual=projected_total,
                limit=settings.DAILY_VELOCITY_LIMIT,
                details={"existing_total": recent_total, "proposed_amount": action.amount}
            )

        return None

velocity_engine = VelocityEngine()
