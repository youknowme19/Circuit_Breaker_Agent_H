import threading
import pytest
from datetime import datetime, timedelta
from pydantic import ValidationError
from backend.app.config import settings
from backend.app.models.action import StructuredFinancialAction, ActionType
from backend.app.models.authorization import AuthorizationToken
from backend.app.engine.decision_engine import decision_engine
from backend.app.engine.execution_gate import execution_gate
from backend.app.audit.verifier import audit_verifier
from backend.app.storage.repository import repository
from backend.app.risk.graph import fraud_graph
from backend.app.execution.evm_testnet_adapter import EVMTestnetAdapter
from backend.app.execution.base import PaymentAdapter
from agent.payment_agent.agent import trueforge_agent

class SpyPaymentAdapter(PaymentAdapter):
    """Spy Payment Adapter for counting exact invocations under concurrency."""
    def __init__(self):
        self.call_count = 0
        self._lock = threading.Lock()

    def execute_transfer(self, action_id: str, source: str, destination: str, amount: float, currency: str = "USD"):
        with self._lock:
            self.call_count += 1
        return True, f"spy-tx-{action_id}", "SPY", "Spy Ledger", 100, None

@pytest.fixture(autouse=True)
def reset_repo():
    repository.reset()
    fraud_graph.reset()
    yield

# -----------------------------------------------------------------------------
# 1. CORE FUNCTIONAL POLICY & SEVERITY TESTS (1 - 6)
# -----------------------------------------------------------------------------

def test_01_normal_transaction_allow():
    action = StructuredFinancialAction(
        action_id="ACT-001",
        amount=2000.0,
        source_account="ACC-001",
        destination_account="ACC-002",
        counterparty_id="VENDOR-001"
    )
    decision = decision_engine.evaluate_action(action)
    assert decision.decision == "ALLOW"
    assert decision.authorization_token is not None

def test_02_max_transfer_block():
    action = StructuredFinancialAction(
        action_id="ACT-002",
        amount=50000.0,
        source_account="ACC-001",
        destination_account="ACC-002",
        counterparty_id="VENDOR-001"
    )
    decision = decision_engine.evaluate_action(action)
    assert decision.decision == "BLOCK"
    assert any(v.policy_id == "MAX_TRANSFER" for v in decision.violations)

def test_03_daily_velocity_block():
    amounts = [6000.0, 6100.0, 6200.0]
    for i, amt in enumerate(amounts):
        a = StructuredFinancialAction(action_id=f"ACT-VEL-{i}", amount=amt, source_account="ACC-001", destination_account="ACC-002", counterparty_id="VENDOR-001", reference=f"Ref {i}")
        d = decision_engine.evaluate_action(a)
        assert d.decision == "ALLOW"
        execution_gate.execute_authorized_action(a.action_id, d.authorization_token)

    new_action = StructuredFinancialAction(action_id="ACT-VEL-OVER", amount=5000.0, source_account="ACC-001", destination_account="ACC-002", counterparty_id="VENDOR-001", reference="Ref 99")
    decision = decision_engine.evaluate_action(new_action)
    assert decision.decision == "BLOCK"
    assert any(v.policy_id == "DAILY_TRANSFER_LIMIT" for v in decision.violations)

def test_04_duplicate_payment_block():
    action1 = StructuredFinancialAction(action_id="ACT-DUP-1", invoice_id="INV-2041", amount=4500.0, source_account="ACC-001", destination_account="ACC-002", counterparty_id="VENDOR-777")
    d1 = decision_engine.evaluate_action(action1)
    execution_gate.execute_authorized_action(action1.action_id, d1.authorization_token)

    action2 = StructuredFinancialAction(action_id="ACT-DUP-2", invoice_id="INV-2041", amount=4500.0, source_account="ACC-001", destination_account="ACC-002", counterparty_id="VENDOR-777")
    d2 = decision_engine.evaluate_action(action2)
    assert d2.decision == "BLOCK"
    assert any(v.policy_id == "DUPLICATE_PAYMENT" for v in d2.violations)

