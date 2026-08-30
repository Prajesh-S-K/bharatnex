"""Tests for intelligence/trend.py: the I-05 deterministic trend/persistence module."""

from __future__ import annotations

from intelligence import trend


def test_insufficient_data_below_minimum_points():
    result = trend.evaluate_trend([10.0, 20.0])  # fewer than min_points_for_trend (3)
    assert result["trend"] == "INSUFFICIENT_DATA"


def test_stable_sequence_reports_stable():
    result = trend.evaluate_trend([10.0, 11.0, 10.0, 11.0, 10.0])
    assert result["trend"] == "STABLE"


def test_rising_sequence_reports_rising():
    result = trend.evaluate_trend([5.0, 15.0, 25.0, 35.0, 45.0])
    assert result["trend"] == "RISING"


def test_falling_sequence_reports_falling():
    result = trend.evaluate_trend([80.0, 60.0, 40.0, 20.0, 0.0])
    assert result["trend"] == "FALLING"


def test_recovering_sequence_from_critical_reports_falling():
    """A descent from a high value is reported as FALLING -- there is no separate
    'RECOVERING' label in the decision contract's trend enum."""
    result = trend.evaluate_trend([90.0, 70.0, 50.0, 30.0])
    assert result["trend"] == "FALLING"


def test_persistent_abnormality_detected_after_min_streak():
    result = trend.evaluate_trend([60.0, 55.0, 52.0])  # 3 consecutive >= WARNING (50)
    assert result["persistent_abnormal"] is True
    assert result["streak"] == 3
    assert result["reason_codes"] == ["PERSISTENT_EVENT"]


def test_single_dip_below_warning_resets_the_streak():
    result = trend.evaluate_trend([60.0, 40.0, 55.0])  # streak broken by the middle dip
    assert result["persistent_abnormal"] is False
    assert result["streak"] == 1
    assert result["reason_codes"] == []


def test_trend_never_claims_prediction_language():
    """The module may explain that it does NOT predict; it must never affirmatively
    claim to predict/forecast a future event or a collapse."""
    import inspect

    source = inspect.getsource(trend).lower()
    forbidden_affirmative_phrases = (
        "predicts",
        "will collapse",
        "collapse time",
        "collapse probability",
        "forecasts",
    )
    for phrase in forbidden_affirmative_phrases:
        assert phrase not in source
