"""Tests for intelligence/features.py against the authoritative sensor-reading contract."""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from intelligence.features import InvalidPacketError, extract_features, validate_packet

REPO_ROOT = Path(__file__).resolve().parents[2]
NORMAL_PACKET_PATH = REPO_ROOT / "contracts" / "examples" / "sensor-reading.normal.json"
ABNORMAL_CANDIDATE_PATH = (
    Path(__file__).resolve().parents[1] / "fixtures" / "packet_abnormal_candidate.json"
)


def _load(path: Path) -> dict:
    with path.open(encoding="utf-8") as file:
        return json.load(file)


@pytest.fixture
def normal_packet() -> dict:
    return _load(NORMAL_PACKET_PATH)


@pytest.fixture
def abnormal_candidate_packet() -> dict:
    return _load(ABNORMAL_CANDIDATE_PATH)


def test_valid_normal_packet_is_accepted(normal_packet):
    assert validate_packet(normal_packet) == []
    extract_features(normal_packet)  # must not raise


def test_abnormal_candidate_packet_is_accepted_structurally(abnormal_candidate_packet):
    assert validate_packet(abnormal_candidate_packet) == []
    extract_features(abnormal_candidate_packet)  # must not raise


def test_extracted_sensor_and_health_values_are_correct(normal_packet):
    features = extract_features(normal_packet)
    assert features["node_id"] == "NODE_A"
    assert features["sequence"] == 1
    assert features["tilt_x_deg"] == pytest.approx(0.4)
    assert features["tilt_y_deg"] == pytest.approx(0.2)
    assert features["vibration_g"] == pytest.approx(0.08)
    assert features["displacement_mm"] == pytest.approx(1.2)
    assert features["mpu6050_ok"] is True
    assert features["displacement_input_ok"] is True
    assert features["connection_ok"] is True


def test_missing_required_field_raises_invalid_packet_error(normal_packet):
    broken = copy.deepcopy(normal_packet)
    del broken["sensors"]["displacement_mm"]
    with pytest.raises(InvalidPacketError):
        extract_features(broken)


def test_wrong_datatype_raises_invalid_packet_error(normal_packet):
    broken = copy.deepcopy(normal_packet)
    broken["sensors"]["tilt_x_deg"] = "not-a-number"
    with pytest.raises(InvalidPacketError):
        extract_features(broken)


def test_connection_ok_false_remains_structurally_valid_and_stays_false(normal_packet):
    unhealthy = copy.deepcopy(normal_packet)
    unhealthy["health"]["connection_ok"] = False
    assert validate_packet(unhealthy) == []
    features = extract_features(unhealthy)
    assert features["connection_ok"] is False


def test_unknown_additional_property_is_rejected(normal_packet):
    broken = copy.deepcopy(normal_packet)
    broken["unexpected_field"] = "not-part-of-the-contract"
    with pytest.raises(InvalidPacketError):
        extract_features(broken)
