#!/usr/bin/env python3
"""CIRCUIT BREAKER — Judge demo. Safe mock only. Exit 0 iff security properties hold."""

import sys
from backend.app.config import settings
from backend.app.demo.scenarios import run_full_demo
from backend.app.execution.mock_adapter import MockPaymentAdapter
from backend.app.storage.repository import repository
from backend.app.risk.graph import fraud_graph


def banner():
    print("╔════════════════════════════════════════════════════════╗")
    print("║          CIRCUIT BREAKER SECURITY DEMO                 ║")
    print("║  The agent can be fooled. The money doesn't have to be.║")
    print("╚════════════════════════════════════════════════════════╝")


def main() -> int:
    if settings.ENABLE_TESTNET_EXECUTION:
        print("REFUSED: ENABLE_TESTNET_EXECUTION=true. Demo is mock-only.")
        return 1

    MockPaymentAdapter.force_failure = False
    MockPaymentAdapter.force_exception = False
    repository.reset()
    fraud_graph.reset()

    banner()
    print(f"\nExecution mode: DEMO-SAFE MOCK")
    print("TrueForge: in-process MCP sandbox (no LLM keys)")
    print("MCP: same tool functions as stdio server\n")

    result = run_full_demo(reset=True)
    labels = [
        ("[01] SAFE PAYMENT", "ALLOW → EXECUTED"),
        ("[02] PROMPT INJECTION", "BLOCK → PREVENTED"),
        ("[03] REVIEW PAYMENT", "REVIEW → HUMAN APPROVAL REQUIRED"),
        ("[04] FRAUDGRAPH", "REVIEW/BLOCK"),
        ("[05] REPLAY ATTACK", "DENIED"),
        ("[06] CONCURRENT DOUBLE-SPEND", "1 SUCCESS / 19 DENIED"),
        ("[07] AUDIT TAMPERING", "DETECTED"),
    ]
    for i, scene in enumerate(result["scenes"]):
        title, expected = labels[i]
        mark = "PASS" if scene.get("passed") else "FAIL"
        print(f"{title}")
        print(f"     EXPECTED: {expected}")
        print(f"     RESULT:   {mark}")
        if scene.get("attack") == "CONCURRENT_DOUBLE_SPEND":
            print(f"     ATTEMPTS: {scene.get('attempts')}  EXECUTIONS: {scene.get('executions')}  DENIED: {scene.get('denied')}")
        print()

    status = "PASS" if result["passed"] else "FAIL"
    print("────────────────────────────────────────")
    print(f"FINAL SECURITY STATUS: {status}")
    print("────────────────────────────────────────")
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
