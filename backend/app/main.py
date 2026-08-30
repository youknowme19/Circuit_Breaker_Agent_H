import logging
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from sse_starlette.sse import EventSourceResponse
import asyncio
import json

from backend.app.config import settings
from backend.app.api import actions, approvals, audit, health, console
from backend.app.storage.repository import repository

logging.basicConfig(level=getattr(logging, str(settings.LOG_LEVEL).upper(), logging.INFO))
logger = logging.getLogger("circuit_breaker")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        "Deterministic authorization layer between AI agents and financial execution. "
        "The agent proposes. Circuit Breaker authorizes. Only the execution gate can move money. "
        "MCP execute_payment requires a valid authorization token."
    ),
    version="1.1.0",
    contact={"name": "Circuit Breaker"},
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(actions.router)
app.include_router(approvals.router)
app.include_router(audit.router)
app.include_router(health.router)
app.include_router(console.router)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    if isinstance(exc, StarletteHTTPException):
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
    if isinstance(exc, RequestValidationError):
        return JSONResponse(status_code=422, content={"detail": exc.errors()})
    logger.exception("Unhandled error on %s", request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal error — fail closed"})


@app.get("/api/stream", summary="SSE decision telemetry")
async def event_stream(request: Request):
    async def event_generator():
        last_count = 0
        while True:
            if await request.is_disconnected():
                break

            current_decisions = list(repository.decisions.values())
            if len(current_decisions) > last_count:
                for dec in current_decisions[last_count:]:
                    act = repository.get_action(dec.action_id)
                    txs = repository.list_transactions()
                    matching_tx = next((t for t in txs if t.action_id == dec.action_id), None)
                    payload = {
                        "event_type": "decision_evaluated",
                        "action": act.model_dump() if act else None,
                        "decision": dec.model_dump(),
                        "transaction": matching_tx.model_dump() if matching_tx else None,
                    }
                    yield {"event": "message", "data": json.dumps(payload)}
                last_count = len(current_decisions)

            await asyncio.sleep(1.0)

    return EventSourceResponse(event_generator())
