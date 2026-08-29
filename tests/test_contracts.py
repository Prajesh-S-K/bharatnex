"""Contract tests shared by all three workstreams."""

from scripts.validate_contracts import VALIDATION_PAIRS, validate_pair


def test_all_registered_examples_match_their_schemas() -> None:
    for schema_path, example_path in VALIDATION_PAIRS:
        validate_pair(schema_path, example_path)
