# Circuit Breaker — Limitations

Honest disclosures for judges.

| Topic | Reality |
| :--- | :--- |
| Status | Security-hardened **prototype**, not a bank product |
| Mock mode | Default. `mock-tx-…` ids. **No** Etherscan URL |
| Sepolia | Opt-in. Requires RPC URL + private key. Not verified in CI unless you broadcast |
| Keys | Never commit them. Missing keys + testnet enabled → fail closed |
| TrueForge | Skill + MCP server packaged. Demo path is **in-process sandbox** without LLM keys |
| MCP | Real stdio server exists. Demos do not pretend to open a network MCP session |
| Audit chain | Tamper-evident SHA-256 log in local memory/process. **Not** decentralized consensus. **Not** “blockchain audit” |
| State | In-process repository. Reset on process restart. Not a durable bank ledger |
| Banking | No production core-banking or card-network integration |
| Compliance | No SOC2 / PCI / banking certification |
| Infrastructure | A compromised host, stolen `SECRET_KEY`, or stolen wallet key is out of scope |
| FraudGraph | Heuristic topology signals, not a GNN and not complete fraud coverage |
| Qodo | Not run in this agent environment unless separately executed |

Do **not** claim: production banking security, real bank integration, or blockchain consensus for the audit log.
