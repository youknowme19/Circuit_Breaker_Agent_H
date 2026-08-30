import hashlib
from typing import Tuple, Optional
from backend.app.execution.base import PaymentAdapter


class MockPaymentAdapter(PaymentAdapter):
    """Deterministic Mock Payment Adapter for Demo-Safe Mode.

    Mock transaction IDs are prefixed with `mock-tx-` and never receive an explorer URL.
    """

    force_failure: bool = False
    force_exception: bool = False

    def execute_transfer(
        self, action_id: str, source: str, destination: str, amount: float, currency: str = "USD"
    ) -> Tuple[bool, str, str, str, Optional[int], Optional[str]]:
        if MockPaymentAdapter.force_exception:
            raise RuntimeError("ADAPTER_EXCEPTION_SIMULATED")
        if MockPaymentAdapter.force_failure:
            return False, "ADAPTER_FAILURE_SIMULATED", "MOCK", "Mock Execution Ledger (Demo-Safe)", None, None

        raw_seed = f"MOCK_TX:{action_id}:{source}:{destination}:{amount}:{currency}"
        hash_digest = hashlib.sha256(raw_seed.encode("utf-8")).hexdigest()
        tx_hash = f"mock-tx-{hash_digest[:32]}"
        chain_network = "Mock Execution Ledger (Demo-Safe)"
        block_number = 5891024
        explorer_url = None
        return True, tx_hash, "MOCK", chain_network, block_number, explorer_url
