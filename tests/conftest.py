import pytest
from backend.app.storage.repository import repository
from backend.app.risk.graph import fraud_graph
from backend.app.execution.mock_adapter import MockPaymentAdapter


from backend.app.config import settings


@pytest.fixture(autouse=True)
def reset_state():
    repository.reset()
    fraud_graph.reset()
    MockPaymentAdapter.force_failure = False
    MockPaymentAdapter.force_exception = False
    settings.ENABLE_TESTNET_EXECUTION = False
    yield

