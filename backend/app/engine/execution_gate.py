from typing import Tuple, Optional
from datetime import datetime
from backend.app.config import settings
from backend.app.storage.repository import repository
from backend.app.models.transaction import TransactionRecord
from backend.app.execution.base import get_payment_adapter
from backend.app.risk.graph import fraud_graph
from backend.app.observability import emit

class ExecutionGate:
    """Fail-closed, thread-safe execution boundary. Money movement MUST pass through this gate."""

    def execute_authorized_action(self, action_id: str, token_id: Optional[str]) -> Tuple[bool, str, Optional[TransactionRecord]]:
        # 1. Action lookup
        action = repository.get_action(action_id)
        if not action:
            return False, "EXECUTION_REFUSED: Target financial action not found", None

        # 2. Token presence check
        if not token_id or not token_id.strip():
            emit("TOKEN_REJECTED", "Missing authorization token", action_id=action_id)
            return False, "EXECUTION_REFUSED: Missing authorization token", None

        token = repository.get_token(action_id)
        if not token or token.token_id != token_id.strip():
            return False, "EXECUTION_REFUSED: Invalid or unissued authorization token", None

        # 3. Explicit Token-Action Cross Binding Check
        if token.action_id != action_id:
            return False, "EXECUTION_REFUSED: Authorization token is bound to a different action ID", None

        # 4. Cryptographic Signature verification
        if not token.verify_signature(settings.SECRET_KEY):
            emit("TOKEN_REJECTED", "Signature mismatch", action_id=action_id)
            return False, "EXECUTION_REFUSED: Authorization token signature verification failed", None

        # 5. TTL Expiry check
        if token.is_expired():
            return False, "EXECUTION_REFUSED: Authorization token TTL has expired", None

        # 6. Action Hash Mismatch Check (Detects payload mutation post-authorization)
        current_action_hash = action.compute_hash()
        if current_action_hash != token.action_hash:
            emit("HASH_MISMATCH", "Action payload mutated post-authorization", action_id=action_id)
            return False, "EXECUTION_REFUSED: Action payload mutated post-authorization (Hash Mismatch)", None

        # 7. Decision State Check
        decision = repository.get_decision(action_id)
        if not decision:
            return False, "EXECUTION_REFUSED: No authorization decision record found", None

        if decision.decision == "BLOCK":
            return False, "EXECUTION_REFUSED: Action was BLOCKED by policy engine", None

        if decision.decision == "REVIEW":
            approval = repository.get_human_approval(action_id)
            if not approval or not approval.get("approved", False):
                return False, "EXECUTION_REFUSED: Action marked for REVIEW has not received human approval", None

        if decision.decision not in ("ALLOW", "REVIEW"):
            return False, "EXECUTION_REFUSED: Unknown decision state — fail closed", None

        # 8. ATOMIC RESERVATION & REPLAY/CONCURRENCY VELOCITY CHECK
        reserved_ok, reserve_msg = repository.reserve_action_execution(
            action_id=action.action_id,
            token_id=token.token_id,
            amount=action.amount,
            daily_limit=settings.DAILY_VELOCITY_LIMIT
        )
        if not reserved_ok:
            if "already been executed" in reserve_msg or "consumed" in reserve_msg.lower():
                emit("REPLAY_REJECTED", reserve_msg, action_id=action_id)
            return False, reserve_msg, None

        emit("EXECUTION_RESERVED", f"Reserved {action_id}", action_id=action_id, token_id=token.token_id)
        emit("EXECUTION_STARTED", f"Adapter execution started for {action_id}", action_id=action_id)

        # 9. Execute via configured Payment Adapter (Mock or EVM Testnet)
        try:
            adapter = get_payment_adapter()
            success, tx_hash, mode, chain_network, block_num, explorer_url = adapter.execute_transfer(
                action_id=action.action_id,
                source=action.source_account,
                destination=action.destination_account,
                amount=action.amount,
                currency=action.currency
            )
        except Exception as e:
            repository.release_action_reservation(action.action_id, token.token_id)
            emit("EXECUTION_FAILED", "Adapter exception — fail closed", action_id=action_id)
            return False, f"EXECUTION_REFUSED: Payment adapter unhandled exception ({str(e)})", None

        if not success:
            repository.release_action_reservation(action.action_id, token.token_id)
            emit("EXECUTION_FAILED", "Adapter failure — fail closed", action_id=action_id)
            return False, f"EXECUTION_REFUSED: Payment adapter failure ({tx_hash})", None

        # 10. Dynamic FraudGraph State Update (only after confirmed execution)
        fraud_graph.add_transaction_edge(action.source_account, action.destination_account, action.amount)

        # 11. Record executed transaction & Mark Token Consumed
        tx_record = TransactionRecord(
            transaction_id=f"TX-{len(repository.transactions) + 1:04d}",
            action_id=action.action_id,
            source_account=action.source_account,
            destination_account=action.destination_account,
            counterparty_id=action.counterparty_id,
            amount=action.amount,
            currency=action.currency,
            invoice_id=action.invoice_id,
            reference=action.reference,
            timestamp=datetime.utcnow().isoformat() + "Z",
            status="EXECUTED",
            blockchain_tx_hash=tx_hash,
            execution_mode=mode,
            chain_network=chain_network,
            block_number=block_num,
            explorer_url=explorer_url
        )
        repository.mark_action_executed(action.action_id, token.token_id, tx_record)
        emit("EXECUTION_SUCCEEDED", f"Executed {action_id}", action_id=action_id, execution_mode=mode)

        # 12. Append Audit Event for execution
        event_id = f"EVT-{len(repository.audit_chain):04d}"
        repository.append_audit_event(
            event_id=event_id,
            action_id=action.action_id,
            decision="EXECUTED",
            risk_score=decision.risk_score,
            violations=[f"TX_HASH:{tx_hash}"]
        )

        return True, "EXECUTION_SUCCESSFUL", tx_record

execution_gate = ExecutionGate()
