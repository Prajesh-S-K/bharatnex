"""Tests for Part A (device-health telemetry) and Part B (BLE-anchor relative
proximity) -- apps/api/storage.py's new tables/methods and the routes wired to
them."""

from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from apps.api.models import DeviceHealthRequest, UnitProximityRequest
from apps.api.routes import report_device_health, report_proximity
from apps.api.storage import Database


def test_device_health_round_trips(tmp_path) -> None:
    store = Database(tmp_path / "health.db")
    store.initialize()

    store.record_device_health("GATEWAY_01", chip_temp_c=42.5, chip_temp_warning=False)

    result = store.device_health()
    assert result == [
        {
            "device_id": "GATEWAY_01",
            "chip_temp_c": 42.5,
            "chip_temp_warning": False,
            "updated_at": result[0]["updated_at"],
        }
    ]


def test_device_health_upsert_updates_the_same_device_row(tmp_path) -> None:
    store = Database(tmp_path / "health.db")
    store.initialize()

    store.record_device_health("NODE_A", chip_temp_c=50.0, chip_temp_warning=False)
    store.record_device_health("NODE_A", chip_temp_c=95.0, chip_temp_warning=True)

    result = store.device_health()
    assert len(result) == 1
    assert result[0]["chip_temp_c"] == 95.0
    assert result[0]["chip_temp_warning"] is True


def test_report_device_health_route_requires_gateway_key(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("SMART_MINE_GATEWAY_KEY", "secret-key")
    store = Database(tmp_path / "health.db")
    store.initialize()
    request = SimpleNamespace(app=SimpleNamespace(state=SimpleNamespace(database=store)))
    health = DeviceHealthRequest(chip_temp_c=91.0, chip_temp_warning=True)

    with pytest.raises(HTTPException) as excinfo:
        report_device_health("GATEWAY_01", health, request, x_device_key=None)

    assert excinfo.value.status_code == 401


def test_units_have_no_anchor_reading_by_default(tmp_path) -> None:
    store = Database(tmp_path / "units.db")
    store.initialize()

    units = store.units()

    assert all(unit["anchor_rssi"] is None for unit in units)
    assert all(unit["closer_to_anchor"] is None for unit in units)


def test_closer_to_anchor_is_none_when_only_one_unit_has_reported(tmp_path) -> None:
    store = Database(tmp_path / "units.db")
    store.initialize()

    store.record_proximity("ALPHA", -50)

    units = {unit["id"]: unit for unit in store.units()}
    assert units["ALPHA"]["anchor_rssi"] == -50
    assert units["ALPHA"]["closer_to_anchor"] is None
    assert units["BRAVO"]["closer_to_anchor"] is None


def test_closer_to_anchor_picks_the_less_negative_rssi(tmp_path) -> None:
    store = Database(tmp_path / "units.db")
    store.initialize()

    store.record_proximity("ALPHA", -40)  # stronger signal = closer
    store.record_proximity("BRAVO", -70)

    units = {unit["id"]: unit for unit in store.units()}
    assert units["ALPHA"]["closer_to_anchor"] is True
    assert units["BRAVO"]["closer_to_anchor"] is False


def test_closer_to_anchor_ignores_a_stale_reading(tmp_path) -> None:
    store = Database(tmp_path / "units.db")
    store.initialize()
    store.record_proximity("ALPHA", -40)
    store.record_proximity("BRAVO", -70)

    # Force BRAVO's stored timestamp far in the past to exercise the freshness
    # boundary with a real timestamp rather than mocking internals.
    with store._connection() as connection:
        connection.execute(
            "UPDATE units SET anchor_rssi_updated_at = ? WHERE id = ?",
            ("2000-01-01T00:00:00Z", "BRAVO"),
        )

    units = {unit["id"]: unit for unit in store.units()}
    assert units["ALPHA"]["closer_to_anchor"] is None
    assert units["BRAVO"]["closer_to_anchor"] is None


def test_proximity_route_rejects_reporting_for_a_different_unit(tmp_path) -> None:
    store = Database(tmp_path / "units.db")
    store.initialize()
    request = SimpleNamespace(app=SimpleNamespace(state=SimpleNamespace(database=store)))
    session = {"role": "INSPECTION", "unit_id": "ALPHA"}

    with pytest.raises(HTTPException) as excinfo:
        report_proximity("BRAVO", UnitProximityRequest(rssi=-50), request, session=session)

    assert excinfo.value.status_code == 403


def test_proximity_route_accepts_reporting_for_the_owning_unit(tmp_path) -> None:
    store = Database(tmp_path / "units.db")
    store.initialize()
    request = SimpleNamespace(app=SimpleNamespace(state=SimpleNamespace(database=store)))
    session = {"role": "INSPECTION", "unit_id": "ALPHA"}

    result = report_proximity("ALPHA", UnitProximityRequest(rssi=-55), request, session=session)

    assert result == {"status": "recorded"}
    assert store.units()[0]["anchor_rssi"] == -55
