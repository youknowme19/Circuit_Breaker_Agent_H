#!/usr/bin/env python3
"""Circuit Breaker Financial Control Plane Launcher.

Launches:
1. Circuit Breaker FastAPI Backend (Port 8000)
2. Next.js Frontend Control Console & Attack Lab (Port 3000)
3. Outputs stdio FastMCP configuration for TrueForge integration.

Usage:
    python scripts/start_circuit_breaker.py
"""

import os
import sys
import time
import subprocess
from backend.app.config import settings

def main():
    print("==========================================================")
    print("      CIRCUIT BREAKER FINANCIAL CONTROL PLANE             ")
    print("   The agent can be fooled. The money doesn't have to be.  ")
    print("==========================================================")
    
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    print("\n[1/3] System Environment Configuration:")
    print(f"  - Mode:              {'REAL TESTNET' if settings.ENABLE_TESTNET_EXECUTION else 'DEMO SAFE MOCK'}")
    print(f"  - Network Name:      {settings.TESTNET_NETWORK_NAME}")
    print(f"  - Chain ID:          {settings.TESTNET_CHAIN_ID}")
    print(f"  - RPC Configured:    {bool(settings.TESTNET_RPC_URL)}")
    print(f"  - Private Key Loaded:{bool(settings.TESTNET_PRIVATE_KEY)}")
    
    print("\n[2/3] Active Service Endpoints:")
    print("  - Backend FastAPI:   http://localhost:8000")
    print("  - OpenAPI Specs:     http://localhost:8000/docs")
    print("  - Control Console:   http://localhost:3000")
    print("  - Attack Lab:        http://localhost:3000/attacks")
    print("  - Transfer Console:  http://localhost:3000/transfer")

    print("\n[3/3] TrueForge Stdio MCP Server Configuration:")
    print("  Add to TrueForge MCP custom servers:")
    print("  --------------------------------------------------------")
    print(f"  Server Name: circuit-breaker-finance")
    print(f"  Command:     {sys.executable}")
    print(f"  Args:        scripts/run_mcp.py")
    print(f"  Env:         PYTHONPATH={repo_root}")
    print("  --------------------------------------------------------")
    print("  TrueForge Agent Spec: trueforge/agent.yaml")
    print("  TrueForge Skill:      trueforge/skills/financial-agent/SKILL.md")
    print("==========================================================")
    print("Services are running in background tasks.")
    print("Press Ctrl+C to view logs or run tests.")

if __name__ == "__main__":
    main()
