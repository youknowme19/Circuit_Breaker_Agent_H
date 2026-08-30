# CIRCUIT BREAKER — Security Model & Cryptographic Specification

> **Tagline:** *"The agent can be fooled. The money doesn't have to be."*

---

## 1. Security Axioms

1. **AI Reasoning is Untrusted:** No natural-language LLM output, chain-of-thought, prompt context, or tool output is trusted as an authorization claim.
2. **Authority Enclave Separation:** The agent cannot issue authorization decisions. Authorization can only be issued by the Circuit Breaker control plane.
3. **Execution Gate Fail-Closed:** If any verification step fails, or if Circuit Breaker is unreachable, execution MUST be denied.
4. **Tamper-Evident Evidence:** All authorization state transitions and decisions generate an immutable, cryptographically chained audit log.

---

## 2. Cryptographic Authorization Token Specification

When Circuit Breaker evaluates a transaction and decides `ALLOW` (or when `REVIEW` receives valid human approval), it issues an immutable **AuthorizationToken**.

### 2.1. Token Schema

```json
{
  "token_id": "AUTH-78901234",
  "action_id": "ACT-10291",
  "action_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "decision": "ALLOW",
  "issued_at": "2026-08-20T19:35:00Z",
  "expires_at": "2026-08-20T19:50:00Z",
  "human_approval_id": null,
  "signature": "8f3a9b1...crypto_signature..."
}
```

### 2.2. Action Hash Computation
$$\text{ActionHash} = \text{SHA256}(\text{CanonicalJSON}(\text{StructuredAction}))$$

Where `CanonicalJSON` sorts keys lexicographically and strips extraneous whitespace.

If any field of `StructuredAction` (such as `amount`, `destination_account`, `counterparty_id`) is modified between authorization and execution, $\text{ActionHash}$ changes, causing the Execution Gate to immediately fail verification.

---

## 3. Cryptographic Audit Log (Hash-Chain) Specification

Each audit event $E_i$ contains:
- `event_id`: Unique event string
- `timestamp`: ISO-8601 UTC timestamp
- `action_id`: Linked financial action ID
- `decision`: Decision output (`ALLOW`, `REVIEW`, `BLOCK`)
- `risk_score`: Computed FraudGraph risk float $[0.0, 1.0]$
- `violations`: Array of policy violation objects
- `previous_hash`: $H(E_{i-1})$
- `event_hash`: $H(E_i)$

### 3.1. Event Hash Formula
$$H(E_i) = \text{SHA256}(E_i.\text{event\_id} + E_i.\text{timestamp} + E_i.\text{action\_id} + E_i.\text{decision} + E_i.\text{previous\_hash})$$

Genesis Event $E_0$:
$$E_0.\text{previous\_hash} = \text{"0000000000000000000000000000000000000000000000000000000000000000"}$$

---

## 4. Execution Gate Control Flow

```
[Agent Execution Request] 
          │
          ▼
Is AuthorizationToken Present? ──NO──► DENY EXECUTION
          │ YES
          ▼
Is Token Signature Valid? ───────NO──► DENY EXECUTION
          │ YES
          ▼
Is Current Time < Token TTL? ────NO──► DENY EXECUTION
          │ YES
          ▼
Does ActionHash match Token? ────NO──► DENY EXECUTION
          │ YES
          ▼
Was Decision ALLOW or APPROVED? ─NO──► DENY EXECUTION
          │ YES
          ▼
[ALLOW PAYMENT EXECUTION / TESTNET TX]
```
