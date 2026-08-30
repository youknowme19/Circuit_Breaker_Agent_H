#!/usr/bin/env python3
"""CIRCUIT BREAKER — Real Sepolia Testnet Verification Script."""

import sys
from backend.app.config import settings
from backend.app.execution.evm_testnet_adapter import EVMTestnetAdapter

def main():
    print("=" * 80)
    print("  CIRCUIT BREAKER — SEPOLIA TESTNET CONFIGURATION VERIFICATION")
    print("=" * 80)

    print(f"ENABLE_TESTNET_EXECUTION : {settings.ENABLE_TESTNET_EXECUTION}")
    print(f"TESTNET_RPC_URL          : {settings.TESTNET_RPC_URL or 'NOT CONFIGURED'}")
    print(f"TESTNET_CHAIN_ID         : {settings.TESTNET_CHAIN_ID}")
    print(f"PRIVATE_KEY PRESENT      : {'YES (Masked)' if settings.TESTNET_PRIVATE_KEY else 'NO'}\n")

    if not settings.ENABLE_TESTNET_EXECUTION or not settings.TESTNET_RPC_URL or not settings.TESTNET_PRIVATE_KEY:
        print("RESULT: REAL SEPOLIA TESTNET IS NOT CONFIGURED.")
        print("Circuit Breaker is operating in DEMO-SAFE MOCK MODE.")
        print("To enable real Sepolia execution, set in .env:")
        print("  ENABLE_TESTNET_EXECUTION=true")
        print("  TESTNET_RPC_URL=https://rpc.sepolia.org")
        print("  TESTNET_PRIVATE_KEY=0x_your_sepolia_private_key")
        sys.exit(0)

    adapter = EVMTestnetAdapter()
    print("Testing server-side Sepolia RPC connection and transaction preparation...")
    success, tx_hash, mode, chain, block_num, explorer_url = adapter.execute_transfer(
        action_id="VERIFY-SEP-001",
        source="ACC-001",
        destination="ACC-002",
        amount=100.0,
        currency="USD"
    )

    print(f"Execution Success : {success}")
    print(f"Execution Mode    : {mode}")
    print(f"Chain / Network   : {chain}")
    print(f"Latest Block      : {block_num}")
    print(f"Transaction Hash  : {tx_hash}")
    print(f"Explorer URL      : {explorer_url}")

    if success and tx_hash.startswith("0x"):
        print("\n✓ REAL SEPOLIA TESTNET ADAPTER VERIFIED WORKING SUCCESSFULLY.")
    else:
        print("\n✕ SEPOLIA TESTNET ADAPTER FAILED TO BROADCAST.")

if __name__ == "__main__":
    main()
