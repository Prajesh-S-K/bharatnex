"""I-06 Neighbour correlation: independent evidence from Node A and Node B together.

Consumes each node's already-computed Risk/Confidence result plus its packet
timestamp -- never raw sensor values, and never one node's data standing in for the
other's. Correlation means both nodes independently show elevated concern within a
shared time window; it does not mean copying one node's Risk onto the other, and it
does not require the SAME sensor feature to be elevated on both nodes.
"""

from __future__ import annotations

from datetime import datetime

from intelligence import config


def _parse_timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def evaluate_correlation(
    node_a: dict,
    node_b: dict,
    tuning: config.PrototypeCorrelationTuning = config.PROTOTYPE_CORRELATION_TUNING,
) -> dict:
    """Evaluate whether Node A and Node B independently corroborate the same concern.

    Args:
        node_a, node_b: {"risk": float, "confidence": float, "timestamp": str}, each
            already produced by intelligence.risk.score_risk() /
            intelligence.confidence.score_confidence() for that node's own reading.

    Returns:
        {
            "correlated": bool,
            "node_a_abnormal": bool,
            "node_b_abnormal": bool,
            "stale": bool,               # readings fall outside the correlation window
            "reason_codes": [str, ...],  # from decision contract enum
            "notes": [str, ...],         # human-readable limitations, not fabricated data
        }
    """
    time_a = _parse_timestamp(node_a["timestamp"])
    time_b = _parse_timestamp(node_b["timestamp"])
    gap_seconds = abs((time_a - time_b).total_seconds())
    stale = gap_seconds > tuning.window_seconds

    watch_anchor = config.RISK_SCALE_ANCHORS["watch"]
    node_a_abnormal = node_a["risk"] >= watch_anchor
    node_b_abnormal = node_b["risk"] >= watch_anchor

    node_a_trustworthy = node_a["confidence"] >= tuning.min_trustworthy_confidence
    node_b_trustworthy = node_b["confidence"] >= tuning.min_trustworthy_confidence

    notes = []
    if stale:
        notes.append(
            f"neighbour readings are {gap_seconds:.1f}s apart, outside the "
            f"{tuning.window_seconds:.0f}s correlation window"
        )
    if not node_a_trustworthy:
        notes.append("node A confidence is below the trustworthy bar; correlation withheld")
    if not node_b_trustworthy:
        notes.append("node B confidence is below the trustworthy bar; correlation withheld")

    correlated = (
        not stale
        and node_a_abnormal
        and node_b_abnormal
        and node_a_trustworthy
        and node_b_trustworthy
    )

    reason_codes = ["NEIGHBOUR_CORRELATION"] if correlated else []

    return {
        "correlated": correlated,
        "node_a_abnormal": node_a_abnormal,
        "node_b_abnormal": node_b_abnormal,
        "stale": stale,
        "reason_codes": reason_codes,
        "notes": notes,
    }
