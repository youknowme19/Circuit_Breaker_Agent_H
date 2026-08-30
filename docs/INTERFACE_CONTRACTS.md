# CIRCUIT BREAKER — Interface Contracts & Data Schemas

> **Tagline:** *"The agent can be fooled. The money doesn't have to be."*

---

## 1. Structured Financial Action Schema

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "StructuredFinancialAction",
  "type": "object",
  "properties": {
    "action_id": { "type": "string", "example": "ACT-10291" },
    "agent_id": { "type": "string", "example": "finance-agent-01" },
    "type": { "type": "string", "enum": ["TRANSFER", "INVOICE_PAYMENT", "REFUND"] },
    "amount": { "type": "number", "minimum": 0.01, "example": 50000.00 },
    "currency": { "type": "string", "example": "USD" },
    "source_account": { "type": "string", "example": "ACC-001" },
    "destination_account": { "type": "string", "example": "ACC-991" },
    "counterparty_id": { "type": "string", "example": "VENDOR-991" },
    "invoice_id": { "type": "string", "nullable": true, "example": "INV-2041" },
    "reference": { "type": "string", "nullable": true, "example": "Q3 Infrastructure Payment" },
    "timestamp": { "type": "string", "format": "date-time" },
    "reason": { "type": "string", "example": "Invoice INV-2041 verification and settlement" },
    "metadata": { "type": "object", "additionalProperties": true }
  },
  "required": ["action_id", "agent_id", "type", "amount", "currency", "source_account", "destination_account", "counterparty_id", "timestamp"]
}
```

---

## 2. Policy Violation & Decision Schemas

### 2.1. Policy Violation
```json
{
  "policy_id": "MAX_TRANSFER",
  "severity": "BLOCK",
  "message": "Transaction exceeds maximum allowed single transfer limit",
  "actual": 50000.00,
  "limit": 10000.00,
  "details": { "currency": "USD" }
}
```

### 2.2. Unified Authorization Decision
```json
{
  "decision_id": "DEC-90812",
  "action_id": "ACT-10291",
  "decision": "BLOCK",
  "risk_score": 0.91,
  "requires_human_approval": false,
  "violations": [
    {
      "policy_id": "MAX_TRANSFER",
      "severity": "BLOCK",
      "message": "Transaction exceeds maximum allowed single transfer limit",
      "actual": 50000.00,
      "limit": 10000.00
    }
  ],
  "risk_signals": ["HIGH_AMOUNT_OUTLIER", "CIRCULAR_LAYERING_PATTERN"],
  "evaluated_at": "2026-08-20T19:35:02Z",
  "authorization_token": null
}
```

---

## 3. Financial MCP Tool Definitions

The TrueForge Agent interacts with the financial environment strictly via these Model Context Protocol (MCP) tools:

### Tool 1: `get_account`
- **Input:** `{ "account_id": "ACC-001" }`
- **Output:** Account balance, status, daily cumulative spent.

### Tool 2: `get_invoice`
- **Input:** `{ "invoice_id": "INV-2041" }`
- **Output:** Vendor name, amount, line items, status, raw payload.

### Tool 3: `get_transaction_history`
- **Input:** `{ "account_id": "ACC-001", "limit": 20 }`
- **Output:** Array of historical transactions.

### Tool 4: `get_counterparty`
- **Input:** `{ "counterparty_id": "VENDOR-991" }`
- **Output:** Verification status, historical volume, risk flags.

### Tool 5: `get_risk_context`
- **Input:** `{ "destination_account": "ACC-991" }`
- **Output:** FraudGraph risk score, graph neighbors, layering alerts.

### Tool 6: `propose_payment`
- **Input:** `StructuredFinancialAction` payload
- **Output:** Circuit Breaker evaluation result (`ALLOW`, `REVIEW`, `BLOCK`).

### Tool 7: `authorize_payment`
- **Input:** `{ "action_id": "ACT-10291", "human_approval_token": "..." }`
- **Output:** Signed `AuthorizationToken`.

### Tool 8: `execute_payment`
- **Input:** `{ "action_id": "ACT-10291", "authorization_token": "..." }`
- **Output:** Execution status, Blockchain TX hash (if testnet), Audit Event ID.

### Tool 9: `get_audit_event`
- **Input:** `{ "event_id": "EVT-10291" }`
- **Output:** Full audit event record.

### Tool 10: `verify_audit_chain`
- **Input:** `{}`
- **Output:** `{ "valid": true, "events_checked": 42 }`
