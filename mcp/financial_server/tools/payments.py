from typing import Any, Dict, Optional
from backend.app.models.action import StructuredFinancialAction
from backend.app.engine.decision_engine import decision_engine
from backend.app.engine.execution_gate import execution_gate
from backend.app.observability import emit


def propose_payment_tool(action_dict: Dict[str, Any]):
    action = StructuredFinancialAction(**action_dict)
    emit("ACTION_NORMALIZED", f"MCP propose_payment {action.action_id}", action_id=action.action_id)
    decision = decision_engine.evaluate_action(action)
    return decision.model_dump()


def execute_payment_tool(action_id: str, authorization_token_id: Optional[str] = None):
    """Executes payment strictly via Execution Gate. Missing token cannot execute."""
    success, message, tx_record = execution_gate.execute_authorized_action(action_id, authorization_token_id)
    return {
        "success": success,
        "message": message,
        "transaction": tx_record.model_dump() if tx_record else None,
    }
