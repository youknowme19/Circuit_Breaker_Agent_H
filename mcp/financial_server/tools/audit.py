from backend.app.audit.verifier import audit_verifier
from backend.app.storage.repository import repository

def get_audit_event_tool(event_id: str):
    chain = repository.get_audit_chain()
    for evt in chain:
        if evt.event_id == event_id:
            return evt.model_dump()
    return {"error": f"Audit event '{event_id}' not found"}

def verify_audit_chain_tool():
    return audit_verifier.verify_chain()
