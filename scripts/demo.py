#!/usr/bin/env python3
"""CIRCUIT BREAKER — Narrative demo (mock-safe). Exit 0 if all scenes hold."""

import os
import sys

repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if sys.path[0] != repo_root:
    sys.path.insert(0, repo_root)

from backend.app.config import settings
from backend.app.demo.scenarios import run_full_demo



def main() -> int:
    if settings.ENABLE_TESTNET_EXECUTION:
        print("REFUSED: demo will not run with ENABLE_TESTNET_EXECUTION=true")
        return 1
    result = run_full_demo(reset=True)
    print("\nCIRCUIT BREAKER — THE AGENT CAN BE FOOLED. THE MONEY DOESN'T HAVE TO BE.\n")
    for scene in result["scenes"]:
        name = scene.get("scene") or scene.get("attack")
        print(f"  {name}: {'PASS' if scene.get('passed') else 'FAIL'}")
    print(f"\nFINAL: {'PASS' if result['passed'] else 'FAIL'}\n")
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
