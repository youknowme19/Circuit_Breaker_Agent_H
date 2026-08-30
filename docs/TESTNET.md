# CIRCUIT BREAKER — Testnet & Demo-Safe Mode Specification

> **Tagline:** *"The agent can be fooled. The money doesn't have to be."*

---

## 1. Demo-Safe Mode & Zero-Credential Default

Circuit Breaker provides a dual-mode execution engine designed for absolute security:

1. **Demo-Safe Mode (Default):**
   - Runs out-of-the-box without requiring any testnet funds, RPC providers, or private keys.
- Uses a deterministic **Mock Payment Adapter** that returns `mock-tx-…` identifiers and **never** an Etherscan URL.
   - Ideal for local development, CI/CD pipelines, automated testing, and offline hackathon presentations.

2. **Real Testnet Execution Mode (Opt-In):**
   - Activated strictly via environment variables (`ENABLE_TESTNET_EXECUTION=true`).
   - Connects to an EVM testnet (e.g., Sepolia) using `TESTNET_RPC_URL` and `TESTNET_PRIVATE_KEY`.
   - Submits real testnet smart contract transactions / transfers and returns verified on-chain transaction hashes.

---

## 2. Environment Variables Configuration (`.env.example`)

```bash
# Circuit Breaker Server Settings
PORT=8000
ENVIRONMENT=development
LOG_LEVEL=info

# Execution Adapter Selection (Default: false for Demo-Safe Mode)
ENABLE_TESTNET_EXECUTION=false

# Testnet Settings (Only required if ENABLE_TESTNET_EXECUTION=true)
TESTNET_RPC_URL=https://rpc.sepolia.org
TESTNET_CHAIN_ID=11155111
TESTNET_PRIVATE_KEY=

# TrueForge (optional)
TRUEFORGE_API_KEY=
```

---

## 3. Strict Secret Handling Rules

- Secrets (`TESTNET_PRIVATE_KEY`, `TRUEFORGE_API_KEY`) must **NEVER** be committed to git.
- Secrets must **NEVER** be printed in application logs or standard output.
- Secrets must **NEVER** be exposed in API responses or dashboard UI views.
- If invalid keys or RPC connection failures occur, the execution gate immediately **FAILS CLOSED** (denies execution).

---

## 4. Execution Matrix

| Decision | Demo-Safe Mode Output | Real Testnet Mode Output | Blockchain TX in Dashboard |
| :--- | :--- | :--- | :--- |
| `ALLOW` | Deterministic Mock Hash (`0x7f9a...`) | Verified On-Chain Sepolia Hash | `EXECUTED ✓ (0x7f9a...)` |
| `REVIEW` (Approved) | Deterministic Mock Hash (`0x3c2b...`) | Verified On-Chain Sepolia Hash | `EXECUTED ✓ (0x3c2b...)` |
| `REVIEW` (Rejected) | Execution Denied | None | `REJECTED BY HUMAN ✕ (NONE)` |
| `BLOCK` | Execution Denied | None | `BLOCKED BY POLICY ✕ (NONE)` |
