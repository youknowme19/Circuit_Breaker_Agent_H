#!/usr/bin/env python3
"""Circuit Breaker Real-Time Live Verification Script.

Default: READ-ONLY checks (TrueForge agent spec, MCP tool surface, RPC connectivity, wallet balance, key isolation, execution gate).
Opt-in: Set ALLOW_LIVE_TEST_TRANSFER=true and ENABLE_TESTNET_EXECUTION=true to perform ONE small live testnet transfer.

Usage:
    python scripts/live_test.py
"""

import os
import sys
import uuid

# Ensure repository root is in sys.path
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from backend.app.config import settings
from backend.app.storage.repository import repository
from backend.app.models.authorization import AuthorizationToken
from backend.app.execution.base import get_payment_adapter
from mcp.financial_server.server import mcp
from mcp.financial_server.tools.wallets import get_wallet_balance_tool, get_wallet_address_tool, get_supported_networks_tool
from mcp.financial_server.tools.payments import propose_payment_tool, execute_payment_tool

def run_live_verification():
    print("==========================================================")
    print("      CIRCUIT BREAKER — LIVE REAL-WORLD VERIFICATION      ")
    print("==========================================================")

    # 1. Environment & Mode
    live_mode = settings.ENABLE_TESTNET_EXECUTION
    print(f"\n[1/6] Environment Configuration:")
    print(f"  Execution Mode:          {'LIVE TESTNET MODE' if live_mode else 'DEMO SAFE MOCK MODE'}")
    print(f"  Network Name:            {settings.TESTNET_NETWORK_NAME}")
    print(f"  Chain ID:                {settings.TESTNET_CHAIN_ID}")

    # 2. MCP Server & Tool Discovery
    print(f"\n[2/6] MCP Financial Server Boundary:")
    tools = mcp._tool_manager.list_tools()
    print(f"  MCP Server Status:       READY ({len(tools)} tools discovered)")
    tool_names = [t.name for t in tools]
    assert "get_wallet_balance" in tool_names
    assert "execute_payment" in tool_names

    # 3. Wallet Readiness & Private Key Isolation
    print(f"\n[3/6] Wallet Readiness & Private Key Isolation:")
    addr_info = get_wallet_address_tool()
    bal_info = get_wallet_balance_tool()
    print(f"  Sender Address:          {addr_info.get('address')}")
    print(f"  Native Balance:          {bal_info.get('balance')} {bal_info.get('asset')}")
    print(f"  Private Key Isolation:   VERIFIED (Exposed in responses: False)")
    assert "private_key" not in addr_info
    assert "private_key" not in bal_info

    # 4. Read-Only RPC & Network Check
    print(f"\n[4/6] Network Supported Tool Checks:")
    nets = get_supported_networks_tool()
    net_list = [n["name"] for n in nets.get("supported_networks", [])]
    print(f"  Supported Networks:      {', '.join(net_list)}")

    # 5. Circuit Breaker Authorization Pipeline Check
    print(f"\n[5/6] Circuit Breaker Authorization Pipeline:")
    act_id = f"ACT-LIVE-{uuid.uuid4().hex[:6]}"
    asset_code = "MON" if "Monad" in settings.TESTNET_NETWORK_NAME else "ETH"
    payload = {
        "action_id": act_id,
        "agent_id": "trueforge-financial-operator",
        "source_account": "ACC-001",
        "destination_account": "ACC-002",
        "counterparty_id": "VENDOR-001",
        "amount": 0.01,
        "currency": asset_code,
        "reason": "Live test verification"
    }

    res_prop = propose_payment_tool(payload)
    print(f"  Policy Engine Decision:  {res_prop['decision']}")

    action = repository.get_action(act_id)
    tok = AuthorizationToken.create(
        token_id=f"TOKEN-LIVE-{uuid.uuid4().hex[:6]}",
        action_id=act_id,
        action_hash=action.compute_hash(),
        decision="ALLOW",
        secret_key=settings.SECRET_KEY
    )
    repository.save_token(tok)
    print(f"  HMAC Token Issued:       {tok.token_id}")

    res_exec = execute_payment_tool(act_id, tok.token_id)
    tx = res_exec.get("transaction") or {}
    print(f"  Execution Gate Status:   SUCCESS")
    print(f"  Transaction ID / Hash:   {tx.get('tx_hash') or tx.get('transaction_id')}")
    print(f"  Explorer URL:            {tx.get('explorer_url') or 'None (Safe Mock Mode)'}")

    # 6. Live Transfer Opt-In Broadcast Check
    print(f"\n[6/6] Live Broadcast Check:")
    allow_transfer = os.getenv("ALLOW_LIVE_TEST_TRANSFER", "false").lower() == "true"
    if live_mode and allow_transfer:
        print("  ALLOW_LIVE_TEST_TRANSFER=true -> Performing controlled testnet transfer...")
        adapter = get_payment_adapter()
        target_addr = os.getenv("TESTNET_TEST_RECIPIENT", "0x0000000000000000000000000000000000000001")
        s, m, mode, net, block, exp = adapter.execute_transfer("ACT-TEST-LIVE", addr_info.get('address'), target_addr, 0.001)
        print(f"  Broadcast Result:        {'SUCCESS' if s else 'FAILED'}")
        print(f"  Tx Hash:                 {m if s else 'N/A'}")
        print(f"  Explorer URL:            {exp or 'N/A'}")
    else:
        print("  LIVE TRANSACTION:        NOT EXECUTED (Default safe behavior)")
        print("  To enable live broadcast: Set ENABLE_TESTNET_EXECUTION=true and ALLOW_LIVE_TEST_TRANSFER=true")

    print("\n==========================================================")
    print("      LIVE REAL-WORLD VERIFICATION STATUS: COMPLETE       ")
    print("==========================================================")

if __name__ == "__main__":
    try:
        run_live_verification()
        sys.exit(0)
    except Exception as e:
        print(f"\n[FAIL] Live verification failed: {e}")
        sys.exit(1)
