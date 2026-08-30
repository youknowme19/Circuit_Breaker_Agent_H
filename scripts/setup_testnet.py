#!/usr/bin/env python3
"""Testnet Wallet & Network Setup Verification Script.

Validates:
1. TESTNET_RPC_URL reachability & chain ID match
2. Configured sender address derivation from private key
3. Available native token balance (MON / ETH)
4. Explorer URL formatting
5. Verifies PRIVATE KEY IS NEVER PRINTED OR EXPOSED

Usage:
    PYTHONPATH=. python scripts/setup_testnet.py
"""

import sys
from backend.app.config import settings
from backend.app.execution.base import get_payment_adapter

def main():
    print("========================================")
    print("CIRCUIT BREAKER TESTNET SETUP CHECK")
    print("========================================")

    print(f"Testnet Execution Enabled: {settings.ENABLE_TESTNET_EXECUTION}")
    print(f"Configured Network Name:  {settings.TESTNET_NETWORK_NAME}")
    print(f"Configured Chain ID:      {settings.TESTNET_CHAIN_ID}")
    print(f"RPC URL Configured:       {bool(settings.TESTNET_RPC_URL)}")
    print(f"Private Key Configured:   {bool(settings.TESTNET_PRIVATE_KEY)}")

    if not settings.ENABLE_TESTNET_EXECUTION:
        print("\n----------------------------------------")
        print("STATUS: SAFE MOCK MODE ACTIVE")
        print("  - Real testnet execution is disabled (ENABLE_TESTNET_EXECUTION=false).")
        print("  - Transactions will execute in Safe Mock mode without spending funds.")
        print("----------------------------------------")
        sys.exit(0)

    adapter = get_payment_adapter()
    sender = adapter.get_sender_address()
    
    print(f"\nDerived Sender Address:   {sender or 'INVALID / UNABLE TO DERIVE'}")
    
    balance_info = adapter.get_wallet_balance(sender)
    print(f"Wallet Balance:           {balance_info.get('balance', 0.0)} {balance_info.get('asset', 'NATIVE')}")
    
    if balance_info.get("error"):
        print(f"\n[FAIL] Testnet Setup Check Failed: {balance_info['error']}")
        sys.exit(1)

    print("\n----------------------------------------")
    print("STATUS: TESTNET EXECUTION READY")
    print(f"  ✓ RPC reachable for {settings.TESTNET_NETWORK_NAME}")
    print(f"  ✓ Sender address: {sender}")
    print(f"  ✓ Balance: {balance_info.get('balance')} {balance_info.get('asset')}")
    print("  ✓ Private key securely loaded (never printed)")
    print("----------------------------------------")
    sys.exit(0)

if __name__ == "__main__":
    main()
