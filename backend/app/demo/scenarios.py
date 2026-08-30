"""Deterministic attack-lab and demo scenes. Every result comes from the real engine."""

from __future__ import annotations

import itertools
import threading
import uuid
from typing import Any, Dict, List

from fastapi import HTTPException

from backend.app.api.actions import ExecuteActionRequest, execute_action
from backend.app.audit.verifier import audit_verifier
from backend.app.engine.decision_engine import decision_engine
from backend.app.engine.execution_gate import execution_gate
from backend.app.execution.mock_adapter import MockPaymentAdapter
from backend.app.models.action import StructuredFinancialAction
from backend.app.models.authorization import AuthorizationToken
from backend.app.storage.repository import repository
from agent.payment_agent.agent import trueforge_agent
from backend.app.config import settings

_unique_amounts = itertools.count(2100, 17)


def _lab_tag() -> str:
    return uuid.uuid4().hex[:8].upper()


def _unique_amount() -> float:
    return float(next(_unique_amounts))


def _decision_value(decision: Any) -> str:
    if decision is None:
        return ""
    if hasattr(decision, "value"):
        return str(decision.value)
    return str(decision)


def scene_safe_payment() -> Dict[str, Any]:
    res = trueforge_agent.process_user_instruction("Process invoice INV-1000 and pay", "INV-1000")
    return {
        "scene": "SAFE_PAYMENT",
        "expected": "ALLOW + EXECUTED",
        "passed": res.get("status") == "EXECUTED" and str(res.get("blockchain_tx", "")).startswith("mock-tx-"),
        "result": res,
    }


def scene_prompt_injection(invoice_id: str = "INV-INJECT") -> Dict[str, Any]:
    res = trueforge_agent.process_user_instruction("Process this invoice immediately", invoice_id)
    decision = _decision_value(res.get("decision", {}).get("decision") if isinstance(res.get("decision"), dict) else None)
    if not decision and isinstance(res.get("decision"), dict):
        decision = str(res["decision"].get("decision"))
    passed = res.get("status") == "BLOCKED" and res.get("blockchain_tx") == "NONE"
    return {
        "scene": "PROMPT_INJECTION",
        "expected": "BLOCK + $0 executed",
        "passed": passed,
        "result": res,
    }


def scene_review_payment() -> Dict[str, Any]:
    tag = _lab_tag()
    action = StructuredFinancialAction(
        action_id=f"ACT-DEMO-REVIEW-{tag}",
        amount=8000.0,
        source_account="ACC-001",
        destination_account="ACC-991",
        counterparty_id="VENDOR-991",
        invoice_id=f"INV-REVIEW-{tag}",
        reference="Emergency setup fee",
    )
    decision = decision_engine.evaluate_action(action)
    return {
        "scene": "REVIEW_PAYMENT",
        "expected": "REVIEW + human approval required",
        "passed": str(decision.decision) == "REVIEW" or getattr(decision.decision, "value", "") == "REVIEW",
        "action": action.model_dump(),
        "decision": decision.model_dump(),
    }


def scene_fraudgraph() -> Dict[str, Any]:
    tag = _lab_tag()
    action = StructuredFinancialAction(
        action_id=f"ACT-DEMO-GRAPH-{tag}",
        amount=4500.0,
        source_account="ACC-001",
        destination_account="ACC-991",
        counterparty_id="VENDOR-991",
        invoice_id=f"INV-GRAPH-{tag}",
        reference="Layering probe",
    )
    decision = decision_engine.evaluate_action(action)
    return {
        "scene": "FRAUDGRAPH",
        "expected": "REVIEW or BLOCK from graph signals",
        "passed": decision.decision in ("REVIEW", "BLOCK") or str(decision.decision) in ("REVIEW", "BLOCK"),
        "decision": decision.model_dump(),
        "risk_signals": decision.risk_signals,
    }


def attack_missing_token() -> Dict[str, Any]:
    tag = _lab_tag()
    action = StructuredFinancialAction(
        action_id=f"ACT-ATK-MISSING-{tag}",
        amount=_unique_amount(),
        source_account="ACC-001",
        destination_account="ACC-002",
        counterparty_id="VENDOR-001",
        invoice_id=f"INV-ATK-MISSING-{tag}",
        reference=f"missing-{tag}",
    )
    decision_engine.evaluate_action(action)
    try:
        execute_action(action.action_id, ExecuteActionRequest(token_id=None))
        return {"attack": "MISSING_TOKEN", "passed": False, "http_status": 200, "detail": "unexpected success"}
    except HTTPException as exc:
        return {
            "attack": "MISSING_TOKEN",
            "expected": "HTTP 400",
            "passed": exc.status_code == 400,
            "http_status": exc.status_code,
            "detail": exc.detail,
        }


