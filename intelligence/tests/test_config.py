"""Tests for intelligence/config.py: the central Intelligence configuration."""

from __future__ import annotations

import importlib
import json
from pathlib import Path

import pytest

from intelligence import config

REPO_ROOT = Path(__file__).resolve().parents[2]
SENSOR_SCHEMA_PATH = REPO_ROOT / "contracts" / "sensor-reading.schema.json"
NORMAL_EXAMPLE_PATH = REPO_ROOT / "contracts" / "examples" / "sensor-reading.normal.json"

FORBIDDEN_SENSOR_FIELDS = {"crack", "edge_risk", "battery", "gas", "gas_ppm", "co2", "methane"}


def _load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as file:
        return json.load(file)


def _load_schema() -> dict:
    return _load_json(SENSOR_SCHEMA_PATH)


def _representative_warning_value(thresholds: config.SensorThresholdSet) -> float:
    """A value solidly inside the WARNING band: the midpoint between warning and critical."""
    return thresholds.warning + (thresholds.critical - thresholds.warning) / 2


def _representative_critical_value(thresholds: config.SensorThresholdSet) -> float:
    """A value solidly inside CRITICAL: one warning-to-critical band width past critical."""
    return thresholds.critical + (thresholds.critical - thresholds.warning)


def test_all_four_frozen_sensor_features_have_configuration():
    assert config.SENSOR_FEATURES == (
        "tilt_x_deg",
        "tilt_y_deg",
        "vibration_g",
        "displacement_mm",
    )
    for feature in config.SENSOR_FEATURES:
        assert feature in config.PROTOTYPE_SENSOR_THRESHOLDS


def test_sensor_features_match_the_live_schema_exactly():
    """Guards against config.py drifting from contracts/sensor-reading.schema.json."""
    schema = _load_schema()
    schema_sensor_fields = set(schema["properties"]["sensors"]["required"])
    schema_health_fields = set(schema["properties"]["health"]["required"])

    assert set(config.SENSOR_FEATURES) == schema_sensor_fields
    assert set(config.HEALTH_FLAGS) == schema_health_fields


def test_no_obsolete_or_unapproved_sensor_fields_exist():
    configured_fields = set(config.SENSOR_FEATURES) | set(config.HEALTH_FLAGS)
    assert configured_fields.isdisjoint(FORBIDDEN_SENSOR_FIELDS)
    assert "crack" not in configured_fields
    assert "edge_risk" not in configured_fields
    assert "battery" not in configured_fields


def test_sensor_threshold_values_are_non_negative_and_ordered():
    for feature, thresholds in config.PROTOTYPE_SENSOR_THRESHOLDS.items():
        assert thresholds.watch >= 0, feature
        assert thresholds.warning >= 0, feature
        assert thresholds.critical >= 0, feature
        assert thresholds.watch < thresholds.warning < thresholds.critical, feature


def test_confidence_weights_are_non_negative_and_sum_to_100():
    weights = config.PROTOTYPE_CONFIDENCE_WEIGHTS
    for flag, weight in weights.items():
        assert weight.points >= 0, flag
    total = sum(weight.points for weight in weights.values())
    assert total == pytest.approx(100.0)


def test_state_trend_reason_code_and_action_vocabularies_match_decision_schema():
    with (REPO_ROOT / "contracts" / "decision.schema.json").open(encoding="utf-8") as file:
        decision_schema = json.load(file)

    assert set(config.STATES) == set(decision_schema["properties"]["state"]["enum"])
    assert set(config.TRENDS) == set(decision_schema["properties"]["trend"]["enum"])
    assert set(config.REASON_CODES) == set(
        decision_schema["properties"]["reason_codes"]["items"]["enum"]
    )
    assert set(config.ACTIONS) == set(decision_schema["properties"]["actions"]["items"]["enum"])


