"""Readings, command-centre state, simulator, and dispatch routes."""

import csv
import io
import os
import secrets
from datetime import UTC, datetime
from html import escape

from fastapi import (
    APIRouter,
    Depends,
    Header,
    HTTPException,
    Request,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.responses import HTMLResponse, StreamingResponse

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
    "watch": {"NODE_A": (1.3, 0.9, 0.16, 1.9), "NODE_B": (1.1, 0.8, 0.14, 1.7)},
    "warning": {"NODE_A": (2.3, 1.7, 0.30, 3.2), "NODE_B": (2.1, 1.5, 0.27, 2.8)},
    "critical": {"NODE_A": (5.8, 3.7, 0.75, 7.4), "NODE_B": (4.9, 3.1, 0.62, 6.8)},
    "sensor_failure": {"NODE_A": (1.2, 0.8, 0.1, 1.8), "NODE_B": (1.1, 0.7, 0.12, 1.7)},
    "node_offline": {"NODE_A": (0.4, 0.2, 0.06, 1.0), "NODE_B": (0.5, 0.3, 0.08, 1.2)},
}
REPORTING_INTERVALS_MS = {"NORMAL": 5000, "WATCH": 2000, "WARNING": 1000, "CRITICAL": 500}


def database(request: Request):
    return request.app.state.database


@router.post("/readings", status_code=201)
async def ingest_reading(
    packet: dict,
    request: Request,
    x_device_id: str = Header(default="DIRECT_OR_SIMULATOR"),
    x_device_key: str | None = Header(default=None),
):
    configured_key = os.getenv("SMART_MINE_GATEWAY_KEY")
    if configured_key and (
        x_device_key is None or not secrets.compare_digest(x_device_key, configured_key)
    ):
        raise HTTPException(status_code=401, detail="Invalid gateway credentials")
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
        raise HTTPException(
            status_code=409,
            detail="Sequence is not newer than the latest stored reading for this node",
        )
    incident_id = store.open_incident(decision)
    if incident_id and "DISPATCH_INSPECTION" in decision["actions"]:
        store.auto_assign(incident_id, tuple(NODE_POSITIONS[packet["node_id"]]))
    gateway_command = {
        "command_id": f"{packet['node_id']}-{packet['sequence']}",
        "reporting_interval_ms": REPORTING_INTERVALS_MS[decision["state"]],
        "led_state": decision["state"],
        "buzzer": decision["state"] == "CRITICAL",
    }
    result = {
        "id": reading_id,
        "source": x_device_id,
        "packet": packet,
        "decision": decision,
        "gateway_command": gateway_command,
    }
    store.audit(
        x_device_id,
        "READING_ACCEPTED",
        incident_id,
        {"node_id": packet["node_id"], "sequence": packet["sequence"]},
    )
    await request.app.state.event_hub.publish("READING_CREATED", result)
    return result


@router.post("/gateway/ack")
async def acknowledge_gateway_command(
    acknowledgement: dict,
    request: Request,
    x_device_id: str = Header(default="ESP32-S3-GATEWAY"),
    x_device_key: str | None = Header(default=None),
):
    configured_key = os.getenv("SMART_MINE_GATEWAY_KEY")
    if configured_key and (
        x_device_key is None or not secrets.compare_digest(x_device_key, configured_key)
    ):
        raise HTTPException(status_code=401, detail="Invalid gateway credentials")
    if not acknowledgement.get("command_id") or acknowledgement.get("status") not in {
        "APPLIED",
        "FAILED",
    }:
        raise HTTPException(status_code=422, detail="command_id and APPLIED/FAILED status required")
    database(request).audit(x_device_id, "GATEWAY_COMMAND_ACK", None, acknowledgement)
    await request.app.state.event_hub.publish("GATEWAY_COMMAND_ACK", acknowledgement)
    return {"accepted": True, **acknowledgement}


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
                "connection_ok": scenario != "node_offline" or node_id != "NODE_B",
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


