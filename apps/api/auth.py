"""Minimal role sessions for a closed-network hackathon prototype."""

import logging
import os
import secrets
from datetime import UTC, datetime, timedelta

from fastapi import Header, HTTPException, Request

from apps.api.models import LoginRequest

logger = logging.getLogger(__name__)

DEFAULT_SESSION_TTL_SECONDS = 14400  # 4 hours


def _session_ttl() -> timedelta:
    ttl_seconds = int(os.getenv("SMART_MINE_SESSION_TTL_SECONDS", DEFAULT_SESSION_TTL_SECONDS))
    return timedelta(seconds=ttl_seconds)


def login(request: Request, credentials: LoginRequest) -> dict:
    configured_pin = os.getenv("SMART_MINE_DEMO_PIN", "2468")
    if not secrets.compare_digest(credentials.pin, configured_pin):
        logger.info("login failed role=%s unit_id=%s", credentials.role, credentials.unit_id)
        raise HTTPException(status_code=401, detail="Incorrect prototype PIN")
    token = secrets.token_urlsafe(24)
    session = {"role": credentials.role, "unit_id": credentials.unit_id}
    request.app.state.sessions[token] = {**session, "issued_at": datetime.now(UTC)}
    logger.info("login succeeded role=%s unit_id=%s", credentials.role, credentials.unit_id)
    # NOTE: the returned dict deliberately excludes issued_at -- only the stored
    # session (above) is annotated with it, so it never leaks into the API response.
    return {"access_token": token, **session}


def require_session(
    request: Request,
    authorization: str | None = Header(default=None),
) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Prototype session required")
    sessions = request.app.state.sessions
    key = authorization.removeprefix("Bearer ")
    session = sessions.get(key)
    if not session:
        raise HTTPException(status_code=401, detail="Prototype session expired")
    if datetime.now(UTC) - session["issued_at"] > _session_ttl():
        del sessions[key]
        raise HTTPException(status_code=401, detail="Prototype session expired")
    return session


def logout(request: Request, authorization: str | None = Header(default=None)) -> dict:
    if authorization and authorization.startswith("Bearer "):
        request.app.state.sessions.pop(authorization.removeprefix("Bearer "), None)
    logger.info("logout")
    return {"status": "logged_out"}


def require_roles(session: dict, *roles: str) -> None:
    if session["role"] not in roles:
        raise HTTPException(status_code=403, detail="Role is not permitted for this action")
