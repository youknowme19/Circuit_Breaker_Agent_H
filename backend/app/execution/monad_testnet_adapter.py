import logging
from typing import Dict, Any, Tuple, Optional
from backend.app.config import settings
from backend.app.execution.evm_testnet_adapter import EVMTestnetAdapter

logger = logging.getLogger(__name__)


class MonadTestnetAdapter(EVMTestnetAdapter):
    """Monad Testnet Adapter (EVM-compatible layer-1 testnet).

    Chain ID: 10143
    Native Asset: MON
    Explorer: https://testnet.monadexplorer.com
    """

    def get_wallet_balance(self, address: Optional[str] = None) -> Dict[str, Any]:
        res = super().get_wallet_balance(address)
        res["asset"] = "MON"
        res["network"] = "Monad Testnet"
        return res

    def execute_transfer(
        self, action_id: str, source: str, destination: str, amount: float, currency: str = "MON"
    ) -> Tuple[bool, str, str, str, Optional[int], Optional[str]]:
        
        # Override network default if not specified
        original_network = settings.TESTNET_NETWORK_NAME
        try:
            if not settings.TESTNET_NETWORK_NAME or settings.TESTNET_NETWORK_NAME == "Monad Testnet":
                settings.TESTNET_NETWORK_NAME = "Monad Testnet"
            
            success, tx_hash, mode, network, block_num, explorer_url = super().execute_transfer(
                action_id, source, destination, amount, currency
            )
            
            if success and tx_hash and tx_hash.startswith("0x"):
                if not explorer_url or "etherscan" in explorer_url:
                    explorer_url = f"https://testnet.monadexplorer.com/tx/{tx_hash}"

            return success, tx_hash, mode, "Monad Testnet", block_num, explorer_url
        finally:
            settings.TESTNET_NETWORK_NAME = original_network
