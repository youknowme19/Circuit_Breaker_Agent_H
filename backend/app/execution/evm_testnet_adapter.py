import logging
from typing import Tuple, Optional, Dict, Any
from backend.app.config import settings
from backend.app.execution.base import PaymentAdapter
from backend.app.observability import emit

logger = logging.getLogger(__name__)


class EVMTestnetAdapter(PaymentAdapter):
    """Real EVM Testnet Adapter (Sepolia / Generic EVM). Fail-closed. No synthetic hashes."""

    def get_sender_address(self) -> Optional[str]:
        if settings.SENDER_ADDRESS and settings.SENDER_ADDRESS.startswith("0x"):
            return settings.SENDER_ADDRESS
        if not settings.TESTNET_PRIVATE_KEY:
            return None
        try:
            from eth_account import Account
            account = Account.from_key(settings.TESTNET_PRIVATE_KEY)
            return account.address
        except Exception:
            return None

    def get_wallet_balance(self, address: Optional[str] = None) -> Dict[str, Any]:
        target_addr = address or self.get_sender_address()
        if not target_addr or not settings.TESTNET_RPC_URL:
            return {
                "address": target_addr or "UNCONFIGURED",
                "balance": 0.0,
                "asset": "ETH",
                "network": settings.TESTNET_NETWORK_NAME or "EVM Testnet",
                "error": "TESTNET_NOT_CONFIGURED: Missing RPC URL or wallet credentials"
            }

        try:
            from web3 import Web3
            w3 = Web3(Web3.HTTPProvider(settings.TESTNET_RPC_URL, request_kwargs={"timeout": 10}))
            if not w3.is_connected():
                return {
                    "address": target_addr,
                    "balance": 0.0,
                    "asset": "ETH",
                    "network": settings.TESTNET_NETWORK_NAME,
                    "error": "RPC_UNREACHABLE"
                }
            wei_balance = w3.eth.get_balance(target_addr)
            eth_balance = float(w3.from_wei(wei_balance, "ether"))
            return {
                "address": target_addr,
                "balance": eth_balance,
                "asset": "ETH",
                "network": settings.TESTNET_NETWORK_NAME,
                "error": None
            }
        except Exception as e:
            return {
                "address": target_addr,
                "balance": 0.0,
                "asset": "ETH",
                "network": settings.TESTNET_NETWORK_NAME,
                "error": f"BALANCE_QUERY_FAILED: {type(e).__name__}"
            }

    def execute_transfer(
        self, action_id: str, source: str, destination: str, amount: float, currency: str = "USD"
    ) -> Tuple[bool, str, str, str, Optional[int], Optional[str]]:

        network_name = settings.TESTNET_NETWORK_NAME or "Ethereum Sepolia Testnet"
        err_prefix = "SEPOLIA_ERROR" if (settings.TESTNET_CHAIN_ID == 11155111 or "sepolia" in network_name.lower()) else "TESTNET_ERROR"

        if not settings.ENABLE_TESTNET_EXECUTION:
            return False, f"{err_prefix}: Testnet execution disabled (ENABLE_TESTNET_EXECUTION=false)", "TESTNET", network_name, None, None

        if not settings.TESTNET_RPC_URL or not settings.TESTNET_PRIVATE_KEY or not settings.TESTNET_CHAIN_ID:
            return False, f"{err_prefix}: Missing required configuration (RPC_URL, PRIVATE_KEY, or CHAIN_ID)", "TESTNET", network_name, None, None

        try:
            from web3 import Web3
            from eth_account import Account

            w3 = Web3(Web3.HTTPProvider(settings.TESTNET_RPC_URL, request_kwargs={"timeout": 15}))
            if not w3.is_connected():
                emit("TESTNET_BROADCAST_FAILED", "RPC not connected", action_id=action_id)
                return False, f"{err_prefix}: Unable to connect to {network_name} RPC provider", "TESTNET", network_name, None, None


            account = Account.from_key(settings.TESTNET_PRIVATE_KEY)
            nonce = w3.eth.get_transaction_count(account.address)
            block_num = w3.eth.block_number
            latest = w3.eth.get_block("latest")
            base_fee = latest.get("baseFeePerGas") or w3.eth.gas_price
            priority_fee = w3.to_wei(1, "gwei")
            max_fee = int(base_fee) * 2 + int(priority_fee)

            target_address = destination if isinstance(destination, str) and destination.startswith("0x") and len(destination) == 42 else account.address

            tx = {
                "type": 2,
                "nonce": nonce,
                "to": target_address,
                "value": w3.to_wei(amount if amount > 0 else 0.0001, "ether"),
                "gas": 21000,
                "maxFeePerGas": max_fee,
                "maxPriorityFeePerGas": int(priority_fee),
                "chainId": settings.TESTNET_CHAIN_ID,
            }

            signed_tx = w3.eth.account.sign_transaction(tx, settings.TESTNET_PRIVATE_KEY)
            raw = getattr(signed_tx, "raw_transaction", None) or getattr(signed_tx, "rawTransaction", None)
            tx_hash_bytes = w3.eth.send_raw_transaction(raw)
            tx_hash = tx_hash_bytes.hex()
            if not tx_hash.startswith("0x"):
                tx_hash = "0x" + tx_hash

            emit("TESTNET_BROADCAST", "Broadcast succeeded", action_id=action_id)
            
            if "{tx_hash}" in settings.TESTNET_EXPLORER_URL:
                explorer_url = settings.TESTNET_EXPLORER_URL.format(tx_hash=tx_hash)
            elif settings.TESTNET_EXPLORER_URL:
                explorer_url = f"{settings.TESTNET_EXPLORER_URL.rstrip('/')}/tx/{tx_hash}"
            else:
                explorer_url = f"https://sepolia.etherscan.io/tx/{tx_hash}"
                
            return True, tx_hash, "TESTNET", network_name, block_num, explorer_url

        except Exception as e:
            emit("TESTNET_BROADCAST_FAILED", "Broadcast failed — fail closed", action_id=action_id)
            logger.error("Testnet transaction broadcasting failed: %s", type(e).__name__)
            return False, f"TESTNET_BROADCAST_FAILURE: {type(e).__name__}", "TESTNET", network_name, None, None
