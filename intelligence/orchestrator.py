"""I-08 Decision orchestration: the one place that assembles a full decision.

Runs the deterministic pipeline built so far (I-02 through I-07) over one packet and
returns an object that validates against contracts/decision.schema.json exactly --
every produced decision is checked against the authoritative schema before being
returned, using the same jsonschema approach as intelligence/features.py.

    extract_features -> score_risk -> score_confidence -> evaluate_trend
        -> evaluate_state -> (optional) anomaly evidence -> assemble + validate

This module does not call an LLM. LLM explanation (I-10) is a separate, optional,
downstream step that consumes the finished decision object -- it never sits inside
this pipeline, so a failing/absent LLM can never affect a decision.

ML (I-09 Isolation Forest) is also optional here: `anomaly_evidence=None` (the
default) means ML is disabled and the deterministic pipeline runs unaffected, exactly
as required. When supplied, it can only ADD the existing SENSOR_ANOMALY reason code --
it never overrides Risk, Confidence, state, or actions.
"""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

from intelligence import confidence as confidence_module
from intelligence import config
from intelligence import correlation as correlation_module
from intelligence import features as features_module
from intelligence import risk as risk_module
from intelligence import state_machine as state_machine_module
from intelligence import trend as trend_module

REPO_ROOT = Path(__file__).resolve().parents[1]
DECISION_SCHEMA_PATH = REPO_ROOT / "contracts" / "decision.schema.json"

_validator_cache: dict = {}


class InvalidDecisionError(ValueError):
    """Raised if an assembled decision fails contracts/decision.schema.json validation.

    This should never happen if every input module behaves -- it exists as the
    checkpoint's required safety net ("validate every produced decision").
    """


def _get_decision_validator(schema_path: Path = DECISION_SCHEMA_PATH) -> Draft202012Validator:
    if schema_path not in _validator_cache:
        with schema_path.open(encoding="utf-8") as file:
            schema = json.load(file)
        Draft202012Validator.check_schema(schema)
        _validator_cache[schema_path] = Draft202012Validator(schema, format_checker=FormatChecker())
    return _validator_cache[schema_path]


def validate_decision(decision: dict, schema_path: Path = DECISION_SCHEMA_PATH) -> list[str]:
    """Validate `decision` against contracts/decision.schema.json.

    Returns a list of human-readable "path: message" error strings; empty means valid.
    """
    validator = _get_decision_validator(schema_path)
    errors = sorted(validator.iter_errors(decision), key=lambda error: list(error.path))
    return [
        f"{'.'.join(str(part) for part in error.path) or '<root>'}: {error.message}"
        for error in errors
    ]


def orchestrate_decision(
    packet: dict,
    previous_state: str = "NORMAL",
    streak: int = 0,
    risk_history: list | None = None,
    neighbour: dict | None = None,
    evidence_gap: bool = False,
    anomaly_evidence: dict | None = None,
    profile: config.IntelligenceProfile = config.ACTIVE_PROFILE,
) -> dict:
    """Run the full deterministic pipeline for one packet.

    Args:
        packet: raw sensor-reading packet (validated here via extract_features()).
        previous_state: state machine's prior state; pass "NORMAL" for a fresh node.
        streak: state machine's prior de-escalation streak; pass 0 for a fresh node.
        risk_history: prior Risk scores (chronological, NOT including this reading);
            None/[] means trend reports INSUFFICIENT_DATA.
        neighbour: the other node's {"risk", "confidence", "timestamp"}, or None to
            skip correlation entirely (no reason code, no fabricated evidence).
        evidence_gap: passed through to confidence.score_confidence().
        anomaly_evidence: optional I-09 output, e.g. {"anomalous": bool}. None means
            ML is disabled; the pipeline is unaffected.

    Returns:
        {
            "decision": {...},   # exactly the contracts/decision.schema.json shape
            "evidence": {...},   # rich supplementary detail, NOT part of the contract
        }

    Raises:
        features.InvalidPacketError: the raw packet failed sensor-reading schema validation.
        InvalidDecisionError: the assembled decision failed decision schema validation
            (should not happen; see class docstring).
    """
    extracted = features_module.extract_features(packet)

    risk_result = risk_module.score_risk(extracted, profile)
    confidence_result = confidence_module.score_confidence(extracted, evidence_gap, profile)

    full_risk_history = [*(risk_history or []), risk_result["risk"]]
    trend_result = trend_module.evaluate_trend(full_risk_history)

    state_result = state_machine_module.evaluate_state(
        previous_state, streak, risk_result["risk"], confidence_result["confidence"]
    )

    correlation_result = None
    if neighbour is not None:
        self_node = {
            "risk": risk_result["risk"],
            "confidence": confidence_result["confidence"],
            "timestamp": extracted["timestamp"],
        }
        correlation_result = correlation_module.evaluate_correlation(self_node, neighbour)

    reason_codes = set(risk_result["reason_codes"])
    reason_codes.update(confidence_result["reason_codes"])
    reason_codes.update(trend_result["reason_codes"])
    if correlation_result is not None:
        reason_codes.update(correlation_result["reason_codes"])
    if anomaly_evidence and anomaly_evidence.get("anomalous"):
        reason_codes.add("SENSOR_ANOMALY")

    decision = {
        "schema_version": config.DECISION_SCHEMA_VERSION,
        "node_id": extracted["node_id"],
        "timestamp": extracted["timestamp"],
        "state": state_result["state"],
        "risk": risk_result["risk"],
        "confidence": confidence_result["confidence"],
        "trend": trend_result["trend"],
        "reason_codes": sorted(reason_codes),
        "actions": list(config.STATE_ACTIONS[state_result["state"]]),
    }

    errors = validate_decision(decision)
    if errors:
        raise InvalidDecisionError(
            f"Assembled decision failed decision schema validation: {'; '.join(errors)}"
        )

    evidence = {
        "per_feature_scores": risk_result["per_feature_scores"],
        "highest_contributors": risk_result["highest_contributors"],
        "trustworthy_sensor_count": confidence_result["trustworthy_sensor_count"],
        "streak": state_result["streak"],
        "raw_state": state_result["raw_state"],
        "persistent_abnormal": trend_result["persistent_abnormal"],
        "correlation": correlation_result,
        "anomaly_evidence": anomaly_evidence,
    }

    return {"decision": decision, "evidence": evidence}
