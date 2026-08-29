"""Feature extraction for a single frozen sensor packet.

Validates a packet against the authoritative contracts/sensor-reading.schema.json before
any feature is trusted. Nothing here scores risk or confidence -- this is the input stage
those modules will build on.

Validation policy:
    - A packet that fails schema validation (missing required field, wrong type, an
      unknown property, a bad enum value, etc.) is invalid/malformed input.
      extract_features() raises InvalidPacketError; nothing is normalized or defaulted.
    - A packet that passes schema validation but has one or more health.* flags set to
      False is valid input describing a real sensor-health failure, and is returned
      normally. Confidence scoring (not built yet) is where that health failure gets
      weighed.

Mirrors the validation approach already used by scripts/validate_contracts.py.
"""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = REPO_ROOT / "contracts" / "sensor-reading.schema.json"

_validator_cache: dict[Path, Draft202012Validator] = {}


class InvalidPacketError(ValueError):
    """Raised when a packet fails contracts/sensor-reading.schema.json validation.

    This means malformed/invalid input (missing required field, wrong type, unknown
    property, bad enum value) -- not a sensor/health failure, which is valid input.
    """


def _get_validator(schema_path: Path = SCHEMA_PATH) -> Draft202012Validator:
    """Load and cache the compiled schema validator."""
    if schema_path not in _validator_cache:
        with schema_path.open(encoding="utf-8") as file:
            schema = json.load(file)
        Draft202012Validator.check_schema(schema)
        _validator_cache[schema_path] = Draft202012Validator(schema, format_checker=FormatChecker())
    return _validator_cache[schema_path]


def validate_packet(packet: dict, schema_path: Path = SCHEMA_PATH) -> list[str]:
    """Validate `packet` against contracts/sensor-reading.schema.json.

    Returns a list of human-readable "path: message" error strings; empty list means valid.
    """
    validator = _get_validator(schema_path)
    errors = sorted(validator.iter_errors(packet), key=lambda error: list(error.path))
    return [
        f"{'.'.join(str(part) for part in error.path) or '<root>'}: {error.message}"
        for error in errors
    ]


def extract_features(packet: dict, schema_path: Path = SCHEMA_PATH) -> dict:
    """Validate a frozen packet against the shared contract and return its feature dict.

    Raises InvalidPacketError for any schema violation -- see module docstring for why
    that is a hard rejection rather than a best-effort/normalized read.

    Returns (field names match the schema exactly, just flattened for convenience):
        {
            "schema_version": str, "node_id": str, "sequence": int, "timestamp": str,
            "tilt_x_deg": float, "tilt_y_deg": float, "vibration_g": float,
            "displacement_mm": float, "mpu6050_ok": bool, "displacement_input_ok": bool,
            "connection_ok": bool,
        }
    """
    errors = validate_packet(packet, schema_path)
    if errors:
        raise InvalidPacketError(
            f"Packet failed contracts/sensor-reading.schema.json validation: {'; '.join(errors)}"
        )

    sensors = packet["sensors"]
    health = packet["health"]
    return {
        "schema_version": packet["schema_version"],
        "node_id": packet["node_id"],
        "sequence": packet["sequence"],
        "timestamp": packet["timestamp"],
        "tilt_x_deg": float(sensors["tilt_x_deg"]),
        "tilt_y_deg": float(sensors["tilt_y_deg"]),
        "vibration_g": float(sensors["vibration_g"]),
        "displacement_mm": float(sensors["displacement_mm"]),
        "mpu6050_ok": bool(health["mpu6050_ok"]),
        "displacement_input_ok": bool(health["displacement_input_ok"]),
        "connection_ok": bool(health["connection_ok"]),
    }
