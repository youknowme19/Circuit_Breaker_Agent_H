import logging
import threading
from collections import deque
from datetime import datetime
from typing import Any, Deque, Dict, List, Optional

_REDACT_KEYS = {
    "secret_key",
    "private_key",
    "testnet_private_key",
    "authorization_signature",
    "signature",
    "password",
    "api_key",
    "trueforge_api_key",
}

logger = logging.getLogger("circuit_breaker")


class SecurityTimeline:
    """In-memory, thread-safe security event timeline. Never stores secrets."""

    def __init__(self, maxlen: int = 500):
        self._lock = threading.Lock()
        self._events: Deque[Dict[str, Any]] = deque(maxlen=maxlen)

    def emit(self, event_type: str, message: str, **fields: Any) -> Dict[str, Any]:
        safe = {k: v for k, v in fields.items() if k.lower() not in _REDACT_KEYS}
        record = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "event_type": event_type,
            "message": message,
            **safe,
        }
        with self._lock:
            self._events.append(record)
        logger.info("%s %s", event_type, message)
        return record

    def list_events(self) -> List[Dict[str, Any]]:
        with self._lock:
            return list(self._events)

    def reset(self) -> None:
        with self._lock:
            self._events.clear()


timeline = SecurityTimeline()


def emit(event_type: str, message: str, **fields: Any) -> Dict[str, Any]:
    return timeline.emit(event_type, message, **fields)


def redact_token(token: Optional[Any]) -> Optional[Dict[str, Any]]:
    if token is None:
        return None
    data = token.model_dump() if hasattr(token, "model_dump") else dict(token)
    if "signature" in data and data["signature"]:
        data["signature"] = "[redacted]"
    return data


def emit_agent_trace(stage: str, agent_id: str, action_id: str, detail: str) -> Dict[str, Any]:
    """Emit a redacted TrueForge agent execution trace event."""
    return emit(
        event_type="TRUEFORGE_AGENT_TRACE",
        message=f"[{stage}] Agent {agent_id} -> Action {action_id}: {detail}",
        stage=stage,
        agent_id=agent_id,
        action_id=action_id,
    )

