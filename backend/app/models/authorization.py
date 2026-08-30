import hashlib
import hmac
import json
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel, Field

class AuthorizationToken(BaseModel):
    token_id: str = Field(..., description="Unique token ID e.g. AUTH-9012")
    action_id: str = Field(..., description="Associated action ID")
    action_hash: str = Field(..., description="SHA-256 digest of canonical action")
    decision: str = Field(..., description="Decision state: ALLOW or APPROVED")
    issued_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    expires_at: str = Field(...)
    human_approval_id: Optional[str] = Field(default=None, description="Linked human approval record ID if applicable")
    signature: str = Field(..., description="Cryptographic signature of token data")

    @classmethod
    def create(
        cls,
        token_id: str,
        action_id: str,
        action_hash: str,
        decision: str,
        secret_key: str,
        ttl_minutes: int = 15,
        human_approval_id: Optional[str] = None
    ) -> "AuthorizationToken":
        if not secret_key or not secret_key.strip():
            raise ValueError("SECRET_KEY is required to create an authorization token")

        now = datetime.utcnow()
        expires = now + timedelta(minutes=ttl_minutes)
        issued_at_str = now.isoformat() + "Z"
        expires_at_str = expires.isoformat() + "Z"

        payload = f"{token_id}:{action_id}:{action_hash}:{decision}:{issued_at_str}:{expires_at_str}:{human_approval_id or ''}"
        sig = hmac.new(secret_key.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()

        return cls(
            token_id=token_id,
            action_id=action_id,
            action_hash=action_hash,
            decision=decision,
            issued_at=issued_at_str,
            expires_at=expires_at_str,
            human_approval_id=human_approval_id,
            signature=sig
        )

    def verify_signature(self, secret_key: str) -> bool:
        if not secret_key or not secret_key.strip():
            return False
        payload = f"{self.token_id}:{self.action_id}:{self.action_hash}:{self.decision}:{self.issued_at}:{self.expires_at}:{self.human_approval_id or ''}"
        expected = hmac.new(secret_key.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()
        return hmac.compare_digest(self.signature, expected)

    def is_expired(self) -> bool:
        try:
            expires_dt = datetime.fromisoformat(self.expires_at.replace("Z", "+00:00"))
            now_dt = datetime.now(expires_dt.tzinfo)
            return now_dt > expires_dt
        except Exception:
            return True
