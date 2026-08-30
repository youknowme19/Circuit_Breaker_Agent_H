# Qodo Security & Architecture Review Workflow

> **Repository PR Review Target:** [`https://github.com/youknowme19/Circuit_Breaker_Agent_H/pull/new/security/final-execution-hardening`](https://github.com/youknowme19/Circuit_Breaker_Agent_H/pull/new/security/final-execution-hardening)

This document outlines the security-critical files and pull request review workflow configured for automated review by **Qodo** (Qodo Merge / Qodo Gen / Qodo Cover).

---

## High-Priority Security Targets for Review

### 1. Execution Gate & Atomic Reservation
- **File:** [`backend/app/engine/execution_gate.py`](file:///Volumes/SSD/circuit_breaker/backend/app/engine/execution_gate.py)
- **Key Invariant:** Ensures an authorization token can be executed at most once. Enforces atomic reservation under repository lock prior to calling payment adapters.
- **Review Focus:** Replay protection, double-spend prevention under concurrency, fail-closed handling on adapter exceptions, deterministic error code tags (`[REJECTED_FORGED_SIGNATURE]`, `[REJECTED_EXPIRED_TOKEN]`, `[REJECTED_MUTATED_PAYLOAD]`, `[REJECTED_CONSUMED_TOKEN]`).

### 2. Cryptographic HMAC Authorization Tokens
- **File:** [`backend/app/models/authorization.py`](file:///Volumes/SSD/circuit_breaker/backend/app/models/authorization.py)
- **Key Invariant:** HMAC-SHA256 signature verification over canonical action digest (`token_id:action_id:action_hash:decision:issued_at:expires_at`). Uses `hmac.compare_digest` for constant-time comparison.
- **Review Focus:** Signature tampering, constant-time validation, secret key handling.

### 3. Layer-1 Testnet Payment Adapters
- **Files:**
  - [`backend/app/execution/base.py`](file:///Volumes/SSD/circuit_breaker/backend/app/execution/base.py)
  - [`backend/app/execution/evm_testnet_adapter.py`](file:///Volumes/SSD/circuit_breaker/backend/app/execution/evm_testnet_adapter.py)
  - [`backend/app/execution/monad_testnet_adapter.py`](file:///Volumes/SSD/circuit_breaker/backend/app/execution/monad_testnet_adapter.py)
- **Key Invariant:** Private key (`TESTNET_PRIVATE_KEY`) is read strictly within backend execution adapters and is never returned over MCP tools or HTTP responses. If RPC is unreachable or credentials missing, fails closed without synthetic hashes.
- **Review Focus:** Credential leakage prevention, raw transaction signing, Monad Explorer URL generation.

---

## Automated Verification Suite

The repository is validated by a 65-scenario pytest suite:

```bash
PYTHONPATH=. ./venv/bin/python -m pytest -v
./venv/bin/python scripts/verify_all.py
```
