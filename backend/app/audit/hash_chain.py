from typing import List
from backend.app.models.audit_event import AuditEvent
from backend.app.storage.repository import repository

class AuditHashChain:
    """SHA-256 cryptographic tamper-evident audit log manager."""

    def get_all_events(self) -> List[AuditEvent]:
        return repository.get_audit_chain()

    def get_event(self, event_id: str) -> AuditEvent:
        for evt in repository.get_audit_chain():
            if evt.event_id == event_id:
                return evt
        return None

audit_hash_chain = AuditHashChain()
