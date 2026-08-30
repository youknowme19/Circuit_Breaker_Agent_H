from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from backend.app.config import settings
from backend.app.demo.scenarios import run_attack, run_full_demo
from backend.app.observability import timeline
from backend.app.storage.repository import repository

router = APIRouter(prefix="/api", tags=["console"])


@router.get("/transactions", summary="List executed ledger transactions")
def list_transactions():
    return repository.list_transactions()


@router.get("/timeline", summary="Security event timeline")
def get_timeline():
    return timeline.list_events()


@router.get("/invoices", summary="List invoices (untrusted content)")
def list_invoices():
    return repository.list_invoices()


class DemoRunRequest(BaseModel):
    reset: bool = True


@router.post(
    "/demo/run",
    summary="Run the canonical security demo",
    description="Executes real policy, token, execution-gate, concurrency, and audit checks. Mock mode only.",
)
def demo_run(req: DemoRunRequest = DemoRunRequest()):
    if settings.ENABLE_TESTNET_EXECUTION:
        raise HTTPException(status_code=403, detail="Demo runner refuses to operate while ENABLE_TESTNET_EXECUTION=true")
    return run_full_demo(reset=req.reset)


@router.post("/demo/run-scenarios", summary="Run detailed security scenario suite for frontend demo page")
def demo_run_scenarios():
    data = run_full_demo(reset=True)
    scenarios = []
    for sc in data.get("scenes", []):
        scenarios.append({
            "name": sc.get("scene") or sc.get("attack", "Scenario"),
            "result": "PASS" if sc.get("passed") else "FAIL",
            "description": sc.get("expected") or sc.get("detail", ""),
            "explorer_url": sc.get("result", {}).get("explorer_url") if isinstance(sc.get("result"), dict) else None
        })
    return {
        "status": "PASS" if data.get("passed") else "FAIL",
        "scenarios": scenarios
    }



class AttackRunRequest(BaseModel):
    attack_id: str = Field(..., description="Attack identifier")


@router.post("/attacks/run", summary="Run one Attack Lab scenario against the live engine")
def attacks_run(req: AttackRunRequest):
    try:
        return run_attack(req.attack_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/attacks", summary="List Attack Lab scenarios")
def list_attacks():
    return [
        {"id": "prompt_injection", "name": "Prompt Injection", "expected": "BLOCK"},
        {"id": "missing_token", "name": "Missing Token", "expected": "HTTP 400"},
        {"id": "forged_token", "name": "Forged Token", "expected": "SIGNATURE MISMATCH"},
        {"id": "payload_mutation", "name": "Payload Mutation", "expected": "HASH MISMATCH"},
        {"id": "replay", "name": "Replay", "expected": "ALREADY EXECUTED"},
        {"id": "review_without_approval", "name": "REVIEW Without Approval", "expected": "HUMAN APPROVAL REQUIRED"},
        {"id": "concurrent_double_spend", "name": "Concurrent Double Spend", "expected": "1 / 19"},
        {"id": "adapter_failure", "name": "Adapter Failure", "expected": "FAIL CLOSED"},
        {"id": "safe_payment", "name": "Safe Payment", "expected": "ALLOW"},
        {"id": "review_payment", "name": "Risky Payment", "expected": "REVIEW"},
        {"id": "fraudgraph", "name": "FraudGraph", "expected": "REVIEW/BLOCK"},
        {"id": "audit_tamper", "name": "Audit Tampering", "expected": "CHAIN INVALID"},
    ]