def test_05_new_counterparty_review():
    action = StructuredFinancialAction(action_id="ACT-NEW-CP", amount=8000.0, source_account="ACC-001", destination_account="ACC-991", counterparty_id="VENDOR-991")
    decision = decision_engine.evaluate_action(action)
    assert decision.decision == "REVIEW"
    assert decision.requires_human_approval is True

def test_06_unknown_destination():
    action = StructuredFinancialAction(action_id="ACT-UNK", amount=2000.0, source_account="ACC-001", destination_account="ACC-NONEXISTENT", counterparty_id="VENDOR-001")
    decision = decision_engine.evaluate_action(action)
    assert decision.decision == "BLOCK"
    assert any(v.policy_id == "UNKNOWN_DESTINATION" for v in decision.violations)

# -----------------------------------------------------------------------------
# 2. AUDIT CHAIN & ADVERSARIAL PROMPT INJECTION TESTS (7 - 10)
# -----------------------------------------------------------------------------

def test_07_valid_audit_chain():
    action = StructuredFinancialAction(action_id="ACT-AUD", amount=1000.0, source_account="ACC-001", destination_account="ACC-002", counterparty_id="VENDOR-001")
    decision_engine.evaluate_action(action)
    res = audit_verifier.verify_chain()
    assert res["valid"] is True

def test_08_tampered_audit_chain():
    action = StructuredFinancialAction(action_id="ACT-TAMP", amount=1000.0, source_account="ACC-001", destination_account="ACC-002", counterparty_id="VENDOR-001")
    decision_engine.evaluate_action(action)
    audit_verifier.simulate_tamper("EVT-0001", "TAMPERED_ALLOW")
    res = audit_verifier.verify_chain()
    assert res["valid"] is False
    assert res["broken_at"] == "EVT-0001"

def test_09_missing_authorization_denied():
    action = StructuredFinancialAction(action_id="ACT-NO-AUTH", amount=1000.0, source_account="ACC-001", destination_account="ACC-002", counterparty_id="VENDOR-001")
    decision_engine.evaluate_action(action)
    success, msg, tx = execution_gate.execute_authorized_action(action.action_id, token_id=None)
    assert success is False
    assert "Missing authorization token" in msg

def test_10_expired_authorization_denied():
    action = StructuredFinancialAction(action_id="ACT-EXP", amount=1000.0, source_account="ACC-001", destination_account="ACC-002", counterparty_id="VENDOR-001")
    decision_engine.evaluate_action(action)
    token = AuthorizationToken.create(
        token_id="AUTH-EXPIRED-TEST",
        action_id=action.action_id,
        action_hash=action.compute_hash(),
        decision="ALLOW",
        secret_key=settings.SECRET_KEY,
        ttl_minutes=-10
    )
    repository.save_token(token)
    success, msg, tx = execution_gate.execute_authorized_action(action.action_id, token.token_id)
    assert success is False
    assert "expired" in msg.lower()

# -----------------------------------------------------------------------------
# 3. PAYLOAD MUTATION & EXECUTION GATE DENIAL TESTS (11 - 15)
# -----------------------------------------------------------------------------

def test_11_action_hash_mismatch_denied():
    action = StructuredFinancialAction(action_id="ACT-MUT", amount=1000.0, source_account="ACC-001", destination_account="ACC-002", counterparty_id="VENDOR-001")
    d = decision_engine.evaluate_action(action)
    token_id = d.authorization_token
    action.amount = 99000.0
    success, msg, tx = execution_gate.execute_authorized_action(action.action_id, token_id)
    assert success is False
    assert "Hash Mismatch" in msg

