from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.storage.repository import repository
from backend.app.risk.graph import fraud_graph
from backend.app.execution.mock_adapter import MockPaymentAdapter


from backend.app.config import settings

def setup_function():
    repository.reset()
    fraud_graph.reset()
    MockPaymentAdapter.force_failure = False
    settings.ENABLE_TESTNET_EXECUTION = False



client = TestClient(app)


def test_health_reports_mock_mode():
    res = client.get("/api/health")
    assert res.status_code == 200
    body = res.json()
    assert body["system_status"] == "PROTECTED"
    assert "MOCK" in body["execution_mode"]


def test_config_has_no_secrets():
    res = client.get("/api/config")
    assert res.status_code == 200
    text = res.text.lower()
    assert "private_key" not in text
    assert "secret_key" not in text


def test_execute_empty_body_is_400():
    res = client.post("/api/actions/ACT-X/execute", json={})
    assert res.status_code == 400


def test_audit_verify_and_timeline():
    assert client.get("/api/audit").status_code == 200
    v = client.post("/api/audit/verify")
    assert v.status_code == 200
    assert v.json()["valid"] is True
    assert client.get("/api/timeline").status_code == 200
    assert client.get("/api/graph").status_code == 200
    assert client.get("/api/metrics").status_code == 200


def test_demo_run_api_passes():
    res = client.post("/api/demo/run", json={"reset": True})
    assert res.status_code == 200
    assert res.json()["passed"] is True


def test_attack_lab_prompt_injection():
    res = client.post("/api/attacks/run", json={"attack_id": "prompt_injection"})
    assert res.status_code == 200
    assert res.json()["passed"] is True