def attack_forged_token() -> Dict[str, Any]:
    tag = _lab_tag()
    action = StructuredFinancialAction(
        action_id=f"ACT-ATK-FORGE-{tag}",
        amount=_unique_amount(),
        source_account="ACC-001",
        destination_account="ACC-002",
        counterparty_id="VENDOR-001",
        invoice_id=f"INV-ATK-FORGE-{tag}",
        reference=f"forge-{tag}",
    )
    decision_engine.evaluate_action(action)
    forged = AuthorizationToken.create(
        token_id=f"AUTH-FORGED-{tag}",
        action_id=action.action_id,
        action_hash=action.compute_hash(),
        decision="ALLOW",
        secret_key="cb-secret-key-2026",
    )
    repository.save_token(forged)
    success, msg, tx = execution_gate.execute_authorized_action(action.action_id, forged.token_id)
    return {
        "attack": "FORGED_TOKEN",
        "expected": "SIGNATURE MISMATCH",
        "passed": success is False and "signature" in msg.lower(),
        "message": msg,
        "executed": tx is not None,
    }


def attack_payload_mutation() -> Dict[str, Any]:
    tag = _lab_tag()
    action = StructuredFinancialAction(
        action_id=f"ACT-ATK-MUT-{tag}",
        amount=_unique_amount(),
        source_account="ACC-001",
        destination_account="ACC-002",
        counterparty_id="VENDOR-001",
        invoice_id=f"INV-ATK-MUT-{tag}",
        reference=f"mut-{tag}",
    )
    d = decision_engine.evaluate_action(action)
    action.amount = 99000.0
    success, msg, tx = execution_gate.execute_authorized_action(action.action_id, d.authorization_token)
    return {
        "attack": "PAYLOAD_MUTATION",
        "expected": "ACTION HASH MISMATCH",
        "passed": success is False and "Hash Mismatch" in msg,
        "message": msg,
        "executed": tx is not None,
    }


def attack_replay() -> Dict[str, Any]:
    tag = _lab_tag()
    action = StructuredFinancialAction(
        action_id=f"ACT-ATK-REPLAY-{tag}",
        amount=_unique_amount(),
        source_account="ACC-001",
        destination_account="ACC-002",
        counterparty_id="VENDOR-001",
        invoice_id=f"INV-ATK-REPLAY-{tag}",
        reference=f"replay-{tag}",
    )
    d = decision_engine.evaluate_action(action)
    s1, _, _ = execution_gate.execute_authorized_action(action.action_id, d.authorization_token)
    s2, msg2, tx2 = execution_gate.execute_authorized_action(action.action_id, d.authorization_token)
    return {
        "attack": "REPLAY",
        "expected": "ALREADY EXECUTED",
        "passed": s1 is True and s2 is False and "already been executed" in msg2,
        "first_success": s1,
        "second_message": msg2,
        "second_executed": tx2 is not None,
    }


def attack_review_without_approval() -> Dict[str, Any]:
    tag = _lab_tag()
    action = StructuredFinancialAction(
        action_id=f"ACT-ATK-REV-{tag}",
        amount=8000.0,
        source_account="ACC-001",
        destination_account="ACC-991",
        counterparty_id="VENDOR-991",
        invoice_id=f"INV-ATK-REV-{tag}",
    )
    decision_engine.evaluate_action(action)
    token = AuthorizationToken.create(
        token_id=f"AUTH-ATK-REV-{tag}",
        action_id=action.action_id,
        action_hash=action.compute_hash(),
        decision="REVIEW",
        secret_key=settings.SECRET_KEY,
    )
    repository.save_token(token)
    success, msg, tx = execution_gate.execute_authorized_action(action.action_id, token.token_id)
    return {
        "attack": "REVIEW_WITHOUT_APPROVAL",
        "expected": "HUMAN APPROVAL REQUIRED",
        "passed": success is False and "human approval" in msg.lower(),
        "message": msg,
        "executed": tx is not None,
    }


