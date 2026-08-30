"""Tests for intelligence/correlation.py: the I-06 Node A / Node B correlation module."""

from __future__ import annotations

from intelligence import config, correlation, risk

T0 = "2026-08-29T16:30:00Z"
T0_PLUS_10S = "2026-08-29T16:30:10Z"
T0_PLUS_60S = "2026-08-29T16:31:00Z"  # outside the 30s window


def _node(risk_value: float, confidence_value: float, timestamp: str = T0) -> dict:
    return {"risk": risk_value, "confidence": confidence_value, "timestamp": timestamp}


def test_only_node_a_abnormal_is_not_correlated():
    node_a = _node(risk_value=40.0, confidence_value=100.0)
    node_b = _node(risk_value=5.0, confidence_value=100.0)
    result = correlation.evaluate_correlation(node_a, node_b)
    assert result["node_a_abnormal"] is True
    assert result["node_b_abnormal"] is False
    assert result["correlated"] is False
    assert result["reason_codes"] == []


def test_only_node_b_abnormal_is_not_correlated():
    node_a = _node(risk_value=5.0, confidence_value=100.0)
    node_b = _node(risk_value=40.0, confidence_value=100.0)
    result = correlation.evaluate_correlation(node_a, node_b)
    assert result["correlated"] is False


def test_both_abnormal_fresh_and_healthy_is_correlated():
    node_a = _node(risk_value=40.0, confidence_value=100.0, timestamp=T0)
    node_b = _node(risk_value=45.0, confidence_value=100.0, timestamp=T0_PLUS_10S)
    result = correlation.evaluate_correlation(node_a, node_b)
    assert result["correlated"] is True
    assert result["reason_codes"] == ["NEIGHBOUR_CORRELATION"]


def test_stale_neighbour_reading_is_not_correlated():
    node_a = _node(risk_value=40.0, confidence_value=100.0, timestamp=T0)
    node_b = _node(risk_value=45.0, confidence_value=100.0, timestamp=T0_PLUS_60S)
    result = correlation.evaluate_correlation(node_a, node_b)
    assert result["stale"] is True
    assert result["correlated"] is False
    assert any("window" in note for note in result["notes"])


def test_unhealthy_low_confidence_neighbour_is_not_correlated():
    node_a = _node(risk_value=40.0, confidence_value=100.0)
    node_b = _node(risk_value=45.0, confidence_value=10.0)  # below trustworthy bar
    result = correlation.evaluate_correlation(node_a, node_b)
    assert result["correlated"] is False
    assert any("trustworthy" in note for note in result["notes"])


def test_different_abnormal_features_still_correlate():
    """Correlation must not require the SAME sensor to be elevated on both nodes."""
    tilt_thresholds = config.ACTIVE_PROFILE.sensor_thresholds["tilt_x_deg"]
    vibration_thresholds = config.ACTIVE_PROFILE.sensor_thresholds["vibration_g"]

    node_a_features = {
        "tilt_x_deg": tilt_thresholds.warning,
        "tilt_y_deg": 0.0,
        "vibration_g": 0.0,
        "displacement_mm": 0.0,
    }
    node_b_features = {
        "tilt_x_deg": 0.0,
        "tilt_y_deg": 0.0,
        "vibration_g": vibration_thresholds.warning,
        "displacement_mm": 0.0,
    }
    node_a_risk = risk.score_risk(node_a_features)
    node_b_risk = risk.score_risk(node_b_features)
    assert node_a_risk["highest_contributors"] != node_b_risk["highest_contributors"]

    node_a = _node(risk_value=node_a_risk["risk"], confidence_value=100.0, timestamp=T0)
    node_b = _node(risk_value=node_b_risk["risk"], confidence_value=100.0, timestamp=T0_PLUS_10S)
    result = correlation.evaluate_correlation(node_a, node_b)
    assert result["correlated"] is True


def test_does_not_fabricate_sensor_data():
    node_a = _node(risk_value=40.0, confidence_value=100.0)
    node_b = _node(risk_value=45.0, confidence_value=100.0)
    result = correlation.evaluate_correlation(node_a, node_b)
    assert "tilt_x_deg" not in result
    assert "sensors" not in result
