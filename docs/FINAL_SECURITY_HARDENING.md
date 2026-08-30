# Circuit Breaker — Final Security Hardening Specification

> **"Deterministic error tagging and fail-closed audit trace events for financial execution authorization."**

---

## 1. Problem Addressed
Previously, execution authorization failures returned generic text messages without explicit deterministic error tags. This made client-side classification and structured audit logging ambiguous when distinguishing between forged signatures, expired tokens, mutated action payloads, and token replay attempts.

---

## 2. Hardening Improvements
- **Deterministic Error Tags**: Appended explicit tags `[REJECTED_FORGED_SIGNATURE]`, `[REJECTED_EXPIRED_TOKEN]`, `[REJECTED_MUTATED_PAYLOAD]`, and `[REJECTED_CONSUMED_TOKEN]` to `ExecutionGate` error responses.
- **Redacted Trace Events**: Enhanced `backend/app/engine/execution_gate.py` to emit structured audit trace events with secret key redaction via `backend/app/observability.py`.

---

## 3. Verified Security Invariant
$$\text{ONE AUTHORIZATION} \longrightarrow \text{EXACTLY ONE FINANCIAL EXECUTION}$$

---

## 4. Test Coverage Summary (65 Passing Scenarios)
- `test_63_final_hardening_deterministic_error_codes`: Valid execution succeeds and token replay yields `[REJECTED_CONSUMED_TOKEN]`.
- `test_64_final_hardening_forged_and_mutated_rejections`: Forged HMAC signature yields `[REJECTED_FORGED_SIGNATURE]`.
- `test_65_final_hardening_expired_ttl_rejection`: Expired TTL yields `[REJECTED_EXPIRED_TOKEN]`.
