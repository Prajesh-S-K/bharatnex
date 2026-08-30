"""Tests for intelligence/confidence.py: the I-04 Confidence module, independent of Risk."""

from __future__ import annotations

import inspect

import pytest

from intelligence import confidence, config, risk


def _features(**overrides) -> dict:
    base = {
        "node_id": "NODE_A",
        "sequence": 1,
        "timestamp": "2026-08-29T16:30:00Z",
        "tilt_x_deg": 0.0,
        "tilt_y_deg": 0.0,
        "vibration_g": 0.0,
        "displacement_mm": 0.0,
        "mpu6050_ok": True,
        "displacement_input_ok": True,
        "connection_ok": True,
    }
    base.update(overrides)
    return base


def test_score_confidence_has_no_risk_parameter():
    """Structural proof: Confidence cannot be derived from Risk if it never receives one."""
    parameters = inspect.signature(confidence.score_confidence).parameters
    assert "risk" not in parameters


def test_all_healthy_yields_full_confidence():
    result = confidence.score_confidence(_features())
    assert result["confidence"] == pytest.approx(100.0)
    assert result["trustworthy_sensor_count"] == 3
    assert result["reason_codes"] == []


def test_one_unhealthy_flag_reduces_confidence_and_adds_reason_code():
    result = confidence.score_confidence(_features(connection_ok=False))
    assert result["confidence"] == pytest.approx(200.0 / 3)
    assert result["trustworthy_sensor_count"] == 2
    assert result["reason_codes"] == ["LOW_SENSOR_HEALTH"]


def test_all_unhealthy_flags_yield_zero_confidence():
    result = confidence.score_confidence(
        _features(mpu6050_ok=False, displacement_input_ok=False, connection_ok=False)
    )
    assert result["confidence"] == pytest.approx(0.0)
    assert result["trustworthy_sensor_count"] == 0
    assert result["reason_codes"] == ["LOW_SENSOR_HEALTH"]


def test_evidence_gap_applies_penalty_and_reason_code():
    result = confidence.score_confidence(_features(), evidence_gap=True)
    expected = 100.0 - config.PROTOTYPE_STALE_EVIDENCE_PENALTY.points
    assert result["confidence"] == pytest.approx(expected)
    assert result["reason_codes"] == ["MISSING_DATA"]


def test_evidence_gap_penalty_floors_at_zero_not_negative():
    result = confidence.score_confidence(
        _features(mpu6050_ok=False, displacement_input_ok=False, connection_ok=False),
        evidence_gap=True,
    )
    assert result["confidence"] == pytest.approx(0.0)
    assert set(result["reason_codes"]) == {"LOW_SENSOR_HEALTH", "MISSING_DATA"}


def test_structurally_valid_unhealthy_packet_does_not_raise():
    features = _features(mpu6050_ok=False)
    result = confidence.score_confidence(features)  # must not raise
    assert 0.0 <= result["confidence"] <= 100.0


def test_malformed_input_missing_health_flag_is_rejected():
    features = _features()
    del features["connection_ok"]
    with pytest.raises(confidence.MalformedFeaturesError):
        confidence.score_confidence(features)


def test_malformed_input_non_boolean_health_flag_is_rejected():
    features = _features(connection_ok="true")
    with pytest.raises(confidence.MalformedFeaturesError):
        confidence.score_confidence(features)


def test_high_risk_reading_can_have_low_confidence():
    displacement = config.ACTIVE_PROFILE.sensor_thresholds["displacement_mm"]
    features = _features(
        displacement_mm=displacement.critical,  # drives Risk high
        mpu6050_ok=False,
        displacement_input_ok=False,
        connection_ok=False,  # drives Confidence to zero
    )
    risk_result = risk.score_risk(features)
    confidence_result = confidence.score_confidence(features)
    assert risk_result["risk"] >= config.RISK_SCALE_ANCHORS["critical"]
    assert confidence_result["confidence"] == pytest.approx(0.0)


def test_low_risk_reading_can_also_have_low_confidence():
    features = _features(mpu6050_ok=False, displacement_input_ok=False, connection_ok=False)
    risk_result = risk.score_risk(features)  # baseline sensor values -> low Risk
    confidence_result = confidence.score_confidence(features)
    assert risk_result["risk"] == pytest.approx(0.0)
    assert confidence_result["confidence"] == pytest.approx(0.0)


def test_high_risk_reading_can_also_have_high_confidence():
    displacement = config.ACTIVE_PROFILE.sensor_thresholds["displacement_mm"]
    features = _features(displacement_mm=displacement.critical)  # healthy, but extreme
    risk_result = risk.score_risk(features)
    confidence_result = confidence.score_confidence(features)
    assert risk_result["risk"] >= config.RISK_SCALE_ANCHORS["critical"]
    assert confidence_result["confidence"] == pytest.approx(100.0)
