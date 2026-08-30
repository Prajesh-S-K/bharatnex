"""Minimal role sessions for a closed-network hackathon prototype."""

import os
import secrets

from fastapi import Header, HTTPException, Request

from apps.api.models import LoginRequest


def login(request: Request, credentials: LoginRequest) -> dict:
    configured_pin = os.getenv("SMART_MINE_DEMO_PIN", "2468")
    if not secrets.compare_digest(credentials.pin, configured_pin):
        raise HTTPException(status_code=401, detail="Incorrect prototype PIN")
    token = secrets.token_urlsafe(24)
    session = {"role": credentials.role, "unit_id": credentials.unit_id}
    request.app.state.sessions[token] = session
    return {"access_token": token, **session}


def require_session(
    request: Request,
    authorization: str | None = Header(default=None),
) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Prototype session required")
    session = request.app.state.sessions.get(authorization.removeprefix("Bearer "))
    if not session:
        raise HTTPException(status_code=401, detail="Prototype session expired")
    return session


def require_roles(session: dict, *roles: str) -> None:
    if session["role"] not in roles:
        raise HTTPException(status_code=403, detail="Role is not permitted for this action")
