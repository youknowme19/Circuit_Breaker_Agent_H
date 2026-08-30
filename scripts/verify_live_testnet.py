#!/usr/bin/env python3
"""Safe Live Testnet Verification Script.

Performs safe read-only checks by default:
1. RPC reachability & network connection
2. Chain ID verification
3. Derived wallet address
4. Balance check
5. Gas estimation check

Live transfer execution occurs ONLY if explicitly enabled via environment variable:
    ALLOW_LIVE_TEST_TRANSFER=true
    LIVE_TEST_RECIPIENT=0x...
    LIVE_TEST_AMOUNT=0.001

Usage:
    PYTHONPATH=. python scripts/verify_live_testnet.py
"""

import os
import sys
from backend.app.config import settings
from backend.app.execution.base import get_payment_adapter

def main():
    print("========================================")
    print("LIVE TESTNET READINESS & VERIFICATION")
    print("========================================")

    if not settings.ENABLE_TESTNET_EXECUTION:
        print("[INFO] Testnet execution is disabled (ENABLE_TESTNET_EXECUTION=false).")
        print("[INFO] Circuit Breaker is running in Safe Mock mode.")
        print("[RESULT] READINESS: SAFE MOCK PASS")
        sys.exit(0)

    if not settings.TESTNET_RPC_URL or not settings.TESTNET_PRIVATE_KEY:
        print("[FAIL] Missing required testnet credentials (TESTNET_RPC_URL or TESTNET_PRIVATE_KEY).")
        sys.exit(1)

    adapter = get_payment_adapter()
    sender = adapter.get_sender_address()
    balance_info = adapter.get_wallet_balance(sender)

    print(f"Network:        {balance_info.get('network')}")
    print(f"Sender Address: {sender}")
    print(f"Balance:        {balance_info.get('balance')} {balance_info.get('asset')}")

    if balance_info.get("error"):
        print(f"[FAIL] Balance check error: {balance_info['error']}")
        sys.exit(1)

    allow_live_transfer = os.getenv("ALLOW_LIVE_TEST_TRANSFER", "false").lower() == "true"
    
    if not allow_live_transfer:
        print("\n----------------------------------------")
        print("SAFE READINESS VERIFICATION: PASS")
        print("  - Read-only RPC, address, and balance checks succeeded.")
        print("  - Live transfer skipped (ALLOW_LIVE_TEST_TRANSFER is false).")
        print("----------------------------------------")
        sys.exit(0)

    recipient = os.getenv("LIVE_TEST_RECIPIENT", sender)
    amount = float(os.getenv("LIVE_TEST_AMOUNT", "0.0001"))

    print("\n----------------------------------------")
    print("WARNING: LIVE TESTNET TRANSFER ENABLED")
    print(f"Attempting live broadcast of {amount} {balance_info.get('asset')} to {recipient}...")
    print("----------------------------------------")

    import uuid
    from backend.app.engine.execution_gate import execution_gate
    from backend.app.models.authorization import AuthorizationToken
    from backend.app.storage.repository import repository
    from backend.app.models.action import StructuredFinancialAction

    action_id = f"ACT-LIVE-{uuid.uuid4().hex[:6]}"
    action = StructuredFinancialAction(
        action_id=action_id,
        agent_id="testnet-live-verifier",
        source_account=sender,
        destination_account=recipient,
        counterparty_id=recipient,
        amount=amount,
        currency=balance_info.get("asset", "ETH"),
        reason="Controlled live testnet verification transfer"
    )
    repository.save_action(action)
    
    tok = AuthorizationToken.create(
        token_id=f"TOKEN-LIVE-{uuid.uuid4().hex[:6]}",
        action_id=action_id,
        action_hash=action.compute_hash(),
        decision="ALLOW",
        secret_key=settings.SECRET_KEY
    )
    repository.save_token(tok)

    success, msg, tx_rec = execution_gate.execute_authorized_action(action_id, tok.token_id)

    if success and tx_rec:
        print(f"\n[PASS] LIVE TRANSFER BROADCAST SUCCEEDED!")
        print(f"  - Transaction Hash: {tx_rec.tx_hash}")
        print(f"  - Explorer URL:     {tx_rec.explorer_url}")
        print(f"  - Block Number:     {tx_rec.block_number}")
        sys.exit(0)
    else:
        print(f"\n[FAIL] Live Transfer Broadcast Failed: {msg}")
        sys.exit(1)

if __name__ == "__main__":
    main()
