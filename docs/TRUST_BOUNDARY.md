# Circuit Breaker — Trust Boundaries

> The agent is untrusted. MCP is a capability interface. Circuit Breaker is the authorization control plane. The execution gate is the enforcement boundary. The payment adapter is execution only.

```
[Untrusted agent] → [TrueForge harness] → [MCP tools] → [Circuit Breaker] → [Gate] → [Adapter]
```

## Agent

Never trusted. May be prompt-injected. May call tools in any order. Must not call adapters.

## TrueForge

Runs the model loop, MCP client, sandbox, and optional human tool-approval pauses. That pause is **not** Circuit Breaker authorization.

## MCP

Exposes `propose_payment` and `execute_payment`. Missing tokens fail closed. MCP must not become a bypass.

### Transports

- **In-process sandbox:** demo scripts and the UI demo agent call the same Python tool functions. Documented honestly. No fake sockets.
- **stdio FastMCP:** `scripts/run_mcp.py` for a real TrueForge connection.

## Circuit Breaker

Policy, risk, tokens, approvals, audit. Deterministic Python.

## Execution gate

The only path to an adapter. Fail closed.

## Adapters

- **Mock:** local, `mock-tx-*`, no Etherscan. Safe default.
- **Sepolia:** real RPC, EIP-1559, broadcast, explorer URL only after success. Opt-in. Different trust (you trust RPC + key handling).
