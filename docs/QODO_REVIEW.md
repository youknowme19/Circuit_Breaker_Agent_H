# Qodo Security & Architecture Review Guide

> **Status:** QODO REVIEW NOT AVAILABLE IN THIS ENVIRONMENT (Qodo CLI/extension not installed in local environment).

This document outlines the security-critical files prepared for automated review by **Qodo** (Qodo Merge / Qodo Gen / Qodo Cover).

---

## High-Priority Security Targets for Review

### 1. Execution Gate & Atomic Reservation
- **File:** [backend/app/engine/execution_gate.py](file:///Volumes/SSD/circuit_breaker/backend/app/engine/execution_gate.py)
- **Key Invariant:** Ensures an authorization token can be executed at most once. Enforces atomic reservation under repository lock prior to calling payment adapters.
- **Review Focus:** Replay protection, double-spend prevention under concurrency, fail-closed handling on adapter exceptions.

### 2. Cryptographic HMAC Authorization Tokens
- **File:** [backend/app/models/authorization.py](file:///Volumes/SSD/circuit_breaker/backend/app/models/authorization.py)
- **Key Invariant:** HMAC-SHA256 signature verification over canonical action digest (`token_id:action_id:action_hash:decision:issued_at:expires_at`). Uses `hmac.compare_digest` for constant-time comparison.
- **Review Focus:** Signature tampering, constant-time validation, secret key handling.

### 3. Chain-Agnostic Testnet Payment Adapters
- **Files:**
  - [backend/app/execution/base.py](file:///Volumes/SSD/circuit_breaker/backend/app/execution/base.py)
  - [backend/app/execution/evm_testnet_adapter.py](file:///Volumes/SSD/circuit_breaker/backend/app/execution/evm_testnet_adapter.py)
  - [backend/app/execution/monad_testnet_adapter.py](file:///Volumes/SSD/circuit_breaker/backend/app/execution/monad_testnet_adapter.py)
- **Key Invariant:** Private key (`TESTNET_PRIVATE_KEY`) is read strictly within backend execution adapters and is never returned over MCP tools or HTTP responses. If RPC is unreachable or credentials missing, fails closed without synthetic hashes.
- **Review Focus:** Credential leakage prevention, raw transaction signing, Etherscan / Monad Explorer URL generation.

### 4. Thread-Safe State Repository
- **File:** [backend/app/storage/repository.py](file:///Volumes/SSD/circuit_breaker/backend/app/storage/repository.py)
- **Key Invariant:** Thread-safe singleton utilizing `threading.Lock` to guarantee atomic state transitions (`ISSUED → RESERVED → CONSUMED`).
- **Review Focus:** Lock granularity, race condition resistance under high concurrency.

### 5. MCP Tool Surface & Boundary
- **File:** [mcp/financial_server/server.py](file:///Volumes/SSD/circuit_breaker/mcp/financial_server/server.py)
- **Key Invariant:** Exposes financial capabilities (`get_wallet_balance`, `estimate_transfer`, `request_transfer`, etc.) without exposing execution authority. `execute_payment` requires a valid Circuit Breaker authorization token.
- **Review Focus:** Interface separation, LLM authorization bypass defense.

---

## Local Automated Verification Alternative

In the absence of Qodo in this local environment, the repository relies on a 60-scenario pytest suite:

```bash
PYTHONPATH=. pytest -v
python scripts/verify_all.py
```
