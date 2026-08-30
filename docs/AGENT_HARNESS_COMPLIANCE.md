# Circuit Breaker — Agent Harness Hackathon Compliance Matrix

> **"TrueForge provides the agent execution harness. Circuit Breaker provides the deterministic financial security boundary."**

---

## Harness Compliance Audit Matrix

| Hackathon Expectation | Circuit Breaker Implementation | Verification Evidence & Location | Status |
| :--- | :--- | :--- | :--- |
| **TrueForge Agent Harness** | TrueForge v0.1.4 running on port `8790` (`http://localhost:8790`). Manages agent runtime, session orchestration, and skill packs. | [`trueforge/agent.yaml`](file:///Volumes/SSD/circuit_breaker/trueforge/agent.yaml), [`trueforge/skills/circuit-breaker-finance/SKILL.md`](file:///Volumes/SSD/circuit_breaker/trueforge/skills/circuit-breaker-finance/SKILL.md), `/healthz` API endpoint | **VERIFIED** |
| **FastMCP Tools Surface** | 19 financial tools registered via FastMCP stdio transport (`mcp/financial_server/server.py`). | [`mcp/financial_server/server.py`](file:///Volumes/SSD/circuit_breaker/mcp/financial_server/server.py), [`scripts/verify_mcp.py`](file:///Volumes/SSD/circuit_breaker/scripts/verify_mcp.py) | **VERIFIED** |
| **Tool Execution Boundary** | Categorized into READ ONLY, PREPARATION, and EXECUTION. Only `execute_payment` can move funds and strictly requires a Circuit Breaker HMAC token. | [`mcp/financial_server/tools/wallets.py`](file:///Volumes/SSD/circuit_breaker/mcp/financial_server/tools/wallets.py), [`frontend/app/agent/tools/page.tsx`](file:///Volumes/SSD/circuit_breaker/frontend/app/agent/tools/page.tsx) | **VERIFIED** |
| **Human-in-the-Loop Approval** | High-risk payments or unknown counterparties transition to `REVIEW` requiring explicit operator `APPROVE` / `REJECT`. | [`backend/app/api/approvals.py`](file:///Volumes/SSD/circuit_breaker/backend/app/api/approvals.py), [`frontend/components/HumanApprovalModal.tsx`](file:///Volumes/SSD/circuit_breaker/frontend/components/HumanApprovalModal.tsx) | **VERIFIED** |
| **Deterministic Security Layer** | Policy Engine, velocity limits, duplicate payment detection, FraudGraph risk scoring, and prompt injection filters evaluate actions independently of LLM output. | [`backend/app/engine/policy_engine.py`](file:///Volumes/SSD/circuit_breaker/backend/app/engine/policy_engine.py), [`backend/app/engine/decision_engine.py`](file:///Volumes/SSD/circuit_breaker/backend/app/engine/decision_engine.py) | **VERIFIED** |
| **Single-Use Execution Gate** | `ExecutionGate` consumes HMAC authorization tokens under an atomic single-use reservation lock. Replays return `TOKEN_ALREADY_CONSUMED`. | [`backend/app/engine/execution_gate.py`](file:///Volumes/SSD/circuit_breaker/backend/app/engine/execution_gate.py), `test_19_replay_authorization_denied` | **VERIFIED** |
| **Concurrency Double-Spend Defense** | Atomic reservation lock prevents double-spend under 20-thread race conditions (yielding 1 execution, 19 denials). | `test_33_true_20_thread_concurrent_execution_race` | **VERIFIED** |
| **Monad Testnet Integration** | Layer-1 EVM transaction signing & broadcast on Monad Testnet (`Chain ID 10143`). | [`backend/app/execution/monad_testnet_adapter.py`](file:///Volumes/SSD/circuit_breaker/backend/app/execution/monad_testnet_adapter.py), Block #57687057 | **VERIFIED** |
| **Tamper-Evident Audit Chain** | SHA-256 hash-chained immutable audit ledger for every policy decision and transaction event. | [`backend/app/audit/hash_chain.py`](file:///Volumes/SSD/circuit_breaker/backend/app/audit/hash_chain.py), [`frontend/app/audit/page.tsx`](file:///Volumes/SSD/circuit_breaker/frontend/app/audit/page.tsx) | **VERIFIED** |
| **Qodo Code Review Workflow** | Pull Request security review workflow configured on GitHub feature branches. | [`docs/QODO_REVIEW.md`](file:///Volumes/SSD/circuit_breaker/docs/QODO_REVIEW.md), GitHub PR `hackathon/final-hardening` | **VERIFIED** |

---

## Architectural Responsibility Separation

1. **TrueForge Agent Harness**: Discovers tools over FastMCP, interprets user natural language, and prepares structured intent payloads.
2. **Circuit Breaker Control Plane**: Evaluates risk, enforces velocity & injection rules, and issues time-bound cryptographic HMAC signatures.
3. **Execution Gate & Adapter**: Server-side isolated signing, single-use reservation lock, and RPC broadcast to Monad Testnet.
