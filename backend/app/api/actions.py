from typing import List, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from backend.app.models.action import StructuredFinancialAction
from backend.app.models.decision import AuthorizationDecision
from backend.app.engine.decision_engine import decision_engine
from backend.app.engine.execution_gate import execution_gate
from backend.app.storage.repository import repository
from backend.app.observability import emit, redact_token

router = APIRouter(prefix="/api/actions", tags=["actions"])


class ActionProposalRequest(BaseModel):
    action: StructuredFinancialAction


class ExecuteActionRequest(BaseModel):
    token_id: Optional[str] = Field(default=None, description="Authorization token ID issued by Circuit Breaker. Required.")


@router.post(
    "/propose",
    response_model=AuthorizationDecision,
    status_code=status.HTTP_201_CREATED,
    summary="Propose a financial action",
    description="Submit a structured financial action. The agent is untrusted; Circuit Breaker independently normalizes and evaluates the payload.",
)
def propose_action(req: ActionProposalRequest):
    emit("AGENT_ACTION_PROPOSED", f"Proposed {req.action.action_id}", action_id=req.action.action_id, amount=req.action.amount)
    emit("ACTION_NORMALIZED", f"Normalized {req.action.action_id}", action_id=req.action.action_id, action_hash=req.action.compute_hash())
    decision = decision_engine.evaluate_action(req.action)
    return decision


@router.get("/feed", summary="List proposed actions with decisions")
def list_actions():
    rows = []
    for action in repository.list_actions():
        decision = repository.get_decision(action.action_id)
        approval = repository.get_human_approval(action.action_id)
        txs = [t for t in repository.list_transactions() if t.action_id == action.action_id]
        rows.append({
            "action": action,
            "decision": decision,
            "human_approval": approval,
            "transaction": txs[-1] if txs else None,
        })
    return rows


@router.get("/{action_id}", summary="Fetch action, decision, approval, and redacted token")
def get_action(action_id: str):
    action = repository.get_action(action_id)
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")
    decision = repository.get_decision(action_id)
    approval = repository.get_human_approval(action_id)
    token = repository.get_token(action_id)
    txs = [t for t in repository.list_transactions() if t.action_id == action_id]
    return {
        "action": action,
        "decision": decision,
        "human_approval": approval,
        "token": redact_token(token),
        "transaction": txs[-1] if txs else None,
        "token_lifecycle": repository.get_token_lifecycle(token.token_id) if token else None,
    }


@router.post(
    "/{action_id}/execute",
    summary="Execute an authorized action",
    description="Fail-closed execution. Requires an explicit token_id bound to this action. Missing, forged, expired, mutated, or replayed tokens are refused.",
    responses={
        400: {"description": "Execution refused (missing token, policy, hash, replay, adapter failure)"},
        404: {"description": "Action not found"},
    },
)
def execute_action(action_id: str, req: ExecuteActionRequest):
    token_id = req.token_id
    if not token_id or not token_id.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="EXECUTION_REFUSED: Missing explicit authorization token in request body"
        )

    success, message, tx_record = execution_gate.execute_authorized_action(action_id, token_id.strip())
    if not success:
        code = status.HTTP_400_BAD_REQUEST
        if "not found" in message.lower():
            code = status.HTTP_404_NOT_FOUND
        raise HTTPException(status_code=code, detail=message)
    return {
        "success": True,
        "message": message,
        "transaction": tx_record
    }
