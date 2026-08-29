"""Smoke tests for the Full Stack API boundary."""

from fastapi.routing import APIRoute

from apps.api.main import app


def find_route(path: str) -> APIRoute:
    return next(route for route in app.routes if isinstance(route, APIRoute) and route.path == path)


def test_health_endpoint_reports_ok() -> None:
    route = find_route("/health")

    assert "GET" in route.methods
    assert route.endpoint() == {"status": "ok"}
