"""Tests for intelligence/risk.py: the I-03 deterministic Risk-scoring module."""

from __future__ import annotations

import pytest

from intelligence import config, risk

DISPLACEMENT = config.ACTIVE_PROFILE.sensor_thresholds["displacement_mm"]
TILT_X = config.ACTIVE_PROFILE.sensor_thresholds["tilt_x_deg"]
ANCHORS = config.RISK_SCALE_ANCHORS


def _baseline_features(**overrides) -> dict:
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


def test_physical_zero_scores_zero():
    assert risk.score_feature(0.0, DISPLACEMENT) == pytest.approx(ANCHORS["physical_zero"])


def test_just_below_watch_scores_between_zero_and_watch_anchor():
    value = DISPLACEMENT.watch - 1.0  # 1.0mm, watch=2.0mm
    score = risk.score_feature(value, DISPLACEMENT)
    assert 0.0 < score < ANCHORS["watch"]


def test_watch_anchor_scores_exactly_25():
    assert risk.score_feature(DISPLACEMENT.watch, DISPLACEMENT) == pytest.approx(ANCHORS["watch"])


def test_between_watch_and_warning_scores_between_25_and_50():
    midpoint = (DISPLACEMENT.watch + DISPLACEMENT.warning) / 2
    score = risk.score_feature(midpoint, DISPLACEMENT)
    assert ANCHORS["watch"] < score < ANCHORS["warning"]


def test_warning_anchor_scores_exactly_50():
    assert risk.score_feature(DISPLACEMENT.warning, DISPLACEMENT) == pytest.approx(
        ANCHORS["warning"]
    )


def test_between_warning_and_critical_scores_between_50_and_80():
    midpoint = (DISPLACEMENT.warning + DISPLACEMENT.critical) / 2
    score = risk.score_feature(midpoint, DISPLACEMENT)
    assert ANCHORS["warning"] < score < ANCHORS["critical"]


def test_critical_anchor_scores_exactly_80():
    assert risk.score_feature(DISPLACEMENT.critical, DISPLACEMENT) == pytest.approx(
        ANCHORS["critical"]
    )


def test_above_critical_scores_between_80_and_100():
    value = DISPLACEMENT.critical + (DISPLACEMENT.critical - DISPLACEMENT.warning) / 2
    score = risk.score_feature(value, DISPLACEMENT)
    assert ANCHORS["critical"] < score < ANCHORS["cap"]


def test_cap_point_and_beyond_are_capped_at_100():
    cap_point = DISPLACEMENT.critical + (DISPLACEMENT.critical - DISPLACEMENT.warning)
    assert risk.score_feature(cap_point, DISPLACEMENT) == pytest.approx(ANCHORS["cap"])
    assert risk.score_feature(cap_point * 10, DISPLACEMENT) == pytest.approx(ANCHORS["cap"])


def test_negative_tilt_scores_by_absolute_magnitude():
    positive = risk.score_feature(TILT_X.warning + 0.5, TILT_X)
    negative = risk.score_feature(-(TILT_X.warning + 0.5), TILT_X)
    assert negative == pytest.approx(positive)


def test_multi_feature_max_selection_lists_every_tied_contributor():
    features = _baseline_features(
        displacement_mm=DISPLACEMENT.critical,  # scores exactly 80
        tilt_x_deg=TILT_X.critical,  # also scores exactly 80
    )
    result = risk.score_risk(features)
    assert result["risk"] == pytest.approx(ANCHORS["critical"])
    assert set(result["highest_contributors"]) == {"displacement_mm", "tilt_x_deg"}


def test_single_contributor_when_no_tie():
    features = _baseline_features(displacement_mm=DISPLACEMENT.critical)
    result = risk.score_risk(features)
    assert result["highest_contributors"] == ["displacement_mm"]


def test_reason_codes_map_to_elevated_features_only():
    features = _baseline_features(displacement_mm=DISPLACEMENT.warning)  # above watch
    result = risk.score_risk(features)
    assert result["reason_codes"] == ["DISPLACEMENT_RISING"]
    assert set(result["reason_codes"]).issubset(set(config.REASON_CODES))


def test_baseline_reading_has_no_reason_codes():
    result = risk.score_risk(_baseline_features())
    assert result["risk"] == pytest.approx(0.0)
    assert result["reason_codes"] == []


def test_malformed_input_missing_feature_is_rejected():
    features = _baseline_features()
    del features["vibration_g"]
    with pytest.raises(risk.MalformedFeaturesError):
        risk.score_risk(features)


def test_malformed_input_non_numeric_feature_is_rejected():
    features = _baseline_features(vibration_g="not-a-number")
    with pytest.raises(risk.MalformedFeaturesError):
        risk.score_risk(features)


def test_score_risk_never_computes_confidence():
    result = risk.score_risk(_baseline_features())
    assert "confidence" not in result
