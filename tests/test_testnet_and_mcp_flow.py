import pytest
from backend.app.config import settings
from backend.app.execution.base import get_payment_adapter
from backend.app.execution.evm_testnet_adapter import EVMTestnetAdapter
from backend.app.execution.monad_testnet_adapter import MonadTestnetAdapter
from mcp.financial_server.tools.wallets import (
    get_wallet_balance_tool,
    get_wallet_address_tool,
    get_supported_networks_tool,
    estimate_transfer_tool,
    prepare_transfer_tool
)
from mcp.financial_server.server import get_wallet_address, get_supported_networks, request_transfer

def test_55_evm_adapter_fails_closed_when_disabled():
    settings.ENABLE_TESTNET_EXECUTION = False
    adapter = EVMTestnetAdapter()
    success, msg, mode, network, block_num, explorer = adapter.execute_transfer(
        "ACT-TEST-01", "0x111", "0x222", 0.1
    )
    assert not success
    assert "disabled" in msg.lower()

def test_56_monad_adapter_balance_returns_mon_asset():
    adapter = MonadTestnetAdapter()
    res = adapter.get_wallet_balance("0x1234567890123456789012345678901234567890")
    assert res["asset"] == "MON"
    assert res["network"] == "Monad Testnet"

def test_57_private_key_never_exposed_in_wallet_address_tool():
    res = get_wallet_address_tool()
    assert res.get("private_key_exposed") is False
    assert "private_key" not in res
    assert "secret" not in res

def test_58_supported_networks_tool_lists_monad_and_sepolia():
    res = get_supported_networks_tool()
    networks = res.get("supported_networks", [])
    net_ids = [n["id"] for n in networks]
    assert "monad-testnet" in net_ids
    assert "ethereum-sepolia" in net_ids

def test_59_estimate_transfer_tool_calculates_gas_cost():
    res = estimate_transfer_tool("0x1234567890123456789012345678901234567890", 0.5, "MON")
    assert res["destination_account"] == "0x1234567890123456789012345678901234567890"
    assert res["amount"] == 0.5
    assert res["total_cost"] > 0.5

def test_60_request_transfer_mcp_evaluates_via_circuit_breaker():
    res = request_transfer("monad-testnet", "ACC-001", "ACC-002", 100.0, "MON", "MCP transfer test")
    assert "decision" in res
    dec_val = str(res["decision"])
    assert any(d in dec_val for d in ["ALLOW", "REVIEW", "BLOCK"])


def test_61_trueforge_mcp_real_payment_flow():
    import uuid
    from backend.app.storage.repository import repository
    from backend.app.models.authorization import AuthorizationToken
    from mcp.financial_server.tools.payments import propose_payment_tool, execute_payment_tool

    act_id = f"ACT-TF-E2E-{uuid.uuid4().hex[:6]}"
    payload = {
        "action_id": act_id,
        "agent_id": "trueforge-financial-operator",
        "source_account": "ACC-001",
        "destination_account": "ACC-002",
        "counterparty_id": "VENDOR-001",
        "amount": 0.1,
        "currency": "MON",
        "reason": "E2E integration test transfer"
    }

    # 1. Propose payment via MCP
    prop = propose_payment_tool(payload)
    assert str(prop["decision"]) in ["ALLOW", "DecisionType.ALLOW"]

    # 2. Issue HMAC authorization token
    action = repository.get_action(act_id)
    tok = AuthorizationToken.create(
        token_id=f"TOKEN-E2E-{uuid.uuid4().hex[:6]}",
        action_id=act_id,
        action_hash=action.compute_hash(),
        decision="ALLOW",
        secret_key=settings.SECRET_KEY
    )
    repository.save_token(tok)

    # 3. Execute payment via MCP
    res_exec = execute_payment_tool(act_id, tok.token_id)
    assert res_exec["success"] is True
    assert "transaction" in res_exec

def test_62_mock_mode_never_returns_synthetic_blockchain_hash():
    from backend.app.execution.mock_adapter import MockPaymentAdapter
    settings.ENABLE_TESTNET_EXECUTION = False
    adapter = MockPaymentAdapter()
    success, mock_id, mode, network, block_num, explorer = adapter.execute_transfer("ACT-MOCK-REG-01", "ACC-001", "ACC-002", 0.1)
    assert success is True
    assert mode == "MOCK"
    assert explorer is None
    assert mock_id.startswith("mock-tx-")