@router.get("/configuration")
def prototype_configuration():
    return {
        "profile": "PROTOTYPE / SYNTHETIC / TEST-ONLY",
        "active_panel": "PANEL-01",
        "reporting_intervals_ms": REPORTING_INTERVALS_MS,
        "offline_after_missed_intervals": 3,
        "intelligence_engine": "FALLBACK",
        "target_devices": [
            {"unit": "ALPHA", "model": "OnePlus Nord CE5", "platform": "Android 16"},
            {
                "unit": "BRAVO",
                "model": "Moto G86 Power 5G",
                "platform": "Android 16",
                "resolution": "2712x1220",
            },
        ],
    }


@router.get("/exports/readings.csv")
def export_readings(request: Request):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "node_id",
            "sequence",
            "timestamp",
            "tilt_x_deg",
            "tilt_y_deg",
            "vibration_g",
            "displacement_mm",
            "state",
            "risk",
            "confidence",
            "trend",
        ]
    )
    for reading in reversed(database(request).latest()):
        packet, decision = reading["packet"], reading["decision"]
        writer.writerow(
            [
                packet["node_id"],
                packet["sequence"],
                packet["timestamp"],
                packet["sensors"]["tilt_x_deg"],
                packet["sensors"]["tilt_y_deg"],
                packet["sensors"]["vibration_g"],
                packet["sensors"]["displacement_mm"],
                decision["state"],
                decision["risk"],
                decision["confidence"],
                decision["trend"],
            ]
        )
    headers = {"Content-Disposition": 'attachment; filename="smart-mine-readings.csv"'}
    return StreamingResponse(iter([output.getvalue()]), media_type="text/csv", headers=headers)


@router.get("/incidents/{incident_id}/report", response_class=HTMLResponse)
def printable_incident_report(incident_id: int, request: Request):
    store = database(request)
    incident = store.incident(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    updates = store.inspection_updates(incident_id)
    rows = "".join(
        f"<tr><td>{item['timestamp']}</td><td>{item['unit_id']}</td>"
        f"<td>{escape(item['status'])}</td><td>{escape(item.get('notes') or '—')}</td></tr>"
        for item in updates
    )
    return f"""<!doctype html><title>Incident INC-{incident_id:03d}</title>
    <style>body{{font:14px Arial;max-width:850px;margin:40px auto;color:#172033}}
    h1{{border-bottom:3px solid #10b981;padding-bottom:12px}}
    table{{width:100%;border-collapse:collapse}}
    td,th{{padding:9px;border:1px solid #ccd4df;text-align:left}}small{{color:#64748b}}</style>
    <h1>SMART-MINE AI — Incident INC-{incident_id:03d}</h1>
    <p><b>Node:</b> {incident["node_id"]} &nbsp; <b>State:</b> {incident["state"]} &nbsp;
    <b>Status:</b> {incident["status"]}</p><p><b>Opened:</b> {incident["opened_at"]} &nbsp;
    <b>Assigned unit:</b> {incident.get("assigned_unit") or "Unassigned"}</p>
    <p><b>Safety response:</b> {incident["recommendation"]}</p>
    <h2>Inspection timeline</h2><table><tr><th>Time</th><th>Actor</th><th>Status</th>
    <th>Notes</th></tr>{rows}</table><p><small>Prototype decision-support report.
    Not a certified industrial safety record.</small></p>"""


@router.post("/automation/complete-inspections")
async def complete_demo_inspections(request: Request):
    store = database(request)
    completed = []
    for unit in store.units():
        incident = store.unit_assignment(unit["id"])
        if not incident:
            continue
        result = None
        for status in ("ACCEPTED", "EN_ROUTE", "ON_SITE", "INSPECTION_STARTED", "COMPLETED"):
            result = store.update_inspection(
                incident["id"],
                unit["id"],
                {
                    "status": status,
                    "notes": "Automated judge-demo inspection" if status == "COMPLETED" else None,
                    "severity": "MODERATE" if status == "COMPLETED" else None,
                    "checklist": {"demo_verified": True} if status == "COMPLETED" else {},
                },
            )
        completed.append(result)
    await request.app.state.event_hub.publish("INSPECTION_UPDATED", {"completed": completed})
    return {"completed": completed}


@router.post("/automation/reset")
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
