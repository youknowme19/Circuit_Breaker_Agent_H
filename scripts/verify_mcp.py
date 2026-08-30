#!/usr/bin/env python3
"""Deterministic MCP Authorization Boundary Verification Script.

Tests the actual MCP tool functions against Circuit Breaker's execution gate to verify:

1. No token        -> DENY
2. Invalid token   -> DENY
3. Wrong action    -> DENY
4. Expired token   -> DENY
5. Valid token     -> ALLOW (Executes)
6. Replay token    -> DENY

Usage:
    PYTHONPATH=. python scripts/verify_mcp.py
"""

import sys
import uuid
import time
from backend.app.config import settings
from backend.app.storage.repository import repository
from backend.app.models.authorization import AuthorizationToken
from backend.app.engine.decision_engine import decision_engine
from backend.app.engine.execution_gate import execution_gate
from mcp.financial_server.tools.payments import propose_payment_tool, execute_payment_tool

def test_mcp_boundary():
    print("========================================")
    print("MCP AUTHORIZATION BOUNDARY VERIFICATION")
    print("========================================")
    
    act_id = f"ACT-MCP-{uuid.uuid4().hex[:6]}"
    payload = {
        "action_id": act_id,
        "agent_id": "trueforge-finance-agent",
        "source_account": "ACC-001",
        "destination_account": "ACC-002",
        "counterparty_id": "VENDOR-001",
        "amount": 2500.0,
        "currency": "USD",
        "reference": "MCP Boundary Test Payment"
    }
    
    prop_res = propose_payment_tool(payload)
    action_id = prop_res["action_id"]
    action = repository.get_action(action_id)
    
    print(f"Action Created: {action_id} (Decision: {prop_res['decision']})")
    print("Testing MCP `execute_payment` security checks:\n")
    
    # 1. No token
    res1 = execute_payment_tool(action_id, "")
    print(f"1. No Token:       {'ALLOW' if res1.get('success') else 'DENY'} | Response: {res1.get('message')}")
    assert not res1["success"], "Failed: No token was allowed!"

    # 2. Invalid/Forged Token ID
    res2 = execute_payment_tool(action_id, "token_invalid_forged_999")
    print(f"2. Invalid Token:  {'ALLOW' if res2.get('success') else 'DENY'} | Response: {res2.get('message')}")
    assert not res2["success"], "Failed: Invalid token was allowed!"

    # 3. Token for wrong action
    act_id_other = f"ACT-MCP-{uuid.uuid4().hex[:6]}"
    payload_other = {
        "action_id": act_id_other,
        "agent_id": "trueforge-finance-agent",
        "source_account": "ACC-001",
        "destination_account": "ACC-002",
        "counterparty_id": "VENDOR-001",
        "amount": 100.0,
        "currency": "USD",
        "reference": "Other Action"
    }
    other_prop = propose_payment_tool(payload_other)
    other_action = repository.get_action(other_prop["action_id"])
    
    tok_other = AuthorizationToken.create(
        token_id=f"TOKEN-{uuid.uuid4().hex[:6]}",
        action_id=other_action.action_id,
        action_hash=other_action.compute_hash(),
        decision="ALLOW",
        secret_key=settings.SECRET_KEY
    )
    repository.save_token(tok_other)
    
    res3 = execute_payment_tool(action_id, tok_other.token_id)
    print(f"3. Wrong Action:   {'ALLOW' if res3.get('success') else 'DENY'} | Response: {res3.get('message')}")
    assert not res3["success"], "Failed: Token for wrong action was allowed!"

    # 4. Expired Token
    tok_expired = AuthorizationToken.create(
        token_id=f"TOKEN-EXP-{uuid.uuid4().hex[:6]}",
        action_id=action_id,
        action_hash=action.compute_hash(),
        decision="ALLOW",
        secret_key=settings.SECRET_KEY,
        ttl_minutes=-10
    )
    repository.save_token(tok_expired)
    
    res4 = execute_payment_tool(action_id, tok_expired.token_id)
    print(f"4. Expired Token:  {'ALLOW' if res4.get('success') else 'DENY'} | Response: {res4.get('message')}")
    assert not res4["success"], "Failed: Expired token was allowed!"

    # 5. Valid Token
    tok_valid = AuthorizationToken.create(
        token_id=f"TOKEN-VAL-{uuid.uuid4().hex[:6]}",
        action_id=action_id,
        action_hash=action.compute_hash(),
        decision="ALLOW",
        secret_key=settings.SECRET_KEY,
        ttl_minutes=15
    )
    repository.save_token(tok_valid)
    
    res5 = execute_payment_tool(action_id, tok_valid.token_id)
    print(f"5. Valid Token:    {'ALLOW' if res5.get('success') else 'DENY'} | Tx ID: {res5.get('transaction', {}).get('transaction_id') if res5.get('transaction') else None}")
    assert res5["success"], f"Failed: Valid token was denied! Message: {res5.get('message')}"

    # 6. Replay Token
    res6 = execute_payment_tool(action_id, tok_valid.token_id)
    print(f"6. Replay Token:   {'ALLOW' if res6.get('success') else 'DENY'} | Response: {res6.get('message')}")
    assert not res6["success"], "Failed: Replay of consumed token was allowed!"

    print("\n----------------------------------------")
    print("MCP BOUNDARY STATUS: PASS (VERIFIED)")
    print("All 6 security boundary invariants held.")
    print("----------------------------------------")

if __name__ == "__main__":
    try:
        test_mcp_boundary()
        sys.exit(0)
    except Exception as e:
        print(f"\n[FAIL] MCP Boundary Verification failed: {e}")
        sys.exit(1)
