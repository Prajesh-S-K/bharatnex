"""Tests for intelligence/state_machine.py: the I-07 hysteresis-protected state machine."""

from __future__ import annotations

import pytest

from intelligence import config, state_machine

NORMAL_RISK = 10.0
WATCH_RISK = 30.0
WARNING_RISK = 60.0
CRITICAL_RISK = 90.0
FULL_CONFIDENCE = 100.0
LOW_CONFIDENCE = 10.0


def test_bucket_for_risk_matches_scale_anchors():
    assert state_machine.bucket_for_risk(0.0) == "NORMAL"
    assert state_machine.bucket_for_risk(WATCH_RISK) == "WATCH"
    assert state_machine.bucket_for_risk(WARNING_RISK) == "WARNING"
    assert state_machine.bucket_for_risk(CRITICAL_RISK) == "CRITICAL"


def test_full_escalation_path_is_immediate_each_step():
    result = state_machine.evaluate_state("NORMAL", 0, WATCH_RISK, FULL_CONFIDENCE)
    assert result["state"] == "WATCH"
    result = state_machine.evaluate_state(
        result["state"], result["streak"], WARNING_RISK, FULL_CONFIDENCE
    )
    assert result["state"] == "WARNING"
    result = state_machine.evaluate_state(
        result["state"], result["streak"], CRITICAL_RISK, FULL_CONFIDENCE
    )
    assert result["state"] == "CRITICAL"


def test_recovery_requires_the_full_deescalation_streak():
    streak_needed = config.PROTOTYPE_STATE_TUNING.deescalation_streak
    state, streak = "CRITICAL", 0
    for _ in range(streak_needed - 1):
        result = state_machine.evaluate_state(state, streak, WARNING_RISK, FULL_CONFIDENCE)
        assert result["state"] == "CRITICAL"  # still holding
        state, streak = result["state"], result["streak"]

    final = state_machine.evaluate_state(state, streak, WARNING_RISK, FULL_CONFIDENCE)
    assert final["state"] == "WARNING"  # streak completed -> steps down exactly one tier
    assert final["streak"] == 0


def test_full_recovery_path_normal_from_critical():
    state, streak = "CRITICAL", 0
    for target_risk in (WARNING_RISK, WARNING_RISK, WARNING_RISK):
        result = state_machine.evaluate_state(state, streak, target_risk, FULL_CONFIDENCE)
        state, streak = result["state"], result["streak"]
    assert state == "WARNING"

    for target_risk in (WATCH_RISK, WATCH_RISK, WATCH_RISK):
        result = state_machine.evaluate_state(state, streak, target_risk, FULL_CONFIDENCE)
        state, streak = result["state"], result["streak"]
    assert state == "WATCH"

    for target_risk in (NORMAL_RISK, NORMAL_RISK, NORMAL_RISK):
        result = state_machine.evaluate_state(state, streak, target_risk, FULL_CONFIDENCE)
        state, streak = result["state"], result["streak"]
    assert state == "NORMAL"


def test_oscillating_risk_at_a_boundary_does_not_flap():
    """A risk value bouncing between WARNING and WATCH must never toggle the state
    back and forth -- de-escalation needs a sustained streak, and any reading that
    is NOT strictly calmer than the current state resets the streak to zero."""
    state, streak = "WARNING", 0
    for _ in range(10):
        result = state_machine.evaluate_state(state, streak, WATCH_RISK, FULL_CONFIDENCE)
        state, streak = result["state"], result["streak"]
        assert state == "WARNING"  # never flips on a single calmer reading
        result = state_machine.evaluate_state(state, streak, WARNING_RISK, FULL_CONFIDENCE)
        state, streak = result["state"], result["streak"]
        assert state == "WARNING"
        assert streak == 0  # the equal-severity reading resets the streak


def test_low_confidence_blocks_deescalation_indefinitely():
    state, streak = "CRITICAL", 0
    for _ in range(10):
        result = state_machine.evaluate_state(state, streak, WARNING_RISK, LOW_CONFIDENCE)
        state, streak = result["state"], result["streak"]
    assert state == "CRITICAL"  # never recovers on untrustworthy calm readings
    assert streak == 0


def test_low_confidence_does_not_block_escalation():
    result = state_machine.evaluate_state("NORMAL", 0, CRITICAL_RISK, 0.0)
    assert result["state"] == "CRITICAL"  # escalation ignores confidence entirely


def test_same_bucket_reading_holds_state_and_resets_streak():
    result = state_machine.evaluate_state("WARNING", 2, WARNING_RISK, FULL_CONFIDENCE)
    assert result["state"] == "WARNING"
    assert result["streak"] == 0


def test_unknown_previous_state_raises():
    with pytest.raises(ValueError):
        state_machine.evaluate_state("NOT_A_STATE", 0, WATCH_RISK, FULL_CONFIDENCE)
