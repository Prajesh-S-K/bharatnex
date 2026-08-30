"""Tests for apps/api/logging_config.py."""

import contextlib
import logging
from types import SimpleNamespace

from fastapi import HTTPException

from apps.api.auth import login
from apps.api.logging_config import configure_logging
from apps.api.models import LoginRequest


def test_configure_logging_honors_the_env_var_level(monkeypatch) -> None:
    monkeypatch.setenv("SMART_MINE_LOG_LEVEL", "WARNING")

    configure_logging()

    assert logging.getLogger().getEffectiveLevel() == logging.WARNING


def test_configure_logging_defaults_to_info(monkeypatch) -> None:
    monkeypatch.delenv("SMART_MINE_LOG_LEVEL", raising=False)

    configure_logging()

    assert logging.getLogger().getEffectiveLevel() == logging.INFO


def test_login_failure_never_logs_the_literal_pin(monkeypatch, caplog) -> None:
    monkeypatch.setenv("SMART_MINE_DEMO_PIN", "2468")
    request = SimpleNamespace(app=SimpleNamespace(state=SimpleNamespace(sessions={})))

    with caplog.at_level(logging.INFO), contextlib.suppress(HTTPException):
        login(request, LoginRequest(pin="9999-secret-guess", role="OPERATOR"))

    assert "9999-secret-guess" not in caplog.text
