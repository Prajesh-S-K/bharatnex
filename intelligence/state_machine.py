"""I-07 State machine: deterministic NORMAL -> WATCH -> WARNING -> CRITICAL transitions.

A pure function, not a stateful object: the caller (I-08's orchestrator) persists the
previous state and streak counter between calls and passes them back in each time. This
keeps every transition deterministic and independently testable, with no hidden state.

Hysteresis rule (anti-flapping):
    - Escalation (toward a MORE severe state) happens immediately on any single
      reading -- a rising hazard is never delayed by this module.
    - De-escalation (toward a LESS severe state) requires `deescalation_streak`
      consecutive readings that are both calmer (lower risk bucket) AND sufficiently
      confident (>= the shared trustworthy-confidence bar) before the state actually
      steps down. An untrustworthy "calm" reading does not count toward recovery and
      resets the streak.

The raw severity bucket for a Risk score reuses intelligence.config.RISK_SCALE_ANCHORS
directly -- watch=25, warning=50, critical=80 -- so there is exactly one place that
mapping lives.
"""

from __future__ import annotations

from intelligence import config

_SEVERITY_ORDER: tuple = ("NORMAL", "WATCH", "WARNING", "CRITICAL")
_SEVERITY_RANK: dict = {state: rank for rank, state in enumerate(_SEVERITY_ORDER)}


def bucket_for_risk(risk: float, anchors: dict = config.RISK_SCALE_ANCHORS) -> str:
    """The raw severity state a Risk score alone would suggest, before hysteresis."""
    if risk < anchors["watch"]:
        return "NORMAL"
    if risk < anchors["warning"]:
        return "WATCH"
    if risk < anchors["critical"]:
        return "WARNING"
    return "CRITICAL"


def evaluate_state(
    previous_state: str,
    streak: int,
    risk: float,
    confidence: float,
    tuning: config.PrototypeStateTuning = config.PROTOTYPE_STATE_TUNING,
    min_trustworthy_confidence: float = (
        config.PROTOTYPE_CORRELATION_TUNING.min_trustworthy_confidence
    ),
) -> dict:
    """Advance the state machine by exactly one reading.

    Args:
        previous_state: one of config.STATES -- the state before this reading.
        streak: the de-escalation streak counter carried over from the previous call
            (0 if the last reading was not a de-escalation candidate).
        risk: this reading's overall Risk (0-100, from intelligence.risk.score_risk()).
        confidence: this reading's Confidence (0-100, from
            intelligence.confidence.score_confidence()).

    Returns:
        {"state": one of config.STATES, "streak": int, "raw_state": one of config.STATES}
    """
    if previous_state not in _SEVERITY_RANK:
        raise ValueError(
            f"Unknown previous_state {previous_state!r}; expected one of {config.STATES}"
        )

    raw_state = bucket_for_risk(risk)
    previous_rank = _SEVERITY_RANK[previous_state]
    raw_rank = _SEVERITY_RANK[raw_state]

    if raw_rank > previous_rank:
        return {"state": raw_state, "streak": 0, "raw_state": raw_state}

    if raw_rank < previous_rank:
        trustworthy = confidence >= min_trustworthy_confidence
        new_streak = streak + 1 if trustworthy else 0
        if new_streak >= tuning.deescalation_streak:
            return {"state": raw_state, "streak": 0, "raw_state": raw_state}
        return {"state": previous_state, "streak": new_streak, "raw_state": raw_state}

    return {"state": previous_state, "streak": 0, "raw_state": raw_state}