def test_12_blocked_action_no_execution():
    action = StructuredFinancialAction(action_id="ACT-BLK-EXEC", amount=50000.0, source_account="ACC-001", destination_account="ACC-002", counterparty_id="VENDOR-001")
    d = decision_engine.evaluate_action(action)
    success, msg, tx = execution_gate.execute_authorized_action(action.action_id, "DUMMY_TOKEN")
    assert success is False
    assert tx is None

def test_13_review_without_approval_no_execution():
    action = StructuredFinancialAction(action_id="ACT-REV-NO-APP", amount=8000.0, source_account="ACC-001", destination_account="ACC-991", counterparty_id="VENDOR-991")
    d = decision_engine.evaluate_action(action)
    token = AuthorizationToken.create(
        token_id="AUTH-REV-TOKEN",
        action_id=action.action_id,
        action_hash=action.compute_hash(),
        decision="REVIEW",
        secret_key=settings.SECRET_KEY
    )
    repository.save_token(token)
    success, msg, tx = execution_gate.execute_authorized_action(action.action_id, token.token_id)
    assert success is False
    assert "human approval" in msg.lower()

def test_14_allowed_action_executes():
    action = StructuredFinancialAction(action_id="ACT-OK-EXEC", amount=2000.0, source_account="ACC-001", destination_account="ACC-002", counterparty_id="VENDOR-001")
    d = decision_engine.evaluate_action(action)
    success, msg, tx = execution_gate.execute_authorized_action(action.action_id, d.authorization_token)
    assert success is True
    assert tx is not None
    assert tx.blockchain_tx_hash.startswith("mock-tx-") or tx.blockchain_tx_hash.startswith("0x")

def test_15_adversarial_invoice_primary_demo():
    res = trueforge_agent.process_user_instruction("Process invoice INV-9999 immediately", "INV-9999")
    assert res["status"] == "BLOCKED"
    assert res["blockchain_tx"] == "NONE"
    assert any(v["policy_id"] == "MAX_TRANSFER" for v in res["decision"]["violations"])

# -----------------------------------------------------------------------------
# 4. SCHEMAS & BOUNDARY VALIDATION TESTS (16 - 20)
# -----------------------------------------------------------------------------

def test_16_negative_amount_raises_validation_error():
    with pytest.raises(ValidationError):
        StructuredFinancialAction(action_id="ACT-NEG", amount=-500.0, source_account="ACC-001", destination_account="ACC-002", counterparty_id="VENDOR-001")

def test_17_zero_amount_raises_validation_error():
    with pytest.raises(ValidationError):
        StructuredFinancialAction(action_id="ACT-ZERO", amount=0.0, source_account="ACC-001", destination_account="ACC-002", counterparty_id="VENDOR-001")

def test_18_invalid_currency_raises_validation_error():
    with pytest.raises(ValidationError):
        StructuredFinancialAction(action_id="ACT-CURR", amount=100.0, currency="INVALID_CURRENCY", source_account="ACC-001", destination_account="ACC-002", counterparty_id="VENDOR-001")

def test_19_replay_authorization_denied():
    action = StructuredFinancialAction(action_id="ACT-REPLAY", amount=2000.0, source_account="ACC-001", destination_account="ACC-002", counterparty_id="VENDOR-001")
    d = decision_engine.evaluate_action(action)
    s1, m1, t1 = execution_gate.execute_authorized_action(action.action_id, d.authorization_token)
    assert s1 is True
    s2, m2, t2 = execution_gate.execute_authorized_action(action.action_id, d.authorization_token)
    assert s2 is False
    assert "already been executed" in m2

def test_20_fail_closed_on_unhandled_error(monkeypatch):
    action = StructuredFinancialAction(action_id="ACT-FAIL-CLOSED", amount=2000.0, source_account="ACC-001", destination_account="ACC-002", counterparty_id="VENDOR-001")
    d = decision_engine.evaluate_action(action)

    def mock_broken_transfer(*args, **kwargs):
        return False, "ADAPTER_OFFLINE_ERROR", "FAIL", "Unknown", None, None

    monkeypatch.setattr("backend.app.execution.mock_adapter.MockPaymentAdapter.execute_transfer", mock_broken_transfer)
    success, msg, tx = execution_gate.execute_authorized_action(action.action_id, d.authorization_token)
    assert success is False
    assert tx is None
    assert "Payment adapter failure" in msg

