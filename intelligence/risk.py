"""I-03 Risk scoring: deterministic hazard evidence score, NOT collapse probability.

Consumes the flattened, already-validated feature dict returned by
intelligence.features.extract_features(). Reads all thresholds from
intelligence.config.ACTIVE_PROFILE and intelligence.config.RISK_SCALE_ANCHORS --
nothing here duplicates a threshold or scale value.

Per-feature scoring is a transparent piecewise-linear mapping:

    physical zero            -> 0
    profile WATCH threshold  -> 25
    profile WARNING threshold -> 50
    profile CRITICAL threshold -> 80
    one more WATCH-WARNING-sized band above CRITICAL -> 100 (capped beyond that)

Signed features (tilt_x_deg, tilt_y_deg) are scored on their absolute magnitude --
a -3.0deg tilt is exactly as hazardous as a +3.0deg tilt.

overall Risk for this checkpoint = max(per_feature_scores). This module does not
calculate Confidence, select a state, or claim collapse prediction.
"""

from __future__ import annotations

from intelligence import config

#: Reason code each sensor feature contributes when its score reaches at least the
#: WATCH anchor. Restricted to codes that already exist in contracts/decision.schema.json.
_FEATURE_REASON_CODES: dict[str, str] = {
    "tilt_x_deg": "TILT_CHANGE",
    "tilt_y_deg": "TILT_CHANGE",
    "vibration_g": "VIBRATION_SPIKE",
    "displacement_mm": "DISPLACEMENT_RISING",
}


class MalformedFeaturesError(ValueError):
    """Raised when the input dict is not a complete, valid extracted-feature set.

    This is a defensive check against a caller skipping extract_features(); it is not
    meant to duplicate schema validation, which already happened upstream.
    """


def _require_features(features: dict) -> None:
    missing = [name for name in config.SENSOR_FEATURES if name not in features]
    if missing:
        raise MalformedFeaturesError(f"features dict is missing required keys: {missing}")
    for name in config.SENSOR_FEATURES:
        value = features[name]
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise MalformedFeaturesError(f"feature '{name}' must be numeric, got {value!r}")


def _lerp(value: float, in_lo: float, in_hi: float, out_lo: float, out_hi: float) -> float:
    if in_hi == in_lo:
        return out_hi
    fraction = (value - in_lo) / (in_hi - in_lo)
    return out_lo + fraction * (out_hi - out_lo)


def score_feature(
    magnitude: float,
    thresholds: config.SensorThresholdSet,
    anchors: dict = config.RISK_SCALE_ANCHORS,
) -> float:
    """Piecewise-linear 0-100 score for one already-non-negative feature magnitude."""
    magnitude = abs(magnitude)
    watch, warning, critical = thresholds.watch, thresholds.warning, thresholds.critical
    zero, watch_score, warning_score, critical_score, cap_score = (
        anchors["physical_zero"],
        anchors["watch"],
        anchors["warning"],
        anchors["critical"],
        anchors["cap"],
    )
    cap_point = critical + (critical - warning)

    if magnitude <= zero:
        return zero
    if magnitude <= watch:
        return _lerp(magnitude, zero, watch, zero, watch_score)
    if magnitude <= warning:
        return _lerp(magnitude, watch, warning, watch_score, warning_score)
    if magnitude <= critical:
        return _lerp(magnitude, warning, critical, warning_score, critical_score)
    if magnitude <= cap_point:
        return _lerp(magnitude, critical, cap_point, critical_score, cap_score)
    return cap_score


def score_risk(features: dict, profile: config.IntelligenceProfile = config.ACTIVE_PROFILE) -> dict:
    """Score one reading's Risk.

    Returns:
        {
            "risk": float 0-100,                  # max(per_feature_scores)
            "per_feature_scores": {feature: float, ...},
            "highest_contributors": [feature, ...],  # all features tied for the max
            "reason_codes": [str, ...],  # sorted, deduplicated, from decision contract enum
        }

    Raises MalformedFeaturesError if `features` is missing a required sensor field or
    a sensor field is non-numeric.
    """
    _require_features(features)

    per_feature_scores = {
        name: round(score_feature(features[name], profile.sensor_thresholds[name]), 4)
        for name in config.SENSOR_FEATURES
    }

    overall_risk = max(per_feature_scores.values())
    highest_contributors = sorted(
        name for name, score in per_feature_scores.items() if score == overall_risk
    )

    reason_codes = sorted(
        {
            _FEATURE_REASON_CODES[name]
            for name, score in per_feature_scores.items()
            if score >= config.RISK_SCALE_ANCHORS["watch"]
        }
    )

    return {
        "risk": round(overall_risk, 4),
        "per_feature_scores": per_feature_scores,
        "highest_contributors": highest_contributors,
        "reason_codes": reason_codes,
    }
