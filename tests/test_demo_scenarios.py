"""Tests for apps/api/routes.py SCENARIOS: every documented demo scenario must exist
and produce its intended state (FS-F06 Judge Demo hardening)."""

from apps.api.decision import evaluate
from apps.api.routes import SCENARIOS

REQUIRED_SCENARIOS = {"normal", "watch", "warning", "critical", "sensor_failure", "node_offline"}


def _packet(node_id: str, values: tuple) -> dict:
    tilt_x, tilt_y, vibration, displacement = values
    return {
        "schema_version": "1.0",
        "node_id": node_id,
        "sequence": 1,
        "timestamp": "2026-08-30T00:00:00Z",
        "sensors": {
            "tilt_x_deg": tilt_x,
            "tilt_y_deg": tilt_y,
            "vibration_g": vibration,
            "displacement_mm": displacement,
        },
        "health": {"mpu6050_ok": True, "displacement_input_ok": True, "connection_ok": True},
    }


def test_all_documented_demo_scenarios_are_registered():
    assert REQUIRED_SCENARIOS.issubset(SCENARIOS.keys())


def test_watch_scenario_produces_watch_state_for_both_nodes():
    for node_id, values in SCENARIOS["watch"].items():
        decision = evaluate(_packet(node_id, values))
        assert decision["state"] == "WATCH", f"{node_id}: {decision}"


def test_normal_scenario_produces_normal_state_for_both_nodes():
    for node_id, values in SCENARIOS["normal"].items():
        decision = evaluate(_packet(node_id, values))
        assert decision["state"] == "NORMAL", f"{node_id}: {decision}"


def test_warning_scenario_produces_warning_state_for_both_nodes():
    for node_id, values in SCENARIOS["warning"].items():
        decision = evaluate(_packet(node_id, values))
        assert decision["state"] == "WARNING", f"{node_id}: {decision}"


def test_critical_scenario_produces_critical_state_for_both_nodes():
    for node_id, values in SCENARIOS["critical"].items():
        decision = evaluate(_packet(node_id, values))
        assert decision["state"] == "CRITICAL", f"{node_id}: {decision}"