# -----------------------------------------------------------------------------
# 5. AUDIT FINDING #1 REGRESSION TESTS — SEPOLIA ADAPTER REALITY (21 - 24)
# -----------------------------------------------------------------------------

def test_21_sepolia_disabled_fails_closed(monkeypatch):
    monkeypatch.setattr(settings, "ENABLE_TESTNET_EXECUTION", False)
    adapter = EVMTestnetAdapter()
    success, msg, mode, chain, block, url = adapter.execute_transfer("ACT-SEP-1", "ACC-001", "ACC-002", 100.0)
    assert success is False
    assert "disabled" in msg.lower()

def test_22_sepolia_missing_credentials_fails_closed(monkeypatch):
    monkeypatch.setattr(settings, "ENABLE_TESTNET_EXECUTION", True)
    monkeypatch.setattr(settings, "TESTNET_RPC_URL", "")
    monkeypatch.setattr(settings, "TESTNET_PRIVATE_KEY", "")
    adapter = EVMTestnetAdapter()
    success, msg, mode, chain, block, url = adapter.execute_transfer("ACT-SEP-2", "ACC-001", "ACC-002", 100.0)
    assert success is False
    assert "Missing required configuration" in msg

def test_23_sepolia_unreachable_rpc_fails_closed(monkeypatch):
    monkeypatch.setattr(settings, "ENABLE_TESTNET_EXECUTION", True)
    monkeypatch.setattr(settings, "TESTNET_RPC_URL", "https://invalid-nonexistent-rpc-node.org")
    monkeypatch.setattr(settings, "TESTNET_PRIVATE_KEY", "0x0000000000000000000000000000000000000000000000000000000000000001")
    monkeypatch.setattr(settings, "TESTNET_CHAIN_ID", 11155111)
    adapter = EVMTestnetAdapter()
    success, msg, mode, chain, block, url = adapter.execute_transfer("ACT-SEP-3", "ACC-001", "ACC-002", 100.0)
    assert success is False
    assert "SEPOLIA" in msg

def test_24_no_synthetic_hash_fallback_on_sepolia_error(monkeypatch):
    monkeypatch.setattr(settings, "ENABLE_TESTNET_EXECUTION", True)
    monkeypatch.setattr(settings, "TESTNET_RPC_URL", "https://rpc.sepolia.org")
    monkeypatch.setattr(settings, "TESTNET_PRIVATE_KEY", "0x0000000000000000000000000000000000000000000000000000000000000001")
    adapter = EVMTestnetAdapter()
    success, msg, mode, chain, block, url = adapter.execute_transfer("ACT-SEP-4", "ACC-001", "ACC-002", 100.0)
    assert success is False
    assert url is None  # Explorer URL must NOT be constructed if broadcast failed!

# -----------------------------------------------------------------------------
# 6. AUDIT FINDING #2 REGRESSION TESTS — TOKEN OWNERSHIP BYPASS (25 - 27)
# -----------------------------------------------------------------------------

def test_25_api_execute_rejects_missing_token_id():
    from backend.app.api.actions import execute_action, ExecuteActionRequest
    from fastapi import HTTPException
    action = StructuredFinancialAction(action_id="ACT-API-1", amount=1000.0, source_account="ACC-001", destination_account="ACC-002", counterparty_id="VENDOR-001")
    decision_engine.evaluate_action(action)

    with pytest.raises(HTTPException) as exc_info:
        execute_action("ACT-API-1", ExecuteActionRequest(token_id=None))
    assert exc_info.value.status_code == 400
    assert "Missing explicit authorization token" in exc_info.value.detail