def test_state_actions_only_reference_known_states_and_actions():
    assert set(config.STATE_ACTIONS) == set(config.STATES)
    for state, actions in config.STATE_ACTIONS.items():
        assert set(actions).issubset(set(config.ACTIONS)), state


def test_configuration_structures_are_immutable():
    with pytest.raises(TypeError):
        config.PROTOTYPE_SENSOR_THRESHOLDS["tilt_x_deg"] = None
    with pytest.raises(AttributeError):
        config.PROTOTYPE_SENSOR_THRESHOLDS["tilt_x_deg"].watch = 999.0
    with pytest.raises(TypeError):
        config.ACTIVE_PROFILE.sensor_thresholds["tilt_x_deg"] = None


def test_current_normal_example_remains_below_watch_for_every_sensor():
    normal_packet = _load_json(NORMAL_EXAMPLE_PATH)
    sensors = normal_packet["sensors"]
    for feature, thresholds in config.PROTOTYPE_SENSOR_THRESHOLDS.items():
        assert sensors[feature] < thresholds.watch, feature


def test_representative_warning_values_enter_the_warning_tier():
    for feature, thresholds in config.PROTOTYPE_SENSOR_THRESHOLDS.items():
        value = _representative_warning_value(thresholds)
        assert thresholds.warning <= value < thresholds.critical, feature


def test_representative_critical_values_enter_the_critical_tier():
    for feature, thresholds in config.PROTOTYPE_SENSOR_THRESHOLDS.items():
        value = _representative_critical_value(thresholds)
        assert value >= thresholds.critical, feature


def test_active_profile_wraps_the_prototype_data_without_duplicating_it():
    """ACTIVE_PROFILE must reference the same objects as the module-level constants --
    not a copy -- so there is exactly one source of truth for each threshold/weight."""
    assert config.ACTIVE_PROFILE is config.PROTOTYPE_PROFILE
    assert config.ACTIVE_PROFILE.sensor_thresholds is config.PROTOTYPE_SENSOR_THRESHOLDS
    assert config.ACTIVE_PROFILE.confidence_weights is config.PROTOTYPE_CONFIDENCE_WEIGHTS
    assert config.ACTIVE_PROFILE.name  # non-empty, named
    assert config.ACTIVE_PROFILE.status == config.PROTOTYPE_STATUS


def test_configuration_can_be_imported_consistently():
    """Two independent import paths must resolve to the exact same module object,
    so future risk/confidence/decision modules can all trust one shared source."""
    import intelligence.config as config_via_package

    reimported = importlib.import_module("intelligence.config")
    assert config_via_package is config
    assert reimported is config


def test_prototype_status_is_explicit_on_every_numeric_value():
    assert config.PROTOTYPE_STATUS == "PROTOTYPE / SYNTHETIC / TEST-ONLY"
    for thresholds in config.PROTOTYPE_SENSOR_THRESHOLDS.values():
        assert thresholds.status == config.PROTOTYPE_STATUS
    for weight in config.PROTOTYPE_CONFIDENCE_WEIGHTS.values():
        assert weight.status == config.PROTOTYPE_STATUS


def test_prototype_status_is_not_described_as_a_safety_threshold():
    """The module docstring is allowed to name these phrases only to PROHIBIT them
    (as the checkpoint instructions require); they must never label an actual value.
    So this checks the lines that assign numeric values, not the whole file's prose.
    """
    forbidden_phrases = (
        "safe mine limit",
        "collapse threshold",
        "roof-fall threshold",
        "certified warning threshold",
    )
    value_defining_markers = ("watch=", "warning=", "critical=", "points=")
    source_lines = Path(config.__file__).read_text(encoding="utf-8").lower().splitlines()
    value_lines = [
        line for line in source_lines if any(marker in line for marker in value_defining_markers)
    ]

    assert value_lines, "expected at least one numeric value-defining line to check"
    for line in value_lines:
        for phrase in forbidden_phrases:
            assert phrase not in line, f"{phrase!r} used to label a value: {line!r}"
