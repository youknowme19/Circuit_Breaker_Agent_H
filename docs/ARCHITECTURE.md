# CIRCUIT BREAKER — Architectural Specification

> **Tagline:** *"The agent can be fooled. The money doesn't have to be."*

---

## 1. System Overview & Core Philosophy

**Circuit Breaker** is an independent authorization and enforcement control plane positioned strictly between AI Agent reasoning and financial execution layers.

In traditional agentic finance architectures, an LLM agent is given direct access to financial execution APIs or tools. This creates an unacceptably large attack surface where prompt injections, invoice manipulation, hallucinated account IDs, or velocity spikes can trigger unauthorized financial transactions.

### Core Architectural Trust Model

- **LLM Reasoning:** Probabilistic reasoning, document extraction, invoice interpretation. (*Untrusted*)
- **TrueForge:** Agent orchestration, session state, MCP tool runtime, sandboxed document reading, human-in-the-loop intercepts. (*Harness*)
- **Circuit Breaker:** Independent deterministic policy evaluation, state velocity tracking, counterparty exposure checks, FraudGraph risk signals, and audit chain logging. (*Authorization Boundary*)
- **Execution Gate & Blockchain/Testnet:** Downstream payment execution strictly requiring a cryptographically signed, unexpired `AuthorizationToken`. (*Protected Execution Enclave*)

```
                    ┌───────────────────┐
                    │    TRUEFORGE      │
                    │   AGENT SESSION   │
                    └─────────┬─────────┘
                              │
                         MCP TOOLS
                              │
                              ▼
                  ┌──────────────────────┐
                  │  FINANCIAL SYSTEM    │
                  │  (Invoices, State)   │
                  └──────────┬───────────┘
                             │
                     proposed action
                             │
                             ▼
                ╔══════════════════════════╗
                ║     CIRCUIT BREAKER      ║
                ║                          ║
                ║  Policy Engine           ║
                ║  State Engine            ║
                ║  Duplicate Detection     ║
                ║  Counterparty Controls   ║
                ║  FraudGraph Risk Engine  ║
                ║  Audit Chain             ║
                ╚════════════╤═════════════╝
                             │
                    ┌────────┼────────┐
                    ▼        ▼        ▼
                  ALLOW    REVIEW    BLOCK
                    │        │
                    │        ▼
                    │    HUMAN APPROVAL
                    │        │
                    └────┬───┘
                         ▼
                 EXECUTION GATE (Fail-Closed)
                         │
                         ▼
               PAYMENT SIMULATOR / TESTNET
```

---

## 2. Priority Hierarchy & Execution Strategy

1. **TrueForge Agent Harness Integration:** Visible session management, MCP tool calls, sandboxed parsing, human approval pause.
2. **Deterministic Policy Enforcement:** `MAX_TRANSFER`, `DAILY_TRANSFER_LIMIT`, `DUPLICATE_PAYMENT`, `UNKNOWN_DESTINATION`, `NEW_COUNTERPARTY_REVIEW`.
3. **Fail-Closed Execution Gate:** Strict verification of signed `AuthorizationToken`, action hash (`SHA-256`), TTL expiration, and human approval.
4. **Real Testnet Execution Proof:** EVM testnet adapter (Sepolia) with real Tx hash output on `ALLOW`, fallback to Demo-Safe Mock Adapter when credentials are omitted.
5. **Primary Adversarial Demo:** Synthetic malicious prompt injection invoice ($50k) $\to$ Agent proposes $\to$ Circuit Breaker `BLOCK` $\to$ Blockchain TX: `NONE`.
6. **Tamper-Evident Audit Chain:** SHA-256 event chaining and chain verification endpoint `/api/audit/verify`.
7. **Control Plane Security Dashboard:** Modern visual hierarchy, real-time action stream, interactive human approval modal, live testnet tx feedback.
8. **FraudGraph Behavioral Risk Signals:** Graph network analysis ($A \to B \to C \to D \to E$ layering detection) as a signal input to the unified decision engine.
9. **GNN / Advanced Stretch Features:** Explicitly deferred until core execution boundary, TrueForge harness, testnet adapter, and primary demo are 100% stable.

---

## 3. Demo-Safe Mode & Credential Isolation

Circuit Breaker includes an explicit **Demo-Safe Mode**:
- Zero hardcoded credentials or private keys in source code, logs, screenshots, or repos.
- Default configuration uses deterministic **Mock Execution Adapter** if no RPC/private keys are provided in `.env`.
- Testnet execution is **opt-in** via `ENABLE_TESTNET_EXECUTION=true` + `TESTNET_RPC_URL` + `TESTNET_PRIVATE_KEY`.
- Secrets are never printed in logs or returned via API responses.

---

## 4. TrueForge Harness Mechanics

TrueForge acts as the central harness:
- **Session Persistence:** Manages agent execution lifecycle across multi-turn reasoning and human-in-the-loop pauses.
- **MCP Server Protocol:** Financial tools are exposed strictly via standard MCP protocol.
- **Sandboxed Execution:** Invoice reading runs inside sandboxed execution to isolate untrusted text payloads.
- **Human Intercept:** Suspends execution during `REVIEW` state and presents structured approval UI to the human operator.

---

## 5. Fail-Closed Security Guarantees

If any of the following occur, the Execution Gate immediately **DENIES EXECUTION**:
- Missing `AuthorizationToken`
- Token signature mismatch or invalid key
- Action payload hash mismatch (`SHA-256(Action)`)
- Token TTL expired (> 15 minutes)
- Circuit Breaker backend / database unreachable
- Human approval status `REJECTED` or unverified
- Decision was `BLOCK`
