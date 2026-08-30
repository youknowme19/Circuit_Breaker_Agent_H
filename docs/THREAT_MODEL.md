# Circuit Breaker — Threat Model

Security-hardened prototype. Not a claim of “100% secure.”

## Assets

- Money-movement authority (execution gate + payment adapter)
- Authorization tokens (HMAC payload + lifecycle)
- Structured financial actions and canonical hashes
- Audit records (hash chain)
- Account, invoice, and counterparty records in the local repository

## Threat actors

- Malicious prompt / prompt injection
- Malicious invoice body
- Compromised or over-eager agent
- Compromised MCP client
- Malicious direct API caller
- Replay attacker
- Concurrent / race attacker
- Audit-storage tamperer (local process / disk)

## Trust boundaries

1. **Untrusted:** prompts, invoices, LLM output, tool arguments, agent JSON.
2. **Harness:** TrueForge session, MCP transport, sandbox — orchestration only.
3. **Control plane:** Circuit Breaker policy, tokens, approvals, audit.
4. **Enforcement:** execution gate.
5. **Adapter:** mock ledger vs Sepolia RPC (different trust; mock is not a chain).

## Security controls

- Independent normalization and pydantic validation (finite amounts, precision, ids)
- Deterministic policy / velocity / duplicate / FraudGraph
- HMAC-SHA256 tokens, `hmac.compare_digest`, configured `SECRET_KEY`
- Token–action binding and canonical hash
- Atomic reservation (ISSUED → RESERVED → CONSUMED)
- Velocity includes in-flight reservations
- Duplicate invoice lock during reservation
- REVIEW requires human approval recorded server-side
- Fail closed on adapter/RPC errors
- Mock txs never get explorer URLs
- Audit chain verification endpoint
- Structured logs without secrets or full signatures

## Out of scope

- Compromised host, stolen `SECRET_KEY`, stolen Sepolia key
- Production banking rails, KYC/AML certification
- Decentralized consensus for the audit log
- Guaranteeing the LLM will not *propose* a bad payment (it will; we block execution)
- TrueForge cloud tenancy hardening
