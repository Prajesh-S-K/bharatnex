"""Tests for apps/api/storage.py sequence-ordering hardening (FS-F02)."""

from apps.api.decision import evaluate
from apps.api.storage import Database


def packet(sequence: int, displacement: float = 1.0) -> dict:
    return {
        "schema_version": "1.0",
        "node_id": "NODE_A",
        "sequence": sequence,
        "timestamp": "2026-08-30T00:00:00Z",
        "sensors": {
            "tilt_x_deg": 0.4,
            "tilt_y_deg": 0.2,
            "vibration_g": 0.08,
            "displacement_mm": displacement,
        },
        "health": {"mpu6050_ok": True, "displacement_input_ok": True, "connection_ok": True},
    }


def test_exact_duplicate_sequence_is_rejected(tmp_path) -> None:
    store = Database(tmp_path / "dup.db")
    store.initialize()
    reading = packet(5)
    decision = evaluate(reading)

    first_id, created = store.save(reading, decision)
    second_id, duplicate_created = store.save(reading, decision)

    assert created is True
    assert duplicate_created is False
    assert second_id == first_id


def test_older_out_of_order_sequence_is_rejected_not_silently_accepted(tmp_path) -> None:
    store = Database(tmp_path / "older.db")
    store.initialize()
    store.save(packet(10, displacement=8.0), evaluate(packet(10, displacement=8.0)))

    late_arrival = packet(3, displacement=0.5)  # an OLD packet, delivered out of order
    _, accepted = store.save(late_arrival, evaluate(late_arrival))

    assert accepted is False
    latest = store.latest_by_node()["NODE_A"]
    assert latest["packet"]["sequence"] == 10  # must NOT have reverted to the stale reading


def test_newer_sequence_after_an_older_one_is_still_accepted(tmp_path) -> None:
    """The fix must reject only sequences that are not newer -- normal forward
    progress must keep working exactly as before."""
    store = Database(tmp_path / "forward.db")
    store.initialize()
    store.save(packet(1), evaluate(packet(1)))

    _, accepted = store.save(packet(2), evaluate(packet(2)))

    assert accepted is True
    assert store.latest_by_node()["NODE_A"]["packet"]["sequence"] == 2


def test_first_reading_for_a_node_is_always_accepted(tmp_path) -> None:
    store = Database(tmp_path / "first.db")
    store.initialize()
    _, accepted = store.save(packet(500), evaluate(packet(500)))
    assert accepted is True


def test_sequence_ordering_is_independent_per_node(tmp_path) -> None:
    """NODE_A's sequence history must not affect what is accepted for NODE_B."""
    store = Database(tmp_path / "per_node.db")
    store.initialize()
    node_a_high = packet(50)
    store.save(node_a_high, evaluate(node_a_high))

    node_b_low = dict(packet(2), node_id="NODE_B")
    node_b_low["sensors"] = dict(node_b_low["sensors"])
    _, accepted = store.save(node_b_low, evaluate(node_b_low))

    assert accepted is True


def test_connections_are_closed_after_every_operation(tmp_path) -> None:
    """Regression guard for the Windows file-lock issue: after any operation, the
    database file must be immediately deletable (no lingering open handle)."""
    db_path = tmp_path / "closable.db"
    store = Database(db_path)
    store.initialize()
    store.save(packet(1), evaluate(packet(1)))
    store.latest_by_node()

    db_path.unlink()  # must not raise PermissionError on Windows
    assert not db_path.exists()
