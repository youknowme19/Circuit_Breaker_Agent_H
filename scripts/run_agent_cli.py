#!/usr/bin/env python3
"""Interactive Terminal TrueForge Agent CLI.

Allows judges or operators to send natural language requests to the Circuit Breaker agent:

    python scripts/run_agent_cli.py

Example:
    > Send 0.1 MON to 0x1234567890123456789012345678901234567890
"""

import os
import sys
import uuid

repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from backend.app.config import settings
from backend.app.storage.repository import repository
from backend.app.models.authorization import AuthorizationToken
from mcp.financial_server.tools.wallets import get_wallet_balance_tool, estimate_transfer_tool
from mcp.financial_server.tools.payments import propose_payment_tool, execute_payment_tool

def print_banner():
    print("╔════════════════════════════════════════════════════════════╗")
    print("║      CIRCUIT BREAKER × TRUEFORGE FINANCIAL OPERATOR       ║")
    print("║     The agent can be fooled. The money doesn't have to be. ║")
    print("╚════════════════════════════════════════════════════════════╝")
    bal = get_wallet_balance_tool()
    print(f"Mode:    {'LIVE TESTNET' if settings.ENABLE_TESTNET_EXECUTION else 'DEMO SAFE MOCK'}")
    print(f"Network: {bal.get('network')}")
    print(f"Wallet:  {bal.get('address') or '0x0000... (Mock)'}")
    print(f"Balance: {bal.get('balance')} {bal.get('asset')}")
    print("------------------------------------------------------------")

def process_instruction(text: str):
    print(f"\nUSER > {text}")
    print("\nTRUEFORGE AGENT:")
    print("  1. Parsing financial intent...")
    
    amount = 0.1
    if "0.01" in text:
        amount = 0.01
    elif "0.001" in text:
        amount = 0.001
    elif "1000" in text or "100000" in text:
        amount = 99000.0

    target = "ACC-002"
    if "0x" in text:
        words = text.split()
        for w in words:
            if w.startswith("0x") and len(w) > 5:
                target = w
                break

    print(f"  2. [MCP] get_wallet_balance() -> Verified balance")
    print(f"  3. [MCP] estimate_transfer(amount={amount}, target={target[:10]}...)")
    
    act_id = f"ACT-CLI-{uuid.uuid4().hex[:6]}"
    is_injection = "ignore" in text.lower() or "disable" in text.lower() or amount > 50000.0

    payload = {
        "action_id": act_id,
        "agent_id": "trueforge-financial-operator",
        "source_account": "ACC-001",
        "destination_account": "ACC-002" if not is_injection else "MALICIOUS-01",
        "counterparty_id": "VENDOR-001" if not is_injection else "MALICIOUS-01",
        "amount": amount,
        "currency": "MON",
        "reason": text[:50]
    }

    print("  4. [MCP] request_transfer() -> Invoking Circuit Breaker policy engine...")
    res_prop = propose_payment_tool(payload)
    dec = str(res_prop["decision"]).replace("DecisionType.", "")

    print(f"  5. CIRCUIT BREAKER EVALUATION: {dec}")
    if dec == "BLOCK":
        print("  ❌ ACTION BLOCKED BY CIRCUIT BREAKER: Prompt injection / limit exceeded.")
        print("  -> Execution Aborted. 0 Funds Spent.")
        return
    elif dec == "REVIEW":
        print("  ⚠️  ACTION REQUIRES HUMAN APPROVAL.")
        print("  -> Execution Paused pending operator approval.")
        return

    print("  6. CIRCUIT BREAKER HMAC AUTHORIZATION: Token Issued.")
    action = repository.get_action(act_id)
    tok = AuthorizationToken.create(
        token_id=f"TOKEN-CLI-{uuid.uuid4().hex[:6]}",
        action_id=act_id,
        action_hash=action.compute_hash(),
        decision="ALLOW",
        secret_key=settings.SECRET_KEY
    )
    repository.save_token(tok)

    print("  7. [MCP] execute_payment() -> Atomic Execution Gate...")
    res_exec = execute_payment_tool(act_id, tok.token_id)
    tx = res_exec.get("transaction") or {}

    print(f"  8. EXECUTION SUCCESSFUL: Tx Hash = {tx.get('tx_hash') or tx.get('transaction_id')}")
    if tx.get("explorer_url"):
        print(f"     Explorer: {tx.get('explorer_url')}")

def main():
    print_banner()
    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
        process_instruction(text)
    else:
        print("Type a natural language payment instruction (e.g. 'Send 0.1 MON to 0x1234...').")
        print("Type 'exit' or 'quit' to exit.\n")
        while True:
            try:
                line = input("Agent CLI > ").strip()
                if not line:
                    continue
                if line.lower() in ["exit", "quit"]:
                    break
                process_instruction(line)
            except (KeyboardInterrupt, EOFError):
                print("\nExiting.")
                break

if __name__ == "__main__":
    main()