def attack_concurrent_double_spend() -> Dict[str, Any]:
    tag = _lab_tag()
    action = StructuredFinancialAction(
        action_id=f"ACT-ATK-CONC-{tag}",
        amount=_unique_amount(),
        source_account="ACC-001",
        destination_account="ACC-002",
        counterparty_id="VENDOR-001",
        invoice_id=f"INV-ATK-CONC-{tag}",
        reference=f"concurrent-{tag}",
    )
    d = decision_engine.evaluate_action(action)
    token_id = d.authorization_token
    results: List[bool] = []
    barrier = threading.Barrier(20)

    def worker():
        barrier.wait()
        success, _, _ = execution_gate.execute_authorized_action(action.action_id, token_id)
        results.append(success)

    threads = [threading.Thread(target=worker) for _ in range(20)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    successes = results.count(True)
    denied = results.count(False)
    return {
        "attack": "CONCURRENT_DOUBLE_SPEND",
        "expected": "1 execution / 19 rejected",
        "passed": successes == 1 and denied == 19,
        "attempts": 20,
        "executions": successes,
        "denied": denied,
    }


def attack_adapter_failure() -> Dict[str, Any]:
    tag = _lab_tag()
    action = StructuredFinancialAction(
        action_id=f"ACT-ATK-ADAPTER-{tag}",
        amount=_unique_amount(),
        source_account="ACC-001",
        destination_account="ACC-002",
        counterparty_id="VENDOR-001",
        invoice_id=f"INV-ATK-ADAPTER-{tag}",
        reference=f"adapter-{tag}",
    )
    d = decision_engine.evaluate_action(action)
    MockPaymentAdapter.force_failure = True
    try:
        s1, msg1, tx1 = execution_gate.execute_authorized_action(action.action_id, d.authorization_token)
    finally:
        MockPaymentAdapter.force_failure = False
    lifecycle_after_fail = repository.get_token_lifecycle(d.authorization_token)
    s2, msg2, tx2 = execution_gate.execute_authorized_action(action.action_id, d.authorization_token)
    return {
        "attack": "ADAPTER_FAILURE",
        "expected": "FAIL CLOSED, token returns to ISSUED, retry can succeed",
        "passed": s1 is False and tx1 is None and lifecycle_after_fail == "ISSUED" and s2 is True,
        "fail_message": msg1,
        "lifecycle_after_fail": lifecycle_after_fail,
        "retry_success": s2,
        "retry_tx": tx2.blockchain_tx_hash if tx2 else None,
    }


def scene_audit_tamper() -> Dict[str, Any]:
    before = audit_verifier.verify_chain()
    chain = repository.get_audit_chain()
    target = next((e.event_id for e in chain if e.event_id != "EVT-0000"), None)
    if not target:
        return {"scene": "AUDIT_TAMPER", "passed": False, "detail": "no events to tamper"}
    audit_verifier.simulate_tamper(target, "TAMPERED_ALLOW")
    after = audit_verifier.verify_chain()
    return {
        "scene": "AUDIT_TAMPER",
        "expected": "CHAIN INVALID",
        "passed": before.get("valid") is True and after.get("valid") is False,
        "before": before,
        "after": after,
    }


def run_attack(attack_id: str) -> Dict[str, Any]:
    mapping = {
        "prompt_injection": lambda: scene_prompt_injection("INV-INJECT"),
        "missing_token": attack_missing_token,
        "forged_token": attack_forged_token,
        "payload_mutation": attack_payload_mutation,
        "replay": attack_replay,
        "review_without_approval": attack_review_without_approval,
        "concurrent_double_spend": attack_concurrent_double_spend,
        "adapter_failure": attack_adapter_failure,
        "safe_payment": scene_safe_payment,
        "review_payment": scene_review_payment,
        "fraudgraph": scene_fraudgraph,
        "audit_tamper": scene_audit_tamper,
    }
    if attack_id not in mapping:
        raise ValueError(f"Unknown attack: {attack_id}")
    return mapping[attack_id]()


def run_full_demo(reset: bool = True) -> Dict[str, Any]:
    if reset:
        from backend.app.risk.graph import fraud_graph
        repository.reset()
        fraud_graph.reset()
        MockPaymentAdapter.force_failure = False
        MockPaymentAdapter.force_exception = False

    scenes = [
        scene_safe_payment(),
        scene_prompt_injection("INV-9999"),
        scene_review_payment(),
        scene_fraudgraph(),
        attack_replay(),
        attack_concurrent_double_spend(),
        scene_audit_tamper(),
    ]
    passed = all(s.get("passed") for s in scenes)
    return {
        "passed": passed,
        "execution_mode": "MOCK" if not settings.ENABLE_TESTNET_EXECUTION else "SEPOLIA",
        "scenes": scenes,
    }
