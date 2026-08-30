import uuid
from typing import Dict, Any
from backend.app.models.action import StructuredFinancialAction, ActionType
from mcp.financial_server.tools.invoices import get_invoice_tool
from mcp.financial_server.tools.payments import propose_payment_tool, execute_payment_tool
from mcp.financial_server.tools.accounts import get_account_tool
from mcp.financial_server.tools.counterparties import get_counterparty_tool
from backend.app.observability import emit


class TrueForgePaymentAgent:
    """Circuit Breaker Financial Agent.

    In demo-safe / in-process sandbox mode this runner calls the same MCP tool
    functions TrueForge binds over stdio/SSE. It never calls the payment adapter.
    Authorization is owned by Circuit Breaker; this agent cannot override BLOCK/REVIEW.
    """

    def __init__(self, agent_id: str = "circuit-breaker-financial-agent"):
        self.agent_id = agent_id

    def process_user_instruction(self, user_instruction: str, invoice_id: str) -> Dict[str, Any]:
        session_id = f"SESS-{uuid.uuid4().hex[:8]}"
        events = [{"step": 1, "name": "Agent Started", "session_id": session_id, "instruction": user_instruction, "mode": "in-process-mcp-sandbox"}]
        emit("AGENT_ACTION_PROPOSED", "Agent session started", session_id=session_id, invoice_id=invoice_id)

        events.append({"step": 2, "name": "MCP Call: get_invoice", "invoice_id": invoice_id})
        inv = get_invoice_tool(invoice_id)
        if "error" in inv:
            events.append({"step": 3, "name": "Error", "message": inv["error"]})
            return {"status": "FAILED", "events": events, "error": inv["error"]}

        events.append({"step": 3, "name": "MCP Call: get_account", "account_id": "ACC-001"})
        get_account_tool("ACC-001")
        events.append({"step": 4, "name": "MCP Call: get_counterparty", "counterparty_id": inv["counterparty_id"]})
        get_counterparty_tool(inv["counterparty_id"])

        destination = "ACC-002" if inv["counterparty_id"] == "VENDOR-001" else "ACC-991"
        if inv["counterparty_id"] == "VENDOR-777":
            destination = "ACC-002"

        action_id = f"ACT-{uuid.uuid4().hex[:6].upper()}"
        action = StructuredFinancialAction(
            action_id=action_id,
            agent_id=self.agent_id,
            type=ActionType.TRANSFER,
            amount=inv["amount"],
            currency=inv.get("currency", "USD"),
            source_account="ACC-001",
            destination_account=destination,
            counterparty_id=inv["counterparty_id"],
            invoice_id=inv["invoice_id"],
            reference=f"Payment for {inv['invoice_id']}",
            reason=f"Processing invoice {inv['invoice_id']} per request: {user_instruction}",
            metadata={"invoice_description": inv.get("description"), "untrusted": True},
        )

        events.append({
            "step": 5,
            "name": "MCP Call: propose_payment",
            "action_id": action_id,
            "amount": action.amount,
            "note": "Invoice text is untrusted. Circuit Breaker evaluates the structured action, not the prompt.",
        })
        decision = propose_payment_tool(action.model_dump())
        decision_value = decision.get("decision") if isinstance(decision, dict) else str(decision)
        events.append({
            "step": 6,
            "name": "Circuit Breaker Evaluation",
            "decision": decision_value,
            "risk_score": decision.get("risk_score") if isinstance(decision, dict) else None,
            "violations": decision.get("violations") if isinstance(decision, dict) else [],
        })

        if decision_value == "BLOCK":
            events.append({"step": 7, "name": "Execution Blocked", "message": "Circuit Breaker issued BLOCK. Agent cannot override."})
            return {
                "status": "BLOCKED",
                "session_id": session_id,
                "action": action.model_dump(),
                "decision": decision,
                "blockchain_tx": "NONE",
                "events": events,
            }

        if decision_value == "REVIEW":
            events.append({"step": 7, "name": "Human Approval Intercept", "message": "REVIEW — agent paused. No execution authority."})
            return {
                "status": "REVIEW_PENDING",
                "session_id": session_id,
                "action": action.model_dump(),
                "decision": decision,
                "blockchain_tx": "NONE",
                "events": events,
            }

        token_id = decision.get("authorization_token") if isinstance(decision, dict) else None
        events.append({"step": 7, "name": "MCP Call: execute_payment", "action_id": action_id, "token_id": token_id})
        exec_res = execute_payment_tool(action_id, token_id)
        tx = exec_res.get("transaction") if isinstance(exec_res, dict) else None
        tx_hash = tx.get("blockchain_tx_hash") if tx else "NONE"
        events.append({"step": 8, "name": "Execution Completed", "success": exec_res.get("success"), "tx_hash": tx_hash})
        return {
            "status": "EXECUTED" if exec_res.get("success") else "EXECUTION_REFUSED",
            "session_id": session_id,
            "action": action.model_dump(),
            "decision": decision,
            "transaction": tx,
            "blockchain_tx": tx_hash or "NONE",
            "events": events,
        }


trueforge_agent = TrueForgePaymentAgent()
