#!/usr/bin/env python3
"""Start the Circuit Breaker financial MCP server over stdio (real MCP transport).

TrueForge binds this process as an MCP server. The tools call Circuit Breaker;
execute_payment cannot move money without a valid authorization token.

Usage:
    PYTHONPATH=. python scripts/run_mcp.py
"""

from mcp.financial_server.server import mcp

if __name__ == "__main__":
    mcp.run(transport="stdio")
