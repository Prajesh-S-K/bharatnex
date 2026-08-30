"""Tests for intelligence/orchestrator.py: the I-08 decision orchestrator."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from intelligence import config, features, orchestrator

REPO_ROOT = Path(__file__).resolve().parents[2]


def _packet(
    node_id="NODE_A",
    sequence=1,
    timestamp="2026-08-29T16:30:00Z",
    tilt_x=0.0,
    tilt_y=0.0,
    vibration=0.0,
    displacement=0.0,
    mpu6050_ok=True,
    displacement_input_ok=True,
    connection_ok=True,
) -> dict:
    return {
        "schema_version": "1.0",
        "node_id": node_id,
        "sequence": sequence,
        "timestamp": timestamp,
        "sensors": {
            "tilt_x_deg": tilt_x,
            "tilt_y_deg": tilt_y,
            "vibration_g": vibration,
            "displacement_mm": displacement,
        },
        "health": {
            "mpu6050_ok": mpu6050_ok,
            "displacement_input_ok": displacement_input_ok,
            "connection_ok": connection_ok,
        },
    }


def _decision_schema_validator():
    from jsonschema import Draft202012Validator, FormatChecker

    with (REPO_ROOT / "contracts" / "decision.schema.json").open(encoding="utf-8") as file:
        schema = json.load(file)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def test_normal_reading_produces_a_schema_valid_normal_decision():
    result = orchestrator.orchestrate_decision(_packet(displacement=1.2))
    decision = result["decision"]
    assert decision["state"] == "NORMAL"
    assert _decision_schema_validator().is_valid(decision)


def test_watch_reading_produces_watch_state():
    result = orchestrator.orchestrate_decision(_packet(displacement=2.5))
    assert result["decision"]["state"] == "WATCH"


def test_warning_reading_produces_warning_state():
    result = orchestrator.orchestrate_decision(_packet(displacement=4.5))
    assert result["decision"]["state"] == "WARNING"


def test_critical_reading_produces_critical_state():
    result = orchestrator.orchestrate_decision(_packet(displacement=9.0))
    assert result["decision"]["state"] == "CRITICAL"


def test_every_produced_decision_validates_against_the_live_schema():
    validator = _decision_schema_validator()
    for displacement in (1.2, 2.5, 4.5, 9.0):
        result = orchestrator.orchestrate_decision(_packet(displacement=displacement))
        errors = list(validator.iter_errors(result["decision"]))
        assert errors == []


def test_state_actions_match_frozen_decision_contract_exactly():
    result = orchestrator.orchestrate_decision(_packet(displacement=9.0))
    decision = result["decision"]
    expected_actions = list(config.STATE_ACTIONS[decision["state"]])
    assert decision["actions"] == expected_actions
    assert set(decision["actions"]).issubset(set(config.ACTIONS))


def test_malformed_packet_raises_invalid_packet_error():
    broken = _packet()
    del broken["sensors"]["displacement_mm"]
    with pytest.raises(features.InvalidPacketError):
        orchestrator.orchestrate_decision(broken)


def test_degraded_health_lowers_confidence_and_adds_reason_code():
    result = orchestrator.orchestrate_decision(_packet(displacement=1.2, connection_ok=False))
    decision = result["decision"]
    assert decision["confidence"] < 100.0
    assert "LOW_SENSOR_HEALTH" in decision["reason_codes"]
    # health failure alone must not raise or block a decision from being produced
    assert decision["state"] in config.STATES


def test_stale_missing_evidence_flag_adds_reason_code():
    result = orchestrator.orchestrate_decision(_packet(displacement=1.2), evidence_gap=True)
    decision = result["decision"]
    assert "MISSING_DATA" in decision["reason_codes"]
    assert decision["confidence"] < 100.0


def test_neighbour_correlation_is_reflected_in_decision_and_evidence():
    neighbour = {"risk": 40.0, "confidence": 100.0, "timestamp": "2026-08-29T16:30:05Z"}
    result = orchestrator.orchestrate_decision(_packet(displacement=4.5), neighbour=neighbour)
    decision = result["decision"]
    assert "NEIGHBOUR_CORRELATION" in decision["reason_codes"]
    assert result["evidence"]["correlation"]["correlated"] is True


def test_stale_neighbour_does_not_trigger_correlation():
    neighbour = {
        "risk": 40.0,
        "confidence": 100.0,
        "timestamp": "2026-08-29T18:00:00Z",
    }  # far apart
    result = orchestrator.orchestrate_decision(_packet(displacement=4.5), neighbour=neighbour)
    decision = result["decision"]
    assert "NEIGHBOUR_CORRELATION" not in decision["reason_codes"]
    assert result["evidence"]["correlation"]["stale"] is True


def test_no_neighbour_skips_correlation_entirely_without_error():
    result = orchestrator.orchestrate_decision(_packet(displacement=1.2), neighbour=None)
    assert result["evidence"]["correlation"] is None
    assert "NEIGHBOUR_CORRELATION" not in result["decision"]["reason_codes"]


def test_pipeline_operates_deterministically_with_ml_disabled():
    """anomaly_evidence=None (the default) means ML is disabled; the pipeline must
    still produce a complete, valid decision, unaffected."""
    result = orchestrator.orchestrate_decision(_packet(displacement=1.2), anomaly_evidence=None)
    assert "SENSOR_ANOMALY" not in result["decision"]["reason_codes"]
    assert _decision_schema_validator().is_valid(result["decision"])


def test_ml_evidence_can_only_add_the_sensor_anomaly_reason_code():
    baseline = orchestrator.orchestrate_decision(_packet(displacement=1.2))
    with_anomaly = orchestrator.orchestrate_decision(
        _packet(displacement=1.2), anomaly_evidence={"anomalous": True}
    )
    assert "SENSOR_ANOMALY" not in baseline["decision"]["reason_codes"]
    assert "SENSOR_ANOMALY" in with_anomaly["decision"]["reason_codes"]
    # everything else about the decision is unchanged by ML being on
    for key in ("risk", "confidence", "state", "trend", "actions"):
        assert baseline["decision"][key] == with_anomaly["decision"][key]


def test_pipeline_never_imports_or_calls_an_llm():
    """The docstring may explain that this module does NOT call an LLM; it must not
    actually import one. Checked via real import statements, not prose."""
    import ast
    import inspect

    tree = ast.parse(inspect.getsource(orchestrator))
    imported_names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_names.add(node.module)
            imported_names.update(alias.name for alias in node.names)

    assert not any("llm" in name.lower() for name in imported_names)
    assert not any("explanation" in name.lower() for name in imported_names)


def test_trend_uses_supplied_risk_history():
    rising_history = [10.0, 30.0, 50.0]
    result = orchestrator.orchestrate_decision(
        _packet(displacement=4.5), risk_history=rising_history
    )
    assert result["decision"]["trend"] == "RISING"


def test_insufficient_risk_history_reports_insufficient_data_trend():
    result = orchestrator.orchestrate_decision(_packet(displacement=1.2), risk_history=None)
    assert result["decision"]["trend"] == "INSUFFICIENT_DATA"
