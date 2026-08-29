"""Readings, command-centre state, simulator, and dispatch routes."""

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Request, WebSocket, WebSocketDisconnect

from apps.api.auth import login, require_roles, require_session
from apps.api.decision import evaluate
from apps.api.models import (
    AcknowledgeRequest,
    InspectionUpdateRequest,
    LoginRequest,
    ResolveRequest,
)
from intelligence.features import InvalidPacketError, extract_features

router = APIRouter(prefix="/api/v1")
SESSION_DEPENDENCY = Depends(require_session)
NODE_POSITIONS = {"NODE_A": [22, 42], "NODE_B": [67, 62]}
SCENARIOS = {
    "normal": {"NODE_A": (0.4, 0.2, 0.06, 1.0), "NODE_B": (0.5, 0.3, 0.08, 1.2)},
    "warning": {"NODE_A": (2.3, 1.7, 0.30, 3.2), "NODE_B": (2.1, 1.5, 0.27, 2.8)},
    "critical": {"NODE_A": (5.8, 3.7, 0.75, 7.4), "NODE_B": (4.9, 3.1, 0.62, 6.8)},
    "sensor_failure": {"NODE_A": (1.2, 0.8, 0.1, 1.8), "NODE_B": (1.1, 0.7, 0.12, 1.7)},
}


def database(request: Request):
    return request.app.state.database


@router.post("/readings", status_code=201)
async def ingest_reading(packet: dict, request: Request):
    try:
        extract_features(packet)
    except InvalidPacketError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    store = database(request)
    history = store.latest(packet["node_id"])
    latest = store.latest_by_node()
    neighbour_id = "NODE_B" if packet["node_id"] == "NODE_A" else "NODE_A"
    decision = evaluate(packet, history[0] if history else None, latest.get(neighbour_id))
    reading_id, created = store.save(packet, decision)
    if not created:
        raise HTTPException(status_code=409, detail="Duplicate node sequence")
    incident_id = store.open_incident(decision)
    if incident_id and "DISPATCH_INSPECTION" in decision["actions"]:
        store.auto_assign(incident_id, tuple(NODE_POSITIONS[packet["node_id"]]))
    result = {"id": reading_id, "packet": packet, "decision": decision}
    await request.app.state.event_hub.publish("READING_CREATED", result)
    return result


@router.get("/readings")
def list_readings(request: Request, node_id: str | None = None):
    return database(request).latest(node_id)


@router.get("/overview")
def overview(request: Request):
    store = database(request)
    latest = store.latest_by_node()
    nodes = []
    for node_id in ("NODE_A", "NODE_B"):
        item = latest.get(node_id)
        nodes.append(
            {
                "node_id": node_id,
                "position": NODE_POSITIONS[node_id],
                "reading": item,
                "online": bool(item and item["packet"]["health"]["connection_ok"]),
            }
        )
    return {
        "system": "SMART-MINE AI",
        "mode": "PROTOTYPE",
        "nodes": nodes,
        "incidents": store.incidents(),
        "units": store.units(),
        "intelligence_engine": "FALLBACK",
    }


@router.post("/demo/{scenario}")
async def run_demo(scenario: str, request: Request):
    if scenario not in SCENARIOS:
        raise HTTPException(status_code=404, detail=f"Unknown scenario: {scenario}")
    store = database(request)
    latest = store.latest_by_node()
    created = []
    now = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    keys = ("tilt_x_deg", "tilt_y_deg", "vibration_g", "displacement_mm")
    for node_id, values in SCENARIOS[scenario].items():
        previous_sequence = latest.get(node_id, {}).get("packet", {}).get("sequence", 0)
        packet = {
            "schema_version": "1.0",
            "node_id": node_id,
            "sequence": previous_sequence + 1,
            "timestamp": now,
            "sensors": dict(zip(keys, values, strict=True)),
            "health": {
                "mpu6050_ok": scenario != "sensor_failure",
                "displacement_input_ok": True,
                "connection_ok": True,
            },
        }
        other = "NODE_B" if node_id == "NODE_A" else "NODE_A"
        decision = evaluate(packet, latest.get(node_id), latest.get(other))
        reading_id, _ = store.save(packet, decision)
        incident_id = store.open_incident(decision)
        if incident_id and "DISPATCH_INSPECTION" in decision["actions"]:
            store.auto_assign(incident_id, tuple(NODE_POSITIONS[node_id]))
        created.append({"id": reading_id, "packet": packet, "decision": decision})
        latest[node_id] = created[-1]
    result = {"scenario": scenario, "created": created}
    await request.app.state.event_hub.publish("DEMO_UPDATED", result)
    return result


