"""FastAPI application for the SMART-MINE prototype command centre."""

import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from apps.api.logging_config import configure_logging
from apps.api.rate_limit import SlidingWindowRateLimiter
from apps.api.realtime import EventHub
from apps.api.routes import router
from apps.api.storage import Database

configure_logging()

_DEFAULT_DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "smart_mine.db"


def _resolve_data_path() -> Path:
    # .env.example documents SMART_MINE_DATABASE_URL as sqlite:///<path> but nothing
    # previously read it -- wiring it up here also lets tests point at an isolated
    # database instead of the real prototype's data/smart_mine.db. Read at lifespan
    # startup time (not module-import time) so it can vary across TestClient runs.
    database_url = os.getenv("SMART_MINE_DATABASE_URL")
    return Path(database_url.removeprefix("sqlite:///")) if database_url else _DEFAULT_DATA_PATH


@asynccontextmanager
async def lifespan(application: FastAPI):
    application.state.database = Database(_resolve_data_path())
    application.state.database.initialize()
    application.state.sessions = {}
    application.state.event_hub = EventHub()
    application.state.readings_rate_limiter = SlidingWindowRateLimiter(
        int(os.getenv("SMART_MINE_READINGS_RATE_LIMIT_PER_SECOND", "10"))
    )
    yield


app = FastAPI(
    title="SMART-MINE AI API",
    version="0.2.0-prototype",
    description="Prototype monitoring and decision-support API; not a certified safety system.",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)


@app.get("/health")
def health_check(request: Request) -> dict:
    checks = {"database": "ok"}
    try:
        request.app.state.database.latest()
    except Exception:
        checks["database"] = "error"
    status = "ok" if all(value == "ok" for value in checks.values()) else "degraded"
    return {"status": status, "checks": checks}
