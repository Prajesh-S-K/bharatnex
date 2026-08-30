"""Adapter wiring the Full Stack prototype to the Intelligence workstream's real
deterministic pipeline (I-02 through I-09), replacing the temporary fallback.

Keeps the exact call boundary documented in docs/INTEGRATION_GUIDE.md: this module
alone knows that `intelligence/` exists. `apps/api/routes.py` just calls `evaluate()`
and gets back the frozen decision fields -- it never imports Intelligence directly.

Every number in this file's output traces back to intelligence/config.py's centrally
documented PROTOTYPE / SYNTHETIC / TEST-ONLY thresholds -- nothing here recalculates
or duplicates a threshold.
"""

from __future__ import annotations

from intelligence import anomaly, orchestrator, state_machine
from intelligence import features as features_module

_anomaly_bundle: dict | None = None
_anomaly_attempted = False


def _get_anomaly_bundle() -> dict | None:
    """Lazily train and cache an Isolation Forest bundle from synthetic baseline data.

    Supplementary evidence only (I-09). If training ever fails for any reason, the
    deterministic pipeline keeps working with ML disabled (anomaly_evidence=None) --
    that is the whole point of I-09's optional-by-design boundary.
    """
    global _anomaly_bundle, _anomaly_attempted
    if not _anomaly_attempted:
        _anomaly_attempted = True
        try:
            baseline = anomaly.generate_synthetic_baseline()
            _anomaly_bundle = anomaly.train(baseline)
        except Exception:
            _anomaly_bundle = None
    return _anomaly_bundle


def _replay_state(risk_confidence_pairs: list) -> tuple[str, int]:
    """Reconstruct (state, streak) as of just before the current reading.

    intelligence.state_machine.evaluate_state() is a pure function of
    (previous_state, streak, risk, confidence) -- replaying it over this node's
    prior readings reconstructs the correct hysteresis state without needing a
    persisted streak column anywhere in storage.
    """
    state, streak = "NORMAL", 0
    for risk, confidence in risk_confidence_pairs:
        result = state_machine.evaluate_state(state, streak, risk, confidence)
        state, streak = result["state"], result["streak"]
    return state, streak


def evaluate(packet: dict, history: list | None = None, neighbour: dict | None = None) -> dict:
    """Evaluate one packet using the real Intelligence pipeline.

    Args:
        packet: one frozen v1 sensor-reading packet.
        history: this node's prior readings, newest first, each shaped like
            apps.api.storage.Database.latest()'s return value
            ({"id", "packet", "decision"}). Must NOT include the current packet.
        neighbour: the other node's most recent {"packet", "decision"} in the same
            shape, or None if it has never reported.

    Returns the frozen decision dict (contracts/decision.schema.json shape).
    """
    history = history or []
    risk_confidence_pairs = [
        (item["decision"]["risk"], item["decision"]["confidence"]) for item in reversed(history)
    ]
    previous_state, streak = _replay_state(risk_confidence_pairs)
    risk_history = [risk for risk, _confidence in risk_confidence_pairs]

    neighbour_arg = None
    if neighbour is not None:
        neighbour_arg = {
            "risk": neighbour["decision"]["risk"],
            "confidence": neighbour["decision"]["confidence"],
            "timestamp": neighbour["packet"]["timestamp"],
        }

    anomaly_evidence = None
    bundle = _get_anomaly_bundle()
    if bundle is not None:
        extracted = features_module.extract_features(packet)
        anomaly_evidence = anomaly.score_anomaly(extracted, bundle)

    result = orchestrator.orchestrate_decision(
        packet,
        previous_state=previous_state,
        streak=streak,
        risk_history=risk_history,
        neighbour=neighbour_arg,
        anomaly_evidence=anomaly_evidence,
    )
    return result["decision"]


def configuration_snapshot() -> dict:
    """Non-frozen traceability info for GET /api/v1/configuration and /overview.

    Never touches the frozen decision.schema.json shape -- this is a separate,
    additive endpoint payload. Reads the `_anomaly_bundle` module global directly
    rather than calling `_get_anomaly_bundle()`, which would force lazy training
    just to answer a status check.
    """
    from intelligence import config as intelligence_config

    return {
        "intelligence_profile": intelligence_config.ACTIVE_PROFILE.name,
        "intelligence_profile_status": intelligence_config.ACTIVE_PROFILE.status,
        "decision_schema_version": intelligence_config.DECISION_SCHEMA_VERSION,
        "anomaly_model_trained": _anomaly_bundle is not None,
    }
