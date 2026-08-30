from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from backend.app.config import settings
from backend.app.models.authorization import AuthorizationToken
from backend.app.models.decision import DecisionType
from backend.app.storage.repository import repository
from backend.app.observability import emit, redact_token

router = APIRouter(prefix="/api/actions", tags=["approvals"])


class HumanApprovalRequest(BaseModel):
    approver: str = "security-admin"


@router.post(
    "/{action_id}/approve",
    summary="Grant human approval for a REVIEW action",
    description="Issues an authorization token only after a REVIEW decision. Concurrent approvals succeed exactly once.",
)
def approve_action(action_id: str, req: HumanApprovalRequest):
    action = repository.get_action(action_id)
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")

    decision = repository.get_decision(action_id)
    if not decision or decision.decision != DecisionType.REVIEW:
        raise HTTPException(status_code=400, detail="Action is not pending human review")

    approval_record = repository.save_human_approval(action_id, approved=True, approver=req.approver)
    if approval_record is None:
        raise HTTPException(status_code=409, detail="HUMAN_APPROVAL_ALREADY_RECORDED")

    token_obj = AuthorizationToken.create(
        token_id=repository.next_id("AUTH"),
        action_id=action.action_id,
        action_hash=action.compute_hash(),
        decision="APPROVED",
        secret_key=settings.SECRET_KEY,
        human_approval_id=approval_record["approval_id"]
    )
    repository.save_token(token_obj)
    decision.authorization_token = token_obj.token_id
    emit("HUMAN_APPROVAL_GRANTED", f"Approved {action_id}", action_id=action_id, approver=req.approver)

    return {
        "success": True,
        "message": "Human approval granted. Authorization token issued.",
        "approval": approval_record,
        "token": redact_token(token_obj),
        "token_id": token_obj.token_id,
    }


@router.post("/{action_id}/reject", summary="Reject a REVIEW action")
def reject_action(action_id: str, req: HumanApprovalRequest):
    action = repository.get_action(action_id)
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")

    approval_record = repository.save_human_approval(action_id, approved=False, approver=req.approver)
    if approval_record is None:
        raise HTTPException(status_code=409, detail="HUMAN_APPROVAL_ALREADY_RECORDED")
    emit("HUMAN_APPROVAL_REJECTED", f"Rejected {action_id}", action_id=action_id, approver=req.approver)
    return {
        "success": True,
        "message": "Action rejected by human operator.",
        "approval": approval_record
    }
