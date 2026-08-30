# Circuit Breaker — Final security audit (productization pass)

**Classification:** Security-hardened prototype. Adversarially tested. Fail-closed execution boundary. Not “100% secure.” Not production banking.

## Executive summary

The existing authorization core (policy, HMAC tokens, atomic reservation, velocity including in-flight work, mock vs Sepolia honesty) was preserved and extended. Productization added a judge-facing UI, Attack Lab wired to the live engine, demo APIs, MCP/TrueForge packaging, and extra adversarial tests.

No path was found that executes a payment without a valid, bound, unexpired token after policy ALLOW/approved REVIEW. Concurrent same-action execution remains 1 success / 19 reject in tests and the demo.

## Architecture

Untrusted agent → TrueForge (orchestration) → MCP tools → structured action → Circuit Breaker → token → execution gate → mock or Sepolia adapter → audit chain.

## Threat model

See `docs/THREAT_MODEL.md`.

## Security controls verified in this pass

- Missing / empty `token_id` → HTTP 400 / gate refuse
- Forged HMAC (`cb-secret-key-2026`) → signature mismatch
- Payload mutation → hash mismatch
- Replay → already executed
- REVIEW without approval → refuse
- Adapter false / exception → fail closed, token ISSUED again
- 20-thread same action → adapter once
- Velocity race → committed total ≤ daily limit
- Duplicate invoice (including amount-changed same invoice id) → BLOCK
- Token A cannot execute action B
- Concurrent human approval → one grant
- Mock tx prefix `mock-tx-`, `explorer_url` is None
- GET action redacts HMAC signature
- Amount: reject ≤0, non-finite, >2 decimal places
- MCP `execute_payment` without token does not move money

## Adversarial / concurrency tests

`tests/test_all_security_scenarios.py` (38) + `tests/test_adversarial_extra.py` (10) + `tests/test_api_surface.py` (6) = **54 passed**.

## Findings in this pass

| Item | Result |
| :--- | :--- |
| Demo replay/concurrent after $1,000 safe pay | Duplicate vendor+amount blocked first execute — **fixed** by unique demo amounts |
| Token signature in GET `/api/actions/{id}` | **Redacted** |
| `.env.example` previously enabled testnet with a dummy key | **Corrected** to mock-safe placeholders |
| LIMITATIONS still claimed mock `0x…` hashes | **Corrected** to `mock-tx-` |
| TrueForge | Packaged skill + stdio MCP; **demo is in-process sandbox** |
| Qodo | **Not run** in this environment |

No remaining authorization bypass identified in the Python control plane under the tested attacks. Host compromise, stolen `SECRET_KEY`, or stolen Sepolia keys remain out of scope.

## Remaining limitations

See `docs/LIMITATIONS.md`. In-memory repository. Audit chain is local tamper-evidence. Sepolia live broadcast **not verified** here.

## Mock mode

Default. Demo and Attack Lab refuse to run if `ENABLE_TESTNET_EXECUTION=true`.

## Sepolia status

Adapter fail-closed paths tested. **Real Sepolia broadcast: NOT VERIFIED.**

## TrueForge / MCP

- MCP tool boundary: **yes** (`execute_payment` requires token)
- stdio FastMCP: `scripts/run_mcp.py`
- Judge demo: in-process calls to the same tools (no LLM)

## Audit chain

SHA-256 linked events. `/api/audit/verify` is real. Tamper helper is explicit and for demo only.

## Final test results (this environment)

```
Backend tests:       PASS (54)
Security tests:      PASS
Concurrency tests:   PASS
Frontend build:      PASS
Frontend lint:       PASS
Demo:                PASS
Audit verification:  PASS (via tests + demo)
Mock safety:         PASS
Sepolia real execution: NOT VERIFIED
Coverage (backend/app): 84%
```
