import math
import threading
import pytest
from pydantic import ValidationError
from fastapi import HTTPException
from backend.app.config import settings
from backend.app.models.action import StructuredFinancialAction
from backend.app.models.authorization import AuthorizationToken
from backend.app.engine.decision_engine import decision_engine
from backend.app.engine.execution_gate import execution_gate
from backend.app.storage.repository import repository
from backend.app.execution.mock_adapter import MockPaymentAdapter
from backend.app.api.actions import execute_action, ExecuteActionRequest
from mcp.financial_server.tools.payments import execute_payment_tool


def test_39_token_id_guessing_rejected():
    action = StructuredFinancialAction(
        action_id="ACT-GUESS", amount=1000.0, source_account="ACC-001",
        destination_account="ACC-002", counterparty_id="VENDOR-001"
    )
    decision_engine.evaluate_action(action)
    success, msg, tx = execution_gate.execute_authorized_action(action.action_id, "AUTH-9999")
    assert success is False
    assert tx is None


def test_40_malformed_and_truncated_signature_rejected():
    action = StructuredFinancialAction(
        action_id="ACT-SIG", amount=1000.0, source_account="ACC-001",
        destination_account="ACC-002", counterparty_id="VENDOR-001"
    )
    d = decision_engine.evaluate_action(action)
    token = repository.get_token(action.action_id)
    token.signature = token.signature[:16]
    success, msg, tx = execution_gate.execute_authorized_action(action.action_id, d.authorization_token)
    assert success is False
    assert "signature" in msg.lower()


def test_41_json_field_ordering_does_not_break_hash():
    a1 = StructuredFinancialAction(
        action_id="ACT-JSON", amount=1000.0, source_account="ACC-001",
        destination_account="ACC-002", counterparty_id="VENDOR-001", reference="r"
    )
    dumped = a1.model_dump()
    a2 = StructuredFinancialAction(**dumped)
    assert a1.compute_hash() == a2.compute_hash()


def test_42_amount_precision_and_non_finite_rejected():
    with pytest.raises(ValidationError):
        StructuredFinancialAction(
            action_id="ACT-PREC", amount=10.001, source_account="ACC-001",
            destination_account="ACC-002", counterparty_id="VENDOR-001"
        )
    with pytest.raises(ValidationError):
        StructuredFinancialAction(
            action_id="ACT-INF", amount=math.inf, source_account="ACC-001",
            destination_account="ACC-002", counterparty_id="VENDOR-001"
        )
    with pytest.raises(ValidationError):
        StructuredFinancialAction(
            action_id="ACT-NAN", amount=math.nan, source_account="ACC-001",
            destination_account="ACC-002", counterparty_id="VENDOR-001"
        )


def test_43_duplicate_invoice_modified_amount_still_blocked():
    a1 = StructuredFinancialAction(
        action_id="ACT-DUPA", invoice_id="INV-2041", amount=4500.0,
        source_account="ACC-001", destination_account="ACC-002", counterparty_id="VENDOR-777"
    )
    d1 = decision_engine.evaluate_action(a1)
    execution_gate.execute_authorized_action(a1.action_id, d1.authorization_token)
    a2 = StructuredFinancialAction(
        action_id="ACT-DUPB", invoice_id="INV-2041", amount=4499.0,
        source_account="ACC-001", destination_account="ACC-002", counterparty_id="VENDOR-777"
    )
    d2 = decision_engine.evaluate_action(a2)
    assert d2.decision == "BLOCK"


def test_44_mcp_execute_without_token_cannot_move_money():
    action = StructuredFinancialAction(
        action_id="ACT-MCP", amount=1000.0, source_account="ACC-001",
        destination_account="ACC-002", counterparty_id="VENDOR-001"
    )
    decision_engine.evaluate_action(action)
    res = execute_payment_tool(action.action_id, None)
    assert res["success"] is False
    assert res["transaction"] is None


def test_45_adapter_exception_fail_closed_releases_token():
    action = StructuredFinancialAction(
        action_id="ACT-EXC", amount=1000.0, source_account="ACC-001",
        destination_account="ACC-002", counterparty_id="VENDOR-001"
    )
    d = decision_engine.evaluate_action(action)
    MockPaymentAdapter.force_exception = True
    try:
        success, msg, tx = execution_gate.execute_authorized_action(action.action_id, d.authorization_token)
    finally:
        MockPaymentAdapter.force_exception = False
    assert success is False
    assert tx is None
    assert repository.get_token_lifecycle(d.authorization_token) == "ISSUED"
    success2, _, tx2 = execution_gate.execute_authorized_action(action.action_id, d.authorization_token)
    assert success2 is True
    assert tx2 is not None


def test_46_get_action_does_not_leak_hmac_signature():
    from backend.app.api.actions import get_action
    action = StructuredFinancialAction(
        action_id="ACT-LEAK", amount=1000.0, source_account="ACC-001",
        destination_account="ACC-002", counterparty_id="VENDOR-001"
    )
    decision_engine.evaluate_action(action)
    payload = get_action("ACT-LEAK")
    assert payload["token"]["signature"] == "[redacted]"


def test_47_execute_wrong_action_id_with_valid_token():
    a = StructuredFinancialAction(
        action_id="ACT-OWN", amount=1000.0, source_account="ACC-001",
        destination_account="ACC-002", counterparty_id="VENDOR-001"
    )
    d = decision_engine.evaluate_action(a)
    success, msg, tx = execution_gate.execute_authorized_action("ACT-DOES-NOT-EXIST", d.authorization_token)
    assert success is False
    assert tx is None


def test_48_mock_tx_never_has_explorer_url():
    action = StructuredFinancialAction(
        action_id="ACT-MOCKURL", amount=1000.0, source_account="ACC-001",
        destination_account="ACC-002", counterparty_id="VENDOR-001"
    )
    d = decision_engine.evaluate_action(action)
    success, _, tx = execution_gate.execute_authorized_action(action.action_id, d.authorization_token)
    assert success is True
    assert tx.blockchain_tx_hash.startswith("mock-tx-")
    assert tx.explorer_url is None
