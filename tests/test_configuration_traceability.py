"""Tests for the decision-traceability fields added to /configuration and
/overview (Module 5/7) -- and that the stale "FALLBACK" string is gone now
that apps/api/decision.py wires the real Intelligence pipeline."""

from types import SimpleNamespace

from apps.api import decision
from apps.api.routes import overview, prototype_configuration
from apps.api.storage import Database


def reset_anomaly_bundle_state() -> None:
    # _anomaly_bundle/_anomaly_attempted are process-wide module globals that
    # other tests may have already populated by calling evaluate() -- reset
    # them so this test's assertion about anomaly_model_trained is deterministic
    # regardless of what ran before it in the suite.
    decision._anomaly_bundle = None
    decision._anomaly_attempted = False


def test_configuration_exposes_intelligence_profile_and_no_stale_fallback_string() -> None:
    result = prototype_configuration()

    assert result["intelligence_profile"] == "prototype-synthetic-v1"
    assert result["intelligence_profile_status"] == "PROTOTYPE / SYNTHETIC / TEST-ONLY"
    assert result["profile"] == "PROTOTYPE / SYNTHETIC / TEST-ONLY"
    assert "FALLBACK" not in str(result)


def test_configuration_reports_anomaly_model_not_yet_trained_without_forcing_it() -> None:
    reset_anomaly_bundle_state()

    result = prototype_configuration()

    assert result["anomaly_model_trained"] is False
    # Reading the snapshot must not have forced lazy training as a side effect.
    assert decision._anomaly_attempted is False


def test_overview_exposes_the_same_traceability_fields_and_no_stale_fallback(tmp_path) -> None:
    store = Database(tmp_path / "overview.db")
    store.initialize()
    request = SimpleNamespace(app=SimpleNamespace(state=SimpleNamespace(database=store)))

    result = overview(request)

    assert result["intelligence_profile"] == "prototype-synthetic-v1"
    assert "FALLBACK" not in str(result)
