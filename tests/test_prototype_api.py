"""Core prototype tests without depending on an HTTP test client."""

from apps.api.decision import evaluate
from apps.api.storage import Database


def packet(sequence: int, displacement: float, vibration: float = 0.08) -> dict:
    return {
        "schema_version": "1.0",
        "node_id": "NODE_A",
        "sequence": sequence,
        "timestamp": "2026-08-30T00:00:00Z",
        "sensors": {
            "tilt_x_deg": displacement / 2,
            "tilt_y_deg": 0.2,
            "vibration_g": vibration,
            "displacement_mm": displacement,
        },
        "health": {
            "mpu6050_ok": True,
            "displacement_input_ok": True,
            "connection_ok": True,
        },
    }


def test_decision_keeps_risk_and_confidence_separate() -> None:
    decision = evaluate(packet(1, 4.5, 0.4))

    assert decision["state"] == "WARNING"
    assert decision["risk"] != decision["confidence"]
    assert "CREATE_INCIDENT" in decision["actions"]
    assert "DISPLACEMENT_RISING" in decision["reason_codes"]


def test_database_persists_and_rejects_duplicate_sequence(tmp_path) -> None:
    store = Database(tmp_path / "prototype.db")
    store.initialize()
    reading = packet(1, 1.0)
    decision = evaluate(reading)

    reading_id, created = store.save(reading, decision)
    duplicate_id, duplicate_created = store.save(reading, decision)

    assert created is True
    assert duplicate_created is False
    assert duplicate_id == reading_id
    assert store.latest_by_node()["NODE_A"]["packet"] == reading


def test_inspection_lifecycle_is_persisted_and_audited(tmp_path) -> None:
    store = Database(tmp_path / "workflow.db")
    store.initialize()
    critical = evaluate(packet(1, 8.0, 0.8))
    incident_id = store.open_incident(critical)

    assignment = store.auto_assign(incident_id, (22, 42))
    assert assignment is not None
    unit_id = assignment["assigned_unit"]

    accepted = store.update_inspection(incident_id, unit_id, {"status": "ACCEPTED"})
    completed = store.update_inspection(
        incident_id,
        unit_id,
        {
            "status": "COMPLETED",
            "severity": "MODERATE",
            "notes": "Model joint inspected",
            "checklist": {"area_isolated": True},
        },
    )

    assert accepted["status"] == "ACCEPTED"
    assert completed["checklist"] == {"area_isolated": True}
    assert store.incident(incident_id)["status"] == "INSPECTION_COMPLETED"
    assert store.unit_assignment(unit_id) is None
    assert {event["event_type"] for event in store.audit_events(incident_id)} >= {
        "INCIDENT_CREATED",
        "UNIT_DISPATCHED",
        "ACCEPTED",
        "COMPLETED",
    }


def test_rejected_assignment_returns_unit_and_incident_to_queue(tmp_path) -> None:
    store = Database(tmp_path / "reject.db")
    store.initialize()
    incident_id = store.open_incident(evaluate(packet(1, 8.0, 0.8)))
    assignment = store.assign(incident_id, "ALPHA")

    store.update_inspection(
        incident_id,
        assignment["assigned_unit"],
        {"status": "REJECTED", "rejection_reason": "Route obstructed"},
    )

    assert store.incident(incident_id)["status"] == "OPEN"
    assert store.incident(incident_id)["assigned_unit"] is None
    assert next(unit for unit in store.units() if unit["id"] == "ALPHA")["status"] == "AVAILABLE"
