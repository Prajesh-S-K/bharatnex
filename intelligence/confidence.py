"""I-04 Confidence: trust in the available evidence, independent of Risk.

Consumes the flattened, already-validated feature dict returned by
intelligence.features.extract_features(). Reads weights from
intelligence.config.ACTIVE_PROFILE.confidence_weights and the evidence-gap penalty
from intelligence.config.PROTOTYPE_STALE_EVIDENCE_PENALTY.

Confidence considers:
    - mpu6050_ok, displacement_input_ok, connection_ok (weighted, equal split)
    - missing/delayed evidence (the `evidence_gap` flag, set by a future
      temporal/orchestration caller once I-05 exists; defaults to False here)
    - the resulting count of trustworthy contributing sensors

score_confidence() NEVER takes a Risk value as input -- structurally, there is no
parameter for it. A high-Risk reading can have low Confidence (bad health, extreme
values) and a low-Risk reading can also have low Confidence (bad health, calm
values); this module has no way to know or care which case it is in.

Structurally valid packets with health flags False remain fully processable here --
they just score lower, never raise.
"""

from __future__ import annotations

from intelligence import config


class MalformedFeaturesError(ValueError):
    """Raised when the input dict is missing a required health flag or it is non-boolean."""


def _require_health_flags(features: dict) -> None:
    missing = [name for name in config.HEALTH_FLAGS if name not in features]
    if missing:
        raise MalformedFeaturesError(f"features dict is missing required keys: {missing}")
    for name in config.HEALTH_FLAGS:
        value = features[name]
        if not isinstance(value, bool):
            raise MalformedFeaturesError(f"health flag '{name}' must be boolean, got {value!r}")


def score_confidence(
    features: dict,
    evidence_gap: bool = False,
    profile: config.IntelligenceProfile = config.ACTIVE_PROFILE,
) -> dict:
    """Score one reading's Confidence.

    Args:
        features: extract_features() output.
        evidence_gap: True when the caller knows this evidence is stale, delayed, or
            otherwise incomplete beyond what the packet itself carries (e.g. a
            skipped sequence number or an overdue heartbeat). Defaults to False since
            no temporal tracking exists yet at this checkpoint.

    Returns:
        {
            "confidence": float 0-100,
            "trustworthy_sensor_count": int,  # 0-3, health flags currently True
            "reason_codes": [str, ...],       # from decision contract enum
        }

    Raises MalformedFeaturesError if a required health flag is missing or non-boolean.
    """
    _require_health_flags(features)

    trustworthy_sensor_count = sum(1 for name in config.HEALTH_FLAGS if features[name] is True)
    weighted_points = sum(
        profile.confidence_weights[name].points
        for name in config.HEALTH_FLAGS
        if features[name] is True
    )

    if evidence_gap:
        weighted_points = max(0.0, weighted_points - config.PROTOTYPE_STALE_EVIDENCE_PENALTY.points)

    reason_codes = set()
    if trustworthy_sensor_count < len(config.HEALTH_FLAGS):
        reason_codes.add("LOW_SENSOR_HEALTH")
    if evidence_gap:
        reason_codes.add("MISSING_DATA")

    return {
        "confidence": round(max(0.0, min(100.0, weighted_points)), 4),
        "trustworthy_sensor_count": trustworthy_sensor_count,
        "reason_codes": sorted(reason_codes),
    }
