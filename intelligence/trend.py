"""I-05 Temporal evidence: deterministic trend and persistence over a Risk history.

Consumes a chronological list of prior Risk scores (from intelligence.risk.score_risk(),
oldest first, ending with the current reading) and reports a direction plus whether the
reading has been persistently abnormal. This is NOT a prediction of what happens next --
only a description of what the recent history already shows.

Trend direction is a plain least-squares slope over (index, risk) pairs, pure stdlib, no
ML. Persistence is a simple trailing-streak count against the WARNING risk anchor.
"""

from __future__ import annotations

from intelligence import config


def _linear_slope(values: list) -> float:
    """Least-squares slope of `values` against their index. 0.0 for a flat/degenerate series."""
    n = len(values)
    xs = list(range(n))
    mean_x = sum(xs) / n
    mean_y = sum(values) / n
    numerator = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, values, strict=True))
    denominator = sum((x - mean_x) ** 2 for x in xs)
    return numerator / denominator if denominator else 0.0


def _persistent_streak(risk_history: list, warning_anchor: float) -> int:
    """Count of trailing consecutive readings at/above the WARNING risk anchor."""
    streak = 0
    for value in reversed(risk_history):
        if value >= warning_anchor:
            streak += 1
        else:
            break
    return streak


def evaluate_trend(
    risk_history: list,
    tuning: config.PrototypeTrendTuning = config.PROTOTYPE_TREND_TUNING,
) -> dict:
    """Evaluate direction and persistence over a chronological Risk-score history.

    Args:
        risk_history: chronological list of 0-100 Risk scores, oldest first, with the
            current reading's Risk as the last element.

    Returns:
        {
            "trend": one of config.TRENDS,       # "INSUFFICIENT_DATA" if too few points
            "persistent_abnormal": bool,
            "streak": int,                        # trailing consecutive WARNING+ readings
            "reason_codes": [str, ...],           # from decision contract enum
        }
    """
    warning_anchor = config.RISK_SCALE_ANCHORS["warning"]
    streak = _persistent_streak(risk_history, warning_anchor)
    persistent_abnormal = streak >= tuning.persistent_min_streak

    if len(risk_history) < tuning.min_points_for_trend:
        trend = "INSUFFICIENT_DATA"
    else:
        slope = _linear_slope(risk_history)
        if slope > tuning.flat_slope_per_step:
            trend = "RISING"
        elif slope < -tuning.flat_slope_per_step:
            trend = "FALLING"
        else:
            trend = "STABLE"

    reason_codes = ["PERSISTENT_EVENT"] if persistent_abnormal else []

    return {
        "trend": trend,
        "persistent_abnormal": persistent_abnormal,
        "streak": streak,
        "reason_codes": reason_codes,
    }
