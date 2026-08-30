from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.app.audit.verifier import audit_verifier
from backend.app.observability import emit
from backend.app.storage.repository import repository

router = APIRouter(prefix="/api/audit", tags=["audit"])


class TamperSimulationRequest(BaseModel):
    event_id: str
    new_decision: str = "ALLOW"


@router.get("", summary="Retrieve full audit log chain")
def get_audit_log():
    return repository.get_audit_chain()


@router.get("/{event_id}", summary="Retrieve a single audit event")
def get_audit_event(event_id: str):
    for evt in repository.get_audit_chain():
        if evt.event_id == event_id:
            return evt
    raise HTTPException(status_code=404, detail="Audit event not found")


@router.post("/verify", summary="Verify SHA-256 hash chain integrity")
def verify_audit_chain():
    result = audit_verifier.verify_chain()
    if not result.get("valid"):
        emit("AUDIT_TAMPER_DETECTED", "Audit chain verification failed", broken_at=result.get("broken_at"))
    return result


@router.post("/tamper-simulate", summary="Demo helper: mutate an audit event without updating its hash")
def tamper_simulate(req: TamperSimulationRequest):
    success = audit_verifier.simulate_tamper(req.event_id, req.new_decision)
    if not success:
        raise HTTPException(status_code=404, detail="Audit event not found for tamper simulation")
    emit("AUDIT_TAMPER_DETECTED", "Tamper simulation applied", event_id=req.event_id)
    return {"success": True, "message": f"Simulated tamper on event '{req.event_id}'."}
