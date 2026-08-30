from fastapi import APIRouter
from backend.app.config import settings
from backend.app.risk.graph import fraud_graph
from backend.app.storage.repository import repository

router = APIRouter(prefix="/api", tags=["system"])


@router.get("/health", summary="Health and execution mode")
def health_check():
    testnet = bool(settings.ENABLE_TESTNET_EXECUTION)
    return {
        "status": "healthy",
        "project": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
        "system_status": "PROTECTED",
        "execution_mode": "SEPOLIA TESTNET" if testnet else "DEMO SAFE / MOCK",
        "testnet_execution_enabled": testnet,
        "mcp_boundary": "yes",
        "mcp_transport": "stdio available; demo uses in-process sandbox",
        "trueforge": "skill + MCP server packaged; demo agent is in-process sandbox without LLM keys",
    }


@router.get("/config", summary="Public policy configuration (no secrets)")
def get_config():
    return {
        "max_single_transfer": settings.MAX_SINGLE_TRANSFER,
        "daily_velocity_limit": settings.DAILY_VELOCITY_LIMIT,
        "new_counterparty_threshold": settings.NEW_COUNTERPARTY_THRESHOLD,
        "duplicate_window_minutes": settings.DUPLICATE_WINDOW_MINUTES,
        "high_risk_threshold": settings.HIGH_RISK_THRESHOLD,
        "enable_testnet_execution": settings.ENABLE_TESTNET_EXECUTION,
        "execution_mode": "SEPOLIA" if settings.ENABLE_TESTNET_EXECUTION else "MOCK",
    }


@router.get("/graph", summary="FraudGraph export")
def get_fraud_graph():
    return fraud_graph.get_graph_export()


@router.get("/metrics", summary="Authorization outcome counters")
def get_metrics():
    decisions = list(repository.decisions.values())
    allowed = sum(1 for d in decisions if d.decision == "ALLOW")
    review = sum(1 for d in decisions if d.decision == "REVIEW")
    blocked = sum(1 for d in decisions if d.decision == "BLOCK")
    high_risk = sum(1 for d in decisions if d.risk_score >= settings.HIGH_RISK_THRESHOLD)
    executed = len(repository.list_transactions())
    return {
        "allowed": allowed,
        "review": review,
        "blocked": blocked,
        "high_risk": high_risk,
        "total_evaluated": len(decisions),
        "executed": executed,
        "system_status": "PROTECTED",
    }
