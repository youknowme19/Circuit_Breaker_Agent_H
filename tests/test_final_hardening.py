import pytest
from datetime import datetime, timedelta, timezone
from backend.app.models.action import StructuredFinancialAction
from backend.app.models.decision import AuthorizationDecision
from backend.app.models.authorization import AuthorizationToken
from backend.app.storage.repository import repository
from backend.app.engine.execution_gate import execution_gate
from backend.app.config import settings

def test_63_final_hardening_deterministic_error_codes():
    action = StructuredFinancialAction(
        action_id="ACT-HARDEN-001",
        source_account="ACC-001",
        destination_account="ACC-002",
        amount=100.0,
        currency="USD",
        invoice_id="INV-HARDEN-001",
        counterparty_id="CP-001",
        reference="Test hardening"
    )
    repository.save_action(action)

    decision = AuthorizationDecision(
        decision_id="DEC-HARDEN-001",
        action_id="ACT-HARDEN-001",
        decision="ALLOW",
        risk_score=0.1,
        policy_violations=[]
    )
    repository.save_decision(decision)

    token = AuthorizationToken.create(
        token_id="TOK-HARDEN-001",
        action_id=action.action_id,
        action_hash=action.compute_hash(),
        decision="ALLOW",
        secret_key=settings.SECRET_KEY,
        ttl_minutes=15
    )
    repository.save_token(token)

    # 1. Valid execution succeeds
    success, msg, tx = execution_gate.execute_authorized_action(action.action_id, token.token_id)
    assert success is True
    assert msg == "EXECUTION_SUCCESSFUL"
    assert tx is not None

    # 2. Replay returns REJECTED_CONSUMED_TOKEN
    rep_ok, rep_msg, rep_tx = execution_gate.execute_authorized_action(action.action_id, token.token_id)
    assert rep_ok is False
    assert "[REJECTED_CONSUMED_TOKEN]" in rep_msg

def test_64_final_hardening_forged_and_mutated_rejections():
    # Setup action & decision
    action = StructuredFinancialAction(
        action_id="ACT-HARDEN-002",
        source_account="ACC-001",
        destination_account="ACC-002",
        amount=200.0,
        currency="USD",
        invoice_id="INV-HARDEN-002",
        counterparty_id="CP-002",
        reference="Forged test"
    )
    repository.save_action(action)
    decision = AuthorizationDecision(
        decision_id="DEC-HARDEN-002",
        action_id="ACT-HARDEN-002",
        decision="ALLOW",
        risk_score=0.1,
        policy_violations=[]
    )
    repository.save_decision(decision)

    # Forged Token Signature
    token_forged = AuthorizationToken(
        token_id="TOK-FORGED-001",
        action_id=action.action_id,
        action_hash=action.compute_hash(),
        decision="ALLOW",
        issued_at=datetime.utcnow().isoformat() + "Z",
        expires_at=(datetime.utcnow() + timedelta(minutes=15)).isoformat() + "Z",
        signature="invalid_signature_string"
    )
    repository.save_token(token_forged)

    ok, msg, _ = execution_gate.execute_authorized_action(action.action_id, token_forged.token_id)
    assert ok is False
    assert "[REJECTED_FORGED_SIGNATURE]" in msg

def test_65_final_hardening_expired_ttl_rejection():
    action = StructuredFinancialAction(
        action_id="ACT-HARDEN-003",
        source_account="ACC-001",
        destination_account="ACC-002",
        amount=300.0,
        currency="USD",
        invoice_id="INV-HARDEN-003",
        counterparty_id="CP-003",
        reference="Expired TTL"
    )
    repository.save_action(action)
    decision = AuthorizationDecision(
        decision_id="DEC-HARDEN-003",
        action_id="ACT-HARDEN-003",
        decision="ALLOW",
        risk_score=0.1,
        policy_violations=[]
    )
    repository.save_decision(decision)

    # Expired Token (ttl_minutes = -10)
    token_expired = AuthorizationToken.create(
        token_id="TOK-EXPIRED-001",
        action_id=action.action_id,
        action_hash=action.compute_hash(),
        decision="ALLOW",
        secret_key=settings.SECRET_KEY,
        ttl_minutes=-10
    )
    repository.save_token(token_expired)

    ok, msg, _ = execution_gate.execute_authorized_action(action.action_id, token_expired.token_id)
    assert ok is False
    assert "[REJECTED_EXPIRED_TOKEN]" in msg
