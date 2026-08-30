from abc import ABC, abstractmethod
from typing import Tuple, Optional, Dict, Any

class PaymentAdapter(ABC):
    @abstractmethod
    def execute_transfer(self, action_id: str, source: str, destination: str, amount: float, currency: str = "USD") -> Tuple[bool, str, str, str, Optional[int], Optional[str]]:
        """Returns (success_boolean, tx_hash_or_error, execution_mode, chain_network, block_number, explorer_url)."""
        pass

    def get_wallet_balance(self, address: Optional[str] = None) -> Dict[str, Any]:
        """Query native token balance. Returns dict with address, balance, asset, network."""
        return {"address": address or "0x0000000000000000000000000000000000000000", "balance": 0.0, "asset": "MOCK", "network": "Safe Mock"}

def get_payment_adapter() -> PaymentAdapter:
    from backend.app.config import settings
    if settings.ENABLE_TESTNET_EXECUTION and settings.TESTNET_RPC_URL and settings.TESTNET_PRIVATE_KEY:
        if settings.TESTNET_CHAIN_ID == 10143 or "monad" in settings.TESTNET_NETWORK_NAME.lower():
            from backend.app.execution.monad_testnet_adapter import MonadTestnetAdapter
            return MonadTestnetAdapter()
        else:
            from backend.app.execution.evm_testnet_adapter import EVMTestnetAdapter
            return EVMTestnetAdapter()
    else:
        from backend.app.execution.mock_adapter import MockPaymentAdapter
        return MockPaymentAdapter()
