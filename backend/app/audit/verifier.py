from typing import Dict, Any
from backend.app.storage.repository import repository

class AuditVerifier:
    """Verifies SHA-256 hash chain integrity from genesis to head."""

    def verify_chain(self) -> Dict[str, Any]:
        chain = repository.get_audit_chain()
        if not chain:
            return {"valid": True, "events_checked": 0}

        events_checked = 0

        for i, event in enumerate(chain):
            events_checked += 1

            # 1. Recompute event hash and verify match
            recomputed = event.compute_hash()
            if event.event_hash != recomputed:
                return {
                    "valid": False,
                    "broken_at": event.event_id,
                    "index": i,
                    "reason": f"Payload hash mismatch in event '{event.event_id}' (stored: {event.event_hash[:10]}... != recomputed: {recomputed[:10]}...)",
                    "events_checked": events_checked
                }

            # 2. Check previous_hash chaining link
            if i > 0:
                prev_event = chain[i - 1]
                if event.previous_hash != prev_event.event_hash:
                    return {
                        "valid": False,
                        "broken_at": event.event_id,
                        "index": i,
                        "reason": f"Previous hash link broken at event '{event.event_id}' (expected: {prev_event.event_hash[:10]}..., actual: {event.previous_hash[:10]}...)",
                        "events_checked": events_checked
                    }

        return {"valid": True, "events_checked": events_checked}

    def simulate_tamper(self, event_id: str, new_decision: str = "TAMPERED_ALLOW") -> bool:
        """Development helper to simulate database record tampering for demonstration."""
        chain = repository.get_audit_chain()
        for evt in chain:
            if evt.event_id == event_id:
                # Mutate payload field without updating stored event_hash digest
                evt.decision = new_decision
                return True
        return False

audit_verifier = AuditVerifier()
