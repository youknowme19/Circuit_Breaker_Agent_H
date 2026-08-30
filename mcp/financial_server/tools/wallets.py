from typing import Any, Dict, Optional, List
from backend.app.config import settings
from backend.app.execution.base import get_payment_adapter

def get_wallet_balance_tool(address: Optional[str] = None) -> Dict[str, Any]:
    """Retrieve native testnet wallet balance for configured address."""
    adapter = get_payment_adapter()
    return adapter.get_wallet_balance(address)

def get_wallet_address_tool() -> Dict[str, Any]:
    """Retrieve public testnet sender wallet address. Private keys are NEVER returned."""
    adapter = get_payment_adapter()
    balance_info = adapter.get_wallet_balance()
    return {
        "configured_address": balance_info.get("address"),
        "network": balance_info.get("network"),
        "asset": balance_info.get("asset"),
        "private_key_exposed": False
    }

def get_supported_networks_tool() -> Dict[str, Any]:
    """List financial networks supported by Circuit Breaker."""
    active_network = settings.TESTNET_NETWORK_NAME if settings.ENABLE_TESTNET_EXECUTION else "Safe Mock Network"
    return {
        "active_mode": "REAL TESTNET" if settings.ENABLE_TESTNET_EXECUTION else "DEMO SAFE MOCK",
        "configured_network": active_network,
        "supported_networks": [
            {
                "id": "monad-testnet",
                "name": "Monad Testnet",
                "chain_id": 10143,
                "asset": "MON",
                "explorer": "https://testnet.monadexplorer.com",
                "active": settings.ENABLE_TESTNET_EXECUTION and settings.TESTNET_CHAIN_ID == 10143
            },
            {
                "id": "ethereum-sepolia",
                "name": "Ethereum Sepolia Testnet",
                "chain_id": 11155111,
                "asset": "ETH",
                "explorer": "https://sepolia.etherscan.io",
                "active": settings.ENABLE_TESTNET_EXECUTION and settings.TESTNET_CHAIN_ID == 11155111
            },
            {
                "id": "safe-mock",
                "name": "Safe Mock Network",
                "chain_id": 0,
                "asset": "USD",
                "explorer": None,
                "active": not settings.ENABLE_TESTNET_EXECUTION
            }
        ]
    }

def estimate_transfer_tool(destination_account: str, amount: float, asset: str = "MON") -> Dict[str, Any]:
    """Estimate gas fee and total cost for a testnet transfer."""
    if amount <= 0:
        return {"success": False, "error": "Amount must be greater than zero"}
    
    estimated_gas_limit = 21000
    estimated_gas_price_gwei = 1.5
    estimated_fee_asset = (estimated_gas_limit * estimated_gas_price_gwei) / 1e9
    
    return {
        "destination_account": destination_account,
        "amount": amount,
        "asset": asset,
        "estimated_gas_limit": estimated_gas_limit,
        "estimated_gas_price_gwei": estimated_gas_price_gwei,
        "estimated_fee": estimated_fee_asset,
        "total_cost": amount + estimated_fee_asset
    }

def prepare_transfer_tool(network: str, from_address: str, to_address: str, amount: float, asset: str = "MON", reason: str = "") -> Dict[str, Any]:
    """Prepare a structured transfer payload ready for Circuit Breaker submission."""
    import uuid
    action_id = f"ACT-{uuid.uuid4().hex[:8]}"
    return {
        "action_id": action_id,
        "network": network,
        "source_account": from_address,
        "destination_account": to_address,
        "counterparty_id": to_address,
        "amount": amount,
        "currency": asset,
        "reason": reason,
        "prepared": True
    }
