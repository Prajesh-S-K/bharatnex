"""Tests for apps/api/auth.py -- previously had zero coverage."""

from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from apps.api.auth import login, logout, require_session
from apps.api.models import LoginRequest


def fake_request(sessions: dict | None = None) -> SimpleNamespace:
    return SimpleNamespace(app=SimpleNamespace(state=SimpleNamespace(sessions=sessions or {})))


def test_login_rejects_wrong_pin(monkeypatch) -> None:
    monkeypatch.setenv("SMART_MINE_DEMO_PIN", "2468")
    request = fake_request()

    with pytest.raises(HTTPException) as excinfo:
        login(request, LoginRequest(pin="0000", role="OPERATOR"))

    assert excinfo.value.status_code == 401


def test_login_returns_token_without_leaking_issued_at(monkeypatch) -> None:
    monkeypatch.setenv("SMART_MINE_DEMO_PIN", "2468")
    request = fake_request()

    result = login(request, LoginRequest(pin="2468", role="OPERATOR"))

    assert "access_token" in result
    assert result["role"] == "OPERATOR"
    assert "issued_at" not in result
    stored = request.app.state.sessions[result["access_token"]]
    assert "issued_at" in stored


def test_require_session_accepts_a_fresh_session() -> None:
    session = {"role": "OPERATOR", "unit_id": None, "issued_at": datetime.now(UTC)}
    request = fake_request({"tok": session})

    session = require_session(request, authorization="Bearer tok")

    assert session["role"] == "OPERATOR"


def test_require_session_rejects_an_expired_session(monkeypatch) -> None:
    monkeypatch.setenv("SMART_MINE_SESSION_TTL_SECONDS", "60")
    old = datetime.now(UTC) - timedelta(seconds=120)
    request = fake_request({"tok": {"role": "OPERATOR", "unit_id": None, "issued_at": old}})

    with pytest.raises(HTTPException) as excinfo:
        require_session(request, authorization="Bearer tok")

    assert excinfo.value.status_code == 401
    assert excinfo.value.detail == "Prototype session expired"
    assert "tok" not in request.app.state.sessions


def test_require_session_rejects_an_unknown_token() -> None:
    request = fake_request()

    with pytest.raises(HTTPException) as excinfo:
        require_session(request, authorization="Bearer nope")

    assert excinfo.value.status_code == 401


def test_logout_removes_the_session() -> None:
    session = {"role": "OPERATOR", "unit_id": None, "issued_at": datetime.now(UTC)}
    request = fake_request({"tok": session})

    result = logout(request, authorization="Bearer tok")

    assert result == {"status": "logged_out"}
    assert "tok" not in request.app.state.sessions


def test_logout_is_idempotent_against_an_already_removed_token() -> None:
    request = fake_request()

    result = logout(request, authorization="Bearer nope")

    assert result == {"status": "logged_out"}
