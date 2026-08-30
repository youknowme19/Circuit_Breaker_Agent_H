from typing import Optional
from backend.app.models.action import StructuredFinancialAction
from backend.app.models.policy import PolicyViolation, PolicySeverity
from backend.app.storage.repository import repository

class CounterpartyEngine:
    """Evaluates counterparty status and cumulative exposure limit."""

    def evaluate(self, action: StructuredFinancialAction, max_exposure: float = 25000.0) -> Optional[PolicyViolation]:
        txs = repository.get_transactions_for_account(action.source_account)
        cumulative_exposure = sum(t.amount for t in txs if t.counterparty_id == action.counterparty_id and t.status == "EXECUTED")
        projected = cumulative_exposure + action.amount

        if projected > max_exposure:
            return PolicyViolation(
                policy_id="COUNTERPARTY_EXPOSURE",
                severity=PolicySeverity.REVIEW,
                message=f"Cumulative exposure for counterparty '{action.counterparty_id}' (${projected:,.2f}) exceeds exposure threshold of ${max_exposure:,.2f}",
                actual=projected,
                limit=max_exposure,
                details={"existing_exposure": cumulative_exposure, "proposed_amount": action.amount}
            )

        return None

counterparty_engine = CounterpartyEngine()