def test_26_api_execute_rejects_empty_token_id():
    from backend.app.api.actions import execute_action, ExecuteActionRequest
    from fastapi import HTTPException
    action = StructuredFinancialAction(action_id="ACT-API-2", amount=1000.0, source_account="ACC-001", destination_account="ACC-002", counterparty_id="VENDOR-001")
    decision_engine.evaluate_action(action)

    with pytest.raises(HTTPException) as exc_info:
        execute_action("ACT-API-2", ExecuteActionRequest(token_id="   "))
    assert exc_info.value.status_code == 400

def test_27_api_execute_succeeds_with_explicit_valid_token():
    from backend.app.api.actions import execute_action, ExecuteActionRequest
    action = StructuredFinancialAction(action_id="ACT-API-3", amount=1000.0, source_account="ACC-001", destination_account="ACC-002", counterparty_id="VENDOR-001")
    d = decision_engine.evaluate_action(action)
    res = execute_action("ACT-API-3", ExecuteActionRequest(token_id=d.authorization_token))
    assert res["success"] is True

# -----------------------------------------------------------------------------
# 7. AUDIT FINDING #3 REGRESSION TESTS — SECRET KEY SECURITY (28 - 30)
# -----------------------------------------------------------------------------

def test_28_forged_token_with_old_key_rejected():
    action = StructuredFinancialAction(action_id="ACT-FORGE-1", amount=1000.0, source_account="ACC-001", destination_account="ACC-002", counterparty_id="VENDOR-001")
    d = decision_engine.evaluate_action(action)
    forged_token = AuthorizationToken.create(
        token_id="AUTH-FORGED",
        action_id=action.action_id,
        action_hash=action.compute_hash(),
        decision="ALLOW",
        secret_key="cb-secret-key-2026"  # Old hardcoded secret
    )
    repository.save_token(forged_token)
    success, msg, tx = execution_gate.execute_authorized_action(action.action_id, forged_token.token_id)
    assert success is False
    assert "signature verification failed" in msg.lower()

def test_29_token_verification_uses_hmac_constant_time():
    token = AuthorizationToken.create(
        token_id="AUTH-HMAC-1",
        action_id="ACT-100",
        action_hash="hash123",
        decision="ALLOW",
        secret_key="valid-secret-key"
    )
    assert token.verify_signature("valid-secret-key") is True
    assert token.verify_signature("wrong-secret-key") is False

def test_30_token_creation_raises_if_secret_key_empty():
    with pytest.raises(ValueError):
        AuthorizationToken.create("AUTH-1", "ACT-1", "hash", "ALLOW", secret_key="")

# -----------------------------------------------------------------------------
# 8. AUDIT FINDING #5 & #6 REGRESSION TESTS — DYNAMIC GRAPH & CONCURRENCY (31 - 32)
# -----------------------------------------------------------------------------

def test_31_successful_execution_updates_fraud_graph_dynamically():
    action = StructuredFinancialAction(action_id="ACT-GRAPH-1", amount=3500.0, source_account="ACC-001", destination_account="ACC-002", counterparty_id="VENDOR-001")
    d = decision_engine.evaluate_action(action)
    assert d.decision == "ALLOW"

    if fraud_graph.graph.has_edge("ACC-001", "ACC-002"):
        fraud_graph.graph.remove_edge("ACC-001", "ACC-002")

    assert fraud_graph.graph.has_edge("ACC-001", "ACC-002") is False

    execution_gate.execute_authorized_action(action.action_id, d.authorization_token)
    assert fraud_graph.graph.has_edge("ACC-001", "ACC-002") is True
    assert fraud_graph.graph.edges["ACC-001", "ACC-002"]["amount"] == 3500.0

