"""Tests for apps/api/rate_limit.py and its wiring into POST /api/v1/readings.

No TestClient here -- starlette.testclient requires an httpx binding not
installed in this environment (the same reason noted in an earlier session:
FastAPI 0.141 deprecated the installed httpx integration). Calls the route
function directly with a fake Request, matching every other test in this
suite (see tests/test_health.py).
"""

import asyncio
from types import SimpleNamespace

from fastapi import HTTPException

from apps.api.rate_limit import SlidingWindowRateLimiter
from apps.api.realtime import EventHub
from apps.api.routes import ingest_reading
from apps.api.storage import Database


class FakeClock:
    def __init__(self):
        self.now = 0.0

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


def test_third_request_in_window_is_rejected_then_recovers() -> None:
    clock = FakeClock()
    limiter = SlidingWindowRateLimiter(max_requests=2, window_seconds=1.0, clock=clock)

    assert limiter.allow("NODE_A") is True
    assert limiter.allow("NODE_A") is True
    assert limiter.allow("NODE_A") is False

    clock.advance(1.1)
    assert limiter.allow("NODE_A") is True


def test_default_limit_never_trips_at_the_critical_demo_cadence() -> None:
    """CRITICAL scenario cadence is 500ms/reading = 2/sec/node (REPORTING_INTERVALS_MS
    in apps/api/routes.py). The real default (10/sec/node) must give it headroom."""
    clock = FakeClock()
    limiter = SlidingWindowRateLimiter(max_requests=10, window_seconds=1.0, clock=clock)

    for _ in range(20):
        assert limiter.allow("NODE_A") is True
        clock.advance(0.5)


def packet(sequence: int) -> dict:
    return {
        "schema_version": "1.0",
        "node_id": "NODE_A",
        "sequence": sequence,
        "timestamp": "2026-08-30T00:00:00Z",
        "sensors": {
            "tilt_x_deg": 0.4,
            "tilt_y_deg": 0.2,
            "vibration_g": 0.06,
            "displacement_mm": 1.0,
        },
        "health": {"mpu6050_ok": True, "displacement_input_ok": True, "connection_ok": True},
    }


def fake_request(database, limiter) -> SimpleNamespace:
    state = SimpleNamespace(database=database, readings_rate_limiter=limiter, event_hub=EventHub())
    return SimpleNamespace(app=SimpleNamespace(state=state))


def test_readings_endpoint_returns_429_once_the_real_limiter_is_exhausted(tmp_path) -> None:
    store = Database(tmp_path / "rate_limit.db")
    store.initialize()
    limiter = SlidingWindowRateLimiter(max_requests=2)
    request = fake_request(store, limiter)

    statuses = []
    for i in range(4):
        try:
            # x_device_id passed explicitly: calling the route function directly
            # bypasses FastAPI's dependency injection, so its Header(default=...)
            # would otherwise bind to the Header descriptor object itself, which
            # sqlite3 cannot store via store.audit()'s actor column.
            asyncio.run(ingest_reading(packet(i + 1), request, x_device_id="TEST"))
            statuses.append(201)
        except HTTPException as error:
            statuses.append(error.status_code)

    assert statuses == [201, 201, 429, 429]
