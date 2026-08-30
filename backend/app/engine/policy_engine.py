from typing import List
from backend.app.config import settings
from backend.app.models.action import StructuredFinancialAction
from backend.app.models.policy import PolicyViolation, PolicySeverity
from backend.app.storage.repository import repository

class DeterministicPolicyEngine:
    """Deterministic business policy evaluator. The LLM is NEVER consulted."""

    def evaluate(self, action: StructuredFinancialAction) -> List[PolicyViolation]:
        violations: List[PolicyViolation] = []

        # Policy 1: MAX_TRANSFER
        if action.amount > settings.MAX_SINGLE_TRANSFER:
            violations.append(
                PolicyViolation(
                    policy_id="MAX_TRANSFER",
                    severity=PolicySeverity.BLOCK,
                    message=f"Transaction amount ${action.amount:,.2f} exceeds maximum single transfer limit of ${settings.MAX_SINGLE_TRANSFER:,.2f}",
                    actual=action.amount,
                    limit=settings.MAX_SINGLE_TRANSFER,
                    details={"currency": action.currency}
                )
            )

        # Policy 2: UNKNOWN_DESTINATION
        dest_account = repository.get_account(action.destination_account)
        if not dest_account:
            violations.append(
                PolicyViolation(
                    policy_id="UNKNOWN_DESTINATION",
                    severity=PolicySeverity.BLOCK,
                    message=f"Destination account '{action.destination_account}' is unverified or non-existent in ledger registry",
                    actual=action.destination_account,
                    limit="REGISTERED_ACCOUNT"
                )
            )

        # Policy 3: NEW_COUNTERPARTY_REVIEW
        counterparty = repository.get_counterparty(action.counterparty_id)
        if not counterparty or not counterparty.get("verified", False):
            if action.amount >= settings.NEW_COUNTERPARTY_THRESHOLD:
                violations.append(
                    PolicyViolation(
                        policy_id="NEW_COUNTERPARTY_REVIEW",
                        severity=PolicySeverity.REVIEW,
                        message=f"Transfer of ${action.amount:,.2f} to unverified counterparty '{action.counterparty_id}' requires human approval",
                        actual=action.amount,
                        limit=settings.NEW_COUNTERPARTY_THRESHOLD,
                        details={"counterparty_id": action.counterparty_id}
                    )
                )

        return violations

policy_engine = DeterministicPolicyEngine()
