from typing import List
from backend.app.config import settings
from backend.app.models.action import StructuredFinancialAction
from backend.app.models.policy import PolicyViolation, PolicySeverity
from backend.app.models.decision import AuthorizationDecision, DecisionType
from backend.app.models.authorization import AuthorizationToken
from backend.app.engine.policy_engine import policy_engine
from backend.app.engine.velocity import velocity_engine
from backend.app.engine.duplicate_detector import duplicate_detector
from backend.app.engine.counterparty import counterparty_engine
from backend.app.risk.risk_engine import risk_engine
from backend.app.storage.repository import repository
from backend.app.observability import emit

class DecisionEngine:
    """Unified Authorization Decision Orchestrator. Evaluates policies, state, and risk."""

    def evaluate_action(self, action: StructuredFinancialAction) -> AuthorizationDecision:
        # Save proposed action to repo
        repository.save_action(action)

        violations: List[PolicyViolation] = []

        # 1. Deterministic Policies
        violations.extend(policy_engine.evaluate(action))

        # 2. Velocity Engine
        vel_viol = velocity_engine.evaluate(action)
        if vel_viol:
            violations.append(vel_viol)

        # 3. Duplicate Detector
        dup_viol = duplicate_detector.evaluate(action)
        if dup_viol:
            violations.append(dup_viol)

        # 4. Counterparty Engine
        cp_viol = counterparty_engine.evaluate(action)
        if cp_viol:
            violations.append(cp_viol)

        # 5. FraudGraph Risk Engine
        risk_score, risk_signals = risk_engine.evaluate(action)
        if risk_score >= settings.HIGH_RISK_THRESHOLD:
            violations.append(
                PolicyViolation(
                    policy_id="HIGH_FRAUD_RISK",
                    severity=PolicySeverity.REVIEW,
                    message=f"FraudGraph detected elevated risk score {risk_score:.2f} (Threshold: {settings.HIGH_RISK_THRESHOLD:.2f})",
                    actual=risk_score,
                    limit=settings.HIGH_RISK_THRESHOLD,
                    details={"risk_signals": risk_signals}
                )
            )

        # Determine Decision Outcome
        has_block = any(v.severity == PolicySeverity.BLOCK for v in violations)
        has_review = any(v.severity == PolicySeverity.REVIEW for v in violations)

        if has_block:
            decision_type = DecisionType.BLOCK
            requires_approval = False
        elif has_review:
            decision_type = DecisionType.REVIEW
            requires_approval = True
        else:
            decision_type = DecisionType.ALLOW
            requires_approval = False

        decision_id = repository.next_id("DEC")
        auth_token_str = None

        # If ALLOW, issue signed AuthorizationToken
        if decision_type == DecisionType.ALLOW:
            token_obj = AuthorizationToken.create(
                token_id=repository.next_id("AUTH"),
                action_id=action.action_id,
                action_hash=action.compute_hash(),
                decision="ALLOW",
                secret_key=settings.SECRET_KEY
            )
            repository.save_token(token_obj)
            auth_token_str = token_obj.token_id

        decision = AuthorizationDecision(
            decision_id=decision_id,
            action_id=action.action_id,
            decision=decision_type,
            risk_score=risk_score,
            requires_human_approval=requires_approval,
            violations=violations,
            risk_signals=risk_signals,
            authorization_token=auth_token_str
        )

        repository.save_decision(decision)

        emit(
            f"ACTION_{decision_type.value}",
            f"Policy evaluated {action.action_id} → {decision_type.value}",
            action_id=action.action_id,
            amount=action.amount,
            destination=action.destination_account,
            decision=decision_type.value,
            risk_score=risk_score,
        )
        emit("POLICY_EVALUATED", f"{action.action_id} decision={decision_type.value}", action_id=action.action_id)
        if decision_type == DecisionType.ALLOW:
            emit("TOKEN_ISSUED", f"Token issued for {action.action_id}", action_id=action.action_id, token_id=auth_token_str)
        elif decision_type == DecisionType.BLOCK:
            emit("TOKEN_REJECTED", f"No token issued for blocked action {action.action_id}", action_id=action.action_id)

        # Append to SHA-256 Audit Chain
        event_id = f"EVT-{len(repository.audit_chain):04d}"
        violation_codes = [v.policy_id for v in violations]
        repository.append_audit_event(
            event_id=event_id,
            action_id=action.action_id,
            decision=decision_type.value,
            risk_score=risk_score,
            violations=violation_codes
        )

        return decision

decision_engine = DecisionEngine()
