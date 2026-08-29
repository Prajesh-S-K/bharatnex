"""Validate SMART-MINE example payloads against their versioned JSON Schemas."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
CONTRACTS = ROOT / "contracts"

VALIDATION_PAIRS = (
    (
        CONTRACTS / "sensor-reading.schema.json",
        CONTRACTS / "examples" / "sensor-reading.normal.json",
    ),
    (
        CONTRACTS / "decision.schema.json",
        CONTRACTS / "examples" / "decision.warning.json",
    ),
)


def load_json(path: Path) -> object:
    """Read a UTF-8 JSON document."""
    with path.open(encoding="utf-8") as file:
        return json.load(file)


def validate_pair(schema_path: Path, example_path: Path) -> None:
    """Validate one example and raise a readable error on failure."""
    schema = load_json(schema_path)
    example = load_json(example_path)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(example), key=lambda error: list(error.path))

    if errors:
        details = "\n".join(
            f"- {'.'.join(map(str, error.path)) or '<root>'}: {error.message}" for error in errors
        )
        raise ValueError(f"{example_path.name} failed {schema_path.name}:\n{details}")


def main() -> None:
    """Validate every registered example/schema pair."""
    for schema_path, example_path in VALIDATION_PAIRS:
        validate_pair(schema_path, example_path)
        print(f"PASS {example_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
