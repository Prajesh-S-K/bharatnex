"""I-10 LLM explanation: human-readable prose only, generated LAST and never trusted
for anything else.

Input is exactly the finished, schema-valid decision object from
intelligence.orchestrator.orchestrate_decision() plus its supplementary evidence --
never a raw packet, and this module has no access to raw sensor values at all (the
decision object only carries Risk/Confidence/state/trend/reason_codes/actions, and
evidence carries derived per-feature 0-100 scores, not raw measurements).

No real LLM provider is wired up in this repository yet (no API key/client in
.env.example). `llm_client` is the extension point: pass a callable(decision,
evidence) -> str once one exists. With `llm_client=None` (the default), this module
falls back to a deterministic, template-based explanation built only from already-
decided facts -- exactly the kind of sentence an LLM would be asked to phrase more
naturally, e.g.: "Displacement and vibration exceeded prototype warning ranges on
both nearby nodes, increasing confidence in the warning."

Hard boundary: generate_explanation() returns ONLY a text string (+ its source). It
never returns or recomputes risk, confidence, state, or a recommended action, and
ANY exception raised by `llm_client` is caught here -- a failing/misbehaving LLM
falls back to the template and the decision pipeline continues normally.
"""

from __future__ import annotations

from collections.abc import Callable

_REASON_CODE_CLAUSES: dict = {
    "SENSOR_ANOMALY": "the sensor pattern was statistically unusual",
    "DISPLACEMENT_RISING": "displacement moved into the prototype elevated range",
    "TILT_CHANGE": "tilt moved into the prototype elevated range",
    "VIBRATION_SPIKE": "vibration moved into the prototype elevated range",
    "NEIGHBOUR_CORRELATION": "a nearby node independently showed related movement",
    "NEAR_ACTIVE_FACE": "the node is close to the active face",
    "PERSISTENT_EVENT": "the elevated reading has persisted across multiple checks",
    "LOW_SENSOR_HEALTH": "one or more sensors reported reduced health",
    "MISSING_DATA": "recent evidence was stale or incomplete",
}


def _template_explanation(decision: dict) -> str:
    """Deterministic fallback: turns already-decided facts into one plain sentence."""
    reason_codes = decision.get("reason_codes", [])
    if not reason_codes:
        return f"Node {decision['node_id']} is {decision['state']}: no elevated evidence to report."

    clauses = "; ".join(_REASON_CODE_CLAUSES.get(code, code) for code in reason_codes)
    trend = decision["trend"].lower()
    return f"Node {decision['node_id']} is {decision['state']} because {clauses}. Trend: {trend}."


def generate_explanation(
    decision: dict,
    evidence: dict,
    llm_client: Callable[[dict, dict], str] | None = None,
) -> dict:
    """Produce a human-readable explanation for one finished decision.

    Args:
        decision: the schema-valid decision object from orchestrate_decision().
        evidence: that same call's supplementary evidence dict.
        llm_client: optional callable(decision, evidence) -> str. None (the default)
            means no LLM is configured; the template fallback is used directly.

    Returns:
        {"explanation": str, "source": "llm" | "template_fallback"}

    Never raises: any exception from `llm_client`, or a non-string/empty response,
    falls back to the deterministic template.
    """
    if llm_client is not None:
        try:
            text = llm_client(decision, evidence)
        except Exception:
            text = None  # LLM failed for any reason -- fall back, pipeline continues normally

        if isinstance(text, str) and text.strip():
            return {"explanation": text.strip(), "source": "llm"}

    return {"explanation": _template_explanation(decision), "source": "template_fallback"}
