#!/usr/bin/env python3
"""Read-Only Verification Script for Monad Testnet Wallet Readiness.

1. Loads TESTNET_PRIVATE_KEY from root .env ONLY.
2. Derives public address via eth_account.
3. Asserts derived address == 0x57d1Cf3D387de087Eda90a1cC81eAc608F7a8f55.
4. Connects to Monad RPC & verifies Chain ID is 10143.
5. Queries real MON balance.
6. Reports wallet readiness (READ-ONLY — NEVER spends funds).

Usage:
    PYTHONPATH=. ./venv/bin/python scripts/verify_live_key.py
"""

import os
import sys
from dotenv import load_dotenv

repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

# Reload .env explicitly
load_dotenv(os.path.join(repo_root, ".env"), override=True)

from backend.app.config import settings
from backend.app.execution.monad_testnet_adapter import MonadTestnetAdapter

EXPECTED_SENDER = "0x57d1Cf3D387de087Eda90a1cC81eAc608F7a8f55"

def verify_live_key_readonly():
    print("====================================================================")
    print("   CIRCUIT BREAKER — READ-ONLY MONAD TESTNET VERIFICATION           ")
    print("====================================================================")

    # 1. Environment & Mode Verification
    print(f"\n[1/3] Checking .env Configuration...")
    print(f"  ENABLE_TESTNET_EXECUTION:  {settings.ENABLE_TESTNET_EXECUTION}")
    print(f"  ALLOW_LIVE_TEST_TRANSFER:  {os.getenv('ALLOW_LIVE_TEST_TRANSFER', 'false')}")
    print(f"  TESTNET_RPC_URL:           {settings.TESTNET_RPC_URL}")
    print(f"  TESTNET_CHAIN_ID:          {settings.TESTNET_CHAIN_ID}")
    print(f"  TESTNET_NETWORK_NAME:      {settings.TESTNET_NETWORK_NAME}")

    if not settings.ENABLE_TESTNET_EXECUTION:
        print("\n  ❌ FAIL CLOSED: ENABLE_TESTNET_EXECUTION=false in .env")
        sys.exit(1)

    if settings.TESTNET_CHAIN_ID != 10143:
        print(f"\n  ❌ FAIL CLOSED: Expected Chain ID 10143, got {settings.TESTNET_CHAIN_ID}")
        sys.exit(1)

    # 2. Derive Public Address from TESTNET_PRIVATE_KEY
    print(f"\n[2/3] Deriving Public Address from TESTNET_PRIVATE_KEY...")
    pkey = settings.TESTNET_PRIVATE_KEY.strip()
    if not pkey:
        print("\n  ❌ FAIL CLOSED: TESTNET_PRIVATE_KEY is empty in root .env file.")
        sys.exit(1)

    adapter = MonadTestnetAdapter()
    derived_addr = adapter.get_sender_address()
    if not derived_addr:
        print("\n  ❌ FAIL CLOSED: Unable to derive valid EVM address from TESTNET_PRIVATE_KEY.")
        sys.exit(1)

    print(f"  Derived Address:  {derived_addr}")
    print(f"  Expected Address: {EXPECTED_SENDER}")

    if derived_addr.lower() != EXPECTED_SENDER.lower():
        print(f"\n  ❌ FAIL CLOSED: Derived address ({derived_addr}) does NOT match expected sender ({EXPECTED_SENDER})!")
        sys.exit(1)

    print("  ✓ Derived address matches expected sender!")

    # 3. Query Real Monad Testnet RPC Balance
    print(f"\n[3/3] Querying Real Monad Testnet RPC Balance...")
    bal_info = adapter.get_wallet_balance(derived_addr)
    mon_bal = bal_info.get("balance", 0.0)
    print(f"  RPC Balance:      {mon_bal:.6f} MON ({bal_info.get('network')})")

    if mon_bal < 0.02:
        print(f"\n  ❌ FAIL CLOSED: Wallet balance ({mon_bal} MON) is insufficient for transfer + gas.")
        sys.exit(1)

    print("\n====================================================================")
    print(f"  Network:        Monad Testnet")
    print(f"  Chain ID:       10143")
    print(f"  Sender:         {derived_addr}")
    print(f"  Balance:        {mon_bal:.6f} MON")
    print(f"  Wallet Status:  READY (Read-only check passed — 0 funds spent)")
    print("====================================================================")

if __name__ == "__main__":
    verify_live_key_readonly()
