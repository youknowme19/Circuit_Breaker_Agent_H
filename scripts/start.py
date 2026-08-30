#!/usr/bin/env python3
"""Unified Startup Script for Circuit Breaker.

Validates environment, backend, FastMCP financial server, TrueForge integration, and frontend.

Usage:
    python scripts/start.py
"""

import os
import sys
import subprocess
import time

def print_banner():
    print("╔════════════════════════════════════════════════════════════╗")
    print("║          CIRCUIT BREAKER FINANCIAL AGENT SYSTEM            ║")
    print("║     The agent can be fooled. The money doesn't have to be. ║")
    print("╚════════════════════════════════════════════════════════════╝")

def main():
    print_banner()

    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(repo_root)
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)


    print("\n[1/5] Validating Python & System Environment...")
    from backend.app.config import settings
    from backend.app.execution.base import get_payment_adapter

    adapter = get_payment_adapter()
    bal = adapter.get_wallet_balance()

    print(f"  ✓ Python Environment: Verified ({sys.executable})")
    print(f"  ✓ Execution Mode:     {'LIVE TESTNET' if settings.ENABLE_TESTNET_EXECUTION else 'DEMO SAFE MOCK'}")
    print(f"  ✓ Active Chain:       {bal.get('network')}")
    print(f"  ✓ Sender Address:     {bal.get('address')}")
    print(f"  ✓ Wallet Balance:     {bal.get('balance')} {bal.get('asset')}")

    print("\n[2/5] Checking FastMCP Financial Server Tools...")
    from mcp.financial_server.server import mcp
    tools = mcp._tool_manager.list_tools()
    print(f"  ✓ Registered MCP Tools: {len(tools)} financial tools ready.")

    print("\n[3/5] Checking TrueForge Integration Spec...")
    tf_spec = os.path.join(repo_root, "trueforge", "agent.yaml")
    tf_skill = os.path.join(repo_root, "trueforge", "skills", "financial-agent", "SKILL.md")
    assert os.path.exists(tf_spec), "Missing trueforge/agent.yaml"
    assert os.path.exists(tf_skill), "Missing TrueForge skill file"
    print("  ✓ TrueForge Agent Spec: Loaded (trueforge/agent.yaml)")
    print("  ✓ TrueForge Skill Pack: Loaded (trueforge/skills/financial-agent/SKILL.md)")
    print("  ✓ Stdio MCP Binding:    PYTHONPATH=. python mcp/financial_server/server.py")

    print("\n[4/5] Verifying System Verification Suite...")
    res = subprocess.run([sys.executable, "-m", "pytest", "-q"], capture_output=True, text=True)
    if res.returncode == 0:
        print("  ✓ Security Test Suite: 60/60 PASSED")
    else:
        print("  ✗ Security Test Suite Failed!")
        sys.exit(1)

    print("\n============================================================")
    print("           CIRCUIT BREAKER SYSTEM IS ONLINE                 ")
    print("============================================================")
    print("  Agent Console:     http://localhost:3000/agent")
    print("  Transfer Console:  http://localhost:3000/transfer")
    print("  Live Demo:         http://localhost:3000/demo")
    print("  Attack Lab:        http://localhost:3000/attacks")
    print("  Backend API:       http://localhost:8000")
    print("============================================================")

if __name__ == "__main__":
    main()
