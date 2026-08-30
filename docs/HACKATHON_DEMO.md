# Hackathon demo — 5 minutes

**What to say:** Autonomous agents should reason about money without owning it.

**Default:** mock mode. No private keys.

## Minute 0–1 — Landing (`/`)

Show the headline. Point at the pipeline: Agent → MCP → Circuit Breaker → Authorization → Gate → Payment.

CTA: **Launch Security Console**.

## Minute 1–2 — Console (`/console`)

System status PROTECTED. Execution: DEMO SAFE / MOCK.

Click **Run Security Demo**. Scenes are live `/api/demo/run` results, not animations.

## Act 1 — Safe payment

Invoice ~$1,000. Agent proposes. Policy ALLOW. Mock execution `mock-tx-…`. No explorer link.

**Why it matters:** legitimate work still completes.

## Act 2 — Prompt injection

Attack Lab → Prompt Injection. Invoice tells the agent to send $99,000.

Agent can propose. Circuit Breaker **BLOCK**. $0 executed.

**Why it matters:** the model can be fooled; the gate cannot be sweet-talked.

## Act 3 — REVIEW

Risky / new counterparty. REVIEW. Agent stops. Operator **APPROVE** hits `/approve` then execute with issued `token_id`.

**Why it matters:** the agent cannot self-approve.

## Act 4 — Replay

Attack Lab → Replay. Second execute **DENIED**.

## Act 5 — Concurrent double spend

20 threads. Show `executions: 1`, `denied: 19`.

## Act 6 — Audit

Audit page → VERIFY CHAIN (valid) → simulate tamper → VERIFY (COMPROMISED). Backend `/api/audit/verify`.

## What not to say

- Do not call mock hashes Sepolia transactions.
- Do not say TrueForge ran the loop unless you actually attached the harness.
- Do not say Qodo reviewed it unless you ran Qodo.
