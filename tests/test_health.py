"""Smoke tests for the Full Stack API boundary."""

from types import SimpleNamespace

from fastapi.routing import APIRoute

from apps.api.main import app
from apps.api.storage import Database


def find_route(path: str) -> APIRoute:
    return next(route for route in app.routes if isinstance(route, APIRoute) and route.path == path)


def fake_request(database) -> SimpleNamespace:
    return SimpleNamespace(app=SimpleNamespace(state=SimpleNamespace(database=database)))


def test_health_endpoint_reports_ok(tmp_path) -> None:
    route = find_route("/health")
    store = Database(tmp_path / "health.db")
    store.initialize()

    assert "GET" in route.methods
    assert route.endpoint(fake_request(store)) == {"status": "ok", "checks": {"database": "ok"}}


def test_health_endpoint_reports_degraded_when_database_check_fails() -> None:
    route = find_route("/health")

    class BrokenDatabase:
        def latest(self, node_id=None):
            raise RuntimeError("database unavailable")

    result = route.endpoint(fake_request(BrokenDatabase()))

    assert result == {"status": "degraded", "checks": {"database": "error"}}
