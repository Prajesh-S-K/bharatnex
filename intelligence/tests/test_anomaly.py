"""Tests for intelligence/anomaly.py: the I-09 supplementary anomaly-evidence module."""

from __future__ import annotations

import pytest

from intelligence import anomaly, config, orchestrator


def _packet(displacement=1.2, tilt_x=0.4, tilt_y=0.2, vibration=0.08):
    return {
        "schema_version": "1.0",
        "node_id": "NODE_A",
        "sequence": 1,
        "timestamp": "2026-08-29T16:30:00Z",
        "sensors": {
            "tilt_x_deg": tilt_x,
            "tilt_y_deg": tilt_y,
            "vibration_g": vibration,
            "displacement_mm": displacement,
        },
        "health": {"mpu6050_ok": True, "displacement_input_ok": True, "connection_ok": True},
    }


@pytest.fixture(scope="module")
def trained_bundle():
    baseline = anomaly.generate_synthetic_baseline(n=150)
    return anomaly.train(baseline)


def test_ml_disabled_returns_safe_non_anomalous_default():
    result = anomaly.score_anomaly({"tilt_x_deg": 99.0}, bundle=None)
    assert result == {"anomalous": False, "anomaly_score": 0.0, "ml_enabled": False}


def test_score_anomaly_never_exposes_risk_confidence_state_or_action():
    result = anomaly.score_anomaly({"tilt_x_deg": 0.4}, bundle=None)
    forbidden_keys = {"risk", "confidence", "state", "action", "actions"}
    assert forbidden_keys.isdisjoint(result.keys())


def test_normal_synthetic_reading_scores_low(trained_bundle):
    normal_features = {
        "tilt_x_deg": 0.4,
        "tilt_y_deg": 0.2,
        "vibration_g": 0.08,
        "displacement_mm": 1.2,
    }
    result = anomaly.score_anomaly(normal_features, trained_bundle)
    assert result["ml_enabled"] is True
    assert result["anomaly_score"] < config.PROTOTYPE_ANOMALY_TUNING.anomalous_threshold
    assert result["anomalous"] is False


def test_extreme_reading_scores_high_and_anomalous(trained_bundle):
    extreme_features = {
        "tilt_x_deg": 20.0,
        "tilt_y_deg": 15.0,
        "vibration_g": 5.0,
        "displacement_mm": 100.0,
    }
    result = anomaly.score_anomaly(extreme_features, trained_bundle)
    assert result["anomaly_score"] > 0.7
    assert result["anomalous"] is True


def test_generate_synthetic_baseline_is_deterministic():
    first = anomaly.generate_synthetic_baseline(n=50, seed=7)
    second = anomaly.generate_synthetic_baseline(n=50, seed=7)
    assert first == second


def test_train_rejects_too_little_baseline_data():
    tiny_baseline = anomaly.generate_synthetic_baseline(n=3)
    with pytest.raises(ValueError):
        anomaly.train(tiny_baseline)


def test_deterministic_pipeline_operates_with_ml_disabled_end_to_end():
    """The full orchestrator, run with anomaly_evidence=None, must still produce a
    complete valid decision -- the deterministic pipeline is unaffected by ML."""
    result = orchestrator.orchestrate_decision(_packet(), anomaly_evidence=None)
    assert result["decision"]["state"] == "NORMAL"
    assert "SENSOR_ANOMALY" not in result["decision"]["reason_codes"]


def test_anomaly_evidence_flows_into_orchestrator_as_supplementary_only(trained_bundle):
    extreme_features_packet = _packet(
        displacement=1.2
    )  # calm sensors, but we'll force anomaly evidence
    baseline = orchestrator.orchestrate_decision(extreme_features_packet)

    forced_anomaly_evidence = anomaly.score_anomaly(
        {"tilt_x_deg": 20.0, "tilt_y_deg": 15.0, "vibration_g": 5.0, "displacement_mm": 100.0},
        trained_bundle,
    )
    assert forced_anomaly_evidence["anomalous"] is True

    with_anomaly = orchestrator.orchestrate_decision(
        extreme_features_packet, anomaly_evidence=forced_anomaly_evidence
    )
    assert "SENSOR_ANOMALY" in with_anomaly["decision"]["reason_codes"]
    # Risk/Confidence/state/actions come from the calm sensor values, not from the
    # anomaly flag -- ML evidence only adds a reason code, never overrides these.
    for key in ("risk", "confidence", "state", "actions"):
        assert baseline["decision"][key] == with_anomaly["decision"][key]