@router.post("/incidents/{incident_id}/dispatch")
async def dispatch(incident_id: int, request: Request, unit: str = "ALPHA"):
    if unit not in {"ALPHA", "BRAVO"}:
        raise HTTPException(status_code=422, detail="Unit must be ALPHA or BRAVO")
    incident = database(request).assign(incident_id, unit)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    await request.app.state.event_hub.publish("INCIDENT_UPDATED", incident)
    return incident


@router.post("/auth/login")
def create_session(credentials: LoginRequest, request: Request):
    return login(request, credentials)


@router.get("/units")
def list_units(request: Request):
    return database(request).units()


@router.get("/units/{unit_id}/assignment")
def unit_assignment(unit_id: str, request: Request):
    if unit_id not in {"ALPHA", "BRAVO"}:
        raise HTTPException(status_code=404, detail="Inspection unit not found")
    store = database(request)
    incident = store.unit_assignment(unit_id)
    if not incident:
        return {"unit_id": unit_id, "assignment": None}
    latest = store.latest(incident["node_id"])
    return {
        "unit_id": unit_id,
        "assignment": {
            **incident,
            "latest_reading": latest[0] if latest else None,
            "inspection_updates": store.inspection_updates(incident["id"]),
        },
    }


@router.post("/incidents/{incident_id}/inspection")
async def inspection_update(
    incident_id: int,
    update: InspectionUpdateRequest,
    request: Request,
    session: dict = SESSION_DEPENDENCY,
):
    require_roles(session, "INSPECTION")
    unit_id = session.get("unit_id")
    result = database(request).update_inspection(incident_id, unit_id, update.model_dump())
    if not result:
        raise HTTPException(status_code=404, detail="Assignment does not belong to this unit")
    await request.app.state.event_hub.publish("INSPECTION_UPDATED", result)
    return result


@router.post("/incidents/{incident_id}/acknowledge")
async def acknowledge_incident(
    incident_id: int,
    acknowledgement: AcknowledgeRequest,
    request: Request,
):
    result = database(request).acknowledge(incident_id, acknowledgement.actor)
    if not result:
        raise HTTPException(status_code=404, detail="Incident not found")
    await request.app.state.event_hub.publish("INCIDENT_UPDATED", result)
    return result


@router.post("/incidents/{incident_id}/resolve")
async def resolve_incident(
    incident_id: int,
    resolution: ResolveRequest,
    request: Request,
    session: dict = SESSION_DEPENDENCY,
):
    require_roles(session, "OPERATOR", "ADMIN")
    result = database(request).resolve(incident_id, session["role"], resolution.notes)
    if not result:
        raise HTTPException(status_code=404, detail="Incident not found")
    await request.app.state.event_hub.publish("INCIDENT_UPDATED", result)
    return result


@router.get("/incidents/{incident_id}")
def incident_detail(incident_id: int, request: Request):
    store = database(request)
    incident = store.incident(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return {
        **incident,
        "inspection_updates": store.inspection_updates(incident_id),
        "audit_events": store.audit_events(incident_id),
    }


@router.post("/demo/reset")
async def reset_demo(
    request: Request,
    session: dict = SESSION_DEPENDENCY,
):
    require_roles(session, "OPERATOR", "ADMIN")
    database(request).reset_demo()
    await request.app.state.event_hub.publish("DEMO_RESET", {})
    return {"status": "reset"}


@router.websocket("/live")
async def live_events(websocket: WebSocket):
    hub = websocket.app.state.event_hub
    await hub.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        hub.disconnect(websocket)