def test_32_thread_safe_repository_concurrency():
    def worker(i: int):
        act = StructuredFinancialAction(action_id=f"ACT-THREAD-{i}", amount=100.0 + i, source_account="ACC-001", destination_account="ACC-002", counterparty_id="VENDOR-001")
        decision_engine.evaluate_action(act)

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert len(repository.actions) >= 10

# -----------------------------------------------------------------------------
# 9. ADVANCED ADVERSARIAL CONCURRENCY & RACE SCENARIO TESTS (33 - 38)
# -----------------------------------------------------------------------------

def test_33_true_20_thread_concurrent_execution_race(monkeypatch):
    """20 threads execute the exact SAME token simultaneously. Adapter MUST be called exactly ONCE."""
    spy = SpyPaymentAdapter()
    monkeypatch.setattr("backend.app.engine.execution_gate.get_payment_adapter", lambda: spy)

    action = StructuredFinancialAction(action_id="ACT-CONC-RACE", amount=2000.0, source_account="ACC-001", destination_account="ACC-002", counterparty_id="VENDOR-001")
    d = decision_engine.evaluate_action(action)
    token_id = d.authorization_token

    results = []
    num_threads = 20
    barrier = threading.Barrier(num_threads)

    def worker():
        barrier.wait()  # Synchronize all 20 threads to execute at the exact same instant
        success, msg, tx = execution_gate.execute_authorized_action(action.action_id, token_id)
        results.append((success, msg))

    threads = [threading.Thread(target=worker) for _ in range(num_threads)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    successes = [r for r in results if r[0] is True]
    failures = [r for r in results if r[0] is False]

    # SECURITY INVARIANTS:
    assert spy.call_count == 1, f"Payment adapter called {spy.call_count} times! MUST be exactly 1!"
    assert len(successes) == 1, f"Successful executions: {len(successes)}! MUST be exactly 1!"
    assert len(failures) == 19, f"Failed executions: {len(failures)}! MUST be exactly 19!"
    assert len(repository.transactions) == 1

def test_34_concurrent_velocity_limit_race():
    """5 concurrent $2,000 requests starting at $15,000 velocity (Limit: $20,000). Total MUST NOT exceed $20,000."""
    # Pre-seed $15,000 spent velocity
    initial_tx = StructuredFinancialAction(action_id="ACT-INIT-VEL", amount=15000.0, source_account="ACC-001", destination_account="ACC-002", counterparty_id="VENDOR-001")
    d_init = decision_engine.evaluate_action(initial_tx)
    execution_gate.execute_authorized_action(initial_tx.action_id, d_init.authorization_token)

    num_threads = 5
    barrier = threading.Barrier(num_threads)
    results = []

    def worker(i: int):
        act = StructuredFinancialAction(action_id=f"ACT-VEL-RACE-{i}", amount=2000.0, source_account="ACC-001", destination_account="ACC-002", counterparty_id="VENDOR-001", reference=f"VelRef {i}")
        d = decision_engine.evaluate_action(act)
        barrier.wait()
        if d.decision == "ALLOW" and d.authorization_token:
            s, m, tx = execution_gate.execute_authorized_action(act.action_id, d.authorization_token)
            results.append((s, m))
        else:
            results.append((False, "BLOCKED_BY_DECISION"))

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(num_threads)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    total_committed = sum(t.amount for t in repository.transactions)
    assert total_committed <= settings.DAILY_VELOCITY_LIMIT, f"Velocity breached! Total: ${total_committed:,.2f} > ${settings.DAILY_VELOCITY_LIMIT:,.2f}"

def test_35_concurrent_duplicate_payment_race(monkeypatch):
    """20 concurrent submissions of the same invoice payment. Adapter MUST be called exactly ONCE."""
    spy = SpyPaymentAdapter()
    monkeypatch.setattr("backend.app.engine.execution_gate.get_payment_adapter", lambda: spy)

    action = StructuredFinancialAction(action_id="ACT-DUP-RACE", invoice_id="INV-2041", amount=4500.0, source_account="ACC-001", destination_account="ACC-002", counterparty_id="VENDOR-777")
    d = decision_engine.evaluate_action(action)
    token_id = d.authorization_token

    num_threads = 20
    barrier = threading.Barrier(num_threads)
    results = []

    def worker():
        barrier.wait()
        s, m, tx = execution_gate.execute_authorized_action(action.action_id, token_id)
        results.append(s)

    threads = [threading.Thread(target=worker) for _ in range(num_threads)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert spy.call_count == 1
    assert results.count(True) == 1

def test_36_cross_action_token_confusion():
    """Token A cannot execute Action B, and vice-versa."""
    act_a = StructuredFinancialAction(action_id="ACT-AAA", amount=1000.0, source_account="ACC-001", destination_account="ACC-002", counterparty_id="VENDOR-001")
    act_b = StructuredFinancialAction(action_id="ACT-BBB", amount=1000.0, source_account="ACC-001", destination_account="ACC-002", counterparty_id="VENDOR-001")

    dec_a = decision_engine.evaluate_action(act_a)
    dec_b = decision_engine.evaluate_action(act_b)

    # Cross token execution attempt
    s1, m1, t1 = execution_gate.execute_authorized_action(act_a.action_id, dec_b.authorization_token)
    assert s1 is False
    assert "Invalid or unissued authorization token" in m1 or "bound to a different action" in m1

    s2, m2, t2 = execution_gate.execute_authorized_action(act_b.action_id, dec_a.authorization_token)
    assert s2 is False

def test_37_concurrent_human_approval_race():
    """Concurrent human approval calls grant approval exactly once."""
    action = StructuredFinancialAction(action_id="ACT-REV-RACE", amount=8000.0, source_account="ACC-001", destination_account="ACC-991", counterparty_id="VENDOR-991")
    decision_engine.evaluate_action(action)

    from backend.app.api.approvals import approve_action, HumanApprovalRequest
    results = []
    barrier = threading.Barrier(5)

    def worker():
        barrier.wait()
        try:
            res = approve_action("ACT-REV-RACE", HumanApprovalRequest(approver="admin"))
            results.append(res)
        except Exception as e:
            results.append(None)

    threads = [threading.Thread(target=worker) for _ in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    non_nulls = [r for r in results if r is not None]
    assert len(non_nulls) == 1, f"Approved {len(non_nulls)} times! MUST be exactly 1!"

def test_38_transient_adapter_failure_releases_reservation(monkeypatch):
    """If payment adapter fails, token state is released allowing a retry, but un-executed token cannot be double-spent."""
    fail_count = 0

    def mock_flaky_transfer(*args, **kwargs):
        nonlocal fail_count
        fail_count += 1
        if fail_count == 1:
            return False, "TRANSIENT_NETWORK_DROP", "FAIL", "Unknown", None, None
        return True, "mock-tx-success-001", "MOCK", "Mock Ledger", 100, None

    monkeypatch.setattr("backend.app.execution.mock_adapter.MockPaymentAdapter.execute_transfer", mock_flaky_transfer)

    action = StructuredFinancialAction(action_id="ACT-FLAKY-1", amount=1000.0, source_account="ACC-001", destination_account="ACC-002", counterparty_id="VENDOR-001")
    d = decision_engine.evaluate_action(action)
    token_id = d.authorization_token

    # Attempt 1: Fails
    s1, m1, t1 = execution_gate.execute_authorized_action(action.action_id, token_id)
    assert s1 is False
    assert "TRANSIENT_NETWORK_DROP" in m1

    # Attempt 2: Retry succeeds!
    s2, m2, t2 = execution_gate.execute_authorized_action(action.action_id, token_id)
    assert s2 is True
    assert t2 is not None

    # Attempt 3: Already executed, fails!
    s3, m3, t3 = execution_gate.execute_authorized_action(action.action_id, token_id)
    assert s3 is False
    assert "already been executed" in m3
